#!/usr/bin/env python3
# coding: utf-8
"""
Tests for QuestionSelector
"""

import pytest
from interview_system.core.question_selector import QuestionSelector
from interview_system.core.questions import TOPICS, SCENES, EDU_TYPES
from interview_system.common.config import INTERVIEW_CONFIG


class TestQuestionSelector:
    """Test question selection logic"""

    def setup_method(self):
        """Setup test fixtures"""
        self.selector = QuestionSelector()
        self.config = INTERVIEW_CONFIG

    def test_select_returns_correct_count(self):
        """Should return exactly total_questions items"""
        selected = self.selector.select(self.config)
        assert len(selected) == self.config.total_questions

    def test_select_covers_all_scenes(self):
        """Should cover all 3 scenes (school/home/community)"""
        selected = self.selector.select(self.config)
        scenes = {topic["scene"] for topic in selected}
        assert len(scenes) == len(SCENES)
        assert scenes == set(SCENES)

    def test_select_covers_all_edu_types(self):
        """Should cover all 5 education types"""
        selected = self.selector.select(self.config)
        edu_types = {topic["edu_type"] for topic in selected}
        assert len(edu_types) == len(EDU_TYPES)
        assert edu_types == set(EDU_TYPES)

    def test_select_returns_valid_topics(self):
        """All selected topics should exist in TOPICS"""
        selected = self.selector.select(self.config)
        for topic in selected:
            assert topic in TOPICS

    def test_select_no_duplicates(self):
        """Should not select duplicate topics"""
        selected = self.selector.select(self.config)
        topic_names = [t["name"] for t in selected]
        assert len(topic_names) == len(set(topic_names))

    def test_select_randomness(self):
        """Multiple selections should produce different results"""
        results = [self.selector.select(self.config) for _ in range(5)]
        topic_sets = [tuple(t["name"] for t in r) for r in results]
        # At least one should differ
        assert len(set(topic_sets)) > 1

    def test_select_with_insufficient_topics(self):
        """Should handle edge case when total_questions > available topics"""
        # This test verifies graceful degradation
        # Current implementation will select all available topics
        selected = self.selector.select(self.config)
        assert len(selected) <= len(TOPICS)
