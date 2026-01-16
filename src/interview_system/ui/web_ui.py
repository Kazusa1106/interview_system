#!/usr/bin/env python3
# coding: utf-8
"""
Web Interface Module
Gradio-based web interface for interviews
"""

from typing import Tuple, List

import interview_system.common.logger as logger
from interview_system.common.config import WEB_CONFIG
from interview_system.ui.web_handler import InterviewHandler
from interview_system.ui.web_utils import get_local_ip
from interview_system.ui.web_styles import get_custom_css
from interview_system.ui.web_components import (
    create_header,
    create_chatbot,
    create_input_area,
    create_action_buttons,
    create_sidebar,
    init_handler,
    respond,
    undo_action,
    skip_question,
    new_interview
)

# Check Gradio availability
GRADIO_AVAILABLE = False
try:
    import gradio as gr
    import qrcode
    from PIL import Image
    GRADIO_AVAILABLE = True
except ImportError as e:
    logger.warning(f"无法使用 Web 功能。原因：{e}")
    logger.warning("请运行 `pip install gradio qrcode[pil]` 安装缺失的库")


def _register_events(demo, components: dict):
    """Register all event handlers for the interface"""
    _register_init_events(demo, components)
    _register_message_events(components)
    _register_navigation_events(components)


def _register_init_events(demo, components: dict):
    """Register initialization events"""
    demo.load(
        init_handler,
        outputs=[components['handler_state'], components['chatbot']]
    )


def _register_message_events(components: dict):
    """Register message input/submit events"""
    msg = components['msg']
    submit_btn = components['submit_btn']
    chatbot = components['chatbot']
    handler_state = components['handler_state']

    msg.submit(
        respond,
        [msg, chatbot, handler_state],
        [chatbot, msg, msg, handler_state]
    )

    submit_btn.click(
        respond,
        [msg, chatbot, handler_state],
        [chatbot, msg, msg, handler_state]
    )


def _register_navigation_events(components: dict):
    """Register navigation/action button events"""
    skip_btn = components['skip_btn']
    refresh_btn = components['refresh_btn']
    undo_btn = components['undo_btn']
    chatbot = components['chatbot']
    handler_state = components['handler_state']
    msg = components['msg']

    skip_btn.click(
        skip_question,
        [chatbot, handler_state],
        [chatbot, handler_state, msg]
    )

    refresh_btn.click(
        new_interview,
        outputs=[handler_state, chatbot, msg]
    )

    undo_btn.click(
        undo_action,
        inputs=[chatbot, handler_state],
        outputs=[chatbot, msg, msg, handler_state]
    )


def create_web_interface():
    """创建Web界面"""
    if not GRADIO_AVAILABLE:
        logger.error("Gradio未安装，无法创建Web界面")
        return None

    with gr.Blocks(
        title=WEB_CONFIG.title
    ) as demo:
        handler_state = gr.State(None)

        with gr.Row():
            create_header()

        with gr.Row():
            with gr.Column(scale=3):
                chatbot = create_chatbot()

                with gr.Row(elem_id="interview_input_bar"):
                    msg, submit_btn = create_input_area()

                with gr.Row(elem_id="interview_action_bar"):
                    undo_btn, skip_btn, refresh_btn = create_action_buttons()

            with gr.Column(scale=1, elem_id="interview_sidebar"):
                instructions, stats_display = create_sidebar()

        _register_events(demo, {
            'msg': msg,
            'submit_btn': submit_btn,
            'skip_btn': skip_btn,
            'refresh_btn': refresh_btn,
            'undo_btn': undo_btn,
            'chatbot': chatbot,
            'handler_state': handler_state
        })

    return demo


def start_web_server(share: bool = None):
    """
    启动Web服务器

    Args:
        share: 是否生成公网链接（默认使用配置）
    """
    log = logger.get_logger(__name__)

    if not GRADIO_AVAILABLE:
        log.error("无法启动Web服务：缺少 gradio 库")
        return

    demo = create_web_interface()
    if not demo:
        log.error("创建Web界面失败")
        return

    should_share = share if share is not None else WEB_CONFIG.share
    _launch_and_serve(demo, should_share, log)


def _launch_and_serve(demo, share: bool, log):
    """Launch Gradio server and serve until interrupted"""
    local_ip = get_local_ip()
    port = WEB_CONFIG.port
    url = f"http://{local_ip}:{port}"

    log.info("准备启动Web服务器", extra={"url": url, "share": share})
    _print_pre_launch_info(url, share)

    try:
        app, local_url, share_url = demo.launch(
            server_name=WEB_CONFIG.host,
            server_port=port,
            share=share,
            prevent_thread_lock=True,
            theme=gr.themes.Soft(),
            css=get_custom_css()
        )

        final_url = share_url if share_url else url
        _print_post_launch_info(final_url, share_url, url)
        _generate_qr_code(final_url, log)

        log.info("Web服务器已启动", extra={"url": final_url})
        _keep_alive(log)

    except Exception as e:
        log.error("启动Web服务器失败", extra={"error": str(e)}, exc_info=True)


def _print_pre_launch_info(url: str, share: bool):
    """Print pre-launch information"""
    print("\n" + "=" * 50)
    print(f"🚀 Web 服务器即将启动！")
    print(f"📍 局域网地址：{url}")
    if share:
        print("🌐 正在生成公网链接，请稍候...")
    print("=" * 50 + "\n")


def _print_post_launch_info(final_url: str, share_url: str, local_url: str):
    """Print post-launch information"""
    print("\n" + "=" * 50)
    if share_url:
        print(f"✅ 公网链接已生成：{share_url}")
        print("📱 任何人都可以扫描下方二维码访问（无需同一WiFi）")
    else:
        print(f"📍 局域网地址：{local_url}")
        print("📱 请确保手机与电脑在同一WiFi下")
    print("=" * 50 + "\n")


def _generate_qr_code(url: str, log):
    """Generate and save QR code for URL"""
    try:
        qr = qrcode.QRCode()
        qr.add_data(url)
        qr.print_ascii()

        img = qrcode.make(url)
        img.save("access_code.png")
        log.info("二维码已生成", extra={"path": "access_code.png"})
        print(f"\n✅ 已生成二维码图片：access_code.png")
    except Exception as e:
        log.warning("生成二维码失败", extra={"error": str(e)})


def _keep_alive(log):
    """Keep server running until keyboard interrupt"""
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Web服务器停止（用户中断）")
        print("\n服务已停止。")


def check_gradio_available() -> bool:
    """检查Gradio是否可用"""
    return GRADIO_AVAILABLE
