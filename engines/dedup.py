# -*- coding: utf-8 -*-
"""
降重引擎模块
学术级文本改写，降低重复率
"""

from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
from core.llm import get_llm_client
from core.prompts import PromptTemplates

# 配置常量
MAX_CHANGES_TO_REPORT = 5  # 最多报告的变化条数


@dataclass
class DedupResult:
    """降重结果"""
    original: str
    processed: str
    changes: List[str]
    similarity_before: float
    similarity_after: float
    preserved_terms: List[str] = field(default_factory=list)


class DedupEngine:
    """
    降重引擎
    
    对学术文本进行改写，降低与原文的相似度
    
    使用示例:
        engine = DedupEngine()
        result = engine.process(content, strength=3)
    """
    
    # 默认保留的学术术语
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
        
        # 分段处理长文本
        if len(content) > 2000:
            return self._process_long_text(content, strength, all_terms)
        
        return self._process_single(content, strength, all_terms)
    
    def _process_single(
        self,
        content: str,
        strength: int,
        preserve_terms: List[str]
    ) -> DedupResult:
        """
        处理单段文本
        
        Args:
            content: 文本内容
            strength: 降重强度
            preserve_terms: 保留术语
            
        Returns:
            DedupResult: 降重结果
        """
        # 识别文本中出现的保留术语
        found_terms = [t for t in preserve_terms if t in content]
        
        prompt = PromptTemplates.DEDUP_ACADEMIC.format(
            content=content,
            strength=strength,
            preserve_terms=", ".join(found_terms) if found_terms else "无"
        )
        
        try:
            processed = self.llm.invoke(
                prompt,
                system_prompt="你是学术写作专家，擅长在保持学术规范的前提下改写文本。"
            )
            
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
                preserved_terms=found_terms
            )
            
        except Exception as e:
            return DedupResult(
                original=content,
                processed=content,
                changes=[f"处理失败: {str(e)}"],
                similarity_before=1.0,
                similarity_after=1.0,
                preserved_terms=found_terms
            )
    
    def _process_long_text(
        self,
        content: str,
        strength: int,
        preserve_terms: List[str]
    ) -> DedupResult:
        """
        处理长文本（分段处理）
        
        Args:
            content: 长文本
            strength: 降重强度
            preserve_terms: 保留术语
            
        Returns:
            DedupResult: 降重结果
        """
        # 按段落分割
        paragraphs = content.split("\n\n")
        processed_paragraphs = []
        all_changes = []
        
        for para in paragraphs:
            if len(para.strip()) < 50:
                # 短段落直接保留
                processed_paragraphs.append(para)
            else:
                result = self._process_single(para, strength, preserve_terms)
                processed_paragraphs.append(result.processed)
                all_changes.extend(result.changes)
        
        processed = "\n\n".join(processed_paragraphs)
        
        # 计算整体相似度
        similarity_after = self._calculate_similarity(content, processed)
        
        # 识别文本中出现的保留术语
        found_terms = [t for t in preserve_terms if t in content]
        
        return DedupResult(
            original=content,
            processed=processed,
            changes=list(set(all_changes))[:10],
            similarity_before=1.0,
            similarity_after=similarity_after,
            preserved_terms=found_terms
        )
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算文本相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            float: 相似度 (0-1)
        """
        from difflib import SequenceMatcher
        
        # 使用 SequenceMatcher 计算相似度
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _identify_changes(self, original: str, processed: str) -> List[str]:
        """
        识别主要变化
        
        Args:
            original: 原始文本
            processed: 处理后文本
            
        Returns:
            List[str]: 变化描述列表
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
        orig_sentences = original.count("。") + original.count(".")
        proc_sentences = processed.count("。") + processed.count(".")
        
        if proc_sentences > orig_sentences * 1.3:
            changes.append("拆分了长句，增加了句子数量")
        elif proc_sentences < orig_sentences * 0.7:
            changes.append("合并了相关句子，增强连贯性")
        
        # 检查是否有结构调整
        sequence_markers = ["首先", "其次", "再次", "最后", "第一", "第二"]
        orig_seq = sum(1 for m in sequence_markers if m in original)
        proc_seq = sum(1 for m in sequence_markers if m in processed)
        if proc_seq < orig_seq:
            changes.append("调整了论述结构，减少序列词使用")
        
        # 检查同义词替换
        # 简单检测：如果相似度中等但内容长度相近，说明进行了同义词替换
        similarity = self._calculate_similarity(original, processed)
        if 0.4 < similarity < 0.8 and 0.9 < len_ratio < 1.1:
            changes.append("进行了同义词替换和表达重构")
        
        # 检查段落结构变化
        orig_paras = original.count("\n\n")
        proc_paras = processed.count("\n\n")
        if proc_paras > orig_paras + 1:
            changes.append("增加了段落划分")
        elif proc_paras < orig_paras - 1:
            changes.append("合并了段落，增强整体性")
        
        if not changes:
            changes.append("调整了词汇和表达方式")
        
        return changes[:MAX_CHANGES_TO_REPORT]  # 最多返回指定数量的变化
    
    def get_dedup_report(self, result: DedupResult) -> str:
        """
        生成降重报告
        
        Args:
            result: 降重结果
            
        Returns:
            str: Markdown 格式的报告
        """
        lines = []
        lines.append("# 📊 降重处理报告\n")
        
        # 相似度变化
        reduction = (result.similarity_before - result.similarity_after) * 100
        lines.append(f"## 相似度变化")
        lines.append(f"- 处理前相似度：{result.similarity_before * 100:.1f}%")
        lines.append(f"- 处理后相似度：{result.similarity_after * 100:.1f}%")
        lines.append(f"- 降重幅度：**{reduction:.1f}%**\n")
        
        # 保留术语
        if result.preserved_terms:
            lines.append("## 保留的专业术语")
            lines.append(", ".join(result.preserved_terms))
            lines.append("")
        
        # 主要变化
        lines.append("## 主要变化")
        for change in result.changes:
            lines.append(f"- {change}")
        
        return "\n".join(lines)
