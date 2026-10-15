from loguru import logger

from app.core.config import settings
from app.core.redis_cache import build_cache_key, delete_cache_sync, get_cache_json, set_cache_json
from app.database.mysql import execute_update, execute_query


def get_history_weakness(history_id: int):
    """获取指定面试历史的薄弱点训练题目列表。"""
    try:
        logger.info(f"获取weakness列表: history_id={history_id}")

        # 先确认history存在，避免无效ID返回误导性空列表
        history_exists = execute_query(
            "SELECT history_id FROM interview_history WHERE history_id = %s",
            (history_id,),
        )
        if not history_exists:
            logger.warning(f"未找到面试历史记录: {history_id}")
            return None

        weakness_query = (
            """
            SELECT *
            FROM `weakness`
            WHERE history_id = %s
            ORDER BY created_at ASC
            """
        )
        weakness_list = execute_query(weakness_query, (history_id,))
        logger.info(f"获取weakness列表成功: history_id={history_id}, count={len(weakness_list)}")
        return weakness_list
    except Exception as e:
        error_msg = f"获取weakness列表失败: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

def update_interview_history(history_id: int, evaluation_data: dict) -> bool:
    """
    更新面试历史记录，保存评估结果
    
    Args:
        history_id: 历史记录ID
        evaluation_data: 评估数据字典
        
    Returns:
        bool: 更新是否成功
    """
    try:
        logger.info(f"开始更新面试历史记录: history_id={history_id}")
        
        # 从评估数据中提取评分
        feedback = evaluation_data.get('feedback', {})
        
        update_query = """
        UPDATE interview_history 
        SET 
            professional_knowledge = %s,
            skill_match = %s,
            language_expression = %s,
            logical_thinking = %s,
            stress_resistance = %s,
            feedback_suggestion1 = %s,
            feedback_suggestion2 = %s,
            feedback_suggestion3 = %s
        WHERE history_id = %s
        """
        
        params = (
            feedback.get('Professional Knowledge'),
            feedback.get('Skill Matching'),
            feedback.get('Language Expression'),
            feedback.get('Logical Thinking'),
            feedback.get('Stress & Adaptability'),
            feedback.get('constructiveFeedback', ''),  # 反馈建议1
            '',  # 反馈建议2（预留）
            '',  # 反馈建议3（预留）
            history_id
        )
        
        affected_rows = execute_update(update_query, params)
        
        if affected_rows > 0:
            delete_cache_sync(build_cache_key("ask", "history", history_id, "detail"))
            logger.info(f"面试历史记录更新成功: history_id={history_id}")
            return True
        else:
            logger.warning(f"未找到对应的历史记录: history_id={history_id}")
            return False
            
    except Exception as e:
        error_msg = f"更新面试历史记录失败: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

async def get_interview_history(history_id: int) -> dict:
    """
    获取面试历史记录及其所有问答（qa）
    """
    try:
        logger.info(f"获取面试历史记录: history_id={history_id}")

        cache_key = build_cache_key("ask", "history", history_id, "detail")
        cached_result = await get_cache_json(cache_key)
        if cached_result is not None:
            logger.info(f"命中历史详情缓存: history_id={history_id}")
            return cached_result

        # 查询历史记录
        query = """
        SELECT * FROM interview_history 
        WHERE history_id = %s
        """
        result = execute_query(query, (history_id,))
        if not result:
            logger.warning(f"未找到面试历史记录: {history_id}")
            return {}
        history = result[0]
        # 查询该历史下所有qa
        qa_query = "SELECT * FROM qa WHERE history_id = %s ORDER BY created_at ASC"
        qa_list = execute_query(qa_query, (history_id,))
        
        # 查询该历史下所有薄弱点训练题目（weakness）
        weakness_query = (
            """
            SELECT *
            FROM `weakness`
            WHERE history_id = %s
            ORDER BY created_at ASC
            """
        )
        weakness_list = execute_query(weakness_query, (history_id,))
        
        # 为qa_log添加录音文件信息
        try:
            from app.services.interview.interview_end import _match_audio_files_to_qa_log, _filter_qa_log_skip_first_answer
            qa_list = _filter_qa_log_skip_first_answer(qa_list)
            qa_list = _match_audio_files_to_qa_log(history_id, qa_list, start_answer_index=1)
            logger.info(f"已为history_id={history_id}的qa_log跳过首个回答并添加录音文件信息")
        except Exception as e:
            logger.error(f"为qa_log添加录音文件信息失败: {str(e)}")
            # 即使录音文件匹配失败，也不影响主要功能
        
        # 新增：获取前三张landmark截图（当前为固定示例图片，实际可按history_id动态获取）
        # landmark_images = [
        #     "example_07_landmarks.jpg",
        #     "example_08_landmarks.jpg",
        #     "example_010_landmarks.jpg"
        # ]
        # 如需根据history_id动态获取截图，可使用如下代码：
        import os
        landmark_dir = os.path.join(os.getcwd(), "facial_landmarks", "img-landmarks")
        landmark_images = []
        for n in [1, 2, 3]:
            filename = f"his-{history_id}-img-{n}_landmarks.jpg"
            file_path = os.path.join(landmark_dir, filename)
            logger.info(f"file_path: {file_path}")
            if os.path.exists(file_path):
                landmark_images.append(filename)
        
        logger.info(f"获取面试历史及qa成功: history_id={history_id}")
        result = {
            "interview_history": history,
            "qa_log": qa_list,
            "landmark_images": landmark_images,
            "weakness": weakness_list
        }
        if history:
            ttl = settings.REDIS_CACHE_DEFAULT_TTL if getattr(settings, "REDIS_CACHE_DEFAULT_TTL", None) else None
            await set_cache_json(cache_key, result, ttl=ttl)
        return result
    except Exception as e:
        error_msg = f"获取面试历史记录失败: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

def get_user_interview_history(user_id: str) -> list:
    """
    获取用户的所有面试历史记录（仅返回时间、领域、岗位、分数等简要信息）
    """
    try:
        logger.info(f"获取用户面试历史记录: user_id={user_id}")
        query = """
        SELECT history_id, interview_time, end_time, field, position, professional_knowledge, skill_match, language_expression, logical_thinking, innovation_ability, stress_resistance, feedback_suggestion1, score FROM interview_history 
        WHERE user_id = %s AND end_time IS NOT NULL
        ORDER BY created_at ASC
        """
        histories = execute_query(query, (user_id,))
        logger.info(f"获取用户所有面试历史（简要）成功: user_id={user_id}, count={len(histories)}")
        return histories
    except Exception as e:
        error_msg = f"获取用户面试历史记录失败: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)