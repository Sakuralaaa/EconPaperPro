# -*- coding: utf-8 -*-
"""
异常模块测试
"""

import pytest
from core.exceptions import (
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
    format_error_message,
    is_retriable_error,
    get_user_friendly_message,
)


class TestBaseException:
    """测试基础异常类"""
    
    def test_basic_creation(self):
        """测试基本异常创建"""
        error = EconPaperError("测试错误消息")
        assert error.message == "测试错误消息"
        assert error.error_code == "UNKNOWN_ERROR"
        assert error.details == {}
    
    def test_with_error_code(self):
        """测试带错误码的异常"""
        error = EconPaperError(
            message="测试错误",
            error_code="TEST_ERROR"
        )
        assert error.error_code == "TEST_ERROR"
    
    def test_with_details(self):
        """测试带详情的异常"""
        details = {"key": "value", "count": 10}
        error = EconPaperError(
            message="测试错误",
            details=details
        )
        assert error.details == details
    
    def test_to_dict(self):
        """测试转换为字典"""
        error = EconPaperError(
            message="测试错误",
            error_code="TEST_ERROR",
            details={"info": "test"}
        )
        result = error.to_dict()
        
        assert result["error"] == "EconPaperError"
        assert result["code"] == "TEST_ERROR"
        assert result["message"] == "测试错误"
        assert result["details"] == {"info": "test"}
    
    def test_str_representation(self):
        """测试字符串表示"""
        error = EconPaperError(
            message="测试错误",
            error_code="TEST_ERROR"
        )
        assert str(error) == "[TEST_ERROR] 测试错误"


class TestConfigurationErrors:
    """测试配置相关异常"""
    
    def test_configuration_error(self):
        """测试配置错误"""
        error = ConfigurationError(
            message="配置项缺失",
            config_key="API_KEY"
        )
        assert error.config_key == "API_KEY"
        assert error.error_code == "CONFIG_ERROR"
    
    def test_missing_api_key_error(self):
        """测试 API 密钥缺失错误"""
        error = MissingAPIKeyError(service="OpenAI")
        
        assert "OpenAI" in error.message
        assert error.error_code == "MISSING_API_KEY"
        assert error.details["service"] == "OpenAI"


class TestLLMErrors:
    """测试 LLM 相关异常"""
    
    def test_llm_connection_error(self):
        """测试连接错误"""
        error = LLMConnectionError(
            message="连接超时",
            api_base="https://api.test.com"
        )
        assert error.error_code == "LLM_CONNECTION_ERROR"
        assert error.details["api_base"] == "https://api.test.com"
    
    def test_llm_rate_limit_error(self):
        """测试限流错误"""
        error = LLMRateLimitError(
            message="请求过于频繁",
            retry_after=60
        )
        assert error.retry_after == 60
        assert error.details["retry_after_seconds"] == 60
    
    def test_llm_auth_error(self):
        """测试认证错误"""
        error = LLMAuthenticationError()
        assert error.error_code == "LLM_AUTH_ERROR"
    
    def test_llm_response_error(self):
        """测试响应错误"""
        long_response = "x" * 1000
        error = LLMResponseError(
            message="响应解析失败",
            response=long_response
        )
        # 响应应该被截断
        assert len(error.details.get("response_preview", "")) <= 500
    
    def test_llm_token_limit_error(self):
        """测试 Token 限制错误"""
        error = LLMTokenLimitError(
            message="超出限制",
            token_count=5000,
            max_tokens=4096
        )
        assert error.details["token_count"] == 5000
        assert error.details["max_tokens"] == 4096


class TestParserErrors:
    """测试解析相关异常"""
    
    def test_unsupported_file_type(self):
        """测试不支持的文件类型"""
        error = UnsupportedFileTypeError(file_type="xlsx")
        
        assert "xlsx" in error.message
        assert "pdf" in error.message.lower() or "docx" in error.message.lower()
    
    def test_empty_content_error(self):
        """测试空内容错误"""
        error = EmptyContentError(source="上传文件")
        assert "上传文件" in error.message
    
    def test_content_too_short_error(self):
        """测试内容过短错误"""
        error = ContentTooShortError(
            actual_length=50,
            min_length=100
        )
        assert error.details["actual_length"] == 50
        assert error.details["min_length"] == 100


class TestProcessingErrors:
    """测试处理流程异常"""
    
    def test_diagnosis_error(self):
        """测试诊断错误"""
        error = DiagnosisError(
            message="诊断失败",
            dimension="学术规范性"
        )
        assert error.details["dimension"] == "学术规范性"
    
    def test_optimization_error(self):
        """测试优化错误"""
        error = OptimizationError(
            message="优化失败",
            section="摘要",
            stage="润色"
        )
        assert error.details["section"] == "摘要"
        assert error.details["stage"] == "润色"


class TestHelperFunctions:
    """测试辅助函数"""
    
    def test_format_error_message(self):
        """测试错误消息格式化"""
        # 自定义异常
        error = EconPaperError("自定义错误")
        assert format_error_message(error) == "自定义错误"
        
        # 普通异常
        error = ValueError("普通错误")
        assert format_error_message(error) == "普通错误"
    
    def test_is_retriable_error(self):
        """测试可重试错误判断"""
        # 可重试的错误
        assert is_retriable_error(LLMConnectionError()) is True
        assert is_retriable_error(LLMRateLimitError()) is True
        
        # 不可重试的错误
        assert is_retriable_error(LLMAuthenticationError()) is False
        assert is_retriable_error(ValueError("test")) is False
    
    def test_get_user_friendly_message(self):
        """测试用户友好消息"""
        # 已知错误类型
        error = MissingAPIKeyError()
        msg = get_user_friendly_message(error)
        assert "密钥" in msg or "API" in msg
        
        # 未知错误
        error = ValueError("unknown")
        msg = get_user_friendly_message(error)
        assert "稍后重试" in msg or "错误" in msg


class TestExceptionInheritance:
    """测试异常继承关系"""
    
    def test_llm_errors_inherit_from_base(self):
        """测试 LLM 错误继承关系"""
        error = LLMConnectionError()
        assert isinstance(error, LLMError)
        assert isinstance(error, EconPaperError)
        assert isinstance(error, Exception)
    
    def test_parser_errors_inherit_from_base(self):
        """测试解析错误继承关系"""
        error = UnsupportedFileTypeError(file_type="xlsx")
        assert isinstance(error, ParserError)
        assert isinstance(error, EconPaperError)
    
    def test_processing_errors_inherit_from_base(self):
        """测试处理错误继承关系"""
        error = DiagnosisError()
        assert isinstance(error, ProcessingError)
        assert isinstance(error, EconPaperError)
