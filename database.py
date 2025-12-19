#!/usr/bin/env python3
# coding: utf-8
"""
数据库模块 - 大学生五育并举访谈智能体
提供SQLite数据库支持，实现会话和访谈记录的持久化存储
"""

import sqlite3
import json
import os
import threading
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager

import logger
from config import BASE_DIR


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

        # 初始化数据库
        self._init_database()
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

    # ========== 会话相关操作 ==========

    def create_session(self, session_id: str, user_name: str,
                      selected_topics: List[Dict]) -> bool:
        """创建新会话"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO sessions
                    (session_id, user_name, start_time, selected_topics)
                    VALUES (?, ?, ?, ?)
                """, (
                    session_id,
                    user_name,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    json.dumps(selected_topics, ensure_ascii=False)
                ))
            logger.info(f"创建会话成功: {session_id}")
            return True
        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            return False

    def get_session(self, session_id: str) -> Optional[Dict]:
        """获取会话信息"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM sessions WHERE session_id = ?
                """, (session_id,))
                row = cursor.fetchone()

                if row:
                    return {
                        'session_id': row['session_id'],
                        'user_name': row['user_name'],
                        'start_time': row['start_time'],
                        'end_time': row['end_time'],
                        'is_finished': bool(row['is_finished']),
                        'current_question_idx': row['current_question_idx'],
                        'selected_topics': json.loads(row['selected_topics']) if row['selected_topics'] else []
                    }
        except Exception as e:
            logger.error(f"获取会话失败: {e}")
        return None

    def update_session(self, session_id: str, **kwargs) -> bool:
        """更新会话信息"""
        try:
            # 构建更新语句
            update_fields = []
            values = []

            for key, value in kwargs.items():
                if key == 'selected_topics':
                    update_fields.append(f"{key} = ?")
                    values.append(json.dumps(value, ensure_ascii=False))
                elif key == 'is_finished':
                    update_fields.append(f"{key} = ?")
                    values.append(1 if value else 0)
                else:
                    update_fields.append(f"{key} = ?")
                    values.append(value)

            if not update_fields:
                return False

            # 添加更新时间
            update_fields.append("updated_at = ?")
            values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            values.append(session_id)

            with self.get_cursor() as cursor:
                cursor.execute(f"""
                    UPDATE sessions
                    SET {', '.join(update_fields)}
                    WHERE session_id = ?
                """, values)

            return True
        except Exception as e:
            logger.error(f"更新会话失败: {e}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """删除会话及其所有日志"""
        try:
            with self.get_cursor() as cursor:
                # 先删除对话日志
                cursor.execute("""
                    DELETE FROM conversation_logs WHERE session_id = ?
                """, (session_id,))

                # 再删除会话
                cursor.execute("""
                    DELETE FROM sessions WHERE session_id = ?
                """, (session_id,))

            logger.info(f"删除会话成功: {session_id}")
            return True
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False

    def get_all_sessions(self, limit: int = None, offset: int = 0) -> List[Dict]:
        """获取所有会话列表"""
        try:
            with self.get_cursor() as cursor:
                sql = """
                    SELECT s.*,
                           COUNT(cl.id) as log_count
                    FROM sessions s
                    LEFT JOIN conversation_logs cl ON s.session_id = cl.session_id
                    GROUP BY s.session_id
                    ORDER BY s.start_time DESC
                """

                if limit:
                    sql += f" LIMIT {limit} OFFSET {offset}"

                cursor.execute(sql)
                rows = cursor.fetchall()

                sessions = []
                for row in rows:
                    sessions.append({
                        'session_id': row['session_id'],
                        'user_name': row['user_name'],
                        'start_time': row['start_time'],
                        'end_time': row['end_time'],
                        'is_finished': bool(row['is_finished']),
                        'log_count': row['log_count']
                    })

                return sessions
        except Exception as e:
            logger.error(f"获取会话列表失败: {e}")
            return []

    def get_session_count(self) -> int:
        """获取会话总数"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM sessions")
                row = cursor.fetchone()
                return row['count'] if row else 0
        except Exception as e:
            logger.error(f"获取会话总数失败: {e}")
            return 0

    # ========== 对话日志相关操作 ==========

    def add_conversation_log(self, session_id: str, log_entry: Dict) -> bool:
        """添加对话日志"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO conversation_logs
                    (session_id, timestamp, topic, question_type, question,
                     answer, depth_score, is_ai_generated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    log_entry.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    log_entry.get('topic', ''),
                    log_entry.get('question_type', ''),
                    log_entry.get('question', ''),
                    log_entry.get('answer', ''),
                    log_entry.get('depth_score', 0),
                    1 if log_entry.get('is_ai_generated', False) else 0
                ))
            return True
        except Exception as e:
            logger.error(f"添加对话日志失败: {e}")
            return False

    def get_conversation_logs(self, session_id: str) -> List[Dict]:
        """获取会话的所有对话日志"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM conversation_logs
                    WHERE session_id = ?
                    ORDER BY id ASC
                """, (session_id,))
                rows = cursor.fetchall()

                logs = []
                for row in rows:
                    logs.append({
                        'timestamp': row['timestamp'],
                        'topic': row['topic'],
                        'question_type': row['question_type'],
                        'question': row['question'],
                        'answer': row['answer'],
                        'depth_score': row['depth_score'],
                        'is_ai_generated': bool(row['is_ai_generated'])
                    })

                return logs
        except Exception as e:
            logger.error(f"获取对话日志失败: {e}")
            return []

    # ========== 统计分析相关操作 ==========

    def get_statistics_by_date_range(self, start_date: str = None,
                                     end_date: str = None) -> Dict:
        """获取日期范围内的统计数据"""
        try:
            with self.get_cursor() as cursor:
                # 构建日期过滤条件
                date_filter = ""
                params = []

                if start_date:
                    date_filter += " AND s.start_time >= ?"
                    params.append(start_date)
                if end_date:
                    date_filter += " AND s.start_time <= ?"
                    params.append(end_date)

                # 总会话数和完成率
                cursor.execute(f"""
                    SELECT
                        COUNT(*) as total_sessions,
                        SUM(CASE WHEN is_finished = 1 THEN 1 ELSE 0 END) as finished_sessions
                    FROM sessions s
                    WHERE 1=1 {date_filter}
                """, params)
                row = cursor.fetchone()
                total_sessions = row['total_sessions']
                finished_sessions = row['finished_sessions']

                # 场景分布
                cursor.execute(f"""
                    SELECT
                        CASE
                            WHEN topic LIKE '学校-%' THEN '学校'
                            WHEN topic LIKE '家庭-%' THEN '家庭'
                            WHEN topic LIKE '社区-%' THEN '社区'
                            ELSE '其他'
                        END as scene,
                        COUNT(*) as count
                    FROM conversation_logs cl
                    JOIN sessions s ON cl.session_id = s.session_id
                    WHERE 1=1 {date_filter}
                    GROUP BY scene
                """, params)
                scene_distribution = {row['scene']: row['count'] for row in cursor.fetchall()}

                # 五育分布
                cursor.execute(f"""
                    SELECT
                        CASE
                            WHEN topic LIKE '%-德育' THEN '德育'
                            WHEN topic LIKE '%-智育' THEN '智育'
                            WHEN topic LIKE '%-体育' THEN '体育'
                            WHEN topic LIKE '%-美育' THEN '美育'
                            WHEN topic LIKE '%-劳育' THEN '劳育'
                            ELSE '其他'
                        END as edu_type,
                        COUNT(*) as count
                    FROM conversation_logs cl
                    JOIN sessions s ON cl.session_id = s.session_id
                    WHERE 1=1 {date_filter}
                    GROUP BY edu_type
                """, params)
                edu_distribution = {row['edu_type']: row['count'] for row in cursor.fetchall()}

                # 追问统计
                cursor.execute(f"""
                    SELECT
                        CASE
                            WHEN is_ai_generated = 1 THEN 'AI智能追问'
                            ELSE '预设追问'
                        END as followup_type,
                        COUNT(*) as count
                    FROM conversation_logs cl
                    JOIN sessions s ON cl.session_id = s.session_id
                    WHERE question_type LIKE '%追问%' {date_filter}
                    GROUP BY followup_type
                """, params)
                followup_distribution = {row['followup_type']: row['count'] for row in cursor.fetchall()}

                # 平均深度分数
                cursor.execute(f"""
                    SELECT AVG(depth_score) as avg_depth
                    FROM conversation_logs cl
                    JOIN sessions s ON cl.session_id = s.session_id
                    WHERE 1=1 {date_filter}
                """, params)
                row = cursor.fetchone()
                avg_depth = round(row['avg_depth'], 2) if row['avg_depth'] else 0

                return {
                    'total_sessions': total_sessions,
                    'finished_sessions': finished_sessions,
                    'completion_rate': round(finished_sessions / total_sessions * 100, 1) if total_sessions > 0 else 0,
                    'scene_distribution': scene_distribution,
                    'edu_distribution': edu_distribution,
                    'followup_distribution': followup_distribution,
                    'avg_depth_score': avg_depth
                }
        except Exception as e:
            logger.error(f"获取统计数据失败: {e}")
            return {}

    def get_daily_statistics(self, days: int = 7) -> List[Dict]:
        """获取最近N天的每日统计"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT
                        DATE(start_time) as date,
                        COUNT(*) as session_count,
                        SUM(CASE WHEN is_finished = 1 THEN 1 ELSE 0 END) as finished_count
                    FROM sessions
                    WHERE start_time >= datetime('now', ?)
                    GROUP BY DATE(start_time)
                    ORDER BY date DESC
                """, (f'-{days} days',))

                rows = cursor.fetchall()
                return [
                    {
                        'date': row['date'],
                        'session_count': row['session_count'],
                        'finished_count': row['finished_count']
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"获取每日统计失败: {e}")
            return []

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
