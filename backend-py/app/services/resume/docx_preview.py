import hashlib
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from loguru import logger


class DocxPreviewService:
    """Convert Word documents to PDF for browser preview."""

    PREVIEW_DIR = Path(__file__).resolve().parents[3] / "uploads" / "resume_previews"
    DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    PDF_MIME = "application/pdf"
    MAX_FILE_SIZE = 10 * 1024 * 1024

    @classmethod
    def validate_docx(cls, filename: str, content_type: str, content: bytes) -> None:
        if not filename or not filename.lower().endswith(".docx"):
            raise ValueError("当前仅支持 .docx 文件")
        if not content:
            raise ValueError("文件内容为空")
        if len(content) > cls.MAX_FILE_SIZE:
            raise ValueError("文件大小不能超过 10MB")
        if content_type and content_type not in {cls.DOCX_MIME, "application/octet-stream"}:
            logger.info(f"docx preview received content_type={content_type}, filename={filename}")

    @classmethod
    def convert_docx_to_pdf(cls, content: bytes, filename: str) -> bytes:
        cls.PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
        cached_pdf_path = cls._get_cached_pdf_path(content)
        if cached_pdf_path.exists():
            logger.info(f"命中 Word 预览 PDF 缓存: filename={filename}, path={cached_pdf_path}")
            return cached_pdf_path.read_bytes()

        soffice = cls._find_soffice()
        if not soffice:
            raise RuntimeError("未找到 LibreOffice soffice，请确认已安装并配置到 PATH")

        with tempfile.TemporaryDirectory(prefix="resume_preview_") as temp_dir:
            temp_path = Path(temp_dir)
            profile_path = temp_path / "lo_profile"
            profile_path.mkdir(parents=True, exist_ok=True)
            safe_name = f"{uuid.uuid4().hex}.docx"
            input_path = temp_path / safe_name
            input_path.write_bytes(content)

            command = [
                soffice,
                "--headless",
                "--nologo",
                "--nofirststartwizard",
                f"-env:UserInstallation=file:///{profile_path.as_posix()}",
                "--convert-to",
                "pdf",
                "--outdir",
                str(temp_path),
                str(input_path),
            ]

            logger.info(f"开始转换 Word 预览 PDF: filename={filename}")
            result = subprocess.run(
                command,
                cwd=str(temp_path),
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )

            if result.returncode != 0:
                logger.error(
                    f"LibreOffice 转换失败: code={result.returncode}, stdout={result.stdout}, stderr={result.stderr}"
                )
                raise RuntimeError("LibreOffice 转换 PDF 失败")

            pdf_path = input_path.with_suffix(".pdf")
            if not pdf_path.exists():
                pdf_files = list(temp_path.glob("*.pdf"))
                if not pdf_files:
                    logger.error(f"LibreOffice 未生成 PDF: stdout={result.stdout}, stderr={result.stderr}")
                    raise RuntimeError("LibreOffice 未生成 PDF")
                pdf_path = pdf_files[0]

            logger.info(f"Word 预览 PDF 转换完成: filename={filename}, size={pdf_path.stat().st_size}")
            pdf_content = pdf_path.read_bytes()
            cls._write_cached_pdf(cached_pdf_path, pdf_content)
            return pdf_content

    @classmethod
    def _get_cached_pdf_path(cls, content: bytes) -> Path:
        digest = hashlib.sha256(content).hexdigest()
        return cls.PREVIEW_DIR / f"{digest}.pdf"

    @classmethod
    def _write_cached_pdf(cls, pdf_path: Path, pdf_content: bytes) -> None:
        temp_path = pdf_path.with_suffix(f".{uuid.uuid4().hex}.tmp")
        temp_path.write_bytes(pdf_content)
        os.replace(temp_path, pdf_path)
        logger.info(f"写入 Word 预览 PDF 缓存: {pdf_path}")

    @staticmethod
    def _find_soffice() -> str:
        configured = os.getenv("LIBREOFFICE_PATH") or os.getenv("SOFFICE_PATH")
        candidates = []
        if configured and os.path.isdir(configured):
            candidates.append(os.path.join(configured, "soffice.exe"))
        elif configured:
            candidates.append(configured)

        candidates.extend([
            shutil.which("soffice"),
            shutil.which("libreoffice"),
            r"D:\libreoffice\program\soffice.exe",
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ])

        for candidate in candidates:
            if candidate and os.path.isfile(candidate):
                return candidate
            resolved = shutil.which(candidate) if candidate else None
            if resolved and os.path.isfile(resolved):
                return resolved

        return ""
