# Security Module (src/security/)

**Generated:** 2026-03-08
**Commit:** 6d71d5d
**Branch:** develop

## OVERVIEW
Security enforcement layer - input validation, path security, rate limiting, shell command filtering, and audit logging.

## STRUCTURE
```
security/
├── __init__.py           # Module exports
├── input_sanitizer.py    # SQL injection, XSS, command injection prevention
├── path_security.py      # Path traversal prevention, allowed directories
├── rate_limiter.py       # Request rate limiting per tool category
├── shell_security.py     # Shell command allowlist/blocklist
├── audit_logger.py       # Security event logging
└── exceptions.py         # Security-specific exceptions
```

## WHERE TO LOOK
| Task | File | Key Functions |
|------|------|---------------|
| Sanitize input | `input_sanitizer.py` | `sanitize_input()`, `sanitize_filename()` |
| Validate file path | `path_security.py` | `validate_file_path()`, `is_safe_path()` |
| Rate limiting | `rate_limiter.py` | `RateLimiter.is_allowed()` |
| Shell validation | `shell_security.py` | `ShellSecurity.validate_command()` |
| Log security event | `audit_logger.py` | `AuditLogger.log()` |
| Security exceptions | `exceptions.py` | `SecurityError`, `PathSecurityError` |

## PATH SECURITY
```python
from src.security.path_security import validate_file_path

# MUST call before any file operation
safe_path = validate_file_path(user_input)
if not safe_path:
    raise PathSecurityError("Invalid path")
```

**Blocked patterns:**
- Path traversal: `../`, `..\\`
- Absolute paths outside allowed dirs
- Symlinks to restricted areas
- Null bytes, control characters

## SHELL SECURITY
```python
from src.security.shell_security import ShellSecurity

result = ShellSecurity.validate_command("git status")
# Returns: (is_safe: bool, command: str, message: str)
```

**Safe commands** (no confirmation): `git`, `npm`, `python`, `pytest`, `ls`, `cat`, `grep`
**Blocked commands** (always denied): `rm`, `sudo`, `chmod`, `curl`, `wget`
**Unknown commands**: Require user confirmation

## RATE LIMITING
```python
from src.security.rate_limiter import RateLimiter

limiter = RateLimiter()
if not limiter.is_allowed("shell_execute"):
    raise RateLimitError("Too many requests")
```

| Category | Limit | Period |
|----------|-------|--------|
| Shell | 10 | 1 minute |
| Git | 20 | 1 minute |
| File | 60 | 1 minute |
| Web | 10 | 1 minute |

## INPUT SANITIZATION
```python
from src.security.input_sanitizer import sanitize_input, sanitize_filename

clean_text = sanitize_input(user_input)      # Removes XSS, SQL injection
safe_name = sanitize_filename(filename)      # Removes path chars, null bytes
```

## AUDIT LOGGING
All security events logged to `security_audit.log`:
- Path validation failures
- Shell command denials
- Rate limit violations
- Input sanitization events

## CONVENTIONS
1. ALWAYS validate user input before processing
2. ALWAYS call `validate_file_path()` before file access
3. ALWAYS use `ShellSecurity` for shell commands
4. ALWAYS handle `SecurityError` exceptions gracefully

## ANTI-PATTERNS
- **NEVER** skip path validation for file operations
- **NEVER** execute user input as shell commands directly
- **NEVER** log sensitive data (passwords, tokens)
- **NEVER** catch and silence `SecurityError`
- **NEVER** bypass rate limiting for high-frequency operations