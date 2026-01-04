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
    """现代化样式配置"""
    
    # 颜色主题
    PRIMARY = "#667eea"
    PRIMARY_DARK = "#5a67d8"
    SECONDARY = "#764ba2"
    SUCCESS = "#48bb78"
    WARNING = "#ed8936"
    ERROR = "#f56565"
    
    # 背景色
    BG_MAIN = "#f7fafc"
    BG_CARD = "#ffffff"
    BG_SIDEBAR = "#2d3748"
    
    # 文字颜色
    TEXT_PRIMARY = "#2d3748"
    TEXT_SECONDARY = "#718096"
    TEXT_LIGHT = "#ffffff"
    
    # 边框
    BORDER = "#e2e8f0"
    
    @classmethod
    def configure_styles(cls, root):
        """配置 ttk 样式"""
        style = ttk.Style(root)
        
        # 使用原生主题作为基础
        try:
            style.theme_use('clam')
        except Exception:
            pass
        
        # 主按钮样式
        style.configure(
            "Primary.TButton",
            background=cls.PRIMARY,
            foreground=cls.TEXT_LIGHT,
            padding=(20, 10),
            font=("Microsoft YaHei UI", 10)
        )
        
        # 次要按钮
        style.configure(
            "Secondary.TButton",
            background=cls.BG_CARD,
            foreground=cls.TEXT_PRIMARY,
            padding=(15, 8),
            font=("Microsoft YaHei UI", 9)
        )
        
        # 标签
        style.configure(
            "Title.TLabel",
            background=cls.BG_MAIN,
            foreground=cls.TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 16, "bold")
        )
        
        style.configure(
            "Subtitle.TLabel",
            background=cls.BG_MAIN,
            foreground=cls.TEXT_SECONDARY,
            font=("Microsoft YaHei UI", 10)
        )
        
        # 框架
        style.configure(
            "Card.TFrame",
            background=cls.BG_CARD,
            relief="flat"
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
        """创建侧边栏"""
        sidebar = tk.Frame(parent, bg=ModernStyle.BG_SIDEBAR, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Logo 区域
        logo_frame = tk.Frame(sidebar, bg=ModernStyle.BG_SIDEBAR)
        logo_frame.pack(fill=tk.X, pady=20)
        
        logo_label = tk.Label(
            logo_frame,
            text="📚 EconPaper Pro",
            font=("Microsoft YaHei UI", 14, "bold"),
            bg=ModernStyle.BG_SIDEBAR,
            fg=ModernStyle.TEXT_LIGHT
        )
        logo_label.pack()
        
        version_label = tk.Label(
            logo_frame,
            text="v2.0.0",
            font=("Microsoft YaHei UI", 9),
            bg=ModernStyle.BG_SIDEBAR,
            fg=ModernStyle.TEXT_SECONDARY
        )
        version_label.pack()
        
        # 分隔线
        separator = tk.Frame(sidebar, bg=ModernStyle.TEXT_SECONDARY, height=1)
        separator.pack(fill=tk.X, padx=20, pady=10)
        
        # 导航按钮
        nav_items = [
            ("🔍 论文诊断", "diagnose"),
            ("⚙️ 深度优化", "optimize"),
            ("🔧 降重降AI", "dedup"),
            ("🔎 学术搜索", "search"),
            ("📝 退修助手", "revision"),
            ("⚙️ 系统设置", "settings"),
        ]
        
        for text, page_id in nav_items:
            btn = tk.Button(
                sidebar,
                text=text,
                font=("Microsoft YaHei UI", 11),
                bg=ModernStyle.BG_SIDEBAR,
                fg=ModernStyle.TEXT_LIGHT,
                activebackground=ModernStyle.PRIMARY,
                activeforeground=ModernStyle.TEXT_LIGHT,
                bd=0,
                cursor="hand2",
                anchor="w",
                padx=20,
                pady=12,
                command=lambda p=page_id: self._show_page(p)
            )
            btn.pack(fill=tk.X)
            
            # 鼠标悬停效果
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=ModernStyle.PRIMARY_DARK))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=ModernStyle.BG_SIDEBAR))
    
    def _show_page(self, page_id: str):
        """显示指定页面"""
        self.current_tab.set(page_id)
        
        # 隐藏所有页面
        for page in self.pages.values():
            page.pack_forget()
        
        # 显示选中的页面
        if page_id in self.pages:
            self.pages[page_id].pack(fill=tk.BOTH, expand=True)
    
    def _create_diagnose_page(self):
        """创建论文诊断页面"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_CARD)
        self.pages["diagnose"] = page
        
        # 标题
        title = tk.Label(
            page,
            text="🔍 论文诊断",
            font=("Microsoft YaHei UI", 18, "bold"),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY
        )
        title.pack(anchor="w", padx=20, pady=(20, 5))
        
        subtitle = tk.Label(
            page,
            text="上传论文文件或粘贴内容，获取多维度诊断报告",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 20))
        
        # 分隔容器
        content_container = tk.Frame(page, bg=ModernStyle.BG_CARD)
        content_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 左侧输入区
        input_frame = tk.Frame(content_container, bg=ModernStyle.BG_CARD)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 文件上传按钮
        upload_btn = tk.Button(
            input_frame,
            text="📁 选择论文文件 (PDF/Word)",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.PRIMARY,
            fg=ModernStyle.TEXT_LIGHT,
            activebackground=ModernStyle.PRIMARY_DARK,
            activeforeground=ModernStyle.TEXT_LIGHT,
            bd=0,
            cursor="hand2",
            padx=20,
            pady=10,
            command=lambda: self._select_file("diagnose")
        )
        upload_btn.pack(fill=tk.X, pady=(0, 10))
        
        # 文件路径显示
        self.diag_file_label = tk.Label(
            input_frame,
            text="未选择文件",
            font=("Microsoft YaHei UI", 9),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY,
            anchor="w"
        )
        self.diag_file_label.pack(fill=tk.X, pady=(0, 10))
        
        # 或者粘贴内容
        or_label = tk.Label(
            input_frame,
            text="或粘贴论文内容：",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            anchor="w"
        )
        or_label.pack(fill=tk.X, pady=(10, 5))
        
        # 文本输入框
        self.diag_text = scrolledtext.ScrolledText(
            input_frame,
            font=("Microsoft YaHei UI", 10),
            wrap=tk.WORD,
            height=15,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            bd=1
        )
        self.diag_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 诊断按钮
        diag_btn = tk.Button(
            input_frame,
            text="🔍 开始诊断",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg=ModernStyle.SUCCESS,
            fg=ModernStyle.TEXT_LIGHT,
            activebackground="#38a169",
            activeforeground=ModernStyle.TEXT_LIGHT,
            bd=0,
            cursor="hand2",
            padx=30,
            pady=12,
            command=self._run_diagnose
        )
        diag_btn.pack(pady=10)
        
        # 右侧结果区
        result_frame = tk.Frame(content_container, bg=ModernStyle.BG_CARD)
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        result_title = tk.Label(
            result_frame,
            text="诊断报告",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            anchor="w"
        )
        result_title.pack(fill=tk.X, pady=(0, 10))
        
        # 结果显示
        self.diag_result = scrolledtext.ScrolledText(
            result_frame,
            font=("Microsoft YaHei UI", 10),
            wrap=tk.WORD,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            bd=1,
            state=tk.DISABLED
        )
        self.diag_result.pack(fill=tk.BOTH, expand=True)
        
        # 保存文件路径
        self.diag_file_path = None
        
    def _create_optimize_page(self):
        """创建深度优化页面"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_CARD)
        self.pages["optimize"] = page
        
        # 标题
        title = tk.Label(
            page,
            text="⚙️ 深度优化",
            font=("Microsoft YaHei UI", 18, "bold"),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY
        )
        title.pack(anchor="w", padx=20, pady=(20, 5))
        
        subtitle = tk.Label(
            page,
            text="选择优化阶段和目标期刊，对论文各部分进行智能优化",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 20))
        
        # 主容器
        main_frame = tk.Frame(page, bg=ModernStyle.BG_CARD)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # 左侧配置区
        config_frame = tk.Frame(main_frame, bg=ModernStyle.BG_CARD)
        config_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # 优化阶段选择
        stage_label = tk.Label(
            config_frame,
            text="优化阶段：",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            anchor="w"
        )
        stage_label.pack(fill=tk.X, pady=(0, 5))
        
        self.opt_stage = tk.StringVar(value="submission")
        stages = [
            ("初稿重构", "draft"),
            ("投稿优化", "submission"),
            ("退修回应", "revision"),
            ("终稿定稿", "final")
        ]
        
        for text, value in stages:
            rb = tk.Radiobutton(
                config_frame,
                text=text,
                variable=self.opt_stage,
                value=value,
                font=("Microsoft YaHei UI", 9),
                bg=ModernStyle.BG_CARD,
                fg=ModernStyle.TEXT_PRIMARY,
                selectcolor=ModernStyle.BG_MAIN,
                activebackground=ModernStyle.BG_CARD,
                cursor="hand2"
            )
            rb.pack(anchor="w")
        
        # 目标期刊
        journal_label = tk.Label(
            config_frame,
            text="目标期刊：",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            anchor="w"
        )
        journal_label.pack(fill=tk.X, pady=(20, 5))
        
        self.opt_journal = tk.StringVar(value="")
        journals = ["", "经济研究", "管理世界", "金融研究", "中国工业经济", "会计研究", "其他"]
        
        journal_combo = ttk.Combobox(
            config_frame,
            textvariable=self.opt_journal,
            values=journals,
            state="readonly",
            font=("Microsoft YaHei UI", 9),
            width=20
        )
        journal_combo.pack(fill=tk.X)
        
        # 优化部分选择
        section_label = tk.Label(
            config_frame,
            text="优化部分：",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            anchor="w"
        )
        section_label.pack(fill=tk.X, pady=(20, 5))
        
        sections = [
            ("标题", "title"),
            ("摘要", "abstract"),
            ("引言", "introduction"),
            ("文献综述", "literature"),
            ("理论假设", "theory"),
            ("研究方法", "methodology"),
            ("实证结果", "results"),
            ("结论", "conclusion")
        ]
        
        self.opt_sections = {}
        for text, value in sections:
            var = tk.BooleanVar(value=value in ["abstract", "introduction"])
            self.opt_sections[value] = var
            cb = tk.Checkbutton(
                config_frame,
                text=text,
                variable=var,
                font=("Microsoft YaHei UI", 9),
                bg=ModernStyle.BG_CARD,
                fg=ModernStyle.TEXT_PRIMARY,
                selectcolor=ModernStyle.BG_MAIN,
                activebackground=ModernStyle.BG_CARD,
                cursor="hand2"
            )
            cb.pack(anchor="w")
        
        # 文件上传
        upload_btn = tk.Button(
            config_frame,
            text="📁 选择论文文件",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.PRIMARY,
            fg=ModernStyle.TEXT_LIGHT,
            activebackground=ModernStyle.PRIMARY_DARK,
            bd=0,
            cursor="hand2",
            padx=15,
            pady=8,
            command=lambda: self._select_file("optimize")
        )
        upload_btn.pack(fill=tk.X, pady=(20, 5))
        
        self.opt_file_label = tk.Label(
            config_frame,
            text="未选择文件",
            font=("Microsoft YaHei UI", 9),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY,
            anchor="w",
            wraplength=150
        )
        self.opt_file_label.pack(fill=tk.X)
        
        # 开始优化按钮
        opt_btn = tk.Button(
            config_frame,
            text="⚙️ 开始优化",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg=ModernStyle.SUCCESS,
            fg=ModernStyle.TEXT_LIGHT,
            activebackground="#38a169",
            bd=0,
            cursor="hand2",
            padx=20,
            pady=10,
            command=self._run_optimize
        )
        opt_btn.pack(fill=tk.X, pady=(20, 0))
        
        # 右侧输入/输出区
        io_frame = tk.Frame(main_frame, bg=ModernStyle.BG_CARD)
        io_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 输入区
        input_label = tk.Label(
            io_frame,
            text="论文内容（或直接粘贴）：",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            anchor="w"
        )
        input_label.pack(fill=tk.X, pady=(0, 5))
        
        self.opt_input = scrolledtext.ScrolledText(
            io_frame,
            font=("Microsoft YaHei UI", 10),
            wrap=tk.WORD,
            height=10,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            bd=1
        )
        self.opt_input.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 输出区
        output_label = tk.Label(
            io_frame,
            text="优化结果：",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            anchor="w"
        )
        output_label.pack(fill=tk.X, pady=(0, 5))
        
        self.opt_output = scrolledtext.ScrolledText(
            io_frame,
            font=("Microsoft YaHei UI", 10),
            wrap=tk.WORD,
            height=10,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            bd=1,
            state=tk.DISABLED
        )
        self.opt_output.pack(fill=tk.BOTH, expand=True)
        
        self.opt_file_path = None
        
    def _create_dedup_page(self):
        """创建降重降AI页面"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_CARD)
        self.pages["dedup"] = page
        
        # 标题
        title = tk.Label(
            page,
            text="🔧 降重降AI",
            font=("Microsoft YaHei UI", 18, "bold"),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY
        )
        title.pack(anchor="w", padx=20, pady=(20, 5))
        
        subtitle = tk.Label(
            page,
            text="输入文本，进行智能降重或降AI处理",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 20))
        
        # 主容器
        main_frame = tk.Frame(page, bg=ModernStyle.BG_CARD)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # 配置区
        config_frame = tk.Frame(main_frame, bg=ModernStyle.BG_CARD)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 降重强度
        strength_label = tk.Label(
            config_frame,
            text="降重强度：",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY
        )
        strength_label.pack(side=tk.LEFT)
        
        self.dedup_strength = tk.Scale(
            config_frame,
            from_=1,
            to=5,
            orient=tk.HORIZONTAL,
            length=200,
            bg=ModernStyle.BG_CARD,
            highlightthickness=0,
            font=("Microsoft YaHei UI", 9)
        )
        self.dedup_strength.set(3)
        self.dedup_strength.pack(side=tk.LEFT, padx=10)
        
        # 保留术语
        terms_label = tk.Label(
            config_frame,
            text="保留术语（逗号分隔）：",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY
        )
        terms_label.pack(side=tk.LEFT, padx=(20, 0))
        
        self.dedup_terms = tk.Entry(
            config_frame,
            font=("Microsoft YaHei UI", 10),
            width=30,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            bd=1
        )
        self.dedup_terms.pack(side=tk.LEFT, padx=10)
        
        # 输入区
        input_label = tk.Label(
            main_frame,
            text="输入文本：",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            anchor="w"
        )
        input_label.pack(fill=tk.X, pady=(10, 5))
        
        self.dedup_input = scrolledtext.ScrolledText(
            main_frame,
            font=("Microsoft YaHei UI", 10),
            wrap=tk.WORD,
            height=8,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            bd=1
        )
        self.dedup_input.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 按钮区
        btn_frame = tk.Frame(main_frame, bg=ModernStyle.BG_CARD)
        btn_frame.pack(fill=tk.X, pady=10)
        
        dedup_btn = tk.Button(
            btn_frame,
            text="📉 降重",
            font=("Microsoft YaHei UI", 11),
            bg=ModernStyle.PRIMARY,
            fg=ModernStyle.TEXT_LIGHT,
            activebackground=ModernStyle.PRIMARY_DARK,
            bd=0,
            cursor="hand2",
            padx=25,
            pady=10,
            command=self._run_dedup
        )
        dedup_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        deai_btn = tk.Button(
            btn_frame,
            text="🤖 降AI",
            font=("Microsoft YaHei UI", 11),
            bg=ModernStyle.SECONDARY,
            fg=ModernStyle.TEXT_LIGHT,
            activebackground="#6b4190",
            bd=0,
            cursor="hand2",
            padx=25,
            pady=10,
            command=self._run_deai
        )
        deai_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        both_btn = tk.Button(
            btn_frame,
            text="⚡ 双重处理",
            font=("Microsoft YaHei UI", 11),
            bg=ModernStyle.SUCCESS,
            fg=ModernStyle.TEXT_LIGHT,
            activebackground="#38a169",
            bd=0,
            cursor="hand2",
            padx=25,
            pady=10,
            command=self._run_both_dedup
        )
        both_btn.pack(side=tk.LEFT)
        
        # 输出区
        output_label = tk.Label(
            main_frame,
            text="处理结果：",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            anchor="w"
        )
        output_label.pack(fill=tk.X, pady=(10, 5))
        
        self.dedup_output = scrolledtext.ScrolledText(
            main_frame,
            font=("Microsoft YaHei UI", 10),
            wrap=tk.WORD,
            height=8,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            bd=1,
            state=tk.DISABLED
        )
        self.dedup_output.pack(fill=tk.BOTH, expand=True)
        
    def _create_search_page(self):
        """创建学术搜索页面"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_CARD)
        self.pages["search"] = page
        
        # 标题
        title = tk.Label(
            page,
            text="🔎 学术搜索",
            font=("Microsoft YaHei UI", 18, "bold"),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY
        )
        title.pack(anchor="w", padx=20, pady=(20, 5))
        
        subtitle = tk.Label(
            page,
            text="搜索 Google Scholar 或知网文献",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 20))
        
        # 搜索区
        search_frame = tk.Frame(page, bg=ModernStyle.BG_CARD)
        search_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # 搜索框
        self.search_query = tk.Entry(
            search_frame,
            font=("Microsoft YaHei UI", 12),
            width=40,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            bd=1
        )
        self.search_query.pack(side=tk.LEFT, padx=(0, 10), ipady=8)
        self.search_query.insert(0, "数字经济 企业创新")
        
        # 来源选择
        self.search_source = tk.StringVar(value="Google Scholar")
        source_combo = ttk.Combobox(
            search_frame,
            textvariable=self.search_source,
            values=["Google Scholar", "知网 CNKI"],
            state="readonly",
            font=("Microsoft YaHei UI", 10),
            width=15
        )
        source_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # 搜索按钮
        search_btn = tk.Button(
            search_frame,
            text="🔎 搜索",
            font=("Microsoft YaHei UI", 11),
            bg=ModernStyle.PRIMARY,
            fg=ModernStyle.TEXT_LIGHT,
            activebackground=ModernStyle.PRIMARY_DARK,
            bd=0,
            cursor="hand2",
            padx=20,
            pady=8,
            command=self._run_search
        )
        search_btn.pack(side=tk.LEFT)
        
        # 结果区
        result_label = tk.Label(
            page,
            text="搜索结果：",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            anchor="w"
        )
        result_label.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        self.search_result = scrolledtext.ScrolledText(
            page,
            font=("Microsoft YaHei UI", 10),
            wrap=tk.WORD,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            bd=1,
            state=tk.DISABLED
        )
        self.search_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
    def _create_revision_page(self):
        """创建退修助手页面"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_CARD)
        self.pages["revision"] = page
        
        # 标题
        title = tk.Label(
            page,
            text="📝 退修助手",
            font=("Microsoft YaHei UI", 18, "bold"),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY
        )
        title.pack(anchor="w", padx=20, pady=(20, 5))
        
        subtitle = tk.Label(
            page,
            text="粘贴审稿意见，生成回应策略和回应信",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 20))
        
        # 主容器
        main_frame = tk.Frame(page, bg=ModernStyle.BG_CARD)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # 左侧输入
        input_frame = tk.Frame(main_frame, bg=ModernStyle.BG_CARD)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        comments_label = tk.Label(
            input_frame,
            text="审稿意见：",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            anchor="w"
        )
        comments_label.pack(fill=tk.X, pady=(0, 5))
        
        self.rev_comments = scrolledtext.ScrolledText(
            input_frame,
            font=("Microsoft YaHei UI", 10),
            wrap=tk.WORD,
            height=12,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            bd=1
        )
        self.rev_comments.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        summary_label = tk.Label(
            input_frame,
            text="论文摘要（可选）：",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            anchor="w"
        )
        summary_label.pack(fill=tk.X, pady=(0, 5))
        
        self.rev_summary = scrolledtext.ScrolledText(
            input_frame,
            font=("Microsoft YaHei UI", 10),
            wrap=tk.WORD,
            height=5,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            bd=1
        )
        self.rev_summary.pack(fill=tk.BOTH, pady=(0, 10))
        
        rev_btn = tk.Button(
            input_frame,
            text="📝 生成回应",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg=ModernStyle.SUCCESS,
            fg=ModernStyle.TEXT_LIGHT,
            activebackground="#38a169",
            bd=0,
            cursor="hand2",
            padx=25,
            pady=10,
            command=self._run_revision
        )
        rev_btn.pack()
        
        # 右侧输出
        output_frame = tk.Frame(main_frame, bg=ModernStyle.BG_CARD)
        output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        output_label = tk.Label(
            output_frame,
            text="回应结果：",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            anchor="w"
        )
        output_label.pack(fill=tk.X, pady=(0, 5))
        
        self.rev_output = scrolledtext.ScrolledText(
            output_frame,
            font=("Microsoft YaHei UI", 10),
            wrap=tk.WORD,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            bd=1,
            state=tk.DISABLED
        )
        self.rev_output.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
    def _create_settings_page(self):
        """创建设置页面"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_CARD)
        self.pages["settings"] = page
        
        # 标题
        title = tk.Label(
            page,
            text="⚙️ 系统设置",
            font=("Microsoft YaHei UI", 18, "bold"),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY
        )
        title.pack(anchor="w", padx=20, pady=(20, 5))
        
        subtitle = tk.Label(
            page,
            text="配置 API 密钥和系统参数",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 20))
        
        # 设置容器
        settings_frame = tk.Frame(page, bg=ModernStyle.BG_CARD)
        settings_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # API 配置
        api_label = tk.Label(
            settings_frame,
            text="🔑 API 配置",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            anchor="w"
        )
        api_label.pack(fill=tk.X, pady=(0, 10))
        
        # LLM API
        llm_frame = tk.Frame(settings_frame, bg=ModernStyle.BG_CARD)
        llm_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            llm_frame,
            text="LLM API Base:",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            width=15,
            anchor="e"
        ).pack(side=tk.LEFT)
        
        self.setting_llm_base = tk.Entry(
            llm_frame,
            font=("Microsoft YaHei UI", 10),
            width=50,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            bd=1
        )
        self.setting_llm_base.pack(side=tk.LEFT, padx=10, ipady=5)
        
        # LLM API Key
        key_frame = tk.Frame(settings_frame, bg=ModernStyle.BG_CARD)
        key_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            key_frame,
            text="LLM API Key:",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            width=15,
            anchor="e"
        ).pack(side=tk.LEFT)
        
        self.setting_llm_key = tk.Entry(
            key_frame,
            font=("Microsoft YaHei UI", 10),
            width=50,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            bd=1,
            show="*"
        )
        self.setting_llm_key.pack(side=tk.LEFT, padx=10, ipady=5)
        
        # LLM Model
        model_frame = tk.Frame(settings_frame, bg=ModernStyle.BG_CARD)
        model_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            model_frame,
            text="LLM Model:",
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            width=15,
            anchor="e"
        ).pack(side=tk.LEFT)
        
        self.setting_llm_model = tk.Entry(
            model_frame,
            font=("Microsoft YaHei UI", 10),
            width=50,
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            bd=1
        )
        self.setting_llm_model.pack(side=tk.LEFT, padx=10, ipady=5)
        
        # 保存按钮
        save_btn = tk.Button(
            settings_frame,
            text="💾 保存设置",
            font=("Microsoft YaHei UI", 11),
            bg=ModernStyle.SUCCESS,
            fg=ModernStyle.TEXT_LIGHT,
            activebackground="#38a169",
            bd=0,
            cursor="hand2",
            padx=25,
            pady=10,
            command=self._save_settings
        )
        save_btn.pack(pady=20)
        
        # 使用说明
        help_text = """
📚 使用说明

1. 论文诊断：上传 PDF/Word 文件或粘贴文本，获取多维度诊断报告
2. 深度优化：选择优化阶段和目标期刊，对论文各部分进行优化
3. 降重降AI：输入文本，选择处理方式，获取改写后的内容
4. 学术搜索：搜索 Google Scholar 或知网文献
5. 退修助手：粘贴审稿意见，生成回应策略和回应信

⚠️ 注意事项
- 所有论文内容仅在本地处理，通过配置的 API 进行 LLM 调用
- 长文档会自动分段处理
- 建议配置 API 密钥后使用完整功能
        """
        
        help_label = tk.Label(
            page,
            text=help_text,
            font=("Microsoft YaHei UI", 10),
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY,
            justify=tk.LEFT,
            anchor="nw"
        )
        help_label.pack(fill=tk.X, padx=20, pady=20)
        
        # 加载现有设置
        self._load_settings()
        
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
                result = engine.process(text, strength=strength, preserve_terms=terms)
                
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
                dedup_result = dedup_engine.process(text, strength=strength, preserve_terms=terms)
                
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
            self.setting_llm_base.insert(0, settings.llm_api_base or "")
            self.setting_llm_key.insert(0, settings.llm_api_key or "")
            self.setting_llm_model.insert(0, settings.llm_model or "")
        except Exception:
            pass
    
    def _save_settings(self):
        """保存设置"""
        try:
            env_path = BASE_DIR / ".env"
            
            lines = []
            lines.append(f"LLM_API_BASE={self.setting_llm_base.get()}")
            lines.append(f"LLM_API_KEY={self.setting_llm_key.get()}")
            lines.append(f"LLM_MODEL={self.setting_llm_model.get()}")
            
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            
            messagebox.showinfo("成功", "设置已保存！请重启应用生效。")
            
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
