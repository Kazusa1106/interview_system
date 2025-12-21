# 🎓 大学生五育并举访谈智能体

基于多种大模型API的智能访谈系统，支持多人同时在线访谈。

## ✨ 特性

### 核心功能
- 🤖 **智能追问**：支持多种大模型API（DeepSeek、OpenAI、通义千问、智谱AI、百度千帆），根据回答内容生成针对性追问
- 🔄 **多轮追问**：每题最多追问3次，根据回答深度动态决定是否继续追问
- 🧠 **上下文感知**：AI追问结合用户之前的回答历史，追问更有针对性
- 👥 **多人同时访谈**：支持多用户同时进行访谈，会话隔离
- 📱 **双模式支持**：命令行交互 + Web扫码访问

### 🆕 第一阶段优化新增功能 (v2.0)
- 💾 **数据持久化**：使用SQLite数据库，所有访谈数据永久保存，服务重启不丢失
- 📊 **数据可视化**：内置Plotly图表，支持饼图、柱状图、趋势图、统计仪表盘
- 🔧 **管理后台**：全新管理界面，查看所有访谈、统计分析、数据导出
- 📈 **实时统计**：访谈进度跟踪、场景/五育分布分析、完成率统计
- 🎨 **界面优化**：渐变色设计、进度条显示、侧边栏指南、更好的用户体验
- 📑 **HTML报告**：一键生成精美的HTML统计报告

## 📁 项目结构

```
interview_system/
├── interview_system/      # 运行期引导包（支持 python -m interview_system）
├── src/
│   └── interview_system/  # 真实实现（分层结构：app/ui/core/services/data/...）
├── requirements.txt      # 依赖列表
├── requirements-lock.txt # 精确版本依赖
├── README.md             # 项目说明文档
├── CLAUDE.md             # Claude Code项目配置
├── interview_data.db     # 🆕 SQLite数据库（自动生成）
├── api_config.json       # API配置（自动生成）
├── docs/                 # 📚 文档目录
│   ├── QUICKSTART.md     # 快速开始指南
│   └── INSTALL_TEST.md   # 安装测试指南
├── scripts/              # 🔧 脚本目录
│   ├── start_web.bat     # Windows快速启动访谈界面
│   ├── start_admin.bat   # Windows快速启动管理后台
│   └── install_and_test.bat  # Windows一键安装测试
├── exports/              # 导出的访谈记录（自动生成）
└── logs/                 # 日志文件（自动生成）
```

## 🚀 快速开始

### 环境要求

- **Python版本**: 3.8 - 3.11（不支持3.12+）
- **操作系统**: Windows 10/11, macOS, Linux

### 检查Python版本

```bash
python --version
# 或
python3 --version
```

**重要**: 如果版本是3.12+，请先安装Python 3.8-3.11版本：
- [Python官方下载](https://www.python.org/downloads/)
- Windows: 可从Microsoft Store安装Python 3.11
- macOS: 使用pyenv管理多版本

### 安装步骤

#### 方法一：推荐（使用虚拟环境）

```bash
# 1. 克隆项目
git clone <项目地址>
cd interview_system

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行程序
python -m interview_system
```

### 🧪 自动化测试

```bash
pip install -r requirements-dev.txt
pytest -q
```

#### 方法二：直接安装（不推荐）

```bash
pip install -r requirements.txt
python -m interview_system
```

### 依赖冲突解决方案

如果遇到依赖冲突问题，请使用以下命令安装精确版本：

```bash
pip install -r requirements-lock.txt
```

### 选择运行模式

启动程序后，可选择以下模式：

- 输入 `1`：💻 命令行交互模式
- 输入 `2`（默认）：🌐 Web访谈模式，支持手机扫码访问
- 输入 `3`：🔧 管理后台模式（新增）

### 🆕 使用管理后台

```bash
# 方式1: 启动时选择模式3
python -m interview_system
# 然后输入 3

# 方式2: 直接运行管理后台
python -m interview_system.app.admin

# 方式3: 使用快速启动脚本（Windows）
scripts\start_admin.bat
```

管理后台功能：
- 📊 **概览仪表盘**：总访谈数、完成率、趋势图
- 📋 **会话列表**：查看所有访谈记录和详情
- 📈 **统计分析**：生成可视化统计图表
- 💾 **数据导出**：批量导出JSON、生成HTML报告
- 🔍 **详情查看**：查看每次访谈的完整对话记录

访问地址：`http://localhost:7861`

### Windows 快速启动脚本

项目提供了便捷的Windows批处理脚本：

```bash
# 一键安装和测试
scripts\install_and_test.bat

# 启动访谈界面
scripts\start_web.bat

# 启动管理后台
scripts\start_admin.bat
```

## 🔧 配置说明

### 支持的 API 提供商

| 提供商 | 推荐模型 | 获取API Key |
|--------|----------|-------------|
| **DeepSeek** | deepseek-chat | [platform.deepseek.com](https://platform.deepseek.com/) |
| **OpenAI** | gpt-3.5-turbo | [platform.openai.com](https://platform.openai.com/) |
| **通义千问** | qwen-turbo | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com/) |
| **智谱AI** | glm-4-flash | [open.bigmodel.cn](https://open.bigmodel.cn/) |
| **百度千帆** | ernie-3.5-8k | [qianfan.baidubce.com](https://qianfan.baidubce.com/) |

> ⚠️ **注意**：DeepSeek 请使用 `deepseek-chat` 模型，不要使用 `deepseek-reasoner` (R1)。R1 是推理模型，适合数学/逻辑任务，不适合对话场景，会导致追问内容异常。

### API配置流程

首次运行时，程序会引导你选择API提供商并输入密钥：

```
===== 智能追问 API 配置 =====

支持的 API 提供商：
--------------------------------------------------
  1. DeepSeek (深度求索)
  2. OpenAI (ChatGPT)
  3. 通义千问 (阿里)
  4. 智谱AI (GLM)
  5. 百度千帆 (文心一言)
  0. 跳过配置（使用预设追问）
--------------------------------------------------

请选择 API 提供商 [0-5]:
```

配置成功后会自动保存到 `api_config.json`，下次启动无需重复输入。

### 修改配置参数

编辑 `src/interview_system/common/config.py` 可调整：

```python
# 访谈配置
INTERVIEW_CONFIG = InterviewConfig(
    total_questions=6,              # 每次访谈题目数
    min_answer_length=15,           # 触发追问的最小回答长度
    max_followups_per_question=3,   # 每题最大追问次数
    max_depth_score=4               # 回答深度最高分（达到后不再追问）
)

# Web服务配置
WEB_CONFIG = WebConfig(
    port=7860,                  # 服务端口
    share=True,                 # 是否生成公网链接
    max_sessions=100            # 最大同时会话数
)
```

## 📋 访谈规则

- **题目数量**：每次随机抽取 6 题
- **覆盖要求**：确保覆盖学校、家庭、社区三场景 + 德、智、体、美、劳五育
- **追问机制**：
  - 回答过短（<15字）：自动追问，引导补充
  - 回答深度不足：AI智能追问，挖掘细节和感受
  - 每题最多追问 3 次，根据回答深度动态调整
  - 回答详细且有深度（深度分≥4）：直接进入下一题
- **AI追问特点**：
  - 结合用户之前的回答历史，避免重复追问
  - 追问与当前五育主题相关
  - 口语化表达，像朋友聊天一样自然

## 💡 使用指令

### 命令行模式

| 指令 | 说明 |
|------|------|
| `跳过` | 跳过当前问题 |
| `导出` | 导出当前访谈日志 |
| `结束` | 结束访谈 |

### Web模式

| 操作 | 说明 |
|------|------|
| 「⏭️ 跳过」按钮 | 跳过当前问题 |
| 「🔄 开始新访谈」按钮 | 重新开始一次访谈 |

> 注：Web模式下访谈结束会自动导出日志到 `exports/` 目录

## 📊 导出格式

访谈记录导出为 JSON 格式，包含：

```json
{
  "session_id": "abc12345",
  "user_name": "访谈者",
  "start_time": "2025-12-03 10:00:00",
  "end_time": "2025-12-03 10:30:00",
  "statistics": {
    "total_logs": 8,
    "scene_distribution": {"学校": 3, "家庭": 2, "社区": 3},
    "edu_distribution": {"德育": 2, "智育": 1, ...},
    "followup_distribution": {"预设追问": 1, "AI智能追问": 2}
  },
  "conversation_log": [
    {
      "timestamp": "2025-12-03 10:05:00",
      "topic": "学校-德育",
      "question_type": "核心问题",
      "question": "你认为自己在大学里学习到的最重要的品德是什么？",
      "answer": "...",
      "depth_score": 2
    }
  ]
}
```

## 🛠️ 开发说明

### 模块依赖关系

```
python -m interview_system
  └── interview_system/app/main.py (交互式入口)
        ├── interview_system/ui/web_ui.py (Web 访谈端)
        ├── interview_system/ui/admin_ui.py (管理后台)
        ├── interview_system/core/interview_engine.py (访谈引擎)
        │     ├── interview_system/core/questions.py
        │     ├── interview_system/integrations/api_client.py
        │     └── interview_system/services/session_manager.py
        │           └── interview_system/data/database.py
        └── interview_system/common/config.py + interview_system/common/logger.py
```

### 添加新的API提供商

编辑 `src/interview_system/integrations/api_client.py`，在 `API_PROVIDERS` 字典中添加：

```python
"new_provider": APIProviderConfig(
    name="新提供商名称",
    provider_id="new_provider",
    base_url="https://api.example.com/v1",  # OpenAI兼容格式
    default_model="model-name",
    api_key_name="API Key",
    models=["model-1", "model-2"],
    website="https://example.com/"
)
```

> 注：大多数国产API都兼容OpenAI接口格式，只需修改 base_url 和模型名称即可。

### 扩展题目

编辑 `src/interview_system/core/questions.py`，按以下格式添加话题：

```python
{
    "name": "场景-育类型",       # 如 "学校-德育"
    "scene": "场景",            # 学校/家庭/社区
    "edu_type": "育类型",       # 德育/智育/体育/美育/劳育
    "intro": "话题介绍",
    "questions": ["核心问题"],
    "scenarios": [],            # 情景（可选）
    "followups": ["预设追问1", "预设追问2"]
}
```

## 🆕 新功能使用指南 (v2.0)

### 数据持久化

所有访谈数据自动保存到SQLite数据库（`interview_data.db`），服务重启后数据不丢失。

**数据库包含**：
- 所有历史会话信息
- 完整的对话日志
- 统计分析数据

**备份建议**：定期备份 `interview_data.db` 文件

### 数据可视化

系统内置Plotly图表库，支持多种可视化形式：

```python
# 在管理后台中
from interview_system.reports.visualization import DataVisualizer
from interview_system.services.session_manager import get_session_manager

# 获取统计数据
stats = get_session_manager().get_statistics()

# 创建可视化图表
viz = DataVisualizer()
dashboard = viz.create_statistics_dashboard(stats)

# 生成HTML报告
viz.generate_html_report(stats, daily_stats, "report.html")
```

**支持的图表类型**：
- 饼图：场景分布、五育分布
- 柱状图：追问类型统计
- 折线图：访谈量趋势
- 仪表盘：综合统计展示

### 管理后台API

管理后台提供完整的数据管理功能：

**概览功能**：
- 实时显示总访谈数、完成率
- 最近N天趋势图
- 生成可视化统计报告

**会话管理**：
- 查看所有访谈列表
- 查看单次访谈详情
- 导出指定会话
- 批量导出所有会话

**统计分析**：
- 按日期范围筛选统计
- 场景/五育分布分析
- AI追问效果分析
- 生成HTML统计报告

### 数据导出格式

**JSON格式**（程序化处理）：
```json
{
  "session_id": "abc12345",
  "user_name": "访谈者",
  "statistics": {
    "total_logs": 8,
    "completion_rate": 100,
    "scene_distribution": {"学校": 3, "家庭": 2, "社区": 3},
    "edu_distribution": {"德育": 2, "智育": 2, ...}
  },
  "conversation_log": [...]
}
```

**HTML格式**（可视化报告）：
- 精美的图表展示
- 完整的统计信息
- 可直接在浏览器打开
- 适合分享和演示

## 📄 License

MIT License

