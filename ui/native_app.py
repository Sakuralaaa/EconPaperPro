# -*- coding: utf-8 -*-
"""
EconPaper Pro - 原生 Tkinter GUI 应用 (优化版)
- 修复UI卡顿问题
- 现代化界面设计
- 添加进度指示器
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime
import queue

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
    """现代简约风格配置 - 优化版"""
    
    # 主色调 (更柔和的蓝色系)
    PRIMARY = "#2563EB"        # 品牌蓝
    PRIMARY_DARK = "#1D4ED8"   # 深蓝色
    PRIMARY_LIGHT = "#DBEAFE"  # 浅蓝背景
    PRIMARY_HOVER = "#3B82F6"  # 悬停蓝
    
    # 功能色
    SUCCESS = "#10B981"        # 成功绿
    WARNING = "#F59E0B"        # 警告橙
    ERROR = "#EF4444"          # 错误红
    INFO = "#6366F1"           # 信息紫
    
    # 中性色
    BG_MAIN = "#FFFFFF"        # 主背景
    BG_SECONDARY = "#F8FAFC"   # 次级背景
    BG_SIDEBAR = "#F1F5F9"     # 侧边栏
    BG_CARD = "#FFFFFF"        # 卡片背景
    BG_HOVER = "#E2E8F0"       # 悬停色
    BG_INPUT = "#F8FAFC"       # 输入框背景
    
    # 文字颜色
    TEXT_PRIMARY = "#0F172A"   # 主要文字
    TEXT_SECONDARY = "#64748B" # 次要文字
    TEXT_MUTED = "#94A3B8"     # 弱化文字
    TEXT_LIGHT = "#FFFFFF"     # 亮色文字
    
    # 边框
    BORDER = "#E2E8F0"         # 默认边框
    BORDER_FOCUS = "#2563EB"   # 聚焦边框
    
    # 字体配置
    FONT_FAMILY = "Microsoft YaHei UI"
    FONT_SIZE_XL = 18
    FONT_SIZE_LG = 14
    FONT_SIZE_MD = 11
    FONT_SIZE_SM = 10
    FONT_SIZE_XS = 9
    
    # 间距
    PADDING_XL = 30
    PADDING_LG = 20
    PADDING_MD = 15
    PADDING_SM = 10
    PADDING_XS = 5
    
    # 圆角 (Tkinter 不直接支持，但可用于Canvas绘制)
    RADIUS_SM = 4
    RADIUS_MD = 8
    RADIUS_LG = 12
    
    @classmethod
    def configure_styles(cls, root):
        """配置 ttk 样式"""
        style = ttk.Style(root)
        
        try:
            style.theme_use('clam')
        except Exception:
            pass
        
        # 全局配置
        style.configure(".", 
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_SM),
            background=cls.BG_MAIN
        )
        
        # 主按钮
        style.configure("Primary.TButton",
            background=cls.PRIMARY,
            foreground=cls.TEXT_LIGHT,
            padding=(20, 10),
            borderwidth=0,
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_SM, "bold")
        )
        style.map("Primary.TButton",
            background=[("active", cls.PRIMARY_DARK), ("pressed", cls.PRIMARY_DARK)]
        )
        
        # 次级按钮
        style.configure("Secondary.TButton",
            background=cls.BG_SECONDARY,
            foreground=cls.TEXT_PRIMARY,
            padding=(15, 8),
            borderwidth=1
        )
        
        # 进度条 - 现代风格
        style.configure("Modern.Horizontal.TProgressbar",
            troughcolor=cls.BG_SECONDARY,
            background=cls.PRIMARY,
            lightcolor=cls.PRIMARY,
            darkcolor=cls.PRIMARY,
            borderwidth=0,
            thickness=6
        )
        
        # Combobox
        style.configure("TCombobox",
            fieldbackground=cls.BG_INPUT,
            background=cls.BG_MAIN,
            bordercolor=cls.BORDER,
            arrowcolor=cls.TEXT_SECONDARY,
            padding=5
        )
        style.map("TCombobox",
            fieldbackground=[("readonly", cls.BG_INPUT)],
            selectbackground=[("readonly", cls.PRIMARY_LIGHT)]
        )
        
        # Entry
        style.configure("TEntry",
            fieldbackground=cls.BG_INPUT,
            bordercolor=cls.BORDER,
            padding=8
        )
        
        # Frame
        style.configure("Card.TFrame",
            background=cls.BG_CARD,
            relief="flat"
        )
        
        style.configure("Sidebar.TFrame",
            background=cls.BG_SIDEBAR
        )
        
        return style


class ProgressIndicator:
    """现代进度指示器组件"""
    
    def __init__(self, parent, text="处理中..."):
        self.parent = parent
        self.frame = tk.Frame(parent, bg=ModernStyle.BG_MAIN)
        self.is_active = False
        self._animation_id = None
        
        # 创建进度条容器
        self.container = tk.Frame(self.frame, bg=ModernStyle.BG_MAIN, pady=10)
        self.container.pack(fill=tk.X, padx=20)
        
        # 状态文字
        self.label = tk.Label(
            self.container,
            text=text,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_SECONDARY
        )
        self.label.pack(anchor="w", pady=(0, 5))
        
        # 进度条
        self.progress = ttk.Progressbar(
            self.container,
            style="Modern.Horizontal.TProgressbar",
            mode="indeterminate",
            length=300
        )
        self.progress.pack(fill=tk.X)
        
    def start(self, text=None):
        """开始动画"""
        if text:
            self.label.config(text=text)
        self.is_active = True
        children = self.parent.winfo_children()
        if children:
            self.frame.pack(fill=tk.X, before=children[0])
        else:
            self.frame.pack(fill=tk.X)
        self.progress.start(15)  # 更流畅的动画
        
    def stop(self):
        """停止动画"""
        self.is_active = False
        self.progress.stop()
        self.frame.pack_forget()
        
    def update_text(self, text):
        """更新状态文字"""
        self.label.config(text=text)


class ModernButton(tk.Canvas):
    """现代圆角按钮"""
    
    def __init__(self, parent, text, command=None, width=120, height=36, 
                 bg_color=None, hover_color=None, text_color=None, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg=parent.cget("bg"), **kwargs)
        
        self.command = command
        self.text = text
        self.width = width
        self.height = height
        self.bg_color = bg_color or ModernStyle.PRIMARY
        self.hover_color = hover_color or ModernStyle.PRIMARY_HOVER
        self.text_color = text_color or ModernStyle.TEXT_LIGHT
        self._current_bg = self.bg_color
        
        self._draw_button()
        
        # 绑定事件
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        
    def _draw_button(self):
        """绘制圆角按钮"""
        self.delete("all")
        r = 8  # 圆角半径
        
        # 绘制圆角矩形
        self.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill=self._current_bg, outline="")
        self.create_arc(self.width-r*2, 0, self.width, r*2, start=0, extent=90, fill=self._current_bg, outline="")
        self.create_arc(0, self.height-r*2, r*2, self.height, start=180, extent=90, fill=self._current_bg, outline="")
        self.create_arc(self.width-r*2, self.height-r*2, self.width, self.height, start=270, extent=90, fill=self._current_bg, outline="")
        
        self.create_rectangle(r, 0, self.width-r, self.height, fill=self._current_bg, outline="")
        self.create_rectangle(0, r, self.width, self.height-r, fill=self._current_bg, outline="")
        
        # 绘制文字
        self.create_text(
            self.width/2, self.height/2,
            text=self.text,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            fill=self.text_color
        )
        
    def _on_enter(self, event):
        self._current_bg = self.hover_color
        self._draw_button()
        self.config(cursor="hand2")
        
    def _on_leave(self, event):
        self._current_bg = self.bg_color
        self._draw_button()
        
    def _on_click(self, event):
        self._current_bg = ModernStyle.PRIMARY_DARK
        self._draw_button()
        
    def _on_release(self, event):
        self._current_bg = self.hover_color
        self._draw_button()
        if self.command:
            self.command()


class EconPaperApp:
    """EconPaper Pro 主应用 - 优化版"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("📚 EconPaper Pro - 经管论文智能优化")
        self.root.geometry("1280x800")
        self.root.minsize(1000, 650)
        
        # 设置图标
        try:
            icon_path = BASE_DIR / "assets" / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass
        
        # 配置样式
        self.style = ModernStyle.configure_styles(root)
        self.root.configure(bg=ModernStyle.BG_MAIN)
        
        # 任务队列（用于线程安全的UI更新）
        self.update_queue = queue.Queue()
        
        # 当前选中的标签页
        self.current_tab = tk.StringVar(value="diagnose")
        
        # 状态变量
        self.is_processing = False
        
        # 创建主布局
        self._create_layout()
        
        # 启动UI更新循环
        self._process_queue()
        
    def _process_queue(self):
        """处理队列中的UI更新任务"""
        try:
            while True:
                task = self.update_queue.get_nowait()
                if callable(task):
                    task()
        except queue.Empty:
            pass
        finally:
            # 每50ms检查一次队列，更流畅
            self.root.after(50, self._process_queue)
    
    def _safe_update(self, func):
        """线程安全的UI更新"""
        self.update_queue.put(func)
        
    def _create_layout(self):
        """创建主布局"""
        # 主容器
        main_container = tk.Frame(self.root, bg=ModernStyle.BG_MAIN)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 左侧导航栏
        self._create_sidebar(main_container)
        
        # 右侧内容区
        self.content_frame = tk.Frame(main_container, bg=ModernStyle.BG_MAIN)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建各个功能页面
        self.pages = {}
        self.progress_indicators = {}
        
        self._create_diagnose_page()
        self._create_optimize_page()
        self._create_dedup_page()
        self._create_search_page()
        self._create_revision_page()
        self._create_settings_page()
        
        # 默认显示诊断页面
        self._show_page("diagnose")
        
    def _create_sidebar(self, parent):
        """创建侧边栏 - 优化版"""
        sidebar = tk.Frame(parent, bg=ModernStyle.BG_SIDEBAR, width=240)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # 右侧分隔线
        separator = tk.Frame(sidebar, bg=ModernStyle.BORDER, width=1)
        separator.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Logo 区域
        logo_frame = tk.Frame(sidebar, bg=ModernStyle.BG_SIDEBAR)
        logo_frame.pack(fill=tk.X, pady=(35, 25), padx=25)
        
        # Logo图标 + 标题
        title_container = tk.Frame(logo_frame, bg=ModernStyle.BG_SIDEBAR)
        title_container.pack(anchor="w")
        
        tk.Label(
            title_container,
            text="📚",
            font=(ModernStyle.FONT_FAMILY, 24),
            bg=ModernStyle.BG_SIDEBAR
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        title_text = tk.Frame(title_container, bg=ModernStyle.BG_SIDEBAR)
        title_text.pack(side=tk.LEFT)
        
        tk.Label(
            title_text,
            text="EconPaper",
            font=(ModernStyle.FONT_FAMILY, 16, "bold"),
            bg=ModernStyle.BG_SIDEBAR,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            title_text,
            text="Pro",
            font=(ModernStyle.FONT_FAMILY, 16),
            bg=ModernStyle.BG_SIDEBAR,
            fg=ModernStyle.PRIMARY
        ).pack(anchor="w")
        
        # 副标题
        tk.Label(
            logo_frame,
            text="经管学术论文智能助手",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SIDEBAR,
            fg=ModernStyle.TEXT_MUTED
        ).pack(anchor="w", pady=(8, 0))
        
        # 分隔线
        sep = tk.Frame(sidebar, bg=ModernStyle.BORDER, height=1)
        sep.pack(fill=tk.X, padx=20, pady=10)
        
        # 导航菜单
        nav_frame = tk.Frame(sidebar, bg=ModernStyle.BG_SIDEBAR)
        nav_frame.pack(fill=tk.X, padx=12)
        
        self.nav_buttons = {}
        nav_items = [
            ("diagnose", "🔍", "论文诊断", "多维度分析评估"),
            ("optimize", "⚙️", "深度优化", "智能优化改写"),
            ("dedup", "🔧", "降重降AI", "降低重复率"),
            ("search", "🔎", "学术搜索", "文献检索"),
            ("revision", "📝", "退修助手", "回应审稿意见"),
        ]
        
        for page_id, icon, title, desc in nav_items:
            btn_frame = tk.Frame(nav_frame, bg=ModernStyle.BG_SIDEBAR, cursor="hand2")
            btn_frame.pack(fill=tk.X, pady=2)
            
            btn_inner = tk.Frame(btn_frame, bg=ModernStyle.BG_SIDEBAR, padx=12, pady=10)
            btn_inner.pack(fill=tk.X)
            
            # 图标
            tk.Label(
                btn_inner,
                text=icon,
                font=(ModernStyle.FONT_FAMILY, 14),
                bg=ModernStyle.BG_SIDEBAR
            ).pack(side=tk.LEFT)
            
            # 文字容器
            text_frame = tk.Frame(btn_inner, bg=ModernStyle.BG_SIDEBAR)
            text_frame.pack(side=tk.LEFT, padx=10)
            
            title_label = tk.Label(
                text_frame,
                text=title,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
                bg=ModernStyle.BG_SIDEBAR,
                fg=ModernStyle.TEXT_PRIMARY
            )
            title_label.pack(anchor="w")
            
            desc_label = tk.Label(
                text_frame,
                text=desc,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
                bg=ModernStyle.BG_SIDEBAR,
                fg=ModernStyle.TEXT_MUTED
            )
            desc_label.pack(anchor="w")
            
            self.nav_buttons[page_id] = {
                "frame": btn_frame,
                "inner": btn_inner,
                "title": title_label,
                "desc": desc_label
            }
            
            # 绑定点击事件
            for widget in [btn_frame, btn_inner, title_label, desc_label]:
                widget.bind("<Button-1>", lambda e, p=page_id: self._show_page(p))
                widget.bind("<Enter>", lambda e, p=page_id: self._on_nav_hover(p, True))
                widget.bind("<Leave>", lambda e, p=page_id: self._on_nav_hover(p, False))
        
        # 底部设置按钮
        settings_frame = tk.Frame(sidebar, bg=ModernStyle.BG_SIDEBAR)
        settings_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=12, pady=20)
        
        sep2 = tk.Frame(settings_frame, bg=ModernStyle.BORDER, height=1)
        sep2.pack(fill=tk.X, pady=(0, 15))
        
        settings_btn = tk.Frame(settings_frame, bg=ModernStyle.BG_SIDEBAR, cursor="hand2")
        settings_btn.pack(fill=tk.X)
        
        settings_inner = tk.Frame(settings_btn, bg=ModernStyle.BG_SIDEBAR, padx=12, pady=10)
        settings_inner.pack(fill=tk.X)
        
        settings_icon = tk.Label(
            settings_inner,
            text="⚙️",
            font=(ModernStyle.FONT_FAMILY, 14),
            bg=ModernStyle.BG_SIDEBAR,
            cursor="hand2"
        )
        settings_icon.pack(side=tk.LEFT)
        
        settings_text = tk.Label(
            settings_inner,
            text="系统设置",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SIDEBAR,
            fg=ModernStyle.TEXT_PRIMARY,
            cursor="hand2"
        )
        settings_text.pack(side=tk.LEFT, padx=10)
        
        self.nav_buttons["settings"] = {
            "frame": settings_btn,
            "inner": settings_inner,
            "title": settings_text,
            "desc": None
        }
        
        # 绑定所有相关控件的点击事件
        def on_settings_click(e):
            self._show_page("settings")
        
        settings_btn.bind("<Button-1>", on_settings_click)
        settings_inner.bind("<Button-1>", on_settings_click)
        settings_icon.bind("<Button-1>", on_settings_click)
        settings_text.bind("<Button-1>", on_settings_click)

    def _on_nav_hover(self, page_id, is_enter):
        """导航悬停效果"""
        if page_id not in self.nav_buttons:
            return
            
        btn = self.nav_buttons[page_id]
        if self.current_tab.get() == page_id:
            return
            
        bg_color = ModernStyle.BG_HOVER if is_enter else ModernStyle.BG_SIDEBAR
        btn["frame"].config(bg=bg_color)
        btn["inner"].config(bg=bg_color)
        btn["title"].config(bg=bg_color)
        if btn["desc"]:
            btn["desc"].config(bg=bg_color)

    def _update_nav_style(self):
        """更新导航栏选中样式"""
        current = self.current_tab.get()
        for page_id, btn in self.nav_buttons.items():
            if page_id == current:
                bg_color = ModernStyle.PRIMARY_LIGHT
                btn["frame"].config(bg=bg_color)
                btn["inner"].config(bg=bg_color)
                btn["title"].config(bg=bg_color, fg=ModernStyle.PRIMARY, font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"))
                if btn["desc"]:
                    btn["desc"].config(bg=bg_color, fg=ModernStyle.PRIMARY)
            else:
                bg_color = ModernStyle.BG_SIDEBAR
                btn["frame"].config(bg=bg_color)
                btn["inner"].config(bg=bg_color)
                btn["title"].config(bg=bg_color, fg=ModernStyle.TEXT_PRIMARY, font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM))
                if btn["desc"]:
                    btn["desc"].config(bg=bg_color, fg=ModernStyle.TEXT_MUTED)
    
    def _show_page(self, page_id: str):
        """显示指定页面"""
        self.current_tab.set(page_id)
        self._update_nav_style()
        
        for page in self.pages.values():
            page.pack_forget()
        
        if page_id in self.pages:
            self.pages[page_id].pack(fill=tk.BOTH, expand=True)
    
    def _create_page_header(self, parent, title, subtitle):
        """创建页面标题区域"""
        header = tk.Frame(parent, bg=ModernStyle.BG_MAIN)
        header.pack(fill=tk.X, padx=ModernStyle.PADDING_XL, pady=(ModernStyle.PADDING_XL, ModernStyle.PADDING_LG))
        
        tk.Label(
            header,
            text=title,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XL, "bold"),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            header,
            text=subtitle,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_SECONDARY
        ).pack(anchor="w", pady=(5, 0))
        
        return header
    
    def _create_text_input(self, parent, height=15):
        """创建优化的文本输入框"""
        container = tk.Frame(parent, bg=ModernStyle.BORDER, padx=1, pady=1)
        
        text = scrolledtext.ScrolledText(
            container,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            wrap=tk.WORD,
            bg=ModernStyle.BG_INPUT,
            fg=ModernStyle.TEXT_PRIMARY,
            relief="flat",
            padx=12,
            pady=12,
            height=height,
            insertbackground=ModernStyle.PRIMARY,
            selectbackground=ModernStyle.PRIMARY_LIGHT,
            undo=True
        )
        text.pack(fill=tk.BOTH, expand=True)
        
        return container, text
    
    def _create_text_output(self, parent, height=15):
        """创建优化的文本输出框"""
        container = tk.Frame(parent, bg=ModernStyle.BORDER, padx=1, pady=1)
        
        text = scrolledtext.ScrolledText(
            container,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            wrap=tk.WORD,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            relief="flat",
            padx=12,
            pady=12,
            height=height,
            state=tk.DISABLED
        )
        text.pack(fill=tk.BOTH, expand=True)
        
        return container, text
    
    def _create_diagnose_page(self):
        """创建论文诊断页面"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_MAIN)
        self.pages["diagnose"] = page
        
        # 页面标题
        self._create_page_header(page, "论文诊断", "多维度 AI 分析论文质量，提供改进建议")
        
        # 进度指示器
        self.progress_indicators["diagnose"] = ProgressIndicator(page, "正在分析论文...")
        
        # 主内容区
        content = tk.Frame(page, bg=ModernStyle.BG_MAIN)
        content.pack(fill=tk.BOTH, expand=True, padx=ModernStyle.PADDING_XL, pady=(0, ModernStyle.PADDING_XL))
        
        # 使用 PanedWindow 实现可拖拽分栏
        paned = tk.PanedWindow(content, orient=tk.HORIZONTAL, bg=ModernStyle.BG_MAIN, sashwidth=8, sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧输入
        left_panel = tk.Frame(paned, bg=ModernStyle.BG_MAIN)
        
        # 工具栏
        toolbar = tk.Frame(left_panel, bg=ModernStyle.BG_MAIN)
        toolbar.pack(fill=tk.X, pady=(0, 12))
        
        upload_btn = tk.Button(
            toolbar,
            text="📁 选择文件",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
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
            toolbar,
            text="支持 PDF/Word 文档",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_MUTED,
            padx=12
        )
        self.diag_file_label.pack(side=tk.LEFT)
        
        # 输入框
        tk.Label(
            left_panel,
            text="论文内容",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))
        
        input_container, self.diag_text = self._create_text_input(left_panel)
        input_container.pack(fill=tk.BOTH, expand=True)
        
        # 诊断按钮
        btn_frame = tk.Frame(left_panel, bg=ModernStyle.BG_MAIN)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        ModernButton(
            btn_frame,
            text="开始诊断",
            command=self._run_diagnose,
            width=140,
            height=40
        ).pack(side=tk.LEFT)
        
        paned.add(left_panel, minsize=300)
        
        # 右侧结果
        right_panel = tk.Frame(paned, bg=ModernStyle.BG_MAIN)
        
        tk.Label(
            right_panel,
            text="诊断报告",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))
        
        result_container, self.diag_result = self._create_text_output(right_panel)
        result_container.pack(fill=tk.BOTH, expand=True)
        
        paned.add(right_panel, minsize=300)
        
        self.diag_file_path = None
        
    def _create_optimize_page(self):
        """创建深度优化页面"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_MAIN)
        self.pages["optimize"] = page
        
        self._create_page_header(page, "深度优化", "针对不同阶段和期刊，对论文进行精细化打磨")
        
        self.progress_indicators["optimize"] = ProgressIndicator(page, "正在优化论文...")
        
        content = tk.Frame(page, bg=ModernStyle.BG_MAIN)
        content.pack(fill=tk.BOTH, expand=True, padx=ModernStyle.PADDING_XL, pady=(0, ModernStyle.PADDING_XL))
        
        # 左侧配置面板
        config_panel = tk.Frame(content, bg=ModernStyle.BG_SECONDARY, width=260)
        config_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        config_panel.pack_propagate(False)
        
        config_inner = tk.Frame(config_panel, bg=ModernStyle.BG_SECONDARY, padx=20, pady=20)
        config_inner.pack(fill=tk.BOTH, expand=True)
        
        # 优化阶段
        tk.Label(
            config_inner,
            text="优化阶段",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 10))
        
        self.opt_stage = tk.StringVar(value="submission")
        stages = [
            ("初稿重构", "draft"),
            ("投稿优化", "submission"),
            ("退修回应", "revision"),
            ("终稿定稿", "final")
        ]
        
        for text, value in stages:
            rb = tk.Radiobutton(
                config_inner,
                text=text,
                variable=self.opt_stage,
                value=value,
                bg=ModernStyle.BG_SECONDARY,
                fg=ModernStyle.TEXT_PRIMARY,
                activebackground=ModernStyle.BG_SECONDARY,
                selectcolor=ModernStyle.BG_SECONDARY,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM)
            )
            rb.pack(anchor="w", pady=2)
        
        # 目标期刊
        tk.Label(
            config_inner,
            text="目标期刊",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w", pady=(20, 10))
        
        self.opt_journal = tk.StringVar(value="")
        journals = ["", "经济研究", "管理世界", "金融研究", "中国工业经济", "会计研究", "其他"]
        journal_combo = ttk.Combobox(
            config_inner,
            textvariable=self.opt_journal,
            values=journals,
            state="readonly",
            width=22
        )
        journal_combo.pack(fill=tk.X)
        
        # 优化章节
        tk.Label(
            config_inner,
            text="优化章节",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w", pady=(20, 10))
        
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
                config_inner,
                text=text,
                variable=var,
                bg=ModernStyle.BG_SECONDARY,
                fg=ModernStyle.TEXT_PRIMARY,
                activebackground=ModernStyle.BG_SECONDARY,
                selectcolor=ModernStyle.BG_SECONDARY,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM)
            )
            cb.pack(anchor="w", pady=1)
        
        # 文件上传
        tk.Label(
            config_inner,
            text="上传文件",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w", pady=(20, 10))
        
        tk.Button(
            config_inner,
            text="📁 选择文件",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            bd=1,
            relief="solid",
            command=lambda: self._select_file("optimize")
        ).pack(fill=tk.X)
        
        self.opt_file_label = tk.Label(
            config_inner,
            text="未选择文件",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED,
            wraplength=200
        )
        self.opt_file_label.pack(pady=5)
        
        # 优化按钮
        ModernButton(
            config_inner,
            text="开始优化",
            command=self._run_optimize,
            width=200,
            height=40
        ).pack(side=tk.BOTTOM, pady=10)
        
        # 右侧编辑区
        right_panel = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 输入区
        tk.Label(
            right_panel,
            text="论文内容",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(0, 5))
        
        input_container, self.opt_input = self._create_text_input(right_panel, height=12)
        input_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 输出区
        tk.Label(
            right_panel,
            text="优化结果",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(0, 5))
        
        output_container, self.opt_output = self._create_text_output(right_panel, height=12)
        output_container.pack(fill=tk.BOTH, expand=True)
        
        self.opt_file_path = None
        
    def _create_dedup_page(self):
        """创建降重降AI页面"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_MAIN)
        self.pages["dedup"] = page
        
        self._create_page_header(page, "降重与降AI", "智能改写文本，降低重复率与AI检测痕迹")
        
        self.progress_indicators["dedup"] = ProgressIndicator(page, "正在处理文本...")
        
        content = tk.Frame(page, bg=ModernStyle.BG_MAIN)
        content.pack(fill=tk.BOTH, expand=True, padx=ModernStyle.PADDING_XL, pady=(0, ModernStyle.PADDING_XL))
        
        # 顶部参数栏
        params_frame = tk.Frame(content, bg=ModernStyle.BG_SECONDARY, padx=20, pady=15)
        params_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 处理强度
        tk.Label(
            params_frame,
            text="处理强度:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(side=tk.LEFT)
        
        self.dedup_strength = tk.Scale(
            params_frame,
            from_=1, to=5,
            orient=tk.HORIZONTAL,
            length=150,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            highlightthickness=0,
            troughcolor=ModernStyle.BORDER,
            activebackground=ModernStyle.PRIMARY,
            sliderrelief=tk.FLAT
        )
        self.dedup_strength.set(3)
        self.dedup_strength.pack(side=tk.LEFT, padx=10)
        
        # 强度说明
        strength_labels = tk.Frame(params_frame, bg=ModernStyle.BG_SECONDARY)
        strength_labels.pack(side=tk.LEFT, padx=5)
        tk.Label(
            strength_labels,
            text="1轻度 ←→ 5深度",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED
        ).pack()
        
        # 保留术语
        tk.Label(
            params_frame,
            text="保留术语:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(side=tk.LEFT, padx=(30, 0))
        
        self.dedup_terms = tk.Entry(
            params_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            width=30,
            bg=ModernStyle.BG_MAIN,
            relief="flat"
        )
        self.dedup_terms.pack(side=tk.LEFT, padx=10, ipady=5)
        self.dedup_terms.insert(0, "用逗号分隔，如: DID, PSM")
        self.dedup_terms.bind("<FocusIn>", lambda e: self.dedup_terms.delete(0, tk.END) if "逗号分隔" in self.dedup_terms.get() else None)
        
        # 文本区域
        text_frame = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # 使用 PanedWindow
        paned = tk.PanedWindow(text_frame, orient=tk.HORIZONTAL, bg=ModernStyle.BG_MAIN, sashwidth=8)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧输入
        left_panel = tk.Frame(paned, bg=ModernStyle.BG_MAIN)
        
        tk.Label(
            left_panel,
            text="原始文本",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(0, 5))
        
        input_container, self.dedup_input = self._create_text_input(left_panel)
        input_container.pack(fill=tk.BOTH, expand=True)
        
        paned.add(left_panel, minsize=300)
        
        # 中间按钮
        mid_panel = tk.Frame(paned, bg=ModernStyle.BG_MAIN, width=140)
        mid_panel.pack_propagate(False)
        
        # 居中按钮
        btn_container = tk.Frame(mid_panel, bg=ModernStyle.BG_MAIN)
        btn_container.place(relx=0.5, rely=0.5, anchor="center")
        
        buttons = [
            ("📉 智能降重", self._run_dedup, ModernStyle.PRIMARY),
            ("🤖 降AI痕迹", self._run_deai, ModernStyle.INFO),
            ("⚡ 深度全改", self._run_both_dedup, ModernStyle.SUCCESS)
        ]
        
        for text, cmd, color in buttons:
            ModernButton(
                btn_container,
                text=text,
                command=cmd,
                width=110,
                height=38,
                bg_color=color,
                hover_color=color
            ).pack(pady=8)
        
        paned.add(mid_panel, minsize=140)
        
        # 右侧输出
        right_panel = tk.Frame(paned, bg=ModernStyle.BG_MAIN)
        
        tk.Label(
            right_panel,
            text="改写结果",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(0, 5))
        
        output_container, self.dedup_output = self._create_text_output(right_panel)
        output_container.pack(fill=tk.BOTH, expand=True)
        
        paned.add(right_panel, minsize=300)
        
    def _create_search_page(self):
        """创建学术搜索页面"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_MAIN)
        self.pages["search"] = page
        
        self._create_page_header(page, "学术搜索", "检索 Google Scholar / 知网文献")
        
        self.progress_indicators["search"] = ProgressIndicator(page, "正在搜索文献...")
        
        content = tk.Frame(page, bg=ModernStyle.BG_MAIN)
        content.pack(fill=tk.BOTH, expand=True, padx=ModernStyle.PADDING_XL, pady=(0, ModernStyle.PADDING_XL))
        
        # 搜索栏
        search_frame = tk.Frame(content, bg=ModernStyle.BG_SECONDARY, padx=20, pady=15)
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            search_frame,
            text="🔍",
            font=(ModernStyle.FONT_FAMILY, 16),
            bg=ModernStyle.BG_SECONDARY
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_query = tk.Entry(
            search_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            relief="flat",
            width=50
        )
        self.search_query.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.search_query.insert(0, "数字经济 企业创新")
        
        self.search_source = tk.StringVar(value="Google Scholar")
        source_combo = ttk.Combobox(
            search_frame,
            textvariable=self.search_source,
            values=["Google Scholar", "知网 CNKI"],
            state="readonly",
            width=15
        )
        source_combo.pack(side=tk.LEFT, padx=15)
        
        ModernButton(
            search_frame,
            text="搜索",
            command=self._run_search,
            width=80,
            height=36
        ).pack(side=tk.LEFT)
        
        # 结果区
        tk.Label(
            content,
            text="搜索结果",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(0, 8))
        
        result_container, self.search_result = self._create_text_output(content)
        result_container.pack(fill=tk.BOTH, expand=True)
        
    def _create_revision_page(self):
        """创建退修助手页面"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_MAIN)
        self.pages["revision"] = page
        
        self._create_page_header(page, "退修助手", "智能解析审稿意见，生成逐条回应策略")
        
        self.progress_indicators["revision"] = ProgressIndicator(page, "正在分析审稿意见...")
        
        content = tk.Frame(page, bg=ModernStyle.BG_MAIN)
        content.pack(fill=tk.BOTH, expand=True, padx=ModernStyle.PADDING_XL, pady=(0, ModernStyle.PADDING_XL))
        
        paned = tk.PanedWindow(content, orient=tk.HORIZONTAL, bg=ModernStyle.BG_MAIN, sashwidth=8)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧输入
        left_panel = tk.Frame(paned, bg=ModernStyle.BG_MAIN)
        
        tk.Label(
            left_panel,
            text="审稿意见",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(0, 5))
        
        comments_container, self.rev_comments = self._create_text_input(left_panel, height=12)
        comments_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        tk.Label(
            left_panel,
            text="论文摘要（可选）",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(0, 5))
        
        summary_container, self.rev_summary = self._create_text_input(left_panel, height=6)
        summary_container.pack(fill=tk.X, pady=(0, 15))
        
        ModernButton(
            left_panel,
            text="生成回应策略",
            command=self._run_revision,
            width=160,
            height=40
        ).pack(anchor="w")
        
        paned.add(left_panel, minsize=350)
        
        # 右侧结果
        right_panel = tk.Frame(paned, bg=ModernStyle.BG_MAIN)
        
        tk.Label(
            right_panel,
            text="回应建议",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(0, 8))
        
        output_container, self.rev_output = self._create_text_output(right_panel)
        output_container.pack(fill=tk.BOTH, expand=True)
        
        paned.add(right_panel, minsize=350)
        
    def _create_settings_page(self):
        """创建设置页面"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_MAIN)
        self.pages["settings"] = page
        
        self._create_page_header(page, "系统设置", "配置 AI 模型、API 密钥等参数")
        
        # 滚动区域
        canvas = tk.Canvas(page, bg=ModernStyle.BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernStyle.BG_MAIN)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def configure_canvas(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind('<Configure>', configure_canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 鼠标滚轮
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=ModernStyle.PADDING_XL)
        
        content = scrollable_frame
        
        # 供应商选择
        section1 = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        section1.pack(fill=tk.X, pady=(0, 25))
        
        tk.Label(
            section1,
            text="模型供应商",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LG, "bold"),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 12))
        
        provider_frame = tk.Frame(section1, bg=ModernStyle.BG_SECONDARY, padx=20, pady=15)
        provider_frame.pack(fill=tk.X)
        
        self.provider_var = tk.StringVar(value="OpenAI 兼容")
        providers = ["OpenAI 兼容", "DeepSeek", "硅基流动", "Ollama 本地", "自定义"]
        
        provider_combo = ttk.Combobox(
            provider_frame,
            textvariable=self.provider_var,
            values=providers,
            state="readonly",
            width=25
        )
        provider_combo.pack(side=tk.LEFT)
        provider_combo.bind("<<ComboboxSelected>>", self._on_provider_change)
        
        tk.Label(
            provider_frame,
            text="💡 切换供应商可自动填充 API 地址",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED
        ).pack(side=tk.LEFT, padx=20)
        
        # API 配置
        section2 = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        section2.pack(fill=tk.X, pady=(0, 25))
        
        header2 = tk.Frame(section2, bg=ModernStyle.BG_MAIN)
        header2.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            header2,
            text="API 配置",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LG, "bold"),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(side=tk.LEFT)
        
        tk.Button(
            header2,
            text="🔗 测试连接",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2",
            command=self._test_connection
        ).pack(side=tk.RIGHT)
        
        api_frame = tk.Frame(section2, bg=ModernStyle.BG_SECONDARY, padx=20, pady=20)
        api_frame.pack(fill=tk.X)
        
        # API 地址
        tk.Label(
            api_frame,
            text="API 地址:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            width=12,
            anchor="w"
        ).grid(row=0, column=0, pady=8, sticky="w")
        
        self.setting_llm_base = tk.Entry(
            api_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            width=55
        )
        self.setting_llm_base.grid(row=0, column=1, sticky="we", padx=10, ipady=6)
        
        # API 密钥
        tk.Label(
            api_frame,
            text="API 密钥:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            width=12,
            anchor="w"
        ).grid(row=1, column=0, pady=8, sticky="w")
        
        key_frame = tk.Frame(api_frame, bg=ModernStyle.BG_SECONDARY)
        key_frame.grid(row=1, column=1, sticky="we", padx=10)
        
        self.setting_llm_key = tk.Entry(
            key_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            show="•"
        )
        self.setting_llm_key.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        
        self.show_key = tk.BooleanVar(value=False)
        tk.Checkbutton(
            key_frame,
            text="显示",
            variable=self.show_key,
            command=self._toggle_key_visibility,
            bg=ModernStyle.BG_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS)
        ).pack(side=tk.LEFT, padx=10)
        
        # 模型选择
        section3 = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        section3.pack(fill=tk.X, pady=(0, 25))
        
        tk.Label(
            section3,
            text="模型选择",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LG, "bold"),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 12))
        
        model_frame = tk.Frame(section3, bg=ModernStyle.BG_SECONDARY, padx=20, pady=20)
        model_frame.pack(fill=tk.X)
        
        # LLM 模型
        tk.Label(
            model_frame,
            text="语言模型:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            width=15,
            anchor="w"
        ).grid(row=0, column=0, pady=10, sticky="w")
        
        self.setting_llm_model = ttk.Combobox(
            model_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            width=40,
            values=["gpt-4o", "gpt-4o-mini", "deepseek-chat", "deepseek-coder", "Qwen/Qwen2.5-72B-Instruct"]
        )
        self.setting_llm_model.grid(row=0, column=1, sticky="w", padx=10)
        
        self.llm_status = tk.Label(
            model_frame,
            text="● 未配置",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.WARNING
        )
        self.llm_status.grid(row=0, column=2, padx=10)
        
        # 嵌入模型
        tk.Label(
            model_frame,
            text="嵌入模型:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            width=15,
            anchor="w"
        ).grid(row=1, column=0, pady=10, sticky="w")
        
        self.setting_embed_model = ttk.Combobox(
            model_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            width=40,
            values=["text-embedding-3-small", "text-embedding-3-large", "BAAI/bge-m3"]
        )
        self.setting_embed_model.grid(row=1, column=1, sticky="w", padx=10)
        
        self.use_same_api = tk.BooleanVar(value=True)
        tk.Checkbutton(
            model_frame,
            text="使用同一API",
            variable=self.use_same_api,
            bg=ModernStyle.BG_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM)
        ).grid(row=1, column=2, padx=10)
        
        # 独立嵌入API配置（隐藏）
        self.embed_api_frame = tk.Frame(section3, bg=ModernStyle.BG_INPUT, padx=20, pady=15)
        
        tk.Label(
            self.embed_api_frame,
            text="嵌入API地址:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_INPUT
        ).grid(row=0, column=0, pady=5, sticky="w")
        
        self.setting_embed_base = tk.Entry(
            self.embed_api_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            width=50
        )
        self.setting_embed_base.grid(row=0, column=1, padx=10, ipady=5)
        
        tk.Label(
            self.embed_api_frame,
            text="嵌入API密钥:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_INPUT
        ).grid(row=1, column=0, pady=5, sticky="w")
        
        self.setting_embed_key = tk.Entry(
            self.embed_api_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            width=50,
            show="•"
        )
        self.setting_embed_key.grid(row=1, column=1, padx=10, ipady=5)
        
        # 保存按钮
        btn_frame = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        btn_frame.pack(fill=tk.X, pady=25)
        
        ModernButton(
            btn_frame,
            text="保存配置",
            command=self._save_settings,
            width=140,
            height=42
        ).pack(side=tk.LEFT)
        
        tk.Button(
            btn_frame,
            text="恢复默认",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self._reset_settings
        ).pack(side=tk.LEFT, padx=15)
        
        # 加载现有设置
        self._load_settings()
    
    def _on_provider_change(self, event=None):
        """切换供应商时自动填充"""
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
        """切换密钥显示"""
        if self.show_key.get():
            self.setting_llm_key.config(show="")
        else:
            self.setting_llm_key.config(show="•")
    
    def _test_connection(self):
        """测试API连接"""
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
                self._safe_update(lambda: self._update_status(True))
                self._safe_update(lambda: messagebox.showinfo("成功", "✅ 连接成功！API 配置有效。"))
            except Exception as e:
                self._safe_update(lambda: self._update_status(False))
                self._safe_update(lambda: messagebox.showerror("失败", f"❌ 连接失败:\n{str(e)}"))
        
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
    
    # ==================== 核心功能方法 ====================
    
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
                self.diag_file_label.config(text=f"✓ {file_name}", fg=ModernStyle.SUCCESS)
            elif target == "optimize":
                self.opt_file_path = file_path
                self.opt_file_label.config(text=f"✓ {file_name}", fg=ModernStyle.SUCCESS)
    
    def _set_result(self, widget: scrolledtext.ScrolledText, text: str):
        """设置结果文本（线程安全）"""
        def update():
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            widget.insert("1.0", text)
            widget.config(state=tk.DISABLED)
        self._safe_update(update)
    
    def _run_in_thread(self, func: Callable, *args, **kwargs):
        """在后台线程运行"""
        def wrapper():
            try:
                func(*args, **kwargs)
            except Exception as e:
                self._safe_update(lambda: messagebox.showerror("错误", str(e)))
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
    
    def _run_diagnose(self):
        """运行诊断"""
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
        
        # 显示进度
        self.progress_indicators["diagnose"].start("正在分析论文结构...")
        self._set_result(self.diag_result, "")
        
        def do_diagnose():
            try:
                self._safe_update(lambda: self.progress_indicators["diagnose"].update_text("正在进行多维度诊断..."))
                
                from agents.master import MasterAgent
                from agents.diagnostic import DiagnosticAgent
                
                agent = MasterAgent()
                report = agent.diagnose_only(content, file_type=file_type)
                
                diagnostic = DiagnosticAgent()
                formatted = diagnostic.format_report(report)
                
                result_text = f"""📊 综合评分: {report.overall_score:.1f}/10

{'='*50}

{formatted}
"""
                self._set_result(self.diag_result, result_text)
                
            except Exception as e:
                self._set_result(self.diag_result, f"诊断失败: {e}")
            finally:
                self._safe_update(lambda: self.progress_indicators["diagnose"].stop())
        
        self._run_in_thread(do_diagnose)
    
    def _run_optimize(self):
        """运行优化"""
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
        
        sections = [k for k, v in self.opt_sections.items() if v.get()]
        if not sections:
            messagebox.showwarning("提示", "请至少选择一个要优化的章节")
            return
        
        stage = self.opt_stage.get()
        journal = self.opt_journal.get() or None
        
        self.progress_indicators["optimize"].start("正在优化论文...")
        self._set_result(self.opt_output, "")
        
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
                    self._set_result(self.opt_output, f"优化失败: {result.message}")
                    return
                
                output_parts = []
                for section, opt_result in result.optimizations.items():
                    if opt_result.success:
                        output_parts.append(f"## {section.upper()}\n\n{opt_result.optimized}")
                
                if not output_parts:
                    self._set_result(self.opt_output, "未能生成任何优化结果")
                    return
                
                result_text = "\n\n" + "="*50 + "\n\n".join(output_parts)
                self._set_result(self.opt_output, result_text)
                
            except Exception as e:
                self._set_result(self.opt_output, f"优化失败: {e}")
            finally:
                self._safe_update(lambda: self.progress_indicators["optimize"].stop())
        
        self._run_in_thread(do_optimize)
    
    def _run_dedup(self):
        """运行降重"""
        text = self.dedup_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("提示", "请输入文本")
            return
        
        strength = self.dedup_strength.get()
        terms_str = self.dedup_terms.get().strip()
        if "逗号分隔" in terms_str:
            terms_str = ""
        terms = [t.strip() for t in terms_str.split(",") if t.strip()] if terms_str else None
        
        self.progress_indicators["dedup"].start("正在智能降重...")
        self._set_result(self.dedup_output, "")
        
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
                self._set_result(self.dedup_output, result_text)
                
            except Exception as e:
                self._set_result(self.dedup_output, f"处理失败: {e}")
            finally:
                self._safe_update(lambda: self.progress_indicators["dedup"].stop())
        
        self._run_in_thread(do_dedup)
    
    def _run_deai(self):
        """运行降AI"""
        text = self.dedup_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("提示", "请输入文本")
            return
        
        self.progress_indicators["dedup"].start("正在消除AI痕迹...")
        self._set_result(self.dedup_output, "")
        
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
                self._set_result(self.dedup_output, result_text)
                
            except Exception as e:
                self._set_result(self.dedup_output, f"处理失败: {e}")
            finally:
                self._safe_update(lambda: self.progress_indicators["dedup"].stop())
        
        self._run_in_thread(do_deai)
    
    def _run_both_dedup(self):
        """运行降重+降AI"""
        text = self.dedup_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("提示", "请输入文本")
            return
        
        strength = self.dedup_strength.get()
        terms_str = self.dedup_terms.get().strip()
        if "逗号分隔" in terms_str:
            terms_str = ""
        terms = [t.strip() for t in terms_str.split(",") if t.strip()] if terms_str else None
        
        self.progress_indicators["dedup"].start("正在深度处理...")
        self._set_result(self.dedup_output, "")
        
        def do_both():
            try:
                from engines.dedup import DedupEngine
                from engines.deai import DeAIEngine
                
                self._safe_update(lambda: self.progress_indicators["dedup"].update_text("第1步: 智能降重..."))
                dedup_engine = DedupEngine()
                dedup_result = dedup_engine.process(text, strength=int(strength), preserve_terms=terms)
                
                self._safe_update(lambda: self.progress_indicators["dedup"].update_text("第2步: 消除AI痕迹..."))
                deai_engine = DeAIEngine()
                deai_result = deai_engine.process(dedup_result.processed)
                
                result_text = f"""⚡ 深度处理结果

{deai_result.processed}

{'='*50}

📊 降重报告
{dedup_engine.get_dedup_report(dedup_result)}

📊 降AI报告
{deai_engine.get_report(deai_result)}
"""
                self._set_result(self.dedup_output, result_text)
                
            except Exception as e:
                self._set_result(self.dedup_output, f"处理失败: {e}")
            finally:
                self._safe_update(lambda: self.progress_indicators["dedup"].stop())
        
        self._run_in_thread(do_both)
    
    def _run_search(self):
        """运行学术搜索"""
        query = self.search_query.get().strip()
        if not query:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return
        
        source = self.search_source.get()
        
        self.progress_indicators["search"].start(f"正在搜索 {source}...")
        self._set_result(self.search_result, "")
        
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
                
                self._set_result(self.search_result, formatted)
                
            except Exception as e:
                self._set_result(self.search_result, f"搜索失败: {e}")
            finally:
                self._safe_update(lambda: self.progress_indicators["search"].stop())
        
        self._run_in_thread(do_search)
    
    def _run_revision(self):
        """运行退修处理"""
        comments = self.rev_comments.get("1.0", tk.END).strip()
        if not comments:
            messagebox.showwarning("提示", "请粘贴审稿意见")
            return
        
        summary = self.rev_summary.get("1.0", tk.END).strip() or None
        
        self.progress_indicators["revision"].start("正在分析审稿意见...")
        self._set_result(self.rev_output, "")
        
        def do_revision():
            try:
                self._safe_update(lambda: self.progress_indicators["revision"].update_text("正在生成回应策略..."))
                
                from agents.revision import RevisionAgent
                
                agent = RevisionAgent()
                result = agent.process_comments(comments, summary)
                
                formatted = agent.format_result(result)
                
                result_text = f"""{formatted}

{'='*50}

📧 回应信

{result.response_letter}
"""
                self._set_result(self.rev_output, result_text)
                
            except Exception as e:
                self._set_result(self.rev_output, f"处理失败: {e}")
            finally:
                self._safe_update(lambda: self.progress_indicators["revision"].stop())
        
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
            
            if settings.llm_api_key:
                self.llm_status.config(text="● 已配置", fg=ModernStyle.SUCCESS)
        except Exception:
            pass
    
    def _save_settings(self):
        """保存设置"""
        try:
            env_path = BASE_DIR / ".env"
            
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
