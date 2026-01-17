"""轻量迁移脚本（SQLite）。

说明：
- 该项目当前未引入 Alembic；这里提供最小可用的迁移/建表能力
- 对于已存在的表，仅补齐缺失字段与索引（幂等）
"""

from __future__ import annotations

from sqlalchemy import text

from interview_system.infrastructure.database.models import Base


async def run_migrations(*, engine) -> None:
    """执行迁移（幂等）。"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # sessions 表补齐追问相关字段（幂等）
        result = await conn.execute(text("PRAGMA table_info(sessions)"))
        existing = {row[1] for row in result.fetchall()}  # row[1] = name

        required = {
            "is_followup": "INTEGER DEFAULT 0",
            "current_followup_is_ai": "INTEGER DEFAULT 0",
            "current_followup_count": "INTEGER DEFAULT 0",
            "current_followup_question": "TEXT DEFAULT ''",
        }
        for column_name, column_def in required.items():
            if column_name not in existing:
                await conn.execute(
                    text(f"ALTER TABLE sessions ADD COLUMN {column_name} {column_def}")
                )

        await conn.execute(
            text("CREATE INDEX IF NOT EXISTS idx_session_time ON sessions(start_time)")
        )
        await conn.execute(
            text("CREATE INDEX IF NOT EXISTS idx_topic ON conversation_logs(topic)")
        )
