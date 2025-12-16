"""
Vector database module for DevAssist.

This module provides ChromaDB integration including:
- Unified client wrapper eliminating API duplication
- Space/collection management
- Context retrieval for RAG
"""

from src.vectordb.client import ChromaDBClient, get_chromadb_client
from src.vectordb.spaces import (
    get_space_collection_name,
    ensure_space_collection,
    list_spaces,
    delete_space,
    switch_space,
    save_current_space,
    load_current_space,
)

__all__ = [
    # Client
    "ChromaDBClient",
    "get_chromadb_client",
    # Spaces
    "get_space_collection_name",
    "ensure_space_collection",
    "list_spaces",
    "delete_space",
    "switch_space",
    "save_current_space",
    "load_current_space",
]
