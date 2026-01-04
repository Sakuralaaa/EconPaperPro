# -*- coding: utf-8 -*-
"""
自定义异常模块
定义项目中使用的所有自定义异常类
"""

from typing import Optional, Dict, Any


class EconPaperError(Exception):
    """
    EconPaper Pro 基础异常类
    
    所有自定义异常都继承自此类
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 详细信息字典
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error": self.__class__.__name__,
            "code": self.error_code,
            "message": self.message,
            "details": self.details
        }
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


# ==================== 配置相关异常 ====================

class ConfigurationError(EconPaperError):
    """配置错误"""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if config_key:
            details["config_key"] = config_key
        
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            details=details
        )
        self.config_key = config_key


class MissingAPIKeyError(ConfigurationError):
    """API密钥缺失错误"""
    
    def __init__(self, service: str = "LLM"):
        super().__init__(
            message=f"{service} API 密钥未配置。请在 .env 文件中设置相应的 API_KEY。",
            config_key=f"{service.upper()}_API_KEY",
            details={"service": service}
        )
        self.error_code = "MISSING_API_KEY"


# ==================== LLM API 相关异常 ====================

class LLMError(EconPaperError):
    """LLM 相关错误基类"""
    pass


class LLMConnectionError(LLMError):
    """LLM 连接错误"""
    
    def __init__(
        self,
        message: str = "无法连接到 LLM API 服务",
        api_base: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if api_base:
            details["api_base"] = api_base
        
        super().__init__(
            message=message,
            error_code="LLM_CONNECTION_ERROR",
            details=details
        )


class LLMRateLimitError(LLMError):
    """LLM API 限流错误"""
    
    def __init__(
        self,
        message: str = "API 调用频率超限，请稍后重试",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        
        super().__init__(
            message=message,
            error_code="LLM_RATE_LIMIT",
            details=details
        )
        self.retry_after = retry_after


class LLMAuthenticationError(LLMError):
    """LLM API 认证错误"""
    
    def __init__(
        self,
        message: str = "API 认证失败，请检查 API 密钥是否正确",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="LLM_AUTH_ERROR",
            details=details
        )


class LLMResponseError(LLMError):
    """LLM 响应解析错误"""
    
    def __init__(
        self,
        message: str = "LLM 响应格式异常",
        response: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if response:
            # 截断过长的响应
            details["response_preview"] = response[:500] if len(response) > 500 else response
        
        super().__init__(
            message=message,
            error_code="LLM_RESPONSE_ERROR",
            details=details
        )


class LLMTokenLimitError(LLMError):
    """Token 限制错误"""
    
    def __init__(
        self,
        message: str = "输入内容超出模型 Token 限制",
        token_count: Optional[int] = None,
        max_tokens: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if token_count:
            details["token_count"] = token_count
        if max_tokens:
            details["max_tokens"] = max_tokens
        
        super().__init__(
            message=message,
            error_code="LLM_TOKEN_LIMIT",
            details=details
        )


# ==================== 文档解析相关异常 ====================

class ParserError(EconPaperError):
    """文档解析错误基类"""
    pass


class UnsupportedFileTypeError(ParserError):
    """不支持的文件类型"""
    
    def __init__(
        self,
        file_type: str,
        supported_types: Optional[list] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        supported = supported_types or ["pdf", "docx", "txt"]
        
        details = details or {}
        details["file_type"] = file_type
        details["supported_types"] = supported
        
        super().__init__(
            message=f"不支持的文件类型: {file_type}。支持的类型: {', '.join(supported)}",
            error_code="UNSUPPORTED_FILE_TYPE",
            details=details
        )


class EmptyContentError(ParserError):
    """内容为空错误"""
    
    def __init__(
        self,
        source: str = "文件",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"{source}内容为空，请检查输入",
            error_code="EMPTY_CONTENT",
            details=details
        )


class ContentTooShortError(ParserError):
    """内容过短错误"""
    
    def __init__(
        self,
        actual_length: int,
        min_length: int = 100,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["actual_length"] = actual_length
        details["min_length"] = min_length
        
        super().__init__(
            message=f"内容过短（{actual_length}字），至少需要{min_length}字",
            error_code="CONTENT_TOO_SHORT",
            details=details
        )


class PDFParseError(ParserError):
    """PDF 解析错误"""
    
    def __init__(
        self,
        message: str = "PDF 文件解析失败",
        file_path: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if file_path:
            details["file_path"] = file_path
        
        super().__init__(
            message=message,
            error_code="PDF_PARSE_ERROR",
            details=details
        )


class DocxParseError(ParserError):
    """Word 文档解析错误"""
    
    def __init__(
        self,
        message: str = "Word 文档解析失败",
        file_path: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if file_path:
            details["file_path"] = file_path
        
        super().__init__(
            message=message,
            error_code="DOCX_PARSE_ERROR",
            details=details
        )


# ==================== 处理流程相关异常 ====================

class ProcessingError(EconPaperError):
    """处理流程错误基类"""
    pass


class DiagnosisError(ProcessingError):
    """诊断处理错误"""
    
    def __init__(
        self,
        message: str = "论文诊断过程中发生错误",
        dimension: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if dimension:
            details["dimension"] = dimension
        
        super().__init__(
            message=message,
            error_code="DIAGNOSIS_ERROR",
            details=details
        )


class OptimizationError(ProcessingError):
    """优化处理错误"""
    
    def __init__(
        self,
        message: str = "论文优化过程中发生错误",
        section: Optional[str] = None,
        stage: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if section:
            details["section"] = section
        if stage:
            details["stage"] = stage
        
        super().__init__(
            message=message,
            error_code="OPTIMIZATION_ERROR",
            details=details
        )


class DedupError(ProcessingError):
    """降重处理错误"""
    
    def __init__(
        self,
        message: str = "降重处理过程中发生错误",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="DEDUP_ERROR",
            details=details
        )


class DeAIError(ProcessingError):
    """降AI处理错误"""
    
    def __init__(
        self,
        message: str = "降AI处理过程中发生错误",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="DEAI_ERROR",
            details=details
        )


# ==================== 知识库相关异常 ====================

class KnowledgeBaseError(EconPaperError):
    """知识库错误基类"""
    pass


class VectorStoreError(KnowledgeBaseError):
    """向量存储错误"""
    
    def __init__(
        self,
        message: str = "向量数据库操作失败",
        collection: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if collection:
            details["collection"] = collection
        if operation:
            details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="VECTOR_STORE_ERROR",
            details=details
        )


class EmbeddingError(KnowledgeBaseError):
    """嵌入生成错误"""
    
    def __init__(
        self,
        message: str = "文本嵌入生成失败",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="EMBEDDING_ERROR",
            details=details
        )


class SearchError(KnowledgeBaseError):
    """搜索错误"""
    
    def __init__(
        self,
        message: str = "学术搜索失败",
        source: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if source:
            details["source"] = source
        
        super().__init__(
            message=message,
            error_code="SEARCH_ERROR",
            details=details
        )


# ==================== 验证相关异常 ====================

class ValidationError(EconPaperError):
    """验证错误基类"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if field:
            details["field"] = field
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )


class InvalidInputError(ValidationError):
    """无效输入错误"""
    
    def __init__(
        self,
        message: str = "输入参数无效",
        field: Optional[str] = None,
        expected: Optional[str] = None,
        actual: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if expected:
            details["expected"] = expected
        if actual:
            details["actual"] = actual
        
        super().__init__(
            message=message,
            field=field,
            details=details
        )
        self.error_code = "INVALID_INPUT"


# ==================== 异常处理辅助函数 ====================

def format_error_message(error: Exception) -> str:
    """
    格式化错误消息，用于用户显示
    
    Args:
        error: 异常对象
        
    Returns:
        str: 格式化的错误消息
    """
    if isinstance(error, EconPaperError):
        return error.message
    return str(error)


def is_retriable_error(error: Exception) -> bool:
    """
    判断是否为可重试的错误
    
    Args:
        error: 异常对象
        
    Returns:
        bool: 是否可重试
    """
    retriable_types = (
        LLMConnectionError,
        LLMRateLimitError,
        SearchError,
        VectorStoreError,
    )
    return isinstance(error, retriable_types)


def get_user_friendly_message(error: Exception) -> str:
    """
    获取用户友好的错误消息
    
    Args:
        error: 异常对象
        
    Returns:
        str: 用户友好的错误消息
    """
    error_messages = {
        MissingAPIKeyError: "请先配置 API 密钥再使用此功能",
        LLMConnectionError: "网络连接失败，请检查网络后重试",
        LLMRateLimitError: "请求太频繁，请稍后再试",
        LLMAuthenticationError: "API 认证失败，请检查密钥配置",
        UnsupportedFileTypeError: "请上传 PDF 或 Word 格式的文档",
        EmptyContentError: "请上传文件或输入内容后再操作",
        ContentTooShortError: "内容太短，请提供更完整的论文内容",
    }
    
    for error_type, message in error_messages.items():
        if isinstance(error, error_type):
            return message
    
    if isinstance(error, EconPaperError):
        return error.message
    
    return "操作过程中发生错误，请稍后重试"
