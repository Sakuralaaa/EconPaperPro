# -*- coding: utf-8 -*-
"""
优化Agent模块
对论文各部分进行深度优化
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from core.llm import get_llm_client
from core.prompts import PromptTemplates

# 配置常量
MAX_CHANGES_TO_REPORT = 5  # 最多报告的变化条数


@dataclass
class OptimizationResult:
    """优化结果"""
    section: str
    original: str
    optimized: str
    changes: List[str]
    success: bool = True
    error: Optional[str] = None


class OptimizerAgent:
    """
    论文优化Agent
    
    支持论文各部分的深度优化：
    - 标题、摘要
    - 引言、文献综述
    - 研究假设、研究设计
    - 实证分析、结论
    
    使用示例:
        agent = OptimizerAgent()
        result = agent.optimize_single_section("introduction", content, context)
    """
    
    # 部分名称到提示词模板的映射
    SECTION_PROMPTS = {
        "title": PromptTemplates.OPTIMIZE_TITLE,
        "abstract": PromptTemplates.OPTIMIZE_ABSTRACT,
        "introduction": PromptTemplates.OPTIMIZE_INTRODUCTION,
        "literature": PromptTemplates.OPTIMIZE_LITERATURE,
        "theory": PromptTemplates.OPTIMIZE_HYPOTHESIS,
        "methodology": PromptTemplates.OPTIMIZE_RESEARCH_DESIGN,
        "results": PromptTemplates.OPTIMIZE_EMPIRICAL,
        "conclusion": PromptTemplates.OPTIMIZE_CONCLUSION,
    }
    
    # 优化阶段配置
    STAGES = {
        "draft": {
            "name": "初稿重构",
            "focus": ["structure", "logic", "completeness"],
            "temperature": 0.8
        },
        "submission": {
            "name": "投稿优化",
            "focus": ["innovation", "methodology", "writing"],
            "temperature": 0.7
        },
        "revision": {
            "name": "退修回应",
            "focus": ["targeted", "evidence", "argumentation"],
            "temperature": 0.6
        },
        "final": {
            "name": "终稿定稿",
            "focus": ["polish", "consistency", "formatting"],
            "temperature": 0.5
        }
    }
    
    def __init__(self, stage: str = "submission"):
        """
        初始化优化Agent
        
        Args:
            stage: 优化阶段 (draft/submission/revision/final)
        """
        self.stage = stage
        self.stage_config = self.STAGES.get(stage, self.STAGES["submission"])
        self.llm = get_llm_client()
    
    def optimize(
        self,
        parsed_structure: Dict,
        diagnosis: Optional[Dict] = None,
        sections: Optional[List[str]] = None
    ) -> Dict[str, OptimizationResult]:
        """
        优化论文
        
        Args:
            parsed_structure: 解析后的论文结构
            diagnosis: 诊断结果（可选，用于针对性优化）
            sections: 要优化的部分列表，None 表示全部
            
        Returns:
            Dict[str, OptimizationResult]: 各部分的优化结果
        """
        # 确定要优化的部分
        if sections is None:
            sections = [s for s in self.SECTION_PROMPTS.keys() if s in parsed_structure]
        else:
            sections = [s for s in sections if s in parsed_structure]
        
        # 构建上下文
        context = self._build_context(parsed_structure, diagnosis)
        
        results = {}
        for section in sections:
            content = parsed_structure.get(section, "")
            if content:
                result = self.optimize_single_section(section, content, context)
                results[section] = result
        
        return results
    
    def optimize_single_section(
        self,
        section_name: str,
        content: str,
        context: Optional[str] = None
    ) -> OptimizationResult:
        """
        优化单个部分
        
        Args:
            section_name: 部分名称
            content: 部分内容
            context: 上下文信息
            
        Returns:
            OptimizationResult: 优化结果
        """
        if section_name not in self.SECTION_PROMPTS:
            return OptimizationResult(
                section=section_name,
                original=content,
                optimized=content,
                changes=[],
                success=False,
                error=f"不支持优化的部分: {section_name}"
            )
        
        prompt_template = self.SECTION_PROMPTS[section_name]
        
        try:
            # 构建提示词
            prompt_kwargs = {"content": content}
            if context:
                prompt_kwargs["context"] = context
            if section_name == "title":
                prompt_kwargs["title"] = content
                prompt_kwargs["abstract"] = context or ""
                prompt_kwargs["target_journal"] = "经济研究/管理世界"
            if section_name == "abstract":
                prompt_kwargs["summary"] = context or ""
            
            prompt = prompt_template.format(**prompt_kwargs)
            
            # 调用 LLM
            response = self.llm.invoke(
                prompt,
                system_prompt=PromptTemplates.SYSTEM_ACADEMIC_EXPERT,
                temperature=self.stage_config["temperature"]
            )
            
            # 提取优化后的内容
            optimized = self._extract_optimized_content(response)
            changes = self._identify_changes(content, optimized)
            
            return OptimizationResult(
                section=section_name,
                original=content,
                optimized=optimized,
                changes=changes,
                success=True
            )
            
        except Exception as e:
            return OptimizationResult(
                section=section_name,
                original=content,
                optimized=content,
                changes=[],
                success=False,
                error=str(e)
            )
    
    def optimize_for_journal(
        self,
        parsed_structure: Dict,
        target_journal: str
    ) -> Dict[str, OptimizationResult]:
        """
        针对目标期刊进行优化
        
        Args:
            parsed_structure: 解析后的论文结构
            target_journal: 目标期刊名称
            
        Returns:
            Dict[str, OptimizationResult]: 各部分的优化结果
        """
        # 根据期刊类型调整优化策略
        journal_focus = self._get_journal_focus(target_journal)
        
        context = f"目标期刊：{target_journal}\n期刊特点：{journal_focus}"
        if "abstract" in parsed_structure:
            context += f"\n论文摘要：{parsed_structure['abstract'][:500]}"
        
        results = {}
        for section in ["title", "abstract", "introduction", "conclusion"]:
            if section in parsed_structure:
                result = self.optimize_single_section(
                    section,
                    parsed_structure[section],
                    context
                )
                results[section] = result
        
        return results
    
    def _build_context(
        self,
        parsed_structure: Dict,
        diagnosis: Optional[Dict] = None
    ) -> str:
        """
        构建优化上下文
        
        Args:
            parsed_structure: 论文结构
            diagnosis: 诊断结果
            
        Returns:
            str: 上下文信息
        """
        context_parts = []
        
        # 添加摘要作为核心上下文
        if "abstract" in parsed_structure:
            context_parts.append(f"论文摘要：{parsed_structure['abstract'][:500]}")
        
        # 添加标题
        if "title" in parsed_structure:
            context_parts.append(f"论文标题：{parsed_structure['title']}")
        
        # 添加诊断信息
        if diagnosis:
            issues = []
            for dim, result in diagnosis.items():
                if hasattr(result, 'problems') and result.problems:
                    issues.extend(result.problems[:2])
            if issues:
                context_parts.append(f"待改进问题：{'; '.join(issues[:5])}")
        
        return "\n".join(context_parts)
    
    def _extract_optimized_content(self, response: str) -> str:
        """
        从 LLM 响应中提取优化后的内容
        
        Args:
            response: LLM 响应
            
        Returns:
            str: 优化后的内容
        """
        import re
        
        # 常见的优化内容标记
        content_markers = [
            r'【优化后[^】]*】[：:\s]*([\s\S]+?)(?=【|$)',
            r'优化后[的]?[^：:]*[：:]\s*([\s\S]+?)(?=【|优化说明|$)',
            r'\[优化后[^\]]*\][：:\s]*([\s\S]+?)(?=\[|$)',
        ]
        
        for pattern in content_markers:
            match = re.search(pattern, response)
            if match:
                content = match.group(1).strip()
                if content and len(content) > 50:
                    return content
        
        # 如果没有找到标记，尝试去除引导语
        lines = response.split("\n")
        
        # 跳过开头的说明性文字
        start_idx = 0
        skip_patterns = [
            "以下是", "优化后", "修改后", "这是", "根据", 
            "【", "好的", "我来", "按照", "针对"
        ]
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if any(line_stripped.startswith(p) for p in skip_patterns):
                start_idx = i + 1
            elif line_stripped and len(line_stripped) > 20:
                # 找到实质性内容
                break
        
        # 去除结尾的说明文字
        end_idx = len(lines)
        end_patterns = ["【优化说明", "【说明】", "优化说明", "---"]
        for i in range(len(lines) - 1, -1, -1):
            line_stripped = lines[i].strip()
            if any(p in line_stripped for p in end_patterns):
                end_idx = i
                break
        
        content = "\n".join(lines[start_idx:end_idx]).strip()
        
        # 如果内容为空或太短，返回原始响应
        return content if content and len(content) > 50 else response
    
    def _identify_changes(self, original: str, optimized: str) -> List[str]:
        """
        识别主要变化
        
        Args:
            original: 原始内容
            optimized: 优化后内容
            
        Returns:
            List[str]: 主要变化描述
        """
        changes = []
        
        # 字数变化分析
        orig_len = len(original)
        opt_len = len(optimized)
        len_ratio = opt_len / orig_len if orig_len > 0 else 1
        
        if len_ratio > 1.3:
            changes.append(f"内容扩充约{int((len_ratio-1)*100)}%，增加了详细论述")
        elif len_ratio > 1.1:
            changes.append("适度扩展，补充了必要细节")
        elif len_ratio < 0.7:
            changes.append(f"内容精简约{int((1-len_ratio)*100)}%，删除了冗余表述")
        elif len_ratio < 0.9:
            changes.append("适度精简，优化了表达效率")
        
        # 结构变化分析
        orig_paras = original.count("\n\n")
        opt_paras = optimized.count("\n\n")
        if opt_paras > orig_paras + 2:
            changes.append("增加了段落分层，提升了结构清晰度")
        elif opt_paras < orig_paras - 2:
            changes.append("合并了相关段落，增强了内容连贯性")
        
        # 句子结构分析
        orig_sentences = original.count("。") + original.count(".")
        opt_sentences = optimized.count("。") + optimized.count(".")
        if opt_sentences > orig_sentences * 1.3:
            changes.append("拆分了长句，提升了可读性")
        elif opt_sentences < orig_sentences * 0.7:
            changes.append("合并了短句，增强了表达连贯性")
        
        # 学术表达优化检测
        academic_markers = ["研究发现", "实证结果表明", "本文认为", "分析显示"]
        orig_academic = sum(1 for m in academic_markers if m in original)
        opt_academic = sum(1 for m in academic_markers if m in optimized)
        if opt_academic > orig_academic:
            changes.append("增加了规范的学术表达")
        
        # 如果没有检测到明显变化
        if not changes:
            changes.append("优化了语言表达和论述方式")
        
        return changes[:MAX_CHANGES_TO_REPORT]  # 最多返回指定数量的变化
    
    def _get_journal_focus(self, journal: str) -> str:
        """
        获取期刊特点描述
        
        Args:
            journal: 期刊名称
            
        Returns:
            str: 期刊特点描述
        """
        journal_features = {
            "经济研究": "强调理论深度和原创性，注重规范的计量分析",
            "管理世界": "关注重大现实问题，重视管理实践价值",
            "中国工业经济": "产业经济视角，注重政策含义",
            "金融研究": "金融领域专业性强，数据和模型要求高",
            "会计研究": "会计专业规范，案例和实证并重",
        }
        
        for key, value in journal_features.items():
            if key in journal:
                return value
        
        return "注重学术规范，强调原创贡献"
    
    def set_stage(self, stage: str) -> None:
        """
        设置优化阶段
        
        Args:
            stage: 优化阶段
        """
        if stage in self.STAGES:
            self.stage = stage
            self.stage_config = self.STAGES[stage]
