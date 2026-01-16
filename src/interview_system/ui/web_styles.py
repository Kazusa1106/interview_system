"""Modern Professional CSS for Gradio interface"""

def get_custom_css() -> str:
    """Return custom CSS for Gradio interface."""
    return MODERN_CSS


MODERN_CSS = """
:root {
    --app-bg: #F9FAFB;
    --app-card: #ffffff;
    --app-border: #E5E7EB;
    --app-text: #111827;
    --app-subtext: #6B7280;
    --app-primary: #4F46E5;
    --app-primary-dark: #4338CA;
    --app-gradient-start: #4F46E5;
    --app-gradient-end: #7C3AED;
    --app-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
    --app-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.gradio-container {
    background: var(--app-bg);
}

#interview_header .app-topbar {
    background: linear-gradient(135deg, var(--app-gradient-start) 0%, var(--app-gradient-end) 100%);
    border: none;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: var(--app-shadow-lg);
}
#interview_header .app-title {
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
#interview_header .app-subtitle {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.9);
    margin: 8px 0 0 0;
    line-height: 1.5;
}

#interview_chat {
    border: none;
    background: transparent;
}
#interview_chat .wrap,
#interview_chat .message-wrap,
#interview_chat .message-list {
    background: transparent;
}
#interview_chat .message {
    padding: 8px 0;
}

#interview_chat .message.user .bubble,
#interview_chat .message.user .bubble-wrap,
#interview_chat .message.user .bubble-content {
    background: var(--app-primary) !important;
    color: #ffffff !important;
    border: none;
    border-radius: 18px;
    box-shadow: var(--app-shadow);
}
#interview_chat .message.bot .bubble,
#interview_chat .message.bot .bubble-wrap,
#interview_chat .message.bot .bubble-content {
    background: var(--app-card) !important;
    color: var(--app-text) !important;
    border: 1px solid var(--app-border);
    border-radius: 18px;
    box-shadow: var(--app-shadow);
}

#interview_chat img.avatar,
#interview_chat .avatar img {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    box-shadow: var(--app-shadow);
}

.stats-box {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid var(--app-border);
    border-radius: 16px;
    padding: 12px 16px;
    margin-top: 12px;
    box-shadow: var(--app-shadow);
}

#interview_input_bar {
    position: sticky;
    bottom: 0;
    z-index: 10;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(12px) saturate(180%);
    padding: 16px 12px;
    border-top: 1px solid rgba(229, 231, 235, 0.5);
    border-radius: 16px;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}
#interview_input_bar textarea,
#interview_input_bar input {
    border-radius: 12px !important;
    border: 1px solid var(--app-border) !important;
    background: var(--app-card) !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
    transition: all 0.2s ease;
}
#interview_input_bar textarea:focus,
#interview_input_bar input:focus {
    border-color: var(--app-primary) !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
}
#interview_send_btn {
    border-radius: 12px !important;
    background: var(--app-primary) !important;
    color: #fff !important;
    border: none !important;
    font-weight: 600 !important;
    transition: all 0.2s ease;
}
#interview_send_btn:hover {
    background: var(--app-primary-dark) !important;
    transform: translateY(-1px);
    box-shadow: var(--app-shadow-lg) !important;
}

#interview_action_bar button {
    border-radius: 12px !important;
    transition: all 0.2s ease;
}
#interview_action_bar button:hover {
    transform: translateY(-1px);
}

#interview_sidebar {
    background: var(--app-card);
    border-radius: 16px;
    padding: 16px;
    box-shadow: var(--app-shadow);
}

@media (max-width: 900px) {
    #interview_sidebar {
        display: none;
    }
}
@media (max-width: 640px) {
    #interview_header .app-topbar {
        border-radius: 12px;
        padding: 16px 20px;
    }
    #interview_header .app-title {
        font-size: 20px;
    }
    #interview_header .app-subtitle {
        font-size: 13px;
    }
    #interview_input_bar {
        border-radius: 12px;
        padding: 12px 8px;
    }
}
"""
