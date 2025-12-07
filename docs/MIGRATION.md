# Migration and Database Guide

This guide covers the currently implemented database backends and important migration information for the AI Assistant application.

## ⚠️ Breaking Changes in v0.1

### Configuration Requirements

**IMPORTANT**: Starting with v0.1, the application requires a `.env` file and no longer uses hardcoded defaults.

#### What Changed
- **Before**: Application worked with or without `.env`, used hardcoded fallbacks, ChromaDB was optional
- **After**: Application **requires** `.env` file, **no hardcoded defaults exist**, **ChromaDB is mandatory** for learning features

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

### New Tool Capabilities

**MAJOR ENHANCEMENT**: v0.1 introduces **7 AI tools** that work together with the existing knowledge management system:

#### Tool Integration Architecture
```
User Query → AI (qwen3-vl-30b) → Tool Selection → Execution → Result Integration → AI Response
     ↓              ↓                      ↓            ↓              ↓              ↓
File System    Multimodal Analysis     Secure        Structured     Conversation     Contextual
Operations     & Understanding        Execution      Data Output    Context         Responses
```

#### Tool Result Handling & AI Usage

**Tool Result Lifecycle:**
1. **Execution**: AI calls tool → Tool runs → Returns structured result
2. **Storage**: Results stored in conversation memory (Python variables, not files)
3. **Integration**: Results formatted and added to conversation history as HumanMessage
4. **Processing**: Results become part of LLM's thinking context for response generation
5. **Response**: AI uses tool data to craft informed, accurate responses
6. **Persistence**: Results saved in SQLite conversation history

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
5. **`parse_document()`** - Extract text/tables/forms/layout from documents (ready)
6. **`learn_information()`** - Store in knowledge base (ready)
7. **`search_knowledge()`** - Query learned information (ready)

#### Tool Ecosystem Benefits
- **Document Intelligence**: qwen3-vl-30b's multimodal capabilities for OCR, table extraction, form analysis
- **Knowledge Synthesis**: Tools work together to build comprehensive understanding
- **Result Integration**: Tool outputs seamlessly feed into AI response generation
- **Autonomous Operations**: AI can execute complex multi-step tasks without user intervention
- **Persistent Learning**: Document analyses stored in ChromaDB for future reference
- **Semantic Search**: Vector-based retrieval of learned information and document content

#### Migration for Tool Usage
1. **No additional configuration needed** - tools use existing ChromaDB/Ollama setup
2. **Tools are automatically available** in both GUI and CLI interfaces
3. **Natural language triggers** - AI recognizes intent and calls appropriate tools
4. **Fallback to manual commands** - all tools accessible via slash commands if needed

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
DB_PATH=conversation_memory.db                # SQLite database path

# System Configuration
KMP_DUPLICATE_LIB_OK=TRUE                     # OpenMP workaround
```

## 🗄️ Database Implementation

## 🗄️ Implemented Databases

### SQLite (Recommended)

#### Advantages
- **Zero configuration** - no server setup required
- **ACID transactions** - data integrity guaranteed
- **Concurrent access** - handles multiple processes safely
- **SQL querying** - can search/filter conversation history
- **File-based** - easy backup and portability
- **Built-in encryption** support with SQLCipher

#### Schema Design
```sql
-- Conversations table
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_id TEXT,
    message_type TEXT NOT NULL CHECK (message_type IN ('system', 'human', 'ai')),
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

#### Python Implementation
```python
import sqlite3
import json
from datetime import datetime
import hashlib

class SQLiteMemoryStore:
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    user_id TEXT,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    checksum TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_session_timestamp ON conversations(session_id, timestamp)')

    def save_message(self, session_id: str, message_type: str, content: str,
                    user_id: str = None, metadata: Dict[str, Any] = None) -> str:
        message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]}"
        checksum = hashlib.sha256(content.encode()).hexdigest()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO conversations (id, session_id, user_id, message_type, content, metadata, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (message_id, session_id, user_id, message_type, content,
                  json.dumps(metadata) if metadata else None, checksum))

        return message_id

    def load_conversation(self, session_id: str, limit: int = None) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT id, message_type, content, timestamp, metadata, checksum
                FROM conversations
                WHERE session_id = ?
                ORDER BY timestamp
            '''
            params = [session_id]

            if limit:
                query += ' LIMIT ?'
                params.append(limit)

            cursor = conn.execute(query, params)
            messages = []

            for row in cursor:
                message = {
                    'id': row[0],
                    'type': row[1],
                    'content': row[2],
                    'timestamp': row[3],
                    'metadata': json.loads(row[4]) if row[4] else None,
                    'checksum': row[5]
                }
                messages.append(message)

        return messages
```

#### Encryption Setup
```bash
# Install SQLCipher
pip install pysqlcipher3

# Use encrypted connection
import sqlcipher3 as sqlite3

# Connect with encryption key
conn = sqlite3.connect('conversations.db')
conn.execute(f"PRAGMA key='{encryption_key}'")
```



## 🔐 Security Considerations

### Encryption Strategies

#### 1. Database-Level Encryption
```python
# SQLCipher for SQLite
conn.execute(f"PRAGMA key='{encryption_key}'")

# PostgreSQL with pgcrypto
CREATE EXTENSION pgcrypto;
UPDATE users SET password = crypt('new_password', gen_salt('bf', 8));

# MongoDB with encryption at rest
# Configure mongod with encryption options
```

#### 2. Application-Level Encryption
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

#### Multi-Tenant Isolation
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

## 📊 Performance Optimization

### Indexing Strategies
```sql
-- SQLite
CREATE INDEX idx_session_timestamp ON conversations(session_id, timestamp DESC);
CREATE INDEX idx_content_length ON conversations(LENGTH(content));

-- PostgreSQL
CREATE INDEX CONCURRENTLY idx_content_fts ON conversations USING gin(to_tsvector('english', content));
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
```

### Data Validation
```python
def validate_migration(source_count: int, target_count: int) -> bool:
    """Validate that migration preserved all data"""
    if source_count != target_count:
        logger.error(f"Migration count mismatch: {source_count} -> {target_count}")
        return False

    # Additional checksum validation
    # Compare content hashes between source and target

    return True
```

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
```

### Performance Metrics
```python
def log_query_performance(query_name: str, start_time: float, result_count: int):
    """Log query performance for monitoring"""
    duration = time.time() - start_time
    logger.info(f"Query '{query_name}' took {duration:.3f}s, returned {result_count} results")

    # Could send to monitoring system
    # metrics_client.histogram('db_query_duration', duration, tags={'query': query_name})
```

This guide provides a comprehensive foundation for implementing various database backends for conversation memory storage, with security, performance, and scalability considerations.