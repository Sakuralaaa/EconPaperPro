# -*- coding: utf-8 -*-
"""
差异对比工具模块
生成文本差异对比视图
"""

from typing import List, Tuple
from difflib import SequenceMatcher, unified_diff
from dataclasses import dataclass


@dataclass
class DiffSegment:
    """差异片段"""
    type: str  # "equal", "insert", "delete", "replace"
    old_text: str
    new_text: str


class DiffGenerator:
    """
    差异生成器
    
    生成两段文本的差异对比
    
    使用示例:
        generator = DiffGenerator()
        diff = generator.generate(old_text, new_text)
        html = generator.to_html(diff)
    """
    
    def generate(self, old_text: str, new_text: str) -> List[DiffSegment]:
        """
        生成差异
        
        Args:
            old_text: 原始文本
            new_text: 新文本
            
        Returns:
            List[DiffSegment]: 差异片段列表
        """
        matcher = SequenceMatcher(None, old_text, new_text)
        segments = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            old_segment = old_text[i1:i2]
            new_segment = new_text[j1:j2]
            
            segments.append(DiffSegment(
                type=tag,
                old_text=old_segment,
                new_text=new_segment
            ))
        
        return segments
    
    def to_html(self, segments: List[DiffSegment]) -> str:
        """
        将差异转换为 HTML
        
        Args:
            segments: 差异片段列表
            
        Returns:
            str: HTML 文本
        """
        html_parts = []
        
        for seg in segments:
            if seg.type == "equal":
                html_parts.append(f'<span>{self._escape_html(seg.new_text)}</span>')
            elif seg.type == "insert":
                html_parts.append(f'<span class="diff-insert" style="background-color: #d4edda; color: #155724;">{self._escape_html(seg.new_text)}</span>')
            elif seg.type == "delete":
                html_parts.append(f'<span class="diff-delete" style="background-color: #f8d7da; color: #721c24; text-decoration: line-through;">{self._escape_html(seg.old_text)}</span>')
            elif seg.type == "replace":
                html_parts.append(f'<span class="diff-delete" style="background-color: #f8d7da; color: #721c24; text-decoration: line-through;">{self._escape_html(seg.old_text)}</span>')
                html_parts.append(f'<span class="diff-insert" style="background-color: #d4edda; color: #155724;">{self._escape_html(seg.new_text)}</span>')
        
        return ''.join(html_parts)
    
    def to_markdown(self, segments: List[DiffSegment]) -> str:
        """
        将差异转换为 Markdown（使用删除线和粗体）
        
        Args:
            segments: 差异片段列表
            
        Returns:
            str: Markdown 文本
        """
        md_parts = []
        
        for seg in segments:
            if seg.type == "equal":
                md_parts.append(seg.new_text)
            elif seg.type == "insert":
                md_parts.append(f'**{seg.new_text}**')
            elif seg.type == "delete":
                md_parts.append(f'~~{seg.old_text}~~')
            elif seg.type == "replace":
                md_parts.append(f'~~{seg.old_text}~~ **{seg.new_text}**')
        
        return ''.join(md_parts)
    
    def to_unified(self, old_text: str, new_text: str, context: int = 3) -> str:
        """
        生成统一格式的差异
        
        Args:
            old_text: 原始文本
            new_text: 新文本
            context: 上下文行数
            
        Returns:
            str: 统一格式的差异文本
        """
        old_lines = old_text.splitlines(keepends=True)
        new_lines = new_text.splitlines(keepends=True)
        
        diff = unified_diff(
            old_lines,
            new_lines,
            fromfile='原文',
            tofile='修改后',
            lineterm='',
            n=context
        )
        
        return ''.join(diff)
    
    def get_change_summary(self, old_text: str, new_text: str) -> dict:
        """
        获取变更摘要
        
        Args:
            old_text: 原始文本
            new_text: 新文本
            
        Returns:
            dict: 变更摘要
        """
        segments = self.generate(old_text, new_text)
        
        stats = {
            "total_segments": len(segments),
            "equal": 0,
            "insert": 0,
            "delete": 0,
            "replace": 0,
            "chars_added": 0,
            "chars_removed": 0,
            "similarity": 0.0
        }
        
        for seg in segments:
            stats[seg.type] += 1
            if seg.type == "insert":
                stats["chars_added"] += len(seg.new_text)
            elif seg.type == "delete":
                stats["chars_removed"] += len(seg.old_text)
            elif seg.type == "replace":
                stats["chars_added"] += len(seg.new_text)
                stats["chars_removed"] += len(seg.old_text)
        
        # 计算相似度
        matcher = SequenceMatcher(None, old_text, new_text)
        stats["similarity"] = matcher.ratio()
        
        return stats
    
    def _escape_html(self, text: str) -> str:
        """
        转义 HTML 特殊字符
        
        Args:
            text: 原始文本
            
        Returns:
            str: 转义后的文本
        """
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;")
                .replace("\n", "<br>"))
    
    def side_by_side(
        self,
        old_text: str,
        new_text: str,
        width: int = 50
    ) -> Tuple[str, str]:
        """
        生成并排对比视图
        
        Args:
            old_text: 原始文本
            new_text: 新文本
            width: 每列宽度
            
        Returns:
            Tuple[str, str]: (左侧文本, 右侧文本)
        """
        old_lines = old_text.split('\n')
        new_lines = new_text.split('\n')
        
        # 填充使行数相等
        max_lines = max(len(old_lines), len(new_lines))
        old_lines.extend([''] * (max_lines - len(old_lines)))
        new_lines.extend([''] * (max_lines - len(new_lines)))
        
        return '\n'.join(old_lines), '\n'.join(new_lines)
    
    def highlight_changes_html(
        self,
        old_text: str,
        new_text: str
    ) -> Tuple[str, str]:
        """
        生成带高亮的 HTML 对比
        
        Args:
            old_text: 原始文本
            new_text: 新文本
            
        Returns:
            Tuple[str, str]: (原文HTML, 新文HTML)
        """
        segments = self.generate(old_text, new_text)
        
        old_parts = []
        new_parts = []
        
        for seg in segments:
            if seg.type == "equal":
                old_parts.append(self._escape_html(seg.old_text))
                new_parts.append(self._escape_html(seg.new_text))
            elif seg.type == "insert":
                new_parts.append(f'<mark style="background-color: #d4edda;">{self._escape_html(seg.new_text)}</mark>')
            elif seg.type == "delete":
                old_parts.append(f'<mark style="background-color: #f8d7da;">{self._escape_html(seg.old_text)}</mark>')
            elif seg.type == "replace":
                old_parts.append(f'<mark style="background-color: #f8d7da;">{self._escape_html(seg.old_text)}</mark>')
                new_parts.append(f'<mark style="background-color: #d4edda;">{self._escape_html(seg.new_text)}</mark>')
        
        return ''.join(old_parts), ''.join(new_parts)
