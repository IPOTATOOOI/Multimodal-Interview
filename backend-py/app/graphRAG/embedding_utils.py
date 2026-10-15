import requests
import numpy as np
from typing import List
from app.graphRAG.config import settings

class EmbeddingUtils:
    """嵌入计算工具类"""

    def __init__(self):
        self.ollama_url = f"{settings.OLLAMA_BASE_URL}/api/embeddings"
        self.model = settings.EMBEDDING_MODEL

    def get_embedding(self, text: str) -> List[float]:
        """
        获取文本的嵌入向量

        Args:
            text: 输入文本

        Returns:
            List[float]: 嵌入向量
        """
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=180
            )
            response.raise_for_status()

            result = response.json()
            embedding = result.get("embedding", [])

            if not embedding:
                # 如果获取失败，返回零向量
                return [0.0] * 1024

            return embedding

        except Exception as e:
            print(f"嵌入计算失败: {e}")
            # 失败时返回零向量
            return [0.0] * 1024

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        计算两个向量的余弦相似度

        Args:
            vec1: 向量1
            vec2: 向量2

        Returns:
            float: 余弦相似度
        """
        if not vec1 or not vec2:
            return 0.0

        # 转换为numpy数组
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        # 计算余弦相似度
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        return dot_product / (norm_v1 * norm_v2)