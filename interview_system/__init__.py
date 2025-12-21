#!/usr/bin/env python3
# coding: utf-8
"""
运行期引导包（thin wrapper）

目标：
- 支持在仓库根目录直接运行：`python -m interview_system`
- 不要求先安装包或手动设置 PYTHONPATH

实现：
- 将 `src/interview_system` 追加到本包的 `__path__`，使子模块从 src 中加载。
"""

from __future__ import annotations

import os


def _append_src_package_path():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_pkg = os.path.join(repo_root, "src", "interview_system")
    if os.path.isdir(src_pkg) and src_pkg not in __path__:
        __path__.append(src_pkg)


_append_src_package_path()

