from fastapi import APIRouter, Query, HTTPException
from loguru import logger
from app.database.mysql import execute_query

# 配置日志
logger.add("logs/api_{time}.log", rotation="500 MB", encoding="utf-8")

router = APIRouter(prefix="/written-test", tags=["written-test"])

@router.get("/questions")
async def get_written_test_questions(history_id: int = Query(..., description="面试历史记录ID")):
    """
    根据history_id查询笔试问题列表
    
    Args:
        history_id: 面试历史记录ID
        
    Returns:
        dict: 包含笔试问题列表的JSON对象
    """
    try:
        logger.info(f"收到查询笔试问题请求: history_id={history_id}")
        
        # 查询笔试问题
        query = """
        SELECT record_id, question_id, title, content, choice, question_type, 
               difficulty, standard_answer, tag_name, knowledgepoint_name, question_score
        FROM written_test 
        WHERE history_id = %s 
        ORDER BY record_id ASC
        """
        
        result = execute_query(query, (history_id,))
        
        if not result:
            logger.info(f"未找到笔试问题，history_id={history_id}")
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "history_id": history_id,
                    "questions": [],
                    "total_count": 0
                }
            }
        
        # 处理查询结果
        questions = []
        for row in result:
            questions.append({
                "record_id": row["record_id"],
                "question_id": row["question_id"],
                "title": row["title"],
                "content": row["content"],
                "choice": row["choice"],
                "question_type": row["question_type"],
                "difficulty": row["difficulty"],
                "standard_answer": row["standard_answer"],
                "tag_name": row["tag_name"],
                "knowledgepoint_name": row["knowledgepoint_name"],
                "question_score": float(row["question_score"]) if row["question_score"] else 0.0
            })
        
        logger.info(f"查询笔试问题成功: history_id={history_id}, count={len(questions)}")
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "history_id": history_id,
                "questions": questions,
                "total_count": len(questions)
            }
        }
        
    except Exception as e:
        error_msg = f"查询笔试问题失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/summary")
async def get_written_test_summary(history_id: int = Query(..., description="面试历史记录ID")):
    """
    根据history_id查询笔试问题统计信息
    
    Args:
        history_id: 面试历史记录ID
        
    Returns:
        dict: 包含笔试问题统计信息的JSON对象
    """
    try:
        logger.info(f"收到查询笔试统计信息请求: history_id={history_id}")
        
        # 查询统计信息
        summary_query = """
        SELECT 
            COUNT(*) as total_questions,
            SUM(question_score) as total_score,
            COUNT(CASE WHEN difficulty = 'easy' THEN 1 END) as easy_count,
            COUNT(CASE WHEN difficulty = 'medium' THEN 1 END) as medium_count,
            COUNT(CASE WHEN difficulty = 'hard' THEN 1 END) as hard_count,
            COUNT(CASE WHEN question_type = 'single_choice' THEN 1 END) as single_choice_count,
            COUNT(CASE WHEN question_type = 'multiple_choice' THEN 1 END) as multiple_choice_count,
            COUNT(CASE WHEN question_type = 'essay' THEN 1 END) as essay_count,
            COUNT(CASE WHEN question_type = 'code' THEN 1 END) as code_count
        FROM written_test 
        WHERE history_id = %s
        """
        
        result = execute_query(summary_query, (history_id,))
        
        if not result or result[0]["total_questions"] == 0:
            logger.info(f"未找到笔试问题统计信息，history_id={history_id}")
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "history_id": history_id,
                    "total_questions": 0,
                    "total_score": 0.0,
                    "difficulty_distribution": {
                        "easy": 0,
                        "medium": 0,
                        "hard": 0
                    },
                    "type_distribution": {
                        "single_choice": 0,
                        "multiple_choice": 0,
                        "essay": 0,
                        "code": 0
                    }
                }
            }
        
        summary = result[0]
        
        logger.info(f"查询笔试统计信息成功: history_id={history_id}")
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "history_id": history_id,
                "total_questions": summary["total_questions"],
                "total_score": float(summary["total_score"]) if summary["total_score"] else 0.0,
                "difficulty_distribution": {
                    "easy": summary["easy_count"],
                    "medium": summary["medium_count"],
                    "hard": summary["hard_count"]
                },
                "type_distribution": {
                    "single_choice": summary["single_choice_count"],
                    "multiple_choice": summary["multiple_choice_count"],
                    "essay": summary["essay_count"],
                    "code": summary["code_count"]
                }
            }
        }
        
    except Exception as e:
        error_msg = f"查询笔试统计信息失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg) 