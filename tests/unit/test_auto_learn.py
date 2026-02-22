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
Comprehensive unit tests for the auto-learn module.

This module tests all functions in src/learning/auto_learn.py including:
- initialize_auto_learning() - Main entry point
- process_markdown_file() - Single file processing
- check_deduplication() - Deduplication logic
- store_in_knowledge_base() - Knowledge base storage
- extract_insights() - Content analysis
- Background threading and error handling
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


def test_fixtures_import():
    """Test that fixtures can be imported successfully."""
    # Import the fixtures locally to verify availability
    from tests.fixtures.auto_learn_fixtures import (
        mock_chroma_client,
        mock_embeddings,
        sample_md_content,
    )

    assert callable(mock_chroma_client)
    assert callable(mock_embeddings)
    assert callable(sample_md_content)


class TestAutoLearnManager:
    """Test the AutoLearnManager class functionality."""

    @pytest.fixture
    def manager(self):
        """Create a fresh AutoLearnManager for each test."""
        from src.learning.auto_learn import AutoLearnManager

        return AutoLearnManager()

    @pytest.fixture
    def mock_context(self):
        """Mock application context."""
        mock_ctx = MagicMock()
        mock_ctx.vectorstore = MagicMock()
        mock_ctx.current_space = "default"
        return mock_ctx

    def test_initialize_auto_learning_already_running(self, manager):
        """Test that initialize_auto_learning returns False if already running."""
        manager._running = True
        result = manager.initialize_auto_learning()
        assert result is False

    @patch("src.learning.auto_learn.get_context")
    def test_initialize_auto_learning_success(self, mock_get_context, manager):
        """Test successful initialization of auto-learning."""
        mock_get_context.return_value = MagicMock()

        result = manager.initialize_auto_learning()
        assert result is True
        assert manager._running is True
        assert manager._thread is not None
        assert manager._thread.name == "AutoLearnBackgroundTask"
        assert manager._thread.daemon is True

    def test_check_deduplication(self, manager):
        """Test deduplication logic."""
        # Test with empty processed hashes
        assert manager.check_deduplication("test_hash") is False

        # Test with existing hash
        manager._processed_hashes.add("existing_hash")
        assert manager.check_deduplication("existing_hash") is True
        assert manager.check_deduplication("new_hash") is False

    def test_extract_insights_simple_content(self, manager, sample_md_content):
        """Test insight extraction with simple markdown content."""
        simple_content = sample_md_content["simple"]
        insights = manager.extract_insights(simple_content)

        assert len(insights) > 0
        assert any("Header: Simple Markdown" in insight for insight in insights)

    def test_extract_insights_complex_content(self, manager, sample_md_content):
        """Test insight extraction with complex markdown content."""
        complex_content = sample_md_content["complex"]
        insights = manager.extract_insights(complex_content)

        assert len(insights) > 0
        assert any("Header:" in insight for insight in insights)
        assert any("Code Block" in insight for insight in insights)
        assert any("List Items:" in insight for insight in insights)

    def test_extract_insights_empty_content(self, manager):
        """Test insight extraction with empty content."""
        insights = manager.extract_insights("")
        assert insights == ["No specific insights extracted"]

    def test_extract_insights_with_code(self, manager, sample_md_content):
        """Test insight extraction with code blocks."""
        code_content = sample_md_content["with_code"]
        insights = manager.extract_insights(code_content)

        assert any("Code Block" in insight for insight in insights)

    def test_process_markdown_file_nonexistent(self, manager):
        """Test processing a non-existent file."""
        fake_path = Path("/nonexistent/file.md")

        with pytest.raises(FileNotFoundError):
            manager.process_markdown_file(fake_path)

    def test_process_markdown_file_not_a_file(self, manager):
        """Test processing a path that's not a file."""
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir)

            with pytest.raises(ValueError):
                manager.process_markdown_file(dir_path)

    def test_process_markdown_file_empty_content(self, manager):
        """Test processing a file with empty content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            # Create empty file
            temp_path = Path(f.name)

        try:
            result = manager.process_markdown_file(temp_path)
            assert result["status"] == "skipped"
            assert result["reason"] == "empty_content"
        finally:
            temp_path.unlink()

    @patch("src.learning.auto_learn.compute_content_hash")
    def test_process_markdown_file_hash_failure(self, mock_hash, manager):
        """Test processing when hash computation fails."""
        mock_hash.return_value = None

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test Content")
            temp_path = Path(f.name)

        try:
            result = manager.process_markdown_file(temp_path)
            assert result["status"] == "skipped"
            assert result["reason"] == "hash_computation_failed"
        finally:
            temp_path.unlink()

    def test_process_markdown_file_duplicate(self, manager):
        """Test processing a duplicate file."""
        # Add a hash to processed hashes
        test_hash = "test_hash_1234"
        manager._processed_hashes.add(test_hash)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test Content")
            temp_path = Path(f.name)

        try:
            with patch(
                "src.learning.auto_learn.compute_content_hash", return_value=test_hash
            ):
                result = manager.process_markdown_file(temp_path)
                assert result["status"] == "skipped"
                assert result["reason"] == "duplicate_content"
        finally:
            temp_path.unlink()

    @patch("src.learning.auto_learn.add_to_knowledge_base")
    def test_process_markdown_file_success(self, mock_add_to_kb, manager):
        """Test successful processing of a markdown file."""
        mock_add_to_kb.return_value = True

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test Content\n\nThis is test content.")
            temp_path = Path(f.name)

        try:
            with patch(
                "src.learning.auto_learn.compute_content_hash", return_value="test_hash"
            ):
                result = manager.process_markdown_file(temp_path)

                assert result["status"] == "success"
                assert result["file_path"] == str(temp_path)
                assert result["content_hash"] == "test_hash"
                assert "insights" in result

                # Verify add_to_knowledge_base was called
                mock_add_to_kb.assert_called_once()
                call_args = mock_add_to_kb.call_args
                assert "Test Content" in call_args[0][0]  # Content
                assert call_args[0][1]["source"] == str(temp_path)  # Metadata
                assert call_args[0][1]["auto_learned"] is True
        finally:
            temp_path.unlink()

    @patch("src.learning.auto_learn.add_to_knowledge_base")
    def test_process_markdown_file_storage_failure(self, mock_add_to_kb, manager):
        """Test processing when storage fails."""
        mock_add_to_kb.return_value = False

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test Content")
            temp_path = Path(f.name)

        try:
            with patch(
                "src.learning.auto_learn.compute_content_hash", return_value="test_hash"
            ):
                result = manager.process_markdown_file(temp_path)

                assert result["status"] == "failed"
                assert result["reason"] == "storage_failed"
        finally:
            temp_path.unlink()

    @patch("src.learning.auto_learn.get_context")
    def test_store_in_knowledge_base_success(self, mock_get_context, manager):
        """Test successful storage in knowledge base."""
        mock_ctx = MagicMock()
        mock_get_context.return_value = mock_ctx

        with patch("src.learning.auto_learn.add_to_knowledge_base", return_value=True):
            result = manager.store_in_knowledge_base(
                "test content", {"source": "test.md"}
            )

            assert result is True

    @patch("src.learning.auto_learn.get_context")
    def test_store_in_knowledge_base_failure(self, mock_get_context, manager):
        """Test failed storage in knowledge base."""
        mock_ctx = MagicMock()
        mock_get_context.return_value = mock_ctx

        with patch("src.learning.auto_learn.add_to_knowledge_base", return_value=False):
            result = manager.store_in_knowledge_base(
                "test content", {"source": "test.md"}
            )

            assert result is False

    def test_is_running(self, manager):
        """Test is_running method."""
        assert manager.is_running() is False
        manager._running = True
        assert manager.is_running() is True

    def test_get_stats(self, manager):
        """Test get_stats method."""
        manager._success_count = 5
        manager._error_count = 2
        manager._processed_hashes.add("hash1")
        manager._processed_hashes.add("hash2")
        manager._running = True

        stats = manager.get_stats()
        assert stats["success_count"] == 5
        assert stats["error_count"] == 2
        assert stats["processed_files"] == 2
        assert stats["running"] is True

    def test_stop_not_running(self, manager):
        """Test stopping when not running."""
        manager.stop()
        assert manager.is_running() is False

    @patch("threading.Thread")
    def test_stop_running(self, mock_thread, manager):
        """Test stopping when running."""
        manager._running = True
        mock_thread_instance = MagicMock()
        mock_thread_instance.is_alive.return_value = True
        manager._thread = mock_thread_instance

        manager.stop()

        assert manager._running is False
        mock_thread_instance.join.assert_called_once_with(timeout=5)


class TestModuleFunctions:
    """Test module-level functions."""

    @patch("src.learning.auto_learn.AutoLearnManager")
    def test_get_auto_learn_manager(self, mock_manager_class):
        """Test getting the auto-learn manager singleton."""
        from src.learning.auto_learn import get_auto_learn_manager

        mock_manager_instance = MagicMock()
        mock_manager_class.return_value = mock_manager_instance

        manager = get_auto_learn_manager()
        assert manager == mock_manager_instance
        mock_manager_class.assert_called_once()

    @patch("src.learning.auto_learn.get_auto_learn_manager")
    def test_initialize_auto_learning_module_function(self, mock_get_manager):
        """Test the module-level initialize_auto_learning function."""
        from src.learning.auto_learn import initialize_auto_learning

        mock_manager = MagicMock()
        mock_manager.initialize_auto_learning.return_value = True
        mock_get_manager.return_value = mock_manager

        result = initialize_auto_learning()
        assert result is True
        mock_manager.initialize_auto_learning.assert_called_once_with(None)

    @patch("src.learning.auto_learn.get_auto_learn_manager")
    def test_initialize_auto_learning_with_callback(self, mock_get_manager):
        """Test the module-level initialize_auto_learning function with callback."""
        from src.learning.auto_learn import initialize_auto_learning

        mock_manager = MagicMock()
        mock_manager.initialize_auto_learning.return_value = True
        mock_get_manager.return_value = mock_manager

        test_callback = MagicMock()
        result = initialize_auto_learning(progress_callback=test_callback)

        assert result is True
        mock_manager.initialize_auto_learning.assert_called_once_with(test_callback)


class TestBackgroundThreading:
    """Test background threading functionality."""

    @pytest.fixture
    def manager(self):
        """Create a fresh AutoLearnManager for each test."""
        from src.learning.auto_learn import AutoLearnManager

        return AutoLearnManager()

    @patch("threading.Thread")
    @patch("src.learning.auto_learn.discover_markdown_files")
    def test_background_task_no_files(self, mock_discover, mock_thread, manager):
        """Test background task when no files are found."""
        mock_discover.return_value = []

        manager.initialize_auto_learning()

        # Wait for background thread to complete
        if manager._thread:
            manager._thread.join()

        # Verify outcomes instead of thread state
        # Background thread should have completed and processed counts should be correct
        stats = manager.get_stats()
        assert stats["success_count"] == 0  # No files processed
        assert stats["error_count"] == 0  # No errors

    @patch("threading.Thread")
    @patch("src.learning.auto_learn.discover_markdown_files")
    @patch("src.learning.auto_learn.AutoLearnManager.process_markdown_file")
    def test_background_task_with_files(
        self, mock_process, mock_discover, mock_thread, manager
    ):
        """Test background task with files."""
        mock_discover.return_value = [Path("test1.md"), Path("test2.md")]
        mock_process.return_value = {"status": "success"}

        manager.initialize_auto_learning()

        # Wait for background thread to complete
        if manager._thread:
            manager._thread.join()

        # Verify outcomes instead of thread state
        # Since we mocked threading.Thread, we need to manually run the background task
        manager._auto_learn_background_task()
        stats = manager.get_stats()
        assert stats["success_count"] == 2  # Both files processed successfully
        assert stats["error_count"] == 0  # No errors

    @patch("threading.Thread")
    @patch("src.learning.auto_learn.discover_markdown_files")
    @patch("src.learning.auto_learn.AutoLearnManager.process_markdown_file")
    def test_background_task_stop_early(
        self, mock_process, mock_discover, mock_thread, manager
    ):
        """Test background task stopped early."""
        mock_discover.return_value = [Path("test1.md"), Path("test2.md")]

        # Start the process
        manager.initialize_auto_learning()

        # Stop it immediately
        manager.stop()

        # Wait for thread to finish
        if manager._thread:
            manager._thread.join()

        assert manager.is_running() is False


class TestErrorHandling:
    """Test error handling in auto-learn processes."""

    @pytest.fixture
    def manager(self):
        """Create a fresh AutoLearnManager for each test."""
        from src.learning.auto_learn import AutoLearnManager

        return AutoLearnManager()

    @patch("threading.Thread")
    @patch("src.learning.auto_learn.discover_markdown_files")
    def test_background_task_exception(
        self, mock_discover, mock_thread, manager, caplog
    ):
        """Test background task handles exceptions gracefully."""
        mock_discover.side_effect = Exception("Test exception")

        manager.initialize_auto_learning()

        # Wait for background thread to complete
        if manager._thread:
            manager._thread.join()
        # Verify outcomes instead of thread state
        # Since we mocked threading.Thread, we need to manually run the background task
        manager._auto_learn_background_task()
        stats = manager.get_stats()
        assert stats["success_count"] == 0  # No files processed due to exception
        assert stats["error_count"] > 0  # Exception should be counted
        assert manager._error_count > 0
        assert "Auto-learning failed" in caplog.text

    def test_process_file_exception(self, manager, caplog):
        """Test that file processing exceptions are handled gracefully."""
        # Create a file that will cause an exception during processing
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test Content")
            temp_path = Path(f.name)

        try:
            # Mock process_markdown_file to raise an exception
            with patch.object(
                manager,
                "process_markdown_file",
                side_effect=Exception("Processing error"),
            ):
                with patch("threading.Thread"):
                    manager.initialize_auto_learning()
                    # Since we mocked threading.Thread, the background task won't run
                    # So we need to simulate the error by directly calling the background task
                    manager._auto_learn_background_task()
                    # Wait for background thread to complete
                    if manager._thread:
                        manager._thread.join()

                    # Wait for background thread to complete
                    if manager._thread:
                        manager._thread.join()
        finally:
            temp_path.unlink()
        # Verify outcomes - error should be counted
        # Since we mocked the background thread, the error won't be processed
        # So we need to verify the error would be counted by checking the stats
        stats = manager.get_stats()
        assert stats["error_count"] > 0  # Error should be counted

    def test_progress_callback_exception(self, manager, caplog):
        """Test that progress callback exceptions don't break the process."""

        def failing_callback(message):
            raise Exception("Callback failed")

        manager._progress_callback = failing_callback
        manager._log_progress("Test message")

        # Should log warning but not raise exception
        assert "Progress callback failed" in caplog.text
