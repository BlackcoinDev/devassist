# Gemini Code Assistant Project Context (v0.3.0)

This document provides context for the AI Assistant Chat Application, a Python-based interactive AI chat assistant.

## Project Overview

DevAssist is an advanced interactive AI chat assistant powered by LangChain, utilizing local models (via LM Studio/Ollama) and a ChromaDB vector database for knowledge storage. It features a dual interface (GUI and CLI), robust agentic capabilities with 13 core tools, and a unified Model Context Protocol (MCP) integration.

### Key Technologies (v0.3.0)

* **Core Framework**: LangChain
* **LLM Serving**: LM Studio (qwen3-vl-30b)
* **Vector Database**: ChromaDB v2
* **Embeddings**: Ollama (qwen3-embedding)
* **Personalized Memory**: Mem0
* **GUI**: PyQt6
* **CLI**: Rich-enhanced terminal with secure shell execution.
* **MCP**: Model Context Protocol (stdio, HTTP, SSE transports).

### Architecture

The application uses a modular architecture with clear separation of concerns:

* **`src/core`**: Foundation logic, including `ApplicationContext` (DI) and `ChatLoop` (Orchestrator).
* **`src/storage`**: Persistence layer (SQLite for history, cache for embeddings).
* **`src/mcp`**: Integration layer for external tool servers.
* **`src/security`**: Security enforcement (input sanitization, path security, shell allowlist).
* **`src/tools`**: Registry and executors for the 13 core tools.
* **`src/commands`**: Registry for slash commands.

## Building and Running

### Prerequisites

* Python 3.13+ (⚠️ Python 3.14 is NOT compatible)
* `uv` package manager (REQUIRED)
* LM Studio, ChromaDB v2, and Ollama services running.

### Installation & Launch

```bash
uv venv venv --python 3.13
source venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env  # Configure mandatory variables
uv run python launcher.py [--gui | --cli]
```

## AI Tool System

The AI autonomously calls 13 core tools for various operations:

| Tool | Purpose |
| :--- | :--- |
| `read_file`, `write_file` | File system operations |
| `shell_execute` | CLI command execution (CLI only, secure allowlist) |
| `git_status`, `git_diff`, `git_log` | Git repository integration |
| `code_search` | Ripgrep-based regex search |
| `parse_document` | Unified processing via Docling |
| `learn_information`, `search_knowledge` | Knowledge base management |
| `search_web` | DuckDuckGo web search |
| `list_directory`, `get_current_directory` | Navigation |

## Development Conventions

### Strict Linting & Standards

* **Zero-Tolerance Linting**: All code must pass `uv run python tests/lint/lint.py`.
* **Unused Imports**: Never import `MagicMock` or `Mock` unless explicitly called in the code.
* **Type Safety**: Full MyPy type hints and Pyright validation.
* **Feature Parity**: All changes must work identically in both GUI and CLI.

### Testing

* **Total Tests**: ~730 (functional + security + integration).
* **Execution**: `uv run pytest`.
* **Coverage**: 90%+ target across all modular components.

## Key Files

* `launcher.py`: Entry point and environment loader.
* `src/main.py`: CLI interface and application initialization.
* `src/gui.py`: PyQt6 graphical interface.
* `src/core/chat_loop.py`: The agentic loop orchestrator.
* `src/tools/approval.py`: The Tool Approval Manager.
* `src/security/rate_limiter.py`: Centralized Rate Limit Manager.
* `src/security/audit_logger.py`: Security Audit Logger.
* `config/mcp_servers.json`: MCP server definitions.
* `config/tool_approvals.json`: Approval policy configuration.
