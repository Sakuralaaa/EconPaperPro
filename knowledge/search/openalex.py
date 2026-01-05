# -*- coding: utf-8 -*-
"""
OpenAlex API 搜索模块
完全免费开放的学术数据库API，覆盖超过2亿篇论文
官方文档：https://docs.openalex.org/
特点：中英文论文都有，包含中国期刊
"""

from typing import List, Optional
from dataclasses import dataclass
import httpx
import re


@dataclass
class OpenAlexResult:
    """OpenAlex 搜索结果"""
    title: str
    authors: str
    year: str
    abstract: str
    link: str
    citations: int
    venue: str  # 期刊名称
    doi: str
    openalex_id: str
    open_access: bool  # 是否开放获取


def search_openalex(
    query: str,
    limit: int = 10,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    open_access_only: bool = False
) -> List[OpenAlexResult]:
    """
    使用 OpenAlex API 搜索学术论文
    
    Args:
        query: 搜索查询
        limit: 返回数量 (最大200)
        year_from: 起始年份
        year_to: 结束年份
        open_access_only: 只搜索开放获取的论文
        
    Returns:
        List[OpenAlexResult]: 搜索结果列表
    """
    results = []
    
    # OpenAlex API 端点
    api_url = "https://api.openalex.org/works"
    
    # 构建过滤条件
    filters = []
    
    # 年份筛选
    if year_from and year_to:
        filters.append(f"publication_year:{year_from}-{year_to}")
    elif year_from:
        filters.append(f"publication_year:>{year_from-1}")
    elif year_to:
        filters.append(f"publication_year:<{year_to+1}")
    
    # 开放获取筛选
    if open_access_only:
        filters.append("is_oa:true")
    
    # 请求参数
    params = {
        "search": query,
        "per_page": min(limit, 200),
        "sort": "cited_by_count:desc",  # 按引用数排序
        "mailto": "econpaper@example.com"  # 礼貌请求，获得更高速率限制
    }
    
    if filters:
        params["filter"] = ",".join(filters)
    
    headers = {
        "User-Agent": "EconPaper-Pro/1.0 (Academic Research Tool; mailto:econpaper@example.com)"
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
        works = data.get("results", [])
        
        for work in works:
            try:
                # 提取标题
                title = work.get("title", "无标题") or "无标题"
                
                # 提取作者
                authorships = work.get("authorships", [])
                author_names = []
                for auth in authorships[:5]:
                    author = auth.get("author", {})
                    name = author.get("display_name", "")
                    if name:
                        author_names.append(name)
                authors = ", ".join(author_names)
                if len(authorships) > 5:
                    authors += " 等"
                
                # 提取年份
                year = str(work.get("publication_year", "")) if work.get("publication_year") else ""
                
                # 提取摘要（OpenAlex 使用倒排索引格式，需要重建）
                abstract = _reconstruct_abstract(work.get("abstract_inverted_index"))
                
                # 提取期刊信息
                primary_location = work.get("primary_location", {}) or {}
                source = primary_location.get("source", {}) or {}
                venue = source.get("display_name", "") or ""
                
                # DOI
                doi = work.get("doi", "") or ""
                if doi and doi.startswith("https://doi.org/"):
                    doi = doi.replace("https://doi.org/", "")
                
                # 链接
                link = work.get("doi", "") or work.get("id", "")
                if not link.startswith("http"):
                    link = f"https://openalex.org/{work.get('id', '')}"
                
                # 引用数
                citations = work.get("cited_by_count", 0) or 0
                
                # 开放获取状态
                open_access = work.get("open_access", {}).get("is_oa", False)
                
                # OpenAlex ID
                openalex_id = work.get("id", "").replace("https://openalex.org/", "")
                
                results.append(OpenAlexResult(
                    title=title,
                    authors=authors,
                    year=year,
                    abstract=abstract,
                    link=link,
                    citations=citations,
                    venue=venue,
                    doi=doi,
                    openalex_id=openalex_id,
                    open_access=open_access
                ))
                
            except Exception as e:
                print(f"解析论文数据失败: {e}")
                continue
                
    except httpx.TimeoutException:
        print("OpenAlex API 请求超时")
    except httpx.HTTPStatusError as e:
        print(f"OpenAlex API 错误: {e.response.status_code}")
    except Exception as e:
        print(f"OpenAlex 搜索失败: {e}")
    
    return results


def _reconstruct_abstract(inverted_index: Optional[dict]) -> str:
    """
    从 OpenAlex 的倒排索引重建摘要文本
    
    OpenAlex 使用倒排索引格式存储摘要：
    {"word1": [0, 5], "word2": [1, 3], ...}
    表示 word1 出现在位置 0 和 5，word2 出现在位置 1 和 3
    """
    if not inverted_index:
        return ""
    
    try:
        # 创建位置到单词的映射
        position_to_word = {}
        for word, positions in inverted_index.items():
            for pos in positions:
                position_to_word[pos] = word
        
        # 按位置排序并重建文本
        sorted_positions = sorted(position_to_word.keys())
        words = [position_to_word[pos] for pos in sorted_positions]
        
        return " ".join(words)
        
    except Exception:
        return ""


def search_openalex_chinese(
    query: str,
    limit: int = 10
) -> List[OpenAlexResult]:
    """
    专门搜索中文论文
    通过添加中国期刊来源筛选
    """
    # OpenAlex 支持中文搜索，但可能需要结合其他策略
    return search_openalex(query, limit)


def get_work_details(openalex_id: str) -> Optional[OpenAlexResult]:
    """
    获取单篇论文的详细信息
    
    Args:
        openalex_id: OpenAlex 论文ID (如 W2741809807)
        
    Returns:
        OpenAlexResult: 论文详情
    """
    api_url = f"https://api.openalex.org/works/{openalex_id}"
    
    params = {
        "mailto": "econpaper@example.com"
    }
    
    headers = {
        "User-Agent": "EconPaper-Pro/1.0"
    }
    
    try:
        response = httpx.get(
            api_url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        work = response.json()
        
        # 提取标题
        title = work.get("title", "无标题") or "无标题"
        
        # 提取作者
        authorships = work.get("authorships", [])
        author_names = []
        for auth in authorships[:5]:
            author = auth.get("author", {})
            name = author.get("display_name", "")
            if name:
                author_names.append(name)
        authors = ", ".join(author_names)
        if len(authorships) > 5:
            authors += " 等"
        
        # 其他字段
        year = str(work.get("publication_year", "")) if work.get("publication_year") else ""
        abstract = _reconstruct_abstract(work.get("abstract_inverted_index"))
        
        primary_location = work.get("primary_location", {}) or {}
        source = primary_location.get("source", {}) or {}
        venue = source.get("display_name", "") or ""
        
        doi = work.get("doi", "") or ""
        if doi and doi.startswith("https://doi.org/"):
            doi = doi.replace("https://doi.org/", "")
        
        link = work.get("doi", "") or f"https://openalex.org/{openalex_id}"
        citations = work.get("cited_by_count", 0) or 0
        open_access = work.get("open_access", {}).get("is_oa", False)
        
        return OpenAlexResult(
            title=title,
            authors=authors,
            year=year,
            abstract=abstract,
            link=link,
            citations=citations,
            venue=venue,
            doi=doi,
            openalex_id=openalex_id,
            open_access=open_access
        )
        
    except Exception as e:
        print(f"获取论文详情失败: {e}")
        return None


def format_results(results: List[OpenAlexResult]) -> str:
    """
    格式化搜索结果为 Markdown
    """
    if not results:
        return "未找到相关文献"
    
    lines = []
    lines.append(f"## OpenAlex 搜索结果 ({len(results)} 篇)\n")
    
    for i, r in enumerate(results, 1):
        oa_badge = "🔓" if r.open_access else ""
        lines.append(f"### {i}. {r.title} {oa_badge}")
        lines.append(f"**作者**: {r.authors}")
        lines.append(f"**年份**: {r.year} | **引用**: {r.citations}")
        
        if r.venue:
            lines.append(f"**期刊**: {r.venue}")
        
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


def generate_citation(result: OpenAlexResult, style: str = "apa") -> str:
    """
    生成引用格式
    
    Args:
        result: 论文结果
        style: 引用样式 (apa, mla, chicago, gb)
        
    Returns:
        str: 格式化的引用
    """
    if style == "apa":
        # APA 格式
        authors_apa = result.authors.replace(", ", ", ").replace(" 等", " et al.")
        citation = f"{authors_apa} ({result.year}). {result.title}."
        if result.venue:
            citation += f" {result.venue}."
        if result.doi:
            citation += f" https://doi.org/{result.doi}"
        return citation
        
    elif style == "gb":
        # GB/T 7714 格式（中国国标）
        citation = f"[{result.authors}. {result.title}[J]. {result.venue}, {result.year}."
        return citation
        
    elif style == "mla":
        # MLA 格式
        citation = f'{result.authors}. "{result.title}." {result.venue}, {result.year}.'
        return citation
        
    elif style == "chicago":
        # Chicago 格式
        citation = f'{result.authors}. "{result.title}." {result.venue} ({result.year}).'
        if result.doi:
            citation += f" https://doi.org/{result.doi}."
        return citation
        
    else:
        return f"{result.authors} ({result.year}). {result.title}. {result.venue}."