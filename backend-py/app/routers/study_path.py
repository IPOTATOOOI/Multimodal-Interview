"""
学习路径 API：基于用户画像 + Neo4j Tag/Topic 图遍历，通过 SSE 流式输出个性化学习计划。
不依赖社区检测（graph_operations 的 community 特性），直接使用 WEAK_AT → Tag → Question → Topic 路径。
"""
from __future__ import annotations

import json
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from loguru import logger

from app.services.user_portrait.portrait_service import build_user_portrait
from app.graphRAG_enhanced.graph_operations import Neo4jGraphOperations
from app.services.AI.qwen_api import call_qwen_api_stream

router = APIRouter(prefix="/api/study-path", tags=["study-path"])


class StudyPathRequest(BaseModel):
    user_id: int
    topic_hint: str = ""


def _build_study_path_prompt(
    weak_tag_names: list[str],
    topic_names: list[str],
    weakest_dim_label: str,
    topic_hint: str,
) -> str:
    tags_str = "、".join(weak_tag_names[:6]) if weak_tag_names else "未检测到薄弱标签"
    topics_str = "、".join(topic_names[:6]) if topic_names else "综合知识点"
    hint_line = f"\n用户指定方向：{topic_hint}" if topic_hint.strip() else ""
    return f"""你是专业的面试辅导专家。请为以下候选人生成个性化学习提升计划。

薄弱技能标签：{tags_str}
最薄弱面试维度：{weakest_dim_label}{hint_line}
相关知识主题：{topics_str}

要求：
1. 针对3-5个薄弱标签，每个给出：核心概念要点（1-2条）和推荐练习方向
2. 最后汇总一个1周学习时间表（每天约2小时）
3. 使用 markdown 格式，层级清晰，总字数控制在500字以内
4. 末尾一句鼓励性总结

直接输出计划，不要前置解释。"""


@router.post("/generate")
async def generate_study_path(request: StudyPathRequest):
    """
    SSE 流式输出个性化学习计划。
    事件格式：
      event: metadata   data: {"weak_tags": [...], "focus_label": "..."}
      event: token      data: {"content": "<token>"}
      event: questions  data: {"items": [...]}
      event: done       data: {}
    """
    async def event_generator():
        try:
            # 1. 构建用户画像
            portrait = await build_user_portrait(request.user_id)
            rec = portrait.get("recommendation_profile", {})
            priority_tag_ids: list[str] = rec.get("priority_tag_ids", [])
            focus_label: str = rec.get("study_focus_label", "综合能力提升")
            weak_tags: list[dict] = portrait.get("graph_data", {}).get("weak_area_tags", [])
            weakest_dim_label: str = (
                portrait.get("interview_performance", {}).get("weakest_dimension_label")
                or "专业知识"
            )

            weak_tag_names = [t["tag_name"] for t in weak_tags[:6] if t.get("tag_name")]
            meta = {
                "weak_tags": [{"id": t.get("tag_id"), "name": t.get("tag_name"), "strength": t.get("strength")} for t in weak_tags[:6]],
                "focus_label": focus_label,
            }
            yield f"event: metadata\ndata: {json.dumps(meta, ensure_ascii=False)}\n\n"

            # 2. 从 Neo4j 按薄弱 Tag 查询题目和关联 Topic
            graph_ops = Neo4jGraphOperations()
            questions: list[dict] = []
            topic_names: list[str] = []
            if priority_tag_ids:
                raw = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: graph_ops.get_questions_by_tags_and_topics(
                        tag_ids=priority_tag_ids[:10], limit=15
                    ),
                )
                questions = raw
                topic_names = list({q.get("topic_name") for q in raw if q.get("topic_name")})

            # 3. 流式输出 Qwen 学习计划
            prompt = _build_study_path_prompt(
                weak_tag_names, topic_names, weakest_dim_label, request.topic_hint
            )
            async for token in call_qwen_api_stream(prompt, max_tokens=1024, temperature=0.7):
                yield f"event: token\ndata: {json.dumps({'content': token}, ensure_ascii=False)}\n\n"

            # 4. 输出推荐练习题
            q_items = [
                {
                    "id": q.get("id"),
                    "title": q.get("title"),
                    "difficulty": q.get("difficulty"),
                    "type": q.get("type"),
                    "topic_name": q.get("topic_name"),
                    "sub_category": q.get("sub_category"),
                    "matched_tags": q.get("matched_tags", []),
                }
                for q in questions
            ]
            yield f"event: questions\ndata: {json.dumps({'items': q_items}, ensure_ascii=False)}\n\n"
            yield "event: done\ndata: {}\n\n"

        except Exception as e:
            logger.error(f"generate_study_path 失败 user={request.user_id}: {e}")
            yield f"event: error\ndata: {json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
