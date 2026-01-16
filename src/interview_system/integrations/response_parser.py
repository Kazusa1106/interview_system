#!/usr/bin/env python3
# coding: utf-8
"""Response Parser - Extracts and validates followup questions from API responses"""

from typing import Optional

import interview_system.common.logger as logger


class ResponseParser:
    """Parses and validates API responses for followup questions"""

    @staticmethod
    def extract_followup(response, topic: dict, duration: float) -> Optional[str]:
        """
        Extract followup question from API response

        Args:
            response: API response object
            topic: Current topic dict
            duration: API call duration

        Returns:
            Extracted followup question or None
        """
        if not response or not response.choices:
            logger.log_api_call("generate_followup", True, duration, "API响应无choices")
            return None

        choice = response.choices[0]
        follow_question = ResponseParser._extract_content(choice)

        if not follow_question:
            logger.log_api_call("generate_followup", True, duration, "API返回内容为空")
            return None

        follow_question = ResponseParser._clean_followup(follow_question)

        if not ResponseParser._validate_followup(follow_question, topic):
            logger.log_api_call(
                "generate_followup",
                True,
                duration,
                f"生成内容不符合要求: {follow_question[:50]}",
            )
            return None

        logger.log_api_call("generate_followup", True, duration)
        logger.debug(f"AI生成追问成功: {follow_question}")
        return follow_question

    @staticmethod
    def _extract_content(choice) -> str:
        """Extract content from choice"""
        if not hasattr(choice, "message") or not choice.message:
            return ""

        if hasattr(choice.message, "content") and choice.message.content:
            return choice.message.content.strip()

        if hasattr(choice.message, "reasoning_content"):
            return ResponseParser._extract_from_reasoning(
                choice.message.reasoning_content
            )

        return ""

    @staticmethod
    def _extract_from_reasoning(reasoning: str) -> str:
        """Extract conclusion from reasoning content (DeepSeek R1)"""
        if not reasoning:
            return ""

        lines = reasoning.strip().split("\n")
        for line in reversed(lines):
            line = line.strip()
            if line and len(line) >= 5 and not line.startswith(("<", "【", "```")):
                return line

        return ""

    @staticmethod
    def _clean_followup(text: str) -> str:
        """Clean followup text"""
        prefixes = ["追问：", "追问:", "问：", "问:", "**追问**：", "**追问**:"]
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix) :].strip()

        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1].strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1].strip()

        return text

    @staticmethod
    def _validate_followup(followup: str, topic: dict) -> bool:
        """Validate followup quality"""
        if not followup or len(followup) < 5:
            return False

        preset_follows = topic.get("followups", [])
        original_question = topic.get("questions", [""])[0]

        return followup not in original_question and followup not in preset_follows
