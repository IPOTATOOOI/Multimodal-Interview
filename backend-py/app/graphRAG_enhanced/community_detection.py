import networkx as nx
from community import community_louvain
from app.graphRAG_enhanced.graph_operations import Neo4jGraphOperations
from app.graphRAG_enhanced.config import COMMUNITY_DETECTION_CONFIG
import logging

logger = logging.getLogger(__name__)

class CommunityDetector:
    def __init__(self):
        self.graph_ops = Neo4jGraphOperations()
        self.relationship_weights = COMMUNITY_DETECTION_CONFIG["relationship_weights"]

    def detect_communities(self, user_id: int = None):
        """基于您的图数据库结构进行社区检测，并支持用户隔离"""
        print(f"开始社区检测 (user_id: {user_id})...")

        # 构建NetworkX图
        G = nx.Graph()

        # 获取所有节点和关系
        records = self.graph_ops.get_all_nodes_and_relationships(user_id=user_id)

        # 节点映射：记录节点ID到节点属性的映射
        node_properties = {}

        for record in records:
            node_id = record["node_id"]
            node_labels = record["node_labels"]
            node_props = record["node_props"] or {}

            # 存储节点属性
            node_properties[node_id] = {
                "labels": node_labels,
                "properties": node_props
            }

            # 添加节点（如果不存在）
            if node_id not in G:
                G.add_node(node_id)

            # 添加关系（如果存在）
            if record["related_node_id"] is not None:
                related_node_id = record["related_node_id"]
                rel_type = record["rel_type"]

                # 为关系类型分配权重
                weight = self._get_relationship_weight(rel_type)

                # 添加边
                G.add_edge(node_id, related_node_id, weight=weight, type=rel_type)

        print(f"图构建完成: {G.number_of_nodes()} 个节点, {G.number_of_edges()} 条边")

        # 使用Louvain算法进行社区检测
        partition = community_louvain.best_partition(G, weight='weight', random_state=42)

        # 过滤小社区
        community_sizes = {}
        for node, comm_id in partition.items():
            community_sizes[comm_id] = community_sizes.get(comm_id, 0) + 1

        # 更新节点社区信息到Neo4j
        valid_communities = 0
        communities_with_nodes = {}

        for node_id, community_id in partition.items():
            if community_sizes[community_id] >= COMMUNITY_DETECTION_CONFIG["min_community_size"]:
                self.graph_ops.update_node_community(node_id, community_id)
                valid_communities = max(valid_communities, community_id + 1)

                # 记录社区包含的节点
                if community_id not in communities_with_nodes:
                    communities_with_nodes[community_id] = []
                communities_with_nodes[community_id].append(node_properties[node_id])

        print(f"社区检测完成: 发现 {valid_communities} 个有效社区")
        return valid_communities, communities_with_nodes

    def _get_relationship_weight(self, rel_type):
        """根据关系类型分配权重"""
        return self.relationship_weights.get(rel_type, 1.0)