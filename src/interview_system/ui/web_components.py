#!/usr/bin/env python3
# coding: utf-8
"""
Web UI Component Factory
Extracted component creation logic from web_ui.py
"""

from typing import Tuple, List, Any

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False


def create_header() -> "gr.HTML":
    """Create WeChat-style header"""
    return gr.HTML(
        """
        <div class="wechat-topbar">
            <p class="wechat-title">大学生五育并举访谈</p>
            <p class="wechat-subtitle">像微信一样聊天式访谈，放松分享真实经历与感受</p>
        </div>
        """,
        elem_id="wechat_header"
    )


def create_chatbot() -> "gr.Chatbot":
    """Create chat display area"""
    return gr.Chatbot(
        label="访谈对话",
        height=500,
        show_label=False,
        avatar_images=(None, "https://em-content.zobj.net/source/twitter/376/robot_1f916.png"),
        elem_id="wechat_chat"
    )


def create_input_area() -> Tuple["gr.Textbox", "gr.Button"]:
    """Create input textbox and submit button"""
    textbox = gr.Textbox(
        label="你的回答",
        placeholder="请输入你的回答…",
        scale=6,
        show_label=False,
        lines=2,
        max_lines=5
    )
    button = gr.Button(
        "发送",
        variant="primary",
        scale=1,
        elem_id="wechat_send_btn"
    )
    return textbox, button


def create_action_buttons() -> Tuple["gr.Button", "gr.Button", "gr.Button"]:
    """Create undo, skip, and refresh buttons"""
    undo = gr.Button("↩️ 撤回", variant="secondary", scale=1)
    skip = gr.Button("⏭️ 跳过此题", variant="secondary", scale=1)
    refresh = gr.Button("🔄 重新开始", variant="secondary", scale=1)
    return undo, skip, refresh


def create_sidebar() -> Tuple["gr.Markdown", "gr.Markdown"]:
    """Create sidebar with instructions and stats"""
    instructions = gr.Markdown("""
    ### 📖 使用说明

    欢迎参加访谈！本次访谈将围绕五育发展展开。

    **操作提示**：
    - 💬 在下方输入框输入回答
    - ⏭️ 不方便回答可点击跳过
    - 🔄 可随时重新开始

    **访谈规则**：
    - 共 6 个问题
    - 涵盖学校、家庭、社区场景
    - 包含德智体美劳五育内容
    - AI会根据你的回答智能追问

    ---

    ### 💡 小贴士

    回答时可以包含：
    - ✨ 具体的经历和例子
    - 💭 你的真实感受
    - 📈 你的收获和改变
    - 🔍 过程中的细节

    回答越详细，AI追问会越精准！
    """)

    stats = gr.Markdown("""
    ### 📊 实时统计

    *访谈开始后显示统计*
    """)

    return instructions, stats


# Event Handlers

def init_handler():
    """Initialize handler - lazy load mode"""
    from interview_system.ui.web_handler import InterviewHandler
    handler = InterviewHandler()
    history, _ = handler.lazy_initialize()
    return handler, history


def respond(user_input: str, history: List, handler: Any) -> Tuple[List, str, Any, Any]:
    """Process user input"""
    from interview_system.ui.web_handler import InterviewHandler
    if handler is None:
        handler = InterviewHandler()

    new_history, clear_input, input_update = handler.process_message(user_input, history)
    return new_history, clear_input, input_update, handler


def undo_action(history: List, handler: Any) -> Tuple[List, str, Any, Any]:
    """Undo last operation"""
    if handler is None:
        return history, "", gr.update(), handler
    new_history, restored_input, input_update = handler.undo_last(history)
    return new_history, restored_input, input_update, handler


def skip_question(history: List, handler: Any) -> Tuple[List, Any, Any]:
    """Skip current question"""
    if handler is None or not handler._initialized:
        return history, handler, gr.update()

    new_history, clear_input, input_update = handler.skip_round(history)
    return new_history, handler, input_update


def new_interview() -> Tuple[Any, List, Any]:
    """Start new interview"""
    from interview_system.ui.web_handler import InterviewHandler
    handler = InterviewHandler()
    history, _ = handler.lazy_initialize()
    return handler, history, gr.update(interactive=True)
