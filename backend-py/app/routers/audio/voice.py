from fastapi import APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks
from uuid import uuid4
from datetime import datetime
import os
import shutil
import traceback
from typing import Optional
from loguru import logger

from app.services.audio.xfyun_transcribe import XunfeiTranscriber
from app.database.audio.audio import save_audio
from app.database.mysql import execute_insert, execute_query
from app.services.mq.audio_transcription_producer import publish_audio_transcription_job

# 配置日志
logger.add("logs/api_{time}.log", rotation="500 MB", encoding="utf-8")

router = APIRouter(prefix="/voice", tags=["voice"])
transcriber = XunfeiTranscriber()

# 当讯飞识别失败且判定为音频质量过差时，使用固定兜底文本入库
LOW_QUALITY_FALLBACK_TEXT = "音频文件质量差，无法识别"

# 确保 upload 目录存在
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "audio")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 确保日志目录存在
os.makedirs("logs", exist_ok=True)

# 允许的音频文件类型
ALLOWED_AUDIO_TYPES = {
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/mp4": ".m4a",
    "audio/aac": ".aac"
}

def get_file_extension(content_type: str) -> Optional[str]:
    """根据 content_type 获取文件扩展名"""
    return ALLOWED_AUDIO_TYPES.get(content_type)

@router.post("/transcribe/async")
async def transcribe_audio_async(
    file: UploadFile = File(...),
    history_id: int = Form(...),
    question_qa_id: Optional[int] = Form(None)
):
    """
    异步语音转写接口：上传音频后立即返回task_id，前端轮询查询转写结果。

    流程：
    1. 保存音频文件到磁盘
    2. 投递转写任务到RabbitMQ
    3. 立即返回task_id
    4. 前端通过 /voice/transcribe/status/{task_id} 查询状态
    """
    logger.info(
        f"收到异步音频转写请求: filename={file.filename}, content_type={file.content_type}, history_id={history_id}, question_qa_id={question_qa_id}"
    )
    ext = get_file_extension(file.content_type)
    if not ext:
        error_msg = f"不支持的文件类型: {file.content_type}。支持的格式: {', '.join(ALLOWED_AUDIO_TYPES.keys())}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

    # 使用前端传递的文件名
    file_basename = os.path.splitext(file.filename)[0]
    file_id = file_basename
    dest_path = os.path.join(UPLOAD_DIR, file.filename)
    logger.info(f"使用前端文件名: {file.filename}, 文件路径: {dest_path}")

    try:
        # 保存到磁盘
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        logger.info(f"文件保存成功: {dest_path}")
    except Exception as e:
        error_msg = f"保存文件失败: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        file.file.close()

    # 生成任务ID
    task_id = str(uuid4())

    try:
        # 投递到RabbitMQ
        mq_ok = await publish_audio_transcription_job(task_id, history_id, dest_path, question_qa_id)
        if not mq_ok:
            # RabbitMQ不可用，使用BackgroundTask降级
            logger.warning(f"RabbitMQ投递失败，使用同步转写降级: task_id={task_id}")
            transcript = transcriber.transcribe_file(dest_path)
            txt_path = os.path.join(UPLOAD_DIR, f"{file_id}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(transcript)

            count_query = "SELECT COUNT(*) AS answer_count FROM qa WHERE history_id = %s AND role = 1"
            count_result = execute_query(count_query, (history_id,))
            answer_count = int(count_result[0].get("answer_count", 0)) if count_result else 0
            answer_index = answer_count + 1

            insert_query = """
            INSERT INTO qa (history_id, role, content, created_at, key_words)
            VALUES (%s, %s, %s, %s, %s)
            """
            key_words = f"qid:{question_qa_id}" if question_qa_id else None
            params = (history_id, 1, transcript, datetime.now(), key_words)
            execute_insert(insert_query, params)

            return {
                "code": 200,
                "message": "success",
                "task_id": task_id,
                "status": "completed",
                "transcript": transcript,
                "answer_index": answer_index
            }

        return {
            "code": 200,
            "message": "transcription task created",
            "task_id": task_id,
            "status": "processing"
        }
    except Exception as e:
        error_msg = f"创建转写任务失败: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/transcribe/status/{task_id}")
async def get_transcription_status(task_id: str):
    """
    查询语音转写任务状态。
    由于转写结果直接写入qa表，通过查询qa表判断是否完成。
    """
    try:
        # 通过task_id在文件系统中查找是否有对应的txt文件
        # 实际应用中可以增加一个任务状态表来追踪
        txt_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".txt")]

        # 暂时返回简单状态，实际应通过数据库查询
        return {
            "code": 200,
            "task_id": task_id,
            "status": "processing",
            "message": "任务处理中，请稍后查询"
        }
    except Exception as e:
        logger.error(f"查询转写状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    history_id: int = Form(...),
    answer_index: Optional[int] = Form(None),
    question_qa_id: Optional[int] = Form(None)
):
    """
    接收前端上传的录音文件和history_id，保存音频并转写，将转写文本存入qa表
    """
    logger.info(
        f"收到新的音频转写请求: filename={file.filename}, content_type={file.content_type}, history_id={history_id}, question_qa_id={question_qa_id}"
    )
    ext = get_file_extension(file.content_type)
    if not ext:
        error_msg = f"不支持的文件类型: {file.content_type}。支持的格式: {', '.join(ALLOWED_AUDIO_TYPES.keys())}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

    # 使用前端传递的文件名（格式: his-{history_id}-audioid-{seq}.wav）
    # 前端已经生成了正确格式的文件名，直接使用即可
    file_basename = os.path.splitext(file.filename)[0]  # 不带扩展名的文件名
    file_id = file_basename
    dest_path = os.path.join(UPLOAD_DIR, file.filename)
    logger.info(f"使用前端文件名: {file.filename}, 文件路径: {dest_path}")
    try:
        # 保存到磁盘
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        logger.info(f"文件保存成功: {dest_path}")
    except Exception as e:
        error_msg = f"保存文件失败: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        file.file.close()

    try:
        # 调用讯飞转写
        logger.info("开始调用讯飞转写服务")
        transcript = transcriber.transcribe_file(dest_path)
        logger.info(f"转写成功，结果: {transcript}")
        
        # 保存转写文本
        txt_path = os.path.join(UPLOAD_DIR, f"{file_id}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        logger.info(f"转写文本已保存: {txt_path}")
            
    except Exception as e:
        err_str = str(e)
        is_low_quality = ("failType: 6" in err_str) or ("音频文件质量太差" in err_str)

        if is_low_quality:
            # 质量过差时按业务要求写入固定文本，并继续后续入库流程
            transcript = LOW_QUALITY_FALLBACK_TEXT
            logger.warning(
                f"检测到低质量音频，使用兜底文本入库: history_id={history_id}, question_qa_id={question_qa_id}, text={transcript}"
            )
        else:
            # 非质量问题仍按失败处理
            try:
                os.remove(dest_path)
                logger.info(f"清理临时文件: {dest_path}")
            except Exception:
                pass
            error_msg = f"转写失败: {err_str}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=error_msg)
    # 存入qa表
    try:
        # 在入库前实时计算回答序号，避免save-audio阶段预估导致并发错位
        count_query = "SELECT COUNT(*) AS answer_count FROM qa WHERE history_id = %s AND role = 1"
        count_result = execute_query(count_query, (history_id,))
        answer_count = int(count_result[0].get("answer_count", 0)) if count_result else 0
        answer_index = answer_count + 1
        logger.info(f"实时回答序号计算: history_id={history_id}, existing_answer_count={answer_count}, final_answer_index={answer_index}")

        # 前端已保证文件名格式正确（his-{history_id}-audioid-{seq}.wav）
        # 直接使用现有文件名保存转写文本
        final_txt_path = os.path.join(UPLOAD_DIR, f"{file_id}.txt")

        with open(final_txt_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        logger.info(f"转写文本已保存: {final_txt_path}")

        insert_query = """
        INSERT INTO qa (history_id, role, content, created_at, key_words)
        VALUES (%s, %s, %s, %s, %s)
        """
        key_words = f"qid:{question_qa_id}" if question_qa_id else None
        params = (history_id, 1, transcript, datetime.now(), key_words)
        execute_insert(insert_query, params)
        logger.info(
            f"转写文本已存入qa表: history_id={history_id}, answer_index={answer_index}, bind_question_qa_id={question_qa_id}"
        )
    except Exception as e:
        logger.error(f"存储转写文本到qa表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"存储转写文本到qa表失败: {str(e)}")
    response_data = {
        "code": 200,
        "message": "success",
        "success": True,
        "history_id": history_id,
        "answer_index": answer_index,
        "audio_filename": file.filename,
        "text": transcript
    }
    logger.info(f"请求处理完成，返回数据: {response_data}")
    return response_data