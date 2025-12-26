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
# Standard library imports
import sys
from datetime import datetime

# Third-party imports
import requests  # noqa: F401
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Application imports
from src.core.config import get_config, get_logger
from src.core.context import get_context, set_mcp_client
from src.mcp.client import MCPClient
from src.core.chat_loop import ChatLoop
from src.commands import CommandRegistry
from src.commands.handlers import (  # noqa: F401 (side-effect imports for decorator registration)
    config_commands,
    database_commands,
    export_commands,
    file_commands,
    git_commands,
    help_commands,
    learning_commands,
    mcp_commands,
    memory_commands,
    space_commands,
    system_commands,
)
from src.storage import (
    initialize_database,

    load_embedding_cache,
    load_query_cache,
    cleanup_memory,
)
from src.core.context_utils import get_relevant_context  # noqa: F401 Backwards compatibility

# Setup logging FIRST (before any other imports that use logging)
logger = get_logger()


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
# Memory is now loaded in initialize_user_memory() to ensure tools are ready
# _initial_history = load_memory()
# get_context().conversation_history = _initial_history
# conversation_history = get_context().conversation_history

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


def initialize_llm() -> bool:
    """Initialize LLM connection."""
    try:
        _config = get_config()
        if logger.handlers:
            logger.info("🧠 Initializing LLM connection...")
            logger.debug("🧠 Initializing LLM connection...")
            logger.debug(f"   LM Studio URL: {_config.lm_studio_url}")
            logger.debug(f"   Model: {_config.model_name}")
            logger.debug(f"   Temperature: {_config.temperature}")
        from langchain_openai import ChatOpenAI
        from pydantic import SecretStr

        ctx = get_context()
        if ctx.llm is None:
            logger.debug("   Creating ChatOpenAI instance...")
            logger.debug(f"   Base URL: {_config.lm_studio_url}")
            logger.debug("   API Key: ***")  # Don't log the actual key
            logger.debug(f"   Model: {_config.model_name}")
            logger.debug(f"   Temperature: {_config.temperature}")
            ctx.llm = ChatOpenAI(
                base_url=_config.lm_studio_url,
                api_key=SecretStr(LM_STUDIO_API_KEY),
                model=_config.model_name,
                temperature=_config.temperature,
            )
            logger.debug("   LLM instance created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        return False


def initialize_vectordb():
    """Initialize vector database connection."""
    try:
        config = get_config()
        if logger.handlers:
            logger.info("🌐 Initializing ChromaDB vector database...")
            logger.debug("🌐 Initializing ChromaDB vector database...")
            logger.debug(f"   ChromaDB Host: {config.chroma_host}")
            logger.debug(f"   ChromaDB Port: {config.chroma_port}")
            logger.info("🧮 Initializing Ollama embeddings...")
            logger.debug("🧮 Initializing Ollama embeddings...")
            logger.debug(f"   Ollama URL: {config.ollama_base_url}")
            logger.debug(f"   Embedding Model: {config.embedding_model}")
            logger.debug("   Creating OllamaEmbeddings instance...")
        from langchain_ollama import OllamaEmbeddings

        ctx = get_context()
        if ctx.embeddings is None:
            ctx.embeddings = OllamaEmbeddings(
                model=config.embedding_model,
                base_url=config.ollama_base_url,
            )
            logger.debug("   OllamaEmbeddings instance created successfully")

        # Initialize Vector Store
        from langchain_chroma import Chroma
        import chromadb

        if ctx.vectorstore is None and ctx.embeddings:
            # Use native HttpClient for LangChain compatibility
            # The custom wrapper in src.vectordb.client is mainly for direct API calls,
            # but LangChain expects the official client structure.
            native_client = chromadb.HttpClient(
                host=config.chroma_host,
                port=config.chroma_port
            )

            ctx.vectorstore = Chroma(
                client=native_client,
                collection_name="devassist_knowledge",
                embedding_function=ctx.embeddings,
            )
            logger.debug("   Vector Store initialized successfully")

        return True
    except Exception as e:
        logger.error(f"Failed to initialize vector database: {e}")
        return False


def initialize_user_memory():
    """Initialize user memory system (SQLite + Mem0 local)."""
    try:
        if logger.handlers:
            logger.info("💾 Loading conversation history...")
            logger.debug("🧠 Initializing Mem0 local personalized memory...")

        _config = get_config()
        logger.debug(f"   ChromaDB Host: {_config.chroma_host}:{_config.chroma_port}")

        from src.storage.mem0_local import initialize_mem0_local

        mem0_status = initialize_mem0_local()

        # Load conversation history AFTER tools are initialized
        from src.storage.memory import load_memory
        ctx = get_context()
        ctx.conversation_history = load_memory()

        if isinstance(mem0_status, dict):
            logger.debug(
                f"   Mem0 tables: {mem0_status.get('mem0_preferences', '❌')}/{mem0_status.get('mem0_memories', '❌')}"
            )
            count = len(ctx.conversation_history)
            logger.info(f"💾 Loaded SQLite conversation history with {count} messages")
            logger.info("🧠 Mem0 local personalized memory initialized successfully")
        else:
            logger.error(f"Failed to initialize Mem0 local: {mem0_status}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize user memory: {e}")
        logger.warning("⚠️ Memory load failed. Initializing with fresh System Prompt fallback.")

        # Fallback: Construct system prompt manually if DB fails
        from langchain_core.messages import SystemMessage
        from src.tools.registry import ToolRegistry
        from src.core.constants import SYSTEM_PROMPT
        import json

        tool_defs = ToolRegistry.get_definitions()
        tool_json = json.dumps(tool_defs, indent=2)

        # Verify we are using the authoritative prompt
        fallback_content = SYSTEM_PROMPT + f"\n\nAVAILABLE TOOLS:\n{tool_json}\n"
        ctx = get_context()
        ctx.conversation_history = [SystemMessage(content=fallback_content)]
        return True


def initialize_mcp() -> bool:
    """Initialize MCP client."""
    try:
        ctx = get_context()
        if ctx.mcp_client is None:
            logger.info("Initializing MCP Client...")
            client = MCPClient()
            client.initialize_sync()
            set_mcp_client(client)
        return True
    except Exception as e:
        logger.warning(f"Failed to initialize MCP: {e}")
        return False


def initialize_application() -> bool:
    """Initialize the entire application."""
    try:
        initialize_tools()  # Tools must be initialized first for System Prompt injection
        initialize_llm()
        initialize_vectordb()
        initialize_user_memory()
        initialize_mcp()
        return True
    except Exception:
        return False


def initialize_tools() -> None:
    """Initialize all AI tools by importing tool executors."""
    from src.tools import ToolRegistry

    logger.info(
        f"🛠️ Tool Registry initialized with {len(ToolRegistry._tools)} tools available"
    )


def handle_populate_command(dir_path: str):
    """Handle /populate command for bulk learning."""
    # Implementation for bulk importing codebases
    pass


def run_main_chat_loop() -> bool:
    """Run the main interactive chat loop."""
    print("\n" + "=" * 60)
    print("      AI Assistant Chat Interface v0.3.0")
    print("=" * 60)
    print(f"📍 Python: {sys.version.split()[0]} | Model: {_config.model_name}")
    print(f"🌐 Space: {get_context().current_space}")
    print("\nHello! I'm ready to help you. Type /help for commands.")
    print("Type 'quit', 'exit', or 'q' to exit.\n")

    chat_orchestrator = ChatLoop()

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Check for exit commands
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n👋 Goodbye! Your conversation has been saved.\n")
                break

            # Handle slash commands
            logger.info(f"📋 Main loop: Processing input: '{user_input}'")
            if user_input.startswith("/"):
                logger.info("📋 Main loop: Detected slash command, dispatching...")
                handle_slash_command(user_input)
                continue

            # Process regular message through agentic loop
            print("\n🤖 AI Assistant: ", end="", flush=True)
            response = chat_orchestrator.run_iteration(user_input)
            print(f"{response}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        except EOFError:
            print("\n\n👋 Connection closed. Goodbye!\n")
            break
        except Exception as e:
            logger.error(f"Error in chat loop: {e}")
            print(f"\n❌ Error: {e}\n")

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
