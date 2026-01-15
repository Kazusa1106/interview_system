#!/usr/bin/env python3
# coding: utf-8
"""
配置文件 - 大学生五育并举访谈智能体

src-layout 下的包配置实现。运行期路径统一以项目根目录为基准。
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

from interview_system.common.paths import find_project_root

load_dotenv()


# ----------------------------
# 路径配置（以项目根目录为基准）
# ----------------------------
BASE_DIR = str(find_project_root(Path(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")


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

    depth_keywords: list = field(default_factory=lambda: [
        "例子", "经历", "具体", "当时", "那次", "有一次", "记得",
        "感受", "感觉", "觉得", "认为", "反思", "思考", "意识到",
        "影响", "收获", "学到", "成长", "改变", "进步", "提升",
        "因为", "所以", "后来", "结果", "过程", "细节",
        "开心", "难过", "紧张", "兴奋", "感动", "印象深刻",
        "帮助", "支持", "合作", "沟通", "交流", "一起"
    ])

    common_keywords: list = field(default_factory=lambda: [
        "时间", "方法", "计划", "目标", "团队",
        "互动", "冲突", "经验", "学习", "情绪",
        "家人", "朋友", "老师", "同学", "邻居"
    ])


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

