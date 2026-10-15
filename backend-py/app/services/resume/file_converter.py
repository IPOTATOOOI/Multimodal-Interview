import os
import tempfile
from typing import List, Optional
from loguru import logger
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image
import io
import uuid
import re
from pdfminer.high_level import extract_text

UPLOAD_RESUME_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../uploads/resume'))
os.makedirs(UPLOAD_RESUME_DIR, exist_ok=True)

class FileConverter:
    """文件格式转换服务"""
    
    @staticmethod
    def pdf_to_images(pdf_content: bytes, dpi: int = 200) -> List[bytes]:
        """
        将PDF文件转换为图片列表
        
        Args:
            pdf_content: PDF文件的二进制内容
            dpi: 图片分辨率，默认200
            
        Returns:
            List[bytes]: 图片二进制内容列表
        """
        try:
            logger.info("开始转换PDF为图片")
            
            # 使用pdf2image将PDF转换为图片
            images = convert_from_bytes(pdf_content, dpi=dpi)
            
            image_bytes_list = []
            for i, image in enumerate(images):
                # 将PIL图片转换为字节
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                image_bytes_list.append(img_byte_arr)
                logger.info(f"PDF第{i+1}页转换为图片成功，大小: {len(img_byte_arr)} bytes")
            
            logger.info(f"PDF转换完成，共生成{len(image_bytes_list)}张图片")
            return image_bytes_list
            
        except Exception as e:
            logger.error(f"PDF转图片失败: {str(e)}")
            raise Exception(f"PDF转图片失败: {str(e)}")
    
    @staticmethod
    def save_temp_image(image_bytes: bytes, prefix: str = "resume") -> str:
        """
        保存临时图片文件到 uploads/resume 目录
        """
        try:
            # 生成唯一文件名
            filename = f"{prefix}_{uuid.uuid4().hex}.png"
            file_path = os.path.join(UPLOAD_RESUME_DIR, filename)
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            logger.info(f"临时图片保存成功: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存临时图片失败: {str(e)}")
            raise Exception(f"保存临时图片失败: {str(e)}")
    
    @staticmethod
    def cleanup_temp_file(file_path: str):
        """
        清理临时文件
        
        Args:
            file_path: 临时文件路径
        """
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"临时文件清理成功: {file_path}")
        except Exception as e:
            logger.warning(f"清理临时文件失败: {file_path}, 错误: {str(e)}")
    
    @staticmethod
    def is_pdf_file(content_type: str, filename: str) -> bool:
        """
        判断是否为PDF文件
        
        Args:
            content_type: 文件MIME类型
            filename: 文件名
            
        Returns:
            bool: 是否为PDF文件
        """
        pdf_content_types = [
            'application/pdf',
            'application/x-pdf'
        ]
        
        pdf_extensions = ['.pdf']
        
        # 检查MIME类型
        if content_type.lower() in pdf_content_types:
            return True
        
        # 检查文件扩展名
        if filename and any(filename.lower().endswith(ext) for ext in pdf_extensions):
            return True
        
        return False
    
    @staticmethod
    def is_image_file(content_type: str, filename: str) -> bool:
        """
        判断是否为图片文件
        
        Args:
            content_type: 文件MIME类型
            filename: 文件名
            
        Returns:
            bool: 是否为图片文件
        """
        image_content_types = [
            'image/jpeg',
            'image/jpg',
            'image/png',
            'image/bmp',
            'image/gif',
            'image/tiff',
            'image/webp'
        ]
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
        
        # 检查MIME类型
        if content_type.lower() in image_content_types:
            return True
        
        # 检查文件扩展名
        if filename and any(filename.lower().endswith(ext) for ext in image_extensions):
            return True
        
        return False 

    @staticmethod
    def pdf_extract_text(pdf_content: bytes) -> str:
        """
        从 PDF 二进制内容中提取文本（使用 pdfminer），返回字符串。
        """
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(pdf_content)
                tmp_path = tmp.name

            text = extract_text(tmp_path)
            return text or ""
        except Exception as e:
            logger.warning(f"pdf_extract_text 失败: {str(e)}")
            return ""
        finally:
            try:
                if tmp_path and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception:
                pass

    @staticmethod
    def is_pdf_text_based(pdf_content: bytes, min_chars: int = 30) -> bool:
        """
        快速判断 PDF 是否为文本型（非扫描图像）。
        简单策略：提取文本并判断非空白字符数量是否超过阈值。
        """
        try:
            text = FileConverter.pdf_extract_text(pdf_content)
            if not text:
                return False
            # 计算非空白字符数
            non_ws_len = len(re.sub(r"\s+", "", text))
            return non_ws_len >= min_chars
        except Exception:
            return False