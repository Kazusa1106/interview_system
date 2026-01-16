"""答案处理器（领域服务）。

职责：
- 对答案进行“深度评分”
- 生成结构化 AnswerResult（不修改输入）
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Sequence


@dataclass(frozen=True, slots=True)
class AnswerResult:
    timestamp: datetime
    topic: str
    question_type: str
    question: str
    answer: str
    depth_score: int
    is_ai_generated: bool = False


class AnswerProcessor:
    """纯计算型处理器。"""

    def __init__(
        self,
        *,
        depth_keywords: Sequence[str],
        common_keywords: Sequence[str],
        max_depth_score: int,
    ) -> None:
        self._depth_keywords = tuple(depth_keywords)
        self._common_keywords = tuple(common_keywords)
        self._max_depth_score = int(max_depth_score)

    def score_depth(self, answer: str) -> int:
        if not answer:
            return 0
        text = answer.lower()
        score = sum(1 for kw in self._depth_keywords if kw in text)
        return min(score, self._max_depth_score)

    def extract_keywords(self, answer: str) -> list[str]:
        if not answer:
            return []
        text = answer.lower()
        return [kw for kw in self._common_keywords if kw in text]

    def process_core_answer(
        self, *, answer: str, topic: dict[str, Any], question_text: str | None = None
    ) -> AnswerResult:
        question = question_text or str((topic.get("questions") or [""])[0])
        valid_answer = answer.strip() or "用户未给出有效回答"
        depth = self.score_depth(valid_answer)
        return AnswerResult(
            timestamp=datetime.now(timezone.utc),
            topic=str(topic.get("name", "")),
            question_type="核心问题",
            question=question,
            answer=valid_answer,
            depth_score=depth,
        )

    def process_followup_answer(
        self,
        *,
        answer: str,
        topic: dict[str, Any],
        followup_question: str,
        is_ai_generated: bool,
    ) -> AnswerResult:
        valid_answer = answer.strip() or "用户未补充回答"
        depth = self.score_depth(valid_answer)
        return AnswerResult(
            timestamp=datetime.now(timezone.utc),
            topic=str(topic.get("name", "")),
            question_type="追问回答",
            question=followup_question or "（追问）",
            answer=valid_answer,
            depth_score=depth,
            is_ai_generated=is_ai_generated,
        )
