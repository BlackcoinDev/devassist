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
Integration tests for auto-learn functionality in application startup.
"""

from unittest.mock import MagicMock, patch


class TestAutoLearnIntegration:
    """Integration tests for auto-learn in application startup."""

    def test_auto_learn_startup_enabled(self):
        """Test auto-learn runs when AUTO_LEARN_ON_STARTUP is enabled."""
        from src.main import initialize_application

        # Mock the config to enable auto-learn
        mock_config = MagicMock()
        mock_config.auto_learn_on_startup = True

        # Mock the auto-learn function
        mock_auto_learn = MagicMock()

        with (
            patch("src.main.get_config", return_value=mock_config),
            patch("src.main.initialize_tools", return_value=None),
            patch("src.main.initialize_llm", return_value=True),
            patch("src.main.initialize_vectordb", return_value=True),
            patch("src.main.initialize_auto_learning", side_effect=mock_auto_learn),
            patch("src.main.initialize_user_memory", return_value=True),
            patch("src.main.initialize_mcp", return_value=True),
        ):
            # Test initialization with auto-learn enabled
            result = initialize_application()
            assert result is True

            # Verify auto-learn was called
            mock_auto_learn.assert_called_once()
            # Verify it was called with CLIProgress callback
            call_args = mock_auto_learn.call_args
            assert call_args is not None
            assert "progress_callback" in call_args.kwargs
            # The callback should be a method from CLIProgress instance
            callback = call_args.kwargs["progress_callback"]
            assert callable(callback)

    def test_auto_learn_startup_disabled(self):
        """Test auto-learn does not run when AUTO_LEARN_ON_STARTUP is disabled."""
        from src.main import initialize_application

        # Mock the config to disable auto-learn
        mock_config = MagicMock()
        mock_config.auto_learn_on_startup = False

        # Mock the auto-learn function
        # Mock the auto-learn function - should not be called
        mock_auto_learn = MagicMock()

        with (
            patch("src.main.get_config", return_value=mock_config),
            patch("src.main.initialize_tools", return_value=None),
            patch("src.main.initialize_llm", return_value=True),
            patch("src.main.initialize_vectordb", return_value=True),
            patch(
                "src.learning.auto_learn.initialize_auto_learning",
                side_effect=mock_auto_learn,
            ),
            patch("src.learning.progress.CLIProgress", return_value=MagicMock()),
            patch("src.main.initialize_user_memory", return_value=True),
            patch("src.main.initialize_mcp", return_value=True),
        ):
            # Test initialization with auto-learn disabled
            result = initialize_application()
            assert result is True

            # Verify auto-learn was NOT called
            mock_auto_learn.assert_not_called()

    def test_auto_learn_failure_graceful(self):
        """Test application continues when auto-learn fails."""
        from src.main import initialize_application

        # Mock the config to enable auto-learn
        mock_config = MagicMock()
        mock_config.auto_learn_on_startup = True

        # Mock the auto-learn function to raise an exception
        def failing_auto_learn(**kwargs):
            raise Exception("ChromaDB connection failed")

        with (
            patch("src.main.get_config", return_value=mock_config),
            patch("src.main.initialize_tools", return_value=None),
            patch("src.main.initialize_llm", return_value=True),
            patch("src.main.initialize_vectordb", return_value=True),
            patch("src.main.initialize_auto_learning", side_effect=failing_auto_learn),
            patch("src.main.initialize_user_memory", return_value=True),
            patch("src.main.initialize_mcp", return_value=True),
        ):
            # Test initialization with auto-learn failure
            result = initialize_application()

            # Application should still succeed even if auto-learn fails
            assert result is True

    def test_auto_learn_logging(self):
        """Test auto-learn logging with timing."""
        from src.main import initialize_application

        from datetime import datetime

        # Mock the config to enable auto-learn
        mock_config = MagicMock()
        mock_config.auto_learn_on_startup = True

        # Mock logger and auto-learn function
        mock_logger = MagicMock()
        mock_auto_learn = MagicMock()

        # Mock datetime to control timing
        mock_start_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_end_time = datetime(2024, 1, 1, 12, 0, 1)  # 1 second later

        with (
            patch("src.main.get_config", return_value=mock_config),
            patch("src.main.get_logger", return_value=mock_logger),
            patch("src.main.logger", mock_logger),
            patch("src.main.datetime") as mock_datetime,
            patch("src.main.initialize_tools", return_value=None),
            patch("src.main.initialize_llm", return_value=True),
            patch("src.main.initialize_vectordb", return_value=True),
            patch("src.main.initialize_auto_learning", side_effect=mock_auto_learn),
            patch("src.main.initialize_user_memory", return_value=True),
            patch("src.main.initialize_mcp", return_value=True),
        ):
            # Setup datetime mock to return our controlled times
            mock_datetime.now.side_effect = [mock_start_time, mock_end_time]

            # Test initialization
            result = initialize_application()
            assert result is True

            # Verify logging calls
            mock_logger.info.assert_any_call(
                "📚 Auto-learning project documentation..."
            )
            mock_logger.info.assert_any_call("✅ Auto-learn completed in 1.00 seconds")

    def test_auto_learn_error_logging(self):
        """Test auto-learn error logging."""
        from src.main import initialize_application

        # Mock the config to enable auto-learn
        mock_config = MagicMock()
        mock_config.auto_learn_on_startup = True

        # Mock logger and auto-learn function to fail
        mock_logger = MagicMock()

        def failing_auto_learn(**kwargs):
            raise Exception("Test error message")

        with (
            patch("src.main.get_config", return_value=mock_config),
            patch("src.main.get_logger", return_value=mock_logger),
            patch("src.main.logger", mock_logger),
            patch("src.main.initialize_tools", return_value=None),
            patch("src.main.initialize_llm", return_value=True),
            patch("src.main.initialize_vectordb", return_value=True),
            patch("src.main.initialize_auto_learning", side_effect=failing_auto_learn),
            patch("src.main.initialize_user_memory", return_value=True),
            patch("src.main.initialize_mcp", return_value=True),
        ):
            # Test initialization
            result = initialize_application()
            assert result is True

            # Verify error logging
            mock_logger.warning.assert_called_with(
                "⚠️ Auto-learn failed: Test error message"
            )


class TestAutoLearnInitializationOrder:
    """Test that auto-learn runs at the correct point in initialization."""

    def test_auto_learn_after_vectordb_before_memory(self):
        """Test auto-learn runs after vectordb initialization but before user memory."""
        from src.main import initialize_application

        # Mock the config to enable auto-learn
        mock_config = MagicMock()
        mock_config.auto_learn_on_startup = True

        # Track call order
        call_order = []

        def track_init(name):
            def wrapper(*args, **kwargs):
                call_order.append(name)
                return True if name != "auto_learn" else None

            return wrapper

        with (
            patch("src.main.get_config", return_value=mock_config),
            patch("src.main.initialize_tools", side_effect=track_init("tools")),
            patch("src.main.initialize_llm", side_effect=track_init("llm")),
            patch("src.main.initialize_vectordb", side_effect=track_init("vectordb")),
            patch(
                "src.main.initialize_auto_learning",
                side_effect=track_init("auto_learn"),
            ),
            patch("src.main.initialize_user_memory", side_effect=track_init("memory")),
            patch("src.main.initialize_mcp", side_effect=track_init("mcp")),
        ):
            # Test initialization
            result = initialize_application()
            assert result is True

            # Verify call order
            expected_order = ["tools", "llm", "vectordb", "auto_learn", "memory", "mcp"]
            assert call_order == expected_order
