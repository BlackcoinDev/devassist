# Migration and Database Guide

This guide covers the currently implemented database backends and important
migration information for the AI Assistant application.

## ⚠️ v0.3.0 Migration Notes

### Backward Compatibility

**v0.3.0 is fully backward compatible with v0.2.0 and earlier versions**:

- ✅ **No breaking changes** - All existing functionality preserved
- ✅ **Seamless upgrade** - No database migration required
- ✅ **Feature addition only** - New features added without disrupting existing ones

### New Features in v0.3.0

The following features have been **added** and are **opt-in**:

1. **Shell Execution (CLI Only)**
   - AI can run shell commands with allowlist-based security
   - Safe commands (git, npm, python, etc.) run without confirmation
   - Unknown commands require user approval
   - **No configuration required** - works out of the box

2. **MCP (Model Context Protocol) Integration**
   - External tool server connectivity (stdio, HTTP, SSE)
   - Configuration via `config/mcp_servers.json`
   - Tools prefixed with `mcp_servername_`
   - **Opt-in only** - no external servers configured by default

3. **Git Integration Tools**
   - `git_status()` - Repository status
   - `git_diff()` - Show changes
   - `git_log()` - Commit history  
   - Available as both AI tools and slash commands (`/git-status`, etc.)

4. **Code Search Capability**
   - `code_search()` tool using ripgrep
   - Fast regex search across codebase
   - Available as AI tool and `/search`slash command`

5. **Tool Approval System**
   - Per-tool permission controls: `always`, `ask`, `never`
   - Configuration via `config/tool_approvals.json`
   - Default settings provide secure defaults
   - **No changes required** - sensible defaults provided

### Configuration Changes (Optional)

If you want to customize new features, add these optional files:

```bash
# Optional: Configure external MCP servers
config/mcp_servers.json
{
  "servers": [
    {
      "name": "filesystem",
      "transport": "stdio", 
      "enabled": true,
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    }
  ]
}

# Optional: Configure tool approval behavior
config/tool_approvals.json
{
  "approvals": {
    "shell_execute": "ask",
    "write_file": "ask", 
    "git_status": "always",
    "code_search": "always",
    "mcp_*": "ask"
  }
}
```

**Note:** These are **optional** - the application works perfectly without them.

### Migration Checklist

✅ **Version 0.3.0 upgrade steps:**

1. Update dependencies (if needed): `uv pip install -r requirements.txt`
2. Verify all services running: LM Studio, ChromaDB, Ollama
3. Test new features: `/help` shows new commands (`/git-status`, `/search`, `/shell`, etc.)
4. (Optional) Customize MCP or tool approval settings

**No data migration required** - all existing conversations, learned knowledge, and spaces are fully compatible.

---

## ⚠️ Breaking Changes in v0.2.0

### Configuration Requirements

**IMPORTANT**: Starting with v0.2.0, the application requires a `.env` file and
no longer uses hardcoded defaults.

#### What Changed

- **Before**: Application worked with or without `.env`, used hardcoded fallbacks, ChromaDB was

  optional

- **After**: Application **requires** `.env` file, **no hardcoded defaults exist**, **ChromaDB is

  mandatory** for learning features

#### Migration Steps

1. **Copy configuration template**:

   ```bash
   cp .env.example .env
   ```

2. **Configure all required variables**:
   - All variables in `.env.example` are mandatory
   - No default values exist in the code
   - Application will fail to start without proper configuration

3. **Ensure ChromaDB and Ollama are running**:
   - ChromaDB v2 server is now **mandatory** for learning features
   - Ollama service is now **mandatory** for vector operations
   - Update deployment scripts to start these services

4. **Update your deployment scripts**:
   - Ensure `.env` file is present in production
   - Modify CI/CD pipelines to provide environment variables

#### Error Messages

- **Missing `.env`**: `❌ ERROR: No .env file found!`
- **Missing variables**: `❌ ERROR: [VARIABLE_NAME] environment variable is required`
- **ChromaDB failure**: `❌ ERROR: ChromaDB connection failed: [error]`
- **Application exit**: Application will exit with code 1 if ChromaDB is unavailable

---

## 🔄 Migrating to v0.2.0: Modular Architecture

### Overview of Changes

Version 0.2.0 introduces a significant architectural refactoring, moving from a
monolithic structure to a modular plugin-based architecture:

- **main.py reduced**: From 4,556 lines to 3,175 lines (30% reduction)
- **New modules created**: 8 focused modules with clear responsibilities
- **Plugin systems**: CommandRegistry and ToolRegistry with self-registration
- **Dependency injection**: ApplicationContext replaces scattered globals

### Breaking Changes

#### 1. Import Paths Changed

**Before (v0.2.0):**

```python
from src.main import llm, vectorstore, embeddings, conversation_history
from src.main import get_relevant_context, add_to_knowledge_base

```text

**After (v0.2.0):**

```python

# Use ApplicationContext for all services

from src.core.context import get_context

ctx = get_context()
llm = ctx.llm
vectorstore = ctx.vectorstore
embeddings = ctx.embeddings
conversation_history = ctx.conversation_history

# Import utilities from new modules

from src.core.context_utils import get_relevant_context, add_to_knowledge_base
from src.storage.database import initialize_database
from src.storage.memory import load_memory, save_memory
from src.vectordb.client import ChromaDBClient

```text

#### 2. Command and Tool Registration

**Before (v0.2.0):**

```python

# Commands hardcoded in handle_slash_command() function

# Tools manually added to enable_tools list

```text

**After (v0.2.0):**

```python

# Commands use decorator pattern

from src.commands.registry import CommandRegistry

@CommandRegistry.register("mycommand", "Description", category="utility")
def handle_mycommand(args: str) -> None:
    pass

# Tools use decorator pattern

from src.tools.registry import ToolRegistry

@ToolRegistry.register("my_tool", TOOL_DEFINITION)
def execute_my_tool(arg1: str) -> Dict[str, Any]:
    return {"success": True}

```text

#### 3. Configuration Access

**Before (v0.2.0):**

```python

# Environment variables accessed directly via os.getenv()

import os
chroma_host = os.getenv("CHROMA_HOST")

```text

**After (v0.2.0):**

```python

# Configuration centralized in Config dataclass

from src.core.config import Config

config = Config.load()
chroma_host = config.chroma_host

### Implementation Migration Steps

#### Step 1: Update Custom Code Imports

If you have custom extensions or scripts that import from `src.main`, update
them:

```python

# OLD

from src.main import llm, vectorstore
result = vectorstore.similarity_search(query)

# NEW

from src.core.context import get_context
ctx = get_context()
result = ctx.vectorstore.similarity_search(query)

#### Step 2: Migrate Custom Commands

If you added custom slash commands to `handle_slash_command()`:

1. Create a new handler file in `src/commands/handlers/custom_commands.py`
2. Use the CommandRegistry decorator:

```python
from src.commands.registry import CommandRegistry

@CommandRegistry.register("mycustom", "My custom command", category="custom")
def handle_mycustom(args: str) -> None:
    """Handle /mycustom command."""
    print(f"Custom command executed: {args}")

1. The handler will auto-register when imported

#### Step 3: Migrate Custom Tools

If you added custom AI tools:

1. Create executor in `src/tools/executors/custom_tools.py`
2. Define tool schema and executor:

```python

from src.tools.registry import ToolRegistry
from typing import Dict, Any

MY_TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "my_custom_tool",
        "description": "Custom tool",
        "parameters": {
            "type": "object",
            "properties": {
                "input": {"type": "string"}
            },
            "required": ["input"]
        }
    }
}

@ToolRegistry.register("my_custom_tool", MY_TOOL_DEF)
def execute_my_custom_tool(input: str) -> Dict[str, Any]:
    return {"success": True, "result": input}

```text

#### Step 4: Update Test Code

If you have custom tests:

```python

# OLD

from src.main import llm, vectorstore

def test_something():
    assert llm is not None

# NEW

from src.core.context import get_context, reset_context

def test_something():
    ctx = get_context()
    assert ctx.llm is not None

def teardown():
    reset_context()  # Clean up for next test

### Backwards Compatibility

The following remain compatible:

- ✅ **User-facing features**: All slash commands work identically
- ✅ **GUI/CLI interfaces**: No changes to user experience
- ✅ **Configuration**: `.env` format unchanged
- ✅ **Database schema**: SQLite schema unchanged
- ✅ **ChromaDB collections**: Vector data fully compatible
- ✅ **Tool functionality**: All 8 tools work the same

### What Still Works

- All existing `.env` files
- All existing ChromaDB collections
- All existing conversation history in SQLite
- All existing spaces and configurations
- GUI and CLI interfaces (no user-facing changes)

### Testing Your Migration

After migrating, verify everything works:

```bash

# 1. Run tests with new module coverage

uv run pytest --cov=src --cov=launcher --cov-report=term-missing

# 2. Test both interfaces

uv run python launcher.py --cli
uv run python launcher.py --gui

# 3. Verify slash commands work

# In CLI: /help, /vectordb, /memory, /learn, etc

# 4. Check tool calling

# Ask AI: "read the README file" (should use read_file tool)

```text

### Getting Help

If you encounter issues during migration:

1. Check the [ARCHITECTURE.md](ARCHITECTURE.md) for new module structure
2. See [CLAUDE.md](../CLAUDE.md) for development guidelines
3. Review code examples in updated documentation
4. Check error logs for specific import or module errors

### Rollback Instructions

If you need to rollback to v0.2.0:

```bash
git checkout tags/v0.2.0
uv pip install -r requirements.txt

Note: No database migration is needed for rollback—data formats are compatible.

### New Tool Capabilities

**MAJOR ENHANCEMENT**: v0.2.0 introduces **8 AI tools** that work together with
the existing knowledge management system:

#### Tool Integration Architecture

For detailed tool integration architecture, see
[ARCHITECTURE.md](ARCHITECTURE.md).

#### Tool Result Handling & AI Usage

**Tool Result Lifecycle:**

1. **Execution**: AI calls tool → Tool runs → Returns structured result
2. **Storage**: Results stored in conversation memory (Python variables, not

files)

1. **Integration**: Results formatted and added to conversation history as

HumanMessage

1. **Processing**: Results become part of LLM's thinking context for response

generation

1. **Response**: AI uses tool data to craft informed, accurate responses
2. **Persistence**: Results saved in SQLite conversation history

**Result Locations:**

- **During Execution**: `tool_results` list and `enhanced_history` messages
- **During Response**: Integrated into LLM's context window
- **After Response**: Persisted in SQLite database conversation history
- **No File Storage**: Results exist only in memory/conversation during session

#### Available Tools

1. **`read_file()`** - Read file contents (tested & working with qwen3-vl-30b)
2. **`write_file()`** - Create/modify files (ready)
3. **`list_directory()`** - Browse directories (ready)
4. **`get_current_directory()`** - Show current path (tested & working)
5. **`parse_document()`** - Extract text/tables/forms/layout from documents

(ready)

1. **`learn_information()`** - Store in knowledge base (ready)
2. **`search_knowledge()`** - Query learned information (ready)

#### Tool Ecosystem Benefits

- **Document Intelligence**: qwen3-vl-30b's multimodal capabilities for OCR, table extraction, form

  analysis

- **Knowledge Synthesis**: Tools work together to build comprehensive understanding
- **Result Integration**: Tool outputs seamlessly feed into AI response generation
- **Autonomous Operations**: AI can execute complex multi-step tasks without user intervention
- **Persistent Learning**: Document analyses stored in ChromaDB for future reference
- **Semantic Search**: Vector-based retrieval of learned information and document content

#### Migration for Tool Usage

1. **No additional configuration needed** - tools use existing ChromaDB/Ollama

setup

1. **Tools are automatically available** in both GUI and CLI interfaces
2. **Natural language triggers** - AI recognizes intent and calls appropriate

tools

1. **Fallback to manual commands** - all tools accessible via slash commands if

needed

#### Required Environment Variables

```bash

# LM Studio Configuration

LM_STUDIO_URL=http://192.168.0.203:1234/v1    # Your LM Studio endpoint
LM_STUDIO_KEY=lm-studio                        # API key for authentication
MODEL_NAME=qwen3-vl-30b                        # LLM model name

# Vector Database Configuration (REQUIRED - ChromaDB is mandatory)

CHROMA_HOST=192.168.0.204                      # ChromaDB server host
CHROMA_PORT=8000                               # ChromaDB server port

# Ollama Configuration

OLLAMA_BASE_URL=http://192.168.0.204:11434    # Ollama embeddings endpoint
EMBEDDING_MODEL=qwen3-embedding:latest        # Embedding model name

# Application Settings

MAX_HISTORY_PAIRS=5                            # Conversation memory limit
TEMPERATURE=0.7                               # LLM creativity (0.0-1.0)
MAX_INPUT_LENGTH=10000                        # Maximum input length

# Database Configuration

DB_TYPE=sqlite                                # Database type
DB_PATH=db/history.db                         # SQLite database path

# System Configuration

KMP_DUPLICATE_LIB_OK=TRUE                     # OpenMP workaround

```text

## 🗄️ Database Implementation

For comprehensive database architecture details, please refer to the
[ARCHITECTURE.md](ARCHITECTURE.md) document.

### SQLite (Recommended)

**Advantages:**

- Zero configuration - no server setup required
- ACID transactions - data integrity guaranteed
- Concurrent access - handles multiple processes safely
- SQL querying - can search/filter conversation history
- File-based - easy backup and portability
- Built-in encryption support with SQLCipher

**Complete Schema Design and Implementation:** See
[ARCHITECTURE.md](ARCHITECTURE.md) for detailed SQLite schema, Python
implementation, and encryption setup.

## 🔐 Security Considerations

For comprehensive security architecture details, please refer to the
[ARCHITECTURE.md](ARCHITECTURE.md) document.

### Encryption Strategies

**Database-Level Encryption:**

- SQLCipher for SQLite
- PostgreSQL with pgcrypto
- MongoDB with encryption at rest

**Application-Level Encryption:**

- Fernet encryption for content
- Secure key management

### Access Control

**Multi-Tenant Isolation:**

- User-specific conversation access
- Session-based permissions
- Secure data separation

**Complete Security Implementation:** See [ARCHITECTURE.md](ARCHITECTURE.md) for
detailed encryption strategies, access control mechanisms, and security best
practices.

## 📊 Performance Optimization

For comprehensive performance architecture details, please refer to the
[ARCHITECTURE.md](ARCHITECTURE.md) document.

### Indexing Strategies

**SQLite Optimization:**

- Session-timestamp indexing for fast retrieval
- Content length indexing for size-based queries

**PostgreSQL Optimization:**

- Full-text search with GIN indexes
- Metadata indexing for complex queries

### Query Optimization

**Efficient Data Access:**

- Pagination strategies for large datasets
- Time-based filtering for recent messages
- Optimized query patterns for common operations

**Complete Performance Implementation:** See [ARCHITECTURE.md](ARCHITECTURE.md)
for detailed indexing strategies, query optimization techniques, and performance
best practices.

## 🔄 Migration Strategies

### From JSON to Database

```python

def migrate_json_to_database(json_file: str, db_store):
    """Migrate existing JSON conversations to database"""

    # Load existing JSON
    with open(json_file, 'r') as f:
        messages = json.load(f)

    # Migrate each message
    for msg in messages:
        try:
            db_store.save_message(
                session_id="migrated_session",
                message_type=msg['type'],
                content=msg['content'],
                metadata={'migrated': True, 'original_format': 'json'}
            )
        except Exception as e:
            logger.error(f"Failed to migrate message: {e}")

    # Backup original file
    shutil.move(json_file, f"{json_file}.backup")

```text

### Data Validation

```python

def validate_migration(source_count: int, target_count: int) -> bool:
    """Validate that migration preserved all data"""
    if source_count != target_count:
        logger.error(f"Migration count mismatch: {source_count} ->
{target_count}")
        return False

    # Additional checksum validation
    # Compare content hashes between source and target

    return True

```text

## 📈 Monitoring & Analytics

### Usage Statistics

```sql

-- Conversation statistics
SELECT
    session_id,
    COUNT(*) as message_count,
    MIN(timestamp) as first_message,
    MAX(timestamp) as last_message,
    AVG(LENGTH(content)) as avg_message_length
FROM conversations
GROUP BY session_id
ORDER BY last_message DESC;

-- User activity
SELECT
    user_id,
    COUNT(DISTINCT session_id) as total_sessions,
    COUNT(*) as total_messages,
    MAX(timestamp) as last_activity
FROM conversations
WHERE user_id IS NOT NULL
GROUP BY user_id;

```text

### Performance Metrics

```python

def log_query_performance(query_name: str, start_time: float, result_count:
int):
    """Log query performance for monitoring"""
    duration = time.time() - start_time
    logger.info(f"Query '{query_name}' took {duration:.3f}s, returned
{result_count} results")

    # Could send to monitoring system
    # metrics_client.histogram('db_query_duration', duration, tags={'query':
query_name})
```

This guide provides a comprehensive foundation for implementing various database
backends for conversation memory storage, with security, performance, and
scalability considerations.
