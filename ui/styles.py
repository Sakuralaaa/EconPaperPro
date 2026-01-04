# -*- coding: utf-8 -*-
"""
UI样式模块
自定义 CSS 样式
"""

# 主题色
PRIMARY_COLOR = "#667eea"
SECONDARY_COLOR = "#764ba2"
SUCCESS_COLOR = "#48bb78"
WARNING_COLOR = "#ed8936"
DANGER_COLOR = "#f56565"

# 自定义 CSS
CUSTOM_CSS = """
/* 整体样式 */
.gradio-container {
    font-family: 'Microsoft YaHei', 'PingFang SC', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* 标题样式 */
h1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    font-size: 2.5rem !important;
    margin-bottom: 1rem !important;
}

/* 主按钮样式 */
.primary-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: bold !important;
    transition: all 0.3s ease !important;
}

.primary-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
}

/* 成功按钮 */
.success-btn {
    background: linear-gradient(135deg, #48bb78 0%, #38a169 100%) !important;
    border: none !important;
    color: white !important;
}

/* 警告按钮 */
.warning-btn {
    background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%) !important;
    border: none !important;
    color: white !important;
}

/* 卡片样式 */
.card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* 评分卡片 */
.score-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
}

.score-card .score {
    font-size: 3rem;
    font-weight: bold;
}

.score-card .label {
    font-size: 1rem;
    opacity: 0.9;
}

/* 差异高亮 */
.diff-insert {
    background-color: #d4edda !important;
    color: #155724 !important;
    padding: 2px 4px;
    border-radius: 3px;
}

.diff-delete {
    background-color: #f8d7da !important;
    color: #721c24 !important;
    text-decoration: line-through;
    padding: 2px 4px;
    border-radius: 3px;
}

/* 进度条 */
.progress-bar {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border-radius: 999px;
    height: 8px;
}

/* 标签页样式 */
.tabs > .tabitem {
    border-radius: 8px 8px 0 0 !important;
}

/* 输入框样式 */
textarea, input[type="text"] {
    border-radius: 8px !important;
    border: 2px solid #e2e8f0 !important;
    transition: border-color 0.2s ease !important;
}

textarea:focus, input[type="text"]:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

/* Accordion 样式 */
.accordion {
    border-radius: 8px !important;
    border: 1px solid #e2e8f0 !important;
    margin-bottom: 0.5rem !important;
}

/* 表格样式 */
table {
    border-collapse: collapse;
    width: 100%;
}

th, td {
    border: 1px solid #e2e8f0;
    padding: 12px;
    text-align: left;
}

th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

tr:nth-child(even) {
    background-color: #f7fafc;
}

/* 滑块样式 */
input[type="range"] {
    accent-color: #667eea;
}

/* 复选框样式 */
input[type="checkbox"] {
    accent-color: #667eea;
}

/* 下拉框样式 */
select {
    border-radius: 8px !important;
    border: 2px solid #e2e8f0 !important;
}

/* 文件上传区域 */
.upload-area {
    border: 2px dashed #667eea !important;
    border-radius: 12px !important;
    background: rgba(102, 126, 234, 0.05) !important;
}

/* 状态指示器 */
.status-success {
    color: #48bb78;
}

.status-warning {
    color: #ed8936;
}

.status-error {
    color: #f56565;
}

/* 工具提示 */
.tooltip {
    position: relative;
    display: inline-block;
}

.tooltip .tooltiptext {
    visibility: hidden;
    background-color: #333;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 8px 12px;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}

/* 加载动画 */
.loading-spinner {
    border: 3px solid #f3f3f3;
    border-top: 3px solid #667eea;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* 响应式布局 */
@media (max-width: 768px) {
    h1 {
        font-size: 1.8rem !important;
    }
    
    .card {
        padding: 1rem;
    }
}
"""


def get_score_color(score: float) -> str:
    """
    根据分数返回对应颜色
    
    Args:
        score: 分数 (0-10)
        
    Returns:
        str: 颜色代码
    """
    if score >= 8:
        return SUCCESS_COLOR
    elif score >= 6:
        return PRIMARY_COLOR
    elif score >= 4:
        return WARNING_COLOR
    else:
        return DANGER_COLOR


def get_score_label(score: float) -> str:
    """
    根据分数返回等级标签
    
    Args:
        score: 分数 (0-10)
        
    Returns:
        str: 等级标签
    """
    if score >= 8:
        return "优秀"
    elif score >= 6:
        return "良好"
    elif score >= 4:
        return "一般"
    else:
        return "待改进"


def create_score_html(score: float, label: str = "综合评分") -> str:
    """
    创建评分卡片 HTML
    
    Args:
        score: 分数
        label: 标签
        
    Returns:
        str: HTML 代码
    """
    color = get_score_color(score)
    grade = get_score_label(score)
    
    return f"""
    <div style="
        background: linear-gradient(135deg, {color} 0%, {color}cc 100%);
        color: white;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px {color}40;
    ">
        <div style="font-size: 3rem; font-weight: bold;">{score:.1f}</div>
        <div style="font-size: 1rem; opacity: 0.9;">{label}</div>
        <div style="font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.8;">{grade}</div>
    </div>
    """


def create_progress_bar_html(value: float, max_value: float = 100, label: str = "") -> str:
    """
    创建进度条 HTML
    
    Args:
        value: 当前值
        max_value: 最大值
        label: 标签
        
    Returns:
        str: HTML 代码
    """
    percentage = (value / max_value) * 100
    
    return f"""
    <div style="margin-bottom: 0.5rem;">
        {f'<div style="font-size: 0.9rem; margin-bottom: 0.25rem;">{label}</div>' if label else ''}
        <div style="background: #e2e8f0; border-radius: 999px; height: 8px; overflow: hidden;">
            <div style="
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                width: {percentage}%;
                height: 100%;
                border-radius: 999px;
                transition: width 0.3s ease;
            "></div>
        </div>
        <div style="font-size: 0.8rem; color: #718096; margin-top: 0.25rem;">{value:.1f}%</div>
    </div>
    """
