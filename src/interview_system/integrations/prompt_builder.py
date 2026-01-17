#!/usr/bin/env python3
# coding: utf-8
"""Prompt Builder - Constructs prompts for followup generation"""

from typing import Optional

from interview_system.integrations.prompt_templates import (
    FOLLOWUP_USER_TEMPLATE,
    TONE_MAP,
)


class PromptBuilder:
    """Builds prompts for followup question generation"""

    @staticmethod
    def build_followup_prompt(
        answer: str, topic: dict, conversation_log: list = None
    ) -> str:
        """
        Build prompt for followup generation

        Args:
            answer: User's answer
            topic: Current topic dict
            conversation_log: Conversation history

        Returns:
            Formatted prompt string
        """
        topic_name = topic.get("name", "")
        scene, edu_type = topic_name.split("-", 1) if "-" in topic_name else ("", "")
        original_question = topic.get("questions", [""])[0]

        history_context = PromptBuilder._build_history_context(
            conversation_log, topic_name
        )
        tone_guide = TONE_MAP.get(edu_type, "专业而亲和，像记者采访一样")

        return FOLLOWUP_USER_TEMPLATE.format(
            edu_type=edu_type,
            scene=scene,
            original_question=original_question,
            history_context=history_context,
            answer=answer,
            tone_guide=tone_guide,
        )

    @staticmethod
    def _build_history_context(
        conversation_log: Optional[list], topic_name: str
    ) -> str:
        """Build conversation history context"""
        if not conversation_log:
            return ""

        topic_logs = [log for log in conversation_log if log.get("topic") == topic_name]
        if not topic_logs:
            return ""

        history_parts = []
        for log in topic_logs:
            q_type = log.get("question_type", "")
            q_text = log.get("question", "")
            ans = log.get("answer", "")

            if "核心" in q_type:
                history_parts.append(f"【核心问题】{q_text}\n【回答】{ans}")
            elif "追问" in q_type:
                history_parts.append(
                    f"【追问{len(history_parts)}】{q_text}\n【回答】{ans}"
                )

        if history_parts:
            return "\n\n【对话历史】\n" + "\n\n".join(history_parts)
        return ""
