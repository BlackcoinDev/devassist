# AI Assistant Chat Application v0.1 - Learning Edition

An advanced interactive AI chat assistant powered by LangChain, LM Studio, and ChromaDB vector database. Features comprehensive learning capabilities, multi-format document processing, robust error handling, and complete feature parity between GUI and CLI interfaces.

## 🌟 Features v0.1

- **🖥️ Modern GUI**: Beautiful PyQt6 interface with dark/light themes
- **🧠 Learning AI**: Teach the AI new information via /learn command that persists across sessions
- **🏢 Spaces System**: Isolated workspaces with separate knowledge bases
- **💾 Vector Database**: ChromaDB v2 server (required) for knowledge storage and retrieval
- **📚 Document Processing**: Extract content from PDFs, Word docs, Excel files, RTF, EPUB, and 80+ file types
- **📄 Advanced Document Analysis**: devstral-small-2507's multimodal capabilities for OCR, table extraction, form analysis, and layout understanding
- **🔧 Codebase Ingestion**: Bulk import entire projects with intelligent file type detection
- **🔄 Model Switching**: Easy switching between different AI models
- **💬 Persistent Memory**: SQLite database for conversation history (no JSON files)
- **🎯 Context Awareness**: AI uses learned information in relevant conversations
- **🛠️ AI Tool Calling**: devstral-small-2507-mlx supports 7 powerful tools for file operations, document processing, and knowledge management
- **⚡ Streaming Responses**: Real-time response display for better user experience
- **🛠️ Rich Commands**: Comprehensive slash command system in both GUI and CLI
- **🎨 Markdown Support**: Rich text formatting in GUI with HTML rendering
- **🔧 Configuration**: **Requires** `.env` file - no hardcoded defaults
- **🛡️ Error Handling**: Robust error handling with graceful degradation
- **✅ Type Safety**: Full MyPy type checking with comprehensive linting

## 📖 Documentation

- **[ROADMAP.md](docs/ROADMAP.md)**: Future development plans including security enhancements, Docling integration, Pydantic-AI, LangGraph, and more
- **[MIGRATION.md](docs/MIGRATION.md)**: Migration guide and version upgrade notes
- **[AGENTS.md](AGENTS.md)**: Agent guidelines and architecture documentation
- **[TOOL_CALLING_GUIDE.md](tools/TOOL_CALLING_GUIDE.md)**: Guide for AI tool calling capabilities

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   GUI/CLI       │───▶│   LM Studio     │
│  (GUI or CLI)   │    │   Interface     │    │   (devstral-small-2507-mlx)│
│                 │    │   (v0.1)        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          │                       ▼                       │
          │              ┌─────────────────┐              │
          │              │  Command        │              │
          │              │  Processing     │              │
          │              │  (/help, /clear,│              │
          │              │   /learn, etc.) │              │
          │              └─────────────────┘              │
          │                       │                       │
          ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Conversation    │    │  Main Chat      │    │  ChromaDB v2    │
│   Memory        │◄──▶│   Loop          │◄──▶│   Server        │
│  (SQLite)       │    │   (7 AI Tools)  │    │  (Vector DB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          ▲                       ▲                       ▲
          │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Document        │    │   Ollama        │    │   File Type     │
│ Processing      │◄──▶│ Embeddings      │◄──▶│   Detection     │
│ (devstral-small-2507 OCR)  │    │ qwen3-embedding │    │   (80+ types)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          ▲                       ▲                       ▲
          │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Tools      │    │   Knowledge     │    │   File System   │
│   Integration   │◄──▶│   Management    │◄──▶│   Operations    │
│ (7 Tools)       │    │   (Learn/Search)│    │   (Read/Write)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📄 Document Processing Workflow

### PDF Processing Pipeline
1. **File Discovery**: `/populate <directory>` scans for supported document types (PDF, DOCX, XLSX, RTF, EPUB, TXT, MD, etc.)
2. **Content Extraction**: Specialized libraries extract text content:
   - **PDF**: PyPDF2 for page-by-page text extraction
   - **DOCX**: python-docx for paragraph and table content
   - **RTF**: striprtf for rich text format parsing
   - **EPUB**: ebooklib for e-book HTML content extraction
   - **XLSX**: openpyxl for spreadsheet data extraction
   - **Text Files**: Direct UTF-8 reading with encoding detection
3. **Text Chunking**: RecursiveCharacterTextSplitter creates 1500-character chunks with 200-character overlap for optimal retrieval
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
```
User: What are the key features of the Blackcoin POS protocol?
AI: Based on the Blackcoin POS v3.1 whitepaper, the key features include:
- Energy efficiency improvements over PoW
- Transaction scalability through timestamp field removal
- Bitcoin compatibility with modified transaction layout
- Security enhancements addressing coin-age abuse
- Robust node incentives for network participation
```

**Tool-Based Analysis**:
```
User: Parse the PDF samples/blackcoin-pos-protocol-v3.1-whitepaper.pdf and extract the main sections
AI: [Uses parse_document tool]
✅ Successfully extracted content from blackcoin-pos-protocol-v3.1-whitepaper.pdf
Main sections include: Abstract, Introduction, Background, Proposed Solution, Implementation, Conclusion
```

**Codebase Questions**:
```
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

### Core Components v0.1

1. **🖥️ GUI Interface**: Modern PyQt6 graphical interface with complete CLI command parity
2. **💻 CLI Interface**: Traditional terminal interface with full functionality
3. **🧠 Learning System**: AI can learn and retain information via vector database
4. **💾 ChromaDB v2 Server**: Distributed vector database for persistent knowledge storage
5. **🔍 Semantic Search**: Context-aware information retrieval using embeddings
6. **📄 Document Processing**: devstral-small-2507 multimodal analysis for OCR, table extraction, form analysis, and layout understanding
7. **🛠️ AI Tool Calling**: 7 powerful tools for file operations, document processing, and knowledge management
8. **📝 Code Ingestion**: Bulk import and indexing of codebases with 80+ file type support
9. **💬 Memory Management**: SQLite-based conversation persistence across sessions
10. **🎛️ Model Management**: Dynamic model switching and configuration
11. **⚙️ Command System**: Unified slash commands in both GUI and CLI interfaces
12. **🔗 LangChain Integration**: Orchestrates LLM, embeddings, and vector database interactions
13. **✅ Type Safety**: Full MyPy type checking with comprehensive error handling

## 🗄️ Database Planning

### Storage System

#### SQLite Database (Required)
- **Storage**: SQLite database (`conversation_memory.db`)
- **Features**: ACID transactions, concurrent access, SQL querying, indexing
- **Advantages**: Data integrity, thread-safe, persistent across sessions
- **Configuration**: `DB_TYPE=sqlite` in `.env` (required, no alternatives)

### Future Enhancements
- **Encryption**: Database-level encryption for sensitive conversations
- **Search Features**: Full-text search and conversation analytics
- **Multi-user Support**: User isolation and authentication
- **Advanced Analytics**: Conversation insights and reporting

## 📋 Prerequisites

- **Python 3.13.9** (recommended - tested with this version)
- **LM Studio** running locally with a model loaded (devstral-small-2507-mlx recommended)
- **ChromaDB v2 Server** running locally (port 8000) - **REQUIRED** for learning features
- **Ollama** running locally for embeddings (qwen3-embedding:latest) - **REQUIRED** for learning features
- **Git** for cloning the repository

## 📦 Dependencies

All Python dependencies are listed in `requirements.txt`. Key libraries include:

### Core Dependencies
- **LangChain**: `langchain-openai==1.0.3`, `langchain-core==1.0.5`, `langchain-community==0.4.1`
- **Vector Database**: `langchain-chroma==1.0.0`, `chromadb==1.3.4`
- **Embeddings**: `langchain-ollama==1.0.0`
- **Configuration**: `python-dotenv==1.2.1`, `pydantic==2.12.4`
- **Document Processing**: `PyPDF2==3.0.1`, `python-docx==1.2.0`, `striprtf==0.0.29`, `ebooklib==0.20`, `openpyxl==3.1.5`

### Development Dependencies (Optional)
- **Linting**: `flake8==7.3.0`, `mypy==1.18.2`, `vulture==2.14`, `codespell==2.4.1`
- **Type Stubs**: `types-Markdown==3.10.0.20251106`, `types-requests==2.32.4.20250913`
- **Shell Linting**: `shellcheck` (install with `brew install shellcheck`)
- **HTTP**: `requests==2.32.5` (for direct API calls)

## 🧹 Code Quality & Linting

### Automated Quality Checks
```bash
# Run comprehensive project linting
python test/lint/all-lint.py

# Run Python-specific linting only
python test/lint/lint-python.py
```

### Quality Assurance Tools
- **🐍 Python Linting**: Syntax, style, types, dead code, spelling
- **🐚 Shell Scripts**: ShellCheck for bash script validation
- **📁 Project Structure**: Configuration and dependency validation
- **✅ Type Safety**: Full MyPy coverage with modern type hints
- **📏 Code Style**: PEP8 compliant with 100-char line limits

### Development Workflow
1. **Write Code** → Features implemented with comprehensive error handling
2. **Run Lints** → `python test/lint/all-lint.py` for quality assurance
3. **Fix Issues** → Address any style, type, or logic problems
4. **Test Integration** → Verify with CLI and GUI interfaces
5. **Deploy** → Production-ready code with clean quality metrics

### Quality Metrics
- **✅ MyPy**: Clean type checking (no errors)
- **✅ Syntax**: All Python files compile successfully
- **✅ Style**: All linting checks pass (no warnings)
- **✅ Dependencies**: All imports resolved and tested
- **✅ Documentation**: Required files validated (README.md, AGENTS.md, MIGRATION.md)
- **✅ Core Files**: All application files validated (main.py, gui.py, launcher.py)
- **✅ Feature Parity**: GUI and CLI have identical functionality
- **✅ Logging**: Comprehensive logging across both interfaces

## 🔧 Required Services v0.1

1. **LM Studio** (Port 1234) - **REQUIRED**:
     ```bash
     # Install LM Studio and load devstral-small-2507-mlx model
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

> **⚠️ IMPORTANT**: This application requires a `.env` configuration file. Copy `.env.example` to `.env` and configure all variables before running.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/BlackcoinDev/devassist.git
   cd devassist
   ```

2. **Create Python 3.13 virtual environment**:

     **Using pip3:**
     ```bash
     python3.13 -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     ```

     **Using uv:**
     ```bash
     uv venv venv --python 3.13
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     ```

   3. **Install dependencies**:

      **Using pip3:**
      ```bash
      pip3 install -r requirements.txt
      ```

      **Using uv:**
      ```bash
      uv pip install -r requirements.txt
      ```

   Optional: Install shellcheck for shell script linting (available on macOS via Homebrew, Linux via package managers, Windows via Chocolatey/Scoop). This enables comprehensive linting of shell scripts in the project, helping detect errors and improve code quality. Install with: `brew install shellcheck` (macOS), `sudo apt install shellcheck` (Ubuntu/Debian), or equivalent for your platform.

4. **Configure environment (REQUIRED)**:
     ```bash
     cp .env.example .env
     # Edit .env with your settings (see Configuration section below)
     # The application WILL NOT start without a properly configured .env file
     ```

5. **Start required services** (see Prerequisites section above)

6. **Run the application**:

    **GUI Version (Recommended):**
    ```bash
    python3 launcher.py        # Modern graphical interface
    ```

    **CLI Version (Terminal):**
    ```bash
    python3 launcher.py --cli  # Traditional terminal interface
    ```

## ⚙️ Configuration

**IMPORTANT**: This application requires a `.env` file and does not use any hardcoded defaults. All configuration must be provided through environment variables.

### Setup Requirements

1. **Copy the configuration template**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your specific settings**:
   ```bash
   nano .env  # or your preferred editor
   ```

3. **The application will fail to start** without a properly configured `.env` file.

### Required Settings v0.1

All variables in `.env.example` are **required** - there are no defaults:

```bash
# LM Studio Configuration (REQUIRED)
LM_STUDIO_URL=http://192.168.0.203:1234/v1    # Your LM Studio endpoint
LM_STUDIO_KEY=lm-studio                        # API key for LM Studio
MODEL_NAME=devstral-small-2507-mlx                        # LLM model name

# Vector Database Configuration (REQUIRED - ChromaDB is mandatory)
CHROMA_HOST=192.168.0.204                      # ChromaDB server host
CHROMA_PORT=8000                               # ChromaDB server port

# Ollama Configuration (REQUIRED)
OLLAMA_BASE_URL=http://192.168.0.204:11434    # Ollama embeddings endpoint
EMBEDDING_MODEL=qwen3-embedding:latest        # Embedding model name

# Application Settings (REQUIRED)
MAX_HISTORY_PAIRS=10                           # Conversation memory limit
TEMPERATURE=0.7                               # LLM creativity (0.0-1.0)
MAX_INPUT_LENGTH=10000                        # Maximum input length

# Database Configuration (REQUIRED)
DB_TYPE=sqlite                                # Database type
DB_PATH=conversation_memory.db                # SQLite database path

# System Configuration (REQUIRED)
KMP_DUPLICATE_LIB_OK=TRUE                     # OpenMP workaround
```

### Configuration Validation

The application validates all required environment variables at startup:

- **Missing `.env` file**: Application exits with clear instructions
- **Missing variables**: Application exits with specific error messages
- **Invalid values**: Application may fail during initialization

### Configuration Hierarchy

1. **`.env` File** (required - no fallbacks)
2. **System Environment** (can override `.env` values)

**Note**: Unlike traditional applications, this version has **zero hardcoded defaults** to ensure consistent deployment across different environments.

## 🎯 Usage

### Starting the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Ensure .env file is configured (REQUIRED)
cp .env.example .env  # If not already done
# Edit .env with your configuration

# Start the chat assistant
python3 launcher.py   # Recommended: unified launcher
# OR
python3 launcher.py --cli  # CLI only
# OR
python3 launcher.py --gui  # GUI only
```

**Note**: The application will fail to start without a properly configured `.env` file containing all required environment variables.

### Basic Chat

Start chatting with the AI assistant:

```
You: Hello! How are you?
AI Assistant: Hello! I'm doing well, thank you for asking. How can I help you today?

You: /help
--- Available Commands ---
/memory       - Show conversation history
/vectordb     - Show vector database contents
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
```
┌─────────────────────────────────────────────────┐
│ AI Assistant v0.1 - Learning Edition            │
├─────────────────────────────┬───────────────────┤
│ Chat Display Area           │ Status: Ready     │
│ ┌─────────────────────────┐ │ Model: devstral-small-2507-mlx │
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

**Note**: The GUI provides complete feature parity with the CLI, including all slash commands (/help, /clear, /learn, /vectordb, /populate, /context, /learning, /space, etc.) processed locally without calling the AI. The interface defaults to a dark theme for better readability, with rich markdown formatting and comprehensive logging.

### Markdown Formatting
The GUI supports markdown formatting in messages:
- **Bold**: `**text**` or `__text__`
- *Italic*: `*text*` or `_text_`
- `Code`: `` `code` ``
- Lists, headers, and other markdown elements

### Launching GUI
```bash
python3 launcher.py        # Default - launches GUI
python3 launcher.py --gui  # Explicit GUI launch
```

### GUI vs CLI
- **GUI**: User-friendly, modern interface, quick commands, settings panel
- **CLI**: Full control, all features, terminal-based, faster for power users
============================================================
AI Assistant Chat Interface
============================================================
Hello! I'm ready to help you.
Commands: 'quit', 'exit', or 'q' to exit
Slash commands: /memory, /clear, /help
Type /help for all available commands

You: Hello! How are you?
AI Assistant: Hello! I'm doing well, thank you for asking. How can I help you today?

You: What's machine learning?
AI Assistant: Machine learning algorithms can be supervised, unsupervised, or reinforcement learning. Supervised learning uses labeled training data...
```

### Slash Commands v0.1

| Command | Description | Example |
|---------|-------------|---------|
| `/learn <text>` | **Teach AI new information** (stores in ChromaDB) | `/learn Docker containers are lightweight` |
| `/vectordb` | **Inspect learned knowledge** (queries vector database) | `/vectordb` |
| `/populate <path>` | **Bulk import codebases** (uses document processing tools) | `/populate /path/to/project` |
| `/model` | **Check/switch AI models** | `/model` |
| `/memory` | **View conversation history** (SQLite database) | `/memory` |
| `/clear` | **Reset conversation memory** | `/clear` |
| `/space <cmd>` | **Workspace management** (isolated knowledge bases) | `/space create myproject` |
| `/context <mode>` | **Control context integration** (`auto`/`on`/`off`) | `/context auto` |
| `/learning <mode>` | **Control learning behavior** (`normal`/`strict`/`off`) | `/learning normal` |
| `/export <fmt>` | **Export conversation** (`json`/`markdown`) | `/export json` |
| `/read <file>` | **Read file contents** (direct file access) | `/read README.md` |
| `/write <file>` | **Write content to file** (direct file editing) | `/write notes.txt Hello world` |
| `/list [dir]` | **List directory contents** (filesystem browsing) | `/list src/` |
| `/pwd` | **Show current directory** (navigation) | `/pwd` |
| `/help` | **Show all commands** | `/help` |
| `quit` | **Exit application** | `quit` |

### AI Tool Integration

**7 AI Tools Available** (devstral-small-2507-mlx can call these autonomously):

| Tool | Function | Use Case |
|------|----------|----------|
| `read_file()` | Read file contents | "show me the README" |
| `write_file()` | Create/modify files | "create a config file" |
| `list_directory()` | Browse directories | "what files are here" |
| `get_current_directory()` | Show current path | "where am I" |
| `parse_document()` | Extract text/tables/forms/layout | "analyze this PDF" |
| `learn_information()` | Store in knowledge base | "remember this fact" |
| `search_knowledge()` | Query learned information | "what do you know about X" |

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

### Learning & Knowledge Features v0.1

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
AI Assistant: From the knowledge base, I know that Python was created by Guido van Rossum in 1991, and you mentioned that Python is your favorite programming language...

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
```

This recursively scans directories and adds all code files to the ChromaDB vector database using the direct API for optimal reliability and performance.

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

```bash
# View current conversation
/memory

# Clear all memory
/clear

# Memory persists automatically between sessions
```

## 🔧 Development

### Project Structure

```
devassist/
├── launcher.py                # Unified launcher for GUI/CLI versions
├── gui.py                     # PyQt6 graphical user interface
├── main.py                    # CLI application with learning capabilities
├── run_tests.py               # Test runner script
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Pytest configuration
├── mypy.ini                   # MyPy type checking configuration
├── docs/
│   ├── MIGRATION.md           # Migration guide and documentation
│   └── ROADMAP.md             # Future development roadmap
├── tools/
│   ├── TOOL_CALLING_GUIDE.md          # Guide for AI tool calling
│   ├── populate_codebase.py           # Codebase population script for bulk import
│   ├── document_processing_example.py # Document processing examples
│   ├── integrated_document_workflow.py# Integrated document workflow
│   ├── enable_tools_example.py        # Tool enabling examples
│   ├── tool_demo.py                   # Tool demonstration script
│   ├── test_tools.py                  # Tool testing utilities
│   ├── test_direct_tools.py           # Direct tool tests
│   ├── test_fresh_conversation.py     # Fresh conversation tests
│   ├── test_langchain_tools.py        # LangChain tool tests
│   ├── test_main_tools.py             # Main tool tests
│   └── test_parse_document.py         # Document parsing tests
├── tests/
│   ├── __init__.py            # Test package initialization
│   ├── conftest.py            # Pytest fixtures and configuration
│   ├── fixtures/              # Test fixtures directory
│   ├── integration/           # Integration tests
│   └── unit/                  # Unit tests
├── test/
│   └── lint/                  # Linting scripts
│       ├── all-lint.py        # Comprehensive project linting
│       └── lint-python.py     # Python-specific linting
├── samples/
│   ├── Blackcoin-POS-3.pdf                        # Sample PDF document
│   ├── blackcoin-pos-protocol-v2-whitepaper.pdf   # Sample whitepaper
│   └── blackcoin-pos-protocol-v3.1-whitepaper.pdf # Sample whitepaper v3.1
├── venv/                      # Python 3.13 virtual environment
├── conversation_memory.db     # SQLite database for persistent chat history
├── .env                       # Configuration (copy from .env.example)
├── .env.example               # Configuration template
├── AGENTS.md                  # Agent guidelines and architecture docs
├── LICENSE                    # MIT License
└── README.md                  # This file
```

### Key Files Explanation

- **`main.py`**: Core application with chat loop, ChromaDB integration, and rich commands
- **`gui.py`**: PyQt6-based graphical user interface with full CLI parity
- **`launcher.py`**: Unified entry point for starting GUI or CLI modes
- **`tools/populate_codebase.py`**: Script to bulk-load codebases into ChromaDB vector database
- **`docs/ROADMAP.md`**: Detailed future development plans and integrations
- **`docs/MIGRATION.md`**: Guide for migrating between versions
- **`tests/`**: Comprehensive test suite with unit and integration tests
- **`conversation_memory.db`**: SQLite database for persistent chat history

### Adding New Features

1. **New Commands**: Add to the slash command handler in `main.py`
2. **Configuration**: Add environment variables to `.env` and code
3. **Knowledge**: Use `/learn` command or use the `/populate` command

## 🐛 Troubleshooting

### Common Issues

**"ERROR: No .env file found!"**
- The application requires a `.env` file - copy from template: `cp .env.example .env`
- Edit `.env` with your specific configuration values
- All variables in `.env.example` are required - no defaults exist

**"ERROR: [VARIABLE_NAME] environment variable is required"**
- Check that all required variables are set in your `.env` file
- Compare with `.env.example` to ensure nothing is missing
- Restart the application after fixing the configuration

**"Cannot connect to LM Studio"**
- Ensure LM Studio is running and a model is loaded
- Check `LM_STUDIO_URL` in `.env` matches your LM Studio endpoint
- Verify the model specified in `MODEL_NAME` is loaded in LM Studio

**"ERROR: ChromaDB connection failed"**
- ChromaDB v2 server is **required** for learning features (/learn and /populate)
- Ensure ChromaDB server is running: `chroma run --host 192.168.0.204 --port 8000 --path ./chroma_data`
- Check `CHROMA_HOST` and `CHROMA_PORT` in `.env` match your server
- Ensure Ollama is running: `ollama serve`
- Check `OLLAMA_BASE_URL` points to correct Ollama instance

**"Import errors"**
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Check Python version compatibility (requires Python 3.13.9)

**"Memory not loading"**
- Check `conversation_memory.db` exists and is readable
- Verify file permissions and SQLite database integrity
- The app will create a new database if corrupted

**"Database connection failed"**
- For SQLite: Ensure write permissions to database file location
- For ChromaDB: Check server is running and network connectivity
- For Ollama: Verify service is running and accessible

**"Data corruption detected"**
- Run integrity checks on database
- Restore from backup if available
- Checksum verification failed - data may be compromised

### Debug Mode

Enable detailed logging by modifying the logging level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

### Reset Application

To completely reset the application:

```bash
# Remove memory and vector databases
rm -f conversation_memory.db
rm -rf chroma_data/

# ChromaDB data is stored in server directory and will be reset

# Restart with clean state
python3 main.py
```

## 📊 Performance Notes

- **Memory Usage**: Limited by `MAX_HISTORY_PAIRS` (default: 10 pairs)
- **Response Time**: Depends on LM Studio model size and hardware
- **Storage**: Vector database grows with learned knowledge
- **Token Limits**: Large conversations may hit LLM token limits

## 🚀 Deployment Options

### Installation

For traditional Python installation:

```bash
# Install as a package
pip install -e .

# Run as installed package
ai-assistant-cli    # CLI version
ai-assistant-gui    # GUI version
```

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

### Edge Cases to Test
- Large codebases with thousands of files
- Very long conversations (100+ messages)
- Special characters and Unicode content
- Network interruptions during AI responses
- Memory limits and performance with large vector databases

### Providing Feedback

Please report issues and suggestions at: [GitHub Issues](https://github.com/BlackcoinDev/devassist/issues)

When reporting bugs, please include:
- Operating system and Python version
- Steps to reproduce the issue
- Expected vs actual behavior
- Any error messages or logs

## 🔧 GPU Memory Troubleshooting

### Current Working Configuration

**✅ RECOMMENDED SETUP**: devstral-small-2507-mlx provides optimal performance for most systems.

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
1. **Use devstral-small-2507-mlx** (recommended - already working perfectly)
2. **Reduce memory usage**:
   ```bash
   /clear                    # Reset conversation history
   /learning strict         # Reduce context overhead
   ```
   Update `.env`: `MAX_HISTORY_PAIRS=2`

3. **Force CPU mode** (if GPU issues persist):
   - LM Studio → Model Settings → Override Parameters
   - Add: `--gpu-layers 0`
   - Slower (~10-20s) but stable

**Performance Expectations**:
- **qwen3-4b models**: 3-8 seconds per response
- **CPU mode**: 10-20 seconds per response
- **devstral-small-2507-mlx**: 15-30 seconds (with optimizations)

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

```
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
```

## 🙋 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure all prerequisites are met
4. Create an issue with detailed information

---

**Happy chatting with your AI assistant! 🤖✨**
