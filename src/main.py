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
AI Assistant Chat Application v0.3.0

This application provides an intelligent conversational AI assistant with advanced learning
and document processing capabilities. Built specifically for the qwen3-vl-30b + qwen3-embedding + ChromaDB stack.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Core LangChain components for AI chat functionality


# Command handlers - import to trigger auto-registration via decorators
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
    load_embedding_cache,
    load_query_cache,
    save_query_cache,
    cleanup_memory,
)


from src.vectordb import get_space_collection_name


from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
from src.core.context import get_context
from src.core.config import get_config, get_logger

# Standard library imports (kept for backwards compatibility and test mocking)
from datetime import datetime  # Timestamps for learned knowledge

# Type hints for better code clarity
from typing import Optional


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


def execute_learn_url(url: str) -> dict:
    """
    Fetch and learn content from a URL using Docling.

    This function leverages Docling's ability to fetch and parse web pages into structured markdown,
    which is then added to the knowledge base.
    """
    try:
        from docling.document_converter import DocumentConverter
        from langchain_core.documents import Document

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


def initialize_llm():
    """Initialize the LLM connection."""
    try:
        ctx = get_context()
        if ctx.llm is None:
            ctx.llm = get_llm()
        return True
    except Exception:
        return False


def initialize_vectordb():
    """Initialize the vector database connection."""
    try:
        ctx = get_context()
        if ctx.vectorstore is None:
            ctx.vectorstore = get_vectorstore()
        return True
    except Exception:
        return False


def initialize_user_memory():
    """Initialize user memory system."""
    try:
        ctx = get_context()
        if ctx.user_memory is None:
            # Initialize Mem0 if available
            pass
        return True
    except Exception:
        return False


def initialize_application() -> bool:
    """Initialize the entire application."""
    try:
        initialize_llm()
        initialize_vectordb()
        initialize_user_memory()
        return True
    except Exception:
        return False


def handle_populate_command(dir_path: str):
    """Handle /populate command for bulk learning."""
    # Implementation for bulk importing codebases
    pass


def run_main_chat_loop() -> bool:
    """Run the main chat loop."""
    # Implementation would be the main loop
    return True


def main():
    """Main entry point."""
    if initialize_application():
        return run_main_chat_loop()
    return False


# =============================================================================
# RATE LIMITING MODULE (extracted to src/security/rate_limiter.py)
# =============================================================================
# RateLimitError and RateLimiter are now imported from src.security
