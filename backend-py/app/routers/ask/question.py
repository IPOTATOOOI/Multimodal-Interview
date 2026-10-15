from fastapi import APIRouter, Form, HTTPException
from loguru import logger

from app.core.config import settings
from app.core.redis_cache import build_cache_key, get_cache_json, set_cache_json
from app.database.mysql import execute_query

# 配置日志
logger.add("logs/api_{time}.log", rotation="500 MB", encoding="utf-8")

router = APIRouter(prefix="/ask", tags=["ask"])


@router.post("/generate")
async def generate_questions(history_id: int = Form(...)):
    """
    获取指定历史的面试问题列表。
    这里优先读 Redis，命中后直接返回，避免重复查库。
    """
    try:
        logger.info(f"收到查询面试问题请求: history_id={history_id}")

        cache_key = build_cache_key("ask", "history", history_id, "questions")
        cached_questions = await get_cache_json(cache_key)
        if cached_questions is not None:
            logger.info(f"命中面试问题缓存: history_id={history_id}")
            return {"questions": cached_questions}

        query = """
        SELECT qa_id, content, key_words FROM qa WHERE history_id = %s AND role = 0 ORDER BY qa_id ASC
        """
        result = execute_query(query, (history_id,))
        questions = [
            {"number": idx + 1, "content": row["content"], "key_words": row.get("key_words", "")}
            for idx, row in enumerate(result)
        ]

        ttl = settings.REDIS_CACHE_DEFAULT_TTL if getattr(settings, "REDIS_CACHE_DEFAULT_TTL", None) else None
        await set_cache_json(cache_key, questions, ttl=ttl)

        logger.info(f"查询面试问题成功: history_id={history_id}, count={len(questions)}")
        return {"questions": questions}
    except Exception as e:
        error_msg = f"查询面试问题失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)