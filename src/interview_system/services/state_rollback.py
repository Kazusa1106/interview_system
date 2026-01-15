#!/usr/bin/env python3
# coding: utf-8
"""
StateRollbackManager - Handles session state rollback operations
Extracted from SessionManager to reduce complexity
"""

from typing import Optional
import interview_system.common.logger as logger


class StateRollbackManager:
    """Manages session state rollback operations"""

    def __init__(self, db: Optional[object] = None):
        """
        Initialize rollback manager

        Args:
            db: Database instance (optional)
        """
        self._db = db

    def rollback(
        self,
        session: 'InterviewSession',
        *,
        target_log_count: int,
        session_state: dict
    ) -> bool:
        """
        Rollback session to specified state

        Args:
            session: Session object to rollback
            target_log_count: Target conversation log count after rollback
            session_state: State snapshot to restore

        Returns:
            True if rollback succeeded, False otherwise
        """
        if not self._validate_log_count(session, target_log_count):
            return False

        current_log_count = len(session.conversation_log)

        if not self._rollback_database(
            session.session_id,
            target_log_count,
            session_state,
            current_log_count
        ):
            return False

        self._restore_memory_state(session, target_log_count, session_state)

        logger.log_session(
            session.session_id,
            "回滚会话",
            f"logs={current_log_count}->{target_log_count}"
        )

        return True

    def _validate_log_count(self, session: 'InterviewSession', target_log_count: int) -> bool:
        """Validate target log count is within valid range"""
        current_count = len(session.conversation_log)

        if target_log_count < 0 or target_log_count > current_count:
            logger.warning(
                f"回滚失败：target_log_count={target_log_count} 不合法（当前={current_count}）"
            )
            return False

        return True

    def _rollback_database(
        self,
        session_id: str,
        target_log_count: int,
        session_state: dict,
        current_log_count: int
    ) -> bool:
        """
        Rollback database state atomically

        Returns:
            True if succeeded or no database, False if database rollback failed
        """
        if not self._db:
            return True

        delete_count = current_log_count - target_log_count
        update_data = self._build_update_data(session_state)

        success = self._db.rollback_session_state(
            session_id,
            delete_log_count=delete_count,
            session_update=update_data
        )

        if not success:
            logger.error(f"回滚失败：数据库回滚未成功 (session_id={session_id})")
            return False

        return True

    def _build_update_data(self, session_state: dict) -> dict:
        """Build database update payload from session state"""
        is_finished = bool(session_state.get("is_finished", False))
        end_time = session_state.get("end_time") if is_finished else None

        return {
            "current_question_idx": session_state.get("current_question_idx", 0),
            "is_finished": is_finished,
            "end_time": end_time,
            "is_followup": bool(session_state.get("is_followup", False)),
            "current_followup_is_ai": bool(session_state.get("current_followup_is_ai", False)),
            "current_followup_count": int(session_state.get("current_followup_count", 0)),
            "current_followup_question": session_state.get("current_followup_question", "") or "",
        }

    def _restore_memory_state(
        self,
        session: 'InterviewSession',
        target_log_count: int,
        session_state: dict
    ) -> None:
        """Restore session memory state from snapshot"""
        session.conversation_log = session.conversation_log[:target_log_count]

        session.current_question_idx = int(
            session_state.get("current_question_idx", session.current_question_idx)
        )
        session.is_finished = bool(session_state.get("is_finished", session.is_finished))
        session.end_time = session_state.get("end_time", session.end_time) or ""

        if not session.is_finished:
            session.end_time = ""

        session.is_followup = bool(session_state.get("is_followup", session.is_followup))
        session.current_followup_is_ai = bool(
            session_state.get("current_followup_is_ai", session.current_followup_is_ai)
        )
        session.current_followup_count = int(
            session_state.get("current_followup_count", session.current_followup_count)
        )
        session.current_followup_question = (
            session_state.get("current_followup_question", session.current_followup_question) or ""
        )
