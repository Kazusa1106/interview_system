"""结构化日志配置（structlog）。

目标：
- 默认输出 JSON，便于采集与检索
- 支持 request_id 追踪（通过 contextvars 注入）
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog


def configure_logging(*, log_level: str = "INFO") -> None:
    """配置标准库 logging 与 structlog。"""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level, logging.INFO),
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level, logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )


def get_logger(*args: Any, **initial_values: Any) -> structlog.BoundLogger:
    """获取 structlog logger。"""
    return structlog.get_logger(*args, **initial_values)
