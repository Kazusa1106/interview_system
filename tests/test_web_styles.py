"""Tests for web_styles module"""

import pytest
from interview_system.ui.web_styles import get_custom_css, WECHAT_CSS


def test_get_custom_css_returns_string():
    """get_custom_css() returns a string"""
    result = get_custom_css()
    assert isinstance(result, str)


def test_get_custom_css_returns_wechat_css():
    """get_custom_css() returns WECHAT_CSS constant"""
    result = get_custom_css()
    assert result == WECHAT_CSS


def test_get_custom_css_not_empty():
    """get_custom_css() returns non-empty CSS"""
    result = get_custom_css()
    assert len(result) > 0


def test_wechat_css_contains_root_variables():
    """WECHAT_CSS contains CSS root variables"""
    css = get_custom_css()
    assert ":root" in css
    assert "--wechat-bg" in css
    assert "--wechat-green" in css


def test_wechat_css_contains_chat_styles():
    """WECHAT_CSS contains chat component styles"""
    css = get_custom_css()
    assert "#wechat_chat" in css
    assert "#wechat_input_bar" in css
    assert "#wechat_send_btn" in css
