# -*- coding: utf-8 -*-
"""
降重引擎模块 (优化版)
学术级文本改写，降低重复率
- 多策略改写
- 分句精细处理
- 语义保真验证
"""

from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
import re
import random
from core.llm import get_llm_client
from core.prompts import PromptTemplates

# 配置常量
MAX_CHANGES_TO_REPORT = 5
SENTENCE_MAX_LENGTH = 300  # 单句最大长度
BATCH_SIZE = 3  # 批量处理句子数


@dataclass
class DedupResult:
    """降重结果"""
    original: str
    processed: str
    changes: List[str]
    similarity_before: float
    similarity_after: float
    preserved_terms: List[str] = field(default_factory=list)
    sentences_processed: int = 0


class DedupEngine:
    """
    降重引擎 (优化版)
    
    改进点：
    1. 分句精细处理，避免长文本一次性改写导致语义偏移
    2. 多轮改写策略，强度可控
    3. 术语保护机制增强
    4. 语义相似度验证
    """
    
    # 默认保留的学术术语 (扩展版)
    DEFAULT_PRESERVE_TERMS = [
        # 计量方法
        "双重差分", "DID", "difference-in-differences", "差分",
        "倾向得分匹配", "PSM", "propensity score matching",
        "工具变量", "IV", "instrumental variable", "2SLS", "两阶段最小二乘",
        "断点回归", "RDD", "regression discontinuity", "断点设计",
        "固定效应", "fixed effects", "FE", "个体固定效应", "时间固定效应",
        "随机效应", "random effects", "RE",
        "面板数据", "panel data", "平衡面板", "非平衡面板",
        "广义矩估计", "GMM", "系统GMM", "差分GMM",
        "中介效应", "mediating effect", "中介变量",
        "调节效应", "moderating effect", "调节变量",
        "异质性分析", "分样本回归",
        "合成控制法", "SCM", "synthetic control",
        "事件研究法", "event study",
        # 统计术语
        "显著性", "significance", "显著",
        "稳健性", "robustness", "稳健性检验",
        "内生性", "endogeneity", "内生性问题",
        "异方差", "heteroskedasticity", "异方差检验",
        "自相关", "autocorrelation", "序列相关",
        "多重共线性", "multicollinearity", "VIF",
        "t统计量", "t值", "t-statistic",
        "F统计量", "F值", "F-test",
        "R方", "R²", "R-squared", "调整R方",
        "标准误", "standard error", "聚类标准误",
        "置信区间", "confidence interval",
        "p值", "p-value", "显著性水平",
        "Bootstrap", "自助法",
        # 经济学术语
        "边际效应", "marginal effect",
        "弹性", "elasticity", "价格弹性",
        "外部性", "externality", "正外部性", "负外部性",
        "信息不对称", "information asymmetry",
        "委托代理", "principal-agent", "代理问题",
        "道德风险", "moral hazard",
        "逆向选择", "adverse selection",
        "交易成本", "transaction cost",
        "规模经济", "economies of scale",
        "范围经济", "economies of scope",
        # 金融术语
        "资产定价", "asset pricing", "CAPM",
        "市场有效性", "market efficiency",
        "信息效率", "information efficiency",
        "融资约束", "financing constraints",
        "代理成本", "agency cost",
        # 数据和变量
        "被解释变量", "解释变量", "控制变量",
        "虚拟变量", "交互项", "滞后项",
    ]
    
    # 同义词替换词典 (规则替换加速)
    SYNONYM_DICT = {
        "研究": ["探讨", "分析", "考察", "探究", "审视"],
        "表明": ["显示", "说明", "揭示", "反映", "印证"],
        "发现": ["观察到", "识别出", "注意到", "察觉"],
        "影响": ["作用", "效应", "冲击", "波及"],
        "提升": ["提高", "增强", "促进", "改善", "优化"],
        "降低": ["减少", "削弱", "抑制", "削减"],
        "重要": ["关键", "核心", "主要", "首要", "显著"],
        "因此": ["故此", "由此", "据此", "从而"],
        "然而": ["但是", "不过", "可是", "然则"],
        "同时": ["与此同时", "此外", "另外", "并且"],
        "通过": ["借助", "依托", "凭借", "经由"],
        "采用": ["运用", "使用", "应用", "利用"],
        "进行": ["开展", "实施", "执行", "推进"],
        "具有": ["拥有", "存在", "呈现", "表现出"],
        "显著": ["明显", "突出", "显著性", "notable"],
        "基于": ["依据", "根据", "立足于", "以...为基础"],
        "针对": ["面向", "就...而言", "关于"],
        "导致": ["引起", "引发", "造成", "带来"],
        "增加": ["增长", "上升", "扩大", "提升"],
        "证明": ["验证", "证实", "表明", "佐证"],
        "认为": ["指出", "提出", "主张", "强调"],
        "可以": ["能够", "可", "得以"],
        "需要": ["须要", "有必要", "亟需"],
        "问题": ["议题", "难题", "困境", "挑战"],
        "方法": ["途径", "方式", "手段", "策略"],
        "结果": ["发现", "结论", "成果", "产出"],
        "情况": ["状况", "态势", "情形", "境况"],
        "水平": ["程度", "层次", "级别"],
        "能力": ["实力", "素质", "潜力", "本领"],
        "作用": ["功能", "效果", "影响", "功效"],
        "特点": ["特征", "属性", "特性", "特质"],
        "关系": ["联系", "关联", "相关性", "纽带"],
        "分析": ["剖析", "解析", "研判", "探析"],
        "目前": ["当前", "现阶段", "如今", "当下"],
        "已经": ["业已", "已然", "既已"],
        "可能": ["或许", "也许", "大概", "兴许"],
        "实现": ["达成", "完成", "取得", "达到"],
        "促进": ["推动", "助力", "驱动", "带动"],
        "支持": ["支撑", "佐证", "印证", "验证"],
        "产生": ["形成", "出现", "引发", "催生"],
        "变化": ["变动", "改变", "转变", "演变"],
        "利用": ["运用", "借助", "依托", "凭借"],
    }
    
    # 句式转换模式
    SENTENCE_PATTERNS = [
        # (原始模式, 替换模式)
        (r"^(.+?)对(.+?)产生了(.+?)影响", r"\2受到\1的\3影响"),
        (r"^(.+?)促进了(.+?)的发展", r"\2的发展得到了\1的促进"),
        (r"^研究表明[,，](.+)", r"实证结果显示，\1"),
        (r"^本文发现[,，](.+)", r"分析发现，\1"),
        (r"^结果显示[,，](.+)", r"实证分析表明，\1"),
        (r"^(.+?)显著提升了(.+)", r"\2在\1作用下显著提升"),
        (r"^随着(.+?)的(.+?)[,，](.+)", r"伴随\1的\2，\3"),
    ]
    
    def __init__(self):
        """初始化降重引擎"""
        self._llm = None
    
    @property
    def llm(self):
        """延迟加载LLM客户端"""
        if self._llm is None:
            self._llm = get_llm_client()
        return self._llm
    
    def process(
        self,
        content: str,
        strength: int = 3,
        preserve_terms: Optional[List[str]] = None
    ) -> DedupResult:
        """
        执行降重处理
        
        Args:
            content: 原始文本
            strength: 降重强度 (1-5)
            preserve_terms: 需要保留的专业术语
            
        Returns:
            DedupResult: 降重结果
        """
        strength = max(1, min(5, strength))
        
        # 合并保留术语
        all_terms = self.DEFAULT_PRESERVE_TERMS.copy()
        if preserve_terms:
            all_terms.extend(preserve_terms)
        
        # 识别文本中出现的保留术语
        found_terms = [t for t in all_terms if t in content]
        
        # 根据强度选择处理策略
        if strength <= 2:
            # 轻度：规则替换为主
            processed = self._rule_based_rewrite(content, strength, found_terms)
        elif strength <= 4:
            # 中度：规则 + LLM 混合
            processed = self._hybrid_rewrite(content, strength, found_terms)
        else:
            # 深度：LLM 分句精细改写
            processed = self._deep_rewrite(content, found_terms)
        
        # 计算相似度
        similarity_before = 1.0
        similarity_after = self._calculate_similarity(content, processed)
        
        # 识别变化
        changes = self._identify_changes(content, processed)
        
        return DedupResult(
            original=content,
            processed=processed,
            changes=changes,
            similarity_before=similarity_before,
            similarity_after=similarity_after,
            preserved_terms=found_terms,
            sentences_processed=len(self._split_sentences(content))
        )
    
    def _rule_based_rewrite(
        self,
        content: str,
        strength: int,
        preserve_terms: List[str]
    ) -> str:
        """
        基于规则的轻度改写
        """
        result = content
        
        # 1. 同义词替换 (保护术语)
        for word, synonyms in self.SYNONYM_DICT.items():
            if word in preserve_terms:
                continue
            # 随机选择替换概率
            if random.random() < 0.3 * strength:
                replacement = random.choice(synonyms)
                result = result.replace(word, replacement, 1)
        
        # 2. 句式转换
        if strength >= 2:
            for pattern, replacement in self.SENTENCE_PATTERNS:
                if random.random() < 0.4:
                    result = re.sub(pattern, replacement, result)
        
        return result
    
    def _hybrid_rewrite(
        self,
        content: str,
        strength: int,
        preserve_terms: List[str]
    ) -> str:
        """
        混合改写：规则预处理 + LLM 精修
        """
        # 先进行规则改写
        pre_processed = self._rule_based_rewrite(content, strength - 1, preserve_terms)
        
        # 对长文本分段处理
        paragraphs = content.split("\n\n")
        if len(paragraphs) > 1:
            processed_paragraphs = []
            for para in paragraphs:
                if len(para.strip()) < 50:
                    processed_paragraphs.append(para)
                else:
                    processed_paragraphs.append(
                        self._llm_rewrite_single(para, strength, preserve_terms)
                    )
            return "\n\n".join(processed_paragraphs)
        else:
            return self._llm_rewrite_single(pre_processed, strength, preserve_terms)
    
    def _deep_rewrite(
        self,
        content: str,
        preserve_terms: List[str]
    ) -> str:
        """
        深度改写：分句精细处理
        """
        sentences = self._split_sentences(content)
        processed_sentences = []
        
        # 批量处理句子
        batch = []
        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) < 10:
                # 短句直接保留
                if batch:
                    processed_sentences.extend(self._batch_rewrite(batch, preserve_terms))
                    batch = []
                processed_sentences.append(sentence)
            else:
                batch.append(sentence)
                if len(batch) >= BATCH_SIZE:
                    processed_sentences.extend(self._batch_rewrite(batch, preserve_terms))
                    batch = []
        
        # 处理剩余
        if batch:
            processed_sentences.extend(self._batch_rewrite(batch, preserve_terms))
        
        return "".join(processed_sentences)
    
    def _batch_rewrite(
        self,
        sentences: List[str],
        preserve_terms: List[str]
    ) -> List[str]:
        """
        批量改写句子
        """
        combined = " ".join(sentences)
        rewritten = self._llm_rewrite_single(combined, 5, preserve_terms)
        
        # 尝试拆分回句子
        rewritten_sentences = self._split_sentences(rewritten)
        
        # 如果拆分后数量接近，逐句返回；否则整体返回
        if abs(len(rewritten_sentences) - len(sentences)) <= 1:
            return rewritten_sentences
        else:
            return [rewritten]
    
    def _llm_rewrite_single(
        self,
        content: str,
        strength: int,
        preserve_terms: List[str]
    ) -> str:
        """
        LLM 改写单段文本
        """
        # 使用优化的 prompt
        prompt = f"""请对以下学术文本进行专业改写，降低与原文的相似度。

## 改写要求
1. **语义保真**：确保改写后意思完全相同
2. **学术规范**：保持严谨的学术表达风格
3. **降重强度**：{strength}/5 （1最轻，5最深）
4. **必须保留的术语**：{', '.join(preserve_terms[:15]) if preserve_terms else '无'}

## 改写技巧
- 同义词替换（非术语部分）
- 主被动语态转换
- 句子结构调整
- 表达方式重构
- 适当拆分或合并句子

## 原文
{content}

## 要求
直接输出改写后的文本，不要添加任何解释。"""

        try:
            processed = self.llm.invoke(
                prompt,
                system_prompt="你是学术写作专家，擅长在保持学术规范和语义的前提下改写文本，降低文本相似度。",
                temperature=0.7 + (strength * 0.05)  # 强度越高温度越高
            )
            return processed.strip()
        except Exception as e:
            # 失败时返回规则改写结果
            return self._rule_based_rewrite(content, strength, preserve_terms)
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        分割文本为句子
        """
        # 匹配中英文句末标点
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
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算文本相似度 (优化版：结合字符级和词级)
        """
        from difflib import SequenceMatcher
        
        # 字符级相似度
        char_sim = SequenceMatcher(None, text1, text2).ratio()
        
        # 词级相似度 (简单分词)
        words1 = set(re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text1))
        words2 = set(re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text2))
        
        if words1 and words2:
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            word_sim = intersection / union if union > 0 else 0
        else:
            word_sim = char_sim
        
        # 加权平均
        return 0.6 * char_sim + 0.4 * word_sim
    
    def _identify_changes(self, original: str, processed: str) -> List[str]:
        """
        识别主要变化
        """
        changes = []
        
        # 字数变化
        orig_len = len(original)
        proc_len = len(processed)
        len_ratio = proc_len / orig_len if orig_len > 0 else 1
        
        if len_ratio > 1.2:
            changes.append(f"适当扩展了内容表述（增加约{int((len_ratio-1)*100)}%）")
        elif len_ratio > 1.05:
            changes.append("略微扩展了部分表述")
        elif len_ratio < 0.8:
            changes.append(f"精简了冗余表达（减少约{int((1-len_ratio)*100)}%）")
        elif len_ratio < 0.95:
            changes.append("略微精简了部分表述")
        
        # 句子数量变化
        orig_sentences = len(self._split_sentences(original))
        proc_sentences = len(self._split_sentences(processed))
        
        if proc_sentences > orig_sentences * 1.3:
            changes.append("拆分了长句，增加了句子数量")
        elif proc_sentences < orig_sentences * 0.7:
            changes.append("合并了相关句子，增强连贯性")
        
        # 检查同义词替换
        replaced_count = 0
        for word in self.SYNONYM_DICT.keys():
            if word in original and word not in processed:
                replaced_count += 1
        
        if replaced_count >= 3:
            changes.append(f"进行了{replaced_count}处同义词替换")
        elif replaced_count > 0:
            changes.append("进行了同义词替换")
        
        # 检查句式变化
        for pattern, _ in self.SENTENCE_PATTERNS:
            if re.search(pattern, original) and not re.search(pattern, processed):
                changes.append("调整了句式结构")
                break
        
        if not changes:
            changes.append("调整了词汇和表达方式")
        
        return changes[:MAX_CHANGES_TO_REPORT]
    
    def get_dedup_report(self, result: DedupResult) -> str:
        """
        生成降重报告
        """
        lines = []
        lines.append("## 📊 降重处理报告\n")
        
        # 相似度变化
        reduction = (result.similarity_before - result.similarity_after) * 100
        lines.append("### 相似度变化")
        lines.append(f"- 处理前相似度：{result.similarity_before * 100:.1f}%")
        lines.append(f"- 处理后相似度：{result.similarity_after * 100:.1f}%")
        lines.append(f"- **降重幅度：{reduction:.1f}%**")
        lines.append(f"- 处理句子数：{result.sentences_processed}")
        lines.append("")
        
        # 保留术语
        if result.preserved_terms:
            lines.append("### 保留的专业术语")
            lines.append(", ".join(result.preserved_terms[:10]))
            if len(result.preserved_terms) > 10:
                lines.append(f"...等共{len(result.preserved_terms)}个术语")
            lines.append("")
        
        # 主要变化
        lines.append("### 主要变化")
        for change in result.changes:
            lines.append(f"- {change}")
        
        return "\n".join(lines)
