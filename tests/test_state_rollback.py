#!/usr/bin/env python3
# coding: utf-8
"""Tests for StateRollbackManager"""

import pytest
from unittest.mock import Mock, MagicMock
from interview_system.services.state_rollback import StateRollbackManager
from interview_system.services.session_manager import InterviewSession


@pytest.fixture
def mock_db():
    """Mock database"""
    db = Mock()
    db.rollback_session_state = Mock(return_value=True)
    return db


@pytest.fixture
def sample_session():
    """Sample session for testing"""
    session = InterviewSession(
        session_id="test123",
        user_name="测试用户",
        current_question_idx=5,
        is_finished=False,
        is_followup=True,
        current_followup_is_ai=True,
        current_followup_count=2,
        current_followup_question="追问内容"
    )
    session.conversation_log = [
        {"role": "user", "content": "Q1"},
        {"role": "assistant", "content": "A1"},
        {"role": "user", "content": "Q2"},
        {"role": "assistant", "content": "A2"},
        {"role": "user", "content": "Q3"},
    ]
    return session


@pytest.fixture
def rollback_manager(mock_db):
    """StateRollbackManager instance"""
    return StateRollbackManager(mock_db)


class TestStateRollbackManager:
    """Test StateRollbackManager"""

    def test_rollback_success_with_db(self, rollback_manager, sample_session, mock_db):
        """Test successful rollback with database"""
        target_state = {
            "current_question_idx": 3,
            "is_finished": False,
            "is_followup": False,
            "current_followup_is_ai": False,
            "current_followup_count": 0,
            "current_followup_question": ""
        }

        result = rollback_manager.rollback(
            sample_session,
            target_log_count=3,
            session_state=target_state
        )

        assert result is True
        assert len(sample_session.conversation_log) == 3
        assert sample_session.current_question_idx == 3
        assert sample_session.is_followup is False
        assert sample_session.current_followup_count == 0

        mock_db.rollback_session_state.assert_called_once()

    def test_rollback_success_without_db(self, sample_session):
        """Test successful rollback without database"""
        manager = StateRollbackManager(db=None)

        target_state = {
            "current_question_idx": 2,
            "is_finished": False,
        }

        result = manager.rollback(
            sample_session,
            target_log_count=2,
            session_state=target_state
        )

        assert result is True
        assert len(sample_session.conversation_log) == 2
        assert sample_session.current_question_idx == 2

    def test_rollback_invalid_log_count_negative(self, rollback_manager, sample_session):
        """Test rollback with negative log count"""
        result = rollback_manager.rollback(
            sample_session,
            target_log_count=-1,
            session_state={}
        )

        assert result is False
        assert len(sample_session.conversation_log) == 5

    def test_rollback_invalid_log_count_exceeds(self, rollback_manager, sample_session):
        """Test rollback with log count exceeding current"""
        result = rollback_manager.rollback(
            sample_session,
            target_log_count=10,
            session_state={}
        )

        assert result is False
        assert len(sample_session.conversation_log) == 5

    def test_rollback_db_failure(self, rollback_manager, sample_session, mock_db):
        """Test rollback when database operation fails"""
        mock_db.rollback_session_state.return_value = False

        original_log_count = len(sample_session.conversation_log)
        original_idx = sample_session.current_question_idx

        result = rollback_manager.rollback(
            sample_session,
            target_log_count=2,
            session_state={"current_question_idx": 1}
        )

        assert result is False
        assert len(sample_session.conversation_log) == original_log_count
        assert sample_session.current_question_idx == original_idx

    def test_rollback_clears_end_time_when_not_finished(self, rollback_manager, sample_session):
        """Test that end_time is cleared when is_finished=False"""
        sample_session.is_finished = True
        sample_session.end_time = "2026-01-15 10:00:00"

        target_state = {
            "is_finished": False,
            "end_time": "2026-01-15 10:00:00"
        }

        rollback_manager.rollback(
            sample_session,
            target_log_count=3,
            session_state=target_state
        )

        assert sample_session.is_finished is False
        assert sample_session.end_time == ""

    def test_rollback_preserves_end_time_when_finished(self, rollback_manager, sample_session):
        """Test that end_time is preserved when is_finished=True"""
        target_state = {
            "is_finished": True,
            "end_time": "2026-01-15 10:00:00"
        }

        rollback_manager.rollback(
            sample_session,
            target_log_count=3,
            session_state=target_state
        )

        assert sample_session.is_finished is True
        assert sample_session.end_time == "2026-01-15 10:00:00"

    def test_rollback_handles_empty_state_fields(self, rollback_manager, sample_session):
        """Test rollback with minimal state fields"""
        result = rollback_manager.rollback(
            sample_session,
            target_log_count=2,
            session_state={}
        )

        assert result is True
        assert len(sample_session.conversation_log) == 2
