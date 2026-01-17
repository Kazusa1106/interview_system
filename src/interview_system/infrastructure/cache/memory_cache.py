"""内存缓存（TTL）。"""

from __future__ import annotations

from cachetools import TTLCache

from interview_system.domain.entities.session import Session


class SessionCache:
    def __init__(self, *, maxsize: int = 256, ttl_seconds: int = 300) -> None:
        self._cache: TTLCache[str, Session] = TTLCache(maxsize=maxsize, ttl=ttl_seconds)

    def get(self, session_id: str) -> Session | None:
        return self._cache.get(session_id)

    def set(self, session: Session) -> None:
        self._cache[str(session.id)] = session

    def delete(self, session_id: str) -> None:
        self._cache.pop(session_id, None)
