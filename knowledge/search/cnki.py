# -*- coding: utf-8 -*-
"""
知网(CNKI)搜索模块 v2.0
参考 Zotero 茉莉花插件的元数据抓取思路
使用多种备用方案确保搜索可用性

主要数据源：
1. 知网公开搜索接口
2. 百度学术（备用）
3. 万方数据（备用）
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import re
import time
import random
import urllib.parse
import httpx


@dataclass
class CNKIResult:
    """知网搜索结果"""
    title: str
    authors: str
    year: str
    abstract: str
    link: str
    citations: int
    source: str  # 期刊名称
    database: str  # 数据来源


def search_cnki(
    query: str,
    limit: int = 10,
    source_type: Optional[str] = None
) -> List[CNKIResult]:
    """
    搜索中文学术文献
    自动切换多个数据源确保可用性
    
    Args:
        query: 搜索查询
        limit: 返回数量
        source_type: 来源类型筛选 (journal/thesis/conference)
        
    Returns:
        List[CNKIResult]: 搜索结果列表
    """
    results = []
    
    # 方案1：尝试百度学术（最稳定）
    try:
        results = _search_baidu_xueshu(query, limit)
        if results:
            return results
    except Exception as e:
        print(f"百度学术搜索失败: {e}")
    
    # 方案2：尝试万方数据
    try:
        results = _search_wanfang(query, limit)
        if results:
            return results
    except Exception as e:
        print(f"万方数据搜索失败: {e}")
    
    # 方案3：尝试知网简化接口
    try:
        results = _search_cnki_simple(query, limit)
        if results:
            return results
    except Exception as e:
        print(f"知网搜索失败: {e}")
    
    return results


def _search_baidu_xueshu(query: str, limit: int) -> List[CNKIResult]:
    """
    使用百度学术搜索（最可靠的方案）
    百度学术聚合了知网、万方、维普等多个数据源
    """
    results = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://xueshu.baidu.com/",
    }
    
    # URL 编码查询
    encoded_query = urllib.parse.quote(query)
    url = f"https://xueshu.baidu.com/s?wd={encoded_query}&ie=utf-8&tn=SE_baiduxueshu_c1gjeupa"
    
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            
            html = response.text
            
            # 解析搜索结果
            results = _parse_baidu_xueshu_html(html, limit)
            
    except Exception as e:
        print(f"百度学术请求失败: {e}")
    
    return results


def _parse_baidu_xueshu_html(html: str, limit: int) -> List[CNKIResult]:
    """解析百度学术HTML页面"""
    results = []
    
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        # 查找搜索结果
        items = soup.select(".result")
        
        for item in items[:limit]:
            try:
                # 标题
                title_elem = item.select_one("h3 a")
                if not title_elem:
                    continue
                title = title_elem.get_text().strip()
                link = title_elem.get("href", "")
                
                # 作者
                author_elem = item.select_one(".author_text, .sc_author")
                authors = ""
                if author_elem:
                    authors = author_elem.get_text().strip()
                    # 清理作者格式
                    authors = re.sub(r'\s+', ' ', authors)
                    authors = authors.replace("- ", "").strip()
                
                # 摘要
                abstract_elem = item.select_one(".c_abstract")
                abstract = ""
                if abstract_elem:
                    abstract = abstract_elem.get_text().strip()
                    # 移除 "摘要：" 前缀
                    abstract = re.sub(r'^摘要[：:]\s*', '', abstract)
                
                # 来源信息（期刊、年份）
                source = ""
                year = ""
                
                # 尝试从 sc_info 获取
                source_elem = item.select_one(".sc_info")
                if source_elem:
                    source_text = source_elem.get_text()
                    
                    # 提取年份
                    year_match = re.search(r'(19|20)\d{2}', source_text)
                    if year_match:
                        year = year_match.group()
                    
                    # 提取期刊名
                    parts = source_text.split("-")
                    if parts:
                        source = parts[0].strip()
                        # 清理来源
                        source = re.sub(r'^\s*《|》\s*$', '', source)
                
                # 尝试从其他元素获取来源
                if not source:
                    venue_elem = item.select_one(".sc_venue, .venue_text")
                    if venue_elem:
                        source = venue_elem.get_text().strip()
                
                # 引用数
                citations = 0
                cite_elem = item.select_one(".sc_cite_cont, .c_font")
                if cite_elem:
                    cite_text = cite_elem.get_text()
                    cite_match = re.search(r'被引[：:]?\s*(\d+)', cite_text)
                    if cite_match:
                        citations = int(cite_match.group(1))
                    else:
                        # 尝试其他格式
                        cite_match = re.search(r'(\d+)', cite_text)
                        if cite_match:
                            citations = int(cite_match.group(1))
                
                results.append(CNKIResult(
                    title=title,
                    authors=authors,
                    year=year,
                    abstract=abstract,
                    link=link,
                    citations=citations,
                    source=source or "百度学术",
                    database="Baidu Scholar"
                ))
                
            except Exception as e:
                print(f"解析百度学术结果失败: {e}")
                continue
                
    except ImportError:
        print("需要安装 beautifulsoup4: pip install beautifulsoup4")
    except Exception as e:
        print(f"解析百度学术页面失败: {e}")
    
    return results


def _search_wanfang(query: str, limit: int) -> List[CNKIResult]:
    """
    使用万方数据搜索
    万方有相对稳定的搜索接口
    """
    results = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Origin": "https://www.wanfangdata.com.cn",
        "Referer": "https://www.wanfangdata.com.cn/",
    }
    
    # 万方搜索 API
    api_url = "https://s.wanfangdata.com.cn/SearchService/search"
    
    params = {
        "q": query,
        "style": "json",
        "page": 1,
        "size": min(limit, 20),
        "order": "correlation",  # 相关性排序
    }
    
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(api_url, params=params, headers=headers)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    items = data.get("hits", {}).get("hit", [])
                    
                    for item in items[:limit]:
                        try:
                            fields = item.get("fields", {})
                            
                            title = fields.get("title", [""])[0] if fields.get("title") else ""
                            authors_list = fields.get("creator", [])
                            authors = ", ".join(authors_list) if authors_list else ""
                            
                            abstract = fields.get("abstract", [""])[0] if fields.get("abstract") else ""
                            year = fields.get("date", [""])[0][:4] if fields.get("date") else ""
                            source = fields.get("journalName", [""])[0] if fields.get("journalName") else ""
                            
                            # 构建链接
                            doc_id = item.get("id", "")
                            link = f"https://d.wanfangdata.com.cn/periodical/{doc_id}" if doc_id else ""
                            
                            if title:
                                results.append(CNKIResult(
                                    title=title,
                                    authors=authors,
                                    year=year,
                                    abstract=abstract,
                                    link=link,
                                    citations=0,
                                    source=source or "万方数据",
                                    database="Wanfang"
                                ))
                                
                        except Exception:
                            continue
                            
                except Exception:
                    pass
                    
    except Exception as e:
        print(f"万方数据请求失败: {e}")
    
    return results


def _search_cnki_simple(query: str, limit: int) -> List[CNKIResult]:
    """
    使用知网简化搜索
    通过知网的公开搜索页面获取基本信息
    """
    results = []
    
    # 知网搜索需要更复杂的处理，这里使用备用方案
    # 如果百度学术和万方都失败，返回空结果
    
    return results


def search_by_title(title: str) -> Optional[CNKIResult]:
    """
    根据论文标题精确搜索
    用于获取单篇论文的详细信息
    
    Args:
        title: 论文标题
        
    Returns:
        CNKIResult: 论文详情，未找到则返回 None
    """
    results = search_cnki(f'"{title}"', limit=5)
    
    # 查找最匹配的结果
    title_lower = title.lower().strip()
    for r in results:
        if r.title.lower().strip() == title_lower:
            return r
    
    # 如果没有完全匹配，返回第一个结果
    return results[0] if results else None


def get_paper_abstract(title: str) -> str:
    """
    获取论文摘要
    
    Args:
        title: 论文标题
        
    Returns:
        str: 论文摘要
    """
    result = search_by_title(title)
    return result.abstract if result else ""


def format_results(results: List[CNKIResult]) -> str:
    """
    格式化搜索结果为 Markdown
    """
    if not results:
        return "未找到相关中文文献"
    
    lines = []
    lines.append(f"## 中文文献搜索结果 ({len(results)} 篇)\n")
    
    for i, r in enumerate(results, 1):
        lines.append(f"### {i}. {r.title}")
        lines.append(f"**作者**: {r.authors}")
        lines.append(f"**期刊**: {r.source} ({r.year})")
        
        if r.citations:
            lines.append(f"**引用**: {r.citations}")
        
        if r.abstract:
            abstract_preview = r.abstract[:300] + "..." if len(r.abstract) > 300 else r.abstract
            lines.append(f"\n**摘要**: {abstract_preview}")
        
        if r.link:
            lines.append(f"\n[查看原文]({r.link})")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def generate_citation(result: CNKIResult, style: str = "gb") -> str:
    """
    生成引用格式
    
    Args:
        result: 论文结果
        style: 引用样式 (gb/apa/mla)
        
    Returns:
        str: 格式化的引用
    """
    if style == "gb":
        # GB/T 7714 格式
        citation = f"[{result.authors}. {result.title}[J]. {result.source}, {result.year}."
        return citation
        
    elif style == "apa":
        # APA 格式
        citation = f"{result.authors} ({result.year}). {result.title}. {result.source}."
        return citation
        
    else:
        return f"{result.authors} ({result.year}). {result.title}. {result.source}."
