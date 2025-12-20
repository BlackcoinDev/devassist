# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DevAssist (v0.3.0) is an AI-powered learning assistant and development tool that combines conversational AI with
persistent knowledge management. It features dual interfaces (PyQt6 GUI and CLI), AI learning via ChromaDB vector
database, document processing for 80+ file types, and 13 AI tools for file operations, shell execution, git integration,
code search, and knowledge management.

**Core Technology Stack:**

- Python 3.13.x (latest available, e.g., 3.13.11 or newer) (⚠️ Python 3.14 NOT compatible)
- LangChain for AI orchestration
- LM Studio (qwen3-vl-30b) for LLM
- ChromaDB v2 server for vector storage
- Ollama (qwen3-embedding) for embeddings
- SQLite for conversation memory
- PyQt6 for GUI
- MCP (Model Context Protocol) for external tool integration

## Essential Commands

### Development (Using `uv`)

**Setup (one-time):**

```bash

# Create virtual environment with latest Python 3.13.x

uv venv venv --python 3.13  # Uses latest 3.13.x available on your system
source venv/bin/activate    # On Windows: venv\Scripts\activate

# Install dependencies

uv pip install -r requirements.txt
```text

**Running the Application:**

```bash

# CLI (default) - use uv run

uv run python launcher.py

# GUI mode

uv run python launcher.py --gui

# CLI mode (explicit)

uv run python launcher.py --cli

# Direct execution (if in venv)

python launcher.py

### Testing (Using `uv`)

```bash

# Run all tests (436 tests, ~35s execution)

uv run pytest

# Run with coverage report (target: 90%+)

uv run pytest --cov=main --cov=launcher --cov-report=term-missing

# Run specific test categories

uv run pytest tests/unit/              # Unit tests only
uv run pytest tests/integration/       # Integration tests only
uv run pytest tests/unit/test_main.py  # Specific test file

# Run single test

uv run pytest tests/unit/test_main.py::TestSpaceManagement::test_get_space_collection_name -v

# GUI tests (manual only - may cause crashes)

export RUN_GUI_TESTS=1
uv run pytest tests/unit/test_gui.py -v

# Run tests without coverage (faster)

uv run pytest -q

### Code Quality (Using `uv`)

```bash

# Run all linting checks (Python, shell, structure)

uv run python tests/lint/lint.py

# Individual linters via uv

uv run autopep8 --in-place --aggressive --aggressive <file>  # Auto-format
uv run flake8 <file>                                          # Style check
uv run mypy <file>                                            # Type check
uv run vulture <file>                                         # Dead code
uv run codespell <file>                                       # Spelling
```

**Key Patterns:**

- Always prefix commands with `uv run` when using tools
- Use `uv pip` for dependency management (install, uninstall, list)
- Virtual environment must be activated for direct `python`/`pytest` calls
- `uv` handles Python version selection automatically (3.13)

## Architecture Overview

### Three-Tier Storage System

DevAssist uses a sophisticated separation-of-concerns storage architecture:

1. **SQLite** (`db/history.db`): Transactional conversation history with ACID guarantees
2. **ChromaDB v2** (remote server): Semantic vector search for learned knowledge
3. **Mem0**: Personalized user preferences and long-term memory patterns

This separation allows each system to be optimized independently—SQLite for fast retrieval, ChromaDB for semantic
similarity, and Mem0 for personalization.

### Dual Interface Architecture

**Critical Consistency Requirements:**

Both GUI (`src/gui.py`) and CLI (`src/main.py`) MUST maintain complete feature parity:

- Both call `initialize_application()` for backend setup
- Both use shared global variables: `llm`, `vectorstore`, `embeddings`, `conversation_history`
- `launcher.py` loads `.env` for both interfaces before starting
- All slash commands must work identically in both interfaces
- GUI imports backend functions from `src/main.py`—no interface-specific logic paths

**Testing checklist when making changes:**

```bash

# ALWAYS test both interfaces (using uv run)

uv run python launcher.py --cli  # Test CLI
uv run python launcher.py --gui  # Test GUI

# Run full test suite with coverage

uv run pytest --cov=main --cov=launcher --cov-report=term-missing

```text

### Data Flow

```text

User Input → Interface (GUI/CLI)
          → initialize_application() (shared backend)
          → Space loading (space_settings.json)
          → LLM processing (qwen3-vl-30b with 8 tools)
          → Context retrieval (ChromaDB current space collection)
          → Response generation
          → Memory persistence (SQLite + Mem0)

### Spaces System

Each "space" is an isolated workspace with its own ChromaDB collection:

- Default space uses `knowledge_base` collection
- Custom spaces use `space_{name}` collection naming
- Current space persists in `space_settings.json`
- `/populate` and `/learn` add to current space only
- Space switching is instantaneous (no data migration)

## Configuration

### Required Services

**All three services must be running:**

```bash

# Terminal 1: LM Studio (load qwen3-vl-30b model)

lm studio --start-server

# Terminal 2: ChromaDB v2 Server (REQUIRED for learning features)

chroma run --host 192.168.0.204 --port 8000 --path ./chroma_data

# Terminal 3: Ollama (REQUIRED for embeddings)

ollama serve

### Environment Variables

**CRITICAL:** Application requires `.env` file with NO hardcoded defaults. Copy `.env.example` to `.env` and configure
all variables:

```bash

cp .env.example .env

# Edit .env with your settings

Required variables include:

- `LM_STUDIO_URL`, `LM_STUDIO_KEY`, `MODEL_NAME`
- `CHROMA_HOST`, `CHROMA_PORT`
- `OLLAMA_BASE_URL`, `EMBEDDING_MODEL`
- `MAX_HISTORY_PAIRS`, `TEMPERATURE`, `MAX_INPUT_LENGTH`
- `DB_TYPE=sqlite`, `DB_PATH=db/history.db`

### Verbose Logging Configuration

DevAssist supports granular logging control via 4 environment variables:

```bash
# In .env file
VERBOSE_LOGGING=true       # General debug output (context, commands, memory)
SHOW_LLM_REASONING=true    # AI response generation steps and timing
SHOW_TOKEN_USAGE=true      # Token counts for prompts/completions
SHOW_TOOL_DETAILS=true     # Tool execution details with timing
```

**Logging coverage by module:**

| Module | Flags Used |
| -------- | ------------ |
| `src/core/chat_loop.py` | All 4 flags (LLM reasoning, tokens, tools, verbose) |
| `src/tools/registry.py` | `show_tool_details` (registration, execution, timing) |
| `src/commands/registry.py` | `verbose_logging` (dispatch, completion) |
| `src/core/context.py` | `verbose_logging` (initialization) |
| `src/storage/memory.py` | `verbose_logging` (load/save operations) |
| `src/storage/cache.py` | `verbose_logging` (cache operations) |
| `src/tools/executors/*.py` | `show_tool_details` (tool-specific logging) |
| `src/commands/handlers/*.py` | `verbose_logging` (command execution) |
| `src/gui.py` | `verbose_logging` (GUI-specific operations) |

## Document Processing

### Unified Docling Processing

DevAssist uses **Docling** for unified document processing (v0.2.0), replacing separate libraries:

- **Supported formats**: PDF, DOCX, XLSX, RTF, EPUB, HTML, images, plus 80+ code file types
- **Benefits**: Single API, layout preservation, high-fidelity extraction
- **Smart chunking**: 1500-char chunks with paragraph-aware boundaries (`RecursiveCharacterTextSplitter`)
- **Quality filtering**: Skips files with <3 lines or <10% printable content
- **Binary detection**: Null byte and printable character ratio analysis

### Processing Pipeline

```text
File Discovery → Content Extraction (Docling) → Text Chunking (1500 chars)
             → Embedding Generation (Ollama) → Vector Storage (ChromaDB)
             → Metadata Enrichment → Semantic Search Ready

## AI Tool System

### 13 AI Tools Available

The qwen3-vl-30b model can autonomously call these tools:

| Tool                        | Purpose                                  | Test Status |
| --------------------------- | ---------------------------------------- | ----------- |
| `read_file()`               | Read file contents                       | ✅ Tested    |
| `write_file()`              | Create/modify files                      | ✅ Ready     |
| `list_directory()`          | Browse directories                       | ✅ Ready     |
| `get_current_directory()`   | Show current path                        | ✅ Tested    |
| `parse_document()`          | Extract text/tables/forms via Docling    | ✅ Ready     |
| `learn_information()`       | Store in ChromaDB                        | ✅ Ready     |
| `search_knowledge()`        | Query vector DB                          | ✅ Ready     |
| `search_web()`              | DuckDuckGo search                        | ✅ Ready     |
| `shell_execute()`           | Run shell commands (CLI only)            | ✅ Ready     |
| `git_status()`              | Git repository status                    | ✅ Ready     |
| `git_diff()`                | Show git changes                         | ✅ Ready     |
| `git_log()`                 | Commit history                           | ✅ Ready     |
| `code_search()`             | Regex code search (ripgrep)              | ✅ Ready     |

**Tool testing coverage:** 13/13 tools have comprehensive unit and integration tests.

**Shell Execution Security:**
- CLI-only (disabled in GUI mode)
- Allowlist-based: safe commands run without confirmation
- Blocklist: dangerous commands (rm, sudo) always denied
- Unknown commands require user confirmation

### Tool Result Lifecycle

1. AI calls tool → Tool executes → Returns structured result
2. Results stored in conversation memory (SQLite)
3. Results formatted and added to conversation context
4. AI uses tool data for response generation
5. Results persist in conversation history

## Development Guidelines

### Code Style

- **Python Version**: 3.13.x (latest available, e.g., 3.13.11+) managed with `uv`
- **Line Length**: 100 characters maximum
- **Type Hints**: Full MyPy type checking required
- **Style**: PEP 8 compliant (4-space indentation)
- **Imports**: Group as stdlib, third-party, local with blank lines between
- **Naming**: `snake_case` for variables/functions, `PascalCase` for classes
- **Error Handling**: Specific exceptions with comprehensive logging
- **Tool Usage**: Always use `uv run` prefix for linting, testing, and running scripts

### Testing Standards

- **Coverage Target**: 90%+ code coverage
- **Test Execution**: <30 seconds for full suite
- **Markers**: Use `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.gui`
- **Isolation**: Mock external dependencies (LLM, DB, filesystem)
- **Fixtures**: Use `conftest.py` fixtures for shared setup

**Test organization:**

```text

tests/
├── unit/              # ~300 tests (main, launcher, tools, commands, storage)
├── integration/       # ~80 tests (app, tool calling, workflows)
├── security/          # ~40 tests (input sanitization, path security, rate limiting)
├── tools/             # Document parsing tests
└── conftest.py        # Shared fixtures (mock_env, mock_llm, mock_vectorstore)

### GUI/CLI Consistency Checklist

When adding features:

- [ ] Environment variable loading works in both
- [ ] `initialize_application()` called by both interfaces
- [ ] Global variables properly shared
- [ ] Error handling consistent across both
- [ ] All slash commands work identically
- [ ] Context retrieval functional in both
- [ ] Memory persistence works the same
- [ ] Test in BOTH `--cli` and `--gui` modes

### Critical Files

**Core Application:**

| File            | Purpose                              | Lines |
| --------------- | ------------------------------------ | ----- |
| `src/main.py`   | CLI interface + LLM initialization   | 3,175 |
| `src/gui.py`    | PyQt6 GUI interface                  | 2,135 |
| `launcher.py`   | Interface selector + .env loader     | 216   |

**Modular Architecture (v0.3.0):**

| File                           | Purpose                                     | Lines |
| ------------------------------ | ------------------------------------------- | ----- |
| `src/core/config.py`           | Configuration management from .env          | 320   |
| `src/core/context.py`          | ApplicationContext (dependency injection)   | 310   |
| `src/core/context_utils.py`    | Shared utility functions                    | 330   |
| `src/core/chat_loop.py`        | Main chat loop with verbose logging         | 330   |
| `src/commands/registry.py`     | Command dispatcher (plugin system)          | 190   |
| `src/tools/registry.py`        | AI tool dispatcher (plugin system)          | 210   |
| `src/tools/approval.py`        | Tool approval system (ask/always/never)     | 150   |
| `src/vectordb/client.py`       | ChromaDB unified API client                 | 310   |
| `src/storage/database.py`      | SQLite connection management                | 120   |
| `src/storage/memory.py`        | Conversation history persistence            | 205   |
| `src/storage/cache.py`         | Embedding and query caching                 | 140   |
| `src/security/shell_security.py`| Shell command validation (allowlist)       | 120   |
| `src/mcp/client.py`            | MCP client manager                          | 250   |
| `src/mcp/transports/`          | stdio, HTTP, SSE transports                 | ---   |

**Tools & Testing:**

| File                            | Purpose                             | Lines |
| ------------------------------- | ----------------------------------- | ----- |
| `tools/populate_codebase.py`    | Bulk codebase import (production)   | ----- |
| `tests/conftest.py`             | Test fixtures                       | ----- |
| `pytest.ini`                    | Test configuration                  | ----- |

### Common Development Tasks

**Adding a new slash command:**

1. Create handler function in `src/commands/handlers/[category]_commands.py` (choose appropriate category: help, config,

   database, memory, learning, space, file, export)

2. Decorate with `@CommandRegistry.register("command_name", "Description", category="category", aliases=[])`
3. Handler auto-registers on import—no central configuration needed
4. Update GUI command button handlers in `src/gui.py` if adding a button
5. Write unit tests in `tests/unit/test_commands.py`
6. Test in both CLI and GUI modes

**Example:**

```python

# In src/commands/handlers/utility_commands.py

from src.commands.registry import CommandRegistry

@CommandRegistry.register("mycommand", "Does something useful", category="utility")
def handle_mycommand(args: str) -> None:
    """Handle /mycommand - does something useful."""
    print(f"Executing mycommand with args: {args}")

**Adding a new AI tool:**

1. Create executor function in `src/tools/executors/[category]_tools.py` (choose: file_tools, knowledge_tools,

   document_tools, web_tools)

2. Define OpenAI function calling schema in `TOOL_DEFINITION` dictionary
3. Decorate with `@ToolRegistry.register("tool_name", TOOL_DEFINITION)`
4. Executor auto-registers on import and LLM automatically receives tool definition
5. Create unit tests in `tests/unit/test_tools.py`
6. Create integration tests in `tests/integration/test_tool_calling.py`
7. Update this documentation

**Example:**

```python

# In src/tools/executors/utility_tools.py

from src.tools.registry import ToolRegistry
from typing import Dict, Any

MY_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "Does something useful",
        "parameters": {
            "type": "object",
            "properties": {
                "arg1": {"type": "string", "description": "First argument"}
            },
            "required": ["arg1"]
        }
    }
}

@ToolRegistry.register("my_tool", MY_TOOL_DEFINITION)
def execute_my_tool(arg1: str) -> Dict[str, Any]:
    """Execute my_tool with arg1."""
    result = f"Tool executed with: {arg1}"
    return {"success": True, "result": result}

**Modifying document processing:**

1. Update Docling integration in processing pipeline
2. Add new file type to `SUPPORTED_EXTENSIONS`
3. Test with sample files
4. Update quality filtering logic if needed
5. Add tests for new file type

**Adding shell commands to the safe list:**

1. Edit `src/security/shell_security.py`
2. Add command to `SAFE_COMMANDS` set (runs without confirmation)
3. Or add to `BLOCKED_COMMANDS` set (always denied)
4. Add tests for new command validation
5. Document security rationale

**Example:**

```python
# In src/security/shell_security.py

SAFE_COMMANDS: Set[str] = {
    "git", "npm", "python", "pytest",  # Development tools
    "cat", "ls", "grep",               # Read-only utilities
    "my_safe_command",                 # Add your safe command
}

BLOCKED_COMMANDS: Set[str] = {
    "rm", "sudo", "chmod",             # Dangerous operations
}
```

**Adding an MCP server:**

1. Create server configuration in `config/mcp_servers.json`
2. Specify transport type (stdio, http, sse)
3. For stdio: provide command and args
4. For http/sse: provide URL and optional headers
5. Enable server in configuration
6. Tools auto-discovered and prefixed with `mcp_servername_`

**Example:**

```json
{
  "servers": [
    {
      "name": "database",
      "transport": "stdio",
      "enabled": true,
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "mydb.db"]
    },
    {
      "name": "remote",
      "transport": "http",
      "enabled": false,
      "url": "http://localhost:8080/mcp",
      "headers": {"Authorization": "Bearer ${API_KEY}"}
    }
  ]
}
```

**Configuring tool approvals:**

1. Edit `config/tool_approvals.json`
2. Set approval mode: `always`, `ask`, or `never`
3. Use wildcards for MCP tools: `mcp_*`
4. Changes take effect on next tool execution

**Example:**

```json
{
  "approvals": {
    "read_file": "always",        // Safe, read-only
    "write_file": "ask",          // Prompts user
    "shell_execute": "ask",       // Prompts for unknown commands
    "mcp_database_*": "ask",      // All database MCP tools
    "dangerous_tool": "never"     // Blocked entirely
  }
}
```

## Known Issues & Constraints

### Current Limitations (v0.3.0)

- **Python 3.14**: Not compatible yet—use Python 3.13.x (latest available)
- **GUI Tests**: Skipped by default (10 tests) to prevent PyQt6 segfaults
- **Linting Issues**: 32 remaining issues (25 MyPy, 5 Vulture, 5 Flake8) - non-blocking

### Performance Expectations

- **Test Suite**: ~35 seconds for 436 tests (426 passed, 10 GUI skipped)
- **LLM Response Time**: 2-5 seconds (typical queries)
- **Tool Operations**: 5-15 seconds (file/document operations)
- **Memory Usage**: <8GB GPU memory (stable with qwen3-vl-30b)

## Roadmap Highlights (Planned)

**High Priority:**

- SQLCipher encryption for conversation database
- Secure API key storage with keyring
- Address remaining 32 linting issues

**Medium Priority:**

- Performance optimizations (Redis caching, batch processing)
- Advanced AI features (Pydantic-AI, LangGraph)
- Enhanced web capabilities (Crawl4AI)

**Future Vision:**

- Multi-user support
- Cloud deployment (Docker/Kubernetes)
- Plugin system architecture

## Key Architectural Insights

**Why Spaces Work:** Each space is simply a different ChromaDB collection name. No data duplication or migration—just
pointer switching. This allows instant context switching between projects.

**Why Three Storage Systems:** SQLite for transactional integrity (conversations), ChromaDB for semantic search
(embeddings), Mem0 for personalization patterns. Each optimized for its specific use case.

**Why Dual Interface Matters:** GUI and CLI share identical backend (`initialize_application()`) but different
frontends. All business logic lives in `src/main.py`, GUI just renders it. This ensures feature parity and reduces
duplication.

**Testing Philosophy:** 100% pass rate with 90%+ coverage isn't just metrics—tests use isolated fixtures (`conftest.py`)
to prevent production data contamination, critical for AI systems with subtle side effects.
