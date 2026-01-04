# -*- coding: utf-8 -*-
"""
论文结构识别模块
识别经管论文的各个组成部分
"""

from typing import Dict, List, Optional
import re
from core.llm import get_llm_client
from core.prompts import PromptTemplates


class StructureRecognizer:
    """
    论文结构识别器
    
    识别论文的各个组成部分：标题、摘要、引言、文献综述等
    
    使用示例:
        recognizer = StructureRecognizer()
        structure = recognizer.recognize(paper_text)
    """
    
    # 常见的部分标题模式
    SECTION_PATTERNS = {
        "title": r"^(.+?)(?=\n\n|\n摘\s*要|\nAbstract|\n【摘要】)",
        "abstract": r"(?:摘\s*要|Abstract|【摘要】)[：:\s]*\n?([\s\S]+?)(?=\n关键词|\nKeywords|\n【关键词】|\n一、|\n1\.|\n1、|\nI\.)",
        "keywords": r"(?:关键词|Keywords|【关键词】)[：:\s]*(.+?)(?=\n\n|\n一、|\n1\.|\n1、|\nI\.|\n引言)",
        "introduction": r"(?:一、|1\.|1、|I\.|\n)\s*(?:引言|导论|Introduction|前言)[：:\s]*([\s\S]+?)(?=\n(?:二、|2\.|2、|II\.)|文献[综回]述|Literature)",
        "literature": r"(?:二、|2\.|2、|II\.|\n)\s*(?:文献综述|文献回顾|相关研究|Literature\s*Review|研究综述)[：:\s]*([\s\S]+?)(?=\n(?:三、|3\.|3、|III\.)|理论|假设|Theoretical)",
        "theory": r"(?:三、|3\.|3、|III\.|\n)\s*(?:理论分析|研究假设|理论框架|Theoretical\s*Analysis|理论分析与研究假设|理论基础)[：:\s]*([\s\S]+?)(?=\n(?:四、|4\.|4、|IV\.)|研究设计|Methodology|研究方法)",
        "methodology": r"(?:四、|4\.|4、|IV\.|\n)\s*(?:研究设计|研究方法|模型设定|Methodology|Research\s*Design|实证设计)[：:\s]*([\s\S]+?)(?=\n(?:五、|5\.|5、|V\.)|实证[结分]|Empirical)",
        "results": r"(?:五、|5\.|5、|V\.|\n)\s*(?:实证结果|实证分析|回归结果|Empirical\s*Results|实证检验)[：:\s]*([\s\S]+?)(?=\n(?:六、|6\.|6、|VI\.)|稳健性|Robustness|结论|Conclusion)",
        "robustness": r"(?:六、|6\.|6、|VI\.|\n)\s*(?:稳健性检验|稳健性分析|Robustness|内生性处理)[：:\s]*([\s\S]+?)(?=\n(?:七、|7\.|7、|VII\.)|结论|Conclusion)",
        "conclusion": r"(?:七、|7\.|7、|VII\.|六、|6\.|6、|五、|5\.|5、)\s*(?:结论|结论与启示|研究结论|Conclusion|结论与讨论|结论与政策建议)[：:\s]*([\s\S]+?)(?=\n参考文献|\nReferences|\n附录|$)",
        "references": r"(?:参考文献|References|引用文献)[：:\s]*([\s\S]+)$"
    }
    
    def __init__(self, use_llm: bool = True):
        """
        初始化结构识别器
        
        Args:
            use_llm: 是否使用 LLM 辅助识别
        """
        self.use_llm = use_llm
    
    def recognize(self, content: str) -> Dict:
        """
        识别论文结构
        
        Args:
            content: 论文全文
            
        Returns:
            Dict: 各部分内容的字典
        """
        # 首先尝试基于规则的识别
        structure = self._rule_based_recognize(content)
        
        # 如果规则识别效果不佳且启用了 LLM，使用 LLM 辅助
        if self.use_llm and self._need_llm_assist(structure):
            structure = self._llm_recognize(content)
        
        return structure
    
    def _rule_based_recognize(self, content: str) -> Dict:
        """
        基于规则的结构识别
        
        Args:
            content: 论文全文
            
        Returns:
            Dict: 各部分内容
        """
        structure = {}
        
        for section_name, pattern in self.SECTION_PATTERNS.items():
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                # 对于标题特殊处理
                if section_name == "title":
                    structure[section_name] = match.group(1).strip()
                else:
                    structure[section_name] = match.group(1).strip() if match.groups() else match.group(0).strip()
        
        # 如果没有识别出结构，将整个内容作为 full_text
        if not structure:
            structure = {"full_text": content}
        else:
            structure["full_text"] = content
        
        return structure
    
    def _need_llm_assist(self, structure: Dict) -> bool:
        """
        判断是否需要 LLM 辅助识别
        
        Args:
            structure: 当前识别结果
            
        Returns:
            bool: 是否需要 LLM 辅助
        """
        # 如果识别出的部分少于 4 个，认为需要 LLM 辅助
        return len(structure) < 4
    
    def _llm_recognize(self, content: str) -> Dict:
        """
        使用 LLM 辅助识别结构
        
        Args:
            content: 论文全文
            
        Returns:
            Dict: 各部分内容
        """
        try:
            llm = get_llm_client()
            
            # 如果内容过长，只取前面部分识别结构
            truncated = content[:15000] if len(content) > 15000 else content
            
            prompt = PromptTemplates.RECOGNIZE_STRUCTURE.format(content=truncated)
            response = llm.invoke(
                prompt,
                system_prompt="你是一个学术论文结构分析专家。请分析论文结构并以JSON格式输出。"
            )
            
            # 尝试解析 JSON 响应
            import json
            # 提取 JSON 部分
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                structure = json.loads(json_match.group())
                structure["full_text"] = content
                return structure
            
        except Exception:
            pass
        
        # 如果 LLM 识别失败，返回基于规则的结果
        return self._rule_based_recognize(content)
    
    def get_section(self, structure: Dict, section_name: str) -> Optional[str]:
        """
        获取特定部分的内容
        
        Args:
            structure: 结构识别结果
            section_name: 部分名称
            
        Returns:
            Optional[str]: 部分内容，不存在则返回 None
        """
        return structure.get(section_name)
    
    def get_sections_for_optimization(self, structure: Dict) -> List[str]:
        """
        获取可优化的部分列表
        
        Args:
            structure: 结构识别结果
            
        Returns:
            List[str]: 可优化的部分名称列表
        """
        optimizable = [
            "title", "abstract", "introduction", "literature",
            "theory", "methodology", "results", "conclusion"
        ]
        return [s for s in optimizable if s in structure]
