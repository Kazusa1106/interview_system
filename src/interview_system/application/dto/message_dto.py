"""Message DTO（用于 API 展示）。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MessageDTO:
    id: str
    role: str
    content: str
    timestamp: int
