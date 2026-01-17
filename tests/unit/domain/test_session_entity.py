from __future__ import annotations

from interview_system.domain.entities import Session, SessionStatus


def test_session_defaults():
    session = Session(user_name="测试")
    assert session.status == SessionStatus.ACTIVE
    assert session.is_finished() is False


def test_session_finish():
    session = Session(user_name="测试")
    session.finish()
    assert session.is_finished() is True


def test_session_can_undo():
    session = Session(user_name="测试")
    assert session.can_undo() is False

    session.current_question_idx = 1
    assert session.can_undo() is True
