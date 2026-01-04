# -*- coding: utf-8 -*-
"""
Google Scholar 搜索模块
通过 SerpAPI 或 scholarly 库搜索学术文献
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from config.settings import settings


@dataclass
class ScholarResult:
    """学术搜索结果"""
    title: str
    authors: str
    year: str
    abstract: str
    link: str
    citations: int
    source: str


def search_google_scholar(
    query: str,
    limit: int = 10,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None
) -> List[ScholarResult]:
    """
    搜索 Google Scholar
    
    优先使用 SerpAPI（如果配置了密钥），备用方案使用 scholarly 库
    
    Args:
        query: 搜索查询
        limit: 返回数量
        year_from: 起始年份
        year_to: 结束年份
        
    Returns:
        List[ScholarResult]: 搜索结果列表
    """
    # 优先尝试 SerpAPI
    if settings.serpapi_key:
        try:
            return _search_via_serpapi(query, limit, year_from, year_to)
        except Exception:
            pass
    
    # 备用方案：scholarly
    try:
        return _search_via_scholarly(query, limit)
    except Exception:
        pass
    
    # 如果都失败，返回空列表
    return []


def _search_via_serpapi(
    query: str,
    limit: int,
    year_from: Optional[int],
    year_to: Optional[int]
) -> List[ScholarResult]:
    """
    通过 SerpAPI 搜索
    
    Args:
        query: 搜索查询
        limit: 返回数量
        year_from: 起始年份
        year_to: 结束年份
        
    Returns:
        List[ScholarResult]: 搜索结果
    """
    import httpx
    
    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": settings.serpapi_key,
        "num": min(limit, 20)
    }
    
    if year_from:
        params["as_ylo"] = year_from
    if year_to:
        params["as_yhi"] = year_to
    
    response = httpx.get("https://serpapi.com/search", params=params, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    
    results = []
    for item in data.get("organic_results", []):
        # Safely extract authors
        pub_info = item.get("publication_info", {})
        authors_list = pub_info.get("authors", [])
        authors = authors_list[0].get("name", "") if authors_list else ""
        
        result = ScholarResult(
            title=item.get("title", ""),
            authors=authors,
            year=str(pub_info.get("year", "")),
            abstract=item.get("snippet", ""),
            link=item.get("link", ""),
            citations=item.get("inline_links", {}).get("cited_by", {}).get("total", 0),
            source="Google Scholar (SerpAPI)"
        )
        results.append(result)
    
    return results[:limit]


def _search_via_scholarly(
    query: str,
    limit: int
) -> List[ScholarResult]:
    """
    通过 scholarly 库搜索
    
    Args:
        query: 搜索查询
        limit: 返回数量
        
    Returns:
        List[ScholarResult]: 搜索结果
    """
    try:
        from scholarly import scholarly
        
        search_query = scholarly.search_pubs(query)
        
        results = []
        for i, pub in enumerate(search_query):
            if i >= limit:
                break
            
            bib = pub.get("bib", {})
            
            result = ScholarResult(
                title=bib.get("title", ""),
                authors=", ".join(bib.get("author", [])) if isinstance(bib.get("author"), list) else bib.get("author", ""),
                year=str(bib.get("pub_year", "")),
                abstract=bib.get("abstract", ""),
                link=pub.get("pub_url", ""),
                citations=pub.get("num_citations", 0),
                source="Google Scholar (scholarly)"
            )
            results.append(result)
        
        return results
        
    except ImportError:
        raise Exception("scholarly 库未安装")


def format_results(results: List[ScholarResult]) -> str:
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
    lines.append(f"## 搜索结果 ({len(results)} 篇)\n")
    
    for i, r in enumerate(results, 1):
        lines.append(f"### {i}. {r.title}")
        lines.append(f"**作者**: {r.authors}")
        lines.append(f"**年份**: {r.year} | **引用**: {r.citations}")
        
        if r.abstract:
            abstract_preview = r.abstract[:200] + "..." if len(r.abstract) > 200 else r.abstract
            lines.append(f"\n{abstract_preview}")
        
        if r.link:
            lines.append(f"\n[查看原文]({r.link})")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)
