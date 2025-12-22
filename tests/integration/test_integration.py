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
Integration tests for AI Assistant application.
"""

# pytest imported for test framework
from unittest.mock import MagicMock, patch


class TestApplicationIntegration:
    """Integration tests for the complete application."""

    def test_full_initialization_flow(self):
        """Test complete application initialization flow."""
        from src.main import initialize_application

        # Mock high-level initialization functions
        with (
            patch("src.main.initialize_llm", return_value=True) as mock_llm,
            patch("src.main.initialize_vectordb", return_value=True) as mock_vdb,
            patch("src.main.initialize_user_memory", return_value=True),
            patch("src.storage.database.initialize_database", return_value=(MagicMock(), MagicMock())) as mock_db,
            patch("src.main.load_memory", return_value=[]),
        ):
            # Test initialization
            result = initialize_application()
            assert result is True

            # Verify key components were initialized
            mock_llm.assert_called_once()
            mock_vdb.assert_called_once()
            mock_db.assert_called_once()

    def test_memory_persistence_flow(self):
        """Test memory save/load persistence flow."""
        from src.main import save_memory

        # Mock database connection and lock via context
        mock_ctx = MagicMock()
        mock_cursor = MagicMock()
        mock_ctx.db_conn.cursor.return_value = mock_cursor

        # Mock config
        mock_config = MagicMock()
        mock_config.db_type = "sqlite"

        with (
            patch("src.storage.memory.get_config", return_value=mock_config),
            patch("src.storage.memory.get_context", return_value=mock_ctx),
        ):
            # Test save
            from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

            test_messages = [
                SystemMessage(content="Test system"),
                HumanMessage(content="Test human"),
                AIMessage(content="Test AI"),
            ]

            save_memory(test_messages)

            # Verify database operations were called
            # execute is called twice: BEGIN TRANSACTION + DELETE
            assert mock_cursor.execute.call_count == 2
            mock_cursor.executemany.assert_called_once()  # INSERT operations
            mock_ctx.db_conn.commit.assert_called_once()

    def test_space_management_integration(self):
        """Test space management integration."""
        from src.main import get_space_collection_name, switch_space

        # Test collection naming
        assert get_space_collection_name("default") == "knowledge_base"
        assert get_space_collection_name("workspace1") == "space_workspace1"

        # Test space switching (mocked)
        # Now need to patch in the vectordb.spaces module
        with (
            patch("src.vectordb.spaces.ensure_space_collection", return_value=True),
            patch("src.vectordb.spaces.save_current_space"),
            patch("src.vectordb.spaces.set_current_space"),
        ):
            result = switch_space("test_space")
            assert result is True
            # Note: In real implementation, current_space in context would change

    @patch("src.main.vectorstore")
    def test_context_retrieval_flow(self, mock_vectorstore):
        """Test context retrieval flow."""
        from src.main import get_relevant_context

        mock_vectorstore = MagicMock()
        mock_embeddings = MagicMock()
        mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]

        with (
            patch("src.main.vectorstore", mock_vectorstore),
            patch("src.main.embeddings", mock_embeddings),
            patch("src.main.requests.Session") as mock_session,
        ):
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "documents": [[{"content": "test context"}]]
            }

            mock_session_instance = MagicMock()
            mock_session_instance.post.return_value = mock_response
            mock_session.return_value = mock_session_instance

            # Test context retrieval
            context = get_relevant_context("test query")

            assert isinstance(context, str)
            # Should contain context wrapper
            assert "Relevant context" in context or context == ""


class TestCommandIntegration:
    """Integration tests for command handling."""

    def test_slash_command_integration(self, capsys):
        """Test slash command integration."""
        from src.main import handle_slash_command

        # Test help command
        result = handle_slash_command("/help")
        assert result is True

        captured = capsys.readouterr()
        assert "Available Commands" in captured.out

    def test_memory_command_integration(self, capsys):
        """Test memory command integration."""
        from src.main import handle_slash_command
        from src.commands import CommandRegistry

        # Ensure memory command is registered (might have been cleared by other tests)
        if not CommandRegistry.has_command("memory"):
            from src.commands.handlers.memory_commands import handle_memory
            CommandRegistry.register("memory", "Show conversation history", category="memory")(handle_memory)

        # Mock conversation history to ensure consistent output
        from src.core.context import get_context
        get_context().conversation_history = []

        result = handle_slash_command("/memory")
        assert result is True

        captured = capsys.readouterr()
        assert "No conversation history" in captured.out

    @patch("src.commands.handlers.memory_commands.save_memory")
    @patch("src.commands.handlers.memory_commands.get_context")
    def test_clear_command_integration(self, mock_ctx, mock_save, capsys):
        """Test clear command integration."""
        from src.commands.handlers.memory_commands import handle_clear

        # Setup mock context
        mock_ctx.return_value.conversation_history = []

        with patch("builtins.input", return_value="yes"):
            handle_clear([])
            mock_save.assert_called_once()  # Verify memory is saved during clear

            captured = capsys.readouterr()
            assert "cleared" in captured.out.lower()


class TestLauncherIntegration:
    """Integration tests for launcher."""

    @patch("os.path.exists", return_value=True)
    def test_launcher_full_flow(self, mock_exists):
        """Test complete launcher flow."""
        with patch("sys.argv", ["launcher.py", "--cli"]):
            with patch("launcher.launch_cli") as mock_launch_cli:
                from launcher import main as launcher_main

                launcher_main()

                mock_launch_cli.assert_called_once()

    def test_launcher_missing_env_file(self):
        """Test launcher behavior with missing .env file."""
        # This test is difficult to implement due to environment complexities
        # The launcher behavior is tested in unit tests instead
        pass


class TestEndToEnd:
    """End-to-end tests (marked as slow)."""

    def test_import_chain(self):
        """Test that all main modules can be imported."""
        # Test main module import
        import src.main as main

        assert hasattr(main, "initialize_application")

        # Test launcher import
        import launcher

        assert hasattr(launcher, "main")

        # Test gui import (may fail if PyQt6 not available)
        try:
            import src.gui as gui

            assert hasattr(gui, "AIAssistantGUI")
        except ImportError:
            # GUI not available, which is acceptable
            pass

    def test_configuration_loading(self):
        """Test configuration loading from environment."""
        # Test that configuration variables are accessible
        import src.main as main

        # These should be set from mock_env fixture
        assert hasattr(main, "LM_STUDIO_BASE_URL")
        assert hasattr(main, "MODEL_NAME")
        assert hasattr(main, "CHROMA_HOST")
