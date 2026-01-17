from __future__ import annotations

import pytest

from interview_system.application.services.session_service import SessionService
from interview_system.domain.entities import Session


class FakeRepo:
    def __init__(self):
        self.sessions: dict[str, Session] = {}

    async def get(self, session_id):  # type: ignore[override]
        return self.sessions.get(str(session_id))

    async def save(self, session: Session) -> None:  # type: ignore[override]
        self.sessions[str(session.id)] = session

    async def delete(self, session_id):  # type: ignore[override]
        return self.sessions.pop(str(session_id), None) is not None

    async def list_conversation_entries(self, session_id):  # type: ignore[override]
        return []

    async def append_conversation_entry(self, session_id, entry):  # type: ignore[override]
        raise NotImplementedError

    async def delete_last_conversation_entry(self, session_id):  # type: ignore[override]
        return None


@pytest.mark.asyncio
async def test_session_service_create_get_delete():
    repo = FakeRepo()
    service = SessionService(repo)  # type: ignore[arg-type]

    created = await service.create("tester")
    assert created.user_name == "tester"

    loaded = await service.get(created.id)
    assert loaded is not None
    assert loaded.id == created.id

    ok = await service.delete(created.id)
    assert ok is True
    assert await service.get(created.id) is None
