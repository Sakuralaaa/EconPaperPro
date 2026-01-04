# -*- coding: utf-8 -*-
"""
范例管理模块
管理顶刊论文范例，支持分类、搜索和RAG检索
"""

from typing import List, Dict, Optional
import json
import os
from knowledge.vector_store import get_vector_store


class ExemplarManager:
    """
    范例管理器
    
    管理顶刊论文范例库，支持分类浏览、关键词搜索和语义检索
    
    使用示例:
        manager = ExemplarManager()
        manager.load_from_json("data/exemplars/sample.json")
        results = manager.search("引言写作", category="introduction")
    """
    
    # 范例分类
    CATEGORIES = {
        "introduction": "引言范例",
        "literature": "文献综述范例",
        "hypothesis": "研究假设范例",
        "methodology": "研究方法范例",
        "empirical": "实证分析范例",
        "conclusion": "结论范例",
        "abstract": "摘要范例",
        "title": "标题范例"
    }
    
    def __init__(self):
        """初始化范例管理器"""
        self.vector_store = get_vector_store()
    
    def load_from_json(self, file_path: str) -> int:
        """
        从 JSON 文件加载范例
        
        Args:
            file_path: JSON 文件路径
            
        Returns:
            int: 加载的范例数量
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if isinstance(data, list):
            exemplars = data
        elif isinstance(data, dict) and "exemplars" in data:
            exemplars = data["exemplars"]
        else:
            raise ValueError("无效的 JSON 格式")
        
        return self._add_exemplars(exemplars)
    
    def _add_exemplars(self, exemplars: List[Dict]) -> int:
        """
        添加范例到向量库
        
        Args:
            exemplars: 范例列表
            
        Returns:
            int: 添加的数量
        """
        documents = []
        metadatas = []
        ids = []
        
        for i, ex in enumerate(exemplars):
            # 文档内容
            content = ex.get("content", "")
            if not content:
                continue
            
            documents.append(content)
            
            # 元数据
            metadata = {
                "category": ex.get("category", "other"),
                "journal": ex.get("journal", ""),
                "year": ex.get("year", ""),
                "title": ex.get("title", ""),
                "keywords": ",".join(ex.get("keywords", []))
            }
            metadatas.append(metadata)
            
            # ID
            ex_id = ex.get("id", f"exemplar_{i}")
            ids.append(ex_id)
        
        if documents:
            self.vector_store.add(
                collection="exemplars",
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        
        return len(documents)
    
    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        搜索范例
        
        Args:
            query: 搜索查询
            category: 分类筛选
            limit: 返回数量
            
        Returns:
            List[Dict]: 搜索结果
        """
        filter_dict = None
        if category and category in self.CATEGORIES:
            filter_dict = {"category": category}
        
        results = self.vector_store.search(
            query=query,
            collection="exemplars",
            filter_dict=filter_dict,
            limit=limit
        )
        
        # 格式化结果
        formatted = []
        for item in results:
            formatted.append({
                "content": item["document"],
                "category": item["metadata"].get("category", ""),
                "journal": item["metadata"].get("journal", ""),
                "year": item["metadata"].get("year", ""),
                "title": item["metadata"].get("title", ""),
                "relevance": 1 - item["distance"] if item["distance"] else 0
            })
        
        return formatted
    
    def get_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """
        按分类获取范例
        
        Args:
            category: 分类名称
            limit: 返回数量
            
        Returns:
            List[Dict]: 范例列表
        """
        if category not in self.CATEGORIES:
            return []
        
        # 使用通用查询词搜索该分类
        return self.search(
            query=self.CATEGORIES[category],
            category=category,
            limit=limit
        )
    
    def add_exemplar(
        self,
        content: str,
        category: str,
        journal: str = "",
        year: str = "",
        title: str = "",
        keywords: Optional[List[str]] = None
    ) -> str:
        """
        添加单个范例
        
        Args:
            content: 范例内容
            category: 分类
            journal: 期刊名称
            year: 年份
            title: 标题
            keywords: 关键词
            
        Returns:
            str: 范例ID
        """
        import uuid
        
        ex_id = str(uuid.uuid4())
        
        self.vector_store.add(
            collection="exemplars",
            documents=[content],
            metadatas=[{
                "category": category,
                "journal": journal,
                "year": year,
                "title": title,
                "keywords": ",".join(keywords) if keywords else ""
            }],
            ids=[ex_id]
        )
        
        return ex_id
    
    def delete_exemplar(self, exemplar_id: str) -> None:
        """
        删除范例
        
        Args:
            exemplar_id: 范例ID
        """
        self.vector_store.delete(
            collection="exemplars",
            ids=[exemplar_id]
        )
    
    def get_stats(self) -> Dict:
        """
        获取范例库统计
        
        Returns:
            Dict: 统计信息
        """
        stats = self.vector_store.get_collection_stats("exemplars")
        return {
            "total_count": stats["count"],
            "categories": list(self.CATEGORIES.keys())
        }
    
    def export_to_json(self, file_path: str) -> int:
        """
        导出范例到 JSON 文件
        
        Args:
            file_path: 输出文件路径
            
        Returns:
            int: 导出的数量
        """
        # 获取所有范例
        all_exemplars = []
        
        for category in self.CATEGORIES:
            results = self.get_by_category(category, limit=100)
            all_exemplars.extend(results)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"exemplars": all_exemplars}, f, ensure_ascii=False, indent=2)
        
        return len(all_exemplars)
    
    def format_for_display(self, exemplars: List[Dict]) -> str:
        """
        格式化范例用于显示
        
        Args:
            exemplars: 范例列表
            
        Returns:
            str: Markdown 格式的显示文本
        """
        lines = []
        
        for i, ex in enumerate(exemplars, 1):
            lines.append(f"### 范例 {i}")
            
            if ex.get("title"):
                lines.append(f"**标题**: {ex['title']}")
            if ex.get("journal"):
                lines.append(f"**来源**: {ex['journal']} ({ex.get('year', '')})")
            if ex.get("category"):
                category_name = self.CATEGORIES.get(ex["category"], ex["category"])
                lines.append(f"**分类**: {category_name}")
            
            lines.append("")
            lines.append(ex.get("content", "")[:500] + "...")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
