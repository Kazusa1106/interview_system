"""Session 仓储接口。"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from interview_system.domain.entities.session import Session
from interview_system.domain.value_objects.conversation_entry import ConversationEntry


class SessionRepository(Protocol):
    async def get(self, session_id: UUID) -> Session | None: ...

    async def save(self, session: Session) -> None: ...

    async def delete(self, session_id: UUID) -> bool: ...

    async def list_conversation_entries(
        self, session_id: UUID
    ) -> list[ConversationEntry]: ...

    async def append_conversation_entry(
        self, session_id: UUID, entry: ConversationEntry
    ) -> None: ...

    async def delete_last_conversation_entry(
        self, session_id: UUID
    ) -> ConversationEntry | None: ...
