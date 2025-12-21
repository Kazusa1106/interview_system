import os
from pathlib import Path

import pytest


@pytest.fixture()
def isolated_runtime(tmp_path, monkeypatch):
    """
    隔离测试运行时副作用：
    - 将 SQLite DB 指向临时目录，避免污染仓库内的 interview_data.db
    - 将 exports/logs 指向临时目录，避免生成导出文件与日志文件
    - 重置单例（Database/SessionManager），确保每个测试用例独立
    """
    # 延迟导入，避免在 monkeypatch 前触发单例初始化
    import interview_system.common.config as config_module
    import interview_system.data.database as database_module
    import interview_system.services.session_manager as session_manager_module

    exports_dir = tmp_path / "exports"
    logs_dir = tmp_path / "logs"
    exports_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    # 1) 重定向 config 的运行目录
    monkeypatch.setattr(config_module, "EXPORT_DIR", str(exports_dir), raising=False)
    monkeypatch.setattr(config_module, "LOG_DIR", str(logs_dir), raising=False)

    # 2) 重定向 session_manager 中导入的 EXPORT_DIR 常量引用
    monkeypatch.setattr(session_manager_module, "EXPORT_DIR", str(exports_dir), raising=False)

    # 3) 重定向数据库路径（Database.__init__ 会读取 module-level DB_PATH）
    db_path = tmp_path / "interview_data.db"
    monkeypatch.setattr(database_module, "DB_PATH", str(db_path), raising=True)

    # 4) 重置单例，避免跨测试共享状态
    database_module._db_instance = None
    database_module.Database._instance = None

    session_manager_module.SessionManager._instance = None

    # 5) 运行期环境变量（避免外部网络/统计）
    monkeypatch.setenv("GRADIO_ANALYTICS_ENABLED", "False")

    yield {
        "tmp_path": tmp_path,
        "exports_dir": exports_dir,
        "logs_dir": logs_dir,
        "db_path": db_path,
    }
