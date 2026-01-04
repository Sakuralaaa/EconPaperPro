# -*- coding: utf-8 -*-
"""
PDF解析模块
使用 PyMuPDF 解析 PDF 文件，提取文本内容
"""

from typing import Optional, Dict, List
import fitz  # PyMuPDF


class PDFParser:
    """
    PDF 文档解析器
    
    使用示例:
        parser = PDFParser()
        text = parser.parse("paper.pdf")
    """
    
    def parse(self, file_path: str) -> str:
        """
        解析 PDF 文件，提取全部文本
        
        Args:
            file_path: PDF 文件路径
            
        Returns:
            str: 提取的文本内容
        """
        try:
            doc = fitz.open(file_path)
            text_parts = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_parts.append(page.get_text())
            
            doc.close()
            return "\n".join(text_parts)
            
        except Exception as e:
            raise RuntimeError(f"PDF 解析失败: {str(e)}")
    
    def parse_by_page(self, file_path: str) -> List[str]:
        """
        按页解析 PDF 文件
        
        Args:
            file_path: PDF 文件路径
            
        Returns:
            List[str]: 每页的文本内容列表
        """
        try:
            doc = fitz.open(file_path)
            pages = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pages.append(page.get_text())
            
            doc.close()
            return pages
            
        except Exception as e:
            raise RuntimeError(f"PDF 分页解析失败: {str(e)}")
    
    def parse_with_metadata(self, file_path: str) -> Dict:
        """
        解析 PDF 文件并提取元数据
        
        Args:
            file_path: PDF 文件路径
            
        Returns:
            Dict: 包含文本和元数据的字典
        """
        try:
            doc = fitz.open(file_path)
            
            # 提取元数据
            metadata = doc.metadata
            
            # 提取文本
            text_parts = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_parts.append(page.get_text())
            
            page_count = len(doc)
            doc.close()
            
            return {
                "text": "\n".join(text_parts),
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "keywords": metadata.get("keywords", ""),
                "page_count": page_count
            }
            
        except Exception as e:
            raise RuntimeError(f"PDF 元数据解析失败: {str(e)}")
    
    def parse_bytes(self, file_bytes: bytes) -> str:
        """
        从字节流解析 PDF
        
        Args:
            file_bytes: PDF 文件字节流
            
        Returns:
            str: 提取的文本内容
        """
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_parts = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_parts.append(page.get_text())
            
            doc.close()
            return "\n".join(text_parts)
            
        except Exception as e:
            raise RuntimeError(f"PDF 字节流解析失败: {str(e)}")
