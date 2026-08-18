# backend/apps/ai/services/document_processor.py
"""
文档处理工具类
智能过滤无用内容，只保留对学生有价值的信息
"""

import logging
import re
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """处理各种文档格式，智能过滤无用内容"""
    
    # 无用内容特征（代理机构列表）
    AGENT_KEYWORDS = [
        'CO.,LTD', 'SDN BHD', 'SERVICES SDN', 'EDUCATION SERVICES',
        'CONSULTANCY', 'OVERSEAS', 'SHANGHAI', 'BEIJING', 'GUANGZHOU',
        'YAMANE TRADE', 'GLOBAL VISION', 'STUDY GROUP',
        'AGENT', 'REPRESENTATIVE', 'BRANCH OFFICE'
    ]
    
    # 有用内容特征（课程、学费、入学要求、专业术语）
    # ✅ 优化后：扩展到60+关键词，覆盖所有学院和专业领域
    USEFUL_KEYWORDS = [
        # 学位与学历
        'bachelor', 'master', 'phd', 'doctorate', 'diploma', 'degree', 'postgraduate', 'undergraduate',
        'associate', 'foundation', 'certificate', 'qualification',
        
        # 课程相关
        'course', 'programme', 'program', 'curriculum', 'subject', 'module', 'unit',
        'core', 'elective', 'specialization', 'specialisation', 'major', 'minor', 'track',
        
        # 入学与招生
        'entry requirement', 'admission', 'ielts', 'toefl', 'gpa', 'intake', 'application',
        'prerequisite', 'requirement', 'eligibility', 'qualify',
        
        # 学费与奖学金
        'tuition', 'fee', 'scholarship', 'bursary', 'grant', 'financial aid', 'payment',
        
        # 学期与学分
        'semester', 'trimester', 'year of study', 'credit', 'duration', 'period',
        
        # 工程类专业
        'engineering', 'engineer', 'mechanical', 'electrical', 'electronics', 'civil', 
        'software engineering', 'hardware', 'robotics', 'automation', 'mechatronics',
        'telecommunication', 'network engineering',
        
        # 计算机与IT类
        'computer', 'computing', 'programming', 'software', 'data science', 'artificial intelligence',
        'machine learning', 'cybersecurity', 'information technology', 'algorithm', 'coding',
        'database', 'web development', 'mobile app', 'cloud computing',
        
        # 商科类
        'business', 'management', 'marketing', 'finance', 'accounting', 'economics',
        'entrepreneurship', 'commerce', 'banking', 'investment', 'auditing',
        
        # 设计与媒体类
        'design', 'media', 'architecture', 'creative', 'visual', 'graphic', 'animation',
        'multimedia', 'digital media', 'communication design', 'interior design',
        
        # 学术与教学
        'faculty', 'school', 'department', 'institute', 'lecturer', 'professor', 'instructor',
        'academic', 'research', 'laboratory', 'lab', 'project', 'assignment', 'thesis',
        'dissertation', 'internship', 'industrial training', 'practicum',
        
        # 职业发展
        'career', 'employment', 'job prospect', 'graduate', 'alumni', 'industry',
        'professional', 'skill', 'competency',
        
        # 校园设施
        'campus', 'library', 'facility', 'accommodation', 'hostel', 'cafeteria',
        'learning center', 'learning centre', 'student service', 'support'
    ]
    
    @staticmethod
    def is_agent_list_line(line: str) -> bool:
        """判断是否为代理机构列表行"""
        line_upper = line.upper()
        
        # 1. 全大写且包含公司关键词
        if line.isupper() and len(line) > 10:
            if any(kw in line_upper for kw in DocumentProcessor.AGENT_KEYWORDS):
                return True
        
        # 2. 多个连续大写单词（代理名称特征）
        uppercase_words = re.findall(r'\b[A-Z]{2,}\b', line)
        if len(uppercase_words) >= 3:
            return True
        
        return False
    
    @staticmethod
    def is_useful_content(text: str) -> bool:
        """判断文本块是否包含有用信息"""
        text_lower = text.lower()
        
        # 检查是否包含有用关键词
        useful_count = sum(1 for kw in DocumentProcessor.USEFUL_KEYWORDS 
                          if kw in text_lower)
        
        # ✅ 优化：降低门槛从2个降到1个，避免过度过滤
        return useful_count >= 1  # 只要包含1个有用关键词即保留
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本，移除无用内容"""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # 跳过空行
            if not line.strip():
                continue
            
            # 跳过代理列表
            if DocumentProcessor.is_agent_list_line(line):
                continue
            
            # 跳过纯页眉页脚（如"APU is proud..."重复文本）
            if line.strip() in ["APU IS PROUD TO BE RANKED AMONG THE TOP 50 UNIVERSITIES",
                               "ASIA PACIFIC UNIVERSITY OF TECHNOLOGY & INNOVATION"]:
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    @staticmethod
    def extract_pdf_text(pdf_path: str, skip_last_pages: int = 3) -> str:
        """
        从PDF提取文本，智能过滤无用内容
        
        Args:
            pdf_path: PDF文件路径
            skip_last_pages: 跳过最后N页（通常是代理列表）
            
        Returns:
            提取的有用文本内容
        """
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            text_content = []
            
            logger.info(f"开始提取 {Path(pdf_path).name}，总页数: {total_pages}")
            
            # 只提取前 N-skip_last_pages 页
            end_page = max(1, total_pages - skip_last_pages)
            
            for page_num in range(end_page):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                # 清理文本
                cleaned_text = DocumentProcessor.clean_text(text)
                
                # 检查是否包含有用信息
                if cleaned_text.strip() and len(cleaned_text) > 100:
                    # 如果是有用内容或页数较少（前10页通常是重要内容）
                    if page_num < 10 or DocumentProcessor.is_useful_content(cleaned_text):
                        text_content.append(cleaned_text)
                        logger.debug(f"  页 {page_num+1}: 保留（{len(cleaned_text)} 字符）")
                    else:
                        logger.debug(f"  页 {page_num+1}: 跳过（无有用信息）")
            
            doc.close()
            
            full_text = "\n\n".join(text_content)
            logger.info(f"✅ 提取完成: {len(full_text)} 字符（从 {len(text_content)}/{end_page} 页）")
            
            return full_text
            
        except Exception as e:
            logger.error(f"PDF提取失败 {pdf_path}: {e}")
            raise