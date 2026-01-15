#!/usr/bin/env python3
# coding: utf-8
"""
QuestionSelector - Selects interview questions with scene and education type coverage
"""

import random
from typing import List, Dict

from interview_system.common.config import InterviewConfig
from interview_system.core.questions import TOPICS, SCENES, EDU_TYPES


class QuestionSelector:
    """Selects questions ensuring scene and education type coverage"""

    def select(self, config: InterviewConfig) -> List[Dict]:
        """
        Select interview questions
        Rule: Random selection covering 3 scenes + 5 education types

        Args:
            config: Interview configuration

        Returns:
            Selected topic list
        """
        scene_groups = self._group_by_scene()
        edu_groups = self._group_by_edu_type()

        selected = []
        selected.extend(self._select_by_scene(scene_groups))
        selected.extend(self._fill_edu_gaps(edu_groups, selected, config))
        selected.extend(self._fill_remaining(selected, config))

        random.shuffle(selected)
        return selected

    def _group_by_scene(self) -> Dict[str, List[Dict]]:
        """Group topics by scene"""
        groups = {scene: [] for scene in SCENES}
        for topic in TOPICS:
            groups[topic["scene"]].append(topic)
        return groups

    def _group_by_edu_type(self) -> Dict[str, List[Dict]]:
        """Group topics by education type"""
        groups = {edu: [] for edu in EDU_TYPES}
        for topic in TOPICS:
            groups[topic["edu_type"]].append(topic)
        return groups

    def _select_by_scene(self, scene_groups: Dict[str, List[Dict]]) -> List[Dict]:
        """Select one topic per scene"""
        selected = []
        for scene in SCENES:
            if scene_groups[scene]:
                selected.append(random.choice(scene_groups[scene]))
        return selected

    def _fill_edu_gaps(
        self,
        edu_groups: Dict[str, List[Dict]],
        selected: List[Dict],
        config: InterviewConfig
    ) -> List[Dict]:
        """Fill missing education types"""
        covered_edu = {t["edu_type"] for t in selected}
        needed_edu = set(EDU_TYPES) - covered_edu

        filled = []
        while needed_edu and len(selected) + len(filled) < config.total_questions:
            edu_type = needed_edu.pop()
            candidates = [t for t in edu_groups[edu_type] if t not in selected and t not in filled]
            if candidates:
                filled.append(random.choice(candidates))

        return filled

    def _fill_remaining(self, selected: List[Dict], config: InterviewConfig) -> List[Dict]:
        """Fill remaining slots with random topics"""
        remaining = [t for t in TOPICS if t not in selected]
        filled = []

        while len(selected) + len(filled) < config.total_questions and remaining:
            topic = random.choice(remaining)
            filled.append(topic)
            remaining.remove(topic)

        return filled
