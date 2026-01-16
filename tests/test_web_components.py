#!/usr/bin/env python3
# coding: utf-8
"""
Tests for web_components module
"""

import pytest

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not GRADIO_AVAILABLE,
    reason="Gradio not installed"
)


class TestComponentCreation:
    """Test component factory functions"""

    def test_create_header_returns_html(self):
        from interview_system.ui.web_components import create_header

        header = create_header()
        assert isinstance(header, gr.HTML)
        assert header.elem_id == "interview_header"

    def test_create_chatbot_returns_configured_chatbot(self):
        from interview_system.ui.web_components import create_chatbot

        chatbot = create_chatbot()
        assert isinstance(chatbot, gr.Chatbot)
        assert chatbot.height == 500
        assert chatbot.show_label is False
        assert chatbot.elem_id == "interview_chat"

    def test_create_input_area_returns_textbox_and_button(self):
        from interview_system.ui.web_components import create_input_area

        textbox, button = create_input_area()
        assert isinstance(textbox, gr.Textbox)
        assert isinstance(button, gr.Button)
        assert textbox.show_label is False
        assert textbox.lines == 2
        assert textbox.max_lines == 5
        assert button.elem_id == "interview_send_btn"

    def test_create_action_buttons_returns_three_buttons(self):
        from interview_system.ui.web_components import create_action_buttons

        undo, skip, refresh = create_action_buttons()
        assert isinstance(undo, gr.Button)
        assert isinstance(skip, gr.Button)
        assert isinstance(refresh, gr.Button)

    def test_create_sidebar_returns_two_markdowns(self):
        from interview_system.ui.web_components import create_sidebar

        instructions, stats = create_sidebar()
        assert isinstance(instructions, gr.Markdown)
        assert isinstance(stats, gr.Markdown)
