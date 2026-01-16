"""应用层异常（供 API 映射为统一错误响应）。"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SessionNotFoundError(Exception):
    session_id: UUID


@dataclass(frozen=True, slots=True)
class SessionAlreadyCompletedError(Exception):
    session_id: UUID


@dataclass(frozen=True, slots=True)
class NothingToUndoError(Exception):
    session_id: UUID
