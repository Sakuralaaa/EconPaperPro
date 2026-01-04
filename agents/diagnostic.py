# -*- coding: utf-8 -*-
"""
诊断Agent模块
对论文进行多维度诊断分析
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from core.llm import get_llm_client
from core.prompts import PromptTemplates


@dataclass
class DiagnosisResult:
    """诊断结果数据类"""
    dimension: str
    score: float
    problems: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class FullDiagnosisReport:
    """完整诊断报告"""
    overall_score: float
    dimensions: Dict[str, DiagnosisResult] = field(default_factory=dict)
    summary: str = ""
    priority_issues: List[str] = field(default_factory=list)


class DiagnosticAgent:
    """
    论文诊断Agent
    
    对论文进行多维度分析诊断：
    - 结构完整性 (structure)
    - 逻辑严密性 (logic)
    - 方法规范性 (methodology)
    - 创新贡献 (innovation)
    - 写作规范 (writing)
    
    使用示例:
        agent = DiagnosticAgent()
        report = agent.diagnose(paper_content)
    """
    
    DIMENSIONS = {
        "structure": ("结构完整性", PromptTemplates.DIAGNOSIS_STRUCTURE),
        "logic": ("逻辑严密性", PromptTemplates.DIAGNOSIS_LOGIC),
        "methodology": ("方法规范性", PromptTemplates.DIAGNOSIS_METHODOLOGY),
        "innovation": ("创新贡献", PromptTemplates.DIAGNOSIS_INNOVATION),
        "writing": ("写作规范", PromptTemplates.DIAGNOSIS_WRITING),
    }
    
    def __init__(self):
        """初始化诊断Agent"""
        self.llm = get_llm_client()
    
    def diagnose(
        self,
        content: str,
        focus: Optional[List[str]] = None
    ) -> FullDiagnosisReport:
        """
        执行论文诊断
        
        Args:
            content: 论文内容
            focus: 聚焦的诊断维度，None 表示全部
            
        Returns:
            FullDiagnosisReport: 完整诊断报告
        """
        dimensions_to_check = focus if focus else list(self.DIMENSIONS.keys())
        
        results = {}
        for dim in dimensions_to_check:
            if dim in self.DIMENSIONS:
                result = self._diagnose_dimension(content, dim)
                results[dim] = result
        
        # 计算总分
        scores = [r.score for r in results.values()]
        overall_score = sum(scores) / len(scores) if scores else 0
        
        # 生成优先问题列表
        priority_issues = self._extract_priority_issues(results)
        
        # 生成总结
        summary = self._generate_summary(results, overall_score)
        
        return FullDiagnosisReport(
            overall_score=round(overall_score, 1),
            dimensions=results,
            summary=summary,
            priority_issues=priority_issues
        )
    
    def _diagnose_dimension(self, content: str, dimension: str) -> DiagnosisResult:
        """
        诊断单个维度
        
        Args:
            content: 论文内容
            dimension: 维度名称
            
        Returns:
            DiagnosisResult: 诊断结果
        """
        dim_name, prompt_template = self.DIMENSIONS[dimension]
        
        # 如果内容过长，截断
        truncated = content[:12000] if len(content) > 12000 else content
        
        prompt = prompt_template.format(content=truncated)
        
        try:
            response = self.llm.invoke(
                prompt,
                system_prompt=PromptTemplates.SYSTEM_ACADEMIC_EXPERT
            )
            
            return self._parse_diagnosis_response(dimension, response)
            
        except Exception as e:
            return DiagnosisResult(
                dimension=dim_name,
                score=0,
                problems=[f"诊断过程出错: {str(e)}"],
                suggestions=["请检查 API 配置后重试"]
            )
    
    def _parse_diagnosis_response(self, dimension: str, response: str) -> DiagnosisResult:
        """
        解析诊断响应
        
        Args:
            dimension: 维度名称
            response: LLM 响应文本
            
        Returns:
            DiagnosisResult: 解析后的诊断结果
        """
        import re
        
        dim_name = self.DIMENSIONS[dimension][0]
        
        # 提取评分 - 支持多种格式
        score = 5.0  # 默认分数
        score_patterns = [
            r'评分[（(]?\d+-?\d*分?[）)]?[：:]\s*\[?(\d+(?:\.\d+)?)\]?分?',
            r'评分[：:]\s*\[?(\d+(?:\.\d+)?)\]?分?',
            r'\[?(\d+(?:\.\d+)?)\]?分?\s*/\s*10',
            r'(\d+(?:\.\d+)?)\s*[分/]',
            r'评分[（(]1-10分[）)][：:]\s*(\d+(?:\.\d+)?)',
        ]
        for pattern in score_patterns:
            match = re.search(pattern, response)
            if match:
                score = float(match.group(1))
                break
        
        # 提取问题 - 改进的匹配逻辑
        problems = []
        # 尝试匹配"主要问题："后的内容
        problems_patterns = [
            r'主要问题[：:]([\s\S]+?)(?=改进建议|优化建议|$)',
            r'问题[：:]([\s\S]+?)(?=建议|$)',
        ]
        for pattern in problems_patterns:
            match = re.search(pattern, response)
            if match:
                problems_text = match.group(1)
                # 按编号或符号分割
                items = re.split(r'\n\s*(?:\d+[.、)）]|\-|\•|\*)', problems_text)
                problems = [p.strip() for p in items if p.strip() and len(p.strip()) > 5]
                if problems:
                    break
        
        # 如果未提取到问题，尝试按行提取
        if not problems:
            lines = response.split('\n')
            in_problems_section = False
            for line in lines:
                if '主要问题' in line or '问题：' in line:
                    in_problems_section = True
                    continue
                if '改进建议' in line or '建议：' in line:
                    in_problems_section = False
                    continue
                if in_problems_section:
                    cleaned = re.sub(r'^[\d.、)）\-\•\*\s]+', '', line).strip()
                    if cleaned and len(cleaned) > 5:
                        problems.append(cleaned)
        
        # 提取建议 - 改进的匹配逻辑
        suggestions = []
        suggestions_patterns = [
            r'改进建议[：:]([\s\S]+?)$',
            r'优化建议[：:]([\s\S]+?)$',
            r'建议[：:]([\s\S]+?)$',
        ]
        for pattern in suggestions_patterns:
            match = re.search(pattern, response)
            if match:
                suggestions_text = match.group(1)
                # 按编号或符号分割
                items = re.split(r'\n\s*(?:\d+[.、)）]|\-|\•|\*)', suggestions_text)
                suggestions = [s.strip() for s in items if s.strip() and len(s.strip()) > 5]
                if suggestions:
                    break
        
        # 如果未提取到建议，尝试按行提取
        if not suggestions:
            lines = response.split('\n')
            in_suggestions_section = False
            for line in lines:
                if '改进建议' in line or '优化建议' in line:
                    in_suggestions_section = True
                    continue
                if in_suggestions_section:
                    cleaned = re.sub(r'^[\d.、)）\-\•\*\s]+', '', line).strip()
                    if cleaned and len(cleaned) > 5:
                        suggestions.append(cleaned)
        
        return DiagnosisResult(
            dimension=dim_name,
            score=min(10, max(0, score)),
            problems=problems[:5],  # 最多5个问题
            suggestions=suggestions[:5]  # 最多5个建议
        )
    
    def _extract_priority_issues(self, results: Dict[str, DiagnosisResult]) -> List[str]:
        """
        提取优先处理的问题
        
        Args:
            results: 各维度诊断结果
            
        Returns:
            List[str]: 优先问题列表
        """
        # 按分数排序，低分优先
        sorted_dims = sorted(results.items(), key=lambda x: x[1].score)
        
        priority_issues = []
        for dim_key, result in sorted_dims[:3]:  # 取最低的3个维度
            if result.problems:
                issue = f"[{result.dimension}] {result.problems[0]}"
                priority_issues.append(issue)
        
        return priority_issues
    
    def _generate_summary(
        self,
        results: Dict[str, DiagnosisResult],
        overall_score: float
    ) -> str:
        """
        生成诊断总结
        
        Args:
            results: 各维度诊断结果
            overall_score: 总分
            
        Returns:
            str: 总结文本
        """
        if overall_score >= 8:
            level = "优秀"
            advice = "论文整体质量较高，可针对细节进行打磨优化。"
        elif overall_score >= 6:
            level = "良好"
            advice = "论文具备较好基础，建议重点关注低分维度进行提升。"
        elif overall_score >= 4:
            level = "一般"
            advice = "论文存在较多需要改进之处，建议系统性修改。"
        else:
            level = "需大幅改进"
            advice = "论文质量有待提升，建议在导师指导下重新梳理。"
        
        # 找出最强和最弱维度
        scores = [(k, v.score, v.dimension) for k, v in results.items()]
        if scores:
            scores.sort(key=lambda x: x[1], reverse=True)
            strongest = scores[0][2]
            weakest = scores[-1][2]
            
            return f"论文综合评级：{level}（{overall_score}/10分）\n\n" \
                   f"优势维度：{strongest}\n" \
                   f"薄弱维度：{weakest}\n\n" \
                   f"总体建议：{advice}"
        
        return f"论文综合评级：{level}（{overall_score}/10分）\n{advice}"
    
    def diagnose_single(self, content: str, dimension: str) -> DiagnosisResult:
        """
        单维度诊断
        
        Args:
            content: 论文内容
            dimension: 维度名称
            
        Returns:
            DiagnosisResult: 诊断结果
        """
        if dimension not in self.DIMENSIONS:
            raise ValueError(f"未知的诊断维度: {dimension}")
        
        return self._diagnose_dimension(content, dimension)
    
    def format_report(self, report: FullDiagnosisReport) -> str:
        """
        格式化诊断报告为 Markdown
        
        Args:
            report: 诊断报告
            
        Returns:
            str: Markdown 格式的报告
        """
        lines = []
        lines.append("# 📋 论文诊断报告\n")
        lines.append(f"## 综合评分：{report.overall_score}/10\n")
        lines.append(report.summary)
        lines.append("\n---\n")
        
        lines.append("## 各维度详细诊断\n")
        
        for dim_key, result in report.dimensions.items():
            lines.append(f"### {result.dimension}（{result.score}/10分）\n")
            
            if result.problems:
                lines.append("**主要问题：**")
                for i, problem in enumerate(result.problems, 1):
                    lines.append(f"{i}. {problem}")
                lines.append("")
            
            if result.suggestions:
                lines.append("**改进建议：**")
                for i, suggestion in enumerate(result.suggestions, 1):
                    lines.append(f"{i}. {suggestion}")
                lines.append("")
            
            lines.append("")
        
        if report.priority_issues:
            lines.append("---\n")
            lines.append("## 🎯 优先处理事项\n")
            for i, issue in enumerate(report.priority_issues, 1):
                lines.append(f"{i}. {issue}")
        
        return "\n".join(lines)
