#!/usr/bin/env python3
# coding: utf-8
"""CLI Interview Runner - Command-line interview orchestration"""

from typing import Optional

from interview_system.common.logger import get_logger
from interview_system.core.interview_engine import create_interview, QuestionResult
from interview_system.services.session_manager import get_session_manager, InterviewSession
from interview_system.integrations.api_helpers import is_api_available

log = get_logger(__name__)


class CLIInterviewRunner:
    """Command-line interview runner"""

    def __init__(self):
        self.session: Optional[InterviewSession] = None
        self.engine = None

    def run(self):
        """Run CLI interview session"""
        self._show_instructions()
        user_name = self._get_user_name()
        self._create_session(user_name)
        self._show_welcome()
        self._run_interview_loop()
        self._show_summary()

    def _show_instructions(self):
        """Display operation instructions"""
        print("\n" + "─" * 50)
        print("📋 操作提示")
        print("─" * 50)
        print("  · 输入 '跳过' - 跳过当前问题")
        print("  · 输入 '导出' - 保存访谈记录")
        print("  · 输入 '结束' - 结束本次访谈")
        print("─" * 50)

    def _get_user_name(self) -> Optional[str]:
        """Get user name from input"""
        return input("\n请输入你的称呼（直接回车跳过）：").strip() or None

    def _create_session(self, user_name: Optional[str]):
        """Create interview session"""
        log.info("创建CLI访谈会话", extra={"user_name": user_name})
        self.session, self.engine = create_interview(user_name)

    def _show_welcome(self):
        """Display welcome message"""
        print("\n" + "═" * 50)
        print("👋 你好，欢迎参加本次访谈！")
        print("═" * 50)
        print("\n接下来我会向你提出 6 个问题，")
        print("话题涉及你在学校、家庭和社区中的经历与感受。")
        print("\n💬 请放松心情，用自己的话分享真实想法。")
        print("\n准备好了吗？让我们开始吧！\n")
        print(self.engine.get_current_question())

    def _run_interview_loop(self):
        """Main interview loop"""
        while not self.session.is_finished:
            answer = input("\n你的回答：").strip()

            if self._handle_command(answer):
                continue

            if not answer:
                print("请给出一个回答，或输入 '跳过' 跳过当前题、'结束' 结束访谈。")
                continue

            self._process_answer(answer)

    def _handle_command(self, answer: str) -> bool:
        """
        Handle special commands

        Returns:
            True if command was handled
        """
        cmd = answer.lower()

        if cmd in ("结束", "exit", "quit", "结束访谈"):
            self._end_interview()
            return True

        if cmd == "导出":
            self._export_session()
            return True

        if cmd in ("跳过", "不想说", "不愿意", "/跳过"):
            self._skip_question()
            return True

        return False

    def _end_interview(self):
        """End interview manually"""
        log.info("用户手动结束访谈", extra={"session_id": self.session.session_id})
        self.session.is_finished = True

    def _export_session(self):
        """Export session to file"""
        path = get_session_manager().export_session(self.session.session_id)
        if path:
            log.info("用户导出访谈记录", extra={
                "session_id": self.session.session_id,
                "path": path
            })
            print(f"JSON 日志已导出至：{path}")
        else:
            log.warning("导出访谈记录失败", extra={"session_id": self.session.session_id})
            print("导出失败")
        print("你可以继续回答，或输入 '结束' 退出。")

    def _skip_question(self):
        """Skip current question"""
        idx = self.session.current_question_idx
        log.info("用户跳过问题", extra={
            "session_id": self.session.session_id,
            "question_idx": idx
        })
        print(f"\n⏭️ 好的，已跳过第 {idx + 1} 题")
        result = self.engine.skip_question()

        if not result.is_finished:
            print(f"\n{result.next_question}")

    def _process_answer(self, answer: str):
        """Process user answer"""
        result = self.engine.process_answer(answer)

        if result.need_followup:
            self._handle_followup(result)
            return

        if result.is_finished:
            return

        if result.next_question:
            print(f"\n{result.next_question}")

    def _handle_followup(self, result: QuestionResult):
        """Handle followup question"""
        prefix = "💡 " if result.is_ai_generated else "📝 "
        print(f"\n{prefix}{result.followup_question}")

        followup_answer = input("\n你的补充回答：").strip()
        if followup_answer and followup_answer.lower() not in ("跳过", "/跳过"):
            result = self.engine.process_answer(followup_answer)

            if result.is_finished:
                return

            if result.next_question:
                print(f"\n{result.next_question}")

    def _show_summary(self):
        """Display interview summary"""
        log.info("访谈会话结束", extra={"session_id": self.session.session_id})
        print("\n" + "═" * 50)
        print("🎉 访谈结束！感谢你的参与！")
        print("═" * 50)

        summary = self.engine.get_summary()
        stats = summary.get("statistics", {})

        log.info("访谈统计", extra={
            "session_id": self.session.session_id,
            "total_logs": stats.get('total_logs', 0),
            "scene_distribution": stats.get('scene_distribution', {}),
            "edu_distribution": stats.get('edu_distribution', {})
        })

        self._display_statistics(stats)
        self._auto_export()
        self._show_goodbye()

    def _display_statistics(self, stats: dict):
        """Display statistics"""
        print("\n📊 本次访谈统计：")
        print("─" * 30)
        print(f"  📝 回答记录：{stats.get('total_logs', 0)} 条")

        scene_dist = stats.get('scene_distribution', {})
        if scene_dist:
            scenes = '、'.join([f"{k}({v})" for k, v in scene_dist.items()])
            print(f"  🏠 场景覆盖：{scenes}")

        edu_dist = stats.get('edu_distribution', {})
        if edu_dist:
            edus = '、'.join([f"{k}({v})" for k, v in edu_dist.items()])
            print(f"  📚 五育覆盖：{edus}")

        print("─" * 30)

    def _auto_export(self):
        """Auto-export session"""
        path = get_session_manager().export_session(self.session.session_id)
        if path:
            log.info("自动导出访谈记录", extra={
                "session_id": self.session.session_id,
                "path": path
            })
            print(f"\n💾 访谈记录已自动保存至：")
            print(f"   {path}")
        else:
            log.error("自动导出访谈记录失败", extra={"session_id": self.session.session_id})
            print("\n⚠️ 访谈记录导出失败")

    def _show_goodbye(self):
        """Display goodbye message"""
        print("\n" + "═" * 50)
        print("✨ 感谢参与访谈，祝你学习进步！")
        print("═" * 50 + "\n")
