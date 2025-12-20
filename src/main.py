#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2025 BlackcoinDev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
AI Assistant Chat Application v0.2.0 - Learning Edition

CORE SYSTEM OVERVIEW:
====================
This application provides an intelligent conversational AI assistant with advanced learning
and document processing capabilities. Built specifically for the qwen3-vl-30b + qwen3-embedding + ChromaDB stack.

ARCHITECTURAL PRINCIPLES:
- Zero hardcoded defaults - all configuration via .env file
- Type-safe implementation with comprehensive MyPy checking
- Dual interface support (GUI + CLI) with identical functionality
- Sandboxed file operations within current directory only
- Persistent knowledge across sessions via vector database

VERSION 0.1 CAPABILITIES:
========================
🤖 AI FEATURES:
- Conversational AI with qwen3-vl-30b via LM Studio
- 8 specialized tools for file operations, document processing, and web search
- Autonomous tool calling with natural language triggers
- Context-aware responses using learned knowledge

🧠 LEARNING SYSTEM:
- Teach AI new information via /learn command
- Persistent knowledge storage in ChromaDB v2
- Semantic search with qwen3-embedding via Ollama
- Spaces system for isolated knowledge workspaces

📄 DOCUMENT INTELLIGENCE:
- qwen3-vl-30b multimodal analysis for OCR, table extraction, form recognition
- Support for PDFs, images, Office documents, and text files
- Structured data extraction (text, tables, forms, layout)
- Bulk codebase ingestion with 80+ file type support

💾 DATA MANAGEMENT:
- SQLite database for conversation memory
- ChromaDB v2 server for vector knowledge storage
- Automatic conversation persistence across sessions
- Secure file operations with path validation

🎛️ USER INTERFACE:
- Modern PyQt6 GUI with dark/light themes
- Complete CLI interface with identical functionality
- Comprehensive slash command system (/help, /learn, /vectordb, etc.)
- Real-time streaming responses and status updates

🔧 TECHNICAL STACK:
- LLM: qwen3-vl-30b via LM Studio (function calling enabled)
- Embeddings: qwen3-embedding:latest via Ollama
- Vector DB: ChromaDB v2 server for knowledge persistence
- Memory: SQLite for conversation history
- Framework: LangChain for orchestration
- UI: PyQt6 for GUI, Rich CLI for terminal

INITIALIZATION SEQUENCE:
1. Load environment configuration (.env file required)
2. Initialize qwen3-vl-30b connection via LM Studio
3. Connect to ChromaDB v2 server for knowledge operations
4. Initialize Ollama embeddings for vectorization
5. Load/create SQLite database for conversation memory
6. Bind 8 AI tools to LLM for autonomous execution
8. Start interactive chat loop with tool calling support
4. Load space settings and current workspace configuration
5. Load conversation history from SQLite database
6. Enter main chat loop with learning capabilities
7. Persist all data (conversations, learned knowledge, space settings) to respective stores
"""

# =============================================================================
# IMPORTS
# =============================================================================

# Core LangChain components for AI chat functionality
from src.commands.handlers.legacy_commands import (
    handle_read_command,
    handle_write_command,
    handle_list_command,
    handle_pwd_command,
    show_memory,
    handle_clear_command,
    handle_learn_command,
    show_vectordb,
    show_mem0,
    handle_populate_command,
    show_model_info,
    handle_context_command,
    handle_learning_command,
    handle_space_command,
    handle_export_command,
)
from src.tools.executors.document_tools import execute_parse_document
from src.tools import ToolRegistry

# Command handlers removed - now auto-registered via decorators
from src.commands import CommandRegistry

# CLI handlers will be imported as needed to avoid circular imports
# from src.cli.handlers import (
#     handle_read_command,
#     handle_write_command,
#     handle_list_command,
#     handle_pwd_command,
#     handle_clear_command,
#     handle_learn_command,
#     show_vectordb,
# )
from src.storage import (
    initialize_database,
    load_memory,
    save_memory,
    trim_history,
    load_embedding_cache,
    load_query_cache,
    save_query_cache,
    cleanup_memory,
)
from src.vectordb import (
    get_space_collection_name,
    ensure_space_collection,
    list_spaces,
    delete_space,
    switch_space,
    load_current_space,
    save_current_space,
)
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
from src.core.context import get_context
from src.core.config import get_config, get_logger, APP_VERSION
from src.core.utils import chunk_text
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage,
)  # Message types for chat

# Base class for all message types
# BaseMessage removed - not used
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)  # Text chunking for documents

# Standard library imports
import os  # Environment variable and file system operations
import sys  # System operations and exit handling

# Standard library imports (kept for backwards compatibility and test mocking)
import sqlite3
import threading  # Thread synchronization for database operations
from datetime import datetime  # Timestamps for learned knowledge

# Type hints for better code clarity
from typing import List, Optional, cast

# Security and configuration
from pydantic import SecretStr  # Kept for backwards compatibility

# Mem0 for personalized memory
try:
    from mem0 import Memory

    MEM0_AVAILABLE = True
except ImportError:
    Memory = None
    MEM0_AVAILABLE = False

# =============================================================================
# SECURITY MODULE (extracted to src/security/)
# =============================================================================

# Import security classes from dedicated module
# Security classes are imported from src.security as needed

# =============================================================================
# CONFIGURATION MODULE (extracted to src/core/config.py)
# =============================================================================

# Import configuration from dedicated module

# Import application context (dependency injection)

# Setup logging
logger = get_logger()

# Load configuration (validates all required env vars)
_config = get_config()

# =============================================================================
# BACKWARDS-COMPATIBLE CONFIGURATION EXPORTS
# =============================================================================
# These module-level constants are kept for backwards compatibility
# with existing code that imports them directly from main.py

# Core LLM Configuration
LM_STUDIO_BASE_URL: str = _config.lm_studio_url
LM_STUDIO_API_KEY: str = _config.lm_studio_key
MODEL_NAME: str = _config.model_name

# Conversation Memory Configuration
MAX_HISTORY_PAIRS: int = _config.max_history_pairs
TEMPERATURE: float = _config.temperature
MAX_INPUT_LENGTH: int = _config.max_input_length

# Verbose Logging Configuration
VERBOSE_LOGGING: bool = _config.verbose_logging
SHOW_LLM_REASONING: bool = _config.show_llm_reasoning
SHOW_TOKEN_USAGE: bool = _config.show_token_usage
SHOW_TOOL_DETAILS: bool = _config.show_tool_details

# Vector Database Configuration
CHROMA_HOST: str = _config.chroma_host
CHROMA_PORT: int = _config.chroma_port
OLLAMA_BASE_URL: str = _config.ollama_base_url
EMBEDDING_MODEL: str = _config.embedding_model

# =============================================================================
# RUNTIME STATE (now backed by ApplicationContext)
# =============================================================================

# Initialize the application context
_ctx = get_context()

# Backwards-compatible module-level variables
# These are properties that delegate to the ApplicationContext
# Note: For new code, prefer using get_context() or the accessor functions

# AI Behavior Settings - now backed by context
# Use get_context_mode()/set_context_mode() for access
CONTEXT_MODE = _ctx.context_mode
LEARNING_MODE = _ctx.learning_mode
CURRENT_SPACE = _ctx.current_space

# Caches - now backed by context
QUERY_CACHE = _ctx.query_cache

# Core services - now backed by context
# Use get_llm()/set_llm() etc. for access
llm = _ctx.llm
vectorstore = _ctx.vectorstore
embeddings = _ctx.embeddings
chroma_client = _ctx.chroma_client
user_memory = _ctx.user_memory
conversation_history = _ctx.conversation_history

# Operation counter for periodic cleanup
operation_count = 0

# =============================================================================
# HTTP CLIENT SETUP
# =============================================================================


# Create a session with connection pooling and retries
api_session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=0.3,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
api_session.mount("http://", adapter)
api_session.mount("https://", adapter)

# =============================================================================
# VECTORDB MODULE (extracted to src/vectordb/)
# =============================================================================

# Import space management and ChromaDB client from dedicated module

# =============================================================================
# CACHING FUNCTIONS
# =============================================================================


# =============================================================================
# STORAGE MODULE (extracted to src/storage/)
# =============================================================================

# Import storage functions from dedicated module

# Initialize database and caches at module load time
initialize_database()
load_embedding_cache()
load_query_cache()

# Load conversation history (now uses context-backed storage)
_initial_history = load_memory()
get_context().conversation_history = _initial_history
conversation_history = get_context().conversation_history

# Backwards-compatible exports for db_conn and db_lock
# Tests may patch these, so we need to expose them at module level
db_conn = get_context().db_conn
db_lock = get_context().db_lock


def get_llm():
    """Get the current LLM instance. Used by GUI to access initialized LLM."""
    return get_context().llm


def get_vectorstore():
    """Get the current vectorstore instance. Used by GUI to access initialized vectorstore."""
    return get_context().vectorstore


def get_relevant_context(
    query: str, k: int = 3, space_name: Optional[str] = None
) -> str:
    """Get relevant context from vector database with caching."""
    # Use current space if not specified
    if space_name is None:
        space_name = CURRENT_SPACE

    # Check query cache first
    cache_key = f"{space_name}:{query}:{k}"
    if cache_key in QUERY_CACHE:
        cached_results = QUERY_CACHE[cache_key]
        if cached_results:
            context = "\n\n".join(
                [f"From knowledge base:\n{doc}" for doc in cached_results]
            )
            return f"\n\nRelevant context:\n{context}\n\n"

    # Return empty context if vector database not available
    if vectorstore is None:
        return ""

    try:
        # Generate embedding for the query - embeddings will be available at
        # runtime
        try:
            # Use global embeddings variable (initialized during application
            # startup)
            if embeddings is None:
                logger.warning("Embeddings not initialized for context retrieval")
                return ""

            query_embedding = embeddings.embed_query(query)
        except (AttributeError, NameError, Exception) as e:
            logger.warning(f"Embeddings not available for context retrieval: {e}")
            return ""

        # Find collection for the specified space
        collection_id = None
        collection_name = get_space_collection_name(space_name)

        # Try to find the collection by name
        try:
            list_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v2/tenants/default_tenant/databases/default_database/collections"
            list_response = requests.get(list_url, timeout=10)
            if list_response.status_code == 200:
                collections = list_response.json()
                for coll in collections:
                    if coll.get("name") == collection_name:
                        collection_id = coll.get("id")
                        break
        except Exception as e:
            logger.warning(f"Error finding collection for space {space_name}: {e}")

        if not collection_id:
            logger.warning(f"Could not find collection for space {space_name}")
            return ""

        # ChromaDB v2 API endpoint for querying
        query_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v2/tenants/default_tenant/databases/default_database/collections/{collection_id}/query"

        # Query payload with embedding
        payload = {"query_embeddings": [query_embedding], "n_results": k}

        response = api_session.post(query_url, json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Extract documents from response
            docs = []
            if "documents" in data and data["documents"] and len(data["documents"]) > 0:
                documents = data["documents"][0]  # First query result
                for doc_content in documents:
                    docs.append(doc_content)

            # Return empty if no relevant documents found
            if not docs:
                return ""

            # Cache the results
            QUERY_CACHE[cache_key] = docs
            if len(QUERY_CACHE) % 50 == 0:
                save_query_cache()

            context = "\n\n".join([f"From knowledge base:\n{doc}" for doc in docs])
            return f"\n\nRelevant context:\n{context}\n\n"
        else:
            print(f"ChromaDB query failed: {response.status_code}")
            return ""

    except Exception as e:
        # Log error but don't crash - AI can still respond without context
        logger.warning(f"Failed to retrieve context: {e}")
        return ""


# =============================================================================
# COMMANDS MODULE (registry infrastructure in src/commands/)
# =============================================================================

# Import command registry for future migration

# Command handlers are now registered via decorators in their respective modules
# No need to import them here as they're auto-registered

# Import legacy command handlers (will be migrated to new system)

# Note: Command handlers remain in this file for now.
# They can be incrementally migrated to src/commands/handlers/ using:
#   @register_command("help", "Show available commands")
#   def handle_help(args): ...


def handle_slash_command(command: str) -> bool:
    """
    Handle slash commands using CommandRegistry.

    All command handlers are registered via @CommandRegistry.register()
    decorators in src/commands/handlers/.

    Returns True if command was handled, False if it is a regular message.
    """
    # Remove leading slash and split command
    if not command.startswith("/"):
        return False

    cmd_parts = command[1:].split()
    if not cmd_parts:
        return False

    cmd_name = cmd_parts[0].lower()
    cmd_args = cmd_parts[1:] if len(cmd_parts) > 1 else []

    # Import CommandRegistry
    # CommandRegistry is now imported within handle_slash_command as needed

    # Dispatch to registered handler
    handled = CommandRegistry.dispatch(cmd_name, cmd_args)

    if not handled:
        print(f"\n❌ Unknown command: /{cmd_name}")
        print("Type /help for available commands\n")

    return True


def handle_read_command(file_path: str):
    """Handle /read command to read file contents."""
    if not file_path:
        print("\n❌ Usage: /read <file_path>")
        print("Example: /read README.md\n")
        return

    try:
        # Security: Only allow reading files in current directory and
        # subdirectories
        current_dir = os.getcwd()
        full_path = os.path.abspath(file_path)

        # Check if the file is within the current directory
        if not full_path.startswith(current_dir):
            print(f"\n❌ Access denied: Cannot read files outside current directory")
            print(f"Current directory: {current_dir}\n")
            return

        if not os.path.exists(full_path):
            print(f"\n❌ File not found: {file_path}\n")
            return

        if not os.path.isfile(full_path):
            print(f"\n❌ Not a file: {file_path}\n")
            return

        # Check file size (limit to 1MB to prevent memory issues)
        file_size = os.path.getsize(full_path)
        if file_size > 1024 * 1024:  # 1MB limit
            print(f"\n❌ File too large: {file_size} bytes (max 1MB)")
            print("Use a text editor to view large files\n")
            return

        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        print(f"\n📄 File: {file_path}")
        print(f"📊 Size: {file_size} bytes")
        print("-" * 50)
        print(content)
        print("-" * 50)
        print(f"✅ File read successfully\n")

    except UnicodeDecodeError:
        print(f"\n❌ Cannot read binary file: {file_path}")
        print("This appears to be a binary file. Use /list to see file types.\n")
    except Exception as e:
        print(f"\n❌ Failed to read file: {e}\n")


def handle_write_command(args: str):
    """Handle /write command to write content to a file."""
    if not args:
        print("\n❌ Usage: /write <file_path> <content>")
        print("Example: /write notes.txt This is my note\n")
        return

    # Split on first space to separate file path from content
    parts = args.split(" ", 1)
    if len(parts) < 2:
        print("\n❌ Usage: /write <file_path> <content>")
        print("Content is required\n")
        return

    file_path, content = parts

    try:
        # Security: Only allow writing files in current directory and
        # subdirectories
        current_dir = os.getcwd()
        full_path = os.path.abspath(file_path)

        # Check if the file is within the current directory
        if not full_path.startswith(current_dir):
            print(f"\n❌ Access denied: Cannot write files outside current directory")
            print(f"Current directory: {current_dir}\n")
            return

        # Create directory if it doesn't exist
        dir_path = os.path.dirname(full_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"\n✅ File written: {file_path}")
        print(f"📊 Content length: {len(content)} characters\n")

    except Exception as e:
        print(f"\n❌ Failed to write file: {e}\n")


def handle_list_command(dir_path: str = ""):
    """Handle /list command to list directory contents."""
    try:
        if not dir_path:
            target_dir = os.getcwd()
        else:
            # Security: Only allow listing directories in current directory
            current_dir = os.getcwd()
            full_path = os.path.abspath(dir_path)

            if not full_path.startswith(current_dir):
                print(
                    f"\n❌ Access denied: Cannot list directories outside current directory"
                )
                print(f"Current directory: {current_dir}\n")
                return

            if not os.path.exists(full_path):
                print(f"\n❌ Directory not found: {dir_path}\n")
                return

            if not os.path.isdir(full_path):
                print(f"\n❌ Not a directory: {dir_path}\n")
                return

            target_dir = full_path

        print(f"\n📁 Directory: {os.path.relpath(target_dir, os.getcwd()) or '.'}")
        print("-" * 50)

        items = os.listdir(target_dir)
        if not items:
            print("📂 (empty directory)")
        else:
            # Separate files and directories
            dirs = []
            files = []

            for item in sorted(items):
                full_item_path = os.path.join(target_dir, item)
                if os.path.isdir(full_item_path):
                    dirs.append(item + "/")
                else:
                    files.append(item)

            # Display directories first, then files
            for item in dirs + files:
                print(f"  {item}")

        print("-" * 50)
        print(f"📊 Total items: {len(items)}\n")

    except Exception as e:
        print(f"\n❌ Failed to list directory: {e}\n")


def handle_pwd_command():
    """Handle /pwd command to show current working directory."""
    try:
        current_dir = os.getcwd()
        print(f"\n📍 Current directory: {current_dir}\n")
    except Exception as e:
        print(f"\n❌ Failed to get current directory: {e}\n")


def show_memory():
    """Show conversation history."""
    if not conversation_history:
        print("\n📝 No conversation history available.\n")
        return

    print(f"\n📝 Conversation History ({len(conversation_history)} messages):\n")
    for i, msg in enumerate(conversation_history):
        msg_type = type(msg).__name__.replace("Message", "")
        content = str(msg.content)
        content_preview = content[:100] + "..." if len(content) > 100 else content
        print(f"{i + 1:2d}. {msg_type}: {content_preview}")
    print()


def handle_clear_command() -> bool:
    """Handle /clear command. Returns True if should exit."""
    confirm = input(
        "Are you sure you want to clear all conversation history? (yes/no): "
    )
    if confirm.lower() in ["yes", "y"]:
        global conversation_history
        # Clear display and show confirmation
        print("\nConversation memory cleared. Starting fresh.\n")

        # Add a new system message for the fresh start
        from langchain_core.messages import SystemMessage

        conversation_history = [SystemMessage(content="Lets get some coding done..")]
        save_memory(conversation_history)
        return False
    else:
        print("\n❌ Clear cancelled\n")
        return False


def handle_learn_command(content: str):
    """Handle /learn command."""
    # Check if vector database is available
    if vectorstore is None:
        print(
            "\nVector database not available. ChromaDB is required for learning features.\n"
        )
        return

    # Extract content after 'learn ' command
    if not content:
        print("\nUsage: /learn <information to remember>\n")
        return

    try:
        # Import Document class for creating knowledge entries
        from langchain_core.documents import Document

        # Create document with metadata
        doc = Document(
            page_content=content,  # The information to remember
            metadata={
                "source": "user-input",  # Mark as manually added via /learn command
                "added_at": str(datetime.now()),  # Timestamp for tracking
            },
        )

        # Add to vector database for current space
        # Generate embeddings and use direct HTTP API calls to ChromaDB v2

        # Generate embeddings using Ollama
        try:
            # Import here to handle initialization order
            from src.main import embeddings

            embeddings_result = embeddings.embed_documents([doc.page_content])
            if embeddings_result and len(embeddings_result) > 0:
                embedding_vector = embeddings_result[0]

                # Get collection for current space
                collection_name = get_space_collection_name(CURRENT_SPACE)
                collection_id = None

                # Find or create the collection
                try:
                    list_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v2/tenants/default_tenant/databases/default_database/collections"
                    list_response = api_session.get(list_url, timeout=10)
                    if list_response.status_code == 200:
                        collections = list_response.json()
                        for coll in collections:
                            if coll.get("name") == collection_name:
                                collection_id = coll.get("id")
                                break

                    # If collection doesn't exist, create it
                    if not collection_id:
                        create_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v2/tenants/default_tenant/databases/default_database/collections"
                        create_payload = {"name": collection_name}
                        create_response = api_session.post(
                            create_url, json=create_payload, timeout=10
                        )
                        if create_response.status_code == 201:
                            collection_id = create_response.json().get("id")
                            logger.info(
                                f"Created new collection for space {CURRENT_SPACE}: {collection_name}"
                            )
                        else:
                            logger.error(
                                f"Failed to create collection: HTTP {
                                    create_response.status_code
                                }"
                            )
                            raise Exception("Collection creation failed")

                except Exception as e:
                    logger.error(
                        f"Error managing collection for space {CURRENT_SPACE}: {e}"
                    )
                    raise

                # Add document to the space's collection
                add_url = (
                    f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v2/"
                    f"tenants/default_tenant/databases/default_database/"
                    f"collections/{collection_id}/add"
                )

                # Prepare the document data with embeddings
                doc_id = f"doc_{len(doc.page_content)}_{int(datetime.now().timestamp() * 1000000)}"
                payload = {
                    "ids": [doc_id],
                    "embeddings": [embedding_vector],
                    "documents": [doc.page_content],
                    "metadatas": [doc.metadata] if doc.metadata else [{}],
                }

                # Make the API call to add the document
                headers = {"Content-Type": "application/json"}
                response = api_session.post(
                    add_url, json=payload, headers=headers, timeout=10
                )

                if response.status_code == 201:
                    logger.info(
                        f"Document added successfully to space {CURRENT_SPACE}: {doc_id}"
                    )
                else:
                    logger.error(
                        f"Failed to add document to space {CURRENT_SPACE}: {
                            response.status_code
                        } - {response.text}"
                    )
                    raise Exception("Document addition failed")

            else:
                logger.error("Failed to generate embeddings")
                raise Exception("Embedding generation failed")

        except Exception as e:
            logger.error(f"Error with direct ChromaDB v2 API: {e}")
            # Fallback to LangChain method
            try:
                vectorstore.add_documents([doc])
                logger.debug("Used LangChain fallback for document addition")
            except Exception as fallback_e:
                logger.error(f"LangChain fallback also failed: {fallback_e}")
                print(f"\n❌ Failed to learn: {e}\n")
                return

        # Periodic memory cleanup
        global operation_count
        operation_count += 1
        if operation_count % 50 == 0:
            cleanup_memory()

        print(f"\n✅ Learned: {content[:50]}...\n")

    except Exception as e:
        print(f"\n❌ Failed to learn: {e}\n")


def show_vectordb():
    """
    Display information about the current vector database contents.

    Shows collection statistics, chunk count, unique sources, and content insights
    from the ChromaDB vector database. Provides insights into the AI's knowledge base.
    """
    if vectorstore is None:
        print("\n❌ Vector database not available.\n")
        return

    # Initialize variables that may be used in error handling
    collection_name = get_space_collection_name(CURRENT_SPACE)
    collection_id = None

    try:
        print("\n--- Vector Database Contents ---")

        # Try to get documents from ChromaDB via direct API
        try:
            # Find collection for current space
            # collection_name and collection_id are already initialized above

            list_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v2/tenants/default_tenant/databases/default_database/collections"
            list_response = api_session.get(list_url, timeout=10)

            if list_response.status_code == 200:
                collections = list_response.json()
                for coll in collections:
                    if coll.get("name") == collection_name:
                        collection_id = coll.get("id")
                        break

            if not collection_id:
                print(f"❌ No collection found for current space '{CURRENT_SPACE}'")
                print("The space may not have any documents yet.")
                return

            logger.info(
                f"Using collection for space {CURRENT_SPACE}: {collection_name} (ID: {collection_id})"
            )

            # Get collection statistics
            count_url = (
                f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v2/"
                f"tenants/default_tenant/databases/default_database/"
                f"collections/{collection_id}/count"
            )
            count_response = api_session.get(count_url, timeout=10)

            if count_response.status_code == 200:
                count_data = count_response.json()
                chunk_count = (
                    count_data
                    if isinstance(count_data, int)
                    else count_data.get("count", 0)
                )
                print(f"📊 Collection: {collection_name}")
                print(f"📈 Chunks: {chunk_count}")
                print(f"🏢 Space: {CURRENT_SPACE}")

                if chunk_count > 0:
                    try:
                        # Get metadata for statistics
                        chroma_client = vectorstore._client
                        collection = chroma_client.get_collection(collection_name)
                        results = collection.get(
                            # Sample up to 1000 for stats
                            limit=min(chunk_count, 1000),
                            include=["metadatas"],
                        )

                        if results and "metadatas" in results and results["metadatas"]:
                            metadatas = results["metadatas"]
                            if metadatas is None:
                                metadatas = []

                            # Analyze metadata for insights
                            sources = set()
                            content_types = set()
                            dates = []

                            for metadata in metadatas:
                                if metadata:
                                    if "source" in metadata:
                                        sources.add(metadata["source"])
                                    if "content_type" in metadata:
                                        content_types.add(metadata["content_type"])
                                    if "added_at" in metadata:
                                        try:
                                            # Parse date
                                            dates.append(metadata["added_at"])
                                        except Exception:
                                            pass

                            print(f"\n📋 Statistics:")
                            print(f"   📄 Unique Sources: {len(sources)}")
                            if sources:
                                print(
                                    f"   🔗 Sources: {', '.join(list(sources)[:5])}{
                                        '...' if len(sources) > 5 else ''
                                    }"
                                )

                            if content_types:
                                print(
                                    f"   📝 Content Types: {', '.join(content_types)}"
                                )

                            if dates:
                                try:
                                    date_objs = [
                                        datetime.fromisoformat(d.replace("Z", "+00:00"))
                                        for d in dates
                                        if d
                                    ]
                                    if date_objs:
                                        earliest = min(date_objs)
                                        latest = max(date_objs)
                                        print(
                                            f"   📅 Date Range: {
                                                earliest.strftime('%Y-%m-%d')
                                            } to {latest.strftime('%Y-%m-%d')}"
                                        )
                                except Exception:
                                    pass

                            # Show recent additions (last 3 by date)
                            # Show sample sources
                            sample_sources = []
                            # Check first 5 for examples
                            for metadata in metadatas[:5]:
                                if metadata and metadata.get("source"):
                                    sample_sources.append(
                                        (
                                            metadata.get("source"),
                                            metadata.get("added_at", "unknown"),
                                        )
                                    )
                                    if len(sample_sources) >= 3:
                                        break

                            if sample_sources:
                                print(f"\n🕒 Sample Sources:")
                                for i, (source, added_at) in enumerate(sample_sources):
                                    print(f"   {i + 1}. {source} (added: {added_at})")

                        else:
                            print("\n📋 Statistics: Unable to retrieve metadata")

                    except Exception as e:
                        print(f"\n❌ Error retrieving statistics: {e}")
                else:
                    print(f"\n  No chunks found in the knowledge base.")
                    print(
                        f"  Use /learn to add information or /populate to add codebases."
                    )
            else:
                print(f"Failed to retrieve chunks: HTTP {count_response.status_code}")
                print("Vector database connection may have issues.")

            print("--- End Vector Database ---")

        except Exception as e:
            print(f"❌ An error occurred: {e}")
            print(f"DEBUG: Exception type: {type(e)}")
            # The original instruction included 'break' and 'continue' here,
            # but they are only valid inside loops.
            # To maintain syntactical correctness as per instructions,
            # these statements are omitted as this block is not within a loop.
            # If this exception block was part of a loop, 'break' or 'continue'
            # would be placed here.

            # Get collection statistics instead of all documents
            count_url = (
                f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v2/"
                f"tenants/default_tenant/databases/default_database/"
                f"collections/{collection_id}/count"
            )
            count_response = api_session.get(count_url, timeout=10)

            if count_response.status_code == 200:
                count_data = count_response.json()
                count = (
                    count_data
                    if isinstance(count_data, int)
                    else count_data.get("count", 0)
                )
                print(f"📊 Collection: {collection_name}")
                print(f"📈 Documents: {count}")
                print(f"🏢 Space: {CURRENT_SPACE}")

                if count > 0:
                    print("\n📄 Sample Documents:")
                    try:
                        # Try to get sample documents using ChromaDB client
                        # directly
                        chroma_client = vectorstore._client
                        collection = chroma_client.get_collection(collection_name)
                        results = collection.get(
                            limit=3, include=["documents", "metadatas"]
                        )

                        if results and "documents" in results and results["documents"]:
                            docs = results["documents"]
                            if docs is None:
                                docs = []
                            metadatas = results.get("metadatas") or [{}] * len(docs)

                            # First 3 documents
                            for i, doc in enumerate(docs[:3]):
                                metadata = metadatas[i] if i < len(metadatas) else {}
                                if isinstance(doc, str):
                                    # Clean up the preview - remove excessive
                                    # whitespace and binary-looking content
                                    preview = doc.strip()
                                    # Check for binary content, PDF metadata,
                                    # or placeholder text
                                    if (
                                        any(
                                            indicator in preview.lower()
                                            for indicator in [
                                                "<source>",
                                                "</source>",
                                                "<translation",
                                                "<<",
                                                ">>",
                                                "/type",
                                                "/pages",
                                                "xref",
                                                "trailer",
                                                "startxref",
                                            ]
                                        )
                                        or any(
                                            ord(c) < 32 and c not in "\n\t"
                                            for c in preview[:100]
                                        )
                                        or preview.startswith("[Binary file:")
                                        or "[Binary file:" in preview
                                    ):
                                        preview = "[Binary file - content not shown]"
                                    elif len(preview) > 200:
                                        preview = preview[:200] + "..."
                                    elif not preview:
                                        preview = "[empty content]"

                                    source = (
                                        metadata.get("source", "unknown")
                                        if metadata
                                        else "unknown"
                                    )
                                    added_at = (
                                        metadata.get("added_at", "unknown")
                                        if metadata
                                        else "unknown"
                                    )
                                    print(f"  {i + 1}. {source} (added: {added_at})")
                                    print(f"      Preview: {preview}")
                                else:
                                    print(
                                        f"  {i + 1}. [Non-text document: {type(doc)}]"
                                    )
                        else:
                            print("  No documents found in collection")
                    except Exception as e:
                        print(f"  Could not retrieve sample documents: {str(e)[:100]}")
                        print(
                            "  (This is normal for some document types or if the collection is empty)"
                        )
                    print()
            else:
                print("❌ Could not retrieve collection statistics")

    except Exception as e:
        print(f"❌ Error accessing vector database: {e}")


def show_mem0():
    """
    Display information about the current Mem0 personalized memory contents.

    Shows user memory statistics and sample memories from the Mem0 system.
    """
    if user_memory is None:
        print("\n❌ Mem0 not available.\n")
        return

    try:
        print("\n--- Mem0 Personalized Memory Contents ---")

        # Get all memories for the user
        memories = user_memory.get_all(user_id="default_user")

        if VERBOSE_LOGGING:
            print(f"🧠 Mem0: Retrieved {len(memories.get('results', []))} memories")

        if not memories or not memories.get("results"):
            print("📊 No personalized memories stored yet.")
            print("Memories are automatically created from your conversations.")
            return

        results = memories["results"]
        print(f"📊 Memories: {len(results)}")
        print(f"👤 User ID: user")

        if results:
            print("\n🧠 Sample Memories:")
            for i, memory in enumerate(results[:5]):  # Show first 5
                content = memory.get("memory", "No content")
                if len(content) > 200:
                    content = content[:200] + "..."
                print(f"  {i + 1}. {content}")

            if len(results) > 5:
                print(f"  ... and {len(results) - 5} more")

    except Exception as e:
        print(f"\n❌ Failed to retrieve Mem0 contents: {e}\n")


def handle_populate_command(dir_path: str):
    """
    Handle the /populate command to bulk import codebases into the vector database.

    Parses command arguments including optional flags like --dry-run and --direct-api.
    Processes files in batches, extracts content from various file types, and adds
    them to the ChromaDB collection with proper metadata.

    Args:
        dir_path: Directory path with optional flags (--dry-run, --direct-api)
    """
    # Import ChromaDB client for direct API usage
    from chromadb import HttpClient

    # Access global chroma_client
    global chroma_client
    # Parse additional options from dir_path
    parts = dir_path.split()
    directory = parts[0] if parts else ""
    options = parts[1:] if len(parts) > 1 else []

    dry_run = "--dry-run" in options
    use_direct_api = True  # Always use direct API for better reliability
    clear_first = "--clear" in options

    # Check if directory exists
    if not directory:
        print("\nUsage: /populate /path/to/directory [--dry-run] [--direct-api]")
        print("Examples:")
        print("   /populate /Users/username/projects/myapp")
        print("   /populate src/ --dry-run")
        print("   /populate . --clear")
        print("   /populate ~/code --dry-run --clear")
        print("\nOptions:")
        print("  --dry-run     : Validate files without writing to database")
        print("  --clear       : Delete existing collection before repopulating")
        print(
            "\nNote: Designed for code files. For documents (PDFs, etc.), use document processing tools."
        )
        print("Uses direct ChromaDB API for optimal reliability and performance")
        print(
            "\nNote: This will recursively scan and add all code files to the vector database."
        )
        return

    if not os.path.exists(directory):
        print(f"\n❌ Directory not found: {directory}")
        return

    if not os.path.isdir(directory):
        print(f"\n❌ Path is not a directory: {directory}")
        return

    print(f"\n🔍 Starting codebase population from: {directory}")
    if dry_run:
        print("🔍 DRY RUN MODE - No data will be written to database")
    if clear_first:
        print("🧹 CLEAR MODE - Will delete existing collection before repopulating")
    print("🔧 Using direct ChromaDB API for optimal reliability and performance")
    print("This may take some time for large codebases...")
    print()

    # Check if vectorstore is available
    if vectorstore is None:
        print("\n❌ Vector database not available. Check your configuration.")
        return

    # Clear existing collection if requested
    if clear_first and not dry_run:
        print("🧹 Clearing existing collection...")
        try:
            # Get the collection name for current space
            collection_name = get_space_collection_name(CURRENT_SPACE)

            # Use direct ChromaDB API to delete collection
            import requests

            delete_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v2/tenants/default_tenant/databases/default_database/collections/{collection_name}"
            response = requests.delete(delete_url, timeout=10)

            if response.status_code in [200, 204]:
                print(f"✅ Cleared collection: {collection_name}")
            else:
                print(
                    f"⚠️  Collection may not exist or failed to clear: {
                        response.status_code
                    }"
                )
        except Exception as e:
            print(f"⚠️  Failed to clear collection: {e}")

    try:
        # Import required libraries for population
        from pathlib import Path
        from langchain_core.documents import Document

        # Code file extensions (same as tools/populate_codebase.py)
        CODE_EXTENSIONS = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "react",
            ".tsx": "react-typescript",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c-header",
            ".hpp": "cpp-header",
            ".java": "java",
            ".cs": "csharp",
            ".php": "php",
            ".rb": "ruby",
            ".go": "go",
            ".rs": "rust",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "bash",
            ".sql": "sql",
            ".html": "html",
            ".css": "css",
            ".md": "markdown",
            ".json": "json",
            ".xml": "xml",
            ".yaml": "yaml",
            ".yml": "yaml",
        }

        # ChromaDB doesn't provide easy count

        # Scan directory
        directory = Path(directory)
        files_to_process = []

        for file_path in directory.rglob("*"):
            if file_path.is_file() and True:
                files_to_process.append(file_path)

        if not files_to_process:
            print("❌ No code files found in the specified directory.")
            return

        print(f"📋 Found {len(files_to_process)} code files to process")

        # Process files in batches for better performance
        total_chunks = 0
        processed_files = 0
        batch_size = 50  # Maximum chunks per batch to avoid payload too large
        all_documents = []

        print(f"⚡ Processing files in batches of {batch_size} chunks...")

        for file_path in files_to_process:
            relative_path = file_path.relative_to(directory)

            try:
                # Check if it's a document file that can be processed
                if file_path.suffix.lower() in [".pdf"]:
                    # For PDFs, extract text using document processing
                    try:
                        parse_result = execute_parse_document(str(file_path), "text")
                        if parse_result.get("success") and "content" in parse_result:
                            content = parse_result["content"]
                            if not content or (
                                content.startswith("[") and content.endswith("]")
                            ):
                                # If no content or still a placeholder, skip
                                # this file
                                continue
                        else:
                            # If parsing failed, skip this file
                            continue
                    except Exception:
                        # If document processing fails, skip this file
                        continue
                elif file_path.suffix.lower() in [
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".gif",
                    ".bmp",
                ]:
                    # For images, skip them (can't extract text easily)
                    continue
                else:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
            except Exception:
                continue  # Skip files that can't be read

            if not content.strip():
                continue

            # Get metadata
            ext = file_path.suffix.lower()
            language = CODE_EXTENSIONS.get(ext, "unknown")

            # Chunk the content
            chunks = chunk_text(content)

            # Create documents
            for j, chunk in enumerate(chunks):
                metadata = {
                    "source": "codebase",
                    "file_path": str(relative_path),
                    "language": language,
                    "chunk_index": j,
                    "total_chunks": len(chunks),
                    "added_at": str(datetime.now()),
                }

                doc = Document(page_content=chunk, metadata=metadata)
                all_documents.append(doc)

                # Process batch when it reaches the limit
                if len(all_documents) >= batch_size:
                    print(
                        f"💾 Adding batch of {
                            len(all_documents)
                        } chunks to vector database..."
                    )
                    try:
                        if use_direct_api:
                            # Use direct ChromaDB API
                            # Ensure chroma_client is initialized
                            if chroma_client is None:
                                chroma_client = HttpClient(
                                    host=cast(str, CHROMA_HOST), port=CHROMA_PORT
                                )

                            if chroma_client is None or embeddings is None:
                                raise Exception(
                                    "ChromaDB client or embeddings not initialized"
                                )

                            collection_name = get_space_collection_name(CURRENT_SPACE)
                            collection = chroma_client.get_collection(collection_name)

                            texts = [doc.page_content for doc in all_documents]
                            metadatas = [doc.metadata for doc in all_documents]
                            ids = [
                                f"{doc.metadata.get('file_path', 'unknown')}_{
                                    doc.metadata.get('chunk_index', i)
                                }"
                                for i, doc in enumerate(all_documents)
                            ]

                            # Generate embeddings
                            embeddings_list = embeddings.embed_documents(texts)

                            collection.add(
                                documents=texts,
                                embeddings=embeddings_list,  # type: ignore[arg-type]
                                metadatas=metadatas,
                                ids=ids,
                            )
                        else:
                            # Use LangChain wrapper
                            vectorstore.add_documents(all_documents)

                        total_chunks += len(all_documents)
                        all_documents = []  # Clear batch
                    except Exception as e:
                        print(f"❌ Failed to add batch: {e}")
                        # Continue with next batch

            processed_files += 1

            # Progress update every 10 files
            if processed_files % 10 == 0:
                print(
                    f"📄 Processed {processed_files}/{len(files_to_process)} files "
                    f"({total_chunks + len(all_documents)} total chunks)..."
                )

        # Add remaining documents
        if all_documents:
            print(f"💾 Adding final batch of {len(all_documents)} chunks...")
            try:
                if use_direct_api:
                    # Use direct ChromaDB API
                    # Ensure chroma_client is initialized
                    if chroma_client is None:
                        chroma_client = HttpClient(
                            host=cast(str, CHROMA_HOST), port=CHROMA_PORT
                        )

                    if chroma_client is None or embeddings is None:
                        raise Exception("ChromaDB client or embeddings not initialized")

                    collection_name = get_space_collection_name(CURRENT_SPACE)
                    try:
                        collection = chroma_client.get_collection(collection_name)
                    except Exception:
                        # Collection doesn't exist, create it
                        collection = chroma_client.create_collection(collection_name)

                    texts = [doc.page_content for doc in all_documents]
                    metadatas = [doc.metadata for doc in all_documents]
                    ids = [
                        f"{doc.metadata.get('file_path', 'unknown')}_{
                            doc.metadata.get('chunk_index', i)
                        }"
                        for i, doc in enumerate(all_documents)
                    ]

                    # Generate embeddings
                    embeddings_list = embeddings.embed_documents(texts)

                    collection.add(
                        documents=texts,
                        embeddings=embeddings_list,  # type: ignore[arg-type]
                        metadatas=metadatas,
                        ids=ids,
                    )
                else:
                    # Use LangChain wrapper
                    vectorstore.add_documents(all_documents)

                total_chunks += len(all_documents)
            except Exception as e:
                print(f"❌ Failed to add final batch: {e}")

        # Save and show final stats
        save_memory(conversation_history)
        print("\n✅ Codebase population completed!")
        print("📊 Statistics:")
        print(f"   Files processed: {processed_files}")
        print(f"   Total chunks added: {total_chunks}")
        print(f"   Space: {CURRENT_SPACE}")
        print()

    except Exception as e:
        print(f"\n❌ Failed to populate codebase: {e}\n")


def show_model_info():
    """Show current model information."""
    print(f"\n🤖 Current Model: {MODEL_NAME}")
    base_url_display = (
        LM_STUDIO_BASE_URL.replace("/v1", "") if LM_STUDIO_BASE_URL else "unknown"
    )
    print(f"🌐 API Endpoint: http://{base_url_display}")
    print(f"🎯 Temperature: {TEMPERATURE}")
    print(f"📏 Max Input Length: {MAX_INPUT_LENGTH}")
    print(f"💾 Context Window: {MAX_HISTORY_PAIRS} message pairs")
    print()


def handle_context_command(args: List[str]):
    """Handle /context command."""
    global CONTEXT_MODE
    if not args:
        print(f"\n🎯 Current context mode: {CONTEXT_MODE}")
        print("Options: auto, on, off")
        print("- auto: AI decides when to include context")
        print("- on: Always include available context")
        print("- off: Never include context from knowledge base")
        print()
        return

    mode = args[0].lower()
    if mode in ["auto", "on", "off"]:
        CONTEXT_MODE = mode
        print(f"\n✅ Context mode set to: {mode}\n")
    else:
        print(f"\n❌ Invalid context mode: {mode}")
        print("Valid options: auto, on, off\n")


def handle_learning_command(args: List[str]):
    """Handle /learning command."""
    global LEARNING_MODE
    if not args:
        print(f"\n🧠 Current learning mode: {LEARNING_MODE}")
        print("Options: normal, strict, off")
        print("- normal: Balanced learning with context integration")
        print("- strict: Minimal context, focused on explicit learning")
        print("- off: Disable all learning and context features")
        print()
        return

    mode = args[0].lower()
    if mode in ["normal", "strict", "off"]:
        LEARNING_MODE = mode
        print(f"\n✅ Learning mode set to: {mode}\n")
    else:
        print(f"\n❌ Invalid learning mode: {mode}")
        print("Valid options: normal, strict, off\n")


def handle_space_command(cmd_args: str):
    """Handle /space command."""
    space_cmd = cmd_args.strip()

    if not space_cmd:
        # Show current space
        print(f"\nCurrent space: {CURRENT_SPACE}")
        print(f"Collection: {get_space_collection_name(CURRENT_SPACE)}")
        print("\nUsage:")
        print("  /space list                    - List all spaces")
        print("  /space create <name>           - Create new space")
        print("  /space switch <name>           - Switch to space")
        print("  /space delete <name>           - Delete space")
        print("  /space current                 - Show current space\n")
        return

    if space_cmd == "list":
        spaces = list_spaces()
        print(f"\nAvailable spaces ({len(spaces)}):")
        for space in spaces:
            marker = " ← current" if space == CURRENT_SPACE else ""
            print(f"  • {space}{marker}")
        print()

    elif space_cmd == "current":
        print(f"\nCurrent space: {CURRENT_SPACE}")
        print(f"Collection: {get_space_collection_name(CURRENT_SPACE)}\n")

    elif space_cmd.startswith("create "):
        new_space = space_cmd[7:].strip()
        if not new_space:
            print("\n❌ Usage: /space create <name>\n")
            return

        if new_space in list_spaces():
            print(f"\n❌ Space '{new_space}' already exists\n")
            return

        if switch_space(new_space):
            print(f"\n✅ Created and switched to space: {new_space}")
            print(f"Collection: {get_space_collection_name(new_space)}\n")
        else:
            print(f"\n❌ Failed to create space: {new_space}\n")

    elif space_cmd.startswith("switch "):
        target_space = space_cmd[7:].strip()
        if not target_space:
            print("\n❌ Usage: /space switch <name>\n")
            return

        if target_space not in list_spaces():
            print(f"\n❌ Space '{target_space}' does not exist")
            print("Use '/space create {target_space}' to create it first\n")
            return

        if switch_space(target_space):
            print(f"\n✅ Switched to space: {target_space}")
            print(f"Collection: {get_space_collection_name(target_space)}\n")
        else:
            print(f"\n❌ Failed to switch to space: {target_space}\n")

    elif space_cmd.startswith("delete "):
        target_space = space_cmd[7:].strip()
        if not target_space:
            print("\n❌ Usage: /space delete <name>\n")
            return

        if target_space == "default":
            print("\n❌ Cannot delete the default space\n")
            return

        if target_space not in list_spaces():
            print(f"\n❌ Space '{target_space}' does not exist\n")
            return

        # Confirm deletion
        confirm = input(
            f"Are you sure you want to delete space '{target_space}' and all its data? (yes/no): "
        )
        if confirm.lower() not in ["yes", "y"]:
            print("\n❌ Deletion cancelled\n")
            return

        if delete_space(target_space):
            print(f"\n✅ Deleted space: {target_space}\n")
        else:
            print(f"\n❌ Failed to delete space: {target_space}\n")

    else:
        print(f"\n❌ Unknown space command: {space_cmd}")
        print("Use '/space' for help\n")


def handle_export_command(format_type: str = "json"):
    """Handle /export command to save conversation history."""
    if not conversation_history:
        print("\n📝 No conversation history to export.\n")
        return

    # Determine export format
    format_type = format_type.lower().strip()
    if format_type not in ["json", "markdown", "md"]:
        print(f"\n❌ Unsupported format: {format_type}")
        print("Supported formats: json, markdown (md)\n")
        return

    # Generate filename with timestamp
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_export_{timestamp}.{
        format_type if format_type != 'markdown' else 'md'
    }"

    try:
        if format_type == "json":
            # Export as JSON
            import json

            export_data: dict = {
                "export_timestamp": datetime.now().isoformat(),
                "total_messages": len(conversation_history),
                "messages": [],
            }

            for i, msg in enumerate(conversation_history):
                msg_type = type(msg).__name__.replace("Message", "").lower()
                export_data["messages"].append(
                    {
                        "index": i + 1,
                        "type": msg_type,
                        "content": str(msg.content),
                        "timestamp": getattr(
                            msg, "timestamp", datetime.now().isoformat()
                        )
                        if hasattr(msg, "timestamp")
                        else datetime.now().isoformat(),
                    }
                )

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

        else:  # markdown
            # Export as Markdown
            with open(filename, "w", encoding="utf-8") as f:
                f.write("# AI Assistant Conversation Export\n\n")
                f.write(
                    f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                f.write(f"**Total Messages:** {len(conversation_history)}\n\n")
                f.write("---\n\n")

                for i, msg in enumerate(conversation_history):
                    msg_type = type(msg).__name__.replace("Message", "")
                    content = str(msg.content)

                    # Format based on message type
                    if msg_type == "Human":
                        f.write(f"## User Message {i + 1}\n\n{content}\n\n")
                    elif msg_type == "AI":
                        f.write(f"## AI Response {i + 1}\n\n{content}\n\n")
                    elif msg_type == "System":
                        f.write(f"### System Message {i + 1}\n\n*{content}*\n\n")
                    else:
                        f.write(f"## {msg_type} Message {i + 1}\n\n{content}\n\n")

                    f.write("---\n\n")

        print(f"\n✅ Conversation exported to: {filename}")
        print(f"📊 Messages exported: {len(conversation_history)}")
        print(f"📄 Format: {format_type}\n")

    except Exception as e:
        print(f"\n❌ Failed to export conversation: {e}\n")


def initialize_llm():
    """Initialize LLM with tool calling support."""
    global llm
    try:
        from pydantic import SecretStr

        llm = ChatOpenAI(
            base_url=cast(str, LM_STUDIO_BASE_URL),
            api_key=SecretStr(cast(str, LM_STUDIO_API_KEY)),
            model=cast(str, MODEL_NAME),
            temperature=TEMPERATURE,
        )
        from src.tools import ToolRegistry

        tool_definitions = ToolRegistry.get_definitions()
        llm = llm.bind_tools(tool_definitions)
        print(f"✅ Connected to LLM: {MODEL_NAME} (with {len(tool_definitions)} tools)")
        get_context().llm = llm
        return True
    except Exception as e:
        print(f"❌ Failed to initialize LLM: {e}")
        return False


def initialize_vectordb():
    """Initialize ChromaDB and embeddings."""
    global vectorstore, embeddings, chroma_client
    try:
        from chromadb import HttpClient
        from langchain_chroma import Chroma
        from langchain_ollama import OllamaEmbeddings
        from typing import Any

        class CustomOllamaEmbeddings(OllamaEmbeddings):
            @property
            def _default_params(self) -> dict[str, Any]:
                return {
                    "num_ctx": self.num_ctx,
                    "num_gpu": self.num_gpu,
                    "num_thread": self.num_thread,
                    "keep_alive": self.keep_alive,
                }

        chroma_client = HttpClient(host=cast(str, CHROMA_HOST), port=CHROMA_PORT)
        embeddings = CustomOllamaEmbeddings(
            model=cast(str, EMBEDDING_MODEL),
            base_url=cast(str, OLLAMA_BASE_URL),
        )

        from src.vectordb.spaces import get_space_collection_name

        coll_name = get_space_collection_name(CURRENT_SPACE)

        vectorstore = Chroma(
            client=chroma_client,
            collection_name=coll_name,
            embedding_function=embeddings,
        )
        print(f"✅ Connected to vector database ({coll_name})")

        # Update context
        ctx = get_context()
        ctx.vectorstore = vectorstore
        ctx.embeddings = embeddings
        ctx.chroma_client = chroma_client
        return True
    except Exception as e:
        print(f"❌ ChromaDB connection failed: {e}")
        return False


def initialize_user_memory():
    """Initialize Mem0 personalization."""
    global user_memory
    if not MEM0_AVAILABLE:
        return True
    try:
        from mem0 import Memory

        mem0_config = {
            "llm": {
                "provider": "lmstudio",
                "config": {
                    "model": MODEL_NAME,
                    "lmstudio_base_url": LM_STUDIO_BASE_URL,
                    "api_key": LM_STUDIO_API_KEY,
                    "temperature": 0.1,
                    "lmstudio_response_format": {
                        "type": "json_schema",
                        "json_schema": {
                            "schema": {
                                "type": "object",
                                "additionalProperties": True,
                            }
                        },
                    },
                },
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": EMBEDDING_MODEL,
                    "ollama_base_url": OLLAMA_BASE_URL,
                },
            },
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "mem0_user_prefs",
                    "host": CHROMA_HOST,
                    "port": CHROMA_PORT,
                },
            },
        }
        user_memory = Memory.from_config(mem0_config)
        get_context().user_memory = user_memory
        print("✅ Connected to Mem0 (User Personalized Memory)")
        return True
    except Exception as e:
        print(f"⚠️ Failed to initialize Mem0: {e}")
        return False


def initialize_application():
    """
    Initialize all application components required for operation.
    """
    if not initialize_llm():
        return False

    if not initialize_vectordb():
        # ChromaDB is critical for learning, but maybe not for basic chat?
        # The original code exited on failure.
        sys.exit(1)

    # Database initialization (uses storage module)
    from src.storage.database import initialize_database

    db_conn, db_lock = initialize_database()
    if not db_conn:
        print("Falling back to non-persistent mode")

    # Load conversation history
    conversation_history[:] = load_memory()  # type: ignore[assignment]
    get_context().conversation_history = conversation_history

    # Personalization
    initialize_user_memory()

    return True


# show_welcome function moved to src.core.display


# chunk_text function moved to src.core.utils


# =============================================================================
# TOOLS MODULE (registry infrastructure in src/tools/)
# =============================================================================

# Import tool registry for future migration

# Note: Tool executors remain in this file for now.
# They can be incrementally migrated to src/tools/executors/ using:
#   @register_tool("read_file", READ_FILE_DEFINITION)
#   def execute_read_file(file_path: str) -> dict: ...

# =============================================================================
# TOOL SYSTEM (extracted to src/tools/)
# =============================================================================
# Tool definitions and executors have been moved to src/tools/executors/
# Import ToolRegistry to access registered tools

# Backwards compatibility for tests and main loop
execute_tool_call = ToolRegistry.execute_tool_call


# =============================================================================
# CHAT MODULE (infrastructure in src/chat/)
# =============================================================================
# Note: The main() function remains here but can be incrementally migrated
# to src/chat/loop.py, src/chat/message_handler.py, etc.


def main():  # type: ignore[reportGeneralTypeIssues]
    """
    Main entry point - now delegates to modular chat loop.

    The complex chat loop logic has been extracted to src.core.chat_loop
    for better maintainability and modularity.
    """
    # Initialize application components (matches old behavior expected by tests)
    if not initialize_application():
        return False  # Exit if initialization failed (matches test expectations)

    # Run the main chat loop
    from src.core.chat_loop import run_main_chat_loop

    return run_main_chat_loop()


# Standard Python entry point - only execute chat loop when run directly
# Prevents execution when imported as a module by other scripts
# This ensures the chat interface only starts when the script is run standalone
if __name__ == "__main__":
    # Initialize application first
    if not initialize_application():
        exit(1)  # Exit if initialization failed

    # Run the main chat loop
    from src.core.chat_loop import run_main_chat_loop

    success = run_main_chat_loop()
    exit(0 if success else 1)


def execute_learn_url(url: str) -> dict:
    """
    Fetch and learn content from a URL using Docling.

    This function leverages Docling's ability to fetch and parse web pages into structured markdown,
    which is then added to the knowledge base.
    """
    try:
        from docling.document_converter import DocumentConverter
        from langchain_core.documents import Document
        from datetime import datetime

        # Initialize converter
        converter = DocumentConverter()

        # Convert web content directly from URL
        # Docling handles fetching and HTML-to-Markdown conversion
        result = converter.convert(url)
        content = result.document.export_to_markdown()

        # Create metadata
        title = "Web Page"  # Docling might expose title, but safe default
        if hasattr(result.document, "title") and getattr(
            result.document, "title", None
        ):
            title = getattr(result.document, "title")

        doc = Document(
            page_content=content,
            metadata={
                "source": url,
                "title": title,
                "type": "web_page",
                "added_at": datetime.now().isoformat(),
            },
        )

        # Add to vector store
        if vectorstore:
            # Use the existing logic or direct add
            vectorstore.add_documents([doc])

            # Periodic cleanup logic from handle_learn_command
            global operation_count
            operation_count += 1
            if operation_count % 50 == 0:
                cleanup_memory()

            return {"success": True, "title": title, "url": url, "length": len(content)}
        else:
            return {"error": "Vector database not initialized"}

    except ImportError:
        return {"error": "docling library not installed"}
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# RATE LIMITING MODULE (extracted to src/security/rate_limiter.py)
# =============================================================================
# RateLimitError and RateLimiter are now imported from src.security
