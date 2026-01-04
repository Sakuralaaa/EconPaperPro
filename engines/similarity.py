# -*- coding: utf-8 -*-
"""
相似度检测模块
检测文本相似度，找出相似片段
"""

from typing import List, Tuple, Dict
from dataclasses import dataclass, field
from difflib import SequenceMatcher
import re


@dataclass
class SimilarityResult:
    """相似度检测结果"""
    overall_similarity: float  # 整体相似度 0-1
    char_similarity: float  # 字符级相似度
    word_similarity: float  # 词级相似度
    ngram_similarity: float  # N-gram相似度
    similar_segments: List[Tuple[str, str, float]] = field(default_factory=list)  # 相似片段


class SimilarityChecker:
    """
    相似度检测器
    
    检测两段文本的相似度，支持多种算法
    
    使用示例:
        checker = SimilarityChecker()
        result = checker.check(text1, text2)
    """
    
    def __init__(self, ngram_size: int = 3):
        """
        初始化相似度检测器
        
        Args:
            ngram_size: N-gram 的 N 值
        """
        self.ngram_size = ngram_size
    
    def check(self, text1: str, text2: str) -> SimilarityResult:
        """
        检测两段文本的相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            SimilarityResult: 相似度结果
        """
        # 计算各类相似度
        char_sim = self._char_similarity(text1, text2)
        word_sim = self._word_similarity(text1, text2)
        ngram_sim = self._ngram_similarity(text1, text2)
        
        # 综合相似度（加权平均）
        overall = char_sim * 0.3 + word_sim * 0.4 + ngram_sim * 0.3
        
        # 找出相似片段
        similar_segments = self._find_similar_segments(text1, text2)
        
        return SimilarityResult(
            overall_similarity=overall,
            char_similarity=char_sim,
            word_similarity=word_sim,
            ngram_similarity=ngram_sim,
            similar_segments=similar_segments
        )
    
    def _char_similarity(self, text1: str, text2: str) -> float:
        """
        字符级相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            float: 相似度 0-1
        """
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _word_similarity(self, text1: str, text2: str) -> float:
        """
        词级相似度（简单分词）
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            float: 相似度 0-1
        """
        # 简单分词
        words1 = set(self._tokenize(text1))
        words2 = set(self._tokenize(text2))
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard 相似度
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _ngram_similarity(self, text1: str, text2: str) -> float:
        """
        N-gram 相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            float: 相似度 0-1
        """
        ngrams1 = set(self._get_ngrams(text1))
        ngrams2 = set(self._get_ngrams(text2))
        
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = len(ngrams1 & ngrams2)
        union = len(ngrams1 | ngrams2)
        
        return intersection / union if union > 0 else 0.0
    
    def _tokenize(self, text: str) -> List[str]:
        """
        简单分词
        
        Args:
            text: 文本
            
        Returns:
            List[str]: 词列表
        """
        # 移除标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', text)
        
        # 按空格分割（适用于英文）
        words = text.split()
        
        # 对中文进行简单的双字切分
        chinese_words = []
        for word in words:
            if re.match(r'[\u4e00-\u9fa5]+', word):
                # 中文，双字切分
                for i in range(len(word) - 1):
                    chinese_words.append(word[i:i+2])
            else:
                chinese_words.append(word)
        
        return chinese_words if chinese_words else words
    
    def _get_ngrams(self, text: str) -> List[str]:
        """
        获取 N-gram
        
        Args:
            text: 文本
            
        Returns:
            List[str]: N-gram 列表
        """
        # 移除空白
        text = re.sub(r'\s+', '', text)
        
        if len(text) < self.ngram_size:
            return [text]
        
        ngrams = []
        for i in range(len(text) - self.ngram_size + 1):
            ngrams.append(text[i:i + self.ngram_size])
        
        return ngrams
    
    def _find_similar_segments(
        self,
        text1: str,
        text2: str,
        min_length: int = 10,
        threshold: float = 0.8
    ) -> List[Tuple[str, str, float]]:
        """
        找出相似片段
        
        Args:
            text1: 文本1
            text2: 文本2
            min_length: 最小片段长度
            threshold: 相似度阈值
            
        Returns:
            List[Tuple[str, str, float]]: 相似片段列表 (片段1, 片段2, 相似度)
        """
        matcher = SequenceMatcher(None, text1, text2)
        similar_segments = []
        
        for match in matcher.get_matching_blocks():
            if match.size >= min_length:
                segment1 = text1[match.a:match.a + match.size]
                segment2 = text2[match.b:match.b + match.size]
                similarity = 1.0  # 完全匹配
                similar_segments.append((segment1, segment2, similarity))
        
        return similar_segments[:10]  # 最多返回10个
    
    def get_report(self, result: SimilarityResult) -> str:
        """
        生成相似度报告
        
        Args:
            result: 相似度结果
            
        Returns:
            str: Markdown 格式的报告
        """
        lines = []
        lines.append("# 📊 相似度检测报告\n")
        
        lines.append("## 综合相似度")
        lines.append(f"**{result.overall_similarity * 100:.1f}%**\n")
        
        lines.append("## 各维度相似度")
        lines.append(f"- 字符级相似度：{result.char_similarity * 100:.1f}%")
        lines.append(f"- 词级相似度：{result.word_similarity * 100:.1f}%")
        lines.append(f"- N-gram相似度：{result.ngram_similarity * 100:.1f}%\n")
        
        if result.similar_segments:
            lines.append("## 相似片段")
            for i, (seg1, seg2, sim) in enumerate(result.similar_segments[:5], 1):
                lines.append(f"### 片段 {i} (相似度: {sim * 100:.0f}%)")
                lines.append(f"```\n{seg1[:100]}...\n```")
        
        return "\n".join(lines)
    
    def check_against_corpus(
        self,
        text: str,
        corpus: List[str]
    ) -> Dict[int, float]:
        """
        检测文本与语料库的相似度
        
        Args:
            text: 待检测文本
            corpus: 语料库
            
        Returns:
            Dict[int, float]: 与各文档的相似度
        """
        results = {}
        
        for i, doc in enumerate(corpus):
            result = self.check(text, doc)
            results[i] = result.overall_similarity
        
        return results
