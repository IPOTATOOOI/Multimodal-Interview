from typing import Any, Dict, List, Optional
import logging
import re

from fastapi import APIRouter, HTTPException
from neo4j import GraphDatabase
from pydantic import BaseModel, Field

from app.core.config import settings

router = APIRouter(prefix="/graph-rag-keyword", tags=["GraphRAG Keyword"])
logger = logging.getLogger("graph_rag_keyword")

ALLOWED_LABELS = ["RootCategory", "SubCategory", "Topic", "Question", "Tag", "User"]


class KeywordGraphQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题或关键词")
    keywords: Optional[List[str]] = Field(None, description="可选关键词；不传则从 question 中自动切分")
    user_id: Optional[int] = Field(None, description="用户 ID，用于普通用户权限过滤")
    is_admin: bool = Field(False, description="管理员可查询全部节点")
    limit: int = Field(8, ge=1, le=30, description="最多匹配多少个中心节点")
    neighbor_limit: int = Field(80, ge=1, le=200, description="最多返回多少条邻居关系")


class KeywordGraphQueryResponse(BaseModel):
    question: str
    keywords: List[str]
    matched_nodes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    context: str


def _debug(message: str) -> None:
    text = f"[GraphRAGKeyword] {message}"
    print(text, flush=True)
    logger.info(text)


def _append_keyword(keywords: List[str], seen: set, value: str) -> None:
    keyword = str(value or "").strip().lower()
    stop_words = {
        "什么", "怎么", "如何", "为什么", "请问", "介绍", "一下", "这个", "那个", "哪些", "以及",
        "给我", "一些", "入门", "题目", "问题", "学习", "想学习", "我想", "我想学习",
        "the", "and", "for", "with", "what", "how", "why", "is", "are",
    }
    if not keyword or keyword in stop_words or keyword in seen:
        return
    if len(keyword) < 2:
        return
    seen.add(keyword)
    keywords.append(keyword)


def _extract_keywords(question: str, provided: Optional[List[str]] = None) -> List[str]:
    keywords: List[str] = []
    seen = set()

    if provided:
        for item in provided:
            _append_keyword(keywords, seen, item)
        return keywords[:30]

    text = str(question or "")
    raw_tokens = re.findall(r"[A-Za-z0-9_+#.]{2,}|[\u4e00-\u9fa5]{2,}", text)
    for token in raw_tokens:
        _append_keyword(keywords, seen, token)

    # 中文没有天然空格，用户问“我想学习数据结构”时，整句会成为一个 token。
    # 这里生成 2-8 字的连续片段，让“数据结构”这类 Topic 能被命中。
    chinese_spans = re.findall(r"[\u4e00-\u9fa5]{2,}", text)
    for span in chinese_spans:
        max_len = min(8, len(span))
        for size in range(max_len, 1, -1):
            for start in range(0, len(span) - size + 1):
                _append_keyword(keywords, seen, span[start:start + size])
                if len(keywords) >= 30:
                    return keywords

    return keywords[:30]


def _node_to_dict(node, matched_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
    props = dict(node.items())
    labels = list(node.labels)
    return {
        "neo4j_id": node.id,
        "id": str(props.get("id", node.id)),
        "name": props.get("name") or props.get("title") or str(props.get("id", node.id)),
        "type": labels[0] if labels else "Unknown",
        "labels": labels,
        "matched_keywords": matched_keywords or [],
        "properties": props,
    }


def _relationship_to_dict(center, relationship, neighbor) -> Dict[str, Any]:
    return {
        "source": str(center.get("id", center.id)),
        "source_name": center.get("name") or center.get("title") or str(center.get("id", center.id)),
        "target": str(neighbor.get("id", neighbor.id)),
        "target_name": neighbor.get("name") or neighbor.get("title") or str(neighbor.get("id", neighbor.id)),
        "type": relationship.type,
        "properties": dict(relationship.items()),
        "neighbor": _node_to_dict(neighbor),
    }


def _build_context(matched_nodes: List[Dict[str, Any]], relationships: List[Dict[str, Any]]) -> str:
    if not matched_nodes:
        return "未在知识图谱中检索到包含关键词的节点。"

    lines = ["知识图谱关键词检索结果："]
    for index, node in enumerate(matched_nodes, start=1):
        props = node.get("properties", {})
        content = props.get("content") or props.get("description") or props.get("title") or props.get("name") or ""
        matched = "、".join(node.get("matched_keywords") or [])
        matched_text = f"，命中关键词：{matched}" if matched else ""
        lines.append(
            f"{index}. 节点：{node.get('name')}，类型：{node.get('type')}{matched_text}，内容：{str(content)[:180]}"
        )

    if relationships:
        lines.append("相关邻居与关系：")
        for rel in relationships[:30]:
            lines.append(
                f"- {rel.get('source_name')} --[{rel.get('type')}]-- {rel.get('target_name')}"
            )
    return "\n".join(lines)


@router.post("/query", response_model=KeywordGraphQueryResponse)
async def keyword_graph_query(request: KeywordGraphQueryRequest):
    keywords = _extract_keywords(request.question, request.keywords)
    _debug(f"收到问题: {request.question}")
    _debug(f"提取关键词({len(keywords)}): {keywords}")

    if not keywords:
        _debug("未提取到有效关键词，直接返回空结果")
        return KeywordGraphQueryResponse(
            question=request.question,
            keywords=[],
            matched_nodes=[],
            relationships=[],
            context="未能从问题中提取有效关键词。",
        )

    driver = None
    try:
        _debug(f"连接 Neo4j: {settings.NEO4J_URI}")
        driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
        driver.verify_connectivity()

        user_filter = ""
        params: Dict[str, Any] = {
            "keywords": keywords,
            "allowed_labels": ALLOWED_LABELS,
            "limit": request.limit,
            "neighbor_limit": request.neighbor_limit,
        }
        if not request.is_admin and request.user_id is not None:
            user_filter = "AND (n.user_id = $user_id OR n.user_id = 0 OR n.user_id IS NULL)"
            params["user_id"] = request.user_id

        node_query = f"""
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label IN $allowed_labels)
        {user_filter}
        WITH n, [keyword IN $keywords WHERE
            toLower(coalesce(toString(n.name), '')) CONTAINS keyword OR
            toLower(coalesce(toString(n.title), '')) CONTAINS keyword OR
            toLower(coalesce(toString(n.content), '')) CONTAINS keyword OR
            toLower(coalesce(toString(n.id), '')) CONTAINS keyword OR
            toLower(coalesce(toString(n.description), '')) CONTAINS keyword OR
            (size(coalesce(toString(n.name), '')) >= 2 AND keyword CONTAINS toLower(coalesce(toString(n.name), ''))) OR
            (size(coalesce(toString(n.title), '')) >= 2 AND keyword CONTAINS toLower(coalesce(toString(n.title), '')))
        ] AS matched_keywords
        WHERE size(matched_keywords) > 0
        RETURN n, matched_keywords
        ORDER BY size(matched_keywords) DESC
        LIMIT $limit
        """

        neighbor_user_filter = ""
        if not request.is_admin and request.user_id is not None:
            neighbor_user_filter = "AND (m.user_id = $user_id OR m.user_id = 0 OR m.user_id IS NULL)"

        relationship_query = f"""
        MATCH (n)-[r]-(m)
        WHERE id(n) IN $node_ids
        AND any(label IN labels(m) WHERE label IN $allowed_labels)
        {neighbor_user_filter}
        RETURN n, r, m
        LIMIT $neighbor_limit
        """

        with driver.session() as session:
            node_records = list(session.run(node_query, **params))
            matched_nodes = [
                _node_to_dict(record["n"], record.get("matched_keywords", []))
                for record in node_records
            ]
            node_ids = [record["n"].id for record in node_records]

            _debug(f"命中中心节点数: {len(matched_nodes)}")
            for node in matched_nodes[:5]:
                _debug(
                    f"命中节点: name={node.get('name')}, type={node.get('type')}, "
                    f"keywords={node.get('matched_keywords')}"
                )

            relationships = []
            if node_ids:
                rel_params = {
                    "node_ids": node_ids,
                    "allowed_labels": ALLOWED_LABELS,
                    "neighbor_limit": request.neighbor_limit,
                }
                if not request.is_admin and request.user_id is not None:
                    rel_params["user_id"] = request.user_id
                rel_records = session.run(relationship_query, **rel_params)
                for record in rel_records:
                    relationships.append(_relationship_to_dict(record["n"], record["r"], record["m"]))

            _debug(f"返回邻居关系数: {len(relationships)}")

        return KeywordGraphQueryResponse(
            question=request.question,
            keywords=keywords,
            matched_nodes=matched_nodes,
            relationships=relationships,
            context=_build_context(matched_nodes, relationships),
        )
    except Exception as exc:
        _debug(f"关键词图谱检索失败: {exc}")
        raise HTTPException(status_code=500, detail=f"关键词图谱检索失败: {exc}")
    finally:
        if driver:
            driver.close()
