# Migration and Database Guide

This guide covers the currently implemented database backends and important migration information for the AI Assistant application.

## ⚠️ Breaking Changes in v0.1.1

### Configuration Requirements

**IMPORTANT**: Starting with v0.1.1, the application requires a `.env` file and no longer uses hardcoded defaults.

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

**MAJOR ENHANCEMENT**: v0.1.1 introduces **8 AI tools** that work together with the existing knowledge management system:

#### Tool Integration Architecture

For detailed tool integration architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).

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
DB_PATH=db/history.db                         # SQLite database path

# System Configuration
KMP_DUPLICATE_LIB_OK=TRUE                     # OpenMP workaround
```

## 🗄️ Database Implementation

For comprehensive database architecture details, please refer to the [ARCHITECTURE.md](ARCHITECTURE.md) document.

### SQLite (Recommended)

**Advantages:**
- Zero configuration - no server setup required
- ACID transactions - data integrity guaranteed
- Concurrent access - handles multiple processes safely
- SQL querying - can search/filter conversation history
- File-based - easy backup and portability
- Built-in encryption support with SQLCipher

**Complete Schema Design and Implementation:** See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed SQLite schema, Python implementation, and encryption setup.



## 🔐 Security Considerations

For comprehensive security architecture details, please refer to the [ARCHITECTURE.md](ARCHITECTURE.md) document.

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

**Complete Security Implementation:** See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed encryption strategies, access control mechanisms, and security best practices.

## 📊 Performance Optimization

For comprehensive performance architecture details, please refer to the [ARCHITECTURE.md](ARCHITECTURE.md) document.

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

**Complete Performance Implementation:** See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed indexing strategies, query optimization techniques, and performance best practices.

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