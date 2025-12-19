# Linting Tools - DevAssist Project

This directory contains the comprehensive linting suite for the DevAssist project. All tools are designed to work with
**UV** for dependency management and virtual environment handling.

## 📁 File Overview

### Core Linting Files

- **`all-lint.py`** - Master orchestrator (Python, Markdown, Shell, Config)
- **`lint-python.py`** - Python specialist (94 files, 6 tools)
- **`lint-markdown.py`** - Markdown specialist + MD060 tables (17 files)
- **`fix-markdown.py`** - Auto-fix engine (25+ rules, 96% auto-fixable)
- **`table_utils.py`** - Shared utilities (table parsing, MD060 validation)

## 🔧 Quick Start

```bash

# Comprehensive linting (recommended)

uv run python tests/lint/all-lint.py

# Comprehensive linting with auto-fix

uv run python tests/lint/all-lint.py --fix-markdown
uv run python tests/lint/all-lint.py --fix-all

# Individual linters

uv run python tests/lint/lint-python.py
uv run python tests/lint/lint-markdown.py

# Auto-fix markdown issues manually

uv run python tests/lint/fix-markdown.py README.md

## 📋 Detailed File Documentation

### `all-lint.py` - Master Orchestrator

**Purpose:** Entry point for comprehensive project-wide linting.

**What it does:**

- Calls all specialized linters in sequence
- Validates project structure and configuration
- Provides unified reporting and exit codes
- Checks shell scripts (if shellcheck is available)
- **Auto-fix options:** `--fix-markdown` or `--fix-all` to automatically fix markdown issues

**Execution:**

```bash

# Standard linting (reports issues only)

uv run python tests/lint/all-lint.py

# Auto-fix markdown issues after linting

uv run python tests/lint/all-lint.py --fix-markdown

# Auto-fix all supported issues (currently markdown only)

uv run python tests/lint/all-lint.py --fix-all

**Checks performed:**

- 🐍 Python linting (via `lint-python.py`)
- 📄 Markdown linting (via `lint-markdown.py`)
- 🐚 Shell scripts (via shellcheck)
- ⚙️ Configuration files (.env, required files)
- 📁 Project structure validation

### `lint-python.py` - Python Code Quality

**Purpose:** Comprehensive Python code analysis and quality assurance.

**Tools used:**

- **Py_compile:** Syntax validation
- **Flake8:** Style checking (PEP8, errors, complexity)
- **AutoPEP8:** Code formatting validation
- **MyPy:** Static type checking
- **Vulture:** Dead code detection
- **Codespell:** Spelling validation

**Execution:**

```bash
uv run python tests/lint/lint-python.py

**Coverage:** All 93 Python files in the project (excluding venv, cache directories).

**Exit behavior:** Returns non-zero exit code if any issues found.

### `lint-markdown.py` - Markdown Quality + MD060 Tables

**Purpose:** Markdown linting with integrated table alignment checking.

**Features:**

- **Standard markdown linting** via PyMarkdown
- **Custom MD060 table checking** for column alignment
- **Detailed error reporting** with fix suggestions

**Execution:**

```bash

# Check all project markdown files

uv run python tests/lint/lint-markdown.py

# Check specific files/directories

uv run python tests/lint/lint-markdown.py README.md docs/

**Coverage:** All 17 markdown files in the project.

**Special feature:** Detects table pipe misalignment and suggests fixes using `fix-markdown.py`.

### `fix-markdown.py` - Auto-Fix Engine

**Purpose:** Three-phase markdown auto-correction system.

**Architecture:**

- **Phase 1:** PyMarkdown native fixes (16+ rules)
- **Phase 2:** Custom Python logic fixes (8 complex rules)
- **Phase 3:** Table alignment (MD060) using `TableAligner` class

**Execution:**

```bash

# Fix specific file

uv run python tests/lint/fix-markdown.py README.md

# Fix all files in directory

uv run python tests/lint/fix-markdown.py docs/

# Dry run (see what would be changed)

uv run python tests/lint/fix-markdown.py --dry-run README.md
```text

**Coverage:** 96% of markdown issues auto-fixable (25+ rules).

### `table_utils.py` - Shared Table Utilities

**Purpose:** Common table processing functions used by both linting and fixing tools.

**Shared Functions:**

- `find_table_blocks()` - Locate table blocks in markdown content
- `parse_table_rows()` - Parse table lines into structured cell data
- `calculate_column_widths()` - Compute max widths for MD060 compliance
- `check_md060_compliance()` - Validate table alignment (used by `lint-markdown.py`)
- `validate_table_alignment()` - Detailed table validation
- `visual_width()` - Unicode-aware text width calculation

**Integration:** Both `lint-markdown.py` and `fix-markdown.py` import and use these shared utilities, ensuring
consistent table processing logic.

## 🔄 How Files Work Together

```bash
User runs: uv run python tests/lint/all-lint.py
    ↓
all-lint.py orchestrates:
    ├── uv run python tests/lint/lint-python.py
    │   └── Scans all Python files with 6 specialized tools
    │
    ├── uv run python tests/lint/lint-markdown.py
    │   ├── Standard PyMarkdown scanning
    │   └── Custom MD060 table alignment checking
    │       └── Suggests: uv run python tests/lint/fix-markdown.py
    │
    ├── Shell script checking (shellcheck)
    └── Configuration validation

When issues found:
    uv run python tests/lint/fix-markdown.py [file]
        └── Uses TableAligner for MD060 table fixing

## ⚙️ Configuration

### Directory Exclusions (All Tools)

All linting tools automatically exclude these directories:

- `__pycache__`, `.git`, `venv`, `node_modules`
- `faiss_index`, `chroma_data`, `blackcoin-more`, `.pytest_cache`

### Markdown Configuration

- Uses `.pymarkdown` config file in project root
- Line length: 120 characters
- Custom MD060 table alignment validation

### Python Configuration

- Uses `mypy.ini` for type checking configuration
- Line length: 150 characters (Flake8)
- Extensive exclusions for generated/dependency code

## 🚀 Best Practices

### Development Workflow

1. **Pre-commit:** `uv run python tests/lint/all-lint.py`
2. **Fix issues:** Use auto-fix tools where available
3. **Verify:** Re-run linting to confirm fixes
4. **CI/CD:** All tools return proper exit codes

### Performance Tips

- **Individual linters** run faster than comprehensive linting
- **Auto-fix** resolves most markdown issues instantly
- **MD060 checking** is fast and doesn't impact performance

### Common Issues

- **Shellcheck not found:** Install with `brew install shellcheck`
- **Tools missing:** All dependencies listed in project `requirements.txt`
- **Permission issues:** Run with appropriate file permissions

## 📊 Coverage Statistics

- **Python files:** 94 files scanned
- **Markdown files:** 17 files scanned
- **Shared utilities:** 1 module (table_utils.py)
- **Auto-fixable rules:** 96% (25+ markdown rules)
- **MD060 coverage:** Complete table alignment validation
- **Execution time:** ~30 seconds for comprehensive linting

## 🔍 Troubleshooting

### Exit Codes

- **0:** Success - no issues found
- **Non-zero:** Issues found - check output for details

### Verbose Output

```bash

# See detailed output

uv run python tests/lint/all-lint.py 2>&1

```text

### Selective Testing

```bash

# Test only Python linting

uv run python tests/lint/lint-python.py

# Test only markdown linting

uv run python tests/lint/lint-markdown.py

---

**Always use `uv run python` for all linting commands!** 🎯

For questions about specific linting rules or tool configurations, check the individual tool documentation or the main
project AGENTS.md file.
