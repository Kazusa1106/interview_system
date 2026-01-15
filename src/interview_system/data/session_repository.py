#!/usr/bin/env python3
# coding: utf-8
"""Session Repository - Handles session CRUD operations"""

import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

import interview_system.common.logger as logger


class SessionRepository:
    """Repository for session operations"""

    def __init__(self, get_cursor_fn):
        """
        Args:
            get_cursor_fn: Function that returns cursor context manager
        """
        self.get_cursor = get_cursor_fn

    def create(self, session_id: str, user_name: str, selected_topics: List[Dict]) -> bool:
        """Create new session"""
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

    def get(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                return self._build_session_dict(row)
        except Exception as e:
            logger.error(f"获取会话失败: {e}")
            return None

    def update(self, session_id: str, **kwargs) -> bool:
        """Update session"""
        try:
            with self.get_cursor() as cursor:
                return self._update_with_cursor(cursor, session_id, **kwargs)
        except Exception as e:
            logger.error(f"更新会话失败: {e}")
            return False

    def delete(self, session_id: str) -> bool:
        """Delete session"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            logger.info(f"删除会话成功: {session_id}")
            return True
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False

    def get_all(self, limit: int = None, offset: int = 0) -> List[Dict]:
        """Get all sessions"""
        try:
            with self.get_cursor() as cursor:
                sql = """
                    SELECT s.*, COUNT(cl.id) as log_count
                    FROM sessions s
                    LEFT JOIN conversation_logs cl ON s.session_id = cl.session_id
                    GROUP BY s.session_id
                    ORDER BY s.start_time DESC
                """
                if limit:
                    sql += f" LIMIT {limit} OFFSET {offset}"

                cursor.execute(sql)
                rows = cursor.fetchall()

                return [
                    {
                        'session_id': row['session_id'],
                        'user_name': row['user_name'],
                        'start_time': row['start_time'],
                        'end_time': row['end_time'],
                        'is_finished': bool(row['is_finished']),
                        'log_count': row['log_count']
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"获取会话列表失败: {e}")
            return []

    def count(self) -> int:
        """Get total session count"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM sessions")
                row = cursor.fetchone()
                return row['count'] if row else 0
        except Exception as e:
            logger.error(f"获取会话总数失败: {e}")
            return 0

    def _build_session_dict(self, row: sqlite3.Row) -> Dict:
        """Build session dict from row"""
        def safe_get(key: str, default, cast=None):
            if key not in row.keys():
                return default
            val = row[key]
            return cast(val) if cast else val

        return {
            'session_id': row['session_id'],
            'user_name': row['user_name'],
            'start_time': row['start_time'],
            'end_time': row['end_time'],
            'is_finished': bool(row['is_finished']),
            'current_question_idx': row['current_question_idx'],
            'selected_topics': json.loads(row['selected_topics']) if row['selected_topics'] else [],
            'is_followup': safe_get('is_followup', False, bool),
            'current_followup_is_ai': safe_get('current_followup_is_ai', False, bool),
            'current_followup_count': safe_get('current_followup_count', 0),
            'current_followup_question': safe_get('current_followup_question', '')
        }

    def _update_with_cursor(self, cursor: sqlite3.Cursor, session_id: str, **kwargs) -> bool:
        """Update session using given cursor"""
        update_fields = []
        values = []

        for key, value in kwargs.items():
            if key == 'selected_topics':
                update_fields.append(f"{key} = ?")
                values.append(json.dumps(value, ensure_ascii=False))
            elif key in ('is_finished', 'is_followup', 'current_followup_is_ai'):
                update_fields.append(f"{key} = ?")
                values.append(1 if value else 0)
            else:
                update_fields.append(f"{key} = ?")
                values.append(value)

        if not update_fields:
            return False

        update_fields.append("updated_at = ?")
        values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        values.append(session_id)

        cursor.execute(f"""
            UPDATE sessions
            SET {', '.join(update_fields)}
            WHERE session_id = ?
        """, values)
        return True
