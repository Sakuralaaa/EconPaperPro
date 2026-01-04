# -*- coding: utf-8 -*-
"""
配置管理模块
使用 pydantic-settings 管理环境变量，从 .env 文件读取配置
支持用户自定义数据目录和工作区目录
"""

import os
import sys
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


def get_app_data_dir() -> Path:
    """获取应用数据目录"""
    # 优先使用环境变量
    if os.environ.get('ECONPAPER_DATA_DIR'):
        return Path(os.environ['ECONPAPER_DATA_DIR'])
    
    # 打包后使用 AppData 目录
    if getattr(sys, 'frozen', False):
        app_data = Path(os.environ.get('APPDATA', os.path.expanduser('~')))
        return app_data / 'EconPaperPro' / 'data'
    
    # 开发环境使用项目目录
    return Path(__file__).parent.parent / 'data'


def get_workspace_dir() -> Path:
    """获取工作区目录"""
    # 优先使用环境变量
    if os.environ.get('ECONPAPER_WORKSPACE_DIR'):
        return Path(os.environ['ECONPAPER_WORKSPACE_DIR'])
    
    # 默认使用文档目录
    documents = Path(os.path.expanduser('~')) / 'Documents'
    return documents / 'EconPaperPro'


class Settings(BaseSettings):
    """
    应用配置类
    
    所有配置项从环境变量读取，支持 .env 文件
    支持用户自定义目录
    """
    
    # LLM 配置
    llm_api_base: str = Field(
        default="https://api.openai.com/v1",
        description="LLM API 地址"
    )
    llm_api_key: str = Field(
        default="",
        description="LLM API 密钥"
    )
    llm_model: str = Field(
        default="gpt-4o-mini",
        description="LLM 模型名称"
    )
    
    # 备用 LLM 配置（可选）
    llm_backup_api_base: Optional[str] = Field(
        default=None,
        description="备用 LLM API 地址"
    )
    llm_backup_api_key: Optional[str] = Field(
        default=None,
        description="备用 LLM API 密钥"
    )
    llm_backup_model: Optional[str] = Field(
        default=None,
        description="备用 LLM 模型名称"
    )
    
    # 嵌入模型配置
    embedding_api_base: str = Field(
        default="https://api.openai.com/v1",
        description="嵌入 API 地址"
    )
    embedding_api_key: str = Field(
        default="",
        description="嵌入 API 密钥"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="嵌入模型名称"
    )
    
    # 向量数据库配置
    chroma_persist_dir: str = Field(
        default="",
        description="ChromaDB 持久化存储路径"
    )
    
    # 用户自定义目录
    data_dir: str = Field(
        default="",
        description="数据存储目录"
    )
    workspace_dir: str = Field(
        default="",
        description="工作区目录"
    )
    
    # 学术搜索配置（可选）
    serpapi_key: Optional[str] = Field(
        default=None,
        description="SerpAPI 密钥"
    )
    
    # 应用配置
    app_host: str = Field(
        default="127.0.0.1",
        description="应用主机地址"
    )
    app_port: int = Field(
        default=7860,
        description="应用端口"
    )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 设置默认目录
        if not self.data_dir:
            self.data_dir = str(get_app_data_dir())
        if not self.workspace_dir:
            self.workspace_dir = str(get_workspace_dir())
        if not self.chroma_persist_dir:
            self.chroma_persist_dir = str(Path(self.data_dir) / 'chroma_db')
        
        # 确保目录存在
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.workspace_dir).mkdir(parents=True, exist_ok=True)
        Path(self.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
    
    @property
    def log_dir(self) -> Path:
        """日志目录"""
        log_path = Path(self.data_dir) / 'logs'
        log_path.mkdir(parents=True, exist_ok=True)
        return log_path
    
    @property
    def cache_dir(self) -> Path:
        """缓存目录"""
        cache_path = Path(self.data_dir) / 'cache'
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path
    
    @property
    def output_dir(self) -> Path:
        """输出目录"""
        output_path = Path(self.workspace_dir) / 'output'
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path


# 全局配置实例
settings = Settings()
