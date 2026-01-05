# -*- coding: utf-8 -*-
"""
EconPaper Pro - 原生 Tkinter GUI 应用 (v2.3用户体验优化版)
- 修复UI卡顿问题
- 现代化界面设计
- 添加进度指示器
- 优化字体大小
- 分离API配置
- 模型拉取功能
- 首次使用引导
- 实时字数统计
- 关于页面
"""

VERSION = "0.4.3"

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
    """现代简约风格配置 - 优化字体大小"""
    
    # 主色调
    PRIMARY = "#2563EB"
    PRIMARY_DARK = "#1D4ED8"
    PRIMARY_LIGHT = "#DBEAFE"
    PRIMARY_HOVER = "#3B82F6"
    
    # 功能色
    SUCCESS = "#10B981"
    WARNING = "#F59E0B"
    ERROR = "#EF4444"
    INFO = "#6366F1"
    
    # 中性色
    BG_MAIN = "#FFFFFF"
    BG_SECONDARY = "#F8FAFC"
    BG_SIDEBAR = "#F1F5F9"
    BG_CARD = "#FFFFFF"
    BG_HOVER = "#E2E8F0"
    BG_INPUT = "#F8FAFC"
    
    # 文字颜色
    TEXT_PRIMARY = "#0F172A"
    TEXT_SECONDARY = "#64748B"
    TEXT_MUTED = "#94A3B8"
    TEXT_LIGHT = "#FFFFFF"
    
    # 边框
    BORDER = "#E2E8F0"
    BORDER_FOCUS = "#2563EB"
    
    # 字体配置 (优化：增大字体)
    FONT_FAMILY = "Microsoft YaHei UI"
    FONT_SIZE_XXL = 22   # 特大标题
    FONT_SIZE_XL = 18    # 大标题
    FONT_SIZE_LG = 14    # 中标题
    FONT_SIZE_MD = 12    # 正文（增大）
    FONT_SIZE_SM = 11    # 次要文字（增大）
    FONT_SIZE_XS = 10    # 最小字体（增大）
    
    # 间距
    PADDING_XL = 30
    PADDING_LG = 20
    PADDING_MD = 15
    PADDING_SM = 10
    PADDING_XS = 5
    
    @classmethod
    def configure_styles(cls, root):
        """配置 ttk 样式"""
        style = ttk.Style(root)
        
        try:
            style.theme_use('clam')
        except Exception:
            pass
        
        # 全局配置 - 使用更大字体
        style.configure(".", 
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_SM),
            background=cls.BG_MAIN
        )
        
        # 主按钮
        style.configure("Primary.TButton",
            background=cls.PRIMARY,
            foreground=cls.TEXT_LIGHT,
            padding=(20, 12),
            borderwidth=0,
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_SM, "bold")
        )
        style.map("Primary.TButton",
            background=[("active", cls.PRIMARY_DARK), ("pressed", cls.PRIMARY_DARK)]
        )
        
        # 进度条
        style.configure("Modern.Horizontal.TProgressbar",
            troughcolor=cls.BG_SECONDARY,
            background=cls.PRIMARY,
            lightcolor=cls.PRIMARY,
            darkcolor=cls.PRIMARY,
            borderwidth=0,
            thickness=8
        )
        
        # Combobox - 更大的字体和间距
        style.configure("TCombobox",
            fieldbackground=cls.BG_INPUT,
            background=cls.BG_MAIN,
            bordercolor=cls.BORDER,
            arrowcolor=cls.TEXT_SECONDARY,
            padding=8,
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_SM)
        )
        style.map("TCombobox",
            fieldbackground=[("readonly", cls.BG_INPUT)],
            selectbackground=[("readonly", cls.PRIMARY_LIGHT)]
        )
        
        return style


class ProgressIndicator:
    """现代进度指示器组件"""
    
    def __init__(self, parent, text="处理中..."):
        self.parent = parent
        self.frame = tk.Frame(parent, bg=ModernStyle.BG_MAIN)
        self.is_active = False
        
        self.container = tk.Frame(self.frame, bg=ModernStyle.BG_MAIN, pady=10)
        self.container.pack(fill=tk.X, padx=20)
        
        self.label = tk.Label(
            self.container,
            text=text,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_SECONDARY
        )
        self.label.pack(anchor="w", pady=(0, 5))
        
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
        self.progress.start(15)
        
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
    
    def __init__(self, parent, text, command=None, width=120, height=40, 
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
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        
    def _draw_button(self):
        """绘制圆角按钮"""
        self.delete("all")
        r = 8
        
        self.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill=self._current_bg, outline="")
        self.create_arc(self.width-r*2, 0, self.width, r*2, start=0, extent=90, fill=self._current_bg, outline="")
        self.create_arc(0, self.height-r*2, r*2, self.height, start=180, extent=90, fill=self._current_bg, outline="")
        self.create_arc(self.width-r*2, self.height-r*2, self.width, self.height, start=270, extent=90, fill=self._current_bg, outline="")
        
        self.create_rectangle(r, 0, self.width-r, self.height, fill=self._current_bg, outline="")
        self.create_rectangle(0, r, self.width, self.height-r, fill=self._current_bg, outline="")
        
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
    """EconPaper Pro 主应用 - v2.3用户体验优化版"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("📚 EconPaper Pro - 经管论文智能优化")
        self.root.geometry("1400x900")
        self.root.minsize(1100, 700)
        
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
        
        # 任务队列
        self.update_queue = queue.Queue()
        
        # 状态变量
        self.current_tab = tk.StringVar(value="diagnose")
        self.is_processing = False
        self.last_search_results = []  # 存储最近的搜索结果
        self.api_configured = False  # API是否已配置
        
        # 创建主布局
        self._create_layout()
        
        # 启动UI更新循环
        self._process_queue()
        
        # 首次使用检查
        self.root.after(500, self._check_first_run)
        
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
            self.root.after(50, self._process_queue)
    
    def _safe_update(self, func):
        """线程安全的UI更新"""
        self.update_queue.put(func)
        
    def _create_layout(self):
        """创建主布局"""
        main_container = tk.Frame(self.root, bg=ModernStyle.BG_MAIN)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        self._create_sidebar(main_container)
        
        self.content_frame = tk.Frame(main_container, bg=ModernStyle.BG_MAIN)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.pages = {}
        self.progress_indicators = {}
        
        self._create_diagnose_page()
        self._create_optimize_page()
        self._create_dedup_page()
        self._create_search_page()
        self._create_revision_page()
        self._create_settings_page()
        
        self._show_page("diagnose")
        
    def _create_sidebar(self, parent):
        """创建侧边栏 - 优化字体大小"""
        sidebar = tk.Frame(parent, bg=ModernStyle.BG_SIDEBAR, width=260)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        separator = tk.Frame(sidebar, bg=ModernStyle.BORDER, width=1)
        separator.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Logo 区域
        logo_frame = tk.Frame(sidebar, bg=ModernStyle.BG_SIDEBAR)
        logo_frame.pack(fill=tk.X, pady=(35, 25), padx=25)
        
        title_container = tk.Frame(logo_frame, bg=ModernStyle.BG_SIDEBAR)
        title_container.pack(anchor="w")
        
        tk.Label(
            title_container,
            text="📚",
            font=(ModernStyle.FONT_FAMILY, 28),
            bg=ModernStyle.BG_SIDEBAR
        ).pack(side=tk.LEFT, padx=(0, 12))
        
        title_text = tk.Frame(title_container, bg=ModernStyle.BG_SIDEBAR)
        title_text.pack(side=tk.LEFT)
        
        tk.Label(
            title_text,
            text="EconPaper",
            font=(ModernStyle.FONT_FAMILY, 18, "bold"),
            bg=ModernStyle.BG_SIDEBAR,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            title_text,
            text="Pro",
            font=(ModernStyle.FONT_FAMILY, 18),
            bg=ModernStyle.BG_SIDEBAR,
            fg=ModernStyle.PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            logo_frame,
            text="经管学术论文智能助手",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SIDEBAR,
            fg=ModernStyle.TEXT_MUTED
        ).pack(anchor="w", pady=(8, 0))
        
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
            btn_frame.pack(fill=tk.X, pady=3)
            
            btn_inner = tk.Frame(btn_frame, bg=ModernStyle.BG_SIDEBAR, padx=15, pady=12)
            btn_inner.pack(fill=tk.X)
            
            tk.Label(
                btn_inner,
                text=icon,
                font=(ModernStyle.FONT_FAMILY, 16),
                bg=ModernStyle.BG_SIDEBAR
            ).pack(side=tk.LEFT)
            
            text_frame = tk.Frame(btn_inner, bg=ModernStyle.BG_SIDEBAR)
            text_frame.pack(side=tk.LEFT, padx=12)
            
            title_label = tk.Label(
                text_frame,
                text=title,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
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
            
            for widget in [btn_frame, btn_inner, title_label, desc_label]:
                widget.bind("<Button-1>", lambda e, p=page_id: self._show_page(p))
                widget.bind("<Enter>", lambda e, p=page_id: self._on_nav_hover(p, True))
                widget.bind("<Leave>", lambda e, p=page_id: self._on_nav_hover(p, False))
        
        # 底部按钮区
        bottom_frame = tk.Frame(sidebar, bg=ModernStyle.BG_SIDEBAR)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=12, pady=20)
        
        sep2 = tk.Frame(bottom_frame, bg=ModernStyle.BORDER, height=1)
        sep2.pack(fill=tk.X, pady=(0, 15))
        
        # 设置按钮
        settings_btn = tk.Frame(bottom_frame, bg=ModernStyle.BG_SIDEBAR, cursor="hand2")
        settings_btn.pack(fill=tk.X, pady=3)
        
        settings_inner = tk.Frame(settings_btn, bg=ModernStyle.BG_SIDEBAR, padx=15, pady=12)
        settings_inner.pack(fill=tk.X)
        
        settings_icon = tk.Label(
            settings_inner,
            text="⚙️",
            font=(ModernStyle.FONT_FAMILY, 16),
            bg=ModernStyle.BG_SIDEBAR,
            cursor="hand2"
        )
        settings_icon.pack(side=tk.LEFT)
        
        settings_text = tk.Label(
            settings_inner,
            text="系统设置",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SIDEBAR,
            fg=ModernStyle.TEXT_PRIMARY,
            cursor="hand2"
        )
        settings_text.pack(side=tk.LEFT, padx=12)
        
        self.nav_buttons["settings"] = {
            "frame": settings_btn,
            "inner": settings_inner,
            "title": settings_text,
            "desc": None
        }
        
        def on_settings_click(e):
            self._show_page("settings")
        
        settings_btn.bind("<Button-1>", on_settings_click)
        settings_inner.bind("<Button-1>", on_settings_click)
        settings_icon.bind("<Button-1>", on_settings_click)
        settings_text.bind("<Button-1>", on_settings_click)
        
        # 关于按钮
        about_btn = tk.Frame(bottom_frame, bg=ModernStyle.BG_SIDEBAR, cursor="hand2")
        about_btn.pack(fill=tk.X, pady=3)
        
        about_inner = tk.Frame(about_btn, bg=ModernStyle.BG_SIDEBAR, padx=15, pady=10)
        about_inner.pack(fill=tk.X)
        
        about_icon = tk.Label(
            about_inner,
            text="ℹ️",
            font=(ModernStyle.FONT_FAMILY, 14),
            bg=ModernStyle.BG_SIDEBAR,
            cursor="hand2"
        )
        about_icon.pack(side=tk.LEFT)
        
        about_text = tk.Label(
            about_inner,
            text=f"关于 v{VERSION}",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SIDEBAR,
            fg=ModernStyle.TEXT_MUTED,
            cursor="hand2"
        )
        about_text.pack(side=tk.LEFT, padx=12)
        
        def on_about_click(e):
            self._show_about_dialog()
        
        about_btn.bind("<Button-1>", on_about_click)
        about_inner.bind("<Button-1>", on_about_click)
        about_icon.bind("<Button-1>", on_about_click)
        about_text.bind("<Button-1>", on_about_click)

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
                btn["title"].config(bg=bg_color, fg=ModernStyle.PRIMARY, font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"))
                if btn["desc"]:
                    btn["desc"].config(bg=bg_color, fg=ModernStyle.PRIMARY)
            else:
                bg_color = ModernStyle.BG_SIDEBAR
                btn["frame"].config(bg=bg_color)
                btn["inner"].config(bg=bg_color)
                btn["title"].config(bg=bg_color, fg=ModernStyle.TEXT_PRIMARY, font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD))
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
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XXL, "bold"),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            header,
            text=subtitle,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_SECONDARY
        ).pack(anchor="w", pady=(5, 0))
        
        return header
    
    def _create_text_input(self, parent, height=15, show_count=True):
        """创建优化的文本输入框（带字数统计）"""
        outer_container = tk.Frame(parent, bg=ModernStyle.BG_MAIN)
        
        container = tk.Frame(outer_container, bg=ModernStyle.BORDER, padx=1, pady=1)
        container.pack(fill=tk.BOTH, expand=True)
        
        text = scrolledtext.ScrolledText(
            container,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            wrap=tk.WORD,
            bg=ModernStyle.BG_INPUT,
            fg=ModernStyle.TEXT_PRIMARY,
            relief="flat",
            padx=15,
            pady=15,
            height=height,
            insertbackground=ModernStyle.PRIMARY,
            selectbackground=ModernStyle.PRIMARY_LIGHT,
            undo=True
        )
        text.pack(fill=tk.BOTH, expand=True)
        
        # 字数统计标签
        if show_count:
            count_label = tk.Label(
                outer_container,
                text="字数: 0",
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
                bg=ModernStyle.BG_MAIN,
                fg=ModernStyle.TEXT_MUTED,
                anchor="e"
            )
            count_label.pack(fill=tk.X, pady=(3, 0))
            
            # 绑定文本变化事件
            def update_count(event=None):
                content = text.get("1.0", tk.END).strip()
                char_count = len(content)
                word_count = len(content.split()) if content else 0
                count_label.config(text=f"字数: {char_count} | 词数: {word_count}")
            
            text.bind("<KeyRelease>", update_count)
            text.bind("<<Paste>>", lambda e: text.after(10, update_count))
        
        return outer_container, text
    
    def _create_text_output(self, parent, height=15):
        """创建优化的文本输出框"""
        container = tk.Frame(parent, bg=ModernStyle.BORDER, padx=1, pady=1)
        
        text = scrolledtext.ScrolledText(
            container,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            wrap=tk.WORD,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            relief="flat",
            padx=15,
            pady=15,
            height=height,
            state=tk.DISABLED
        )
        text.pack(fill=tk.BOTH, expand=True)
        
        return container, text
    
    def _create_diagnose_page(self):
        """创建论文诊断页面"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_MAIN)
        self.pages["diagnose"] = page
        
        self._create_page_header(page, "论文诊断", "多维度 AI 分析论文质量，提供改进建议")
        
        self.progress_indicators["diagnose"] = ProgressIndicator(page, "正在分析论文...")
        
        content = tk.Frame(page, bg=ModernStyle.BG_MAIN)
        content.pack(fill=tk.BOTH, expand=True, padx=ModernStyle.PADDING_XL, pady=(0, ModernStyle.PADDING_XL))
        
        paned = tk.PanedWindow(content, orient=tk.HORIZONTAL, bg=ModernStyle.BG_MAIN, sashwidth=8, sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧输入
        left_panel = tk.Frame(paned, bg=ModernStyle.BG_MAIN)
        
        toolbar = tk.Frame(left_panel, bg=ModernStyle.BG_MAIN)
        toolbar.pack(fill=tk.X, pady=(0, 15))
        
        upload_btn = tk.Button(
            toolbar,
            text="📁 选择文件",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            activebackground=ModernStyle.BG_HOVER,
            bd=0,
            cursor="hand2",
            padx=18,
            pady=10,
            command=lambda: self._select_file("diagnose")
        )
        upload_btn.pack(side=tk.LEFT)
        
        self.diag_file_label = tk.Label(
            toolbar,
            text="支持 PDF/Word 文档",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_MUTED,
            padx=15
        )
        self.diag_file_label.pack(side=tk.LEFT)
        
        tk.Label(
            left_panel,
            text="论文内容",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 10))
        
        input_container, self.diag_text = self._create_text_input(left_panel)
        input_container.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = tk.Frame(left_panel, bg=ModernStyle.BG_MAIN)
        btn_frame.pack(fill=tk.X, pady=(18, 0))
        
        ModernButton(
            btn_frame,
            text="开始诊断",
            command=self._run_diagnose,
            width=150,
            height=45
        ).pack(side=tk.LEFT)
        
        # 添加文献推荐按钮
        ModernButton(
            btn_frame,
            text="📚 相关文献",
            command=self._recommend_literature,
            width=130,
            height=45,
            bg_color=ModernStyle.INFO,
            hover_color=ModernStyle.INFO
        ).pack(side=tk.LEFT, padx=15)
        
        paned.add(left_panel, minsize=350)
        
        # 右侧结果
        right_panel = tk.Frame(paned, bg=ModernStyle.BG_MAIN)
        
        result_header = tk.Frame(right_panel, bg=ModernStyle.BG_MAIN)
        result_header.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            result_header,
            text="诊断报告",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(side=tk.LEFT)
        
        # 添加导出按钮
        tk.Button(
            result_header,
            text="📥 导出报告",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: self._export_result(self.diag_result.get("1.0", tk.END), "诊断报告")
        ).pack(side=tk.RIGHT)
        
        result_container, self.diag_result = self._create_text_output(right_panel)
        result_container.pack(fill=tk.BOTH, expand=True)
        
        paned.add(right_panel, minsize=350)
        
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
        config_panel = tk.Frame(content, bg=ModernStyle.BG_SECONDARY, width=280)
        config_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        config_panel.pack_propagate(False)
        
        config_inner = tk.Frame(config_panel, bg=ModernStyle.BG_SECONDARY, padx=22, pady=22)
        config_inner.pack(fill=tk.BOTH, expand=True)
        
        # 优化阶段
        tk.Label(
            config_inner,
            text="优化阶段",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 12))
        
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
            rb.pack(anchor="w", pady=3)
        
        # 目标期刊
        tk.Label(
            config_inner,
            text="目标期刊",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w", pady=(22, 12))
        
        self.opt_journal = tk.StringVar(value="")
        journals = ["", "经济研究", "管理世界", "金融研究", "中国工业经济", "会计研究", "其他"]
        journal_combo = ttk.Combobox(
            config_inner,
            textvariable=self.opt_journal,
            values=journals,
            state="readonly",
            width=24,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM)
        )
        journal_combo.pack(fill=tk.X)
        
        # 优化章节
        tk.Label(
            config_inner,
            text="优化章节",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w", pady=(22, 12))
        
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
            cb.pack(anchor="w", pady=2)
        
        # 文件上传
        tk.Label(
            config_inner,
            text="上传文件",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(anchor="w", pady=(22, 12))
        
        tk.Button(
            config_inner,
            text="📁 选择文件",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            bd=1,
            relief="solid",
            padx=15,
            pady=8,
            command=lambda: self._select_file("optimize")
        ).pack(fill=tk.X)
        
        self.opt_file_label = tk.Label(
            config_inner,
            text="未选择文件",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED,
            wraplength=220
        )
        self.opt_file_label.pack(pady=8)
        
        ModernButton(
            config_inner,
            text="开始优化",
            command=self._run_optimize,
            width=220,
            height=45
        ).pack(side=tk.BOTTOM, pady=12)
        
        # 右侧编辑区
        right_panel = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            right_panel,
            text="论文内容",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(0, 8))
        
        input_container, self.opt_input = self._create_text_input(right_panel, height=12)
        input_container.pack(fill=tk.BOTH, expand=True, pady=(0, 18))
        
        tk.Label(
            right_panel,
            text="优化结果",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(0, 8))
        
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
        
        # 参数栏
        params_frame = tk.Frame(content, bg=ModernStyle.BG_SECONDARY, padx=22, pady=18)
        params_frame.pack(fill=tk.X, pady=(0, 22))
        
        tk.Label(
            params_frame,
            text="处理强度:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(side=tk.LEFT)
        
        self.dedup_strength = tk.Scale(
            params_frame,
            from_=1, to=5,
            orient=tk.HORIZONTAL,
            length=160,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            highlightthickness=0,
            troughcolor=ModernStyle.BORDER,
            activebackground=ModernStyle.PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM)
        )
        self.dedup_strength.set(3)
        self.dedup_strength.pack(side=tk.LEFT, padx=12)
        
        tk.Label(
            params_frame,
            text="1轻度 ←→ 5深度",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED
        ).pack(side=tk.LEFT, padx=8)
        
        tk.Label(
            params_frame,
            text="保留术语:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(side=tk.LEFT, padx=(35, 0))
        
        self.dedup_terms = tk.Entry(
            params_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            width=32,
            bg=ModernStyle.BG_MAIN,
            relief="flat"
        )
        self.dedup_terms.pack(side=tk.LEFT, padx=12, ipady=6)
        self.dedup_terms.insert(0, "用逗号分隔，如: DID, PSM")
        self.dedup_terms.bind("<FocusIn>", lambda e: self.dedup_terms.delete(0, tk.END) if "逗号分隔" in self.dedup_terms.get() else None)
        
        # 文本区域
        text_frame = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        paned = tk.PanedWindow(text_frame, orient=tk.HORIZONTAL, bg=ModernStyle.BG_MAIN, sashwidth=8)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧输入
        left_panel = tk.Frame(paned, bg=ModernStyle.BG_MAIN)
        
        tk.Label(
            left_panel,
            text="原始文本",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(0, 8))
        
        input_container, self.dedup_input = self._create_text_input(left_panel)
        input_container.pack(fill=tk.BOTH, expand=True)
        
        paned.add(left_panel, minsize=350)
        
        # 中间按钮
        mid_panel = tk.Frame(paned, bg=ModernStyle.BG_MAIN, width=160)
        mid_panel.pack_propagate(False)
        
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
                width=130,
                height=42,
                bg_color=color,
                hover_color=color
            ).pack(pady=10)
        
        paned.add(mid_panel, minsize=160)
        
        # 右侧输出
        right_panel = tk.Frame(paned, bg=ModernStyle.BG_MAIN)
        
        dedup_result_header = tk.Frame(right_panel, bg=ModernStyle.BG_MAIN)
        dedup_result_header.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(
            dedup_result_header,
            text="改写结果",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(side=tk.LEFT)
        
        tk.Button(
            dedup_result_header,
            text="📥 导出",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: self._export_result(self.dedup_output.get("1.0", tk.END), "改写结果")
        ).pack(side=tk.RIGHT)
        
        # 添加复制按钮
        tk.Button(
            dedup_result_header,
            text="📋 复制",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: self._copy_to_clipboard(self.dedup_output.get("1.0", tk.END))
        ).pack(side=tk.RIGHT, padx=8)
        
        output_container, self.dedup_output = self._create_text_output(right_panel)
        output_container.pack(fill=tk.BOTH, expand=True)
        
        paned.add(right_panel, minsize=350)
        
    def _create_search_page(self):
        """创建学术搜索页面 - v2.0 多数据源学术检索"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.BG_MAIN)
        self.pages["search"] = page
        
        self._create_page_header(page, "学术搜索", "中英文学术文献检索 - 支持多数据源")
        
        self.progress_indicators["search"] = ProgressIndicator(page, "正在搜索文献...")
        
        content = tk.Frame(page, bg=ModernStyle.BG_MAIN)
        content.pack(fill=tk.BOTH, expand=True, padx=ModernStyle.PADDING_XL, pady=(0, ModernStyle.PADDING_XL))
        
        # 搜索栏
        search_frame = tk.Frame(content, bg=ModernStyle.BG_SECONDARY, padx=22, pady=18)
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            search_frame,
            text="🔍",
            font=(ModernStyle.FONT_FAMILY, 18),
            bg=ModernStyle.BG_SECONDARY
        ).pack(side=tk.LEFT, padx=(0, 12))
        
        self.search_query = tk.Entry(
            search_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LG),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            relief="flat",
            width=40
        )
        self.search_query.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        self.search_query.insert(0, "digital economy innovation")
        
        # 绑定回车键搜索
        self.search_query.bind("<Return>", lambda e: self._run_search())
        
        # AI辅助按钮
        ModernButton(
            search_frame,
            text="🤖 AI扩展关键词",
            command=self._ai_expand_keywords,
            width=140,
            height=40,
            bg_color=ModernStyle.INFO,
            hover_color=ModernStyle.INFO
        ).pack(side=tk.LEFT, padx=12)
        
        # 数据源选择 - 中英文双语支持
        self.search_source = tk.StringVar(value="英文文献")
        source_combo = ttk.Combobox(
            search_frame,
            textvariable=self.search_source,
            values=["英文文献", "中文文献", "Semantic Scholar", "OpenAlex", "百度学术"],
            state="readonly",
            width=14,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM)
        )
        source_combo.pack(side=tk.LEFT, padx=12)
        
        ModernButton(
            search_frame,
            text="搜索",
            command=self._run_search,
            width=100,
            height=40
        ).pack(side=tk.LEFT)
        
        # 筛选选项行1
        filter_frame = tk.Frame(content, bg=ModernStyle.BG_SECONDARY, padx=22, pady=12)
        filter_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(
            filter_frame,
            text="结果数量:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.search_limit = tk.Scale(
            filter_frame,
            from_=5, to=50,
            orient=tk.HORIZONTAL,
            length=100,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            highlightthickness=0,
            troughcolor=ModernStyle.BORDER,
            activebackground=ModernStyle.PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS)
        )
        self.search_limit.set(15)
        self.search_limit.pack(side=tk.LEFT, padx=8)
        
        # 年份筛选
        tk.Label(
            filter_frame,
            text="起始年份:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(side=tk.LEFT, padx=(15, 8))
        
        self.search_year_from = tk.Entry(
            filter_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            width=6,
            bg=ModernStyle.BG_MAIN,
            relief="flat"
        )
        self.search_year_from.pack(side=tk.LEFT, ipady=4)
        self.search_year_from.insert(0, "2020")
        
        self.enable_ai_filter = tk.BooleanVar(value=False)
        tk.Checkbutton(
            filter_frame,
            text="✨ AI智能筛选",
            variable=self.enable_ai_filter,
            bg=ModernStyle.BG_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM)
        ).pack(side=tk.LEFT, padx=(20, 8))
        
        tk.Label(
            filter_frame,
            text="💡 英文文献用英文关键词，中文文献用中文关键词",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED
        ).pack(side=tk.RIGHT, padx=12)
        
        # 期刊级别筛选行2
        quality_frame = tk.Frame(content, bg=ModernStyle.BG_SECONDARY, padx=22, pady=12)
        quality_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            quality_frame,
            text="📊 期刊级别筛选:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(side=tk.LEFT, padx=(0, 12))
        
        self.filter_cssci = tk.BooleanVar(value=False)
        tk.Checkbutton(
            quality_frame,
            text="仅CSSCI/北核",
            variable=self.filter_cssci,
            bg=ModernStyle.BG_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM)
        ).pack(side=tk.LEFT, padx=8)
        
        self.filter_ssci = tk.BooleanVar(value=False)
        tk.Checkbutton(
            quality_frame,
            text="仅SSCI Q1/Q2",
            variable=self.filter_ssci,
            bg=ModernStyle.BG_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM)
        ).pack(side=tk.LEFT, padx=8)
        
        self.show_rank_info = tk.BooleanVar(value=True)
        tk.Checkbutton(
            quality_frame,
            text="显示期刊级别",
            variable=self.show_rank_info,
            bg=ModernStyle.BG_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM)
        ).pack(side=tk.LEFT, padx=8)
        
        tk.Label(
            quality_frame,
            text="(基于内置期刊数据库，覆盖经管类核心期刊)",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED
        ).pack(side=tk.LEFT, padx=12)
        
        # 功能按钮区
        action_frame = tk.Frame(content, bg=ModernStyle.BG_SECONDARY, padx=22, pady=12)
        action_frame.pack(fill=tk.X, pady=(0, 15))
        
        ModernButton(
            action_frame,
            text="📝 生成文献综述",
            command=self._generate_literature_review,
            width=140,
            height=38,
            bg_color=ModernStyle.SUCCESS,
            hover_color=ModernStyle.SUCCESS
        ).pack(side=tk.LEFT, padx=8)
        
        ModernButton(
            action_frame,
            text="📋 生成引用格式",
            command=self._generate_citations,
            width=140,
            height=38,
            bg_color=ModernStyle.INFO,
            hover_color=ModernStyle.INFO
        ).pack(side=tk.LEFT, padx=8)
        
        ModernButton(
            action_frame,
            text="📥 导出结果",
            command=lambda: self._export_result(self.search_result.get("1.0", tk.END), "搜索结果"),
            width=110,
            height=38,
            bg_color=ModernStyle.TEXT_SECONDARY,
            hover_color=ModernStyle.TEXT_SECONDARY
        ).pack(side=tk.LEFT, padx=8)
        
        tk.Label(
            action_frame,
            text="📊 英文：Semantic Scholar + OpenAlex | 中文：百度学术 + 万方数据",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED
        ).pack(side=tk.RIGHT, padx=12)
        
        # 结果区
        result_header = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        result_header.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            result_header,
            text="搜索结果",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(side=tk.LEFT)
        
        self.search_status_label = tk.Label(
            result_header,
            text="",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_MUTED
        )
        self.search_status_label.pack(side=tk.RIGHT)
        
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
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(0, 8))
        
        comments_container, self.rev_comments = self._create_text_input(left_panel, height=12)
        comments_container.pack(fill=tk.BOTH, expand=True, pady=(0, 18))
        
        tk.Label(
            left_panel,
            text="论文摘要（可选）",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(0, 8))
        
        summary_container, self.rev_summary = self._create_text_input(left_panel, height=6)
        summary_container.pack(fill=tk.X, pady=(0, 18))
        
        rev_btn_frame = tk.Frame(left_panel, bg=ModernStyle.BG_MAIN)
        rev_btn_frame.pack(fill=tk.X)
        
        ModernButton(
            rev_btn_frame,
            text="生成回应策略",
            command=self._run_revision,
            width=180,
            height=45
        ).pack(side=tk.LEFT)
        
        # 添加文献支撑按钮
        ModernButton(
            rev_btn_frame,
            text="📚 找支撑文献",
            command=self._find_supporting_literature,
            width=140,
            height=45,
            bg_color=ModernStyle.INFO,
            hover_color=ModernStyle.INFO
        ).pack(side=tk.LEFT, padx=15)
        
        paned.add(left_panel, minsize=400)
        
        # 右侧结果
        right_panel = tk.Frame(paned, bg=ModernStyle.BG_MAIN)
        
        tk.Label(
            right_panel,
            text="回应建议",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(0, 10))
        
        output_container, self.rev_output = self._create_text_output(right_panel)
        output_container.pack(fill=tk.BOTH, expand=True)
        
        paned.add(right_panel, minsize=400)
        
    def _create_settings_page(self):
        """创建设置页面 - 优化版：分离API配置 + 模型拉取"""
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
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=ModernStyle.PADDING_XL)
        
        content = scrollable_frame
        
        # ============ 1. 语言模型配置 ============
        section1 = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        section1.pack(fill=tk.X, pady=(0, 30))
        
        header1 = tk.Frame(section1, bg=ModernStyle.BG_MAIN)
        header1.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            header1,
            text="🤖 语言模型配置 (LLM)",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LG, "bold"),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(side=tk.LEFT)
        
        tk.Button(
            header1,
            text="🔗 测试连接",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
            command=self._test_llm_connection
        ).pack(side=tk.RIGHT)
        
        llm_frame = tk.Frame(section1, bg=ModernStyle.BG_SECONDARY, padx=25, pady=25)
        llm_frame.pack(fill=tk.X)
        
        # 供应商选择
        row1 = tk.Frame(llm_frame, bg=ModernStyle.BG_SECONDARY)
        row1.pack(fill=tk.X, pady=10)
        
        tk.Label(
            row1,
            text="供应商:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.llm_provider_var = tk.StringVar(value="OpenAI 兼容")
        providers = ["OpenAI 兼容", "DeepSeek", "硅基流动", "Ollama 本地", "自定义"]
        
        provider_combo = ttk.Combobox(
            row1,
            textvariable=self.llm_provider_var,
            values=providers,
            state="readonly",
            width=25,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM)
        )
        provider_combo.pack(side=tk.LEFT, padx=12)
        provider_combo.bind("<<ComboboxSelected>>", self._on_llm_provider_change)
        
        tk.Label(
            row1,
            text="💡 切换供应商自动填充 API 地址",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED
        ).pack(side=tk.LEFT, padx=18)
        
        # API 地址
        row2 = tk.Frame(llm_frame, bg=ModernStyle.BG_SECONDARY)
        row2.pack(fill=tk.X, pady=10)
        
        tk.Label(
            row2,
            text="API 地址:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.setting_llm_base = tk.Entry(
            row2,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            width=55
        )
        self.setting_llm_base.pack(side=tk.LEFT, padx=12, ipady=8)
        
        # API 密钥
        row3 = tk.Frame(llm_frame, bg=ModernStyle.BG_SECONDARY)
        row3.pack(fill=tk.X, pady=10)
        
        tk.Label(
            row3,
            text="API 密钥:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.setting_llm_key = tk.Entry(
            row3,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            width=45,
            show="•"
        )
        self.setting_llm_key.pack(side=tk.LEFT, padx=12, ipady=8)
        
        self.show_llm_key = tk.BooleanVar(value=False)
        tk.Checkbutton(
            row3,
            text="显示",
            variable=self.show_llm_key,
            command=lambda: self.setting_llm_key.config(show="" if self.show_llm_key.get() else "•"),
            bg=ModernStyle.BG_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM)
        ).pack(side=tk.LEFT, padx=12)
        
        # 模型选择
        row4 = tk.Frame(llm_frame, bg=ModernStyle.BG_SECONDARY)
        row4.pack(fill=tk.X, pady=10)
        
        tk.Label(
            row4,
            text="模型名称:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.setting_llm_model = ttk.Combobox(
            row4,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            width=35,
            values=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "deepseek-chat", "deepseek-coder", 
                   "Qwen/Qwen2.5-72B-Instruct", "claude-3-5-sonnet-20241022"]
        )
        self.setting_llm_model.pack(side=tk.LEFT, padx=12)
        
        tk.Button(
            row4,
            text="📥 拉取模型列表",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            bd=0,
            padx=15,
            pady=6,
            cursor="hand2",
            command=self._fetch_llm_models
        ).pack(side=tk.LEFT, padx=12)
        
        self.llm_status = tk.Label(
            row4,
            text="● 未配置",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.WARNING
        )
        self.llm_status.pack(side=tk.LEFT, padx=12)
        
        # ============ 2. 嵌入模型配置 ============
        section2 = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        section2.pack(fill=tk.X, pady=(0, 30))
        
        header2 = tk.Frame(section2, bg=ModernStyle.BG_MAIN)
        header2.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            header2,
            text="📊 嵌入模型配置 (Embedding)",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LG, "bold"),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(side=tk.LEFT)
        
        # 嵌入模型启用开关 (可选功能)
        self.enable_embedding = tk.BooleanVar(value=False)
        
        self.use_same_api = tk.BooleanVar(value=True)
        tk.Checkbutton(
            header2,
            text="使用与语言模型相同的 API 配置",
            variable=self.use_same_api,
            command=self._toggle_embed_api,
            bg=ModernStyle.BG_MAIN,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM)
        ).pack(side=tk.RIGHT)
        
        self.embed_frame = tk.Frame(section2, bg=ModernStyle.BG_SECONDARY, padx=25, pady=25)
        self.embed_frame.pack(fill=tk.X)
        
        # 嵌入模型 API 地址
        row_e1 = tk.Frame(self.embed_frame, bg=ModernStyle.BG_SECONDARY)
        row_e1.pack(fill=tk.X, pady=10)
        
        tk.Label(
            row_e1,
            text="API 地址:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.setting_embed_base = tk.Entry(
            row_e1,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            width=55
        )
        self.setting_embed_base.pack(side=tk.LEFT, padx=12, ipady=8)
        
        # 嵌入模型 API 密钥
        row_e2 = tk.Frame(self.embed_frame, bg=ModernStyle.BG_SECONDARY)
        row_e2.pack(fill=tk.X, pady=10)
        
        tk.Label(
            row_e2,
            text="API 密钥:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.setting_embed_key = tk.Entry(
            row_e2,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            width=45,
            show="•"
        )
        self.setting_embed_key.pack(side=tk.LEFT, padx=12, ipady=8)
        
        # 嵌入模型选择
        row_e3 = tk.Frame(self.embed_frame, bg=ModernStyle.BG_SECONDARY)
        row_e3.pack(fill=tk.X, pady=10)
        
        tk.Label(
            row_e3,
            text="模型名称:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.setting_embed_model = ttk.Combobox(
            row_e3,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            width=35,
            values=["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002",
                   "BAAI/bge-m3", "BAAI/bge-large-zh-v1.5"]
        )
        self.setting_embed_model.pack(side=tk.LEFT, padx=12)
        
        tk.Button(
            row_e3,
            text="📥 拉取模型列表",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            bd=0,
            padx=15,
            pady=6,
            cursor="hand2",
            command=self._fetch_embed_models
        ).pack(side=tk.LEFT, padx=12)
        
        # 初始状态：隐藏独立配置
        self._toggle_embed_api()
        
        # ============ 3. 数据存储配置 ============
        section3 = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        section3.pack(fill=tk.X, pady=(0, 30))
        
        header3 = tk.Frame(section3, bg=ModernStyle.BG_MAIN)
        header3.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            header3,
            text="📁 数据存储配置",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LG, "bold"),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header3,
            text="💡 自定义存储位置可避免占用C盘空间",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_MUTED
        ).pack(side=tk.RIGHT)
        
        storage_frame = tk.Frame(section3, bg=ModernStyle.BG_SECONDARY, padx=25, pady=25)
        storage_frame.pack(fill=tk.X)
        
        # 数据目录
        row_s1 = tk.Frame(storage_frame, bg=ModernStyle.BG_SECONDARY)
        row_s1.pack(fill=tk.X, pady=10)
        
        tk.Label(
            row_s1,
            text="数据目录:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.setting_data_dir = tk.Entry(
            row_s1,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            width=45
        )
        self.setting_data_dir.pack(side=tk.LEFT, padx=12, ipady=8)
        
        tk.Button(
            row_s1,
            text="📂 浏览",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            bd=0,
            padx=15,
            pady=6,
            cursor="hand2",
            command=lambda: self._browse_directory("data_dir")
        ).pack(side=tk.LEFT, padx=8)
        
        tk.Label(
            row_s1,
            text="(日志、缓存、向量库)",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED
        ).pack(side=tk.LEFT, padx=8)
        
        # 工作区目录
        row_s2 = tk.Frame(storage_frame, bg=ModernStyle.BG_SECONDARY)
        row_s2.pack(fill=tk.X, pady=10)
        
        tk.Label(
            row_s2,
            text="工作区目录:",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.setting_workspace_dir = tk.Entry(
            row_s2,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_MAIN,
            relief="flat",
            width=45
        )
        self.setting_workspace_dir.pack(side=tk.LEFT, padx=12, ipady=8)
        
        tk.Button(
            row_s2,
            text="📂 浏览",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            bd=0,
            padx=15,
            pady=6,
            cursor="hand2",
            command=lambda: self._browse_directory("workspace_dir")
        ).pack(side=tk.LEFT, padx=8)
        
        tk.Label(
            row_s2,
            text="(导出文件存放位置)",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED
        ).pack(side=tk.LEFT, padx=8)
        
        # 当前存储位置显示
        row_s3 = tk.Frame(storage_frame, bg=ModernStyle.BG_SECONDARY)
        row_s3.pack(fill=tk.X, pady=(15, 5))
        
        self.storage_info_label = tk.Label(
            row_s3,
            text="",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED,
            wraplength=600,
            justify="left"
        )
        self.storage_info_label.pack(anchor="w")
        
        # 加载并显示当前存储位置
        self._update_storage_info()
        
        # ============ 4. 保存按钮 ============
        btn_frame = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        btn_frame.pack(fill=tk.X, pady=30)
        
        ModernButton(
            btn_frame,
            text="💾 保存配置",
            command=self._save_settings,
            width=160,
            height=48
        ).pack(side=tk.LEFT)
        
        tk.Button(
            btn_frame,
            text="恢复默认",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            bd=0,
            padx=25,
            pady=12,
            cursor="hand2",
            command=self._reset_settings
        ).pack(side=tk.LEFT, padx=18)
        
        # 加载现有设置
        self._load_settings()
    
    def _toggle_embed_api(self):
        """切换嵌入模型配置显示"""
        # 清除现有内容
        for widget in self.embed_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.destroy()
        
        # 嵌入模型为可选功能，默认使用语言模型的 API
        if self.use_same_api.get():
            # 使用相同API - 只显示模型选择
            row_e3 = tk.Frame(self.embed_frame, bg=ModernStyle.BG_SECONDARY)
            row_e3.pack(fill=tk.X, pady=10)
            
            tk.Label(
                row_e3,
                text="模型名称:",
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
                bg=ModernStyle.BG_SECONDARY,
                fg=ModernStyle.TEXT_PRIMARY,
                width=12,
                anchor="w"
            ).pack(side=tk.LEFT)
            
            self.setting_embed_model = ttk.Combobox(
                row_e3,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
                width=35,
                values=["text-embedding-3-small", "text-embedding-3-large", "BAAI/bge-m3"]
            )
            self.setting_embed_model.pack(side=tk.LEFT, padx=12)
            
            tk.Label(
                row_e3,
                text="💡 将使用语言模型的 API 地址和密钥",
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
                bg=ModernStyle.BG_SECONDARY,
                fg=ModernStyle.TEXT_MUTED
            ).pack(side=tk.LEFT, padx=18)
        else:
            # 使用独立API - 显示完整配置
            # API 地址
            row_e1 = tk.Frame(self.embed_frame, bg=ModernStyle.BG_SECONDARY)
            row_e1.pack(fill=tk.X, pady=10)
            
            tk.Label(
                row_e1,
                text="API 地址:",
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
                bg=ModernStyle.BG_SECONDARY,
                fg=ModernStyle.TEXT_PRIMARY,
                width=12,
                anchor="w"
            ).pack(side=tk.LEFT)
            
            self.setting_embed_base = tk.Entry(
                row_e1,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
                bg=ModernStyle.BG_MAIN,
                relief="flat",
                width=55
            )
            self.setting_embed_base.pack(side=tk.LEFT, padx=12, ipady=8)
            
            # API 密钥
            row_e2 = tk.Frame(self.embed_frame, bg=ModernStyle.BG_SECONDARY)
            row_e2.pack(fill=tk.X, pady=10)
            
            tk.Label(
                row_e2,
                text="API 密钥:",
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
                bg=ModernStyle.BG_SECONDARY,
                fg=ModernStyle.TEXT_PRIMARY,
                width=12,
                anchor="w"
            ).pack(side=tk.LEFT)
            
            self.setting_embed_key = tk.Entry(
                row_e2,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
                bg=ModernStyle.BG_MAIN,
                relief="flat",
                width=45,
                show="•"
            )
            self.setting_embed_key.pack(side=tk.LEFT, padx=12, ipady=8)
            
            # 模型选择
            row_e3 = tk.Frame(self.embed_frame, bg=ModernStyle.BG_SECONDARY)
            row_e3.pack(fill=tk.X, pady=10)
            
            tk.Label(
                row_e3,
                text="模型名称:",
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
                bg=ModernStyle.BG_SECONDARY,
                fg=ModernStyle.TEXT_PRIMARY,
                width=12,
                anchor="w"
            ).pack(side=tk.LEFT)
            
            self.setting_embed_model = ttk.Combobox(
                row_e3,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
                width=35,
                values=["text-embedding-3-small", "text-embedding-3-large", "BAAI/bge-m3"]
            )
            self.setting_embed_model.pack(side=tk.LEFT, padx=12)
    
    def _on_llm_provider_change(self, event=None):
        """切换供应商时自动填充"""
        provider = self.llm_provider_var.get()
        
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
    
    def _fetch_llm_models(self):
        """拉取语言模型列表"""
        api_base = self.setting_llm_base.get().strip()
        api_key = self.setting_llm_key.get().strip()
        
        if not api_base or not api_key:
            messagebox.showwarning("提示", "请先填写 API 地址和密钥")
            return
        
        def do_fetch():
            try:
                from openai import OpenAI
                client = OpenAI(base_url=api_base, api_key=api_key)
                models = client.models.list()
                
                model_ids = [m.id for m in models.data]
                model_ids.sort()
                
                self._safe_update(lambda: self.setting_llm_model.config(values=model_ids))
                self._safe_update(lambda: messagebox.showinfo("成功", f"✅ 获取到 {len(model_ids)} 个模型"))
            except Exception as e:
                self._safe_update(lambda: messagebox.showerror("失败", f"❌ 拉取失败:\n{str(e)}"))
        
        self._run_in_thread(do_fetch)
    
    def _fetch_embed_models(self):
        """拉取嵌入模型列表"""
        if self.use_same_api.get():
            api_base = self.setting_llm_base.get().strip()
            api_key = self.setting_llm_key.get().strip()
        else:
            api_base = self.setting_embed_base.get().strip()
            api_key = self.setting_embed_key.get().strip()
        
        if not api_base or not api_key:
            messagebox.showwarning("提示", "请先填写 API 地址和密钥")
            return
        
        def do_fetch():
            try:
                from openai import OpenAI
                client = OpenAI(base_url=api_base, api_key=api_key)
                models = client.models.list()
                
                # 过滤嵌入模型
                embed_ids = [m.id for m in models.data if 'embed' in m.id.lower() or 'bge' in m.id.lower()]
                embed_ids.sort()
                
                if embed_ids:
                    self._safe_update(lambda: self.setting_embed_model.config(values=embed_ids))
                    self._safe_update(lambda: messagebox.showinfo("成功", f"✅ 获取到 {len(embed_ids)} 个嵌入模型"))
                else:
                    self._safe_update(lambda: messagebox.showinfo("提示", "未找到嵌入模型，请手动输入"))
            except Exception as e:
                self._safe_update(lambda: messagebox.showerror("失败", f"❌ 拉取失败:\n{str(e)}"))
        
        self._run_in_thread(do_fetch)
    
    def _test_llm_connection(self):
        """测试语言模型连接"""
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
                self._safe_update(lambda: self.llm_status.config(text="● 已连接", fg=ModernStyle.SUCCESS))
                self._safe_update(lambda: messagebox.showinfo("成功", "✅ 连接成功！API 配置有效。"))
            except Exception as e:
                self._safe_update(lambda: self.llm_status.config(text="● 连接失败", fg=ModernStyle.ERROR))
                self._safe_update(lambda: messagebox.showerror("失败", f"❌ 连接失败:\n{str(e)}"))
        
        self._run_in_thread(do_test)
    
    def _browse_directory(self, target: str):
        """浏览选择目录"""
        directory = filedialog.askdirectory(title="选择目录")
        if directory:
            if target == "data_dir":
                self.setting_data_dir.delete(0, tk.END)
                self.setting_data_dir.insert(0, directory)
            elif target == "workspace_dir":
                self.setting_workspace_dir.delete(0, tk.END)
                self.setting_workspace_dir.insert(0, directory)
    
    def _update_storage_info(self):
        """更新存储位置信息显示"""
        try:
            from config.settings import settings
            info_text = f"📍 当前数据目录: {settings.data_dir}\n📍 当前工作区: {settings.workspace_dir}"
            self.storage_info_label.config(text=info_text)
            
            # 填充输入框
            self.setting_data_dir.delete(0, tk.END)
            self.setting_data_dir.insert(0, settings.data_dir)
            self.setting_workspace_dir.delete(0, tk.END)
            self.setting_workspace_dir.insert(0, settings.workspace_dir)
        except Exception:
            pass
    
    def _reset_settings(self):
        """重置设置"""
        if messagebox.askyesno("确认", "确定要重置所有设置吗？"):
            self.setting_llm_base.delete(0, tk.END)
            self.setting_llm_key.delete(0, tk.END)
            self.setting_llm_model.set("")
            # 安全访问嵌入模型控件
            if hasattr(self, 'setting_embed_base') and hasattr(self.setting_embed_base, 'winfo_exists') and self.setting_embed_base.winfo_exists():
                self.setting_embed_base.delete(0, tk.END)
            if hasattr(self, 'setting_embed_key') and hasattr(self.setting_embed_key, 'winfo_exists') and self.setting_embed_key.winfo_exists():
                self.setting_embed_key.delete(0, tk.END)
            if hasattr(self, 'setting_embed_model'):
                self.setting_embed_model.set("")
            # 重置存储目录
            if hasattr(self, 'setting_data_dir'):
                self.setting_data_dir.delete(0, tk.END)
            if hasattr(self, 'setting_workspace_dir'):
                self.setting_workspace_dir.delete(0, tk.END)
            self.llm_provider_var.set("OpenAI 兼容")
            self.llm_status.config(text="● 未配置", fg=ModernStyle.WARNING)
    
    def _check_first_run(self):
        """首次运行检查 - 引导用户配置API"""
        try:
            from config.settings import settings
            if not settings.llm_api_key or not settings.llm_api_base:
                self.api_configured = False
                self._show_first_run_guide()
            else:
                self.api_configured = True
        except Exception:
            self.api_configured = False
            self._show_first_run_guide()
    
    def _show_first_run_guide(self):
        """显示首次使用引导"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("🎉 欢迎使用 EconPaper Pro")
        guide_window.geometry("550x450")
        guide_window.resizable(False, False)
        guide_window.configure(bg=ModernStyle.BG_MAIN)
        guide_window.transient(self.root)
        guide_window.grab_set()
        
        # 居中显示
        guide_window.update_idletasks()
        x = (guide_window.winfo_screenwidth() - 550) // 2
        y = (guide_window.winfo_screenheight() - 450) // 2
        guide_window.geometry(f"+{x}+{y}")
        
        # 内容
        content = tk.Frame(guide_window, bg=ModernStyle.BG_MAIN, padx=40, pady=30)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            content,
            text="🎉 欢迎使用 EconPaper Pro!",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XL, "bold"),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(pady=(0, 20))
        
        tk.Label(
            content,
            text="检测到您还未配置 AI 模型，请先完成以下设置：",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_SECONDARY
        ).pack(pady=(0, 25))
        
        # 步骤说明
        steps = [
            ("1️⃣", "准备 API 密钥", "从 OpenAI、DeepSeek 或硅基流动等平台获取"),
            ("2️⃣", "进入设置页面", "点击左侧「系统设置」"),
            ("3️⃣", "填写配置", "选择供应商 → 填写 API 密钥 → 保存"),
            ("4️⃣", "开始使用", "配置完成后即可使用所有功能"),
        ]
        
        for icon, title, desc in steps:
            step_frame = tk.Frame(content, bg=ModernStyle.BG_SECONDARY, padx=15, pady=12)
            step_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(
                step_frame,
                text=icon,
                font=(ModernStyle.FONT_FAMILY, 16),
                bg=ModernStyle.BG_SECONDARY
            ).pack(side=tk.LEFT, padx=(0, 12))
            
            text_frame = tk.Frame(step_frame, bg=ModernStyle.BG_SECONDARY)
            text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            tk.Label(
                text_frame,
                text=title,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
                bg=ModernStyle.BG_SECONDARY,
                fg=ModernStyle.TEXT_PRIMARY,
                anchor="w"
            ).pack(anchor="w")
            
            tk.Label(
                text_frame,
                text=desc,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
                bg=ModernStyle.BG_SECONDARY,
                fg=ModernStyle.TEXT_MUTED,
                anchor="w"
            ).pack(anchor="w")
        
        # 按钮
        btn_frame = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        btn_frame.pack(fill=tk.X, pady=(25, 0))
        
        def go_to_settings():
            guide_window.destroy()
            self._show_page("settings")
        
        ModernButton(
            btn_frame,
            text="前往设置",
            command=go_to_settings,
            width=150,
            height=45
        ).pack(side=tk.LEFT)
        
        tk.Button(
            btn_frame,
            text="稍后配置",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            bd=0,
            padx=25,
            pady=12,
            cursor="hand2",
            command=guide_window.destroy
        ).pack(side=tk.LEFT, padx=15)
    
    def _show_about_dialog(self):
        """显示关于对话框"""
        about_window = tk.Toplevel(self.root)
        about_window.title("关于 EconPaper Pro")
        about_window.geometry("450x380")
        about_window.resizable(False, False)
        about_window.configure(bg=ModernStyle.BG_MAIN)
        about_window.transient(self.root)
        about_window.grab_set()
        
        # 居中显示
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() - 450) // 2
        y = (about_window.winfo_screenheight() - 380) // 2
        about_window.geometry(f"+{x}+{y}")
        
        content = tk.Frame(about_window, bg=ModernStyle.BG_MAIN, padx=40, pady=30)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Logo
        tk.Label(
            content,
            text="📚",
            font=(ModernStyle.FONT_FAMILY, 48),
            bg=ModernStyle.BG_MAIN
        ).pack()
        
        tk.Label(
            content,
            text="EconPaper Pro",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XL, "bold"),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY
        ).pack(pady=(10, 5))
        
        tk.Label(
            content,
            text=f"版本 {VERSION}",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_SECONDARY
        ).pack()
        
        tk.Label(
            content,
            text="经管学术论文智能助手",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_MUTED
        ).pack(pady=(15, 20))
        
        # 功能列表
        features = "✅ 论文诊断  ✅ 深度优化  ✅ 降重降AI\n✅ 学术搜索  ✅ 退修助手  ✅ 期刊过滤"
        tk.Label(
            content,
            text=features,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY,
            justify="center"
        ).pack(pady=(0, 20))
        
        # 链接
        link_frame = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        link_frame.pack()
        
        tk.Label(
            link_frame,
            text="📖 使用帮助",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.PRIMARY,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=15)
        
        tk.Label(
            link_frame,
            text="🐛 反馈问题",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.PRIMARY,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=15)
        
        # 关闭按钮
        tk.Button(
            content,
            text="关闭",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            bd=0,
            padx=30,
            pady=10,
            cursor="hand2",
            command=about_window.destroy
        ).pack(pady=(20, 0))
    
    def _check_api_before_action(self, action_name: str) -> bool:
        """执行操作前检查 API 配置"""
        if not self.api_configured:
            try:
                from config.settings import settings
                if settings.llm_api_key and settings.llm_api_base:
                    self.api_configured = True
                    return True
            except Exception:
                pass
            
            result = messagebox.askyesno(
                "需要配置 API",
                f"使用「{action_name}」功能需要先配置 AI 模型。\n\n是否现在前往设置？"
            )
            if result:
                self._show_page("settings")
            return False
        return True
    
    # ==================== 核心功能方法 ====================
    
    def _export_result(self, content: str, default_name: str):
        """导出结果到文件"""
        if not content or not content.strip():
            messagebox.showwarning("提示", "没有可导出的内容")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="导出结果",
            defaultextension=".txt",
            filetypes=[
                ("文本文件", "*.txt"),
                ("Markdown", "*.md"),
                ("所有文件", "*.*")
            ],
            initialfile=f"{default_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("成功", f"✅ 已导出到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("失败", f"导出失败: {e}")
    
    def _copy_to_clipboard(self, content: str):
        """复制内容到剪贴板"""
        if not content or not content.strip():
            messagebox.showwarning("提示", "没有可复制的内容")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(content.strip())
        messagebox.showinfo("成功", "✅ 已复制到剪贴板")
    
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
        """设置结果文本"""
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
        if not self._check_api_before_action("论文诊断"):
            return
        
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
        if not self._check_api_before_action("深度优化"):
            return
        
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
        if not self._check_api_before_action("智能降重"):
            return
        
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
        if not self._check_api_before_action("降AI痕迹"):
            return
        
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
        if not self._check_api_before_action("深度处理"):
            return
        
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

{dedup_engine.get_dedup_report(dedup_result)}

{deai_engine.get_report(deai_result)}
"""
                self._set_result(self.dedup_output, result_text)
                
            except Exception as e:
                self._set_result(self.dedup_output, f"处理失败: {e}")
            finally:
                self._safe_update(lambda: self.progress_indicators["dedup"].stop())
        
        self._run_in_thread(do_both)
    
    def _ai_expand_keywords(self):
        """AI智能扩展关键词"""
        if not self._check_api_before_action("AI扩展关键词"):
            return
        
        query = self.search_query.get().strip()
        if not query:
            messagebox.showwarning("提示", "请先输入初始关键词")
            return
        
        self.progress_indicators["search"].start("AI正在扩展关键词...")
        
        def do_expand():
            try:
                from openai import OpenAI
                from config.settings import settings
                
                client = OpenAI(base_url=settings.llm_api_base, api_key=settings.llm_api_key)
                
                prompt = f"""作为学术研究助手，请帮我扩展以下研究主题的关键词，用于文献检索。

研究主题：{query}

请提供：
1. 中文关键词扩展（5-8个相关术语，用逗号分隔）
2. 英文关键词扩展（5-8个相关术语，用逗号分隔）
3. 推荐的搜索组合（2-3种）

要求：关键词要学术化、专业化，适合在学术数据库中检索。"""

                response = client.chat.completions.create(
                    model=settings.llm_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                
                result = response.choices[0].message.content
                self._safe_update(lambda: messagebox.showinfo(
                    "AI关键词扩展",
                    f"原始关键词：{query}\n\n{result}"
                ))
                
            except Exception as e:
                self._safe_update(lambda: messagebox.showerror("失败", f"AI扩展失败: {e}"))
            finally:
                self._safe_update(lambda: self.progress_indicators["search"].stop())
        
        self._run_in_thread(do_expand)
    
    def _run_search(self):
        """运行学术搜索 - v2.0 使用可靠的学术API"""
        query = self.search_query.get().strip()
        if not query:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return
        
        source = self.search_source.get()
        limit = int(self.search_limit.get()) if hasattr(self, 'search_limit') else 15
        enable_ai = self.enable_ai_filter.get() if hasattr(self, 'enable_ai_filter') else False
        
        # 获取年份筛选
        year_from = None
        try:
            year_str = self.search_year_from.get().strip()
            if year_str:
                year_from = int(year_str)
        except (ValueError, AttributeError):
            pass
        
        self.progress_indicators["search"].start(f"正在搜索 {source}...")
        self._set_result(self.search_result, "")
        self._safe_update(lambda: self.search_status_label.config(text="搜索中..."))
        
        def do_search():
            try:
                all_results = []
                errors = []
                
                # 根据选择的来源搜索
                # 英文文献数据源
                if source in ["英文文献", "Semantic Scholar"]:
                    self._safe_update(lambda: self.progress_indicators["search"].update_text("正在搜索 Semantic Scholar..."))
                    try:
                        from knowledge.search.semantic_scholar import search_semantic_scholar
                        ss_results = search_semantic_scholar(query, limit=limit, year_from=year_from)
                        
                        for r in ss_results:
                            paper = {
                                'title': r.title,
                                'authors': r.authors,
                                'year': r.year,
                                'abstract': r.abstract,
                                'url': r.link,
                                'citations': r.citations,
                                'journal': r.venue,
                                'doi': r.doi,
                                'source': 'Semantic Scholar'
                            }
                            all_results.append(paper)
                        
                    except Exception as e:
                        errors.append(f"Semantic Scholar: {e}")
                        print(f"Semantic Scholar 搜索失败: {e}")
                
                if source in ["英文文献", "OpenAlex"]:
                    self._safe_update(lambda: self.progress_indicators["search"].update_text("正在搜索 OpenAlex..."))
                    try:
                        from knowledge.search.openalex import search_openalex
                        oa_results = search_openalex(query, limit=limit, year_from=year_from)
                        
                        for r in oa_results:
                            paper = {
                                'title': r.title,
                                'authors': r.authors,
                                'year': r.year,
                                'abstract': r.abstract,
                                'url': r.link,
                                'citations': r.citations,
                                'journal': r.venue,
                                'doi': r.doi,
                                'open_access': getattr(r, 'open_access', False),
                                'source': 'OpenAlex'
                            }
                            all_results.append(paper)
                        
                    except Exception as e:
                        errors.append(f"OpenAlex: {e}")
                        print(f"OpenAlex 搜索失败: {e}")
                
                # 中文文献数据源
                if source in ["中文文献", "百度学术"]:
                    self._safe_update(lambda: self.progress_indicators["search"].update_text("正在搜索中文文献..."))
                    try:
                        from knowledge.search.cnki import search_cnki
                        cnki_results = search_cnki(query, limit=limit)
                        
                        for r in cnki_results:
                            paper = {
                                'title': r.title,
                                'authors': r.authors,
                                'year': r.year,
                                'abstract': r.abstract,
                                'url': r.link,
                                'citations': r.citations,
                                'journal': r.source,
                                'doi': '',
                                'source': r.database
                            }
                            all_results.append(paper)
                        
                    except Exception as e:
                        errors.append(f"中文文献: {e}")
                        print(f"中文文献搜索失败: {e}")
                
                # 获取期刊筛选设置
                filter_cssci = self.filter_cssci.get() if hasattr(self, 'filter_cssci') else False
                filter_ssci = self.filter_ssci.get() if hasattr(self, 'filter_ssci') else False
                show_rank = self.show_rank_info.get() if hasattr(self, 'show_rank_info') else True
                
                # 应用期刊级别筛选
                if all_results and (filter_cssci or filter_ssci or show_rank):
                    self._safe_update(lambda: self.progress_indicators["search"].update_text("正在查询期刊级别..."))
                    try:
                        from knowledge.search.journal_rank import enrich_with_rank_info, filter_by_quality
                        
                        # 添加期刊级别信息
                        if show_rank:
                            all_results = enrich_with_rank_info(all_results)
                        
                        # 筛选高质量期刊
                        if filter_cssci or filter_ssci:
                            original_count = len(all_results)
                            all_results = filter_by_quality(
                                all_results,
                                require_cssci=filter_cssci,
                                require_ssci=filter_ssci,
                                min_ssci_quartile="Q2" if filter_ssci else ""
                            )
                            filtered_count = original_count - len(all_results)
                            if filtered_count > 0:
                                print(f"期刊筛选: 过滤了 {filtered_count} 篇非核心期刊论文")
                    except Exception as e:
                        print(f"期刊筛选失败: {e}")
                
                if not all_results:
                    error_msg = "未找到相关文献。\n\n"
                    if errors:
                        error_msg += "错误信息:\n" + "\n".join(errors)
                    error_msg += "\n\n💡 建议:\n1. 尝试使用英文关键词\n2. 使用更通用的学术术语\n3. 检查网络连接"
                    self._set_result(self.search_result, error_msg)
                    self._safe_update(lambda: self.search_status_label.config(text="未找到结果"))
                    return
                
                # 去重（根据标题）
                seen_titles = set()
                unique_results = []
                for paper in all_results:
                    title_key = paper['title'].lower().strip()
                    if title_key not in seen_titles:
                        seen_titles.add(title_key)
                        unique_results.append(paper)
                all_results = unique_results
                
                # AI智能筛选（如果启用且结果数量足够多）
                if enable_ai and len(all_results) > limit:
                    self._safe_update(lambda: self.progress_indicators["search"].update_text("AI正在筛选最相关文献..."))
                    all_results = self._ai_filter_papers(query, all_results, limit)
                
                # 按引用数排序
                all_results.sort(key=lambda x: x.get('citations', 0) or 0, reverse=True)
                
                # 格式化输出
                formatted = self._format_search_results(all_results, enable_ai)
                self._set_result(self.search_result, formatted)
                
                # 更新状态
                status_text = f"共 {len(all_results)} 篇文献"
                self._safe_update(lambda: self.search_status_label.config(text=status_text))
                
                # 保存搜索结果供其他功能使用
                self.last_search_results = all_results
                
            except Exception as e:
                self._set_result(self.search_result, f"搜索失败: {e}\n\n请检查网络连接后重试。")
                self._safe_update(lambda: self.search_status_label.config(text="搜索失败"))
            finally:
                self._safe_update(lambda: self.progress_indicators["search"].stop())
        
        self._run_in_thread(do_search)
    
    def _generate_literature_review(self):
        """基于搜索结果生成文献综述"""
        if not self._check_api_before_action("生成文献综述"):
            return
        
        if not hasattr(self, 'last_search_results') or not self.last_search_results:
            messagebox.showwarning("提示", "请先搜索文献")
            return
        
        self.progress_indicators["search"].start("AI正在生成文献综述...")
        
        def do_generate():
            try:
                from openai import OpenAI
                from config.settings import settings
                
                client = OpenAI(base_url=settings.llm_api_base, api_key=settings.llm_api_key)
                
                # 构建文献摘要
                papers_text = ""
                for i, p in enumerate(self.last_search_results[:15], 1):
                    title = p.get('title', '无标题')
                    authors = p.get('authors', '未知')
                    year = p.get('year', '')
                    abstract = p.get('abstract', '')[:300]
                    papers_text += f"{i}. {title} ({authors}, {year})\n摘要：{abstract}\n\n"
                
                prompt = f"""请基于以下学术文献，生成一段学术论文风格的文献综述（约500-800字）。

要求：
1. 采用学术论文的写作风格，客观、严谨
2. 综合多篇文献的观点，进行归纳和对比
3. 使用正确的引用格式（作者，年份）
4. 指出研究的共识与分歧
5. 提出未来研究方向

文献列表：
{papers_text}

请生成文献综述："""

                response = client.chat.completions.create(
                    model=settings.llm_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                review = response.choices[0].message.content
                if review:
                    current = self.search_result.get("1.0", tk.END)
                    result_text = f"""{'='*60}
📝 AI 生成的文献综述
{'='*60}

{review}

{'='*60}
原始搜索结果
{'='*60}

{current}"""
                    self._set_result(self.search_result, result_text)
                
            except Exception as e:
                self._safe_update(lambda: messagebox.showerror("失败", f"生成文献综述失败: {e}"))
            finally:
                self._safe_update(lambda: self.progress_indicators["search"].stop())
        
        self._run_in_thread(do_generate)
    
    def _generate_citations(self):
        """生成引用格式"""
        if not hasattr(self, 'last_search_results') or not self.last_search_results:
            messagebox.showwarning("提示", "请先搜索文献")
            return
        
        # 创建选择窗口
        cite_window = tk.Toplevel(self.root)
        cite_window.title("选择引用格式")
        cite_window.geometry("600x500")
        cite_window.configure(bg=ModernStyle.BG_MAIN)
        cite_window.transient(self.root)
        
        # 居中显示
        cite_window.update_idletasks()
        x = (cite_window.winfo_screenwidth() - 600) // 2
        y = (cite_window.winfo_screenheight() - 500) // 2
        cite_window.geometry(f"+{x}+{y}")
        
        content = tk.Frame(cite_window, bg=ModernStyle.BG_MAIN, padx=25, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            content,
            text="选择引用格式",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LG, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(0, 15))
        
        style_var = tk.StringVar(value="apa")
        styles = [
            ("APA 格式", "apa"),
            ("GB/T 7714 格式（中国国标）", "gb"),
            ("MLA 格式", "mla"),
            ("Chicago 格式", "chicago")
        ]
        
        for text, value in styles:
            tk.Radiobutton(
                content,
                text=text,
                variable=style_var,
                value=value,
                bg=ModernStyle.BG_MAIN,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM)
            ).pack(anchor="w", pady=3)
        
        # 引用预览区
        tk.Label(
            content,
            text="引用预览：",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD, "bold"),
            bg=ModernStyle.BG_MAIN
        ).pack(anchor="w", pady=(20, 10))
        
        preview_text = scrolledtext.ScrolledText(
            content,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            height=15,
            wrap=tk.WORD,
            bg=ModernStyle.BG_SECONDARY
        )
        preview_text.pack(fill=tk.BOTH, expand=True)
        
        def update_preview(*args):
            style = style_var.get()
            citations = []
            
            for i, p in enumerate(self.last_search_results[:20], 1):
                authors = p.get('authors', '未知作者')
                year = p.get('year', '')
                title = p.get('title', '无标题')
                journal = p.get('journal', '')
                doi = p.get('doi', '')
                
                if style == "apa":
                    cite = f"{authors} ({year}). {title}."
                    if journal:
                        cite += f" {journal}."
                    if doi:
                        cite += f" https://doi.org/{doi}"
                elif style == "gb":
                    cite = f"[{i}] {authors}. {title}[J]. {journal}, {year}."
                elif style == "mla":
                    cite = f'{authors}. "{title}." {journal}, {year}.'
                elif style == "chicago":
                    cite = f'{authors}. "{title}." {journal} ({year}).'
                    if doi:
                        cite += f" https://doi.org/{doi}."
                else:
                    cite = f"{authors} ({year}). {title}. {journal}."
                
                citations.append(cite)
            
            preview_text.delete("1.0", tk.END)
            preview_text.insert("1.0", "\n\n".join(citations))
        
        style_var.trace("w", update_preview)
        update_preview()
        
        # 按钮
        btn_frame = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        def copy_citations():
            self.root.clipboard_clear()
            self.root.clipboard_append(preview_text.get("1.0", tk.END).strip())
            messagebox.showinfo("成功", "✅ 引用已复制到剪贴板")
        
        ModernButton(
            btn_frame,
            text="📋 复制引用",
            command=copy_citations,
            width=120,
            height=40
        ).pack(side=tk.LEFT)
        
        tk.Button(
            btn_frame,
            text="关闭",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_SECONDARY,
            bd=0,
            padx=20,
            pady=10,
            command=cite_window.destroy
        ).pack(side=tk.LEFT, padx=15)
    
    def _filter_by_journal_rank(self, papers: list, source_type: str, show_rank: bool) -> list:
        """根据期刊级别过滤论文
        
        Args:
            papers: 论文列表
            source_type: "chinese" 或 "english"
            show_rank: 是否显示期刊级别信息
        
        Returns:
            过滤后的论文列表
        """
        try:
            from knowledge.search.journal_rank import check_journal_rank, is_high_quality_journal, format_rank_info
            
            filtered = []
            for paper in papers:
                journal = paper.get("journal", "")
                if not journal:
                    # 如果没有期刊信息，暂时保留
                    filtered.append(paper)
                    continue
                
                rank = check_journal_rank(journal)
                
                if is_high_quality_journal(rank, source_type):
                    if show_rank and rank:
                        paper["rank_info"] = format_rank_info(rank)
                    filtered.append(paper)
            
            # 如果所有论文都被过滤掉，返回前5条原始结果
            return filtered if filtered else papers[:5]
            
        except Exception as e:
            print(f"期刊级别查询失败: {e}")
            return papers
    
    def _ai_filter_papers(self, query: str, papers: list, top_k: int) -> list:
        """AI智能筛选文献"""
        try:
            from openai import OpenAI
            from config.settings import settings
            
            client = OpenAI(base_url=settings.llm_api_base, api_key=settings.llm_api_key)
            
            # 构建文献摘要
            papers_text = ""
            for i, p in enumerate(papers[:30], 1):  # 最多30篇供筛选
                title = p.get('title', '无标题')
                abstract = p.get('abstract', p.get('snippet', '无摘要'))[:150]
                papers_text += f"{i}. {title}\n   摘要：{abstract}\n\n"
            
            prompt = f"""作为学术研究助手，请从以下文献中筛选出与研究主题最相关的 {top_k} 篇。

研究主题：{query}

文献列表：
{papers_text}

请仅返回最相关的文献序号（用逗号分隔，如：1,5,8），从最相关到较相关排序。"""

            response = client.chat.completions.create(
                model=settings.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100
            )
            
            content = response.choices[0].message.content
            if content is None:
                return papers[:top_k]
            selected = content.strip()
            indices = [int(x.strip()) - 1 for x in selected.split(',') if x.strip().isdigit()]
            
            return [papers[i] for i in indices if 0 <= i < len(papers)]
            
        except Exception:
            return papers[:top_k]
    
    def _format_search_results(self, results: list, ai_filtered: bool) -> str:
        """格式化搜索结果"""
        if not results:
            return "未找到相关文献"
        
        output = []
        output.append(f"{'='*60}")
        output.append(f"📚 检索结果：共找到 {len(results)} 篇文献" + (" (AI智能筛选)" if ai_filtered else ""))
        output.append(f"{'='*60}\n")
        
        for i, paper in enumerate(results, 1):
            source = paper.get('source', '未知来源')
            title = paper.get('title', '无标题')
            authors = paper.get('authors', '未知作者')
            year = paper.get('year', '未知年份')
            journal = paper.get('journal', paper.get('venue', ''))
            citations = paper.get('citations', 0)
            abstract = paper.get('abstract', paper.get('snippet', '无摘要'))
            url = paper.get('url', '')
            
            output.append(f"【{i}】{title}")
            output.append(f"    来源: {source}")
            output.append(f"    作者: {authors}")
            output.append(f"    发表: {year}" + (f" | {journal}" if journal else ""))
            
            # 显示期刊级别
            rank_info = paper.get("rank_info", "")
            if rank_info:
                output.append(f"    📊 级别: {rank_info}")
            
            if citations:
                output.append(f"    引用: {citations}")
            output.append(f"    摘要: {abstract[:250]}...")
            if url:
                output.append(f"    链接: {url}")
            output.append("")
        
        output.append(f"\n{'='*60}")
        output.append("💡 提示：点击「深度优化」→「引用文献」将搜索结果融入论文")
        output.append("💡 提示：点击「退修助手」→「找支撑文献」获取审稿回应所需参考")
        
        return "\n".join(output)
    
    def _recommend_literature(self):
        """根据论文内容智能推荐文献"""
        content = self.diag_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("提示", "请先输入论文内容")
            return
        
        self.progress_indicators["diagnose"].start("AI正在分析论文并推荐文献...")
        
        def do_recommend():
            try:
                from openai import OpenAI
                from config.settings import settings
                
                client = OpenAI(base_url=settings.llm_api_base, api_key=settings.llm_api_key)
                
                # 提取关键词
                prompt = f"""请分析以下论文内容，提取3-5个核心研究关键词用于文献检索：

{content[:2000]}

请以逗号分隔的形式返回关键词，例如：数字经济,企业创新,全要素生产率"""

                response = client.chat.completions.create(
                    model=settings.llm_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=100
                )
                
                keywords = response.choices[0].message.content
                if keywords:
                    keywords = keywords.strip()
                    
                    # 自动切换到搜索页面并执行搜索
                    self._safe_update(lambda: self.search_query.delete(0, tk.END))
                    self._safe_update(lambda: self.search_query.insert(0, keywords))
                    self._safe_update(lambda: self._show_page("search"))
                    self._safe_update(lambda: self.progress_indicators["diagnose"].stop())
                    
                    # 延迟执行搜索
                    self.root.after(500, self._run_search)
                    
            except Exception as e:
                self._safe_update(lambda: messagebox.showerror("失败", f"推荐失败: {e}"))
                self._safe_update(lambda: self.progress_indicators["diagnose"].stop())
        
        self._run_in_thread(do_recommend)
    
    def _find_supporting_literature(self):
        """根据审稿意见找支撑文献"""
        comments = self.rev_comments.get("1.0", tk.END).strip()
        if not comments:
            messagebox.showwarning("提示", "请先输入审稿意见")
            return
        
        self.progress_indicators["revision"].start("AI正在分析审稿意见...")
        
        def do_find():
            try:
                from openai import OpenAI
                from config.settings import settings
                
                client = OpenAI(base_url=settings.llm_api_base, api_key=settings.llm_api_key)
                
                prompt = f"""请分析以下审稿意见，提取审稿人关注的核心问题，并生成3-5个用于查找支撑文献的关键词：

审稿意见：
{comments[:1500]}

请以逗号分隔的形式返回搜索关键词，例如：内生性问题,工具变量,稳健性检验"""

                response = client.chat.completions.create(
                    model=settings.llm_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=100
                )
                
                keywords = response.choices[0].message.content
                if keywords:
                    keywords = keywords.strip()
                    
                    # 自动切换到搜索页面
                    self._safe_update(lambda: self.search_query.delete(0, tk.END))
                    self._safe_update(lambda: self.search_query.insert(0, keywords))
                    self._safe_update(lambda: self._show_page("search"))
                    self._safe_update(lambda: self.progress_indicators["revision"].stop())
                    
                    # 延迟执行搜索
                    self.root.after(500, self._run_search)
                    
            except Exception as e:
                self._safe_update(lambda: messagebox.showerror("失败", f"查找失败: {e}"))
                self._safe_update(lambda: self.progress_indicators["revision"].stop())
        
        self._run_in_thread(do_find)
    
    def _run_revision(self):
        """运行退修处理"""
        if not self._check_api_before_action("退修助手"):
            return
        
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
            
            # 安全访问嵌入模型配置控件
            if hasattr(self, 'setting_embed_base') and hasattr(self.setting_embed_base, 'winfo_exists') and self.setting_embed_base.winfo_exists():
                self.setting_embed_base.delete(0, tk.END)
                self.setting_embed_base.insert(0, settings.embedding_api_base or "")
            if hasattr(self, 'setting_embed_key') and hasattr(self.setting_embed_key, 'winfo_exists') and self.setting_embed_key.winfo_exists():
                self.setting_embed_key.delete(0, tk.END)
                self.setting_embed_key.insert(0, settings.embedding_api_key or "")
            if hasattr(self, 'setting_embed_model'):
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
                # 安全访问嵌入模型配置控件
                embed_base = self.setting_embed_base.get() if (hasattr(self, 'setting_embed_base') and hasattr(self.setting_embed_base, 'winfo_exists') and self.setting_embed_base.winfo_exists()) else self.setting_llm_base.get()
                embed_key = self.setting_embed_key.get() if (hasattr(self, 'setting_embed_key') and hasattr(self.setting_embed_key, 'winfo_exists') and self.setting_embed_key.winfo_exists()) else self.setting_llm_key.get()
            
            # 获取存储目录配置
            data_dir = self.setting_data_dir.get().strip() if hasattr(self, 'setting_data_dir') else ""
            workspace_dir = self.setting_workspace_dir.get().strip() if hasattr(self, 'setting_workspace_dir') else ""
            
            lines = [
                f"# EconPaper Pro 配置",
                f"",
                f"# 语言模型 (LLM) 配置",
                f"LLM_API_BASE={self.setting_llm_base.get()}",
                f"LLM_API_KEY={self.setting_llm_key.get()}",
                f"LLM_MODEL={self.setting_llm_model.get()}",
                f"",
                f"# 嵌入模型 (Embedding) 配置",
                f"EMBEDDING_API_BASE={embed_base}",
                f"EMBEDDING_API_KEY={embed_key}",
                f"EMBEDDING_MODEL={self.setting_embed_model.get()}",
                f"",
                f"# 存储目录配置 (避免占用C盘)",
                f"DATA_DIR={data_dir}",
                f"WORKSPACE_DIR={workspace_dir}",
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
