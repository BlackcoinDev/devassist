# Agent Guidelines for DevAssist AI Assistant v0.3.0 - Shell & MCP Integration

## Build Commands

### Python LangChain Application v0.3.0

- **Run CLI application**: `uv run python launcher.py` (default)
- **Run GUI application**: `uv run python launcher.py --gui`
- **Install dependencies**: `uv pip install -r requirements.txt`
 **Python version**: Python 3.12.x (e.g., 3.12.12 or newer)
- **GUI framework**: PyQt6 for modern graphical interface
- **Vector database**: ChromaDB v2 server (implemented)
- **Database**: SQLite for conversation memory (required, no JSON fallback)
- **Document processing**: Unified Docling for PDF, DOCX, RTF, EPUB, XLSX, HTML, and 80+ file types
- **LangChain packages**: Updated to latest versions (langchain-chroma, langchain-ollama)
- **Markdown support**: HTML rendering in GUI for rich text display
- **Security**: Basic SQLite security, shell command allowlisting, tool approval system
- **MCP Support**: Model Context Protocol for external tool integration (stdio, HTTP, SSE)
 **Virtual environment**: `uv venv venv --python 3.12` then `source venv/bin/activate` (Python 3.12.x venv)
- **Code complexity**: Maintained under acceptable thresholds with proper refactoring
- **Type safety**: Full MyPy type checking with type stubs for external libraries

## Test Commands

### Python Application Tests

- **Run all tests**: `uv run pytest`
- **Run with coverage**: `uv run pytest --cov=src --cov=launcher --cov-report=term-missing`
- **Run specific test file**: `uv run pytest tests/unit/test_main.py`
- **Run integration tests**: `uv run pytest tests/integration/`
- **Run GUI tests manually**: `RUN_GUI_TESTS=1 uv run pytest tests/unit/test_gui.py`
 **Test framework**: pytest 9.0.2 with pytest-cov and pytest-mock
 **Test structure**: 830 tests total (functional + security + integration), all tests passing
 **Coverage**: 74% current, 80% target across all modular components, comprehensive tool testing
- **Modular coverage**: Includes src/core, src/storage, src/security, src/vectordb, src/commands, src/tools

## Lint Commands

### Linting Script

- **Run all checks**: `uv run python tests/lint/lint.py`
- **Dependencies**: flake8, mypy, vulture, codespell, shellcheck
- **Type stubs**: types-Markdown, types-requests for MyPy support

#### `tests/lint/lint.py` - Consolidated Project Linting

- **Purpose**: Complete project quality assurance
- **Python Checks**: Syntax, formatting (Autopep8), style (Flake8), types (MyPy), dead code (Vulture), spelling (Codespell)
- **Other Checks**: Shell scripts (ShellCheck), project structure, required files
- **Required Files**: src/main.py, src/gui.py, launcher.py, AGENTS.md, README.md, docs/MIGRATION.md
- **Usage**: `uv run python tests/lint/lint.py`

## Testing Framework v0.3.0

### Test Architecture

 **Framework**: pytest 9.0.2 with comprehensive mocking and fixtures
- **Coverage**: pytest-cov for code coverage reporting
- **Mocking**: pytest-mock for flexible test isolation
- **Structure**: Unit tests, integration tests, and GUI component tests
- **Configuration**: `pytest.ini` with optimized settings for CI/CD

### Test Categories

#### Unit Tests (Core Functionality)

- **src/main.py tests** (26 tests): Application initialization, command handling, memory management
- **launcher.py tests** (6 tests): CLI/GUI selection, environment loading, argument parsing
- **Coverage**: All core business logic and data operations

#### Integration Tests (Component Interaction)

- **Command integration** (4 tests): Slash command processing and responses
- **Memory persistence** (2 tests): Database save/load operations
- **Space management** (2 tests): Workspace switching and collection handling
- **End-to-end validation** (3 tests): Import chains and configuration loading

#### GUI Tests (Isolated Components)

- **Support functions** (6 tests): Markdown/HTML conversion, text formatting
- **Configuration** (2 tests): GUI constants and library availability
- **Worker threads** (2 tests): AI processing thread initialization
- **Status**: Intentionally skipped to prevent PyQt6 segmentation faults

### Test Execution

#### Standard Test Run

```bash

# Run all tests (GUI tests auto-skipped)

uv run pytest

# Result: 501 passed, 10 skipped

```text

#### Advanced Test Options

```bash

# Run with coverage report

uv run pytest --cov=main --cov=launcher --cov-report=term-missing

# Run specific test categories

uv run pytest tests/unit/           # Unit tests only
uv run pytest tests/integration/   # Integration tests only

# Run tests in verbose mode

uv run pytest -v

# Run tests with minimal output

uv run pytest -q
```text

#### GUI Tests (Manual Only)

```bash

# WARNING: May cause segmentation faults and hanging windows

# Close all applications before running

# Enable GUI tests

export RUN_GUI_TESTS=1

# Run GUI tests

uv run pytest tests/unit/test_gui.py -v

# Expected: 10 passed (if no Qt crashes occur)

```text

### Test Configuration

#### pytest.ini Settings

```ini
[tool:pytest]
testpaths = test
python_files = test_*.py *_test.py
addopts =
    --verbose
    --tb=short
    --cov=main
    --cov=launcher
    --cov-report=term-missing
    --cov-fail-under=80
    -k "not test_gui"
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    gui: GUI-related tests (may cause crashes)

#### Test Fixtures (conftest.py)

- **mock_env**: Environment variable mocking for configuration
- **mock_llm**: Language model mocking for AI interactions
- **mock_vectorstore**: Vector database mocking for knowledge base
- **mock_embeddings**: Text embedding mocking for vectorization
- **temp_dir**: Temporary directory creation for file operations

### Test Quality Standards

#### Coverage Requirements

- **Core modules**: src/main.py, launcher.py (target: 80%+ coverage)
- **Critical paths**: Initialization, command handling, data persistence
- **Error conditions**: Exception handling and edge cases
- **GUI components**: Isolated testing without Qt runtime

#### Test Isolation

- **Mock external dependencies**: LLM APIs, databases, file systems
- **Clean test environment**: No persistent state between tests
- **Thread safety**: Proper mocking of concurrent operations
- **Platform independence**: Tests work across different environments

#### CI/CD Integration

- **Fast execution**: Complete test suite runs in ~25 seconds
- **No external dependencies**: All services mocked appropriately
- **Reliable results**: Deterministic test outcomes
- **Clear reporting**: Detailed failure information and coverage metrics

### Test Maintenance

#### Adding New Tests

1. **Unit tests**: Add to `tests/unit/` with descriptive names
2. **Integration tests**: Add to `tests/integration/` for component interaction
3. **GUI tests**: Add to `tests/unit/test_gui.py` (marked with skipif)
4. **Fixtures**: Add shared fixtures to `tests/conftest.py`

#### Test Naming Conventions

- **Files**: `test_*.py` or `*_test.py`
- **Classes**: `Test*` (e.g., `TestSpaceManagement`)
- **Methods**: `test_*` (e.g., `test_get_space_collection_name`)
- **Descriptive**: Method names should clearly indicate what is being tested

#### Debugging Test Failures

```bash

# Run specific failing test with detailed output

uv run pytest tests/unit/test_main.py::TestSpaceManagement::test_get_space_collection_name -v -s

# Run with full traceback

uv run pytest --tb=long

# Debug with pdb

uv run pytest --pdb

### Test Results Summary

#### Current Status (v0.3.0)

 **Total tests**: 830 (functional + security + integration)
- **Pass rate**: 100% (All active tests passing)
- **Execution time**: ~45 seconds
 **Coverage**: 74% current, 80% target including comprehensive tool testing
- **CI/CD ready**: No external dependencies required

#### Test Categories Breakdown

- **Unit Tests**: ~300 tests (main, launcher, tools, commands, storage, config)
- **Integration Tests**: ~80 tests (app, tool calling, workflows)
- **Security Tests**: ~40 tests (input sanitization, path security, rate limiting)
- **GUI Tests**: 10 tests (skipped by default)
- **Total**: 436 tests (426 active + 10 GUI), all AI tools fully covered

### Testing Best Practices

#### Test Organization

- **One concept per test**: Each test should validate a single behavior
- **Descriptive names**: Test names should explain what they verify
- **Arrange-Act-Assert**: Clear structure for each test method
- **Independent tests**: No test should depend on others

#### Mocking Strategy

- **External APIs**: Mock LLM services, vector databases, file operations
- **Complex objects**: Mock Qt widgets, database connections, network calls
- **Time-dependent code**: Mock datetime, random operations, async delays
- **File system**: Mock file reads/writes, directory operations

#### Performance Considerations

- **Fast tests**: Keep individual tests under 1 second
- **Minimal setup**: Reuse fixtures and avoid redundant initialization
- **Parallel execution**: Tests designed to run concurrently
- **Resource cleanup**: Proper teardown of temporary resources

### Linting Tools

#### Core Python Tools

- **Autopep8**: Automatic PEP8 code formatting and style checking
- **Flake8**: Code style and error checking (PEP8, max line length 100)
- **MyPy**: Static type checking with optional imports ignored
- **Vulture**: Dead code detection (unused variables/functions)
- **Codespell**: Spelling checker for comments and strings

#### Additional Tools

- **ShellCheck**: Shell script linting (requires `brew install shellcheck`)
- **Project Structure**: Validates required files and directories

### Quality Standards

- **Line Length**: 100 characters maximum
- **Style**: PEP8 compliant with some exceptions (E203, W503)
- **Types**: Full MyPy coverage with type stubs
- **Imports**: Clean imports, no unused dependencies
- **Documentation**: Comprehensive docstrings and comments

### 🚨 Strict Linting Enforcement (Zero-Tolerance)

This project enforces a zero-warning linting policy via `tests/lint/lint.py`.

#### Zero-Tolerance for Unused Imports
- **MagicMock Tug-of-War**: Many agents redundantly import `MagicMock` when only `@patch` is used. This triggers `F401`.
- **The Rule**: ONLY import symbols that are explicitly used in the code.
- **Verification**: Before finishing any task, you MUST run `uv run python tests/lint/lint.py`. If it fails, your task is incomplete.
- **Redundant Mocks**: If a test uses `@patch("path.to.obj") def test(mock_obj):`, the `mock_obj` is already a mock. Do NOT import `MagicMock` unless you explicitly call `MagicMock()` or `Mock()` in the function body.

## Document Processing

### File Type Support

- **Text files**: .txt, .md, .rst, .adoc, .tex, .bib
- **Documents**: .doc, .docx, .rtf, .odt
- **Spreadsheets**: .xlsx
- **E-books**: .epub, .mobi
- **Data formats**: .json, .xml, .yaml, .yml, .toml, .csv, .tsv, .sql
- **Code files**: 80+ programming languages and frameworks
- **Build systems**: Makefile, CMake, Gradle, Maven
- **Binary handling**: Automatic detection and filtering
- **Encoding support**: UTF-8, Latin-1, CP1252, ISO-8859-1 auto-detection

### Content Extraction (Unified via Docling)

- **Docling**: Single library handling PDF, DOCX, RTF, EPUB, XLSX, HTML, and images with layout preservation
- **chardet**: Character encoding detection for text files with different encodings
- **Note**: Legacy libraries (PyPDF2, python-docx, striprtf, ebooklib, openpyxl) kept in dependencies for compatibility

  but superseded by Docling for v0.2.0+

### Processing Features

- **Smart chunking**: 1500-char chunks with paragraph-aware boundaries
- **Quality filtering**: Skip files with <3 lines or <10% content
- **Binary detection**: Null byte and printable character ratio analysis
- **Metadata enrichment**: File size, line count, modification time, language detection
- **Documentation prioritization**: Process docs before code for better context

## Database Architecture v0.3.0

### ChromaDB v2 (Vector Database - Primary)

- **Setup**: `chroma run --host 192.168.0.204 --port 8000 --path ./chroma_data`
- **Features**: Distributed vector storage, semantic search, persistent metadata
- **Integration**: Direct v2 API calls for reliable document storage/retrieval
- **Persistence**: Server-based storage survives application restarts

### SQLite (Conversation Memory - Implemented)

- **Setup**: Built-in Python support, no additional installation required
- **Features**: ACID transactions, concurrent access, SQL querying, indexing
- **Security**: Basic encryption (SQLCipher planned for production)
- **Migration**: Seamless data integrity across versions

## Application Features v0.3.0

### User Interfaces

- **GUI Application**: Modern PyQt6 interface with complete CLI command parity
- **CLI Application**: Traditional terminal interface with full functionality
- **Unified Launcher**: `launcher.py` provides access to both interfaces
- **Consistency Guarantee**: All features, commands, and behaviors must work identically in both interfaces

### AI Learning Assistant

- **Learning Capability**: AI can be taught new information that persists across sessions
- **Knowledge Base**: ChromaDB v2 server for reliable vector storage and retrieval
- **Document Processing**: Extract content from PDFs, Word docs, RTF, EPUB, and 80+ file types
- **Codebase Ingestion**: Bulk import entire projects with intelligent file type detection
- **Context Awareness**: AI uses learned information in relevant conversations
- **File System Access**: Read/write files and navigate directories in current workspace
- **Natural Language File Commands**: Automatic detection and execution of file operations from conversational requests
- **Tool Calling Capabilities**: qwen3-vl-30b supports 13 tools for file operations, shell execution, git integration,

  code search, document processing, knowledge management, and web search

#### Tool Calling Benefits v0.3.0

**🔧 Deterministic Execution**

- AI models with tool calling can execute file operations with precision
- Structured function calls replace ambiguous natural language interpretation
- Consistent results with clear success/failure feedback

**⚡ Enhanced Capabilities**

- **File Operations**: Direct read/write/create/delete with proper error handling
- **Shell Execution**: Run development commands (git, npm, python, etc.) in CLI mode
- **Git Integration**: Check status, view diffs, browse commit history
- **Code Search**: Fast regex search across codebase using ripgrep
- **MCP Integration**: Connect external tool servers via Model Context Protocol

**🛡️ Reliability Improvements**

- **Structured Parameters**: Tool calls include validated parameters
- **Error Recovery**: Built-in error handling and fallback mechanisms
- **Security Sandboxing**: Controlled access to file system resources
- **Tool Approval**: Per-tool ask/always/never permission controls
- **Audit Trail**: Complete logging of tool executions

**🚀 Advanced Features Ready**

- **Multi-step Operations**: AI can plan and execute complex file management tasks
- **Context Awareness**: Tool usage based on conversation context and learned knowledge
- **Proactive Assistance**: AI can suggest and execute helpful actions automatically
- **Workflow Automation**: Streamlined development and project management tasks

**📋 13 Tools Supported by qwen3-vl-30b**

- **read_file()**: Read file contents (tested & working)
- **write_file()**: Create/modify files
- **list_directory()**: Browse directories
- **get_current_directory()**: Get current path (tested & working)
- **parse_document()**: Extract text/tables/forms from documents (PDF, DOCX, images)
- **learn_information()**: Add to knowledge base
- **search_knowledge()**: Query learned information
- **search_web()**: Search the internet using DuckDuckGo for current information
- **shell_execute()**: Run shell commands (CLI only, allowlist-based security)
- **git_status()**: Get git repository status
- **git_diff()**: Show git changes (staged or unstaged)
- **git_log()**: View commit history
- **code_search()**: Fast regex search using ripgrep

### Additional Features

- **Markdown Support**: Rich text rendering in GUI with HTML formatting
- **Smart Chunking**: 1500-char chunks with paragraph-aware boundaries for better retrieval
- **Quality Filtering**: Automatic filtering of low-value content and binary files
- **Workspace Isolation**: Spaces system for separate knowledge bases per project

### Spaces System v0.1

- **Workspace Isolation**: Each space has its own ChromaDB collection for complete knowledge separation
- **Default Space**: "default" space uses the traditional "knowledge_base" collection
- **Persistent Settings**: Current space is saved and restored across application restarts
- **Dynamic Collections**: Spaces are created automatically when first used
- **GUI Integration**: Space selector in settings panel with real-time switching

### Core Commands v0.3.0

- **`/learn <text>`** - Teach AI new information (primary learning feature)
- **`/web <url>`** - Learn content directly from webpages via Docling
- **`/vectordb`** - View knowledge base statistics and sources in current space
- **`/mem0`** - Inspect personalized memory contents
- **`/populate <path>`** - Bulk import codebases and documentation to current space
- **`/model`** - Check current AI model and switching capabilities
- **`/memory`** - View persistent conversation history
- **`/clear`** - Reset conversation memory (keeps learned knowledge)
- **`/context <mode>`** - Control context integration (auto/on/off)
- **`/learning <mode>`** - Control learning behavior (normal/strict/off)
- **`/export <fmt>`** - Export conversation (json/markdown)
- **`/read <file>`** - Read file contents from current directory
- **`/write <file> <content>`** - Write content to file in current directory
- **`/list [dir]`** - List directory contents
- **`/pwd`** - Show current working directory
- **`/approve <tool> <mode>`** - Set tool approval mode (ask/always/never)
- **`/mcp list`** - List connected MCP servers and their tools
- **`/mcp connect <name>`** - Connect to an MCP server from config
- **`/git-status`** - Show git repository status (aliases: `/gs`, `/status`)
- **`/git-log [n]`** - Show commit history (aliases: `/gl`, `/log`)
- **`/git-diff`** - Show git changes (aliases: `/gd`, `/diff`)
- **`/search <pattern>`** - Code search with ripgrep (aliases: `/grep`, `/rg`)
- **`/shell <cmd>`** - Execute shell command (CLI only, aliases: `/sh`, `/run`)
- **Natural Language**: Say "read the README", "run pytest", or "what changed in git"
- **`/help`** - Comprehensive command reference

### Auto-Learn Feature v0.1
 **Dedicated Collection**: Stores learned information in `agents_knowledge` ChromaDB collection
 **Non-Blocking**: Runs in background thread during startup, doesn't delay application launch
 **Graceful Degradation**: Continues startup if ChromaDB unavailable, logs warning
 **Scope**: Recursively discovers ALL markdown files (*.md, *.markdown) in the project
 **Exclusions**: Skips `.sisyphus/`, `__pycache__/`, `.git/`, `node_modules/`, `.venv/` directories
 **Deduplication**: Uses SHA-256 content hashing (first 1KB) to prevent duplicate entries
 **Insight Extraction**: Extracts headers, code blocks, lists, and links from markdown
 **Configuration**: Controlled via environment variables for user customization
#### Configuration Options

Auto-learn behavior is controlled by these environment variables:
 **`AUTO_LEARN_ON_STARTUP`**: Enable/disable auto-learning (default: `true`)
 **`AUTO_LEARN_MAX_FILE_SIZE_MB`**: Skip files larger than this size (default: `5`)
 **`AUTO_LEARN_TIMEOUT_SECONDS`**: Maximum processing time per file (default: `30`)
 **`AUTO_LEARN_COLLECTION_NAME`**: ChromaDB collection name (default: `agents_knowledge`)
#### Module Structure

The auto-learn feature is implemented in the `src/learning/` module with these components:
 `src/learning/__init__.py` - Module exports
 `src/learning/config.py` - AutoLearnConfig dataclass with environment variable loading
 `src/learning/file_discovery.py` - Recursive file discovery with exclusion patterns
 `src/learning/content_hash.py` - SHA-256 content hashing for deduplication
 `src/learning/progress.py` - ProgressCallback protocol, CLIProgress, NoOpProgress handlers
 `src/learning/auto_learn.py` - AutoLearnManager, initialize_auto_learning(), extract_insights()

#### Key Functions

- `initialize_auto_learning(progress_callback=None)` - Main entry point, starts background learning
- `discover_markdown_files(start_dir, max_size_mb, exclude_dirs)` - Recursive file discovery
- `compute_content_hash(file_path, sample_size)` - SHA-256 hash for deduplication
- `extract_insights(content)` - Parse markdown for headers, code blocks, lists, links


The AI can execute shell commands in CLI mode using an allowlist-based security model:

**Safe Commands (run without confirmation):**
- Development: `git`, `npm`, `yarn`, `python`, `python3`, `pip`, `node`, `cargo`, `go`, `uv`, `pytest`
- Read-only: `cat`, `ls`, `pwd`, `grep`, `rg`, `find`, `tree`, `wc`
- Build tools: `make`, `cmake`, `docker`, `kubectl`

**Blocked Commands (always denied):**
- Destructive: `rm`, `rmdir`, `del`
- Privileged: `sudo`, `su`, `chmod`, `chown`
- Network downloads: `curl`, `wget` (use search_web tool instead)

**Unknown Commands:** Require user confirmation before execution.

### MCP Integration v0.3.0

Model Context Protocol enables external tool server integration:

**Supported Transports:**
- **stdio**: Local subprocess servers (e.g., `npx @modelcontextprotocol/server-filesystem`)
- **HTTP**: Remote REST-based servers
- **SSE**: Server-Sent Events for streaming

**Configuration** (`config/mcp_servers.json`):
```json
{
  "servers": [
    {
      "name": "filesystem",
      "transport": "stdio",
      "enabled": true,
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    }
  ]
}
```

**Tool Naming:** MCP tools are prefixed with `mcp_servername_` (e.g., `mcp_filesystem_read_file`).

### Tool Approval System v0.3.0

Control which tools require confirmation before execution:

| Mode | Behavior |
| ------ | ---------- |
| `always` | Execute without asking (read-only tools) |
| `ask` | Prompt user before execution |
| `never` | Block execution entirely |

**Configuration** (`config/tool_approvals.json`):

```json
{
  "approvals": {
    "shell_execute": "ask",
    "write_file": "ask",
    "git_status": "always",
    "code_search": "always",
    "mcp_*": "ask"
  }
}
```

### Learning Mode Configuration v0.1

The application provides three learning modes to control how the AI uses learned information:

#### Normal Mode (Default)

- **Behavior**: Balanced, intelligent context integration
- **Context Usage**: AI automatically decides when learned information enhances responses
- **Use Case**: Most users - provides helpful context without overwhelming conversations
- **Command**: `/learning normal`

#### Strict Mode

- **Behavior**: Minimal context, focused on explicit learning queries
- **Context Usage**: Only includes learned information for direct questions about knowledge ("what do you know?", "what

  have you learned?")

- **Use Case**: Users wanting focused conversations without background information
- **Command**: `/learning strict`

#### Off Mode

- **Behavior**: Complete learning feature disable
- **Context Usage**: Ignores all learned information from vector database
- **Use Case**: Testing AI capabilities, privacy concerns, or wanting fresh responses
- **Command**: `/learning off`

### Context Integration Control v0.1

Complementing learning modes, context integration can be controlled separately:

- **`/context auto`** - AI decides when to include relevant context (recommended)
- **`/context on`** - Always include available context when possible
- **`/context off`** - Never include context from knowledge base

### Vector Database Architecture v0.1

- **ChromaDB v2 Server**: Dedicated vector database server at <http://192.168.0.204:8000>
- **Ollama Embeddings**: qwen3-embedding:latest for semantic text processing
- **Persistent Storage**: All learned information survives app restarts
- **Direct API Integration**: Optimized for reliability and performance

## Code Style Guidelines

### Python (LangChain Application)

 **Python Version**: 3.12.x (e.g., 3.12.12 or newer)
- **Imports**: Group imports (stdlib, third-party, local) with blank lines between groups
- **Type hints**: Use typing module for function parameters and return values
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Error handling**: Use try/except with specific exceptions, log errors appropriately
- **Docstrings**: Use triple quotes for function/class documentation with detailed explanations
- **Line length**: Keep lines under 100 characters
- **Formatting**: Follow PEP 8 with 4-space indentation
- **Comments**: Comprehensive inline and section comments for maintainability

## Environment Setup v0.3.0

### Required Services

- **LM Studio**: Local LLM server (<http://192.168.0.203:1234>) - AI brain
- **ChromaDB v2 Server**: Vector database (<http://192.168.0.204:8000>) - knowledge storage
- **Ollama**: Embedding server (<http://192.168.0.204:11434>) - text vectorization

### Service Startup Commands

```bash

# Terminal 1: LM Studio (load qwen3-vl-30b model)

lm studio --start-server

# Terminal 2: ChromaDB v2 Server

chroma run --host 192.168.0.204 --port 8000 --path ./chroma_data

# Terminal 3: Ollama

ollama serve

### Configuration Files

- **.env**: Environment variables for all service connections
- **config/mcp_servers.json**: MCP server configurations
- **config/tool_approvals.json**: Tool approval settings
- **AGENTS.md**: This comprehensive documentation

### Verbose Logging Configuration

DevAssist provides granular logging control via these verbose logging variables in `.env`:

```bash
VERBOSE_LOGGING=true       # General debug output (context, commands, memory)
SHOW_LLM_REASONING=true    # AI response generation steps and timing
SHOW_TOKEN_USAGE=true      # Token counts for prompts/completions
SHOW_TOOL_DETAILS=true     # Tool execution details with timing
```

**Coverage:** All 4 flags are fully implemented across 10+ modules including chat_loop, registries, storage, tools, commands, and GUI.

### Virtual Environment

 **Python Version**: 3.12.x (e.g., 3.12.12 or newer)
 **Setup**: `uv venv venv --python 3.12` then `source venv/bin/activate`
- **Dependencies**: LangChain, ChromaDB, Ollama integration packages (install with `uv pip install -r requirements.txt`)

## General Guidelines

### Development

- **Commits**: Write clear, concise commit messages focusing on "why" not "what"
- **Documentation**: Keep code and MD files updated with current architecture
- **Testing**: Test all features after major changes
- **Dependencies**: Only use approved libraries; document new additions

### GUI/CLI Consistency

- **CRITICAL**: All code changes must maintain feature parity between GUI and CLI interfaces
- **Initialization**: Both interfaces must call `initialize_application()` for consistent backend setup
- **Environment Variables**: Both interfaces must have access to same environment configuration
- **Error Handling**: Error messages and behavior must be consistent across interfaces
- **Features**: Learning commands (`/learn`, `/populate`), context retrieval, and all slash commands must work

  identically

- **Testing**: Always test changes in both `uv run python launcher.py --cli` and `uv run python launcher.py --gui`
- **Global State**: Shared global variables (llm, vectorstore, embeddings, conversation_history) must be properly

  initialized in both interfaces

- **Imports**: GUI imports backend functions from `src/main.py` - ensure no interface-specific code paths

#### Consistency Checklist

- [ ] Environment variable loading (launcher.py loads .env for both)
- [ ] Backend initialization (`initialize_application()` called by both)
- [ ] Global variables properly shared (llm, vectorstore, embeddings, conversation_history)
- [ ] Error handling and user feedback consistent
- [ ] All slash commands work in both interfaces
- [ ] Context retrieval and learning features functional in both
- [ ] Memory persistence works identically
- [ ] Model switching and configuration changes apply to both

### Security

- **API Keys**: Never commit secrets, keys, or sensitive information
- **Environment Variables**: Use .env file for configuration
- **Database**: Encrypt sensitive conversation data at rest using SQLCipher or similar
- **Access Control**: Implement user isolation and proper authentication in multi-user scenarios

### Operations

- **Backup**: Regular encrypted backups of conversation databases and vector stores
- **Monitoring**: Check logs for errors and performance issues
- **Updates**: Keep dependencies updated for security and compatibility
- **Documentation**: Update this file when architecture changes

## Code Quality Standards v0.3.0

### Complexity Management

- **Function Complexity**: Maintained under 30 for analyzability (main: 27, well within limits)
- **Code Comments**: Comprehensive documentation for maintainability
- **Error Handling**: Proper exception handling with specific error types
- **Type Safety**: Full MyPy type checking with type stubs for external libraries

### Recent Improvements

- **Document Processing**: Added PDF, DOCX, RTF, EPUB, XLSX extraction with specialized libraries
- **File Type Support**: Expanded to 80+ file types with intelligent detection
- **Smart Chunking**: 1500-char chunks with paragraph-aware boundaries
- **Quality Filtering**: Automatic filtering of binary files and low-value content
- **Type Safety**: Resolved MyPy errors, added type annotations throughout
- **Linting**: Fixed critical errors, maintained clean codebase (0 issues)
 **Testing Infrastructure**: Comprehensive tool testing, 830 tests total, 100% pass rate
- **Code Quality**: Excellent (0 linting issues)
- **Documentation**: Updated all files to reflect current capabilities
- **Test Coverage**: Excellent coverage with 100% pass rate on all tests

## Code Complexity Hotspots

Large files requiring careful maintenance:
 `src/gui.py` (1212 lines) — PyQt6 GUI with full CLI parity, theming, streaming
- `src/core/context_utils.py` (751 lines) — ChromaDB API wrapper, embeddings, caching
- `src/core/chat_loop.py` (605 lines) — Agentic loop, tool calling, approvals
 `src/main.py` (533 lines) — CLI + initialization, command dispatching

## Shared Utilities

Central utility module: `src/core/utils.py`
- `chunk_text()` — Text splitting for vector storage (1500-char chunks)
- `validate_file_path()` — Path traversal prevention
- `get_file_size_info()` — File size retrieval
- `truncate_content()` — Content truncation for display
- `standard_error()` / `standard_success()` — Consistent tool response format

All tool executors use `standard_error/success` for response formatting.

## Anti-Patterns (DO NOT)

- **MagicMock imports**: Only import if calling `MagicMock()` directly; `@patch` provides mock automatically
- **Direct main.py imports**: Use `get_context()` from `src.core.context` for shared state
- **Skipping file validation**: Always call `validate_file_path()` before file operations
- **Hardcoded URLs**: Use `ctx.config.chroma_host` and `ctx.config.ollama_base_url`

## CI/CD Status

**No automated CI/CD pipeline.** All checks run manually:
- Lint: `uv run python tests/lint/lint.py`
- Test: `uv run pytest`
- Coverage: `uv run pytest --cov=src --cov-report=term-missing`

Recommend adding `.github/workflows/ci.yml` for automated testing and linting.

## Architecture Overview v0.3.0 (Modular + Shell/MCP)

### Component Integration

```text

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LM Studio     │    │ ChromaDB v2    │    │    Ollama       │
│ (AI Brain)      │◄──►│ (Vector DB)    │◄──►│ (Embeddings)    │
│ Port: 1234      │    │ Port: 8000     │    │ Port: 11434     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────────┐
                    │      launcher.py        │
                    │    (GUI/CLI selector)   │
                    │     loads .env          │
                    └─────────────────────────┘
                                 │
                ┌────────────────┴────────────────┐
                │                                 │
        ┌───────────────┐              ┌─────────────────┐
        │  src/gui.py   │              │  src/main.py    │
        │  (PyQt6 GUI)  │              │  (CLI + init)   │
        └───────┬───────┘              └────────┬────────┘
                │                               │
                └───────────┬───────────────────┘
                            │
                ┌───────────▼────────────┐
                │ ApplicationContext     │ (Dependency Injection)
                │  - llm, vectorstore    │
                │  - db_conn, history    │
                │  - config, caches      │
                └───────────┬────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
  ┌─────▼──────┐    ┌──────▼───────┐   ┌──────▼────────┐
  │ Commands   │    │    Tools     │   │   Storage     │
  │ (Registry) │    │  (Registry)  │   │   (SQLite)    │
  │ 24 handlers │    │  13 tools    │   │   (Memory)    │
  └────────────┘    └──────────────┘   └───────────────┘
        │                   │                   │
  ┌─────▼──────┐    ┌──────▼───────┐   ┌──────▼────────┐
  │  Security  │    │   VectorDB   │   │    Cache      │
  │ Validators │    │  (ChromaDB)  │   │  (In-memory)  │
  └────────────┘    └──────────────┘   └───────────────┘

```text

### Module Structure

```text

src/
├── core/          # Foundation (Config, ApplicationContext, ChatLoop)
│   ├── config.py           # Configuration management with verbose logging flags
│   ├── context.py          # ApplicationContext (dependency injection)
│   ├── context_utils.py    # Shared utility functions
│   └── chat_loop.py        # Main chat loop with all 4 logging flags
├── storage/       # Persistence (SQLite, memory, cache)
├── security/      # Protection (sanitization, path security)
├── vectordb/      # Knowledge (ChromaDB client, spaces)
├── learning/      # Auto-learn markdown at startup
│   ├── __init__.py         # Module exports
│   ├── config.py           # AutoLearnConfig (4 auto-learn env vars)
│   ├── file_discovery.py   # discover_markdown_files()
│   ├── content_hash.py     # compute_content_hash()
│   ├── progress.py         # CLIProgress, NoOpProgress
│   └── auto_learn.py       # AutoLearnManager, initialize_auto_learning()
├── commands/      # Command handlers (plugin system)
│   ├── registry.py         # CommandRegistry dispatcher with verbose logging
│   └── handlers/           # 11 handler modules (auto-register)
├── tools/         # AI tool executors (plugin system)
│   ├── registry.py         # ToolRegistry dispatcher with show_tool_details
│   └── executors/          # 7 executor modules (auto-register)
├── main.py        # CLI interface + LLM initialization
└── gui.py         # PyQt6 interface with verbose logging

### Data Flow v0.1

1. **Interface Selection** → `launcher.py` chooses GUI or CLI
2. **Application Initialization** → `initialize_application()` sets up LLM and vector database
3. **Space Loading** → Load last used workspace from `space_settings.json`
4. **Welcome Display** → `show_welcome()` shows interface and current space info
5. **User Teaching** → `/learn` commands add knowledge to current space's collection
6. **Code Ingestion** → `/populate` bulk imports codebases to current space
7. **Text Chunking** → `chunk_text()` processes content for vector storage
8. **Query Processing** → User asks questions via GUI or CLI
9. **Context Retrieval** → Current space's ChromaDB collection provides relevant learned information
10. **AI Enhancement** → LM Studio generates responses with space-specific learned context
11. **Memory Persistence** → SQLite saves conversation history
12. **Space Persistence** → Current space setting saved to `space_settings.json`
13. **Knowledge Growth** → AI learns continuously within current space

### Key Features v0.3.0

- **🖥️ Dual Interfaces**: Modern GUI (PyQt6) and traditional CLI
- **🏢 Spaces System**: Isolated workspaces with separate knowledge bases
- **🧠 Learning System**: AI can be taught any information persistently
- **📚 Codebase Knowledge**: Bulk import entire projects for AI understanding
- **🔍 Semantic Retrieval**: Context-aware information retrieval
- **💬 Memory Continuity**: Conversations persist across sessions
- **🎛️ Model Flexibility**: Easy switching between AI models
- **⚡ Direct API**: Optimized ChromaDB v2 integration for reliability
- **🎨 Rich Formatting**: Markdown support in GUI with HTML rendering
- **🛠️ Unified Commands**: Same slash commands work in both GUI and CLI
- **📝 Intelligent Chunking**: RecursiveCharacterTextSplitter for optimal text processing
- **🔧 Robust Initialization**: Comprehensive error handling and component setup
- **📊 Code Quality**: Good overall with some linting issues to address (32 total issues)
 **🐍 Python Version**: Python 3.12.x (e.g., 3.12.12 or newer)
- **📦 Package Manager**: uv (required for all operations) - `uv venv` and `uv pip install -r requirements.txt`
- **🐚 Shell Execution**: AI can execute shell commands in CLI mode with allowlist-based security
- **🔌 MCP Integration**: Connect external tool servers via Model Context Protocol (stdio, HTTP, SSE)
- **📂 Git Integration**: AI tools for git status, diff, log operations
- **🔍 Code Search**: Fast ripgrep-based regex search across codebase
- **🛡️ Tool Approval System**: Per-tool ask/always/never permission controls
