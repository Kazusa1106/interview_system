#!/usr/bin/env python3
# coding: utf-8
"""
数据库模块 - 大学生五育并举访谈智能体
提供SQLite数据库支持，实现会话和访谈记录的持久化存储
"""

import sqlite3
import os
import threading
from contextlib import contextmanager
from typing import List, Dict, Optional

import interview_system.common.logger as logger
from interview_system.common.config import BASE_DIR
from interview_system.data.session_repository import SessionRepository
from interview_system.data.log_repository import LogRepository
from interview_system.data.statistics_repository import StatisticsRepository


# 数据库文件路径
DB_PATH = os.path.join(BASE_DIR, "interview_data.db")


class Database:
    """数据库管理器 - 使用SQLite存储访谈数据"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.db_path = DB_PATH
        self._local = threading.local()
        self._initialized = True

        self._init_database()

        # Initialize repositories
        self.sessions = SessionRepository(self.get_cursor)
        self.logs = LogRepository(self.get_cursor)
        self.statistics = StatisticsRepository(self.get_cursor)

        logger.info(f"数据库初始化完成: {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """获取线程本地的数据库连接"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection

    @contextmanager
    def get_cursor(self):
        """获取游标的上下文管理器"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            cursor.close()

    def _init_database(self):
        """初始化数据库表结构"""
        with self.get_cursor() as cursor:
            # 创建会话表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    is_finished INTEGER DEFAULT 0,
                    current_question_idx INTEGER DEFAULT 0,
                    selected_topics TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 轻量迁移：为 sessions 表补齐追问状态字段（幂等）
            cursor.execute("PRAGMA table_info(sessions)")
            existing_columns = {row["name"] for row in cursor.fetchall()}

            required_columns = {
                "is_followup": "INTEGER DEFAULT 0",
                "current_followup_is_ai": "INTEGER DEFAULT 0",
                "current_followup_count": "INTEGER DEFAULT 0",
                "current_followup_question": "TEXT DEFAULT ''",
            }
            for col_name, col_def in required_columns.items():
                if col_name not in existing_columns:
                    cursor.execute(f"ALTER TABLE sessions ADD COLUMN {col_name} {col_def}")

            # 创建对话日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    question_type TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    depth_score INTEGER DEFAULT 0,
                    is_ai_generated INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_id
                ON conversation_logs(session_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_time
                ON sessions(start_time)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_topic
                ON conversation_logs(topic)
            """)

            logger.info("数据库表结构初始化完成")

    # ========== 会话相关操作 (Delegate to SessionRepository) ==========

    def create_session(self, session_id: str, user_name: str, selected_topics: List[Dict]) -> bool:
        """创建新会话"""
        return self.sessions.create(session_id, user_name, selected_topics)

    def get_session(self, session_id: str) -> Optional[Dict]:
        """获取会话信息"""
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, **kwargs) -> bool:
        """更新会话信息"""
        return self.sessions.update(session_id, **kwargs)

    def delete_session(self, session_id: str) -> bool:
        """删除会话及其所有日志"""
        try:
            with self.get_cursor() as cursor:
                self.logs.delete_by_session(session_id, cursor)
                return self.sessions.delete(session_id)
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False

    def get_all_sessions(self, limit: int = None, offset: int = 0) -> List[Dict]:
        """获取所有会话列表"""
        return self.sessions.get_all(limit, offset)

    def get_session_count(self) -> int:
        """获取会话总数"""
        return self.sessions.count()

    # ========== 对话日志相关操作 (Delegate to LogRepository) ==========

    def add_conversation_log(self, session_id: str, log_entry: Dict) -> bool:
        """添加对话日志"""
        return self.logs.add(session_id, log_entry)

    def get_conversation_logs(self, session_id: str) -> List[Dict]:
        """获取会话的所有对话日志"""
        return self.logs.get_by_session(session_id)

    def delete_last_conversation_logs(
        self,
        session_id: str,
        count: int,
        cursor: Optional[sqlite3.Cursor] = None
    ) -> bool:
        """删除某会话最近 N 条对话日志"""
        return self.logs.delete_last_n(session_id, count, cursor)

    def rollback_session_state(
        self,
        session_id: str,
        *,
        delete_log_count: int,
        session_update: Dict
    ) -> bool:
        """原子回滚会话状态（删尾日志 + 更新 sessions）"""
        if delete_log_count < 0:
            return False

        try:
            with self.get_cursor() as cursor:
                if delete_log_count > 0:
                    ok = self.logs.delete_last_n(session_id, delete_log_count, cursor)
                    if not ok:
                        return False

                if session_update:
                    ok = self.sessions._update_with_cursor(cursor, session_id, **session_update)
                    if not ok:
                        return False

            return True
        except Exception as e:
            logger.error(f"回滚会话状态失败: {e}")
            return False

    # ========== 统计分析相关操作 (Delegate to StatisticsRepository) ==========

    def get_statistics_by_date_range(self, start_date: str = None, end_date: str = None) -> Dict:
        """获取日期范围内的统计数据"""
        return self.statistics.get_by_date_range(start_date, end_date)

    def get_daily_statistics(self, days: int = 7) -> List[Dict]:
        """获取最近N天的每日统计"""
        return self.statistics.get_daily_stats(days)

    def close(self):
        """关闭数据库连接"""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None


# ========== 便捷函数 ==========
_db_instance: Optional[Database] = None


def get_database() -> Database:
    """获取数据库实例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
