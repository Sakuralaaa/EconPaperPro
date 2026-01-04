# -*- coding: utf-8 -*-
"""
启动器模块
处理首次启动配置、目录选择等
"""

import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from typing import Optional, Dict


class LauncherConfig:
    """启动器配置"""
    
    CONFIG_FILE = "launcher_config.json"
    
    def __init__(self):
        self.config_path = self._get_config_path()
        self.config = self._load_config()
    
    def _get_config_path(self) -> Path:
        """获取配置文件路径"""
        if getattr(sys, 'frozen', False):
            # 打包后的应用，配置保存在用户目录
            app_data = Path(os.environ.get('APPDATA', os.path.expanduser('~')))
            config_dir = app_data / 'EconPaperPro'
        else:
            # 开发环境，配置保存在项目目录
            config_dir = Path(__file__).parent
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / self.CONFIG_FILE
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def save_config(self) -> None:
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    @property
    def data_dir(self) -> Optional[str]:
        """获取数据存储目录"""
        return self.config.get('data_dir')
    
    @data_dir.setter
    def data_dir(self, value: str) -> None:
        """设置数据存储目录"""
        self.config['data_dir'] = value
        self.save_config()
    
    @property
    def workspace_dir(self) -> Optional[str]:
        """获取工作区目录"""
        return self.config.get('workspace_dir')
    
    @workspace_dir.setter
    def workspace_dir(self, value: str) -> None:
        """设置工作区目录"""
        self.config['workspace_dir'] = value
        self.save_config()
    
    @property
    def first_run(self) -> bool:
        """是否首次运行"""
        return not self.config.get('setup_completed', False)
    
    def mark_setup_completed(self) -> None:
        """标记设置已完成"""
        self.config['setup_completed'] = True
        self.save_config()


class SetupWizard:
    """首次运行设置向导"""
    
    def __init__(self, config: LauncherConfig):
        self.config = config
        self.result = False
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("EconPaper Pro - 初始设置")
        self.root.geometry("600x520")
        self.root.resizable(False, False)
        
        # 居中显示
        self.center_window()
        
        # 设置样式
        self.setup_styles()
        
        # 构建界面
        self.build_ui()
    
    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
    
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Microsoft YaHei UI', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Microsoft YaHei UI', 10))
        style.configure('Section.TLabel', font=('Microsoft YaHei UI', 11, 'bold'))
        style.configure('Big.TButton', font=('Microsoft YaHei UI', 11), padding=10)
    
    def build_ui(self):
        """构建界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # 标题
        ttk.Label(
            main_frame, 
            text="📚 EconPaper Pro", 
            style='Title.TLabel'
        ).pack(pady=(0, 5))
        
        ttk.Label(
            main_frame, 
            text="经管学术论文智能优化系统", 
            style='Subtitle.TLabel',
            foreground='gray'
        ).pack(pady=(0, 20))
        
        # 分隔线
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # 说明文字
        info_text = "欢迎使用 EconPaper Pro！\n请选择数据存储位置和工作区目录。"
        ttk.Label(
            main_frame, 
            text=info_text,
            justify='center'
        ).pack(pady=10)
        
        # 目录选择区域
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill='x', pady=20)
        
        # 数据目录
        ttk.Label(
            dir_frame, 
            text="📁 数据存储目录", 
            style='Section.TLabel'
        ).pack(anchor='w')
        
        ttk.Label(
            dir_frame, 
            text="用于存储向量数据库、日志文件等",
            foreground='gray'
        ).pack(anchor='w')
        
        data_dir_frame = ttk.Frame(dir_frame)
        data_dir_frame.pack(fill='x', pady=(5, 15))
        
        self.data_dir_var = tk.StringVar(value=self._get_default_data_dir())
        self.data_dir_entry = ttk.Entry(
            data_dir_frame, 
            textvariable=self.data_dir_var,
            width=50
        )
        self.data_dir_entry.pack(side='left', fill='x', expand=True)
        
        ttk.Button(
            data_dir_frame, 
            text="浏览...", 
            command=self.browse_data_dir
        ).pack(side='left', padx=(5, 0))
        
        # 工作区目录
        ttk.Label(
            dir_frame, 
            text="📂 工作区目录", 
            style='Section.TLabel'
        ).pack(anchor='w')
        
        ttk.Label(
            dir_frame, 
            text="用于存储临时文件和输出文件",
            foreground='gray'
        ).pack(anchor='w')
        
        workspace_frame = ttk.Frame(dir_frame)
        workspace_frame.pack(fill='x', pady=(5, 0))
        
        self.workspace_var = tk.StringVar(value=self._get_default_workspace_dir())
        self.workspace_entry = ttk.Entry(
            workspace_frame, 
            textvariable=self.workspace_var,
            width=50
        )
        self.workspace_entry.pack(side='left', fill='x', expand=True)
        
        ttk.Button(
            workspace_frame, 
            text="浏览...", 
            command=self.browse_workspace_dir
        ).pack(side='left', padx=(5, 0))
        
        # 分隔线
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=20)
        
        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(
            btn_frame, 
            text="取消", 
            command=self.on_cancel
        ).pack(side='left')
        
        ttk.Button(
            btn_frame, 
            text="开始使用 →", 
            style='Big.TButton',
            command=self.on_confirm
        ).pack(side='right')
    
    def _get_default_data_dir(self) -> str:
        """获取默认数据目录"""
        if self.config.data_dir:
            return self.config.data_dir
        
        app_data = Path(os.environ.get('APPDATA', os.path.expanduser('~')))
        return str(app_data / 'EconPaperPro' / 'data')
    
    def _get_default_workspace_dir(self) -> str:
        """获取默认工作区目录"""
        if self.config.workspace_dir:
            return self.config.workspace_dir
        
        documents = Path(os.path.expanduser('~')) / 'Documents'
        return str(documents / 'EconPaperPro')
    
    def browse_data_dir(self):
        """浏览数据目录"""
        dir_path = filedialog.askdirectory(
            title="选择数据存储目录",
            initialdir=self.data_dir_var.get()
        )
        if dir_path:
            self.data_dir_var.set(dir_path)
    
    def browse_workspace_dir(self):
        """浏览工作区目录"""
        dir_path = filedialog.askdirectory(
            title="选择工作区目录",
            initialdir=self.workspace_var.get()
        )
        if dir_path:
            self.workspace_var.set(dir_path)
    
    def on_confirm(self):
        """确认设置"""
        data_dir = self.data_dir_var.get().strip()
        workspace_dir = self.workspace_var.get().strip()
        
        if not data_dir or not workspace_dir:
            messagebox.showerror("错误", "请填写所有目录路径")
            return
        
        # 创建目录
        try:
            Path(data_dir).mkdir(parents=True, exist_ok=True)
            Path(workspace_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("错误", f"创建目录失败: {e}")
            return
        
        # 保存配置
        self.config.data_dir = data_dir
        self.config.workspace_dir = workspace_dir
        self.config.mark_setup_completed()
        
        self.result = True
        self.root.destroy()
    
    def on_cancel(self):
        """取消设置"""
        if messagebox.askyesno("确认", "确定要退出吗？"):
            self.root.destroy()
    
    def run(self) -> bool:
        """运行向导"""
        self.root.mainloop()
        return self.result


class SettingsDialog:
    """设置对话框"""
    
    def __init__(self, config: LauncherConfig):
        self.config = config
        self.result = False
        
        # 创建主窗口
        self.root = tk.Toplevel()
        self.root.title("EconPaper Pro - 设置")
        self.root.geometry("500x350")
        self.root.resizable(False, False)
        self.root.transient()
        self.root.grab_set()
        
        # 居中显示
        self.center_window()
        
        # 构建界面
        self.build_ui()
    
    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
    
    def build_ui(self):
        """构建界面"""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(
            main_frame, 
            text="⚙️ 目录设置",
            font=('Microsoft YaHei UI', 14, 'bold')
        ).pack(pady=(0, 20))
        
        # 数据目录
        ttk.Label(main_frame, text="数据存储目录:").pack(anchor='w')
        
        data_frame = ttk.Frame(main_frame)
        data_frame.pack(fill='x', pady=(5, 15))
        
        self.data_dir_var = tk.StringVar(value=self.config.data_dir or "")
        ttk.Entry(
            data_frame, 
            textvariable=self.data_dir_var,
            width=45
        ).pack(side='left', fill='x', expand=True)
        
        ttk.Button(
            data_frame, 
            text="浏览", 
            command=self.browse_data_dir
        ).pack(side='left', padx=(5, 0))
        
        # 工作区目录
        ttk.Label(main_frame, text="工作区目录:").pack(anchor='w')
        
        workspace_frame = ttk.Frame(main_frame)
        workspace_frame.pack(fill='x', pady=(5, 20))
        
        self.workspace_var = tk.StringVar(value=self.config.workspace_dir or "")
        ttk.Entry(
            workspace_frame, 
            textvariable=self.workspace_var,
            width=45
        ).pack(side='left', fill='x', expand=True)
        
        ttk.Button(
            workspace_frame, 
            text="浏览", 
            command=self.browse_workspace_dir
        ).pack(side='left', padx=(5, 0))
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(btn_frame, text="取消", command=self.root.destroy).pack(side='left')
        ttk.Button(btn_frame, text="保存", command=self.on_save).pack(side='right')
    
    def browse_data_dir(self):
        dir_path = filedialog.askdirectory(initialdir=self.data_dir_var.get())
        if dir_path:
            self.data_dir_var.set(dir_path)
    
    def browse_workspace_dir(self):
        dir_path = filedialog.askdirectory(initialdir=self.workspace_var.get())
        if dir_path:
            self.workspace_var.set(dir_path)
    
    def on_save(self):
        data_dir = self.data_dir_var.get().strip()
        workspace_dir = self.workspace_var.get().strip()
        
        if data_dir:
            Path(data_dir).mkdir(parents=True, exist_ok=True)
            self.config.data_dir = data_dir
        
        if workspace_dir:
            Path(workspace_dir).mkdir(parents=True, exist_ok=True)
            self.config.workspace_dir = workspace_dir
        
        self.result = True
        self.root.destroy()
    
    def run(self) -> bool:
        self.root.wait_window()
        return self.result


def apply_config_to_environment(config: LauncherConfig) -> None:
    """将配置应用到环境变量"""
    if config.data_dir:
        os.environ['ECONPAPER_DATA_DIR'] = config.data_dir
        # 设置 ChromaDB 目录
        os.environ['CHROMA_PERSIST_DIR'] = str(Path(config.data_dir) / 'chroma_db')
    
    if config.workspace_dir:
        os.environ['ECONPAPER_WORKSPACE_DIR'] = config.workspace_dir


def run_launcher() -> bool:
    """
    运行启动器
    
    Returns:
        bool: 是否成功完成设置
    """
    config = LauncherConfig()
    
    if config.first_run:
        wizard = SetupWizard(config)
        if not wizard.run():
            return False
    
    apply_config_to_environment(config)
    return True


def show_settings_dialog() -> bool:
    """
    显示设置对话框
    
    Returns:
        bool: 是否保存了设置
    """
    config = LauncherConfig()
    dialog = SettingsDialog(config)
    result = dialog.run()
    
    if result:
        apply_config_to_environment(config)
    
    return result


if __name__ == "__main__":
    # 测试启动器
    if run_launcher():
        print("设置完成!")
        config = LauncherConfig()
        print(f"数据目录: {config.data_dir}")
        print(f"工作区目录: {config.workspace_dir}")
    else:
        print("设置取消")
