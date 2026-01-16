"""异步数据库连接封装（SQLAlchemy async）。"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from interview_system.infrastructure.database.migrations import run_migrations


class AsyncDatabase:
    """异步数据库。"""

    def __init__(
        self,
        database_url: str,
        *,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        self._database_url = self._normalize_url(database_url)
        self.engine = self._create_engine(
            self._database_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self._sessionmaker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
        )

    @staticmethod
    def _normalize_url(url: str) -> str:
        if url.startswith("sqlite://"):
            return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return url

    @staticmethod
    def _create_engine(
        url: str,
        *,
        echo: bool,
        pool_size: int,
        max_overflow: int,
    ) -> AsyncEngine:
        if url.startswith("sqlite+aiosqlite://") and (
            ":memory:" in url or url.endswith("/:memory:")
        ):
            return create_async_engine(
                url,
                echo=echo,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
            )

        return create_async_engine(
            url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
            connect_args={"check_same_thread": False}
            if url.startswith("sqlite+aiosqlite://")
            else {},
        )

    async def init(self) -> None:
        """初始化数据库（建表/迁移）。"""
        await run_migrations(engine=self.engine)

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """获取 AsyncSession（不自动开启事务）。"""
        async with self._sessionmaker() as session:
            yield session

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        """获取带事务的 AsyncSession（自动 commit/rollback）。"""
        async with self._sessionmaker() as session:
            async with session.begin():
                yield session

    async def execute(self, sql: str, params: dict[str, Any] | None = None):
        """执行原生 SQL。"""
        async with self.engine.begin() as conn:
            return await conn.execute(text(sql), params or {})

    async def health_check(self) -> bool:
        """健康检查。"""
        await self.execute("SELECT 1")
        return True

    async def dispose(self) -> None:
        """释放连接池。"""
        await self.engine.dispose()
