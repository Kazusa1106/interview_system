#!/usr/bin/env python3
# coding: utf-8
"""Log Repository - Handles conversation log operations"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

import interview_system.common.logger as logger


class LogRepository:
    """Repository for conversation log operations"""

    def __init__(self, get_cursor_fn):
        """
        Args:
            get_cursor_fn: Function that returns cursor context manager
        """
        self.get_cursor = get_cursor_fn

    def add(self, session_id: str, log_entry: Dict) -> bool:
        """Add conversation log"""
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

    def get_by_session(self, session_id: str) -> List[Dict]:
        """Get all logs for a session"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM conversation_logs
                    WHERE session_id = ?
                    ORDER BY id ASC
                """, (session_id,))
                rows = cursor.fetchall()

                return [
                    {
                        'timestamp': row['timestamp'],
                        'topic': row['topic'],
                        'question_type': row['question_type'],
                        'question': row['question'],
                        'answer': row['answer'],
                        'depth_score': row['depth_score'],
                        'is_ai_generated': bool(row['is_ai_generated'])
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"获取对话日志失败: {e}")
            return []

    def delete_last_n(
        self,
        session_id: str,
        count: int,
        cursor: Optional[sqlite3.Cursor] = None
    ) -> bool:
        """Delete last N logs for a session"""
        if count <= 0:
            return True

        sql = """
            DELETE FROM conversation_logs
            WHERE id IN (
                SELECT id FROM conversation_logs
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
            )
        """

        try:
            if cursor is not None:
                cursor.execute(sql, (session_id, count))
                return True

            with self.get_cursor() as inner_cursor:
                inner_cursor.execute(sql, (session_id, count))
            return True
        except Exception as e:
            logger.error(f"删除对话日志失败: {e}")
            return False

    def delete_by_session(self, session_id: str, cursor: Optional[sqlite3.Cursor] = None) -> bool:
        """Delete all logs for a session"""
        sql = "DELETE FROM conversation_logs WHERE session_id = ?"

        try:
            if cursor is not None:
                cursor.execute(sql, (session_id,))
                return True

            with self.get_cursor() as inner_cursor:
                inner_cursor.execute(sql, (session_id,))
            return True
        except Exception as e:
            logger.error(f"删除会话日志失败: {e}")
            return False
