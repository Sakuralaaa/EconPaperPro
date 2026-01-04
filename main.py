# -*- coding: utf-8 -*-
"""
EconPaper Pro - 经管学术论文智能优化系统

主入口文件
支持 Windows 桌面应用模式（原生窗口界面）
"""

import sys
import os
import threading
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional

# 添加项目根目录到 Python 路径
if getattr(sys, 'frozen', False):
    # 打包后的应用
    BASE_DIR = os.path.dirname(sys.executable)
    # 确保内部资源路径正确
    if hasattr(sys, '_MEIPASS'):
        INTERNAL_DIR = sys._MEIPASS
    else:
        INTERNAL_DIR = BASE_DIR
else:
    # 开发环境
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INTERNAL_DIR = BASE_DIR

sys.path.insert(0, BASE_DIR)
sys.path.insert(0, INTERNAL_DIR)

# 版本信息
__version__ = "1.0.0"
__app_name__ = "EconPaper Pro"


def get_log_path() -> Path:
    """获取日志文件路径"""
    if getattr(sys, 'frozen', False):
        app_data = Path(os.environ.get('APPDATA', os.path.expanduser('~')))
        log_dir = app_data / 'EconPaperPro' / 'logs'
    else:
        log_dir = Path(BASE_DIR) / 'logs'
    
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / f"startup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"


def log_error(message: str, log_path: Optional[Path] = None):
    """记录日志到文件"""
    if log_path is None:
        log_path = get_log_path()
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


def show_error_dialog(title: str, message: str, log_path: Optional[Path] = None):
    """显示错误对话框"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        
        full_message = message
        if log_path and log_path.exists():
            full_message += f"\n\n详细日志已保存到:\n{log_path}"
        
        messagebox.showerror(title, full_message)
        root.destroy()
    except Exception:
        pass


def run_setup_wizard() -> bool:
    """运行首次设置向导"""
    try:
        from launcher import run_launcher
        return run_launcher()
    except ImportError as e:
        log_error(f"启动器导入失败: {e}")
        return True
    except Exception as e:
        log_error(f"设置向导启动失败: {e}\n{traceback.format_exc()}")
        return True


def start_gradio_server(host: str, port: int, log_path: Path):
    """在后台线程中启动 Gradio 服务器"""
    try:
        log_error("导入 UI 模块...", log_path)
        from ui.app import create_app
        
        log_error("创建 Gradio 应用...", log_path)
        app = create_app()
        
        log_error(f"启动 Gradio 服务器于 {host}:{port}...", log_path)
        app.launch(
            server_name=host,
            server_port=port,
            share=False,
            inbrowser=False,
            quiet=True,
            prevent_thread_lock=True  # 不阻塞线程
        )
        log_error("Gradio 服务器已启动", log_path)
    except Exception as e:
        log_error(f"Gradio 启动错误: {e}\n{traceback.format_exc()}", log_path)
        raise


def run_desktop_app():
    """运行桌面应用（使用 PyWebView 创建原生窗口）"""
    log_path = get_log_path()
    log_error("="*50, log_path)
    log_error(f"EconPaper Pro v{__version__} 启动 (桌面模式)", log_path)
    
    try:
        # 检查首次运行设置
        if getattr(sys, 'frozen', False):
            log_error("检查首次运行设置...", log_path)
            if not run_setup_wizard():
                log_error("用户取消了设置", log_path)
                return
        
        # 导入配置
        log_error("导入配置...", log_path)
        from config.settings import settings
        
        host = settings.app_host
        port = settings.app_port
        url = f"http://{host}:{port}"
        
        # 在后台线程启动 Gradio
        log_error("启动后台 Gradio 服务...", log_path)
        server_thread = threading.Thread(
            target=start_gradio_server,
            args=(host, port, log_path),
            daemon=True
        )
        server_thread.start()
        
        # 等待服务器启动
        import time
        log_error("等待服务器就绪...", log_path)
        time.sleep(3)  # 给服务器一些启动时间
        
        # 使用 PyWebView 创建原生窗口
        log_error("创建原生窗口...", log_path)
        import webview
        
        # 创建主窗口
        window = webview.create_window(
            title=f'{__app_name__} v{__version__}',
            url=url,
            width=1200,
            height=800,
            resizable=True,
            min_size=(800, 600),
            text_select=True,
        )
        
        log_error("启动 WebView 主循环...", log_path)
        
        # 启动 WebView (这会阻塞直到窗口关闭)
        webview.start()
        
        log_error("应用已关闭", log_path)
        
    except ImportError as e:
        error_msg = f"缺少依赖: {e}\n\n请确保已安装 pywebview:\npip install pywebview"
        log_error(error_msg, log_path)
        show_error_dialog("EconPaper Pro - 依赖错误", error_msg, log_path)
        sys.exit(1)
    except Exception as e:
        error_msg = f"启动失败: {str(e)}"
        log_error(f"{error_msg}\n{traceback.format_exc()}", log_path)
        show_error_dialog("EconPaper Pro - 启动错误", error_msg, log_path)
        sys.exit(1)


def run_web_mode():
    """运行 Web 模式（在浏览器中打开）"""
    log_path = get_log_path()
    log_error("="*50, log_path)
    log_error(f"EconPaper Pro v{__version__} 启动 (Web 模式)", log_path)
    
    try:
        from config.settings import settings
        from ui.app import create_app
        
        app = create_app()
        
        print(f"\n{'='*50}")
        print(f"  📚 {__app_name__} v{__version__}")
        print(f"  经管学术论文智能优化系统")
        print(f"{'='*50}")
        print(f"\n  🌐 访问地址: http://{settings.app_host}:{settings.app_port}")
        print(f"  按 Ctrl+C 停止服务\n")
        
        app.launch(
            server_name=settings.app_host,
            server_port=settings.app_port,
            share=False,
            inbrowser=True
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 应用已停止")
    except Exception as e:
        log_error(f"启动失败: {e}\n{traceback.format_exc()}", log_path)
        print(f"\n❌ 启动失败: {e}")
        traceback.print_exc()
        sys.exit(1)


def main():
    """主函数 - 根据环境选择运行模式"""
    # 检查命令行参数
    if '--web' in sys.argv:
        # 强制 Web 模式
        run_web_mode()
    elif getattr(sys, 'frozen', False):
        # 打包后的应用使用桌面模式
        run_desktop_app()
    else:
        # 开发环境默认使用 Web 模式
        # 可以通过 --desktop 参数使用桌面模式
        if '--desktop' in sys.argv:
            run_desktop_app()
        else:
            run_web_mode()


def main_gui():
    """GUI 入口点（用于 Windows 打包）"""
    run_desktop_app()


if __name__ == "__main__":
    main()
