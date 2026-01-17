"""Session 领域实体。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"


@dataclass
class Session:
    """访谈会话（领域实体）。"""

    id: UUID = field(default_factory=uuid4)
    user_name: str = "访谈者"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: SessionStatus = SessionStatus.ACTIVE

    current_question_idx: int = 0
    selected_topics: list[dict[str, Any]] = field(default_factory=list)
    is_followup: bool = False
    current_followup_is_ai: bool = False
    current_followup_count: int = 0
    current_followup_question: str = ""

    def is_finished(self) -> bool:
        return self.status == SessionStatus.COMPLETED

    def finish(self) -> None:
        self.status = SessionStatus.COMPLETED

    def can_undo(self) -> bool:
        return self.current_question_idx > 0 or self.current_followup_count > 0
