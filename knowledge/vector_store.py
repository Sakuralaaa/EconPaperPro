# -*- coding: utf-8 -*-
"""
向量库管理模块
使用 ChromaDB 存储和检索向量数据
"""

from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from config.settings import settings
from core.embeddings import get_embedding_client


class VectorStore:
    """
    向量数据库管理类
    
    使用 ChromaDB 进行向量存储和相似度检索
    
    使用示例:
        store = VectorStore()
        store.add("exemplars", documents, metadatas, ids)
        results = store.search("如何写好引言", "exemplars", limit=5)
    """
    
    # 集合名称
    COLLECTIONS = {
        "exemplars": "顶刊论文范例",
        "methodology": "方法论知识",
        "history": "处理历史记录"
    }
    
    def __init__(self, persist_dir: Optional[str] = None):
        """
        初始化向量库
        
        Args:
            persist_dir: 持久化存储路径，默认从配置读取
        """
        self.persist_dir = persist_dir or settings.chroma_persist_dir
        
        # 初始化 ChromaDB 客户端
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # 初始化嵌入客户端
        self._embedding_client = None
        
        # 初始化集合
        self._collections = {}
        self._init_collections()
    
    @property
    def embedding_client(self):
        """延迟加载嵌入客户端"""
        if self._embedding_client is None:
            self._embedding_client = get_embedding_client()
        return self._embedding_client
    
    def _init_collections(self):
        """初始化所有集合"""
        for name in self.COLLECTIONS:
            self._collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"description": self.COLLECTIONS[name]}
            )
    
    def add(
        self,
        collection: str,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        添加文档到集合
        
        Args:
            collection: 集合名称
            documents: 文档列表
            metadatas: 元数据列表
            ids: 文档ID列表
        """
        if collection not in self._collections:
            raise ValueError(f"未知集合: {collection}")
        
        if not documents:
            return
        
        # 生成嵌入
        embeddings = self.embedding_client.embed_batch(documents)
        
        # 生成默认ID
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]
        
        # 生成默认元数据
        if metadatas is None:
            metadatas = [{}] * len(documents)
        
        # 添加到集合
        self._collections[collection].add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(
        self,
        query: str,
        collection: str,
        filter_dict: Optional[Dict] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        搜索相似文档
        
        Args:
            query: 查询文本
            collection: 集合名称
            filter_dict: 过滤条件
            limit: 返回数量
            
        Returns:
            List[Dict]: 搜索结果列表
        """
        if collection not in self._collections:
            raise ValueError(f"未知集合: {collection}")
        
        # 生成查询嵌入
        query_embedding = self.embedding_client.embed(query)
        
        # 执行查询
        results = self._collections[collection].query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=filter_dict
        )
        
        # 格式化结果
        formatted = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                item = {
                    "document": doc,
                    "id": results["ids"][0][i] if results["ids"] else None,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None
                }
                formatted.append(item)
        
        return formatted
    
    def delete(
        self,
        collection: str,
        ids: List[str]
    ) -> None:
        """
        删除文档
        
        Args:
            collection: 集合名称
            ids: 要删除的文档ID列表
        """
        if collection not in self._collections:
            raise ValueError(f"未知集合: {collection}")
        
        self._collections[collection].delete(ids=ids)
    
    def get_collection_stats(self, collection: str) -> Dict:
        """
        获取集合统计信息
        
        Args:
            collection: 集合名称
            
        Returns:
            Dict: 统计信息
        """
        if collection not in self._collections:
            raise ValueError(f"未知集合: {collection}")
        
        coll = self._collections[collection]
        
        return {
            "name": collection,
            "description": self.COLLECTIONS[collection],
            "count": coll.count()
        }
    
    def get_all_stats(self) -> List[Dict]:
        """
        获取所有集合的统计信息
        
        Returns:
            List[Dict]: 统计信息列表
        """
        return [self.get_collection_stats(name) for name in self.COLLECTIONS]
    
    def clear_collection(self, collection: str) -> None:
        """
        清空集合
        
        Args:
            collection: 集合名称
        """
        if collection not in self._collections:
            raise ValueError(f"未知集合: {collection}")
        
        # 删除并重新创建集合
        self.client.delete_collection(collection)
        self._collections[collection] = self.client.get_or_create_collection(
            name=collection,
            metadata={"description": self.COLLECTIONS[collection]}
        )
    
    def get(
        self,
        collection: str,
        ids: List[str]
    ) -> List[Dict]:
        """
        按ID获取文档
        
        Args:
            collection: 集合名称
            ids: 文档ID列表
            
        Returns:
            List[Dict]: 文档列表
        """
        if collection not in self._collections:
            raise ValueError(f"未知集合: {collection}")
        
        results = self._collections[collection].get(ids=ids)
        
        formatted = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                item = {
                    "document": doc,
                    "id": results["ids"][i] if results["ids"] else None,
                    "metadata": results["metadatas"][i] if results["metadatas"] else {}
                }
                formatted.append(item)
        
        return formatted


# 单例存储
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """
    获取向量库单例
    
    Returns:
        VectorStore: 向量库实例
    """
    global _vector_store
    
    if _vector_store is None:
        _vector_store = VectorStore()
    
    return _vector_store
