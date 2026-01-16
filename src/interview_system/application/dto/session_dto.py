"""Session DTO。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SessionDTO:
    id: str
    status: str
    current_question: int
    total_questions: int
    created_at: int
    user_name: str
