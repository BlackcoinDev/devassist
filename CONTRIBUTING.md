# Contributing to DevAssist

Thank you for your interest in contributing to DevAssist!

## Development Setup

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- LM Studio (for local LLM)
- ChromaDB v2 server
- Ollama (for embeddings)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/BlackcoinDev/devassist.git
cd devassist

# Create virtual environment
uv venv venv --python 3.12
source venv/bin/activate  # Linux/macOS
# or: venv\\Scripts\\activate  # Windows

# Install dependencies
uv pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Required: LM_STUDIO_URL, CHROMA_HOST, OLLAMA_BASE_URL

# Run the application
uv run python launcher.py --cli  # CLI mode
uv run python launcher.py --gui  # GUI mode
```

## Development Workflow

### Running Tests

```bash
# All tests (~817 tests, ~45s)
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=term-missing

# Specific test file
uv run pytest tests/unit/test_main.py

# Linting (REQUIRED before commit)
uv run python tests/lint/lint.py
```

### Code Style

- **Line length**: Max 100 characters
- **Type hints**: Required for new code
- **Imports**: Grouped (stdlib, third-party, local) with blank lines
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Error handling**: Specific exception types, proper logging

### Pre-commit Checklist

Before submitting a PR, ensure:

1. [ ] All tests pass: `uv run pytest`
2. [ ] Linting passes: `uv run python tests/lint/lint.py`
3. [ ] No new type errors introduced
4. [ ] Documentation updated if needed
5. [ ] Commit message follows conventions

## Documentation Guidelines

### Single Source Principle

To prevent documentation drift, follow these rules:

| Content Type | Where to Document |
|--------------|------------------|
| Architecture diagrams | `docs/ARCHITECTURE.md` |
| User commands/usage | `docs/MANUAL.md` |
| API reference | `docs/API_DOCUMENTATION.md` |
| Feature overview | `README.md` |
| AI agent context | `AGENTS.md` |

### Counting Things in Docs

**IMPORTANT**: When documenting counts (tests, tools, handlers), use the validation script:

```bash
uv run python tests/lint/docs_consistency.py
```

This ensures documentation matches actual code. If counts are wrong, fix the docs, not the validation.

### Adding New Features

1. **Code first**: Implement the feature
2. **Add tests**: Ensure test coverage
3. **Update docs**: Follow single-source principle
4. **Validate**: Run `docs_consistency.py`
5. **Update AGENTS.md**: Last - affects AI behavior

### Documentation Files

| File | Purpose | When to Update |
|------|---------|----------------|
| `README.md` | User-facing overview | New features, major changes |
| `AGENTS.md` | AI agent context | Any feature/tool change |
| `docs/ARCHITECTURE.md` | Technical architecture | Structural changes |
| `docs/MANUAL.md` | User guide | Command changes, new usage |
| `docs/MIGRATION.md` | Upgrade guide | Version changes |

## Git Conventions

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code improvements

### Commit Messages

```
type: short description

Longer description if needed.

Fixes #123
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

### Pull Requests

1. Create feature branch from `main`
2. Make changes following code style
3. Add tests for new functionality
4. Update documentation
5. Run full test suite
6. Submit PR with description

## Security Guidelines

### Never Commit

- API keys or secrets
- Credentials or tokens
- Environment files with real values
- Passwords or private information

### Use Environment Variables

All sensitive configuration should use `.env`:

```bash
# .env.example (safe to commit)
LM_STUDIO_URL=http://localhost:1234
CHROMA_HOST=localhost
```

### Rate Limiting

When adding new tools, consider adding rate limits in `src/security/rate_limiter.py`.

## Getting Help

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- Join discussions in GitHub Discussions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
