from datetime import datetime
from loguru import logger
from app.database.mysql import execute_insert, execute_update
from app.services.ask.generateQ import generate_first_question

def create_history(user_id: str, field: str, position: str) -> int:
    """
    创建新的面试历史记录
    
    Args:
        user_id: 用户ID
        field: 技术领域
        position: 岗位
        
    Returns:
        int: 新创建的历史记录ID
    """
    try:
        logger.info(f"开始创建面试历史记录: user_id={user_id}, field={field}, position={position}")
        
        # 获取当前时间
        current_time = datetime.now()
        
        # 插入新的面试历史记录
        insert_query = """
        INSERT INTO interview_history 
        (user_id, interview_time, field, position, created_at) 
        VALUES (%s, %s, %s, %s, %s)
        """
        
        params = (user_id, current_time, field, position, current_time)
        
        # 执行插入操作
        history_id = execute_insert(insert_query, params)
        
        logger.info(f"面试历史记录创建成功，history_id: {history_id}")
        
        return history_id
        
    except Exception as e:
        error_msg = f"创建面试历史记录失败: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

def save_questions_to_qa(history_id: int, questions: dict):
    """
    将生成的问题批量存储到qa表，role=0，并存储difficulty和relevantKeywords
    """
    try:
        if not questions or "questions" not in questions:
            logger.warning(f"无有效问题数据，history_id={history_id}")
            return
        for q in questions["questions"]:
            content = q.get("questionText")
            difficulty = q.get("difficulty", "")
            relevant_keywords = q.get("relevantKeywords", [])
            if isinstance(relevant_keywords, list):
                key_words = ",".join(relevant_keywords)
            else:
                key_words = str(relevant_keywords)
            if not content:
                continue
            insert_query = """
            INSERT INTO qa (history_id, role, content, created_at, difficulty, key_words)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (history_id, 0, content, datetime.now(), difficulty, key_words)
            execute_insert(insert_query, params)
        logger.info(f"面试问题已存储到qa表，history_id={history_id}, count={len(questions['questions'])}")
    except Exception as e:
        logger.error(f"存储面试问题到qa表失败: {str(e)}")

def save_programming_question_to_written_test(history_id: int, programming_question: dict):
    """
    将编程题存储到written_test表
    """
    try:
        if not programming_question:
            logger.warning(f"无有效编程题数据，history_id={history_id}")
            return
            
        # 提取编程题信息（只提取大模型返回的字段）
        title = programming_question.get("title", "")
        content = programming_question.get("content", "")
        standard_answer = programming_question.get("standard_answer", "")
        tag_name = programming_question.get("tag_name", "")
        knowledgepoint_name = programming_question.get("knowledgepoint_name", "")
        
        # 固定字段写死
        choice = " "  # 编程题不需要选项
        question_type = "code"  # 编程题类型固定为code
        difficulty = "hard"  # 编程题难度固定为hard
        question_score = 25.0  # 编程题分值固定为25
        
        # 生成编程题的question_id（使用时间戳+随机数确保唯一性）
        import time
        import random
        question_id = f"prog_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # 插入编程题到written_test表
        insert_query = """
        INSERT INTO written_test 
        (history_id, question_id, title, content, choice, question_type, difficulty, 
         standard_answer, tag_name, knowledgepoint_name, question_score, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            history_id, question_id, title, content, choice, question_type, difficulty,
            standard_answer, tag_name, knowledgepoint_name, question_score, datetime.now()
        )
        
        record_id = execute_insert(insert_query, params)
        logger.info(f"编程题已存储到written_test表，history_id={history_id}, record_id={record_id}")
        
    except Exception as e:
        logger.error(f"存储编程题到written_test表失败: {str(e)}")
        raise e

def save_written_test_questions(history_id: int, questions: list):
    """
    将笔试题目批量存储到written_test表
    """
    try:
        if not questions:
            logger.warning(f"无有效笔试题目数据，history_id={history_id}")
            return
            
        inserted_count = 0
        for question in questions:
            # 插入笔试题目到written_test表
            insert_query = """
            INSERT INTO written_test 
            (history_id, question_id, title, content, choice, question_type, difficulty, 
             standard_answer, tag_name, knowledgepoint_name, question_score, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                history_id,
                question.get("question_id", ""),
                question.get("title", ""),
                question.get("content", ""),
                question.get("choice", " "),
                question.get("question_type", ""),
                question.get("difficulty", ""),
                question.get("standard_answer", ""),
                question.get("tag_name", ""),
                question.get("knowledgepoint_name", ""),
                question.get("question_score", 5.0),
                datetime.now()
            )
            
            execute_insert(insert_query, params)
            inserted_count += 1
            
        logger.info(f"笔试题目已存储到written_test表，history_id={history_id}, 插入数量={inserted_count}")
        
    except Exception as e:
        logger.error(f"存储笔试题目到written_test表失败: {str(e)}")
        raise e

def initiate_interview(user_id: str, field: str, position: str) -> dict:
    """
    初始化交互式面试流程：创建历史记录并生成第一道问题。

    Returns:
        dict: {
            history_id, first_question, question_qa_id,
            current_topic, written_test_questions
        }
    """
    try:
        logger.info(f"开始初始化交互式面试流程: user_id={user_id}, field={field}, position={position}")

        # 1. 创建面试历史记录
        history_id = create_history(user_id, field, position)

        # 2. 生成第一道面试问题 + 笔试题
        first_q_data = generate_first_question(field, position, user_id=user_id)
        first_question = first_q_data.get("question", "")
        current_topic = first_q_data.get("topic", position)
        difficulty = first_q_data.get("difficulty", "基础")
        written_test_questions = first_q_data.get("written_test_questions", [])

        # 3. 将第一道题存入 qa 表（role=0）
        insert_query = """
        INSERT INTO qa (history_id, role, content, created_at, difficulty, key_words)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        question_qa_id = execute_insert(
            insert_query,
            (history_id, 0, first_question, datetime.now(), difficulty, current_topic)
        )

        # 4. 更新 interview_history：写入初始会话状态
        execute_update(
            """UPDATE interview_history
               SET current_topic = %s, follow_up_count = 0, total_questions_asked = 1
               WHERE history_id = %s""",
            (current_topic, history_id)
        )

        # 5. 笔试题存入 written_test 表
        if written_test_questions:
            save_written_test_questions(history_id, written_test_questions)

        logger.info(f"交互式面试初始化完成，history_id: {history_id}, question_qa_id: {question_qa_id}, topic: {current_topic}")
        return {
            "code": 200,
            "message": "面试初始化成功",
            "data": {
                "history_id": history_id,
                "first_question": first_question,
                "question_qa_id": question_qa_id,
                "current_topic": current_topic,
                "written_test_questions": written_test_questions,
            }
        }

    except Exception as e:
        error_msg = f"面试初始化失败: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)