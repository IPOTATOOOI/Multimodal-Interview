import chromadb
from sentence_transformers import SentenceTransformer
from app.graphRAG_enhanced.graph_operations import Neo4jGraphOperations
from app.graphRAG_enhanced.config import CHROMA_PERSIST_DIR
import logging

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self):
        self.graph_ops = Neo4jGraphOperations()
        import os
        from dotenv import load_dotenv
        
        # 加载环境变量
        load_dotenv()
        
        self.model = SentenceTransformer(os.getenv('EMBEDDING_MODEL_PATH', 'C:/Users/hp/Desktop/SWCUP-backend/vecDB/paraphrase-multilingual-MiniLM-L12-v2'))

        # 初始化ChromaDB
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(
            "learning_community_embeddings",
            metadata={"description": "学习知识图谱社区嵌入向量"}
        )

    def check_embeddings_exist(self) -> bool:
        """检查是否已存在嵌入向量"""
        try:
            result = self.collection.get(limit=1)
            return len(result['ids']) > 0
        except Exception as e:
            logger.error(f"检查嵌入向量存在性时出错: {e}")
            return False

    def store_community_embeddings(self) -> int:
        """将所有社区摘要存储到向量数据库"""
        # 获取所有社区摘要和关键词
        query = """
        MATCH (c:Community)
        RETURN c.id as community_id, 
               c.summary as summary, 
               c.topic_keywords as keywords,
               c.node_count as node_count
        """

        with self.graph_ops.driver.session() as session:
            results = session.run(query)
            communities = list(results)

        logger.info(f"开始存储 {len(communities)} 个学习社区嵌入向量...")

        embeddings = []
        documents = []
        metadatas = []
        ids = []

        for record in communities:
            community_id = record["community_id"]
            summary = record["summary"]
            keywords = record["keywords"] or []
            node_count = record["node_count"]

            if summary and len(summary) > 10:  # 确保摘要有效
                # 结合摘要和关键词构建搜索文本
                search_text = f"{summary} 关键词: {', '.join(keywords)}"

                # 生成嵌入向量
                embedding = self.model.encode(search_text).tolist()

                embeddings.append(embedding)
                documents.append(summary)  # 原始摘要作为文档内容
                metadatas.append({
                    "community_id": community_id,
                    "node_count": node_count,
                    "keywords": ", ".join(str(k) for k in keywords) if keywords else "",  # 确保转换为字符串
                    "source": "learning_knowledge_graph",
                    "content_type": "community_summary"
                })
                ids.append(f"learning_community_{community_id}")

        # 批量存储到ChromaDB
        if embeddings:
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"成功存储 {len(embeddings)} 个学习社区嵌入向量")

        return len(embeddings)

    def search_similar_communities(self, query_text: str, top_k: int = 3):
        """搜索相似的学习社区"""
        query_embedding = self.model.encode(query_text).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["metadatas", "documents", "distances"]
        )

        return results