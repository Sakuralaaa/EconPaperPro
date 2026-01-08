# -*- coding: utf-8 -*-
"""
退修Agent模块
处理审稿意见，生成回应策略和回应信
"""

from typing import Dict, List, Optional, Generator
from dataclasses import dataclass, field
from core.llm import get_llm_client
from core.prompts import PromptTemplates


@dataclass
class ReviewComment:
    """审稿意见条目"""
    id: int
    category: str  # theory/methodology/data/writing/other
    content: str
    severity: str  # major/minor
    suggestions: List[str] = field(default_factory=list)


@dataclass
class ResponseStrategy:
    """回应策略"""
    comment_id: int
    understanding: str  # 对问题的理解
    attitude: str  # accept/partial/decline
    actions: List[str]  # 具体措施
    expected_changes: str  # 预期修改


@dataclass
class RevisionResult:
    """退修处理结果"""
    parsed_comments: List[ReviewComment]
    strategies: List[ResponseStrategy]
    response_letter: str
    modification_suggestions: Dict[str, List[str]]


class RevisionAgent:
    """
    退修Agent
    
    处理审稿意见，生成回应策略和回应信
    
    使用示例:
        agent = RevisionAgent()
        result = agent.process_comments(reviewer_comments, paper_summary)
    """
    
    def __init__(self):
        """初始化退修Agent"""
        self.llm = get_llm_client()
    
    def process_comments(
        self,
        comments: str,
        paper_summary: Optional[str] = None
    ) -> RevisionResult:
        """
        处理审稿意见
        
        Args:
            comments: 审稿意见文本
            paper_summary: 论文摘要（可选）
            
        Returns:
            RevisionResult: 处理结果
        """
        # 1. 解析审稿意见
        parsed_comments = self.parse_comments(comments)
        
        # 2. 生成回应策略
        strategies = self.generate_strategies(parsed_comments, paper_summary)
        
        # 3. 生成回应信
        response_letter = self.generate_response_letter(strategies)
        
        # 4. 提取修改建议
        modification_suggestions = self._extract_modifications(strategies)
        
        return RevisionResult(
            parsed_comments=parsed_comments,
            strategies=strategies,
            response_letter=response_letter,
            modification_suggestions=modification_suggestions
        )
    
    def parse_comments(self, comments: str) -> List[ReviewComment]:
        """
        解析审稿意见
        
        Args:
            comments: 审稿意见文本
            
        Returns:
            List[ReviewComment]: 解析后的意见列表
        """
        prompt = PromptTemplates.PARSE_REVIEWER_COMMENTS.format(comments=comments)
        
        try:
            response = self.llm.invoke(
                prompt,
                system_prompt="你是学术论文审稿专家，请帮助解析审稿意见。"
            )
            
            return self._parse_comments_response(response)
            
        except Exception as e:
            # 如果解析失败，返回原始意见作为单条
            return [ReviewComment(
                id=1,
                category="other",
                content=comments,
                severity="major"
            )]
    
    def _parse_comments_response(self, response: str) -> List[ReviewComment]:
        """
        解析 LLM 对审稿意见的响应
        
        Args:
            response: LLM 响应
            
        Returns:
            List[ReviewComment]: 审稿意见列表
        """
        import re
        
        comments = []
        
        # 尝试多种分割模式
        # 模式1: 按编号分割
        sections = re.split(r'\n(?=[\d①②③④⑤⑥⑦⑧⑨⑩]+[.、)）]|\n(?=【问题|【意见)', response)
        
        # 模式2: 如果编号分割效果不好，尝试按标题分割
        if len(sections) < 2:
            sections = re.split(r'\n(?=问题\s*\d+|意见\s*\d+|第[一二三四五六七八九十]+[条项点])', response)
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            
            section = section.strip()
            
            # 提取类别
            category = "other"
            category_mapping = {
                "理论": "theory",
                "机制": "theory",
                "假设": "theory",
                "方法": "methodology",
                "计量": "methodology",
                "模型": "methodology",
                "内生": "methodology",
                "稳健": "methodology",
                "数据": "data",
                "样本": "data",
                "变量": "data",
                "写作": "writing",
                "表述": "writing",
                "文献": "writing",
                "格式": "writing",
            }
            for keyword, cat in category_mapping.items():
                if keyword in section:
                    category = cat
                    break
            
            # 提取严重程度
            severity = "major"
            minor_keywords = ["minor", "次要", "小问题", "建议", "可以考虑", "如果可能"]
            major_keywords = ["major", "重大", "严重", "必须", "关键", "核心"]
            
            section_lower = section.lower()
            if any(kw in section or kw in section_lower for kw in minor_keywords):
                severity = "minor"
            elif any(kw in section or kw in section_lower for kw in major_keywords):
                severity = "major"
            
            # 提取建议（如果有）
            suggestions = []
            suggestion_match = re.search(r'建议[：:]([\s\S]+?)(?=\n\n|$)', section)
            if suggestion_match:
                suggestions = [s.strip() for s in suggestion_match.group(1).split('\n') if s.strip()]
            
            comments.append(ReviewComment(
                id=len(comments) + 1,
                category=category,
                content=section,
                severity=severity,
                suggestions=suggestions[:3]  # 最多3条建议
            ))
        
        # 如果没有成功解析，返回原始内容作为单条
        if not comments:
            return [ReviewComment(
                id=1,
                category="other",
                content=response,
                severity="major"
            )]
        
        return comments
    
    def generate_strategies(
        self,
        parsed_comments: List[ReviewComment],
        paper_summary: Optional[str] = None
    ) -> List[ResponseStrategy]:
        """
        生成回应策略
        
        Args:
            parsed_comments: 解析后的审稿意见
            paper_summary: 论文摘要
            
        Returns:
            List[ResponseStrategy]: 回应策略列表
        """
        strategies = []
        
        for comment in parsed_comments:
            strategy = self._generate_single_strategy(comment, paper_summary)
            strategies.append(strategy)
        
        return strategies
    
    def _generate_single_strategy(
        self,
        comment: ReviewComment,
        paper_summary: Optional[str]
    ) -> ResponseStrategy:
        """
        为单条意见生成回应策略
        
        Args:
            comment: 审稿意见
            paper_summary: 论文摘要
            
        Returns:
            ResponseStrategy: 回应策略
        """
        prompt = f"""请为以下审稿意见生成回应策略：

审稿意见：{comment.content}

论文背景：{paper_summary or '无'}

请提供：
1. 问题理解（确认理解正确）
2. 回应态度（接受/部分接受/礼貌拒绝）
3. 具体措施（列表）
4. 预期修改内容"""

        try:
            response = self.llm.invoke(
                prompt,
                system_prompt="你是学术论文写作专家，请帮助制定回应策略。"
            )
            
            return self._parse_strategy_response(comment.id, response)
            
        except Exception:
            return ResponseStrategy(
                comment_id=comment.id,
                understanding="理解待确认",
                attitude="partial",
                actions=["需要进一步分析"],
                expected_changes="待定"
            )
    
    def _parse_strategy_response(self, comment_id: int, response: str) -> ResponseStrategy:
        """
        解析策略响应
        
        Args:
            comment_id: 意见ID
            response: LLM 响应
            
        Returns:
            ResponseStrategy: 解析后的策略
        """
        import re
        
        # 提取各部分
        understanding = ""
        attitude = "partial"
        actions = []
        expected = ""
        
        # 提取问题理解 - 支持多种格式
        understanding_patterns = [
            r'问题理解[：:]([\s\S]+?)(?=回应态度|态度|$)',
            r'理解[：:]([\s\S]+?)(?=态度|措施|$)',
            r'【问题理解】([\s\S]+?)(?=【|$)',
        ]
        for pattern in understanding_patterns:
            match = re.search(pattern, response)
            if match:
                understanding = match.group(1).strip()
                # 清理多余的换行
                understanding = re.sub(r'\n+', ' ', understanding)
                if understanding:
                    break
        
        # 提取回应态度 - 更精确的匹配
        attitude_patterns = [
            (r'完全接受|全部接受|accept', 'accept'),
            (r'部分接受|partial', 'partial'),
            (r'礼貌[拒婉]绝|婉拒|不同意|decline', 'decline'),
        ]
        
        for pattern, att in attitude_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                attitude = att
                break
        
        # 如果没有明确态度关键词，根据上下文判断
        if attitude == "partial":
            if "同意" in response and "不同意" not in response and "部分" not in response:
                attitude = "accept"
            elif "拒绝" in response or "不接受" in response:
                attitude = "decline"
        
        # 提取具体措施 - 改进的匹配逻辑
        actions_patterns = [
            r'具体措施[：:]([\s\S]+?)(?=预期|修改|$)',
            r'措施[：:]([\s\S]+?)(?=预期|修改|$)',
            r'【具体措施】([\s\S]+?)(?=【|$)',
        ]
        for pattern in actions_patterns:
            match = re.search(pattern, response)
            if match:
                measures_text = match.group(1)
                # 按多种分隔符分割
                items = re.split(r'\n\s*(?:\d+[.、)）]|\-|\•|\*)', measures_text)
                actions = [m.strip() for m in items if m.strip() and len(m.strip()) > 3]
                if actions:
                    break
        
        # 如果措施为空，尝试从列表中提取
        if not actions:
            list_match = re.findall(r'(?:^|\n)\s*[\d\-\•\*]+[.、)）]?\s*(.+?)(?=\n|$)', response)
            actions = [m.strip() for m in list_match if m.strip() and len(m.strip()) > 5][:5]
        
        # 提取预期修改
        expected_patterns = [
            r'预期[^：:]*[：:]([\s\S]+?)$',
            r'修改内容[：:]([\s\S]+?)$',
            r'【预期修改】([\s\S]+?)(?=【|$)',
        ]
        for pattern in expected_patterns:
            match = re.search(pattern, response)
            if match:
                expected = match.group(1).strip()
                # 智能截断：在句子边界处截断，避免截断到一半
                max_length = 500
                if len(expected) > max_length:
                    # 找到最后一个句子结束符
                    for sep in ["。", "！", "？", ".", "!", "?"]:
                        last_pos = expected.rfind(sep, 0, max_length)
                        if last_pos > max_length * 0.6:  # 至少保留60%的内容
                            expected = expected[:last_pos + 1]
                            break
                    else:
                        expected = expected[:max_length]
                if expected:
                    break
        
        return ResponseStrategy(
            comment_id=comment_id,
            understanding=understanding or "已理解审稿人意见",
            attitude=attitude,
            actions=actions if actions else ["进行相应修改"],
            expected_changes=expected or "详见修改稿"
        )
    
    def generate_response_letter(
        self,
        strategies: List[ResponseStrategy]
    ) -> str:
        """
        生成回应信
        
        Args:
            strategies: 回应策略列表
            
        Returns:
            str: 回应信文本
        """
        # 构建策略摘要
        strategy_text = ""
        for i, strategy in enumerate(strategies, 1):
            strategy_text += f"""
问题{i}:
- 理解: {strategy.understanding}
- 态度: {strategy.attitude}
- 措施: {'; '.join(strategy.actions)}
- 预期修改: {strategy.expected_changes}
"""
        
        prompt = PromptTemplates.GENERATE_RESPONSE_LETTER.format(
            response_strategy=strategy_text
        )
        
        try:
            response = self.llm.invoke(
                prompt,
                system_prompt="你是学术论文写作专家，请撰写正式的审稿意见回应信。"
            )
            return response
            
        except Exception as e:
            return f"回应信生成失败: {str(e)}"

    def process_comments_stream(
        self,
        comments: str,
        paper_summary: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        流式处理审稿意见 (P0)
        由于退修逻辑较为复杂（多步解析），此流式主要用于回应信生成部分，
        或通过分段 Yield 提供中间反馈。
        """
        yield "🔄 正在解析审稿意见...\n"
        parsed = self.parse_comments(comments)
        
        yield f"✅ 解析完成，共发现 {len(parsed)} 条意见。正在制定回应策略...\n"
        strategies = self.generate_strategies(parsed, paper_summary)
        
        yield "📝 正在生成正式回应信...\n\n"
        
        # 构造策略摘要
        strategy_text = ""
        for i, strategy in enumerate(strategies, 1):
            strategy_text += f"\n问题{i}:\n- 理解: {strategy.understanding}\n- 态度: {strategy.attitude}\n- 措施: {'; '.join(strategy.actions)}\n- 预期修改: {strategy.expected_changes}\n"
        
        prompt = PromptTemplates.GENERATE_RESPONSE_LETTER.format(
            response_strategy=strategy_text
        )
        
        # 调用流式接口生成回应信内容
        yield from self.llm.invoke_stream(
            prompt,
            system_prompt="你是学术论文写作专家，请撰写正式的审稿意见回应信。"
        )

    def _extract_modifications(
        self,
        strategies: List[ResponseStrategy]
    ) -> Dict[str, List[str]]:
        """
        提取修改建议
        
        Args:
            strategies: 回应策略列表
            
        Returns:
            Dict[str, List[str]]: 按类别组织的修改建议
        """
        modifications = {
            "理论完善": [],
            "方法改进": [],
            "数据补充": [],
            "写作优化": [],
            "其他": []
        }
        
        for strategy in strategies:
            for action in strategy.actions:
                # 简单的关键词分类
                if any(k in action for k in ["理论", "机制", "假设"]):
                    modifications["理论完善"].append(action)
                elif any(k in action for k in ["方法", "模型", "变量", "稳健"]):
                    modifications["方法改进"].append(action)
                elif any(k in action for k in ["数据", "样本", "来源"]):
                    modifications["数据补充"].append(action)
                elif any(k in action for k in ["表述", "文字", "格式"]):
                    modifications["写作优化"].append(action)
                else:
                    modifications["其他"].append(action)
        
        # 移除空类别
        return {k: v for k, v in modifications.items() if v}
    
    def format_result(self, result: RevisionResult) -> str:
        """
        格式化结果为 Markdown
        
        Args:
            result: 退修处理结果
            
        Returns:
            str: Markdown 格式的结果
        """
        lines = []
        lines.append("# 📝 退修处理报告\n")
        
        lines.append("## 审稿意见解析\n")
        for comment in result.parsed_comments:
            severity_icon = "🔴" if comment.severity == "major" else "🟡"
            lines.append(f"### {severity_icon} 问题 {comment.id} ({comment.category})")
            lines.append(f"{comment.content}\n")
        
        lines.append("---\n")
        lines.append("## 回应策略\n")
        for strategy in result.strategies:
            attitude_map = {"accept": "✅ 接受", "partial": "⚡ 部分接受", "decline": "❌ 婉拒"}
            lines.append(f"### 问题 {strategy.comment_id}")
            lines.append(f"**态度**: {attitude_map.get(strategy.attitude, strategy.attitude)}")
            lines.append(f"**理解**: {strategy.understanding}")
            lines.append("**措施**:")
            for action in strategy.actions:
                lines.append(f"- {action}")
            lines.append(f"**预期修改**: {strategy.expected_changes}\n")
        
        lines.append("---\n")
        lines.append("## 修改建议汇总\n")
        for category, items in result.modification_suggestions.items():
            lines.append(f"### {category}")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")
        
        lines.append("---\n")
        lines.append("## 回应信\n")
        lines.append(result.response_letter)
        
        return "\n".join(lines)
