#!/usr/bin/env python3
"""
Integration tests for Learning Workflows.

Verifies the end-to-end learning flows:
- Adding direct information (/learn)
- Learning from URLs (/web)
- Knowledge retrieval and verification
"""

import pytest
import responses
from unittest.mock import MagicMock, patch
from src.core.context import get_context, reset_context
from src.core.context_utils import get_relevant_context
from src.commands.handlers.learning_commands import handle_learn, handle_web


class TestLearningWorkflows:
    """End-to-end learning workflow testing."""

    def setup_method(self):
        """Reset context and setup base mocks."""
        reset_context()
        self.host = "localhost"
        self.port = 8000
        self.base_url = f"http://{self.host}:{self.port}/api/v2"
        self.coll_url = f"{self.base_url}/tenants/default_tenant/databases/default_database/collections"

    def teardown_method(self):
        """Cleanup."""
        reset_context()

    @responses.activate
    @patch('src.core.context_utils.get_config')
    def test_learn_and_retrieve_workflow(self, mock_config):
        """Test learning a fact and then retrieving it using semantic search."""
        # 1. Setup mocks
        ctx = get_context()
        ctx.vectorstore = MagicMock()
        ctx.current_space = "default"

        mock_conf = MagicMock()
        mock_conf.chroma_host = self.host
        mock_conf.chroma_port = self.port
        mock_config.return_value = mock_conf

        # Mock embeddings
        mock_embeddings = MagicMock()
        mock_embeddings.embed_query.return_value = [0.1] * 384
        mock_embeddings.embed_documents.return_value = [[0.1] * 384]
        ctx.embeddings = mock_embeddings

        # 2. Add information
        responses.add(
            responses.GET,
            self.coll_url,
            json=[{"name": "knowledge_base", "id": "kb-id"}],
            status=200
        )
        responses.add(responses.POST, f"{self.coll_url}/kb-id/add", status=201)

        handle_learn(["The", "secret", "ingredient", "is", "love"])

        # 3. Retrieve information
        responses.add(
            responses.POST,
            f"{self.coll_url}/kb-id/query",
            json={"documents": [["The secret ingredient is love"]]},
            status=200
        )

        result = get_relevant_context("What is the secret ingredient?")
        assert "love" in result
        assert "secret ingredient" in result

    @responses.activate
    @patch('src.core.context_utils.get_config')
    @patch('src.main.vectorstore', new_callable=MagicMock)
    @patch('docling.document_converter.DocumentConverter')
    def test_web_learning_workflow(self, mock_converter_class, mock_main_vectorstore, mock_config):
        """Test learning from a web URL by mocking Docling and the vectorstore."""
        # 1. Setup mocks
        ctx = get_context()
        ctx.current_space = "default"

        mock_conf = MagicMock()
        mock_conf.chroma_host = self.host
        mock_conf.chroma_port = self.port
        mock_config.return_value = mock_conf

        # Mock Docling conversion
        mock_converter = mock_converter_class.return_value
        mock_result = MagicMock()
        mock_result.document.export_to_markdown.return_value = "# Web Content\nRetrieved from URL."
        mock_result.document.title = "Test Web Page"
        mock_converter.convert.return_value = mock_result

        # Update global vectorstore in main (used by handle_web -> execute_learn_url)
        mock_main_vectorstore.add_documents.return_value = ["doc-id"]

        # 2. Execute /web command
        # Note: We don't need responses for Chroma here because execute_learn_url
        # directly interacts with the global vectorstore mock
        handle_web(["https://example.com"])

        # 3. Verify interactions
        mock_converter.convert.assert_called_with("https://example.com")
        assert mock_main_vectorstore.add_documents.called
        args, _ = mock_main_vectorstore.add_documents.call_args
        doc = args[0][0]
        assert "Retrieved from URL" in doc.page_content
        assert doc.metadata["source"] == "https://example.com"

    @responses.activate
    @patch('src.core.context_utils.get_config')
    def test_learn_error_handling(self, mock_config):
        """Test how the learning workflow handles vector database failure."""
        ctx = get_context()
        ctx.vectorstore = MagicMock()

        mock_conf = MagicMock()
        mock_conf.chroma_host = self.host
        mock_conf.chroma_port = self.port
        mock_config.return_value = mock_conf

        # Mock API failure
        responses.add(responses.GET, self.coll_url, status=500)

        # Should not crash, but print error (we'd need capsys to verify output)
        handle_learn(["Failed", "connection"])

        # Verify it didn't succeed
        assert not get_context().query_cache  # No cache entries
