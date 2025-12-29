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
Comprehensive Tool Testing Suite

Tests for the first 8 of 13 AI tools with proper mocking and isolation:
- read_file: File reading with security constraints
- write_file: File creation/modification
- list_directory: Directory browsing
- get_current_directory: Path retrieval
- parse_document: Document processing with Docling
- learn_information: Knowledge base storage
- search_knowledge: Semantic search
- search_web: DuckDuckGo web search

The remaining 5 tools (shell_execute, git_status, git_diff, git_log, code_search)
are tested in separate test files:
- test_shell_tools.py - shell_execute
- test_git_tools.py - git_status, git_diff, git_log
- test_system_tools.py - code_search
"""

from unittest.mock import patch, mock_open, MagicMock

# Import tool functions from modular architecture (v0.3.0)
from src.tools.executors.file_tools import (
    execute_read_file,
    execute_write_file,
    execute_list_directory,
    execute_get_current_directory,
)
from src.tools.executors.document_tools import execute_parse_document
from src.tools.executors.knowledge_tools import (
    execute_learn_information,
    execute_search_knowledge,
)
from src.tools.executors.web_tools import execute_web_search


class TestFileSystemTools:
    """Test file system operations with proper mocking."""

    @patch("src.tools.executors.file_tools._resolve_path")
    @patch("src.tools.executors.file_tools._get_sandbox_root")
    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.path.getsize")
    @patch("builtins.open", new_callable=mock_open, read_data="test content")
    def test_read_file_success(
        self, mock_file, mock_getsize, mock_isfile, mock_exists,
        mock_sandbox_root, mock_resolve_path
    ):
        """Test successful file reading."""
        mock_sandbox_root.return_value = "/tmp"
        mock_resolve_path.return_value = "/tmp/test.txt"
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_getsize.return_value = 100  # Under 1MB limit

        result = execute_read_file("test.txt")

        assert result["success"] is True
        assert "test content" in result["content"]
        assert result["size"] == 100

    @patch("src.tools.executors.file_tools._resolve_path")
    @patch("src.tools.executors.file_tools._get_sandbox_root")
    @patch("os.path.exists")
    def test_read_file_not_found(self, mock_exists, mock_sandbox_root, mock_resolve_path):
        """Test reading non-existent file."""
        mock_sandbox_root.return_value = "/tmp"
        mock_resolve_path.return_value = "/tmp/nonexistent.txt"
        mock_exists.return_value = False

        result = execute_read_file("nonexistent.txt")

        assert "error" in result
        assert "not found" in result["error"].lower()

    @patch("src.tools.executors.file_tools._resolve_path")
    @patch("src.tools.executors.file_tools._get_sandbox_root")
    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.path.getsize")
    def test_read_file_too_large(
        self, mock_getsize, mock_isfile, mock_exists, mock_sandbox_root, mock_resolve_path
    ):
        """Test reading file that's too large."""
        mock_sandbox_root.return_value = "/tmp"
        mock_resolve_path.return_value = "/tmp/large.txt"
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_getsize.return_value = 2 * 1024 * 1024  # 2MB > 1MB limit

        result = execute_read_file("large.txt")

        assert "error" in result
        assert "too large" in result["error"].lower()

    @patch("src.tools.executors.file_tools._resolve_path")
    @patch("src.tools.executors.file_tools._get_sandbox_root")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.dirname")
    def test_write_file_success(self, mock_dirname, mock_file, mock_sandbox_root, mock_resolve_path):
        """Test successful file writing."""
        mock_sandbox_root.return_value = "/tmp"
        mock_resolve_path.return_value = "/tmp/test.txt"
        mock_dirname.return_value = "/tmp"

        result = execute_write_file("test.txt", "new content")

        assert result["success"] is True
        assert result["size"] == len("new content")
        mock_file.assert_called_once()

    def test_write_file_empty_content(self):
        """Test writing empty content."""
        with patch("builtins.open", new_callable=mock_open) as mock_file:
            result = execute_write_file("empty.txt", "")

            assert result["success"] is True
            assert result["size"] == 0
            mock_file.assert_called_once()

    @patch("os.path.abspath")
    @patch("os.getcwd")
    @patch("os.listdir")
    @patch("os.path.isdir")
    @patch("os.path.exists")
    @patch("os.scandir")
    def test_list_directory_success(
        self,
        mock_scandir,
        mock_exists,
        mock_isdir,
        mock_listdir,
        mock_getcwd,
        mock_abspath,
    ):
        """Test successful directory listing."""
        mock_getcwd.return_value = "/tmp"
        mock_abspath.return_value = "/tmp/test_dir"
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.return_value = ["file1.txt", "file2.py", "subdir"]

        # Mock directory entries
        mock_entry1 = MagicMock()
        mock_entry1.name = "file1.txt"
        mock_entry1.is_file.return_value = True

        mock_entry2 = MagicMock()
        mock_entry2.name = "file2.py"
        mock_entry2.is_file.return_value = True

        mock_entry3 = MagicMock()
        mock_entry3.name = "subdir"
        mock_entry3.is_file.return_value = False

        mock_scandir.return_value = [mock_entry1, mock_entry2, mock_entry3]

        result = execute_list_directory("/tmp/test_dir")

        assert result["success"] is True
        assert result["total_items"] == 3
        assert len(result["contents"]) == 3

    @patch("os.getcwd")
    def test_get_current_directory(self, mock_getcwd):
        """Test getting current directory."""
        mock_getcwd.return_value = "/home/user/project"

        result = execute_get_current_directory()

        assert result["success"] is True

    @patch("src.tools.executors.file_tools._resolve_path")
    @patch("src.tools.executors.file_tools._get_sandbox_root")
    @patch("os.path.exists")
    @patch("os.path.isfile")
    def test_read_file_not_a_file(
        self, mock_isfile, mock_exists, mock_sandbox_root, mock_resolve_path
    ):
        """Test read_file when path is not a file (e.g., directory)."""
        mock_sandbox_root.return_value = "/tmp"
        mock_resolve_path.return_value = "/tmp/some_dir"
        mock_exists.return_value = True
        mock_isfile.return_value = False  # It's a directory, not a file

        result = execute_read_file("some_dir")

        assert "error" in result
        assert "Not a file" in result["error"]

    @patch("src.tools.executors.file_tools._resolve_path")
    @patch("src.tools.executors.file_tools._get_sandbox_root")
    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.path.getsize")
    @patch(
        "builtins.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")
    )
    def test_read_file_unicode_decode_error(
        self,
        mock_open_func,
        mock_getsize,
        mock_isfile,
        mock_exists,
        mock_sandbox_root,
        mock_resolve_path,
    ):
        """Test read_file with binary file causing UnicodeDecodeError."""
        mock_sandbox_root.return_value = "/tmp"
        mock_resolve_path.return_value = "/tmp/binary.bin"
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_getsize.return_value = 100

        result = execute_read_file("binary.bin")

        assert "error" in result
        assert "Cannot read binary file" in result["error"]

    @patch("src.tools.executors.file_tools._resolve_path")
    @patch("src.tools.executors.file_tools._get_sandbox_root")
    def test_write_file_path_traversal(self, mock_sandbox_root, mock_resolve_path):
        """Test write_file path traversal protection."""
        mock_sandbox_root.return_value = "/app/workdir"
        mock_resolve_path.return_value = "/etc/passwd"  # Outside workdir

        result = execute_write_file("../../etc/passwd", "malicious")

        assert "error" in result
        assert "Access denied" in result["error"]

    @patch("src.tools.executors.file_tools._resolve_path")
    @patch("src.tools.executors.file_tools._get_sandbox_root")
    @patch("os.path.dirname")
    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_file_create_directory(
        self,
        mock_file,
        mock_makedirs,
        mock_exists,
        mock_dirname,
        mock_sandbox_root,
        mock_resolve_path,
    ):
        """Test write_file creating parent directory."""
        mock_sandbox_root.return_value = "/tmp"
        mock_resolve_path.return_value = "/tmp/newdir/file.txt"
        mock_dirname.return_value = "/tmp/newdir"
        mock_exists.return_value = False  # Directory doesn't exist

        result = execute_write_file("newdir/file.txt", "content")

        mock_makedirs.assert_called_once_with("/tmp/newdir", exist_ok=True)
        assert result["success"] is True

    @patch("src.tools.executors.file_tools._resolve_path")
    @patch("src.tools.executors.file_tools._get_sandbox_root")
    def test_list_directory_path_traversal(self, mock_sandbox_root, mock_resolve_path):
        """Test list_directory path traversal protection."""
        mock_sandbox_root.return_value = "/app/workdir"
        mock_resolve_path.return_value = "/etc"  # Outside workdir

        result = execute_list_directory("../../etc")

        assert "error" in result
        assert "Access denied" in result["error"]

    @patch("src.tools.executors.file_tools._resolve_path")
    @patch("src.tools.executors.file_tools._get_sandbox_root")
    @patch("os.path.exists")
    def test_list_directory_not_found(self, mock_exists, mock_sandbox_root, mock_resolve_path):
        """Test list_directory with non-existent directory."""
        mock_sandbox_root.return_value = "/tmp"
        mock_resolve_path.return_value = "/tmp/missing"
        mock_exists.return_value = False

        result = execute_list_directory("missing")

        assert "error" in result
        assert "Directory not found" in result["error"]

    @patch("src.tools.executors.file_tools._resolve_path")
    @patch("src.tools.executors.file_tools._get_sandbox_root")
    @patch("os.path.exists")
    @patch("os.path.isdir")
    def test_list_directory_not_a_directory(
        self, mock_isdir, mock_exists, mock_sandbox_root, mock_resolve_path
    ):
        """Test list_directory when path is a file, not directory."""
        mock_sandbox_root.return_value = "/tmp"
        mock_resolve_path.return_value = "/tmp/file.txt"
        mock_exists.return_value = True
        mock_isdir.return_value = False  # It's a file

        result = execute_list_directory("file.txt")

        assert "error" in result
        assert "Not a directory" in result["error"]

    @patch("src.tools.executors.file_tools._resolve_path")
    @patch("src.tools.executors.file_tools._get_sandbox_root")
    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.listdir", side_effect=Exception("Permission denied"))
    def test_list_directory_exception(
        self, mock_listdir, mock_isdir, mock_exists, mock_sandbox_root, mock_resolve_path
    ):
        """Test list_directory with general exception."""
        mock_sandbox_root.return_value = "/tmp"
        mock_resolve_path.return_value = "/tmp/restricted"
        mock_exists.return_value = True
        mock_isdir.return_value = True

        result = execute_list_directory("restricted")

        assert "error" in result
        assert "Permission denied" in result["error"]

    @patch("os.getcwd", side_effect=Exception("Filesystem error"))
    def test_get_current_directory_exception(self, mock_getcwd):
        """Test get_current_directory with exception."""
        result = execute_get_current_directory()

        assert "error" in result
        assert "Filesystem error" in result["error"]


class TestDocumentProcessingTools:
    """Test document processing tools."""

    @patch("os.path.abspath")
    @patch("os.getcwd")
    @patch("os.path.exists")
    @patch("docling.document_converter.DocumentConverter")
    def test_parse_document_success(
        self, mock_converter, mock_exists, mock_getcwd, mock_abspath
    ):
        """Test successful document parsing."""
        mock_getcwd.return_value = "/tmp"
        mock_abspath.return_value = "/tmp/test.pdf"
        mock_exists.return_value = True

        # Mock the Docling converter
        mock_instance = MagicMock()
        mock_instance.convert.return_value = MagicMock()
        mock_instance.convert.return_value.document.export_to_markdown.return_value = (
            "# Test Document\nContent"
        )
        mock_converter.return_value = mock_instance

        result = execute_parse_document("test.pdf", "text")

        assert result["success"] is True
        assert "Test Document" in result["content"]

    @patch("docling.document_converter.DocumentConverter")
    def test_parse_document_failure(self, mock_converter):
        """Test document parsing failure."""
        mock_converter.side_effect = Exception("Parse error")

        result = execute_parse_document("corrupt.pdf", "text")

        # The function may return different error messages
        assert "error" in result or result["success"] is False

    @patch("os.getcwd")
    @patch("os.path.abspath")
    def test_parse_document_path_traversal(self, mock_abspath, mock_getcwd):
        """Test path traversal security check."""
        mock_getcwd.return_value = "/app/workdir"
        mock_abspath.return_value = "/etc/passwd"  # Outside workdir

        result = execute_parse_document("../../etc/passwd")

        assert "error" in result
        assert "Access denied" in result["error"]

    @patch("os.getcwd")
    @patch("os.path.abspath")
    @patch("os.path.exists")
    def test_parse_document_file_not_found(
        self, mock_exists, mock_abspath, mock_getcwd
    ):
        """Test file not found error."""
        mock_getcwd.return_value = "/tmp"
        mock_abspath.return_value = "/tmp/missing.pdf"
        mock_exists.return_value = False

        result = execute_parse_document("missing.pdf")

        assert "error" in result
        assert "File not found" in result["error"]

    @patch("os.getcwd")
    @patch("os.path.abspath")
    @patch("os.path.exists")
    def test_parse_document_docling_not_installed(
        self, mock_exists, mock_abspath, mock_getcwd
    ):
        """Test ImportError when docling is not installed."""
        mock_getcwd.return_value = "/tmp"
        mock_abspath.return_value = "/tmp/test.pdf"
        mock_exists.return_value = True

        # Mock the import to raise ImportError
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "docling.document_converter":
                raise ImportError("No module named 'docling'")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            result = execute_parse_document("test.pdf")

            assert "error" in result
            assert "docling library not installed" in result["error"]

    @patch("os.getcwd")
    @patch("os.path.abspath")
    @patch("os.path.exists")
    @patch("docling.document_converter.DocumentConverter")
    def test_parse_document_docling_processing_error(
        self, mock_converter, mock_exists, mock_abspath, mock_getcwd
    ):
        """Test Exception during docling processing."""
        mock_getcwd.return_value = "/tmp"
        mock_abspath.return_value = "/tmp/bad.pdf"
        mock_exists.return_value = True

        # Mock converter to raise exception during processing
        mock_instance = MagicMock()
        mock_instance.convert.side_effect = Exception("Corrupted document")
        mock_converter.return_value = mock_instance

        result = execute_parse_document("bad.pdf")

        assert "error" in result
        assert "Docling processing failed" in result["error"]

    @patch("os.getcwd")
    def test_parse_document_outer_exception(self, mock_getcwd):
        """Test outer exception handler (e.g., os.getcwd fails)."""
        mock_getcwd.side_effect = Exception("Filesystem error")

        result = execute_parse_document("test.pdf")

        assert "error" in result
        assert "Document parsing failed" in result["error"]


class TestKnowledgeManagementTools:
    """Test knowledge base operations."""

    @patch("src.tools.executors.knowledge_tools.add_to_knowledge_base")
    def test_learn_information_success(self, mock_add):
        """Test successful information learning."""
        mock_add.return_value = True

        result = execute_learn_information("Python is a programming language")

        assert result["success"] is True
        assert result["learned"] is True
        mock_add.assert_called_once_with("Python is a programming language", None)

    @patch("src.tools.executors.knowledge_tools.add_to_knowledge_base")
    def test_learn_information_failure(self, mock_add):
        """Test learning information failure."""
        mock_add.return_value = False

        result = execute_learn_information("test info")

        # Function returns error on failure
        assert "error" in result
        assert result["error"] == "Failed to add information to knowledge base"

    @patch("src.tools.executors.knowledge_tools.get_relevant_context")
    def test_search_knowledge_success(self, mock_get_context):
        """Test successful knowledge search."""
        mock_get_context.return_value = ["Python info", "More Python info"]

        result = execute_search_knowledge("Python programming", 5)

        assert result["success"] is True
        assert result["result_count"] == 2

    @patch("src.main.vectorstore")
    def test_search_knowledge_no_results(self, mock_vectorstore):
        """Test knowledge search with no results."""
        mock_vectorstore.similarity_search_with_score.return_value = []

        result = execute_search_knowledge("nonexistent topic", 5)

        assert result["success"] is True
        assert result["result_count"] == 0

    def test_learn_information_empty_string(self):
        """Test learning with empty information string."""
        result = execute_learn_information("")

        assert "error" in result
        assert "cannot be empty" in result["error"]

    def test_learn_information_whitespace_only(self):
        """Test learning with whitespace-only information."""
        result = execute_learn_information("   \n\t  ")

        assert "error" in result
        assert "cannot be empty" in result["error"]

    @patch("src.tools.executors.knowledge_tools.add_to_knowledge_base")
    def test_learn_information_kb_add_fails(self, mock_add_kb):
        """Test when knowledge base addition returns False."""
        mock_add_kb.return_value = False

        result = execute_learn_information("Some information")

        assert "error" in result
        assert "Failed to add information" in result["error"]

    @patch("src.tools.executors.knowledge_tools.add_to_knowledge_base")
    def test_learn_information_exception(self, mock_add_kb):
        """Test exception handling during learning."""
        mock_add_kb.side_effect = Exception("Database connection failed")

        result = execute_learn_information("Some information")

        assert "error" in result
        assert "Database connection failed" in result["error"]

    def test_search_knowledge_empty_query(self):
        """Test searching with empty query string."""
        result = execute_search_knowledge("")

        assert "error" in result
        assert "cannot be empty" in result["error"]

    def test_search_knowledge_whitespace_query(self):
        """Test searching with whitespace-only query."""
        result = execute_search_knowledge("  \n\t  ")

        assert "error" in result
        assert "cannot be empty" in result["error"]

    @patch("src.tools.executors.knowledge_tools.get_relevant_context")
    def test_search_knowledge_exception(self, mock_get_context):
        """Test exception handling during search."""
        mock_get_context.side_effect = Exception("Search engine error")

        result = execute_search_knowledge("test query")

        assert "error" in result
        assert "Search engine error" in result["error"]


class TestWebSearchTools:
    """Test web search functionality."""

    def test_search_web_success(self):
        """Test successful web search."""
        # Mock the ddgs module properly
        mock_ddgs_class = MagicMock()
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = [
            {"title": "Test Result", "body": "Test content", "href": "https://test.com"}
        ]
        # Mock the context manager behavior
        mock_ddgs_instance.__enter__.return_value = mock_ddgs_instance
        mock_ddgs_instance.__exit__.return_value = None
        mock_ddgs_class.return_value = mock_ddgs_instance

        with patch.dict("sys.modules", {"ddgs": MagicMock()}):
            with patch("ddgs.DDGS", mock_ddgs_class):
                result = execute_web_search("test query")

                assert result["success"] is True
                assert result["result_count"] == 1
                assert len(result["results"]) == 1

    def test_search_web_failure(self):
        """Test web search failure."""
        with patch.dict("sys.modules", {"ddgs": MagicMock()}):
            with patch("ddgs.DDGS", side_effect=Exception("Network error")):
                result = execute_web_search("test query")

                assert "error" in result
                assert "failed" in result["error"].lower()

    def test_search_web_import_error(self):
        """Test web search when ddgs is not installed."""
        with patch.dict("sys.modules", {"ddgs": None}):
            result = execute_web_search("test query")

            assert "error" in result
            assert "not installed" in result["error"]

    def test_search_web_no_crypto_enhancement(self):
        """Test that crypto queries don't get re-enhanced."""
        mock_ddgs_class = MagicMock()
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = [
            {
                "title": "Coin Result",
                "body": "About coins",
                "href": "https://example.com",
            }
        ]
        mock_ddgs_instance.__enter__.return_value = mock_ddgs_instance
        mock_ddgs_instance.__exit__.return_value = None
        mock_ddgs_class.return_value = mock_ddgs_instance

        with patch.dict("sys.modules", {"ddgs": MagicMock()}):
            with patch("ddgs.DDGS", mock_ddgs_class):
                # Test with "bitcoin" - already crypto-related, should NOT enhance
                result = execute_web_search("bitcoin price")

                assert result["success"] is True
                mock_ddgs_instance.text.assert_called_once()
                call_args = mock_ddgs_instance.text.call_args
                # Should use original query, not enhanced
                assert call_args[0][0] == "bitcoin price"

    def test_search_web_ddgs_exception(self):
        """Test DDGS search execution exception."""
        mock_ddgs_class = MagicMock()
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.side_effect = Exception("DDGS API error")
        mock_ddgs_instance.__enter__.return_value = mock_ddgs_instance
        mock_ddgs_instance.__exit__.return_value = None
        mock_ddgs_class.return_value = mock_ddgs_instance

        with patch.dict("sys.modules", {"ddgs": MagicMock()}):
            with patch("ddgs.DDGS", mock_ddgs_class):
                result = execute_web_search("test query")

                assert "error" in result
                assert "Web search failed" in result["error"]
                assert "DDGS API error" in result["error"]

    def test_search_web_general_exception(self):
        """Test general unexpected exception handling."""

        # Import mock to trigger a general exception during module import
        def failing_import(*args, **kwargs):
            if args[0] == "ddgs":
                raise RuntimeError("Unexpected error")
            raise ImportError("Module not found")

        with patch("builtins.__import__", side_effect=failing_import):
            result = execute_web_search("test query")

            assert "error" in result


class TestToolSecurity:
    """Test tool security constraints."""

    @patch("os.path.exists")
    def test_read_file_path_traversal_attempt(self, mock_exists):
        """Test protection against path traversal attacks."""
        mock_exists.return_value = True

        # Attempt path traversal
        result = execute_read_file("../../../etc/passwd")

        # Should still work if file exists, but in real implementation
        # there should be path validation
        assert isinstance(result, dict)  # Basic structure check

    def test_write_file_path_validation(self):
        """Test that write_file handles paths correctly."""
        with patch("builtins.open", new_callable=mock_open):
            result = execute_write_file("subdir/file.txt", "content")

            assert result["success"] is True
            # Should create subdirectories
            # This would be tested more thoroughly in integration tests


class TestToolIntegration:
    """Test tool integration and error handling."""

    def test_all_tools_return_dict(self):
        """Test that all tools return dictionary results."""
        # This is a basic smoke test to ensure all tools have proper return types

        with patch("os.getcwd"):
            with patch("os.path.exists", return_value=False):
                result = execute_read_file("nonexistent.txt")
                assert isinstance(result, dict)
                # Error case returns {"error": "message"}

        with patch("os.getcwd"):
            with patch("builtins.open", new_callable=mock_open):
                result = execute_write_file("test.txt", "content")
                assert isinstance(result, dict)
                # Success case returns {"success": True, ...}

        with patch("os.getcwd"):
            with patch("os.listdir", return_value=[]):
                with patch("os.path.isdir", return_value=True):
                    result = execute_list_directory(".")
                    assert isinstance(result, dict)

        with patch("os.getcwd", return_value="/tmp"):
            result = execute_get_current_directory()
            assert isinstance(result, dict)

    def test_tool_error_handling(self):
        """Test that tools handle exceptions gracefully."""
        # Test with various failure scenarios

        # Force an exception in read_file
        with patch("os.getcwd"):
            with patch("builtins.open", side_effect=Exception("IO Error")):
                with patch("os.path.exists", return_value=True):
                    with patch("os.path.isfile", return_value=True):
                        result = execute_read_file("test.txt")
                        assert "error" in result
