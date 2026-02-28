# DevAssist Source Code (src/)

**Generated:** 2026-02-18
**Context:** Implementation details for src/ modules

## Architecture

```
src/
├── core/           # Foundation (Config, Context, ChatLoop, Utils)
│   ├── config.py           # Env loading, verbose logging flags
│   ├── context.py          # ApplicationContext (DI container)
│   ├── context_utils.py    # ChromaDB API, embeddings, caching (751 lines)
│   ├── chat_loop.py        # Agentic loop, tool calling (605 lines)
│   ├── constants.py        # Shared constants
│   └── utils.py            # chunk_text, validate_file_path, standard_error/success
├── storage/        # Persistence (SQLite, Memory, Cache)
├── security/       # Protection (Input Sanitizer, Path Security, Rate Limiter)
├── vectordb/       # Knowledge (ChromaDB client, Spaces system)
├── learning/        # Auto-learn markdown (config, discovery, hashing, progress, manager)
├── commands/       # Slash commands (plugin registry)
│   ├── registry.py         # CommandRegistry decorator dispatcher
│   └── handlers/           # 12 files, 25 commands (auto-register)
├── tools/          # AI tools (plugin registry)
│   ├── registry.py         # ToolRegistry decorator dispatcher
│   ├── approval.py         # ask/always/never permission system
│   └── executors/          # 7 executor modules (auto-register)
├── mcp/            # Model Context Protocol integration
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
| Add learning feature | `learning/*.py` | AutoLearnConfig, discover_markdown_files(), compute_content_hash() |
| GUI components | `gui.py` | PyQt6 main window, worker threads |

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

## LINTING RULES

Run before committing: `uv run python tests/lint/lint.py`

Key rules enforced:
- Max line length: 100 chars
- No unused imports (F401 zero-tolerance)
- MyPy type checking required
- No `as any` or `@ts-ignore` equivalents