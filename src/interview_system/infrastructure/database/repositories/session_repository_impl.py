"""SessionRepository 的 SQLAlchemy async 实现。"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select

from interview_system.domain.entities.session import Session, SessionStatus
from interview_system.domain.repositories.session_repository import SessionRepository
from interview_system.domain.value_objects.conversation_entry import ConversationEntry
from interview_system.infrastructure.cache.memory_cache import SessionCache
from interview_system.infrastructure.database.connection import AsyncDatabase
from interview_system.infrastructure.database.models import (
    ConversationLogModel,
    SessionModel,
)

_TS_FORMAT = "%Y-%m-%d %H:%M:%S"


class SessionRepositoryImpl(SessionRepository):
    def __init__(self, db: AsyncDatabase, *, cache: SessionCache | None = None) -> None:
        self._db = db
        self._cache = cache

    async def get(self, session_id: UUID) -> Session | None:
        key = str(session_id)
        if self._cache is not None:
            cached = self._cache.get(key)
            if cached is not None:
                return cached

        async with self._db.session() as session:
            model = await session.get(SessionModel, key)
            if model is None:
                return None
            domain = _to_domain_session(model)
            if self._cache is not None:
                self._cache.set(domain)
            return domain

    async def save(self, session_obj: Session) -> None:
        now = datetime.now(timezone.utc)
        async with self._db.transaction() as session:
            key = str(session_obj.id)
            model = await session.get(SessionModel, key)
            if model is None:
                model = SessionModel(
                    session_id=key,
                    user_name=session_obj.user_name,
                    start_time=session_obj.created_at.astimezone(timezone.utc).strftime(
                        _TS_FORMAT
                    ),
                )
                session.add(model)

            model.user_name = session_obj.user_name
            model.is_finished = 1 if session_obj.is_finished() else 0
            model.current_question_idx = int(session_obj.current_question_idx)
            model.selected_topics = json.dumps(
                session_obj.selected_topics, ensure_ascii=False
            )

            model.is_followup = 1 if session_obj.is_followup else 0
            model.current_followup_is_ai = (
                1 if session_obj.current_followup_is_ai else 0
            )
            model.current_followup_count = int(session_obj.current_followup_count)
            model.current_followup_question = (
                session_obj.current_followup_question or ""
            )

            if model.created_at is None:
                model.created_at = now.strftime(_TS_FORMAT)
            model.updated_at = now.strftime(_TS_FORMAT)

        if self._cache is not None:
            self._cache.set(session_obj)

    async def delete(self, session_id: UUID) -> bool:
        key = str(session_id)
        async with self._db.transaction() as session:
            model = await session.get(SessionModel, key)
            if model is None:
                return False
            await session.delete(model)

        if self._cache is not None:
            self._cache.delete(key)
        return True

    async def list_conversation_entries(
        self, session_id: UUID
    ) -> list[ConversationEntry]:
        key = str(session_id)
        async with self._db.session() as session:
            result = await session.execute(
                select(ConversationLogModel)
                .where(ConversationLogModel.session_id == key)
                .order_by(ConversationLogModel.id.asc())
            )
            return [_to_domain_entry(m) for m in result.scalars().all()]

    async def append_conversation_entry(
        self, session_id: UUID, entry: ConversationEntry
    ) -> None:
        key = str(session_id)
        async with self._db.transaction() as session:
            model = ConversationLogModel(
                session_id=key,
                timestamp=entry.timestamp.astimezone(timezone.utc).strftime(_TS_FORMAT),
                topic=entry.topic,
                question_type=entry.question_type,
                question=entry.question,
                answer=entry.answer,
                depth_score=int(entry.depth_score),
                is_ai_generated=1 if entry.is_ai_generated else 0,
                created_at=datetime.now(timezone.utc).strftime(_TS_FORMAT),
            )
            session.add(model)

    async def delete_last_conversation_entry(
        self, session_id: UUID
    ) -> ConversationEntry | None:
        key = str(session_id)
        async with self._db.transaction() as session:
            result = await session.execute(
                select(ConversationLogModel)
                .where(ConversationLogModel.session_id == key)
                .order_by(ConversationLogModel.id.desc())
                .limit(1)
            )
            model = result.scalar_one_or_none()
            if model is None:
                return None
            entry = _to_domain_entry(model)
            await session.delete(model)
            return entry


def _to_domain_session(model: SessionModel) -> Session:
    try:
        created_at = datetime.strptime(model.start_time, _TS_FORMAT).replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        created_at = datetime.now(timezone.utc)

    status = (
        SessionStatus.COMPLETED if bool(model.is_finished) else SessionStatus.ACTIVE
    )
    selected: list[dict] = []
    if model.selected_topics:
        try:
            selected = json.loads(model.selected_topics)
        except json.JSONDecodeError:
            selected = []

    return Session(
        id=UUID(model.session_id),
        user_name=model.user_name,
        created_at=created_at,
        status=status,
        current_question_idx=int(model.current_question_idx or 0),
        selected_topics=selected,
        is_followup=bool(model.is_followup),
        current_followup_is_ai=bool(model.current_followup_is_ai),
        current_followup_count=int(model.current_followup_count or 0),
        current_followup_question=model.current_followup_question or "",
    )


def _to_domain_entry(model: ConversationLogModel) -> ConversationEntry:
    try:
        ts = datetime.strptime(model.timestamp, _TS_FORMAT).replace(tzinfo=timezone.utc)
    except ValueError:
        ts = datetime.now(timezone.utc)

    return ConversationEntry(
        timestamp=ts,
        topic=model.topic or "",
        question_type=model.question_type or "",
        question=model.question or "",
        answer=model.answer or "",
        depth_score=int(model.depth_score or 0),
        is_ai_generated=bool(model.is_ai_generated),
    )
