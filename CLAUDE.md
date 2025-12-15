# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DevAssist (v0.1.1) is an AI-powered learning assistant and development tool that combines conversational AI with persistent knowledge management. It features dual interfaces (PyQt6 GUI and CLI), AI learning via ChromaDB vector database, document processing for 80+ file types, and 8 AI tools for file operations and knowledge management.

**Core Technology Stack:**

- Python 3.13.x (latest available, e.g., 3.13.11 or newer) (⚠️ Python 3.14 NOT compatible)
- LangChain for AI orchestration
- LM Studio (qwen3-vl-30b) for LLM
- ChromaDB v2 server for vector storage
- Ollama (qwen3-embedding) for embeddings
- SQLite for conversation memory
- PyQt6 for GUI

## Essential Commands

### Development (Using `uv`)

**Setup (one-time):**

```bash
# Create virtual environment with latest Python 3.13.x
uv venv venv --python 3.13  # Uses latest 3.13.x available on your system
source venv/bin/activate    # On Windows: venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

**Running the Application:**

```bash
# GUI (default) - use uv run
uv run python launcher.py

# CLI only
uv run python launcher.py --cli

# GUI only
uv run python launcher.py --gui

# Direct execution (if in venv)
python launcher.py
```

### Testing (Using `uv`)

```bash
# Run all tests (89 tests, ~20-25s execution)
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
```

### Code Quality (Using `uv`)

```bash
# Comprehensive project linting (RECOMMENDED)
uv run python tests/lint/all-lint.py

# Python-specific linting only (faster)
uv run python tests/lint/lint-python.py

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

This separation allows each system to be optimized independently—SQLite for fast retrieval, ChromaDB for semantic similarity, and Mem0 for personalization.

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
```

### Data Flow

```text
User Input → Interface (GUI/CLI)
          → initialize_application() (shared backend)
          → Space loading (space_settings.json)
          → LLM processing (qwen3-vl-30b with 8 tools)
          → Context retrieval (ChromaDB current space collection)
          → Response generation
          → Memory persistence (SQLite + Mem0)
```

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
```

### Environment Variables

**CRITICAL:** Application requires `.env` file with NO hardcoded defaults. Copy `.env.example` to `.env` and configure all variables:

```bash
cp .env.example .env
# Edit .env with your settings
```

Required variables include:

- `LM_STUDIO_URL`, `LM_STUDIO_KEY`, `MODEL_NAME`
- `CHROMA_HOST`, `CHROMA_PORT`
- `OLLAMA_BASE_URL`, `EMBEDDING_MODEL`
- `MAX_HISTORY_PAIRS`, `TEMPERATURE`, `MAX_INPUT_LENGTH`
- `DB_TYPE=sqlite`, `DB_PATH=db/history.db`

## Document Processing

### Unified Docling Processing

DevAssist uses **Docling** for unified document processing (v0.1.1), replacing separate libraries:

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
```

## AI Tool System

### 8 AI Tools Available

The qwen3-vl-30b model can autonomously call these tools:

| Tool | Purpose | Test Status |
|------|---------|-------------|
| `read_file()` | Read file contents | ✅ Tested |
| `write_file()` | Create/modify files | ✅ Ready |
| `list_directory()` | Browse directories | ✅ Ready |
| `get_current_directory()` | Show current path | ✅ Tested |
| `parse_document()` | Extract text/tables/forms via Docling | ✅ Ready |
| `learn_information()` | Store in ChromaDB | ✅ Ready |
| `search_knowledge()` | Query vector DB | ✅ Ready |
| `search_web()` | DuckDuckGo search | ✅ Ready |

**Tool testing coverage:** 8/8 tools have comprehensive unit and integration tests (89 total tests, 100% pass rate).

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
├── unit/              # 52 tests (26 main + 6 launcher + 20 tool tests)
├── integration/       # 26 tests (11 app + 15 tool calling)
└── conftest.py        # Shared fixtures (mock_env, mock_llm, mock_vectorstore)
```

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

| File | Purpose | Lines |
|------|---------|-------|
| `src/main.py` | CLI app + shared backend logic | 4,556 |
| `src/gui.py` | PyQt6 GUI interface | 2,139 |
| `launcher.py` | Interface selector + .env loader | 216 |
| `tools/populate_codebase.py` | Bulk codebase import (production) | - |
| `tests/conftest.py` | Test fixtures | - |
| `pytest.ini` | Test configuration | - |

### Common Development Tasks

**Adding a new slash command:**

1. Add command handler to `handle_slash_command()` in `src/main.py` (line 1227)
2. Update GUI command button handlers in `src/gui.py`
3. Add to help text in both files
4. Write unit tests in `tests/unit/test_main.py`
5. Test in both CLI and GUI modes

**Adding a new AI tool:**

1. Define tool function with proper typing and docstring
2. Add to `enable_tools` list in tool initialization
3. Create unit tests in `tests/unit/test_tools.py`
4. Create integration tests in `tests/integration/test_tool_calling.py`
5. Update this documentation

**Modifying document processing:**

1. Update Docling integration in processing pipeline
2. Add new file type to `SUPPORTED_EXTENSIONS`
3. Test with sample files
4. Update quality filtering logic if needed
5. Add tests for new file type

## Known Issues & Constraints

### Current Limitations (v0.1.1)

- **Python 3.14**: Not compatible yet—use Python 3.13.x (latest available)
- **GUI Tests**: Skipped by default (10 tests) to prevent PyQt6 segfaults
- **Linting Issues**: 32 remaining issues (25 MyPy, 5 Vulture, 5 Flake8) - non-blocking

### Performance Expectations

- **Test Suite**: ~20-25 seconds for 89 tests
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

**Why Spaces Work:** Each space is simply a different ChromaDB collection name. No data duplication or migration—just pointer switching. This allows instant context switching between projects.

**Why Three Storage Systems:** SQLite for transactional integrity (conversations), ChromaDB for semantic search (embeddings), Mem0 for personalization patterns. Each optimized for its specific use case.

**Why Dual Interface Matters:** GUI and CLI share identical backend (`initialize_application()`) but different frontends. All business logic lives in `src/main.py`, GUI just renders it. This ensures feature parity and reduces duplication.

**Testing Philosophy:** 100% pass rate with 90%+ coverage isn't just metrics—tests use isolated fixtures (`conftest.py`) to prevent production data contamination, critical for AI systems with subtle side effects.
