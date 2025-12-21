#!/usr/bin/env python3
# coding: utf-8
"""
Web 启动入口：用于替代根目录脚本 `web_server.py`。

用法：
  python -m interview_system.app.web
"""

from interview_system.common.config import ensure_dirs
from interview_system.ui.web_ui import start_web_server


def main():
    ensure_dirs()
    start_web_server()


if __name__ == "__main__":
    main()

