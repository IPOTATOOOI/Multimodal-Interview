from neo4j import GraphDatabase
from typing import List, Dict, Any, Tuple
from app.graphRAG.config import settings
from app.graphRAG.models import RetrievedNode, Entity
from app.graphRAG.embedding_utils import EmbeddingUtils

class GraphRetriever:
    """图数据库检索服务类"""

    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        self.embedding_utils = EmbeddingUtils()

    def close(self):
        """关闭数据库连接"""
        self.driver.close()

    def retrieve_related_nodes(self, entities: List[Entity], max_nodes: int = 50) -> List[RetrievedNode]:
        """
        基于提取的实体检索相关节点

        Args:
            entities: 提取的实体列表
            max_nodes: 最大检索节点数

        Returns:
            List[RetrievedNode]: 检索到的节点列表
        """
        retrieved_nodes = []

        for entity in entities:
            # 基于文本匹配检索
            text_matched_nodes = self._text_match_retrieval(entity, max_nodes)
            retrieved_nodes.extend(text_matched_nodes)

            # 基于语义匹配检索
            semantic_matched_nodes = self._semantic_match_retrieval(entity, max_nodes)
            retrieved_nodes.extend(semantic_matched_nodes)

        # 去重并按相似度排序
        unique_nodes = self._deduplicate_and_sort_nodes(retrieved_nodes)

        # 返回前max_nodes个节点
        return unique_nodes[:max_nodes]

    def _text_match_retrieval(self, entity: Entity, max_nodes: int) -> List[RetrievedNode]:
        """基于文本匹配的检索"""

        # 根据实体类型构建不同的查询
        queries = self._build_text_match_queries(entity)

        retrieved_nodes = []
        for query, params, node_type in queries:
            try:
                with self.driver.session() as session:
                    result = session.run(query, **params)
                    nodes = []

                    for record in result:
                        node = record["n"]
                        properties = dict(node)

                        # 计算文本相似度（简单的字符串匹配分数）
                        similarity = self._calculate_text_similarity(entity.text, properties)
                        # 获取邻居节点和关系
                        neighbors_info, relationships_info = self._get_neighbors_and_relationships(node.id)


                        retrieved_node = RetrievedNode(
                            node_id=properties.get("id", ""),
                            node_type=node_type,
                            content=properties,
                            similarity_score=similarity,
                            retrieval_method="text_match",
                            neighbors=neighbors_info,
                            relationships=relationships_info
                        )
                        nodes.append(retrieved_node)

                    # 按相似度排序并取前几个
                    nodes.sort(key=lambda x: x.similarity_score, reverse=True)
                    retrieved_nodes.extend(nodes[:max_nodes//2])

            except Exception as e:
                print(f"文本匹配检索失败: {e}")
                continue

        return retrieved_nodes

    def _build_text_match_queries(self, entity: Entity) -> List[Tuple[str, Dict, str]]:
        """构建文本匹配查询"""

        queries = []
        entity_text = entity.text

        generic_query = """
        MATCH (n) 
        WHERE n.title CONTAINS $text OR n.content CONTAINS $text
        RETURN n
        LIMIT 20
        """
        queries.append((generic_query, {"text": entity_text}, "GENERIC"))

        return queries

    def _semantic_match_retrieval(self, entity: Entity, max_nodes: int) -> List[RetrievedNode]:
        """基于语义匹配的检索"""

        # 获取实体的嵌入向量
        entity_embedding = self.embedding_utils.get_embedding(entity.text)

        # 查询所有有嵌入向量的Question节点
        query = """
        MATCH (q:Question)
        WHERE q.embedding IS NOT NULL
        RETURN q as n, q.embedding as embedding
        LIMIT 100
        """

        retrieved_nodes = []
        try:
            with self.driver.session() as session:
                result = session.run(query)

                for record in result:
                    node = record["n"]
                    node_embedding = record["embedding"]

                    if node_embedding:
                        # 计算语义相似度
                        similarity = self.embedding_utils.cosine_similarity(
                            entity_embedding, node_embedding
                        )

                        if similarity >= settings.SIMILARITY_THRESHOLD:
                            properties = dict(node)

                            retrieved_node = RetrievedNode(
                                node_id=properties.get("id", ""),
                                node_type="Question",
                                content=properties,
                                similarity_score=similarity,
                                retrieval_method="semantic_match"
                            )
                            retrieved_nodes.append(retrieved_node)

                # 按相似度排序
                retrieved_nodes.sort(key=lambda x: x.similarity_score, reverse=True)
                retrieved_nodes = retrieved_nodes[:max_nodes//2]

        except Exception as e:
            print(f"语义匹配检索失败: {e}")

        return retrieved_nodes

    def _calculate_text_similarity(self, entity_text: str, properties: Dict[str, Any]) -> float:
        """计算文本相似度"""

        # 简单的字符串包含匹配分数
        max_similarity = 0.0
        entity_text_lower = entity_text.lower()

        for key, value in properties.items():
            if isinstance(value, str):
                value_lower = value.lower()
                if entity_text_lower in value_lower:
                    # 计算匹配程度
                    match_ratio = len(entity_text) / len(value) if len(value) > 0 else 0
                    similarity = min(1.0, 0.5 + match_ratio * 0.5)
                    max_similarity = max(max_similarity, similarity)

        return max_similarity

    def _deduplicate_and_sort_nodes(self, nodes: List[RetrievedNode]) -> List[RetrievedNode]:
        """去重并排序节点"""

        # 基于node_id去重
        seen_ids = set()
        unique_nodes = []

        for node in nodes:
            if node.node_id not in seen_ids:
                seen_ids.add(node.node_id)
                unique_nodes.append(node)

        # 按相似度排序
        unique_nodes.sort(key=lambda x: x.similarity_score, reverse=True)
        return unique_nodes
    
    def _get_neighbors_and_relationships(self, node_id: str) -> Tuple[List[Dict], List[Dict]]:
        """获取节点的邻居和关系信息"""
        query = """
        MATCH (n)-[r]-(neighbor) 
        WHERE id(n) = $node_id
        RETURN neighbor, r
        """
        
        neighbors = []
        relationships = []
        
        try:
            with self.driver.session(database=settings.NEO4J_DATABASE) as session:
                result = session.run(query, node_id=int(node_id))
                
                for record in result:
                    neighbor = record["neighbor"]
                    relationship = record["r"]
                    
                    neighbors.append({
                        "id": str(neighbor.id),
                        "type": list(neighbor.labels)[0] if neighbor.labels else "Unknown",
                        "properties": dict(neighbor)
                    })
                    
                    relationships.append({
                        "type": relationship.type,
                        "properties": dict(relationship)
                    })
        except Exception as e:
            print(f"获取邻居节点信息失败: {e}")
        
        return neighbors, relationships 