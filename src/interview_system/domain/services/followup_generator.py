"""追问生成器（领域服务）。

约束：
- 领域层不直接依赖 OpenAI/第三方 SDK
- 通过 FollowupLLM 抽象 LLM 调用，可在测试中 mock
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Protocol, Sequence


class FollowupLLM(Protocol):
    def generate_followup(
        self,
        answer: str,
        topic: dict[str, Any],
        conversation_log: Sequence[dict[str, Any]] | None = None,
    ) -> str | None: ...


@dataclass(frozen=True, slots=True)
class FollowupResult:
    need_followup: bool
    followup_question: str = ""
    is_ai_generated: bool = False


class FollowupGenerator:
    def __init__(
        self,
        *,
        llm: FollowupLLM | None,
        min_answer_length: int,
        max_followups_per_question: int,
        max_depth_score: int,
    ) -> None:
        self._llm = llm
        self._min_answer_length = int(min_answer_length)
        self._max_followups_per_question = int(max_followups_per_question)
        self._max_depth_score = int(max_depth_score)

    def should_followup(
        self,
        *,
        answer: str,
        topic: dict[str, Any],
        conversation_log: Sequence[dict[str, Any]] | None,
        current_followup_count: int,
        depth_score: int,
        seed: int | None = None,
    ) -> FollowupResult:
        valid_answer = answer.strip()
        if current_followup_count >= self._max_followups_per_question:
            return FollowupResult(need_followup=False)

        force = (not valid_answer) or (len(valid_answer) < self._min_answer_length)
        if depth_score >= self._max_depth_score:
            return FollowupResult(need_followup=False)

        # LLM 尝试
        if self._llm is not None:
            followup = self._llm.generate_followup(
                valid_answer, topic, conversation_log
            )
            if followup:
                return FollowupResult(True, followup, True)

        # 强制追问时，使用预设追问兜底
        if force:
            presets = topic.get("followups") or ["能再具体说说吗？"]
            rng = random.Random(seed)
            return FollowupResult(True, str(rng.choice(list(presets))), False)

        return FollowupResult(need_followup=False)
