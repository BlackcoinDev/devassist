# AI Assistant Architecture

This document provides a comprehensive architectural overview of the AI
Assistant
application, serving as a reference for all other documentation files.

## 🏗️ System Architecture

### High-Level Overview (v0.3.0 - Shell & MCP Integration)

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LM Studio     │    │ ChromaDB v2     │    │    Ollama       │
│ (AI Brain)      │◄──►│ (Vector DB)     │◄──►│ (Embeddings)    │
│ Port: 1234      │    │ Port: 8000      │    │ Port: 11434     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────────┐
                    │      launcher.py        │
                    │    (GUI/CLI selector)   │
                    │     loads .env          │
                    └─────────────────────────┘
                                 │
                ┌────────────────┴────────────────┐
                │                                 │
        ┌───────────────┐              ┌─────────────────┐
        │  src/gui.py   │              │  src/main.py    │
        │  (PyQt6 GUI)  │              │  (CLI + init)   │
        └───────┬───────┘              └────────┬────────┘
                │                               │
                └───────────┬───────────────────┘
                            │
                ┌───────────▼────────────┐
                │ ApplicationContext     │ (Dependency Injection)
                │  - llm, vectorstore    │
                │  - db_conn, history    │
                │  - config, caches      │
                └───────────┬────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
  ┌─────▼──────┐    ┌──────▼───────┐   ┌──────▼────────┐
  │ Commands   │    │    Tools     │   │   Storage     │
  │ (Registry) │    │  (Registry)  │   │   (SQLite)    │
   │ 24 handlers │    │ 13 AI tools  │   │   (Memory)    │
  └─────┬──────┘    └──────┬───────┘   └──────┬────────┘
        │                   │                   │
  ┌─────▼──────┐    ┌──────▼───────┐   ┌──────▼────────┐
  │  Security  │    │   VectorDB   │   │    Cache      │
  │ Validators │    │  (ChromaDB)  │   │  (In-memory)  │
  └────────────┘    └──────────────┘   └───────────────┘
        │
  ┌─────▼──────────────┐
  │ Command Handlers   │ (Organized by function in src/commands/handlers/)
  └────────────────────┘
```

### Data Flow

1. **Interface Selection** → `launcher.py` chooses GUI or CLI
2. **Application Initialization** → `initialize_application()` sets up LLM and

vector database

1. **Space Loading** → Load last used workspace from `space_settings.json`
2. **Welcome Display** → `show_welcome()` shows interface and current space info
3. **User Teaching** → `/learn` commands add knowledge to current space's

collection

1. **Code Ingestion** → `/populate` bulk imports codebases to current space
2. **Text Chunking** → `chunk_text()` processes content for vector storage
3. **Query Processing** → User asks questions via GUI or CLI
4. **Context Retrieval** → Current space's ChromaDB collection provides relevant

learned information

1. **AI Enhancement** → LM Studio generates responses with space-specific

learned context

1. **Memory Persistence** → SQLite saves conversation history
2. **Space Persistence** → Current space setting saved to `space_settings.json`
3. **Knowledge Growth** → AI learns continuously within current space

## 🧠 Core Components

### 1. AI Tools (13 Tools)

The AI has access to 13 powerful tools for various operations:

| Tool Name                 | Description                                     | Status              |
| ------------------------- | ----------------------------------------------- | ------------------  |
| `read_file()`             | Read file contents                              | ✅ Tested & Working |
| `write_file()`            | Create/modify files                             | ✅ Tested & Working |
| `list_directory()`        | Browse directories                              | ✅ Tested & Working |
| `get_current_directory()` | Show current path                               | ✅ Tested & Working |
| `parse_document()`        | Extract text/tables/forms/layout from documents | ✅ Tested & Working |
| `learn_information()`     | Store in knowledge base                         | ✅ Tested & Working |
| `search_knowledge()`      | Query learned information                       | ✅ Tested & Working |
| `search_web()`            | Search the internet using DuckDuckGo            | ✅ Tested & Working |
| `shell_execute()`         | Run shell commands (CLI only)                   | ✅ Tested & Working |
| `git_status()`            | Git repository status                           | ✅ Tested & Working |
| `git_diff()`              | Show git changes                                | ✅ Tested & Working |
| `git_log()`               | Commit history                                  | ✅ Tested & Working |
| `code_search()`           | Regex code search (ripgrep)                     | ✅ Tested & Working |

**Tool Integration Architecture:**

```text

User Query → AI (qwen3-vl-30b) → Tool Selection → Execution → Result Integration
→ AI Response
     ↓              ↓                      ↓            ↓              ↓        
     ↓
File System    Multimodal Analysis     Secure        Structured     Conversation
    Contextual
Operations     & Understanding        Execution      Data Output    Context     
   Responses
```

### 2. Spaces System

The Spaces system provides isolated workspaces with separate knowledge bases:

- **Isolation**: Each space has its own dedicated collection in the Vector Database
- **Persistence**: The app remembers your last used space (`space_settings.json`)
- **Safety**: Switching spaces completely changes what the AI "knows"

**Commands:**

- `/space list` - Show all spaces
- `/space switch <name>` - Create or switch to a space
- `/space delete <name>` - Delete a space

### 3. Memory Systems

#### Personalized Memory (Mem0)

Mem0 creates a dynamic profile of user preferences and context:

- **Automatic**: Silent observation of messages in the background
- **Adaptive**: Remembers user preferences and coding style
- **Contextual**: Checks Mem0 for every message to adapt responses

#### Conversation Memory (SQLite)

SQLite database stores conversation history with:

- **ACID transactions** for data integrity
- **Concurrent access** for multiple processes
- **SQL querying** for search/filter operations
- **File-based storage** for easy backup

### 4. Document Processing

The system supports 80+ file types through unified processing:

- **PDF, DOCX, RTF, EPUB, XLSX** extraction
- **Smart chunking** with 1500-char chunks
- **Paragraph-aware boundaries** for better retrieval
- **Quality filtering** to skip low-value content
- **Binary detection** with null byte analysis

### 5. Shell Execution Architecture (v0.3.0)

The shell execution system provides safe command execution in CLI mode only:

```text
User Request → AI decides to call shell_execute()
                         │
                         ▼
              ┌─────────────────────┐
              │   ShellSecurity     │
              │   Validation        │
              └──────────┬──────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ SAFE_CMDS   │  │ BLOCKED_CMDS│  │  UNKNOWN    │
│ git, npm... │  │ rm, sudo... │  │ Confirmation│
│ Execute     │  │ Deny        │  │ Required    │
└─────────────┘  └─────────────┘  └─────────────┘
```

**Security Layers:**

1. **Allowlist**: Safe commands execute without confirmation
2. **Blocklist**: Dangerous commands are always denied
3. **Pattern Detection**: Dangerous patterns like `rm -rf` blocked
4. **CLI-Only**: Shell execution disabled in GUI mode
5. **Timeouts**: Maximum 5-minute execution time
6. **Output Limits**: Truncation prevents memory exhaustion

### 6. MCP Integration Architecture (v0.3.0)

Model Context Protocol enables external tool server integration:

```text
┌─────────────────────────────────────────────────────────────┐
│                      MCP Client Manager                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   stdio      │  │    HTTP      │  │     SSE      │       │
│  │  Transport   │  │  Transport   │  │  Transport   │       │
│  │ (subprocess) │  │   (REST)     │  │ (streaming)  │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                            ▼                                 │
│              ┌─────────────────────────┐                     │
│              │    Protocol Layer       │                     │
│              │  (JSON-RPC 2.0)         │                     │
│              └─────────────────────────┘                     │
│                            │                                 │
│         ┌──────────────────┼──────────────────┐              │
│         ▼                  ▼                  ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│  │tools/list   │    │tools/call   │    │resources/   │       │
│  │(discovery)  │    │(execution)  │    │read         │       │
│  └─────────────┘    └─────────────┘    └─────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │   Tool Registry         │
              │ mcp_servername_toolname │
              └─────────────────────────┘
```

**Key Features:**

- **Transport Abstraction**: Unified interface for stdio/HTTP/SSE
- **Tool Discovery**: Automatic tool enumeration from servers
- **Namespacing**: MCP tools prefixed with `mcp_servername_`
- **Lifecycle Management**: Connect/disconnect server management
- **Error Handling**: Graceful degradation on server failures

### 7. Tool Approval System (v0.3.0)

Per-tool permission control for security:

```text
Tool Execution Request
         │
         ▼
┌─────────────────────┐
│  ToolApprovalManager│
│  check_approval()   │
└──────────┬──────────┘
           │
    ┌──────┼──────┐
    ▼      ▼      ▼
┌──────┐┌──────┐┌──────┐
│ALWAYS││ ASK  ││NEVER │
│Allow ││Prompt││Block │
└──────┘└──┬───┘└──────┘
           │
           ▼
    ┌─────────────┐
    │User Confirm │
    │ yes / no    │
    └─────────────┘
```

**Configuration** (`config/tool_approvals.json`):

```json
{
  "version": "1.0",
  "approvals": {
    "shell_execute": "ask",
    "write_file": "ask",
    "git_status": "always",
    "mcp_*": "ask"
  },
  "defaults": {
    "builtin": "always",
    "mcp": "ask"
  }
}
```

**Default Approval Modes:**

| Tool Category | Default Mode | Rationale |
| -------------- | -------------- | ----------- |
| Read-only (read_file, git_status) | always | Safe operations |
| Write operations (write_file) | ask | Modifies files |
| Shell execution | ask | Potential system impact |
| MCP tools | ask | External systems |

## 🔌 Plugin Architecture (v0.3.0)

The modular architecture introduces self-registering plugin systems for commands
and tools, eliminating the need for central configuration.

### CommandRegistry Pattern

Commands use a decorator-based auto-registration system:

```python

# In src/commands/handlers/utility_commands.py

from src.commands.registry import CommandRegistry

@CommandRegistry.register("mycommand", "Description", category="utility",
aliases=["mc"])
def handle_mycommand(args: str) -> None:
    """Handle /mycommand - does something useful."""
    print(f"Executing: {args}")
```

**How it works:**

1. Decorator executes during module import
2. Function auto-registers in CommandRegistry._commands dict
3. Help text auto-generates from decorator metadata
4. Dispatch via `CommandRegistry.dispatch(command, args)`
5. No central configuration file needed

**Benefits:**

- Add commands without modifying core code
- Help text stays in sync with implementation
- Category-based organization
- Alias support built-in

### ToolRegistry Pattern

AI tools use the same self-registration approach:

```python

# In src/tools/executors/utility_tools.py

from src.tools.registry import ToolRegistry

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "Does something useful",
        "parameters": {
            "type": "object",
            "properties": {
                "arg1": {"type": "string", "description": "Argument"}
            },
            "required": ["arg1"]
        }
    }
}

@ToolRegistry.register("my_tool", TOOL_DEFINITION)
def execute_my_tool(arg1: str) -> Dict[str, Any]:
    """Execute the tool."""
    return {"success": True, "result": f"Executed with {arg1}"}
```

**How it works:**

1. Tool definition follows OpenAI function calling format
2. Decorator registers both definition and executor
3. LLM receives definitions via `ToolRegistry.get_definitions()`
4. AI calls tools autonomously during conversation
5. Execution via `ToolRegistry.execute_tool_call(tool_call)`

**Benefits:**

- Tools auto-register on import
- LLM automatically receives new tool definitions
- Schema and implementation stay together
- No manual binding required

### ApplicationContext Pattern

Centralized dependency injection replaces scattered globals:

```python

# In src/core/context.py

from dataclasses import dataclass

@dataclass
class ApplicationContext:
    llm: Optional[ChatOpenAI] = None
    vectorstore: Optional[Chroma] = None
    embeddings: Optional[OllamaEmbeddings] = None
    db_conn: Optional[sqlite3.Connection] = None
    conversation_history: List[BaseMessage] = field(default_factory=list)
    # ... more services

# Singleton accessor

_context: Optional[ApplicationContext] = None

def get_context() -> ApplicationContext:
    global _context
    if _context is None:
        _context = ApplicationContext()
    return _context

```

**Usage:**

```python
from src.core.context import get_context

ctx = get_context()
ctx.llm  # Access ChatOpenAI instance
ctx.vectorstore  # Access Chroma instance
ctx.conversation_history  # Access message history

```

**Benefits:**

- All services accessible from single source
- Easy mocking for tests
- Thread-safe with proper locking
- Clear dependency relationships

### Module Organization

```text

src/
├── core/               # Foundation layer
│   ├── config.py       # Configuration from .env
│   ├── context.py      # ApplicationContext singleton
│   └── context_utils.py # Utility functions
├── commands/           # Command plugin system
│   ├── registry.py     # CommandRegistry dispatcher
│   └── handlers/       # Auto-registering handlers
│       ├── help_commands.py
│       ├── memory_commands.py
│       ├── database_commands.py
│       ├── learning_commands.py
│       ├── config_commands.py
│       ├── space_commands.py
│       ├── file_commands.py
│       ├── export_commands.py
│       ├── git_commands.py     # /git-status, /git-log, /git-diff
│       ├── system_commands.py  # /search, /shell
│       └── All commands migrated to modern system
├── tools/              # Tool plugin system
│   ├── registry.py     # ToolRegistry dispatcher
│   └── executors/      # Auto-registering executors
│       ├── file_tools.py       # read_file, write_file, list_directory
│       ├── knowledge_tools.py  # learn_information, search_knowledge
│       ├── document_tools.py   # parse_document
│       ├── web_tools.py        # search_web
│       ├── shell_tools.py      # shell_execute
│       ├── git_tools.py        # git_status, git_diff, git_log
│       └── system_tools.py     # code_search
├── storage/            # Persistence layer
├── security/           # Security enforcement
└── vectordb/           # Knowledge storage

```

## 🗄️ Database Architecture

### SQLite Schema

```sql
-- Conversations table
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_id TEXT,
    message_type TEXT NOT NULL CHECK (message_type IN ('system', 'human',
'ai')),
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT, -- JSON string
    checksum TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_session_timestamp ON conversations(session_id, timestamp);
CREATE INDEX idx_user_session ON conversations(user_id, session_id);
CREATE INDEX idx_timestamp ON conversations(timestamp);

-- Sessions table for metadata
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    title TEXT, -- Auto-generated or user-set
    model TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_message_at DATETIME,
    message_count INTEGER DEFAULT 0
);

```

### ChromaDB v2 Architecture

- **Server-based**: Dedicated vector database server
- **Persistent storage**: All learned information survives app restarts
- **Direct API integration**: Optimized for reliability and performance
- **Collection-based**: Each space has its own collection

## 🔧 Configuration

### Required Environment Variables

```bash

# LM Studio Configuration

LM_STUDIO_URL=http://192.168.0.203:1234/v1    # Your LM Studio endpoint
LM_STUDIO_KEY=lm-studio                        # API key for authentication
MODEL_NAME=qwen3-vl-30b                        # LLM model name

# Vector Database Configuration (REQUIRED)

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

```

## 🛡️ Security Architecture

### Encryption Strategies

#### Database-Level Encryption

```python

# SQLCipher for SQLite

conn.execute(f"PRAGMA key='{encryption_key}'")

```

#### Application-Level Encryption

```python
from cryptography.fernet import Fernet

class EncryptedStore:
    def __init__(self, key_path: str):
        self.cipher = self._load_or_create_key(key_path)

    def encrypt_content(self, content: str) -> str:
        return self.cipher.encrypt(content.encode()).decode()

    def decrypt_content(self, encrypted_content: str) -> str:
        return self.cipher.decrypt(encrypted_content.encode()).decode()

```

### Access Control

```python
def get_user_conversations(user_id: str, session_id: str = None):
    """Ensure users can only access their own conversations"""
    query = "SELECT * FROM conversations WHERE user_id = ?"
    params = [user_id]

    if session_id:
        query += " AND session_id = ?"
        params.append(session_id)

    return db.execute(query, params)

```

### Rate Limiting Architecture

Centralized rate limiting prevents abuse:

```python
class RateLimitManager:
    # Singleton managing per-tool Limiters
    limits = {
        "shell": (10, 60),  # 10 calls / min
        "git": (20, 60),    # 20 calls / min
        "file": (60, 60),   # 60 calls / min
        "web": (10, 60)     # 10 calls / min
    }

    def check_limit(tool_name):
        # Checks Token Bucket / Window
        # Raises RateLimitError if exceeded
        # Logs to AuditLogger
```

### Audit Logging

Security events are logged to `audit.log` via `AuditLogger`:

- **Events**: Tool approvals, blocks, rate limit hits, permission denials
- **Format**: `TIMESTAMP [LEVEL] User:SYSTEM Action:EVENT Resource:TARGET Details`

## 🧪 Testing Architecture

### Test Suite Overview

- **Unit Tests**: ~400 tests covering individual modules
- **Integration Tests**: ~80 tests covering component interactions
- **Security Tests**: ~40 tests covering security modules
- **Total**: 555 tests with 90%+ coverage target

### Test Component Integration

```text

┌──────────────────────────────────────────────────────────────────────────┐
│                            Testing Architecture                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────────────────┐  │
│   │  Unit Tests │      │ Integration │      │   Security Tests        │  │
│   │  (171 tests)│      │  (40 tests) │      │   (25 tests)            │  │
│   └──────┬──────┘      └──────┬──────┘      └────────────┬────────────┘  │
│          │                    │                          │               │
│          └────────────────────┴──────────────────────────┘               │
│                               │                                          │
│                               ▼                                          │
│                    ┌─────────────────────┐                               │
│                    │   Test Coverage     │                               │
│                    │   (>90% target)     │                               │
│                    └─────────────────────┘                               │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

```

### Test Categories

- **Unit Tests**: Isolated module testing with mock dependencies
- **Integration Tests**: Component interaction and workflow testing
- **Security Tests**: Path validation, input sanitization, rate limiting
- **Performance Tests**: Latency benchmarks and stress testing

## 📊 Performance Architecture

### Indexing Strategies

```sql
-- SQLite
CREATE INDEX idx_session_timestamp ON conversations(session_id, timestamp DESC);
CREATE INDEX idx_content_length ON conversations(LENGTH(content));

-- PostgreSQL
CREATE INDEX CONCURRENTLY idx_content_fts ON conversations USING
gin(to_tsvector('english', content));
CREATE INDEX CONCURRENTLY idx_metadata ON conversations USING gin(metadata);

```

### Query Optimization

```python

# Efficient pagination

def get_messages_paginated(session_id: str, page: int = 1, per_page: int = 50):
    offset = (page - 1) * per_page
    return db.execute('''
        SELECT * FROM conversations
        WHERE session_id = ?
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
    ''', (session_id, per_page, offset))

# Recent messages (most common query)

def get_recent_messages(session_id: str, hours: int = 24):
    return db.execute('''
        SELECT * FROM conversations
        WHERE session_id = ? AND timestamp > datetime('now', '-{} hours')
        ORDER BY timestamp DESC
    '''.format(hours), (session_id,))

```

## 🔄 Integration Points

### Service Dependencies

1. **LM Studio**: Local LLM server (<http://192.168.0.203:1234>)
2. **ChromaDB v2 Server**: Vector database (<http://192.168.0.204:8000>)
3. **Ollama**: Embedding server (<http://192.168.0.204:11434>)

### Service Startup Commands

```bash

# Terminal 1: LM Studio (load qwen3-vl-30b model)

m studio --start-server

# Terminal 2: ChromaDB v2 Server

chroma run --host 192.168.0.204 --port 8000 --path ./chroma_data

# Terminal 3: Ollama

ollama serve
```

## 📋 Key Features Matrix

| Feature             | Status  | Description                                               |
| ------------------- | ------  | --------------------------------------------------------- |
| Dual Interfaces     | ✅      | GUI (PyQt6) and CLI with full feature parity              |
| AI Learning System  | ✅      | ChromaDB v2 vector database integration                   |
| Document Processing | ✅      | 80+ file types with unified processing                    |
| Spaces System       | ✅      | Isolated workspaces with separate knowledge bases         |
| Tool Calling        | ✅      | 13 AI tools for file, shell, git, search, and knowledge   |
| Shell Execution     | ✅      | CLI-only shell commands with allowlist security           |
| MCP Integration     | ✅      | External tool servers via stdio/HTTP/SSE                  |
| Tool Approval       | ✅      | Per-tool ask/always/never permission controls             |
| Git Integration     | ✅      | AI tools for git status, diff, log, show                  |
| Code Search         | ✅      | Fast ripgrep-based regex search                           |
| Memory Persistence  | ✅      | SQLite database for conversation history                  |
| Markdown Support    | ✅      | Rich text rendering in GUI                                |
| Web Ingestion       | ✅      | URL learning capability via `/web` command                |
| Personalized Memory | ✅      | Mem0 for user preference tracking                         |
| Smart Chunking      | ✅      | 1500-char chunks with paragraph-aware boundaries          |
| Quality Filtering   | ✅      | Automatic filtering of binary files and low-value content |

## 🎯 Design Principles

1. **Local-First**: All processing happens locally for privacy
2. **Modular Architecture**: Components can be updated independently
3. **Feature Parity**: GUI and CLI interfaces must have identical functionality
4. **Extensible**: Easy to add new tools and features
5. **Secure**: Encryption and access control built-in
6. **Performant**: Optimized queries and caching strategies
7. **User-Centric**: Focus on developer productivity and experience

## 🔗 Cross-Reference Guide

For more detailed information, refer to:

- **MANUAL.md**: User-facing documentation and usage guides
- **MIGRATION.md**: Migration instructions and breaking changes
- **ROADMAP.md**: Future development plans and feature timeline

This architecture document serves as the canonical reference for the system's
design and components.
