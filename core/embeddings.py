# -*- coding: utf-8 -*-
"""
嵌入模型客户端模块
支持所有 OpenAI 兼容的嵌入接口
"""

from typing import Optional, List
from openai import OpenAI
from config.settings import settings


class EmbeddingClient:
    """
    统一嵌入模型客户端
    
    使用示例:
        client = EmbeddingClient()
        vector = client.embed("这是一段文本")
        
        # 批量嵌入
        vectors = client.embed_batch(["文本1", "文本2"])
    """
    
    def __init__(
        self,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        初始化嵌入客户端
        
        Args:
            api_base: API 地址，默认从配置读取
            api_key: API 密钥，默认从配置读取
            model: 模型名称，默认从配置读取
        """
        self.api_base = api_base or settings.embedding_api_base
        self.api_key = api_key or settings.embedding_api_key
        self.model = model or settings.embedding_model
        
        # 验证 API 密钥
        if not self.api_key:
            raise ValueError("嵌入模型 API 密钥未配置。请在 .env 文件中设置 EMBEDDING_API_KEY。")
        
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            base_url=self.api_base,
            api_key=self.api_key
        )
    
    def embed(self, text: str) -> List[float]:
        """
        单文本嵌入
        
        Args:
            text: 要嵌入的文本
            
        Returns:
            List[float]: 嵌入向量
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"嵌入生成失败: {str(e)}")
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量文本嵌入
        
        Args:
            texts: 要嵌入的文本列表
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        if not texts:
            return []
            
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            # 按原顺序返回
            embeddings = [None] * len(texts)
            for item in response.data:
                embeddings[item.index] = item.embedding
            return embeddings
        except Exception as e:
            raise RuntimeError(f"批量嵌入生成失败: {str(e)}")
    
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        文档嵌入（LangChain 兼容接口）
        
        Args:
            documents: 文档列表
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        return self.embed_batch(documents)
    
    def embed_query(self, query: str) -> List[float]:
        """
        查询嵌入（LangChain 兼容接口）
        
        Args:
            query: 查询文本
            
        Returns:
            List[float]: 嵌入向量
        """
        return self.embed(query)


# 单例存储
_embedding_client: Optional[EmbeddingClient] = None


def get_embedding_client() -> EmbeddingClient:
    """
    获取嵌入客户端单例
    
    Returns:
        EmbeddingClient: 嵌入客户端实例
    """
    global _embedding_client
    
    if _embedding_client is None:
        _embedding_client = EmbeddingClient()
    
    return _embedding_client
