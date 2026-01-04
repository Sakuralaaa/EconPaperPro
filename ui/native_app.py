# -*- coding: utf-8 -*-
"""
EconPaper Pro - 原生 Tkinter GUI 应用
替代 Gradio Web 界面，直接双击运行
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime

# 确保模块路径正确
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
    INTERNAL_DIR = Path(getattr(sys, '_MEIPASS', BASE_DIR))
else:
    BASE_DIR = Path(__file__).parent.parent
    INTERNAL_DIR = BASE_DIR

sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(INTERNAL_DIR))


class ModernStyle:
    """简约白样式配置"""
    
    # 颜色主题 (Apple Style)
    PRIMARY = "#007AFF"       # 蓝色
    PRIMARY_DARK = "#005BB7"  # 深蓝色 (用于悬停)
    PRIMARY_LIGHT = "#E5F1FF"
    SECONDARY = "#5856D6"     # 紫色 (替代原有的 SECONDARY)
    SUCCESS = "#34C759"       # 绿色
    WARNING = "#FF9500"       # 橙色
    ERROR = "#FF3B30"         # 红色
    
    # 背景色
    BG_MAIN = "#FFFFFF"       # 纯白背景
    BG_CARD = "#FFFFFF"
    BG_SIDEBAR = "#F5F5F7"    # 浅灰侧边栏
    BG_HOVER = "#E8E8ED"      # 悬停色
    
    # 文字颜色
    TEXT_PRIMARY = "#1D1D1F"  # 深灰文字
    TEXT_SECONDARY = "#86868B" # 次要文字
    TEXT_LIGHT = "#FFFFFF"
    
    # 边框
    BORDER = "#D2D2D7"        # 细边框
    
    @classmethod
    def configure_styles(cls, root):
        """配置 ttk 样式"""
        style = ttk.Style(root)
        
        # 使用原生主题作为基础
        try:
            style.theme_use('clam')
        except Exception:
            pass
        
        # 全局配置
        style.configure(".", font=("Microsoft YaHei UI", 10))
        
        # 主按钮样式
        style.configure(
            "Primary.TButton",
            background=cls.PRIMARY,
            foreground=cls.TEXT_LIGHT,
            padding=(20, 10),
            borderwidth=0
        )
        
        # 标签
        style.configure(
            "Title.TLabel",
            background=cls.BG_MAIN,
            foreground=cls.TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 18, "bold")
        )
        
        # 框架
        style.configure(
            "Card.TFrame",
            background=cls.BG_CARD,
            relief="flat"
        )
        
        # 下拉框样式
        style.configure(
            "TCombobox",
            fieldbackground=cls.BG_MAIN,
            background=cls.BG_MAIN,
            bordercolor=cls.BORDER,
            lightcolor=cls.BORDER,
            darkcolor=cls.BORDER
        )
        
        return style


class EconPaperApp:
    """EconPaper Pro 主应用"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("📚 EconPaper Pro - 经管论文智能优化")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # 设置图标（如果存在）
        try:
            icon_path = BASE_DIR / "assets" / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass
        
        # 配置样式
        self.style = ModernStyle.configure_styles(root)
        
        # 设置背景色
        self.root.configure(bg=ModernStyle.BG_MAIN)
        
        # 当前选中的标签页
        self.current_tab = tk.StringVar(value="diagnose")
        
        # 创建主布局
        self._create_layout()
        
        # 状态变量
        self.is_processing = False
        
    def _create_layout(self):
        """创建主布局"""
        # 主容器
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 左侧导航栏
        self._create_sidebar(main_container)
        
        # 右侧内容区
        self.content_frame = ttk.Frame(main_container, style="Card.TFrame")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建各个功能页面
        self.pages = {}
        self._create_diagnose_page()
        self._create_optimize_page()
        self._create_dedup_page()
        self._create_search_page()
        self._create_revision_page()
        self._create_settings_page()
        
        # 默认显示诊断页面
        self._show_page("diagnose")
        
    def _create_sidebar(self, parent):
        """创建侧边栏 - 简约白风格"""
        sidebar = tk.Frame(parent, bg=ModernStyle.BG_SIDEBAR, width=220, bd=0)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # 右侧细边框
        border = tk.Frame(sidebar, bg=ModernStyle.BORDER, width=1)
        border.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Logo 区域
        logo_frame = tk.Frame(sidebar, bg=ModernStyle.BG_SIDEBAR)
        logo_frame.pack(fill=tk.X, pady=(30, 20), padx=20)
        
        logo_label = tk.Label(
            logo_frame,
            text="EconPaper Pro",
            font=("Microsoft YaHei UI", 15, "bold"),
            bg=ModernStyle.BG_SIDEBAR,
            fg=ModernStyle.TEXT_PRIMARY
        )
        logo_label.pack(anchor="w")
        
        version_label = tk.Label(
            logo_frame,
            text="智能学术论文优化系统",
            font=("Microsoft YaHei UI", 9),
            bg=ModernStyle.BG_SIDEBAR,
            fg=ModernStyle.TEXT_SECONDARY
        )
        version_label.pack(anchor="w")
        
        # 导航按钮
        self.nav_buttons = {}
        nav_items = [
            ("diagnose", "🔍 论文诊断"),
            ("optimize", "⚙️ 深度优化"),
            ("dedup", "🔧 降重降AI"),
            ("search", "🔎 学术搜索"),
            ("revision", "📝 退修助手"),
            ("settings", "⚙️ 模型管理"),
        ]
        
        for page_id, text in nav_items:
            btn = tk.Button(
                sidebar,
                text=f"  {text}",
                font=("Microsoft YaHei UI", 10),
                bg=ModernStyle.BG_SIDEBAR,
                fg=ModernStyle.TEXT_PRIMARY,
                activebackground=ModernStyle.BG_HOVER,
                activeforeground=ModernStyle.PRIMARY,
                bd=0,
                cursor="hand2",
                anchor="w",
                padx=15,
                pady=12,
                command=lambda p=page_id: self._show_page(p)
            )
            btn.pack(fill=tk.X, padx=10, pady=2)
            self.nav_buttons[page_id] = btn
            
            # 鼠标悬停效果
            btn.bind("<Enter>", lambda e, b=btn, p=page_id: self._on_nav_hover(b, p, True))
            btn.bind("<Leave>", lambda e, b=btn, p=page_id: self._on_nav_hover(b, p, False))

    def _on_nav_hover(self, btn, page_id, is_enter):
        """导航栏悬停效果"""
        if self.current_tab.get() == page_id:
            return
        if is_enter:
            btn.configure(bg=ModernStyle.BG_HOVER)
        else:
            btn.configure(bg=ModernStyle.BG_SIDEBAR)

    def _update_nav_style(self):
        """更新导航栏选中样式"""
        current = self.current_tab.get()
        for page_id, btn in self.nav_buttons.items():
            if page_id == current:
                btn.configure(bg=ModernStyle.PRIMARY_LIGHT, fg=ModernStyle.PRIMARY, font=("Microsoft YaHei UI", 10, "bold"))
            else:
                btn.configure(bg=ModernStyle.BG_SIDEBAR, fg=ModernStyle.TEXT_PRIMARY, font=("Microsoft YaHei UI", 10))
    
    def _show_page(self, page_id: str):
        """显示指定页面"""
        self.current_tab.set(page_id)
        self._update_nav_style()
        
        # 隐藏所有页面
        for page in self.pages.values():
            page.pack_forget()
        
        # 显示选中的页面
        if page_id in self.pages:
            self.pages[page_id].pack(fill=tk.BOTH, expand=True)
    
    def _create_diagnose_page(self):
        """创建论文诊断页面 - 简约白风格"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_CARD)
        self.pages["diagnose"] = page
        
        # 顶部标题区
        header = tk.Frame(page, bg=ModernStyle.BG_CARD)
        header.pack(fill=tk.X, padx=30, pady=(30, 20))
        
        tk.Label(
            header,
            text="论文诊断",
            font=("Microsoft YaHei UI", 20, "bold"),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            header,
            text="通过多维度 AI 算法分析论文质量，提供改进建议",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY
        ).pack(anchor="w", pady=(5, 0))
        
        # 主内容区
        content = tk.Frame(page, bg=ModernStyle.BG_CARD)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
        # 左侧输入
        left_panel = tk.Frame(content, bg=ModernStyle.BG_CARD)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # 操作栏
        actions = tk.Frame(left_panel, bg=ModernStyle.BG_CARD)
        actions.pack(fill=tk.X, pady=(0, 15))
        
        upload_btn = tk.Button(
            actions,
            text="📁 选择文件",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_SIDEBAR,
            fg=ModernStyle.TEXT_PRIMARY,
            activebackground=ModernStyle.BG_HOVER,
            bd=0,
            cursor="hand2",
            padx=15,
            pady=8,
            command=lambda: self._select_file("diagnose")
        )
        upload_btn.pack(side=tk.LEFT)
        
        self.diag_file_label = tk.Label(
            actions,
            text="未选择文件 (支持 PDF/Docx)",
            font=("Microsoft YaHei UI", 9),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY,
            padx=10
        )
        self.diag_file_label.pack(side=tk.LEFT)
        
        # 输入框容器 (带边框)
        input_border = tk.Frame(left_panel, bg=ModernStyle.BORDER, padx=1, pady=1)
        input_border.pack(fill=tk.BOTH, expand=True)
        
        self.diag_text = scrolledtext.ScrolledText(
            input_border,
            font=("Microsoft YaHei UI", 10),
            wrap=tk.WORD,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            padx=10,
            pady=10,
            undo=True
        )
        self.diag_text.pack(fill=tk.BOTH, expand=True)
        
        # 底部按钮
        diag_btn = tk.Button(
            left_panel,
            text="开始诊断",
            font=("Microsoft YaHei UI", 11, "bold"),
            bg=ModernStyle.PRIMARY,
            fg=ModernStyle.TEXT_LIGHT,
            activebackground=ModernStyle.PRIMARY_DARK,
            bd=0,
            cursor="hand2",
            padx=30,
            pady=10,
            command=self._run_diagnose
        )
        diag_btn.pack(pady=(20, 0))
        
        # 右侧结果
        right_panel = tk.Frame(content, bg=ModernStyle.BG_CARD)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))
        
        tk.Label(
            right_panel,
            text="诊断报告",
            font=("Microsoft YaHei UI", 11, "bold"),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 10))
        
        result_border = tk.Frame(right_panel, bg=ModernStyle.BORDER, padx=1, pady=1)
        result_border.pack(fill=tk.BOTH, expand=True)
        
        self.diag_result = scrolledtext.ScrolledText(
            result_border,
            font=("Microsoft YaHei UI", 10),
            wrap=tk.WORD,
            bg=ModernStyle.BG_SIDEBAR,
            relief="flat",
            padx=10,
            pady=10,
            state=tk.DISABLED
        )
        self.diag_result.pack(fill=tk.BOTH, expand=True)
        
        # 保存文件路径
        self.diag_file_path = None
        
    def _create_optimize_page(self):
        """创建深度优化页面 - 简约白风格"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_CARD)
        self.pages["optimize"] = page
        
        # 顶部标题区
        header = tk.Frame(page, bg=ModernStyle.BG_CARD)
        header.pack(fill=tk.X, padx=30, pady=(30, 20))
        
        tk.Label(
            header,
            text="深度优化",
            font=("Microsoft YaHei UI", 20, "bold"),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            header,
            text="针对不同投稿阶段和目标期刊，对论文各章节进行精细化打磨",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY
        ).pack(anchor="w", pady=(5, 0))
        
        # 主内容区
        content = tk.Frame(page, bg=ModernStyle.BG_CARD)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
        # 左侧配置面板
        config_panel = tk.Frame(content, bg=ModernStyle.BG_SIDEBAR, width=240, padx=20, pady=20)
        config_panel.pack(side=tk.LEFT, fill=tk.Y)
        config_panel.pack_propagate(False)
        
        # 1. 优化阶段
        tk.Label(config_panel, text="1. 优化阶段", font=("Microsoft YaHei UI", 10, "bold"), bg=ModernStyle.BG_SIDEBAR, fg=ModernStyle.TEXT_PRIMARY).pack(anchor="w", pady=(0, 10))
        self.opt_stage = tk.StringVar(value="submission")
        stages = [("初稿重构", "draft"), ("投稿优化", "submission"), ("退修回应", "revision"), ("终稿定稿", "final")]
        for text, value in stages:
            tk.Radiobutton(config_panel, text=text, variable=self.opt_stage, value=value, bg=ModernStyle.BG_SIDEBAR, activebackground=ModernStyle.BG_SIDEBAR, font=("Microsoft YaHei UI", 9)).pack(anchor="w", padx=5)
            
        # 2. 目标期刊
        tk.Label(config_panel, text="2. 目标期刊", font=("Microsoft YaHei UI", 10, "bold"), bg=ModernStyle.BG_SIDEBAR, fg=ModernStyle.TEXT_PRIMARY).pack(anchor="w", pady=(20, 10))
        self.opt_journal = tk.StringVar(value="")
        journals = ["", "经济研究", "管理世界", "金融研究", "中国工业经济", "会计研究", "其他"]
        journal_combo = ttk.Combobox(config_panel, textvariable=self.opt_journal, values=journals, state="readonly", width=18)
        journal_combo.pack(fill=tk.X, padx=5)
        
        # 3. 优化章节
        tk.Label(config_panel, text="3. 优化章节", font=("Microsoft YaHei UI", 10, "bold"), bg=ModernStyle.BG_SIDEBAR, fg=ModernStyle.TEXT_PRIMARY).pack(anchor="w", pady=(20, 10))
        sections = [("标题", "title"), ("摘要", "abstract"), ("引言", "introduction"), ("文献综述", "literature"), ("理论假设", "theory"), ("研究方法", "methodology"), ("实证结果", "results"), ("结论", "conclusion")]
        self.opt_sections = {}
        for text, value in sections:
            var = tk.BooleanVar(value=value in ["abstract", "introduction"])
            self.opt_sections[value] = var
            tk.Checkbutton(config_panel, text=text, variable=var, bg=ModernStyle.BG_SIDEBAR, activebackground=ModernStyle.BG_SIDEBAR, font=("Microsoft YaHei UI", 9)).pack(anchor="w", padx=5)
            
        # 4. 文件上传
        tk.Label(config_panel, text="4. 上传文件", font=("Microsoft YaHei UI", 10, "bold"), bg=ModernStyle.BG_SIDEBAR, fg=ModernStyle.TEXT_PRIMARY).pack(anchor="w", pady=(20, 10))
        tk.Button(config_panel, text="📁 选择文件", font=("Microsoft YaHei UI", 9), bg=ModernStyle.BG_MAIN, bd=1, relief="solid", command=lambda: self._select_file("optimize")).pack(fill=tk.X, padx=5)
        self.opt_file_label = tk.Label(config_panel, text="未选择文件", font=("Microsoft YaHei UI", 8), bg=ModernStyle.BG_SIDEBAR, fg=ModernStyle.TEXT_SECONDARY, wraplength=180)
        self.opt_file_label.pack(pady=5)
        
        # 优化按钮
        tk.Button(config_panel, text="开始优化", font=("Microsoft YaHei UI", 10, "bold"), bg=ModernStyle.PRIMARY, fg=ModernStyle.TEXT_LIGHT, bd=0, pady=8, command=self._run_optimize).pack(fill=tk.X, side=tk.BOTTOM)
        
        # 右侧编辑/结果区
        right_panel = tk.Frame(content, bg=ModernStyle.BG_CARD)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        # 输入
        tk.Label(right_panel, text="论文内容 (或粘贴文本)", font=("Microsoft YaHei UI", 10, "bold"), bg=ModernStyle.BG_CARD).pack(anchor="w", pady=(0, 5))
        in_border = tk.Frame(right_panel, bg=ModernStyle.BORDER, padx=1, pady=1)
        in_border.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        self.opt_input = scrolledtext.ScrolledText(in_border, font=("Microsoft YaHei UI", 10), wrap=tk.WORD, bg=ModernStyle.BG_MAIN, relief="flat", padx=10, pady=10)
        self.opt_input.pack(fill=tk.BOTH, expand=True)
        
        # 输出
        tk.Label(right_panel, text="优化建议与改写结果", font=("Microsoft YaHei UI", 10, "bold"), bg=ModernStyle.BG_CARD).pack(anchor="w", pady=(0, 5))
        out_border = tk.Frame(right_panel, bg=ModernStyle.BORDER, padx=1, pady=1)
        out_border.pack(fill=tk.BOTH, expand=True)
        self.opt_output = scrolledtext.ScrolledText(out_border, font=("Microsoft YaHei UI", 10), wrap=tk.WORD, bg=ModernStyle.BG_SIDEBAR, relief="flat", padx=10, pady=10, state=tk.DISABLED)
        self.opt_output.pack(fill=tk.BOTH, expand=True)
        
        self.opt_file_path = None
        
    def _create_dedup_page(self):
        """创建降重降AI页面 - 简约白风格"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_CARD)
        self.pages["dedup"] = page
        
        # 顶部标题区
        header = tk.Frame(page, bg=ModernStyle.BG_CARD)
        header.pack(fill=tk.X, padx=30, pady=(30, 20))
        
        tk.Label(
            header,
            text="降重与降 AI",
            font=("Microsoft YaHei UI", 20, "bold"),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            header,
            text="智能改写文本，降低重复率与 AI 检测痕迹",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY
        ).pack(anchor="w", pady=(5, 0))
        
        # 主内容区
        content = tk.Frame(page, bg=ModernStyle.BG_CARD)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
        # 顶部工具栏 (参数配置)
        toolbar = tk.Frame(content, bg=ModernStyle.BG_SIDEBAR, padx=15, pady=10)
        toolbar.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(toolbar, text="处理强度:", font=("Microsoft YaHei UI", 9), bg=ModernStyle.BG_SIDEBAR).pack(side=tk.LEFT)
        self.dedup_strength = tk.Scale(toolbar, from_=1, to=5, orient=tk.HORIZONTAL, length=120, bg=ModernStyle.BG_SIDEBAR, highlightthickness=0, bd=0)
        self.dedup_strength.set(3)
        self.dedup_strength.pack(side=tk.LEFT, padx=10)
        
        tk.Label(toolbar, text="保留术语:", font=("Microsoft YaHei UI", 9), bg=ModernStyle.BG_SIDEBAR).pack(side=tk.LEFT, padx=(20, 0))
        self.dedup_terms = tk.Entry(toolbar, font=("Microsoft YaHei UI", 9), width=25, bg=ModernStyle.BG_MAIN, relief="flat")
        self.dedup_terms.pack(side=tk.LEFT, padx=5, ipady=3)
        
        # 分栏布局
        panels = tk.Frame(content, bg=ModernStyle.BG_CARD)
        panels.pack(fill=tk.BOTH, expand=True)
        
        # 左侧输入
        left_p = tk.Frame(panels, bg=ModernStyle.BG_CARD)
        left_p.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(left_p, text="原始文本", font=("Microsoft YaHei UI", 10, "bold"), bg=ModernStyle.BG_CARD).pack(anchor="w", pady=(0, 5))
        in_b = tk.Frame(left_p, bg=ModernStyle.BORDER, padx=1, pady=1)
        in_b.pack(fill=tk.BOTH, expand=True)
        self.dedup_input = scrolledtext.ScrolledText(in_b, font=("Microsoft YaHei UI", 10), wrap=tk.WORD, bg=ModernStyle.BG_MAIN, relief="flat", padx=10, pady=10)
        self.dedup_input.pack(fill=tk.BOTH, expand=True)
        
        # 中间按钮列
        mid_p = tk.Frame(panels, bg=ModernStyle.BG_CARD, width=120)
        mid_p.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        btn_config = [
            ("📉 智能降重", self._run_dedup, ModernStyle.PRIMARY),
            ("🤖 降 AI 痕迹", self._run_deai, ModernStyle.SECONDARY),
            ("⚡ 深度全改", self._run_both_dedup, ModernStyle.SUCCESS)
        ]
        
        tk.Label(mid_p, bg=ModernStyle.BG_CARD).pack(expand=True) # 占位
        for text, cmd, color in btn_config:
            tk.Button(mid_p, text=text, font=("Microsoft YaHei UI", 9), bg=color, fg="white", bd=0, width=12, pady=10, cursor="hand2", command=cmd).pack(pady=5)
        tk.Label(mid_p, bg=ModernStyle.BG_CARD).pack(expand=True) # 占位
        
        # 右侧输出
        right_p = tk.Frame(panels, bg=ModernStyle.BG_CARD)
        right_p.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(right_p, text="改写结果", font=("Microsoft YaHei UI", 10, "bold"), bg=ModernStyle.BG_CARD).pack(anchor="w", pady=(0, 5))
        out_b = tk.Frame(right_p, bg=ModernStyle.BORDER, padx=1, pady=1)
        out_b.pack(fill=tk.BOTH, expand=True)
        self.dedup_output = scrolledtext.ScrolledText(out_b, font=("Microsoft YaHei UI", 10), wrap=tk.WORD, bg=ModernStyle.BG_SIDEBAR, relief="flat", padx=10, pady=10, state=tk.DISABLED)
        self.dedup_output.pack(fill=tk.BOTH, expand=True)
        
    def _create_search_page(self):
        """创建学术搜索页面 - 简约白风格"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_CARD)
        self.pages["search"] = page
        
        # 顶部标题区
        header = tk.Frame(page, bg=ModernStyle.BG_CARD)
        header.pack(fill=tk.X, padx=30, pady=(30, 20))
        
        tk.Label(
            header,
            text="学术搜索",
            font=("Microsoft YaHei UI", 20, "bold"),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w")
        
        # 搜索栏 (Apple Style Search Bar)
        search_bar = tk.Frame(page, bg=ModernStyle.BG_CARD)
        search_bar.pack(fill=tk.X, padx=30, pady=(0, 20))
        
        search_container = tk.Frame(search_bar, bg=ModernStyle.BG_SIDEBAR, padx=10, pady=5)
        search_container.pack(fill=tk.X)
        
        tk.Label(search_container, text="🔍", font=("Microsoft YaHei UI", 12), bg=ModernStyle.BG_SIDEBAR).pack(side=tk.LEFT, padx=5)
        
        self.search_query = tk.Entry(search_container, font=("Microsoft YaHei UI", 11), bg=ModernStyle.BG_SIDEBAR, relief="flat", bd=0)
        self.search_query.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_query.insert(0, "数字经济 企业创新")
        
        self.search_source = tk.StringVar(value="Google Scholar")
        source_combo = ttk.Combobox(search_container, textvariable=self.search_source, values=["Google Scholar", "知网 CNKI"], state="readonly", width=15)
        source_combo.pack(side=tk.LEFT, padx=10)
        
        search_btn = tk.Button(
            search_bar,
            text="搜索文献",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg=ModernStyle.PRIMARY,
            fg=ModernStyle.TEXT_LIGHT,
            bd=0,
            padx=25,
            pady=8,
            cursor="hand2",
            command=self._run_search
        )
        search_btn.pack(pady=15)
        
        # 结果区
        content = tk.Frame(page, bg=ModernStyle.BG_CARD)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
        res_b = tk.Frame(content, bg=ModernStyle.BORDER, padx=1, pady=1)
        res_b.pack(fill=tk.BOTH, expand=True)
        
        self.search_result = scrolledtext.ScrolledText(
            res_b,
            font=("Microsoft YaHei UI", 10),
            wrap=tk.WORD,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            padx=15,
            pady=15,
            state=tk.DISABLED
        )
        self.search_result.pack(fill=tk.BOTH, expand=True)
        
    def _create_revision_page(self):
        """创建退修助手页面 - 简约白风格"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_CARD)
        self.pages["revision"] = page
        
        # 顶部标题区
        header = tk.Frame(page, bg=ModernStyle.BG_CARD)
        header.pack(fill=tk.X, padx=30, pady=(30, 20))
        
        tk.Label(
            header,
            text="退修助手",
            font=("Microsoft YaHei UI", 20, "bold"),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            header,
            text="智能解析审稿意见，生成逐条回应策略与润色后的回应信",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY
        ).pack(anchor="w", pady=(5, 0))
        
        # 主内容区
        content = tk.Frame(page, bg=ModernStyle.BG_CARD)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
        # 左侧输入
        left_panel = tk.Frame(content, bg=ModernStyle.BG_CARD)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        tk.Label(left_panel, text="审稿意见 (Reviewer Comments)", font=("Microsoft YaHei UI", 10, "bold"), bg=ModernStyle.BG_CARD).pack(anchor="w", pady=(0, 5))
        comm_b = tk.Frame(left_panel, bg=ModernStyle.BORDER, padx=1, pady=1)
        comm_b.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        self.rev_comments = scrolledtext.ScrolledText(comm_b, font=("Microsoft YaHei UI", 10), wrap=tk.WORD, bg=ModernStyle.BG_MAIN, relief="flat", padx=10, pady=10)
        self.rev_comments.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(left_panel, text="论文摘要 (可选，提供上下文)", font=("Microsoft YaHei UI", 10, "bold"), bg=ModernStyle.BG_CARD).pack(anchor="w", pady=(0, 5))
        sum_b = tk.Frame(left_panel, bg=ModernStyle.BORDER, padx=1, pady=1)
        sum_b.pack(fill=tk.X, pady=(0, 15))
        self.rev_summary = scrolledtext.ScrolledText(sum_b, font=("Microsoft YaHei UI", 10), wrap=tk.WORD, height=6, bg=ModernStyle.BG_MAIN, relief="flat", padx=10, pady=10)
        self.rev_summary.pack(fill=tk.X)
        
        tk.Button(
            left_panel,
            text="生成回应策略",
            font=("Microsoft YaHei UI", 11, "bold"),
            bg=ModernStyle.PRIMARY,
            fg=ModernStyle.TEXT_LIGHT,
            bd=0,
            pady=10,
            cursor="hand2",
            command=self._run_revision
        ).pack(fill=tk.X)
        
        # 右侧结果
        right_panel = tk.Frame(content, bg=ModernStyle.BG_CARD)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))
        
        tk.Label(right_panel, text="回应建议与回应信草案", font=("Microsoft YaHei UI", 11, "bold"), bg=ModernStyle.BG_CARD).pack(anchor="w", pady=(0, 10))
        res_b = tk.Frame(right_panel, bg=ModernStyle.BORDER, padx=1, pady=1)
        res_b.pack(fill=tk.BOTH, expand=True)
        self.rev_output = scrolledtext.ScrolledText(res_b, font=("Microsoft YaHei UI", 10), wrap=tk.WORD, bg=ModernStyle.BG_SIDEBAR, relief="flat", padx=15, pady=15, state=tk.DISABLED)
        self.rev_output.pack(fill=tk.BOTH, expand=True)
        
    def _create_settings_page(self):
        """创建设置页面 - 简约白风格 + Cherry Studio 模式"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_CARD)
        self.pages["settings"] = page
        
        # 顶部标题区
        header = tk.Frame(page, bg=ModernStyle.BG_CARD)
        header.pack(fill=tk.X, padx=30, pady=(30, 20))
        
        tk.Label(
            header,
            text="模型管理",
            font=("Microsoft YaHei UI", 20, "bold"),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            header,
            text="配置 AI 模型供应商、API 密钥及嵌入模型参数",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY
        ).pack(anchor="w", pady=(5, 0))
        
        # 创建带滚动条的主容器
        main_canvas = tk.Canvas(page, bg=ModernStyle.BG_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg=ModernStyle.BG_CARD)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=800)
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # 鼠标滚轮支持
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=30)
        
        # ============ 1. 供应商选择 ============
        section1 = tk.Frame(scrollable_frame, bg=ModernStyle.BG_CARD)
        section1.pack(fill=tk.X, pady=(0, 25))
        
        tk.Label(section1, text="模型供应商", font=("Microsoft YaHei UI", 12, "bold"), bg=ModernStyle.BG_CARD).pack(anchor="w", pady=(0, 10))
        
        prov_b = tk.Frame(section1, bg=ModernStyle.BG_SIDEBAR, padx=20, pady=15)
        prov_b.pack(fill=tk.X)
        
        self.provider_var = tk.StringVar(value="OpenAI 兼容")
        providers = ["OpenAI 兼容", "DeepSeek", "硅基流动", "Ollama 本地", "自定义"]
        provider_combo = ttk.Combobox(prov_b, textvariable=self.provider_var, values=providers, state="readonly", width=30)
        provider_combo.pack(side=tk.LEFT)
        provider_combo.bind("<<ComboboxSelected>>", self._on_provider_change)
        
        tk.Label(prov_b, text="💡 切换供应商可自动填充常用 API 地址", font=("Microsoft YaHei UI", 9), bg=ModernStyle.BG_SIDEBAR, fg=ModernStyle.TEXT_SECONDARY).pack(side=tk.LEFT, padx=15)
        
        # ============ 2. API 配置 ============
        section2 = tk.Frame(scrollable_frame, bg=ModernStyle.BG_CARD)
        section2.pack(fill=tk.X, pady=(0, 25))
        
        header2 = tk.Frame(section2, bg=ModernStyle.BG_CARD)
        header2.pack(fill=tk.X, pady=(0, 10))
        tk.Label(header2, text="API 配置", font=("Microsoft YaHei UI", 12, "bold"), bg=ModernStyle.BG_CARD).pack(side=tk.LEFT)
        
        tk.Button(header2, text="🔗 测试连接", font=("Microsoft YaHei UI", 9), bg=ModernStyle.BG_SIDEBAR, bd=1, relief="solid", padx=10, command=self._test_connection).pack(side=tk.RIGHT)
        
        api_b = tk.Frame(section2, bg=ModernStyle.BG_SIDEBAR, padx=20, pady=20)
        api_b.pack(fill=tk.X)
        
        # API Base
        tk.Label(api_b, text="API 地址:", font=("Microsoft YaHei UI", 10), bg=ModernStyle.BG_SIDEBAR, width=10, anchor="w").grid(row=0, column=0, pady=5)
        self.setting_llm_base = tk.Entry(api_b, font=("Microsoft YaHei UI", 10), bg=ModernStyle.BG_MAIN, relief="flat", width=50)
        self.setting_llm_base.grid(row=0, column=1, sticky="we", padx=10, ipady=5)
        
        # API Key
        tk.Label(api_b, text="API 密钥:", font=("Microsoft YaHei UI", 10), bg=ModernStyle.BG_SIDEBAR, width=10, anchor="w").grid(row=1, column=0, pady=5)
        key_f = tk.Frame(api_b, bg=ModernStyle.BG_SIDEBAR)
        key_f.grid(row=1, column=1, sticky="we", padx=10)
        
        self.setting_llm_key = tk.Entry(key_f, font=("Microsoft YaHei UI", 10), bg=ModernStyle.BG_MAIN, relief="flat", show="•")
        self.setting_llm_key.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        self.show_key = tk.BooleanVar(value=False)
        tk.Checkbutton(key_f, text="显示", variable=self.show_key, command=self._toggle_key_visibility, bg=ModernStyle.BG_SIDEBAR, font=("Microsoft YaHei UI", 9)).pack(side=tk.LEFT, padx=5)
        
        # ============ 3. 模型设置 ============
        section3 = tk.Frame(scrollable_frame, bg=ModernStyle.BG_CARD)
        section3.pack(fill=tk.X, pady=(0, 25))
        
        tk.Label(section3, text="模型选择", font=("Microsoft YaHei UI", 12, "bold"), bg=ModernStyle.BG_CARD).pack(anchor="w", pady=(0, 10))
        
        model_b = tk.Frame(section3, bg=ModernStyle.BG_SIDEBAR, padx=20, pady=20)
        model_b.pack(fill=tk.X)
        
        # LLM Model
        tk.Label(model_b, text="语言模型 (LLM):", font=("Microsoft YaHei UI", 10), bg=ModernStyle.BG_SIDEBAR, width=15, anchor="w").grid(row=0, column=0, pady=10)
        self.setting_llm_model = ttk.Combobox(model_b, font=("Microsoft YaHei UI", 10), width=40, values=["gpt-4o", "gpt-4o-mini", "deepseek-chat", "deepseek-coder", "Qwen/Qwen2.5-72B-Instruct"])
        self.setting_llm_model.grid(row=0, column=1, sticky="w", padx=10)
        
        self.llm_status = tk.Label(model_b, text="● 未配置", font=("Microsoft YaHei UI", 9), bg=ModernStyle.BG_SIDEBAR, fg=ModernStyle.WARNING)
        self.llm_status.grid(row=0, column=2, padx=10)
        
        # Embedding Model
        tk.Label(model_b, text="嵌入模型 (Embed):", font=("Microsoft YaHei UI", 10), bg=ModernStyle.BG_SIDEBAR, width=15, anchor="w").grid(row=1, column=0, pady=10)
        self.setting_embed_model = ttk.Combobox(model_b, font=("Microsoft YaHei UI", 10), width=40, values=["text-embedding-3-small", "text-embedding-3-large", "BAAI/bge-m3"])
        self.setting_embed_model.grid(row=1, column=1, sticky="w", padx=10)
        
        self.use_same_api = tk.BooleanVar(value=True)
        tk.Checkbutton(model_b, text="使用同一 API", variable=self.use_same_api, command=self._toggle_embed_api, bg=ModernStyle.BG_SIDEBAR, font=("Microsoft YaHei UI", 9)).grid(row=1, column=2, padx=10)
        
        # 独立 Embedding API (默认隐藏)
        self.embed_api_frame = tk.Frame(section3, bg="#F9F9FB", padx=20, pady=15)
        
        tk.Label(self.embed_api_frame, text="独立嵌入 API 地址:", font=("Microsoft YaHei UI", 9), bg="#F9F9FB").grid(row=0, column=0, pady=5, sticky="w")
        self.setting_embed_base = tk.Entry(self.embed_api_frame, font=("Microsoft YaHei UI", 9), bg=ModernStyle.BG_MAIN, relief="flat", width=45)
        self.setting_embed_base.grid(row=0, column=1, padx=10, ipady=3)
        
        tk.Label(self.embed_api_frame, text="独立嵌入 API 密钥:", font=("Microsoft YaHei UI", 9), bg="#F9F9FB").grid(row=1, column=0, pady=5, sticky="w")
        self.setting_embed_key = tk.Entry(self.embed_api_frame, font=("Microsoft YaHei UI", 9), bg=ModernStyle.BG_MAIN, relief="flat", width=45, show="•")
        self.setting_embed_key.grid(row=1, column=1, padx=10, ipady=3)
        
        # ============ 4. 操作按钮 ============
        btn_b = tk.Frame(scrollable_frame, bg=ModernStyle.BG_CARD)
        btn_b.pack(fill=tk.X, pady=20)
        
        tk.Button(btn_b, text="保存配置", font=("Microsoft YaHei UI", 11, "bold"), bg=ModernStyle.PRIMARY, fg="white", bd=0, padx=40, pady=12, cursor="hand2", command=self._save_settings).pack(side=tk.LEFT)
        tk.Button(btn_b, text="恢复默认", font=("Microsoft YaHei UI", 10), bg=ModernStyle.BG_SIDEBAR, bd=0, padx=20, pady=12, cursor="hand2", command=self._reset_settings).pack(side=tk.LEFT, padx=15)
        
        # 加载现有设置
        self._load_settings()
    
    def _on_provider_change(self, event=None):
        """切换供应商时自动填充默认值"""
        provider = self.provider_var.get()
        
        presets = {
            "OpenAI 兼容": ("https://api.openai.com/v1", "gpt-4o-mini", "text-embedding-3-small"),
            "DeepSeek": ("https://api.deepseek.com/v1", "deepseek-chat", "text-embedding-3-small"),
            "硅基流动": ("https://api.siliconflow.cn/v1", "Qwen/Qwen2.5-72B-Instruct", "BAAI/bge-m3"),
            "Ollama 本地": ("http://localhost:11434/v1", "llama3.2", "nomic-embed-text"),
            "自定义": ("", "", ""),
        }
        
        if provider in presets:
            base, model, embed = presets[provider]
            self.setting_llm_base.delete(0, tk.END)
            self.setting_llm_base.insert(0, base)
            self.setting_llm_model.set(model)
            self.setting_embed_model.set(embed)
    
    def _toggle_key_visibility(self):
        """切换密钥显示/隐藏"""
        if self.show_key.get():
            self.setting_llm_key.config(show="")
        else:
            self.setting_llm_key.config(show="•")
    
    def _toggle_embed_api(self):
        """切换嵌入模型独立API配置显示"""
        if self.use_same_api.get():
            self.embed_api_frame.pack_forget()
        else:
            self.embed_api_frame.pack(fill=tk.X, padx=15, pady=5)
    
    def _test_connection(self):
        """测试 API 连接"""
        api_base = self.setting_llm_base.get().strip()
        api_key = self.setting_llm_key.get().strip()
        model = self.setting_llm_model.get().strip()
        
        if not api_base or not api_key:
            messagebox.showwarning("提示", "请先填写 API 地址和密钥")
            return
        
        def do_test():
            try:
                from openai import OpenAI
                client = OpenAI(base_url=api_base, api_key=api_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=5
                )
                self.root.after(0, lambda: self._update_status(True))
                self.root.after(0, lambda: messagebox.showinfo("成功", "✅ 连接成功！API 配置有效。"))
            except Exception as e:
                self.root.after(0, lambda: self._update_status(False))
                self.root.after(0, lambda: messagebox.showerror("失败", f"❌ 连接失败:\n{str(e)}"))
        
        self._run_in_thread(do_test)
    
    def _update_status(self, success: bool):
        """更新状态显示"""
        if success:
            self.llm_status.config(text="● 已连接", fg=ModernStyle.SUCCESS)
        else:
            self.llm_status.config(text="● 连接失败", fg=ModernStyle.ERROR)
    
    def _reset_settings(self):
        """重置设置"""
        if messagebox.askyesno("确认", "确定要重置所有设置吗？"):
            self.setting_llm_base.delete(0, tk.END)
            self.setting_llm_key.delete(0, tk.END)
            self.setting_llm_model.set("")
            self.setting_embed_base.delete(0, tk.END)
            self.setting_embed_key.delete(0, tk.END)
            self.setting_embed_model.set("")
            self.provider_var.set("OpenAI 兼容")
            self.llm_status.config(text="● 未配置", fg=ModernStyle.WARNING)
        
    # ==================== 功能方法 ====================
    
    def _select_file(self, target: str):
        """选择文件"""
        file_path = filedialog.askopenfilename(
            title="选择论文文件",
            filetypes=[
                ("支持的格式", "*.pdf;*.docx"),
                ("PDF 文件", "*.pdf"),
                ("Word 文档", "*.docx"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            file_name = os.path.basename(file_path)
            if target == "diagnose":
                self.diag_file_path = file_path
                self.diag_file_label.config(text=f"已选择: {file_name}")
            elif target == "optimize":
                self.opt_file_path = file_path
                self.opt_file_label.config(text=f"已选择: {file_name}")
    
    def _set_result(self, widget: scrolledtext.ScrolledText, text: str):
        """设置结果文本"""
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)
        widget.config(state=tk.DISABLED)
    
    def _run_in_thread(self, func: Callable, *args, **kwargs):
        """在后台线程运行函数"""
        def wrapper():
            try:
                func(*args, **kwargs)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", str(e)))
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
    
    def _run_diagnose(self):
        """运行诊断"""
        # 获取内容
        content = None
        file_type = None
        
        if self.diag_file_path:
            try:
                with open(self.diag_file_path, "rb") as f:
                    content = f.read()
                if self.diag_file_path.lower().endswith(".pdf"):
                    file_type = "pdf"
                elif self.diag_file_path.lower().endswith(".docx"):
                    file_type = "docx"
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败: {e}")
                return
        else:
            text = self.diag_text.get("1.0", tk.END).strip()
            if text:
                content = text
            else:
                messagebox.showwarning("提示", "请上传文件或粘贴论文内容")
                return
        
        self._set_result(self.diag_result, "正在诊断中，请稍候...")
        
        def do_diagnose():
            try:
                from agents.master import MasterAgent
                from agents.diagnostic import DiagnosticAgent
                
                agent = MasterAgent()
                report = agent.diagnose_only(content, file_type=file_type)
                
                diagnostic = DiagnosticAgent()
                formatted = diagnostic.format_report(report)
                
                # 添加评分信息
                result_text = f"""📊 综合评分: {report.overall_score:.1f}/10

{'='*50}

{formatted}
"""
                self.root.after(0, lambda: self._set_result(self.diag_result, result_text))
                
            except Exception as e:
                self.root.after(0, lambda: self._set_result(self.diag_result, f"诊断失败: {e}"))
        
        self._run_in_thread(do_diagnose)
    
    def _run_optimize(self):
        """运行优化"""
        # 获取内容
        content = None
        file_type = None
        
        if self.opt_file_path:
            try:
                with open(self.opt_file_path, "rb") as f:
                    content = f.read()
                if self.opt_file_path.lower().endswith(".pdf"):
                    file_type = "pdf"
                elif self.opt_file_path.lower().endswith(".docx"):
                    file_type = "docx"
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败: {e}")
                return
        else:
            text = self.opt_input.get("1.0", tk.END).strip()
            if text:
                content = text
            else:
                messagebox.showwarning("提示", "请上传文件或粘贴论文内容")
                return
        
        # 获取选中的部分
        sections = [k for k, v in self.opt_sections.items() if v.get()]
        if not sections:
            messagebox.showwarning("提示", "请至少选择一个要优化的部分")
            return
        
        stage = self.opt_stage.get()
        journal = self.opt_journal.get() or None
        
        self._set_result(self.opt_output, "正在优化中，请稍候...")
        
        def do_optimize():
            try:
                from agents.master import MasterAgent
                
                agent = MasterAgent()
                result = agent.process_paper(
                    content,
                    stage=stage,
                    file_type=file_type,
                    sections_to_optimize=sections,
                    target_journal=journal
                )
                
                if result.status != "success":
                    self.root.after(0, lambda: self._set_result(self.opt_output, f"优化失败: {result.message}"))
                    return
                
                # 格式化结果
                output_parts = []
                for section, opt_result in result.optimizations.items():
                    if opt_result.success:
                        output_parts.append(f"## {section.upper()}\n\n{opt_result.optimized}")
                
                if not output_parts:
                    self.root.after(0, lambda: self._set_result(self.opt_output, "未能生成任何优化结果"))
                    return
                
                result_text = "\n\n" + "="*50 + "\n\n".join(output_parts)
                self.root.after(0, lambda: self._set_result(self.opt_output, result_text))
                
            except Exception as e:
                self.root.after(0, lambda: self._set_result(self.opt_output, f"优化失败: {e}"))
        
        self._run_in_thread(do_optimize)
    
    def _run_dedup(self):
        """运行降重"""
        text = self.dedup_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("提示", "请输入文本")
            return
        
        strength = self.dedup_strength.get()
        terms_str = self.dedup_terms.get().strip()
        terms = [t.strip() for t in terms_str.split(",") if t.strip()] if terms_str else None
        
        self._set_result(self.dedup_output, "正在处理中，请稍候...")
        
        def do_dedup():
            try:
                from engines.dedup import DedupEngine
                
                engine = DedupEngine()
                result = engine.process(text, strength=int(strength), preserve_terms=terms)
                
                report = engine.get_dedup_report(result)
                
                result_text = f"""📝 降重结果

{result.processed}

{'='*50}

📊 处理报告
{report}
"""
                self.root.after(0, lambda: self._set_result(self.dedup_output, result_text))
                
            except Exception as e:
                self.root.after(0, lambda: self._set_result(self.dedup_output, f"处理失败: {e}"))
        
        self._run_in_thread(do_dedup)
    
    def _run_deai(self):
        """运行降AI"""
        text = self.dedup_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("提示", "请输入文本")
            return
        
        self._set_result(self.dedup_output, "正在处理中，请稍候...")
        
        def do_deai():
            try:
                from engines.deai import DeAIEngine
                
                engine = DeAIEngine()
                result = engine.process(text)
                
                report = engine.get_report(result)
                
                result_text = f"""🤖 降AI结果

{result.processed}

{'='*50}

📊 处理报告
{report}
"""
                self.root.after(0, lambda: self._set_result(self.dedup_output, result_text))
                
            except Exception as e:
                self.root.after(0, lambda: self._set_result(self.dedup_output, f"处理失败: {e}"))
        
        self._run_in_thread(do_deai)
    
    def _run_both_dedup(self):
        """运行降重+降AI"""
        text = self.dedup_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("提示", "请输入文本")
            return
        
        strength = self.dedup_strength.get()
        terms_str = self.dedup_terms.get().strip()
        terms = [t.strip() for t in terms_str.split(",") if t.strip()] if terms_str else None
        
        self._set_result(self.dedup_output, "正在处理中，请稍候...")
        
        def do_both():
            try:
                from engines.dedup import DedupEngine
                from engines.deai import DeAIEngine
                
                # 先降重
                dedup_engine = DedupEngine()
                dedup_result = dedup_engine.process(text, strength=int(strength), preserve_terms=terms)
                
                # 再降AI
                deai_engine = DeAIEngine()
                deai_result = deai_engine.process(dedup_result.processed)
                
                result_text = f"""⚡ 双重处理结果

{deai_result.processed}

{'='*50}

📊 降重报告
{dedup_engine.get_dedup_report(dedup_result)}

📊 降AI报告
{deai_engine.get_report(deai_result)}
"""
                self.root.after(0, lambda: self._set_result(self.dedup_output, result_text))
                
            except Exception as e:
                self.root.after(0, lambda: self._set_result(self.dedup_output, f"处理失败: {e}"))
        
        self._run_in_thread(do_both)
    
    def _run_search(self):
        """运行学术搜索"""
        query = self.search_query.get().strip()
        if not query:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return
        
        source = self.search_source.get()
        
        self._set_result(self.search_result, "正在搜索中，请稍候...")
        
        def do_search():
            try:
                if source == "Google Scholar":
                    from knowledge.search.google_scholar import search_google_scholar, format_results
                    results = search_google_scholar(query, limit=10)
                    formatted = format_results(results)
                else:
                    from knowledge.search.cnki import search_cnki, format_results
                    results = search_cnki(query, limit=10)
                    formatted = format_results(results)
                
                self.root.after(0, lambda: self._set_result(self.search_result, formatted))
                
            except Exception as e:
                self.root.after(0, lambda: self._set_result(self.search_result, f"搜索失败: {e}"))
        
        self._run_in_thread(do_search)
    
    def _run_revision(self):
        """运行退修处理"""
        comments = self.rev_comments.get("1.0", tk.END).strip()
        if not comments:
            messagebox.showwarning("提示", "请粘贴审稿意见")
            return
        
        summary = self.rev_summary.get("1.0", tk.END).strip() or None
        
        self._set_result(self.rev_output, "正在生成回应中，请稍候...")
        
        def do_revision():
            try:
                from agents.revision import RevisionAgent
                
                agent = RevisionAgent()
                result = agent.process_comments(comments, summary)
                
                formatted = agent.format_result(result)
                
                result_text = f"""{formatted}

{'='*50}

📧 回应信

{result.response_letter}
"""
                self.root.after(0, lambda: self._set_result(self.rev_output, result_text))
                
            except Exception as e:
                self.root.after(0, lambda: self._set_result(self.rev_output, f"处理失败: {e}"))
        
        self._run_in_thread(do_revision)
    
    def _load_settings(self):
        """加载设置"""
        try:
            from config.settings import settings
            self.setting_llm_base.delete(0, tk.END)
            self.setting_llm_base.insert(0, settings.llm_api_base or "")
            self.setting_llm_key.delete(0, tk.END)
            self.setting_llm_key.insert(0, settings.llm_api_key or "")
            self.setting_llm_model.set(settings.llm_model or "gpt-4o-mini")
            
            self.setting_embed_base.delete(0, tk.END)
            self.setting_embed_base.insert(0, settings.embedding_api_base or "")
            self.setting_embed_key.delete(0, tk.END)
            self.setting_embed_key.insert(0, settings.embedding_api_key or "")
            self.setting_embed_model.set(settings.embedding_model or "text-embedding-3-small")
            
            # 更新状态
            if settings.llm_api_key:
                self.llm_status.config(text="● 已配置", fg=ModernStyle.SUCCESS)
        except Exception:
            pass
    
    def _save_settings(self):
        """保存设置"""
        try:
            env_path = BASE_DIR / ".env"
            
            # 获取嵌入模型配置
            if self.use_same_api.get():
                embed_base = self.setting_llm_base.get()
                embed_key = self.setting_llm_key.get()
            else:
                embed_base = self.setting_embed_base.get()
                embed_key = self.setting_embed_key.get()
            
            lines = [
                f"# EconPaper Pro 配置",
                f"",
                f"# LLM 配置",
                f"LLM_API_BASE={self.setting_llm_base.get()}",
                f"LLM_API_KEY={self.setting_llm_key.get()}",
                f"LLM_MODEL={self.setting_llm_model.get()}",
                f"",
                f"# 嵌入模型配置",
                f"EMBEDDING_API_BASE={embed_base}",
                f"EMBEDDING_API_KEY={embed_key}",
                f"EMBEDDING_MODEL={self.setting_embed_model.get()}",
            ]
            
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            
            self.llm_status.config(text="● 已配置", fg=ModernStyle.SUCCESS)
            messagebox.showinfo("成功", "✅ 配置已保存！\n\n部分设置需要重启应用生效。")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")


def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置 DPI 感知（Windows）
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    
    app = EconPaperApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
