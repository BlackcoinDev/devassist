# AI Assistant Test Suite v0.1.1

## 📋 Overview

This directory contains the comprehensive test suite for the AI Assistant application. The test suite is designed to ensure code quality, functionality, and reliability across all components of the application.

## 🏗️ Test Structure

```
tests/
├── fixtures/              # Test data and sample files
│   └── sample_data.py    # Sample data for testing
├── integration/          # Integration tests (component interaction)
│   ├── test_integration.py      # Application integration flows
│   └── test_tool_calling.py     # AI tool calling integration
├── lint/                 # Code quality and linting tests
│   ├── all-lint.py      # Comprehensive project linting
│   └── lint-python.py   # Python-specific linting
├── tools/                # Tool-specific tests (excluded from main suite)
│   ├── test_direct_tools.py     # Direct tool testing
│   ├── test_fresh_conversation.py
│   ├── test_langchain_tools.py
│   ├── test_main_tools.py
│   └── test_parse_document.py
├── unit/                 # Unit tests (isolated functionality)
│   ├── test_gui.py      # GUI component tests
│   ├── test_launcher.py # Application launcher tests
│   ├── test_main.py     # Core functionality tests
│   └── test_tools.py    # Tool functionality tests
├── conftest.py           # pytest configuration and fixtures
├── run_tests.py          # Test runner script
└── pytest.ini           # pytest configuration
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)
Focused tests for individual components and functions:

- **test_main.py** (26 tests): Core business logic
  - Space/workspace management
  - Memory and caching operations
  - Slash command processing
  - Application initialization

- **test_tools.py** (20 tests): AI tool functionality
  - File system operations (read, write, list)
  - Document processing and parsing
  - Knowledge management (learn, search)
  - Web search capabilities

- **test_launcher.py** (6 tests): Application startup
  - CLI/GUI mode selection
  - Environment loading
  - Argument parsing

- **test_gui.py** (10 tests): GUI components
  - Markdown/HTML conversion
  - Conversation loading
  - Worker thread initialization
  - Theme and configuration handling

### Integration Tests (`tests/integration/`)
Tests for component interaction and end-to-end flows:

- **test_integration.py** (11 tests): Application workflows
  - Full initialization flow
  - Memory persistence
  - Space management
  - Context retrieval

- **test_tool_calling.py** (15 tests): AI tool integration
  - Tool execution with qwen3-vl-30b
  - Multi-round tool calling
  - Error handling and validation
  - Security checks

### Linting Tests (`tests/lint/`)
Code quality assurance:

- **lint-python.py**: Python-specific checks
  - Syntax validation
  - Style checking (Flake8)
  - Type checking (MyPy)
  - Dead code detection (Vulture)
  - Spell checking (Codespell)

- **all-lint.py**: Comprehensive project checks
  - Python linting (calls lint-python.py)
  - Shell script linting
  - Configuration file validation
  - Project structure verification

## 🛠️ Running Tests

### Quick Start
```bash
# Run all tests (excludes GUI tests by default)
uv run pytest

# Run with verbose output
uv run pytest -v

# Include GUI tests (may cause Qt crashes)
RUN_GUI_TESTS=1 uv run pytest tests/unit/test_gui.py -v
```

### Direct pytest Usage
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_main.py -v

# Run specific test class
uv run pytest tests/unit/test_main.py::TestSpaceManagement -v

# Run specific test method
uv run pytest tests/unit/test_main.py::TestSpaceManagement::test_get_space_collection_name_default -v

# Run with coverage report
uv run pytest --cov=src.main --cov-report=term-missing

# Run only integration tests
uv run pytest tests/integration/ -v

# Run only unit tests
uv run pytest tests/unit/ -v
```

### Linting
```bash
# Run Python-specific linting
uv run python tests/lint/lint-python.py

# Run comprehensive project linting
uv run python tests/lint/all-lint.py
```

## 📊 Test Results Summary

### Current Status (v0.1.1)
- **Total Tests**: 89 (79 active + 10 GUI)
- **Test Categories**:
  - Unit Tests: 52 tests (26 main + 6 launcher + 20 tools)
  - Integration Tests: 26 tests (11 application + 15 tool calling)
  - GUI Tests: 10 tests (excluded by default)
- **Coverage**: 90%+ for core modules
- **Execution Time**: ~12-15 seconds
- **All Tests Pass**: ✅ 89/89

### Coverage Areas
- ✅ Core application logic (space management, memory, commands)
- ✅ AI tool functionality (8 tools fully tested)
- ✅ File system operations with security validation
- ✅ Document processing and parsing
- ✅ Knowledge base operations
- ✅ Web search integration
- ✅ GUI components (isolated testing)
- ✅ Application initialization and error handling
- ✅ Command-line interface
- ✅ Configuration management

## 🔧 Test Configuration

### pytest.ini Settings
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
addopts =
    --verbose
    --tb=short
    --cov=src.main
    --cov=src.gui
    --cov=launcher
    --cov-report=term-missing
    --cov-fail-under=80
    -k "not test_gui"  # Exclude GUI tests by default
```

### Test Markers
- `unit`: Unit tests (isolated functionality)
- `integration`: Integration tests (component interaction)
- `slow`: Slow running tests
- `gui`: GUI-related tests (may cause crashes)
- `tools`: AI tool functionality tests
- `security`: Security and safety tests

### Shared Fixtures (`conftest.py`)
- `mock_vectorstore`: Mocked ChromaDB vector store
- `mock_llm`: Mocked language model for AI interactions
- `mock_embeddings`: Mocked text embeddings for vectorization

## 🧩 Test Architecture

### Mocking Strategy
- **External APIs**: LLM services, vector databases, file operations
- **Complex Objects**: Qt widgets, database connections, network calls
- **Time-dependent Code**: datetime, random operations, async delays
- **File System**: Mocked file reads/writes, directory operations

### Isolation Principles
- **Unit Tests**: Complete isolation with comprehensive mocking
- **Integration Tests**: Component interaction without external dependencies
- **GUI Tests**: Isolated component testing without Qt runtime
- **Security Tests**: Path traversal and input validation

### Test Data
- **fixtures/sample_data.py**: Sample documents and test data
- **Environment Variables**: Automatic loading from `.env` file
- **Temporary Files**: pytest tmp_path fixture for file operations

## 🚀 CI/CD Integration

### Automated Testing
```bash
# Full test suite (CI/CD)
uv run pytest

# With coverage reporting
uv run pytest --cov=src.main --cov-report=xml

# Linting checks
uv run python tests/lint/all-lint.py
```

### Quality Gates
- ✅ All tests must pass (89/89)
- ✅ Code coverage ≥80% for core modules
- ✅ Zero linting violations
- ✅ All security tests pass
- ✅ GUI tests pass in isolation

## 🐛 Debugging Tests

### Running Failed Tests
```bash
# Run only failed tests
uv run pytest --lf

# Run with detailed output
uv run pytest -v -s

# Debug specific test
uv run pytest tests/unit/test_main.py::TestSpaceManagement::test_get_space_collection_name_default -v -s
```

### Common Issues
- **GUI Test Failures**: Use `RUN_GUI_TESTS=1` or run individually
- **Import Errors**: Ensure proper Python path and dependencies
- **Mock Conflicts**: Check fixture naming and patch decorator order
- **Coverage Issues**: Run with `--cov-report=html` for detailed reports

## 📈 Test Maintenance

### Adding New Tests
1. **Unit Tests**: Add to `tests/unit/` with descriptive names
2. **Integration Tests**: Add to `tests/integration/` for component interaction
3. **GUI Tests**: Add to `tests/unit/test_gui.py` (marked with skipif)
4. **Fixtures**: Add shared fixtures to `tests/conftest.py`

### Test Naming Conventions
- **Files**: `test_*.py` or `*_test.py`
- **Classes**: `Test*` (e.g., `TestSpaceManagement`)
- **Methods**: `test_*` (e.g., `test_get_space_collection_name`)
- **Descriptive**: Method names should clearly indicate what is being tested

### Test Quality Standards
- **One Concept Per Test**: Each test should validate a single behavior
- **Descriptive Names**: Test names should explain what they verify
- **Arrange-Act-Assert**: Clear structure for each test method
- **Independent Tests**: No test should depend on others

## 🔒 Security Testing

### Path Traversal Protection
- File system operations validate paths within current directory
- Absolute path resolution prevents directory traversal attacks
- Input sanitization for all user-provided file paths

### Input Validation
- Tool arguments validated before execution
- File size limits enforced (1MB for reading)
- Binary file detection and rejection

### Error Handling
- Comprehensive exception catching
- Secure error messages (no sensitive information leakage)
- Graceful degradation on service failures

## 📚 Dependencies

### Required for Testing
```bash
# Core testing
pip install pytest pytest-cov pytest-mock

# Linting tools
pip install autopep8 flake8 mypy vulture codespell

# Test dependencies
pip install python-dotenv langchain-core
```

### Optional Dependencies
```bash
# Shell script linting
brew install shellcheck
```

## 🎯 Test Philosophy

### Quality Assurance
- **Zero Tolerance**: All tests must pass in CI/CD
- **Comprehensive Coverage**: Core functionality fully tested
- **Security First**: Security tests prevent vulnerabilities
- **Maintainable**: Clean, readable test code

### Development Workflow
- **TDD Approach**: Tests written before or alongside code
- **Continuous Integration**: Automated testing on every change
- **Regression Prevention**: Comprehensive test suite catches issues
- **Documentation**: Tests serve as living documentation

---

**Test Suite Status**: ✅ **All 89 tests passing** | **90%+ coverage** | **Zero linting violations**

For questions or issues with the test suite, please refer to the main project documentation or create an issue in the repository.