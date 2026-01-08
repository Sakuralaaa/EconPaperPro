# -*- coding: utf-8 -*-
"""
EconPaper Pro - 公共 UI 组件模块
提供可复用的现代化 UI 组件
v2.5 新增：流式输出、精确进度条
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Callable, List, Tuple, Generator
import threading
import queue
import time


class ModernStyle:
    """现代简约风格配置 - 支持深色模式 (P3)"""
    
    IS_DARK = False
    
    # 基础色（不随主题变化）
    PRIMARY = "#2563EB"
    PRIMARY_DARK = "#1D4ED8"
    PRIMARY_HOVER = "#3B82F6"
    
    # 动态色
    PRIMARY_LIGHT = "#DBEAFE"
    SUCCESS = "#10B981"
    SUCCESS_LIGHT = "#D1FAE5"
    WARNING = "#F59E0B"
    WARNING_LIGHT = "#FEF3C7"
    ERROR = "#EF4444"
    ERROR_LIGHT = "#FEE2E2"
    INFO = "#6366F1"
    INFO_LIGHT = "#E0E7FF"
    
    BG_MAIN = "#FFFFFF"
    BG_SECONDARY = "#F8FAFC"
    BG_SIDEBAR = "#F1F5F9"
    BG_CARD = "#FFFFFF"
    BG_HOVER = "#E2E8F0"
    BG_INPUT = "#F8FAFC"
    BG_DISABLED = "#E5E7EB"
    
    TEXT_PRIMARY = "#0F172A"
    TEXT_SECONDARY = "#64748B"
    TEXT_MUTED = "#94A3B8"
    TEXT_LIGHT = "#FFFFFF"
    TEXT_DISABLED = "#9CA3AF"
    
    BORDER = "#E2E8F0"
    BORDER_FOCUS = "#2563EB"
    BORDER_ERROR = "#EF4444"
    
    TAB_BG = "#F1F5F9"
    TAB_ACTIVE_BG = "#FFFFFF"
    TAB_BORDER = "#E2E8F0"
    TAB_HOVER_BG = "#E2E8F0"

    @classmethod
    def set_dark_mode(cls, is_dark: bool):
        """切换深色模式"""
        cls.IS_DARK = is_dark
        if is_dark:
            cls.PRIMARY_LIGHT = "#1E3A8A"
            cls.SUCCESS_LIGHT = "#064E3B"
            cls.WARNING_LIGHT = "#78350F"
            cls.ERROR_LIGHT = "#7F1D1D"
            cls.INFO_LIGHT = "#312E81"
            
            cls.BG_MAIN = "#0F172A"
            cls.BG_SECONDARY = "#1E293B"
            cls.BG_SIDEBAR = "#020617"
            cls.BG_CARD = "#1E293B"
            cls.BG_HOVER = "#334155"
            cls.BG_INPUT = "#1E293B"
            cls.BG_DISABLED = "#334155"
            
            cls.TEXT_PRIMARY = "#F8FAFC"
            cls.TEXT_SECONDARY = "#CBD5E1"
            cls.TEXT_MUTED = "#64748B"
            cls.TEXT_DISABLED = "#475569"
            
            cls.BORDER = "#334155"
            cls.TAB_BG = "#020617"
            cls.TAB_ACTIVE_BG = "#0F172A"
            cls.TAB_BORDER = "#334155"
            cls.TAB_HOVER_BG = "#1E293B"
        else:
            # 恢复浅色模式
            cls.PRIMARY_LIGHT = "#DBEAFE"
            cls.SUCCESS_LIGHT = "#D1FAE5"
            cls.WARNING_LIGHT = "#FEF3C7"
            cls.ERROR_LIGHT = "#FEE2E2"
            cls.INFO_LIGHT = "#E0E7FF"
            
            cls.BG_MAIN = "#FFFFFF"
            cls.BG_SECONDARY = "#F8FAFC"
            cls.BG_SIDEBAR = "#F1F5F9"
            cls.BG_CARD = "#FFFFFF"
            cls.BG_HOVER = "#E2E8F0"
            cls.BG_INPUT = "#F8FAFC"
            cls.BG_DISABLED = "#E5E7EB"
            
            cls.TEXT_PRIMARY = "#0F172A"
            cls.TEXT_SECONDARY = "#64748B"
            cls.TEXT_MUTED = "#94A3B8"
            cls.TEXT_DISABLED = "#9CA3AF"
            
            cls.BORDER = "#E2E8F0"
            cls.TAB_BG = "#F1F5F9"
            cls.TAB_ACTIVE_BG = "#FFFFFF"
            cls.TAB_BORDER = "#E2E8F0"
            cls.TAB_HOVER_BG = "#E2E8F0"
    
    # 字体配置
    FONT_FAMILY = "Microsoft YaHei UI"
    FONT_SIZE_XXL = 22
    FONT_SIZE_XL = 18
    FONT_SIZE_LG = 14
    FONT_SIZE_MD = 12
    FONT_SIZE_SM = 11
    FONT_SIZE_XS = 10
    
    # 间距
    PADDING_XL = 30
    PADDING_LG = 20
    PADDING_MD = 15
    PADDING_SM = 10
    PADDING_XS = 5
    
    # 动画配置
    ANIMATION_DURATION = 150  # ms
    ANIMATION_STEPS = 8
    
    # 选项卡配置
    TAB_BG = "#F1F5F9"
    TAB_ACTIVE_BG = "#FFFFFF"
    TAB_BORDER = "#E2E8F0"
    TAB_HOVER_BG = "#E2E8F0"
    
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
        
        # Combobox
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
        
        # 选项卡样式
        style.configure("Modern.TNotebook",
            background=cls.BG_MAIN,
            borderwidth=0,
            padding=0
        )
        style.configure("Modern.TNotebook.Tab",
            background=cls.TAB_BG,
            foreground=cls.TEXT_SECONDARY,
            padding=(16, 10),
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_SM),
            borderwidth=0
        )
        style.map("Modern.TNotebook.Tab",
            background=[("selected", cls.TAB_ACTIVE_BG), ("active", cls.TAB_HOVER_BG)],
            foreground=[("selected", cls.TEXT_PRIMARY)],
            expand=[("selected", [0, 0, 0, 2])]
        )
        
        # Treeview 样式
        style.configure("Treeview",
            background=cls.BG_MAIN,
            fieldbackground=cls.BG_MAIN,
            foreground=cls.TEXT_PRIMARY,
            rowheight=35,
            borderwidth=0,
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_SM)
        )
        style.configure("Treeview.Heading",
            background=cls.BG_SIDEBAR,
            foreground=cls.TEXT_SECONDARY,
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_SM, "bold"),
            borderwidth=0
        )
        style.map("Treeview",
            background=[("selected", cls.PRIMARY_LIGHT)],
            foreground=[("selected", cls.PRIMARY)]
        )
        
        return style


class Tooltip:
    """工具提示组件"""
    
    def __init__(self, widget, text: str, delay: int = 500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.scheduled_id = None
        
        self.widget.bind("<Enter>", self._schedule_show)
        self.widget.bind("<Leave>", self._hide)
        self.widget.bind("<Button-1>", self._hide)
    
    def _schedule_show(self, event=None):
        """延迟显示工具提示"""
        self._cancel_scheduled()
        self.scheduled_id = self.widget.after(self.delay, self._show)
    
    def _cancel_scheduled(self):
        """取消已计划的显示"""
        if self.scheduled_id:
            self.widget.after_cancel(self.scheduled_id)
            self.scheduled_id = None
    
    def _show(self, event=None):
        """显示工具提示"""
        if self.tooltip_window:
            return
        
        # 获取位置
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # 创建内容
        frame = tk.Frame(
            tw,
            bg=ModernStyle.TEXT_PRIMARY,
            padx=1,
            pady=1
        )
        frame.pack()
        
        label = tk.Label(
            frame,
            text=self.text,
            bg="#1F2937",
            fg=ModernStyle.TEXT_LIGHT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            padx=8,
            pady=4,
            wraplength=250,
            justify="left"
        )
        label.pack()
    
    def _hide(self, event=None):
        """隐藏工具提示"""
        self._cancel_scheduled()
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def update_text(self, text: str):
        """更新提示文本"""
        self.text = text


class AnimatedProgressBar:
    """带动画效果的进度指示器 - 支持取消按钮"""
    
    def __init__(self, parent, text="处理中...", height=60):
        self.parent = parent
        self.height = height
        self.is_active = False
        self._animation_id = None
        self._pulse_position = 0
        self.cancel_callback = None
        
        # 创建容器
        self.frame = tk.Frame(parent, bg=ModernStyle.BG_MAIN, height=height)
        
        self.container = tk.Frame(self.frame, bg=ModernStyle.BG_MAIN, pady=10)
        self.container.pack(fill=tk.X, padx=20)
        
        # 状态行：文字 + 取消按钮
        self.status_row = tk.Frame(self.container, bg=ModernStyle.BG_MAIN)
        self.status_row.pack(fill=tk.X, pady=(0, 5))
        
        # 状态文本
        self.label = tk.Label(
            self.status_row,
            text=text,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_SECONDARY
        )
        self.label.pack(side=tk.LEFT)
        
        # 取消按钮
        self.cancel_btn = tk.Label(
            self.status_row,
            text="✕ 取消任务",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_MUTED,
            cursor="hand2",
            padx=10
        )
        self.cancel_btn.bind("<Button-1>", self._on_cancel)
        self.cancel_btn.bind("<Enter>", lambda e: self.cancel_btn.config(fg=ModernStyle.ERROR))
        self.cancel_btn.bind("<Leave>", lambda e: self.cancel_btn.config(fg=ModernStyle.TEXT_MUTED))
        
        # 进度条（使用 Canvas 实现脉冲动画）
        self.progress_canvas = tk.Canvas(
            self.container,
            height=6,
            bg=ModernStyle.BG_SECONDARY,
            highlightthickness=0
        )
        self.progress_canvas.pack(fill=tk.X)
        
    def start(self, text=None, on_cancel=None):
        """开始动画"""
        if text:
            self.label.config(text=text)
        
        self.cancel_callback = on_cancel
        if on_cancel:
            self.cancel_btn.pack(side=tk.RIGHT)
        else:
            self.cancel_btn.pack_forget()
            
        self.is_active = True
        
        # 显示进度条
        children = self.parent.winfo_children()
        if children:
            self.frame.pack(fill=tk.X, before=children[0])
        else:
            self.frame.pack(fill=tk.X)
        
        # 开始脉冲动画
        self._animate_pulse()
    
    def _animate_pulse(self):
        """脉冲动画效果"""
        if not self.is_active:
            return
        
        self.progress_canvas.delete("pulse")
        
        width = self.progress_canvas.winfo_width()
        if width < 10:
            width = 300
        
        pulse_width = 100
        x1 = self._pulse_position - pulse_width
        x2 = self._pulse_position
        
        # 创建渐变效果
        self.progress_canvas.create_rectangle(
            x1, 0, x2, 8,
            fill=ModernStyle.PRIMARY,
            outline="",
            tags="pulse"
        )
        
        self._pulse_position = (self._pulse_position + 8) % (width + pulse_width)
        
        self._animation_id = self.parent.after(30, self._animate_pulse)
    
    def stop(self):
        """停止动画"""
        self.is_active = False
        if self._animation_id:
            self.parent.after_cancel(self._animation_id)
            self._animation_id = None
        self.frame.pack_forget()
        self._pulse_position = 0
        self.cancel_callback = None
    
    def _on_cancel(self, event=None):
        """取消按钮点击"""
        if self.cancel_callback:
            self.cancel_callback()
            self.cancel_btn.config(text="正在取消...", fg=ModernStyle.TEXT_DISABLED)

    def update_text(self, text: str):
        """更新状态文字"""
        self.label.config(text=text)


class PreciseProgressBar(tk.Frame):
    """
    精确进度条组件 - 显示实际处理进度
    
    特性：
    - 显示处理进度百分比
    - 显示已处理/总计数
    - 预计剩余时间
    - 处理速度
    - 支持取消操作
    """
    
    def __init__(
        self,
        parent,
        text: str = "处理中...",
        show_eta: bool = True,
        show_speed: bool = True,
        height: int = 80
    ):
        super().__init__(parent, bg=ModernStyle.BG_MAIN, height=height)
        
        self.show_eta = show_eta
        self.show_speed = show_speed
        self.is_active = False
        self.cancel_callback = None
        
        # 时间追踪
        self._start_time = None
        self._current = 0
        self._total = 100
        self._speed_samples = []  # 用于计算平均速度
        
        # 容器
        self.container = tk.Frame(self, bg=ModernStyle.BG_MAIN, pady=10)
        self.container.pack(fill=tk.X, padx=20)
        
        # 第一行：状态文本 + 取消按钮
        self.status_row = tk.Frame(self.container, bg=ModernStyle.BG_MAIN)
        self.status_row.pack(fill=tk.X, pady=(0, 8))
        
        self.label = tk.Label(
            self.status_row,
            text=text,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_SECONDARY
        )
        self.label.pack(side=tk.LEFT)
        
        # 百分比标签
        self.percent_label = tk.Label(
            self.status_row,
            text="0%",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.PRIMARY
        )
        self.percent_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 取消按钮
        self.cancel_btn = tk.Label(
            self.status_row,
            text="✕ 取消",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_MUTED,
            cursor="hand2",
            padx=10
        )
        self.cancel_btn.bind("<Button-1>", self._on_cancel)
        self.cancel_btn.bind("<Enter>", lambda e: self.cancel_btn.config(fg=ModernStyle.ERROR))
        self.cancel_btn.bind("<Leave>", lambda e: self.cancel_btn.config(fg=ModernStyle.TEXT_MUTED))
        
        # 进度条
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self.container,
            variable=self.progress_var,
            maximum=100,
            style="Modern.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 8))
        
        # 第三行：详情信息
        self.detail_row = tk.Frame(self.container, bg=ModernStyle.BG_MAIN)
        self.detail_row.pack(fill=tk.X)
        
        # 进度详情（左侧）
        self.detail_label = tk.Label(
            self.detail_row,
            text="",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_MUTED
        )
        self.detail_label.pack(side=tk.LEFT)
        
        # ETA和速度（右侧）
        self.eta_label = tk.Label(
            self.detail_row,
            text="",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_MUTED
        )
        self.eta_label.pack(side=tk.RIGHT)
    
    def start(self, total: int = 100, text: Optional[str] = None, on_cancel: Optional[Callable] = None):
        """
        开始进度追踪
        
        Args:
            total: 总项目数
            text: 状态文本
            on_cancel: 取消回调
        """
        self._total = max(1, total)
        self._current = 0
        self._start_time = time.time()
        self._speed_samples = []
        
        if text:
            self.label.config(text=text)
        
        self.cancel_callback = on_cancel
        if on_cancel:
            self.cancel_btn.pack(side=tk.RIGHT)
        else:
            self.cancel_btn.pack_forget()
        
        self.progress_var.set(0)
        self.percent_label.config(text="0%")
        self.detail_label.config(text=f"0/{self._total}")
        self.eta_label.config(text="计算中...")
        
        self.is_active = True
        self.pack(fill=tk.X)
    
    def update(self, current: int, message: Optional[str] = None):
        """
        更新进度
        
        Args:
            current: 当前完成数
            message: 可选的状态消息
        """
        if not self.is_active:
            return
        
        self._current = current
        percent = min(100, (current / self._total) * 100)
        
        # 更新进度条
        self.progress_var.set(percent)
        self.percent_label.config(text=f"{percent:.0f}%")
        
        # 更新详情
        detail_text = f"{current}/{self._total}"
        if message:
            detail_text = f"{message} ({current}/{self._total})"
        self.detail_label.config(text=detail_text)
        
        # 计算速度和ETA
        if self._start_time and current > 0:
            elapsed = time.time() - self._start_time
            speed = current / elapsed if elapsed > 0 else 0
            
            # 记录速度样本（用于平滑）
            self._speed_samples.append(speed)
            if len(self._speed_samples) > 5:
                self._speed_samples.pop(0)
            avg_speed = sum(self._speed_samples) / len(self._speed_samples)
            
            # 计算剩余时间
            remaining = self._total - current
            eta_seconds = remaining / avg_speed if avg_speed > 0 else 0
            
            if self.show_eta and self.show_speed:
                eta_text = f"速度: {avg_speed:.1f}/s | 剩余: {self._format_time(eta_seconds)}"
            elif self.show_eta:
                eta_text = f"剩余: {self._format_time(eta_seconds)}"
            elif self.show_speed:
                eta_text = f"速度: {avg_speed:.1f}/s"
            else:
                eta_text = ""
            
            self.eta_label.config(text=eta_text)
    
    def increment(self, amount: int = 1, message: Optional[str] = None):
        """增加进度"""
        self.update(self._current + amount, message)
    
    def stop(self, success: bool = True):
        """停止进度追踪"""
        self.is_active = False
        
        if success and self._start_time:
            elapsed = time.time() - self._start_time
            self.eta_label.config(text=f"完成！用时: {self._format_time(elapsed)}")
            self.percent_label.config(text="100%", fg=ModernStyle.SUCCESS)
            self.progress_var.set(100)
        
        self.cancel_callback = None
        
        # 2秒后自动隐藏
        self.after(2000, self._hide)
    
    def _hide(self):
        """隐藏进度条"""
        self.pack_forget()
        self.percent_label.config(fg=ModernStyle.PRIMARY)
    
    def _on_cancel(self, event=None):
        """取消按钮点击"""
        if self.cancel_callback:
            self.cancel_callback()
            self.cancel_btn.config(text="正在取消...", fg=ModernStyle.TEXT_DISABLED)
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间"""
        if seconds < 60:
            return f"{int(seconds)}秒"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}分{secs}秒"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}时{minutes}分"


class StreamingTextOutput(tk.Frame):
    """
    流式文本输出组件 - 支持实时追加显示与高亮
    
    特性：
    - 支持逐字/逐块追加显示
    - 自动滚动到最新内容
    - 打字机效果（可选）
    - 差异对比高亮支持 (diff_tag)
    """
    
    def __init__(
        self,
        parent,
        height: int = 15,
        typewriter_effect: bool = False,
        typewriter_delay: int = 20,  # 毫秒
        **kwargs
    ):
        super().__init__(parent, bg=ModernStyle.BG_MAIN, **kwargs)
        
        self.typewriter_effect = typewriter_effect
        self.typewriter_delay = typewriter_delay
        self._streaming = False
        self._buffer = []
        self._typing_job = None
        
        # 边框容器
        self.border_frame = tk.Frame(self, bg=ModernStyle.BORDER, padx=1, pady=1)
        self.border_frame.pack(fill=tk.BOTH, expand=True)
        
        # 工具栏
        self.toolbar = tk.Frame(self.border_frame, bg=ModernStyle.BG_SECONDARY, height=30)
        self.toolbar.pack(fill=tk.X)
        self.toolbar.pack_propagate(False)
        
        # 状态标签
        self.status_label = tk.Label(
            self.toolbar,
            text="",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED,
            padx=10
        )
        self.status_label.pack(side=tk.LEFT, pady=5)
        
        # 字数统计
        self.count_label = tk.Label(
            self.toolbar,
            text="0 字",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED,
            padx=10
        )
        self.count_label.pack(side=tk.RIGHT, pady=5)
        
        # 文本框
        self.text = scrolledtext.ScrolledText(
            self.border_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            wrap=tk.WORD,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            relief="flat",
            padx=15,
            pady=15,
            height=height,
            state=tk.DISABLED,
            insertbackground=ModernStyle.PRIMARY
        )
        self.text.pack(fill=tk.BOTH, expand=True)
        
        # 配置差异高亮标签
        self.text.tag_configure("insert", background="#D1FAE5", foreground="#065F46")
        self.text.tag_configure("delete", background="#FEE2E2", foreground="#991B1B", overstrike=True)
        self.text.tag_configure("replace", background="#FEF3C7", foreground="#92400E")
        self.text.tag_configure("cursor", foreground=ModernStyle.PRIMARY)
    
    def start_streaming(self, status_text: str = "正在生成..."):
        """开始流式接收"""
        self.clear()
        self._streaming = True
        self._buffer = []
        self.status_label.config(text=f"🔄 {status_text}", fg=ModernStyle.INFO)
        self.border_frame.config(bg=ModernStyle.INFO)
    
    def append_chunk(self, chunk: str):
        """
        追加文本块
        
        Args:
            chunk: 要追加的文本片段
        """
        if not self._streaming:
            return
        
        if self.typewriter_effect:
            # 打字机效果：将chunk加入缓冲区
            for char in chunk:
                self._buffer.append(char)
            
            # 启动打字效果（如果未运行）
            if self._typing_job is None:
                self._type_next_char()
        else:
            # 直接追加
            self._append_text(chunk)
    
    def _type_next_char(self):
        """打字机效果：显示下一个字符"""
        if self._buffer and self._streaming:
            char = self._buffer.pop(0)
            self._append_text(char)
            self._typing_job = self.after(self.typewriter_delay, self._type_next_char)
        else:
            self._typing_job = None
    
    def _append_text(self, text: str, tag: Optional[str] = None):
        """实际追加文本"""
        self.text.config(state=tk.NORMAL)
        if tag:
            self.text.insert(tk.END, text, tag)
        else:
            self.text.insert(tk.END, text)
        self.text.see(tk.END)  # 自动滚动
        self.text.config(state=tk.DISABLED)
        
        # 更新字数
        content = self.text.get("1.0", tk.END).strip()
        self.count_label.config(text=f"{len(content)} 字")
    
    def end_streaming(self, success: bool = True):
        """结束流式接收"""
        self._streaming = False
        
        # 清空缓冲区（如果使用打字机效果）
        if self._buffer:
            remaining = "".join(self._buffer)
            self._append_text(remaining)
            self._buffer = []
        
        if self._typing_job:
            self.after_cancel(self._typing_job)
            self._typing_job = None
        
        if success:
            self.status_label.config(text="✅ 生成完成", fg=ModernStyle.SUCCESS)
            self.border_frame.config(bg=ModernStyle.SUCCESS)
        else:
            self.status_label.config(text="❌ 生成失败", fg=ModernStyle.ERROR)
            self.border_frame.config(bg=ModernStyle.ERROR)
        
        # 3秒后恢复边框颜色
        self.after(3000, lambda: self.border_frame.config(bg=ModernStyle.BORDER))
    
    def set_content(self, content: str, tag: Optional[str] = None):
        """直接设置内容（非流式）"""
        self._streaming = False
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        if tag:
            self.text.insert("1.0", content, tag)
        else:
            self.text.insert("1.0", content)
        self.text.config(state=tk.DISABLED)
        
        self.count_label.config(text=f"{len(content)} 字")
        self.status_label.config(text="")
        self.border_frame.config(bg=ModernStyle.BORDER)
    
    def get_content(self) -> str:
        """获取内容"""
        return self.text.get("1.0", tk.END).strip()
    
    def clear(self):
        """清空内容"""
        self._streaming = False
        self._buffer = []
        if self._typing_job:
            self.after_cancel(self._typing_job)
            self._typing_job = None
        
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.config(state=tk.DISABLED)
        
        self.count_label.config(text="0 字")
        self.status_label.config(text="")
        self.border_frame.config(bg=ModernStyle.BORDER)
    
    def stream_from_generator(
        self,
        generator: Generator[str, None, None],
        on_complete: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ):
        """
        从生成器流式接收内容
        
        Args:
            generator: 文本生成器
            on_complete: 完成回调
            on_error: 错误回调
        """
        self.start_streaming()
        
        def stream_thread():
            full_content: List[str] = []
            try:
                for chunk in generator:
                    full_content.append(chunk)
                    # 线程安全更新UI - 修复: 添加组件存在性检查防止销毁后调用
                    if self.winfo_exists():
                        self.after(0, lambda c=chunk: self.append_chunk(c))
                    else:
                        break  # 组件已销毁，停止处理
                
                # 完成 - 修复: 添加组件存在性检查
                if self.winfo_exists():
                    self.after(0, lambda: self.end_streaming(True))
                    if on_complete is not None:
                        complete_callback = on_complete
                        final_content = "".join(full_content)
                        self.after(0, lambda: complete_callback(final_content))
                    
            except Exception as e:
                # 修复: 添加组件存在性检查
                if self.winfo_exists():
                    self.after(0, lambda: self.end_streaming(False))
                    if on_error is not None:
                        error_callback = on_error
                        error = e
                        self.after(0, lambda: error_callback(error))
        
        thread = threading.Thread(target=stream_thread, daemon=True)
        thread.start()


class ModernButton(tk.Canvas):
    """现代圆角按钮（带动画效果）"""
    
    def __init__(
        self, 
        parent, 
        text: str, 
        command: Optional[Callable] = None, 
        width: int = 120, 
        height: int = 40,
        bg_color: Optional[str] = None, 
        hover_color: Optional[str] = None, 
        text_color: Optional[str] = None,
        disabled: bool = False,
        tooltip: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            parent, 
            width=width, 
            height=height,
            highlightthickness=0, 
            bg=parent.cget("bg"), 
            **kwargs
        )
        
        self.command = command
        self.text = text
        self.width = width
        self.height = height
        self.bg_color = bg_color or ModernStyle.PRIMARY
        self.hover_color = hover_color or ModernStyle.PRIMARY_HOVER
        self.text_color = text_color or ModernStyle.TEXT_LIGHT
        self.disabled = disabled
        self._current_bg = self.bg_color
        self._animation_id = None
        self._is_pressed = False
        
        self._draw_button()
        
        if not disabled:
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)
            self.bind("<Button-1>", self._on_click)
            self.bind("<ButtonRelease-1>", self._on_release)
        else:
            self._current_bg = ModernStyle.BG_DISABLED
            self._draw_button()
        
        # 添加工具提示
        if tooltip:
            Tooltip(self, tooltip)
    
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
        
        # 绘制文本
        text_color = ModernStyle.TEXT_DISABLED if self.disabled else self.text_color
        self.create_text(
            self.width/2, self.height/2,
            text=self.text,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM, "bold"),
            fill=text_color
        )
    
    def _animate_color(self, target_color: str, steps: int = 6):
        """平滑颜色过渡动画"""
        if self._animation_id:
            self.after_cancel(self._animation_id)
        
        # 简化动画，直接设置目标颜色
        self._current_bg = target_color
        self._draw_button()
    
    def _on_enter(self, event):
        if not self.disabled:
            self._animate_color(self.hover_color)
            self.config(cursor="hand2")
    
    def _on_leave(self, event):
        if not self.disabled and not self._is_pressed:
            self._animate_color(self.bg_color)
    
    def _on_click(self, event):
        if not self.disabled:
            self._is_pressed = True
            self._animate_color(ModernStyle.PRIMARY_DARK)
    
    def _on_release(self, event):
        if not self.disabled:
            self._is_pressed = False
            self._animate_color(self.hover_color)
            if self.command:
                self.command()
    
    def set_disabled(self, disabled: bool):
        """设置禁用状态"""
        self.disabled = disabled
        if disabled:
            self._current_bg = ModernStyle.BG_DISABLED
            self.unbind("<Enter>")
            self.unbind("<Leave>")
            self.unbind("<Button-1>")
            self.unbind("<ButtonRelease-1>")
        else:
            self._current_bg = self.bg_color
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)
            self.bind("<Button-1>", self._on_click)
            self.bind("<ButtonRelease-1>", self._on_release)
        self._draw_button()
    
    def set_text(self, text: str):
        """更新按钮文字"""
        self.text = text
        self._draw_button()


class PlaceholderEntry(tk.Entry):
    """带占位符的输入框"""
    
    def __init__(
        self,
        parent,
        placeholder: str = "",
        placeholder_color: Optional[str] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.placeholder = placeholder
        self.placeholder_color = placeholder_color or ModernStyle.TEXT_MUTED
        self.default_fg = kwargs.get('fg', ModernStyle.TEXT_PRIMARY)
        self._has_placeholder = False
        
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        
        self._show_placeholder()
    
    def _show_placeholder(self):
        """显示占位符"""
        if not self.get():
            self._has_placeholder = True
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)
    
    def _on_focus_in(self, event):
        """获得焦点时"""
        if self._has_placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg)
            self._has_placeholder = False
    
    def _on_focus_out(self, event):
        """失去焦点时"""
        if not self.get():
            self._show_placeholder()
    
    def get_value(self) -> str:
        """获取实际值（排除占位符）"""
        if self._has_placeholder:
            return ""
        return self.get()
    
    def set_value(self, value: str):
        """设置值"""
        self.delete(0, tk.END)
        if value:
            self._has_placeholder = False
            self.config(fg=self.default_fg)
            self.insert(0, value)
        else:
            self._show_placeholder()


class StatusBar:
    """状态栏组件"""
    
    def __init__(self, parent):
        self.parent = parent
        
        self.frame = tk.Frame(
            parent,
            bg=ModernStyle.BG_SECONDARY,
            height=28
        )
        self.frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.frame.pack_propagate(False)
        
        # 分隔线
        tk.Frame(
            self.frame,
            bg=ModernStyle.BORDER,
            height=1
        ).pack(side=tk.TOP, fill=tk.X)
        
        # 状态文本
        self.status_label = tk.Label(
            self.frame,
            text="就绪",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED,
            padx=15
        )
        self.status_label.pack(side=tk.LEFT, pady=4)
        
        # 右侧信息
        self.info_label = tk.Label(
            self.frame,
            text="",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED,
            padx=15
        )
        self.info_label.pack(side=tk.RIGHT, pady=4)
    
    def set_status(self, text: str, status_type: str = "normal"):
        """设置状态文本"""
        colors = {
            "normal": ModernStyle.TEXT_MUTED,
            "success": ModernStyle.SUCCESS,
            "warning": ModernStyle.WARNING,
            "error": ModernStyle.ERROR,
            "info": ModernStyle.INFO
        }
        color = colors.get(status_type, ModernStyle.TEXT_MUTED)
        self.status_label.config(text=text, fg=color)
    
    def set_info(self, text: str):
        """设置右侧信息"""
        self.info_label.config(text=text)


class TaskManager:
    """任务管理器 - 管理后台任务的执行和取消"""
    
    def __init__(self, safe_update_func: Callable):
        self.safe_update = safe_update_func
        self.active_tasks = {}
        self._task_counter = 0
        self._lock = threading.Lock()
    
    def submit(
        self, 
        func: Callable, 
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_progress: Optional[Callable] = None,
        task_name: str = "task"
    ) -> str:
        """
        提交任务
        
        Returns:
            str: 任务ID，可用于取消任务
        """
        with self._lock:
            self._task_counter += 1
            task_id = f"{task_name}_{self._task_counter}"
        
        cancel_event = threading.Event()
        self.active_tasks[task_id] = {
            "cancel_event": cancel_event,
            "status": "running"
        }
        
        # 保存回调函数的本地引用
        complete_callback = on_complete
        error_callback = on_error
        
        def wrapper():
            try:
                # 执行任务，传入取消检查函数
                result = func(lambda: cancel_event.is_set())
                
                if not cancel_event.is_set() and complete_callback:
                    def do_complete(r=result, cb=complete_callback):
                        if cb: cb(r)
                    self.safe_update(do_complete)
                    
            except Exception as e:
                if not cancel_event.is_set() and error_callback:
                    def do_error(err=e, cb=error_callback):
                        if cb: cb(err)
                    self.safe_update(do_error)
            finally:
                with self._lock:
                    if task_id in self.active_tasks:
                        self.active_tasks[task_id]["status"] = "completed"
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
        
        return task_id
    
    def cancel(self, task_id: str) -> bool:
        """取消任务"""
        with self._lock:
            if task_id in self.active_tasks:
                self.active_tasks[task_id]["cancel_event"].set()
                self.active_tasks[task_id]["status"] = "cancelled"
                return True
        return False
    
    def cancel_all(self):
        """取消所有任务"""
        with self._lock:
            for task_id, task in self.active_tasks.items():
                task["cancel_event"].set()
                task["status"] = "cancelled"
    
    def is_running(self, task_id: str) -> bool:
        """检查任务是否正在运行"""
        with self._lock:
            return (
                task_id in self.active_tasks and 
                self.active_tasks[task_id]["status"] == "running"
            )


class TextInputWithCount(tk.Frame):
    """带字数统计的文本输入框"""
    
    def __init__(
        self, 
        parent, 
        height: int = 15,
        placeholder: str = "",
        show_count: bool = True,
        **kwargs
    ):
        super().__init__(parent, bg=ModernStyle.BG_MAIN)
        
        self.placeholder = placeholder
        self.show_count = show_count
        self._has_placeholder = False
        self.max_chars = kwargs.get('max_chars', 0)
        
        # 边框容器
        self.border_frame = tk.Frame(self, bg=ModernStyle.BORDER, padx=1, pady=1)
        self.border_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文本框
        self.text = scrolledtext.ScrolledText(
            self.border_frame,
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
            undo=True,
            autoseparators=True,
            maxundo=-1
        )
        self.text.pack(fill=tk.BOTH, expand=True)

        # 右上角清除按钮
        self.clear_btn = tk.Label(
            self.text,
            text="✕",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_INPUT,
            fg=ModernStyle.TEXT_MUTED,
            cursor="hand2",
            padx=2,
            pady=2
        )
        self.clear_btn.place(relx=1.0, x=-20, y=5, anchor="ne")
        self.clear_btn.bind("<Button-1>", lambda e: self.clear())
        self.clear_btn.bind("<Enter>", lambda e: self.clear_btn.config(fg=ModernStyle.ERROR))
        self.clear_btn.bind("<Leave>", lambda e: self.clear_btn.config(fg=ModernStyle.TEXT_MUTED))

        # 绑定标准快捷键支持（部分平台 Tkinter 默认不完整）
        self.text.bind("<Control-z>", lambda e: self._undo())
        self.text.bind("<Control-y>", lambda e: self._redo())
        self.text.bind("<Control-Shift-Z>", lambda e: self._redo())
        
        # 字数统计
        if show_count:
            self.count_label = tk.Label(
                self,
                text="字数: 0",
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
                bg=ModernStyle.BG_MAIN,
                fg=ModernStyle.TEXT_MUTED,
                anchor="e"
            )
            self.count_label.pack(fill=tk.X, pady=(3, 0))
            
            # 绑定文本变化事件
            self.text.bind("<KeyRelease>", self._update_count)
            self.text.bind("<<Paste>>", lambda e: self.after(10, self._update_count))
        
        # 占位符处理
        if placeholder:
            self._show_placeholder()
            self.text.bind("<FocusIn>", self._on_focus_in)
            self.text.bind("<FocusOut>", self._on_focus_out)
    
    def _show_placeholder(self):
        """显示占位符"""
        content = self.text.get("1.0", tk.END).strip()
        if not content:
            self._has_placeholder = True
            self.text.insert("1.0", self.placeholder)
            self.text.config(fg=ModernStyle.TEXT_MUTED)
    
    def _on_focus_in(self, event):
        """获得焦点"""
        if self._has_placeholder:
            self.text.delete("1.0", tk.END)
            self.text.config(fg=ModernStyle.TEXT_PRIMARY)
            self._has_placeholder = False
    
    def _on_focus_out(self, event):
        """失去焦点"""
        content = self.text.get("1.0", tk.END).strip()
        if not content and self.placeholder:
            self._show_placeholder()
    
    def _update_count(self, event=None):
        """更新字数统计"""
        if self._has_placeholder:
            self.count_label.config(text="字数: 0")
            return
        
        content = self.text.get("1.0", tk.END).strip()
        char_count = len(content)
        word_count = len(content.split()) if content else 0
        
        count_text = f"字数: {char_count}"
        if self.max_chars > 0:
            count_text += f" / {self.max_chars}"
            if char_count > self.max_chars:
                self.count_label.config(fg=ModernStyle.ERROR)
                self.border_frame.config(bg=ModernStyle.ERROR)
            else:
                self.count_label.config(fg=ModernStyle.TEXT_MUTED)
                self.border_frame.config(bg=ModernStyle.BORDER)
        
        count_text += f" | 词数: {word_count}"
        self.count_label.config(text=count_text)
    
    def get_content(self) -> str:
        """获取内容"""
        if self._has_placeholder:
            return ""
        return self.text.get("1.0", tk.END).strip()
    
    def set_content(self, content: str, highlight: bool = False):
        """设置内容"""
        self._has_placeholder = False
        self.text.config(fg=ModernStyle.TEXT_PRIMARY)
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        if self.show_count:
            self._update_count()
        
        if highlight:
            self.highlight()
    
    def highlight(self, color: str = ModernStyle.SUCCESS, duration: int = 1500):
        """高亮显示组件边框（用于提示数据已填充）"""
        original_bg = self.border_frame.cget("bg")
        self.border_frame.config(bg=color)
        self.after(duration, lambda: self.border_frame.config(bg=original_bg))

    def _undo(self):
        """执行撤销"""
        try:
            self.text.edit_undo()
            self._update_count()
        except tk.TclError:
            pass
        return "break"

    def _redo(self):
        """执行重做"""
        try:
            self.text.edit_redo()
            self._update_count()
        except tk.TclError:
            pass
        return "break"

    def clear(self):
        """清空内容"""
        self.text.delete("1.0", tk.END)
        if self.placeholder:
            self._show_placeholder()
        if self.show_count:
            self._update_count()


class TextOutputBox(tk.Frame):
    """只读文本输出框"""
    
    def __init__(self, parent, height: int = 15, **kwargs):
        super().__init__(parent, bg=ModernStyle.BG_MAIN)
        
        # 边框容器
        self.border_frame = tk.Frame(self, bg=ModernStyle.BORDER, padx=1, pady=1)
        self.border_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文本框
        self.text = scrolledtext.ScrolledText(
            self.border_frame,
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
        self.text.pack(fill=tk.BOTH, expand=True)
    
    def set_content(self, content: str):
        """设置内容"""
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        self.text.config(state=tk.DISABLED)
    
    def get_content(self) -> str:
        """获取内容"""
        return self.text.get("1.0", tk.END).strip()
    
    def clear(self):
        """清空内容"""
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.config(state=tk.DISABLED)


class NotificationBanner:
    """通知横幅组件"""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_banner = None
        self._hide_id = None
    
    def show(
        self, 
        message: str, 
        banner_type: str = "info", 
        duration: int = 3000
    ):
        """显示通知"""
        # 清除现有通知
        self.hide()
        
        # 颜色配置
        colors = {
            "success": (ModernStyle.SUCCESS_LIGHT, ModernStyle.SUCCESS),
            "warning": (ModernStyle.WARNING_LIGHT, ModernStyle.WARNING),
            "error": (ModernStyle.ERROR_LIGHT, ModernStyle.ERROR),
            "info": (ModernStyle.INFO_LIGHT, ModernStyle.INFO),
        }
        bg_color, text_color = colors.get(banner_type, colors["info"])
        
        # 图标
        icons = {
            "success": "✓",
            "warning": "⚠",
            "error": "✕",
            "info": "ℹ"
        }
        icon = icons.get(banner_type, "ℹ")
        
        # 创建横幅
        self.current_banner = tk.Frame(
            self.parent,
            bg=bg_color,
            padx=20,
            pady=10
        )
        self.current_banner.pack(fill=tk.X, side=tk.TOP)
        
        tk.Label(
            self.current_banner,
            text=f"{icon} {message}",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=bg_color,
            fg=text_color
        ).pack(side=tk.LEFT)
        
        # 关闭按钮
        close_btn = tk.Label(
            self.current_banner,
            text="✕",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=bg_color,
            fg=text_color,
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", lambda e: self.hide())
        
        # 自动隐藏
        if duration > 0:
            self._hide_id = self.parent.after(duration, self.hide)
    
    def hide(self):
        """隐藏通知"""
        if self._hide_id:
            self.parent.after_cancel(self._hide_id)
            self._hide_id = None
        if self.current_banner:
            self.current_banner.destroy()
            self.current_banner = None


class KeyboardShortcuts:
    """键盘快捷键管理器"""
    
    def __init__(self, root):
        self.root = root
        self.shortcuts = {}
    
    def bind(self, shortcut: str, callback: Callable, description: str = ""):
        """绑定快捷键"""
        self.shortcuts[shortcut] = {
            "callback": callback,
            "description": description
        }
        self.root.bind(shortcut, lambda e: callback())
    
    def unbind(self, shortcut: str):
        """解绑快捷键"""
        if shortcut in self.shortcuts:
            del self.shortcuts[shortcut]
            self.root.unbind(shortcut)
    
    def get_shortcuts_list(self) -> List[Tuple[str, str]]:
        """获取快捷键列表"""
        return [
            (shortcut, info["description"])
            for shortcut, info in self.shortcuts.items()
        ]

    def show_shortcut_hints(self, parent):
        """在页面底部显示快捷键提示栏"""
        hint_frame = tk.Frame(parent, bg=ModernStyle.BG_MAIN)
        hint_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # 选取几个常用的显示
        common = [
            ("Ctrl+1..5", "切页面"),
            ("Esc", "取消任务"),
            ("F1", "帮助")
        ]
        
        for key, desc in common:
            lbl = tk.Label(
                hint_frame,
                text=f" {key} ",
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS, "bold"),
                bg=ModernStyle.BG_SECONDARY,
                fg=ModernStyle.TEXT_SECONDARY,
                relief="flat",
                padx=5
            )
            lbl.pack(side=tk.LEFT, padx=(10, 5))
            
            tk.Label(
                hint_frame,
                text=desc,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
                bg=ModernStyle.BG_MAIN,
                fg=ModernStyle.TEXT_MUTED
            ).pack(side=tk.LEFT)


class ConfirmDialog:
    """确认对话框"""
    
    @staticmethod
    def show(
        parent,
        title: str,
        message: str,
        confirm_text: str = "确定",
        cancel_text: str = "取消"
    ) -> bool:
        """显示确认对话框"""
        result = [False]
        
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("400x180")
        dialog.resizable(False, False)
        dialog.configure(bg=ModernStyle.BG_MAIN)
        dialog.transient(parent)
        dialog.grab_set()
        
        # 居中
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 400) // 2
        y = (dialog.winfo_screenheight() - 180) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # 内容
        content = tk.Frame(dialog, bg=ModernStyle.BG_MAIN, padx=30, pady=25)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            content,
            text=message,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MD),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_PRIMARY,
            wraplength=340,
            justify="left"
        ).pack(anchor="w", pady=(0, 20))
        
        # 按钮
        btn_frame = tk.Frame(content, bg=ModernStyle.BG_MAIN)
        btn_frame.pack(fill=tk.X)
        
        def on_confirm():
            result[0] = True
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        ModernButton(
            btn_frame,
            text=confirm_text,
            command=on_confirm,
            width=100,
            height=38
        ).pack(side=tk.LEFT)
        
        tk.Button(
            btn_frame,
            text=cancel_text,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SM),
            bg=ModernStyle.BG_SECONDARY,
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=on_cancel
        ).pack(side=tk.LEFT, padx=15)
        
        dialog.wait_window()
        return result[0]


class DualOutputFrame(tk.Frame):
    """双重输出框架 - 将结果内容与分析报告分离显示
    
    使用选项卡实现：
    - Tab 1: ✨ 结果内容 (纯净的 AI 生成文本，便于复制)
    - Tab 2: 📊 分析报告 (诊断建议、统计数据等)
    """
    
    def __init__(
        self,
        parent,
        height: int = 15,
        show_actions: bool = True,
        on_send_to: Optional[Callable[[str, str, bool], None]] = None,
        **kwargs
    ):
        """
        初始化双重输出框架
        
        Args:
            parent: 父容器
            height: 文本框高度
            show_actions: 是否显示操作按钮区
            on_send_to: 流转回调函数 (target_page, content, as_context) -> None
        """
        super().__init__(parent, bg=ModernStyle.BG_MAIN, **kwargs)
        
        self.height = height
        self.on_send_to = on_send_to
        self._content = ""
        self._report = ""
        
        # 创建选项卡
        self.notebook = ttk.Notebook(self, style="Modern.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: 结果内容
        self.content_frame = tk.Frame(self.notebook, bg=ModernStyle.BG_MAIN)
        self.notebook.add(self.content_frame, text="  ✨ 结果内容  ")
        
        self._create_content_tab()
        
        # Tab 2: 分析报告
        self.report_frame = tk.Frame(self.notebook, bg=ModernStyle.BG_MAIN)
        self.notebook.add(self.report_frame, text="  📊 分析报告  ")
        
        self._create_report_tab()
        
        # 操作按钮区（流转、复制、导出）
        if show_actions:
            self._create_action_bar()
    
    def _create_content_tab(self):
        """创建结果内容选项卡"""
        # 工具栏
        toolbar = tk.Frame(self.content_frame, bg=ModernStyle.BG_MAIN)
        toolbar.pack(fill=tk.X, pady=(8, 5), padx=5)
        
        tk.Label(
            toolbar,
            text="💡 此处显示纯净的处理结果，可直接复制使用",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_MUTED
        ).pack(side=tk.LEFT)
        
        # 复制按钮
        copy_btn = tk.Label(
            toolbar,
            text="📋 复制全部",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.PRIMARY,
            cursor="hand2",
            padx=10
        )
        copy_btn.pack(side=tk.RIGHT)
        copy_btn.bind("<Button-1>", lambda e: self._copy_content())
        copy_btn.bind("<Enter>", lambda e: copy_btn.config(fg=ModernStyle.PRIMARY_DARK))
        copy_btn.bind("<Leave>", lambda e: copy_btn.config(fg=ModernStyle.PRIMARY))
        
        # 文本框 - 使用 StreamingTextOutput 支持流式显示 (P0)
        self.content_output = StreamingTextOutput(self.content_frame, height=self.height)
        self.content_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
    
    def _create_report_tab(self):
        """创建分析报告选项卡"""
        # 工具栏
        toolbar = tk.Frame(self.report_frame, bg=ModernStyle.BG_MAIN)
        toolbar.pack(fill=tk.X, pady=(8, 5), padx=5)
        
        tk.Label(
            toolbar,
            text="📈 此处显示 AI 分析诊断、评分建议等详细报告",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.TEXT_MUTED
        ).pack(side=tk.LEFT)
        
        # 导出按钮
        export_btn = tk.Label(
            toolbar,
            text="📥 导出报告",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_MAIN,
            fg=ModernStyle.INFO,
            cursor="hand2",
            padx=10
        )
        export_btn.pack(side=tk.RIGHT)
        export_btn.bind("<Button-1>", lambda e: self._export_report())
        export_btn.bind("<Enter>", lambda e: export_btn.config(fg=ModernStyle.PRIMARY_DARK))
        export_btn.bind("<Leave>", lambda e: export_btn.config(fg=ModernStyle.INFO))
        
        # 文本框 - 使用 StreamingTextOutput 支持流式显示 (P0)
        self.report_output = StreamingTextOutput(self.report_frame, height=self.height)
        self.report_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
    
    def _create_action_bar(self):
        """创建操作按钮区"""
        self.action_bar = tk.Frame(self, bg=ModernStyle.BG_SECONDARY, padx=15, pady=10)
        self.action_bar.pack(fill=tk.X, pady=(5, 0))
        
        # 流转按钮容器（动态添加）
        self.flow_buttons_frame = tk.Frame(self.action_bar, bg=ModernStyle.BG_SECONDARY)
        self.flow_buttons_frame.pack(side=tk.LEFT)
        
        # 右侧统计信息
        self.stats_label = tk.Label(
            self.action_bar,
            text="",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED
        )
        self.stats_label.pack(side=tk.RIGHT)
    
    def add_flow_button(self, text: str, target_page: str, icon: str = "➡️", as_context: bool = False):
        """添加流转按钮
        
        Args:
            text: 按钮文本 (如 "发送至优化")
            target_page: 目标页面 ID (如 "optimize")
            icon: 图标
            as_context: 是否作为背景参考发送
        """
        btn = ModernButton(
            self.flow_buttons_frame,
            text=f"{icon} {text}",
            command=lambda: self._do_send_to(target_page, as_context),
            width=130,
            height=34,
            bg_color=ModernStyle.INFO if as_context else ModernStyle.SUCCESS,
            hover_color=ModernStyle.INFO if as_context else ModernStyle.SUCCESS,
            tooltip=f"将结果内容{'作为背景参考' if as_context else ''}发送至{text.replace('发送至', '')}"
        )
        btn.pack(side=tk.LEFT, padx=(0, 10))
    
    def _do_send_to(self, target_page: str, as_context: bool = False):
        """执行流转操作"""
        if self.on_send_to and self._content:
            self.on_send_to(target_page, self._content, as_context)
    
    def _copy_content(self):
        """复制内容到剪贴板"""
        if self._content:
            self.winfo_toplevel().clipboard_clear()
            self.winfo_toplevel().clipboard_append(self._content)
            # 尝试调用主应用的通知系统
            try:
                app = self.winfo_toplevel()
                notification = getattr(app, 'notification', None)
                if notification and hasattr(notification, 'show'):
                    notification.show("已复制到剪贴板", "success")
            except Exception:
                pass
    
    def _export_report(self):
        """导出报告"""
        if self._report:
            from tkinter import filedialog
            from datetime import datetime
            file_path = filedialog.asksaveasfilename(
                title="导出分析报告",
                defaultextension=".md",
                filetypes=[
                    ("Markdown", "*.md"),
                    ("文本文件", "*.txt"),
                    ("所有文件", "*.*")
                ],
                initialfile=f"分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self._report)
    
    def set_content(self, content: str, report: str = "", diff_mode: bool = False, old_content: str = ""):
        """设置输出内容
        
        Args:
            content: 结果内容（纯净文本）
            report: 分析报告（诊断、建议等）
            diff_mode: 是否启用差异高亮模式
            old_content: 差异对比的原文
        """
        self._content = content
        self._report = report
        
        if diff_mode and old_content:
            self._display_diff(old_content, content)
        else:
            self.content_output.set_content(content)
            
        self.report_output.set_content(report if report else "暂无分析报告")
        
        # 更新统计信息
        if hasattr(self, 'stats_label'):
            content_chars = len(content)
            report_chars = len(report)
            self.stats_label.config(
                text=f"结果: {content_chars} 字 | 报告: {report_chars} 字"
            )
        
        # 自动切换到有内容的选项卡
        if content and not report:
            self.notebook.select(0)
        elif report and not content:
            self.notebook.select(1)
    
    def set_result(self, result: dict):
        """设置结构化结果
        
        Args:
            result: 包含 'content' 和 'report' 键的字典
        """
        content = result.get('content', '')
        report = result.get('report', '')
        self.set_content(content, report)
    
    def get_content(self) -> str:
        """获取结果内容"""
        return self._content
    
    def get_report(self) -> str:
        """获取分析报告"""
        return self._report
    
    def clear(self):
        """清空内容"""
        self._content = ""
        self._report = ""
        self.content_output.clear()
        self.report_output.clear()
        if hasattr(self, 'stats_label'):
            self.stats_label.config(text="")

    def _display_diff(self, old_text: str, new_text: str):
        """在内容窗口显示差异高亮"""
        from utils.diff import DiffGenerator
        gen = DiffGenerator()
        segments = gen.generate(old_text, new_text)
        
        self.content_output.clear()
        self.content_output.text.config(state=tk.NORMAL)
        
        for seg in segments:
            # tag_type = seg.type # equal, insert, delete, replace
            if seg.type == "equal":
                self.content_output.text.insert(tk.END, seg.new_text)
            elif seg.type == "insert":
                self.content_output.text.insert(tk.END, seg.new_text, "insert")
            elif seg.type == "delete":
                self.content_output.text.insert(tk.END, seg.old_text, "delete")
            elif seg.type == "replace":
                self.content_output.text.insert(tk.END, seg.old_text, "delete")
                self.content_output.text.insert(tk.END, seg.new_text, "insert")
                
        self.content_output.text.config(state=tk.DISABLED)
        self.content_output.status_label.config(text="✨ 已开启差异高亮视图", fg=ModernStyle.SUCCESS)


class WorkflowConnector:
    """工作流连接器 - 管理页面间的数据流转"""
    
    def __init__(self, app):
        """
        初始化工作流连接器
        
        Args:
            app: EconPaperApp 实例
        """
        self.app = app
        self.flow_history = []  # 流转历史
    
    def send_to_page(self, target_page: str, content: str, source_page: str = "", as_context: bool = False):
        """发送内容到目标页面
        
        Args:
            target_page: 目标页面 ID
            content: 要发送的内容
            source_page: 来源页面 ID
            as_context: 是否作为背景参考发送
        """
        # 记录流转历史
        self.flow_history.append({
            'from': source_page,
            'to': target_page,
            'as_context': as_context,
            'content_preview': content[:100] if content else ''
        })
        
        # 根据目标页面填充内容
        if target_page == "optimize":
            self._fill_optimize_page(content, as_context)
        elif target_page == "dedup":
            self._fill_dedup_page(content)
        elif target_page == "search":
            self._fill_search_page(content)
        elif target_page == "revision":
            self._fill_revision_page(content, as_context)
        
        # 切换到目标页面
        self.app._show_page(target_page)
        
        # 显示通知
        if hasattr(self.app, 'notification'):
            page_names = {
                "optimize": "深度优化",
                "dedup": "降重降AI",
                "search": "学术搜索",
                "revision": "退修助手"
            }
            self.app.notification.show(
                f"内容已发送至「{page_names.get(target_page, target_page)}」",
                "success"
            )
    
    def _fill_optimize_page(self, content: str, as_context: bool = False):
        """填充优化页面"""
        if as_context:
            if hasattr(self.app, '_toggle_opt_context'):
                self.app._toggle_opt_context(show=True)
            if hasattr(self.app, 'opt_context_input'):
                self.app.opt_context_input.set_content(content, highlight=True)
        else:
            if hasattr(self.app, 'opt_input_comp'):
                self.app.opt_input_comp.set_content(content, highlight=True)
            elif hasattr(self.app, 'opt_input'):
                self.app.opt_input.delete("1.0", tk.END)
                self.app.opt_input.insert("1.0", content)
    
    def _fill_dedup_page(self, content: str):
        """填充降重页面"""
        if hasattr(self.app, 'dedup_input_comp'):
            self.app.dedup_input_comp.set_content(content, highlight=True)
        elif hasattr(self.app, 'dedup_input'):
            self.app.dedup_input.delete("1.0", tk.END)
            self.app.dedup_input.insert("1.0", content)
    
    def _fill_search_page(self, content: str):
        """填充搜索页面（提取关键词）"""
        # 如果内容较短，直接作为搜索词
        if len(content) < 100:
            if hasattr(self.app, 'search_query'):
                self.app.search_query.delete(0, tk.END)
                self.app.search_query.insert(0, content)
                # 搜索框高亮反馈
                original_bg = self.app.search_query.cget("bg")
                self.app.search_query.config(bg=ModernStyle.SUCCESS_LIGHT)
                self.app.root.after(1500, lambda: self.app.search_query.config(bg=original_bg))
        # 否则需要 AI 提取关键词
    
    def _fill_revision_page(self, content: str, as_context: bool = False):
        """填充退修页面"""
        if as_context:
            if hasattr(self.app, 'rev_summary_comp'):
                self.app.rev_summary_comp.set_content(content, highlight=True)
        else:
            if hasattr(self.app, 'rev_comments_comp'):
                self.app.rev_comments_comp.set_content(content, highlight=True)
            elif hasattr(self.app, 'rev_comments'):
                self.app.rev_comments.delete("1.0", tk.END)
                self.app.rev_comments.insert("1.0", content)