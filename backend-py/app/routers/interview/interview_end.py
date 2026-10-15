import json

from fastapi import APIRouter, HTTPException, Form, BackgroundTasks, UploadFile, File, Request
from fastapi.responses import FileResponse, StreamingResponse
from loguru import logger
from app.services.interview.interview_end import end_interview_session, InterviewEndService
from app.database.mysql import execute_query, execute_update
from app.services.interview.interactive_interview import process_answer, process_answer_stream
from app.models.enums import ProcessStatus
import os
import shutil
from datetime import datetime
from typing import Dict, Optional, Tuple

# 配置日志
logger.add("logs/api_{time}.log", rotation="500 MB", encoding="utf-8")

router = APIRouter(prefix="/interview", tags=["interview"])

# 视频统一保存目录：项目根目录/video
VIDEO_DIR = os.path.join(os.getcwd(), "video")
os.makedirs(VIDEO_DIR, exist_ok=True)

# 内存态记录：用于标记某个问题的视频录制是否已开始
_active_video_sessions: Dict[str, datetime] = {}

# 允许的视频类型
ALLOWED_VIDEO_TYPES = {
    "video/webm": ".webm",
    "video/mp4": ".mp4",
    "video/ogg": ".ogv",
    "video/quicktime": ".mov",
    "video/x-matroska": ".mkv"
}

VIDEO_EXTENSION_TO_MEDIA_TYPE = {
    ".webm": "video/webm",
    ".mp4": "video/mp4",
    ".ogv": "video/ogg",
    ".mov": "video/quicktime",
    ".mkv": "video/x-matroska"
}


def _video_session_key(history_id: int, question_qa_id: int) -> str:
    return f"{history_id}:{question_qa_id}"


def _request_source(request: Request) -> str:
    client = request.client
    if client is None:
        return "unknown"
    return f"{client.host}:{client.port}"


def _normalize_content_type(content_type: Optional[str]) -> str:
    if not content_type:
        return ""
    return content_type.split(";", 1)[0].strip().lower()


def _find_video_file_by_question_id(question_qa_id: int) -> Tuple[Optional[str], Optional[str]]:
    for ext, media_type in VIDEO_EXTENSION_TO_MEDIA_TYPE.items():
        filename = f"{question_qa_id}{ext}"
        file_path = os.path.join(VIDEO_DIR, filename)
        if os.path.exists(file_path):
            return file_path, media_type
    return None, None


@router.post("/video/start")
async def start_video_recording(
    request: Request,
    history_id: int = Form(...),
    question_qa_id: int = Form(...)
):
    """
    标记某个问题的视频录制开始。
    前端应在"问题提出"时调用该接口，然后立即开始本地录制。
    """
    try:
        source = _request_source(request)
        logger.info(
            f"[video/start] 接口被调用: source={source}, method={request.method}, path={request.url.path}, "
            f"history_id={history_id}, question_qa_id={question_qa_id}"
        )
        key = _video_session_key(history_id, question_qa_id)
        started_at = datetime.now()
        _active_video_sessions[key] = started_at

        # 文件名按问题qa_id命名，扩展名由结束上传时的真实类型决定
        response = {
            "code": 200,
            "message": "video recording started",
            "data": {
                "history_id": history_id,
                "question_qa_id": question_qa_id,
                "suggested_filename": f"{question_qa_id}",
                "started_at": started_at.isoformat()
            }
        }
        logger.info(
            f"[video/start] 调用成功: session_key={key}, active_sessions={len(_active_video_sessions)}"
        )
        return response
    except Exception as e:
        error_msg = f"开始视频录制失败: {str(e)}"
        logger.exception(f"[video/start] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/video/end")
async def end_video_recording(
    request: Request,
    file: UploadFile = File(...),
    history_id: int = Form(...),
    question_qa_id: int = Form(...)
):
    """
    结束某个问题的视频录制并上传视频文件（异步处理RabbitMQ）。
    前端应在"用户点击结束语音"时调用该接口。
    """
    import uuid

    try:
        source = _request_source(request)
        start_ts = datetime.now()
        logger.info(
            f"[video/end] 接口被调用: source={source}, method={request.method}, path={request.url.path}, "
            f"history_id={history_id}, question_qa_id={question_qa_id}, filename={file.filename}, content_type={file.content_type}"
        )

        normalized_content_type = _normalize_content_type(file.content_type)
        ext = ALLOWED_VIDEO_TYPES.get(normalized_content_type)
        if not ext:
            logger.warning(
                f"[video/end] 不支持的视频类型: raw_content_type={file.content_type}, "
                f"normalized_content_type={normalized_content_type}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"不支持的视频类型: {file.content_type}"
            )

        logger.info(
            f"[video/end] 视频类型识别成功: raw_content_type={file.content_type}, "
            f"normalized_content_type={normalized_content_type}, ext={ext}"
        )

        # 先保存到临时目录
        temp_dir = os.path.join(os.getcwd(), "video_temp")
        os.makedirs(temp_dir, exist_ok=True)
        task_id = str(uuid.uuid4())
        temp_filename = f"{task_id}{ext}"
        temp_file_path = os.path.join(temp_dir, temp_filename)

        with open(temp_file_path, "wb") as target:
            shutil.copyfileobj(file.file, target)

        file_size = os.path.getsize(temp_file_path)

        key = _video_session_key(history_id, question_qa_id)
        started_at = _active_video_sessions.pop(key, None)

        # 直接同步移动到目标目录
        filename = f"{question_qa_id}{ext}"
        file_path = os.path.join(VIDEO_DIR, filename)
        shutil.move(temp_file_path, file_path)

        elapsed_ms = int((datetime.now() - start_ts).total_seconds() * 1000)
        logger.info(
            f"[video/end] 视频保存完成: filename={filename}, file_size={file_size}, cost_ms={elapsed_ms}"
        )
        return {
            "code": 200,
            "message": "video recording ended",
            "data": {
                "history_id": history_id,
                "question_qa_id": question_qa_id,
                "filename": filename,
                "saved_path": file_path,
                "file_size": file_size,
                "started": bool(started_at),
                "started_at": started_at.isoformat() if started_at else None,
                "ended_at": datetime.now().isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"结束视频录制失败: {str(e)}"
        logger.exception(f"[video/end] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        try:
            file.file.close()
        except Exception:
            pass


@router.get("/video/question/{question_qa_id}")
async def get_video_file_by_question_id(question_qa_id: int, request: Request):
    """按题目qa_id自动查找对应视频文件，前端无需关心扩展名。"""
    try:
        source = _request_source(request)
        logger.info(
            f"[video/get-by-question] 接口被调用: source={source}, method={request.method}, "
            f"path={request.url.path}, question_qa_id={question_qa_id}"
        )

        file_path, media_type = _find_video_file_by_question_id(question_qa_id)
        if not file_path or not media_type:
            logger.warning(f"[video/get-by-question] 未找到视频文件: question_qa_id={question_qa_id}")
            raise HTTPException(status_code=404, detail="视频文件不存在")

        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        logger.info(
            f"[video/get-by-question] 返回视频文件: path={file_path}, filename={filename}, "
            f"file_size={file_size}, media_type={media_type}"
        )
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"按题目ID获取视频文件失败: {str(e)}"
        logger.exception(f"[video/get-by-question] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.api_route("/video/{filename}", methods=["GET", "HEAD"])
async def get_video_file(filename: str, request: Request):
    """获取面试题目对应的视频文件。"""
    try:
        source = _request_source(request)
        logger.info(
            f"[video/get] 接口被调用: source={source}, method={request.method}, path={request.url.path}, filename={filename}"
        )

        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        media_type = VIDEO_EXTENSION_TO_MEDIA_TYPE.get(ext)
        if not media_type:
            raise HTTPException(status_code=400, detail="无效的视频文件类型")

        file_path = os.path.join(VIDEO_DIR, filename)

        if not os.path.abspath(file_path).startswith(os.path.abspath(VIDEO_DIR)):
            logger.error(f"尝试访问非法视频路径: {file_path}")
            raise HTTPException(status_code=403, detail="访问被拒绝")

        if not os.path.exists(file_path):
            logger.warning(f"视频文件不存在: {file_path}")
            raise HTTPException(status_code=404, detail="视频文件不存在")

        file_size = os.path.getsize(file_path)
        logger.info(f"[video/get] 返回视频文件: path={file_path}, file_size={file_size}, media_type={media_type}")
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"获取视频文件失败: {str(e)}"
        logger.exception(f"[video/get] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/answer")
async def submit_answer(
    history_id: int = Form(...),
    question_qa_id: int = Form(...),
    answer_content: Optional[str] = Form(None),
):
    """
    提交候选人对当前问题的回答，触发实时单题评估并返回下一步动作。

    语音回答流程：先调用 POST /voice/transcribe 让系统把语音转写存入 qa 表，
    再调用本接口（不传 answer_content），系统自动从 qa 表取最新回答。

    文字回答流程：直接传入 answer_content，系统入库后立即评估。

    Returns:
        {
            action: "follow_up" | "next_topic" | "end",
            next_question: str | null,
            question_qa_id: int | null,  # 新题的 qa_id
            current_topic: str,
            evaluation: { evaluation, feedback, reference_a, skill, category, answer_rating }
        }
    """
    try:
        logger.info(
            f"收到提交回答请求: history_id={history_id}, question_qa_id={question_qa_id}, "
            f"has_text_answer={answer_content is not None}"
        )
        result = await process_answer(
            history_id=history_id,
            question_qa_id=question_qa_id,
            answer_content=answer_content or None,
        )
        logger.info(
            f"提交回答处理完成: history_id={history_id}, action={result.get('action')}, "
            f"next_qa_id={result.get('question_qa_id')}"
        )
        return {"code": 200, "message": "success", "data": result}
    except ValueError as e:
        logger.warning(f"提交回答参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"提交回答处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"提交回答失败: {str(e)}")


@router.post("/answer/stream")
async def submit_answer_stream(
    background_tasks: BackgroundTasks,
    history_id: int = Form(...),
    question_qa_id: int = Form(...),
    answer_content: Optional[str] = Form(None),
):
    """
    流式版本：SSE 实时推送下一题 Token，大幅降低首字节延迟。

    单题评估异步投递到 RabbitMQ（或降级到 BackgroundTask），不阻塞主流程。
    DB 写操作在流结束后后台完成。

    SSE 事件协议：
      event: metadata  → {"action": "follow_up|next_topic|end", "current_topic": "..."}
      event: token     → {"content": "<token>"}  （问题生成期间，多次）
      event: done      → {"question_qa_id": int|null, "action": "...", "current_topic": "...",
                          "next_question": "..."}
      event: error     → {"message": "..."}  （异常时单次，随后流关闭）
    """
    async def event_generator():
        try:
            async for chunk in process_answer_stream(
                background_tasks, history_id, question_qa_id, answer_content or None
            ):
                yield chunk
        except GeneratorExit:
            logger.info(f"SSE 客户端断开: history_id={history_id}")
        except Exception as e:
            logger.error(f"SSE 流式传输异常: history_id={history_id}, error={e}")
            yield f"event: error\ndata: {json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n"

    logger.info(
        f"收到流式提交回答请求: history_id={history_id}, question_qa_id={question_qa_id}, "
        f"has_text_answer={answer_content is not None}"
    )
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.post("/end")
async def end_interview(
    background_tasks: BackgroundTasks,
    history_id: int = Form(...)
):
    """
    异步结束面试，对整个面试过程进行总结性评估（BackgroundTask 异步处理）

    Args:
        history_id: 面试历史ID

    Returns:
        dict: 包含处理ID和状态信息
    """
    try:
        import uuid
        process_id = str(uuid.uuid4())

        logger.info(f"收到结束面试请求: history_id={history_id}, process_id={process_id}")

        await InterviewEndService.cleanup_old_processes()
        InterviewEndService._process_store[process_id] = {
            "status": ProcessStatus.PROCESSING,
            "history_id": history_id,
            "timestamp": datetime.now(),
            "result": None,
            "error": None
        }

        # 将 process_id 写入数据库，支持通过 DB 判断完成状态
        execute_update(
            "UPDATE interview_history SET process_id = %s WHERE history_id = %s",
            (process_id, history_id)
        )

        background_tasks.add_task(
            InterviewEndService.process_interview_end_async,
            process_id,
            history_id
        )

        return {
            "code": 202,
            "message": "Interview end processing started",
            "data": {
                "process_id": process_id,
                "status": ProcessStatus.PROCESSING
            }
        }

    except Exception as e:
        error_msg = f"结束面试处理失败: {str(e)}"
        logger.error(error_msg)
        return {
            "code": 500,
            "message": error_msg,
            "data": None
        }

@router.get("/end/status/{process_id}")
async def check_interview_end_status(process_id: str):
    """
    查询面试结束处理状态。
    优先从内存中获取状态，如果没有则检查数据库中是否有面试结束时间。
    """
    try:
        # 1. 优先检查内存中的处理状态
        status_info = await InterviewEndService.get_process_status(process_id)
        if status_info["status"] != ProcessStatus.FAILED or "Process not found" not in (status_info.get("error") or ""):
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "status": status_info["status"],
                    "process_id": process_id,
                    "result": status_info.get("result")
                }
            }
        
        # 2. 内存中未找到，检查数据库（处理历史记录）
        # 尝试从process_store中获取history_id
        if process_id in InterviewEndService._process_store:
            history_id = InterviewEndService._process_store[process_id].get("history_id")
            if history_id:
                # 检查数据库中是否有结束时间
                rows = execute_query(
                    "SELECT end_time FROM interview_history WHERE history_id = %s",
                    (history_id,)
                )
                if rows and rows[0].get("end_time"):
                    return {
                        "code": 200,
                        "message": "success",
                        "data": {
                            "status": ProcessStatus.COMPLETED,
                            "process_id": process_id
                        }
                    }
        
        # 3. 默认返回处理中
        return {
            "code": 200,
            "message": "success",
            "data": {
                "status": ProcessStatus.PROCESSING,
                "process_id": process_id
            }
        }
    except Exception as e:
        logger.error(f"查询面试结束处理状态失败: {str(e)}")
        return {
            "code": 500,
            "message": str(e),
            "data": None
        }

@router.post("/end/sync")
async def end_interview_sync(
    history_id: int = Form(...)
):
    """
    同步结束面试，对整个面试过程进行总结性评估（保留原有接口）
    
    Args:
        history_id: 面试历史ID
        
    Returns:
        dict: 包含最终面试报告和问答详情
    """
    try:
        logger.info(f"收到同步结束面试请求: history_id={history_id}")
        
        # 调用服务
        result = end_interview_session(history_id)
        
        logger.info(f"面试总结评估成功: history_id={history_id}")
        return {
            "code": 200,
            "message": "success",
            "data": result
        }
        
    except Exception as e:
        error_msg = f"结束面试失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """
    获取录音文件
    
    Args:
        filename: 录音文件名，格式为 his-{history_id}-audioid-{number}.wav
        
    Returns:
        FileResponse: 录音文件
    """
    try:
        logger.info(f"收到录音文件请求: filename={filename}")
        
        # 验证文件名格式
        if not filename.startswith("his-") or not filename.endswith(".wav"):
            raise HTTPException(status_code=400, detail="无效的文件名格式")
        
        # 构建文件路径
        audio_dir = os.path.join(os.getcwd(), "uploads", "audio")
        file_path = os.path.join(audio_dir, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"录音文件不存在: {file_path}")
            raise HTTPException(status_code=404, detail="录音文件不存在")
        
        # 检查文件是否在uploads/audio目录下（安全验证）
        if not os.path.abspath(file_path).startswith(os.path.abspath(audio_dir)):
            logger.error(f"尝试访问非法路径: {file_path}")
            raise HTTPException(status_code=403, detail="访问被拒绝")
        
        logger.info(f"返回录音文件: {file_path}")
        return FileResponse(
            path=file_path,
            media_type="audio/wav",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"获取录音文件失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/landmark-image/{filename}")
async def get_landmark_image(filename: str):
    """
    获取landmark截图文件
    Args:
        filename: 截图文件名，格式如 his-123-img-1_landmarks.jpg 或示例图片
    Returns:
        FileResponse: 图片文件
    """
    import os
    logger.info(f"收到landmark截图文件请求: filename={filename}")
    # 放宽校验，允许三种示例图片名
    ALLOWED_EXAMPLES = {
        "example_07_landmarks.jpg",
        "example_08_landmarks.jpg",
        "example_010_landmarks.jpg"
    }
    if not ((filename.startswith("his-") and filename.endswith(".jpg")) or filename in ALLOWED_EXAMPLES):
        raise HTTPException(status_code=400, detail="无效的文件名格式")
    # 构建文件路径
    img_dir = os.path.join(os.getcwd(), "facial_landmarks", "img-landmarks")
    file_path = os.path.join(img_dir, filename)
    logger.info(f"file_path: {file_path}")
    # 检查文件是否存在
    if not os.path.exists(file_path):
        logger.warning(f"landmark截图文件不存在: {file_path}")
        raise HTTPException(status_code=404, detail="截图文件不存在")
    # 检查文件是否在img-landmarks目录下（安全验证）
    if not os.path.abspath(file_path).startswith(os.path.abspath(img_dir)):
        logger.error(f"尝试访问非法路径: {file_path}")
        raise HTTPException(status_code=403, detail="访问被拒绝")
    logger.info(f"返回landmark截图文件: {file_path}")
    return FileResponse(
        path=file_path,
        media_type="image/jpeg",
        filename=filename
    )