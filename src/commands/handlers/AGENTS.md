# Command Handlers (src/commands/handlers/)

**Generated:** 2026-03-08
**Commit:** 6d71d5d
**Branch:** develop

## OVERVIEW
Slash command handlers - plugin-style auto-registration via decorators. Each file handles a category of commands.

## STRUCTURE
```
handlers/
├── __init__.py           # Module exports
├── help_commands.py      # /help, /commands
├── config_commands.py    # /model, /context, /learning
├── database_commands.py  # /vectordb, /mem0
├── memory_commands.py    # /memory, /clear
├── learning_commands.py  # /learn, /populate, /web
├── space_commands.py     # /space (create, switch, list, delete)
├── file_commands.py      # /read, /write, /list, /pwd
├── export_commands.py    # /export (json/markdown)
├── git_commands.py       # /git-status, /git-log, /git-diff
├── system_commands.py    # /shell, /search, /approve
└── mcp_commands.py       # /mcp list, /mcp connect
```

## WHERE TO LOOK
| Task | File | Function |
|------|------|----------|
| Add help text | `help_commands.py` | `handle_help()` |
| Add config cmd | `config_commands.py` | Use `@CommandRegistry.register()` |
| Add learning cmd | `learning_commands.py` | `/learn`, `/populate`, `/web` |
| Add git cmd | `git_commands.py` | Uses `git_tools.py` executors |
| Add shell cmd | `system_commands.py` | CLI-only, allowlist security |

## REGISTRATION PATTERN
```python
from src.commands.registry import CommandRegistry

@CommandRegistry.register("mycommand", "Description here", category="utility", aliases=["mc"])
def handle_mycommand(args: str) -> None:
    """Handle /mycommand - description."""
    # Implementation
```

**Parameters:**
- `name`: Command name (without slash)
- `description`: Help text
- `category`: Grouping for help display
- `aliases`: Optional list of alternative names

## OUTPUT HANDLING
Commands print directly to stdout/stderr. For GUI compatibility, use the print function (GUI captures it).

## CONVENTIONS
1. Handler signature: `def handle_xxx(args: str) -> None`
2. Args are the text after the command (may be empty)
3. Use `get_context()` for shared state, never import from main.py
4. Call tool executors for file/git/shell operations

## ANTI-PATTERNS
- **NEVER** bypass CommandRegistry - auto-registration is required
- **NEVER** import from `src.main` - use `get_context()`
- **NEVER** execute shell commands directly - use `shell_tools.py`
- **NEVER** access files directly - use `file_tools.py`