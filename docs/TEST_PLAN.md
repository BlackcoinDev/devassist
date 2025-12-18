# Comprehensive Test Plan for Modular Architecture v0.2.0

**Document Version:** 1.0
**Created:** 2025-12-18
**Status:** Planning Phase
**Target Coverage:** 90%+ for all modular components

---

## Executive Summary

This document outlines the comprehensive testing strategy for DevAssist's modular architecture (v0.2.0). The modular refactoring extracted ~2,995 lines of code into 37 focused modules, but currently has 0% test coverage for new components.

**Current Test Status:**
- **Total Tests:** 256 (collected)
- **Passing:** 256 passed (including Phase 5 unit test expansion)
- **Broken:** 0 tests
- **Coverage:** ~64% overall (Core components verified at >90%)

**Target State:**
- **Total Tests:** ~300+ tests
- **Coverage:** 90%+ for all modules
- **Estimated Effort:** 20-30 hours of test development

---

## 1. CRITICAL PRIORITY - Core Infrastructure

### 1.1 ApplicationContext (src/core/context.py) - 295 lines

**Status:** ✅ 15+ tests | **Priority:** P0 (CRITICAL)
**Target:** 15 tests | **Estimated Time:** 2-3 hours

The ApplicationContext is the dependency injection container that all modules depend on.

#### Test File: `tests/unit/test_application_context.py`

**Test Classes:**
1. **TestContextInitialization** (5 tests)
   - `test_initialize_creates_context` - Verify context object creation
   - `test_initialize_loads_config` - Verify configuration loading from .env
   - `test_initialize_with_invalid_config` - Handle missing .env gracefully
   - `test_initialize_sets_up_llm` - Verify LLM initialization
   - `test_initialize_connects_to_chroma` - Verify ChromaDB connection

2. **TestContextGetters** (5 tests)
   - `test_get_context_returns_singleton` - Verify singleton pattern
   - `test_get_config_returns_config_object` - Verify config accessor
   - `test_get_llm_returns_llm_instance` - Verify LLM accessor
   - `test_get_vectorstore_returns_vectorstore` - Verify vectorstore accessor
   - `test_get_conversation_history_returns_history` - Verify history accessor

3. **TestContextLifecycle** (5 tests)
   - `test_context_cleanup_closes_connections` - Verify cleanup
   - `test_context_is_initialized_check` - Verify initialization state
   - `test_context_reinitialize_after_cleanup` - Verify re-initialization
   - `test_context_thread_safety` - Verify thread-safe access
   - `test_context_lazy_loading` - Verify lazy initialization of components

**Mocking Strategy:**
- Mock LM Studio connection
- Mock ChromaDB connection
- Mock .env file loading
- Use temporary files for testing

---

### 1.2 Configuration Management (src/core/config.py) - 319 lines

**Status:** ✅ 12+ tests | **Priority:** P0 (CRITICAL)
**Target:** 12 tests | **Estimated Time:** 2 hours

Configuration loading and validation is critical for application startup.

#### Test File: `tests/unit/test_config.py`

**Test Classes:**
1. **TestConfigLoading** (5 tests)
   - `test_load_config_from_env` - Load all required variables
   - `test_load_config_with_missing_required` - Handle missing variables
   - `test_load_config_with_defaults` - Apply default values
   - `test_load_config_validates_types` - Type validation (int, bool, str)
   - `test_load_config_from_custom_path` - Load from non-default .env

2. **TestConfigValidation** (4 tests)
   - `test_validate_url_format` - Validate LM_STUDIO_URL format
   - `test_validate_port_range` - Validate CHROMA_PORT range (1-65535)
   - `test_validate_model_name_not_empty` - Validate MODEL_NAME required
   - `test_validate_temperature_range` - Validate TEMPERATURE (0.0-2.0)

3. **TestConfigAccessors** (3 tests)
   - `test_get_config_value` - Get individual config values
   - `test_config_to_dict` - Export config as dictionary
   - `test_config_immutability` - Verify config cannot be modified after load

**Mocking Strategy:**
- Mock os.environ for .env variables
- Use tempfile for temporary .env files
- Mock validation failures

---

### 1.3 Context Utilities (src/core/context_utils.py) - 313 lines

**Status:** ✅ 10+ tests | **Priority:** P1 (HIGH)
**Target:** 18 tests | **Estimated Time:** 3 hours

Shared utility functions used across the application.

#### Test File: `tests/unit/test_context_utils.py`

**Test Classes:**
1. **TestKnowledgeBaseFunctions** (6 tests)
   - `test_add_to_knowledge_base` - Add text to ChromaDB
   - `test_add_to_knowledge_base_with_metadata` - Add with metadata
   - `test_add_to_knowledge_base_handles_errors` - Error handling
   - `test_get_relevant_context` - Retrieve similar documents
   - `test_get_relevant_context_with_limit` - Limit results
   - `test_get_relevant_context_empty_results` - No matches found

2. **TestConversationFunctions** (4 tests)
   - `test_save_conversation_to_history` - Save to SQLite
   - `test_load_conversation_history` - Load from SQLite
   - `test_clear_conversation_history` - Clear history
   - `test_conversation_history_limit` - Respect MAX_HISTORY_PAIRS

3. **TestMemoryFunctions** (4 tests)
   - `test_add_to_memory` - Add to Mem0
   - `test_search_memory` - Search Mem0
   - `test_get_all_memories` - Retrieve all memories
   - `test_memory_error_handling` - Handle Mem0 unavailable

4. **TestUtilityHelpers** (4 tests)
   - `test_format_tool_result` - Format tool output
   - `test_chunk_text` - Text chunking function
   - `test_sanitize_input` - Input sanitization
   - `test_validate_file_path` - File path validation

**Mocking Strategy:**
- Mock ChromaDB client
- Mock SQLite database
- Mock Mem0 client
- Use temporary directories for file operations

---

## 2. HIGH PRIORITY - Command Handlers

### 2.1 Command Handler Modules (src/commands/handlers/*.py) - 1,230 lines

**Status:** ✅ 40+ tests | **Priority:** P1 (HIGH)
**Target:** 40 tests (5 per handler) | **Estimated Time:** 6-8 hours

Eight command handler modules need individual testing.

#### Test File: `tests/unit/test_command_handlers.py`

**Modules to Test:**
1. **config_commands.py** (86 lines) - 5 tests
   - Test config display, modification, reset

2. **database_commands.py** (310 lines) - 5 tests
   - Test database operations, migrations, cleanup

3. **export_commands.py** (112 lines) - 5 tests
   - Test export to JSON, Markdown, TXT formats

4. **file_commands.py** (205 lines) - 5 tests
   - Test file operations triggered by commands

5. **help_commands.py** (88 lines) - 5 tests
   - Test help text generation, command listing

6. **legacy_commands.py** (23,867 bytes) - 20 tests
   - Test all 15 legacy command handlers
   - Verify backward compatibility
   - Test integration with new command system

7. **learning_commands.py** (110 lines) - 5 tests

6. **learning_commands.py** (110 lines) - 5 tests
   - Test /learn, /populate commands

7. **memory_commands.py** (130 lines) - 5 tests
   - Test memory operations, history management

8. **space_commands.py** (137 lines) - 5 tests
   - Test space creation, switching, deletion

**Test Strategy:**
- Mock CommandRegistry to verify registration
- Mock ApplicationContext for dependencies
- Test each command with valid/invalid arguments
- Verify output format and error messages
- Test integration with underlying systems

**Example Test Structure (per handler):**
```python
class TestConfigCommands:
    def test_register_config_commands():
        """Verify commands are registered."""

    def test_show_config_displays_current():
        """Test /config show command."""

    def test_set_config_updates_value():
        """Test /config set key=value command."""

    def test_reset_config_restores_defaults():
        """Test /config reset command."""

    def test_config_error_handling():
        """Test error handling for invalid configs."""
```

---

## 3. HIGH PRIORITY - Storage Layer

### 3.1 Database Module (src/storage/database.py) - 119 lines

**Status:** ✅ 10+ tests | **Priority:** P1 (HIGH)
**Target:** 10 tests | **Estimated Time:** 1.5 hours

#### Test File: `tests/unit/test_database.py`

**Test Classes:**
1. **TestDatabaseConnection** (4 tests)
   - `test_initialize_database` - Create db/history.db
   - `test_initialize_creates_tables` - Verify schema creation
   - `test_get_connection` - Get active connection
   - `test_connection_thread_safety` - Verify thread-safe access

2. **TestDatabaseOperations** (6 tests)
   - `test_execute_query` - Execute SQL query
   - `test_execute_query_with_params` - Parameterized query
   - `test_execute_query_error_handling` - SQL error handling
   - `test_commit_transaction` - Commit changes
   - `test_rollback_transaction` - Rollback on error
   - `test_close_connection` - Clean shutdown

---

### 3.2 Memory Module (src/storage/memory.py) - 194 lines

**Status:** ✅ 12+ tests | **Priority:** P1 (HIGH)
**Target:** 12 tests | **Estimated Time:** 2 hours

#### Test File: `tests/unit/test_memory.py`

**Test Classes:**
1. **TestConversationPersistence** (6 tests)
   - `test_save_message` - Save user/AI messages
   - `test_load_history` - Load conversation history
   - `test_load_history_with_limit` - Limit loaded messages
   - `test_clear_history` - Clear all history
   - `test_message_ordering` - Verify chronological order
   - `test_concurrent_saves` - Thread safety

2. **TestMemoryStatistics** (3 tests)
   - `test_get_message_count` - Count total messages
   - `test_get_conversation_count` - Count conversations
   - `test_get_memory_usage` - Database size

3. **TestMemoryMigration** (3 tests)
   - `test_migrate_from_json` - Import JSON history
   - `test_export_to_json` - Export to JSON
   - `test_backup_restore` - Backup and restore

---

### 3.3 Cache Module (src/storage/cache.py) - 183 lines

**Status:** ✅ 10+ tests | **Priority:** P1 (HIGH)
**Target:** 10 tests | **Estimated Time:** 1.5 hours

#### Test File: `tests/unit/test_cache.py`

**Test Classes:**
1. **TestEmbeddingCache** (5 tests)
   - `test_cache_embedding` - Store embedding
   - `test_retrieve_cached_embedding` - Get cached embedding
   - `test_cache_miss` - Handle cache miss
   - `test_cache_invalidation` - Clear cache
   - `test_cache_size_limit` - Enforce size limits

2. **TestQueryCache** (5 tests)
   - `test_cache_query_result` - Cache query results
   - `test_retrieve_cached_query` - Get cached query
   - `test_cache_expiration` - Time-based expiration
   - `test_cache_hit_rate` - Track hit rate metrics
   - `test_cache_statistics` - Get cache stats

---

## 4. HIGH PRIORITY - Vector Database

### 4.1 ChromaDB Client (src/vectordb/client.py) - 313 lines

**Status:** ✅ 15+ tests | **Priority:** P1 (HIGH)
**Target:** 15 tests | **Estimated Time:** 2.5 hours

#### Test File: `tests/unit/test_vectordb_client.py`

**Test Classes:**
1. **TestClientInitialization** (3 tests)
   - `test_connect_to_chroma` - Establish connection
   - `test_connection_retry` - Retry on failure
   - `test_connection_error_handling` - Handle unavailable server

2. **TestCollectionOperations** (6 tests)
   - `test_create_collection` - Create new collection
   - `test_get_existing_collection` - Get collection reference
   - `test_delete_collection` - Delete collection
   - `test_list_collections` - List all collections
   - `test_collection_metadata` - Get/set metadata
   - `test_collection_count` - Count documents

3. **TestDocumentOperations** (6 tests)
   - `test_add_documents` - Add documents to collection
   - `test_query_documents` - Query by similarity
   - `test_update_documents` - Update existing documents
   - `test_delete_documents` - Delete documents
   - `test_batch_operations` - Batch add/delete
   - `test_metadata_filtering` - Filter by metadata

---

### 4.2 Spaces Module (src/vectordb/spaces.py) - 183 lines

**Status:** ✅ 12+ tests | **Priority:** P1 (HIGH)
**Target:** 12 tests | **Estimated Time:** 2 hours

#### Test File: `tests/unit/test_spaces.py`

**Test Classes:**
1. **TestSpaceManagement** (6 tests)
   - `test_create_space` - Create new space
   - `test_switch_space` - Switch active space
   - `test_delete_space` - Delete space
   - `test_list_spaces` - List all spaces
   - `test_get_current_space` - Get active space
   - `test_space_persistence` - Persist in space_settings.json

2. **TestSpaceIsolation** (6 tests)
   - `test_documents_isolated_by_space` - Verify isolation
   - `test_learn_in_specific_space` - Learn to specific space
   - `test_search_in_current_space_only` - Search scoped
   - `test_populate_respects_space` - Populate scoped
   - `test_space_statistics` - Per-space statistics
   - `test_default_space_behavior` - Default space handling

---

## 5. CRITICAL PRIORITY - Security Modules

### 5.1 Security Modules (src/security/*.py) - 642 lines

**Status:** ✅ 25 tests | **Priority:** P0 (CRITICAL)
**Target:** 25 tests | **Estimated Time:** 4 hours

Security modules are critical and currently have ZERO tests.

#### Test File: `tests/security/test_input_sanitizer.py` (10 tests)

**Test Classes:**
1. **TestInputSanitization** (5 tests)
   - `test_sanitize_removes_dangerous_chars` - Remove <, >, &, etc.
   - `test_sanitize_preserves_safe_input` - Keep normal text
   - `test_sanitize_handles_unicode` - Unicode support
   - `test_sanitize_empty_input` - Handle empty strings
   - `test_sanitize_long_input` - Handle large inputs

2. **TestSQLInjectionPrevention** (5 tests)
   - `test_detect_sql_injection` - Detect SQL keywords
   - `test_sanitize_sql_input` - Sanitize SQL-dangerous input
   - `test_parameterized_query_support` - Verify safe approach
   - `test_detect_union_attack` - Detect UNION attacks
   - `test_detect_comment_attack` - Detect comment attacks

---

#### Test File: `tests/security/test_path_security.py` (10 tests)

**Test Classes:**
1. **TestPathTraversalPrevention** (5 tests)
   - `test_detect_path_traversal` - Detect ../ attacks
   - `test_validate_safe_path` - Allow safe paths
   - `test_resolve_symlinks` - Handle symbolic links
   - `test_prevent_absolute_path_access` - Restrict to base_dir
   - `test_prevent_home_directory_access` - Block ~/

2. **TestPathValidation** (5 tests)
   - `test_validate_file_exists` - Check file existence
   - `test_validate_file_readable` - Check read permissions
   - `test_validate_file_writable` - Check write permissions
   - `test_validate_path_length` - Enforce length limits
   - `test_validate_file_extension` - Whitelist extensions

---

#### Test File: `tests/security/test_rate_limiter.py` (5 tests)

**Test Classes:**
1. **TestRateLimiting** (5 tests)
   - `test_rate_limit_allows_below_threshold` - Allow normal rate
   - `test_rate_limit_blocks_above_threshold` - Block excessive rate
   - `test_rate_limit_resets_after_window` - Reset window
   - `test_rate_limit_per_user` - Per-user limits
   - `test_rate_limit_statistics` - Track limit hits

---

## 6. MEDIUM PRIORITY - Tool Executors

### 6.1 Tool Executor Modules (src/tools/executors/*.py) - 725 lines

**Status:** ⚠️ 35 tests exist but BROKEN (now fixed) | **Priority:** P2 (MEDIUM)
**Target:** Verify existing tests work | **Estimated Time:** 1 hour

Existing tests in `test_tools.py` and `test_tool_calling.py` cover tool executors, but imports were broken.

**Action Items:**
1. ✅ Update imports (COMPLETE)
2. ⏳ Run tests to verify functionality
3. Add integration tests for tool chains
4. Add tests for error conditions in each tool

**Additional Tests Needed:**
- Test tool execution with invalid file paths
- Test tool execution with permission errors
- Test tool chaining (one tool's output → another's input)
- Test concurrent tool execution
- Test tool timeout handling

---

## 7. Test Suite Organization

### 7.1 Recommended Directory Structure

```
tests/
├── unit/                           # Isolated unit tests
│   ├── test_application_context.py    # NEW (15 tests)
│   ├── test_config.py                   # NEW (12 tests)
│   ├── test_context_utils.py           # NEW (18 tests)
│   ├── test_command_registry.py         # DONE (21 tests)
│   ├── test_tool_registry.py            # DONE (27 tests)
│   ├── test_command_handlers.py         # NEW (40 tests)
│   ├── test_database.py                 # NEW (10 tests)
│   ├── test_memory.py                   # NEW (12 tests)
│   ├── test_cache.py                    # NEW (10 tests)
│   ├── test_vectordb_client.py          # NEW (15 tests)
│   ├── test_spaces.py                   # NEW (12 tests)
│   ├── test_main.py                     # EXISTS (26 tests)
│   ├── test_launcher.py                 # EXISTS (6 tests)
│   ├── test_tools.py                    # FIXED (20 tests)
│   └── test_gui.py                      # EXISTS (10 tests, skipped)
│
├── integration/                    # Integration tests
│   ├── test_integration.py              # EXISTS (11 tests)
│   ├── test_tool_calling.py             # FIXED (15 tests)
│   ├── test_space_workflows.py          # NEW (8 tests)
│   ├── test_learning_workflows.py       # NEW (10 tests)
│   └── test_end_to_end.py               # NEW (12 tests)
│
├── security/                       # Security-specific tests
│   ├── test_input_sanitizer.py          # NEW (10 tests)
│   ├── test_path_security.py            # NEW (10 tests)
│   └── test_rate_limiter.py             # NEW (5 tests)
│
├── performance/                    # Performance tests
│   ├── test_cache_performance.py        # NEW (5 tests)
│   └── test_query_performance.py        # NEW (5 tests)
│
└── conftest.py                     # Shared fixtures
```

### 7.2 Test Count Projection

| Category | Current | Needed | Total Target |
|----------|---------|--------|--------------|
| Unit Tests | 226 | +20 | 246 |
| Integration Tests | 26 | +30 | 56 |
| Security Tests | 19 | 0 | 19 |
| Performance Tests | 0 | +10 | 10 |
| **TOTAL** | **271** | **+60** | **331** |

---

## 8. Implementation Roadmap

### Phase 1: Critical Infrastructure (Week 1-2)
**Priority:** P0 | **Tests:** 52 | **Time:** 8-10 hours

1. ✅ CommandRegistry tests (21 tests) - DONE
2. ✅ ToolRegistry tests (27 tests) - DONE
3. ✅ ApplicationContext tests (15 tests) - DONE
4. ✅ Configuration tests (12 tests) - DONE
5. ✅ Security tests (25 tests) - DONE

**Success Criteria:**
- All P0 components have >90% coverage
- Security vulnerabilities tested
- Core infrastructure stable

---

### Phase 2: Storage & Vector DB (Week 3)
**Priority:** P1 | **Tests:** 59 | **Time:** 8-10 hours

1. ✅ Database tests (10 tests) - DONE
2. ✅ Memory tests (12 tests) - DONE
3. ✅ Cache tests (10 tests) - DONE
4. ✅ ChromaDB client tests (15 tests) - DONE
5. ✅ Spaces tests (12 tests) - DONE

**Success Criteria:**
- Storage layer fully tested
- Vector DB operations verified
- Space isolation confirmed

---

### Phase 3: Command Handlers & Utils (Week 4)
**Priority:** P1-P2 | **Tests:** 58 | **Time:** 10-12 hours

1. ✅ Context utilities tests (10 tests) - DONE
2. ✅ Command handler tests (40 tests) - DONE

**Success Criteria:**
- All command handlers tested
- Utility functions covered
- CommandRegistry integration verified

---

### Phase 4: Integration & Performance (Week 5)
**Priority:** P2 | **Tests:** 60 | **Time:** 10-12 hours

1. ✅ Tool executor verification (existing tests) - DONE
2. ✅ Space workflow tests (8 tests) - DONE
3. ✅ Learning workflow tests (10 tests) - DONE
4. ✅ End-to-end tests (12 tests) - DONE
5. ✅ Performance tests (10 tests) - DONE
6. ✅ Additional integration tests (20 tests) - DONE

**Success Criteria:**
- Full workflows tested end-to-end
- Performance benchmarks established
- All components integrate correctly

---

## 9. Testing Standards & Guidelines

### 9.1 Test Naming Convention

```python
def test_<action>_<condition>_<expected_result>():
    """
    Test that <action> under <condition> results in <expected result>.

    Example:
    def test_execute_tool_with_missing_args_returns_error():
        '''Test that executing tool with missing args returns error.'''
    """
```

### 9.2 Test Structure (AAA Pattern)

```python
def test_example():
    # Arrange - Set up test data and mocks
    registry = CommandRegistry()
    mock_handler = Mock()

    # Act - Execute the code under test
    result = registry.dispatch("test", [])

    # Assert - Verify expected behavior
    assert result is True
    mock_handler.assert_called_once()
```

### 9.3 Mocking Strategy

**Always Mock:**
- External services (LM Studio, ChromaDB, Ollama)
- File system operations (use tempfile or mock)
- Network calls
- Environment variables

**Never Mock:**
- The code under test
- Simple data structures
- Pure functions without side effects

### 9.4 Test Isolation

**Requirements:**
- Each test must be independent
- Use `setup_method()` and `teardown_method()`
- Clear registries/caches before/after tests
- Use temporary files/directories
- Clean up resources in teardown

### 9.5 Coverage Targets & Current Status

| Component Type | Minimum Coverage | Target Coverage | Current Status |
|----------------|------------------|-----------------|----------------|
| Core Infrastructure | 90% | 95% | ✅ **100%** (context.py, config.py) |
| Security Modules | 95% | 100% | ✅ **91-100%** (rate_limiter.py 100%, path_security.py 91%) |
| Storage Layer | 85% | 90% | ✅ **98-100%** (database.py 100%, memory.py 98%, cache.py 100%) |
| Command Handlers | 80% | 85% | ✅ **86-100%** (7/8 handlers ≥86%, 4 at 100%) |
| Tool Executors | 85% | 90% | ✅ **97-100%** (3/4 executors at 100%) |
| Utilities | 85% | 90% | ✅ **87-100%** (context_utils.py 87%, client.py 95%) |

**Overall Achievement:** ✅ **20/28 modules (71%) ≥90% coverage** (Target: 24/28 = 86%)

---

## 10. Continuous Integration

### 10.1 Test Execution Pipeline

```bash
# Local development
uv run pytest tests/unit/        # Fast unit tests (~10s)
uv run pytest tests/integration/ # Integration tests (~30s)
uv run pytest tests/security/    # Security tests (~5s)

# CI/CD pipeline
uv run pytest --cov=src --cov-report=html --cov-fail-under=90
```

### 10.2 Pre-commit Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run unit tests (fast)
uv run pytest tests/unit/ -q

# Run linting
uv run python tests/lint/lint-python.py

# Check coverage
uv run pytest --cov=src --cov-fail-under=85 -q
```

### 10.3 CI/CD Requirements

**Pull Request Checks:**
- ✅ All tests must pass
- ✅ Coverage must be ≥90%
- ✅ No linting errors
- ✅ No security test failures
- ✅ Performance tests within thresholds

---

## 11. Test Maintenance

### 11.1 When to Update Tests

**Always update tests when:**
- Adding new features
- Modifying existing functionality
- Fixing bugs (add regression test)
- Refactoring code
- Changing APIs or signatures

### 11.2 Test Review Checklist

- [ ] Test names clearly describe what they test
- [ ] Tests are independent (no shared state)
- [ ] Mocks are properly configured
- [ ] Assertions are specific and meaningful
- [ ] Error cases are tested
- [ ] Edge cases are covered
- [ ] Tests run quickly (<1s per unit test)
- [ ] Tests are deterministic (no flaky tests)

### 11.3 Identifying Flaky Tests

**Signs of flaky tests:**
- Passes locally but fails in CI
- Fails intermittently
- Depends on timing or execution order
- Uses real external services

**Solutions:**
- Add proper mocking
- Increase timeouts
- Fix race conditions
- Isolate test data
- Use deterministic seeds for random data

---

## 12. Success Metrics

### 12.1 Quantitative Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Total Tests | 256 | 365+ |
| Test Coverage | ~64% | >90% |
| Test Execution Time | ~45s | <60s |
| Passing Rate | 100% | 100% |
| Flaky Test Rate | 0% | <1% |
| Security Test Coverage | 100% | 100% |

### 12.2 Qualitative Metrics

- All critical paths have tests
- All security modules have comprehensive tests
- All public APIs have tests
- All error conditions have tests
- All edge cases are documented and tested
- New features ship with tests

---

## 13. Resources & References

### 13.1 Documentation

- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)

### 13.2 Internal References

- `tests/conftest.py` - Shared test fixtures
- `pytest.ini` - Test configuration
- `ARCHITECTURE.md` - System architecture
- `MIGRATION.md` - Migration guide for v0.2.0

### 13.3 Tools

- **pytest** - Test framework
- **pytest-cov** - Coverage reporting
- **pytest-mock** - Mocking utilities
- **pytest-xdist** - Parallel test execution
- **hypothesis** - Property-based testing (future)

---

## 14. Next Steps

### Immediate Actions

1. ✅ Fix broken test imports (COMPLETE)
2. ✅ Create registry tests (COMPLETE)
3. ✅ Implement Phase 1, 2 & 3 tests (COMPLETE)
4. ✅ Set up coverage requirements (COMPLETE)
5. ✅ Create shared fixtures in conftest.py (COMPLETE)

### Short-Term (1-2 weeks)

1. ✅ Complete Phase 1, 2 & 3 tests (169 new tests) - DONE
2. ✅ Achieve >80% unit test coverage for core components - DONE
3. ✅ Document test results (227 tests passing) - DONE
4. ✅ Implement Phase 4: Workflow and Performance tests - DONE

### Phase 5: High-Coverage Unit Testing (Week 6)
**Priority:** P2 | **Tests:** 15 | **Time:** 6-8 hours

1. ✅ Expand ApplicationContext coverage to 100% - DONE
2. ✅ Add Main Loop Orchestration error tests - DONE
3. ✅ Fill coverage gaps in Storage Memory/Database - DONE

### Long-Term (1 month)

1. Complete all phases (365+ tests)
2. Achieve >90% coverage
3. Implement performance testing
4. Add property-based testing with Hypothesis

---

## Appendix A: Test Template

```python
#!/usr/bin/env python3
"""
Test suite for [Module Name].

Tests cover:
- [Feature 1]
- [Feature 2]
- [Feature 3]
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.module import ClassUnderTest


class TestFeatureGroup:
    """Test [feature description]."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        self.instance = ClassUnderTest()

    def teardown_method(self):
        """Clean up after each test."""
        # Clean up resources
        pass

    def test_feature_with_valid_input(self):
        """Test feature works with valid input."""
        # Arrange
        input_data = {"key": "value"}

        # Act
        result = self.instance.method(input_data)

        # Assert
        assert result["success"] is True

    def test_feature_with_invalid_input(self):
        """Test feature handles invalid input gracefully."""
        # Arrange
        invalid_input = None

        # Act & Assert
        with pytest.raises(ValueError):
            self.instance.method(invalid_input)
```

---

**Document End**

For questions or clarifications, contact the test infrastructure team.
