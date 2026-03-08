# AI Assistant Chat Application v0.3.0 - Shell & MCP Integration

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/BlackcoinDev/devassist)

An advanced interactive AI chat assistant powered by LangChain, LM Studio, and ChromaDB vector database. Features
comprehensive learning capabilities, multi-format document processing, robust error handling, and complete feature
parity between GUI and CLI interfaces.

## 🌟 Features v0.3.0

### New in v0.3.0

- **🔧 Shell Execution (CLI)**: AI can run shell commands with allowlist-based safety (git, npm, python, etc.)
- **🔌 MCP Support**: Model Context Protocol integration for external tool servers (stdio, HTTP, SSE transports)
- **📂 Git Integration**: AI tools for git status, diff, log, show operations
- **🔍 Code Search**: Fast ripgrep-based regex search across codebase
- **🛡️ Tool Approval System**: Per-tool ask/always/never permission controls
- **🔒 Rate Limiting**: Centralized rate limiting for Shell (10/min), Git (20/min), and File (60/min) operations
- **⚡ Enhanced Caching**: Persistent LRU cache for embeddings and queries with file permission hardening (0o600)

### Core Features

- **🖥️ Modern GUI**: Beautiful PyQt6 interface with dark/light themes
- **🧠 Learning AI**: Teach the AI new information via /learn command that persists across sessions
- **🏢 Spaces System**: Isolated workspaces with separate knowledge bases
- **💾 Vector Database**: ChromaDB v2 server (required) for knowledge storage and retrieval
- **📚 Document Processing**: Unified processing via Docling for PDFs, Word, Excel, RTF, EPUB, and more
- **🌍 Web Ingestion**: Learn direct from URLs with `/web` command (powered by Docling)
- **📄 Advanced Document Analysis**: qwen3-vl-30b's multimodal capabilities for OCR, table extraction, form analysis, and

  layout understanding

- **🔧 Codebase Ingestion**: Bulk import entire projects with intelligent file type detection
- **📘 Auto-learn**: AI automatically learns project documentation at startup
- **🔄 Model Switching**: Easy switching between different AI models
- **💬 Persistent Memory**: SQLite database for conversation history (no JSON files)
- **🎯 Context Awareness**: AI uses learned information in relevant conversations
- **👤 Personalized Memory**: Learns user preferences and style automatically via Mem0
- **🧠 Mem0 AI Integration**: Advanced memory system that creates dynamic user profiles, remembers preferences, coding

  style, and personal context for better personalized responses

- **🛠️ AI Tool Calling**: qwen3-vl-30b supports 13 powerful tools for file operations, shell commands, git, code search,

  document processing, knowledge management, and web search

- **⚡ Streaming Responses**: Real-time response display for better user experience
- **🔍 Verbose Logging**: Optional detailed step-by-step AI processing visibility
- **🛠️ Rich Commands**: Comprehensive slash command system in both GUI and CLI
- **🎨 Markdown Support**: Rich text formatting in GUI with HTML rendering
- **🔧 Configuration**: **Requires** `.env` file - no hardcoded defaults
- **🛡️ Error Handling**: Robust error handling with graceful degradation
- **✅ Type Safety**: Full MyPy type checking with comprehensive linting

## 📋 Recent Refactoring (v0.2.0)

### 🏗️ Modular Architecture Improvements

**Command System Refactoring:**

- ✅ **Reduced main.py complexity** by separating command functionality
- ✅ **Maintained 100% backward compatibility** - all existing commands work unchanged
- ✅ **All 240+ tests still passing** - no functionality lost

### 🧪 Comprehensive Test Suite

**Test Coverage Status:**

- **Total Tests**: 830 tests (394 unit + 25 integration + 34 security)
- **Coverage**: 49% overall, 71% modules ≥90% (20/28 modules)
- **Pass Rate**: 100% (394 passing, 10 skipped GUI tests)
- **Execution Time**: ~55-65 seconds
- **Test Quality**: 44 new tests added, 163 total increase (+64%)

**Test Categories:**

- **Unit Tests**: Isolated module testing with mock dependencies
- **Integration Tests**: Component interaction and workflow testing
- **Security Tests**: Path validation, input sanitization, rate limiting, and permission enforcement
- **Performance Tests**: Latency benchmarks, cache hit rates, and stress testing

**New Module Structure:**

```text
src/commands/handlers/
├── help_commands.py        # New command system
├── memory_commands.py     # New command system
├── database_commands.py   # New command system
├── learning_commands.py   # New command system
├── config_commands.py     # New command system
├── space_commands.py      # New command system
├── file_commands.py       # New command system
├── export_commands.py     # New command system
```

**Migration Path:** Commands use `@CommandRegistry.register()` decorators for
consistency across the command system.

## 📖 Documentation

- **[CLAUDE.md](CLAUDE.md)**: Developer guide with setup instructions and project guidelines
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Comprehensive system architecture, component diagrams, and technical

  implementation details

- **[MANUAL.md](docs/MANUAL.md)**: User guide with command reference and usage examples
- **[SEARCH.md](docs/SEARCH.md)**: Detailed search and RAG (Retrieval-Augmented Generation) documentation
- **[ROADMAP.md](docs/ROADMAP.md)**: Future development plans including security enhancements, Docling integration,

  Pydantic-AI, LangGraph, and more

- **[MIGRATION.md](docs/MIGRATION.md)**: Migration guide and version upgrade notes
- **[AGENTS.md](AGENTS.md)**: Agent guidelines and architecture documentation

## 🏗️ Architecture

```text

┌──────────────────────────────────────────────────────────────────────────┐
│                            DevAssist v0.3.0                             │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────────────────┐  │
│   │   GUI       │      │   CLI       │      │   Slash Commands        │  │
│   │  (PyQt6)    │      │  (Terminal) │      │  /learn /populate /help │  │
│   └──────┬──────┘      └──────┬──────┘      └────────────┬────────────┘  │
│          │                    │                          │               │
│          └────────────────────┴──────────────────────────┘               │
│                               │                                          │
│                               ▼                                          │
│                    ┌─────────────────────┐                               │
│                    │   LangChain Core    │                               │
│                    │   (Orchestration)   │                               │
│                    └──────────┬──────────┘                               │
│                               │                                          │
│     ┌─────────────────────────┼─────────────────────────┐                │
│     ▼                         ▼                         ▼                │
│ ┌──────────────┐      ┌─────────────┐      ┌─────────────────┐           │
│ │  AI Tools    │      │  Memory     │      │   Knowledge     │           │
│ │  (13 tools)  │      │  (SQLite)   │      │   (ChromaDB)    │           │
│ │ shell/git/   │      └─────────────┘      └─────────────────┘           │
│ │ search/mcp   │                                                         │
│ └──────┬───────┘                                                         │
│        │                                                                 │
│        ▼                                                                 │
│ ┌──────────────┐      ┌─────────────────────────────────────┐            │
│ │Tool Approval │      │           MCP Servers               │            │
│ │ask/always/   │      │  (stdio | HTTP | SSE transports)    │            │
│ │never         │      │  External tools via protocol        │            │
│ └──────────────┘      └─────────────────────────────────────┘            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LM Studio     │    │     Ollama      │    │   File System   │
│   (LLM API)     │    │  (Embeddings)   │    │   (Documents)   │
│  qwen3-vl-30b   │    │ qwen3-embedding │    │   80+ formats   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Shell Execution & MCP (v0.3.0)

### Shell Execution (CLI Only)

The AI can execute shell commands directly in CLI mode using an allowlist-based security model:

**Safe Commands** (run without confirmation):

```bash
git, npm, yarn, python, python3, pip, node, cargo, go, uv, pytest, make,
cat, ls, pwd, grep, rg, find, tree, docker, kubectl
```

**Blocked Commands** (always denied):

```bash
rm, sudo, chmod, chown, curl, wget, dd, mkfs
```

**Unknown Commands**: Require user confirmation before execution.

**Example Usage:**

```text
You: run npm install
AI: [Executes npm install automatically - safe command]

You: run custom_script.sh
AI: Command 'custom_script.sh' requires confirmation. Reply 'yes' to execute.
```

### MCP (Model Context Protocol) Support

Connect external tool servers via MCP protocol with three transport options:

| Transport | Use Case | Example |
| ----------- | ---------- | --------- |
| **stdio** | Local subprocess servers | `npx @modelcontextprotocol/server-filesystem` |
| **HTTP** | Remote REST-based servers | `http://localhost:8080/mcp` |
| **SSE** | Streaming notifications | `http://localhost:8081/sse` |

**Configuration** (`config/mcp_servers.json`):

```json
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
```

### Tool Approval System

Control which tools require confirmation before execution:

| Mode | Behavior |
| ------ | ---------- |
| `always` | Execute without asking (read-only tools) |
| `ask` | Prompt user before execution |
| `never` | Block execution entirely |

**Configuration** (`config/tool_approvals.json`):

```json
{
  "approvals": {
    "shell_execute": "ask",
    "write_file": "ask",
    "git_status": "always",
    "code_search": "always"
  }
}
```

To prevent abuse and resource exhaustion, tool execution is rate-limited:

| Tool Category | Limit | Period |
| ------------- | ----- | ------ |
| **Shell** | 10 calls | 1 minute |
| **Git** | 20 calls | 1 minute |
| **File Systems** | 60 calls | 1 minute |
| **Web** | 10 calls | 1 minute |
| **Default** | 30 calls | 1 minute |

Violations are logged to the security audit log.

## 📄 Document Processing Workflow

### PDF Processing Pipeline

1. **File Discovery**: `/populate <directory>` scans for supported document types (PDF, DOCX, XLSX, RTF, EPUB, TXT, MD,

   etc.)

2. **Content Extraction**: Specialized libraries extract text content:
   - **Unified**: Docling handles PDF, DOCX, XLSX, RTF, EPUB, HTML, and Images
   - **Performance**: High-fidelity text extraction with layout awareness
   - **Text Files**: Direct UTF-8 reading with encoding detection
3. **Text Chunking**: RecursiveCharacterTextSplitter creates 1500-character chunks with 200-character overlap for

   optimal retrieval

4. **Embedding Generation**: Ollama qwen3-embedding:latest converts text chunks to vector embeddings
5. **Vector Storage**: ChromaDB v2 server stores embeddings with metadata (file path, chunk index, modification time)
6. **Semantic Search**: User queries generate embeddings for similarity search against stored vectors
7. **Context Integration**: Relevant document chunks are included in AI responses for informed answers

### Supported File Types

- **Documents**: PDF, DOCX, RTF, EPUB
- **Spreadsheets**: XLSX
- **Text Files**: TXT, MD, RST, JSON, XML, CSV
- **Images**: PNG, JPG, JPEG, BMP, TIFF (placeholder for future OCR)
- **Office Files**: PPTX (placeholder for future processing)

### Quality Features

- **Binary Filtering**: Automatic detection and exclusion of non-text files
- **Content Validation**: Minimum content thresholds prevent empty document storage
- **Metadata Enrichment**: File size, modification time, and language detection
- **Error Handling**: Graceful degradation for unsupported or corrupted files

### Example Conversations

**Document Analysis**:

```text
User: What are the key features of the Blackcoin POS protocol?
AI: Based on the Blackcoin POS v3.1 whitepaper, the key features include:

- Energy efficiency improvements over PoW
- Transaction scalability through timestamp field removal
- Bitcoin compatibility with modified transaction layout
- Security enhancements addressing coin-age abuse
- Robust node incentives for network participation
```

**Tool-Based Analysis**:

```text
User: Parse the PDF samples/blackcoin-pos-protocol-v3.1-whitepaper.pdf and extract the main sections
AI: [Uses parse_document tool]
✅ Successfully extracted content from blackcoin-pos-protocol-v3.1-whitepaper.pdf
Main sections include: Abstract, Introduction, Background, Proposed Solution, Implementation, Conclusion
```

**Codebase Questions**:

```text
User: How does the populate command work?
AI: The /populate command processes documents by:

1. Scanning the specified directory for supported file types
2. Extracting text content using specialized libraries
3. Chunking text into 1500-character segments
4. Generating vector embeddings via Ollama
5. Storing in ChromaDB for semantic search
```

### Real-World Usage Scenarios

**Research Assistant**:

- Upload research papers (PDF) and ask questions about methodologies, findings, or related work
- Compare different approaches across multiple documents
- Extract key insights and summarize complex topics

**Code Documentation**:

- Ingest entire codebases with `/populate src/`
- Ask "How does the authentication system work?" or "What functions handle user input?"
- Get context-aware answers based on actual code content

**Legal Document Analysis**:

- Process contracts, agreements, or legal documents
- Ask questions about terms, conditions, or obligations
- Extract specific clauses or requirements

**Technical Documentation**:

- Import API documentation, manuals, or specifications
- Query about specific features, configurations, or troubleshooting steps
- Get accurate answers from official documentation

**Learning and Education**:

- Teach the AI new concepts with `/learn` commands
- Build custom knowledge bases for specific domains
- Ask questions that combine learned information with document content

### Core Components v0.2.0

1. **🖥️ GUI Interface**: Modern PyQt6 graphical interface with complete CLI command parity
2. **💻 CLI Interface**: Traditional terminal interface with full functionality
3. **🧠 Learning System**: AI can learn and retain information via vector database
4. **💾 ChromaDB v2 Server**: Distributed vector database for persistent knowledge storage
5. **🔍 Semantic Search**: Context-aware information retrieval using embeddings
6. **📄 Document Processing**: qwen3-vl-30b multimodal analysis for OCR, table extraction, form analysis, and layoutunderstanding
7. **🛠️ AI Tool Calling**: 8 powerful tools for file operations, document processing, knowledge management, and websearch
8. **📝 Code Ingestion**: Bulk import and indexing of codebases with 80+ file type support
9. **💬 Memory Management**: SQLite-based conversation persistence across sessions
10. **🎛️ Model Management**: Dynamic model switching and configuration
11. **⚙️ Command System**: Unified slash commands in both GUI and CLI interfaces
12. **🔗 LangChain Integration**: Orchestrates LLM, embeddings, and vector database interactions
13. **✅ Type Safety**: Full MyPy type checking with comprehensive error handling
14. **🧠 Mem0 Personalized Memory**: Advanced AI memory system for user preference tracking and contextual awareness
15. **🌍 Web Ingestion**: URL-based learning with Docling for web content extraction and processing

## 🗄️ Database Planning

### Storage System

#### SQLite Database (Required)

- **Storage**: SQLite database (`db/history.db`)
- **Features**: ACID transactions, concurrent access, SQL querying, indexing
- **Advantages**: Data integrity, thread-safe, persistent across sessions
- **Configuration**: `DB_TYPE=sqlite` in `.env` (required, no alternatives)

### Future Enhancements

- **Encryption**: Database-level encryption for sensitive conversations
- **Search Features**: Full-text search and conversation analytics
- **Multi-user Support**: User isolation and authentication
- **Advanced Analytics**: Conversation insights and reporting

## 🧠 Mem0 Personalized Memory System

The AI now "knows" you through the Mem0 personalized memory system:

- **Automatic Learning**: Mem0 silently observes your messages and learns your preferences without explicit commands
- **Adaptive Responses**: The AI remembers your coding style, preferences, and context to provide better tailored responses
- **Contextual Awareness**: For every message, Mem0 provides relevant context to help the AI understand your needs
- **Persistent Memory**: User preferences are stored and remembered across sessions

**Example Usage:**

```bash

You: "I prefer Python 3.10 type hints"
Mem0: *Silently remembers your preference*
You: "Write a function to sum a list"
AI: *Generates code with Python 3.10 type hints because it remembers your preference*
```

## 🌍 Web Ingestion Features

The `/web` command allows you to learn content directly from webpages:

- **URL Learning**: Ingest any webpage content into your knowledge base
- **Docling Processing**: Uses Docling for high-quality content extraction and cleaning
- **Markdown Conversion**: Converts web content to clean Markdown format
- **Vector Storage**: Stores web content in ChromaDB for semantic search

**Example Usage:**

```bash
You: /web https://example.com/documentation
AI: ✅ Learned from web: Example Documentation
You: What did you learn about Example?
AI: *Provides summary based on web content*
```

## 📋 Prerequisites

- **Python 3.13.x** (latest available, e.g., 3.13.11 or newer) ⚠️ **Python 3.14 is NOT compatible yet**
- **uv** package manager (recommended for dependency management)
- **LM Studio** running locally with a model loaded (qwen3-vl-30b recommended)
- **ChromaDB v2 Server** running locally (port 8000) - **REQUIRED** for learning features
- **Ollama** running locally for embeddings (qwen3-embedding:latest) - **REQUIRED** for learning features
- **Git** for cloning the repository

## 📦 Dependencies

All Python dependencies are listed in `requirements.txt`. Key libraries include:

### Core Dependencies

- **LangChain**: `langchain`, `langchain-openai`, `langchain-core`, `langchain-community`, `langchain-ollama`, `langchain-text-splitters`, `langchain-chroma`
- **Vector Database**: `chromadb`
- **HTTP/Async**: `aiohttp` (MCP HTTP/SSE transport), `requests`
- **Configuration**: `python-dotenv`, `pydantic`
- **GUI**: `PyQt6`, `Markdown`
- **Document Processing**: `docling` (unified processing for PDF, DOCX, RTF, EPUB, XLSX)
- **CLI Enhancement**: `rich`
- **MCP Support**: `mcp[cli,rich]`

### Development Dependencies (Optional)

- **Linting**: `flake8`, `mypy`, `vulture`, `codespell`, `autopep8`, `pylint`, `pyright`, `bandit`, `black`
- **Type Stubs**: `types-Markdown`, `types-requests`, `types-psutil`
- **Testing**: `pytest`, `pytest-cov`, `pytest-mock`, `pytest-asyncio`, `responses`
- **Shell Linting**: `shellcheck` (install with `brew install shellcheck`)

## 🧹 Code Quality & Linting

### Automated Quality Checks

```bash

# Run all linting checks (Python, shell, structure)

python tests/lint/lint.py
```

### Quality Assurance Tools

- **🐍 Python Linting**: Syntax, style, types, dead code, spelling
- **🐚 Shell Scripts**: ShellCheck for bash script validation
- **📁 Project Structure**: Configuration and dependency validation
- **✅ Type Safety**: Full MyPy coverage with modern type hints
- **📏 Code Style**: PEP8 compliant with 100-char line limits

### Development Workflow

1. **Write Code** → Features implemented with comprehensive error handling
2. **Run Lints** → `python tests/lint/lint.py` for quality assurance
3. **Fix Issues** → Address any style, type, or logic problems
4. **Test Integration** → Verify with CLI and GUI interfaces
5. **Deploy** → Production-ready code with clean quality metrics

### Quality Metrics

- **✅ MyPy**: Clean type checking (no errors)
- **✅ Syntax**: All Python files compile successfully
- **✅ Style**: All linting checks pass (no warnings)
- **✅ Dependencies**: All imports resolved and tested
- **✅ Documentation**: Required files validated (README.md, AGENTS.md, MIGRATION.md)
- **✅ Core Files**: All application files validated (src/main.py, src/gui.py, launcher.py)
- **✅ Feature Parity**: GUI and CLI have identical functionality
- **✅ Logging**: Comprehensive logging across both interfaces

## 🔧 Required Services v0.2.0

1. **LM Studio** (Port 1234) - **REQUIRED**:

    ```bash
    # Install LM Studio and load qwen3-vl-30b model
    # Start local server at http://192.168.0.203:1234
    ```

2. **ChromaDB v2 Server** (Port 8000) - **REQUIRED** for learning features:

    ```bash
    # Install ChromaDB
    pip install chromadb

    # Start ChromaDB v2 server (MANDATORY for /learn and /populate commands)
    chroma run --host 192.168.0.204 --port 8000 --path ./chroma_data
    ```

3. **Ollama** (Port 11434) - **REQUIRED** for learning features:

    ```bash
    # Install Ollama for embeddings
    ollama pull qwen3-embedding:latest

   # Start Ollama service (MANDATORY for vector database operations)
     ollama serve
    ```

### Current Implementation

- **SQLite**: Built-in Python support (currently implemented for conversation memory)
- **ChromaDB v2**: Vector database for knowledge storage (currently implemented)
- **Ollama**: Embeddings service (currently implemented)

## 🚀 Installation

**⚠️ IMPORTANT**: This application requires a `.env` configuration file. Copy `.env.example` to `.env` and configure
all variables before running.

1. **Clone the repository:**

   ```bash
   git clone https://github.com/BlackcoinDev/devassist.git
   cd devassist
   ```

2. **Create Python 3.13.x virtual environment**:

   **Using uv (recommended)**:

   ```bash
   uv venv venv --python 3.13  # Uses latest 3.13.x available on your system
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```

   **Using pip3:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   **Using uv (recommended):**

   ```bash
   uv pip install -r requirements.txt
   ```

   **Using pip3:**

   ```bash
   pip3 install -r requirements.txt
   ```

   Optional: Install shellcheck for shell script linting (available on macOS via Homebrew, Linux via package managers,
Windows via Chocolatey/Scoop). This enables comprehensive linting of shell scripts in the project, helping detect errors
and improve code quality. Install with: `brew install shellcheck` (macOS), `sudo apt install shellcheck`
(Ubuntu/Debian), or equivalent for your platform.

4. **Configure environment (REQUIRED)**:

   ```bash
   cp .env.example .env
   # Edit .env with your settings (see Configuration section below)
   # The application WILL NOT start without a properly configured .env file
5. **Start required services** (see Prerequisites section above)

6. **Run the application**:

   **GUI Version (Recommended):**

   ```bash
   uv run python launcher.py        # Modern graphical interface
   ```

   **CLI Version (Terminal):**

   ```bash
   uv run python launcher.py --cli  # Traditional terminal interface
   ```

## ⚙️ Configuration

**IMPORTANT**: This application requires a `.env` file and does not use any hardcoded defaults. All configuration must
be provided through environment variables.

### Setup Requirements

1. **Copy the configuration template**:

   ```bash
   cp .env.example .env

2. **Edit `.env` with your specific settings**:

   ```bash
   nano .env  # or your preferred editor

3. **The application will fail to start** without a properly configured `.env` file.

### Required Settings v0.2.0

All variables in `.env.example` are **required** - there are no defaults:

```bash

# LM Studio Configuration (REQUIRED)

LM_STUDIO_URL=http://192.168.0.203:1234/v1    # Your LM Studio endpoint
LM_STUDIO_KEY=lm-studio                        # API key for LM Studio
MODEL_NAME=qwen3-vl-30b                        # LLM model name

# Vector Database Configuration (REQUIRED - ChromaDB is mandatory)

CHROMA_HOST=192.168.0.204                      # ChromaDB server host
CHROMA_PORT=8000                               # ChromaDB server port

# Ollama Configuration (REQUIRED)

OLLAMA_BASE_URL=http://192.168.0.204:11434    # Ollama embeddings endpoint
EMBEDDING_MODEL=qwen3-embedding:latest        # Embedding model name

# Application Settings (REQUIRED)

MAX_HISTORY_PAIRS=5                            # Conversation memory limit
TEMPERATURE=0.7                               # LLM creativity (0.0-1.0)
MAX_INPUT_LENGTH=10000                        # Maximum input length

# Verbose Logging (Optional - shows detailed AI processing)

VERBOSE_LOGGING=false                         # Enable detailed step-by-step logging
SHOW_LLM_REASONING=true                        # Display LLM reasoning content
SHOW_TOKEN_USAGE=true                          # Show token usage statistics
SHOW_TOOL_DETAILS=true                         # Detailed tool execution logging

# Database Configuration (REQUIRED)

DB_TYPE=sqlite                                # Database type
DB_PATH=db/history.db                         # SQLite database path

# System Configuration (REQUIRED)

KMP_DUPLICATE_LIB_OK=TRUE                     # OpenMP workaround

# Auto-learn Configuration (Optional)

AUTO_LEARN_ON_STARTUP=true                         # Enable/disable auto-learning (default: true)
AUTO_LEARN_MAX_FILE_SIZE_MB=5                     # Skip files larger than this size (default: 5)
AUTO_LEARN_TIMEOUT_SECONDS=30                   # Maximum processing time per file (default: 30)
AUTO_LEARN_COLLECTION_NAME=agents_knowledge     # ChromaDB collection name (default: agents_knowledge)
```

### Configuration Validation

The application validates all required environment variables at startup:

- **Missing `.env` file**: Application exits with clear instructions
- **Missing variables**: Application exits with specific error messages
- **Invalid values**: Application may fail during initialization

### Configuration Hierarchy

1. **`.env` File** (required - no fallbacks)
2. **System Environment** (can override `.env` values)

**Note**: Unlike traditional applications, this version has **zero hardcoded defaults** to ensure consistent deployment
across different environments.

## 🎯 Usage

### Starting the Application

```bash

# Activate virtual environment

source venv/bin/activate

# Ensure .env file is configured (REQUIRED)

cp .env.example .env  # If not already done

# Edit .env with your configuration

# Start the chat assistant

uv run python launcher.py   # Recommended: unified launcher

# OR

uv run python launcher.py --cli  # CLI only

# OR

uv run python launcher.py --gui  # GUI only
```

**Note**: The application will fail to start without a properly configured `.env` file containing all required
environment variables.

### Basic Chat

Start chatting with the AI assistant:

```text
You: Hello! How are you?
AI Assistant: Hello! I'm doing well, thank you for asking. How can I help you today?

You: /help
--- Available Commands ---
/memory       - Show conversation history
/vectordb     - Show vector database contents
/mem0         - Show personalized memory contents
/model        - Show current model information
/context <mode> - Control context integration (auto/on/off)
/learning <mode> - Control learning behavior (normal/strict/off)
/populate <path> - Add code files from directory to vector DB
/clear        - Clear conversation history
/learn <text> - Add information to knowledge base
/export <fmt> - Export conversation (json/markdown)
/read <file>  - Read file contents
/write <file> - Write content to file
/list [dir]   - List directory contents
/pwd          - Show current directory
/help         - Show this help message

Regular commands (no slash needed):
quit    - Exit the application
exit    - Exit the application
q       - Exit the application
```

## 🖥️ GUI Interface

The application includes a modern PyQt6-based graphical interface with:

### GUI Features

- **📱 Chat Display**: Scrollable conversation history with rich markdown formatting
- **⌨️ Input System**: Text field with Enter key support + Send button
- **🎛️ Quick Commands**: One-click buttons for common operations (/help, /clear, /memory, etc.)
- **⚙️ Settings Panel**: Dropdown menus to control context and learning modes
- **🎨 Theme Toggle**: Switch between dark and light themes (dark theme default)
- **📊 Status Display**: Real-time status updates and model information
- **🔄 Streaming Responses**: Real-time display of AI responses as they generate
- **📝 Markdown Support**: Rich text rendering with bold, italic, code blocks, and lists
- **⚡ Complete CLI Parity**: All slash commands work directly in GUI (no AI calls needed)

### GUI Layout

```text
┌─────────────────────────────────────────────────┐
│ AI Assistant v0.2.0 - Learning Edition            │
├─────────────────────────────┬───────────────────┤
│ Chat Display Area           │ Status: Ready     │
│ ┌─────────────────────────┐ │ Model: qwen3-vl-30b │
│ │ You: Hello!            │ │                   │
│ │ AI: Hi there!          │ │ Quick Commands     │
│ │ ...                     │ │ ┌─────────────┐   │
│ └─────────────────────────┘ │ │ Help        │   │
├─────────────────────────────┤ │ Clear Chat  │   │
│ [Input Field] [Send]        │ │ Show Memory │   │
└─────────────────────────────┴─┼─────────────┼───┘
                                │ Settings        │
                                │ Theme: [🌙 Dark] │
                                │ Context: [auto ▼]│
                                │ Learning:[normal▼│
                                └─────────────────┘
```

**Note**: The GUI provides complete feature parity with the CLI, including all slash commands (/help, /clear, /learn,
/vectordb, /mem0, /populate, /context, /learning, /space, etc.) processed locally without calling the AI. The interface
defaults to a dark theme for better readability, with rich markdown formatting and comprehensive logging.

### Markdown Formatting

The GUI supports markdown formatting in messages:

- **Bold**: `**text**` or `__text__`
- *Italic*: `*text*` or `_text_`
- `Code`: `` `code` ``
- Lists, headers, and other markdown elements

### Launching GUI

```bash

uv run python launcher.py        # Default - launches GUI
uv run python launcher.py --gui  # Explicit GUI launch

```

### GUI vs CLI

- **GUI**: User-friendly, modern interface, quick commands, settings panel
- **CLI**: Full control, all features, terminal-based, faster for power users

```text

============================================================
      AI Assistant Chat Interface v0.2.0
============================================================
📍 Python: 3.13.11 | Model: qwen3-vl-30b
🔗 LM Studio: http://192.168.0.203:1234/v1
🗄️  ChromaDB: 192.168.0.204:8000
🧠 Embeddings: qwen3-embedding:latest
💾 Memory: SQLite (11 messages loaded)
🌐 Space: default (collection: knowledge_base)

Hello! I'm ready to help you.
Commands: 'quit', 'exit', or 'q' to exit
Type /help for all available commands

✅ Connected to LLM: qwen3-vl-30b (with tool calling)
✅ Connected to vector database (existing collection)
✅ Connected to SQLite database for conversation memory

You: Hello! How are you?
AI Assistant: Hello! I'm doing well, thank you for asking. How can I help you today?

You: quit

👋 Goodbye! Your conversation has been saved.

```

### Slash Commands v0.3.0

| Command            | Description                                                    | Example                                    |
| ------------------ | -------------------------------------------------------------- | ------------------------------------------ |
| `/learn <text>`    | **Teach AI new information** (stores in ChromaDB)              | `/learn Docker containers are lightweight` |
| `/web <url>`       | **Learn content from webpage** (web ingestion via Docling)     | `/web https://example.com`                 |
| `/vectordb`        | **Inspect knowledge base** (shows chunks, sources, statistics) | `/vectordb`                                |
| `/mem0`            | **Inspect personalized memory** (user preferences and context) | `/mem0`                                    |
| `/populate <path>` | **Bulk import codebases** (uses document processing tools)     | `/populate /path/to/project`               |
| `/model`           | **Check/switch AI models**                                     | `/model`                                   |
| `/memory`          | **View conversation history** (SQLite database)                | `/memory`                                  |
| `/clear`           | **Reset conversation memory**                                  | `/clear`                                   |
| `/space <cmd>`     | **Workspace management** (isolated knowledge bases)            | `/space create myproject`                  |
| `/context <mode>`  | **Control context integration** (`auto`/`on`/`off`)            | `/context auto`                            |
| `/learning <mode>` | **Control learning behavior** (`normal`/`strict`/`off`)        | `/learning normal`                         |
| `/export <fmt>`    | **Export conversation** (`json`/`markdown`)                    | `/export json`                             |
| `/read <file>`     | **Read file contents** (direct file access)                    | `/read README.md`                          |
| `/write <file>`    | **Write content to file** (direct file editing)                | `/write notes.txt Hello world`             |
| `/list [dir]`      | **List directory contents** (filesystem browsing)              | `/list src/`                               |
| `/pwd`             | **Show current directory** (navigation)                        | `/pwd`                                     |
| `/git-status`      | **Show git repository status** (aliases: `/gs`, `/status`)     | `/git-status`                              |
| `/git-log [n]`     | **Show commit history** (aliases: `/gl`, `/log`)               | `/git-log 20`                              |
| `/git-diff`        | **Show git changes** (aliases: `/gd`, `/diff`)                 | `/git-diff --staged`                       |
| `/search <pat>`    | **Code search with ripgrep** (aliases: `/grep`, `/rg`)         | `/search "def main" --type py`             |
| `/shell <cmd>`     | **Execute shell command** (CLI only, aliases: `/sh`, `/run`)   | `/shell npm test`                          |
| `/help`            | **Show all commands**                                          | `/help`                                    |
| `quit`             | **Exit application**                                           | `quit`                                     |

### AI Tool Integration

**13 AI Tools Available** (qwen3-vl-30b can call these autonomously):

| Tool                      | Function                         | Use Case                   |
| ------------------------- | -------------------------------- | -------------------------- |
| `read_file()`             | Read file contents               | "show me the README"       |
| `write_file()`            | Create/modify files              | "create a config file"     |
| `list_directory()`        | Browse directories               | "what files are here"      |
| `get_current_directory()` | Show current path                | "where am I"               |
| `parse_document()`        | Extract text/tables/forms/layout | "analyze this PDF"         |
| `learn_information()`     | Store in knowledge base          | "remember this fact"       |
| `search_knowledge()`      | Query learned information        | "what do you know about X" |
| `search_web()`            | Search internet with DuckDuckGo  | "what's the latest on AI"  |
| `shell_execute()`         | Run shell commands (CLI only)    | "run npm install"          |
| `git_status()`            | Git repository status            | "what changed"             |
| `git_diff()`              | Show git changes                 | "show the diff"            |
| `git_log()`               | Commit history                   | "recent commits"           |
| `code_search()`           | Regex code search (ripgrep)      | "find TODO comments"       |

**Tool Testing Status:**

- ✅ All 13 tools are fully tested and working (unit + integration tests)
- ✅ `read_file()` and `get_current_directory()` are confirmed functional
- ✅ Shell execution, Git integration, and Code search are verified
- ✅ Document processing and Knowledge management are covered by tests

#### Tool Result Flow & AI Usage

**When AI uses tools, results follow this lifecycle:**

1. **Tool Execution**: AI calls tool → Tool executes → Returns structured result
2. **Result Storage**: Results stored in conversation memory (not written to files)
3. **Context Integration**: Results formatted and added to conversation history
4. **AI Processing**: Results become part of LLM's thinking context for response generation
5. **Response Generation**: AI uses tool data to craft informed, accurate responses
6. **Persistence**: Results saved in SQLite conversation history

**Example Flow:**

```bash
User: "analyze this PDF"
AI: Calls parse_document() → Gets {"success": true, "content": "..."} → Analyzes data → "Based on the PDF content..."
```

### Verbose Logging & AI Transparency

**See exactly what the AI is thinking and doing** with detailed step-by-step logging:

```bash

# Enable in .env file

VERBOSE_LOGGING=true
SHOW_LLM_REASONING=true
SHOW_TOKEN_USAGE=true
SHOW_TOOL_DETAILS=true
```

**What you'll see:**

```text
🤖 Sending prompt to LLM...
📥 LLM Response received
🔄 Token Usage: 1245 prompt + 685 completion = 1930 total
🧠 LLM Reasoning: The user is asking about their AI agent project...
🔧 LLM Generated 1 Tool Call(s)

   1. read_file

⚙️ Executing read_file...
   Arguments: {'file_path': 'README.md'}
✅ Tool read_file completed (1247 chars read)
AI Assistant: [comprehensive analysis based on file content]
```

**Configuration Options:**

- `VERBOSE_LOGGING`: Master switch for detailed logging
- `SHOW_LLM_REASONING`: Display AI's internal thought process
- `SHOW_TOKEN_USAGE`: Show prompt/completion token counts
- `SHOW_TOOL_DETAILS`: Detailed tool execution information

**Perfect for:**

- Understanding AI decision-making
- Debugging tool usage
- Educational purposes
- Development and testing

### Learning & Knowledge Features v0.2.0

**Teach the AI anything:**

```bash

You: /learn Docker containers provide lightweight, portable application packaging
✅ Learned: Docker containers provide lightweight, portable...

You: /learn Python was created by Guido van Rossum in 1991
✅ Learned: Python was created by Guido van Rossum...

You: /learn My favorite programming language is Python
✅ Learned: My favorite programming language is...

```

**AI uses learned information in conversations:**

```bash

You: What programming languages do you know about?
AI Assistant: From the knowledge base, I know that Python was created by Guido van Rossum in 1991, and you mentioned
that Python is your favorite programming language...

You: Tell me about containers
AI Assistant: Based on what you've taught me, Docker containers provide lightweight, portable application packaging...

```

**Bulk import entire codebases:**

```bash

You: /populate /path/to/your/project
⏳ Processing codebase...
✅ Added 47 files to knowledge base

You: How does the authentication work in this codebase?
AI Assistant: Based on the codebase, the authentication system uses JWT tokens...

```

### Learning Mode Control

Control how the AI uses learned information with three learning modes:

#### `normal` Mode (Default)

- **Behavior**: Balanced, intelligent context integration
- **Usage**: AI automatically decides when learned information is relevant
- **Best for**: Most users who want helpful context without overwhelming responses

#### `strict` Mode

- **Behavior**: Minimal context usage, focused on learning queries only
- **Usage**: Only uses learned information for explicit questions like "what do you know about X?"
- **Best for**: Users who want the AI to focus on immediate conversation topics

#### `off` Mode

- **Behavior**: Complete learning feature disable
- **Usage**: Ignores all learned information entirely
- **Best for**: Testing AI capabilities, privacy concerns, or wanting "fresh" responses

**Usage:**

```bash
/learning normal  # Balanced learning and context (default)
/learning strict  # Minimal context, learning queries only
/learning off     # Disable all learning features

```

## 🛠️ Advanced Usage

### Populating Knowledge Base

Use the `/populate` command to bulk-load codebases:

```bash

/populate /path/to/your/codebase
/populate samples/ --clear    # Clear existing data first
/populate . --dry-run         # Validate without saving

This recursively scans directories and adds all code files to the ChromaDB vector database using the direct API for
optimal reliability and performance.
```

**Options:**

- `--clear`: Delete existing collection before repopulating (prevents duplicates)
- `--dry-run`: Validate files without writing to database

### Custom Knowledge Addition

```bash

# Add specific information

/learn Git is a distributed version control system
/learn REST APIs use HTTP methods like GET, POST, PUT, DELETE
/learn Neural networks consist of interconnected nodes called neurons

# Add entire codebases

/populate /path/to/project/src
/populate .  # Current directory
```

### Memory Management

## View current conversation

/memory

## Clear all memory

/clear

## Memory persists automatically between sessions

## 🔧 Development

### Project Structure

```text
devassist/
├── launcher.py                # Unified launcher for GUI/CLI versions
├── src/
│   ├── __init__.py
│   ├── main.py                # CLI interface + LLM initialization (547 lines)
│   ├── gui.py                 # PyQt6 graphical user interface (1,212 lines)
│   ├── core/                  # Application foundation
│   │   ├── config.py          # Configuration management from .env
│   │   ├── context.py         # ApplicationContext (dependency injection)
│   │   └── context_utils.py   # Shared utility functions
│   ├── storage/               # Persistence layer
│   │   ├── database.py        # SQLite connection management
│   │   ├── memory.py          # Conversation history persistence
│   │   └── cache.py           # Embedding and query caching
│   ├── security/              # Security enforcement
│   │   ├── input_sanitizer.py # Input validation and sanitization
│   │   ├── path_security.py   # Path traversal prevention
│   │   ├── rate_limiter.py    # Request rate limiting
│   │   └── exceptions.py      # Security exception classes
│   ├── vectordb/              # Knowledge storage
│   │   ├── client.py          # ChromaDB unified HTTP API client
│   │   └── spaces.py          # Workspace/collection management
│   ├── commands/              # Command system (plugin architecture)
│   │   ├── registry.py        # CommandRegistry dispatcher
│   │   └── handlers/          # Command handler modules
│   │       ├── help_commands.py
│   │       ├── config_commands.py
│   │       ├── database_commands.py
│   │       ├── memory_commands.py
│   │       ├── learning_commands.py
│   │       ├── space_commands.py
│   │       ├── file_commands.py
│   │       └── export_commands.py
│   └── tools/                 # AI tool system (plugin architecture)
│       ├── registry.py        # ToolRegistry dispatcher
│       └── executors/         # AI tool executor modules
│           ├── file_tools.py
│           ├── knowledge_tools.py
│           ├── document_tools.py
│           └── web_tools.py
├── tests/
│   ├── __init__.py            # Test package initialization
│   ├── conftest.py            # Pytest fixtures and configuration
│   ├── fixtures/              # Test fixtures directory
│   ├── integration/           # Integration tests
│   ├── unit/                  # Unit tests
│   └── lint/                  # Linting scripts
│       └── lint.py            # Consolidated project linting
├── tools/
│   ├── README.md              # Guide for AI tool calling
│   ├── populate_codebase.py  # Codebase population script for bulk import
│   ├── docling_example.py    # Document processing with Docling
│   └── ...                    # Other tool examples
├── docs/
│   ├── ARCHITECTURE.md        # System architecture documentation
│   ├── MANUAL.md              # User guide
│   ├── MIGRATION.md           # Migration guide and documentation
│   ├── ROADMAP.md             # Future development roadmap
│   └── SEARCH.md              # Search and RAG documentation
├── samples/
│   ├── Blackcoin-POS-3.pdf                        # Sample PDF document
│   └── ...                                        # Other sample files
├── db/                        # Database files directory
│   └── history.db             # SQLite database for persistent chat history
├── venv/                      # Python 3.13 virtual environment
├── .env                       # Configuration (copy from .env.example)
├── .env.example               # Configuration template
├── CLAUDE.md                  # Developer guide for Claude Code
├── AGENTS.md                  # Agent guidelines and architecture docs
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Pytest configuration
├── mypy.ini                   # MyPy type checking configuration
├── LICENSE                    # MIT License
└── README.md                  # This file
```

### Key Files Explanation

**Core Application:**

- **`src/main.py`** (547 lines): CLI interface and LLM initialization with chat loop
- **`src/gui.py`** (1,212 lines): PyQt6-based graphical user interface with full CLI parity
- **`launcher.py`** (221 lines): Unified entry point for starting GUI or CLI modes

**Modular Architecture (v0.2.0):**

- **`src/core/context.py`**: ApplicationContext dependency injection container—centralizes all application state
- **`src/commands/registry.py`**: CommandRegistry dispatcher with self-registering plugin system
- **`src/tools/registry.py`**: ToolRegistry dispatcher for AI tool auto-registration
- **`src/vectordb/client.py`**: Unified ChromaDB HTTP API wrapper (eliminates 10+ duplicate API patterns)
- **`src/storage/database.py`**: Thread-safe SQLite connection management
- **`src/storage/memory.py`**: Conversation history persistence and trimming
- **`src/storage/cache.py`**: Embedding and query result caching
- **`src/security/input_sanitizer.py`**: SQL injection, XSS, command injection prevention

**Tools & Documentation:**

- **`tools/populate_codebase.py`**: Script to bulk-load codebases into ChromaDB vector database
- **`docs/ROADMAP.md`**: Detailed future development plans and integrations
- **`docs/MIGRATION.md`**: Guide for migrating between versions
- **`docs/ARCHITECTURE.md`**: System architecture and plugin documentation
- **`tests/`**: Test suite (137 tests defined, 101 passing, see tests/README.md for status)
- **`db/history.db`**: SQLite database for persistent chat history

### Adding New Features

1. **New Commands**: Create handler in `src/commands/handlers/` with `@CommandRegistry.register()` decorator
2. **New Tools**: Create executor in `src/tools/executors/` with `@ToolRegistry.register()` decorator
3. **Configuration**: Add environment variables to `.env` and `src/core/config.py`
4. **Knowledge**: Use `/learn` command or `/populate` command to teach the AI

## 🐛 Troubleshooting

### Common Issues

**ERROR: No .env file found!**

- The application requires a `.env` file - copy from template: `cp .env.example .env`
- Edit `.env` with your specific configuration values
- All variables in `.env.example` are required - no defaults exist

#### ERROR: [VARIABLE_NAME] environment variable is required

- Check that all required variables are set in your `.env` file
- Compare with `.env.example` to ensure nothing is missing
- Restart the application after fixing the configuration

#### Cannot connect to LM Studio

- Ensure LM Studio is running and a model is loaded.
- Verify the LM Studio server is listening on the correct host and port (default: `http://localhost:1234/v1`).
- Check that `LM_STUDIO_URL` in `.env` matches the LM Studio endpoint exactly (including `/v1`).
- Confirm that the model specified in `MODEL_NAME` is loaded and available in LM Studio.
- If LM Studio is behind a firewall or running on a remote host, ensure the host and port are reachable from your machine.
- Restart LM Studio if you recently changed the model or configuration.
- Verify that the `LM_STUDIO_KEY` is set correctly if authentication is enabled.

#### ERROR: ChromaDB connection failed

- ChromaDB v2 server is **required** for learning features (/learn and /populate)
- Ensure ChromaDB server is running: `chroma run --host 192.168.0.204 --port 8000 --path ./chroma_data`
- Check `CHROMA_HOST` and `CHROMA_PORT` in `.env` match your server
- Ensure Ollama is running: `ollama serve`
- Check `OLLAMA_BASE_URL` points to correct Ollama instance

#### Import errors

- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `uv pip install -r requirements.txt`
- Check Python version compatibility (requires Python 3.13.x)

#### Memory not loading

- Check `db/history.db` exists and is readable
- Verify file permissions and SQLite database integrity
- The app will create a new database if corrupted

#### Database connection failed

- For SQLite: Ensure write permissions to database file location
- For ChromaDB: Check server is running and network connectivity
- For Ollama: Verify service is running and accessible

#### Data corruption detected

- Run integrity checks on database
- Restore from backup if available
- Checksum verification failed - data may be compromised

### Debug Mode

Enable detailed logging by modifying the logging level in `src/main.py`:

```python

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

```text

### Reset Application

To completely reset the application:

```bash

# Remove memory and vector databases

rm -f db/history.db
rm -rf chroma_data/

# ChromaDB data is stored in server directory and will be reset

# Restart with clean state

uv run python src/main.py

## 📊 Performance Notes

- **Memory Usage**: Limited by `MAX_HISTORY_PAIRS` (default: 5 pairs)
- **Response Time**: Depends on LM Studio model size and hardware
- **Storage**: Vector database grows with learned knowledge
- **Token Limits**: Large conversations may hit LLM token limits
- **Test Execution**: 101 passing tests execute in ~20-25 seconds (see tests/README.md)
- **Code Quality**: Good overall with some linting issues to address

## 🚀 Deployment Options

### Installation

For traditional Python installation:

```bash

# Install as a package

uv pip install -e .

# Run as installed package

ai-assistant-cli    # CLI version
ai-assistant-gui    # GUI version

## 🧪 User Testing & Feedback

The application is now ready for user testing! Key areas for feedback:

### Usability Testing

- **Interface Experience**: How intuitive are the GUI and CLI interfaces?
- **Command Discovery**: Are slash commands easy to find and use?
- **Learning Features**: How effective is the AI's learning capability?
- **Performance**: Response times and overall application speed

### Feature Testing

- **Document Processing**: Test with various file types (PDF, DOCX, code files)
- **Conversation Export**: Try exporting conversations in both JSON and Markdown formats
- **Space Management**: Test creating and switching between workspaces
- **Model Switching**: Verify different AI models work correctly
- **Web Ingestion**: Test the `/web` command with various URLs
- **Mem0 Personalization**: Verify personalized memory features work correctly

### Edge Cases to Test

- Large codebases with thousands of files
- Very long conversations (100+ messages)
- Special characters and Unicode content
- Network interruptions during AI responses
- Memory limits and performance with large vector databases
- Web ingestion with complex HTML pages
- Mem0 with extensive user preferences

### Providing Feedback

Please report issues and suggestions at: [GitHub Issues](https://github.com/BlackcoinDev/devassist/issues)

When reporting bugs, please include:

- Operating system and Python version
- Steps to reproduce the issue
- Expected vs actual behavior
- Any error messages or logs

## 🔧 GPU Memory Troubleshooting

### Current Working Configuration

**✅ RECOMMENDED SETUP**: qwen3-vl-30b provides optimal performance for most systems.

**Performance Expectations**:

- **Response Times**: 2-5 seconds for typical queries
- **Tool Operations**: 5-15 seconds for file/document operations
- **Memory Usage**: Stable under 8GB GPU memory
- **Stability**: No GPU crashes with proper configuration

### GPU Memory Issues (For Other Models)

**If using larger models like qwen3-vl-30b**:

**Symptom**: LM Studio crashes with "Metal GPU Error" or GPU memory exhaustion

**Root Cause**: Large models require 60GB+ VRAM + context overhead

**Solutions**:

1. **Use qwen3-vl-30b** (recommended - already working perfectly)
2. **Reduce memory usage**:

   ```bash
   /clear                    # Reset conversation history
   /learning strict         # Reduce context overhead

Update `.env`: `MAX_HISTORY_PAIRS=2`

1. **Force CPU mode** (if GPU issues persist):
   - LM Studio → Model Settings → Override Parameters
   - Add: `--gpu-layers 0`
   - Slower (~10-20s) but stable

**Performance Expectations**:

- **qwen3-4b models**: 3-8 seconds per response
- **CPU mode**: 10-20 seconds per response
- **qwen3-vl-30b**: 15-30 seconds (with optimizations)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style

- Follow PEP 8 Python style guidelines
- Add docstrings to new functions
- Include type hints where appropriate
- Test changes with existing functionality

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License

```text

MIT License

Copyright (c) 2025 BlackcoinDev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 🙋 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure all prerequisites are met
4. Create an issue with detailed information

---

**Happy chatting with your AI assistant! 🤖✨**
