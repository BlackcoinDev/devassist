# DevAssist Source Code (src/)

**Generated:** 2026-03-08
**Commit:** 6d71d5d
**Branch:** develop
**Context:** Implementation details for src/ modules

## Architecture

```
src/
├── core/           # Foundation (Config, Context, ChatLoop, Utils)
│   ├── config.py           # Env loading, verbose logging flags (352 lines)
│   ├── context.py          # ApplicationContext (DI container)
│   ├── context_utils.py    # ChromaDB API, embeddings, caching (751 lines)
│   ├── chat_loop.py        # Agentic loop, tool calling (605 lines)
│   ├── constants.py        # Shared constants
│   └── utils.py            # chunk_text, validate_file_path, standard_error/success
├── storage/        # Persistence (SQLite, Memory, Cache)
│   ├── database.py         # SQLite connection management (229 lines)
│   ├── memory.py           # Conversation history persistence (248 lines)
│   └── cache.py            # Embedding and query caching (352 lines)
├── security/       # Protection (Input Sanitizer, Path Security, Rate Limiter)
│   ├── input_sanitizer.py  # SQL injection, XSS, command injection
│   ├── path_security.py    # Path traversal prevention
│   ├── rate_limiter.py     # Request rate limiting
│   ├── shell_security.py   # Shell command allowlist (333 lines)
│   └── audit_logger.py     # Security event logging
├── vectordb/       # Knowledge (ChromaDB client, Spaces system)
│   ├── client.py           # ChromaDB unified HTTP API client (335 lines)
│   └── spaces.py           # Workspace/collection management
├── learning/       # Auto-learn markdown at startup
│   ├── config.py           # AutoLearnConfig (4 env vars)
│   ├── file_discovery.py   # discover_markdown_files()
│   ├── content_hash.py     # SHA-256 content hashing
│   ├── progress.py         # CLIProgress, NoOpProgress
│   └── auto_learn.py       # AutoLearnManager, initialize_auto_learning()
├── commands/       # Slash commands (plugin registry)
│   ├── registry.py         # CommandRegistry decorator dispatcher (228 lines)
│   └── handlers/           # 12 files, 25 commands (auto-register)
├── tools/          # AI tools (plugin registry)
│   ├── registry.py         # ToolRegistry decorator dispatcher (340 lines)
│   ├── approval.py         # ask/always/never permissions (226 lines)
│   └── executors/          # 7 executor modules (auto-register)
├── mcp/            # Model Context Protocol integration
│   ├── client.py           # MCPClient (315 lines)
│   └── transports/         # stdio, HTTP, SSE transports
├── gui.py          # PyQt6 GUI (1212 lines)
└── main.py         # CLI + initialization (547 lines)
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add slash command | `commands/handlers/*.py` | Use `@CommandRegistry.register()` |
| Add AI tool | `tools/executors/*.py` | Use `@ToolRegistry.register()` |
| Modify chat behavior | `core/chat_loop.py` | Tool execution, memory management |
| Vector DB operations | `core/context_utils.py` | ChromaDB HTTP API wrapper |
| Configuration | `core/config.py` | Env vars, verbose logging flags |
| Security validation | `security/*.py` | Input sanitizer, path security |
| Add learning feature | `learning/*.py` | AutoLearnConfig, discover_markdown_files() |
| GUI components | `gui.py` | PyQt6 main window, worker threads |
| Rate limiting | `security/rate_limiter.py` | Per-tool category limits |
| Shell safety | `security/shell_security.py` | Allowlist/blocklist validation |
| MCP integration | `mcp/client.py` | External tool server connection |

## CONVENTIONS (PROJECT-SPECIFIC)

### Plugin Registration Pattern
Both commands and tools use decorator-based auto-registration:

```python
# Commands: src/commands/handlers/category_commands.py
@CommandRegistry.register("mycommand", "Description", category="category")
def handle_mycommand(args: str) -> None:
    ...

# Tools: src/tools/executors/category_tools.py
@ToolRegistry.register("my_tool", TOOL_DEFINITION)
def execute_my_tool(arg: str) -> Dict[str, Any]:
    ...
```

### Standard Response Pattern
All tool executors use `standard_error/success` from `core/utils.py`:

```python
from src.core.utils import standard_error, standard_success

def execute_my_tool(arg: str) -> Dict[str, Any]:
    if error:
        return standard_error(f"Failed: {error}")
    return standard_success({"result": data})
```

### ApplicationContext Pattern
Centralized state via `src/core/context.py`:

```python
from src.core.context import get_context

ctx = get_context()  # Returns ApplicationContext singleton
ctx.llm, ctx.vectorstore, ctx.config  # Access shared resources
```

## ANTI-PATTERNS (THIS PROJECT)

- **DO NOT** import directly from `main.py` for new modules - use `get_context()`
- **DO NOT** skip `standard_error/success` in tool executors
- **DO NOT** bypass `validate_file_path()` for file operations
- **DO NOT** hardcode ChromaDB URLs - use `ctx.config.chroma_host`
- **DO NOT** execute shell commands without `ShellSecurity.validate()`

## LINTING RULES

Run before committing: `uv run python tests/lint/lint.py`

Key rules enforced:
- Max line length: 100 chars
- No unused imports (F401 zero-tolerance)
- MyPy type checking required
- No `as any` or `@ts-ignore` equivalents

## SUBDIRECTORIES

| Directory | AGENTS.md | Purpose |
|-----------|-----------|---------|
| `commands/handlers/` | Yes | Slash command handlers (25 commands) |
| `tools/executors/` | Yes | AI tool executors (13 tools) |
| `security/` | Yes | Security enforcement layer |