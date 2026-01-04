# -*- coding: utf-8 -*-
"""
UI组件模块
可复用的 Gradio UI 组件
"""

from typing import List, Dict, Optional, Tuple, Any
from ui.styles import (
    create_score_html,
    create_progress_bar_html,
    get_score_color,
    get_score_label
)


def create_score_display(
    scores: Dict[str, float],
    overall_score: Optional[float] = None
) -> str:
    """
    创建评分展示 HTML
    
    Args:
        scores: 各维度评分 {"维度名": 分数}
        overall_score: 综合评分
        
    Returns:
        str: HTML 代码
    """
    html_parts = ['<div style="display: flex; flex-wrap: wrap; gap: 1rem;">']
    
    # 综合评分
    if overall_score is not None:
        html_parts.append(f'''
        <div style="flex: 1; min-width: 150px;">
            {create_score_html(overall_score, "综合评分")}
        </div>
        ''')
    
    # 各维度评分
    html_parts.append('<div style="flex: 2; min-width: 250px;">')
    
    for dim_name, score in scores.items():
        color = get_score_color(score)
        html_parts.append(f'''
        <div style="margin-bottom: 0.75rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                <span style="font-size: 0.9rem;">{dim_name}</span>
                <span style="font-weight: bold; color: {color};">{score:.1f}</span>
            </div>
            <div style="background: #e2e8f0; border-radius: 999px; height: 8px; overflow: hidden;">
                <div style="
                    background: {color};
                    width: {score * 10}%;
                    height: 100%;
                    border-radius: 999px;
                "></div>
            </div>
        </div>
        ''')
    
    html_parts.append('</div></div>')
    
    return ''.join(html_parts)


def create_diff_display(
    original: str,
    modified: str,
    title: str = "修改对比"
) -> str:
    """
    创建差异对比展示 HTML
    
    Args:
        original: 原始文本
        modified: 修改后文本
        title: 标题
        
    Returns:
        str: HTML 代码
    """
    from utils.diff import DiffGenerator
    
    diff_gen = DiffGenerator()
    old_html, new_html = diff_gen.highlight_changes_html(original, modified)
    stats = diff_gen.get_change_summary(original, modified)
    
    similarity_pct = stats['similarity'] * 100
    
    return f'''
    <div style="border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            font-weight: bold;
        ">
            {title}
            <span style="float: right; font-weight: normal; opacity: 0.9;">
                相似度: {similarity_pct:.1f}%
            </span>
        </div>
        <div style="display: flex;">
            <div style="flex: 1; padding: 1rem; border-right: 1px solid #e2e8f0;">
                <div style="font-size: 0.8rem; color: #718096; margin-bottom: 0.5rem;">原文</div>
                <div style="line-height: 1.8;">{old_html}</div>
            </div>
            <div style="flex: 1; padding: 1rem;">
                <div style="font-size: 0.8rem; color: #718096; margin-bottom: 0.5rem;">修改后</div>
                <div style="line-height: 1.8;">{new_html}</div>
            </div>
        </div>
        <div style="
            background: #f7fafc;
            padding: 0.75rem 1rem;
            font-size: 0.85rem;
            color: #718096;
        ">
            变更统计: 新增 {stats['chars_added']} 字符 | 删除 {stats['chars_removed']} 字符 | 替换 {stats['replace']} 处
        </div>
    </div>
    '''


def create_diagnosis_card(
    dimension: str,
    score: float,
    problems: List[str],
    suggestions: List[str]
) -> str:
    """
    创建诊断卡片 HTML
    
    Args:
        dimension: 维度名称
        score: 评分
        problems: 问题列表
        suggestions: 建议列表
        
    Returns:
        str: HTML 代码
    """
    color = get_score_color(score)
    grade = get_score_label(score)
    
    problems_html = ''.join([f'<li style="margin-bottom: 0.5rem;">{p}</li>' for p in problems])
    suggestions_html = ''.join([f'<li style="margin-bottom: 0.5rem;">{s}</li>' for s in suggestions])
    
    return f'''
    <div style="
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        margin-bottom: 1rem;
        overflow: hidden;
    ">
        <div style="
            background: {color}15;
            border-bottom: 1px solid #e2e8f0;
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <span style="font-weight: bold; font-size: 1.1rem;">{dimension}</span>
            <span style="
                background: {color};
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 999px;
                font-size: 0.9rem;
            ">{score:.1f}分 · {grade}</span>
        </div>
        <div style="padding: 1rem;">
            <div style="margin-bottom: 1rem;">
                <div style="font-weight: bold; color: #e53e3e; margin-bottom: 0.5rem;">🔴 主要问题</div>
                <ul style="margin: 0; padding-left: 1.5rem; color: #4a5568;">
                    {problems_html if problems else '<li>暂无明显问题</li>'}
                </ul>
            </div>
            <div>
                <div style="font-weight: bold; color: #48bb78; margin-bottom: 0.5rem;">✅ 改进建议</div>
                <ul style="margin: 0; padding-left: 1.5rem; color: #4a5568;">
                    {suggestions_html if suggestions else '<li>继续保持</li>'}
                </ul>
            </div>
        </div>
    </div>
    '''


def create_processing_status(
    status: str,
    message: str,
    progress: Optional[float] = None
) -> str:
    """
    创建处理状态展示 HTML
    
    Args:
        status: 状态 (processing/success/error)
        message: 消息
        progress: 进度 (0-100)
        
    Returns:
        str: HTML 代码
    """
    icons = {
        "processing": "⏳",
        "success": "✅",
        "error": "❌",
        "warning": "⚠️"
    }
    
    colors = {
        "processing": "#667eea",
        "success": "#48bb78",
        "error": "#f56565",
        "warning": "#ed8936"
    }
    
    icon = icons.get(status, "ℹ️")
    color = colors.get(status, "#718096")
    
    progress_html = ""
    if progress is not None:
        progress_html = f'''
        <div style="margin-top: 0.75rem;">
            {create_progress_bar_html(progress, 100)}
        </div>
        '''
    
    return f'''
    <div style="
        background: {color}10;
        border-left: 4px solid {color};
        padding: 1rem;
        border-radius: 0 8px 8px 0;
    ">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <span style="color: {color}; font-weight: bold;">{message}</span>
        </div>
        {progress_html}
    </div>
    '''


def create_search_result_card(
    title: str,
    authors: str,
    year: str,
    abstract: str,
    citations: int,
    source: str,
    link: str = ""
) -> str:
    """
    创建搜索结果卡片 HTML
    
    Args:
        title: 标题
        authors: 作者
        year: 年份
        abstract: 摘要
        citations: 引用数
        source: 来源
        link: 链接
        
    Returns:
        str: HTML 代码
    """
    abstract_preview = abstract[:200] + "..." if len(abstract) > 200 else abstract
    
    link_html = f'<a href="{link}" target="_blank" style="color: #667eea; text-decoration: none;">查看原文 →</a>' if link else ''
    
    return f'''
    <div style="
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        transition: box-shadow 0.2s ease;
    " onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)'" 
       onmouseout="this.style.boxShadow='none'">
        <div style="font-weight: bold; font-size: 1.1rem; color: #2d3748; margin-bottom: 0.5rem;">
            {title}
        </div>
        <div style="color: #718096; font-size: 0.9rem; margin-bottom: 0.5rem;">
            {authors} · {year} · 引用: {citations}
        </div>
        <div style="color: #4a5568; font-size: 0.9rem; margin-bottom: 0.75rem;">
            {abstract_preview}
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="
                background: #667eea20;
                color: #667eea;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.8rem;
            ">{source}</span>
            {link_html}
        </div>
    </div>
    '''


def create_stat_card(
    value: str,
    label: str,
    icon: str = "📊",
    color: str = "#667eea"
) -> str:
    """
    创建统计卡片 HTML
    
    Args:
        value: 数值
        label: 标签
        icon: 图标
        color: 颜色
        
    Returns:
        str: HTML 代码
    """
    return f'''
    <div style="
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        min-width: 120px;
    ">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 1.8rem; font-weight: bold; color: {color};">{value}</div>
        <div style="font-size: 0.85rem; color: #718096;">{label}</div>
    </div>
    '''


def create_step_progress(
    steps: List[Dict[str, str]],
    current_step: int
) -> str:
    """
    创建步骤进度展示 HTML
    
    Args:
        steps: 步骤列表 [{"name": "步骤名", "desc": "描述"}]
        current_step: 当前步骤索引 (从0开始)
        
    Returns:
        str: HTML 代码
    """
    html_parts = ['<div style="display: flex; flex-direction: column; gap: 0.5rem; padding: 1rem;">']
    
    for i, step in enumerate(steps):
        if i < current_step:
            # 已完成
            status_icon = "✅"
            bg_color = "#48bb78"
            text_color = "#276749"
            line_color = "#48bb78"
            status = "completed"
        elif i == current_step:
            # 进行中
            status_icon = "⏳"
            bg_color = "#667eea"
            text_color = "#4c51bf"
            line_color = "#e2e8f0"
            status = "active"
        else:
            # 待处理
            status_icon = "○"
            bg_color = "#e2e8f0"
            text_color = "#a0aec0"
            line_color = "#e2e8f0"
            status = "pending"
        
        # 连接线（除了最后一个）
        connector_html = ""
        if i < len(steps) - 1:
            connector_html = f'''
            <div style="
                position: absolute;
                left: 15px;
                top: 32px;
                width: 2px;
                height: calc(100% - 20px);
                background: {line_color};
            "></div>
            '''
        
        # 动画效果（仅当前步骤）
        animation_style = ""
        if status == "active":
            animation_style = '''
                animation: pulse 2s infinite;
            '''
        
        html_parts.append(f'''
        <div style="
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            position: relative;
            padding-bottom: 1rem;
        ">
            {connector_html}
            <div style="
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: {bg_color}20;
                border: 2px solid {bg_color};
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1rem;
                flex-shrink: 0;
                {animation_style}
            ">
                {status_icon}
            </div>
            <div style="flex: 1;">
                <div style="
                    font-weight: {'bold' if status == 'active' else 'normal'};
                    color: {text_color};
                    font-size: 1rem;
                ">{step.get('name', f'步骤 {i+1}')}</div>
                <div style="
                    color: #718096;
                    font-size: 0.85rem;
                    margin-top: 0.25rem;
                ">{step.get('desc', '')}</div>
            </div>
        </div>
        ''')
    
    html_parts.append('</div>')
    
    # 添加动画样式
    html_parts.insert(0, '''
    <style>
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.05); }
        }
    </style>
    ''')
    
    return ''.join(html_parts)


def create_processing_timeline(
    events: List[Dict[str, str]]
) -> str:
    """
    创建处理时间线展示 HTML
    
    Args:
        events: 事件列表 [{"time": "时间", "event": "事件", "status": "状态"}]
        
    Returns:
        str: HTML 代码
    """
    html_parts = ['<div style="padding: 1rem; border: 1px solid #e2e8f0; border-radius: 12px;">']
    html_parts.append('<div style="font-weight: bold; margin-bottom: 1rem; color: #2d3748;">📋 处理记录</div>')
    
    for event in events:
        status = event.get('status', 'info')
        
        status_colors = {
            'success': '#48bb78',
            'error': '#f56565',
            'warning': '#ed8936',
            'info': '#667eea',
            'processing': '#805ad5'
        }
        
        status_icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'processing': '⏳'
        }
        
        color = status_colors.get(status, '#718096')
        icon = status_icons.get(status, '•')
        
        html_parts.append(f'''
        <div style="
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.5rem 0;
            border-bottom: 1px solid #f7fafc;
        ">
            <span style="
                color: #a0aec0;
                font-size: 0.8rem;
                min-width: 60px;
            ">{event.get('time', '')}</span>
            <span style="font-size: 1rem;">{icon}</span>
            <span style="color: #4a5568; flex: 1;">{event.get('event', '')}</span>
        </div>
        ''')
    
    html_parts.append('</div>')
    return ''.join(html_parts)


def create_loading_spinner(
    message: str = "正在处理中...",
    sub_message: str = ""
) -> str:
    """
    创建加载动画 HTML
    
    Args:
        message: 主消息
        sub_message: 副消息
        
    Returns:
        str: HTML 代码
    """
    return f'''
    <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        @keyframes fadeIn {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
    </style>
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem;
        animation: fadeIn 0.3s ease;
    ">
        <div style="
            width: 48px;
            height: 48px;
            border: 4px solid #e2e8f0;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 1.5rem;
        "></div>
        <div style="
            font-size: 1.1rem;
            color: #2d3748;
            font-weight: 500;
            margin-bottom: 0.5rem;
        ">{message}</div>
        <div style="
            font-size: 0.9rem;
            color: #718096;
        ">{sub_message}</div>
    </div>
    '''


def create_task_summary(
    title: str,
    stats: Dict[str, Any],
    duration_seconds: float = 0
) -> str:
    """
    创建任务完成摘要 HTML
    
    Args:
        title: 标题
        stats: 统计数据
        duration_seconds: 耗时（秒）
        
    Returns:
        str: HTML 代码
    """
    # 格式化时间
    if duration_seconds >= 60:
        duration_str = f"{int(duration_seconds // 60)}分{int(duration_seconds % 60)}秒"
    else:
        duration_str = f"{duration_seconds:.1f}秒"
    
    stats_html = ""
    for key, value in stats.items():
        stats_html += f'''
        <div style="
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #f7fafc;
        ">
            <span style="color: #718096;">{key}</span>
            <span style="font-weight: 500; color: #2d3748;">{value}</span>
        </div>
        '''
    
    return f'''
    <div style="
        background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
        border: 1px solid #667eea40;
        border-radius: 12px;
        padding: 1.5rem;
    ">
        <div style="
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
        ">
            <span style="font-size: 1.5rem;">✅</span>
            <span style="font-size: 1.2rem; font-weight: bold; color: #2d3748;">{title}</span>
        </div>
        <div style="
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #667eea;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        ">
            ⏱️ 总耗时: {duration_str}
        </div>
        <div style="
            background: white;
            border-radius: 8px;
            padding: 1rem;
        ">
            {stats_html}
        </div>
    </div>
    '''


def create_error_display(
    error_message: str,
    error_code: str = "",
    suggestions: Optional[List[str]] = None
) -> str:
    """
    创建错误展示 HTML
    
    Args:
        error_message: 错误消息
        error_code: 错误代码
        suggestions: 建议列表
        
    Returns:
        str: HTML 代码
    """
    suggestions = suggestions or []
    
    suggestions_html = ""
    if suggestions:
        suggestions_html = '<div style="margin-top: 1rem;"><div style="font-weight: 500; margin-bottom: 0.5rem;">💡 建议操作：</div><ul style="margin: 0; padding-left: 1.5rem; color: #4a5568;">'
        for s in suggestions:
            suggestions_html += f'<li style="margin-bottom: 0.25rem;">{s}</li>'
        suggestions_html += '</ul></div>'
    
    code_html = f'<div style="color: #c53030; font-size: 0.8rem; font-family: monospace; margin-top: 0.5rem;">[{error_code}]</div>' if error_code else ""
    
    return f'''
    <div style="
        background: #fed7d7;
        border: 1px solid #fc8181;
        border-radius: 12px;
        padding: 1.5rem;
    ">
        <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
            <span style="font-size: 1.5rem;">❌</span>
            <div style="flex: 1;">
                <div style="font-weight: bold; color: #c53030; margin-bottom: 0.25rem;">处理出错</div>
                <div style="color: #742a2a;">{error_message}</div>
                {code_html}
                {suggestions_html}
            </div>
        </div>
    </div>
    '''
