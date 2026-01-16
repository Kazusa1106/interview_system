from __future__ import annotations

import pytest

from interview_system.infrastructure.database import AsyncDatabase


@pytest.mark.asyncio
async def test_migrations_create_tables_and_columns():
    db = AsyncDatabase("sqlite+aiosqlite:///:memory:")
    await db.init()

    result = await db.execute("PRAGMA table_info(sessions)")
    columns = {row[1] for row in result.fetchall()}  # row[1] = name

    assert "session_id" in columns
    assert "user_name" in columns
    assert "is_followup" in columns
    assert "current_followup_question" in columns

    result2 = await db.execute("PRAGMA table_info(conversation_logs)")
    columns2 = {row[1] for row in result2.fetchall()}
    assert "session_id" in columns2
    assert "question" in columns2
    assert "answer" in columns2

    await db.dispose()
