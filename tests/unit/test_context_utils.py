#!/usr/bin/env python3
"""
Test suite for Context Utilities (src/core/context_utils.py).

Tests cover:
- Knowledge base context retrieval (get_relevant_context)
- Adding content to knowledge base (add_to_knowledge_base)
- Query caching behavior
- Error handling for missing services
"""

import pytest
import responses
from unittest.mock import Mock, patch, MagicMock
from langchain_core.documents import Document
from src.core.context_utils import get_relevant_context, add_to_knowledge_base
from src.core.context import get_context, reset_context


class TestKnowledgeBaseFunctions:
    """Test interaction with ChromaDB via context utilities."""

    def setup_method(self):
        """Set up test environment."""
        reset_context()
        self.host = "localhost"
        self.port = 8000
        self.base_url = f"http://{self.host}:{self.port}/api/v2"
        self.coll_url = f"{self.base_url}/tenants/default_tenant/databases/default_database/collections"

    def teardown_method(self):
        """Clean up test environment."""
        reset_context()

    @responses.activate
    def test_get_relevant_context_from_cache(self):
        """Test that get_relevant_context returns cached results if available."""
        ctx = get_context()
        ctx.current_space = "default"
        query = "test query"
        cache_key = f"default:{query}:3"
        ctx.query_cache[cache_key] = ["cached doc 1", "cached doc 2"]

        # No network calls should be made
        result = get_relevant_context(query)
        
        assert "Relevant context:" in result
        assert "cached doc 1" in result
        assert "cached doc 2" in result

    @responses.activate
    def test_get_relevant_context_api_call(self):
        """Test retrieving context via ChromaDB API."""
        ctx = get_context()
        ctx.current_space = "default"
        ctx.vectorstore = MagicMock() # Ensure not None
        
        # Mock embeddings
        mock_embeddings = MagicMock()
        mock_embeddings.embed_query.return_value = [0.1, 0.2]
        ctx.embeddings = mock_embeddings

        # Mock config
        mock_config = MagicMock()
        mock_config.chroma_host = self.host
        mock_config.chroma_port = self.port

        with patch('src.core.context_utils.get_config', return_value=mock_config):
            # 1. Mock listing collections to find 'knowledge_base' (default)
            responses.add(
                responses.GET, 
                self.coll_url, 
                json=[{"id": "kb-id", "name": "knowledge_base"}], 
                status=200
            )
            
            # 2. Mock query endpoint
            query_url = f"{self.coll_url}/kb-id/query"
            responses.add(
                responses.POST, 
                query_url, 
                json={"documents": [["doc from api"]]}, 
                status=200
            )

            result = get_relevant_context("query")
            
            assert "Relevant context:" in result
            assert "doc from api" in result
            # Verify it was cached
            assert ctx.query_cache["default:query:3"] == ["doc from api"]

    @responses.activate
    def test_add_to_knowledge_base_success(self):
        """Test adding document to knowledge base."""
        ctx = get_context()
        ctx.current_space = "default"
        ctx.vectorstore = MagicMock()
        
        # Mock embeddings
        mock_embeddings = MagicMock()
        mock_embeddings.embed_documents.return_value = [[0.1, 0.2]]
        ctx.embeddings = mock_embeddings

        mock_config = MagicMock()
        mock_config.chroma_host = self.host
        mock_config.chroma_port = self.port

        with patch('src.core.context_utils.get_config', return_value=mock_config):
            # 1. Mock listing collections
            responses.add(
                responses.GET, 
                self.coll_url, 
                json=[{"id": "kb-id", "name": "knowledge_base"}], 
                status=200
            )
            
            # 2. Mock add endpoint
            add_url = f"{self.coll_url}/kb-id/add"
            responses.add(responses.POST, add_url, status=201)

            success = add_to_knowledge_base("new knowledge")
            assert success is True

    def test_add_to_knowledge_base_fallback(self):
        """Test fallback to LangChain when API fails."""
        ctx = get_context()
        ctx.current_space = "default"
        ctx.vectorstore = MagicMock()
        
        # Mock embeddings
        mock_embeddings = MagicMock()
        mock_embeddings.embed_documents.return_value = [[0.1, 0.2]]
        ctx.embeddings = mock_embeddings

        # Force an exception in the API part
        with patch('src.core.context_utils._get_api_session', side_effect=Exception("API Down")):
            success = add_to_knowledge_base("fallback knowledge")
            
            # Should have used LangChain fallback
            assert success is True
            assert ctx.vectorstore.add_documents.called

    def test_get_relevant_context_no_vectorstore(self):
        """Test behavior when vectorstore is not initialized."""
        ctx = get_context()
        ctx.vectorstore = None
        
        result = get_relevant_context("query")
        assert result == ""
