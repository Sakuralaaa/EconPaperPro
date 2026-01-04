# -*- mode: python ; coding: utf-8 -*-
"""
EconPaper Pro - PyInstaller 打包配置

用于将应用打包为 Windows 可执行文件（无控制台窗口）
"""

import os
import sys
from pathlib import Path

# 获取项目根目录
SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
PROJECT_DIR = SPEC_DIR

# 应用信息
APP_NAME = 'EconPaper Pro'
APP_VERSION = '1.0.0'
APP_ICON = None  # 可以设置为 'assets/icon.ico'

# 收集数据文件
datas = [
    # 范例数据
    (os.path.join(PROJECT_DIR, 'data', 'exemplars'), 'data/exemplars'),
    # 提示词模板
    (os.path.join(PROJECT_DIR, 'prompts'), 'prompts'),
    # 配置文件模板
    (os.path.join(PROJECT_DIR, '.env.example'), '.'),
]

# 过滤不存在的数据文件
datas = [(src, dst) for src, dst in datas if os.path.exists(src)]

# 隐式导入的模块 - 完整列表确保所有依赖被包含
hiddenimports = [
    # ========== PyWebView (桌面窗口) ==========
    'webview',
    'webview.platforms',
    'webview.platforms.winforms',
    'webview.platforms.edgechromium',
    'webview.platforms.cef',
    'clr',
    'clr_loader',
    'pythonnet',
    
    # ========== Gradio 及其依赖 ==========
    'gradio',
    'gradio.themes',
    'gradio.themes.base',
    'gradio.themes.soft',
    'gradio.components',
    'gradio.blocks',
    'gradio.interface',
    'gradio.layouts',
    'gradio.routes',
    'gradio.utils',
    'gradio.processing_utils',
    'gradio.networking',
    'gradio_client',
    'gradio_client.utils',
    
    # ========== FastAPI / Starlette / Uvicorn ==========
    'fastapi',
    'fastapi.applications',
    'fastapi.routing',
    'fastapi.middleware',
    'starlette',
    'starlette.applications',
    'starlette.routing',
    'starlette.middleware',
    'starlette.responses',
    'starlette.requests',
    'starlette.staticfiles',
    'starlette.templating',
    'starlette.websockets',
    'uvicorn',
    'uvicorn.main',
    'uvicorn.config',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    
    # ========== HTTP / 网络 ==========
    'httpx',
    'httpx._transports',
    'httpx._transports.default',
    'httpcore',
    'h11',
    'anyio',
    'anyio._backends',
    'anyio._backends._asyncio',
    'sniffio',
    'websockets',
    'websockets.legacy',
    'websockets.legacy.server',
    
    # ========== OpenAI ==========
    'openai',
    'openai.resources',
    'openai._client',
    'openai.types',
    
    # ========== ChromaDB ==========
    'chromadb',
    'chromadb.config',
    'chromadb.api',
    'chromadb.db',
    'chromadb.segment',
    'onnxruntime',
    'tokenizers',
    
    # ========== Pydantic ==========
    'pydantic',
    'pydantic.fields',
    'pydantic.main',
    'pydantic_settings',
    'pydantic_core',
    
    # ========== 其他依赖 ==========
    'aiofiles',
    'python_multipart',
    'multipart',
    'jinja2',
    'markupsafe',
    'orjson',
    'typing_extensions',
    'annotated_types',
    'packaging',
    'pillow',
    'PIL',
    'PIL.Image',
    
    # ========== tkinter (设置向导) ==========
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    
    # ========== 项目模块 ==========
    'config',
    'config.settings',
    'core',
    'core.llm',
    'core.embedding',
    'core.knowledge_base',
    'core.optimizer',
    'core.logger',
    'core.exceptions',
    'ui',
    'ui.app',
    'ui.components',
    'launcher',
    
    # ========== Python 标准库 ==========
    'json',
    'webbrowser',
    'traceback',
    'datetime',
    'pathlib',
    'logging',
    'logging.handlers',
]

# 排除的模块（减小包体积）
excludes = [
    'matplotlib',
    'scipy',
    'numpy.testing',
    'pytest',
    'setuptools',
    'pip',
    'wheel',
    'black',
    'isort',
    'mypy',
]

# 分析配置
a = Analysis(
    [os.path.join(PROJECT_DIR, 'main.py')],
    pathex=[PROJECT_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

# 清理重复文件
pyz = PYZ(a.pure, a.zipped_data)

# 主程序 EXE - 隐藏控制台窗口
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EconPaperPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # ★ 隐藏控制台窗口，显示为纯 GUI 应用
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=APP_ICON,
    version_info=None,
)

# 收集所有文件
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EconPaperPro',
)
