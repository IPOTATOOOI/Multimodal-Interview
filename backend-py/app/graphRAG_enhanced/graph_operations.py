from neo4j import GraphDatabase
from app.graphRAG_enhanced.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE
import logging
import json

logger = logging.getLogger(__name__)

class Neo4jGraphOperations:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def check_communities_exist(self) -> bool:
        """检查是否已存在社区数据"""
        try:
            query = """
            MATCH (c:Community) 
            RETURN count(c) > 0 as has_communities
            UNION
            MATCH (n) WHERE n.community_id IS NOT NULL
            RETURN count(n) > 0 as has_communities
            """

            with self.driver.session(database=NEO4J_DATABASE) as session:
                result = session.run(query)
                records = list(result)

                # 检查是否有社区节点或带有社区ID的节点
                return any(record.values()[0] for record in records)

        except Exception as e:
            logger.error(f"检查社区存在性时出错: {e}")
            return False

    def get_all_nodes_and_relationships(self,user_id: int = None):
        """获取所有节点和关系用于社区检测 - 适配您的数据结构"""
        user_filter = ""
        params = {}
        if user_id is not None:
            user_filter = "AND (n.user_id = $user_id OR n.user_id = 0)"
            params["user_id"] = user_id
        
        query = f"""
        // 获取所有节点和它们之间的关系
        MATCH (n)
        OPTIONAL MATCH (n)-[r]->(m)
        WHERE any(label IN labels(n) WHERE label IN ['RootCategory', 'SubCategory', 'Topic', 'Question', 'Tag', 'User'])
        AND any(label IN labels(m) WHERE label IN ['RootCategory', 'SubCategory', 'Topic', 'Question', 'Tag', 'User'])
        {user_filter}
        RETURN 
            id(n) as node_id,
            labels(n) as node_labels,
            properties(n) as node_props,
            id(m) as related_node_id,
            type(r) as rel_type,
            properties(r) as rel_props
        """

        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query, **params)
            return list(result)


    def get_community_subgraph(self, community_id: int, user_id: int = None):
        """获取指定社区的完整子图 - 适配您的数据结构"""
        user_filter = ""
        params = {"community_id": community_id}
        if user_id is not None:
            user_filter = "AND (n.user_id = $user_id OR n.user_id = 0) AND (m.user_id = $user_id OR m.user_id = 0)"
            params["user_id"] = user_id
            
        query = f"""
        // 获取社区内的所有节点和关系
        MATCH (n {{community_id: $community_id}})
        OPTIONAL MATCH (n)-[r]-(m {{community_id: $community_id}})
        WHERE 1=1 {user_filter}
        RETURN 
            n.name as node_name,
            labels(n) as node_labels,
            properties(n) as node_properties,
            type(r) as relationship_type,
            m.name as related_node_name,
            labels(m) as related_node_labels,
            properties(r) as relationship_properties
        ORDER BY node_name, relationship_type
        """

        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query, **params)
            return list(result)

    def update_node_community(self, node_id: int, community_id: int):
        """为节点添加社区ID"""
        query = """
        MATCH (n) WHERE id(n) = $node_id
        SET n.community_id = $community_id
        """

        with self.driver.session(database=NEO4J_DATABASE) as session:
            session.run(query, node_id=node_id, community_id=community_id)

    def store_community_summary(self, community_id: int, summary: str, topic_keywords: list):
        """存储社区摘要和关键词"""
        query = """
        WITH $community_id AS communityId, $summary AS summary, $topic_keywords AS topicKeywords
        MATCH (n {community_id: communityId})
        WITH communityId, summary, topicKeywords, count(n) AS nodeCount
        MERGE (c:Community {id: communityId})
        SET c.summary = summary,
            c.topic_keywords = topicKeywords,
            c.created_at = timestamp(),
            c.node_count = nodeCount
        """

        with self.driver.session(database=NEO4J_DATABASE) as session:
            session.run(query,
                        community_id=community_id,
                        summary=summary,
                        topic_keywords=topic_keywords)

    def get_community_nodes_count(self):
        """获取每个社区的节点数量"""
        query = """
        MATCH (n)
        WHERE n.community_id IS NOT NULL
        RETURN n.community_id as community_id, count(n) as node_count
        ORDER BY node_count DESC
        """

        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query)
            return {record["community_id"]: record["node_count"] for record in result}

    def get_community_statistics(self, community_id: int):
        """获取社区的统计信息"""
        query = """
        MATCH (n {community_id: $community_id})
        WITH n
        RETURN 
            sum(CASE WHEN 'RootCategory' IN labels(n) THEN 1 ELSE 0 END) as root_categories,
            sum(CASE WHEN 'SubCategory' IN labels(n) THEN 1 ELSE 0 END) as sub_categories,
            sum(CASE WHEN 'Topic' IN labels(n) THEN 1 ELSE 0 END) as topics,
            sum(CASE WHEN 'Question' IN labels(n) THEN 1 ELSE 0 END) as questions,
            sum(CASE WHEN 'Tag' IN labels(n) THEN 1 ELSE 0 END) as tags,
            sum(CASE WHEN 'User' IN labels(n) THEN 1 ELSE 0 END) as users
        """

        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query, community_id=community_id)
            return result.single()
    
    def check_community_summaries_exist(self) -> bool:
        """检查是否已存在社区摘要"""
        try:
            query = """
            MATCH (c:Community)
            WHERE c.summary IS NOT NULL AND c.summary <> ''
            RETURN count(c) > 0 as has_summaries
            """
            
            with self.driver.session(database=NEO4J_DATABASE) as session:
                result = session.run(query)
                record = result.single()
                return record["has_summaries"] if record else False
                
        except Exception as e:
            logger.error(f"检查社区摘要存在性时出错: {e}")

    # ──────────────── 用户画像 / 个性化推荐方法 ────────────────

    def upsert_weak_at_with_strength(self, user_id: int, tag_id: str, strength: float):
        """创建或更新 WEAK_AT 关系，携带 strength 属性（0-5，越高越弱）。
        ON MATCH 取两值较大者，避免单次成绩好掩盖长期薄弱。
        """
        try:
            with self.driver.session(database=NEO4J_DATABASE) as session:
                session.run("""
                    MERGE (u:User {id: $uid})
                    WITH u
                    MATCH (t:Tag {id: $tid})
                    MERGE (u)-[r:WEAK_AT]->(t)
                    ON CREATE SET r.strength = $strength, r.updated_at = timestamp()
                    ON MATCH SET
                        r.strength = CASE WHEN r.strength < $strength THEN $strength ELSE r.strength END,
                        r.updated_at = timestamp()
                """, uid=user_id, tid=tag_id, strength=strength)
        except Exception as e:
            logger.error(f"upsert_weak_at_with_strength 失败 user={user_id} tag={tag_id}: {e}")

    def get_user_weak_tags(self, user_id: int) -> list:
        """返回用户的薄弱 Tag 列表，按 strength 降序排列"""
        try:
            with self.driver.session(database=NEO4J_DATABASE) as session:
                result = session.run("""
                    MATCH (u:User {id: $uid})-[r:WEAK_AT]->(t:Tag)
                    RETURN t.id AS tag_id, t.name AS tag_name,
                           coalesce(r.strength, 1.0) AS strength
                    ORDER BY strength DESC
                """, uid=user_id)
                return [dict(r) for r in result]
        except Exception as e:
            logger.error(f"get_user_weak_tags 失败 user={user_id}: {e}")
            return []

    def get_questions_by_tags_and_topics(
        self, tag_ids: list, exclude_question_ids: list = None, limit: int = 15
    ) -> list:
        """按薄弱 Tag 查询对应题目，同时返回所属 Topic / SubCategory（用于学习路径分组）。
        exclude_question_ids 传入已练习过的题目 ID，自动排除。
        """
        exclude = exclude_question_ids or []
        try:
            with self.driver.session(database=NEO4J_DATABASE) as session:
                result = session.run("""
                    MATCH (t:Tag)<-[:MARKED_AS]-(q:Question)<-[:INCLUDES]-(tp:Topic)
                    WHERE t.id IN $tag_ids AND NOT q.id IN $exclude
                    OPTIONAL MATCH (sc:SubCategory)-[:CONTAINS_TOPIC]->(tp)
                    WITH q, tp, sc, collect(t.name) AS matched_tags
                    RETURN q.id AS id, q.title AS title, q.content AS content,
                           q.difficulty AS difficulty, q.type AS type,
                           tp.name AS topic_name, sc.name AS sub_category,
                           matched_tags
                    ORDER BY size(matched_tags) DESC, q.difficulty ASC
                    LIMIT $limit
                """, tag_ids=tag_ids, exclude=exclude, limit=limit)
                return [dict(r) for r in result]
        except Exception as e:
            logger.error(f"get_questions_by_tags_and_topics 失败: {e}")
            return []