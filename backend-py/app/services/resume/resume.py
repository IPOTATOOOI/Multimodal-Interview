import os
import threading
from typing import Dict, Any

from rapidocr import RapidOCR
from loguru import logger
from app.services.resume.spark import SparkService
from app.services.resume.file_converter import FileConverter
from app.models.enums import ProcessStatus
import uuid
import asyncio
from datetime import datetime, timedelta
from app.services.ask.initiate import initiate_interview
import concurrent.futures

from app.core.config import settings
from app.core.redis_cache import build_cache_key, fingerprint_bytes, get_cache_json, set_cache_json, delete_cache, get_redis_client

class ResumeService:
    # 添加线程池
    _thread_pool = concurrent.futures.ThreadPoolExecutor(
        max_workers=4,
        thread_name_prefix="resume_process"
    )

    _rapidocr_engine = None
    _rapidocr_lock = threading.Lock()

    # 用于存储处理状态和结果的内存字典（仅在 Redis 不可用时回退）
    _process_store: Dict[str, Dict[str, Any]] = {}

    @classmethod
    async def cleanup_old_processes(cls):
        """清理超过30分钟的处理记录"""
        # 如果启用了 Redis，则依赖 Redis 的 TTL 来清理过期记录
        if get_redis_client() is not None:
            return

        current_time = datetime.now()
        expired_ids = [
            pid for pid, data in cls._process_store.items()
            if current_time - data['timestamp'] > timedelta(minutes=30)
        ]
        for pid in expired_ids:
            cls._process_store.pop(pid, None)

    @classmethod
    async def start_processing(cls, user_id: str) -> str:
        """初始化处理任务"""
        await cls.cleanup_old_processes()
        process_id = str(uuid.uuid4())

        redis_client = get_redis_client()
        key = build_cache_key("resume", "process", process_id)
        payload = {
            "status": ProcessStatus.PROCESSING.value,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "result": None,
            "error": None,
        }

        if redis_client is not None:
            ttl = settings.REDIS_CACHE_PROCESS_TTL if getattr(settings, "REDIS_CACHE_PROCESS_TTL", None) else None
            await set_cache_json(key, payload, ttl=ttl)
        else:
            cls._process_store[process_id] = {
                "status": ProcessStatus.PROCESSING,
                "user_id": user_id,
                "timestamp": datetime.now(),
                "result": None,
                "error": None
            }

        return process_id

    @classmethod
    async def process_resume_async(cls, process_id: str, contents: bytes, user_id: str,
                                   domain: str, position: str, content_type: str,
                                   filename: str):
        """异步处理简历"""
        try:
            # 直接在主事件循环中执行异步的 process_resume，
            # 内部会使用线程池来处理同步OCR/图像转换任务，避免创建新的 event loop。
            result = await cls.process_resume(contents, user_id, domain, position, content_type, filename)
            if result.get("code") == 200:
                # 创建面试历史记录、生成首问、保存笔试题（交互式模式，单次调用）
                loop = asyncio.get_running_loop()
                init_result = await loop.run_in_executor(
                    cls._thread_pool, initiate_interview, user_id, domain, position
                )
                # 更新 Redis 或回退到内存
                key = build_cache_key("resume", "process", process_id)
                existing = await get_cache_json(key)
                new_payload = {
                    "status": ProcessStatus.COMPLETED.value,
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                    "result": {
                        **result,
                        **init_result["data"]
                    },
                    "error": None
                }

                if existing is not None:
                    # 合并保留原始 timestamp 与 user_id
                    new_payload["timestamp"] = existing.get("timestamp", new_payload["timestamp"]) 
                    new_payload["user_id"] = existing.get("user_id", new_payload["user_id"]) 

                if get_redis_client() is not None:
                    ttl = settings.REDIS_CACHE_PROCESS_TTL if getattr(settings, "REDIS_CACHE_PROCESS_TTL", None) else None
                    await set_cache_json(key, new_payload, ttl=ttl)
                else:
                    cls._process_store.get(process_id, {}).update({
                        "status": ProcessStatus.COMPLETED,
                        "result": {
                            **result,
                            **init_result["data"]
                        }
                    })
            else:
                # 失败分支
                key = build_cache_key("resume", "process", process_id)
                existing = await get_cache_json(key)
                new_payload = {
                    "status": ProcessStatus.FAILED.value,
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                    "result": None,
                    "error": result.get("message")
                }
                if existing is not None:
                    new_payload["timestamp"] = existing.get("timestamp", new_payload["timestamp"]) 
                    new_payload["user_id"] = existing.get("user_id", new_payload["user_id"]) 

                if get_redis_client() is not None:
                    ttl = settings.REDIS_CACHE_PROCESS_TTL if getattr(settings, "REDIS_CACHE_PROCESS_TTL", None) else None
                    await set_cache_json(key, new_payload, ttl=ttl)
                else:
                    cls._process_store.get(process_id, {}).update({
                        "status": ProcessStatus.FAILED,
                        "error": result.get("message")
                    })
        except Exception as e:
            # 异常时也写入 Redis 或内存
            key = build_cache_key("resume", "process", process_id)
            existing = await get_cache_json(key)
            new_payload = {
                "status": ProcessStatus.FAILED.value,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "result": None,
                "error": str(e)
            }
            if existing is not None:
                new_payload["timestamp"] = existing.get("timestamp", new_payload["timestamp"]) 
                new_payload["user_id"] = existing.get("user_id", new_payload["user_id"]) 

            if get_redis_client() is not None:
                ttl = settings.REDIS_CACHE_PROCESS_TTL if getattr(settings, "REDIS_CACHE_PROCESS_TTL", None) else None
                await set_cache_json(key, new_payload, ttl=ttl)
            else:
                cls._process_store.get(process_id, {}).update({
                    "status": ProcessStatus.FAILED,
                    "error": str(e)
                })

    @classmethod
    async def get_process_status(cls, process_id: str) -> Dict[str, Any]:
        """获取处理状态和结果"""
        # 优先从 Redis 读取
        key = build_cache_key("resume", "process", process_id)
        cached = await get_cache_json(key)
        if cached is not None:
            return {
                "status": cached.get("status", ProcessStatus.FAILED.value),
                "result": cached.get("result"),
                "error": cached.get("error")
            }

        # 回退到内存存储
        if process_id not in cls._process_store:
            return {
                "status": ProcessStatus.FAILED,
                "error": "Process not found"
            }
        return {
            "status": cls._process_store[process_id]["status"],
            "result": cls._process_store[process_id]["result"],
            "error": cls._process_store[process_id]["error"]
        }

    @classmethod
    def _get_rapidocr_engine(cls):
        """延迟初始化 RapidOCR 引擎，避免在启动阶段加载模型。"""
        if cls._rapidocr_engine is not None:
            return cls._rapidocr_engine

        with cls._rapidocr_lock:
            if cls._rapidocr_engine is None:
                cls._rapidocr_engine = RapidOCR()
                logger.info("RapidOCR 引擎初始化成功")

        return cls._rapidocr_engine

    @staticmethod
    def _extract_rapidocr_text(ocr_result: Any) -> str:
        """从 RapidOCR 返回结果中提取文本。"""
        if ocr_result is None:
            return ""

        txts = None
        if hasattr(ocr_result, "txts"):
            txts = getattr(ocr_result, "txts")
        elif isinstance(ocr_result, dict):
            txts = ocr_result.get("txts")
        elif isinstance(ocr_result, tuple) and len(ocr_result) >= 2:
            txts = ocr_result[1]

        if not txts:
            return ""

        if isinstance(txts, str):
            return txts.strip()

        if isinstance(txts, list):
            return "\n".join(
                text.strip() for text in txts
                if isinstance(text, str) and text.strip()
            ).strip()

        return str(txts).strip()

    @staticmethod
    def process_single_image_sync(image_bytes: bytes) -> str:
        """同步处理单张图片：使用 RapidOCR 提取文本。"""
        try:
            engine = ResumeService._get_rapidocr_engine()
            text_content = ResumeService._extract_rapidocr_text(engine(image_bytes))

            if text_content:
                logger.info("RapidOCR 识别成功")
                print("\n[RapidOCR] 单图识别结果:\n" + text_content + "\n")
                return text_content

            raise Exception("RapidOCR 未识别到文本")

        except Exception as error:
            logger.error(f"RapidOCR 识别失败，原因: {error}")
            raise Exception(f"RapidOCR识别失败: {error}")

    @staticmethod
    async def process_resume(file_content: bytes, user_id: str, domain: str, position: str,
                             content_type: str = None, filename: str = None) -> Dict[str, Any]:
        """处理简历文件：支持PDF和图片格式，OCR识别后通过星火大模型解析为结构化数据"""
        try:
            file_fingerprint = fingerprint_bytes(file_content)
            text_content = ""
            # 1. 判断文件类型并处理
            if FileConverter.is_pdf_file(content_type, filename):
                # PDF文件：先判断是否为文本型PDF，若是则直接提取文本，否则转换为图片并OCR
                logger.info(f"检测到PDF文件: {filename}")
                try:
                    if FileConverter.is_pdf_text_based(file_content):
                        logger.info(f"检测到文本型PDF，直接提取文本: {filename}")
                        ocr_cache_key = build_cache_key("resume", "ocr", "pdf_text", file_fingerprint)
                        cached_text = await get_cache_json(ocr_cache_key)
                        if isinstance(cached_text, dict) and cached_text.get("text"):
                            text_content = cached_text["text"]
                            logger.info(f"命中文本型PDF缓存: filename={filename}")
                        else:
                            text_content = FileConverter.pdf_extract_text(file_content)
                            if text_content:
                                await set_cache_json(
                                    ocr_cache_key,
                                    {"text": text_content, "input_kind": "pdf_text"},
                                    ttl=settings.REDIS_CACHE_RESUME_OCR_TTL,
                                )
                    else:
                        # 传统扫描件/图片型PDF，走原有的 PDF->图片->OCR 路径
                        ocr_cache_key = build_cache_key("resume", "ocr", "pdf_image", file_fingerprint)
                        cached_text = await get_cache_json(ocr_cache_key)
                        if isinstance(cached_text, dict) and cached_text.get("text"):
                            text_content = cached_text["text"]
                            logger.info(f"命中图片型PDF缓存: filename={filename}")
                        else:
                            image_bytes_list = FileConverter.pdf_to_images(file_content)

                            if not image_bytes_list:
                                return {
                                    "code": 400,
                                    "message": "PDF转换图片失败",
                                    "data": None
                                }

                            # 使用线程池处理所有图片页面
                            loop = asyncio.get_event_loop()
                            tasks = [
                                loop.run_in_executor(
                                    ResumeService._thread_pool,
                                    ResumeService.process_single_image_sync,
                                    image_bytes
                                )
                                for image_bytes in image_bytes_list
                            ]

                            # 等待所有页面处理完成
                            all_text_content = []
                            page_results = await asyncio.gather(*tasks, return_exceptions=True)

                            for i, page_result in enumerate(page_results):
                                if isinstance(page_result, Exception):
                                    logger.warning(f"PDF第{i+1}页OCR识别失败: {str(page_result)}")
                                    continue
                                all_text_content.append(f"=== 第{i+1}页 ===\n{page_result}")
                                logger.info(f"PDF第{i+1}页OCR识别成功")

                            if not all_text_content:
                                return {
                                    "code": 400,
                                    "message": "所有PDF页面OCR识别均失败",
                                    "data": None
                                }

                            # 合并所有页面的文本
                            text_content = "\n\n".join(all_text_content)
                            await set_cache_json(
                                ocr_cache_key,
                                {"text": text_content, "input_kind": "pdf_image"},
                                ttl=settings.REDIS_CACHE_RESUME_OCR_TTL,
                            )
                            print("\n[RapidOCR] PDF识别结果:\n" + text_content + "\n")
                except Exception as e:
                    return {
                        "code": 500,
                        "message": f"处理PDF文件时出错: {str(e)}",
                        "data": None
                    }

            elif FileConverter.is_image_file(content_type, filename):
                # 图片文件，直接OCR识别
                logger.info(f"检测到图片文件: {filename}")
                ocr_cache_key = build_cache_key("resume", "ocr", "image", file_fingerprint)
                cached_text = await get_cache_json(ocr_cache_key)
                if isinstance(cached_text, dict) and cached_text.get("text"):
                    text_content = cached_text["text"]
                    logger.info(f"命中图片OCR缓存: filename={filename}")
                else:
                    # 使用线程池执行OCR识别
                    loop = asyncio.get_event_loop()
                    text_content = await loop.run_in_executor(
                        ResumeService._thread_pool,
                        ResumeService.process_single_image_sync,
                        file_content
                    )
                    if text_content:
                        await set_cache_json(
                            ocr_cache_key,
                            {"text": text_content, "input_kind": "image"},
                            ttl=settings.REDIS_CACHE_RESUME_OCR_TTL,
                        )

            else:
                return {
                    "code": 400,
                    "message": f"不支持的文件格式: {content_type}。支持PDF和图片格式",
                    "data": None
                }

            if not text_content:
                return {
                    "code": 400,
                    "message": "OCR识别失败或未识别到文本",
                    "data": None
                }

            # 2. 使用星火大模型处理文本（保持异步）
            structured_data = await SparkService.process_text_to_json(text_content, user_id, domain, position)

            # 3. 处理返回结果
            if isinstance(structured_data, dict) and "error" in structured_data:
                return {
                    "code": 500,
                    "message": structured_data["error"],
                    "data": None
                }

            # 4. 构建成功响应
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "resume_info": structured_data,
                    "original_text": text_content,
                    "file_type": "PDF" if FileConverter.is_pdf_file(content_type, filename) else "IMAGE"
                }
            }

        except Exception as e:
            return {
                "code": 500,
                "message": f"简历处理失败: {str(e)}",
                "data": None
            }