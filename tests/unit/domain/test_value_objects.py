from __future__ import annotations

import pytest

from interview_system.domain.value_objects import Answer, ConversationEntry, Question


def test_value_objects_are_immutable():
    q = Question(text="Q")
    a = Answer(text="A")

    with pytest.raises(Exception):
        q.text = "Q2"  # type: ignore[misc]

    with pytest.raises(Exception):
        a.text = "A2"  # type: ignore[misc]


def test_value_objects_equality_by_value():
    assert Question(text="Q") == Question(text="Q")
    assert Answer(text="A") == Answer(text="A")


def test_conversation_entry_immutable():
    from datetime import datetime, timezone

    e = ConversationEntry(
        timestamp=datetime.now(timezone.utc),
        topic="t",
        question_type="核心问题",
        question="Q",
        answer="A",
        depth_score=1,
        is_ai_generated=False,
    )
    with pytest.raises(Exception):
        e.answer = "B"  # type: ignore[misc]
