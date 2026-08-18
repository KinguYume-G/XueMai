"""
文件上传和处理服务

支持的文件类型：
- PDF: 简历、文档、论文
- DOCX: Word文档
- PNG/JPG/JPEG: 图片、截图、课程表（本地视觉AI分析 + OCR文字提取）
- MP4/MOV/AVI: 视频（抽取关键帧，交由视觉AI逐帧分析）
- TXT: 纯文本文件
- CSV: 数据文件
"""

import os
import logging
import mimetypes
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import hashlib

# PDF处理
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logging.warning("pdfplumber not installed, PDF support disabled")

# Word文档处理
try:
    import docx
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False
    logging.warning("python-docx not installed, DOCX support disabled")

# 图片OCR处理
try:
    from PIL import Image
    import pytesseract
    OCR_SUPPORT = True
except ImportError:
    OCR_SUPPORT = False
    logging.warning("PIL/pytesseract not installed, OCR support disabled")

logger = logging.getLogger(__name__)


class FileProcessor:
    """文件处理器基类"""
    
    ALLOWED_EXTENSIONS = {
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'txt': 'text/plain',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'csv': 'text/csv',
        'mp4': 'video/mp4',
        'mov': 'video/quicktime',
        'avi': 'video/x-msvideo',
    }

    VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi'}

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB（文档/图片）
    VIDEO_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB（视频）
    
    @classmethod
    def validate_file(cls, file_obj) -> Dict[str, Any]:
        """
        验证文件是否合法
        
        Args:
            file_obj: Django UploadedFile对象
        
        Returns:
            Dict: 验证结果
        
        Raises:
            ValueError: 文件验证失败
        """
        # 检查文件扩展名
        file_ext = Path(file_obj.name).suffix[1:].lower()
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(f"不支持的文件类型: {file_ext}")

        # 检查文件大小（视频允许更大的体积上限）
        max_size = cls.VIDEO_MAX_FILE_SIZE if file_ext in cls.VIDEO_EXTENSIONS else cls.MAX_FILE_SIZE
        if file_obj.size > max_size:
            raise ValueError(f"文件大小不能超过 {max_size / 1024 / 1024:.0f}MB")

        # 检查MIME类型
        expected_mime = cls.ALLOWED_EXTENSIONS[file_ext]
        actual_mime = file_obj.content_type
        
        if actual_mime and expected_mime != actual_mime:
            raise ValueError(f"文件 MIME 类型不匹配: 期望 {expected_mime}, 实际 {actual_mime}")
        
        return {
            "valid": True,
            "file_name": file_obj.name,
            "file_size": file_obj.size,
            "file_extension": file_ext,
            "mime_type": actual_mime,
        }
    
    @classmethod
    def compute_file_hash(cls, file_obj) -> str:
        """计算文件哈希值（用于去重）"""
        hasher = hashlib.md5()
        for chunk in file_obj.chunks():
            hasher.update(chunk)
        return hasher.hexdigest()
    
    @classmethod
    def process_file(cls, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        处理文件，提取文本内容
        
        Args:
            file_path: 文件路径
            file_type: 文件类型（扩展名）
        
        Returns:
            Dict: 处理结果，包含 extracted_text, metadata等
        """
        if file_type == 'pdf':
            return cls._process_pdf(file_path)
        elif file_type == 'docx':
            return cls._process_docx(file_path)
        elif file_type in ['png', 'jpg', 'jpeg']:
            return cls._process_image(file_path)
        elif file_type in ['mp4', 'mov', 'avi']:
            return cls._process_video(file_path)
        elif file_type == 'txt':
            return cls._process_text(file_path)
        elif file_type == 'csv':
            return cls._process_csv(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
    
    @classmethod
    def process_file_from_stream(cls, file_obj, file_type: str) -> Dict[str, Any]:
        """
        从文件流处理文件（避免路径问题）
        
        Args:
            file_obj: Django UploadedFile对象
            file_type: 文件类型（扩展名）
        
        Returns:
            Dict: 处理结果
        """
        if file_type == 'docx':
            return cls._process_docx_from_stream(file_obj)
        elif file_type == 'pdf':
            return cls._process_pdf_from_stream(file_obj)
        elif file_type == 'txt':
            # TXT直接读取
            content = file_obj.read().decode('utf-8', errors='ignore')
            return {
                "extracted_text": content,
                "line_count": content.count('\n') + 1,
                "metadata": {},
            }
        else:
            # 其他类型仍需要保存到临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_type}') as tmp:
                if hasattr(file_obj, "chunks"):
                    for chunk in file_obj.chunks():
                        tmp.write(chunk)
                else:
                    file_obj.seek(0)
                    tmp.write(file_obj.read())
                tmp_path = tmp.name
            try:
                return cls.process_file(tmp_path, file_type)
            finally:
                os.unlink(tmp_path)
    
    @classmethod
    def _process_pdf(cls, file_path: str) -> Dict[str, Any]:
        """处理PDF文件"""
        if not PDF_SUPPORT:
            raise RuntimeError("PDF处理功能未安装，请安装 pdfplumber")
        
        try:
            with pdfplumber.open(file_path) as pdf:
                text_parts = []
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"[Page {page_num}]\n{text}")
                
                extracted_text = "\n\n".join(text_parts)
                
                return {
                    "extracted_text": extracted_text,
                    "page_count": len(pdf.pages),
                    "metadata": pdf.metadata or {},
                }
        except Exception as e:
            logger.error(f"PDF处理失败: {e}", exc_info=True)
            raise RuntimeError(f"PDF处理失败: {str(e)}")
    
    @classmethod
    def _process_docx(cls, file_path: str) -> Dict[str, Any]:
        """处理Word文档"""
        if not DOCX_SUPPORT:
            raise RuntimeError("DOCX处理功能未安装，请安装 python-docx")
        
        try:
            doc = docx.Document(file_path)
            
            # 提取段落文本
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)
            
            # 提取表格文本
            tables_text = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells)
                    if row_text.strip():
                        tables_text.append(row_text)
            
            extracted_text = "\n\n".join(paragraphs)
            if tables_text:
                extracted_text += "\n\n[表格数据]\n" + "\n".join(tables_text)
            
            return {
                "extracted_text": extracted_text,
                "paragraph_count": len(paragraphs),
                "table_count": len(doc.tables),
                "metadata": {},
            }
        except Exception as e:
            logger.error(f"DOCX处理失败: {e}", exc_info=True)
            raise RuntimeError(f"DOCX处理失败: {str(e)}")
    
    @classmethod
    def _process_docx_from_stream(cls, file_obj) -> Dict[str, Any]:
        """从文件流处理Word文档（避免路径问题）"""
        if not DOCX_SUPPORT:
            raise RuntimeError("DOCX处理功能未安装，请安装 python-docx")
        
        try:
            from io import BytesIO
            
            # 读取文件内容到BytesIO
            file_obj.seek(0)
            file_bytes = file_obj.read()
            file_stream = BytesIO(file_bytes)
            
            # 使用BytesIO打开文档
            doc = docx.Document(file_stream)
            
            # 提取段落文本
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)
            
            # 提取表格文本
            tables_text = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells)
                    if row_text.strip():
                        tables_text.append(row_text)
            
            # ✅ 新增：提取页眉页脚内容
            headers_footers = []
            for section in doc.sections:
                # 页眉
                if section.header:
                    for para in section.header.paragraphs:
                        if para.text.strip():
                            headers_footers.append(para.text)
                # 页脚
                if section.footer:
                    for para in section.footer.paragraphs:
                        if para.text.strip():
                            headers_footers.append(para.text)
            
            # ✅ 新增：尝试提取文本框和形状中的文字（通过XML）
            textbox_content = []
            try:
                from docx.oxml.text.paragraph import CT_P
                from docx.oxml.table import CT_Tbl
                from docx.oxml import parse_xml
                
                # 遍历文档的XML来查找文本框
                body_element = doc.element.body
                for child in body_element.iter():
                    # 查找文本框元素 (w:txbxContent)
                    if hasattr(child, 'tag') and 'txbxContent' in child.tag:
                        for para_elem in child.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                            para_text = []
                            for text_elem in para_elem.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                                if text_elem.text:
                                    para_text.append(text_elem.text)
                            if para_text:
                                textbox_content.append(''.join(para_text))
            except Exception as e:
                logger.warning(f"提取文本框内容失败: {e}")
            
            # 组合所有文本
            all_text_parts = []
            
            if paragraphs:
                all_text_parts.append("\n\n".join(paragraphs))
            
            if tables_text:
                all_text_parts.append("\n\n[表格数据]\n" + "\n".join(tables_text))
            
            if headers_footers:
                all_text_parts.append("\n\n[页眉页脚]\n" + "\n".join(headers_footers))
            
            if textbox_content:
                all_text_parts.append("\n\n[文本框内容]\n" + "\n".join(textbox_content))
            
            extracted_text = "\n\n".join(all_text_parts)
            
            logger.info(f"DOCX提取统计: 段落={len(paragraphs)}, 表格={len(doc.tables)}, 页眉页脚={len(headers_footers)}, 文本框={len(textbox_content)}")
            
            return {
                "extracted_text": extracted_text,
                "paragraph_count": len(paragraphs),
                "table_count": len(doc.tables),
                "textbox_count": len(textbox_content),
                "metadata": {},
            }
        except Exception as e:
            logger.error(f"DOCX流处理失败: {e}", exc_info=True)
            raise RuntimeError(f"DOCX流处理失败: {str(e)}")
    
    @classmethod
    def _process_pdf_from_stream(cls, file_obj) -> Dict[str, Any]:
        """从文件流处理PDF"""
        if not PDF_SUPPORT:
            raise RuntimeError("PDF处理功能未安装")
        
        try:
            from io import BytesIO
            file_obj.seek(0)
            pdf_bytes = file_obj.read()
            pdf_stream = BytesIO(pdf_bytes)
            
            with pdfplumber.open(pdf_stream) as pdf:
                text_parts = []
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"[Page {page_num}]\n{text}")
                
                extracted_text = "\n\n".join(text_parts)
                
                return {
                    "extracted_text": extracted_text,
                    "page_count": len(pdf.pages),
                    "metadata": {},
                }
        except Exception as e:
            logger.error(f"PDF流处理失败: {e}", exc_info=True)
            raise RuntimeError(f"PDF流处理失败: {str(e)}")
    
    @classmethod
    def _get_vision_client(cls):
        """获取用于图片/视频帧分析的本地视觉AI客户端（始终走 Ollama，不受 AI_CLIENT_TYPE 影响）"""
        from django.conf import settings
        from ..clients.ollama_client import OllamaClient

        return OllamaClient(
            base_url=getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434"),
            vision_model=getattr(settings, "OLLAMA_VISION_MODEL", "llama3.2-vision:11b"),
            timeout=getattr(settings, "OLLAMA_VISION_TIMEOUT", 180),
        )

    @classmethod
    def _process_image(cls, file_path: str) -> Dict[str, Any]:
        """
        处理图片：优先使用本地视觉AI（如 llama3.2-vision）生成内容描述，
        使 AI 能真正"看懂"图片（物体、场景、图表等），而不仅仅是提取图片中的文字。
        若安装了 pytesseract 且系统装有 Tesseract，再额外补充 OCR 文字提取。
        """
        # 尽量获取图片基础信息（PIL 通常总是可用，见文件顶部导入逻辑）
        image_size = None
        image_format = None
        try:
            with Image.open(file_path) as img:
                image_size = img.size
                image_format = img.format
        except Exception as e:
            logger.warning(f"读取图片元信息失败: {e}")

        # 1) 视觉AI分析（主要内容来源）
        vision_description = ""
        vision_error = None
        try:
            with open(file_path, "rb") as f:
                image_bytes = f.read()
            client = cls._get_vision_client()
            vision_description = client.analyze_image(image_bytes).strip()
        except Exception as e:
            logger.error(f"视觉AI图片分析失败: {e}", exc_info=True)
            vision_error = str(e)

        # 2) OCR文字提取（可选补充，仅当 pytesseract + Tesseract 二进制均可用时生效）
        ocr_text = ""
        if OCR_SUPPORT:
            try:
                with Image.open(file_path) as img:
                    ocr_text = pytesseract.image_to_string(img, lang='chi_sim+eng').strip()
            except Exception as e:
                logger.warning(f"OCR识别失败（不影响视觉AI分析结果）: {e}")

        parts = []
        if vision_description:
            parts.append(f"[图片内容分析]\n{vision_description}")
        if ocr_text:
            parts.append(f"[图片中的文字（OCR提取）]\n{ocr_text}")

        extracted_text = "\n\n".join(parts)

        if not extracted_text:
            return {
                "extracted_text": "",
                "error": f"图片分析失败: {vision_error or '未知错误'}",
                "image_size": image_size,
                "image_format": image_format,
                "metadata": {},
            }

        return {
            "extracted_text": extracted_text,
            "image_size": image_size,
            "image_format": image_format,
            "metadata": {
                "has_vision_description": bool(vision_description),
                "has_ocr_text": bool(ocr_text),
            },
        }

    @classmethod
    def _ffmpeg_path(cls) -> Optional[str]:
        return shutil.which("ffmpeg")

    @classmethod
    def _ffprobe_path(cls) -> Optional[str]:
        return shutil.which("ffprobe")

    @classmethod
    def _get_video_duration(cls, file_path: str) -> Optional[float]:
        """使用 ffprobe 获取视频时长（秒），失败返回 None"""
        ffprobe = cls._ffprobe_path()
        if not ffprobe:
            return None
        try:
            result = subprocess.run(
                [
                    ffprobe, "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    file_path,
                ],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except Exception as e:
            logger.warning(f"获取视频时长失败: {e}")
        return None

    @classmethod
    def _extract_frame(cls, file_path: str, timestamp: float, output_path: str) -> bool:
        """使用 ffmpeg 从视频中抽取指定时间点的一帧，保存为图片"""
        ffmpeg = cls._ffmpeg_path()
        if not ffmpeg:
            return False
        try:
            result = subprocess.run(
                [
                    ffmpeg, "-y",
                    "-ss", str(max(timestamp, 0)),
                    "-i", file_path,
                    "-frames:v", "1",
                    "-q:v", "2",
                    output_path,
                ],
                capture_output=True, timeout=30,
            )
            return (
                result.returncode == 0
                and os.path.exists(output_path)
                and os.path.getsize(output_path) > 0
            )
        except Exception as e:
            logger.warning(f"提取视频帧失败 (t={timestamp}): {e}")
            return False

    @classmethod
    def _process_video(cls, file_path: str) -> Dict[str, Any]:
        """
        处理视频：抽取若干代表性关键帧，逐帧交给本地视觉AI分析，
        再将各帧的描述拼接为对视频内容的整体概述。

        注意：这是基于关键帧的"视觉摘要"，并非完整的视频理解（不含音频/字幕转录），
        依赖服务器已安装 ffmpeg/ffprobe，若未安装则明确返回不支持提示。
        """
        if not cls._ffmpeg_path() or not cls._ffprobe_path():
            logger.warning("视频处理跳过：未检测到 ffmpeg/ffprobe")
            return {
                "extracted_text": "",
                "error": "视频分析依赖 ffmpeg，当前服务器环境未安装，暂不支持视频内容分析",
                "metadata": {},
            }

        duration = cls._get_video_duration(file_path)
        if duration and duration > 0:
            # 避开首尾边界帧，取时间轴上具代表性的三个点
            timestamps = [round(duration * f, 2) for f in (0.1, 0.5, 0.85)]
        else:
            # 无法探测时长时的保守回退
            timestamps = [1.0, 3.0, 5.0]

        frame_descriptions = []
        with tempfile.TemporaryDirectory() as tmp_dir:
            for idx, ts in enumerate(timestamps, 1):
                frame_path = os.path.join(tmp_dir, f"frame_{idx}.jpg")
                if not cls._extract_frame(file_path, ts, frame_path):
                    logger.warning(f"视频帧抽取失败，跳过 (t={ts})")
                    continue
                try:
                    with open(frame_path, "rb") as f:
                        frame_bytes = f.read()
                    client = cls._get_vision_client()
                    frame_prompt = (
                        "这是一段视频中的一帧画面（该帧约位于视频第 {ts:.1f} 秒"
                        + (f"，视频总时长约 {duration:.0f} 秒" if duration else "")
                        + "）。请用中文描述这一帧画面中的内容：场景、人物/物体、"
                        "正在发生的动作，以及画面中任何可见的文字。"
                    ).format(ts=ts)
                    description = client.analyze_image(frame_bytes, prompt=frame_prompt).strip()
                    if description:
                        frame_descriptions.append(f"[视频画面 {idx}，约第 {ts:.1f} 秒]\n{description}")
                except Exception as e:
                    logger.warning(f"视频帧AI分析失败 (t={ts}): {e}")

        if not frame_descriptions:
            return {
                "extracted_text": "",
                "error": "视频关键帧分析失败，未能生成任何帧描述",
                "duration_seconds": duration,
                "metadata": {},
            }

        extracted_text = (
            "以下是基于视频关键帧的AI视觉分析摘要（抽取了几个代表性时间点的画面，"
            "并非逐秒的完整视频内容，也不包含音频）：\n\n"
            + "\n\n".join(frame_descriptions)
        )

        return {
            "extracted_text": extracted_text,
            "duration_seconds": duration,
            "frame_count": len(frame_descriptions),
            "metadata": {"analysis_type": "keyframe_vision"},
        }

    @classmethod
    def _process_text(cls, file_path: str) -> Dict[str, Any]:
        """处理纯文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            return {
                "extracted_text": text,
                "line_count": text.count('\n') + 1,
                "metadata": {},
            }
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    text = f.read()
                return {
                    "extracted_text": text,
                    "line_count": text.count('\n') + 1,
                    "metadata": {"encoding": "gbk"},
                }
            except Exception as e:
                logger.error(f"文本文件读取失败: {e}", exc_info=True)
                raise RuntimeError(f"文本文件读取失败: {str(e)}")
    
    @classmethod
    def _process_csv(cls, file_path: str) -> Dict[str, Any]:
        """处理CSV文件"""
        try:
            import csv
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # 转换为文本表示
            text_lines = []
            for row in rows:
                text_lines.append(" | ".join(row))
            
            extracted_text = "\n".join(text_lines)
            
            return {
                "extracted_text": extracted_text,
                "row_count": len(rows),
                "column_count": len(rows[0]) if rows else 0,
                "metadata": {},
            }
        except Exception as e:
            logger.error(f"CSV文件处理失败: {e}", exc_info=True)
            raise RuntimeError(f"CSV文件处理失败: {str(e)}")



