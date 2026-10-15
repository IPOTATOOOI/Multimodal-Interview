import subprocess
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import Response
from loguru import logger
from urllib.parse import quote
from app.services.resume.resume import ResumeService
from app.services.resume.docx_preview import DocxPreviewService
from app.services.ask.initiate import initiate_interview
from app.models.enums import ProcessStatus

# 配置日志
logger.add("logs/api_{time}.log", rotation="500 MB", encoding="utf-8")

router = APIRouter(prefix="/resume", tags=["resume"])

@router.post("/preview-pdf")
async def preview_resume_pdf(file: UploadFile = File(...)):
    """
    将 .docx 简历转换为 PDF，用于前端原版式预览。
    需要服务器安装 LibreOffice，并确保 soffice 可执行文件在 PATH 中，
    或通过 LIBREOFFICE_PATH / SOFFICE_PATH 指定完整路径。
    """
    try:
        contents = await file.read()
        DocxPreviewService.validate_docx(file.filename, file.content_type, contents)
        pdf_content = DocxPreviewService.convert_docx_to_pdf(contents, file.filename)

        preview_name = (file.filename or "resume.docx").rsplit(".", 1)[0] + ".pdf"
        encoded_name = quote(preview_name)
        return Response(
            content=pdf_content,
            media_type=DocxPreviewService.PDF_MIME,
            headers={
                "Content-Disposition": f"inline; filename*=UTF-8''{encoded_name}",
                "Cache-Control": "no-store",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except subprocess.TimeoutExpired:
        logger.error(f"Word 预览 PDF 转换超时: filename={file.filename}")
        raise HTTPException(status_code=504, detail="Word 转 PDF 超时，请稍后重试")
    except RuntimeError as e:
        logger.error(f"Word 预览 PDF 转换失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception(f"Word 预览 PDF 接口异常: filename={file.filename}")
        raise HTTPException(status_code=500, detail=f"Word 预览 PDF 生成失败: {str(e)}")

@router.post("/upload")
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    domain: str = Form(...),
    position: str = Form(...),
    user_id: str = Form(...)
):
    """
    上传简历文件并进行OCR识别，成功后自动创建面试历史记录并生成面试问题
    支持PDF和图片格式
    """
    try:
        logger.info(f"收到简历上传请求: user_id={user_id}, domain={domain}, position={position}, filename={file.filename}, content_type={file.content_type}")
        
        # 读取文件内容
        contents = await file.read()
        
        # 开始异步处理，获取处理ID
        process_id = await ResumeService.start_processing(user_id)
        
        # 添加后台任务
        background_tasks.add_task(
            ResumeService.process_resume_async,
            process_id,
            contents,
            user_id,
            domain,
            position,
            file.content_type,
            file.filename
        )
        
        return {
            "code": 202,
            "message": "Resume processing started",
            "data": {
                "process_id": process_id,
                "status": ProcessStatus.PROCESSING
            }
        }
            
    except Exception as e:
        error_msg = f"简历上传处理失败: {str(e)}"
        logger.error(error_msg)
        return {
            "code": 500,
            "message": error_msg,
            "data": None
        }

@router.get("/status/{process_id}")
async def check_process_status(process_id: str):
    """查询简历处理状态"""
    try:
        status_info = await ResumeService.get_process_status(process_id)
        return {
            "code": 200,
            "message": "success",
            "data": status_info
        }
    except Exception as e:
        logger.error(f"查询处理状态失败: {str(e)}")
        return {
            "code": 500,
            "message": str(e),
            "data": None
        }
