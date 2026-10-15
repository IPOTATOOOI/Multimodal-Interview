from fastapi import APIRouter, Query, HTTPException
from app.database.mysql import execute_query

router = APIRouter()



@router.get("/getQuestion")
async def get_question(history: str = Query(..., min_length=1)):
    """
    根据history参数获取qa表中的问题列表

    参数:
    history: URL参数，用于筛选qa表记录

    返回:
    { "questions": [{"qa_id": int, "content": str, "key_words": str}, ...] }
    """
    try:
        # 修改查询语句添加key_words字段
        query = "SELECT qa_id, content, key_words FROM qa WHERE history_id = %s"
        results = execute_query(query, (history,))

        # 处理查询结果
        if not results:
            return {"questions": []}

        return {"questions": results}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"数据库查询失败: {str(e)}"
        )