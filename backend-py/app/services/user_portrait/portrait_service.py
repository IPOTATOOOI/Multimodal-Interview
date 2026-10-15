"""
用户画像服务：聚合 MySQL 面试记录 + Neo4j 图数据，构建结构化用户画像。
画像数据用于个性化推荐和学习路径生成。
"""
from __future__ import annotations

import asyncio
from loguru import logger

from app.database.mysql import execute_query
from app.database.neo4j import graph
from app.services.AI.qwen_api import call_qwen_api

_DIMENSION_KEYS = [
    "professional_knowledge",
    "skill_match",
    "language_expression",
    "logical_thinking",
    "innovation_ability",
    "stress_resistance",
]
_DIMENSION_LABELS = {
    "professional_knowledge": "专业知识",
    "skill_match": "技能匹配",
    "language_expression": "语言表达",
    "logical_thinking": "逻辑思维",
    "innovation_ability": "创新能力",
    "stress_resistance": "抗压能力",
}


async def build_user_portrait(user_id: int) -> dict:
    """
    构建用户画像，聚合三个来源：
    ① MySQL user 表（基本信息）
    ② MySQL interview_history + written_test（面试表现 + 笔试 Tag 正确率）
    ③ Neo4j WEAK_AT + INTERACTS（图谱薄弱点 + 答题统计）
    最后用 Qwen 生成 study_focus_label（4-8 字学习主题名）。
    """
    # 并发执行 MySQL 和 Neo4j 查询
    basic_info, interview_perf, written_stats, graph_data = await asyncio.gather(
        _fetch_basic_info(user_id),
        _fetch_interview_performance(user_id),
        _fetch_written_test_stats(user_id),
        _fetch_graph_data(user_id),
    )

    # 计算推荐配置（priority_tag_ids 先于 LLM 调用，因为 focus_label 需要它）
    priority_tag_ids = _compute_priority_tags(graph_data["weak_area_tags"], written_stats)

    # 并发调用两个 Qwen 生成任务
    study_focus_label, weakness_analysis = await asyncio.gather(
        _generate_focus_label(graph_data["weak_area_tags"], interview_perf),
        _generate_weakness_analysis(interview_perf, graph_data["weak_area_tags"], written_stats),
    )

    return {
        "user_id": user_id,
        "basic_info": basic_info,
        "interview_performance": interview_perf,
        "written_test_stats": written_stats,
        "graph_data": graph_data,
        "recommendation_profile": {
            "priority_tag_ids": priority_tag_ids[:10],
            "study_focus_label": study_focus_label,
            "weakness_analysis": weakness_analysis,
        },
    }


# ──────────────── 私有查询函数 ────────────────

async def _fetch_basic_info(user_id: int) -> dict:
    try:
        rows = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: execute_query(
                "SELECT name, gender, age, university, major FROM user WHERE user_id = %s LIMIT 1",
                (user_id,),
            ),
        )
        if rows:
            row = rows[0]
            gender_map = {1: "男", 2: "女", 0: "未知"}
            return {
                "name": row.get("name") or "",
                "gender": gender_map.get(row.get("gender", 0), "未知"),
                "age": row.get("age"),
                "university": row.get("university") or "",
                "major": row.get("major") or "",
            }
    except Exception as e:
        logger.error(f"_fetch_basic_info user={user_id}: {e}")
    return {}


async def _fetch_interview_performance(user_id: int) -> dict:
    try:
        rows = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: execute_query(
                """
                SELECT history_id, score, field, position,
                       professional_knowledge, skill_match, language_expression,
                       logical_thinking, innovation_ability, stress_resistance,
                       interview_time
                FROM interview_history
                WHERE user_id = %s
                ORDER BY interview_time ASC
                """,
                (user_id,),
            ),
        )
        if not rows:
            return {"total_interviews": 0}

        total = len(rows)
        avg_scores = {}
        for key in _DIMENSION_KEYS:
            vals = [r[key] for r in rows if r.get(key) is not None]
            avg_scores[f"avg_{key}"] = round(sum(vals) / len(vals), 2) if vals else None

        # 找最弱维度
        weakest = min(
            _DIMENSION_KEYS,
            key=lambda k: avg_scores.get(f"avg_{k}") or 999,
        )

        # 近期趋势（最多取5次）
        trend = [
            {"history_id": r["history_id"], "score": r.get("score"),
             "date": str(r.get("interview_time", ""))[:10]}
            for r in rows[-5:]
        ]

        return {
            "total_interviews": total,
            **avg_scores,
            "weakest_dimension": weakest,
            "weakest_dimension_label": _DIMENSION_LABELS.get(weakest, weakest),
            "score_trend": trend,
        }
    except Exception as e:
        logger.error(f"_fetch_interview_performance user={user_id}: {e}")
        return {"total_interviews": 0}


async def _fetch_written_test_stats(user_id: int) -> dict:
    try:
        rows = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: execute_query(
                """
                SELECT wt.tag_name,
                       COUNT(*) AS cnt,
                       SUM(CASE WHEN wt.question_score > 0 THEN 1 ELSE 0 END) AS ok_cnt
                FROM written_test wt
                JOIN interview_history ih ON wt.history_id = ih.history_id
                WHERE ih.user_id = %s AND wt.tag_name IS NOT NULL
                GROUP BY wt.tag_name
                ORDER BY (SUM(CASE WHEN wt.question_score > 0 THEN 1 ELSE 0 END) / COUNT(*)) ASC
                """,
                (user_id,),
            ),
        )
        by_tag = {}
        for row in (rows or []):
            tag = row["tag_name"]
            cnt = row["cnt"] or 1
            ok = row["ok_cnt"] or 0
            by_tag[tag] = {
                "cnt": cnt,
                "ok_cnt": ok,
                "correct_rate": round(ok / cnt, 2),
            }
        return {"by_tag": by_tag}
    except Exception as e:
        logger.error(f"_fetch_written_test_stats user={user_id}: {e}")
        return {"by_tag": {}}


async def _fetch_graph_data(user_id: int) -> dict:
    try:
        def _query():
            if graph is None:
                return [], 0, 0.0
            weak = graph.run("""
                MATCH (u:User {id: $uid})-[r:WEAK_AT]->(t:Tag)
                RETURN t.id AS tag_id, t.name AS tag_name,
                       coalesce(r.strength, 1.0) AS strength
                ORDER BY strength DESC
            """, uid=user_id).data()

            interact = graph.run("""
                MATCH (u:User {id: $uid})-[r:INTERACTS]->(q:Question)
                RETURN count(q) AS total,
                       avg(coalesce(r.correctness, 0)) AS correct_rate
            """, uid=user_id).data()

            total_q = interact[0]["total"] if interact else 0
            correct_rate = round(interact[0]["correct_rate"] or 0.0, 2) if interact else 0.0
            return weak, total_q, correct_rate

        weak_tags, total_q, correct_rate = await asyncio.get_event_loop().run_in_executor(
            None, _query
        )
        return {
            "weak_area_tags": weak_tags,
            "interacted_question_count": total_q,
            "correct_rate": correct_rate,
        }
    except Exception as e:
        logger.error(f"_fetch_graph_data user={user_id}: {e}")
        return {"weak_area_tags": [], "interacted_question_count": 0, "correct_rate": 0.0}


def _compute_priority_tags(weak_area_tags: list, written_stats: dict) -> list:
    """
    综合 Neo4j WEAK_AT strength 和笔试错误率，给出优先练习的 tag_id 列表。
    """
    # 从 Neo4j WEAK_AT 拿 tag_id（已按 strength 降序）
    priority = [t["tag_id"] for t in weak_area_tags if t.get("tag_id")]

    # 补充笔试失败率高的 tag（按 correct_rate 升序）
    written_weak = sorted(
        [(tag, info["correct_rate"]) for tag, info in written_stats.get("by_tag", {}).items()],
        key=lambda x: x[0],
    )
    for tag_name, _ in written_weak:
        if tag_name not in priority:
            priority.append(tag_name)

    return priority


async def _generate_focus_label(weak_area_tags: list, interview_perf: dict) -> str:
    """用 Qwen 生成 4-8 字的学习主题标签，失败时返回默认值"""
    try:
        top_names = [t["tag_name"] for t in weak_area_tags[:5] if t.get("tag_name")]
        weakest_label = interview_perf.get("weakest_dimension_label", "")
        if not top_names and not weakest_label:
            return "综合能力提升"
        hint = "、".join(top_names) if top_names else weakest_label
        label = await call_qwen_api(
            f"用4-8个汉字总结以下技术标签或能力的核心学习主题：{hint}。只输出主题名，不加任何解释和标点。",
            max_tokens=20,
            temperature=0.1,
        )
        return label.strip()[:16] or "综合能力提升"
    except Exception as e:
        logger.warning(f"_generate_focus_label 失败: {e}")
        return "综合能力提升"


async def _generate_weakness_analysis(
    interview_perf: dict,
    weak_tags: list,
    written_stats: dict,
) -> str:
    """用 Qwen 生成个性化薄弱点分析文字（80-120字），无面试记录时返回空字符串"""
    try:
        total = interview_perf.get("total_interviews", 0)
        if total == 0:
            return ""

        weakest_label = interview_perf.get("weakest_dimension_label", "")
        weakest_key = interview_perf.get("weakest_dimension", "")
        weakest_score = interview_perf.get(f"avg_{weakest_key}") if weakest_key else None

        top_tags = [t["tag_name"] for t in weak_tags[:3] if t.get("tag_name")]

        # 笔试失败率最高的 tag（correct_rate 最低）
        failed_test_tags = sorted(
            [(k, v["correct_rate"]) for k, v in written_stats.get("by_tag", {}).items()],
            key=lambda x: x[1],
        )[:2]
        failed_str = (
            "、".join(f"{k}（{int(v * 100)}%正确率）" for k, v in failed_test_tags)
            if failed_test_tags else "暂无笔试数据"
        )

        prompt = f"""你是专业面试辅导专家。根据以下候选人面试数据，生成一段个性化薄弱点分析（80-120字）。

面试次数：{total}次
最弱面试维度：{weakest_label}（{f"{weakest_score:.1f}/5" if weakest_score else "N/A"}）
长期薄弱技术标签：{"、".join(top_tags) if top_tags else "暂无数据"}
笔试最差表现：{failed_str}

要求：
1. 结合维度和技术标签，指出最需要提升的具体方向
2. 语气鼓励，内容具体而非泛泛
3. 直接输出分析文本，不加任何标题、符号或格式"""

        result = await call_qwen_api(prompt, max_tokens=200, temperature=0.5)
        return result.strip()
    except Exception as e:
        logger.warning(f"_generate_weakness_analysis 失败: {e}")
        return ""