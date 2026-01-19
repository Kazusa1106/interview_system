#!/usr/bin/env python3
# coding: utf-8
"""
配置文件 - 大学生五育并举访谈智能体

src-layout 下的包配置实现。运行期路径统一以项目根目录为基准。
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, field_validator

from interview_system.common.paths import find_project_root

load_dotenv()


# ----------------------------
# 路径配置（以项目根目录为基准）
# ----------------------------
BASE_DIR = str(find_project_root(Path(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

DEFAULT_DEPTH_KEYWORDS: list[str] = [
    "例子",
    "经历",
    "具体",
    "当时",
    "那次",
    "有一次",
    "记得",
    "感受",
    "感觉",
    "觉得",
    "认为",
    "反思",
    "思考",
    "意识到",
    "影响",
    "收获",
    "学到",
    "成长",
    "改变",
    "进步",
    "提升",
    "因为",
    "所以",
    "后来",
    "结果",
    "过程",
    "细节",
    "开心",
    "难过",
    "紧张",
    "兴奋",
    "感动",
    "印象深刻",
    "帮助",
    "支持",
    "合作",
    "沟通",
    "交流",
    "一起",
]

DEFAULT_COMMON_KEYWORDS: list[str] = [
    "时间",
    "方法",
    "计划",
    "目标",
    "团队",
    "互动",
    "冲突",
    "经验",
    "学习",
    "情绪",
    "家人",
    "朋友",
    "老师",
    "同学",
    "邻居",
]


class InterviewKeywordsConfig(BaseModel):
    depth_keywords: list[str]
    common_keywords: list[str]

    @field_validator("depth_keywords", "common_keywords")
    @classmethod
    def _validate_keywords(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("关键词列表不能为空")
        normalized: list[str] = []
        for item in value:
            text = str(item).strip()
            if not text:
                raise ValueError("关键词不能为空字符串")
            normalized.append(text)
        return normalized


def _strip_yaml_comment(line: str) -> str:
    if "#" not in line:
        return line
    head, _sep, _tail = line.partition("#")
    return head


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """
    解析一个极简 YAML 子集：
    - 顶层 key:
    - 子级为 '- value' 列表
    - 或顶层 key: value 标量
    """
    data: dict[str, Any] = {}
    current_key: str | None = None

    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = _strip_yaml_comment(raw_line).rstrip()
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))
        content = line.lstrip(" ")

        if indent == 0 and content.endswith(":"):
            current_key = content[:-1].strip()
            if not current_key:
                raise ValueError(f"YAML 第 {lineno} 行：空 key")
            data[current_key] = []
            continue

        if indent == 0 and ":" in content:
            key, _sep, value = content.partition(":")
            key = key.strip()
            value = value.strip()
            if not key:
                raise ValueError(f"YAML 第 {lineno} 行：空 key")
            current_key = None
            data[key] = value
            continue

        if content.startswith("- "):
            if current_key is None:
                raise ValueError(f"YAML 第 {lineno} 行：列表项缺少上级 key")
            value = content[2:].strip()
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1].strip()
            data[current_key].append(value)
            continue

        raise ValueError(f"YAML 第 {lineno} 行：不支持的语法")

    return data


def _resolve_interview_keywords_path() -> Path | None:
    env_path = os.getenv("INTERVIEW_KEYWORDS_PATH")
    if env_path:
        return Path(env_path).expanduser()

    base = Path(BASE_DIR)
    candidates = [
        base / "config" / "interview_keywords.yaml",
        base / "config" / "interview_keywords.yml",
        base / "interview_keywords.yaml",
        base / "interview_keywords.yml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


@lru_cache(maxsize=1)
def load_interview_keywords() -> InterviewKeywordsConfig:
    path = _resolve_interview_keywords_path()
    if path is None:
        return InterviewKeywordsConfig(
            depth_keywords=DEFAULT_DEPTH_KEYWORDS,
            common_keywords=DEFAULT_COMMON_KEYWORDS,
        )

    raw = path.read_text(encoding="utf-8")
    data = _parse_simple_yaml(raw)
    try:
        return InterviewKeywordsConfig.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"关键词配置无效: {path}") from exc


def _default_depth_keywords() -> list[str]:
    return list(load_interview_keywords().depth_keywords)


def _default_common_keywords() -> list[str]:
    return list(load_interview_keywords().common_keywords)


# ----------------------------
# 访谈系统配置
# ----------------------------
@dataclass
class InterviewConfig:
    """访谈系统配置"""

    total_questions: int = 6  # 每次访谈的题目数量
    min_answer_length: int = 15  # 触发追问的最小回答长度
    max_followups_per_question: int = 3  # 每题最大追问次数
    max_depth_score: int = 4  # 回答深度最高分

    depth_keywords: list[str] = field(default_factory=_default_depth_keywords)
    common_keywords: list[str] = field(default_factory=_default_common_keywords)


# ----------------------------
# Web 服务配置
# ----------------------------
@dataclass
class WebConfig:
    """Web服务配置"""

    host: str = os.getenv("WEB_HOST", "127.0.0.1")
    port: int = int(os.getenv("WEB_PORT", "7860"))
    share: bool = os.getenv("WEB_SHARE", "false").lower() == "true"
    title: str = "大学生五育并举访谈智能体"
    max_sessions: int = 100
    session_timeout: int = 3600


# ----------------------------
# 日志配置
# ----------------------------
@dataclass
class LogConfig:
    """日志配置"""

    level: str = os.getenv("LOG_LEVEL", "INFO")
    log_to_file: bool = True
    log_to_console: bool = True
    log_format: str = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    max_file_size: int = 10 * 1024 * 1024
    backup_count: int = 5


INTERVIEW_CONFIG = InterviewConfig()
WEB_CONFIG = WebConfig()
LOG_CONFIG = LogConfig()


def ensure_dirs():
    """确保必要的目录存在"""
    for dir_path in [LOG_DIR, EXPORT_DIR]:
        os.makedirs(dir_path, exist_ok=True)
