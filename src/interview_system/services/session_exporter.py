#!/usr/bin/env python3
# coding: utf-8
"""
Session Export - Pure function module
No dependencies on SessionManager
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

import interview_system.common.logger as logger
from interview_system.common.config import EXPORT_DIR


def export_session(
    session_id: str,
    user_name: str,
    start_time: str,
    end_time: str,
    conversation_log: List[Dict],
    file_path: str = None
) -> Optional[str]:
    """
    Export session to JSON file

    Returns:
        File path on success, None on failure
    """
    if not conversation_log:
        logger.warning(f"导出失败：会话 {session_id} 无对话记录")
        return None

    summary = _generate_summary(
        session_id,
        user_name,
        start_time,
        end_time,
        conversation_log
    )

    if not file_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(EXPORT_DIR, f"interview_{user_name}_{timestamp}.json")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        logger.log_session(session_id, "导出会话", f"文件: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"导出会话失败: {e}")
        return None


def _generate_summary(
    session_id: str,
    user_name: str,
    start_time: str,
    end_time: str,
    conversation_log: List[Dict]
) -> dict:
    """Generate session summary with statistics"""
    scene_stats = {}
    edu_stats = {}
    followup_stats = {"预设追问": 0, "AI智能追问": 0}

    for log in conversation_log:
        topic = log.get("topic", "")
        if "-" in topic:
            scene, edu = topic.split("-")
            scene_stats[scene] = scene_stats.get(scene, 0) + 1
            edu_stats[edu] = edu_stats.get(edu, 0) + 1

        q_type = log.get("question_type", "")
        if "追问" in q_type:
            if log.get("is_ai_generated"):
                followup_stats["AI智能追问"] += 1
            else:
                followup_stats["预设追问"] += 1

    return {
        "session_id": session_id,
        "user_name": user_name,
        "start_time": start_time,
        "end_time": end_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "statistics": {
            "total_logs": len(conversation_log),
            "scene_distribution": scene_stats,
            "edu_distribution": edu_stats,
            "followup_distribution": followup_stats
        },
        "conversation_log": conversation_log
    }
