# -*- coding: utf-8 -*-
"""
日志管理模块
使用 loguru 实现统一的日志记录
"""

import sys
import os
from pathlib import Path
from typing import Optional

# 安全导入 loguru
try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False
    logger = None

# 日志系统初始化标志
_logger_initialized = False


def setup_logger(
    log_dir: Optional[str] = None,
    log_level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "7 days",
    console_output: bool = True
) -> None:
    """
    配置日志系统
    
    Args:
        log_dir: 日志目录路径，默认为项目根目录下的 logs 文件夹
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        rotation: 日志轮转大小
        retention: 日志保留时间
        console_output: 是否输出到控制台
    """
    global _logger_initialized
    
    if not LOGURU_AVAILABLE or logger is None:
        _logger_initialized = False
        return
    
    try:
        # 移除默认的 handler
        logger.remove()
        
        # 确定日志目录
        log_path: Path
        if log_dir is None:
            # 尝试使用多个可能的路径
            try:
                # 首选：从配置获取
                from config.settings import settings
                if hasattr(settings, 'data_dir') and settings.data_dir:
                    log_path = Path(settings.data_dir) / "logs"
                else:
                    # 备选：项目根目录
                    project_root = Path(__file__).parent.parent
                    log_path = project_root / "logs"
            except Exception:
                # 最终备选：用户目录
                log_path = Path.home() / ".econpaper" / "logs"
        else:
            log_path = Path(log_dir)
        
        # 创建日志目录
        try:
            log_path.mkdir(parents=True, exist_ok=True)
        except Exception:
            # 如果无法创建目录，只使用控制台输出
            log_path = None
        
        # 日志格式
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        # 简化的控制台格式
        console_format = (
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<level>{message}</level>"
        )
        
        # 控制台输出
        if console_output:
            logger.add(
                sys.stderr,
                format=console_format,
                level=log_level,
                colorize=True
            )
        
        # 只有在成功创建日志目录时才添加文件处理器
        if log_path is not None:
            # 主日志文件 - 所有级别
            logger.add(
                log_path / "app.log",
                format=log_format,
                level="DEBUG",
                rotation=rotation,
                retention=retention,
                encoding="utf-8",
                enqueue=True  # 异步写入，提高性能
            )
            
            # 错误日志文件 - 仅错误和严重级别
            logger.add(
                log_path / "error.log",
                format=log_format,
                level="ERROR",
                rotation=rotation,
                retention=retention,
                encoding="utf-8",
                enqueue=True
            )
            
            # API调用日志 - 专门记录 LLM API 调用
            logger.add(
                log_path / "api.log",
                format=log_format,
                level="DEBUG",
                rotation=rotation,
                retention=retention,
                encoding="utf-8",
                enqueue=True,
                filter=lambda record: "api" in record["extra"]
            )
        
        _logger_initialized = True
        logger.info("日志系统初始化完成")
        
    except Exception as e:
        # 日志系统初始化失败，静默处理
        _logger_initialized = False
        print(f"[警告] 日志系统初始化失败: {e}")


class DummyLogger:
    """占位日志器，当 loguru 不可用时使用"""
    
    def debug(self, msg, *args, **kwargs):
        pass
    
    def info(self, msg, *args, **kwargs):
        pass
    
    def warning(self, msg, *args, **kwargs):
        print(f"[WARN] {msg}")
    
    def error(self, msg, *args, **kwargs):
        print(f"[ERROR] {msg}")
    
    def bind(self, **kwargs):
        return self


_dummy_logger = DummyLogger()


def get_logger(name: str = "econpaper"):
    """
    获取带有模块名称的 logger 实例
    
    Args:
        name: 模块名称
        
    Returns:
        logger: 配置好的 logger 实例
    """
    if not LOGURU_AVAILABLE or logger is None:
        return _dummy_logger
    
    try:
        return logger.bind(module=name)
    except Exception:
        return _dummy_logger


def log_api_call(
    action: str,
    model: str,
    tokens_used: Optional[int] = None,
    latency_ms: Optional[float] = None,
    success: bool = True,
    error: Optional[str] = None
) -> None:
    """
    记录 API 调用信息
    
    Args:
        action: 操作类型 (chat, embed, etc.)
        model: 使用的模型
        tokens_used: 使用的 token 数量
        latency_ms: 延迟毫秒数
        success: 是否成功
        error: 错误信息
    """
    api_logger = logger.bind(api=True)
    
    log_data = {
        "action": action,
        "model": model,
        "tokens": tokens_used,
        "latency_ms": latency_ms,
        "success": success
    }
    
    if success:
        api_logger.info(f"API调用: {action} | 模型: {model} | Tokens: {tokens_used} | 延迟: {latency_ms}ms")
    else:
        api_logger.error(f"API调用失败: {action} | 模型: {model} | 错误: {error}")


def log_user_action(
    action: str,
    details: Optional[str] = None,
    content_length: Optional[int] = None
) -> None:
    """
    记录用户操作
    
    Args:
        action: 操作类型
        details: 操作详情
        content_length: 内容长度
    """
    msg = f"用户操作: {action}"
    if details:
        msg += f" | {details}"
    if content_length:
        msg += f" | 内容长度: {content_length}"
    
    logger.info(msg)


def log_performance(
    operation: str,
    duration_ms: float,
    items_processed: Optional[int] = None
) -> None:
    """
    记录性能指标
    
    Args:
        operation: 操作名称
        duration_ms: 耗时毫秒数
        items_processed: 处理的项目数量
    """
    msg = f"性能: {operation} | 耗时: {duration_ms:.2f}ms"
    if items_processed:
        msg += f" | 处理项: {items_processed}"
    
    logger.debug(msg)


# 在模块加载时自动初始化日志系统
# 可以通过环境变量控制
if os.environ.get("ECONPAPER_INIT_LOGGER", "1") == "1":
    try:
        setup_logger()
    except Exception as e:
        print(f"[警告] 日志初始化异常: {e}")
