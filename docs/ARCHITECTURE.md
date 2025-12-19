# AI Assistant Architecture

This document provides a comprehensive architectural overview of the AI
Assistant
application, serving as a reference for all other documentation files.

## 🏗️ System Architecture

### High-Level Overview (v0.2.0 - Modular Architecture)

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
  │ 8 handlers │    │  8 tools     │   │   (Memory)    │
  └─────┬──────┘    └──────┬───────┘   └──────┬────────┘
        │                   │                   │
  ┌─────▼──────┐    ┌──────▼───────┐   ┌──────▼────────┐
  │  Security  │    │   VectorDB   │   │    Cache      │
  │ Validators │    │  (ChromaDB)  │   │  (In-memory)  │
  └────────────┘    └──────────────┘   └───────────────┘
        │
  ┌─────▼──────────────┐
  │ Legacy Commands    │ (15 handlers - being migrated)
  │                    | (src/commands/handlers/legacy_commands.py)
  └────────────────────┘

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

### 1. AI Tools (8 Tools)

The AI has access to 8 powerful tools for various operations:

| Tool Name                   | Description                                          | Status              |
| --------------------------- | ---------------------------------------------------- | ------------------- |
| `read_file()`               | Read file contents                                   | ✅ Tested & Working  |
| `write_file()`              | Create/modify files                                  | ✅ Ready             |
| `list_directory()`          | Browse directories                                   | ✅ Ready             |
| `get_current_directory()`   | Show current path                                    | ✅ Tested & Working  |
| `parse_document()`          | Extract text/tables/forms/layout from documents      | ✅ Ready             |
| `learn_information()`       | Store in knowledge base                              | ✅ Ready             |
| `search_knowledge()`        | Query learned information                            | ✅ Ready             |
| `search_web()`              | Search the internet using DuckDuckGo                 | ✅ Ready             |

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

## 🔌 Plugin Architecture (v0.2.0)

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

```text

**Usage:**

```python
from src.core.context import get_context

ctx = get_context()
ctx.llm  # Access ChatOpenAI instance
ctx.vectorstore  # Access Chroma instance
ctx.conversation_history  # Access message history

```text

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
│       └── legacy_commands.py  # 15 legacy handlers (being migrated)
├── tools/              # Tool plugin system
│   ├── registry.py     # ToolRegistry dispatcher
│   └── executors/      # Auto-registering executors
├── storage/            # Persistence layer
├── security/           # Security enforcement
└── vectordb/           # Knowledge storage

```text

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

```text

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

```text

## 🛡️ Security Architecture

### Encryption Strategies

#### Database-Level Encryption

```python

# SQLCipher for SQLite

conn.execute(f"PRAGMA key='{encryption_key}'")

```text

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

```text

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

```text

## 🧪 Testing Architecture

### Test Suite Overview

- **Unit Tests**: 171 tests covering individual modules
- **Integration Tests**: 40 tests covering component interactions
- **Security Tests**: 25 tests covering security modules
- **Total**: 240+ tests with 90%+ coverage target

### Test Component Integration

```text

┌──────────────────────────────────────────────────────────────────────────┐
│                            Testing Architecture                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────────────────┐  │
│   │  Unit Tests │      │ Integration │      │   Security Tests       │  │
│   │  (171 tests)│      │  (40 tests) │      │   (25 tests)           │  │
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

```text

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

```text

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

```text

## 🔄 Integration Points

### Service Dependencies

1. **LM Studio**: Local LLM server (http://192.168.0.203:1234)
2. **ChromaDB v2 Server**: Vector database (http://192.168.0.204:8000)
3. **Ollama**: Embedding server (http://192.168.0.204:11434)

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

| Feature              | Status  | Description                                                   |
| -------------------- | ------- | ------------------------------------------------------------- |
| Dual Interfaces      | ✅       | GUI (PyQt6) and CLI with full feature parity                  |
| AI Learning System   | ✅       | ChromaDB v2 vector database integration                       |
| Document Processing  | ✅       | 80+ file types with unified processing                        |
| Spaces System        | ✅       | Isolated workspaces with separate knowledge bases             |
| Tool Calling         | ✅       | 8 AI tools for file operations and knowledge management       |
| Memory Persistence   | ✅       | SQLite database for conversation history                      |
| Markdown Support     | ✅       | Rich text rendering in GUI                                    |
| Web Ingestion        | ✅       | URL learning capability via `/web` command                    |
| Personalized Memory  | ✅       | Mem0 for user preference tracking                             |
| Smart Chunking       | ✅       | 1500-char chunks with paragraph-aware boundaries              |
| Quality Filtering    | ✅       | Automatic filtering of binary files and low-value content     |

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
- **AGENTS.md**: Comprehensive agent documentation and technical details

This architecture document serves as the canonical reference for the system's
design and components.
