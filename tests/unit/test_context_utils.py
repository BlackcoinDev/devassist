#!/usr/bin/env python3
"""
Test suite for Context Utilities (src/core/context_utils.py).

Tests cover:
- Knowledge base context retrieval (get_relevant_context)
- Adding content to knowledge base (add_to_knowledge_base)
- Query caching behavior
- Error handling for missing services
"""

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
        ctx.vectorstore = MagicMock()  # Ensure not None

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

    @responses.activate
    def test_get_relevant_context_no_embeddings(self):
        """Test behavior when embeddings are not available."""
        ctx = get_context()
        ctx.current_space = "default"
        ctx.vectorstore = MagicMock()
        ctx.embeddings = None

        result = get_relevant_context("query")
        assert result == ""

    @responses.activate
    def test_get_relevant_context_embeddings_exception(self):
        """Test behavior when embeddings generation fails."""
        ctx = get_context()
        ctx.current_space = "default"
        ctx.vectorstore = MagicMock()

        # Mock embeddings that raise exception
        mock_embeddings = MagicMock()
        mock_embeddings.embed_query.side_effect = Exception("Embedding error")
        ctx.embeddings = mock_embeddings

        result = get_relevant_context("query")
        assert result == ""

    @responses.activate
    def test_get_relevant_context_collection_not_found(self):
        """Test behavior when collection is not found."""
        ctx = get_context()
        ctx.current_space = "default"
        ctx.vectorstore = MagicMock()

        # Mock embeddings
        mock_embeddings = MagicMock()
        mock_embeddings.embed_query.return_value = [0.1, 0.2]
        ctx.embeddings = mock_embeddings

        mock_config = MagicMock()
        mock_config.chroma_host = self.host
        mock_config.chroma_port = self.port

        with patch('src.core.context_utils.get_config', return_value=mock_config):
            # Mock listing collections - empty list
            responses.add(
                responses.GET,
                self.coll_url,
                json=[],
                status=200
            )

            result = get_relevant_context("query")
            assert result == ""

    @responses.activate
    def test_get_relevant_context_api_failure(self):
        """Test behavior when ChromaDB API call fails."""
        ctx = get_context()
        ctx.current_space = "default"
        ctx.vectorstore = MagicMock()

        # Mock embeddings
        mock_embeddings = MagicMock()
        mock_embeddings.embed_query.return_value = [0.1, 0.2]
        ctx.embeddings = mock_embeddings

        mock_config = MagicMock()
        mock_config.chroma_host = self.host
        mock_config.chroma_port = self.port

        with patch('src.core.context_utils.get_config', return_value=mock_config):
            # Mock listing collections
            responses.add(
                responses.GET,
                self.coll_url,
                json=[{"id": "kb-id", "name": "knowledge_base"}],
                status=200
            )

            # Mock query endpoint failure
            query_url = f"{self.coll_url}/kb-id/query"
            responses.add(responses.POST, query_url, status=500)

            result = get_relevant_context("query")
            assert result == ""

    @responses.activate
    def test_get_relevant_context_no_documents_found(self):
        """Test behavior when no relevant documents are found."""
        ctx = get_context()
        ctx.current_space = "default"
        ctx.vectorstore = MagicMock()

        # Mock embeddings
        mock_embeddings = MagicMock()
        mock_embeddings.embed_query.return_value = [0.1, 0.2]
        ctx.embeddings = mock_embeddings

        mock_config = MagicMock()
        mock_config.chroma_host = self.host
        mock_config.chroma_port = self.port

        with patch('src.core.context_utils.get_config', return_value=mock_config):
            # Mock listing collections
            responses.add(
                responses.GET,
                self.coll_url,
                json=[{"id": "kb-id", "name": "knowledge_base"}],
                status=200
            )

            # Mock query endpoint with empty documents
            query_url = f"{self.coll_url}/kb-id/query"
            responses.add(
                responses.POST,
                query_url,
                json={"documents": [[]]},
                status=200
            )

            result = get_relevant_context("query")
            assert result == ""

    @responses.activate
    def test_add_to_knowledge_base_empty_content(self):
        """Test behavior when empty content is provided."""
        ctx = get_context()
        ctx.current_space = "default"
        ctx.vectorstore = MagicMock()

        success = add_to_knowledge_base("")
        assert success is False

    @responses.activate
    def test_add_to_knowledge_base_collection_creation(self):
        """Test collection creation when it doesn't exist."""
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
            # Mock listing collections - empty (collection doesn't exist)
            responses.add(responses.GET, self.coll_url, json=[], status=200)

            # Mock collection creation
            create_url = f"{self.coll_url}"
            responses.add(
                responses.POST,
                create_url,
                json={"id": "new-kb-id", "name": "knowledge_base"},
                status=201
            )

            # Mock add endpoint
            add_url = f"{self.coll_url}/new-kb-id/add"
            responses.add(responses.POST, add_url, status=201)

            success = add_to_knowledge_base("new knowledge")
            assert success is True

    @responses.activate
    def test_add_to_knowledge_base_collection_creation_failure(self):
        """Test behavior when collection creation fails."""
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
            # Mock listing collections - empty (collection doesn't exist)
            responses.add(responses.GET, self.coll_url, json=[], status=200)

            # Mock collection creation failure
            create_url = f"{self.coll_url}"
            responses.add(responses.POST, create_url, status=500)

            success = add_to_knowledge_base("new knowledge")
            assert success is False

    @responses.activate
    def test_add_to_knowledge_base_api_add_failure(self):
        """Test behavior when document addition via API fails."""
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
            # Mock listing collections
            responses.add(
                responses.GET,
                self.coll_url,
                json=[{"id": "kb-id", "name": "knowledge_base"}],
                status=200
            )

            # Mock add endpoint failure
            add_url = f"{self.coll_url}/kb-id/add"
            responses.add(responses.POST, add_url, status=500)

            success = add_to_knowledge_base("new knowledge")
            assert success is False

    def test_add_to_knowledge_base_no_vectorstore(self):
        """Test behavior when vectorstore is not available."""
        ctx = get_context()
        ctx.vectorstore = None

        success = add_to_knowledge_base("new knowledge")
        assert success is False

    @responses.activate
    def test_save_query_cache_exception(self):
        """Test behavior when saving query cache fails."""
        ctx = get_context()
        ctx.current_space = "default"
        ctx.vectorstore = MagicMock()

        # Mock embeddings
        mock_embeddings = MagicMock()
        mock_embeddings.embed_query.return_value = [0.1, 0.2]
        ctx.embeddings = mock_embeddings

        # Fill cache to trigger save
        for i in range(50):
            ctx.query_cache[f"key_{i}"] = [f"doc_{i}"]

        mock_config = MagicMock()
        mock_config.chroma_host = self.host
        mock_config.chroma_port = self.port

        with patch('src.core.context_utils.get_config', return_value=mock_config):
            # Mock listing collections
            responses.add(
                responses.GET,
                f"http://{self.host}:{self.port}/api/v2/tenants/default_tenant/databases/default_database/collections",
                json=[{"id": "kb-id", "name": "knowledge_base"}],
                status=200
            )

            # Mock query endpoint
            query_url = f"http://{self.host}:{self.port}/api/v2/tenants/default_tenant/databases/default_database/collections/kb-id/query"
            responses.add(
                responses.POST,
                query_url,
                json={"documents": [["doc from api"]]},
                status=200
            )

            # Mock _save_query_cache to raise exception
            with patch('src.storage.cache.save_query_cache', side_effect=Exception("Save error")):
                result = get_relevant_context("query")
                assert "Relevant context:" in result
                assert "doc from api" in result
