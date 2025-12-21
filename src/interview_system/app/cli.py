#!/usr/bin/env python3
# coding: utf-8
"""
CLI 启动入口：用于直接进入命令行访谈。

用法：
  python -m interview_system.app.cli
"""

from interview_system.app.main import run_cli_mode
from interview_system.common.config import ensure_dirs


def main():
    ensure_dirs()
    run_cli_mode()


if __name__ == "__main__":
    main()

