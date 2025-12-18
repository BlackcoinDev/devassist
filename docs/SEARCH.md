# Search and RAG (Retrieval-Augmented Generation) in DevAssist

DevAssist uses **Retrieval-Augmented Generation (RAG)** to enhance AI responses with relevant knowledge from your learned documents. This document explains how the search system works, how to control it, and how to maximize its effectiveness.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [Architecture](#architecture)
4. [Search Methods](#search-methods)
5. [Context Modes](#context-modes)
6. [Learning Features](#learning-features)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Using Context in Conversations

```bash
# Check current context mode
/context

# Enable context for every query (full RAG mode)
/context on

# Let AI decide when to use context (default, most efficient)
/context auto

# Disable context searching
/context off
```

### Teaching DevAssist

```bash
# Remember a piece of information
/learn Python is a high-level programming language with dynamic typing

# Bulk import a codebase into the knowledge base
/populate /path/to/your/project

# Search what you've taught DevAssist (ask the AI, it will search automatically)
You: "What do you know about Python programming fundamentals?"
# AI autonomously calls search_knowledge tool and responds with context
```

---

## Core Concepts

### What is RAG?

**Retrieval-Augmented Generation** combines two processes:

1. **Retrieval**: Finding relevant documents from your knowledge base
2. **Generation**: Using those documents to improve AI responses

**Example:**
- User: "How does our authentication system work?"
- System: Searches knowledge base → finds auth docs → provides them to AI
- AI: Incorporates the docs → gives more accurate, specific answer about YOUR system

### Key Differences: Semantic vs Keyword Search

DevAssist uses **semantic search** (not keyword search):

| Aspect | Semantic Search (DevAssist) | Keyword Search |
|--------|---------------------------|-----------------|
| **How it works** | Converts text to embeddings (vector numbers), finds similar meanings | Looks for exact text matches |
| **Query**: "How to write Python code" | Finds docs about "programming in Python" ✅ | Misses it (no keyword match) ❌ |
| **Intelligence** | Understands context and meaning | Simple pattern matching |
| **Flexibility** | High—finds related concepts | Low—needs exact words |
| **Speed** | Medium (embedding generation) | Very fast |

---

## Architecture

### Component Overview

```
User Query
    ↓
[1] AI Decision Layer
    • Context Mode: auto/on/off
    • Decides if search is needed
    ↓
[2] Embedding Generation (Ollama)
    • Converts query to vector (384-dimensional)
    • Uses qwen3-embedding model
    ↓
[3] Vector Search (ChromaDB)
    • Compares query vector to learned document vectors
    • Returns k=3-5 most similar documents
    ↓
[4] Result Caching
    • Stores results in memory + disk (query_cache.json)
    • Same query returns instantly on re-run
    ↓
[5] Context Injection
    • Formats results as "From knowledge base: ..."
    • Appends to AI's context window
    ↓
AI Response (using context + general knowledge)
```

### Storage Architecture (Three-Tier System)

```
SQLite (history.db)
├─ Purpose: Conversation history storage
├─ Query speed: ~1ms (transactional)
└─ Capacity: Unlimited conversations

ChromaDB v2 (Remote server)
├─ Purpose: Semantic search on learned documents
├─ Query speed: ~50-200ms (vector operations)
├─ Capacity: Thousands of documents per space
└─ Collections: One per space (space_name → knowledge_base or space_{name})

In-Memory Cache (QUERY_CACHE)
├─ Purpose: Fast repeat queries
├─ Query speed: <1ms (instant)
├─ Capacity: Last 500-1000 queries
└─ Persistence: query_cache.json
```

---

## Search Methods

### 1. **Semantic Search (Knowledge Base)**

**Function**: `get_relevant_context()` (src/main.py:1084)

Searches learned documents using embeddings:

```python
def get_relevant_context(
    query: str,
    k: int = 3,                    # Return top 3 results
    space_name: Optional[str] = None
) -> str:
    # 1. Check cache first (instant if cached)
    # 2. Generate query embedding via Ollama
    # 3. Find ChromaDB collection for space
    # 4. Query with embeddings (cosine similarity)
    # 5. Cache results for future use
    # 6. Return formatted context string
```

**When it's called:**
- Automatically when `context_mode == "on"`
- AI decides when `context_mode == "auto"` (recommended)
- Never when `context_mode == "off"`

**Example flow:**
```
User: "What are the performance best practices?"
       ↓
Context: on → get_relevant_context("What are the performance best practices?")
       ↓
Query embedding generated
       ↓
ChromaDB search finds:
  - "Use connection pooling for databases"
  - "Cache frequently accessed data"
  - "Profile before optimizing"
       ↓
AI response: "Based on your knowledge base: [context]. Additionally..."
```

### 2. **Web Search (Knowledge from Internet)**

**Function**: `execute_web_search()` (src/main.py:3007)

Uses DuckDuckGo API for real-time information:

```python
def execute_web_search(query: str) -> dict:
    # 1. Enhance query if needed (e.g., add "cryptocurrency" context)
    # 2. Call DuckDuckGo API (max 10 results)
    # 3. Return raw results with title, link, snippet
```

**When it's called:**
- AI autonomously decides based on query type
- Used for current events, general knowledge, external info
- Not subject to context mode (independent tool)

**Example:**
```
User: "What's the latest in AI?"
AI decides: This needs current info → calls search_web()
Result: Latest news articles from internet
```

### 3. **AI Tool: search_knowledge()**

**Function**: `execute_search_knowledge()` (src/main.py:3330)

Wrapper tool that AI can call explicitly:

```python
def execute_search_knowledge(query: str, limit: int = 5) -> dict:
    # Calls get_relevant_context() with configurable limit
    # Returns structured result: {success, query, results, result_count}
```

**When AI calls it:**
- User asks meta questions: "What do you know about X?"
- Debugging: "Show me what you learned about authentication"
- Verification: "Find the docs on feature Y"

---

## Context Modes

DevAssist has three context modes that control when knowledge base search happens:

### Mode: `auto` (Default) ⭐ Recommended

AI intelligently decides when to search:

```
User: "What's 2+2?"
→ AI: No context needed, responds "4" (instant)

User: "How does our authentication work?"
→ AI: Context needed, searches knowledge base, responds with specifics

User: "What's the capital of France?"
→ AI: No context needed (general knowledge), responds "Paris"
```

**Advantages:**
- Fastest response times (avoids unnecessary searches)
- Most efficient (no redundant vector operations)
- Best accuracy (AI knows when context helps)

**Enable:**
```bash
/context auto
```

### Mode: `on` (Always Search)

Always includes knowledge base context with every query:

```
User: "What's 2+2?"
→ Searches knowledge base (slower)
→ Returns context if found, else empty
→ AI responds "4 (from math docs)" or just "4"
```

**Advantages:**
- Ensures all learned info is considered
- Good for debugging why knowledge isn't being used

**Disadvantages:**
- Slower (extra search for every query)
- May include irrelevant context

**Enable:**
```bash
/context on
```

### Mode: `off` (Never Search)

Never searches knowledge base:

```
User: "How does our system work?"
→ No search
→ AI responds using only general knowledge
```

**Advantages:**
- Fastest (no embedding/search overhead)
- Useful for testing general AI capabilities

**Disadvantages:**
- AI forgets everything you taught it
- Can't access learned documents

**Enable:**
```bash
/context off
```

### Checking Current Mode

```bash
/context
# Output:
# 🎯 Current context mode: auto
# Options: auto, on, off
# - auto: AI decides when to include context
# - on: Always include available context
# - off: Never include context from knowledge base
```

---

## Learning Features

### Teaching DevAssist (Remember Information)

#### Method 1: `/learn` Command

Remember a single piece of information:

**Note:** There is no `/search` slash command. To search your knowledge base:
- Ask the AI a question and it autonomously calls the `search_knowledge` tool
- Use `/context on` to ensure knowledge base is searched
- Use `/context auto` (default) for smart searching

#### Method 2: Via AI Autonomous Search

```bash
/learn Python functions are first-class objects that can be passed as arguments
```

**What happens:**
1. Text is converted to embedding (vector)
2. Stored in ChromaDB with metadata (timestamp, source)
3. Indexed for semantic search
4. Returns instantly

**Use cases:**
- Team standards or conventions
- Important decisions
- Technical explanations
- Configuration values
- Best practices

**Example session:**
```bash
You: /learn Our database uses PostgreSQL 15 with connection pooling enabled

DevAssist: ✅ Learned: "Our database uses PostgreSQL 15 with connection pooling enabled"

[Later...]

You: What database do we use?
DevAssist: Based on what you've taught me, you use PostgreSQL 15 with connection pooling enabled.
```

#### Method 2: `/populate` Command

Bulk import an entire codebase:

```bash
# Basic usage
/populate /path/to/your/project

# Dry run (validate without writing)
/populate /path/to/your/project --dry-run

# Clear existing knowledge, then repopulate
/populate /path/to/your/project --clear

# Real-world example
/populate ~/projects/myapp --clear
```

**Process:**
1. Recursively scans directory for code files
2. Extracts content from 80+ file types:
   - Languages: Python, JavaScript, Java, Go, Rust, etc.
   - Documents: PDF, DOCX, XLSX, Markdown, etc.
   - Code: Source files with syntax preservation
3. Chunks content into 1500-character segments
4. Generates embeddings for each chunk
5. Stores with metadata (filename, line numbers)

**Options:**
- `--dry-run`: Validate without writing to database
- `--clear`: Delete existing collection before repopulating

**Progress:**
```
🔍 Starting codebase population from: /Users/user/projects/myapp
🔧 Using direct ChromaDB API for optimal reliability and performance
This may take some time for large codebases...

Processing files...
✅ 342 files processed
✅ 1,847 chunks created and embedded
✅ Successfully added to knowledge base
```

**Performance:**
- Small project (< 100 files): ~10-30 seconds
- Medium project (100-500 files): ~1-3 minutes
- Large project (500+ files): ~5-15 minutes

### Document Learning (AI Tool)

The `learn_information()` AI tool allows the model to autonomously save information:

```bash
You: Remember that we migrated from MySQL to PostgreSQL last month

DevAssist: [Calls learn_information tool]
✅ Learned: "Migrated from MySQL to PostgreSQL last month"

[Later...]

You: When did we switch databases?
DevAssist: Based on what I've learned, you migrated from MySQL to PostgreSQL last month.
```

---

## Performance Optimization

### Caching Strategy

DevAssist uses **two-level caching** for maximum performance:

#### Level 1: In-Memory Cache (QUERY_CACHE)

**How it works:**
- Cache key: `{space_name}:{query}:{k}`
- Stores last 1000 query results
- Lookup time: <1ms (instant)

**Example:**
```bash
User: "Tell me about Python"
→ Search → 50ms delay → AI responds

User: "Tell me about Python" [again]
→ Cache hit → <1ms → AI responds instantly
```

#### Level 2: Disk Cache (query_cache.json)

**How it works:**
- Persists in-memory cache to disk
- Survives application restarts
- Automatically saved every 50 queries
- Limited to 1000 entries (newest kept)

**Files:**
```
devassist/
├── query_cache.json          # Search result cache
└── embedding_cache.json      # Document embedding cache
```

### Cache Management

**View cache stats:**
```bash
# Check cache size (in code debug mode)
# QUERY_CACHE contains {space}:{query}:{k} → [results]
```

**Clear cache (if needed):**
```bash
# Remove query_cache.json to reset
rm query_cache.json

# Or just clear space-specific cache by changing space
/space myspace
```

### Optimization Tips

1. **Use `context auto` (not `on`)**
   - Saves redundant searches: ~50-100ms per query
   - AI knows when context is needed

2. **Reuse queries**
   - Ask similar questions → cache hits
   - Same question twice → instant response

3. **Batch `/populate` operations**
   - Populate once with `--clear` flag
   - Don't repeatedly populate same directory

4. **Use specific queries**
   - Good: "How do we handle authentication?"
   - Bad: "everything" (too broad)

5. **Monitor knowledge base size**
   - Large knowledge base = slower searches
   - Consider using spaces for different projects
   - Use `/populate . --clear` to reset if needed

---

## Spaces and Search Isolation

Each **space** is a separate knowledge base:

```bash
# Switch to project A knowledge base
/space projectA
You: /populate ~/projects/projectA

# Switch to project B
/space projectB
You: /populate ~/projects/projectB

# Queries only search current space
You: "How do we handle authentication?"
→ Searches projectB knowledge base only
→ projectA docs are ignored
```

**Benefits:**
- Isolate knowledge by project
- Prevent cross-project confusion
- Faster searches (smaller collection)
- Easy project switching

**Collections:**
```
ChromaDB Collections:
├── knowledge_base (default space)
├── space_projectA
├── space_projectB
└── space_research
```

---

## Troubleshooting

### "No relevant context found" or empty results

**Problem:** Searched knowledge base but got no results.

**Causes & Solutions:**

1. **Knowledge base is empty**
   ```bash
   # Check if you've learned anything
   /populate /path/to/project
   # or
   /learn Some important information
   ```

2. **Context mode is off**
   ```bash
   /context on    # or auto
   ```

3. **Wrong space selected**
   ```bash
   /space         # Check current space
   /space myspace # Switch to right space
   ```

4. **Query doesn't match learned content**
   ```bash
   # Good queries (ask the AI):
   "What database do we use?" (finds "PostgreSQL 15" docs)
   "How do we handle authentication?" (finds auth system docs)

   # Poor queries:
   "Tell me about xyz" (very specific, may not match learned content)
   ```

### Slow search responses

**Problem:** Context retrieval takes 2-5 seconds.

**Causes & Solutions:**

1. **ChromaDB server not running**
   ```bash
   # Terminal 2: Start ChromaDB
   chroma run --host 192.168.0.204 --port 8000 --path ./chroma_data
   ```

2. **Context mode is `on`** (searching every query)
   ```bash
   /context auto  # Let AI decide
   ```

3. **Large knowledge base**
   ```bash
   # Check collection size
   /space           # List spaces

   # If too large, consider:
   /space projectA
   /populate . --clear  # Only keep current project
   ```

4. **Ollama not running** (embedding generation slow)
   ```bash
   # Terminal 3: Start Ollama
   ollama serve
   ```

### LLM doesn't use the context

**Problem:** Context found but AI doesn't incorporate it.

**Diagnosis:**
```bash
# Check if context is being retrieved
/context on     # Force context for every query
/search "your question"  # Manually search

# If results appear but AI ignores them, try:
# - Rephrase question (more specific)
# - Clear cache: rm query_cache.json
# - Check LEARNING_MODE with /learning command
```

### ChromaDB connection errors

**Problem:** "Failed to retrieve context: Connection error"

**Debugging:**
```bash
# Check if ChromaDB server is running
curl http://192.168.0.204:8000/api/heartbeat

# If not running, start it:
chroma run --host 192.168.0.204 --port 8000 --path ./chroma_data

# Check .env configuration
cat .env | grep CHROMA
```

### Cache growing too large

**Problem:** `query_cache.json` becomes huge (slow startup).

**Solution:**
```bash
# Automatically managed (max 1000 entries)
# If needed, clear:
rm query_cache.json

# App will recreate on next search
```

---

## Implementation Details

### Core Functions

The DevAssist modular architecture organizes search functionality across several focused modules:

| Function | Module Location | Purpose |
|----------|-----------------|---------|
| `get_relevant_context()` | `src/core/context_utils.py` | Semantic search with caching |
| `execute_search_knowledge()` | `src/tools/executors/knowledge_tools.py` | AI tool for knowledge base searches |
| `execute_web_search()` | `src/tools/executors/web_tools.py` | DuckDuckGo web search tool |
| `handle_context_command()` | `src/commands/handlers/config_commands.py` | `/context` command handler |
| `load_query_cache()` | `src/storage/cache.py` | Load search result cache from disk |
| `save_query_cache()` | `src/storage/cache.py` | Persist search cache to disk |
| `handle_learn_command()` | `src/commands/handlers/learning_commands.py` | `/learn` command handler |
| `handle_populate_command()` | `src/commands/handlers/learning_commands.py` | `/populate` command handler |

**Architecture Notes:**
- **Commands** auto-register via `@CommandRegistry.register()` decorator
- **Tools** auto-register via `@ToolRegistry.register()` decorator
- Search functions integrate with `ApplicationContext` for accessing ChromaDB and embeddings
- All search operations use the unified `ChromaDBClient` class (`src/vectordb/client.py`)

### Environment Variables

```bash
# ChromaDB Configuration
CHROMA_HOST=192.168.0.204
CHROMA_PORT=8000

# Embedding Configuration
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=qwen3-embedding

# LLM Configuration
LM_STUDIO_URL=http://localhost:1234/v1
MODEL_NAME=qwen3-vl-30b

# Search Configuration
MAX_HISTORY_PAIRS=50
TEMPERATURE=0.7
MAX_INPUT_LENGTH=2000
```

### Cache Files

```
devassist/
├── query_cache.json          # Search result cache
│                             # Format: {space:query:k: [results]}
└── embedding_cache.json      # Document embedding cache
```

---

## Best Practices

### ✅ DO

- Use `context auto` (default, most efficient)
- Teach DevAssist your project's standards with `/learn`
- Use `/populate` to bulk import codebases
- Ask specific questions for better matches
- Use different spaces for different projects
- Check `/context` status before debugging

### ❌ DON'T

- Leave `context on` for casual questions (slower)
- Use `context off` if you want to use learned knowledge
- Teach highly redundant information multiple times
- `/populate` same directory repeatedly
- Ask vague questions ("tell me everything")
- Mix unrelated projects in same space

---

## Performance Benchmarks

**Note:** These are estimated timings based on typical operation patterns. Actual performance depends on hardware, model size, network conditions, and knowledge base size.

### Response Times (Context Modes)

Based on official expectations (CLAUDE.md):
- **LLM base response time**: 2-5 seconds
- **Search operations**: Additional overhead varies by knowledge base size

```
Context Mode: off
└─ Pure LLM response: ~2-5 seconds

Context Mode: auto (AI decides search needed)
├─ No search required: ~2-5 seconds (same as off)
└─ Search required: ~2.5-6 seconds (includes search time)

Context Mode: on (always search)
└─ Every query: ~2.5-6 seconds (search for every query)

Cache Hit (repeat query with cached search)
└─ Search step: <1ms (instant cache lookup)
└─ Total response: ~2-5 seconds (LLM dominates timing)
```

### Search Operation Timing

These are approximate timings for the ChromaDB query operation only (not including LLM response time):

| Knowledge Base Size | Search Time | Embedding Generation |
|-------------------|------------|---------------------|
| <10 docs | ~10-20ms | ~30-50ms |
| 10-100 docs | ~20-50ms | ~30-50ms |
| 100-1000 docs | ~50-100ms | ~30-50ms |
| 1000+ docs | ~100-200ms | ~30-50ms |

**Caching Impact:**
- First query: Full embedding + search time
- Repeat query (cache hit): <1ms (instant, from memory)

---

## Roadmap & Future Improvements

**Planned:**
- [ ] Hybrid search (semantic + keyword)
- [ ] Query expansion and reranking
- [ ] Automatic knowledge summarization
- [ ] Multi-model embeddings
- [ ] Real-time knowledge updates
- [ ] Search analytics and insights

**Under consideration:**
- GPT-4 level semantic understanding
- Pinecone integration for larger scale
- Knowledge graph construction
- Automatic relevance feedback

---

## Related Documentation

- [CLAUDE.md](./CLAUDE.md) - Project overview and configuration
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [MANUAL.md](./MANUAL.md) - User guide (includes `/learn`, `/context`, `/populate`)
- [ROADMAP.md](./ROADMAP.md) - Future features

---

## Quick Reference

```bash
# Check context status
/context

# Control context (auto = AI decides, on = always, off = never)
/context auto
/context on
/context off

# Search knowledge base (ask the AI - it autonomously calls search_knowledge)
You: "What do you know about [topic]?"

# Teach DevAssist
/learn Important information to remember

# Bulk import codebase
/populate /path/to/project
/populate /path/to/project --dry-run
/populate /path/to/project --clear

# Switch knowledge base
/space myproject
/space list

# Check learning mode
/learning
/learning normal
```

---

**Last Updated:** December 2024
**Version:** DevAssist v0.1.1
