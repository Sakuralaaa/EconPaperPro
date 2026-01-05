# -*- coding: utf-8 -*-
"""
期刊级别查询模块
使用 Easy Scholar API 查询期刊分区和级别
支持 CSSCI、SSCI、SCI 等多种索引
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
import re
import time


@dataclass
class JournalRank:
    """期刊级别信息"""
    name: str
    issn: str
    # 中文核心
    cssci: bool = False  # CSSCI 收录
    cssci_expanded: bool = False  # CSSCI 扩展版
    pku_core: bool = False  # 北大核心
    # 国际索引
    ssci: bool = False
    ssci_zone: str = ""  # Q1, Q2, Q3, Q4
    sci: bool = False
    sci_zone: str = ""
    # 其他信息
    impact_factor: float = 0.0
    ahci: bool = False
    esci: bool = False
    ei: bool = False


def check_journal_rank(journal_name: str, issn: str = "") -> Optional[JournalRank]:
    """
    查询期刊级别
    
    优先使用 Easy Scholar API，备用使用本地缓存
    
    Args:
        journal_name: 期刊名称
        issn: ISSN 号（可选）
        
    Returns:
        JournalRank: 期刊级别信息
    """
    # 尝试 Easy Scholar API
    try:
        return _query_easy_scholar(journal_name, issn)
    except Exception as e:
        print(f"Easy Scholar 查询失败: {e}")
    
    # 尝试通过网页抓取
    try:
        return _scrape_journal_info(journal_name)
    except Exception as e:
        print(f"网页抓取失败: {e}")
    
    # 使用本地知识库
    return _query_local_database(journal_name)


def _query_easy_scholar(journal_name: str, issn: str) -> Optional[JournalRank]:
    """
    通过 Easy Scholar API 查询
    
    Easy Scholar 是一个浏览器插件，可以显示论文的期刊分区信息
    这里我们模拟其查询接口
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError("需要安装 playwright: pip install playwright && playwright install chromium")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        try:
            # 访问 Easy Scholar 官网或中科院期刊分区表
            url = f"https://www.letpub.com.cn/index.php?page=journalapp&view=search&searchname={journal_name}"
            page.goto(url, timeout=15000)
            
            # 等待结果
            page.wait_for_selector("table", timeout=10000)
            time.sleep(1)
            
            # 查找匹配的期刊
            rows = page.query_selector_all("table tbody tr")
            
            for row in rows:
                cells = row.query_selector_all("td")
                if len(cells) >= 5:
                    name = cells[0].inner_text().strip()
                    if journal_name.lower() in name.lower():
                        issn_found = cells[1].inner_text().strip() if len(cells) > 1 else ""
                        
                        # 解析分区信息
                        zone_text = cells[4].inner_text().strip() if len(cells) > 4 else ""
                        if_text = cells[3].inner_text().strip() if len(cells) > 3 else ""
                        
                        ssci = "SSCI" in zone_text
                        sci = "SCI" in zone_text
                        
                        # 解析分区
                        ssci_zone = ""
                        sci_zone = ""
                        zone_match = re.search(r'(\d)区', zone_text)
                        if zone_match:
                            zone_num = zone_match.group(1)
                            if ssci:
                                ssci_zone = f"Q{zone_num}"
                            if sci:
                                sci_zone = f"Q{zone_num}"
                        
                        # 解析影响因子
                        impact_factor = 0.0
                        if_match = re.search(r'[\d.]+', if_text)
                        if if_match:
                            try:
                                impact_factor = float(if_match.group())
                            except:
                                pass
                        
                        return JournalRank(
                            name=name,
                            issn=issn_found,
                            ssci=ssci,
                            ssci_zone=ssci_zone,
                            sci=sci,
                            sci_zone=sci_zone,
                            impact_factor=impact_factor
                        )
                        
        finally:
            browser.close()
    
    return None


def _scrape_journal_info(journal_name: str) -> Optional[JournalRank]:
    """
    从中科院期刊分区表网页抓取
    """
    import httpx
    from bs4 import BeautifulSoup
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 尝试 LetPub
    url = f"https://www.letpub.com.cn/index.php?page=journalapp&view=search&searchname={journal_name}"
    
    response = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 解析表格
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")
        for row in rows[1:]:  # 跳过表头
            cells = row.find_all("td")
            if len(cells) >= 5:
                name = cells[0].get_text().strip()
                if journal_name.lower() in name.lower():
                    issn = cells[1].get_text().strip()
                    zone_text = cells[4].get_text().strip()
                    if_text = cells[3].get_text().strip()
                    
                    ssci = "SSCI" in zone_text
                    sci = "SCI" in zone_text
                    
                    ssci_zone = ""
                    sci_zone = ""
                    zone_match = re.search(r'(\d)区', zone_text)
                    if zone_match:
                        zone_num = zone_match.group(1)
                        if ssci:
                            ssci_zone = f"Q{zone_num}"
                        if sci:
                            sci_zone = f"Q{zone_num}"
                    
                    impact_factor = 0.0
                    try:
                        if_match = re.search(r'[\d.]+', if_text)
                        if if_match:
                            impact_factor = float(if_match.group())
                    except Exception:
                        pass
                    
                    return JournalRank(
                        name=name,
                        issn=issn,
                        ssci=ssci,
                        ssci_zone=ssci_zone,
                        sci=sci,
                        sci_zone=sci_zone,
                        impact_factor=impact_factor
                    )
    
    return None


def _query_local_database(journal_name: str) -> Optional[JournalRank]:
    """
    查询本地知识库（常见期刊）
    """
    # 常见中文核心期刊
    CSSCI_JOURNALS = {
        "经济研究": JournalRank(name="经济研究", issn="0577-9154", cssci=True, pku_core=True),
        "管理世界": JournalRank(name="管理世界", issn="1002-5502", cssci=True, pku_core=True),
        "金融研究": JournalRank(name="金融研究", issn="1002-7246", cssci=True, pku_core=True),
        "中国工业经济": JournalRank(name="中国工业经济", issn="1006-480X", cssci=True, pku_core=True),
        "会计研究": JournalRank(name="会计研究", issn="1003-2886", cssci=True, pku_core=True),
        "世界经济": JournalRank(name="世界经济", issn="1002-9621", cssci=True, pku_core=True),
        "经济学季刊": JournalRank(name="经济学(季刊)", issn="2095-1086", cssci=True, pku_core=True),
        "南开管理评论": JournalRank(name="南开管理评论", issn="1008-3448", cssci=True, pku_core=True),
        "经济科学": JournalRank(name="经济科学", issn="1002-5839", cssci=True, pku_core=True),
        "财经研究": JournalRank(name="财经研究", issn="1001-9952", cssci=True, pku_core=True),
        "财贸经济": JournalRank(name="财贸经济", issn="1002-8102", cssci=True, pku_core=True),
        "数量经济技术经济研究": JournalRank(name="数量经济技术经济研究", issn="1000-3894", cssci=True, pku_core=True),
        "审计研究": JournalRank(name="审计研究", issn="1002-4239", cssci=True, pku_core=True),
        "国际金融研究": JournalRank(name="国际金融研究", issn="1006-1029", cssci=True, pku_core=True),
        "中国农村经济": JournalRank(name="中国农村经济", issn="1002-8870", cssci=True, pku_core=True),
    }
    
    # 常见 SSCI 期刊（Q1/Q2）
    SSCI_TOP_JOURNALS = {
        "Journal of Finance": JournalRank(name="Journal of Finance", issn="0022-1082", ssci=True, ssci_zone="Q1", impact_factor=7.5),
        "Journal of Financial Economics": JournalRank(name="Journal of Financial Economics", issn="0304-405X", ssci=True, ssci_zone="Q1", impact_factor=8.0),
        "Review of Financial Studies": JournalRank(name="Review of Financial Studies", issn="0893-9454", ssci=True, ssci_zone="Q1", impact_factor=6.5),
        "Journal of Accounting and Economics": JournalRank(name="Journal of Accounting and Economics", issn="0165-4101", ssci=True, ssci_zone="Q1", impact_factor=5.5),
        "Journal of Political Economy": JournalRank(name="Journal of Political Economy", issn="0022-3808", ssci=True, ssci_zone="Q1", impact_factor=9.0),
        "American Economic Review": JournalRank(name="American Economic Review", issn="0002-8282", ssci=True, ssci_zone="Q1", impact_factor=6.8),
        "Quarterly Journal of Economics": JournalRank(name="Quarterly Journal of Economics", issn="0033-5533", ssci=True, ssci_zone="Q1", impact_factor=11.0),
        "Econometrica": JournalRank(name="Econometrica", issn="0012-9682", ssci=True, ssci_zone="Q1", impact_factor=6.5),
        "Review of Economic Studies": JournalRank(name="Review of Economic Studies", issn="0034-6527", ssci=True, ssci_zone="Q1", impact_factor=5.0),
        "Journal of Monetary Economics": JournalRank(name="Journal of Monetary Economics", issn="0304-3932", ssci=True, ssci_zone="Q1", impact_factor=4.5),
        "Management Science": JournalRank(name="Management Science", issn="0025-1909", ssci=True, ssci_zone="Q1", impact_factor=5.0),
        "Strategic Management Journal": JournalRank(name="Strategic Management Journal", issn="0143-2095", ssci=True, ssci_zone="Q1", impact_factor=7.5),
        "Journal of International Business Studies": JournalRank(name="Journal of International Business Studies", issn="0047-2506", ssci=True, ssci_zone="Q1", impact_factor=8.0),
        "Journal of Management": JournalRank(name="Journal of Management", issn="0149-2063", ssci=True, ssci_zone="Q1", impact_factor=10.0),
        "Academy of Management Journal": JournalRank(name="Academy of Management Journal", issn="0001-4273", ssci=True, ssci_zone="Q1", impact_factor=10.5),
        "Organization Science": JournalRank(name="Organization Science", issn="1047-7039", ssci=True, ssci_zone="Q1", impact_factor=4.5),
    }
    
    # 合并查找
    all_journals = {**CSSCI_JOURNALS, **SSCI_TOP_JOURNALS}
    
    # 精确匹配
    if journal_name in all_journals:
        return all_journals[journal_name]
    
    # 模糊匹配
    journal_lower = journal_name.lower()
    for name, rank in all_journals.items():
        if journal_lower in name.lower() or name.lower() in journal_lower:
            return rank
    
    return None


def is_high_quality_journal(rank: Optional[JournalRank], source_type: str = "chinese") -> bool:
    """
    判断是否为高质量期刊
    
    Args:
        rank: 期刊级别信息
        source_type: "chinese" 或 "english"
        
    Returns:
        bool: 是否符合标准
    """
    if not rank:
        return False
    
    if source_type == "chinese":
        # 中文要求：CSSCI 或 北大核心
        return rank.cssci or rank.cssci_expanded or rank.pku_core
    else:
        # 英文要求：SSCI Q1/Q2 或 SCI Q1/Q2
        if rank.ssci and rank.ssci_zone in ["Q1", "Q2"]:
            return True
        if rank.sci and rank.sci_zone in ["Q1", "Q2"]:
            return True
        return False


def filter_high_quality_papers(papers: List[dict], source_type: str = "chinese") -> List[dict]:
    """
    过滤保留高质量期刊的论文
    
    Args:
        papers: 论文列表
        source_type: "chinese" 或 "english"
        
    Returns:
        List[dict]: 过滤后的论文列表
    """
    filtered = []
    
    for paper in papers:
        journal = paper.get("journal", paper.get("source", ""))
        if not journal:
            continue
        
        rank = check_journal_rank(journal)
        
        if is_high_quality_journal(rank, source_type):
            # 添加级别信息
            if rank:
                if source_type == "chinese":
                    paper["rank_info"] = "CSSCI" if rank.cssci else ("北大核心" if rank.pku_core else "")
                else:
                    if rank.ssci:
                        paper["rank_info"] = f"SSCI {rank.ssci_zone}"
                    elif rank.sci:
                        paper["rank_info"] = f"SCI {rank.sci_zone}"
                    
                    if rank.impact_factor > 0:
                        paper["impact_factor"] = rank.impact_factor
            
            filtered.append(paper)
    
    return filtered


def format_rank_info(rank: Optional[JournalRank]) -> str:
    """
    格式化期刊级别信息为显示字符串
    """
    if not rank:
        return "未知"
    
    parts = []
    
    if rank.cssci:
        parts.append("CSSCI")
    elif rank.cssci_expanded:
        parts.append("CSSCI扩展")
    
    if rank.pku_core:
        parts.append("北大核心")
    
    if rank.ssci:
        parts.append(f"SSCI {rank.ssci_zone}")
    
    if rank.sci:
        parts.append(f"SCI {rank.sci_zone}")
    
    if rank.ahci:
        parts.append("AHCI")
    
    if rank.ei:
        parts.append("EI")
    
    if rank.impact_factor > 0:
        parts.append(f"IF={rank.impact_factor:.2f}")
    
    return " | ".join(parts) if parts else "未索引"