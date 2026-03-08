# Tool Executors (src/tools/executors/)

**Generated:** 2026-03-08
**Commit:** 6d71d5d
**Branch:** develop

## OVERVIEW
AI tool executors - functions that qwen3-vl-30b can call autonomously. 13 tools for file, git, shell, search, and knowledge operations.

## STRUCTURE
```
executors/
├── __init__.py           # Module exports
├── file_tools.py         # read_file, write_file, list_directory, get_current_directory
├── document_tools.py     # parse_document (Docling integration)
├── knowledge_tools.py    # learn_information, search_knowledge
├── web_tools.py          # search_web (DuckDuckGo)
├── shell_tools.py        # shell_execute (CLI only, allowlist security)
├── git_tools.py          # git_status, git_diff, git_log
└── system_tools.py       # code_search (ripgrep)
```

## WHERE TO LOOK
| Task | File | Tool Name |
|------|------|-----------|
| Add file tool | `file_tools.py` | `read_file`, `write_file`, etc. |
| Add search tool | `system_tools.py` | `code_search` |
| Add git tool | `git_tools.py` | `git_status`, `git_diff`, `git_log` |
| Add web tool | `web_tools.py` | `search_web` |
| Modify shell | `shell_tools.py` | Allowlist in `shell_security.py` |

## REGISTRATION PATTERN
```python
from src.tools.registry import ToolRegistry
from src.core.utils import standard_error, standard_success
from typing import Dict, Any

MY_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "What this tool does",
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
    try:
        result = do_something(arg1)
        return standard_success({"result": result})
    except Exception as e:
        return standard_error(f"Failed: {e}")
```

## RESPONSE FORMAT
All executors MUST use `standard_error` and `standard_success` from `src.core.utils`:

```python
return standard_success({"data": value})  # Success
return standard_error("Error message")     # Failure
```

## SECURITY
- File operations: MUST call `validate_file_path()` before access
- Shell commands: MUST use `ShellSecurity` allowlist validation
- Rate limiting: Tools are rate-limited (see `src/security/rate_limiter.py`)

## CONVENTIONS
1. Executor signature: `def execute_xxx(params) -> Dict[str, Any]`
2. Always wrap in try/except with standard_error on failure
3. Use `get_context()` for shared state
4. Validate inputs before processing

## ANTI-PATTERNS
- **NEVER** bypass `ToolRegistry` - auto-registration is required
- **NEVER** skip `standard_error/success` - breaks response format
- **NEVER** bypass `validate_file_path()` for file operations
- **NEVER** execute shell commands without `ShellSecurity.validate()`
- **NEVER** access `ctx.config` URLs directly - use config values