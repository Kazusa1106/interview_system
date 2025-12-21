@echo off
chcp 65001 >nul
echo ========================================
echo   启动管理后台
echo ========================================
echo.
echo 启动中...
echo 访问地址: http://localhost:7861
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python -c "import sys; sys.exit(0) if __name__ == '__main__' else sys.exit(1)" >nul 2>&1
if errorlevel 1 (
    echo ❌ Python环境异常
    pause
    exit /b 1
)

python -m interview_system.app.admin
