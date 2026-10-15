from fastapi import APIRouter, HTTPException
from loguru import logger

from app.services.user_portrait.portrait_service import build_user_portrait

router = APIRouter(prefix="/api/user", tags=["user-portrait"])


@router.get("/portrait/{user_id}")
async def get_user_portrait(user_id: int):
    """返回指定用户的完整画像，包含面试历史均分、笔试 Tag 正确率、Neo4j 薄弱点和学习主题标签。"""
    try:
        portrait = await build_user_portrait(user_id)
        return {"code": 200, "data": portrait}
    except Exception as e:
        logger.error(f"获取用户画像失败 user_id={user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
