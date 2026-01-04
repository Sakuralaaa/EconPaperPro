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
import time
import socket
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
__version__ = "1.0.1"
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


# 全局日志路径
LOG_PATH = None


def log_error(message: str, log_path: Optional[Path] = None):
    """记录日志到文件"""
    global LOG_PATH
    if log_path is None:
        if LOG_PATH is None:
            LOG_PATH = get_log_path()
        log_path = LOG_PATH
    
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


def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """检查端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def wait_for_server(host: str, port: int, timeout: int = 60, interval: float = 0.5) -> bool:
    """等待服务器启动"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_open(host, port):
            log_error(f"服务器已就绪 (耗时 {time.time() - start_time:.1f} 秒)")
            return True
        time.sleep(interval)
        log_error(f"等待服务器启动... ({time.time() - start_time:.1f}s)")
    return False


# 全局变量，用于存储服务器启动状态
server_started = False
server_error = None


def start_gradio_server(host: str, port: int):
    """在后台线程中启动 Gradio 服务器"""
    global server_started, server_error
    
    try:
        log_error("开始导入模块...")
        
        # 导入配置
        log_error("导入 config.settings...")
        from config.settings import settings
        log_error(f"配置加载成功")
        
        # 导入 UI
        log_error("导入 ui.app...")
        from ui.app import create_app
        log_error("UI 模块导入成功")
        
        # 创建应用
        log_error("创建 Gradio 应用...")
        app = create_app()
        log_error("Gradio 应用创建成功")
        
        # 启动服务器
        log_error(f"启动 Gradio 服务器于 {host}:{port}...")
        app.launch(
            server_name=host,
            server_port=port,
            share=False,
            inbrowser=False,
            quiet=True,
            prevent_thread_lock=True
        )
        log_error("Gradio 服务器已启动")
        server_started = True
        
    except Exception as e:
        error_msg = f"Gradio 启动错误: {e}\n{traceback.format_exc()}"
        log_error(error_msg)
        server_error = str(e)
        server_started = False


def get_loading_html(message: str = "正在启动...") -> str:
    """获取加载页面的 HTML"""
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>EconPaper Pro - 加载中</title>
        <style>
            body {{
                font-family: 'Microsoft YaHei', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                color: white;
            }}
            .container {{
                text-align: center;
                padding: 40px;
            }}
            .logo {{
                font-size: 48px;
                margin-bottom: 20px;
            }}
            .title {{
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .subtitle {{
                font-size: 16px;
                opacity: 0.8;
                margin-bottom: 40px;
            }}
            .spinner {{
                width: 50px;
                height: 50px;
                border: 4px solid rgba(255,255,255,0.3);
                border-top: 4px solid white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .message {{
                font-size: 18px;
            }}
        </style>
        <script>
            // 每2秒刷新一次，检查服务是否就绪
            setTimeout(function() {{
                window.location.href = 'http://127.0.0.1:7860';
            }}, 2000);
        </script>
    </head>
    <body>
        <div class="container">
            <div class="logo">📚</div>
            <div class="title">EconPaper Pro</div>
            <div class="subtitle">经管学术论文智能优化系统</div>
            <div class="spinner"></div>
            <div class="message">{message}</div>
        </div>
    </body>
    </html>
    '''


def run_desktop_app():
    """运行桌面应用（使用 PyWebView 创建原生窗口）"""
    global LOG_PATH, server_started, server_error
    
    LOG_PATH = get_log_path()
    log_error("="*50)
    log_error(f"EconPaper Pro v{__version__} 启动 (桌面模式)")
    log_error(f"Python: {sys.version}")
    log_error(f"Frozen: {getattr(sys, 'frozen', False)}")
    log_error(f"BASE_DIR: {BASE_DIR}")
    log_error(f"INTERNAL_DIR: {INTERNAL_DIR}")
    
    try:
        # 检查首次运行设置
        if getattr(sys, 'frozen', False):
            log_error("检查首次运行设置...")
            if not run_setup_wizard():
                log_error("用户取消了设置")
                return
        
        # 配置
        host = "127.0.0.1"
        port = 7860
        url = f"http://{host}:{port}"
        
        # 在后台线程启动 Gradio
        log_error("启动后台 Gradio 服务线程...")
        server_thread = threading.Thread(
            target=start_gradio_server,
            args=(host, port),
            daemon=True
        )
        server_thread.start()
        
        # 使用 PyWebView 创建原生窗口
        log_error("导入 webview...")
        import webview
        log_error("webview 导入成功")
        
        # 创建加载页面的临时 HTML 文件
        loading_html_path = Path(BASE_DIR) / "loading.html"
        with open(loading_html_path, 'w', encoding='utf-8') as f:
            f.write(get_loading_html("正在初始化，请稍候..."))
        log_error(f"创建加载页面: {loading_html_path}")
        
        # 创建主窗口，先显示加载页面
        log_error("创建主窗口...")
        window = webview.create_window(
            title=f'{__app_name__} v{__version__}',
            url=str(loading_html_path),
            width=1200,
            height=800,
            resizable=True,
            min_size=(800, 600),
            text_select=True,
        )
        
        def on_loaded():
            """窗口加载后的回调"""
            log_error("窗口已加载，等待服务器就绪...")
            
            # 等待服务器启动
            if wait_for_server(host, port, timeout=60):
                log_error("服务器就绪，跳转到主页面")
                # 服务器就绪，跳转到 Gradio 界面
                window.load_url(url)
            else:
                log_error("服务器启动超时")
                error_html = get_loading_html("服务器启动失败，请查看日志")
                with open(loading_html_path, 'w', encoding='utf-8') as f:
                    f.write(error_html)
                window.load_url(str(loading_html_path))
        
        # 在后台线程中处理服务器等待
        def background_check():
            time.sleep(1)  # 等待窗口显示
            on_loaded()
        
        check_thread = threading.Thread(target=background_check, daemon=True)
        check_thread.start()
        
        log_error("启动 WebView 主循环...")
        webview.start()
        
        log_error("应用已关闭")
        
        # 清理临时文件
        try:
            if loading_html_path.exists():
                loading_html_path.unlink()
        except Exception:
            pass
        
    except ImportError as e:
        error_msg = f"缺少依赖: {e}\n\n请确保已安装 pywebview:\npip install pywebview"
        log_error(error_msg)
        show_error_dialog("EconPaper Pro - 依赖错误", error_msg, LOG_PATH)
        sys.exit(1)
    except Exception as e:
        error_msg = f"启动失败: {str(e)}"
        log_error(f"{error_msg}\n{traceback.format_exc()}")
        show_error_dialog("EconPaper Pro - 启动错误", error_msg, LOG_PATH)
        sys.exit(1)


def run_web_mode():
    """运行 Web 模式（在浏览器中打开）"""
    global LOG_PATH
    LOG_PATH = get_log_path()
    log_error("="*50)
    log_error(f"EconPaper Pro v{__version__} 启动 (Web 模式)")
    
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
        log_error(f"启动失败: {e}\n{traceback.format_exc()}")
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
        if '--desktop' in sys.argv:
            run_desktop_app()
        else:
            run_web_mode()


def main_gui():
    """GUI 入口点（用于 Windows 打包）"""
    run_desktop_app()


if __name__ == "__main__":
    main()
