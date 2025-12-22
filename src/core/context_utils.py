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
Context Utilities - Shared functions for knowledge base operations.

This module provides reusable utilities for interacting with the ChromaDB
vector database, including context retrieval and document addition.
These functions are used by both command handlers and tool executors.
"""

import logging
from typing import Optional
from datetime import datetime
import requests

from langchain_core.documents import Document
from src.core.config import get_config
from src.core.context import get_context


logger = logging.getLogger(__name__)

# HTTP session for API calls (with retry logic)
_api_session: Optional[requests.Session] = None


def _get_api_session() -> requests.Session:
    """Get or create HTTP session with retry logic."""
    global _api_session
    if _api_session is None:
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        _api_session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy, pool_connections=10, pool_maxsize=20
        )
        _api_session.mount("http://", adapter)
        _api_session.mount("https://", adapter)
    return _api_session


def get_relevant_context(
    query: str, k: int = 3, space_name: Optional[str] = None
) -> str:
    """
    Get relevant context from vector database with caching.

    Args:
        query: Search query string
        k: Number of results to return (default: 3)
        space_name: Space to search in (default: current space)

    Returns:
        Formatted context string with relevant documents, or empty string
    """
    ctx = get_context()
    config = get_config()

    # Use current space if not specified
    if space_name is None:
        space_name = ctx.current_space

    # Check query cache first
    cache_key = f"{space_name}:{query}:{k}"
    if cache_key in ctx.query_cache:
        cached_results = ctx.query_cache[cache_key]
        if cached_results:
            context = "\n\n".join(
                [f"From knowledge base:\n{doc}" for doc in cached_results]
            )
            return f"\n\nRelevant context:\n{context}\n\n"

    # Return empty context if vector database not available
    if ctx.vectorstore is None:
        return ""

    try:
        # Generate embedding for the query
        try:
            if ctx.embeddings is None:
                logger.warning("Embeddings not initialized for context retrieval")
                return ""

            query_embedding = ctx.embeddings.embed_query(query)
        except (AttributeError, NameError, Exception) as e:
            logger.warning(f"Embeddings not available for context retrieval: {e}")
            return ""

        # Find collection for the specified space
        from src.vectordb.spaces import get_space_collection_name
        collection_id = None
        collection_name = get_space_collection_name(space_name)
        api_session = None

        # Try to find the collection by name
        try:
            list_url = f"http://{config.chroma_host}:{config.chroma_port}/api/v2/tenants/default_tenant/databases/default_database/collections"
            api_session = _get_api_session()
            list_response = api_session.get(list_url, timeout=10)
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

        if api_session is None:
            logger.warning("API session not initialized for context retrieval")
            return ""

        # ChromaDB v2 API endpoint for querying
        base_url = f"http://{config.chroma_host}:{config.chroma_port}/api/v2"
        query_url = f"{base_url}/tenants/default_tenant/databases/default_database/collections/{collection_id}/query"

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
            ctx.query_cache[cache_key] = docs
            if len(ctx.query_cache) % 50 == 0:
                _save_query_cache()

            context = "\n\n".join([f"From knowledge base:\n{doc}" for doc in docs])
            return f"\n\nRelevant context:\n{context}\n\n"
        else:
            logger.error(f"ChromaDB query failed: {response.status_code}")
            return ""

    except Exception as e:
        # Log error but don't crash - AI can still respond without context
        logger.warning(f"Failed to retrieve context: {e}")
        return ""


def add_to_knowledge_base(content: str, metadata: Optional[dict] = None) -> bool:
    """
    Add information to the current space's knowledge base.

    Args:
        content: Text content to store
        metadata: Optional metadata dict (default: {"source": "user-input"})

    Returns:
        True if successful, False otherwise
    """
    ctx = get_context()
    config = get_config()

    # Check if vector database is available
    if ctx.vectorstore is None:
        logger.error("Vector database not available for learning")
        return False

    if ctx.embeddings is None:
        logger.error("Embeddings not available for learning")
        return False

    if not content:
        logger.error("Cannot add empty content to knowledge base")
        return False

    try:
        # Set default metadata if not provided
        if metadata is None:
            metadata = {
                "source": "user-input",
                "added_at": str(datetime.now()),
            }

        # Create document
        doc = Document(page_content=content, metadata=metadata)

        # Generate embeddings using Ollama
        try:
            embeddings_result = ctx.embeddings.embed_documents([doc.page_content])
            if not embeddings_result or len(embeddings_result) == 0:
                logger.error("Failed to generate embeddings")
                return False

            embedding_vector = embeddings_result[0]

            # Get collection for current space
            from src.vectordb.spaces import get_space_collection_name
            collection_name = get_space_collection_name(ctx.current_space)
            collection_id = None

            # Find or create the collection
            api_session = _get_api_session()
            list_url = f"http://{config.chroma_host}:{config.chroma_port}/api/v2/tenants/default_tenant/databases/default_database/collections"
            list_response = api_session.get(list_url, timeout=10)

            if list_response.status_code == 200:
                collections = list_response.json()
                for coll in collections:
                    if coll.get("name") == collection_name:
                        collection_id = coll.get("id")
                        break

            # If collection doesn't exist, create it
            if not collection_id:
                create_url = f"http://{config.chroma_host}:{config.chroma_port}/api/v2/tenants/default_tenant/databases/default_database/collections"
                create_payload = {"name": collection_name}
                create_response = api_session.post(
                    create_url, json=create_payload, timeout=10
                )
                if create_response.status_code == 201:
                    collection_id = create_response.json().get("id")
                    if config.verbose_logging:
                        logger.info(
                            f"Created new collection for space {ctx.current_space}: {collection_name}"
                        )
                else:
                    logger.error(
                        f"Failed to create collection: HTTP {create_response.status_code}"
                    )
                    return False

            # Add document to the space's collection
            add_url = (
                f"http://{config.chroma_host}:{config.chroma_port}/api/v2/"
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
                if config.verbose_logging:
                    logger.info(
                        f"Document added successfully to space {ctx.current_space}: {doc_id}"
                    )
                return True
            else:
                logger.error(
                    f"Failed to add document to space {ctx.current_space}: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"Error with direct ChromaDB v2 API: {e}")
            # Fallback to LangChain method
            try:
                ctx.vectorstore.add_documents([doc])
                if config.verbose_logging:
                    logger.debug("Used LangChain fallback for document addition")
                return True
            except Exception as fallback_e:
                logger.error(f"LangChain fallback also failed: {fallback_e}")
                return False

    except Exception as e:
        logger.error(f"Failed to add to knowledge base: {e}")
        return False


def _save_query_cache():
    """Save query cache to disk."""
    try:
        from src.storage.cache import save_query_cache

        save_query_cache()
    except Exception as e:
        logger.warning(f"Failed to save query cache: {e}")


__all__ = ["get_relevant_context", "add_to_knowledge_base"]
