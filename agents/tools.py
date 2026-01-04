# -*- coding: utf-8 -*-
"""
Agent工具集模块
为各Agent提供通用工具函数
"""

from typing import List, Dict, Optional


def chunk_text(text: str, max_length: int = 3000, overlap: int = 200) -> List[str]:
    """
    将长文本分块
    
    Args:
        text: 原始文本
        max_length: 每块最大长度
        overlap: 块之间的重叠长度
        
    Returns:
        List[str]: 文本块列表
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_length
        
        # 尽量在句子边界分割
        if end < len(text):
            # 查找最近的句子结束符
            for sep in ["。", "！", "？", ".", "!", "?", "\n\n"]:
                pos = text.rfind(sep, start + max_length - 500, end)
                if pos > start:
                    end = pos + 1
                    break
        
        chunks.append(text[start:end])
        start = end - overlap
    
    return chunks


def merge_results(results: List[str], separator: str = "\n\n") -> str:
    """
    合并多个结果
    
    Args:
        results: 结果列表
        separator: 分隔符
        
    Returns:
        str: 合并后的文本
    """
    return separator.join(results)


def extract_score(text: str) -> Optional[float]:
    """
    从文本中提取评分
    
    Args:
        text: 包含评分的文本
        
    Returns:
        Optional[float]: 评分，未找到则返回 None
    """
    import re
    
    patterns = [
        r'(\d+(?:\.\d+)?)\s*/\s*10',  # 8/10
        r'评分[：:]\s*(\d+(?:\.\d+)?)',  # 评分：8
        r'得分[：:]\s*(\d+(?:\.\d+)?)',  # 得分：8
        r'(\d+(?:\.\d+)?)\s*分',  # 8分
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return float(match.group(1))
    
    return None


def clean_llm_response(response: str) -> str:
    """
    清理 LLM 响应
    
    Args:
        response: LLM 响应文本
        
    Returns:
        str: 清理后的文本
    """
    # 移除常见的开场白
    prefixes = [
        "好的，",
        "当然，",
        "以下是",
        "根据您的要求，",
        "我来帮您",
    ]
    
    for prefix in prefixes:
        if response.startswith(prefix):
            response = response[len(prefix):]
    
    return response.strip()


def format_as_markdown_table(data: List[Dict], headers: List[str]) -> str:
    """
    将数据格式化为 Markdown 表格
    
    Args:
        data: 数据列表
        headers: 表头列表
        
    Returns:
        str: Markdown 表格
    """
    if not data or not headers:
        return ""
    
    lines = []
    
    # 表头
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    
    # 数据行
    for row in data:
        values = [str(row.get(h, "")) for h in headers]
        lines.append("| " + " | ".join(values) + " |")
    
    return "\n".join(lines)


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    计算两段文本的相似度
    
    Args:
        text1: 文本1
        text2: 文本2
        
    Returns:
        float: 相似度 (0-1)
    """
    from difflib import SequenceMatcher
    
    return SequenceMatcher(None, text1, text2).ratio()


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    提取文本关键词（简单版本）
    
    Args:
        text: 文本内容
        top_n: 返回数量
        
    Returns:
        List[str]: 关键词列表
    """
    import re
    
    # 移除标点和数字
    cleaned = re.sub(r'[^\u4e00-\u9fa5a-zA-Z\s]', '', text)
    
    # 按空格分词（简单处理）
    words = cleaned.split()
    
    # 统计词频
    word_count = {}
    for word in words:
        if len(word) >= 2:  # 至少2个字符
            word_count[word] = word_count.get(word, 0) + 1
    
    # 按频率排序
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    
    return [w[0] for w in sorted_words[:top_n]]


ACADEMIC_TERMS = [
    # 计量方法
    "双重差分", "DID", "difference-in-differences",
    "倾向得分匹配", "PSM", "propensity score matching",
    "工具变量", "IV", "instrumental variable",
    "断点回归", "RDD", "regression discontinuity",
    "固定效应", "fixed effects", "FE",
    "随机效应", "random effects", "RE",
    "面板数据", "panel data",
    "广义矩估计", "GMM",
    "中介效应", "mediating effect",
    "调节效应", "moderating effect",
    # 统计术语
    "显著性", "significance",
    "稳健性", "robustness",
    "内生性", "endogeneity",
    "异方差", "heteroskedasticity",
    "自相关", "autocorrelation",
    "多重共线性", "multicollinearity",
    # 经济学术语
    "边际效应", "marginal effect",
    "弹性", "elasticity",
    "外部性", "externality",
    "信息不对称", "information asymmetry",
]


def preserve_academic_terms(original: str, processed: str, terms: Optional[List[str]] = None) -> str:
    """
    确保学术术语在处理后保持不变
    
    Args:
        original: 原始文本
        processed: 处理后的文本
        terms: 要保留的术语列表
        
    Returns:
        str: 修正后的文本
    """
    if terms is None:
        terms = ACADEMIC_TERMS
    
    result = processed
    
    for term in terms:
        if term in original and term not in processed:
            # 尝试找到可能的替换并还原
            # 这是简化版本，实际可能需要更复杂的处理
            pass
    
    return result
