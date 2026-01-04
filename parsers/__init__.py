# -*- coding: utf-8 -*-
"""文档解析模块 - PDF、Word解析及论文结构识别"""
from .pdf_parser import PDFParser
from .docx_parser import DocxParser
from .structure import StructureRecognizer

__all__ = [
    "PDFParser",
    "DocxParser",
    "StructureRecognizer",
]
