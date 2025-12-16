"""
Core module for DevAssist.

This module provides core application infrastructure including:
- Configuration management (environment loading, validation)
- Application context (dependency injection container)
- Shared utilities and constants
"""

from src.core.config import Config, get_config, APP_VERSION
from src.core.context import (
    ApplicationContext,
    get_context,
    set_context,
    reset_context,
    # Backwards-compatible accessors
    get_llm,
    set_llm,
    get_vectorstore,
    set_vectorstore,
    get_embeddings,
    set_embeddings,
    get_chroma_client,
    set_chroma_client,
    get_user_memory,
    set_user_memory,
    get_db_conn,
    set_db_conn,
    get_db_lock,
    set_db_lock,
    get_conversation_history,
    set_conversation_history,
    get_context_mode,
    set_context_mode,
    get_learning_mode,
    set_learning_mode,
    get_current_space,
    set_current_space,
    get_embedding_cache,
    get_query_cache,
)

__all__ = [
    # Config
    "Config",
    "get_config",
    "APP_VERSION",
    # Context
    "ApplicationContext",
    "get_context",
    "set_context",
    "reset_context",
    # Accessors
    "get_llm",
    "set_llm",
    "get_vectorstore",
    "set_vectorstore",
    "get_embeddings",
    "set_embeddings",
    "get_chroma_client",
    "set_chroma_client",
    "get_user_memory",
    "set_user_memory",
    "get_db_conn",
    "set_db_conn",
    "get_db_lock",
    "set_db_lock",
    "get_conversation_history",
    "set_conversation_history",
    "get_context_mode",
    "set_context_mode",
    "get_learning_mode",
    "set_learning_mode",
    "get_current_space",
    "set_current_space",
    "get_embedding_cache",
    "get_query_cache",
]
