# DevAssist Test Suite (tests/)

**Generated:** 2026-02-18
**Context:** Testing conventions and patterns

## Structure

```
tests/
├── conftest.py            # Shared fixtures (mock_env, mock_llm, mock_vectorstore)
├── unit/                  # ~300 unit tests (isolated functionality)
├── integration/           # ~80 integration tests (component interaction)
├── security/              # ~40 security tests (path, input, rate limiting)
├── tools/                 # Tool-specific tests
├── performance/           # Performance regression tests
└── lint/
    └── lint.py            # Consolidated linting script
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add unit test | `unit/test_*.py` | Follow AAA pattern (Arrange-Act-Assert) |
| Add integration test | `integration/test_*.py` | Test component interactions |
| Add security test | `security/test_*.py` | Path traversal, injection, rate limits |
| Shared fixtures | `conftest.py` | mock_env, mock_llm, mock_vectorstore |
| Linting rules | `lint/lint.py` | flake8, mypy, vulture, codespell |

## CONVENTIONS (PROJECT-SPECIFIC)

### Test Naming
- Files: `test_*.py` or `*_test.py`
- Classes: `Test<Component>` (e.g., `TestSpaceManagement`)
- Methods: `test_<functionality>_<scenario>` (e.g., `test_git_status_clean_repo`)

### Mocking Pattern
Use `conftest.py` fixtures and `@patch`:

```python
from unittest.mock import MagicMock, patch
from tests.conftest import mock_vectorstore, mock_llm

@patch("src.vectordb.spaces.get_context")
def test_ensure_space_collection_success(mock_get_context, mock_vectorstore):
    mock_ctx = MagicMock()
    mock_ctx.vectorstore = mock_vectorstore
    mock_get_context.return_value = mock_ctx
    # ... test code
```

### GUI Test Handling
GUI tests are **skipped by default** due to PyQt6 segfaults:

```python
import pytest
@pytest.mark.skipif(not os.environ.get("RUN_GUI_TESTS"), reason="GUI tests disabled")
def test_gui_component():
    ...
```

Run manually: `RUN_GUI_TESTS=1 uv run pytest tests/unit/test_gui.py -v`

## COMMANDS

```bash
# All tests (~730 tests, ~45s)
uv run pytest

# With coverage (target: 90%+)
uv run pytest --cov=src --cov=launcher --cov-report=term-missing

# Unit only
uv run pytest tests/unit/

# Integration only
uv run pytest tests/integration/

# Specific test
uv run pytest tests/unit/test_main.py::TestSpaceManagement::test_get_space_collection_name -v

# Linting
uv run python tests/lint/lint.py
```

## ANTI-PATTERNS (THIS PROJECT)

- **DO NOT** import `MagicMock` if only using `@patch` (F401 zero-tolerance)
- **DO NOT** run GUI tests in CI (segfault risk)
- **DO NOT** use `@pytest.mark.skip` without reason string
- **DO NOT** skip linting before committing