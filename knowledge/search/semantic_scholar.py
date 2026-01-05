# -*- coding: utf-8 -*-
"""
Semantic Scholar API 搜索模块
免费API，无需认证，提供论文标题、摘要、作者等信息
官方API文档：https://api.semanticscholar.org/
"""

from typing import List, Optional
from dataclasses import dataclass
import httpx
import time


@dataclass
class SemanticScholarResult:
    """Semantic Scholar 搜索结果"""
    title: str
    authors: str
    year: str
    abstract: str
    link: str
    citations: int
    venue: str  # 期刊/会议名称
    paper_id: str
    doi: str


def search_semantic_scholar(
    query: str,
    limit: int = 10,
    year_from: Optional[int] = None,
    fields_of_study: Optional[List[str]] = None
) -> List[SemanticScholarResult]:
    """
    使用 Semantic Scholar API 搜索学术论文
    
    Args:
        query: 搜索查询
        limit: 返回数量 (最大100)
        year_from: 起始年份
        fields_of_study: 研究领域筛选，如 ["Economics", "Business"]
        
    Returns:
        List[SemanticScholarResult]: 搜索结果列表
    """
    results = []
    
    # Semantic Scholar API 端点
    api_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    # 请求参数
    params = {
        "query": query,
        "limit": min(limit, 100),  # API限制最大100
        "fields": "title,authors,year,abstract,url,citationCount,venue,externalIds,paperId"
    }
    
    # 年份筛选
    if year_from:
        params["year"] = f"{year_from}-"
    
    # 领域筛选
    if fields_of_study:
        params["fieldsOfStudy"] = ",".join(fields_of_study)
    
    headers = {
        "User-Agent": "EconPaper-Pro/1.0 (Academic Research Tool)"
    }
    
    try:
        response = httpx.get(
            api_url, 
            params=params, 
            headers=headers, 
            timeout=30,
            follow_redirects=True
        )
        response.raise_for_status()
        
        data = response.json()
        papers = data.get("data", [])
        
        for paper in papers:
            try:
                # 提取作者
                authors_list = paper.get("authors", [])
                authors = ", ".join([a.get("name", "") for a in authors_list[:5]])
                if len(authors_list) > 5:
                    authors += " 等"
                
                # 提取 DOI
                external_ids = paper.get("externalIds", {}) or {}
                doi = external_ids.get("DOI", "")
                
                # 构建链接
                paper_id = paper.get("paperId", "")
                link = paper.get("url", "")
                if not link and paper_id:
                    link = f"https://www.semanticscholar.org/paper/{paper_id}"
                
                results.append(SemanticScholarResult(
                    title=paper.get("title", "无标题"),
                    authors=authors,
                    year=str(paper.get("year", "")) if paper.get("year") else "",
                    abstract=paper.get("abstract", "") or "",
                    link=link,
                    citations=paper.get("citationCount", 0) or 0,
                    venue=paper.get("venue", "") or "",
                    paper_id=paper_id,
                    doi=doi
                ))
                
            except Exception as e:
                print(f"解析论文数据失败: {e}")
                continue
                
    except httpx.TimeoutException:
        print("Semantic Scholar API 请求超时")
    except httpx.HTTPStatusError as e:
        print(f"Semantic Scholar API 错误: {e.response.status_code}")
    except Exception as e:
        print(f"Semantic Scholar 搜索失败: {e}")
    
    return results


def search_semantic_scholar_bulk(
    queries: List[str],
    limit_per_query: int = 5
) -> List[SemanticScholarResult]:
    """
    批量搜索多个关键词
    
    Args:
        queries: 关键词列表
        limit_per_query: 每个关键词返回的结果数
        
    Returns:
        List[SemanticScholarResult]: 合并后的结果（去重）
    """
    all_results = []
    seen_ids = set()
    
    for query in queries:
        results = search_semantic_scholar(query, limit=limit_per_query)
        
        for r in results:
            if r.paper_id not in seen_ids:
                seen_ids.add(r.paper_id)
                all_results.append(r)
        
        # 避免请求过快
        time.sleep(0.5)
    
    return all_results


def get_paper_details(paper_id: str) -> Optional[SemanticScholarResult]:
    """
    获取单篇论文的详细信息
    
    Args:
        paper_id: Semantic Scholar 论文ID
        
    Returns:
        SemanticScholarResult: 论文详情
    """
    api_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
    
    params = {
        "fields": "title,authors,year,abstract,url,citationCount,venue,externalIds,references.title,references.authors"
    }
    
    headers = {
        "User-Agent": "EconPaper-Pro/1.0 (Academic Research Tool)"
    }
    
    try:
        response = httpx.get(
            api_url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        paper = response.json()
        
        # 提取作者
        authors_list = paper.get("authors", [])
        authors = ", ".join([a.get("name", "") for a in authors_list[:5]])
        if len(authors_list) > 5:
            authors += " 等"
        
        # 提取 DOI
        external_ids = paper.get("externalIds", {}) or {}
        doi = external_ids.get("DOI", "")
        
        link = paper.get("url", "")
        if not link:
            link = f"https://www.semanticscholar.org/paper/{paper_id}"
        
        return SemanticScholarResult(
            title=paper.get("title", "无标题"),
            authors=authors,
            year=str(paper.get("year", "")) if paper.get("year") else "",
            abstract=paper.get("abstract", "") or "",
            link=link,
            citations=paper.get("citationCount", 0) or 0,
            venue=paper.get("venue", "") or "",
            paper_id=paper_id,
            doi=doi
        )
        
    except Exception as e:
        print(f"获取论文详情失败: {e}")
        return None


def format_results(results: List[SemanticScholarResult]) -> str:
    """
    格式化搜索结果为 Markdown
    """
    if not results:
        return "未找到相关文献"
    
    lines = []
    lines.append(f"## Semantic Scholar 搜索结果 ({len(results)} 篇)\n")
    
    for i, r in enumerate(results, 1):
        lines.append(f"### {i}. {r.title}")
        lines.append(f"**作者**: {r.authors}")
        lines.append(f"**年份**: {r.year} | **引用**: {r.citations}")
        
        if r.venue:
            lines.append(f"**期刊/会议**: {r.venue}")
        
        if r.abstract:
            abstract_preview = r.abstract[:300] + "..." if len(r.abstract) > 300 else r.abstract
            lines.append(f"\n**摘要**: {abstract_preview}")
        
        if r.doi:
            lines.append(f"\n**DOI**: {r.doi}")
        
        if r.link:
            lines.append(f"\n[查看原文]({r.link})")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)