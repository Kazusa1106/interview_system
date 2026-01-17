"""问题选择器（领域服务）。

约束：
- 不依赖外部单例/全局状态
- 通过 seed 控制随机性，便于测试
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from typing import Any


def select_questions(
    *,
    topics: Sequence[dict[str, Any]],
    scenes: Sequence[str],
    edu_types: Sequence[str],
    total_questions: int,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    rng = random.Random(seed)

    scene_groups: dict[str, list[dict[str, Any]]] = {scene: [] for scene in scenes}
    edu_groups: dict[str, list[dict[str, Any]]] = {edu: [] for edu in edu_types}

    for topic in topics:
        scene_groups.get(str(topic.get("scene")), []).append(topic)
        edu_groups.get(str(topic.get("edu_type")), []).append(topic)

    selected: list[dict[str, Any]] = []

    # 每个场景至少选一个
    for scene in scenes:
        if len(selected) >= total_questions:
            break
        candidates = scene_groups.get(scene) or []
        if candidates:
            selected.append(rng.choice(candidates))

    # 覆盖缺失的教育类型
    covered_edu = {str(t.get("edu_type")) for t in selected}
    needed_edu = [e for e in edu_types if e not in covered_edu]

    filled: list[dict[str, Any]] = []
    while needed_edu and len(selected) + len(filled) < total_questions:
        edu = needed_edu.pop(0)
        candidates = [
            t
            for t in (edu_groups.get(edu) or [])
            if t not in selected and t not in filled
        ]
        if candidates:
            filled.append(rng.choice(candidates))

    # 补齐剩余
    remaining = [t for t in topics if t not in selected and t not in filled]
    while len(selected) + len(filled) < total_questions and remaining:
        chosen = rng.choice(remaining)
        filled.append(chosen)
        remaining.remove(chosen)

    selected.extend(filled)
    rng.shuffle(selected)
    return selected
