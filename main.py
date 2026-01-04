# -*- coding: utf-8 -*-
"""
EconPaper Pro - 经管学术论文智能优化系统

主入口文件 - 原生桌面应用（无需浏览器）
双击即可运行，无需任何配置
"""

import sys
import os
from pathlib import Path

# ============== 路径设置 ==============
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后
    BASE_DIR = Path(sys.executable).parent
    INTERNAL_DIR = Path(getattr(sys, '_MEIPASS', BASE_DIR))
else:
    # 开发环境
    BASE_DIR = Path(__file__).parent
    INTERNAL_DIR = BASE_DIR

# 添加到路径
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(INTERNAL_DIR))

# 设置工作目录
os.chdir(str(BASE_DIR))

# ============== 版本信息 ==============
__version__ = "2.0.0"
__app_name__ = "EconPaper Pro"


def show_error(title: str, message: str):
    """显示错误对话框"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:
        print(f"[ERROR] {title}: {message}")


def check_dependencies():
    """检查必要依赖"""
    missing = []
    
    # 核心依赖检查
    try:
        import tkinter
    except ImportError:
        missing.append("tkinter")
    
    # 可选依赖（不阻止启动）
    optional_missing = []
    try:
        import openai
    except ImportError:
        optional_missing.append("openai")
    
    if missing:
        show_error(
            "缺少依赖",
            f"缺少必要的 Python 模块:\n{', '.join(missing)}\n\n请运行: pip install {' '.join(missing)}"
        )
        return False
    
    return True


def main():
    """主函数"""
    # 检查依赖
    if not check_dependencies():
        return 1
    
    try:
        # 导入并启动原生 GUI
        from ui.native_app import main as run_app
        run_app()
        return 0
        
    except Exception as e:
        import traceback
        error_msg = f"启动失败:\n{str(e)}\n\n{traceback.format_exc()}"
        show_error("启动错误", error_msg)
        return 1


if __name__ == "__main__":
    sys.exit(main())
