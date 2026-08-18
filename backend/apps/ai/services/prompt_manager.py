"""
Prompt Template Engine - 支持动态变量的 Prompt 模板系统

功能：
1. 加载 Prompt 文件
2. 支持动态变量替换：{user_name}, {university}, {major}, {grade} 等
3. 条件渲染
4. 模板缓存
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)


class PromptTemplate:
    """Prompt 模板类"""
    
    def __init__(self, template_path: Path):
        """
        初始化 Prompt 模板
        
        Args:
            template_path: Prompt 文件路径
        """
        self.template_path = template_path
        self.raw_content = ""
        self._load()
    
    def _load(self):
        """加载模板文件"""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                self.raw_content = f.read()
            logger.debug(f"[PromptTemplate] 加载成功: {self.template_path.name}")
        except Exception as e:
            logger.error(f"[PromptTemplate] 加载失败 {self.template_path}: {e}")
            raise
    
    def render(self, variables: Optional[Dict[str, Any]] = None) -> str:
        """
        渲染模板（替换变量）
        
        Args:
            variables: 变量字典，如 {"user_name": "张三", "university": "APU"}
            
        Returns:
            渲染后的 Prompt 文本
        """
        if not variables:
            variables = {}
        
        # 添加默认变量
        defaults = {
            "user_name": "同学",
            "university": "APU",
            "major": "计算机科学",
            "grade": "大三",
            "platform": "UniPulse Asia"
        }
        
        # 合并用户变量和默认变量（用户变量优先）
        merged_vars = {**defaults, **variables}
        
        # 替换变量
        content = self.raw_content
        for key, value in merged_vars.items():
            placeholder = f"{{{key}}}"
            if placeholder in content:
                content = content.replace(placeholder, str(value))
                logger.debug(f"[PromptTemplate] 替换变量: {placeholder} -> {value}")
        
        return content
    
    def get_variables(self) -> list:
        """
        提取模板中使用的所有变量
        
        Returns:
            变量列表，如 ["user_name", "university"]
        """
        # 匹配 {variable_name} 格式的变量
        pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
        variables = re.findall(pattern, self.raw_content)
        return list(set(variables))  # 去重


class PromptManager:
    """Prompt 管理器 - 负责加载和缓存所有 Prompts"""
    
    def __init__(self, prompts_dir: Optional[Path] = None):
        """
        初始化 Prompt 管理器
        
        Args:
            prompts_dir: Prompts 目录路径，默认为 apps/ai/prompts/
        """
        if prompts_dir is None:
            # 默认路径：相对于当前文件
            prompts_dir = Path(__file__).parent.parent / "prompts"
        
        self.prompts_dir = prompts_dir
        self._cache: Dict[str, PromptTemplate] = {}
        
        logger.info(f"[PromptManager] 初始化，Prompts 目录: {self.prompts_dir}")
    
    def get_template(self, prompt_file: str) -> PromptTemplate:
        """
        获取 Prompt 模板（带缓存）
        
        Args:
            prompt_file: Prompt 文件名或相对路径，如 "course_query.txt" 或 "prompts/course_query.txt"
            
        Returns:
            PromptTemplate 对象
        """
        # 规范化路径
        if prompt_file.startswith("prompts/"):
            prompt_file = prompt_file[8:]  # 去掉 "prompts/" 前缀
        
        # 检查缓存
        if prompt_file in self._cache:
            logger.debug(f"[PromptManager] 使用缓存: {prompt_file}")
            return self._cache[prompt_file]
        
        # 加载模板
        template_path = self.prompts_dir / prompt_file
        
        if not template_path.exists():
            logger.error(f"[PromptManager] 文件不存在: {template_path}")
            # 降级到通用 prompt
            fallback_path = self.prompts_dir / "general.txt"
            if fallback_path.exists():
                logger.warning(f"[PromptManager] 降级使用 general.txt")
                template_path = fallback_path
            else:
                raise FileNotFoundError(f"Prompt 文件不存在: {prompt_file}")
        
        template = PromptTemplate(template_path)
        
        # 缓存
        self._cache[prompt_file] = template
        logger.info(f"[PromptManager] 加载并缓存: {prompt_file}")
        
        return template
    
    def render_prompt(self, prompt_file: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """
        一步渲染 Prompt（便捷方法）
        
        Args:
            prompt_file: Prompt 文件名
            variables: 变量字典
            
        Returns:
            渲染后的 Prompt 文本
        """
        template = self.get_template(prompt_file)
        return template.render(variables)
    
    def list_prompts(self) -> list:
        """
        列出所有可用的 Prompt 文件
        
        Returns:
            Prompt 文件名列表
        """
        try:
            prompt_files = []
            for file_path in self.prompts_dir.glob("*.txt"):
                if file_path.stem != "__init__":
                    prompt_files.append(file_path.name)
            
            logger.info(f"[PromptManager] 找到 {len(prompt_files)} 个 Prompt 文件")
            return sorted(prompt_files)
        except Exception as e:
            logger.error(f"[PromptManager] 列出 Prompts 失败: {e}")
            return []
    
    def validate_prompts(self) -> Dict[str, Any]:
        """
        验证所有 Prompt 文件是否可加载
        
        Returns:
            验证结果字典
        """
        results = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        prompt_files = self.list_prompts()
        results["total"] = len(prompt_files)
        
        for prompt_file in prompt_files:
            try:
                template = self.get_template(prompt_file)
                variables = template.get_variables()
                
                results["success"] += 1
                results["details"].append({
                    "file": prompt_file,
                    "status": "ok",
                    "variables": variables,
                    "size": len(template.raw_content)
                })
                
                logger.info(f"[Validation] ✓ {prompt_file} ({len(variables)} 变量)")
                
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "file": prompt_file,
                    "status": "error",
                    "error": str(e)
                })
                
                logger.error(f"[Validation] ✗ {prompt_file}: {e}")
        
        return results
    
    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        logger.info("[PromptManager] 缓存已清空")


# ========== 全局单例 ==========
_prompt_manager = None

def get_prompt_manager() -> PromptManager:
    """获取全局 PromptManager 单例"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager






