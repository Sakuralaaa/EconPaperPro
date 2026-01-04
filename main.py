# -*- coding: utf-8 -*-
"""
EconPaper Pro - 经管学术论文智能优化系统

主入口文件
支持 Windows 桌面应用模式
"""

import sys
import os

# 添加项目根目录到 Python 路径
if getattr(sys, 'frozen', False):
    # 打包后的应用
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 开发环境
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)

# 版本信息
__version__ = "1.0.0"
__app_name__ = "EconPaper Pro"


def print_banner():
    """打印启动横幅"""
    banner = f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ███████╗ ██████╗ ██████╗ ███╗   ██╗                    ║
    ║   ██╔════╝██╔════╝██╔═══██╗████╗  ██║                    ║
    ║   █████╗  ██║     ██║   ██║██╔██╗ ██║                    ║
    ║   ██╔══╝  ██║     ██║   ██║██║╚██╗██║                    ║
    ║   ███████╗╚██████╗╚██████╔╝██║ ╚████║                    ║
    ║   ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝                    ║
    ║                                                           ║
    ║   📚 {__app_name__} v{__version__}                                   ║
    ║   经管学术论文智能优化系统                                ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_config():
    """检查配置"""
    from config.settings import settings
    
    print("📋 配置检查...")
    print(f"   LLM API: {settings.llm_api_base}")
    print(f"   LLM Model: {settings.llm_model}")
    print(f"   Embedding API: {settings.embedding_api_base}")
    print(f"   Embedding Model: {settings.embedding_model}")
    print(f"   数据目录: {settings.data_dir}")
    print(f"   工作区: {settings.workspace_dir}")
    
    if not settings.llm_api_key:
        print("\n⚠️  警告: LLM API Key 未配置，部分功能可能无法使用")
        print("   请在设置中配置 API Key 或编辑 .env 文件")
    
    print()


def run_setup_wizard():
    """运行首次设置向导"""
    try:
        from launcher import run_launcher
        return run_launcher()
    except ImportError:
        # 如果启动器模块不可用，跳过设置向导
        return True
    except Exception as e:
        print(f"⚠️  设置向导启动失败: {e}")
        return True


def main():
    """主函数"""
    # 检查是否需要运行设置向导
    if getattr(sys, 'frozen', False):
        # 打包后的应用，检查首次运行
        if not run_setup_wizard():
            print("用户取消了设置，应用退出")
            sys.exit(0)
    
    print_banner()
    check_config()
    
    print("🚀 启动应用...")
    print()
    
    try:
        from ui.app import create_app
        from config.settings import settings
        
        app = create_app()
        
        print(f"✅ 应用已启动")
        print(f"🌐 访问地址: http://{settings.app_host}:{settings.app_port}")
        print()
        print("按 Ctrl+C 停止应用")
        print()
        
        app.launch(
            server_name=settings.app_host,
            server_port=settings.app_port,
            share=False,
            inbrowser=True
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 应用已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main_gui():
    """
    GUI 入口点（用于 Windows 打包）
    隐藏控制台窗口
    """
    main()


if __name__ == "__main__":
    main()
