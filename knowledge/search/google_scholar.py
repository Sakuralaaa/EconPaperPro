# -*- coding: utf-8 -*-
"""
Google Scholar 搜索模块
使用无头浏览器进行真实网页抓取
支持 Google 账号认证以避免频率限制
"""

from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path
import json
import re
import time
import random
import os

# Cookies 存储路径
COOKIES_DIR = Path.home() / ".econpaper_pro" / "cookies"
GS_COOKIES_FILE = COOKIES_DIR / "google_scholar_cookies.json"


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
    使用无头浏览器进行真实网页抓取
    
    Args:
        query: 搜索查询
        limit: 返回数量
        year_from: 起始年份
        year_to: 结束年份
        
    Returns:
        List[ScholarResult]: 搜索结果列表
    """
    # 优先尝试 Playwright
    try:
        return _search_via_playwright(query, limit, year_from, year_to)
    except Exception as e:
        print(f"Playwright 搜索失败: {e}")
    
    # 备用方案：Selenium
    try:
        return _search_via_selenium(query, limit, year_from, year_to)
    except Exception as e:
        print(f"Selenium 搜索失败: {e}")
    
    # 最后备用：httpx 直接请求（可能被反爬）
    try:
        return _search_via_httpx(query, limit, year_from, year_to)
    except Exception as e:
        print(f"httpx 搜索失败: {e}")
    
    return []


def authenticate_google_scholar(callback=None):
    """
    打开可见浏览器窗口让用户登录 Google Scholar
    登录完成后保存 cookies 供后续使用
    
    Args:
        callback: 认证完成后的回调函数，接收 success: bool 参数
    
    Returns:
        bool: 认证是否成功
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        if callback:
            callback(False)
        raise ImportError("需要安装 playwright: pip install playwright && playwright install chromium")
    
    # 确保 cookies 目录存在
    COOKIES_DIR.mkdir(parents=True, exist_ok=True)
    
    success = False
    
    with sync_playwright() as p:
        # 启动可见浏览器（非无头模式）
        browser = p.chromium.launch(
            headless=False,  # 可见模式
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()
        
        try:
            # 导航到 Google Scholar
            page.goto("https://scholar.google.com/", timeout=60000)
            
            print("=" * 50)
            print("请在浏览器中登录您的 Google 账号")
            print("登录完成后，浏览器将自动关闭并保存认证信息")
            print("=" * 50)
            
            # 等待用户登录（检测登录状态）
            # 可以通过检测页面元素或 URL 来判断登录状态
            max_wait = 300  # 最多等待 5 分钟
            wait_interval = 2
            waited = 0
            
            while waited < max_wait:
                time.sleep(wait_interval)
                waited += wait_interval
                
                # 检查是否已登录（Google 账号头像或登录按钮）
                try:
                    # 检查是否有用户头像（已登录状态）
                    avatar = page.query_selector("a[href*='SignOut'], img[alt*='Account'], a[aria-label*='Google']")
                    if avatar:
                        # 已登录，保存 cookies
                        cookies = context.cookies()
                        
                        # 保存到文件
                        with open(GS_COOKIES_FILE, "w", encoding="utf-8") as f:
                            json.dump(cookies, f, indent=2)
                        
                        print("✅ 登录成功！Cookies 已保存")
                        success = True
                        break
                        
                except Exception:
                    pass
                
                # 检查用户是否手动关闭了页面
                if page.is_closed():
                    print("⚠️ 浏览器窗口已关闭")
                    break
            
            if not success and waited >= max_wait:
                print("⚠️ 登录超时，请重试")
                
        except Exception as e:
            print(f"认证过程出错: {e}")
            
        finally:
            browser.close()
    
    if callback:
        callback(success)
    
    return success


def check_authentication_status() -> bool:
    """
    检查是否已有有效的 Google Scholar 认证
    
    Returns:
        bool: 是否已认证
    """
    if not GS_COOKIES_FILE.exists():
        return False
    
    try:
        with open(GS_COOKIES_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        
        # 检查是否有有效的 Google cookies
        for cookie in cookies:
            if "google" in cookie.get("domain", "").lower():
                # 检查是否过期
                expires = cookie.get("expires", -1)
                if expires == -1 or expires > time.time():
                    return True
        
        return False
        
    except Exception:
        return False


def clear_authentication():
    """
    清除保存的认证信息
    """
    if GS_COOKIES_FILE.exists():
        GS_COOKIES_FILE.unlink()
        print("✅ 认证信息已清除")


def _load_cookies():
    """
    加载保存的 cookies
    
    Returns:
        list: cookies 列表，如果不存在则返回空列表
    """
    if not GS_COOKIES_FILE.exists():
        return []
    
    try:
        with open(GS_COOKIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _search_via_playwright(
    query: str,
    limit: int,
    year_from: Optional[int],
    year_to: Optional[int]
) -> List[ScholarResult]:
    """
    使用 Playwright 无头浏览器搜索
    如果有保存的 cookies 则使用已认证的会话
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError("需要安装 playwright")
    
    results = []
    cookies = _load_cookies()
    
    with sync_playwright() as p:
        # 启动无头浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # 如果有保存的 cookies，加载它们
        if cookies:
            context.add_cookies(cookies)
        
        page = context.new_page()
        
        try:
            # 构建搜索URL
            url = f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}"
            if year_from:
                url += f"&as_ylo={year_from}"
            if year_to:
                url += f"&as_yhi={year_to}"
            
            page.goto(url, timeout=30000)
            
            # 等待搜索结果加载
            page.wait_for_selector(".gs_r.gs_or.gs_scl", timeout=10000)
            
            # 随机延迟，避免被检测
            time.sleep(random.uniform(1, 2))
            
            # 解析搜索结果
            items = page.query_selector_all(".gs_r.gs_or.gs_scl")
            
            for item in items[:limit]:
                try:
                    # 标题和链接
                    title_elem = item.query_selector(".gs_rt a")
                    if title_elem:
                        title = title_elem.inner_text()
                        link = title_elem.get_attribute("href") or ""
                    else:
                        title_elem = item.query_selector(".gs_rt")
                        title = title_elem.inner_text() if title_elem else "无标题"
                        link = ""
                    
                    # 作者和出版信息
                    author_elem = item.query_selector(".gs_a")
                    author_text = author_elem.inner_text() if author_elem else ""
                    
                    # 解析作者和年份
                    authors = ""
                    year = ""
                    if author_text:
                        parts = author_text.split(" - ")
                        if parts:
                            authors = parts[0].strip()
                        # 尝试提取年份
                        year_match = re.search(r'\b(19|20)\d{2}\b', author_text)
                        if year_match:
                            year = year_match.group()
                    
                    # 摘要
                    abstract_elem = item.query_selector(".gs_rs")
                    abstract = abstract_elem.inner_text() if abstract_elem else ""
                    
                    # 引用数
                    citations = 0
                    cite_elem = item.query_selector("a[href*='cites']")
                    if cite_elem:
                        cite_text = cite_elem.inner_text()
                        cite_match = re.search(r'\d+', cite_text)
                        if cite_match:
                            citations = int(cite_match.group())
                    
                    results.append(ScholarResult(
                        title=title,
                        authors=authors,
                        year=year,
                        abstract=abstract,
                        link=link,
                        citations=citations,
                        source="Google Scholar"
                    ))
                    
                except Exception as e:
                    continue
                    
        finally:
            browser.close()
    
    return results


def _search_via_selenium(
    query: str,
    limit: int,
    year_from: Optional[int],
    year_to: Optional[int]
) -> List[ScholarResult]:
    """
    使用 Selenium 无头浏览器搜索
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    results = []
    
    # 配置无头浏览器
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # 构建搜索URL
        url = f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}"
        if year_from:
            url += f"&as_ylo={year_from}"
        if year_to:
            url += f"&as_yhi={year_to}"
        
        driver.get(url)
        
        # 等待搜索结果
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".gs_r.gs_or.gs_scl")))
        
        time.sleep(random.uniform(1, 2))
        
        # 解析结果
        items = driver.find_elements(By.CSS_SELECTOR, ".gs_r.gs_or.gs_scl")
        
        for item in items[:limit]:
            try:
                # 标题和链接
                try:
                    title_elem = item.find_element(By.CSS_SELECTOR, ".gs_rt a")
                    title = title_elem.text
                    link = title_elem.get_attribute("href") or ""
                except Exception:
                    title_elem = item.find_element(By.CSS_SELECTOR, ".gs_rt")
                    title = title_elem.text
                    link = ""
                
                # 作者信息
                try:
                    author_elem = item.find_element(By.CSS_SELECTOR, ".gs_a")
                    author_text = author_elem.text
                except Exception:
                    author_text = ""
                
                authors = ""
                year = ""
                if author_text:
                    parts = author_text.split(" - ")
                    if parts:
                        authors = parts[0].strip()
                    year_match = re.search(r'\b(19|20)\d{2}\b', author_text)
                    if year_match:
                        year = year_match.group()
                
                # 摘要
                try:
                    abstract_elem = item.find_element(By.CSS_SELECTOR, ".gs_rs")
                    abstract = abstract_elem.text
                except Exception:
                    abstract = ""
                
                # 引用数
                citations = 0
                try:
                    cite_elem = item.find_element(By.CSS_SELECTOR, "a[href*='cites']")
                    cite_text = cite_elem.text
                    cite_match = re.search(r'\d+', cite_text)
                    if cite_match:
                        citations = int(cite_match.group())
                except Exception:
                    pass
                
                results.append(ScholarResult(
                    title=title,
                    authors=authors,
                    year=year,
                    abstract=abstract,
                    link=link,
                    citations=citations,
                    source="Google Scholar"
                ))
                
            except Exception:
                continue
                
    finally:
        if driver:
            driver.quit()
    
    return results


def _search_via_httpx(
    query: str,
    limit: int,
    year_from: Optional[int],
    year_to: Optional[int]
) -> List[ScholarResult]:
    """
    使用 httpx 直接请求（备用方案）
    """
    import httpx
    from bs4 import BeautifulSoup
    
    results = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    url = f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}"
    if year_from:
        url += f"&as_ylo={year_from}"
    if year_to:
        url += f"&as_yhi={year_to}"
    
    response = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select(".gs_r.gs_or.gs_scl")
    
    for item in items[:limit]:
        try:
            # 标题和链接
            title_elem = item.select_one(".gs_rt a")
            if title_elem:
                title = title_elem.get_text()
                link = title_elem.get("href", "")
            else:
                title_elem = item.select_one(".gs_rt")
                title = title_elem.get_text() if title_elem else "无标题"
                link = ""
            
            # 作者信息
            author_elem = item.select_one(".gs_a")
            author_text = author_elem.get_text() if author_elem else ""
            
            authors = ""
            year = ""
            if author_text:
                parts = author_text.split(" - ")
                if parts:
                    authors = parts[0].strip()
                year_match = re.search(r'\b(19|20)\d{2}\b', author_text)
                if year_match:
                    year = year_match.group()
            
            # 摘要
            abstract_elem = item.select_one(".gs_rs")
            abstract = abstract_elem.get_text() if abstract_elem else ""
            
            # 引用数
            citations = 0
            cite_elem = item.select_one("a[href*='cites']")
            if cite_elem:
                cite_text = cite_elem.get_text()
                cite_match = re.search(r'\d+', cite_text)
                if cite_match:
                    citations = int(cite_match.group())
            
            results.append(ScholarResult(
                title=title,
                authors=authors,
                year=year,
                abstract=abstract,
                link=link,
                citations=citations,
                source="Google Scholar"
            ))
            
        except Exception:
            continue
    
    return results


def format_results(results: List[ScholarResult]) -> str:
    """
    格式化搜索结果为 Markdown
    """
    if not results:
        return "未找到相关文献"
    
    lines = []
    lines.append(f"## Google Scholar 搜索结果 ({len(results)} 篇)\n")
    
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
