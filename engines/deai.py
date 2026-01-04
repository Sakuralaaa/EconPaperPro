# -*- coding: utf-8 -*-
"""
降AI引擎模块
消除AI写作痕迹，使文本更具人类学者风格
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from core.llm import get_llm_client
from core.prompts import PromptTemplates


def split_sentences(text: str) -> List[str]:
    """
    分割文本为句子列表
    
    Args:
        text: 输入文本
        
    Returns:
        List[str]: 句子列表
    """
    # 标准化句末标点
    normalized = text.replace("！", "。").replace("？", "。")
    sentences = [s.strip() for s in normalized.split("。") if s.strip()]
    return sentences


@dataclass
class AIDetectionResult:
    """AI检测结果"""
    overall_score: float  # AI概率 0-100
    dimensions: Dict[str, float]  # 各维度评分
    ai_markers: List[str]  # AI痕迹示例
    suggestions: List[str]  # 改进建议


@dataclass
class DeAIResult:
    """降AI处理结果"""
    original: str
    processed: str
    ai_score_before: float
    ai_score_after: float
    changes: List[str]


class DeAIEngine:
    """
    降AI引擎
    
    消除AI写作痕迹，使文本更具人类学者风格
    
    使用示例:
        engine = DeAIEngine()
        result = engine.process(content)
    """
    
    # AI写作特征
    AI_MARKERS = {
        # 结构化序列
        "sequence_markers": [
            "首先", "其次", "再次", "最后", "第一", "第二", "第三", "第四",
            "一方面", "另一方面", "此外", "同时", "另外", "与此同时",
            "紧接着", "随后", "进一步",
        ],
        # 填充短语
        "filler_phrases": [
            "值得注意的是", "需要指出的是", "综上所述", "总的来说", 
            "总而言之", "不难发现", "显而易见", "毋庸置疑", "不可否认", 
            "众所周知", "事实上", "实际上", "可以说", "由此可见",
            "需要强调的是", "特别值得一提的是", "不言而喻",
        ],
        # 模糊表达
        "vague_expressions": [
            "在一定程度上", "在某种意义上", "从某种角度来看",
            "可能会", "或许", "大概", "似乎", "貌似",
            "相对而言", "总体上看", "一般来说", "通常情况下",
        ],
        # 过度正式
        "overly_formal": [
            "鉴于此", "基于此", "据此", "由此可见", "由此可知", 
            "由上可知", "综合以上分析", "基于上述分析",
            "承上所述", "如前所述", "正如前文所述",
        ],
        # 连接词滥用
        "connector_abuse": [
            "然而", "但是", "因此", "所以", "故而", "于是",
            "尽管如此", "虽然如此", "即便如此",
        ]
    }
    
    def __init__(self):
        """初始化降AI引擎"""
        self._llm = None
    
    @property
    def llm(self):
        """延迟加载LLM客户端"""
        if self._llm is None:
            self._llm = get_llm_client()
        return self._llm
    
    def process(self, content: str) -> DeAIResult:
        """
        执行降AI处理
        
        Args:
            content: 原始文本
            
        Returns:
            DeAIResult: 降AI结果
        """
        # 1. 检测AI痕迹
        ai_score_before = self.estimate_ai_score(content)
        
        # 2. 人性化改写
        processed = self._humanize(content)
        
        # 3. 再次检测
        ai_score_after = self.estimate_ai_score(processed)
        
        # 4. 识别变化
        changes = self._identify_changes(content, processed)
        
        return DeAIResult(
            original=content,
            processed=processed,
            ai_score_before=ai_score_before,
            ai_score_after=ai_score_after,
            changes=changes
        )
    
    def estimate_ai_score(self, text: str) -> float:
        """
        估算AI写作概率
        
        Args:
            text: 文本内容
            
        Returns:
            float: AI概率 (0-100)
        """
        if not text:
            return 0.0
        
        # 对于非常短的文本，AI检测不可靠
        if len(text) < 30:
            return 0.0
        
        scores = []
        weights = []
        
        # 1. 检测结构化序列（权重20%）
        sequence_count = sum(
            text.count(m) for m in self.AI_MARKERS["sequence_markers"]
        )
        # 根据文本长度归一化
        text_len_factor = len(text) / 1000
        normalized_seq = sequence_count / max(1, text_len_factor)
        sequence_score = min(100, normalized_seq * 12)
        scores.append(sequence_score)
        weights.append(0.20)
        
        # 2. 检测填充短语（权重25%）
        filler_count = sum(
            text.count(p) for p in self.AI_MARKERS["filler_phrases"]
        )
        normalized_filler = filler_count / max(1, text_len_factor)
        filler_score = min(100, normalized_filler * 20)
        scores.append(filler_score)
        weights.append(0.25)
        
        # 3. 检测模糊表达（权重15%）
        vague_count = sum(
            text.count(e) for e in self.AI_MARKERS["vague_expressions"]
        )
        normalized_vague = vague_count / max(1, text_len_factor)
        vague_score = min(100, normalized_vague * 15)
        scores.append(vague_score)
        weights.append(0.15)
        
        # 4. 检测句子长度均匀度（权重20%）
        sentences = split_sentences(text)
        if len(sentences) >= 3:
            lengths = [len(s) for s in sentences if len(s) > 5]
            if lengths:
                avg_len = sum(lengths) / len(lengths)
                variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
                std_dev = variance ** 0.5
                # 标准差越小，越可能是AI（句子长度过于均匀）
                # 人类写作标准差通常在15-40之间
                if std_dev < 10:
                    uniformity_score = 90
                elif std_dev < 20:
                    uniformity_score = 60
                elif std_dev < 30:
                    uniformity_score = 30
                else:
                    uniformity_score = 10
                scores.append(uniformity_score)
                weights.append(0.20)
        
        # 5. 过度正式表达（权重10%）
        formal_count = sum(
            text.count(f) for f in self.AI_MARKERS["overly_formal"]
        )
        normalized_formal = formal_count / max(1, text_len_factor)
        formal_score = min(100, normalized_formal * 18)
        scores.append(formal_score)
        weights.append(0.10)
        
        # 6. 连接词滥用（权重10%）
        connector_count = sum(
            text.count(c) for c in self.AI_MARKERS["connector_abuse"]
        )
        normalized_connector = connector_count / max(1, text_len_factor)
        connector_score = min(100, normalized_connector * 8)
        scores.append(connector_score)
        weights.append(0.10)
        
        # 计算加权平均
        if scores and weights:
            total_weight = sum(weights)
            weighted_sum = sum(s * w for s, w in zip(scores, weights))
            return weighted_sum / total_weight
        
        return 50.0
    
    def detect_ai_features(self, text: str) -> AIDetectionResult:
        """
        详细检测AI特征
        
        Args:
            text: 文本内容
            
        Returns:
            AIDetectionResult: 检测结果
        """
        dimensions = {}
        ai_markers = []
        suggestions = []
        
        # 检测各维度
        for category, markers in self.AI_MARKERS.items():
            found = [m for m in markers if m in text]
            count = len(found)
            
            if category == "sequence_markers":
                dimensions["结构规整度"] = min(10, count * 2)
                if found:
                    ai_markers.extend([f"序列词: {m}" for m in found[:3]])
                    suggestions.append("减少使用'首先、其次、最后'等序列词")
                    
            elif category == "filler_phrases":
                dimensions["填充短语"] = min(10, count * 3)
                if found:
                    ai_markers.extend([f"填充语: {m}" for m in found[:3]])
                    suggestions.append("删除'值得注意的是'等填充性短语")
                    
            elif category == "vague_expressions":
                dimensions["模糊表达"] = min(10, count * 2)
                if found:
                    ai_markers.extend([f"模糊语: {m}" for m in found[:3]])
                    suggestions.append("使用更具体的表述替代模糊表达")
                    
            elif category == "overly_formal":
                dimensions["过度正式"] = min(10, count * 3)
                if found:
                    ai_markers.extend([f"正式语: {m}" for m in found[:3]])
                    suggestions.append("适当降低语言的正式程度")
        
        # 检测句子均匀度
        sentences = split_sentences(text)
        if len(sentences) >= 3:
            lengths = [len(s) for s in sentences]
            avg_len = sum(lengths) / len(lengths)
            variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
            uniformity = max(0, 10 - variance / 50)
            dimensions["句式均匀度"] = uniformity
            if uniformity > 7:
                suggestions.append("变化句子长度，打破均匀节奏")
        
        overall = sum(dimensions.values()) / len(dimensions) * 10 if dimensions else 50
        
        return AIDetectionResult(
            overall_score=overall,
            dimensions=dimensions,
            ai_markers=ai_markers,
            suggestions=suggestions
        )
    
    def _humanize(self, content: str) -> str:
        """
        人性化改写
        
        Args:
            content: 原始文本
            
        Returns:
            str: 改写后的文本
        """
        prompt = PromptTemplates.DEAI_HUMANIZE.format(content=content)
        
        try:
            processed = self.llm.invoke(
                prompt,
                system_prompt="你是资深学术写作专家，请将AI风格的文本改写为更具人类学者特色的表达。"
            )
            return processed
            
        except Exception:
            # 如果LLM调用失败，尝试规则替换
            return self._rule_based_humanize(content)
    
    def _rule_based_humanize(self, content: str) -> str:
        """
        基于规则的人性化改写
        
        Args:
            content: 原始文本
            
        Returns:
            str: 改写后的文本
        """
        result = content
        
        # 替换填充短语
        filler_replacements = {
            "值得注意的是，": "",
            "需要指出的是，": "",
            "综上所述，": "",
            "总的来说，": "",
            "不难发现，": "",
            "显而易见，": "",
            "毋庸置疑，": "",
            "众所周知，": "",
            "事实上，": "",
            "不可否认，": "",
            "需要强调的是，": "",
            "特别值得一提的是，": "",
        }
        
        for old, new in filler_replacements.items():
            result = result.replace(old, new)
        
        # 替换过于规整的序列结构
        # 只替换每个标记的第一次出现，避免过度修改
        sequence_replacements = {
            "首先，": "",  # 删除"首先"使结构不那么机械
            "其次，": "在此基础上，",
            "再次，": "同样值得关注的是，",
            "最后，": "更重要的是，",
            "一方面，": "从一个角度来看，",
            "另一方面，": "从另一个维度来看，",
        }
        
        for old, new in sequence_replacements.items():
            result = result.replace(old, new, 1)  # 只替换第一次出现
        
        # 替换过度正式的表达
        formal_replacements = {
            "鉴于此，": "基于这一考虑，",
            "基于此，": "由此，",
            "综合以上分析，": "从上述分析来看，",
            "由此可见，": "这表明，",
            "由此可知，": "可以看出，",
        }
        
        for old, new in formal_replacements.items():
            result = result.replace(old, new)
        
        return result
    
    def _identify_changes(self, original: str, processed: str) -> List[str]:
        """
        识别主要变化
        
        Args:
            original: 原始文本
            processed: 处理后文本
            
        Returns:
            List[str]: 变化描述
        """
        changes = []
        
        # 检测序列词变化
        orig_seq = sum(original.count(m) for m in self.AI_MARKERS["sequence_markers"])
        proc_seq = sum(processed.count(m) for m in self.AI_MARKERS["sequence_markers"])
        if proc_seq < orig_seq:
            changes.append("减少了序列性词汇使用")
        
        # 检测填充短语变化
        orig_fill = sum(original.count(p) for p in self.AI_MARKERS["filler_phrases"])
        proc_fill = sum(processed.count(p) for p in self.AI_MARKERS["filler_phrases"])
        if proc_fill < orig_fill:
            changes.append("删除了填充性短语")
        
        # 长度变化
        if len(processed) < len(original) * 0.95:
            changes.append("精简了冗余表达")
        
        if not changes:
            changes.append("调整了表达方式")
        
        return changes
    
    def get_report(self, result: DeAIResult) -> str:
        """
        生成降AI报告
        
        Args:
            result: 降AI结果
            
        Returns:
            str: Markdown 格式的报告
        """
        lines = []
        lines.append("# 🤖 降AI处理报告\n")
        
        # AI概率变化
        reduction = result.ai_score_before - result.ai_score_after
        lines.append("## AI概率变化")
        lines.append(f"- 处理前AI概率：{result.ai_score_before:.1f}%")
        lines.append(f"- 处理后AI概率：{result.ai_score_after:.1f}%")
        lines.append(f"- 降低幅度：**{reduction:.1f}%**\n")
        
        # 主要变化
        lines.append("## 主要变化")
        for change in result.changes:
            lines.append(f"- {change}")
        
        return "\n".join(lines)
