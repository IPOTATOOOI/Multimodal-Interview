from neo4j import GraphDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class GraphService:
    def __init__(self):
        self.driver = None
        self._connect()

    def _connect(self):
        """建立Neo4j连接"""
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            # 验证连接
            self.driver.verify_connectivity()
            logger.info(f"成功连接到Neo4j: {settings.NEO4J_URI}")
        except Exception as e:
            logger.error(f"Neo4j连接失败: {str(e)}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()
            logger.info("Neo4j连接已关闭")

    def get_graph_data(self, user_id: int = None, is_admin: bool = False):
        """获取图数据"""
        if not self.driver:
            # 如果连接失败，返回空数据
            logger.warning("Neo4j驱动未初始化，返回空数据")
            return {"nodes": [], "links": []}

        try:
            with self.driver.session() as session:
                # 1. 查询所有节点（管理员模式不限制，普通用户模式保留权限过滤）
                if is_admin:
                    nodes_query = "MATCH (n) RETURN n"
                    nodes_params = {}
                else:
                    nodes_query = "MATCH (n) WHERE n.user_id = $user_id OR n.user_id = 0 OR n.user_id IS NULL RETURN n"
                    nodes_params = {"user_id": user_id}
                
                nodes_result = session.run(nodes_query, nodes_params)
                nodes = []
                for record in nodes_result:
                    node = record["n"]
                    labels = list(node.labels)
                    node_data = {
                        "id": str(node.get("id", node.get("name", "unknown"))),
                        "name": node.get("name", "Unnamed"),
                        "type": labels[0] if labels else "Unknown",
                        "properties": {k: v for k, v in dict(node.items()).items() if k not in ["id", "name"]}
                    }
                    nodes.append(node_data)

                # 2. 查询所有关系
                if is_admin:
                    relationships_query = "MATCH (s)-[r]->(t) RETURN s, r, t"
                    relationships_params = {}
                else:
                    relationships_query = """
                    MATCH (s)-[r]->(t) 
                    WHERE (s.user_id = $user_id OR s.user_id = 0 OR s.user_id IS NULL) 
                    AND (t.user_id = $user_id OR t.user_id = 0 OR t.user_id IS NULL)
                    RETURN s, r, t
                    """
                    relationships_params = {"user_id": user_id}
                
                relationships_result = session.run(relationships_query, relationships_params)
                links = []
                for record in relationships_result:
                    source_node = record["s"]
                    relationship = record["r"]
                    target_node = record["t"]

                    link_data = {
                        "source": str(source_node.get("id", source_node.get("name", "unknown"))),
                        "target": str(target_node.get("id", target_node.get("name", "unknown"))),
                        "name": relationship.type,
                        "properties": dict(relationship.items())
                    }
                    links.append(link_data)

                logger.info(f"获取到 {len(nodes)} 个节点和 {len(links)} 条关系")
                return {"nodes": nodes, "links": links}

        except Exception as e:
            logger.error(f"查询图数据失败: {str(e)}")
            return {"nodes": [], "links": []}

    def delete_nodes(self, node_ids: list, user_id: int = None, is_admin: bool = False):
        """删除节点"""
        with self.driver.session() as session:
            if is_admin:
                # 管理员可以删除所有节点
                query = "MATCH (n) WHERE n.id IN $node_ids DELETE n"
                params = {"node_ids": node_ids}
            else:
                # 普通用户只能删除自己的节点和公共节点
                query = "MATCH (n) WHERE n.id IN $node_ids AND (n.user_id = $user_id OR n.user_id = 0) DELETE n"
                params = {"node_ids": node_ids, "user_id": user_id}
            
            result = session.run(query, params)
            return {"deleted_count": result.consume().counters.nodes_deleted}

    def delete_relationships(self, relationships: list, user_id: int = None, is_admin: bool = False):
        """删除关系"""
        with self.driver.session() as session:
            deleted_count = 0
            
            for rel in relationships:
                source_id = rel.get("source")
                target_id = rel.get("target")
                rel_type = rel.get("name")
                
                if is_admin:
                    # 管理员可以删除所有关系
                    query = """
                    MATCH (s)-[r]->(t) 
                    WHERE s.id = $source_id AND t.id = $target_id AND type(r) = $rel_type
                    DELETE r
                    """
                    params = {
                        "source_id": source_id,
                        "target_id": target_id,
                        "rel_type": rel_type
                    }
                else:
                    # 普通用户只能删除涉及自己节点的关系
                    query = """
                    MATCH (s)-[r]->(t) 
                    WHERE s.id = $source_id AND t.id = $target_id AND type(r) = $rel_type
                    AND (s.user_id = $user_id OR s.user_id = 0)
                    AND (t.user_id = $user_id OR t.user_id = 0)
                    DELETE r
                    """
                    params = {
                        "source_id": source_id,
                        "target_id": target_id,
                        "rel_type": rel_type,
                        "user_id": user_id
                    }
                
                result = session.run(query, params)
                deleted_count += result.consume().counters.relationships_deleted
            
            return {"deleted_count": deleted_count}

# 创建单例服务实例
graph_service = GraphService()

# 对外暴露的接口方法（供路由调用）
def get_graph_data(user_id: int = None, is_admin: bool = False):
    return graph_service.get_graph_data(user_id, is_admin)

def delete_nodes(node_ids: list, user_id: int = None, is_admin: bool = False):
    return graph_service.delete_nodes(node_ids, user_id, is_admin)

def delete_relationships(relationships: list, user_id: int = None, is_admin: bool = False):
    return graph_service.delete_relationships(relationships, user_id, is_admin)