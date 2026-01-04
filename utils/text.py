# -*- coding: utf-8 -*-
"""
文本处理工具模块
提供各种文本处理函数
"""

from typing import List, Tuple, Optional
import re


class TextProcessor:
    """
    文本处理器
    
    提供文本清洗、分割、统计等功能
    
    使用示例:
        processor = TextProcessor()
        cleaned = processor.clean(text)
        sentences = processor.split_sentences(text)
    """
    
    def clean(self, text: str) -> str:
        """
        清洗文本
        
        Args:
            text: 原始文本
            
        Returns:
            str: 清洗后的文本
        """
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        
        # 标准化标点
        text = text.replace('，', ', ').replace('。', '. ')
        text = text.replace('；', '; ').replace('：', ': ')
        
        return text.strip()
    
    def split_sentences(self, text: str) -> List[str]:
        """
        分句
        
        Args:
            text: 文本
            
        Returns:
            List[str]: 句子列表
        """
        # 使用中英文句号分割
        sentences = re.split(r'(?<=[。！？.!?])\s*', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def split_paragraphs(self, text: str) -> List[str]:
        """
        分段
        
        Args:
            text: 文本
            
        Returns:
            List[str]: 段落列表
        """
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
    
    def count_words(self, text: str) -> int:
        """
        统计词数（中文按字计算，英文按空格分词）
        
        Args:
            text: 文本
            
        Returns:
            int: 词数
        """
        # 统计中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', text))
        
        # 统计英文单词
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        
        return chinese_chars + english_words
    
    def count_sentences(self, text: str) -> int:
        """
        统计句子数
        
        Args:
            text: 文本
            
        Returns:
            int: 句子数
        """
        return len(self.split_sentences(text))
    
    def extract_numbers(self, text: str) -> List[str]:
        """
        提取数字
        
        Args:
            text: 文本
            
        Returns:
            List[str]: 数字列表
        """
        return re.findall(r'\d+\.?\d*', text)
    
    def remove_citations(self, text: str) -> str:
        """
        移除引用标记
        
        Args:
            text: 文本
            
        Returns:
            str: 移除引用后的文本
        """
        # 移除 [1], [1,2], (Smith, 2020) 等格式
        text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
        text = re.sub(r'\([A-Za-z]+(?:\s+et\s+al\.?)?,\s*\d{4}\)', '', text)
        return text
    
    def extract_keywords_simple(self, text: str, top_n: int = 10) -> List[str]:
        """
        简单关键词提取
        
        Args:
            text: 文本
            top_n: 返回数量
            
        Returns:
            List[str]: 关键词列表
        """
        # 移除标点
        cleaned = re.sub(r'[^\u4e00-\u9fa5a-zA-Z\s]', '', text)
        
        # 中文双字切分 + 英文分词
        words = []
        for part in cleaned.split():
            if re.match(r'[\u4e00-\u9fa5]+', part):
                # 中文，双字切分
                for i in range(len(part) - 1):
                    words.append(part[i:i+2])
            else:
                words.append(part.lower())
        
        # 统计词频
        word_count = {}
        for word in words:
            if len(word) >= 2:
                word_count[word] = word_count.get(word, 0) + 1
        
        # 排序
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        
        return [w[0] for w in sorted_words[:top_n]]
    
    def truncate(self, text: str, max_length: int, suffix: str = "...") -> str:
        """
        截断文本
        
        Args:
            text: 文本
            max_length: 最大长度
            suffix: 后缀
            
        Returns:
            str: 截断后的文本
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    def highlight_keywords(
        self,
        text: str,
        keywords: List[str],
        before: str = "**",
        after: str = "**"
    ) -> str:
        """
        高亮关键词
        
        Args:
            text: 文本
            keywords: 关键词列表
            before: 前缀标记
            after: 后缀标记
            
        Returns:
            str: 高亮后的文本
        """
        result = text
        for keyword in keywords:
            result = result.replace(keyword, f"{before}{keyword}{after}")
        return result
    
    def get_text_stats(self, text: str) -> dict:
        """
        获取文本统计信息
        
        Args:
            text: 文本
            
        Returns:
            dict: 统计信息
        """
        return {
            "char_count": len(text),
            "word_count": self.count_words(text),
            "sentence_count": self.count_sentences(text),
            "paragraph_count": len(self.split_paragraphs(text)),
            "avg_sentence_length": len(text) / max(1, self.count_sentences(text))
        }
