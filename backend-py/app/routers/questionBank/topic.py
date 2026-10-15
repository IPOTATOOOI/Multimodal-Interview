from fastapi import APIRouter, Query, HTTPException
from typing import List
from py2neo import NodeMatcher
from app.database.neo4j import graph
from loguru import logger

router = APIRouter(prefix="/questionBank", tags=["questionBank"])

@router.get("/topics")
async def get_topics(
    root_category_name: str = Query(..., description="根分类名称"),
    sub_category_name: str = Query(..., description="二级分类名称")
):
    """
    根据RootCategory和SubCategory的name查询其下所有Topic，返回Topic的id、name和题目数量
    """
    try:
        if graph is None:
            logger.error("Neo4j数据库未连接")
            raise HTTPException(status_code=500, detail="Neo4j数据库未连接")
            
        matcher = NodeMatcher(graph)
        # 校验RootCategory和SubCategory是否存在
        root = matcher.match("RootCategory", name=root_category_name).first()
        if not root:
            raise HTTPException(status_code=404, detail="RootCategory不存在")
        sub = matcher.match("SubCategory", name=sub_category_name).first()
        if not sub:
            raise HTTPException(status_code=404, detail="SubCategory不存在")
        # 查询SubCategory下所有Topic及题目数量
        query = (
            "MATCH (r:RootCategory {name: $root_name})-[:HAS_SUB]->(s:SubCategory {name: $sub_name})-[:CONTAINS_TOPIC]->(t:Topic) "
            "OPTIONAL MATCH (t)-[:INCLUDES]->(q:Question) "
            "WITH t, count(q) AS question_count "
            "RETURN t.id AS id, t.name AS name, question_count ORDER BY t.name ASC"
        )
        result = graph.run(query, root_name=root_category_name, sub_name=sub_category_name).data()
        topics = [{"id": row["id"], "name": row["name"], "question_count": row["question_count"]} for row in result]
        return {"topics": topics}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询Topic失败: {str(e)}")

@router.get("/questions")
async def get_questions_by_topic(
    topic_id: str = Query(..., description="主题ID")
):
    """
    根据Topic的id随机查询15道Question，返回每道题的详细信息（含Tag和KnowledgePoint）
    """
    try:
        if graph is None:
            logger.error("Neo4j数据库未连接")
            raise HTTPException(status_code=500, detail="Neo4j数据库未连接")
            
        # Cypher: 随机15题，带Tag和KnowledgePoint，只取前5个标签
        query = (
            "MATCH (t:Topic {id: $topic_id})-[:INCLUDES]->(q:Question) "
            "OPTIONAL MATCH (q)-[:MARKED_AS]->(tag:Tag) "
            "OPTIONAL MATCH (q)-[:TESTS]->(kp:KnowledgePoint) "
            "WITH q, collect(DISTINCT tag) AS allTags, collect(DISTINCT kp) AS kps "
            "WITH q, allTags[0..5] AS tags, kps "
            "WITH q, tags, kps ORDER BY rand() LIMIT 15 "
            "RETURN "
            "  q.id            AS id, "
            "  q.title         AS title, "
            "  q.content       AS content, "
            "  q.choice        AS choice, "
            "  q.type          AS type, "
            "  q.difficulty    AS difficulty, "
            "  q.answer        AS answer, "
            "  [tag IN tags | {id: tag.id, name: tag.name}]                    AS tags, "
            "  [kp  IN kps  | {id: kp.id,   name: kp.name, level: kp.level}] AS knowledge_points"
        )
        result = graph.run(query, topic_id=topic_id).data()
        questions = [{
            "id": row["id"],
            "title": row["title"],
            "content": row["content"],
            "choice": row["choice"],
            "type": row["type"],
            "difficulty": row["difficulty"],
            "answer": row["answer"],
            "tags": row["tags"],
            "knowledge_points": row["knowledge_points"]
        } for row in result]
        return {"questions": questions}

    except Exception as e:
        # 把原始错误打印出来，方便下一步定位
        logger.exception("查询Question失败")
        raise HTTPException(status_code=500, detail=f"查询Question失败: {str(e)}")
