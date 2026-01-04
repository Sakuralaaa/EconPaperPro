# -*- coding: utf-8 -*-
"""
知网(CNKI)搜索模块
搜索中国知网文献

注意：由于知网反爬严格，本模块提供模拟数据作为演示
后续可根据需要扩展真实爬虫功能
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class CNKIResult:
    """知网搜索结果"""
    title: str
    authors: str
    year: str
    abstract: str
    link: str
    citations: int
    source: str  # 期刊/学位论文等
    database: str  # CNKI


def search_cnki(
    query: str,
    limit: int = 10,
    source_type: Optional[str] = None
) -> List[CNKIResult]:
    """
    搜索知网文献
    
    由于知网反爬严格，当前返回模拟数据
    
    Args:
        query: 搜索查询
        limit: 返回数量
        source_type: 来源类型筛选 (journal/thesis/conference)
        
    Returns:
        List[CNKIResult]: 搜索结果列表
    """
    # 返回模拟数据
    return _get_mock_results(query, limit, source_type)


def _get_mock_results(
    query: str,
    limit: int,
    source_type: Optional[str]
) -> List[CNKIResult]:
    """
    获取模拟搜索结果
    
    Args:
        query: 搜索查询
        limit: 返回数量
        source_type: 来源类型
        
    Returns:
        List[CNKIResult]: 模拟结果
    """
    mock_data = [
        CNKIResult(
            title=f"数字经济发展与企业创新效率研究——基于{query}视角的分析",
            authors="张三, 李四",
            year="2023",
            abstract=f"本文基于2010-2022年中国A股上市公司数据，采用双重差分方法研究了{query}对企业创新效率的影响。研究发现...",
            link="https://www.cnki.net/",
            citations=156,
            source="经济研究",
            database="CNKI"
        ),
        CNKIResult(
            title=f"环境规制、绿色创新与高质量发展——{query}的经验证据",
            authors="王五, 赵六",
            year="2023",
            abstract=f"本文利用省级面板数据，构建了{query}相关的理论分析框架，并运用工具变量方法进行了实证检验...",
            link="https://www.cnki.net/",
            citations=89,
            source="管理世界",
            database="CNKI"
        ),
        CNKIResult(
            title=f"金融科技赋能实体经济：机制、路径与效果——基于{query}的研究",
            authors="陈七, 周八",
            year="2022",
            abstract=f"金融科技的快速发展为实体经济转型升级提供了新动能。本文从{query}角度出发，分析了...",
            link="https://www.cnki.net/",
            citations=234,
            source="金融研究",
            database="CNKI"
        ),
        CNKIResult(
            title=f"公司治理、信息披露与资本市场效率——来自{query}的证据",
            authors="吴九, 郑十",
            year="2022",
            abstract=f"本文以2015-2021年沪深两市A股上市公司为样本，研究了{query}背景下公司治理对资本市场效率的影响...",
            link="https://www.cnki.net/",
            citations=78,
            source="会计研究",
            database="CNKI"
        ),
        CNKIResult(
            title=f"产业政策与企业全要素生产率：{query}的准自然实验",
            authors="钱一, 孙二",
            year="2023",
            abstract=f"本文将{query}作为准自然实验，运用双重差分模型识别了产业政策对企业全要素生产率的因果效应...",
            link="https://www.cnki.net/",
            citations=167,
            source="中国工业经济",
            database="CNKI"
        ),
    ]
    
    # 根据来源类型筛选
    if source_type == "journal":
        results = [r for r in mock_data if "研究" in r.source or "世界" in r.source]
    elif source_type == "thesis":
        results = []  # 模拟数据中没有学位论文
    else:
        results = mock_data
    
    return results[:limit]


def format_results(results: List[CNKIResult]) -> str:
    """
    格式化搜索结果为 Markdown
    
    Args:
        results: 搜索结果列表
        
    Returns:
        str: Markdown 格式的文本
    """
    if not results:
        return "未找到相关文献"
    
    lines = []
    lines.append(f"## 知网搜索结果 ({len(results)} 篇)\n")
    lines.append("> 注意：当前显示的是模拟数据，实际使用需配置知网访问权限\n")
    
    for i, r in enumerate(results, 1):
        lines.append(f"### {i}. {r.title}")
        lines.append(f"**作者**: {r.authors}")
        lines.append(f"**期刊**: {r.source} ({r.year}) | **引用**: {r.citations}")
        
        if r.abstract:
            abstract_preview = r.abstract[:200] + "..." if len(r.abstract) > 200 else r.abstract
            lines.append(f"\n{abstract_preview}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def get_article_detail(article_id: str) -> Optional[Dict]:
    """
    获取文章详情（预留接口）
    
    Args:
        article_id: 文章ID
        
    Returns:
        Optional[Dict]: 文章详情
    """
    # 预留接口，待后续实现
    return None
