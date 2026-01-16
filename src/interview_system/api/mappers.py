"""API 层对象转换。"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, cast
from uuid import uuid4

from interview_system.api.schemas.message import MessageResponse
from interview_system.api.schemas.session import SessionResponse
from interview_system.domain.entities.session import Session


Role = Literal["user", "assistant", "system"]


def to_session_response(session: Session) -> SessionResponse:
    return SessionResponse(
        id=str(session.id),
        status="completed" if session.is_finished() else "active",
        current_question=int(session.current_question_idx),
        total_questions=len(session.selected_topics) if session.selected_topics else 0,
        created_at=int(session.created_at.timestamp() * 1000),
        user_name=session.user_name,
    )


def to_message_response(
    role: Role,
    content: str,
    *,
    msg_id: str | None = None,
    timestamp_ms: int | None = None,
) -> MessageResponse:
    ts = (
        timestamp_ms
        if timestamp_ms is not None
        else int(datetime.now(timezone.utc).timestamp() * 1000)
    )
    return MessageResponse(
        id=msg_id or f"msg_{uuid4().hex[:8]}",
        role=role,
        content=content,
        timestamp=ts,
    )


def to_message_responses(messages: list[dict]) -> list[MessageResponse]:
    result: list[MessageResponse] = []
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    for i, msg in enumerate(messages):
        raw_role = str(msg.get("role", "assistant"))
        normalized_role: Role = "assistant"
        if raw_role in {"user", "assistant", "system"}:
            normalized_role = cast(Role, raw_role)
        result.append(
            to_message_response(
                role=normalized_role,
                content=str(msg.get("content", "")),
                msg_id=f"msg_{i}",
                timestamp_ms=int(msg.get("timestamp") or now_ms),
            )
        )
    return result
