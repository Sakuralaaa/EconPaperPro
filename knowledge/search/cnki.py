# -*- coding: utf-8 -*-
"""
知网(CNKI)搜索模块
使用无头浏览器进行真实网页抓取
"""

from typing import List, Optional
from dataclasses import dataclass
import re
import time
import random


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
    database: str  # CNKI


def search_cnki(
    query: str,
    limit: int = 10,
    source_type: Optional[str] = None
) -> List[CNKIResult]:
    """
    搜索知网文献
    使用无头浏览器进行真实网页抓取
    
    Args:
        query: 搜索查询
        limit: 返回数量
        source_type: 来源类型筛选 (journal/thesis/conference)
        
    Returns:
        List[CNKIResult]: 搜索结果列表
    """
    # 优先尝试 Playwright
    try:
        return _search_via_playwright(query, limit, source_type)
    except Exception as e:
        print(f"CNKI Playwright 搜索失败: {e}")
    
    # 备用方案：Selenium
    try:
        return _search_via_selenium(query, limit, source_type)
    except Exception as e:
        print(f"CNKI Selenium 搜索失败: {e}")
    
    # 备用：使用百度学术
    try:
        return _search_via_baidu_xueshu(query, limit)
    except Exception as e:
        print(f"百度学术搜索失败: {e}")
    
    return []


def _search_via_playwright(
    query: str,
    limit: int,
    source_type: Optional[str]
) -> List[CNKIResult]:
    """
    使用 Playwright 无头浏览器搜索知网
    """
    from playwright.sync_api import sync_playwright
    
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            # 访问知网学术搜索
            url = f"https://kns.cnki.net/kns8s/search?q={query}"
            page.goto(url, timeout=30000)
            
            # 等待搜索结果加载
            page.wait_for_selector(".result-table-list", timeout=15000)
            time.sleep(random.uniform(2, 3))
            
            # 解析搜索结果
            items = page.query_selector_all(".result-table-list tbody tr")
            
            for item in items[:limit]:
                try:
                    # 标题
                    title_elem = item.query_selector("td.name a.fz14")
                    if title_elem:
                        title = title_elem.inner_text().strip()
                        link = title_elem.get_attribute("href") or ""
                        if link and not link.startswith("http"):
                            link = "https://kns.cnki.net" + link
                    else:
                        continue
                    
                    # 作者
                    author_elem = item.query_selector("td.author")
                    authors = author_elem.inner_text().strip() if author_elem else ""
                    
                    # 期刊来源
                    source_elem = item.query_selector("td.source a")
                    source = source_elem.inner_text().strip() if source_elem else ""
                    
                    # 发表时间
                    date_elem = item.query_selector("td.date")
                    date_text = date_elem.inner_text().strip() if date_elem else ""
                    year = date_text[:4] if date_text else ""
                    
                    # 引用数（需要点击或另外获取）
                    cite_elem = item.query_selector("td.quote")
                    citations = 0
                    if cite_elem:
                        cite_text = cite_elem.inner_text().strip()
                        if cite_text.isdigit():
                            citations = int(cite_text)
                    
                    results.append(CNKIResult(
                        title=title,
                        authors=authors,
                        year=year,
                        abstract="",  # 需要点击进入详情页获取
                        link=link,
                        citations=citations,
                        source=source,
                        database="CNKI"
                    ))
                    
                except Exception:
                    continue
                    
        finally:
            browser.close()
    
    return results


def _search_via_selenium(
    query: str,
    limit: int,
    source_type: Optional[str]
) -> List[CNKIResult]:
    """
    使用 Selenium 无头浏览器搜索知网
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    results = []
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        url = f"https://kns.cnki.net/kns8s/search?q={query}"
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".result-table-list")))
        time.sleep(random.uniform(2, 3))
        
        items = driver.find_elements(By.CSS_SELECTOR, ".result-table-list tbody tr")
        
        for item in items[:limit]:
            try:
                title_elem = item.find_element(By.CSS_SELECTOR, "td.name a.fz14")
                title = title_elem.text.strip()
                link = title_elem.get_attribute("href") or ""
                
                try:
                    author_elem = item.find_element(By.CSS_SELECTOR, "td.author")
                    authors = author_elem.text.strip()
                except Exception:
                    authors = ""
                
                try:
                    source_elem = item.find_element(By.CSS_SELECTOR, "td.source a")
                    source = source_elem.text.strip()
                except Exception:
                    source = ""
                
                try:
                    date_elem = item.find_element(By.CSS_SELECTOR, "td.date")
                    date_text = date_elem.text.strip()
                    year = date_text[:4] if date_text else ""
                except Exception:
                    year = ""
                
                citations = 0
                try:
                    cite_elem = item.find_element(By.CSS_SELECTOR, "td.quote")
                    cite_text = cite_elem.text.strip()
                    if cite_text.isdigit():
                        citations = int(cite_text)
                except Exception:
                    pass
                
                results.append(CNKIResult(
                    title=title,
                    authors=authors,
                    year=year,
                    abstract="",
                    link=link,
                    citations=citations,
                    source=source,
                    database="CNKI"
                ))
                
            except Exception:
                continue
                
    finally:
        if driver:
            driver.quit()
    
    return results


def _search_via_baidu_xueshu(query: str, limit: int) -> List[CNKIResult]:
    """
    使用百度学术作为备用搜索源
    优先使用 Playwright，失败则回退到 httpx
    """
    # 尝试 Playwright
    try:
        return _search_baidu_playwright(query, limit)
    except Exception as e:
        print(f"百度学术 Playwright 失败: {e}")
    
    # 回退到 httpx
    return _search_baidu_httpx(query, limit)


def _search_baidu_playwright(query: str, limit: int) -> List[CNKIResult]:
    """使用 Playwright 搜索百度学术"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError("需要安装 playwright")
    
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        try:
            url = f"https://xueshu.baidu.com/s?wd={query}&ie=utf-8"
            page.goto(url, timeout=30000)
            
            page.wait_for_selector(".result", timeout=10000)
            time.sleep(random.uniform(1, 2))
            
            items = page.query_selector_all(".result")
            
            for item in items[:limit]:
                try:
                    # 标题
                    title_elem = item.query_selector("h3 a")
                    if title_elem:
                        title = title_elem.inner_text().strip()
                        link = title_elem.get_attribute("href") or ""
                    else:
                        continue
                    
                    # 作者
                    author_elem = item.query_selector(".author_text")
                    authors = author_elem.inner_text().strip() if author_elem else ""
                    
                    # 摘要
                    abstract_elem = item.query_selector(".c_abstract")
                    abstract = abstract_elem.inner_text().strip() if abstract_elem else ""
                    
                    # 来源和年份
                    source = ""
                    year = ""
                    source_elem = item.query_selector(".sc_info")
                    if source_elem:
                        source_text = source_elem.inner_text()
                        year_match = re.search(r'\b(19|20)\d{2}\b', source_text)
                        if year_match:
                            year = year_match.group()
                        # 提取期刊名
                        parts = source_text.split("-")
                        if len(parts) > 1:
                            source = parts[0].strip()
                    
                    # 引用数
                    citations = 0
                    cite_elem = item.query_selector(".sc_cite_cont")
                    if cite_elem:
                        cite_text = cite_elem.inner_text()
                        cite_match = re.search(r'\d+', cite_text)
                        if cite_match:
                            citations = int(cite_match.group())
                    
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
                    
                except Exception:
                    continue
                    
        finally:
            browser.close()
    
    return results


def _search_baidu_httpx(query: str, limit: int) -> List[CNKIResult]:
    """
    使用 httpx 搜索百度学术（纯HTTP请求，无浏览器依赖）
    """
    import httpx
    from bs4 import BeautifulSoup
    
    results = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    url = f"https://xueshu.baidu.com/s?wd={query}&ie=utf-8"
    
    try:
        response = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(".result")
        
        for item in items[:limit]:
            try:
                # 标题
                title_elem = item.select_one("h3 a")
                if title_elem:
                    title = title_elem.get_text().strip()
                    link = title_elem.get("href", "")
                else:
                    continue
                
                # 作者
                author_elem = item.select_one(".author_text")
                authors = author_elem.get_text().strip() if author_elem else ""
                
                # 摘要
                abstract_elem = item.select_one(".c_abstract")
                abstract = abstract_elem.get_text().strip() if abstract_elem else ""
                
                # 来源和年份
                source = ""
                year = ""
                source_elem = item.select_one(".sc_info")
                if source_elem:
                    source_text = source_elem.get_text()
                    year_match = re.search(r'\b(19|20)\d{2}\b', source_text)
                    if year_match:
                        year = year_match.group()
                    parts = source_text.split("-")
                    if len(parts) > 1:
                        source = parts[0].strip()
                
                # 引用数
                citations = 0
                cite_elem = item.select_one(".sc_cite_cont")
                if cite_elem:
                    cite_text = cite_elem.get_text()
                    cite_match = re.search(r'\d+', cite_text)
                    if cite_match:
                        citations = int(cite_match.group())
                
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
                
            except Exception:
                continue
                
    except Exception as e:
        print(f"httpx 百度学术搜索失败: {e}")
    
    return results


def format_results(results: List[CNKIResult]) -> str:
    """
    格式化搜索结果为 Markdown
    """
    if not results:
        return "未找到相关文献"
    
    lines = []
    lines.append(f"## 中文文献搜索结果 ({len(results)} 篇)\n")
    
    for i, r in enumerate(results, 1):
        lines.append(f"### {i}. {r.title}")
        lines.append(f"**作者**: {r.authors}")
        lines.append(f"**期刊**: {r.source} ({r.year}) | **引用**: {r.citations}")
        
        if r.abstract:
            abstract_preview = r.abstract[:200] + "..." if len(r.abstract) > 200 else r.abstract
            lines.append(f"\n{abstract_preview}")
        
        if r.link:
            lines.append(f"\n[查看原文]({r.link})")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def get_article_detail(article_id: str) -> Optional[dict]:
    """
    获取文章详情（预留接口）
    """
    return None
