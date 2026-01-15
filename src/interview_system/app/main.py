
#!/usr/bin/env python3
# coding: utf-8
"""
大学生五育并举访谈智能体（重构版）

主入口文件 - 整合所有模块，提供统一的启动入口

特点：
- 模块化设计，代码结构清晰
- 配置与代码分离
- 统一日志输出
- API调用失败时自动重试
- 支持多人同时访谈
- 支持命令行和Web两种模式
"""

from interview_system.common.logger import get_logger
from interview_system.common.config import ensure_dirs
from interview_system.app.api_config_wizard import APIConfigWizard
from interview_system.app.cli_runner import CLIInterviewRunner
from interview_system.ui.web_ui import start_web_server, check_gradio_available

log = get_logger(__name__)

# 尝试导入管理后台（可选）
try:
    from interview_system.ui.admin_ui import start_admin_server
    ADMIN_AVAILABLE = True
except ImportError:
    ADMIN_AVAILABLE = False


def setup_api_interactive():
    """Interactive API configuration"""
    wizard = APIConfigWizard()
    wizard.run()


def run_cli_mode():
    """Run CLI interview mode"""
    runner = CLIInterviewRunner()
    runner.run()


def run_web_mode():
    """运行Web模式"""
    if not check_gradio_available():
        log.error("无法启动Web模式：缺少gradio库")
        return

    log.info("启动Web访谈服务器")
    start_web_server()


def run_admin_mode():
    """运行管理后台模式"""
    if not ADMIN_AVAILABLE:
        log.error("无法启动管理后台：缺少必要模块")
        return

    log.info("启动管理后台服务器")
    start_admin_server()


def main():
    """主入口函数"""
    log.info("应用启动")
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "🎓 大学生五育并举访谈智能体".center(48) + "║")
    print("║" + " " * 58 + "║")
    print("║" + "探索德·智·体·美·劳，记录你的成长故事".center(42) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")

    ensure_dirs()
    log.info("工作目录已就绪")

    setup_api_interactive()
    log.info("API配置已完成")

    print("\n" + "─" * 50)
    print("请选择启动模式：")
    print("  1. 💻 命令行模式   - 在终端中进行访谈")
    print("  2. 🌐 Web访谈模式  - 生成网页链接，支持手机访问")
    print("  3. 🔧 管理后台模式 - 查看数据、统计分析")
    print("─" * 50)
    mode = input("请输入选项 [默认2]: ").strip()

    log.info("用户选择启动模式", extra={"mode": mode or "2"})

    if mode == "1":
        log.info("进入命令行模式")
        run_cli_mode()
    elif mode == "3":
        log.info("进入管理后台模式")
        run_admin_mode()
    else:
        log.info("进入Web访谈模式")
        run_web_mode()


def run_web():
    """Direct entry point for web mode (used by CLI script)"""
    ensure_dirs()
    log.info("工作目录已就绪")
    setup_api_interactive()
    log.info("API配置已完成")
    run_web_mode()


if __name__ == "__main__":
    main()
