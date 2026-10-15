from fastapi import APIRouter, HTTPException
from loguru import logger
from app.services.ask.history import get_interview_history, get_user_interview_history, get_history_weakness

# 配置日志
logger.add("logs/api_{time}.log", rotation="500 MB", encoding="utf-8")

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/{history_id}")
async def get_history(history_id: int):
    """
    获取指定的面试历史记录及其所有问答
    """
    try:
        logger.info(f"获取面试历史记录: history_id={history_id}")
        history_data = await get_interview_history(history_id)
        if not history_data:
            raise HTTPException(status_code=404, detail="历史记录不存在")
        logger.info(f"获取面试历史记录成功: history_id={history_id}")
        return history_data
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"获取面试历史记录失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/{history_id}/weakness")
async def get_history_weakness_list(history_id: int):
    """获取指定面试历史的weakness题目列表。"""
    try:
        logger.info(f"获取weakness题目列表: history_id={history_id}")
        weakness_list = get_history_weakness(history_id)
        if weakness_list is None:
            raise HTTPException(status_code=404, detail="历史记录不存在")
        logger.info(f"获取weakness题目列表成功: history_id={history_id}, count={len(weakness_list)}")
        return {
            "history_id": history_id,
            "total": len(weakness_list),
            "weakness": weakness_list,
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"获取weakness题目列表失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/user/{user_id}")
async def get_user_history(user_id: str):
    """
    获取用户的所有面试历史记录（简要信息）
    """
    try:
        logger.info(f"获取用户面试历史记录: user_id={user_id}")
        history_list = get_user_interview_history(user_id)
        logger.info(f"获取用户面试历史记录成功: user_id={user_id}, count={len(history_list)}")
        return {
            "user_id": user_id,
            "total": len(history_list),
            "history_list": history_list
        }
    except Exception as e:
        error_msg = f"获取用户面试历史记录失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg) 