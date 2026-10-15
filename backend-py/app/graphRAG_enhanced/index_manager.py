import asyncio
from typing import Optional
from app.graphRAG_enhanced.graph_operations import Neo4jGraphOperations
from app.graphRAG_enhanced.community_detection import CommunityDetector
from app.graphRAG_enhanced.summary_generation import SummaryGenerator
from app.graphRAG_enhanced.vector_store import VectorStoreManager
import logging

logger = logging.getLogger(__name__)

class GraphRAGIndexManager:
    def __init__(self):
        self.graph_ops = Neo4jGraphOperations()
        self.community_detector = CommunityDetector()
        self.summary_generator = SummaryGenerator()
        self.vector_store = None
        self._index_built = False

    async def initialize_index(self):
        """初始化索引：检查是否存在，不存在则自动构建"""
        if await self._check_index_exists():
            logger.info("知识图谱索引已存在，跳过构建过程")
            self._index_built = True
            return True

        logger.info("检测到知识图谱索引不存在，开始自动构建...")
        success = await self.build_full_index()
        if success:
            logger.info("知识图谱索引构建完成")
            self._index_built = True
        else:
            logger.error("知识图谱索引构建失败")

        return success

    async def _check_index_exists(self) -> bool:
        """检查索引是否已构建"""
        try:
            # 检查是否存在Community节点和向量数据库中有数据
            community_check = self.graph_ops.check_communities_exist()
            vector_check = self.vector_store.check_embeddings_exist()

            # 如果数据存在，同步状态
            if community_check and vector_check:
                self._index_built = True
            return community_check and vector_check
        except Exception as e:
            logger.error(f"检查索引存在性时出错: {e}")
            return False

    async def build_full_index(self, user_id: int = None) -> bool:
        """构建完整的学习知识图谱索引，并支持用户隔离"""
        try:
            logger.info(f"开始构建知识图谱索引 (user_id: {user_id})...")

            # 1. 社区检测
            logger.info("开始社区检测...")
            community_count, communities_data = self.community_detector.detect_communities(user_id=user_id)
            if community_count == 0:
                logger.error("社区检测失败，未发现有效社区")
                return False

            logger.info(f"社区检测完成，发现 {community_count} 个学习社区")

            # 2. 检查是否已存在社区摘要，如果不存在则生成
            if not self.graph_ops.check_community_summaries_exist():
                logger.info("开始生成社区摘要...")
                summary_count = self.summary_generator.generate_all_community_summaries(user_id=user_id)
            else:
                logger.info("检测到已存在社区摘要，跳过摘要生成步骤")
                # 获取社区数量用于日志
                community_counts = self.graph_ops.get_community_nodes_count()
                summary_count = len(community_counts)

            # 3. 存储向量索引
            logger.info("开始存储向量索引...")
            vector_count = self.vector_store.store_community_embeddings()

            logger.info(f"知识图谱索引构建完成: {community_count} 个社区, {summary_count} 个摘要, {vector_count} 个向量")
            return True

        except Exception as e:
            logger.error(f"索引构建时发生错误: {e}")
            return False

    def search_similar_communities(self, query: str, top_k: int = 3, user_id: int = None):
        """搜索相似的学习社区，并支持用户隔离"""
        if not self._index_built:
            raise RuntimeError("知识图谱索引尚未构建，请先调用 initialize_index()")

        return self.vector_store.search_similar_communities(query, top_k)

    def get_community_details(self, community_id: int, user_id: int = None):
        """获取学习社区详情，并支持用户隔离"""
        return self.graph_ops.get_community_subgraph(community_id, user_id=user_id)

# 全局索引管理器实例
index_manager = GraphRAGIndexManager()