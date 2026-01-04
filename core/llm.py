# -*- coding: utf-8 -*-
"""
LLM客户端模块
支持所有OpenAI兼容接口（OpenAI、DeepSeek、硅基流动、Ollama等）
"""

import time
from typing import Optional, List, Dict, Generator, Union
from openai import OpenAI
import openai
from config.settings import settings
from core.logger import get_logger, log_api_call
from core.exceptions import (
    MissingAPIKeyError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMResponseError,
    LLMTokenLimitError,
)

# 获取模块日志器
logger = get_logger("llm")


class LLMClient:
    """
    统一LLM客户端
    
    使用示例:
        client = LLMClient()
        response = client.invoke("你好")
        
        # 自定义配置
        client = LLMClient(
            api_base="https://api.deepseek.com/v1",
            api_key="sk-xxx",
            model="deepseek-chat"
        )
    """
    
    def __init__(
        self,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        """
        初始化LLM客户端
        
        Args:
            api_base: API 地址，默认从配置读取
            api_key: API 密钥，默认从配置读取
            model: 模型名称，默认从配置读取
            temperature: 生成温度
            max_tokens: 最大生成 token 数
        """
        self.api_base = api_base or settings.llm_api_base
        self.api_key = api_key or settings.llm_api_key
        self.model = model or settings.llm_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 验证 API 密钥
        if not self.api_key:
            logger.error("LLM API 密钥未配置")
            raise MissingAPIKeyError(service="LLM")
        
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            base_url=self.api_base,
            api_key=self.api_key
        )
        
        logger.info(f"LLM 客户端初始化成功: api_base={self.api_base}, model={self.model}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[str, Generator[str, None, None]]:
        """
        发送对话请求
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            stream: 是否使用流式输出
            **kwargs: 其他参数传递给 API
            
        Returns:
            str 或 Generator: 非流式返回完整文本，流式返回生成器
            
        Raises:
            LLMConnectionError: 网络连接失败
            LLMRateLimitError: API 速率限制
            LLMAuthenticationError: 认证失败
            LLMTokenLimitError: Token 超限
            LLMResponseError: 其他响应错误
        """
        start_time = time.time()
        prompt_preview = ""
        if messages:
            last_msg = messages[-1].get("content", "")
            prompt_preview = last_msg[:100] + "..." if len(last_msg) > 100 else last_msg
        
        logger.debug(f"发送 LLM 请求: model={self.model}, stream={stream}, messages_count={len(messages)}")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                stream=stream,
                **{k: v for k, v in kwargs.items()
                   if k not in ["temperature", "max_tokens"]}
            )
            
            if stream:
                logger.debug("返回流式响应生成器")
                return self._stream_response(response)
            else:
                result = response.choices[0].message.content or ""
                elapsed = time.time() - start_time
                
                # 记录 API 调用日志
                log_api_call(
                    action="chat",
                    model=self.model,
                    tokens_used=getattr(response.usage, 'total_tokens', None) if hasattr(response, 'usage') else None,
                    latency_ms=elapsed * 1000  # 转换为毫秒
                )
                
                logger.info(f"LLM 请求完成: 耗时 {elapsed:.2f}s, 响应长度 {len(result)} 字符")
                return result
                
        except openai.AuthenticationError as e:
            logger.error(f"LLM 认证失败: {e}")
            raise LLMAuthenticationError(
                message=f"API 认证失败: {str(e)}",
                details={"original_error": str(e), "api_base": self.api_base}
            )
        except openai.RateLimitError as e:
            logger.warning(f"LLM 速率限制: {e}")
            raise LLMRateLimitError(
                message=f"API 调用频率超限: {str(e)}",
                retry_after=getattr(e, 'retry_after', None),
                details={"original_error": str(e), "api_base": self.api_base}
            )
        except openai.APIConnectionError as e:
            logger.error(f"LLM 连接失败: {e}")
            raise LLMConnectionError(
                message=f"无法连接到 LLM API 服务: {str(e)}",
                api_base=self.api_base,
                details={"original_error": str(e)}
            )
        except openai.BadRequestError as e:
            error_msg = str(e)
            if "maximum context length" in error_msg.lower() or "token" in error_msg.lower():
                logger.error(f"Token 超限: {e}")
                raise LLMTokenLimitError(
                    message=f"输入内容超出模型 Token 限制: {error_msg}",
                    details={"original_error": error_msg, "model": self.model}
                )
            else:
                logger.error(f"LLM 请求错误: {e}")
                raise LLMResponseError(
                    message=f"LLM 请求失败: {error_msg}",
                    details={"original_error": error_msg}
                )
        except openai.APIStatusError as e:
            logger.error(f"LLM API 状态错误: {e}")
            raise LLMResponseError(
                message=f"LLM API 错误: {str(e)}",
                details={"original_error": str(e), "status_code": getattr(e, 'status_code', None)}
            )
        except Exception as e:
            logger.error(f"LLM 调用发生未知错误: {type(e).__name__}: {e}")
            raise LLMResponseError(
                message=f"LLM 调用失败: {str(e)}",
                details={"error_type": type(e).__name__, "original_error": str(e)}
            )
    
    def _stream_response(self, response) -> Generator[str, None, None]:
        """处理流式响应"""
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def invoke(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        简化调用接口
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词（可选）
            **kwargs: 其他参数
            
        Returns:
            str: LLM 响应文本
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return self.chat(messages, stream=False, **kwargs)
    
    def invoke_with_context(
        self,
        prompt: str,
        context: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        带上下文调用
        
        Args:
            prompt: 用户提示词
            context: 上下文内容
            system_prompt: 系统提示词（可选）
            **kwargs: 其他参数
            
        Returns:
            str: LLM 响应文本
        """
        full_prompt = f"上下文信息:\n{context}\n\n用户请求:\n{prompt}"
        return self.invoke(full_prompt, system_prompt=system_prompt, **kwargs)
    
    def invoke_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        流式调用接口
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词（可选）
            **kwargs: 其他参数
            
        Yields:
            str: LLM 响应文本片段
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return self.chat(messages, stream=True, **kwargs)


# 单例存储
_llm_client: Optional[LLMClient] = None
_backup_llm_client: Optional[LLMClient] = None


def get_llm_client(use_backup: bool = False) -> LLMClient:
    """
    获取 LLM 客户端单例
    
    Args:
        use_backup: 是否使用备用客户端
        
    Returns:
        LLMClient: LLM 客户端实例
    """
    global _llm_client, _backup_llm_client
    
    if use_backup:
        if _backup_llm_client is None:
            if settings.llm_backup_api_base and settings.llm_backup_api_key:
                _backup_llm_client = LLMClient(
                    api_base=settings.llm_backup_api_base,
                    api_key=settings.llm_backup_api_key,
                    model=settings.llm_backup_model or settings.llm_model
                )
            else:
                raise ValueError("备用 LLM 配置不完整")
        return _backup_llm_client
    else:
        if _llm_client is None:
            _llm_client = LLMClient()
        return _llm_client
