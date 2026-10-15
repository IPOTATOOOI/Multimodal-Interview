import json
import uuid
import asyncio
import copy
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from loguru import logger
from app.database.mysql import execute_update, execute_query, execute_insert
from app.services.AI.qwen_api import call_qwen_api
from app.database.neo4j import graph
from app.core.redis_cache import build_cache_key, delete_cache_sync
from app.models.enums import ProcessStatus
import concurrent.futures


def _call_qwen_sync(prompt: str, **kwargs) -> str:
    """在同步（ThreadPoolExecutor）上下文中调用 Qwen API"""
    return asyncio.run(call_qwen_api(prompt, **kwargs))


class InterviewEndService:
    # 用于存储处理状态和结果的内存字典
    _process_store: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    async def cleanup_old_processes(cls):
        """清理超过30分钟的处理记录"""
        current_time = datetime.now()
        expired_ids = [
            pid for pid, data in cls._process_store.items()
            if current_time - data['timestamp'] > timedelta(minutes=30)
        ]
        for pid in expired_ids:
            cls._process_store.pop(pid, None)

    @classmethod
    async def start_processing(cls, history_id: int) -> str:
        """初始化处理任务"""
        await cls.cleanup_old_processes()
        process_id = str(uuid.uuid4())
        cls._process_store[process_id] = {
            "status": ProcessStatus.PROCESSING,
            "history_id": history_id,
            "timestamp": datetime.now(),
            "result": None,
            "error": None
        }
        return process_id

    @classmethod
    async def process_interview_end_async(cls, process_id: str, history_id: int):
        """异步处理面试结束评估"""
        try:
            # 使用线程池执行同步的end_interview_session函数
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor, 
                    end_interview_session, 
                    history_id
                )
            
            # 更新处理状态和结果
            cls._process_store[process_id].update({
                "status": ProcessStatus.COMPLETED,
                "result": result
            })
            logger.info(f"面试结束评估完成 - process_id: {process_id}, history_id: {history_id}")
        except Exception as e:
            logger.error(f"面试结束评估失败 - process_id: {process_id}, history_id: {history_id}, 错误: {str(e)}")
            cls._process_store[process_id].update({
                "status": ProcessStatus.FAILED,
                "error": str(e)
            })

    @classmethod
    async def get_process_status(cls, process_id: str) -> Dict[str, Any]:
        """获取处理状态和结果"""
        if process_id not in cls._process_store:
            # 内存中未找到，尝试从数据库查询（处理跨进程状态同步问题）
            try:
                # 查询是否有对应的历史记录
                rows = execute_query(
                    "SELECT end_time, history_id FROM interview_history WHERE process_id = %s",
                    (process_id,)
                )
                if rows:
                    history_id = rows[0].get("history_id")
                    end_time = rows[0].get("end_time")
                    
                    if end_time and history_id:
                        # 任务已完成，查询完整的评估结果
                        history_rows = execute_query(
                            "SELECT * FROM interview_history WHERE history_id = %s",
                            (history_id,)
                        )
                        qa_rows = execute_query(
                            "SELECT * FROM qa WHERE history_id = %s ORDER BY created_at ASC",
                            (history_id,)
                        )
                        result = {
                            "interview_history": history_rows[0] if history_rows else None,
                            "qa_log": qa_rows
                        }
                        # 为qa_log添加录音文件信息
                        try:
                            result["qa_log"] = _filter_qa_log_skip_first_answer(result["qa_log"])
                            result["qa_log"] = _match_audio_files_to_qa_log(
                                history_id,
                                result["qa_log"],
                                start_answer_index=1,
                            )
                        except Exception as e:
                            logger.error(f"为qa_log添加录音文件信息失败: {str(e)}")
                        
                        return {
                            "status": ProcessStatus.COMPLETED,
                            "result": result,
                            "error": None
                        }
                    elif history_id:
                        # 有记录但未完成
                        return {
                            "status": ProcessStatus.PROCESSING,
                            "result": None,
                            "error": None
                        }
                
                # 数据库中也未找到
                return {
                    "status": ProcessStatus.FAILED,
                    "error": "Process not found"
                }
            except Exception as e:
                logger.error(f"从数据库查询状态失败: {e}")
                return {
                    "status": ProcessStatus.FAILED,
                    "error": "查询状态失败"
                }
        
        process_data = cls._process_store[process_id]

        # 跨进程场景：consumer 在另一个进程更新了 DB，但无法修改 uvicorn 的内存。
        # 当内存状态仍为 PROCESSING 时，用 DB 的 end_time 做权威判断。
        if process_data["status"] == ProcessStatus.PROCESSING:
            try:
                rows = execute_query(
                    "SELECT end_time, history_id FROM interview_history WHERE process_id = %s",
                    (process_id,)
                )
                if rows and rows[0].get("end_time"):
                    history_id_db = rows[0].get("history_id")
                    history_rows = execute_query(
                        "SELECT * FROM interview_history WHERE history_id = %s",
                        (history_id_db,)
                    )
                    qa_rows = execute_query(
                        "SELECT * FROM qa WHERE history_id = %s ORDER BY created_at ASC",
                        (history_id_db,)
                    )
                    db_result = {
                        "interview_history": history_rows[0] if history_rows else None,
                        "qa_log": qa_rows
                    }
                    try:
                        db_result["qa_log"] = _filter_qa_log_skip_first_answer(db_result["qa_log"])
                        db_result["qa_log"] = _match_audio_files_to_qa_log(
                            history_id_db, db_result["qa_log"], start_answer_index=1
                        )
                    except Exception as e:
                        logger.error(f"为qa_log添加录音文件信息失败(DB回退): {e}")
                    # 同步回内存，避免下次轮询再查 DB
                    process_data.update({"status": ProcessStatus.COMPLETED, "result": db_result})
                    return {"status": ProcessStatus.COMPLETED, "result": db_result, "error": None}
            except Exception as e:
                logger.warning(f"跨进程状态回退DB查询失败: {e}")

        raw_result = process_data["result"]
        # 轮询status时使用副本，避免反复修改内存中的原始结果导致qa_log被重复过滤
        result = copy.deepcopy(raw_result) if raw_result is not None else None

        # 如果处理完成且有结果，为qa_log添加录音文件信息
        if process_data["status"] == ProcessStatus.COMPLETED and result:
            try:
                # 获取history_id
                history_id = process_data.get("history_id")
                if history_id and "qa_log" in result:
                    # status接口统一跳过首个回答（无论该回答是文本还是语音）
                    # 然后从第2个回答序号开始匹配录音文件，避免文字/语音混合导致错位
                    result["qa_log"] = _filter_qa_log_skip_first_answer(result["qa_log"])
                    result["qa_log"] = _match_audio_files_to_qa_log(
                            history_id,
                            result["qa_log"],
                            start_answer_index=1,
                        )
                    logger.info(f"已为history_id={history_id}的status qa_log跳过首个回答并添加录音文件信息")
            except Exception as e:
                logger.error(f"为qa_log添加录音文件信息失败: {str(e)}")
                # 即使录音文件匹配失败，也不影响主要功能
        
        return {
            "status": process_data["status"],
            "result": result,
            "error": process_data["error"]
        }

def _build_overall_eval_prompt(qa_summaries: list) -> str:
    """构建仅输出 overall_evaluation 的 prompt（交互式模式专用，individual_evaluations 已实时完成）。"""
    lines = []
    for i, item in enumerate(qa_summaries, 1):
        lines.append(
            f"第{i}题  问题：{item.get('question', '')}\n"
            f"  回答：{item.get('answer', '')}\n"
            f"  评分：{item.get('answer_rating', 'N/A')}/5.0  技能：{item.get('skill', '')}  类别：{item.get('category', '')}\n"
            f"  评价摘要：{item.get('evaluation', '')}"
        )
    summary_text = "\n\n".join(lines)

    return f"""你是资深 HR 与技术面试评审专家，依据面试问答摘要客观公正完成候选人综合评测，评分贴合真实面试表现，松紧适度、拒绝极端打分。评测全程以问答里实际作答内容、项目经历、实操思路、应答状态为核心依据，理性评判不主观偏见。{summary_text}
评测核心规范：
六大维度独立打分，结合作答深浅、实操经验、表述完整度灵活判定，分值区间 0-5 分，不刻意压分也不盲目高分。
总分综合六大维度整体表现核算，分值贴合真实水平，区间自然分布，不强制固定档位、不批量统一分数。
作答有完整项目案例、落地方法、实际成果、清晰实操经验，维度可给到 3-5 分；仅掌握基础理论、作答浅显无实操支撑，给到 1-3 分；知识点薄弱、应答卡顿含糊酌情 0-2 分。
整体基础扎实、应答流畅、具备岗位适配经验，总分合理落在 60-75 分；基础尚可但经验偏少、部分知识点生疏，总分 40-65 分；能力突出经验充足可 75 分以上，基础薄弱不足 40 分。
建设性建议贴合候选人实际短板撰写，务实中肯，侧重提升方向而非片面否定。
最终仅输出标准 JSON 对象，无额外文字、无 markdown、无多余解释。
JSON 固定格式：
{{"overall_evaluation": 
{{"professional_knowledge": "<int, 0-5>",
"skill_match": "<int, 0-5>",
"language_expression": "<int, 0-5>",
"logical_thinking": "<int, 0-5>",
"innovation_ability": "<int, 0-5>",
"stress_resistance": "<int, 0-5>",
"feedback_suggestion1": "< 建设性提升建议，35 字左右 >",
"feedback_suggestion2": "< 建设性提升建议，35 字左右 >",
"feedback_suggestion3": "< 建设性提升建议，35 字左右 >",
"score": "<int, 1-100，贴合真实面试水平合理打分 >"}}}}"""


def _apply_overall_score_cap(overall_eval: dict, qa_count: int) -> dict:
    """保留模型返回的总分，仅做类型与范围归一化。"""
    score_value = overall_eval.get("score")
    try:
        score_number = int(round(float(score_value)))
    except Exception:
        score_number = 0

    overall_eval["score"] = max(0, min(100, score_number))
    return overall_eval


def _extract_json_candidate(response: str) -> str:
    """提取可能的JSON主体，去除markdown包裹和前后缀噪声。"""
    cleaned_response = response.strip()
    # 去除三引号代码块包裹
    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response[7:]
    if cleaned_response.startswith("```"):
        cleaned_response = cleaned_response[3:]
    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3]
    cleaned_response = cleaned_response.strip()

    # 截取首尾花括号，去掉非JSON前后缀
    start_idx = cleaned_response.find("{")
    end_idx = cleaned_response.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        cleaned_response = cleaned_response[start_idx:end_idx + 1]

    return cleaned_response


def _clean_json_response(response: str) -> dict:
    """清理星火大模型返回的可能包含markdown格式或反引号HTML的JSON字符串"""
    cleaned_response = _extract_json_candidate(response)

    # 最终解析为JSON
    return json.loads(cleaned_response)


def _build_json_repair_prompt(raw_response: str) -> str:
    """构建JSON格式修复提示词，仅允许修复格式，不改变语义。"""
    return f"""
你是一个严格的JSON格式修复器。

任务：
1. 仅修复下面内容中的JSON语法错误（如缺逗号、引号、转义、括号不闭合等）。
2. 不得更改字段名，不得新增/删除业务字段，不得改变任何值的语义。
3. 输出必须是一个可被JSON解析器直接解析的JSON对象。
4. 只输出JSON对象本体，不要输出解释、注释或markdown代码块。

待修复内容：
{raw_response}
"""


def _json_error_context(raw_response: str, parse_error: Exception, radius: int = 120) -> Tuple[Optional[int], str]:
    """提取JSON解析错误附近片段，便于日志定位。"""
    candidate = _extract_json_candidate(raw_response)

    if isinstance(parse_error, json.JSONDecodeError):
        pos = parse_error.pos
        start = max(0, pos - radius)
        end = min(len(candidate), pos + radius)
        snippet = candidate[start:end]
        pointer = " " * max(0, pos - start) + "^"
        context = f"{snippet}\n{pointer}"
        return pos, context

    # 非JSONDecodeError时退化为首段内容，避免日志为空
    fallback = candidate[: radius * 2]
    return None, fallback


def _parse_with_repair(raw_response: str, history_id: int) -> dict:
    """先按现有方式解析，失败后自动触发一次JSON格式修复。"""
    try:
        return _clean_json_response(raw_response)
    except Exception as first_err:
        logger.warning(f"评估结果首次解析失败，尝试JSON格式修复: history_id={history_id}, error={str(first_err)}")

        repair_prompt = _build_json_repair_prompt(raw_response)
        repaired_response = _call_qwen_sync(repair_prompt)
        if not repaired_response or not repaired_response.strip():
            pos, ctx = _json_error_context(raw_response, first_err)
            logger.error(
                f"JSON修复失败：修复模型返回空内容, history_id={history_id}, first_error={str(first_err)}, first_error_pos={pos}, first_error_context={ctx}"
            )
            raise ValueError(f"评估结果解析失败，JSON修复返回空内容: {str(first_err)}")

        try:
            return _clean_json_response(repaired_response)
        except Exception as second_err:
            pos1, ctx1 = _json_error_context(raw_response, first_err)
            pos2, ctx2 = _json_error_context(repaired_response, second_err)
            logger.error(
                "评估结果JSON修复后仍解析失败: "
                f"history_id={history_id}, first_error={str(first_err)}, first_error_pos={pos1}, "
                f"second_error={str(second_err)}, second_error_pos={pos2}, "
                f"first_error_context={ctx1}, second_error_context={ctx2}"
            )
            raise ValueError(
                "评估结果解析失败，且JSON修复后仍无法解析: "
                f"原始错误: {str(first_err)}; 修复后错误: {str(second_err)}"
            )

def _get_random_tags_from_neo4j(count: int = 50) -> list:
    """从软件开发路径下定向查询 Tag（比纯随机更具针对性）"""
    try:
        if graph is None:
            logger.error("Neo4j数据库未连接")
            return []

        query = """
        MATCH (rc:RootCategory {name: '软件开发'})
        MATCH (rc)-[:HAS_SUB]->(sc)-[:CONTAINS_TOPIC]->(tp)-[:INCLUDES]->(q)-[:MARKED_AS]->(t:Tag)
        WITH DISTINCT t
        RETURN t.id AS id, t.name AS name
        ORDER BY rand() LIMIT $count
        """
        result = graph.run(query, count=count).data()
        if not result:
            # 回退到全量随机查询
            result = graph.run(
                "MATCH (t:Tag) RETURN t.id AS id, t.name AS name ORDER BY rand() LIMIT $count",
                count=count
            ).data()
        tags = [{"id": row["id"], "name": row["name"]} for row in result]
        logger.info(f"从Neo4j定向查询到{len(tags)}个Tag节点")
        return tags
    except Exception as e:
        logger.error(f"查询Neo4j Tag节点失败: {str(e)}")
        return []


def _upsert_weak_at(user_id, tag_id: str, strength: float):
    """创建或更新 WEAK_AT 关系，取既有 strength 与新值中的较大值"""
    try:
        if graph is None:
            return
        try:
            uid = int(user_id)
        except Exception:
            uid = user_id
        graph.run("""
            MERGE (u:User {id: $uid})
            WITH u
            MATCH (t:Tag {id: $tid})
            MERGE (u)-[r:WEAK_AT]->(t)
            ON CREATE SET r.strength = $strength, r.updated_at = timestamp()
            ON MATCH SET
                r.strength = CASE WHEN r.strength < $strength THEN $strength ELSE r.strength END,
                r.updated_at = timestamp()
        """, uid=uid, tid=tag_id, strength=strength)
    except Exception as e:
        logger.error(f"upsert_weak_at 失败 tag_id={tag_id}: {e}")


def _upsert_interacts(user_id, question_title: str, correctness: float):
    """创建或更新 User-INTERACTS->Question 关系（笔试答题记录）"""
    try:
        if graph is None:
            return
        try:
            uid = int(user_id)
        except Exception:
            uid = user_id
        graph.run("""
            MERGE (u:User {id: $uid})
            WITH u
            MATCH (q:Question {title: $title})
            MERGE (u)-[r:INTERACTS]->(q)
            ON CREATE SET r.correctness = $correctness, r.updated_at = timestamp()
            ON MATCH SET
                r.correctness = $correctness,
                r.updated_at = timestamp()
        """, uid=uid, title=question_title, correctness=correctness)
    except Exception as e:
        logger.error(f"upsert_interacts 失败 question_title={question_title}: {e}")


def _update_weak_at_from_written_test(history_id: int, user_id) -> None:
    """根据笔试题目得分将薄弱 Tag 写入 Neo4j WEAK_AT（question_score=0 视为失败）"""
    try:
        rows = execute_query(
            "SELECT tag_name, COUNT(*) AS cnt, "
            "SUM(CASE WHEN question_score = 0 THEN 1 ELSE 0 END) AS fail_cnt "
            "FROM written_test WHERE history_id = %s GROUP BY tag_name",
            (history_id,)
        )
        if not rows:
            return
        for row in rows:
            fail_cnt = row.get("fail_cnt") or 0
            cnt = row.get("cnt") or 1
            if not fail_cnt:
                continue
            strength = round((fail_cnt / cnt) * 5.0, 2)
            tag_name = row.get("tag_name")
            if not tag_name:
                continue
            tag_result = graph.run(
                "MATCH (t:Tag {name: $name}) RETURN t.id AS id LIMIT 1",
                name=tag_name
            ).data()
            if tag_result:
                _upsert_weak_at(user_id, tag_result[0]["id"], strength)
        logger.info(f"written_test WEAK_AT 同步完成 history_id={history_id}")
    except Exception as e:
        logger.error(f"_update_weak_at_from_written_test 失败: {e}")

def _select_tags_by_evaluation(overall_eval: dict, individual_evals: list, all_tags: list, user_id) -> list:
    """
    使用大模型根据评估结果从Tag中筛选出20个最适合的Tag
    
    Args:
        overall_eval: 总体评估结果
        individual_evals: 单项评估结果列表
        all_tags: 所有可用的Tag列表
        
    Returns:
        list: 筛选出的Tag ID列表，并在Neo4j中将这些Tag与当前用户通过 WEAK_AT 关联
    """
    try:
        # 构建Tag列表字符串
        tags_str = "\n".join([f"- {tag['name']} (ID: {tag['id']})" for tag in all_tags])
        
        # 构建评估结果摘要
        eval_summary = f"""
总体评估：
- 专业知识: {overall_eval.get('professional_knowledge', 'N/A')}/5
- 技能匹配: {overall_eval.get('skill_match', 'N/A')}/5
- 语言表达: {overall_eval.get('language_expression', 'N/A')}/5
- 逻辑思维: {overall_eval.get('logical_thinking', 'N/A')}/5
- 创新能力: {overall_eval.get('innovation_ability', 'N/A')}/5
- 抗压能力: {overall_eval.get('stress_resistance', 'N/A')}/5
- 总分: {overall_eval.get('score', 'N/A')}/100

单项评估摘要：
"""
        for i, eval_item in enumerate(individual_evals[:3]):  # 只取前3个作为示例
            eval_summary += f"- 问题{i+1}: 技能={eval_item.get('skill', 'N/A')}, 类别={eval_item.get('category', 'N/A')}, 评分={eval_item.get('answer_rating', 'N/A')}/5.0\n"
        
        prompt = f"""
你是专业的面试评估专家。根据以下面试评估结果，从提供的Tag中选择20个最适合该候选人的Tag，用于推荐练习题目。

评估结果：
{eval_summary}

可用Tag列表：
{tags_str}

要求：
1. 根据候选人的薄弱环节和需要提升的技能选择Tag
2. 优先选择与候选人技能匹配度较低的Tag
3. 考虑候选人的专业领域和岗位要求
4. 只返回JSON格式的Tag ID列表，不要有任何解释说明
5. 返回格式：["tag-id-1", "tag-id-2", ..., "tag-id-20"]

重要：只返回JSON数组，不要有markdown格式。
"""
        
        result = _call_qwen_sync(prompt)
        logger.info(f"大模型返回的Tag筛选结果: {result}")
        
        # 检查返回结果是否为空
        if not result or result.strip() == "":
            logger.warning("大模型返回空结果，使用默认Tag")
            # 使用一些通用的重要Tag作为默认值
            default_tags = [
                "tag-algorithm-complexity", "tag-data-structure", "tag-sort-algorithm",
                "tag-search-algorithm", "tag-class", "tag-inheritance", "tag-thread",
                "tag-concurrency", "tag-tree-structure", "tag-graph-structure",
                "tag-func-lib", "tag-exception", "tag-test-case", "tag-oop", "tag-memory",
                "tag-string", "tag-file", "tag-database", "tag-network", "tag-security"
            ]
            return default_tags[:20]
        
        # 清理JSON字符串
        cleaned_result = result.strip()
        if cleaned_result.startswith("```json"):
            cleaned_result = cleaned_result[7:]
        if cleaned_result.startswith("```"):
            cleaned_result = cleaned_result[3:]
        if cleaned_result.endswith("```"):
            cleaned_result = cleaned_result[:-3]
        cleaned_result = cleaned_result.strip()
        
        try:
            selected_tag_ids = json.loads(cleaned_result)
            logger.info(f"筛选出的Tag ID列表: {selected_tag_ids}")

            # 在图数据库中将用户与这些Tag建立 WEAK_AT 关系（携带 strength）
            try:
                base_strength = min(4.0, max(0.5, 5.0 - overall_eval.get('score', 60) / 20.0))
                for tid in selected_tag_ids[:20]:
                    _upsert_weak_at(user_id, tid, base_strength)
                logger.info(f"已为用户 {user_id} 写入 {len(selected_tag_ids[:20])} 个 WEAK_AT 关系 (strength={base_strength:.1f})")
            except Exception as neo_err:
                logger.error(f"在Neo4j中建立用户与Tag关系失败: {str(neo_err)}")

            return selected_tag_ids[:20]  # 确保只返回20个
        except json.JSONDecodeError as json_error:
            logger.error(f"JSON解析失败: {str(json_error)}, 原始内容: {cleaned_result}")
            # 使用默认Tag
            default_tags = [
                "tag-algorithm-complexity", "tag-data-structure", "tag-sort-algorithm",
                "tag-search-algorithm", "tag-class", "tag-inheritance", "tag-thread",
                "tag-concurrency", "tag-tree-structure", "tag-graph-structure",
                "tag-func-lib", "tag-exception", "tag-test-case", "tag-oop", "tag-memory",
                "tag-string", "tag-file", "tag-database", "tag-network", "tag-security"
            ]
            # 建立关系（即使使用默认Tag，也尽量建立关系）
            try:
                base_strength = min(4.0, max(0.5, 5.0 - overall_eval.get('score', 60) / 20.0))
                for tid in default_tags[:20]:
                    _upsert_weak_at(user_id, tid, base_strength)
            except Exception as neo_err:
                logger.error(f"在Neo4j中建立用户与默认Tag关系失败: {str(neo_err)}")
            return default_tags[:20]

    except Exception as e:
        logger.error(f"筛选Tag失败: {str(e)}")
        default_tags = [
            "tag-algorithm-complexity", "tag-data-structure", "tag-sort-algorithm",
            "tag-search-algorithm", "tag-class", "tag-inheritance", "tag-thread",
            "tag-concurrency", "tag-tree-structure", "tag-graph-structure",
            "tag-func-lib", "tag-exception", "tag-test-case", "tag-oop", "tag-memory",
            "tag-string", "tag-file", "tag-database", "tag-network", "tag-security"
        ]
        try:
            for tid in default_tags[:20]:
                _upsert_weak_at(user_id, tid, 2.0)
        except Exception as neo_err:
            logger.error(f"在Neo4j中建立用户与默认Tag关系失败: {str(neo_err)}")
        return default_tags[:20]

def _get_questions_by_tags(tag_ids: list) -> list:
    """
    根据Tag ID列表从Neo4j中查询对应的题目，每个Tag随机选择一道题
    
    Args:
        tag_ids: Tag ID列表
        
    Returns:
        list: 题目列表，每个元素包含题目的完整信息
    """
    try:
        if graph is None:
            logger.error("Neo4j数据库未连接")
            return []
            
        questions = []
        for tag_id in tag_ids:
            # 为每个Tag随机查询一道题
            query = """
            MATCH (t:Tag {id: $tag_id})-[:MARKED_AS]-(q:Question)
            OPTIONAL MATCH (q)-[:TESTS]->(kp:KnowledgePoint)
            WITH q, t, collect(DISTINCT kp.name) AS knowledge_points
            RETURN q.id AS id, q.title AS title, q.content AS content, 
                   q.choice AS choice, q.type AS type, q.difficulty AS difficulty, 
                   q.answer AS answer, t.name AS tag_name,
                   knowledge_points[0] AS knowledgepoint_name
            ORDER BY rand() LIMIT 1
            """
            result = graph.run(query, tag_id=tag_id).data()
            
            if result:
                question = result[0]
                questions.append({
                    "question_id": question["id"],
                    "title": question["title"],
                    "content": question["content"],
                    "choice": question["choice"] or " ",
                    "question_type": question["type"],
                    "difficulty": question["difficulty"],
                    "standard_answer": question["answer"],
                    "tag_name": question["tag_name"],
                    "knowledgepoint_name": question["knowledgepoint_name"] or "",
                    "question_score": 5.0
                })
                logger.info(f"为Tag {tag_id} 查询到题目: {question['title']}")
            else:
                logger.warning(f"为Tag {tag_id} 未查询到题目")
        
        logger.info(f"总共查询到{len(questions)}道推荐题目")
        return questions
        
    except Exception as e:
        logger.error(f"根据Tag查询题目失败: {str(e)}")
        return []

def _get_weak_at_tags_from_neo4j(user_id, count: int = 60) -> list:
    """查询用户已有的 WEAK_AT 标签（来自历次面试积累），按 strength 降序。"""
    try:
        if graph is None or user_id is None:
            return []
        try:
            uid = int(user_id)
        except Exception:
            uid = user_id
        result = graph.run("""
            MATCH (u:User {id: $uid})-[r:WEAK_AT]->(t:Tag)
            RETURN t.id AS id, t.name AS name, coalesce(r.strength, 1.0) AS strength
            ORDER BY strength DESC LIMIT $count
        """, uid=uid, count=count).data()
        return [{"id": row["id"], "name": row["name"]} for row in result]
    except Exception as e:
        logger.warning(f"查询用户 WEAK_AT 标签失败: {e}")
        return []


def _get_recommended_questions(overall_eval: dict, individual_evals: list, user_id) -> list:
    """
    根据评估结果获取推荐题目。
    优先使用用户在 Neo4j 中积累的 WEAK_AT 标签作为候选池（质量高于随机），
    仅在用户首次面试（无历史 WEAK_AT）时回退到定向随机查询。
    """
    try:
        # 1. 优先使用用户已有的 WEAK_AT 标签（历次面试积累）
        all_tags = _get_weak_at_tags_from_neo4j(user_id, count=60)
        if all_tags:
            logger.info(f"使用用户 WEAK_AT 标签作为候选池，共 {len(all_tags)} 个")
        else:
            # 首次面试或无历史数据 → 定向随机查询（软件开发路径下）
            logger.info("用户无历史 WEAK_AT 标签，使用定向随机 Tag 池")
            all_tags = _get_random_tags_from_neo4j(60)

        if not all_tags:
            logger.warning("未查询到 Tag，返回空推荐列表")
            return []

        # 2. 使用 Qwen 结合评估结果筛选 20 个最相关 Tag（同时写入 WEAK_AT）
        selected_tag_ids = _select_tags_by_evaluation(overall_eval, individual_evals, all_tags, user_id)
        if not selected_tag_ids:
            logger.warning("未筛选出 Tag，返回空推荐列表")
            return []

        # 3. 根据选中的 Tag 查询对应题目
        return _get_questions_by_tags(selected_tag_ids)

    except Exception as e:
        logger.error(f"获取推荐题目失败: {str(e)}")
        return []

def _filter_qa_log_skip_first_answer(qa_log: list) -> list:
    """
    过滤qa_log，问题和回答都保留。
    第一题已改为固定的自我介绍问题，会存入数据库，不需要跳过首个回答。
    """
    questions = [item for item in qa_log if item.get('role') == 0]
    answers = [item for item in qa_log if item.get('role') == 1]
    # 保留所有问题和回答（第一题自我介绍已存入数据库）
    filtered_questions = questions
    filtered_answers = answers
    # 优先按question_qa_id绑定，未绑定的回答再按顺序回填
    question_index_by_id = {q.get('qa_id'): idx for idx, q in enumerate(filtered_questions)}
    assigned_answers = [None] * len(filtered_questions)
    unbound_answers = []

    for ans in filtered_answers:
        kw = ans.get('key_words')
        bound_idx = None
        if isinstance(kw, str) and kw.startswith("qid:"):
            try:
                qid = int(kw.split(":", 1)[1])
                if qid in question_index_by_id:
                    bound_idx = question_index_by_id[qid]
            except ValueError:
                bound_idx = None

        if bound_idx is not None and assigned_answers[bound_idx] is None:
            assigned_answers[bound_idx] = ans
        else:
            unbound_answers.append(ans)

    # 未绑定回答优先做关键词/题干兜底匹配，减少回答乱序导致的错配
    def _safe_text(value: Any) -> str:
        return str(value).strip().lower() if value is not None else ""

    def _score_answer_to_question(answer_item: dict, question_item: dict) -> int:
        score = 0
        answer_text = _safe_text(answer_item.get("content"))
        if not answer_text:
            return 0

        # 1) 关键字命中权重更高
        key_words = _safe_text(question_item.get("key_words"))
        if key_words:
            for kw in [x.strip().lower() for x in key_words.split(",") if x.strip()]:
                if kw and kw in answer_text:
                    score += 5

        # 2) 题干短语命中作为辅助
        q_text = _safe_text(question_item.get("content"))
        if q_text:
            for token in [t.strip() for t in q_text.replace("，", " ").replace("。", " ").replace("？", " ").replace("、", " ").split() if len(t.strip()) >= 2]:
                if token and token.lower() in answer_text:
                    score += 1

        return score

    # 先尝试语义兜底匹配
    remaining_unbound = []
    for ans in unbound_answers:
        best_idx = None
        best_score = 0
        for idx, q in enumerate(filtered_questions):
            if assigned_answers[idx] is not None:
                continue
            s = _score_answer_to_question(ans, q)
            if s > best_score:
                best_score = s
                best_idx = idx

        if best_idx is not None and best_score > 0:
            assigned_answers[best_idx] = ans
            logger.info(
                f"未绑定回答兜底匹配成功: answer_qa_id={ans.get('qa_id')} -> question_qa_id={filtered_questions[best_idx].get('qa_id')}, score={best_score}"
            )
        else:
            remaining_unbound.append(ans)

    # 仍未匹配上的回答再按题目顺序填补空位（兼容旧数据）
    unbound_iter = iter(remaining_unbound)
    for idx in range(len(assigned_answers)):
        if assigned_answers[idx] is None:
            assigned_answers[idx] = next(unbound_iter, None)

    # 合并为交替排列
    result = []
    for i, q in enumerate(filtered_questions):
        result.append(q)
        ans = assigned_answers[i]
        if ans is not None:
            ans_copy = ans.copy()
            # 对前端隐藏内部绑定标记
            if isinstance(ans_copy.get('key_words'), str) and ans_copy['key_words'].startswith('qid:'):
                ans_copy['key_words'] = None
            result.append(ans_copy)
    return result



def _collect_interactive_qa_summaries(history_id: int) -> tuple:
    """
    收集交互式面试中已完成的单题评估数据，用于构建 overall_evaluation prompt。
    Returns:
        (qa_summaries: list, individual_evals: list)
        qa_summaries 供 prompt 构建；individual_evals 供 _get_recommended_questions。
    """
    # 按顺序拉取题目和回答，跳过首条回答
    q_rows = execute_query(
        "SELECT qa_id, content FROM qa WHERE history_id = %s AND role = 0 ORDER BY created_at ASC",
        (history_id,),
    )
    a_rows = execute_query(
        """SELECT qa_id, content, evaluation, feedback, reference_a, skill, category, answer_rating, key_words
           FROM qa WHERE history_id = %s AND role = 1 ORDER BY created_at ASC""",
        (history_id,),
    )

    qa_summaries = []
    individual_evals = []
    for i, q in enumerate(q_rows):
        a = a_rows[i] if i < len(a_rows) else None
        summary = {
            "question": q["content"],
            "answer": a["content"] if a else "",
            "evaluation": a.get("evaluation", "") if a else "",
            "feedback": a.get("feedback", "") if a else "",
            "skill": a.get("skill", "") if a else "",
            "category": a.get("category", "") if a else "",
            "answer_rating": a.get("answer_rating") if a else None,
        }
        qa_summaries.append(summary)
        individual_evals.append({
            "evaluation": summary["evaluation"],
            "feedback": summary["feedback"],
            "skill": summary["skill"],
            "category": summary["category"],
            "answer_rating": summary["answer_rating"],
        })

    return qa_summaries, individual_evals


def end_interview_session(history_id: int) -> dict:
    """
    结束面试会话：汇总各题实时评估结果，调用一次 LLM 生成 overall_evaluation，
    并完成薄弱点推荐与数据持久化。
    """
    try:
        logger.info(f"开始结束面试流程，history_id: {history_id}")

        # 1. 更新面试结束时间
        end_time = datetime.now()
        execute_update("UPDATE interview_history SET end_time = %s WHERE history_id = %s", (end_time, history_id))
        logger.info(f"已记录面试结束时间，history_id: {history_id}")

        # 2. 校验存在问答记录
        qa_count = execute_query(
            "SELECT COUNT(*) AS cnt FROM qa WHERE history_id = %s", (history_id,)
        )
        if not qa_count or qa_count[0]["cnt"] == 0:
            raise ValueError("未找到该面试的问答记录")

        # 3. 收集各题已完成的实时评估，构建 overall_evaluation prompt
        qa_summaries, individual_evals = _collect_interactive_qa_summaries(history_id)
        logger.info(f"收集到 {len(qa_summaries)} 组问答摘要用于总体评估，history_id: {history_id}")

        prompt = _build_overall_eval_prompt(qa_summaries)
        api_result_str = ""
        for attempt in range(2):
            api_result_str = _call_qwen_sync(prompt)
            if api_result_str and api_result_str.strip():
                break
            logger.warning(f"总体评估模型返回空内容: history_id={history_id}, attempt={attempt + 1}/2")
        if not api_result_str or not api_result_str.strip():
            raise ValueError("总体评估模型返回空内容，请稍后重试")

        api_result_json = _parse_with_repair(api_result_str, history_id)
        overall_eval = api_result_json.get("overall_evaluation", {})
        overall_eval = _apply_overall_score_cap(overall_eval, len(qa_summaries))

        logger.info(
            f"评估摘要: score={overall_eval.get('score')}, skill_match={overall_eval.get('skill_match')}, "
            f"language_expression={overall_eval.get('language_expression')}"
        )

        # ── 5. 更新 interview_history 表（两种模式共用）────────────────────
        execute_update(
            """UPDATE interview_history SET
                   professional_knowledge=%s, skill_match=%s, language_expression=%s,
                   logical_thinking=%s, innovation_ability=%s, stress_resistance=%s,
                   feedback_suggestion1=%s, feedback_suggestion2=%s, feedback_suggestion3=%s,
                   score=%s, html=%s
               WHERE history_id=%s""",
            (
                overall_eval.get('professional_knowledge'), overall_eval.get('skill_match'),
                overall_eval.get('language_expression'), overall_eval.get('logical_thinking'),
                overall_eval.get('innovation_ability'), overall_eval.get('stress_resistance'),
                overall_eval.get('feedback_suggestion1'), overall_eval.get('feedback_suggestion2'),
                overall_eval.get('feedback_suggestion3'), overall_eval.get('score'),
                " ", history_id,
            ),
        )
        delete_cache_sync(build_cache_key("ask", "history", history_id, "detail"))
        logger.info(f"interview_history表已更新，history_id: {history_id}")

        # ── 6. 薄弱点推荐（两种模式共用）────────────────────────────────────
        try:
            user_info = execute_query("SELECT user_id FROM interview_history WHERE history_id = %s", (history_id,))
            current_user_id = user_info[0]["user_id"] if user_info else None
        except Exception:
            current_user_id = None

        recommended_questions = _get_recommended_questions(overall_eval, individual_evals, current_user_id)

        # 7.1 将推荐的薄弱点题目写入 weakness 表
        try:
            if recommended_questions:
                insert_sql = (
                    """
                    INSERT INTO `weakness`
                        (`history_id`, `question_id`, `title`, `content`, `choice`, `question_type`,
                         `difficulty`, `standard_answer`, `tag_name`, `knowledgepoint_name`, `question_score`)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                )

                inserted_count = 0
                for question_item in recommended_questions:
                    params = (
                        history_id,
                        question_item.get("question_id"),
                        question_item.get("title"),
                        question_item.get("content"),
                        question_item.get("choice", " "),
                        question_item.get("question_type"),
                        question_item.get("difficulty"),
                        question_item.get("standard_answer"),
                        question_item.get("tag_name"),
                        question_item.get("knowledgepoint_name", ""),
                        question_item.get("question_score", 5.0)
                    )
                    execute_insert(insert_sql, params)
                    inserted_count += 1
                logger.info(f"weakness表已插入{inserted_count}条薄弱点推荐题目，history_id: {history_id}")
            else:
                logger.info("未生成薄弱点推荐题目，跳过weakness表写入")
        except Exception as weakness_err:
            logger.error(f"写入weakness表失败: {str(weakness_err)}")

        # 笔试薄弱点同步到 Neo4j WEAK_AT（不影响主流程）
        try:
            if current_user_id:
                _update_weak_at_from_written_test(history_id, current_user_id)
        except Exception as e:
            logger.warning(f"written_test WEAK_AT 同步失败: {e}")

        # 笔试答题记录同步到 Neo4j INTERACTS 关系（不影响主流程）
        try:
            if current_user_id:
                written_test_rows = execute_query(
                    "SELECT title, question_score FROM written_test WHERE history_id = %s",
                    (history_id,)
                )
                for row in written_test_rows:
                    title = row.get("title")
                    score = row.get("question_score")
                    if title and score is not None:
                        try:
                            score_float = float(score)
                            correctness = score_float / 5.0  # 转换为 0-1 的正确率
                            _upsert_interacts(current_user_id, title, correctness)
                        except (ValueError, TypeError):
                            logger.warning(f"无效的评分值: {score}")
                logger.info(f"INTERACTS 关系同步完成 history_id={history_id}")
        except Exception as e:
            logger.warning(f"INTERACTS 关系同步失败: {e}")

        # 8. 获取并返回最新数据
        final_history = execute_query("SELECT * FROM interview_history WHERE history_id = %s", (history_id,))
        final_qa = execute_query("SELECT * FROM qa WHERE history_id = %s ORDER BY created_at ASC", (history_id,))
        # 返回完整qa_log，并按回答序号分配音频
        final_qa = _match_audio_files_to_qa_log(history_id, final_qa)

        # 新增：获取前三张landmark截图（当前为固定示例图片，实际可按history_id动态获取）
        # landmark_images = [
        #     "example_07_landmarks.jpg",
        #     "example_08_landmarks.jpg",
        #     "example_010_landmarks.jpg"
        # ]
        # 如需根据history_id动态获取截图，可使用如下代码：
        import os
        landmark_dir = os.path.join(os.getcwd(), "facial_landmarks", "img-landmarks")
        landmark_images = []
        for n in [1, 2, 3]:
            filename = f"his-{history_id}-img-{n}_landmarks.jpg"
            file_path = os.path.join(landmark_dir, filename)
            logger.info(f"file_path: {file_path}")
            if os.path.exists(file_path):
                landmark_images.append(filename)
        
        return {
            "interview_history": final_history[0] if final_history else None,
            "qa_log": final_qa,
            "recommended_questions": recommended_questions,
            "landmark_images": landmark_images
        }
    except Exception as e:
        logger.error(f"结束面试流程失败: {e}")
        raise e 

def _match_audio_files_to_qa_log(history_id: int, qa_log: list, start_answer_index: int = 1) -> list:
    """
    将录音文件匹配到qa_log中的每个问答记录
    
    Args:
        history_id: 面试历史ID
        qa_log: 问答记录列表
        
    Returns:
        list: 包含录音文件信息的qa_log
    """
    try:
        import os
        import glob
        
        # 获取uploads/audio目录下的所有录音文件
        audio_dir = os.path.join(os.getcwd(), "uploads", "audio")
        if not os.path.exists(audio_dir):
            logger.warning(f"录音文件目录不存在: {audio_dir}")
            return qa_log
        
        # 建立"回答序号 -> 音频文件名"映射，支持多种扩展名
        pattern = f"his-{history_id}-audioid-*.*"
        audio_files = glob.glob(os.path.join(audio_dir, pattern))
        audio_map = {}

        for audio_file in audio_files:
            filename = os.path.basename(audio_file)
            try:
                # 文件名格式: his-{history_id}-audioid-{answer_index}.{ext}
                prefix = f"his-{history_id}-audioid-"
                if not filename.startswith(prefix):
                    continue
                number_part = filename[len(prefix):].split('.')[0]
                answer_index = int(number_part)
                audio_map[answer_index] = filename
            except (ValueError, IndexError):
                logger.warning(f"解析录音文件名失败: {filename}")

        if not audio_map:
            logger.info(f"未找到history_id={history_id}的可匹配录音文件")
            return qa_log

        logger.info(f"找到{len(audio_map)}个可匹配录音文件")

        # 将录音文件按回答序号精确匹配到qa_log中的回答记录
        # start_answer_index用于支持“跳过前N个回答后再返回”场景
        answer_order = 0
        updated_qa_log = []
        
        for qa_record in qa_log:
            qa_record_copy = qa_record.copy()
            
            # 只为回答记录（role=1）添加录音文件，并按回答序号匹配
            if qa_record.get('role') == 1:
                answer_order += 1
                expected_answer_index = start_answer_index + answer_order - 1
                audio_filename = audio_map.get(expected_answer_index)
                if audio_filename:
                    qa_record_copy['audio_file'] = {
                        "filename": audio_filename
                    }
                    logger.info(
                        f"为qa_id={qa_record.get('qa_id')}按回答序号{expected_answer_index}匹配录音文件: {audio_filename}"
                    )
                else:
                    qa_record_copy['audio_file'] = None
            else:
                qa_record_copy['audio_file'] = None
            
            updated_qa_log.append(qa_record_copy)
        
        return updated_qa_log
        
    except Exception as e:
        logger.error(f"匹配录音文件失败: {str(e)}")
        return qa_log