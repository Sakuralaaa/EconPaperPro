# -*- coding: utf-8 -*-
"""
LLM 客户端模块测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os

# 禁用日志自动初始化
os.environ["ECONPAPER_INIT_LOGGER"] = "0"


class TestLLMClientInit:
    """测试 LLM 客户端初始化"""
    
    def test_missing_api_key_raises_error(self, monkeypatch):
        """测试缺少 API 密钥时抛出异常"""
        # 清除所有 API 密钥相关环境变量
        monkeypatch.delenv("LLM_API_KEY", raising=False)
        monkeypatch.setenv("LLM_API_BASE", "https://api.test.com/v1")
        
        from core.exceptions import MissingAPIKeyError
        
        # 需要重新加载模块以应用新的环境变量
        with pytest.raises(MissingAPIKeyError):
            # 直接创建一个新客户端，明确不提供 api_key
            from core.llm import LLMClient
            LLMClient(api_key="")
    
    def test_client_creation_with_valid_config(self, mock_env_settings):
        """测试有效配置时的客户端创建"""
        from core.llm import LLMClient
        
        client = LLMClient(
            api_base="https://api.test.com/v1",
            api_key="test-key",
            model="test-model"
        )
        
        assert client.api_base == "https://api.test.com/v1"
        assert client.api_key == "test-key"
        assert client.model == "test-model"
    
    def test_default_temperature_and_tokens(self, mock_env_settings):
        """测试默认温度和 token 设置"""
        from core.llm import LLMClient
        
        client = LLMClient(
            api_base="https://api.test.com/v1",
            api_key="test-key",
            model="test-model"
        )
        
        assert client.temperature == 0.7
        assert client.max_tokens == 4096
    
    def test_custom_temperature_and_tokens(self, mock_env_settings):
        """测试自定义温度和 token 设置"""
        from core.llm import LLMClient
        
        client = LLMClient(
            api_base="https://api.test.com/v1",
            api_key="test-key",
            model="test-model",
            temperature=0.5,
            max_tokens=2048
        )
        
        assert client.temperature == 0.5
        assert client.max_tokens == 2048


class TestLLMClientChat:
    """测试 LLM 客户端聊天功能"""
    
    @pytest.fixture
    def llm_client(self, mock_env_settings):
        """创建测试用 LLM 客户端"""
        from core.llm import LLMClient
        return LLMClient(
            api_base="https://api.test.com/v1",
            api_key="test-key",
            model="test-model"
        )
    
    def test_chat_returns_string(self, llm_client, mock_openai_client):
        """测试聊天返回字符串"""
        llm_client.client = mock_openai_client
        
        messages = [{"role": "user", "content": "你好"}]
        result = llm_client.chat(messages, stream=False)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_chat_with_stream_returns_generator(self, llm_client, mock_openai_client):
        """测试流式聊天返回生成器"""
        llm_client.client = mock_openai_client
        
        messages = [{"role": "user", "content": "你好"}]
        result = llm_client.chat(messages, stream=True)
        
        # 生成器应该是可迭代的
        assert hasattr(result, '__iter__')


class TestLLMClientInvoke:
    """测试 LLM 客户端简化调用接口"""
    
    @pytest.fixture
    def llm_client(self, mock_env_settings):
        """创建测试用 LLM 客户端"""
        from core.llm import LLMClient
        client = LLMClient(
            api_base="https://api.test.com/v1",
            api_key="test-key",
            model="test-model"
        )
        return client
    
    def test_invoke_builds_correct_messages(self, llm_client):
        """测试 invoke 构建正确的消息列表"""
        with patch.object(llm_client, 'chat', return_value="响应") as mock_chat:
            llm_client.invoke("用户输入", system_prompt="系统提示")
            
            # 验证调用参数
            call_args = mock_chat.call_args
            messages = call_args[0][0]
            
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[0]["content"] == "系统提示"
            assert messages[1]["role"] == "user"
            assert messages[1]["content"] == "用户输入"
    
    def test_invoke_without_system_prompt(self, llm_client):
        """测试不带系统提示的 invoke"""
        with patch.object(llm_client, 'chat', return_value="响应") as mock_chat:
            llm_client.invoke("用户输入")
            
            call_args = mock_chat.call_args
            messages = call_args[0][0]
            
            assert len(messages) == 1
            assert messages[0]["role"] == "user"
    
    def test_invoke_with_context(self, llm_client):
        """测试带上下文的 invoke"""
        with patch.object(llm_client, 'invoke', return_value="响应") as mock_invoke:
            llm_client.invoke_with_context(
                prompt="分析这段内容",
                context="这是上下文信息",
                system_prompt="你是助手"
            )
            
            # 验证调用
            mock_invoke.assert_called_once()


class TestLLMClientErrorHandling:
    """测试 LLM 客户端错误处理"""
    
    @pytest.fixture
    def llm_client(self, mock_env_settings):
        """创建测试用 LLM 客户端"""
        from core.llm import LLMClient
        return LLMClient(
            api_base="https://api.test.com/v1",
            api_key="test-key",
            model="test-model"
        )
    
    def test_auth_error_handling(self, llm_client):
        """测试认证错误处理"""
        import openai
        from core.exceptions import LLMAuthenticationError
        
        # 模拟认证错误
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = openai.AuthenticationError(
            message="Invalid API key",
            response=MagicMock(status_code=401),
            body={}
        )
        llm_client.client = mock_client
        
        with pytest.raises(LLMAuthenticationError):
            llm_client.chat([{"role": "user", "content": "test"}])
    
    def test_rate_limit_error_handling(self, llm_client):
        """测试限流错误处理"""
        import openai
        from core.exceptions import LLMRateLimitError
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = openai.RateLimitError(
            message="Rate limit exceeded",
            response=MagicMock(status_code=429),
            body={}
        )
        llm_client.client = mock_client
        
        with pytest.raises(LLMRateLimitError):
            llm_client.chat([{"role": "user", "content": "test"}])
    
    def test_connection_error_handling(self, llm_client):
        """测试连接错误处理"""
        import openai
        from core.exceptions import LLMConnectionError
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = openai.APIConnectionError(
            request=MagicMock()
        )
        llm_client.client = mock_client
        
        with pytest.raises(LLMConnectionError):
            llm_client.chat([{"role": "user", "content": "test"}])


class TestGetLLMClient:
    """测试获取 LLM 客户端单例"""
    
    def test_get_llm_client_returns_same_instance(self, mock_env_settings):
        """测试获取相同实例"""
        from core import llm
        
        # 重置单例
        llm._llm_client = None
        
        client1 = llm.get_llm_client()
        client2 = llm.get_llm_client()
        
        assert client1 is client2
    
    def test_get_backup_client_raises_without_config(self, mock_env_settings, monkeypatch):
        """测试无备用配置时抛出异常"""
        from core import llm
        
        # 清除备用配置
        monkeypatch.delenv("LLM_BACKUP_API_BASE", raising=False)
        monkeypatch.delenv("LLM_BACKUP_API_KEY", raising=False)
        
        llm._backup_llm_client = None
        
        with pytest.raises(ValueError, match="备用.*配置不完整"):
            llm.get_llm_client(use_backup=True)
