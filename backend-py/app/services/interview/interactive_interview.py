import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator, Optional

from fastapi import BackgroundTasks
from loguru import logger

from app.database.mysql import execute_query, execute_insert, execute_update
from app.services.AI.qwen_api import call_qwen_api, call_qwen_api_stream
from app.services.interview.interview_end import _parse_with_repair
from app.services.mq.rabbitmq_producer import publish_evaluation_job

MAX_FOLLOW_UP = 3        # 同一话题最多连续追问次数
MAX_TOTAL_QUESTIONS = 10 # 全程最多题目数量（含首问）
CONTEXT_WINDOW = 6       # 发给 LLM 的最近 QA 条数


# ── 提示词构建 ────────────────────────────────────────────────────────────────

def _build_single_eval_prompt(question: str, answer: str) -> str:
    return f"""
你是面试评估专家，请对以下单道面试问答进行独立评估。

问题：{question}
候选人回答：{answer}

**严格要求：**
只返回JSON对象，不要任何解释说明，不要markdown格式，不要代码块。

JSON格式：
{{
  "evaluation": "<对该回答的具体评价，中文，50字左右>",
  "feedback": "<针对性改进建议，中文，50字左右>",
  "reference_a": "<该问题的参考答案，中文>",
  "skill": "<该问题考察的专业技能，例如：Python并发编程>",
  "category": "<问题所属类别，例如：后端开发/数据库/算法>",
  "answer_rating": <float, 0.0-5.0, 回答质量评分>
}}
"""


def _build_action_decision_prompt(
    career_domain: str,
    job_role: str,
    current_topic: str,
    follow_up_count: int,
    total_asked: int,
    recent_context: str,
    answer: str,
) -> str:
    """
    轻量级 JSON 决策提示词：仅决定下一步行动和话题，不生成问题正文。
    响应体积小，耗时约 300ms。
    """
    return f"""
你是一名资深面试官，正在对{career_domain}领域{job_role}岗位的候选人进行面试。

当前面试状态：
- 当前考察话题：{current_topic}
- 本话题已连续追问次数：{follow_up_count}（上限{MAX_FOLLOW_UP}次，达到上限必须切换话题）
- 已提问总题数：{total_asked}（上限{MAX_TOTAL_QUESTIONS}题，达到上限必须结束）

最近对话记录：
{recent_context}

候选人刚才的回答：
{answer}

**你的任务：**
根据候选人的表现决定下一步行动。

**决策规则：**
1. 回答不完整/有明显知识盲点/值得深挖，且追问未达上限 → follow_up
2. 当前话题已充分考察，或追问已达上限 → next_topic
3. 已提问总数达到上限，或整体表现已足够评估 → end

**难度规则：** 根据候选人表现动态调整（优秀→困难，一般→中等/基础）

**严格要求：** 只返回JSON对象，无任何解释或markdown。

JSON格式：
{{
  "action": "follow_up 或 next_topic 或 end",
  "topic": "下一道题所属话题（follow_up时与当前话题相同，end时填null）",
  "difficulty": "基础/中等/困难（end时填null）"
}}
"""


def _build_question_generation_prompt(
    action: str,
    topic: str,
    difficulty: str,
    career_domain: str,
    job_role: str,
    recent_context: str,
) -> str:
    """
    流式问题生成提示词：要求 LLM 直接输出问题正文（纯文本，无 JSON 包装）。
    该结果直接流式推送给前端。
    """
    action_desc = "追问（在当前话题上进一步深挖）" if action == "follow_up" else "切换到新话题提问"
    return f"""
你是一名资深面试官，正在对{career_domain}领域{job_role}岗位的候选人进行面试。

当前操作：{action_desc}
话题：{topic}
难度：{difficulty}

最近对话记录：
{recent_context}

**你的任务：**
请直接输出一道面试问题，用于{action_desc}。

**要求：**
- 直接输出问题正文，不要加任何前缀（如"问题："、"好的，"等）
- 问题要简洁明确，中文，一到两句话
- 不要输出 JSON，不要输出解释，只输出问题本身
"""


# ── 数据库辅助函数（供 asyncio.to_thread 调用）────────────────────────────────

def _save_text_answer(history_id: int, question_qa_id: int, answer_content: str) -> int:
    """将文字回答写入 qa 表，返回 answer_qa_id。"""
    answer_qa_id = execute_insert(
        """INSERT INTO qa (history_id, role, content, created_at, key_words)
           VALUES (%s, %s, %s, %s, %s)""",
        (history_id, 1, answer_content, datetime.now(), f"qid:{question_qa_id}"),
    )
    logger.info(f"文字回答已写入 qa 表: answer_qa_id={answer_qa_id}")
    return answer_qa_id


def _get_voice_answer(history_id: int, question_qa_id: int) -> tuple[int, str]:
    """从 qa 表查找已转写的语音回答，返回 (answer_qa_id, answer_content)。"""
    rows = execute_query(
        """SELECT qa_id, content FROM qa
           WHERE history_id = %s AND role = 1 AND key_words = %s
           ORDER BY created_at DESC LIMIT 1""",
        (history_id, f"qid:{question_qa_id}"),
    )
    if not rows:
        rows = execute_query(
            """SELECT qa_id, content FROM qa
               WHERE history_id = %s AND role = 1
               ORDER BY created_at DESC LIMIT 1""",
            (history_id,),
        )
    if not rows:
        raise ValueError(f"找不到 history_id={history_id} 的回答记录，请先提交回答")
    return rows[0]["qa_id"], rows[0]["content"]


def _get_question_and_session(
    history_id: int, question_qa_id: int
) -> tuple[str, str, dict]:
    """
    合并读取：问题内容 + 会话状态，减少 DB 往返次数。
    返回 (question_content, stored_topic, session_dict)。
    """
    question_rows = execute_query(
        "SELECT content, key_words FROM qa WHERE qa_id = %s AND role = 0",
        (question_qa_id,),
    )
    if not question_rows:
        raise ValueError(f"找不到 qa_id={question_qa_id} 的问题记录")

    history_rows = execute_query(
        """SELECT current_topic, follow_up_count, total_questions_asked, field, position
           FROM interview_history WHERE history_id = %s""",
        (history_id,),
    )
    if not history_rows:
        raise ValueError(f"找不到 history_id={history_id} 的面试记录")

    return (
        question_rows[0]["content"],
        question_rows[0].get("key_words") or "",
        history_rows[0],
    )


def get_recent_context(history_id: int, window: int = CONTEXT_WINDOW) -> str:
    """从 qa 表中提取最近 window 条记录，拼接为上下文字符串。"""
    try:
        rows = execute_query(
            """SELECT role, content FROM qa
               WHERE history_id = %s
               ORDER BY created_at DESC
               LIMIT %s""",
            (history_id, window),
        )
        if not rows:
            return ""
        lines = []
        for row in reversed(rows):
            prefix = "面试官" if row["role"] == 0 else "候选人"
            lines.append(f"{prefix}：{row['content']}")
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"获取对话上下文失败: {e}")
        return ""


def _update_session_state(history_id: int, action: str, next_topic: str) -> None:
    """更新 interview_history 中的会话状态。"""
    if action == "follow_up":
        execute_update(
            """UPDATE interview_history
               SET follow_up_count = follow_up_count + 1,
                   total_questions_asked = total_questions_asked + 1
               WHERE history_id = %s""",
            (history_id,),
        )
    elif action == "next_topic":
        execute_update(
            """UPDATE interview_history
               SET follow_up_count = 0, current_topic = %s,
                   total_questions_asked = total_questions_asked + 1
               WHERE history_id = %s""",
            (next_topic, history_id),
        )


def _insert_next_question(
    history_id: int, question_text: str, difficulty: str, topic: str
) -> int:
    """将下一道题保存到 qa 表，返回新的 qa_id。"""
    new_qa_id = execute_insert(
        """INSERT INTO qa (history_id, role, content, created_at, difficulty, key_words)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (history_id, 0, question_text, datetime.now(), difficulty, topic),
    )
    logger.info(
        f"下一道题已写入 qa 表: new_qa_id={new_qa_id}, topic={topic}, difficulty={difficulty}"
    )
    return new_qa_id


# ── 原有同步评估（降级用）───────────────────────────────────────────────────────

def evaluate_single_qa_sync(
    history_id: int,
    answer_qa_id: int,
    question_content: str,
    answer_content: str,
) -> None:
    """
    同步版本的单题评估，用于 RabbitMQ 不可用时的 BackgroundTask 降级。
    在线程池中运行，不阻塞事件循环。
    """
    async def _run():
        prompt = _build_single_eval_prompt(question_content, answer_content)
        try:
            raw = await call_qwen_api(prompt, max_tokens=1024, temperature=0.5)
            eval_result = _parse_with_repair(raw, history_id)
        except Exception as e:
            logger.error(f"降级评估 Qwen 调用失败: {e}")
            eval_result = {
                "evaluation": "评估失败",
                "feedback": "请重新尝试",
                "reference_a": "",
                "skill": "",
                "category": "",
                "answer_rating": None,
            }
        try:
            execute_update(
                """UPDATE qa SET evaluation=%s, feedback=%s, reference_a=%s,
                                  skill=%s, category=%s, answer_rating=%s
                   WHERE qa_id=%s""",
                (
                    eval_result.get("evaluation"),
                    eval_result.get("feedback"),
                    eval_result.get("reference_a", ""),
                    eval_result.get("skill", ""),
                    eval_result.get("category", ""),
                    eval_result.get("answer_rating"),
                    answer_qa_id,
                ),
            )
            logger.info(f"降级评估已写库: answer_qa_id={answer_qa_id}")
        except Exception as e:
            logger.error(f"降级评估写库失败: {e}")

    asyncio.run(_run())


# ── 主流程：异步流式生成 ──────────────────────────────────────────────────────

async def process_answer_stream(
    background_tasks: BackgroundTasks,
    history_id: int,
    question_qa_id: int,
    answer_content: Optional[str],
) -> AsyncGenerator[str, None]:
    """
    核心流程编排器，yield SSE 格式字符串。

    SSE 事件顺序：
      event: metadata  → {"action": ..., "current_topic": ...}
      event: token     → {"content": "<token>"}  （多次）
      event: done      → {"question_qa_id": ..., "action": ..., "current_topic": ...}
      event: error     → {"message": "..."}  （异常时）
    """

    def _sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    try:
        # ── Step 1：并发执行「获取问题+会话状态」与「保存/查找回答」────────────
        if answer_content:
            (question_content, stored_topic, session), answer_qa_id = await asyncio.gather(
                asyncio.to_thread(_get_question_and_session, history_id, question_qa_id),
                asyncio.to_thread(_save_text_answer, history_id, question_qa_id, answer_content),
            )
        else:
            (question_content, stored_topic, session), (answer_qa_id, answer_content) = (
                await asyncio.gather(
                    asyncio.to_thread(_get_question_and_session, history_id, question_qa_id),
                    asyncio.to_thread(_get_voice_answer, history_id, question_qa_id),
                )
            )

        # ── Step 2：解析会话状态 ─────────────────────────────────────────────
        current_topic = session["current_topic"] or stored_topic or session["position"]
        follow_up_count = session["follow_up_count"] or 0
        total_asked = session["total_questions_asked"] or 1
        career_domain = session["field"]
        job_role = session["position"]
        force_switch = follow_up_count >= MAX_FOLLOW_UP

        # ── Step 3：投递评估任务到 RabbitMQ（fire & forget）─────────────────
        logger.info(f"开始投递评估任务到 RabbitMQ: answer_qa_id={answer_qa_id}, history_id={history_id}")
        mq_ok = await publish_evaluation_job(
            history_id, answer_qa_id, question_content, answer_content
        )
        if not mq_ok:
            # 降级：进程内后台任务
            logger.warning(f"RabbitMQ 投递失败，降级到 BackgroundTask: answer_qa_id={answer_qa_id}")
            background_tasks.add_task(
                evaluate_single_qa_sync,
                history_id,
                answer_qa_id,
                question_content,
                answer_content,
            )
        else:
            logger.info(f"评估任务已投递 RabbitMQ: answer_qa_id={answer_qa_id}")

        # ── Step 4：强制检查总题数上限 ───────────────────────────────────────
        if total_asked >= MAX_TOTAL_QUESTIONS:
            logger.info(f"已达总题数上限({MAX_TOTAL_QUESTIONS})，强制结束: history_id={history_id}")
            yield _sse("metadata", {"action": "end", "current_topic": current_topic})
            yield _sse("done", {
                "action": "end",
                "next_question": None,
                "question_qa_id": None,
                "current_topic": current_topic,
            })
            return

        # ── Step 5：获取近期上下文 + 调用 Qwen 决策（非流式，快速）───────────
        recent_context = await asyncio.to_thread(get_recent_context, history_id, CONTEXT_WINDOW)

        action_prompt = _build_action_decision_prompt(
            career_domain, job_role, current_topic,
            follow_up_count, total_asked, recent_context, answer_content,
        )
        raw_action = await call_qwen_api(action_prompt, max_tokens=256, temperature=0.3)
        action_result = _parse_action_decision(raw_action)

        action = action_result.get("action", "next_topic")
        next_topic = action_result.get("topic") or current_topic
        difficulty = action_result.get("difficulty") or "中等"

        # ── Step 6：强制规则覆盖 ─────────────────────────────────────────────
        if force_switch and action == "follow_up":
            action = "next_topic"
            logger.info(f"已达追问上限({MAX_FOLLOW_UP})，强制切换话题: history_id={history_id}")

        # ── Step 7：结束分支 ─────────────────────────────────────────────────
        if action == "end":
            yield _sse("metadata", {"action": "end", "current_topic": current_topic})
            yield _sse("done", {
                "action": "end",
                "next_question": None,
                "question_qa_id": None,
                "current_topic": current_topic,
            })
            return

        # ── Step 8：流式生成问题，同时收集完整文本 ────────────────────────────
        yield _sse("metadata", {"action": action, "current_topic": next_topic})

        question_gen_prompt = _build_question_generation_prompt(
            action, next_topic, difficulty, career_domain, job_role, recent_context
        )

        full_question_parts: list[str] = []
        try:
            async for token in call_qwen_api_stream(question_gen_prompt):
                full_question_parts.append(token)
                yield _sse("token", {"content": token})
        except Exception as e:
            logger.error(f"问题流式生成失败: history_id={history_id}, error={e}")
            yield _sse("error", {"message": f"问题生成失败: {str(e)}"})
            return

        full_question = "".join(full_question_parts).strip()

        # ── Step 9：流结束后写库（更新会话状态 + 保存新题目）────────────────
        insert_event = asyncio.Event()
        new_qa_id_holder: dict = {}

        async def _persist():
            try:
                await asyncio.gather(
                    asyncio.to_thread(_update_session_state, history_id, action, next_topic),
                    asyncio.to_thread(
                        lambda: new_qa_id_holder.__setitem__(
                            "id",
                            _insert_next_question(history_id, full_question, difficulty, next_topic),
                        )
                    ),
                )
            except Exception as e:
                logger.error(f"流结束后写库失败: history_id={history_id}, error={e}")
                new_qa_id_holder["id"] = None
            finally:
                insert_event.set()

        asyncio.create_task(_persist())
        # 等待写库完成（通常 < 50ms），以便 done 事件携带真实 qa_id
        await insert_event.wait()

        logger.info(
            f"process_answer_stream 完成: history_id={history_id}, action={action}, "
            f"new_qa_id={new_qa_id_holder.get('id')}, total_asked={total_asked}"
        )

        yield _sse("done", {
            "action": action,
            "next_question": full_question,
            "question_qa_id": new_qa_id_holder.get("id"),
            "current_topic": next_topic,
        })

    except ValueError as e:
        logger.warning(f"process_answer_stream 参数错误: {e}")
        yield _sse("error", {"message": str(e)})
    except Exception as e:
        logger.error(f"process_answer_stream 未知异常: history_id={history_id}, error={e}")
        yield _sse("error", {"message": f"服务内部错误: {str(e)}"})


# ── JSON 解析辅助 ─────────────────────────────────────────────────────────────

def _parse_action_decision(raw: str) -> dict:
    """解析 action 决策 JSON，容错处理。"""
    cleaned = raw.strip()
    for prefix in ("```json", "```"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end > start:
        cleaned = cleaned[start: end + 1]

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"action 决策 JSON 解析失败: {e}, 原始: {raw[:200]}")
        return {"action": "next_topic", "topic": None, "difficulty": "中等"}


# ── 保留原有接口（供旧端点 /answer 继续使用）────────────────────────────────

async def process_answer(
    history_id: int,
    question_qa_id: int,
    answer_content: Optional[str] = None,
) -> dict:
    """
    原有接口升级为 async，旧端点 POST /interview/answer 用 await 调用。
    保留全部同步语义（等待评估完成再返回），仅将 LLM 替换为 Qwen。
    新端点 POST /interview/answer/stream 使用 process_answer_stream。
    """
    # 获取问题和会话状态
    if answer_content:
        (question_content, stored_topic, session), answer_qa_id = await asyncio.gather(
            asyncio.to_thread(_get_question_and_session, history_id, question_qa_id),
            asyncio.to_thread(_save_text_answer, history_id, question_qa_id, answer_content),
        )
    else:
        (question_content, stored_topic, session), (answer_qa_id, answer_content) = (
            await asyncio.gather(
                asyncio.to_thread(_get_question_and_session, history_id, question_qa_id),
                asyncio.to_thread(_get_voice_answer, history_id, question_qa_id),
            )
        )

    current_topic = session["current_topic"] or stored_topic or session["position"]
    follow_up_count = session["follow_up_count"] or 0
    total_asked = session["total_questions_asked"] or 1
    career_domain = session["field"]
    job_role = session["position"]
    force_switch = follow_up_count >= MAX_FOLLOW_UP

    # 评估（串行，等待结果以便返回给前端）
    eval_prompt = _build_single_eval_prompt(question_content, answer_content)
    try:
        raw_eval = await call_qwen_api(eval_prompt, max_tokens=1024, temperature=0.5)
        eval_result = _parse_with_repair(raw_eval, history_id)
    except Exception as e:
        logger.error(f"评估 Qwen 调用失败: {e}")
        eval_result = {
            "evaluation": "评估失败", "feedback": "", "reference_a": "",
            "skill": "", "category": "", "answer_rating": None,
        }

    await asyncio.to_thread(
        execute_update,
        """UPDATE qa SET evaluation=%s, feedback=%s, reference_a=%s,
                         skill=%s, category=%s, answer_rating=%s
           WHERE qa_id=%s""",
        (eval_result.get("evaluation"), eval_result.get("feedback"),
         eval_result.get("reference_a", ""), eval_result.get("skill", ""),
         eval_result.get("category", ""), eval_result.get("answer_rating"),
         answer_qa_id),
    )

    if total_asked >= MAX_TOTAL_QUESTIONS:
        return {
            "action": "end", "next_question": None, "question_qa_id": None,
            "current_topic": current_topic, "evaluation": eval_result,
        }

    recent_context = await asyncio.to_thread(get_recent_context, history_id, CONTEXT_WINDOW)
    action_prompt = _build_action_decision_prompt(
        career_domain, job_role, current_topic,
        follow_up_count, total_asked, recent_context, answer_content,
    )
    raw_action = await call_qwen_api(action_prompt, max_tokens=256, temperature=0.3)
    action_result = _parse_action_decision(raw_action)

    action = action_result.get("action", "next_topic")
    next_topic = action_result.get("topic") or current_topic
    difficulty = action_result.get("difficulty") or "中等"

    if force_switch and action == "follow_up":
        action = "next_topic"

    if action == "end":
        return {
            "action": "end", "next_question": None, "question_qa_id": None,
            "current_topic": current_topic, "evaluation": eval_result,
        }

    question_gen_prompt = _build_question_generation_prompt(
        action, next_topic, difficulty, career_domain, job_role, recent_context
    )
    next_question = (
        await call_qwen_api(question_gen_prompt, max_tokens=512, temperature=0.8)
    ).strip()

    await asyncio.to_thread(_update_session_state, history_id, action, next_topic)
    new_qa_id = await asyncio.to_thread(
        _insert_next_question, history_id, next_question, difficulty, next_topic
    )

    return {
        "action": action,
        "next_question": next_question,
        "question_qa_id": new_qa_id,
        "current_topic": next_topic,
        "evaluation": eval_result,
    }
