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
Application context for DevAssist.

This module provides a centralized dependency injection container that replaces
global variables. All application state is stored in the ApplicationContext
dataclass, enabling:

1. **Testability**: Easy to create mock contexts for testing
2. **Explicit dependencies**: Functions declare what they need
3. **Thread safety**: State is contained, not scattered across modules
4. **Initialization control**: Clear startup sequence

Usage:
    from src.core.context import get_context, initialize_context

    # At startup
    ctx = initialize_context()

    # In functions that need application state
    ctx = get_context()
    llm = ctx.llm
    vectorstore = ctx.vectorstore
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import threading


@dataclass
class ApplicationContext:
    """
    Centralized application state container.

    This replaces all global variables with a single, manageable object.
    All fields have sensible defaults, allowing partial initialization
    for testing.

    Attributes:
        # Core AI services
        llm: LangChain ChatOpenAI instance
        vectorstore: ChromaDB vector store
        embeddings: Ollama embeddings instance
        chroma_client: ChromaDB HTTP client
        user_memory: Mem0 personalized memory instance

        # Database
        db_conn: SQLite connection
        db_lock: Threading lock for database operations

        # Conversation state
        conversation_history: List of chat messages

        # AI behavior modes
        context_mode: "auto", "on", or "off"
        learning_mode: "normal", "strict", or "off"
        current_space: Current workspace name

        # Caches
        embedding_cache: Dict mapping text to embedding vectors
        query_cache: Dict mapping queries to cached results
        operation_count: Counter for cleanup scheduling
    """

    # Core AI services (initialized during startup)
    llm: Optional[Any] = None
    vectorstore: Optional[Any] = None
    embeddings: Optional[Any] = None
    chroma_client: Optional[Any] = None
    user_memory: Optional[Any] = None

    # Database (initialized during startup)
    db_conn: Optional[Any] = None
    db_lock: Optional[threading.Lock] = None

    # Conversation state
    conversation_history: List[Any] = field(default_factory=list)

    # AI behavior modes (configurable via slash commands)
    context_mode: str = "auto"  # "auto", "on", "off"
    learning_mode: str = "normal"  # "normal", "strict", "off"
    current_space: str = "default"  # Current workspace name

    # Caches
    embedding_cache: Dict[str, List[float]] = field(default_factory=dict)
    query_cache: Dict[str, List[str]] = field(default_factory=dict)
    operation_count: int = 0

    def reset_caches(self) -> None:
        """Clear all caches."""
        self.embedding_cache.clear()
        self.query_cache.clear()

    def reset_conversation(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()


# Thread-safe singleton
_context: Optional[ApplicationContext] = None
_context_lock = threading.Lock()


def get_context() -> ApplicationContext:
    """
    Get the global application context singleton.

    Creates the context on first call. Thread-safe.

    Returns:
        ApplicationContext: The global application context

    Example:
        ctx = get_context()
        if ctx.llm is not None:
            response = ctx.llm.invoke(messages)
    """
    global _context
    if _context is None:
        with _context_lock:
            if _context is None:
                _context = ApplicationContext()
    return _context


def set_context(ctx: ApplicationContext) -> None:
    """
    Replace the global context. Useful for testing.

    Args:
        ctx: New application context to use
    """
    global _context
    with _context_lock:
        _context = ctx


def reset_context() -> None:
    """
    Reset the global context to None. Useful for testing.
    """
    global _context
    with _context_lock:
        _context = None


# =============================================================================
# BACKWARDS COMPATIBILITY ACCESSORS
# =============================================================================
# These functions provide backwards-compatible access to context state.
# They allow existing code that uses `from src.main import llm` pattern
# to continue working during the migration.


def get_llm() -> Optional[Any]:
    """Get the LLM instance from context."""
    return get_context().llm


def set_llm(value: Any) -> None:
    """Set the LLM instance in context."""
    get_context().llm = value


def get_vectorstore() -> Optional[Any]:
    """Get the vectorstore instance from context."""
    return get_context().vectorstore


def set_vectorstore(value: Any) -> None:
    """Set the vectorstore instance in context."""
    get_context().vectorstore = value


def get_embeddings() -> Optional[Any]:
    """Get the embeddings instance from context."""
    return get_context().embeddings


def set_embeddings(value: Any) -> None:
    """Set the embeddings instance in context."""
    get_context().embeddings = value


def get_chroma_client() -> Optional[Any]:
    """Get the ChromaDB client from context."""
    return get_context().chroma_client


def set_chroma_client(value: Any) -> None:
    """Set the ChromaDB client in context."""
    get_context().chroma_client = value


def get_user_memory() -> Optional[Any]:
    """Get the user memory (Mem0) instance from context."""
    return get_context().user_memory


def set_user_memory(value: Any) -> None:
    """Set the user memory (Mem0) instance in context."""
    get_context().user_memory = value


def get_db_conn() -> Optional[Any]:
    """Get the database connection from context."""
    return get_context().db_conn


def set_db_conn(value: Any) -> None:
    """Set the database connection in context."""
    get_context().db_conn = value


def get_db_lock() -> Optional[threading.Lock]:
    """Get the database lock from context."""
    return get_context().db_lock


def set_db_lock(value: threading.Lock) -> None:
    """Set the database lock in context."""
    get_context().db_lock = value


def get_conversation_history() -> List[Any]:
    """Get the conversation history from context."""
    return get_context().conversation_history


def set_conversation_history(value: List[Any]) -> None:
    """Set the conversation history in context."""
    get_context().conversation_history = value


def get_context_mode() -> str:
    """Get the context mode from context."""
    return get_context().context_mode


def set_context_mode(value: str) -> None:
    """Set the context mode in context."""
    get_context().context_mode = value


def get_learning_mode() -> str:
    """Get the learning mode from context."""
    return get_context().learning_mode


def set_learning_mode(value: str) -> None:
    """Set the learning mode in context."""
    get_context().learning_mode = value


def get_current_space() -> str:
    """Get the current space from context."""
    return get_context().current_space


def set_current_space(value: str) -> None:
    """Set the current space in context."""
    get_context().current_space = value


def get_embedding_cache() -> Dict[str, List[float]]:
    """Get the embedding cache from context."""
    return get_context().embedding_cache


def get_query_cache() -> Dict[str, List[str]]:
    """Get the query cache from context."""
    return get_context().query_cache
