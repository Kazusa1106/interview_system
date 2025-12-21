# 🚀 快速使用指南 - 大学生五育并举访谈智能体 v2.0

## 📦 安装依赖

```bash
# 安装所有依赖（包括新增的plotly）
pip install -r requirements.txt
```

## 🎯 三种运行模式

### 1. 💻 命令行模式 - 传统交互

```bash
python -m interview_system
# 选择 1
```

适合：熟悉命令行的用户，快速单次访谈

### 2. 🌐 Web访谈模式 - 手机扫码访问（默认）

```bash
python -m interview_system
# 选择 2 或直接回车
```

特点：
- 生成二维码，手机扫码访问
- 支持多人同时访谈
- 美化的渐变色界面
- 实时进度显示
- 侧边栏使用指南

访问地址：`http://localhost:7860`

### 3. 🔧 管理后台模式 - 数据分析（新增）

```bash
python -m interview_system
# 选择 3

# 或直接运行
python -m interview_system.app.admin
```

功能：
- 📊 查看所有访谈记录
- 📈 生成统计图表
- 💾 批量导出数据
- 📑 生成HTML报告

访问地址：`http://localhost:7861`

## 🆕 新功能快速体验

### 查看数据持久化

所有访谈数据自动保存到 `interview_data.db`：

```bash
# 查看数据库文件
ls -lh interview_data.db

# 使用SQLite工具查看（可选）
sqlite3 interview_data.db
.tables  # 查看所有表
SELECT * FROM sessions LIMIT 5;  # 查看前5条会话
```

### 使用管理后台

1. **启动管理后台**
   ```bash
   python -m interview_system
   # 选择 3
   ```

2. **打开浏览器**
   访问 `http://localhost:7861`

3. **查看概览**
   - 总访谈数、完成率一目了然
   - 最近7天趋势图

4. **查看会话列表**
   - 切换到"📋 会话列表"标签
   - 点击"刷新列表"查看所有访谈
   - 复制会话ID到输入框
   - 点击"查看详情"查看完整对话

5. **生成统计报告**
   - 切换到"📊 概览"标签
   - 选择统计天数（1-30天）
   - 点击"生成统计图表"查看可视化
   - 点击"导出HTML报告"保存报告

6. **批量导出数据**
   - 切换到"🗄️ 数据管理"标签
   - 点击"导出所有会话"
   - 所有JSON文件保存到 `exports/` 目录

### 生成可视化报告

```python
# 在Python脚本中使用
from interview_system.reports.visualization import DataVisualizer
from interview_system.services.session_manager import get_session_manager

# 获取统计数据
sm = get_session_manager()
stats = sm.get_statistics()
daily_stats = sm.get_daily_statistics(7)

# 生成HTML报告
viz = DataVisualizer()
report_path = viz.generate_html_report(
    statistics=stats,
    daily_stats=daily_stats,
    output_path="exports/my_report.html"
)

print(f"报告已生成: {report_path}")
```

## 📊 数据分析示例

### 查询数据库

```python
from interview_system.data.database import get_database

db = get_database()

# 获取总会话数
count = db.get_session_count()
print(f"总访谈数: {count}")

# 获取最近7天统计
stats = db.get_statistics_by_date_range(
    start_date="2025-12-10 00:00:00",
    end_date="2025-12-17 23:59:59"
)
print(f"完成率: {stats['completion_rate']}%")

# 获取所有会话
sessions = db.get_all_sessions(limit=10)
for session in sessions:
    print(f"{session['session_id']}: {session['user_name']}")
```

### 导出自定义格式

```python
from interview_system.services.session_manager import get_session_manager
import json

# 获取会话
sm = get_session_manager()
session = sm.get_session("abc12345")

# 自定义导出
custom_data = {
    "user": session.user_name,
    "date": session.start_time,
    "answers": [
        {
            "topic": log["topic"],
            "answer": log["answer"]
        }
        for log in session.conversation_log
    ]
}

# 保存
with open("custom_export.json", "w", encoding="utf-8") as f:
    json.dump(custom_data, f, ensure_ascii=False, indent=2)
```

## 🎨 Web界面新功能

### 访谈界面优化

- **渐变色标题**：更美观的视觉效果
- **进度条**：实时显示访谈进度
- **侧边栏指南**：提供使用说明和小贴士
- **机器人头像**：AI回答带机器人图标
- **响应式布局**：适配不同屏幕尺寸

### 实时统计（即将推出）

访谈过程中实时显示：
- 当前进度（X/6题）
- 已覆盖场景
- 已覆盖五育维度

## 🔧 常见问题

### Q: 数据库文件在哪里？
A: 项目根目录下的 `interview_data.db`

### Q: 如何备份数据？
A: 直接复制 `interview_data.db` 文件即可

### Q: 管理后台和访谈界面能同时运行吗？
A: 可以！它们使用不同的端口（7860和7861）

### Q: 如何清除所有数据？
A: 删除 `interview_data.db` 文件，系统会自动创建新的空数据库

### Q: plotly图表无法显示？
A: 确保已安装 plotly: `pip install plotly`

### Q: 如何自定义统计时间范围？
A: 在管理后台的"概览"标签中，使用滑块选择天数（1-30天）

## 📝 最佳实践

### 数据管理

1. **定期备份**
   ```bash
   # 每周备份数据库
   cp interview_data.db backups/interview_$(date +%Y%m%d).db
   ```

2. **批量导出**
   - 使用管理后台的"批量导出"功能
   - 定期生成HTML报告存档

3. **数据清理**
   - 测试数据可通过管理后台删除
   - 或直接操作数据库：
   ```python
   from interview_system.data.database import get_database
   db = get_database()
   db.delete_session("test_session_id")
   ```

### 性能优化

- 访谈数据超过1000条时，建议定期清理测试数据
- HTML报告生成可能需要几秒钟，请耐心等待
- 管理后台建议仅管理员访问，不对外开放

## 🎉 开始使用

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动访谈界面
python -m interview_system.app.web

# 3. 在另一个终端启动管理后台
python -m interview_system.app.admin

# 4. 开始访谈并在管理后台查看数据！
```

## 📞 获取帮助

- 查看 README.md 了解详细信息
- 查看 CLAUDE.md 了解项目架构
- 检查 logs/ 目录下的日志文件

---

🎓 大学生五育并举访谈智能体 v2.0
💾 现在支持数据持久化 | 📊 内置数据可视化 | 🔧 全新管理后台
