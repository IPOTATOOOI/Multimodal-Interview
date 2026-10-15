# app/routers/text_input.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from loguru import logger
from app.database.mysql import execute_insert

# 配置日志
logger.add("logs/api_{time}.log", rotation="500 MB", encoding="utf-8")

router = APIRouter(prefix="/text-input", tags=["text-input"])

class TextInputRequest(BaseModel):
    history_id: int
    role: int # 0: 面试官, 1: 面试者
    content: str
    question_qa_id: Optional[int] = None

@router.post("/save-text-input")
async def save_text_input(request: TextInputRequest):
    """
    保存面试过程中双方的文本输入（面试官和面试者）

    Args:
        request: 包含 history_id, role, content 的请求体

    Returns:
        dict: 包含保存结果的JSON对象
    """
    try:
        logger.info(
            f"收到保存文本输入请求: history_id={request.history_id}, role={request.role}, question_qa_id={request.question_qa_id}, content={request.content}"
        )

        # 文字输入接口仅用于保存用户回答，避免将问题(role=0)重复写入qa表
        if request.role != 1:
            logger.warning(f"text-input接口收到非回答角色role={request.role}，已按回答(role=1)入库")
        role = 1

        # 插入数据库
        query = """
        INSERT INTO qa (history_id, role, content, created_at, key_words)
    
        VALUES (%s, %s, %s, %s, %s)
        """
        key_words = f"qid:{request.question_qa_id}" if request.question_qa_id else None
        params = (request.history_id, role, request.content, datetime.now(), key_words)

        execute_insert(query, params)

        return {
            "code": 200,
            "message": "Text input saved successfully",
            "data": None
        }

    except Exception as e:
        error_msg = f"保存文本输入失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)