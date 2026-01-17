"""Interview 处理结果 DTO。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InterviewResultDTO:
    assistant_message: str
    is_finished: bool = False
