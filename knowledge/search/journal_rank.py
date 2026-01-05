# -*- coding: utf-8 -*-
"""
期刊层次查询模块
查询期刊的级别信息（CSSCI/北核/SSCI/SCI等）

数据来源：
1. 内置期刊数据库（常见经管类期刊）
2. Easy Scholar API（如可用）
"""

from typing import Optional, Dict, List
from dataclasses import dataclass
import re


@dataclass
class JournalRank:
    """期刊级别信息"""
    name: str
    cssci: bool = False  # 是否CSSCI
    pku: bool = False    # 是否北大核心
    ssci: bool = False   # 是否SSCI
    sci: bool = False    # 是否SCI
    ssci_quartile: str = ""  # SSCI分区 (Q1/Q2/Q3/Q4)
    sci_quartile: str = ""   # SCI分区
    impact_factor: float = 0.0  # 影响因子
    category: str = ""   # 学科分类


# 内置经管类核心期刊数据库
# 数据来源：中国社科院期刊等级目录、北大核心期刊目录
CHINESE_TOP_JOURNALS = {
    # 经济学顶刊（A类/权威期刊）
    "经济研究": JournalRank("经济研究", cssci=True, pku=True, category="经济学"),
    "管理世界": JournalRank("管理世界", cssci=True, pku=True, category="管理学"),
    "中国社会科学": JournalRank("中国社会科学", cssci=True, pku=True, category="综合"),
    "经济学(季刊)": JournalRank("经济学(季刊)", cssci=True, pku=True, category="经济学"),
    "经济学季刊": JournalRank("经济学季刊", cssci=True, pku=True, category="经济学"),
    
    # 经济学A类期刊
    "金融研究": JournalRank("金融研究", cssci=True, pku=True, category="金融学"),
    "中国工业经济": JournalRank("中国工业经济", cssci=True, pku=True, category="产业经济"),
    "世界经济": JournalRank("世界经济", cssci=True, pku=True, category="国际经济"),
    "经济科学": JournalRank("经济科学", cssci=True, pku=True, category="经济学"),
    "南开经济研究": JournalRank("南开经济研究", cssci=True, pku=True, category="经济学"),
    "经济理论与经济管理": JournalRank("经济理论与经济管理", cssci=True, pku=True, category="经济学"),
    
    # 管理学A类期刊
    "会计研究": JournalRank("会计研究", cssci=True, pku=True, category="会计学"),
    "南开管理评论": JournalRank("南开管理评论", cssci=True, pku=True, category="管理学"),
    "管理科学学报": JournalRank("管理科学学报", cssci=True, pku=True, category="管理学"),
    "中国管理科学": JournalRank("中国管理科学", cssci=True, pku=True, category="管理学"),
    "管理评论": JournalRank("管理评论", cssci=True, pku=True, category="管理学"),
    
    # 金融学期刊
    "国际金融研究": JournalRank("国际金融研究", cssci=True, pku=True, category="金融学"),
    "金融经济学研究": JournalRank("金融经济学研究", cssci=True, pku=True, category="金融学"),
    "证券市场导报": JournalRank("证券市场导报", cssci=True, pku=True, category="金融学"),
    "保险研究": JournalRank("保险研究", cssci=True, pku=True, category="金融学"),
    
    # 其他CSSCI期刊
    "财经研究": JournalRank("财经研究", cssci=True, pku=True, category="经济学"),
    "财贸经济": JournalRank("财贸经济", cssci=True, pku=True, category="经济学"),
    "数量经济技术经济研究": JournalRank("数量经济技术经济研究", cssci=True, pku=True, category="经济学"),
    "产业经济研究": JournalRank("产业经济研究", cssci=True, pku=True, category="产业经济"),
    "经济管理": JournalRank("经济管理", cssci=True, pku=True, category="管理学"),
    "中国农村经济": JournalRank("中国农村经济", cssci=True, pku=True, category="农业经济"),
    "农业经济问题": JournalRank("农业经济问题", cssci=True, pku=True, category="农业经济"),
    "财政研究": JournalRank("财政研究", cssci=True, pku=True, category="财政学"),
    "税务研究": JournalRank("税务研究", cssci=True, pku=True, category="财政学"),
    "审计研究": JournalRank("审计研究", cssci=True, pku=True, category="会计学"),
    "统计研究": JournalRank("统计研究", cssci=True, pku=True, category="统计学"),
    "中国软科学": JournalRank("中国软科学", cssci=True, pku=True, category="科技管理"),
    "科研管理": JournalRank("科研管理", cssci=True, pku=True, category="科技管理"),
    "科学学研究": JournalRank("科学学研究", cssci=True, pku=True, category="科技管理"),
    "外国经济与管理": JournalRank("外国经济与管理", cssci=True, pku=True, category="管理学"),
    "经济与管理研究": JournalRank("经济与管理研究", cssci=True, pku=True, category="经济学"),
    "当代经济科学": JournalRank("当代经济科学", cssci=True, pku=True, category="经济学"),
    "经济问题探索": JournalRank("经济问题探索", cssci=True, pku=True, category="经济学"),
    "财经论丛": JournalRank("财经论丛", cssci=True, pku=True, category="经济学"),
    "商业经济与管理": JournalRank("商业经济与管理", cssci=True, pku=True, category="工商管理"),
    "国际贸易问题": JournalRank("国际贸易问题", cssci=True, pku=True, category="国际经济"),
    "国际经济评论": JournalRank("国际经济评论", cssci=True, pku=True, category="国际经济"),
    "亚太经济": JournalRank("亚太经济", cssci=True, pku=True, category="国际经济"),
    "投资研究": JournalRank("投资研究", cssci=True, category="金融学"),
    "上海金融": JournalRank("上海金融", cssci=True, category="金融学"),
}

# SSCI/SCI 经管类期刊数据库
ENGLISH_TOP_JOURNALS = {
    # SSCI 顶刊 Q1
    "american economic review": JournalRank("American Economic Review", ssci=True, ssci_quartile="Q1", impact_factor=6.0, category="Economics"),
    "quarterly journal of economics": JournalRank("Quarterly Journal of Economics", ssci=True, ssci_quartile="Q1", impact_factor=11.0, category="Economics"),
    "journal of political economy": JournalRank("Journal of Political Economy", ssci=True, ssci_quartile="Q1", impact_factor=7.0, category="Economics"),
    "econometrica": JournalRank("Econometrica", ssci=True, ssci_quartile="Q1", impact_factor=5.0, category="Economics"),
    "review of economic studies": JournalRank("Review of Economic Studies", ssci=True, ssci_quartile="Q1", impact_factor=5.0, category="Economics"),
    
    # 金融学顶刊
    "journal of finance": JournalRank("Journal of Finance", ssci=True, ssci_quartile="Q1", impact_factor=7.0, category="Finance"),
    "journal of financial economics": JournalRank("Journal of Financial Economics", ssci=True, ssci_quartile="Q1", impact_factor=6.0, category="Finance"),
    "review of financial studies": JournalRank("Review of Financial Studies", ssci=True, ssci_quartile="Q1", impact_factor=5.0, category="Finance"),
    
    # 管理学顶刊
    "academy of management journal": JournalRank("Academy of Management Journal", ssci=True, ssci_quartile="Q1", impact_factor=10.0, category="Management"),
    "academy of management review": JournalRank("Academy of Management Review", ssci=True, ssci_quartile="Q1", impact_factor=12.0, category="Management"),
    "administrative science quarterly": JournalRank("Administrative Science Quarterly", ssci=True, ssci_quartile="Q1", impact_factor=9.0, category="Management"),
    "management science": JournalRank("Management Science", ssci=True, ssci_quartile="Q1", impact_factor=5.0, category="Management"),
    "strategic management journal": JournalRank("Strategic Management Journal", ssci=True, ssci_quartile="Q1", impact_factor=8.0, category="Management"),
    "organization science": JournalRank("Organization Science", ssci=True, ssci_quartile="Q1", impact_factor=4.0, category="Management"),
    
    # 营销学顶刊
    "journal of marketing": JournalRank("Journal of Marketing", ssci=True, ssci_quartile="Q1", impact_factor=9.0, category="Marketing"),
    "journal of marketing research": JournalRank("Journal of Marketing Research", ssci=True, ssci_quartile="Q1", impact_factor=5.0, category="Marketing"),
    "journal of consumer research": JournalRank("Journal of Consumer Research", ssci=True, ssci_quartile="Q1", impact_factor=5.0, category="Marketing"),
    
    # 会计学顶刊
    "accounting review": JournalRank("Accounting Review", ssci=True, ssci_quartile="Q1", impact_factor=4.0, category="Accounting"),
    "journal of accounting research": JournalRank("Journal of Accounting Research", ssci=True, ssci_quartile="Q1", impact_factor=4.0, category="Accounting"),
    "journal of accounting and economics": JournalRank("Journal of Accounting and Economics", ssci=True, ssci_quartile="Q1", impact_factor=5.0, category="Accounting"),
    
    # 其他 SSCI Q1/Q2 期刊
    "journal of international economics": JournalRank("Journal of International Economics", ssci=True, ssci_quartile="Q1", category="Economics"),
    "journal of monetary economics": JournalRank("Journal of Monetary Economics", ssci=True, ssci_quartile="Q1", category="Economics"),
    "journal of development economics": JournalRank("Journal of Development Economics", ssci=True, ssci_quartile="Q1", category="Economics"),
    "journal of public economics": JournalRank("Journal of Public Economics", ssci=True, ssci_quartile="Q1", category="Economics"),
    "journal of labor economics": JournalRank("Journal of Labor Economics", ssci=True, ssci_quartile="Q1", category="Economics"),
    "journal of econometrics": JournalRank("Journal of Econometrics", ssci=True, ssci_quartile="Q1", category="Economics"),
    "review of economics and statistics": JournalRank("Review of Economics and Statistics", ssci=True, ssci_quartile="Q1", category="Economics"),
    "economic journal": JournalRank("Economic Journal", ssci=True, ssci_quartile="Q1", category="Economics"),
    "journal of business venturing": JournalRank("Journal of Business Venturing", ssci=True, ssci_quartile="Q1", category="Management"),
    "research policy": JournalRank("Research Policy", ssci=True, ssci_quartile="Q1", category="Management"),
    "journal of international business studies": JournalRank("Journal of International Business Studies", ssci=True, ssci_quartile="Q1", category="Management"),
    
    # SSCI Q2 期刊
    "world development": JournalRank("World Development", ssci=True, ssci_quartile="Q2", category="Economics"),
    "china economic review": JournalRank("China Economic Review", ssci=True, ssci_quartile="Q2", category="Economics"),
    "journal of comparative economics": JournalRank("Journal of Comparative Economics", ssci=True, ssci_quartile="Q2", category="Economics"),
    "energy economics": JournalRank("Energy Economics", ssci=True, ssci_quartile="Q1", category="Economics"),
    "ecological economics": JournalRank("Ecological Economics", ssci=True, ssci_quartile="Q1", category="Economics"),
    "journal of business ethics": JournalRank("Journal of Business Ethics", ssci=True, ssci_quartile="Q2", category="Management"),
    "journal of management studies": JournalRank("Journal of Management Studies", ssci=True, ssci_quartile="Q1", category="Management"),
    "journal of operations management": JournalRank("Journal of Operations Management", ssci=True, ssci_quartile="Q1", category="Management"),
}


def check_journal_rank(journal_name: str) -> Optional[JournalRank]:
    """
    查询期刊级别
    
    Args:
        journal_name: 期刊名称
        
    Returns:
        JournalRank: 期刊级别信息，未找到则返回 None
    """
    if not journal_name:
        return None
    
    # 清理期刊名称
    name = journal_name.strip()
    name_lower = name.lower()
    
    # 查询中文期刊
    if name in CHINESE_TOP_JOURNALS:
        return CHINESE_TOP_JOURNALS[name]
    
    # 模糊匹配中文期刊
    for key, rank in CHINESE_TOP_JOURNALS.items():
        if key in name or name in key:
            return rank
    
    # 查询英文期刊
    if name_lower in ENGLISH_TOP_JOURNALS:
        return ENGLISH_TOP_JOURNALS[name_lower]
    
    # 模糊匹配英文期刊
    for key, rank in ENGLISH_TOP_JOURNALS.items():
        if key in name_lower or name_lower in key:
            return rank
    
    return None


def is_high_quality_journal(rank: Optional[JournalRank], language: str = "any") -> bool:
    """
    判断是否为高质量期刊
    
    Args:
        rank: 期刊级别信息
        language: 语言类型 ("chinese", "english", "any")
        
    Returns:
        bool: 是否为高质量期刊
    """
    if rank is None:
        return False
    
    if language == "chinese":
        return rank.cssci or rank.pku
    elif language == "english":
        return rank.ssci or rank.sci
    else:
        return rank.cssci or rank.pku or rank.ssci or rank.sci


def format_rank_info(rank: JournalRank) -> str:
    """
    格式化期刊级别信息
    
    Args:
        rank: 期刊级别信息
        
    Returns:
        str: 格式化的级别字符串
    """
    parts = []
    
    if rank.cssci:
        parts.append("CSSCI")
    if rank.pku:
        parts.append("北核")
    if rank.ssci:
        quartile = f"({rank.ssci_quartile})" if rank.ssci_quartile else ""
        parts.append(f"SSCI{quartile}")
    if rank.sci:
        quartile = f"({rank.sci_quartile})" if rank.sci_quartile else ""
        parts.append(f"SCI{quartile}")
    
    if rank.impact_factor > 0:
        parts.append(f"IF={rank.impact_factor:.1f}")
    
    return " | ".join(parts) if parts else "普通期刊"


def get_journal_category(rank: JournalRank) -> str:
    """
    获取期刊学科分类
    
    Args:
        rank: 期刊级别信息
        
    Returns:
        str: 学科分类
    """
    return rank.category if rank else ""


def filter_by_quality(papers: List[Dict], 
                     require_cssci: bool = False,
                     require_ssci: bool = False,
                     min_ssci_quartile: str = "") -> List[Dict]:
    """
    根据期刊级别筛选论文
    
    Args:
        papers: 论文列表
        require_cssci: 是否要求CSSCI/北核
        require_ssci: 是否要求SSCI
        min_ssci_quartile: 最低SSCI分区要求 (Q1/Q2/Q3/Q4)
        
    Returns:
        List[Dict]: 筛选后的论文列表
    """
    if not require_cssci and not require_ssci:
        return papers
    
    filtered = []
    quartile_order = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
    min_quartile_num = quartile_order.get(min_ssci_quartile, 4)
    
    for paper in papers:
        journal = paper.get("journal", "")
        rank = check_journal_rank(journal)
        
        if rank is None:
            # 无法识别的期刊，保留（避免误删）
            filtered.append(paper)
            continue
        
        # 检查是否满足要求
        if require_cssci and (rank.cssci or rank.pku):
            paper["rank_info"] = format_rank_info(rank)
            filtered.append(paper)
            continue
            
        if require_ssci and rank.ssci:
            # 检查分区要求
            quartile_num = quartile_order.get(rank.ssci_quartile, 4)
            if quartile_num <= min_quartile_num:
                paper["rank_info"] = format_rank_info(rank)
                filtered.append(paper)
                continue
    
    return filtered


def enrich_with_rank_info(papers: List[Dict]) -> List[Dict]:
    """
    为论文添加期刊级别信息
    
    Args:
        papers: 论文列表
        
    Returns:
        List[Dict]: 添加了级别信息的论文列表
    """
    for paper in papers:
        journal = paper.get("journal", "")
        rank = check_journal_rank(journal)
        
        if rank:
            paper["rank_info"] = format_rank_info(rank)
            paper["journal_category"] = rank.category
        else:
            paper["rank_info"] = ""
            paper["journal_category"] = ""
    
    return papers