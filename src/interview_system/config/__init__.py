"""配置包。

提供全局 Settings 实例，作为应用配置的统一入口。
"""

from __future__ import annotations

from interview_system.config.settings import Settings

settings = Settings()

__all__ = ["Settings", "settings"]
