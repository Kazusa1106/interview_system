"""SQLAlchemy 模型定义。

约束：
- 优先兼容既有 SQLite 表结构（如存在）
- 兼容异步 SQLAlchemy 2.0
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative Base。"""


class SessionModel(Base):
    """会话表。"""

    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_name: Mapped[str] = mapped_column(String, nullable=False)

    start_time: Mapped[str] = mapped_column(String, nullable=False)
    end_time: Mapped[str | None] = mapped_column(String, nullable=True)

    is_finished: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_question_idx: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    selected_topics: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[str | None] = mapped_column(String, nullable=True)

    is_followup: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_followup_is_ai: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    current_followup_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    current_followup_question: Mapped[str] = mapped_column(
        String, nullable=False, default=""
    )

    conversation_logs: Mapped[list["ConversationLogModel"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class ConversationLogModel(Base):
    """对话日志表（按 Q/A 结构记录）。"""

    __tablename__ = "conversation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.session_id"), index=True
    )

    timestamp: Mapped[str] = mapped_column(String, nullable=False)
    topic: Mapped[str] = mapped_column(String, nullable=False, default="")
    question_type: Mapped[str] = mapped_column(String, nullable=False, default="")
    question: Mapped[str] = mapped_column(Text, nullable=False, default="")
    answer: Mapped[str] = mapped_column(Text, nullable=False, default="")
    depth_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_ai_generated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[str | None] = mapped_column(String, nullable=True)

    session: Mapped[SessionModel] = relationship(back_populates="conversation_logs")


Index("idx_session_time", SessionModel.start_time)
Index("idx_topic", ConversationLogModel.topic)
