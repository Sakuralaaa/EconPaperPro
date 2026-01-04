# -*- coding: utf-8 -*-
"""
EconPaper Pro - 经管学术论文智能优化系统

主入口文件 - 桌面应用模式
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

# ============== 最早期初始化 ==============
# 获取基础目录（在任何其他代码之前）
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
    INTERNAL_DIR = Path(getattr(sys, '_MEIPASS', BASE_DIR))
else:
    BASE_DIR = Path(__file__).parent
    INTERNAL_DIR = BASE_DIR

# 创建日志文件（直接在exe目录下）
LOG_FILE = BASE_DIR / "startup.log"

def write_log(message: str):
    """写入日志（尽早初始化）"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        # 如果连日志都写不了，至少打印到控制台
        print(f"[LOG ERROR] {e}: {message}")

# 第一条日志
write_log("="*60)
write_log("EconPaper Pro 启动")
write_log(f"Python: {sys.version}")
write_log(f"Frozen: {getattr(sys, 'frozen', False)}")
write_log(f"BASE_DIR: {BASE_DIR}")
write_log(f"INTERNAL_DIR: {INTERNAL_DIR}")
write_log(f"sys.executable: {sys.executable}")
write_log(f"sys.path: {sys.path}")

# 添加路径
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(INTERNAL_DIR))
write_log(f"Updated sys.path: {sys.path}")

# ============== 版本信息 ==============
__version__ = "1.0.3"
__app_name__ = "EconPaper Pro"

# ============== 辅助函数 ==============

def show_error_dialog(title: str, message: str):
    """显示错误对话框"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        full_message = f"{message}\n\n日志文件: {LOG_FILE}"
        messagebox.showerror(title, full_message)
        root.destroy()
    except Exception as e:
        write_log(f"显示错误对话框失败: {e}")


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


def wait_for_server(host: str, port: int, timeout: int = 120) -> bool:
    """等待服务器启动"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_open(host, port):
            write_log(f"服务器就绪 (耗时 {time.time() - start_time:.1f}s)")
            return True
        time.sleep(1)
        elapsed = time.time() - start_time
        if int(elapsed) % 5 == 0:
            write_log(f"等待服务器... {elapsed:.0f}s")
    return False


# ============== Gradio 服务器 ==============

gradio_error = None
gradio_started = False

def start_gradio_server(host: str, port: int):
    """启动 Gradio 服务器"""
    global gradio_error, gradio_started
    
    try:
        write_log("--- 开始启动 Gradio 服务 ---")
        
        # 尝试导入配置
        write_log("导入 config.settings...")
        try:
            from config.settings import settings
            write_log(f"配置加载成功: host={settings.app_host}, port={settings.app_port}")
        except Exception as e:
            write_log(f"配置导入失败: {e}")
            write_log(traceback.format_exc())
            raise
        
        # 尝试导入 UI
        write_log("导入 ui.app...")
        try:
            from ui.app import create_app
            write_log("UI 模块导入成功")
        except Exception as e:
            write_log(f"UI 导入失败: {e}")
            write_log(traceback.format_exc())
            raise
        
        # 创建应用
        write_log("创建 Gradio 应用...")
        try:
            app = create_app()
            write_log("Gradio 应用创建成功")
        except Exception as e:
            write_log(f"创建应用失败: {e}")
            write_log(traceback.format_exc())
            raise
        
        # 启动服务器
        write_log(f"启动 Gradio 于 {host}:{port}...")
        app.launch(
            server_name=host,
            server_port=port,
            share=False,
            inbrowser=False,
            quiet=True,
            prevent_thread_lock=True
        )
        write_log("Gradio 服务已启动")
        gradio_started = True
        
    except Exception as e:
        gradio_error = str(e)
        write_log(f"Gradio 启动失败: {e}")
        write_log(traceback.format_exc())


# ============== 加载页面 HTML ==============

LOADING_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="3;url=http://127.0.0.1:7860">
    <title>EconPaper Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
        }
        .container {
            text-align: center;
            padding: 40px;
        }
        .logo { font-size: 64px; margin-bottom: 20px; }
        .title { font-size: 36px; font-weight: bold; margin-bottom: 10px; }
        .subtitle { font-size: 18px; opacity: 0.8; margin-bottom: 40px; }
        .spinner {
            width: 60px; height: 60px;
            border: 5px solid rgba(255,255,255,0.3);
            border-top: 5px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 30px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .message { font-size: 20px; }
        .hint { font-size: 14px; opacity: 0.6; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📚</div>
        <div class="title">EconPaper Pro</div>
        <div class="subtitle">经管学术论文智能优化系统</div>
        <div class="spinner"></div>
        <div class="message">正在启动，请稍候...</div>
        <div class="hint">首次启动可能需要 10-30 秒</div>
    </div>
</body>
</html>
'''


# ============== 首次设置向导 ==============

def run_setup_wizard() -> bool:
    """运行首次设置向导"""
    try:
        write_log("检查首次运行设置...")
        from launcher import run_launcher
        result = run_launcher()
        write_log(f"设置向导结果: {result}")
        return result
    except ImportError as e:
        write_log(f"launcher 模块不存在，跳过设置: {e}")
        return True
    except Exception as e:
        write_log(f"设置向导异常: {e}")
        write_log(traceback.format_exc())
        return True


# ============== 桌面应用模式 ==============

def run_desktop_app():
    """运行桌面应用"""
    write_log("--- 进入桌面应用模式 ---")
    
    try:
        # 首次设置
        if getattr(sys, 'frozen', False):
            if not run_setup_wizard():
                write_log("用户取消设置")
                return
        
        host = "127.0.0.1"
        port = 7860
        url = f"http://{host}:{port}"
        
        # 启动 Gradio 后台服务
        write_log("启动 Gradio 后台线程...")
        server_thread = threading.Thread(
            target=start_gradio_server,
            args=(host, port),
            daemon=True
        )
        server_thread.start()
        
        # 创建加载页面
        loading_html_path = BASE_DIR / "loading.html"
        write_log(f"创建加载页面: {loading_html_path}")
        try:
            with open(loading_html_path, 'w', encoding='utf-8') as f:
                f.write(LOADING_HTML)
        except Exception as e:
            write_log(f"创建加载页面失败: {e}")
        
        # 导入并启动 PyWebView
        write_log("导入 webview...")
        try:
            import webview
            write_log("webview 导入成功")
        except ImportError as e:
            write_log(f"webview 导入失败: {e}")
            show_error_dialog("依赖错误", f"无法导入 pywebview:\n{e}")
            return
        
        # 创建窗口
        write_log("创建主窗口...")
        
        def on_shown():
            """窗口显示后的回调"""
            write_log("窗口已显示")
        
        def on_loaded():
            """页面加载完成后的回调"""
            write_log("页面已加载")
        
        window = webview.create_window(
            title=f'{__app_name__} v{__version__}',
            url=str(loading_html_path),
            width=1200,
            height=800,
            resizable=True,
            min_size=(800, 600),
            text_select=True,
        )
        
        # 在后台检查服务是否就绪，然后跳转
        def check_and_redirect():
            write_log("后台检查线程启动")
            time.sleep(2)  # 等待窗口完全显示
            
            if wait_for_server(host, port, timeout=120):
                write_log("服务就绪，跳转到主界面")
                try:
                    window.load_url(url)
                except Exception as e:
                    write_log(f"跳转失败: {e}")
            else:
                write_log("服务启动超时")
                if gradio_error:
                    write_log(f"Gradio 错误: {gradio_error}")
        
        check_thread = threading.Thread(target=check_and_redirect, daemon=True)
        check_thread.start()
        
        write_log("启动 WebView 主循环...")
        webview.start()
        write_log("应用已关闭")
        
        # 清理
        try:
            if loading_html_path.exists():
                loading_html_path.unlink()
        except Exception:
            pass
        
    except Exception as e:
        write_log(f"桌面应用模式异常: {e}")
        write_log(traceback.format_exc())
        show_error_dialog("启动错误", str(e))


# ============== Web 模式 ==============

def run_web_mode():
    """运行 Web 模式（开发用）"""
    write_log("--- 进入 Web 模式 ---")
    
    try:
        from config.settings import settings
        from ui.app import create_app
        
        app = create_app()
        
        print(f"\n{'='*50}")
        print(f"  📚 {__app_name__} v{__version__}")
        print(f"{'='*50}")
        print(f"\n  🌐 http://{settings.app_host}:{settings.app_port}")
        print(f"  按 Ctrl+C 停止\n")
        
        app.launch(
            server_name=settings.app_host,
            server_port=settings.app_port,
            share=False,
            inbrowser=True
        )
    except KeyboardInterrupt:
        print("\n👋 已停止")
    except Exception as e:
        write_log(f"Web 模式异常: {e}")
        print(f"❌ 错误: {e}")


# ============== 主入口 ==============

def main():
    """主函数"""
    write_log("=== main() 开始 ===")
    
    if '--web' in sys.argv:
        run_web_mode()
    elif getattr(sys, 'frozen', False):
        run_desktop_app()
    else:
        if '--desktop' in sys.argv:
            run_desktop_app()
        else:
            run_web_mode()


def main_gui():
    """GUI 入口（PyInstaller 使用）"""
    run_desktop_app()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        write_log(f"顶层异常: {e}")
        write_log(traceback.format_exc())
        show_error_dialog("严重错误", str(e))
