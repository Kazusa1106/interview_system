#!/usr/bin/env python3
# coding: utf-8
"""
Tests for web_handler.py bounded undo stack
"""

import pytest
from collections import deque

from interview_system.ui.web_handler import InterviewHandler


class TestUndoStackBounds:
    """Test bounded undo stack behavior"""

    def test_undo_stack_is_deque(self):
        """Undo stack should be a deque"""
        handler = InterviewHandler()
        assert isinstance(handler._undo_stack, deque)

    def test_undo_stack_has_maxlen(self):
        """Undo stack should have maxlen=10"""
        handler = InterviewHandler()
        assert handler._undo_stack.maxlen == 10

    def test_undo_stack_bounds_at_10(self):
        """Undo stack should not exceed 10 items"""
        handler = InterviewHandler()

        # Push 15 snapshots
        for i in range(15):
            snapshot = {
                "history_before": [],
                "submitted_text": f"text_{i}",
                "session_state_before": {},
                "log_count_before": i,
            }
            handler._undo_stack.append(snapshot)

        # Should only keep last 10
        assert len(handler._undo_stack) == 10

        # First item should be from iteration 5 (0-4 dropped)
        assert handler._undo_stack[0]["log_count_before"] == 5
        assert handler._undo_stack[-1]["log_count_before"] == 14

    def test_undo_stack_fifo_eviction(self):
        """Oldest items should be evicted first"""
        handler = InterviewHandler()

        # Push 12 items
        for i in range(12):
            handler._undo_stack.append({"id": i})

        # Items 0 and 1 should be gone
        ids = [item["id"] for item in handler._undo_stack]
        assert ids == list(range(2, 12))
