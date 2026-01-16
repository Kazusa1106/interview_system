"""ConversationEntry 值对象。

用于记录一次“问题-回答”的结构化条目（可用于落库/统计/重放）。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ConversationEntry:
    timestamp: datetime
    topic: str
    question_type: str
    question: str
    answer: str
    depth_score: int = 0
    is_ai_generated: bool = False
