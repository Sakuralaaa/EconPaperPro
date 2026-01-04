# -*- coding: utf-8 -*-
"""核心模块 - LLM客户端、嵌入模型、提示词模板、日志、异常处理"""
from .llm import LLMClient, get_llm_client
from .embeddings import EmbeddingClient, get_embedding_client
from .prompts import PromptTemplates
from .logger import (
    setup_logger,
    get_logger,
    log_api_call,
    log_user_action,
    log_performance
)
from .exceptions import (
    EconPaperError,
    ConfigurationError,
    MissingAPIKeyError,
    LLMError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMResponseError,
    LLMTokenLimitError,
    ParserError,
    UnsupportedFileTypeError,
    EmptyContentError,
    ContentTooShortError,
    ProcessingError,
    DiagnosisError,
    OptimizationError,
    ValidationError,
    format_error_message,
    get_user_friendly_message,
)

__all__ = [
    # LLM
    "LLMClient",
    "get_llm_client",
    # Embeddings
    "EmbeddingClient",
    "get_embedding_client",
    # Prompts
    "PromptTemplates",
    # Logger
    "setup_logger",
    "get_logger",
    "log_api_call",
    "log_user_action",
    "log_performance",
    # Exceptions
    "EconPaperError",
    "ConfigurationError",
    "MissingAPIKeyError",
    "LLMError",
    "LLMConnectionError",
    "LLMRateLimitError",
    "LLMAuthenticationError",
    "LLMResponseError",
    "LLMTokenLimitError",
    "ParserError",
    "UnsupportedFileTypeError",
    "EmptyContentError",
    "ContentTooShortError",
    "ProcessingError",
    "DiagnosisError",
    "OptimizationError",
    "ValidationError",
    "format_error_message",
    "get_user_friendly_message",
]
