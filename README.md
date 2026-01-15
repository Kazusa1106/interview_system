<div align="center">

# Interview System

**AI-Powered Interview Platform for Holistic Education Assessment**

[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

[Quick Start](#quick-start) • [Features](#features) • [Documentation](#documentation) • [Configuration](#configuration)

</div>

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Providers](#api-providers)
- [Project Structure](#project-structure)
- [Development](#development)
- [License](#license)

---

## Features

<table>
<tr>
<td width="50%">

**Core Capabilities**
- Multi-LLM support (DeepSeek, OpenAI, Qwen, GLM, ERNIE)
- Dynamic follow-up questions (max 3 per question)
- Context-aware AI responses
- Multi-user concurrent sessions
- CLI + Web interface

</td>
<td width="50%">

**v2.0 Enhancements**
- SQLite persistence
- Plotly visualization
- Admin dashboard
- Real-time statistics
- HTML report generation

</td>
</tr>
</table>

---

## Quick Start

### Prerequisites

- **Python**: 3.8 - 3.11 (3.12+ not supported)
- **OS**: Windows 10/11, macOS, Linux

### Check Python Version

```bash
python --version  # Must be 3.8-3.11
```

### Install & Run

```bash
# Clone repository
git clone https://github.com/username/interview_system.git
cd interview_system

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python -m interview_system
```

### Windows Quick Launch

```bash
scripts\install_and_test.bat  # Install & test
scripts\start_web.bat         # Launch web interface
scripts\start_admin.bat       # Launch admin dashboard
```

---

## Installation

<details>
<summary><b>Method 1: Virtual Environment (Recommended)</b></summary>

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

</details>

<details>
<summary><b>Method 2: Direct Install</b></summary>

```bash
pip install -r requirements.txt
```

</details>

<details>
<summary><b>Dependency Conflicts</b></summary>

Use locked versions if conflicts occur:

```bash
pip install -r requirements-lock.txt
```

</details>

### Testing

```bash
pip install -r requirements-dev.txt
pytest -q
```

---

## Configuration

### API Providers

| Provider | Model | API Key |
|----------|-------|---------|
| **DeepSeek** | `deepseek-chat` | [platform.deepseek.com](https://platform.deepseek.com/) |
| **OpenAI** | `gpt-3.5-turbo` | [platform.openai.com](https://platform.openai.com/) |
| **Qwen** | `qwen-turbo` | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com/) |
| **GLM** | `glm-4-flash` | [open.bigmodel.cn](https://open.bigmodel.cn/) |
| **ERNIE** | `ernie-3.5-8k` | [qianfan.baidubce.com](https://qianfan.baidubce.com/) |

> Use `deepseek-chat`. R1 is for math/logic only.

### Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env`:

```ini
# API Configuration
API_PROVIDER=deepseek
API_KEY=your_api_key_here
API_MODEL=deepseek-chat

# Web Server
WEB_HOST=127.0.0.1
WEB_PORT=7860
WEB_SHARE=false
```

**Priority**: Environment variables > `.env` file > `api_config.json` (deprecated)

### Security

- **Never commit** `.env` or `api_config.json`
- Use system environment variables in production
- Rotate API keys regularly
- `.gitignore` excludes sensitive files by default

<details>
<summary><b>Custom Configuration</b></summary>

Edit `src/interview_system/common/config.py`:

```python
INTERVIEW_CONFIG = InterviewConfig(
    total_questions=6,              # Questions per interview
    min_answer_length=15,           # Min length to trigger follow-up
    max_followups_per_question=3,   # Max follow-ups per question
    max_depth_score=4               # Max depth score (stops follow-ups)
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

## Usage

### Run Modes

```bash
python -m interview_system
```

Select mode:
- `1`: CLI interactive mode
- `2`: Web mode (default) - QR code for mobile access
- `3`: Admin dashboard

### Admin Dashboard

```bash
# Method 1: Select mode 3 at startup
python -m interview_system

# Method 2: Direct launch
python -m interview_system.app.admin

# Method 3: Windows script
scripts\start_admin.bat
```

**Access**: `http://localhost:7861`

**Features**:
- Overview dashboard (total interviews, completion rate, trends)
- Session list (view all interviews and details)
- Statistical analysis (visualizations, distributions)
- Data export (JSON batch export, HTML reports)
- Detail view (complete conversation logs)

### Commands

**CLI Mode**:
| Command | Action |
|---------|--------|
| `跳过` | Skip current question |
| `导出` | Export interview log |
| `结束` | End interview |

**Web Mode**:
| Button | Action |
|--------|--------|
| 跳过 | Skip current question |
| 开始新访谈 | Start new interview |

> Auto-exports to `exports/` on completion

---

## Data & Reports

### Export Format

```json
{
  "session_id": "abc12345",
  "user_name": "Interviewee",
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

### Visualization

Built-in Plotly charts:
- Pie charts: Scene/education distribution
- Bar charts: Follow-up type statistics
- Line charts: Interview volume trends
- Dashboards: Comprehensive statistics

### HTML Reports

Generate visual reports from admin dashboard:
- Beautiful chart displays
- Complete statistics
- Browser-ready
- Shareable

---

## Project Structure

```
interview_system/
├── interview_system/          # Bootstrap package (python -m entry)
├── src/
│   └── interview_system/      # Core implementation
│       ├── app/               # Application layer
│       ├── ui/                # User interfaces
│       ├── core/              # Business logic
│       ├── services/          # Services
│       ├── data/              # Data layer
│       ├── integrations/      # External APIs
│       ├── reports/           # Reporting & visualization
│       └── common/            # Shared utilities
├── docs/                      # Documentation
│   ├── QUICKSTART.md
│   └── INSTALL_TEST.md
├── scripts/                   # Utility scripts
│   ├── start_web.bat
│   ├── start_admin.bat
│   └── install_and_test.bat
├── exports/                   # Exported interviews (auto-generated)
├── logs/                      # Log files (auto-generated)
├── requirements.txt           # Dependencies
├── requirements-lock.txt      # Locked versions
├── .env.example               # Environment template
└── interview_data.db          # SQLite database (auto-generated)
```

---

## Development

### Module Dependencies

```
python -m interview_system
  └── app/main.py
        ├── ui/web_ui.py (Web interface)
        ├── ui/admin_ui.py (Admin dashboard)
        ├── core/interview_engine.py
        │     ├── core/questions.py
        │     ├── integrations/api_client.py
        │     └── services/session_manager.py
        │           └── data/database.py
        └── common/config.py + common/logger.py
```

### Add API Provider

Edit `src/interview_system/integrations/api_client.py`:

```python
"new_provider": APIProviderConfig(
    name="Provider Name",
    provider_id="new_provider",
    base_url="https://api.example.com/v1",  # OpenAI-compatible
    default_model="model-name",
    api_key_name="API Key",
    models=["model-1", "model-2"],
    website="https://example.com/"
)
```

### Extend Questions

Edit `src/interview_system/core/questions.py`:

```python
{
    "name": "场景-育类型",
    "scene": "场景",            # 学校/家庭/社区
    "edu_type": "育类型",       # 德育/智育/体育/美育/劳育
    "intro": "话题介绍",
    "questions": ["核心问题"],
    "scenarios": [],            # Optional
    "followups": ["预设追问1", "预设追问2"]
}
```

### Interview Rules

- **Questions**: 6 random questions per interview
- **Coverage**: Ensures 3 scenes (学校/家庭/社区) + 5 education types (德智体美劳)
- **Follow-up Logic**:
  - Answer too short (<15 chars): Auto follow-up
  - Insufficient depth: AI follow-up
  - Max 3 follow-ups per question
  - Depth score ≥4: Skip to next question
- **AI Follow-up**:
  - Context-aware (uses answer history)
  - Topic-relevant
  - Conversational tone

---

## License

MIT License

---

## Contributing

Contributions welcome. Follow existing code style (Hemingway principles: terse, high-signal).

---

## Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [Installation & Testing](docs/INSTALL_TEST.md)

---
