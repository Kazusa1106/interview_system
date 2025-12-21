#!/usr/bin/env python3
# coding: utf-8
"""
Web服务模块 - 大学生五育并举访谈智能体
基于Gradio实现Web界面，支持多人同时访谈
"""

import socket
import copy
from typing import Tuple, List, Optional

import interview_system.common.logger as logger
from interview_system.common.config import WEB_CONFIG
from interview_system.services.session_manager import get_session_manager, InterviewSession
from interview_system.core.interview_engine import InterviewEngine, create_interview

# 检查Gradio是否可用
GRADIO_AVAILABLE = False
try:
    import gradio as gr
    import qrcode
    from PIL import Image
    GRADIO_AVAILABLE = True
except ImportError as e:
    logger.warning(f"无法使用 Web 功能。原因：{e}")
    logger.warning("请运行 `pip install gradio qrcode[pil]` 安装缺失的库")


class WebInterviewHandler:
    """Web访谈处理器 - 处理单个用户的访谈会话"""
    
    def __init__(self):
        self.session: Optional[InterviewSession] = None
        self.engine: Optional[InterviewEngine] = None
        self._initialized = False
        self._undo_stack: List[dict] = []

    def _capture_session_state(self) -> dict:
        """捕获可回滚的会话状态快照"""
        if not self.session:
            return {}
        return {
            "session_id": self.session.session_id,
            "current_question_idx": self.session.current_question_idx,
            "is_finished": self.session.is_finished,
            "end_time": self.session.end_time,
            "is_followup": getattr(self.session, "is_followup", False),
            "current_followup_is_ai": getattr(self.session, "current_followup_is_ai", False),
            "current_followup_count": getattr(self.session, "current_followup_count", 0),
            "current_followup_question": getattr(self.session, "current_followup_question", ""),
        }

    def _push_undo_snapshot(self, history: List, submitted_text: str):
        """对会改变状态/日志的操作压栈，用于撤回"""
        if not self.session:
            return
        snapshot = {
            "history_before": copy.deepcopy(history),
            "submitted_text": submitted_text,
            "session_state_before": self._capture_session_state(),
            "log_count_before": len(self.session.conversation_log) if self.session.conversation_log else 0,
        }
        self._undo_stack.append(snapshot)
    
    def initialize(self, user_name: str = None) -> Tuple[List, str]:
        """
        初始化访谈会话
        
        Args:
            user_name: 用户名
            
        Returns:
            (聊天历史, 状态消息)
        """
        self.session, self.engine = create_interview(user_name or "Web访谈者")
        self._initialized = True
        self._undo_stack = []
        
        # 获取第一个问题
        first_question = self.engine.get_current_question()
        
        # 构建欢迎消息
        welcome = (
            "👋 你好，欢迎参加本次访谈！\n\n"
            "接下来我会向你提出 6 个问题，话题涉及你在学校、家庭和社区中的经历与感受。\n\n"
            "💬 请放松心情，用自己的话分享真实想法，没有标准答案。\n"
            "⏭️ 如果某个问题不方便回答，可以点击「跳过」按钮。\n\n"
            "准备好了吗？让我们开始吧！"
        )
        
        history = [
            [None, welcome],
            [None, first_question]
        ]
        
        logger.log_interview(
            self.session.session_id,
            "Web访谈开始",
            {"user": self.session.user_name}
        )
        
        return history, ""
    
    def lazy_initialize(self) -> Tuple[List, str]:
        """
        初始化访谈 - 直接创建会话并显示第一个问题
        
        Returns:
            (聊天历史, 状态消息)
        """
        # 直接初始化完整会话
        self.session, self.engine = create_interview("Web访谈者")
        self._initialized = True
        self._undo_stack = []
        
        # 获取第一个问题
        first_question = self.engine.get_current_question()
        
        # 构建欢迎消息
        welcome = (
            "👋 你好，欢迎参加本次访谈！\n\n"
            "接下来我会向你提出 6 个问题，话题涉及你在学校、家庭和社区中的经历与感受。\n\n"
            "💬 请放松心情，用自己的话分享真实想法，没有标准答案。\n"
            "⏭️ 如果某个问题不方便回答，可以点击「跳过」按钮。\n\n"
            "准备好了吗？让我们开始吧！"
        )
        
        history = [
            [None, welcome],
            [None, first_question]
        ]
        
        logger.log_interview(
            self.session.session_id,
            "Web访谈开始",
            {"user": self.session.user_name}
        )
        
        return history, ""
    
    def process_message(
        self, 
        user_input: str, 
        history: List
    ) -> Tuple[List, str, dict]:
        """
        处理用户消息
        
        Args:
            user_input: 用户输入
            history: 聊天历史
            
        Returns:
            (更新后的历史, 清空输入框的值, 输入框更新)
        """
        # 检查会话是否已初始化
        if not self._initialized or not self.session or not self.engine:
            return history, "", gr.update()
        
        if self.session.is_finished:
            # 访谈已结束
            history.append([user_input, "访谈已结束，请点击下方按钮开始新访谈。"])
            return history, "", gr.update(interactive=False)
        
        if not user_input.strip():
            return history, "", gr.update()
        
        # 处理跳过命令
        if user_input.strip() in ["/跳过", "跳过", "/skip"]:
            was_followup = bool(getattr(self.session, "is_followup", False))
            self._push_undo_snapshot(history, submitted_text="")
            result = self.engine.skip_round()
            if was_followup:
                history.append([user_input, "好的，已跳过本轮追问。"])
            else:
                history.append([user_input, "好的，已跳过当前问题。"])
            
            if result.is_finished:
                # 访谈结束，自动导出日志
                self.export_log()
                history.append([None, "🎉 访谈结束！感谢你的参与。"])
                return history, "", gr.update(interactive=False)
            else:
                history.append([None, result.next_question])
                return history, "", gr.update()
        
        # 处理普通回答
        self._push_undo_snapshot(history, submitted_text=user_input)
        result = self.engine.process_answer(user_input)
        
        # 添加用户回答到历史
        history.append([user_input, None])
        
        if result.need_followup:
            # 需要追问
            prefix = "💡 " if result.is_ai_generated else "📝 "
            history[-1][1] = "收到。"
            history.append([None, f"{prefix}{result.followup_question}"])
        elif result.is_finished:
            # 访谈结束，自动导出日志
            self.export_log()
            history[-1][1] = "收到。"
            history.append([None, "🎉 访谈结束！感谢你的参与。"])
            return history, "", gr.update(interactive=False)
        else:
            # 进入下一题
            history[-1][1] = "✅ 收到，进入下一题。"
            history.append([None, result.next_question])
        
        return history, "", gr.update()

    def skip_round(self, history: List) -> Tuple[List, str, dict]:
        """
        跳过本轮对话（当前题或当前追问）

        Args:
            history: 聊天历史

        Returns:
            (更新后的历史, 清空输入框的值, 输入框更新)
        """
        if not self._initialized or not self.session or not self.engine:
            return history, "", gr.update()

        if self.session.is_finished:
            history.append([None, "访谈已结束，请点击下方按钮开始新访谈。"])
            return history, "", gr.update(interactive=False)

        was_followup = bool(getattr(self.session, "is_followup", False))
        self._push_undo_snapshot(history, submitted_text="")
        result = self.engine.skip_round()

        if was_followup:
            history.append([None, "好的，已跳过本轮追问。"])
        else:
            history.append([None, "好的，已跳过当前问题。"])

        if result.is_finished:
            self.export_log()
            history.append([None, "🎉 访谈结束！感谢你的参与。"])
            return history, "", gr.update(interactive=False, value="")

        if result.next_question:
            history.append([None, result.next_question])
        return history, "", gr.update(value="")

    def undo_last(self, history: List) -> Tuple[List, str, dict]:
        """
        撤回最近一次操作（发送/跳过）

        Returns:
            (回滚后的历史, 回填输入框的值, 输入框更新)
        """
        if not self._initialized or not self.session or not self.engine:
            return history, "", gr.update()

        if not self._undo_stack:
            history.append([None, "暂无可撤回内容。"])
            return history, "", gr.update()

        snapshot = self._undo_stack[-1]
        session_id = snapshot.get("session_state_before", {}).get("session_id")
        target_log_count = int(snapshot.get("log_count_before", 0))
        session_state = snapshot.get("session_state_before", {})

        ok = get_session_manager().rollback_session(
            session_id,
            target_log_count=target_log_count,
            session_state=session_state
        )
        if not ok:
            history.append([None, "撤回失败：数据回滚未成功，请稍后重试。"])
            return history, "", gr.update()

        # 回滚成功后再弹栈，避免失败导致丢失快照
        self._undo_stack.pop()

        restored_history = snapshot.get("history_before", history)
        restored_text = snapshot.get("submitted_text", "") or ""
        interactive = not bool(session_state.get("is_finished", False))
        return restored_history, restored_text, gr.update(value=restored_text, interactive=interactive)
    
    def export_log(self) -> Optional[str]:
        """
        导出访谈日志
        
        Returns:
            导出的文件路径
        """
        if not self.session:
            return None
        
        return get_session_manager().export_session(self.session.session_id)
    
    def get_statistics(self) -> str:
        """
        获取访谈统计信息
        
        Returns:
            统计信息文本
        """
        if not self.session or not self.engine:
            return "暂无统计信息"
        
        summary = self.engine.get_summary()
        stats = summary.get("statistics", {})
        
        text = f"""
📊 **访谈统计**

- 会话ID: {summary.get('session_id', 'N/A')}
- 用户: {summary.get('user_name', 'N/A')}
- 开始时间: {summary.get('start_time', 'N/A')}
- 总记录数: {stats.get('total_logs', 0)}

**场景分布:**
{self._format_dict(stats.get('scene_distribution', {}))}

**五育分布:**
{self._format_dict(stats.get('edu_distribution', {}))}

**追问统计:**
{self._format_dict(stats.get('followup_distribution', {}))}
"""
        return text.strip()
    
    def _format_dict(self, d: dict) -> str:
        """格式化字典为文本"""
        if not d:
            return "  无"
        return "\n".join(f"  - {k}: {v}" for k, v in d.items())


def get_local_ip() -> str:
    """获取本机局域网IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def create_web_interface():
    """创建Web界面"""
    if not GRADIO_AVAILABLE:
        logger.error("Gradio未安装，无法创建Web界面")
        return None

    # 自定义CSS样式
    custom_css = """
    :root {
        --wechat-bg: #f5f5f5;
        --wechat-card: #ffffff;
        --wechat-border: #e9e9e9;
        --wechat-text: #111111;
        --wechat-subtext: #6b6b6b;
        --wechat-green: #07c160;
        --wechat-bubble-green: #95ec69;
        --wechat-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
    }

    /* 全局背景与容器间距 */
    .gradio-container {
        background: var(--wechat-bg);
    }

    /* 顶部栏：接近微信会话页 */
    #wechat_header .wechat-topbar {
        background: var(--wechat-card);
        border: 1px solid var(--wechat-border);
        border-radius: 12px;
        padding: 12px 16px;
        box-shadow: var(--wechat-shadow);
    }
    #wechat_header .wechat-title {
        font-size: 18px;
        font-weight: 700;
        color: var(--wechat-text);
        line-height: 1.2;
        margin: 0;
    }
    #wechat_header .wechat-subtitle {
        font-size: 13px;
        color: var(--wechat-subtext);
        margin: 6px 0 0 0;
        line-height: 1.4;
    }

    /* 聊天区域：气泡 + 背景 */
    #wechat_chat {
        border: none;
        background: transparent;
    }
    #wechat_chat .wrap,
    #wechat_chat .message-wrap,
    #wechat_chat .message-list {
        background: var(--wechat-bg);
    }
    #wechat_chat .message {
        padding: 6px 0;
    }

    /* 兼容不同 Gradio DOM：优先使用常见的 .message.user/.message.bot */
    #wechat_chat .message.user .bubble,
    #wechat_chat .message.user .bubble-wrap,
    #wechat_chat .message.user .bubble-content {
        background: var(--wechat-bubble-green) !important;
        color: #000 !important;
        border: 1px solid rgba(0, 0, 0, 0.04);
        border-radius: 18px 6px 18px 18px;
        box-shadow: var(--wechat-shadow);
    }
    #wechat_chat .message.bot .bubble,
    #wechat_chat .message.bot .bubble-wrap,
    #wechat_chat .message.bot .bubble-content {
        background: var(--wechat-card) !important;
        color: var(--wechat-text) !important;
        border: 1px solid var(--wechat-border);
        border-radius: 6px 18px 18px 18px;
        box-shadow: var(--wechat-shadow);
    }

    /* 头像尺寸更接近聊天应用 */
    #wechat_chat img.avatar,
    #wechat_chat .avatar img {
        width: 32px;
        height: 32px;
        border-radius: 50%;
    }

    /* 进度卡片：弱化为系统信息样式 */
    .stats-box {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid var(--wechat-border);
        border-radius: 12px;
        padding: 10px 12px;
        margin-top: 10px;
        box-shadow: var(--wechat-shadow);
    }
    .progress-bar {
        background: #ededed;
        border-radius: 999px;
        height: 10px;
        margin: 8px 0;
        overflow: hidden;
    }
    .progress-fill {
        background: var(--wechat-green);
        height: 100%;
        border-radius: 999px;
        transition: width 0.3s ease;
    }

    /* 底部输入条：stick to bottom（在容器内） */
    #wechat_input_bar {
        position: sticky;
        bottom: 0;
        z-index: 10;
        background: rgba(245, 245, 245, 0.96);
        backdrop-filter: blur(6px);
        padding: 10px 8px 12px 8px;
        border-top: 1px solid var(--wechat-border);
        border-radius: 12px;
    }
    #wechat_input_bar textarea,
    #wechat_input_bar input {
        border-radius: 18px !important;
        border: 1px solid #d9d9d9 !important;
        background: var(--wechat-card) !important;
        padding: 10px 12px !important;
        font-size: 14px !important;
        line-height: 1.4 !important;
    }
    #wechat_send_btn {
        border-radius: 18px !important;
        background: var(--wechat-green) !important;
        color: #fff !important;
        border: none !important;
    }

    /* 次要操作按钮 */
    #wechat_action_bar button {
        border-radius: 18px !important;
    }

    /* 移动端：隐藏侧栏，收紧间距 */
    @media (max-width: 900px) {
        #wechat_sidebar {
            display: none;
        }
    }
    @media (max-width: 640px) {
        #wechat_header .wechat-topbar {
            border-radius: 10px;
            padding: 10px 12px;
        }
        #wechat_header .wechat-title {
            font-size: 16px;
        }
        #wechat_header .wechat-subtitle {
            font-size: 12px;
        }
        #wechat_input_bar {
            border-radius: 10px;
            padding: 8px 6px 10px 6px;
        }
    }
    """

    with gr.Blocks(
        title=WEB_CONFIG.title,
        theme=gr.themes.Soft(),
        css=custom_css
    ) as demo:
        # 状态：每个用户独立的处理器
        handler_state = gr.State(None)

        # 顶部栏（微信风格近似）
        with gr.Row():
            gr.HTML(
                """
                <div class="wechat-topbar">
                    <p class="wechat-title">大学生五育并举访谈</p>
                    <p class="wechat-subtitle">像微信一样聊天式访谈，放松分享真实经历与感受</p>
                </div>
                """,
                elem_id="wechat_header"
            )

        with gr.Row():
            with gr.Column(scale=3):
                # 聊天区域
                chatbot = gr.Chatbot(
                    label="访谈对话",
                    height=500,
                    show_label=False,
                    bubble_full_width=False,
                    avatar_images=(None, "https://em-content.zobj.net/source/twitter/376/robot_1f916.png"),
                    elem_id="wechat_chat"
                )

                # 进度显示
                progress_html = gr.HTML("""
                <div class="stats-box">
                    <p><strong>📊 访谈进度</strong></p>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 0%;"></div>
                    </div>
                    <p style="text-align: center; margin: 5px 0 0 0;">准备开始访谈...</p>
                </div>
                """)

                with gr.Row(elem_id="wechat_input_bar"):
                    msg = gr.Textbox(
                        label="你的回答",
                        placeholder="请输入你的回答…",
                        scale=6,
                        show_label=False,
                        lines=2,
                        max_lines=5
                    )
                    submit_btn = gr.Button("发送", variant="primary", scale=1, elem_id="wechat_send_btn")

                with gr.Row(elem_id="wechat_action_bar"):
                    undo_btn = gr.Button("↩️ 撤回", variant="secondary", scale=1)
                    skip_btn = gr.Button("⏭️ 跳过此题", variant="secondary", scale=1)
                    refresh_btn = gr.Button("🔄 重新开始", variant="secondary", scale=1)

            with gr.Column(scale=1, elem_id="wechat_sidebar"):
                # 侧边栏 - 使用说明和统计
                gr.Markdown("""
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

                # 实时统计（如果可用）
                stats_display = gr.Markdown("""
                ### 📊 实时统计

                *访谈开始后显示统计*
                """)
        
        # 事件处理函数
        def init_handler():
            """初始化处理器 - 延迟加载模式，快速返回欢迎页面"""
            handler = WebInterviewHandler()
            history, _ = handler.lazy_initialize()  # 使用延迟初始化
            return handler, history
        
        def respond(user_input, history, handler):
            """处理用户输入"""
            if handler is None:
                handler = WebInterviewHandler()
            
            new_history, clear_input, input_update = handler.process_message(user_input, history)
            return new_history, clear_input, input_update, handler

        def undo_action(history, handler):
            """撤回最近一次操作"""
            if handler is None:
                return history, "", gr.update(), handler
            new_history, restored_input, input_update = handler.undo_last(history)
            return new_history, restored_input, input_update, handler
        
        def skip_question(history, handler):
            """跳过当前问题"""
            if handler is None or not handler._initialized:
                return history, handler, gr.update()

            new_history, clear_input, input_update = handler.skip_round(history)
            return new_history, handler, input_update
        
        def new_interview():
            """开始新访谈"""
            handler = WebInterviewHandler()
            history, _ = handler.lazy_initialize()  # 使用延迟初始化
            return handler, history, gr.update(interactive=True)
        
        # 页面加载时初始化
        demo.load(
            init_handler,
            outputs=[handler_state, chatbot]
        )
        
        # 绑定事件
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
    
    return demo


def start_web_server(share: bool = None):
    """
    启动Web服务器
    
    Args:
        share: 是否生成公网链接（默认使用配置）
    """
    if not GRADIO_AVAILABLE:
        logger.error("无法启动Web服务：缺少 gradio 库")
        print("❌ 无法启动 Web 版：缺少 gradio 库。请先运行 pip install gradio qrcode[pil]")
        return
    
    demo = create_web_interface()
    if not demo:
        return
    
    local_ip = get_local_ip()
    port = WEB_CONFIG.port
    url = f"http://{local_ip}:{port}"
    should_share = share if share is not None else WEB_CONFIG.share
    
    print("\n" + "=" * 50)
    print(f"🚀 Web 服务器即将启动！")
    print(f"📍 局域网地址：{url}")
    if should_share:
        print("🌐 正在生成公网链接，请稍候...")
    print("=" * 50 + "\n")
    
    try:
        app, local_url, share_url = demo.launch(
            server_name=WEB_CONFIG.host,
            server_port=port,
            share=should_share,
            prevent_thread_lock=True
        )
        
        # 确定最终URL
        final_url = share_url if share_url else url
        
        print("\n" + "=" * 50)
        if share_url:
            print(f"✅ 公网链接已生成：{share_url}")
            print("📱 任何人都可以扫描下方二维码访问（无需同一WiFi）")
        else:
            print(f"📍 局域网地址：{url}")
            print("📱 请确保手机与电脑在同一WiFi下")
        print("=" * 50 + "\n")
        
        # 生成二维码
        try:
            qr = qrcode.QRCode()
            qr.add_data(final_url)
            qr.print_ascii()
            
            # 保存二维码图片
            img = qrcode.make(final_url)
            img.save("access_code.png")
            print(f"\n✅ 已生成二维码图片：access_code.png")
        except Exception as e:
            logger.warning(f"生成二维码失败: {e}")
        
        logger.info(f"Web服务器已启动 - {final_url}")
        
        # 保持运行
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n服务已停止。")
            logger.info("Web服务器已停止")
    
    except Exception as e:
        logger.error(f"启动Web服务器失败: {e}")
        print(f"❌ 启动失败: {e}")


def check_gradio_available() -> bool:
    """检查Gradio是否可用"""
    return GRADIO_AVAILABLE
