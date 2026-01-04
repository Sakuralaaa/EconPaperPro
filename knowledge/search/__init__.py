# -*- coding: utf-8 -*-
"""学术搜索模块 - Google Scholar、知网搜索"""
from .google_scholar import search_google_scholar
from .cnki import search_cnki

__all__ = [
    "search_google_scholar",
    "search_cnki",
]
