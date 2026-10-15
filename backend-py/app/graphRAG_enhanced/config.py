import os
from dotenv import load_dotenv

load_dotenv()

# Neo4j配置 - 根据您的图片信息
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# LLM配置
LOCAL_LLM_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ChromaDB配置
CHROMA_PERSIST_DIR = os.getenv("CHROMA_DB_PATH", "./chroma_db")

# 社区检测参数
COMMUNITY_DETECTION_CONFIG = {
    "min_community_size": 5,  # 最小社区大小
    "resolution_parameter": 1.0,
    "relationship_weights": {
        "HAS_SUB": 2.0,           # 分类层级关系，权重高
        "CONTAINS_TOPIC": 2.0,    # 包含主题关系
        "INCLUDES": 1.8,          # 包含题目关系
        "MARKED_AS": 1.5,         # 标签标记关系
        "WEAK_AT": 0.8           # 用户薄弱点关系，权重较低
    }
}

# 日志配置
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'graph_rag': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
