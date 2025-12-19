# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

大学生五育并举访谈智能体 (University Student Five-Education Interview AI Agent) - An intelligent interview system that supports multiple users simultaneously, with AI-powered follow-up questions based on various LLM APIs.

## Common Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application (main entry point)
python main.py

# Run with specific mode
python main.py  # Interactive mode selection
```

### Available Runtime Modes
1. **CLI Mode** (`python main.py` → select option 1) - Command-line interface for interviews
2. **Web Mode** (`python main.py` → select option 2, default) - Gradio-based web interface with QR code access

## High-Level Architecture

### Core Module Dependencies

```
main.py (Entry point)
├── config.py (Configuration management)
├── logger.py (Centralized logging)
├── api_client.py (Multi-provider LLM API client)
│   ├── Supports: DeepSeek, OpenAI, Qwen, GLM, Baidu Qianfan
│   └── Unified OpenAI-compatible interface
├── session_manager.py (Multi-user session handling)
├── interview_engine.py (Core interview logic)
│   ├── questions.py (15 topics: 3 scenes × 5 education types)
│   ├── api_client.py (AI follow-up generation)
│   └── session_manager.py (Session state management)
└── web_server.py (Gradio web interface)
    ├── session_manager.py
    └── interview_engine.py
```

### Key Components

**Interview Engine (`interview_engine.py`)**
- Core interview logic and flow control
- AI-powered follow-up question generation
- Answer depth scoring algorithm
- Question selection ensuring coverage across 3 scenes + 5 education types

**Session Manager (`session_manager.py`)**
- Thread-safe multi-user session management
- Automatic session cleanup and timeout handling
- JSON export functionality with statistics

**API Client (`api_client.py`)**
- Unified interface for multiple LLM providers
- Automatic retry mechanisms
- Configuration persistence in `api_config.json`

**Question System (`questions.py`)**
- 15 interview topics covering:
  - Scenes: 学校 (School), 家庭 (Family), 社区 (Community)
  - Education Types: 德 (Moral), 智 (Intellectual), 体 (Physical), 美 (Aesthetic), 劳 (Labor)
- Preset follow-up questions for each topic

## Configuration

### Main Configuration (`config.py`)
- `INTERVIEW_CONFIG`: Interview parameters (question count, follow-up limits, depth scoring)
- `WEB_CONFIG`: Web server settings (port, session limits)
- `LOG_CONFIG`: Logging configuration

### API Configuration
First-time setup guides through provider selection:
- Interactive API key configuration
- Auto-saves to `api_config.json`
- Supports 5 major LLM providers

## Data Flow

1. **Session Creation**: `session_manager.py` creates unique session with ID
2. **Question Selection**: `interview_engine.py` selects 6 questions ensuring scene/education coverage
3. **Answer Processing**: Answers evaluated for depth, triggering AI or preset follow-ups
4. **AI Follow-up**: `api_client.py` generates contextual questions using conversation history
5. **Export**: Sessions auto-exported to JSON with statistics in `exports/` directory

## File Structure Context

- `/logs/` - Application logs (auto-created)
- `/exports/` - Interview session JSON exports (auto-created)
- `api_config.json` - Persistent API configuration (auto-generated)

## Development Notes

- The system uses a modular design with clear separation of concerns
- All text content is in Chinese, designed for Chinese university students
- AI follow-ups consider conversation history to avoid repetition
- DeepSeek R1 model is explicitly excluded due to unsuitability for conversation
- Thread-safe design supports simultaneous multi-user interviews