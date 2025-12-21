#!/usr/bin/env python3
# coding: utf-8
"""
管理后台启动入口：用于替代根目录脚本 `admin_server.py`。

用法：
  python -m interview_system.app.admin
"""

from interview_system.common.config import ensure_dirs
from interview_system.ui.admin_ui import start_admin_server


def main():
    ensure_dirs()
    start_admin_server()


if __name__ == "__main__":
    main()

