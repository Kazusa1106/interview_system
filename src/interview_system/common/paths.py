#!/usr/bin/env python3
# coding: utf-8
"""
路径工具

目的：
- 让 src-layout 下的包代码仍能以“项目根目录”为基准定位运行时文件（logs/exports/db/api_config）。
- 避免依赖 sys.path 注入的 __file__ 相对路径推断。
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


def find_project_root(start: Optional[Path] = None) -> Path:
    """
    向上查找项目根目录。

    判定标记（任一命中即视为根）：
    - .spec-workflow/ 目录
    - requirements.txt 文件
    """
    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent

    for parent in [current] + list(current.parents):
        if (parent / ".spec-workflow").exists():
            return parent
        if (parent / "requirements.txt").exists():
            return parent

    # 兜底：返回起点目录
    return current
