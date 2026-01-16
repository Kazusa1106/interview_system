from __future__ import annotations

from datetime import datetime, timezone

import pytest

from interview_system.domain.entities import Session
from interview_system.domain.value_objects.conversation_entry import ConversationEntry
from interview_system.infrastructure.cache import SessionCache
from interview_system.infrastructure.database import AsyncDatabase
from interview_system.infrastructure.database.repositories import SessionRepositoryImpl


@pytest.mark.asyncio
async def test_session_repository_save_get_delete_and_logs():
    db = AsyncDatabase("sqlite+aiosqlite:///:memory:")
    await db.init()

    repo = SessionRepositoryImpl(db, cache=SessionCache())

    session = Session(user_name="tester")
    session.selected_topics = [
        {"name": "学校-德育", "scene": "学校", "edu_type": "德育", "questions": ["Q1"]}
    ]
    await repo.save(session)

    loaded = await repo.get(session.id)
    assert loaded is not None
    assert loaded.user_name == "tester"
    assert loaded.selected_topics

    entry = ConversationEntry(
        timestamp=datetime.now(timezone.utc),
        topic="学校-德育",
        question_type="核心问题",
        question="Q1",
        answer="A1",
        depth_score=1,
        is_ai_generated=False,
    )
    await repo.append_conversation_entry(session.id, entry)

    entries = await repo.list_conversation_entries(session.id)
    assert len(entries) == 1
    assert entries[0].answer == "A1"

    deleted = await repo.delete_last_conversation_entry(session.id)
    assert deleted is not None
    assert deleted.answer == "A1"
    assert await repo.list_conversation_entries(session.id) == []

    ok = await repo.delete(session.id)
    assert ok is True
    assert await repo.get(session.id) is None

    await db.dispose()
