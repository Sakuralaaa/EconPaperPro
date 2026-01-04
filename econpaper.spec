# -*- mode: python ; coding: utf-8 -*-
"""
EconPaper Pro - PyInstaller Packaging Configuration
Native tkinter GUI application - no browser required
"""

import os
import sys
from pathlib import Path

# Get project root directory
SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
PROJECT_DIR = SPEC_DIR

# Application info
APP_NAME = 'EconPaper Pro'
APP_VERSION = '2.0.0'
APP_ICON = None  # Can be set to 'assets/icon.ico'

# Collect data files
datas = [
    # Example data
    (os.path.join(PROJECT_DIR, 'data', 'exemplars'), 'data/exemplars'),
    # Configuration template
    (os.path.join(PROJECT_DIR, '.env.example'), '.'),
]

# Filter non-existent data files
datas = [(src, dst) for src, dst in datas if os.path.exists(src)]

# Hidden imports - minimal set for native tkinter app
hiddenimports = [
    # ========== tkinter (native GUI) ==========
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    
    # ========== OpenAI ==========
    'openai',
    'openai.resources',
    'openai._client',
    'openai.types',
    
    # ========== HTTP ==========
    'httpx',
    'httpx._transports',
    'httpx._transports.default',
    'httpcore',
    'h11',
    'anyio',
    'anyio._backends',
    'anyio._backends._asyncio',
    'sniffio',
    
    # ========== Pydantic ==========
    'pydantic',
    'pydantic.fields',
    'pydantic.main',
    'pydantic_settings',
    'pydantic_core',
    
    # ========== Document Parsing ==========
    'pypdf',
    'docx',
    
    # ========== Text Processing ==========
    'jieba',
    
    # ========== Other Dependencies ==========
    'dotenv',
    'typing_extensions',
    'annotated_types',
    'packaging',
    'tenacity',
    
    # ========== Project Modules ==========
    'config',
    'config.settings',
    'core',
    'core.llm',
    'core.embeddings',
    'core.exceptions',
    'core.logger',
    'core.prompts',
    'agents',
    'agents.master',
    'agents.diagnostic',
    'agents.optimizer',
    'agents.revision',
    'agents.tools',
    'engines',
    'engines.dedup',
    'engines.deai',
    'engines.similarity',
    'parsers',
    'parsers.pdf_parser',
    'parsers.docx_parser',
    'parsers.structure',
    'knowledge',
    'knowledge.exemplars',
    'knowledge.vector_store',
    'knowledge.search',
    'knowledge.search.google_scholar',
    'knowledge.search.cnki',
    'ui',
    'ui.native_app',
    'utils',
    'utils.diff',
    'utils.text',
    'launcher',
    
    # ========== Python Standard Library ==========
    'json',
    'traceback',
    'datetime',
    'pathlib',
    'logging',
    'logging.handlers',
    'threading',
    'ctypes',
]

# Excluded modules (reduce package size)
excludes = [
    # Web frameworks (not needed for native app)
    'gradio',
    'gradio_client',
    'fastapi',
    'starlette',
    'uvicorn',
    'websockets',
    'webview',
    'pywebview',
    
    # Heavy ML libraries
    'torch',
    'tensorflow',
    'transformers',
    'chromadb',
    'onnxruntime',
    
    # Visualization
    'matplotlib',
    'scipy',
    'pandas',
    'numpy.testing',
    
    # Development tools
    'pytest',
    'setuptools',
    'pip',
    'wheel',
    'black',
    'isort',
    'mypy',
    
    # Other large packages
    'PIL',
    'pillow',
    'jinja2',
]

# Analysis configuration
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

# Remove duplicate files
pyz = PYZ(a.pure, a.zipped_data)

# Main EXE - hide console window
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
    console=False,  # Hide console window, pure GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=APP_ICON,
    version_info=None,
)

# Collect all files
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
