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


def _find_collection_id(collection_name: str, space_name: str) -> Optional[str]:
    """
    Find collection ID by name via ChromaDB API.

    Args:
        collection_name: Name of the collection to find
        space_name: Space name for logging context

    Returns:
        Collection ID if found, None otherwise
    """
    config = get_config()
    try:
        api_session = _get_api_session()
        list_url = f"http://{config.chroma_host}:{config.chroma_port}/api/v2/tenants/default_tenant/databases/default_database/collections"
        if config.verbose_logging:
            logger.debug(f"🔍 Finding collection for space: {space_name}")
            logger.debug(f"   API URL: {list_url}")
        list_response = api_session.get(list_url, timeout=10)
        if config.verbose_logging:
            logger.debug(f"   API Response Status: {list_response.status_code}")
        if list_response.status_code == 200:
            collections = list_response.json()
            if config.verbose_logging:
                logger.debug(f"   Found {len(collections)} collections")
            for coll in collections:
                if coll.get("name") == collection_name:
                    collection_id = coll.get("id")
                    if config.verbose_logging:
                        logger.debug(f"✅ Found collection: {collection_name} (ID: {collection_id})")
                    return collection_id
            if config.verbose_logging:
                logger.debug(f"❌ Collection {collection_name} not found in {len(collections)} collections")
    except Exception as e:
        logger.warning(f"Error finding collection for space {space_name}: {e}")
    return None


def _query_chromadb(collection_id: str, query_embedding: list, k: int) -> list:
    """
    Query ChromaDB API for similar documents.

    Args:
        collection_id: ID of the collection to query
        query_embedding: Embedding vector for the query
        k: Number of results to return

    Returns:
        List of document contents found in ChromaDB
    """
    config = get_config()
    docs = []
    try:
        base_url = f"http://{config.chroma_host}:{config.chroma_port}/api/v2"
        query_url = f"{base_url}/tenants/default_tenant/databases/default_database/collections/{collection_id}/query"
        payload = {"query_embeddings": [query_embedding], "n_results": k}

        if config.verbose_logging:
            logger.debug("🌐 Querying ChromaDB API")
            logger.debug(f"   URL: {query_url}")
            logger.debug(f"   Payload: n_results={k}, embedding_length={len(query_embedding)}")
        api_session = _get_api_session()
        response = api_session.post(query_url, json=payload, timeout=10)
        if config.verbose_logging:
            logger.debug(f"   Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if config.verbose_logging:
                logger.debug("📄 Processing ChromaDB response")
                logger.debug(f"   Response keys: {list(data.keys())}")

            if "documents" in data and data["documents"] and len(data["documents"]) > 0:
                documents = data["documents"][0]
                if config.verbose_logging:
                    logger.debug(f"   Found {len(documents)} document results")
                for i, doc_content in enumerate(documents):
                    docs.append(doc_content)
                    if config.verbose_logging:
                        logger.debug(f"   Document {i+1}: {len(doc_content)} chars - {doc_content[:50]}...")
            if config.verbose_logging:
                logger.debug(f"📄 Retrieved {len(docs)} documents from ChromaDB")
        else:
            logger.error(f"ChromaDB query failed: {response.status_code}")
            if config.verbose_logging:
                logger.debug(f"   Response content: {response.text[:200]}...")
    except Exception as e:
        logger.warning(f"Failed to query ChromaDB: {e}")
    return docs


def _format_context_results(docs: list) -> str:
    """
    Format document results for LLM context.

    Args:
        docs: List of document contents

    Returns:
        Formatted context string, or empty string if no documents
    """
    config = get_config()
    if not docs:
        if config.verbose_logging:
            logger.debug("📄 No documents to format")
        return ""

    context = "\n\n".join([f"From knowledge base:\n{doc}" for doc in docs])
    if config.verbose_logging:
        logger.debug(f"✅ Formatted context ({len(context)} chars)")
        logger.debug(f"   Context preview: {context[:100]}...")
    return f"\n\nRelevant context:\n{context}\n\n"


def _check_cache_for_context(cache_key: str) -> Optional[str]:
    """
    Check query cache and return formatted results if hit.

    Args:
        cache_key: Cache key for query

    Returns:
        Formatted context string if cache hit, None if cache miss
    """
    ctx = get_context()
    config = get_config()

    if config.verbose_logging:
        logger.debug(f"💾 Checking cache with key: {cache_key}")

    if cache_key in ctx.query_cache:
        cached_results = ctx.query_cache[cache_key]
        if cached_results:
            if config.verbose_logging:
                logger.debug(f"💾 Cache hit: {len(cached_results)} cached results found")
                for i, result in enumerate(cached_results):
                    logger.debug(f"   Result {i+1}: {result[:100]}...")
            return _format_context_results(cached_results)

    if config.verbose_logging:
        logger.debug("💾 Cache miss, proceeding with vector database query")
    return None


def _generate_query_embedding(query: str) -> Optional[list]:
    """
    Generate embedding vector for a search query.

    Args:
        query: Search query string

    Returns:
        Embedding vector or None if generation fails
    """
    ctx = get_context()
    config = get_config()

    if ctx.embeddings is None:
        logger.warning("Embeddings not initialized for context retrieval")
        return None

    if config.verbose_logging:
        logger.debug("🧮 Initializing embedding generation for query")
        logger.debug(f"   Query length: {len(query)} characters")

    try:
        query_embedding = ctx.embeddings.embed_query(query)
        if config.verbose_logging:
            logger.debug(f"✅ Generated embedding vector (length: {len(query_embedding)})")
            logger.debug(f"   First 5 values: {query_embedding[:5] if len(query_embedding) >= 5 else query_embedding}")
        return query_embedding
    except Exception as e:
        logger.warning(f"Failed to generate query embedding: {e}")
        return None


def _retrieve_and_cache_context(
    query_embedding: list, collection_id: str, k: int, cache_key: str, space_name: str
) -> str:
    """
    Query ChromaDB and cache results.

    Args:
        query_embedding: Embedding vector for query
        collection_id: ChromaDB collection ID
        k: Number of results to return
        cache_key: Cache key for storing results
        space_name: Space name for logging

    Returns:
        Formatted context string
    """
    ctx = get_context()
    config = get_config()

    # Query the database
    docs = _query_chromadb(collection_id, query_embedding, k)

    # Cache and return results
    if docs:
        ctx.query_cache[cache_key] = docs
        if config.verbose_logging:
            logger.debug(f"💾 Cached results under key: {cache_key}")
        if len(ctx.query_cache) % 50 == 0:
            _save_query_cache()
            if config.verbose_logging:
                logger.debug("💾 Saved query cache to disk (50+ entries)")

    return _format_context_results(docs)


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

    if config.verbose_logging:
        logger.debug(f"🔍 get_relevant_context called with query: '{query}' (k={k}, space={space_name})")

    # Use current space if not specified
    if space_name is None:
        space_name = ctx.current_space
        if config.verbose_logging:
            logger.debug(f"🏢 Using default space: {space_name}")
    else:
        if config.verbose_logging:
            logger.debug(f"🏢 Using specified space: {space_name}")

    # Check cache first
    cache_key = f"{space_name}:{query}:{k}"
    cached_context = _check_cache_for_context(cache_key)
    if cached_context is not None:
        return cached_context

    # Return empty context if vector database not available
    if ctx.vectorstore is None:
        if config.verbose_logging:
            logger.warning("❌ Vectorstore not available for context retrieval")
        return ""

    try:
        # Generate embedding for the query
        query_embedding = _generate_query_embedding(query)
        if query_embedding is None:
            return ""

        # Find collection for the specified space
        from src.vectordb.spaces import get_space_collection_name
        collection_name = get_space_collection_name(space_name)
        collection_id = _find_collection_id(collection_name, space_name)

        if not collection_id:
            logger.warning(f"Could not find collection for space {space_name}")
            return ""

        # Query and cache results
        return _retrieve_and_cache_context(query_embedding, collection_id, k, cache_key, space_name)

    except (AttributeError, NameError, Exception) as e:
        logger.warning(f"Failed to retrieve context: {e}")
        return ""


def _generate_embeddings(content: str) -> Optional[list]:
    """
    Generate embeddings for document content.

    Args:
        content: Text content to embed

    Returns:
        Embedding vector if successful, None otherwise
    """
    ctx = get_context()
    config = get_config()

    try:
        if ctx.embeddings is None:
            logger.error("Embeddings not available")
            return None

        if config.verbose_logging:
            logger.debug("🧮 Generating embeddings for document")
            logger.debug(f"   Content length: {len(content)} chars")

        embeddings_result = ctx.embeddings.embed_documents([content])
        if not embeddings_result:
            logger.error("Failed to generate embeddings")
            return None

        try:
            embedding_vector = embeddings_result[0]
        except (IndexError, TypeError):
            logger.error("Failed to get embedding vector from result")
            return None

        if config.verbose_logging:
            try:
                logger.debug(f"✅ Generated embedding vector (length: {len(embedding_vector)})")
                logger.debug(f"   Sample: {embedding_vector[:3]}...{embedding_vector[-3:]}")
            except (TypeError, IndexError):
                logger.debug("✅ Generated embedding vector")

        return embedding_vector
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return None


def _find_or_create_collection(collection_name: str, space_name: str) -> Optional[str]:
    """
    Find existing collection or create new one.

    Args:
        collection_name: Name of the collection
        space_name: Space name for logging

    Returns:
        Collection ID if found or created, None if failed (HTTP error)
        Raises: Exception if API communication fails
    """
    config = get_config()
    api_session = _get_api_session()
    list_url = f"http://{config.chroma_host}:{config.chroma_port}/api/v2/tenants/default_tenant/databases/default_database/collections"

    if config.verbose_logging:
        logger.debug(f"🔍 Finding/creating collection: {collection_name}")
        logger.debug(f"   List URL: {list_url}")

    list_response = api_session.get(list_url, timeout=10)
    if config.verbose_logging:
        logger.debug(f"   List response status: {list_response.status_code}")

    if list_response.status_code == 200:
        collections = list_response.json()
        if config.verbose_logging:
            logger.debug(f"   Found {len(collections)} total collections")
            for coll in collections:
                logger.debug(f"     - {coll.get('name')} (ID: {coll.get('id')})")
        for coll in collections:
            if coll.get("name") == collection_name:
                collection_id = coll.get("id")
                if config.verbose_logging:
                    logger.debug(f"✅ Found existing collection: {collection_name} (ID: {collection_id})")
                return collection_id

    # Collection doesn't exist, create it
    if config.verbose_logging:
        logger.debug(f"🏗️ Creating new collection: {collection_name}")

    create_url = f"http://{config.chroma_host}:{config.chroma_port}/api/v2/tenants/default_tenant/databases/default_database/collections"
    create_payload = {"name": collection_name}

    if config.verbose_logging:
        logger.debug(f"   Create URL: {create_url}")
        logger.debug(f"   Create payload: {create_payload}")

    create_response = api_session.post(create_url, json=create_payload, timeout=10)
    if config.verbose_logging:
        logger.debug(f"   Create response status: {create_response.status_code}")

    if create_response.status_code == 201:
        collection_id = create_response.json().get("id")
        if config.verbose_logging:
            logger.debug(
                f"✅ Created new collection for space {space_name}: {collection_name} (ID: {collection_id})"
            )
        return collection_id
    else:
        logger.error(f"Failed to create collection: HTTP {create_response.status_code}")
        if config.verbose_logging:
            logger.debug(f"   Create response content: {create_response.text}")
        return None


def _store_document_in_chromadb(
    collection_id: str, doc_content: str, embedding_vector: list, metadata: dict, space_name: str
) -> bool:
    """
    Store document in ChromaDB with embeddings.

    Args:
        collection_id: ID of the target collection
        doc_content: Document content text
        embedding_vector: Generated embedding vector
        metadata: Document metadata
        space_name: Space name for logging

    Returns:
        True if successful, False otherwise
    """
    config = get_config()

    try:
        api_session = _get_api_session()
        add_url = (
            f"http://{config.chroma_host}:{config.chroma_port}/api/v2/"
            "tenants/default_tenant/databases/default_database/"
            f"collections/{collection_id}/add"
        )

        # Prepare the document data with embeddings
        doc_id = f"doc_{len(doc_content)}_{int(datetime.now().timestamp() * 1000000)}"
        payload = {
            "ids": [doc_id],
            "embeddings": [embedding_vector],
            "documents": [doc_content],
            "metadatas": [metadata] if metadata else [{}],
        }

        if config.verbose_logging:
            logger.debug("📤 Adding document to ChromaDB")
            logger.debug(f"   URL: {add_url}")
            logger.debug(f"   Document ID: {doc_id}")
            logger.debug(f"   Content length: {len(doc_content)} chars")
            logger.debug(f"   Embedding length: {len(embedding_vector)}")
            logger.debug(f"   Metadata: {metadata}")

        headers = {"Content-Type": "application/json"}
        response = api_session.post(add_url, json=payload, headers=headers, timeout=10)

        if config.verbose_logging:
            logger.debug(f"   Add response status: {response.status_code}")

        if response.status_code == 201:
            if config.verbose_logging:
                logger.debug(f"✅ Document added successfully to space {space_name}: {doc_id}")
            return True
        else:
            logger.error(
                f"Failed to add document to space {space_name}: {response.status_code} - {response.text}"
            )
            if config.verbose_logging:
                logger.debug(f"   Add response content: {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error storing document in ChromaDB: {e}")
        return False


def _validate_learning_inputs(content: str) -> bool:
    """
    Validate that learning is possible.

    Args:
        content: Text content to learn

    Returns:
        True if valid, False otherwise
    """
    ctx = get_context()

    if ctx.embeddings is None:
        logger.error("Embeddings not available for learning")
        return False

    if not content:
        logger.error("Cannot add empty content to knowledge base")
        return False

    return True


def _prepare_document_for_learning(content: str, metadata: Optional[dict] = None) -> Optional[tuple]:
    """
    Prepare document and generate embeddings for learning.

    Args:
        content: Text content to learn
        metadata: Optional metadata dict

    Returns:
        (Document, embedding_vector) tuple or None if generation fails
    """
    # Set default metadata if not provided
    if metadata is None:
        metadata = {
            "source": "user-input",
            "added_at": str(datetime.now()),
        }

    # Create document
    doc = Document(page_content=content, metadata=metadata)

    # Generate embeddings
    embedding_vector = _generate_embeddings(doc.page_content)
    if embedding_vector is None:
        return None

    return (doc, embedding_vector)


def _store_in_chromadb_with_fallback(
    doc: Document, embedding_vector: list, collection_name: str, collection_id: str
) -> bool:
    """
    Store document in ChromaDB with fallback to LangChain.

    Args:
        doc: Document to store
        embedding_vector: Generated embedding vector
        collection_name: ChromaDB collection name
        collection_id: ChromaDB collection ID

    Returns:
        True if successful, False otherwise
    """
    ctx = get_context()
    config = get_config()

    try:
        # Try direct API method
        if _store_document_in_chromadb(collection_id, doc.page_content, embedding_vector, doc.metadata, collection_name):
            return True

        # API returned an error (not an exception), don't try fallback
        return False

    except Exception as api_e:
        # API raised an exception, try LangChain fallback
        logger.warning(f"Direct API call failed with exception, trying LangChain fallback: {api_e}")
        if ctx.vectorstore is not None:
            ctx.vectorstore.add_documents([doc])
            if config.verbose_logging:
                logger.debug("Used LangChain fallback for document addition")
            return True
        else:
            logger.error("No vectorstore available for fallback")
            return False


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

    if config.verbose_logging:
        logger.debug("📚 add_to_knowledge_base called")
        logger.debug(f"   Content: '{content}' ({len(content)} chars)")
        logger.debug(f"   Metadata: {metadata}")

    # Validate inputs
    if not _validate_learning_inputs(content):
        return False

    if config.verbose_logging:
        logger.debug(f"🏢 Adding to space: {ctx.current_space}")
        from src.vectordb.spaces import get_space_collection_name
        logger.debug(f"   Space collection: {get_space_collection_name(ctx.current_space)}")

    # Prepare document and embeddings
    result = _prepare_document_for_learning(content, metadata)
    if result is None:
        return False

    doc, embedding_vector = result

    try:
        # Try API-based storage
        from src.vectordb.spaces import get_space_collection_name
        collection_name = get_space_collection_name(ctx.current_space)
        collection_id = _find_or_create_collection(collection_name, ctx.current_space)

        if not collection_id:
            logger.error(f"Could not find or create collection for space {ctx.current_space}")
            # Try fallback before failing
            if ctx.vectorstore is not None:
                ctx.vectorstore.add_documents([doc])
                if config.verbose_logging:
                    logger.debug("Used LangChain fallback after failed collection creation")
                return True
            return False

        # Store document with fallback
        return _store_in_chromadb_with_fallback(doc, embedding_vector, collection_name, collection_id)

    except Exception as e:
        # API failed, try LangChain fallback
        logger.warning(f"API call failed, attempting LangChain fallback: {e}")
        if ctx.vectorstore is not None:
            try:
                ctx.vectorstore.add_documents([doc])
                if config.verbose_logging:
                    logger.debug("Successfully used LangChain fallback")
                return True
            except Exception as fallback_e:
                logger.error(f"Both API and fallback failed: {fallback_e}")
                return False
        else:
            logger.error("No vectorstore available for fallback")
            return False


def _save_query_cache():
    """Save query cache to disk."""
    try:
        from src.storage.cache import save_query_cache

        save_query_cache()
    except Exception as e:
        logger.warning(f"Failed to save query cache: {e}")


__all__ = ["get_relevant_context", "add_to_knowledge_base"]
