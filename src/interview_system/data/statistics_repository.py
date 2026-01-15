#!/usr/bin/env python3
# coding: utf-8
"""Statistics Repository - Handles statistical queries"""

from typing import List, Dict

import interview_system.common.logger as logger


class StatisticsRepository:
    """Repository for statistics operations"""

    def __init__(self, get_cursor_fn):
        """
        Args:
            get_cursor_fn: Function that returns cursor context manager
        """
        self.get_cursor = get_cursor_fn

    def get_by_date_range(self, start_date: str = None, end_date: str = None) -> Dict:
        """Get statistics by date range"""
        try:
            with self.get_cursor() as cursor:
                date_filter, params = self._build_date_filter(start_date, end_date)

                session_stats = self._get_session_stats(cursor, date_filter, params)
                scene_dist = self._get_scene_distribution(cursor, date_filter, params)
                edu_dist = self._get_edu_distribution(cursor, date_filter, params)
                followup_dist = self._get_followup_distribution(cursor, date_filter, params)
                avg_depth = self._get_avg_depth(cursor, date_filter, params)

                return {
                    'total_sessions': session_stats['total'],
                    'finished_sessions': session_stats['finished'],
                    'completion_rate': self._calc_completion_rate(session_stats),
                    'scene_distribution': scene_dist,
                    'edu_distribution': edu_dist,
                    'followup_distribution': followup_dist,
                    'avg_depth_score': avg_depth
                }
        except Exception as e:
            logger.error(f"获取统计数据失败: {e}")
            return {}

    def get_daily_stats(self, days: int = 7) -> List[Dict]:
        """Get daily statistics for last N days"""
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

    def _build_date_filter(self, start_date: str, end_date: str) -> tuple:
        """Build date filter SQL and params"""
        date_filter = ""
        params = []

        if start_date:
            date_filter += " AND s.start_time >= ?"
            params.append(start_date)
        if end_date:
            date_filter += " AND s.start_time <= ?"
            params.append(end_date)

        return date_filter, params

    def _get_session_stats(self, cursor, date_filter: str, params: list) -> Dict:
        """Get session statistics"""
        cursor.execute(f"""
            SELECT
                COUNT(*) as total_sessions,
                SUM(CASE WHEN is_finished = 1 THEN 1 ELSE 0 END) as finished_sessions
            FROM sessions s
            WHERE 1=1 {date_filter}
        """, params)
        row = cursor.fetchone()
        return {'total': row['total_sessions'], 'finished': row['finished_sessions']}

    def _get_scene_distribution(self, cursor, date_filter: str, params: list) -> Dict:
        """Get scene distribution"""
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
        return {row['scene']: row['count'] for row in cursor.fetchall()}

    def _get_edu_distribution(self, cursor, date_filter: str, params: list) -> Dict:
        """Get education type distribution"""
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
        return {row['edu_type']: row['count'] for row in cursor.fetchall()}

    def _get_followup_distribution(self, cursor, date_filter: str, params: list) -> Dict:
        """Get followup distribution"""
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
        return {row['followup_type']: row['count'] for row in cursor.fetchall()}

    def _get_avg_depth(self, cursor, date_filter: str, params: list) -> float:
        """Get average depth score"""
        cursor.execute(f"""
            SELECT AVG(depth_score) as avg_depth
            FROM conversation_logs cl
            JOIN sessions s ON cl.session_id = s.session_id
            WHERE 1=1 {date_filter}
        """, params)
        row = cursor.fetchone()
        return round(row['avg_depth'], 2) if row['avg_depth'] else 0

    def _calc_completion_rate(self, session_stats: Dict) -> float:
        """Calculate completion rate"""
        total = session_stats['total']
        finished = session_stats['finished']
        return round(finished / total * 100, 1) if total > 0 else 0
