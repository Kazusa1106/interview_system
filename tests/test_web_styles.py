"""Tests for web_styles module"""

import pytest
from interview_system.ui.web_styles import get_custom_css, MODERN_CSS


def test_get_custom_css_returns_string():
    """get_custom_css() returns a string"""
    result = get_custom_css()
    assert isinstance(result, str)


def test_get_custom_css_returns_modern_css():
    """get_custom_css() returns MODERN_CSS constant"""
    result = get_custom_css()
    assert result == MODERN_CSS


def test_get_custom_css_not_empty():
    """get_custom_css() returns non-empty CSS"""
    result = get_custom_css()
    assert len(result) > 0


def test_modern_css_contains_root_variables():
    """MODERN_CSS contains CSS root variables"""
    css = get_custom_css()
    assert ":root" in css
    assert "--app-bg" in css
    assert "--app-primary" in css


def test_modern_css_contains_chat_styles():
    """MODERN_CSS contains chat component styles"""
    css = get_custom_css()
    assert "#interview_chat" in css
    assert "#interview_input_bar" in css
    assert "#interview_send_btn" in css
