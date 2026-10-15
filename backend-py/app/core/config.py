from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Neo4j 数据库连接配置（当前 graph_service 需要的核心配置）
    NEO4J_URI: str = "bolt://localhost:7687"  # 默认值，可通过环境变量覆盖
    NEO4J_USER: str = "neo4j"                 # Neo4j 用户名
    NEO4J_PASSWORD: str = ""

    # LLM日志模式开关：False=仅摘要日志，True=详细日志（含思维链/原始消息）
    LLM_DETAILED_LOG: bool = False

    # 千问 Qwen 配置（通过 Dashscope OpenAI 兼容接口）
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL: str = "qwen-plus"

    # RabbitMQ 配置
    RABBITMQ_URL: str = "amqp://guest:guest@localhost/"

    # Redis 缓存配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_ENABLED: bool = True
    REDIS_CACHE_PREFIX: str = "swcup"
    REDIS_CACHE_DEFAULT_TTL: int = 3600
    REDIS_CACHE_RESUME_OCR_TTL: int = 86400
    REDIS_CACHE_RESUME_RESULT_TTL: int = 86400
    # Resume process state TTL (seconds). 0 or None means no TTL.
    REDIS_CACHE_PROCESS_TTL: int = 86400

    # JWT配置
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # 管理员注册码配置
    ADMIN_REGISTRATION_CODES: str = ""

    # Cloudflare Turnstile 配置
    CF_TURNSTILE_SECRET_KEY: str = ""  # Turnstile 密钥，从环境变量获取

    # # 其他可能的项目配置（根据需求扩展）
    # API_V1_STR: str = "/api/v1"
    # PROJECT_NAME: str = "SWCUP-backend"

    class Config:
        extra = "allow"
        # 从项目根目录的 .env 文件加载环境变量（可选）
        env_file = ("../.env", ".env")
        # 区分环境变量大小写（如 NEO4J_URI 和 neo4j_uri 视为不同变量）
        case_sensitive = True

    # 创建配置实例，全局使用
settings = Settings()
