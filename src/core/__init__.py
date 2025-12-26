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
from src.core.context_utils import get_relevant_context, add_to_knowledge_base
from src.core.utils import (
    chunk_text,
    validate_file_path,
    get_file_size_info,
    truncate_content,
)

# Display functions removed to avoid circular imports

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
    # Utilities
    "get_relevant_context",
    "add_to_knowledge_base",
    "chunk_text",
    "validate_file_path",
    "get_file_size_info",
    "truncate_content",
]
