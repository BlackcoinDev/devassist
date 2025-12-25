#!/usr/bin/env python3
"""
Unit tests for Database Commands Handler.

Tests cover:
- Vector database statistics display
- Collection finding and counting
- Metadata analysis
- Error handling for API failures
"""

import unittest
from io import StringIO
import sys
from unittest.mock import patch, MagicMock
from src.commands.handlers.database_commands import (
    handle_vectordb,
    _find_collection_for_space,
    _get_collection_count,
    _analyze_collection_metadata,
    _format_statistics_output,
)


class TestFindCollectionForSpace(unittest.TestCase):
    """Test collection finding functionality."""

    @patch("src.commands.handlers.database_commands._get_api_session")
    def test_find_collection_success(self, mock_session):
        """Test finding a collection successfully."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "knowledge_base", "id": "abc123"},
            {"name": "space_test", "id": "def456"},
        ]
        mock_session.return_value.get.return_value = mock_response

        mock_ctx = MagicMock()
        mock_config = MagicMock()
        mock_config.chroma_host = "localhost"
        mock_config.chroma_port = 8000

        result = _find_collection_for_space("knowledge_base", mock_ctx, mock_config)

        self.assertEqual(result, "abc123")

    @patch("src.commands.handlers.database_commands._get_api_session")
    def test_find_collection_not_found(self, mock_session):
        """Test when collection is not found."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "other_collection", "id": "xyz789"},
        ]
        mock_session.return_value.get.return_value = mock_response

        mock_ctx = MagicMock()
        mock_config = MagicMock()
        mock_config.chroma_host = "localhost"
        mock_config.chroma_port = 8000

        result = _find_collection_for_space("nonexistent", mock_ctx, mock_config)

        self.assertIsNone(result)

    @patch("src.commands.handlers.database_commands._get_api_session")
    def test_find_collection_api_error(self, mock_session):
        """Test handling of API errors."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_session.return_value.get.return_value = mock_response

        mock_ctx = MagicMock()
        mock_config = MagicMock()
        mock_config.chroma_host = "localhost"
        mock_config.chroma_port = 8000

        result = _find_collection_for_space("test", mock_ctx, mock_config)

        self.assertIsNone(result)

    @patch("src.commands.handlers.database_commands._get_api_session")
    def test_find_collection_exception(self, mock_session):
        """Test handling of exceptions."""
        mock_session.return_value.get.side_effect = Exception("Connection failed")

        mock_ctx = MagicMock()
        mock_config = MagicMock()
        mock_config.chroma_host = "localhost"
        mock_config.chroma_port = 8000

        result = _find_collection_for_space("test", mock_ctx, mock_config)

        self.assertIsNone(result)


class TestGetCollectionCount(unittest.TestCase):
    """Test collection count functionality."""

    @patch("src.commands.handlers.database_commands._get_api_session")
    def test_get_count_success_int(self, mock_session):
        """Test getting count when API returns integer."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = 42
        mock_session.return_value.get.return_value = mock_response

        mock_config = MagicMock()
        mock_config.chroma_host = "localhost"
        mock_config.chroma_port = 8000

        result = _get_collection_count("abc123", mock_config)

        self.assertEqual(result, 42)

    @patch("src.commands.handlers.database_commands._get_api_session")
    def test_get_count_success_dict(self, mock_session):
        """Test getting count when API returns dict."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"count": 100}
        mock_session.return_value.get.return_value = mock_response

        mock_config = MagicMock()
        mock_config.chroma_host = "localhost"
        mock_config.chroma_port = 8000

        result = _get_collection_count("abc123", mock_config)

        self.assertEqual(result, 100)

    @patch("src.commands.handlers.database_commands._get_api_session")
    def test_get_count_api_error(self, mock_session):
        """Test handling of API errors."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_session.return_value.get.return_value = mock_response

        mock_config = MagicMock()
        mock_config.chroma_host = "localhost"
        mock_config.chroma_port = 8000

        result = _get_collection_count("abc123", mock_config)

        self.assertIsNone(result)

    @patch("src.commands.handlers.database_commands._get_api_session")
    def test_get_count_exception(self, mock_session):
        """Test handling of exceptions."""
        mock_session.return_value.get.side_effect = Exception("Timeout")

        mock_config = MagicMock()
        mock_config.chroma_host = "localhost"
        mock_config.chroma_port = 8000

        result = _get_collection_count("abc123", mock_config)

        self.assertIsNone(result)


class TestAnalyzeCollectionMetadata(unittest.TestCase):
    """Test metadata analysis functionality."""

    def test_analyze_empty_collection(self):
        """Test analysis with zero chunks."""
        mock_ctx = MagicMock()
        mock_ctx.vectorstore = None

        result = _analyze_collection_metadata("test_collection", 0, mock_ctx)

        self.assertIn("sources", result)
        self.assertIn("content_types", result)

    def test_analyze_with_vectorstore(self):
        """Test analysis when vectorstore is available."""
        mock_ctx = MagicMock()
        mock_vectorstore = MagicMock()

        # Mock the get() method to return documents
        mock_result = {
            "metadatas": [
                {"source": "file1.py", "content_type": "code"},
                {"source": "file2.py", "content_type": "code"},
                {"source": "README.md", "content_type": "text"},
            ]
        }
        mock_vectorstore.get.return_value = mock_result
        mock_ctx.vectorstore = mock_vectorstore

        result = _analyze_collection_metadata("test_collection", 50, mock_ctx)

        self.assertIn("sources", result)


class TestFormatStatisticsOutput(unittest.TestCase):
    """Test statistics output formatting."""

    def test_format_basic_stats(self):
        """Test formatting basic statistics."""
        from datetime import datetime

        stats = {
            "sources": {"file1.py", "file2.py"},
            "content_types": {"code"},
            "date_range": None,
            "sample_sources": [
                ("file1.py", datetime(2024, 1, 1)),
                ("file2.py", datetime(2024, 1, 2)),
            ],
        }

        result = _format_statistics_output("knowledge_base", 100, "default", stats)

        self.assertIn("knowledge_base", result)
        self.assertIn("100", result)
        self.assertIn("default", result)

    def test_format_with_date_range(self):
        """Test formatting with date range."""
        from datetime import datetime

        stats = {
            "sources": {"file1.py"},
            "content_types": {"code"},
            "date_range": (datetime(2024, 1, 1), datetime(2024, 12, 31)),
            "sample_sources": [("file1.py", datetime(2024, 6, 15))],
        }

        result = _format_statistics_output("test", 50, "project", stats)

        self.assertIn("test", result)
        self.assertIn("50", result)

    def test_format_empty_sample_sources(self):
        """Test formatting with empty sample sources."""
        stats = {
            "sources": set(),
            "content_types": set(),
            "date_range": None,
            "sample_sources": [],
        }

        result = _format_statistics_output("empty", 0, "default", stats)

        self.assertIn("empty", result)


class TestHandleVectordb(unittest.TestCase):
    """Test main vectordb command handler."""

    @patch("src.commands.handlers.database_commands._format_statistics_output")
    @patch("src.commands.handlers.database_commands._analyze_collection_metadata")
    @patch("src.commands.handlers.database_commands._get_collection_count")
    @patch("src.commands.handlers.database_commands._find_collection_for_space")
    @patch("src.commands.handlers.database_commands.get_space_collection_name")
    @patch("src.commands.handlers.database_commands.get_config")
    @patch("src.commands.handlers.database_commands.get_context")
    def test_handle_vectordb_success(
        self,
        mock_get_ctx,
        mock_get_config,
        mock_get_space,
        mock_find,
        mock_count,
        mock_analyze,
        mock_format,
    ):
        """Test successful vectordb display."""
        mock_ctx = MagicMock()
        mock_ctx.current_space = "default"
        mock_get_ctx.return_value = mock_ctx

        mock_config = MagicMock()
        mock_get_config.return_value = mock_config

        mock_get_space.return_value = "knowledge_base"
        mock_find.return_value = "abc123"
        mock_count.return_value = 100
        mock_analyze.return_value = {"sources": set(), "content_types": set()}
        mock_format.return_value = "Formatted output"

        captured = StringIO()
        sys.stdout = captured
        handle_vectordb([])
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("Vector Database", output)

    @patch("src.commands.handlers.database_commands._find_collection_for_space")
    @patch("src.commands.handlers.database_commands.get_space_collection_name")
    @patch("src.commands.handlers.database_commands.get_config")
    @patch("src.commands.handlers.database_commands.get_context")
    def test_handle_vectordb_no_collection(
        self, mock_get_ctx, mock_get_config, mock_get_space, mock_find
    ):
        """Test when no collection found for space."""
        mock_ctx = MagicMock()
        mock_ctx.current_space = "new-project"
        mock_get_ctx.return_value = mock_ctx

        mock_config = MagicMock()
        mock_get_config.return_value = mock_config

        mock_get_space.return_value = "space_new-project"
        mock_find.return_value = None

        captured = StringIO()
        sys.stdout = captured
        handle_vectordb([])
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("No collection found", output)

    @patch("src.commands.handlers.database_commands._get_collection_count")
    @patch("src.commands.handlers.database_commands._find_collection_for_space")
    @patch("src.commands.handlers.database_commands.get_space_collection_name")
    @patch("src.commands.handlers.database_commands.get_config")
    @patch("src.commands.handlers.database_commands.get_context")
    def test_handle_vectordb_count_failure(
        self, mock_get_ctx, mock_get_config, mock_get_space, mock_find, mock_count
    ):
        """Test when count retrieval fails."""
        mock_ctx = MagicMock()
        mock_ctx.current_space = "default"
        mock_get_ctx.return_value = mock_ctx

        mock_config = MagicMock()
        mock_get_config.return_value = mock_config

        mock_get_space.return_value = "knowledge_base"
        mock_find.return_value = "abc123"
        mock_count.return_value = None

        captured = StringIO()
        sys.stdout = captured
        handle_vectordb([])
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("Failed to retrieve chunks", output)


if __name__ == "__main__":
    unittest.main()
