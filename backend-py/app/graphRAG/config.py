import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置类"""

    # Neo4j数据库配置
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = ""
    NEO4J_DATABASE: str = "neo4j"

    # Ollama配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    QWEN_MODEL: str = "qwen3:4b"
    EMBEDDING_MODEL: str = "bge-m3"

    # 检索配置
    MAX_RETRIEVAL_NODES: int = 10  # 最大检索节点数
    SIMILARITY_THRESHOLD: float = 0.6  # 语义相似度阈值

    class Config:
        env_file = ("../.env", ".env")
        extra = "ignore"
        case_sensitive = True

settings = Settings()
