# 自动化测试指南

本项目当前使用 `pytest` 作为自动化测试框架，测试用例位于 `tests/` 目录。

## 1. 安装测试依赖

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 2. 运行测试

在项目根目录执行：

```bash
pytest
```

说明：

- 测试默认会将 SQLite 数据库、`exports/`、`logs/` 重定向到临时目录，避免污染你的真实运行数据。
- 若你的环境不允许写入（例如只读沙箱），请在本机正常环境下运行测试。

当前测试覆盖重点（会随功能演进而扩展）：

- `InterviewEngine.skip_round`：追问态跳过推进与日志写入
- `Database.delete_last_conversation_logs`：按会话删除尾部 N 条日志
- `Database.rollback_session_state` / `SessionManager.rollback_session`：撤回相关的原子回滚与状态恢复
