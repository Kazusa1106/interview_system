@echo off
chcp 65001 >nul
echo ========================================
echo   大学生五育并举访谈智能体 v2.0
echo   快速安装和测试脚本
echo ========================================
echo.

echo [步骤1] 检查Python版本...
python --version
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8-3.11
    pause
    exit /b 1
)
echo.

echo [步骤2] 安装依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo ⚠️ 依赖安装遇到问题，尝试继续...
)
echo.

echo [步骤3] 运行功能测试...
python test_features.py
if errorlevel 1 (
    echo ⚠️ 部分测试失败，但可能不影响使用
)
echo.

echo ========================================
echo   测试完成！
echo ========================================
echo.
echo 接下来您可以：
echo   1. 运行 'python main.py' 启动系统
echo   2. 选择模式 2 启动Web访谈
echo   3. 选择模式 3 启动管理后台
echo.
echo 或者直接运行：
echo   start_web.bat     - 启动访谈界面
echo   start_admin.bat   - 启动管理后台
echo.

pause
