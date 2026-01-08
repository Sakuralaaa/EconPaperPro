# -*- coding: utf-8 -*-
"""
EconPaper Pro - 历史记录管理
支持将 AI 生成结果持久化存储到本地 SQLite 数据库
"""

import sqlite3
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# 创建模块级 logger
logger = logging.getLogger(__name__)

class HistoryManager:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # 默认存储在用户数据目录下
            from config.settings import settings
            db_dir = Path(settings.data_dir) / "history"
            db_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = db_dir / "history.db"
        else:
            self.db_path = Path(db_path)
            
        self._init_db()

    def _init_db(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action_type TEXT NOT NULL,
                input_content TEXT,
                output_content TEXT,
                report TEXT,
                metadata TEXT
            )
        ''')
        
        # 新增：用户偏好设置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # 新增：API 用量统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                model TEXT,
                action_type TEXT,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                cost REAL
            )
        ''')

        # 新增：预设模板表 (P3)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                is_system INTEGER DEFAULT 0
            )
        ''')
        
        # 插入一些默认系统模板
        cursor.execute('SELECT COUNT(*) FROM templates WHERE is_system = 1')
        if cursor.fetchone()[0] == 0:
            system_templates = [
                ("学术润色", "请作为一名资深的经管类学术期刊编辑，对以下文本进行润色。要求：1. 语言专业严谨；2. 逻辑连贯；3. 消除口语化表达；4. 增强学术说服力。", "optimize"),
                ("逻辑检查", "请分析以下段落的论证逻辑，指出是否存在逻辑跳跃、循环论证或证据不足的问题，并给出修改建议。", "diagnose"),
                ("摘要重构", "请根据论文正文内容，重新撰写摘要。要求包含：研究背景、研究问题、研究方法、主要发现和政策启示。字数控制在300字以内。", "optimize"),
                ("审稿回应(委婉)", "请将以下对审稿意见的回应修改得更加委婉和专业。要求：1. 感谢审稿人的建议；2. 明确说明修改之处；3. 对无法修改的部分给出合理的学术解释。", "revision")
            ]
            cursor.executemany('INSERT INTO templates (name, content, category, is_system) VALUES (?, ?, ?, 1)', system_templates)
        
        # 创建索引加速查询
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_action_type ON records(action_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON records(timestamp)')
        
        conn.commit()
        conn.close()

    def save_record(self, action_type: str, input_content: str, output_content: str, report: str = "", metadata: Optional[Dict] = None):
        """保存一条历史记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            meta_json = json.dumps(metadata) if metadata else "{}"
            
            cursor.execute('''
                INSERT INTO records (action_type, input_content, output_content, report, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (action_type, input_content, output_content, report, meta_json))
            
            conn.commit()
            record_id = cursor.lastrowid
            conn.close()
            return record_id
        except Exception as e:
            logger.warning(f"Failed to save history: {e}")
            return None

    def get_recent_records(self, action_type: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """获取最近的历史记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if action_type:
                cursor.execute('''
                    SELECT * FROM records 
                    WHERE action_type = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (action_type, limit))
            else:
                cursor.execute('''
                    SELECT * FROM records 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            logger.warning(f"Failed to fetch history: {e}")
            return []

    def get_record_by_id(self, record_id: int) -> Optional[Dict]:
        """根据 ID 获取完整历史记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM records WHERE id = ?', (record_id,))
            row = cursor.fetchone()
            conn.close()
            
            return dict(row) if row else None
        except Exception as e:
            logger.warning(f"Failed to fetch record {record_id}: {e}")
            return None

    def delete_record(self, record_id: int):
        """删除特定记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM records WHERE id = ?', (record_id,))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def set_preference(self, key: str, value: Any):
        """设置偏好"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            val_str = json.dumps(value)
            cursor.execute('INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)', (key, val_str))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def get_preference(self, key: str, default: Any = None) -> Any:
        """获取偏好"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM preferences WHERE key = ?', (key,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return json.loads(row[0])
            return default
        except Exception:
            return default

    def log_usage(self, model: str, action_type: str, prompt_tokens: int, completion_tokens: int, cost: float = 0.0):
        """记录 API 用量"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            total = prompt_tokens + completion_tokens
            cursor.execute('''
                INSERT INTO usage_stats (model, action_type, prompt_tokens, completion_tokens, total_tokens, cost)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (model, action_type, prompt_tokens, completion_tokens, total, cost))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def get_usage_summary(self) -> Dict:
        """获取用量概览"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT SUM(total_tokens), SUM(cost), COUNT(*) FROM usage_stats')
            row = cursor.fetchone()
            conn.close()
            return {
                'total_tokens': row[0] or 0,
                'total_cost': row[1] or 0.0,
                'total_requests': row[2] or 0
            }
        except Exception:
            return {'total_tokens': 0, 'total_cost': 0.0, 'total_requests': 0}

    def clear_history(self, action_type: Optional[str] = None):
        """清空历史记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            if action_type:
                cursor.execute('DELETE FROM records WHERE action_type = ?', (action_type,))
            else:
                cursor.execute('DELETE FROM records')
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def get_templates(self, category: Optional[str] = None) -> List[Dict]:
        """获取预设模板 (P3)"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if category:
                cursor.execute('SELECT * FROM templates WHERE category = ? OR is_system = 1 ORDER BY is_system DESC, id ASC', (category,))
            else:
                cursor.execute('SELECT * FROM templates ORDER BY is_system DESC, id ASC')
            
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception:
            return []

    def save_template(self, name: str, content: str, category: str = "general"):
        """保存自定义模板 (P3)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO templates (name, content, category, is_system)
                VALUES (?, ?, ?, 0)
            ''', (name, content, category))
            conn.commit()
            template_id = cursor.lastrowid
            conn.close()
            return template_id
        except Exception:
            return None

    def delete_template(self, template_id: int):
        """删除自定义模板 (P3)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # 不允许删除系统模板
            cursor.execute('DELETE FROM templates WHERE id = ? AND is_system = 0', (template_id,))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False