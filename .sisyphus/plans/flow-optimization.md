# Flow & Command Optimization Plan

## TL;DR

> **Quick Summary**: Optimize DevAssist command/tool flows through 3 phases: complete stub refactoring, consolidate duplicate code into shared utilities, and add async execution support for 4 long-running tools.
>
> **Deliverables**:
> - Completed stub handlers (populate, web) extracted from main.py
> - New shared utilities: security_utils.py, subprocess_utils.py
> - Unified path validation and SAFE_ENV_VARS
> - Async execution layer with qasync GUI integration
> - 4 async tools: search_web, parse_document, code_search, git operations
>
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 3 phases with internal parallelism
> **Critical Path**: Phase 1 → Phase 2 → Phase 3 (sequential phases, parallel tasks within)

---

## Context

### Original Request
Optimize flows and commands for DevAssist - a local AI learning assistant with 13 AI tools, 11 command handlers, ChromaDB knowledge base, and PyQt6 GUI.

### Interview Summary
**Goal**: Both performance AND maintainability across all 4 areas (Command Dispatch, Tool Execution, Chat Loop, Shared Utilities)

**Key Decisions**:
- Complete incomplete refactoring (populate/web stubs): YES
- Add async execution support: YES
- Consolidate tool modules: YES
- Async tools: search_web, parse_document, code_search, git_log/git_diff
- GUI integration: qasync for PyQt6 + asyncio
- Phasing: Stubs → Refactor → Async

### Metis Review

**Critical Findings**:
1. **BUG**: `SAFE_ENV_VARS` inconsistency - shell_tools.py has 5 vars, mcp/transports/stdio.py has 7 vars (different!)
2. **Circular Import Risk**: learning_commands.py imports from main.py - must verify no circular deps
3. **Path Validation Duplication**: 3 implementations in utils.py, path_security.py, git_tools.py

**Identified Gaps** (addressed):
- No specific async tools listed → User selected 4 tools
- No GUI async strategy → User selected qasync
- No acceptance criteria → Added agent-executable criteria below

---

## Work Objectives

### Core Objective
Refactor DevAssist command/tool architecture to eliminate code duplication, complete pending refactoring, and add async execution support while maintaining 100% backward compatibility and test coverage.

### Concrete Deliverables
- 2 completed stub handlers (handle_populate, handle_web)
- 2 new utility modules (security_utils.py, subprocess_utils.py)
- Unified SAFE_ENV_VARS in constants.py
- Async tool execution layer in ToolRegistry
- qasync integration in GUI

### Definition of Done
- [ ] All 730+ tests pass (`uv run pytest`)
- [ ] No circular imports verified
- [ ] Linting passes (`uv run python tests/lint/lint.py`)
- [ ] Manual QA: `/populate` and `/web` work without main.py imports

### Must Have
- Complete stub refactoring (populate, web handlers)
- Consolidated path validation
- Unified SAFE_ENV_VARS
- Async execution for 4 tools
- Backward compatibility for all 13 existing tools

### Must NOT Have (Guardrails)
- Must NOT change tool definitions (JSON schemas for LLM binding)
- Must NOT modify test assertions (tests must pass unchanged)
- Must NOT change ChatLoop public method signatures
- Must NOT remove or rename existing commands/tools
- Must NOT relax security validations during consolidation
- Must NOT break GUI or CLI interfaces

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: YES (TDD for new code, regression for existing)
- **Framework**: pytest with pytest-asyncio for async tests

### QA Policy
Every task includes agent-executed QA scenarios. Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

---

## Execution Strategy

### Parallel Execution Waves

```
PHASE 1 (Sequential - Foundation):
└── Task 1.1: Verify no circular imports [quick]

PHASE 1 - Wave 1 (Parallel after 1.1):
├── Task 1.2: Extract handle_populate from main.py [unspecified-high]
├── Task 1.3: Extract execute_learn_url from main.py [unspecified-high]
└── Task 1.4: Update learning_commands.py imports [quick]

PHASE 1 - Wave 2 (After Wave 1):
├── Task 1.5: Remove dead code from main.py [quick]
└── Task 1.6: Run full test suite [quick]

PHASE 2 - Wave 1 (Shared Utilities):
├── Task 2.1: Create security_utils.py [unspecified-high]
├── Task 2.2: Create subprocess_utils.py [unspecified-high]
└── Task 2.3: Unify SAFE_ENV_VARS in constants.py [quick]

PHASE 2 - Wave 2 (Consolidation):
├── Task 2.4: Migrate file_tools.py to security_utils [quick]
├── Task 2.5: Migrate git_tools.py to subprocess_utils [quick]
├── Task 2.6: Migrate shell_tools.py to shared utils [quick]
└── Task 2.7: Update mcp/transports/stdio.py imports [quick]

PHASE 2 - Wave 3 (Cleanup):
├── Task 2.8: Remove duplicate path validation [quick]
├── Task 2.9: Remove duplicate subprocess code [quick]
└── Task 2.10: Run full test suite [quick]

PHASE 3 - Wave 1 (Async Infrastructure):
├── Task 3.1: Add pytest-asyncio dependency [quick]
├── Task 3.2: Create async tool base class [deep]
├── Task 3.3: Update ToolRegistry for async support [deep]
└── Task 3.4: Add qasync to requirements.txt [quick]

PHASE 3 - Wave 2 (Async Tools):
├── Task 3.5: Make search_web async [unspecified-high]
├── Task 3.6: Make parse_document async [unspecified-high]
├── Task 3.7: Make code_search async [unspecified-high]
└── Task 3.8: Make git tools async [unspecified-high]

PHASE 3 - Wave 3 (GUI Integration):
├── Task 3.9: Integrate qasync in gui.py [visual-engineering]
├── Task 3.10: Test async tools in GUI [unspecified-high]
└── Task 3.11: Run full test suite [quick]

PHASE FINAL (Verification):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Manual QA - CLI (unspecified-high)
└── Task F4: Manual QA - GUI (unspecified-high)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|------------|--------|
| 1.1 | — | 1.2-1.6, all Phase 2-3 |
| 1.2-1.4 | 1.1 | 1.5-1.6 |
| 1.5-1.6 | 1.2-1.4 | All Phase 2 |
| 2.1-2.3 | 1.6 | 2.4-2.7 |
| 2.4-2.7 | 2.1-2.3 | 2.8-2.10 |
| 2.8-2.10 | 2.4-2.7 | All Phase 3 |
| 3.1-3.4 | 2.10 | 3.5-3.11 |
| 3.5-3.8 | 3.1-3.4 | 3.9-3.11 |
| 3.9-3.11 | 3.5-3.8 | Final |
| F1-F4 | 3.11 | — |

---

## TODOs

---

### PHASE 1: Complete Stub Refactoring

- [ ] 1.1. Verify No Circular Imports

  **What to do**:
  - Check if `handle_populate_command` and `execute_learn_url` in main.py depend on main.py global state
  - Use `lsp_find_references` to find all references to these functions
  - Verify learning_commands.py can import utilities without circular dependency

  **Must NOT do**:
  - Do NOT modify any files yet - this is read-only verification

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple verification task
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: NO (blocks Phase 1 Wave 1)
  - **Parallel Group**: Sequential
  - **Blocks**: All Phase 1 Wave 1 tasks
  - **Blocked By**: None (can start immediately)

  **References**:
  - `src/main.py` - Find `handle_populate_command` function (currently called by stub)
  - `src/main.py` - Find `execute_learn_url` function (currently called by stub)
  - `src/commands/handlers/learning_commands.py:98-101` - Current stub implementation for populate
  - `src/commands/handlers/learning_commands.py:112-135` - Current stub implementation for web

  **Acceptance Criteria**:
  - [ ] List of all global variables used by `handle_populate_command`
  - [ ] List of all global variables used by `execute_learn_url`
  - [ ] Decision: Can these be extracted? (YES/NO + rationale)

  **QA Scenarios**:

  ```
  Scenario: Verify populate function dependencies
    Tool: Bash (grep/ripgrep)
    Steps:
      1. grep -n "handle_populate_command" src/main.py
      2. Read the function and identify all global variable references
      3. Check if any global is modified in main.py after initialization
    Expected Result: List of dependencies captured
    Evidence: .sisyphus/evidence/task-1-1-populate-deps.txt

  Scenario: Verify web function dependencies
    Tool: Bash (grep/ripgrep)
    Steps:
      1. grep -n "execute_learn_url" src/main.py
      2. Read the function and identify all global variable references
      3. Check if any global is modified in main.py after initialization
    Expected Result: List of dependencies captured
    Evidence: .sisyphus/evidence/task-1-1-web-deps.txt
  ```

  **Commit**: NO

---

- [ ] 1.2. Extract handle_populate from main.py

  **What to do**:
  - Move `handle_populate_command` logic from main.py to learning_commands.py
  - Update imports to use ApplicationContext for dependencies
  - Change stub to direct implementation
  - Maintain exact same behavior

  **Must NOT do**:
  - Do NOT change function behavior
  - Do NOT add new features
  - Do NOT modify test files

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires careful code migration with dependency management
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 1.3)
  - **Parallel Group**: Phase 1 Wave 1
  - **Blocks**: Tasks 1.5, 1.6
  - **Blocked By**: Task 1.1

  **References**:
  - `src/main.py` - Source function to extract
  - `src/commands/handlers/learning_commands.py:89-101` - Destination (replace stub)
  - `src/core/context.py` - ApplicationContext for dependency injection
  - `src/core/context_utils.py` - Utility for knowledge base operations

  **Acceptance Criteria**:
  - [ ] Function moved to learning_commands.py as `handle_populate_impl`
  - [ ] Uses `get_context()` instead of main.py globals
  - [ ] Stub replaced with actual implementation
  - [ ] No import from main.py in learning_commands.py

  **QA Scenarios**:

  ```
  Scenario: Populate command works without main.py import
    Tool: Bash (python)
    Steps:
      1. uv run python -c "from src.commands.handlers.learning_commands import handle_populate; print('OK')"
    Expected Result: OK (no ImportError)
    Evidence: .sisyphus/evidence/task-1-2-no-import-error.txt

  Scenario: Populate still processes files
    Tool: Bash (python)
    Steps:
      1. Create test directory with sample files
      2. Run handle_populate on test directory
      3. Verify files were processed
    Expected Result: Files added to knowledge base
    Evidence: .sisyphus/evidence/task-1-2-populate-works.txt
  ```

  **Commit**: NO (groups with Phase 1)

---

- [ ] 1.3. Extract execute_learn_url from main.py

  **What to do**:
  - Move `execute_learn_url` logic from main.py to learning_commands.py
  - Update imports to use ApplicationContext for dependencies
  - Change stub to direct implementation
  - Maintain exact same behavior

  **Must NOT do**:
  - Do NOT change function behavior
  - Do NOT add new features
  - Do NOT modify test files

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires careful code migration with dependency management
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 1.2)
  - **Parallel Group**: Phase 1 Wave 1
  - **Blocks**: Tasks 1.5, 1.6
  - **Blocked By**: Task 1.1

  **References**:
  - `src/main.py` - Source function to extract
  - `src/commands/handlers/learning_commands.py:104-135` - Destination (replace stub)
  - `src/core/context.py` - ApplicationContext for dependency injection

  **Acceptance Criteria**:
  - [ ] Function moved to learning_commands.py as `execute_learn_url_impl`
  - [ ] Uses `get_context()` instead of main.py globals
  - [ ] Stub replaced with actual implementation
  - [ ] No import from main.py in learning_commands.py

  **QA Scenarios**:

  ```
  Scenario: Web command works without main.py import
    Tool: Bash (python)
    Steps:
      1. uv run python -c "from src.commands.handlers.learning_commands import handle_web; print('OK')"
    Expected Result: OK (no ImportError)
    Evidence: .sisyphus/evidence/task-1-3-no-import-error.txt

  Scenario: Web learning completes
    Tool: Bash (python)
    Steps:
      1. Run handle_web with a valid URL (mock or simple site)
      2. Verify content was learned
    Expected Result: Content added to knowledge base
    Evidence: .sisyphus/evidence/task-1-3-web-works.txt
  ```

  **Commit**: NO (groups with Phase 1)

---

- [ ] 1.4. Update learning_commands.py imports

  **What to do**:
  - Remove imports from main.py
  - Add imports from core utilities (context_utils, etc.)
  - Ensure all dependencies are satisfied from modular sources

  **Must NOT do**:
  - Do NOT add unused imports
  - Do NOT import from main.py

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple import cleanup
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 1.2, 1.3)
  - **Parallel Group**: Phase 1 Wave 1
  - **Blocks**: Tasks 1.5, 1.6
  - **Blocked By**: Task 1.1

  **References**:
  - `src/commands/handlers/learning_commands.py` - File to update
  - `src/core/context.py` - ApplicationContext import
  - `src/core/context_utils.py` - Knowledge base utilities

  **Acceptance Criteria**:
  - [ ] No imports from src.main
  - [ ] All necessary imports from src.core modules
  - [ ] No unused imports (F401 check)

  **QA Scenarios**:

  ```
  Scenario: No main.py imports remain
    Tool: Bash (grep)
    Steps:
      1. grep -n "from src.main" src/commands/handlers/learning_commands.py
      2. grep -n "import src.main" src/commands/handlers/learning_commands.py
    Expected Result: No matches
    Evidence: .sisyphus/evidence/task-1-4-no-main-imports.txt

  Scenario: Linting passes
    Tool: Bash (python)
    Steps:
      1. uv run python -c "import flake8; ..." or use tests/lint/lint.py
    Expected Result: No F401 (unused import) errors
    Evidence: .sisyphus/evidence/task-1-4-lint-pass.txt
  ```

  **Commit**: NO (groups with Phase 1)

---

- [ ] 1.5. Remove dead code from main.py

  **What to do**:
  - Remove `handle_populate_command` from main.py (now in learning_commands.py)
  - Remove `execute_learn_url` from main.py (now in learning_commands.py)
  - Clean up any now-unused helper functions
  - Verify no other code depends on these functions

  **Must NOT do**:
  - Do NOT remove functions still referenced elsewhere
  - Do NOT break any tests

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple dead code removal
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on 1.2-1.4)
  - **Parallel Group**: Sequential
  - **Blocks**: Task 1.6
  - **Blocked By**: Tasks 1.2, 1.3, 1.4

  **References**:
  - `src/main.py` - File to clean up
  - Use `lsp_find_references` to verify no remaining references

  **Acceptance Criteria**:
  - [ ] `handle_populate_command` removed from main.py
  - [ ] `execute_learn_url` removed from main.py
  - [ ] No other code references these functions
  - [ ] main.py length reduced (document line count change)

  **QA Scenarios**:

  ```
  Scenario: Functions removed from main.py
    Tool: Bash (grep)
    Steps:
      1. grep -n "handle_populate_command" src/main.py
      2. grep -n "execute_learn_url" src/main.py
    Expected Result: No matches
    Evidence: .sisyphus/evidence/task-1-5-functions-removed.txt

  Scenario: No broken references
    Tool: Bash (python)
    Steps:
      1. uv run python -c "import src.main; print('OK')"
    Expected Result: OK (no ImportError or AttributeError)
    Evidence: .sisyphus/evidence/task-1-5-no-broken-refs.txt
  ```

  **Commit**: NO (groups with Phase 1)

---

- [ ] 1.6. Run Full Test Suite (Phase 1 Checkpoint)

  **What to do**:
  - Run `uv run pytest` to verify no regressions
  - Run `uv run python tests/lint/lint.py` to verify code quality
  - Document test results

  **Must NOT do**:
  - Do NOT skip any tests
  - Do NOT modify test expectations

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Standard test execution
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: NO (Phase 1 checkpoint)
  - **Parallel Group**: Sequential
  - **Blocks**: All Phase 2 tasks
  - **Blocked By**: Tasks 1.2-1.5

  **References**:
  - pytest configuration in pytest.ini
  - lint script in tests/lint/lint.py

  **Acceptance Criteria**:
  - [ ] All tests pass (730+ tests)
  - [ ] No linting errors
  - [ ] Test count matches pre-refactor count

  **QA Scenarios**:

  ```
  Scenario: Tests pass
    Tool: Bash (pytest)
    Steps:
      1. uv run pytest --tb=short
    Expected Result: All tests pass, 0 failures
    Evidence: .sisyphus/evidence/task-1-6-tests-pass.txt

  Scenario: Linting passes
    Tool: Bash (python)
    Steps:
      1. uv run python tests/lint/lint.py
    Expected Result: All checks passed
    Evidence: .sisyphus/evidence/task-1-6-lint-pass.txt
  ```

  **Commit**: YES
  - Message: `refactor(commands): complete populate and web handler extraction`
  - Files: `src/main.py`, `src/commands/handlers/learning_commands.py`

---

### PHASE 2: Consolidate Shared Utilities

- [ ] 2.1. Create security_utils.py

  **What to do**:
  - Create `src/core/security_utils.py` with unified security functions
  - Include: `validate_path()`, `sanitize_path()`, `validate_command()`
  - Consolidate logic from path_security.py and git_tools.py
  - Export via __all__

  **Must NOT do**:
  - Do NOT break existing path_security.py (will migrate callers later)
  - Do NOT relax security checks

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Security-critical code consolidation
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 2.2, 2.3)
  - **Parallel Group**: Phase 2 Wave 1
  - **Blocks**: Tasks 2.4-2.7
  - **Blocked By**: Task 1.6

  **References**:
  - `src/core/utils.py:89-103` - Current basic validate_file_path
  - `src/security/path_security.py` - Comprehensive validate_path (220 lines)
  - `src/tools/executors/git_tools.py:69-96` - _sanitize_file_path (duplicate logic)
  - `src/tools/executors/shell_tools.py` - ShellSecurity class

  **Acceptance Criteria**:
  - [ ] File created: `src/core/security_utils.py`
  - [ ] Functions: `validate_path()`, `sanitize_path()`, `validate_command()`
  - [ ] Docstrings with examples
  - [ ] Type hints on all functions

  **QA Scenarios**:

  ```
  Scenario: Module imports correctly
    Tool: Bash (python)
    Steps:
      1. uv run python -c "from src.core.security_utils import validate_path, sanitize_path, validate_command; print('OK')"
    Expected Result: OK
    Evidence: .sisyphus/evidence/task-2-1-imports.txt

  Scenario: Path validation works
    Tool: Bash (python)
    Steps:
      1. uv run python -c "
from src.core.security_utils import validate_path
assert validate_path('/etc/passwd', allow_root=False) == False
assert validate_path('./local_file.txt', allow_root=False) == True
print('OK')
"
    Expected Result: OK
    Evidence: .sisyphus/evidence/task-2-1-validate-works.txt
  ```

  **Commit**: NO (groups with Phase 2)

---

- [ ] 2.2. Create subprocess_utils.py

  **What to do**:
  - Create `src/core/subprocess_utils.py` with unified subprocess functions
  - Include: `run_command()`, `get_safe_env()`, `run_git_command()`
  - Consistent timeout handling
  - Consistent error handling

  **Must NOT do**:
  - Do NOT change shell_security.py behavior
  - Do NOT add commands to safe list

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Cross-cutting utility for subprocess operations
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 2.1, 2.3)
  - **Parallel Group**: Phase 2 Wave 1
  - **Blocks**: Tasks 2.4-2.7
  - **Blocked By**: Task 1.6

  **References**:
  - `src/tools/executors/shell_tools.py:240` - subprocess.run usage
  - `src/tools/executors/git_tools.py:193` - subprocess.run usage
  - `src/tools/executors/system_tools.py:230` - subprocess.run usage
  - `src/security/shell_security.py` - Safe command patterns

  **Acceptance Criteria**:
  - [ ] File created: `src/core/subprocess_utils.py`
  - [ ] Functions: `run_command()`, `get_safe_env()`, `run_git_command()`
  - [ ] Timeout parameter with default
  - [ ] Consistent error return format

  **QA Scenarios**:

  ```
  Scenario: Module imports correctly
    Tool: Bash (python)
    Steps:
      1. uv run python -c "from src.core.subprocess_utils import run_command, get_safe_env, run_git_command; print('OK')"
    Expected Result: OK
    Evidence: .sisyphus/evidence/task-2-2-imports.txt

  Scenario: Safe env is sanitized
    Tool: Bash (python)
    Steps:
      1. uv run python -c "
from src.core.subprocess_utils import get_safe_env
env = get_safe_env()
assert 'PATH' in env or len(env) > 0  # Should have safe vars
assert 'API_KEY' not in env  # Should not have secrets
print('OK')
"
    Expected Result: OK
    Evidence: .sisyphus/evidence/task-2-2-safe-env.txt
  ```

  **Commit**: NO (groups with Phase 2)

---

- [ ] 2.3. Unify SAFE_ENV_VARS in constants.py

  **What to do**:
  - Add `SAFE_ENV_VARS` to `src/core/constants.py`
  - Use the comprehensive list from mcp/transports/stdio.py (7 vars)
  - Update shell_tools.py to import from constants
  - Update mcp/transports/stdio.py to import from constants
  - Fix the inconsistency bug identified by Metis

  **Must NOT do**:
  - Do NOT add new environment variables to the list
  - Do NOT remove any variables that are currently used

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple constant consolidation
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 2.1, 2.2)
  - **Parallel Group**: Phase 2 Wave 1
  - **Blocks**: Tasks 2.4-2.7
  - **Blocked By**: Task 1.6

  **References**:
  - `src/tools/executors/shell_tools.py:55` - Current SAFE_ENV_VARS (5 vars)
  - `src/mcp/transports/stdio.py:16` - Current SAFE_ENV_VARS (7 vars) - USE THIS
  - `src/core/constants.py` - Destination for unified constant

  **Acceptance Criteria**:
  - [ ] `SAFE_ENV_VARS` added to constants.py with 7 vars: PATH, HOME, LANG, TERM, SHELL, USER, PWD
  - [ ] shell_tools.py imports from constants
  - [ ] mcp/transports/stdio.py imports from constants
  - [ ] Only one definition of SAFE_ENV_VARS in codebase

  **QA Scenarios**:

  ```
  Scenario: Only one SAFE_ENV_VARS definition
    Tool: Bash (grep)
    Steps:
      1. grep -r "SAFE_ENV_VARS\s*=" src/ | wc -l
    Expected Result: 1 (only in constants.py)
    Evidence: .sisyphus/evidence/task-2-3-single-definition.txt

  Scenario: Imports work correctly
    Tool: Bash (python)
    Steps:
      1. uv run python -c "
from src.core.constants import SAFE_ENV_VARS
assert 'USER' in SAFE_ENV_VARS
assert 'PWD' in SAFE_ENV_VARS
print('OK')
"
    Expected Result: OK
    Evidence: .sisyphus/evidence/task-2-3-imports.txt
  ```

  **Commit**: NO (groups with Phase 2)

---

- [ ] 2.4. Migrate file_tools.py to security_utils

  **What to do**:
  - Update file_tools.py to use `validate_path()` from security_utils
  - Update file_tools.py to use `standard_error/standard_success` (already using)
  - Remove any inline path validation code

  **Must NOT do**:
  - Do NOT change tool behavior
  - Do NOT modify tool definitions

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple import update
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 2.5, 2.6, 2.7)
  - **Parallel Group**: Phase 2 Wave 2
  - **Blocks**: Tasks 2.8-2.10
  - **Blocked By**: Tasks 2.1-2.3

  **References**:
  - `src/tools/executors/file_tools.py` - File to update
  - `src/core/security_utils.py` - New utility to use

  **Acceptance Criteria**:
  - [ ] Imports from `src.core.security_utils`
  - [ ] Path validation uses shared function
  - [ ] Tests still pass

  **QA Scenarios**:

  ```
  Scenario: File tools import from shared utils
    Tool: Bash (grep)
    Steps:
      1. grep "from src.core.security_utils" src/tools/executors/file_tools.py
    Expected Result: Match found
    Evidence: .sisyphus/evidence/task-2-4-migrated.txt

  Scenario: File tools still work
    Tool: Bash (python)
    Steps:
      1. uv run pytest tests/unit/test_tools.py -k file -v
    Expected Result: All file tool tests pass
    Evidence: .sisyphus/evidence/task-2-4-tests.txt
  ```

  **Commit**: NO (groups with Phase 2)

---

- [ ] 2.5. Migrate git_tools.py to shared utils

  **What to do**:
  - Update git_tools.py to use `run_git_command()` from subprocess_utils
  - Update git_tools.py to use `validate_path()` from security_utils
  - Remove `_sanitize_file_path()` duplicate function

  **Must NOT do**:
  - Do NOT change git tool behavior
  - Do NOT modify tool definitions

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple import update with function removal
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 2.4, 2.6, 2.7)
  - **Parallel Group**: Phase 2 Wave 2
  - **Blocks**: Tasks 2.8-2.10
  - **Blocked By**: Tasks 2.1-2.3

  **References**:
  - `src/tools/executors/git_tools.py:69-96` - _sanitize_file_path to remove
  - `src/core/security_utils.py` - validate_path to use
  - `src/core/subprocess_utils.py` - run_git_command to use

  **Acceptance Criteria**:
  - [ ] `_sanitize_file_path()` removed
  - [ ] Uses shared path validation
  - [ ] Uses shared subprocess execution
  - [ ] Tests still pass

  **QA Scenarios**:

  ```
  Scenario: No duplicate sanitize function
    Tool: Bash (grep)
    Steps:
      1. grep "_sanitize_file_path" src/tools/executors/git_tools.py
    Expected Result: No matches
    Evidence: .sisyphus/evidence/task-2-5-no-duplicate.txt

  Scenario: Git tools still work
    Tool: Bash (python)
    Steps:
      1. uv run pytest tests/unit/test_tools.py -k git -v
    Expected Result: All git tool tests pass
    Evidence: .sisyphus/evidence/task-2-5-tests.txt
  ```

  **Commit**: NO (groups with Phase 2)

---

- [ ] 2.6. Migrate shell_tools.py to shared utils

  **What to do**:
  - Update shell_tools.py to use `run_command()` from subprocess_utils
  - Update shell_tools.py to use `SAFE_ENV_VARS` from constants
  - Keep ShellSecurity class for now (will be refactored later)

  **Must NOT do**:
  - Do NOT change shell tool behavior
  - Do NOT modify ShellSecurity allowlist/blocklist

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Import updates
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 2.4, 2.5, 2.7)
  - **Parallel Group**: Phase 2 Wave 2
  - **Blocks**: Tasks 2.8-2.10
  - **Blocked By**: Tasks 2.1-2.3

  **References**:
  - `src/tools/executors/shell_tools.py` - File to update
  - `src/core/subprocess_utils.py` - run_command to use
  - `src/core/constants.py` - SAFE_ENV_VARS to use

  **Acceptance Criteria**:
  - [ ] Uses `run_command()` from subprocess_utils
  - [ ] Uses `SAFE_ENV_VARS` from constants
  - [ ] Tests still pass

  **QA Scenarios**:

  ```
  Scenario: Shell tools use shared utils
    Tool: Bash (grep)
    Steps:
      1. grep "from src.core.constants" src/tools/executors/shell_tools.py
      2. grep "from src.core.subprocess_utils" src/tools/executors/shell_tools.py
    Expected Result: Both matches found
    Evidence: .sisyphus/evidence/task-2-6-migrated.txt

  Scenario: Shell tools still work
    Tool: Bash (python)
    Steps:
      1. uv run pytest tests/unit/test_tools.py -k shell -v
    Expected Result: All shell tool tests pass
    Evidence: .sisyphus/evidence/task-2-6-tests.txt
  ```

  **Commit**: NO (groups with Phase 2)

---

- [ ] 2.7. Update mcp/transports/stdio.py imports

  **What to do**:
  - Update stdio.py to import `SAFE_ENV_VARS` from constants
  - Remove local definition of `SAFE_ENV_VARS`

  **Must NOT do**:
  - Do NOT change MCP transport behavior
  - Do NOT break MCP integration

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple constant consolidation
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 2.4, 2.5, 2.6)
  - **Parallel Group**: Phase 2 Wave 2
  - **Blocks**: Tasks 2.8-2.10
  - **Blocked By**: Tasks 2.1-2.3

  **References**:
  - `src/mcp/transports/stdio.py:16` - Local SAFE_ENV_VARS to remove
  - `src/core/constants.py` - SAFE_ENV_VARS source

  **Acceptance Criteria**:
  - [ ] Local `SAFE_ENV_VARS` removed
  - [ ] Imports from constants
  - [ ] MCP tests pass

  **QA Scenarios**:

  ```
  Scenario: MCP uses shared constant
    Tool: Bash (grep)
    Steps:
      1. grep "from src.core.constants" src/mcp/transports/stdio.py
    Expected Result: Match found
    Evidence: .sisyphus/evidence/task-2-7-migrated.txt

  Scenario: MCP tests pass
    Tool: Bash (python)
    Steps:
      1. uv run pytest tests/ -k mcp -v
    Expected Result: All MCP tests pass
    Evidence: .sisyphus/evidence/task-2-7-tests.txt
  ```

  **Commit**: NO (groups with Phase 2)

---

- [ ] 2.8. Remove duplicate path validation code

  **What to do**:
  - Search for all path validation patterns using ast_grep_search
  - Verify all tools use shared security_utils
  - Remove any remaining inline validation

  **Must NOT do**:
  - Do NOT skip security checks

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Cleanup after migration
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 2.9)
  - **Parallel Group**: Phase 2 Wave 3
  - **Blocks**: Task 2.10
  - **Blocked By**: Tasks 2.4-2.7

  **References**:
  - Use `ast_grep_search` with pattern for path validation functions
  - Verify against grep results

  **Acceptance Criteria**:
  - [ ] Only one path validation implementation (in security_utils.py)
  - [ ] No inline path validation in tools

  **QA Scenarios**:

  ```
  Scenario: No duplicate path validation
    Tool: Bash (grep/ripgrep)
    Steps:
      1. grep -r "def.*validate.*path" src/ | grep -v security_utils
      2. grep -r "def.*sanitize.*path" src/ | grep -v security_utils
    Expected Result: No matches
    Evidence: .sisyphus/evidence/task-2-8-no-duplicates.txt
  ```

  **Commit**: NO (groups with Phase 2)

---

- [ ] 2.9. Remove duplicate subprocess code

  **What to do**:
  - Search for all subprocess.run patterns
  - Verify all tools use shared subprocess_utils
  - Remove any remaining inline subprocess calls (outside subprocess_utils)

  **Must NOT do**:
  - Do NOT break any subprocess functionality

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Cleanup after migration
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 2.8)
  - **Parallel Group**: Phase 2 Wave 3
  - **Blocks**: Task 2.10
  - **Blocked By**: Tasks 2.4-2.7

  **References**:
  - Use `ast_grep_search` for subprocess.run patterns
  - Verify against grep results

  **Acceptance Criteria**:
  - [ ] subprocess.run only in subprocess_utils.py (or security-approved locations)
  - [ ] No inline subprocess calls in tool executors

  **QA Scenarios**:

  ```
  Scenario: Subprocess calls consolidated
    Tool: Bash (grep)
    Steps:
      1. grep -rn "subprocess\.run" src/tools/executors/ 
    Expected Result: No matches (all moved to subprocess_utils)
    Evidence: .sisyphus/evidence/task-2-9-no-duplicates.txt
  ```

  **Commit**: NO (groups with Phase 2)

---

- [ ] 2.10. Run Full Test Suite (Phase 2 Checkpoint)

  **What to do**:
  - Run `uv run pytest` to verify no regressions
  - Run `uv run python tests/lint/lint.py` to verify code quality
  - Document results

  **Must NOT do**:
  - Do NOT skip any tests

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Standard test execution
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: NO (Phase 2 checkpoint)
  - **Parallel Group**: Sequential
  - **Blocks**: All Phase 3 tasks
  - **Blocked By**: Tasks 2.8-2.9

  **References**:
  - pytest.ini for test configuration

  **Acceptance Criteria**:
  - [ ] All tests pass (730+ tests)
  - [ ] No linting errors
  - [ ] SAFE_ENV_VARS unified (1 definition)

  **QA Scenarios**:

  ```
  Scenario: Tests pass
    Tool: Bash (pytest)
    Steps:
      1. uv run pytest --tb=short
    Expected Result: All tests pass
    Evidence: .sisyphus/evidence/task-2-10-tests-pass.txt

  Scenario: Linting passes
    Tool: Bash (python)
    Steps:
      1. uv run python tests/lint/lint.py
    Expected Result: All checks passed
    Evidence: .sisyphus/evidence/task-2-10-lint-pass.txt
  ```

  **Commit**: YES
  - Message: `refactor(core): add shared utilities and consolidate duplicate code`
  - Files: All modified files in Phase 2

---

### PHASE 3: Add Async Execution Support

- [ ] 3.1. Add pytest-asyncio dependency

  **What to do**:
  - Add `pytest-asyncio` to requirements.txt
  - Add `[tool:pytest]` async mode configuration
  - Verify import works

  **Must NOT do**:
  - Do NOT add other async libraries yet

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple dependency addition
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 3.2, 3.3, 3.4)
  - **Parallel Group**: Phase 3 Wave 1
  - **Blocks**: Tasks 3.5-3.11
  - **Blocked By**: Task 2.10

  **References**:
  - `requirements.txt` - Add pytest-asyncio
  - `pytest.ini` - May need async configuration

  **Acceptance Criteria**:
  - [ ] `pytest-asyncio` in requirements.txt
  - [ ] `uv pip install -r requirements.txt` succeeds
  - [ ] Can write async test functions

  **QA Scenarios**:

  ```
  Scenario: Async test framework works
    Tool: Bash (python)
    Steps:
      1. uv run python -c "import pytest_asyncio; print('OK')"
    Expected Result: OK
    Evidence: .sisyphus/evidence/task-3-1-asyncio-import.txt
  ```

  **Commit**: NO (groups with Phase 3)

---

- [ ] 3.2. Create async tool base class

  **What to do**:
  - Create `AsyncToolExecutor` base class in `src/tools/base.py`
  - Provide async `execute()` method
  - Support both sync and async tools

  **Must NOT do**:
  - Do NOT break existing sync tools
  - Do NOT change ToolRegistry interface yet

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: New architecture pattern with backward compatibility
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 3.1, 3.3, 3.4)
  - **Parallel Group**: Phase 3 Wave 1
  - **Blocks**: Tasks 3.5-3.11
  - **Blocked By**: Task 2.10

  **References**:
  - `src/tools/registry.py` - Current tool registry
  - `src/tools/executors/*.py` - Current executor patterns

  **Acceptance Criteria**:
  - [ ] File created: `src/tools/base.py`
  - [ ] Class: `AsyncToolExecutor` with `async def execute()`
  - [ ] Documentation for sync/async pattern

  **QA Scenarios**:

  ```
  Scenario: Base class imports correctly
    Tool: Bash (python)
    Steps:
      1. uv run python -c "from src.tools.base import AsyncToolExecutor; print('OK')"
    Expected Result: OK
    Evidence: .sisyphus/evidence/task-3-2-imports.txt

  Scenario: Async execution works
    Tool: Bash (python)
    Steps:
      1. Create test async tool using base class
      2. Execute and verify result
    Expected Result: Async tool executes correctly
    Evidence: .sisyphus/evidence/task-3-2-async-works.txt
  ```

  **Commit**: NO (groups with Phase 3)

---

- [ ] 3.3. Update ToolRegistry for async support

  **What to do**:
  - Add `execute_async()` method to ToolRegistry
  - Keep `execute()` for sync tools
  - Handle both sync and async executors
  - Maintain approval and rate limiting for async

  **Must NOT do**:
  - Do NOT break existing `execute()` method
  - Do NOT change tool definitions

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Core registry modification with backward compatibility
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 3.1, 3.2, 3.4)
  - **Parallel Group**: Phase 3 Wave 1
  - **Blocks**: Tasks 3.5-3.11
  - **Blocked By**: Task 2.10

  **References**:
  - `src/tools/registry.py:115-195` - Current execute() method
  - `src/tools/approval.py` - Approval checking
  - `src/security/rate_limiter.py` - Rate limiting

  **Acceptance Criteria**:
  - [ ] `execute_async()` method added
  - [ ] Approval checked before async execution
  - [ ] Rate limiting works with async
  - [ ] Sync `execute()` still works

  **QA Scenarios**:

  ```
  Scenario: Sync tools still work
    Tool: Bash (python)
    Steps:
      1. uv run pytest tests/unit/test_tools.py -v
    Expected Result: All existing tests pass
    Evidence: .sisyphus/evidence/task-3-3-sync-works.txt

  Scenario: Async execute method exists
    Tool: Bash (python)
    Steps:
      1. uv run python -c "from src.tools.registry import ToolRegistry; assert hasattr(ToolRegistry, 'execute_async'); print('OK')"
    Expected Result: OK
    Evidence: .sisyphus/evidence/task-3-3-async-method.txt
  ```

  **Commit**: NO (groups with Phase 3)

---

- [ ] 3.4. Add qasync to requirements.txt

  **What to do**:
  - Add `qasync` to requirements.txt
  - Add `asyncio` related dependencies if needed
  - Document qasync usage in code comments

  **Must NOT do**:
  - Do NOT modify gui.py yet

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple dependency addition
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 3.1, 3.2, 3.3)
  - **Parallel Group**: Phase 3 Wave 1
  - **Blocks**: Task 3.9
  - **Blocked By**: Task 2.10

  **References**:
  - `requirements.txt` - Add qasync
  - qasync documentation for PyQt6 integration

  **Acceptance Criteria**:
  - [ ] `qasync` in requirements.txt
  - [ ] Install succeeds
  - [ ] Import works

  **QA Scenarios**:

  ```
  Scenario: qasync imports correctly
    Tool: Bash (python)
    Steps:
      1. uv run python -c "import qasync; print('OK')"
    Expected Result: OK
    Evidence: .sisyphus/evidence/task-3-4-qasync-import.txt
  ```

  **Commit**: NO (groups with Phase 3)

---

- [ ] 3.5. Make search_web async

  **What to do**:
  - Convert `search_web` to async function
  - Use aiohttp or async ddgs for web requests
  - Keep sync wrapper for backward compatibility
  - Use `@ToolRegistry.register_async()`

  **Must NOT do**:
  - Do NOT change tool definition (JSON schema)
  - Do NOT break sync usage

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Network I/O optimization with backward compatibility
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 3.6, 3.7, 3.8)
  - **Parallel Group**: Phase 3 Wave 2
  - **Blocks**: Tasks 3.9-3.11
  - **Blocked By**: Tasks 3.1-3.4

  **References**:
  - `src/tools/executors/web_tools.py` - Current sync implementation
  - `src/tools/base.py` - AsyncToolExecutor base class
  - ddgs library async support

  **Acceptance Criteria**:
  - [ ] `execute_search_web_async()` created
  - [ ] Sync wrapper `execute_search_web()` still works
  - [ ] Tool definition unchanged
  - [ ] Web search tests pass

  **QA Scenarios**:

  ```
  Scenario: Async web search works
    Tool: Bash (python)
    Steps:
      1. uv run python -c "
import asyncio
from src.tools.executors.web_tools import execute_search_web_async
result = asyncio.run(execute_search_web_async('test'))
print('OK')
"
    Expected Result: OK (or valid search result)
    Evidence: .sisyphus/evidence/task-3-5-async-works.txt

  Scenario: Sync web search still works
    Tool: Bash (python)
    Steps:
      1. uv run pytest tests/unit/test_tools.py -k web -v
    Expected Result: Tests pass
    Evidence: .sisyphus/evidence/task-3-5-sync-works.txt
  ```

  **Commit**: NO (groups with Phase 3)

---

- [ ] 3.6. Make parse_document async

  **What to do**:
  - Convert `parse_document` to async function
  - Use async file operations
  - Keep sync wrapper for backward compatibility
  - Consider Docling async support

  **Must NOT do**:
  - Do NOT change tool definition
  - Do NOT break document parsing behavior

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: File I/O + CPU intensive operation
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 3.5, 3.7, 3.8)
  - **Parallel Group**: Phase 3 Wave 2
  - **Blocks**: Tasks 3.9-3.11
  - **Blocked By**: Tasks 3.1-3.4

  **References**:
  - `src/tools/executors/document_tools.py` - Current sync implementation
  - `src/tools/base.py` - AsyncToolExecutor base class
  - Docling library for document parsing

  **Acceptance Criteria**:
  - [ ] `execute_parse_document_async()` created
  - [ ] Sync wrapper still works
  - [ ] Tool definition unchanged
  - [ ] Document parsing tests pass

  **QA Scenarios**:

  ```
  Scenario: Async document parsing works
    Tool: Bash (python)
    Steps:
      1. Create test PDF file
      2. Run async parse_document
      3. Verify content extracted
    Expected Result: Content extracted correctly
    Evidence: .sisyphus/evidence/task-3-6-async-works.txt

  Scenario: Sync document parsing still works
    Tool: Bash (python)
    Steps:
      1. uv run pytest tests/unit/test_tools.py -k document -v
    Expected Result: Tests pass
    Evidence: .sisyphus/evidence/task-3-6-sync-works.txt
  ```

  **Commit**: NO (groups with Phase 3)

---

- [ ] 3.7. Make code_search async

  **What to do**:
  - Convert `code_search` to async function
  - Use asyncio.create_subprocess_exec for ripgrep
  - Keep sync wrapper for backward compatibility

  **Must NOT do**:
  - Do NOT change tool definition
  - Do NOT break ripgrep functionality

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: File system I/O can be slow on large codebases
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 3.5, 3.6, 3.8)
  - **Parallel Group**: Phase 3 Wave 2
  - **Blocks**: Tasks 3.9-3.11
  - **Blocked By**: Tasks 3.1-3.4

  **References**:
  - `src/tools/executors/system_tools.py` - Current sync implementation
  - `src/tools/base.py` - AsyncToolExecutor base class
  - `src/core/subprocess_utils.py` - Async subprocess support

  **Acceptance Criteria**:
  - [ ] `execute_code_search_async()` created
  - [ ] Sync wrapper still works
  - [ ] Tool definition unchanged
  - [ ] Code search tests pass

  **QA Scenarios**:

  ```
  Scenario: Async code search works
    Tool: Bash (python)
    Steps:
      1. uv run python -c "
import asyncio
from src.tools.executors.system_tools import execute_code_search_async
result = asyncio.run(execute_code_search_async('def main'))
print('OK')
"
    Expected Result: OK (or valid search results)
    Evidence: .sisyphus/evidence/task-3-7-async-works.txt

  Scenario: Sync code search still works
    Tool: Bash (python)
    Steps:
      1. uv run pytest tests/unit/test_tools.py -k code_search -v
    Expected Result: Tests pass
    Evidence: .sisyphus/evidence/task-3-7-sync-works.txt
  ```

  **Commit**: NO (groups with Phase 3)

---

- [ ] 3.8. Make git tools async

  **What to do**:
  - Convert `git_status`, `git_diff`, `git_log` to async
  - Use asyncio.create_subprocess_exec for git commands
  - Keep sync wrappers for backward compatibility

  **Must NOT do**:
  - Do NOT change tool definitions
  - Do NOT break git functionality

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Git operations can be slow on large repos
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 3.5, 3.6, 3.7)
  - **Parallel Group**: Phase 3 Wave 2
  - **Blocks**: Tasks 3.9-3.11
  - **Blocked By**: Tasks 3.1-3.4

  **References**:
  - `src/tools/executors/git_tools.py` - Current sync implementations
  - `src/tools/base.py` - AsyncToolExecutor base class
  - `src/core/subprocess_utils.py` - Async subprocess support

  **Acceptance Criteria**:
  - [ ] `execute_git_status_async()`, `execute_git_diff_async()`, `execute_git_log_async()` created
  - [ ] Sync wrappers still work
  - [ ] Tool definitions unchanged
  - [ ] Git tool tests pass

  **QA Scenarios**:

  ```
  Scenario: Async git tools work
    Tool: Bash (python)
    Steps:
      1. uv run python -c "
import asyncio
from src.tools.executors.git_tools import execute_git_status_async
result = asyncio.run(execute_git_status_async())
print('OK')
"
    Expected Result: OK (or valid git status)
    Evidence: .sisyphus/evidence/task-3-8-async-works.txt

  Scenario: Sync git tools still work
    Tool: Bash (python)
    Steps:
      1. uv run pytest tests/unit/test_tools.py -k git -v
    Expected Result: Tests pass
    Evidence: .sisyphus/evidence/task-3-8-sync-works.txt
  ```

  **Commit**: NO (groups with Phase 3)

---

- [ ] 3.9. Integrate qasync in gui.py

  **What to do**:
  - Update gui.py to use qasync for event loop integration
  - Ensure async tools can be called from GUI
  - Add async event loop to QApplication

  **Must NOT do**:
  - Do NOT break existing GUI functionality
  - Do NOT change GUI layout or widgets

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: GUI integration with async event loop
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on 3.5-3.8)
  - **Parallel Group**: Sequential
  - **Blocks**: Tasks 3.10, 3.11
  - **Blocked By**: Tasks 3.1-3.8

  **References**:
  - `src/gui.py` - Current PyQt6 implementation
  - qasync documentation for QApplication integration
  - `src/core/chat_loop.py` - Where async tools are called

  **Acceptance Criteria**:
  - [ ] qasync event loop integrated with QApplication
  - [ ] GUI can call async tools
  - [ ] GUI still responsive during async operations

  **QA Scenarios**:

  ```
  Scenario: GUI starts without errors
    Tool: Bash (python)
    Steps:
      1. timeout 5 uv run python launcher.py --gui 2>&1 | head -20
    Expected Result: GUI starts, no qasync errors
    Evidence: .sisyphus/evidence/task-3-9-gui-starts.txt

  Scenario: Async tools callable from GUI
    Tool: interactive_bash (tmux)
    Steps:
      1. Start GUI
      2. Send message that triggers async tool
      3. Verify response received
    Expected Result: Async tool executes and returns result
    Evidence: .sisyphus/evidence/task-3-9-gui-async.png
  ```

  **Commit**: NO (groups with Phase 3)

---

- [ ] 3.10. Test async tools in GUI

  **What to do**:
  - Manual testing of each async tool in GUI
  - Verify no blocking of GUI thread
  - Test error handling for async tools
  - Capture evidence of async execution

  **Must NOT do**:
  - Do NOT modify GUI code (just test)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Thorough testing required
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on 3.9)
  - **Parallel Group**: Sequential
  - **Blocks**: Task 3.11
  - **Blocked By**: Task 3.9

  **References**:
  - `src/gui.py` - GUI to test
  - Async tools from 3.5-3.8

  **Acceptance Criteria**:
  - [ ] search_web works in GUI without blocking
  - [ ] parse_document works in GUI without blocking
  - [ ] code_search works in GUI without blocking
  - [ ] git tools work in GUI without blocking

  **QA Scenarios**:

  ```
  Scenario: Test all 4 async tools in GUI
    Tool: interactive_bash (tmux + playwright)
    Steps:
      1. Start GUI
      2. Test "search the web for ..." (search_web)
      3. Test "parse this document" (parse_document)
      4. Test "find all TODO comments" (code_search)
      5. Test "what changed in git" (git tools)
    Expected Result: All 4 tools execute correctly, GUI remains responsive
    Evidence: .sisyphus/evidence/task-3-10-gui-async-test.png
  ```

  **Commit**: NO (groups with Phase 3)

---

- [ ] 3.11. Run Full Test Suite (Phase 3 Checkpoint)

  **What to do**:
  - Run `uv run pytest` to verify all tests pass
  - Run `uv run python tests/lint/lint.py` for code quality
  - Verify async tests are included
  - Document final test count

  **Must NOT do**:
  - Do NOT skip any tests
  - Do NOT ignore errors

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Standard test execution
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: NO (Phase 3 checkpoint)
  - **Parallel Group**: Sequential
  - **Blocks**: Final Verification Wave
  - **Blocked By**: Tasks 3.5-3.10

  **References**:
  - pytest.ini for test configuration

  **Acceptance Criteria**:
  - [ ] All tests pass (730+ tests)
  - [ ] No linting errors
  - [ ] Async tests included in results

  **QA Scenarios**:

  ```
  Scenario: Final test suite passes
    Tool: Bash (pytest)
    Steps:
      1. uv run pytest --tb=short
    Expected Result: All tests pass
    Evidence: .sisyphus/evidence/task-3-11-tests-pass.txt

  Scenario: Final linting passes
    Tool: Bash (python)
    Steps:
      1. uv run python tests/lint/lint.py
    Expected Result: All checks passed
    Evidence: .sisyphus/evidence/task-3-11-lint-pass.txt
  ```

  **Commit**: YES
  - Message: `feat(tools): add async execution support with qasync integration`
  - Files: All modified files in Phase 3

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns. Check evidence files exist in .sisyphus/evidence/.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `uv run python tests/lint/lint.py`. Review all changed files for unused imports, dead code, type safety.
  Output: `Lint [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Manual QA - CLI** — `unspecified-high`
  Start CLI, test `/populate`, `/web`, async tools. Verify no regressions.
  Evidence: `.sisyphus/evidence/final-qa-cli.log`

- [ ] F4. **Manual QA - GUI** — `unspecified-high`
  Start GUI, test all commands including async tools. Verify qasync integration works.
  Evidence: `.sisyphus/evidence/final-qa-gui.log`

---

## Commit Strategy

- **Phase 1**: `refactor(commands): complete populate and web handler extraction`
- **Phase 2**: `refactor(core): add shared utilities and consolidate duplicate code`
- **Phase 3**: `feat(tools): add async execution support with qasync integration`

---

## Success Criteria

### Verification Commands

```bash
# Test suite passes
uv run pytest
# Expected: 730+ tests, 0 failures

# Linting passes
uv run python tests/lint/lint.py
# Expected: All checks passed

# No circular imports
uv run python -c "from src.commands.handlers.learning_commands import handle_populate, handle_web; print('OK')"
# Expected: OK (no ImportError)

# Shared utilities exist
uv run python -c "from src.core.security_utils import validate_path, sanitize_path; print('OK')"
# Expected: OK

uv run python -c "from src.core.subprocess_utils import run_command, get_safe_env; print('OK')"
# Expected: OK

# Async tool support
uv run python -c "from src.tools.registry import ToolRegistry; print('sync' if hasattr(ToolRegistry, 'execute') else 'missing')"
# Expected: sync

uv run python -c "from src.tools.registry import ToolRegistry; print('async' if hasattr(ToolRegistry, 'execute_async') else 'missing')"
# Expected: async
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass (730+)
- [ ] Linting passes (0 issues)
- [ ] No circular imports
- [ ] Async tools work in CLI
- [ ] Async tools work in GUI
