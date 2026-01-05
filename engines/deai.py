# -*- coding: utf-8 -*-
"""
降AI引擎模块 (优化版)
消除AI写作痕迹，使文本更具人类学者风格

优化内容：
1. 使用专业的论文修改助手提示词
2. 增强规则替换策略
3. 分句精细处理
4. 多维度AI检测
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
import re
import random
from core.llm import get_llm_client


def split_sentences(text: str) -> List[str]:
    """分割文本为句子列表"""
    pattern = r'([。！？；.!?;])'
    parts = re.split(pattern, text)
    
    sentences = []
    i = 0
    while i < len(parts):
        if i + 1 < len(parts) and re.match(pattern, parts[i + 1]):
            sentences.append(parts[i] + parts[i + 1])
            i += 2
        else:
            if parts[i].strip():
                sentences.append(parts[i])
            i += 1
    
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
    sentences_processed: int = 0


class DeAIEngine:
    """
    降AI引擎 (优化版)
    
    使用专业的论文修改助手策略：
    1. 解释性扩展 - 使表达更详尽
    2. 系统性词汇替换 - 固定替换模式
    3. 句式微调 - 增强逻辑连接
    4. 消除AI典型特征 - 删除填充词/规整结构
    """
    
    # AI写作特征 (用于检测)
    AI_MARKERS = {
        "sequence_markers": [
            "首先", "其次", "再次", "最后", "第一", "第二", "第三", "第四",
            "一方面", "另一方面", "此外", "同时", "另外", "与此同时",
            "紧接着", "随后", "进一步",
        ],
        "filler_phrases": [
            "值得注意的是", "需要指出的是", "综上所述", "总的来说", 
            "总而言之", "不难发现", "显而易见", "毋庸置疑", "不可否认", 
            "众所周知", "事实上", "实际上", "可以说", "由此可见",
            "需要强调的是", "特别值得一提的是", "不言而喻",
        ],
        "vague_expressions": [
            "在一定程度上", "在某种意义上", "从某种角度来看",
            "可能会", "或许", "大概", "似乎", "貌似",
            "相对而言", "总体上看", "一般来说", "通常情况下",
        ],
        "overly_formal": [
            "鉴于此", "基于此", "据此", "由此可见", "由此可知", 
            "由上可知", "综合以上分析", "基于上述分析",
            "承上所述", "如前所述", "正如前文所述",
        ],
        "connector_abuse": [
            "然而", "但是", "因此", "所以", "故而", "于是",
            "尽管如此", "虽然如此", "即便如此",
        ]
    }
    
    # 专业词汇替换规则 (基于用户提供的策略)
    WORD_SUBSTITUTIONS = {
        # 动词替换
        "采用": ["运用", "选用"],
        "使用": ["运用", "借助"],
        "基于": ["依据", "根据"],
        "利用": ["借助", "运用"],
        "通过": ["借助", "经由"],
        "并": ["并且", "同时"],
        # 名词/形容词替换
        "原因": ["缘由"],
        "符合": ["契合"],
        "适合": ["适宜"],
        "特点": ["特性"],
        "提升": ["提高"],
        "提高": ["提升"],
        "极大地": ["在极大程度上"],
        "立即": ["即刻"],
        # 连词替换
        "和": ["以及", "与"],
        "及": ["以及"],
        "与": ["以及", "同"],
        "其": ["该", "相应"],
    }
    
    # 动词扩展规则
    VERB_EXPANSIONS = {
        "管理": ["开展管理工作", "进行管理"],
        "配置": ["进行配置", "完成配置操作"],
        "处理": ["执行处理工作", "进行处理"],
        "恢复": ["执行恢复操作"],
        "实现": ["得以实现", "用以实现"],
        "交互": ["进行数据交互", "开展交互"],
        "分析": ["开展分析工作", "进行分析"],
        "研究": ["开展研究工作", "进行深入研究"],
        "探讨": ["展开探讨", "进行探讨"],
        "验证": ["进行验证", "开展验证工作"],
        "检验": ["进行检验", "开展检验"],
        "优化": ["进行优化", "开展优化工作"],
    }
    
    # 填充短语删除映射
    FILLER_REPLACEMENTS = {
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
        "总而言之，": "",
        "由此可见，": "这表明，",
        "基于此，": "据此，",
        "鉴于此，": "考虑到这一点，",
    }
    
    # 句式转换模式
    SENTENCE_TRANSFORMS = [
        # (原始模式, 替换模式)
        (r"若(.+?)，则(.+)", r"如果\1，那么\2"),
        (r"(.+?)对(.+?)产生了(.+?)影响", r"\1对\2形成了\3作用"),
        (r"^首先，(.+?)。其次，(.+?)。最后，(.+?)。", r"\1。在此基础上，\2。更为重要的是，\3。"),
        (r"一方面，(.+?)；另一方面，(.+?)", r"\1。与此同时，\2"),
    ]
    
    # 专业论文修改助手系统提示词
    SYSTEM_PROMPT = """你的角色与目标：

你现在扮演一个专业的"论文（或技术文档）修改助手"。你的核心任务是接收一段中文原文（通常是技术性或学术性的描述），并将其改写成一种特定的风格。

这种风格的特点是：在保持专业性的前提下，增强文本的解释性和可读性，使表达更为详尽和流畅。最终输出应是一篇结构完整、逻辑清晰、语言精练的学术性文本。你的目标是精确地模仿分析得出的修改模式，生成"修改后"风格的文本，同时务必保持原文的核心技术信息、逻辑关系和事实准确性。

核心原则与新增要求（全局最高优先级）

坚守学术严谨性：
- 绝对保留专有名词：任何学术概念、技术术语、代码标识符、库名、配置项等专有内容必须保持原样，不得进行任何形式的修改或转写。
- 避免空泛修饰：除非原文已有，否则不得引入"系统性"、"根本性"、"本质上"等意义宽泛、缺乏具体指向的"高端"词汇，确保语言的精确度和客观性。

强化句子结构与连贯性：
- 优先使用完整句式：致力于输出结构完整的长句，减少使用逗号、破折号将句子分割成零散短语的情况。可以通过使用连词或调整语序，将原本分散的信息点有机地组织在一起。
- 确保行文流畅：改写应以提升文本的流畅度为目标，避免因生硬套用规则而导致语句结构不自然或逻辑断裂。

控制输出篇幅：
- 篇幅严格对等：修改后的文本长度应与原文大致相等。新增的解释性词语是为了使语义更清晰，而非简单地增加字数。

杜绝过度口语化：
- 维持书面语风格：严禁使用"至于xxx呢"、"这个嘛"等带有明显口语或语气助词的表达方式。

核心修改手法与规则

1. 解释性扩展（Verbose Elaboration）

动词短语扩展：将简洁的动词或动词短语，替换为更能体现动作过程的表达。
- "管理" -> "开展...的管理工作" 或 "进行...的管理"
- "交互" -> "进行数据交互" 或 "与...开展交互"
- "配置" -> "进行参数配置" 或 "对...完成配置"
- "处理" -> "执行...的处理工作" 或 "对...进行处理"
- "恢复" -> "执行恢复操作"
- "实现" -> "得以实现" 或 "用以实现"

增加辅助词/结构：在句子中审慎地添加语法上允许但非必需的词语，使句子更饱满。
- 适当增加 "了"、"的"、"地"、"所"、"可以"、"该"、"相应" 等。
- "提供功能" -> "具备...的功能" 或 "能够提供...功能"

2. 系统性词汇替换（Systematic Phrasing Substitution）

特定动词/介词/连词替换：
- 采用 / 使用 -> 运用 / 选用
- 基于 -> 依据 / 根据...来
- 利用 -> 借助 / 运用
- 通过 -> 借助 / 经由
- 和 / 及 / 与 -> 以及
- 并 -> 并且 / 同时
- 其 -> 该 / 其

特定名词/形容词替换：
- 原因 -> 缘由
- 符合 -> 契合
- 适合 -> 适宜
- 特点 -> 特性
- 提升 / 提高 -> 提升
- 极大(地) -> 在极大程度上
- 立即 -> 即刻

3. 括号内容处理（Bracket Content Integration）

解释性括号：对于原文中用于解释、举例或说明缩写的括号 (...) 或 （...），优先将其信息自然地融入句子。
- 融合方式：使用 "即"、"也就是"、"例如" 等引导词进行连接。
- 示例：ORM（对象关系映射） -> 对象关系映射（ORM）技术
- 示例：功能（如ORM、Admin） -> 具体功能，例如ORM与Admin

代码/标识符旁括号：对于紧跟在代码、文件名、类名旁的括号，通常直接移除括号，将其作为文本的自然组成部分。
- 示例：视图 (views.py) 中 -> 在视图文件views.py中
- 示例：权限类 (admin_panel.permissions) -> 权限类admin_panel.permissions

4. 句式微调（Sentence Structure Refinement）

使用"把"字句：在合适的场景下，可选用"把"字句以优化语序。
- 示例："会将对象移动" -> "会把相应的对象移动"

条件句式转换：将较书面的条件句式改为严谨的表达。
- 示例："若...，则..." -> "如果...，那么..." 或 "在...的情况下，便会..."

增加逻辑连接词：在句首或句中适当添加"首先"、"其次"、"此外"、"因此"、"综上所述"等词语，以增强逻辑的清晰度。

请根据以上规则进行改写，直接输出修改后的文本，不添加任何解释。"""

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
        
        # 2. 多策略人性化改写
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
            changes=changes,
            sentences_processed=len(split_sentences(content))
        )
    
    def estimate_ai_score(self, text: str) -> float:
        """
        估算AI写作概率
        
        基于多维度特征检测
        """
        if not text or len(text) < 30:
            return 0.0
        
        scores = []
        weights = []
        
        text_len_factor = len(text) / 1000
        
        # 1. 检测结构化序列（权重20%）
        sequence_count = sum(
            text.count(m) for m in self.AI_MARKERS["sequence_markers"]
        )
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
        """详细检测AI特征"""
        dimensions = {}
        ai_markers = []
        suggestions = []
        
        for category, markers in self.AI_MARKERS.items():
            found = [m for m in markers if m in text]
            count = len(found)
            
            if category == "sequence_markers":
                dimensions["结构规整度"] = min(10, count * 2)
                if found:
                    ai_markers.extend([f"序列词: {m}" for m in found[:3]])
                    suggestions.append("减少使用'首先、其次、最后'等序列词，改用更自然的过渡")
                    
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
        人性化改写 - 多策略组合
        
        1. 先进行规则替换（快速）
        2. 再用LLM精修（深度）
        """
        # Step 1: 规则预处理
        pre_processed = self._rule_based_humanize(content)
        
        # Step 2: LLM 精修
        try:
            processed = self._llm_humanize(pre_processed)
            return processed
        except Exception:
            # 如果LLM调用失败，返回规则处理结果
            return pre_processed
    
    def _rule_based_humanize(self, content: str) -> str:
        """
        基于规则的人性化改写
        """
        result = content
        
        # 1. 删除/替换填充短语
        for old, new in self.FILLER_REPLACEMENTS.items():
            result = result.replace(old, new)
        
        # 2. 词汇替换
        for word, replacements in self.WORD_SUBSTITUTIONS.items():
            if word in result:
                replacement = random.choice(replacements)
                # 只替换部分，保持自然
                count = result.count(word)
                replace_count = max(1, count // 2)
                for _ in range(replace_count):
                    result = result.replace(word, replacement, 1)
        
        # 3. 动词扩展 (选择性)
        for verb, expansions in self.VERB_EXPANSIONS.items():
            if verb in result and random.random() < 0.3:
                expansion = random.choice(expansions)
                result = result.replace(verb, expansion, 1)
        
        # 4. 句式转换
        for pattern, replacement in self.SENTENCE_TRANSFORMS:
            if random.random() < 0.5:
                result = re.sub(pattern, replacement, result)
        
        # 5. 打破规整的序列结构
        sequence_replacements = {
            "首先，": "",
            "其次，": "在此基础上，",
            "再次，": "同样值得关注的是，",
            "最后，": "更为重要的是，",
            "一方面，": "从一个角度来看，",
            "另一方面，": "从另一个维度来看，",
        }
        for old, new in sequence_replacements.items():
            result = result.replace(old, new, 1)
        
        return result
    
    def _llm_humanize(self, content: str) -> str:
        """
        使用LLM进行人性化改写
        """
        # 分段处理长文本
        if len(content) > 2000:
            paragraphs = content.split("\n\n")
            processed_paragraphs = []
            for para in paragraphs:
                if len(para.strip()) < 50:
                    processed_paragraphs.append(para)
                else:
                    processed_paragraphs.append(self._llm_humanize_single(para))
            return "\n\n".join(processed_paragraphs)
        else:
            return self._llm_humanize_single(content)
    
    def _llm_humanize_single(self, content: str) -> str:
        """
        LLM改写单段文本
        """
        prompt = f"""请对以下学术文本进行改写，消除AI写作痕迹，使其更像人类学者的表达。

## 改写要求
1. 保持原文的核心观点和专业术语
2. 消除规整的序列结构（首先、其次、最后）
3. 删除填充性短语（值得注意的是、综上所述等）
4. 变化句子长度，避免过于均匀
5. 使用更自然的过渡和连接
6. 保持学术规范性和专业性
7. 输出长度与原文大致相等

## 原文
{content}

## 要求
直接输出改写后的文本，不添加任何解释说明。"""

        try:
            processed = self.llm.invoke(
                prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.75  # 稍高的温度增加变化性
            )
            return processed.strip()
        except Exception:
            return content
    
    def _identify_changes(self, original: str, processed: str) -> List[str]:
        """识别主要变化"""
        changes = []
        
        # 检测序列词变化
        orig_seq = sum(original.count(m) for m in self.AI_MARKERS["sequence_markers"])
        proc_seq = sum(processed.count(m) for m in self.AI_MARKERS["sequence_markers"])
        if proc_seq < orig_seq:
            changes.append(f"减少了{orig_seq - proc_seq}处序列性词汇")
        
        # 检测填充短语变化
        orig_fill = sum(original.count(p) for p in self.AI_MARKERS["filler_phrases"])
        proc_fill = sum(processed.count(p) for p in self.AI_MARKERS["filler_phrases"])
        if proc_fill < orig_fill:
            changes.append(f"删除了{orig_fill - proc_fill}处填充性短语")
        
        # 词汇替换检测
        replaced_count = 0
        for word in self.WORD_SUBSTITUTIONS.keys():
            if word in original and word not in processed:
                replaced_count += 1
        if replaced_count > 0:
            changes.append(f"进行了{replaced_count}处词汇优化")
        
        # 句式变化检测
        orig_sentences = len(split_sentences(original))
        proc_sentences = len(split_sentences(processed))
        if abs(proc_sentences - orig_sentences) >= 2:
            changes.append("调整了句子结构")
        
        # 长度变化
        len_ratio = len(processed) / len(original) if len(original) > 0 else 1
        if len_ratio < 0.95:
            changes.append("精简了冗余表达")
        elif len_ratio > 1.05:
            changes.append("增强了解释性表达")
        
        if not changes:
            changes.append("调整了表达方式，增强自然度")
        
        return changes[:5]
    
    def get_report(self, result: DeAIResult) -> str:
        """生成降AI报告"""
        lines = []
        lines.append("## 🤖 降AI处理报告\n")
        
        # AI概率变化
        reduction = result.ai_score_before - result.ai_score_after
        reduction_pct = (reduction / result.ai_score_before * 100) if result.ai_score_before > 0 else 0
        
        lines.append("### AI概率变化")
        lines.append(f"- 处理前AI概率：{result.ai_score_before:.1f}%")
        lines.append(f"- 处理后AI概率：{result.ai_score_after:.1f}%")
        lines.append(f"- **降低幅度：{reduction:.1f}% ({reduction_pct:.0f}%)**")
        lines.append(f"- 处理句子数：{result.sentences_processed}")
        lines.append("")
        
        # 效果评估
        if result.ai_score_after < 30:
            lines.append("### 效果评估")
            lines.append("✅ **优秀** - AI痕迹已基本消除，文本自然度高")
        elif result.ai_score_after < 50:
            lines.append("### 效果评估")
            lines.append("⚠️ **良好** - AI痕迹显著减少，建议进一步优化")
        else:
            lines.append("### 效果评估")
            lines.append("❌ **需改进** - 仍有明显AI痕迹，建议手动调整")
        lines.append("")
        
        # 主要变化
        lines.append("### 主要变化")
        for change in result.changes:
            lines.append(f"- {change}")
        
        return "\n".join(lines)
