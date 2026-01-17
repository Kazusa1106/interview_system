#!/usr/bin/env python3
# coding: utf-8
"""
interview_system 包

采用 src-layout，将核心逻辑放入可导入的包中；根目录脚本保留为兼容入口。
"""

from __future__ import annotations

from interview_system.api.main import create_app
from interview_system.config.settings import Settings

__all__ = ["Settings", "create_app"]
