"""Session 应用服务（CRUD 用例）。"""

from __future__ import annotations

from uuid import UUID

from interview_system.domain.entities.session import Session
from interview_system.domain.repositories.session_repository import SessionRepository


class SessionService:
    def __init__(self, repository: SessionRepository) -> None:
        self._repository = repository

    async def create(self, user_name: str | None = None) -> Session:
        session = Session(user_name=user_name or "访谈者")
        await self._repository.save(session)
        return session

    async def get(self, session_id: UUID) -> Session | None:
        return await self._repository.get(session_id)

    async def delete(self, session_id: UUID) -> bool:
        return await self._repository.delete(session_id)
