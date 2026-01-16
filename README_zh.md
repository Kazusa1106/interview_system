<div align="center">

# 访谈系统

**AI驱动的五育并举教育评估访谈平台**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

[快速开始](#快速开始) • [功能特性](#功能特性) • [配置说明](#配置说明) • [使用指南](#使用指南)

[English](README.md) | **中文**

</div>

---

## 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [安装说明](#安装说明)
- [配置说明](#配置说明)
- [使用指南](#使用指南)
- [API服务商](#api服务商)
- [项目结构](#项目结构)
- [开发指南](#开发指南)
- [许可证](#许可证)

---

## 功能特性

<table>
<tr>
<td width="50%">

**核心能力**
- 多LLM支持 (DeepSeek、OpenAI、通义千问、智谱GLM、文心一言)
- 动态追问 (每题最多3次)
- 上下文感知AI响应
- 多用户并发会话
- CLI + Web双界面

</td>
<td width="50%">

**v2.0新特性**
- SQLite持久化存储
- Plotly可视化图表
- 管理后台
- 实时统计分析
- HTML报告生成

</td>
</tr>
</table>

---

## 快速开始

### 环境要求

- **Python**: 3.10+ (支持 3.10、3.11、3.12、3.13)
- **操作系统**: Windows 10/11、macOS、Linux

### 检查Python版本

```bash
python --version  # 必须是 3.10+
```

### 安装与运行

```bash
# 克隆仓库
git clone https://github.com/username/interview_system.git
cd interview_system

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/macOS

# 安装为可编辑模式（必需）
pip install -e .

# 运行（三选一）
interview          # 交互式模式选择
interview-web      # 直接启动Web模式
interview-admin    # 管理后台
```

---

## 安装说明

<details>
<summary><b>依赖冲突处理</b></summary>

如遇依赖冲突，使用锁定版本：

```bash
pip install -r requirements-lock.txt
```

</details>

### 运行测试

```bash
pip install -e ".[dev]"
pytest -q
```

---

## 配置说明

### API服务商

| 服务商 | 模型 | API密钥获取 |
|--------|------|-------------|
| **DeepSeek** | `deepseek-chat` | [platform.deepseek.com](https://platform.deepseek.com/) |
| **OpenAI** | `gpt-3.5-turbo` | [platform.openai.com](https://platform.openai.com/) |
| **通义千问** | `qwen-turbo` | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com/) |
| **智谱GLM** | `glm-4-flash` | [open.bigmodel.cn](https://open.bigmodel.cn/) |
| **文心一言** | `ernie-3.5-8k` | [qianfan.baidubce.com](https://qianfan.baidubce.com/) |

> 推荐使用 `deepseek-chat`。R1模型仅适用于数学/逻辑推理。

### 环境变量配置

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env`：

```ini
# API配置
API_PROVIDER=deepseek
API_KEY=your_api_key_here
API_MODEL=deepseek-chat

# Web服务器
WEB_HOST=127.0.0.1
WEB_PORT=7860
WEB_SHARE=false
```

**优先级**: 环境变量 > `.env`文件 > `api_config.json`（已废弃）

### 安全须知

- **禁止提交** `.env` 或 `api_config.json`
- 生产环境使用系统环境变量
- 定期轮换API密钥
- `.gitignore` 已默认排除敏感文件

<details>
<summary><b>自定义配置</b></summary>

编辑 `src/interview_system/common/config.py`：

```python
INTERVIEW_CONFIG = InterviewConfig(
    total_questions=6,              # 每次访谈题目数
    min_answer_length=15,           # 触发追问的最小回答长度
    max_followups_per_question=3,   # 每题最大追问次数
    max_depth_score=4               # 最大深度分（达到后跳过追问）
)

WEB_CONFIG = WebConfig(
    host="127.0.0.1",
    port=7860,
    share=False,
    max_sessions=100
)
```

</details>

---

## 使用指南

### 运行模式

```bash
interview  # 启动后选择模式
```

选择模式：
- `1`: CLI交互模式
- `2`: Web模式（默认）- 支持手机扫码访问
- `3`: 管理后台

### 管理后台

```bash
# 方式一：启动时选择模式3
interview

# 方式二：直接启动
interview-admin

# 方式三：Windows脚本
scripts\start_admin.bat
```

**访问地址**: `http://localhost:7861`

**功能模块**:
- 概览面板（访谈总数、完成率、趋势图）
- 会话列表（查看所有访谈及详情）
- 统计分析（可视化图表、分布统计）
- 数据导出（JSON批量导出、HTML报告）
- 详情查看（完整对话记录）

### 操作命令

**CLI模式**:
| 命令 | 功能 |
|------|------|
| `跳过` | 跳过当前问题 |
| `导出` | 导出访谈记录 |
| `结束` | 结束访谈 |

**Web模式**:
| 按钮 | 功能 |
|------|------|
| 跳过 | 跳过当前问题 |
| 开始新访谈 | 开始新的访谈 |

> 访谈完成后自动导出至 `exports/` 目录

---

## 数据与报告

### 导出格式

```json
{
  "session_id": "abc12345",
  "user_name": "受访者",
  "start_time": "2025-12-03 10:00:00",
  "end_time": "2025-12-03 10:30:00",
  "statistics": {
    "total_logs": 8,
    "completion_rate": 100,
    "scene_distribution": {"学校": 3, "家庭": 2, "社区": 3},
    "edu_distribution": {"德育": 2, "智育": 1, "体育": 2, "美育": 1, "劳育": 2},
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

### 可视化图表

内置Plotly图表：
- 饼图：场景/育类型分布
- 柱状图：追问类型统计
- 折线图：访谈量趋势
- 仪表盘：综合统计

### HTML报告

通过管理后台生成可视化报告：
- 精美图表展示
- 完整统计数据
- 浏览器直接查看
- 便于分享

---

## 项目结构

```
interview_system/
├── src/
│   └── interview_system/      # 核心实现 (src-layout)
│       ├── app/               # 应用层
│       ├── ui/                # 用户界面
│       ├── core/              # 业务逻辑
│       ├── services/          # 服务层
│       ├── data/              # 数据层
│       ├── integrations/      # 外部API集成
│       ├── reports/           # 报告与可视化
│       └── common/            # 公共工具
├── docs/                      # 文档
│   ├── QUICKSTART.md
│   └── INSTALL_TEST.md
├── exports/                   # 导出文件（自动生成）
├── logs/                      # 日志文件（自动生成）
├── pyproject.toml             # 项目配置 (PEP 517/518)
├── requirements-lock.txt      # 锁定版本
├── .env.example               # 环境变量模板
└── interview_data.db          # SQLite数据库（自动生成）
```

---

## 开发指南

### 模块依赖

```
interview (CLI entry point)
  └── src/interview_system/app/main.py
        ├── ui/web_ui.py (Web界面)
        ├── ui/admin_ui.py (管理后台)
        ├── core/interview_engine.py
        │     ├── core/questions.py
        │     ├── integrations/api_client.py
        │     └── services/session_manager.py
        │           └── data/database.py
        └── common/config.py + common/logger.py
```

### 添加API服务商

编辑 `src/interview_system/integrations/api_client.py`：

```python
"new_provider": APIProviderConfig(
    name="服务商名称",
    provider_id="new_provider",
    base_url="https://api.example.com/v1",  # OpenAI兼容接口
    default_model="model-name",
    api_key_name="API密钥",
    models=["model-1", "model-2"],
    website="https://example.com/"
)
```

### 扩展题库

编辑 `src/interview_system/core/questions.py`：

```python
{
    "name": "场景-育类型",
    "scene": "场景",            # 学校/家庭/社区
    "edu_type": "育类型",       # 德育/智育/体育/美育/劳育
    "intro": "话题介绍",
    "questions": ["核心问题"],
    "scenarios": [],            # 可选
    "followups": ["预设追问1", "预设追问2"]
}
```

### 访谈规则

- **题目数量**: 每次访谈随机抽取6题
- **覆盖要求**: 确保覆盖3个场景（学校/家庭/社区）+ 5种育类型（德智体美劳）
- **追问逻辑**:
  - 回答过短（<15字）：自动追问
  - 深度不足：AI智能追问
  - 每题最多追问3次
  - 深度分≥4：跳至下一题
- **AI追问特点**:
  - 上下文感知（使用回答历史）
  - 话题相关
  - 对话式语气

---

## 许可证

MIT License

---

## 贡献指南

欢迎贡献代码。请遵循现有代码风格（海明威原则：简洁、高信噪比）。

---

## 相关文档

- [快速入门指南](docs/QUICKSTART.md)
- [安装与测试](docs/INSTALL_TEST.md)

---
