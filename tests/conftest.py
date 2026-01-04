# -*- coding: utf-8 -*-
"""
测试配置文件
使用 pytest 作为测试框架
"""

import os
import sys
from pathlib import Path

import pytest

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置测试环境变量，避免自动初始化日志
os.environ["ECONPAPER_INIT_LOGGER"] = "0"


@pytest.fixture(scope="session")
def project_root_path():
    """返回项目根目录路径"""
    return project_root


@pytest.fixture
def sample_paper_content():
    """返回示例论文内容"""
    return """
    摘要：本文研究了数字经济对中国区域经济发展的影响机制。通过构建面板数据模型，
    分析了2010-2020年间31个省份的经济数据。研究发现，数字经济发展水平与区域经济
    增长存在显著正相关关系，且这一效应在东部地区更为明显。本研究为理解数字经济
    赋能区域发展提供了实证依据。
    
    关键词：数字经济；区域发展；面板数据；经济增长
    
    一、引言
    随着信息技术的快速发展，数字经济已成为推动经济增长的重要引擎。近年来，
    中国政府高度重视数字经济发展，出台了一系列支持政策。然而，数字经济对
    不同区域的影响是否存在差异，其作用机制如何，仍有待深入研究。
    
    二、文献综述
    已有研究主要从以下几个方面展开：首先，关于数字经济的内涵界定。学者们
    普遍认为，数字经济是以数据为关键生产要素，以数字技术为核心驱动力的
    新经济形态（张三，2020）。其次，关于数字经济与经济增长的关系。多数
    研究表明二者存在正向关联（李四等，2021）。
    
    三、研究方法
    本文采用双向固定效应模型，控制了时间和个体效应。被解释变量为人均GDP
    增长率，核心解释变量为数字经济发展指数。控制变量包括人力资本、固定
    资产投资、对外开放度等。
    
    四、实证结果
    回归结果显示，数字经济发展指数的系数为0.15，在1%水平上显著，表明
    数字经济发展对区域经济增长具有积极影响。分区域来看，东部地区系数
    为0.22，中部地区为0.12，西部地区为0.08。
    
    五、结论与建议
    本文研究表明，数字经济发展能够有效促进区域经济增长。基于此，建议：
    第一，加大数字基础设施投资；第二，培育数字经济人才；第三，促进
    区域间数字经济协调发展。
    """


@pytest.fixture
def sample_short_content():
    """返回过短的内容用于测试"""
    return "这是一段很短的测试内容。"


@pytest.fixture
def mock_llm_response():
    """返回模拟的 LLM 响应"""
    return {
        "diagnosis": {
            "overall_score": 75,
            "dimensions": {
                "学术规范性": {"score": 80, "comment": "格式较规范"},
                "逻辑结构": {"score": 70, "comment": "结构基本清晰"},
                "文献综述": {"score": 65, "comment": "文献引用偏少"},
                "研究方法": {"score": 85, "comment": "方法较科学"},
                "创新性": {"score": 75, "comment": "有一定创新"}
            }
        }
    }


@pytest.fixture
def mock_env_settings(monkeypatch):
    """设置测试用环境变量"""
    monkeypatch.setenv("LLM_API_KEY", "test-api-key-12345")
    monkeypatch.setenv("LLM_API_BASE", "https://api.test.com/v1")
    monkeypatch.setenv("LLM_MODEL", "test-model")


class MockOpenAIClient:
    """模拟 OpenAI 客户端"""
    
    class ChatCompletions:
        @staticmethod
        def create(**kwargs):
            class Choice:
                class Message:
                    content = "这是一个模拟的 LLM 响应内容。"
                message = Message()
                
                class Delta:
                    content = "流式响应片段"
                delta = Delta()
            
            class Usage:
                total_tokens = 100
                prompt_tokens = 50
                completion_tokens = 50
            
            class Response:
                choices = [Choice()]
                usage = Usage()
                
                def __iter__(self):
                    yield self
            
            return Response()
    
    class Chat:
        completions = ChatCompletions()
    
    chat = Chat()


@pytest.fixture
def mock_openai_client():
    """返回模拟的 OpenAI 客户端"""
    return MockOpenAIClient()
