# -*- coding: utf-8 -*-
"""
智能重试机制模块
支持指数退避重试和自动故障恢复
"""

import time
import random
from functools import wraps
from typing import Callable, Optional, Tuple, Type, Union
import logging

logger = logging.getLogger(__name__)


class RetryConfig:
    """重试配置"""
    
    # 默认重试次数
    MAX_RETRIES = 3
    
    # 初始延迟（秒）
    INITIAL_DELAY = 1.0
    
    # 退避因子
    BACKOFF_FACTOR = 2.0
    
    # 最大延迟（秒）
    MAX_DELAY = 30.0
    
    # 抖动范围（避免雷群效应）
    JITTER_RANGE = 0.1
    
    # 可重试的异常类型
    RETRYABLE_EXCEPTIONS: Tuple[Type[Exception], ...] = (
        ConnectionError,
        TimeoutError,
        OSError,
    )


class RetryError(Exception):
    """重试失败异常"""
    
    def __init__(self, message: str, last_error: Exception, attempts: int):
        super().__init__(message)
        self.last_error = last_error
        self.attempts = attempts


class RetryState:
    """重试状态跟踪"""
    
    def __init__(self):
        self.attempt = 0
        self.total_delay = 0.0
        self.errors = []
    
    def record_attempt(self, error: Exception, delay: float):
        """记录一次重试尝试"""
        self.attempt += 1
        self.total_delay += delay
        self.errors.append(str(error))


def calculate_delay(
    attempt: int,
    initial_delay: float = RetryConfig.INITIAL_DELAY,
    backoff_factor: float = RetryConfig.BACKOFF_FACTOR,
    max_delay: float = RetryConfig.MAX_DELAY,
    jitter_range: float = RetryConfig.JITTER_RANGE
) -> float:
    """
    计算重试延迟（指数退避 + 随机抖动）
    
    Args:
        attempt: 当前尝试次数（从0开始）
        initial_delay: 初始延迟
        backoff_factor: 退避因子
        max_delay: 最大延迟
        jitter_range: 抖动范围（0-1）
    
    Returns:
        float: 延迟秒数
    """
    # 指数退避
    delay = initial_delay * (backoff_factor ** attempt)
    
    # 限制最大延迟
    delay = min(delay, max_delay)
    
    # 添加随机抖动
    jitter = delay * jitter_range * random.uniform(-1, 1)
    delay = max(0, delay + jitter)
    
    return delay


def is_retryable(
    error: Exception,
    retryable_exceptions: Tuple[Type[Exception], ...] = RetryConfig.RETRYABLE_EXCEPTIONS
) -> bool:
    """
    检查异常是否可重试
    
    Args:
        error: 异常实例
        retryable_exceptions: 可重试的异常类型元组
    
    Returns:
        bool: 是否可重试
    """
    # 检查是否为可重试异常类型
    if isinstance(error, retryable_exceptions):
        return True
    
    # 检查 OpenAI 特定错误
    error_str = str(error).lower()
    retryable_keywords = [
        'timeout',
        'connection',
        'rate limit',
        'too many requests',
        'service unavailable',
        '503',
        '502',
        '504',
        'overloaded',
        'capacity',
    ]
    
    for keyword in retryable_keywords:
        if keyword in error_str:
            return True
    
    return False


def with_retry(
    max_retries: int = RetryConfig.MAX_RETRIES,
    initial_delay: float = RetryConfig.INITIAL_DELAY,
    backoff_factor: float = RetryConfig.BACKOFF_FACTOR,
    max_delay: float = RetryConfig.MAX_DELAY,
    retryable_exceptions: Tuple[Type[Exception], ...] = RetryConfig.RETRYABLE_EXCEPTIONS,
    on_retry: Optional[Callable[[int, int, Exception, float], None]] = None,
    on_success: Optional[Callable[[int], None]] = None,
    on_failure: Optional[Callable[[int, Exception], None]] = None
):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        initial_delay: 初始延迟
        backoff_factor: 退避因子
        max_delay: 最大延迟
        retryable_exceptions: 可重试的异常类型
        on_retry: 重试回调 (attempt, max_retries, error, delay) -> None
        on_success: 成功回调 (attempts) -> None
        on_failure: 失败回调 (attempts, last_error) -> None
    
    Returns:
        装饰器函数
    
    Usage:
        @with_retry(max_retries=3, on_retry=lambda a, m, e, d: print(f"重试 {a}/{m}"))
        def call_api():
            return requests.get(url)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            state = RetryState()
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # 成功回调
                    if on_success and attempt > 0:
                        on_success(attempt + 1)
                    
                    return result
                    
                except Exception as e:
                    last_error = e
                    
                    # 检查是否可重试
                    if not is_retryable(e, retryable_exceptions):
                        logger.warning(f"不可重试的异常: {type(e).__name__}: {e}")
                        raise
                    
                    # 已达最大重试次数
                    if attempt >= max_retries:
                        logger.error(f"重试 {max_retries} 次后仍然失败: {e}")
                        
                        # 失败回调
                        if on_failure:
                            on_failure(attempt + 1, e)
                        
                        raise RetryError(
                            f"经过 {max_retries + 1} 次尝试后失败",
                            last_error=e,
                            attempts=max_retries + 1
                        )
                    
                    # 计算延迟
                    delay = calculate_delay(
                        attempt,
                        initial_delay,
                        backoff_factor,
                        max_delay
                    )
                    
                    # 记录状态
                    state.record_attempt(e, delay)
                    
                    # 重试回调
                    if on_retry:
                        on_retry(attempt + 1, max_retries, e, delay)
                    
                    logger.info(
                        f"重试 {attempt + 1}/{max_retries}: "
                        f"等待 {delay:.1f}s... "
                        f"错误: {type(e).__name__}"
                    )
                    
                    # 等待
                    time.sleep(delay)
            
            # 理论上不会到达这里
            if last_error is not None:
                raise last_error
            raise RuntimeError("重试失败但没有记录错误")
        
        return wrapper
    return decorator


class RetryContext:
    """
    重试上下文管理器
    
    Usage:
        with RetryContext(max_retries=3) as retry:
            while retry.should_continue():
                try:
                    result = do_something()
                    break
                except Exception as e:
                    retry.record_failure(e)
    """
    
    def __init__(
        self,
        max_retries: int = RetryConfig.MAX_RETRIES,
        initial_delay: float = RetryConfig.INITIAL_DELAY,
        backoff_factor: float = RetryConfig.BACKOFF_FACTOR,
        max_delay: float = RetryConfig.MAX_DELAY,
        on_retry: Optional[Callable[[int, int, Exception, float], None]] = None
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        self.on_retry = on_retry
        
        self._attempt = 0
        self._last_error = None
        self._success = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and not self._success:
            if self._attempt >= self.max_retries:
                raise RetryError(
                    f"经过 {self.max_retries + 1} 次尝试后失败",
                    last_error=exc_val,
                    attempts=self._attempt + 1
                )
        return False
    
    def should_continue(self) -> bool:
        """是否应该继续尝试"""
        return self._attempt <= self.max_retries and not self._success
    
    def record_failure(self, error: Exception):
        """记录失败"""
        self._last_error = error
        
        if not is_retryable(error):
            raise error
        
        if self._attempt < self.max_retries:
            delay = calculate_delay(
                self._attempt,
                self.initial_delay,
                self.backoff_factor,
                self.max_delay
            )
            
            if self.on_retry:
                self.on_retry(self._attempt + 1, self.max_retries, error, delay)
            
            logger.info(f"重试 {self._attempt + 1}/{self.max_retries}: 等待 {delay:.1f}s...")
            time.sleep(delay)
        
        self._attempt += 1
    
    def record_success(self):
        """记录成功"""
        self._success = True
    
    @property
    def attempt(self) -> int:
        """当前尝试次数"""
        return self._attempt
    
    @property
    def last_error(self) -> Optional[Exception]:
        """最后一个错误"""
        return self._last_error


# 预配置的重试装饰器
def retry_on_network_error(func):
    """网络错误重试装饰器（预配置）"""
    return with_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0
    )(func)


def retry_on_rate_limit(func):
    """速率限制重试装饰器（更长延迟）"""
    return with_retry(
        max_retries=5,
        initial_delay=2.0,
        backoff_factor=2.5,
        max_delay=60.0
    )(func)