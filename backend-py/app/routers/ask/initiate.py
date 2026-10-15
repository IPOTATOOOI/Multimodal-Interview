from fastapi import APIRouter, HTTPException, Form
from loguru import logger
from app.services.ask.initiate import initiate_interview

# 配置日志
logger.add("logs/api_{time}.log", rotation="500 MB", encoding="utf-8")

router = APIRouter(prefix="/interview", tags=["interview"])

@router.post("/start")
async def start_interview(
    user_id: str = Form(...),
    field: str = Form(...),
    position: str = Form(...)
):
    """
    开始面试：创建历史记录并生成面试问题
    
    Args:
        user_id: 用户ID（表单字段）
        field: 技术领域（表单字段）
        position: 岗位（表单字段）
        
    Returns:
        dict: 包含历史记录ID和面试问题的JSON对象
    """
    try:
        logger.info(f"收到开始面试请求: user_id={user_id}, field={field}, position={position}")
        
        # 调用面试初始化服务
        result = initiate_interview(
            user_id=user_id,
            field=field,
            position=position
        )
        
        logger.info(f"面试初始化成功: history_id={result['data']['history_id']}")
        return result
        
    except Exception as e:
        error_msg = f"开始面试失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)