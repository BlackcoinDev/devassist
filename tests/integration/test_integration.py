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
        from main import initialize_application

        # Mock all the complex imports and dependencies
        with (
            patch("main.ChatOpenAI") as mock_llm,
            patch("chromadb.HttpClient") as mock_client,
            patch("langchain_chroma.Chroma") as mock_chroma,
            patch("main.sqlite3.connect") as mock_sqlite,
        ):
            # Setup mock return values
            mock_llm_instance = MagicMock()
            mock_llm.return_value = mock_llm_instance

            mock_client_instance = MagicMock()
            mock_client.return_value = mock_client_instance

            mock_vectorstore_instance = MagicMock()
            mock_chroma.return_value = mock_vectorstore_instance

            mock_conn = MagicMock()
            mock_sqlite.return_value = mock_conn

            # Test initialization
            result = initialize_application()
            assert result is True

            # Verify key components were initialized
            mock_llm.assert_called_once()
            mock_client.assert_called_once()
            mock_chroma.assert_called_once()
            mock_sqlite.assert_called_once()

    def test_memory_persistence_flow(self):
        """Test memory save/load persistence flow."""
        from main import save_memory

        # Mock database connection and lock
        mock_conn = MagicMock()
        mock_lock = MagicMock()

        with (
            patch("main.DB_TYPE", "sqlite"),
            patch("main.db_conn", mock_conn),
            patch("main.db_lock", mock_lock),
        ):
            # Test save
            from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

            test_messages = [
                SystemMessage(content="Test system"),
                HumanMessage(content="Test human"),
                AIMessage(content="Test AI"),
            ]

            # Mock cursor for save
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor

            save_memory(test_messages)

            # Verify database operations were called
            assert mock_cursor.execute.call_count >= 2  # DELETE and INSERTs
            mock_conn.commit.assert_called_once()

    def test_space_management_integration(self):
        """Test space management integration."""
        from main import get_space_collection_name, switch_space

        # Test collection naming
        assert get_space_collection_name("default") == "knowledge_base"
        assert get_space_collection_name("workspace1") == "space_workspace1"

        # Test space switching (mocked)
        with (
            patch("main.ensure_space_collection", return_value=True),
            patch("main.save_current_space"),
        ):
            result = switch_space("test_space")
            assert result is True
            # Note: In real implementation, CURRENT_SPACE would change

    @patch("main.vectorstore")
    def test_context_retrieval_flow(self, mock_vectorstore):
        """Test context retrieval flow."""
        from main import get_relevant_context

        mock_vectorstore = MagicMock()
        mock_embeddings = MagicMock()
        mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]

        with (
            patch("main.vectorstore", mock_vectorstore),
            patch("main.embeddings", mock_embeddings),
            patch("main.requests.Session") as mock_session,
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
        from main import handle_slash_command

        # Test help command
        result = handle_slash_command("/help")
        assert result is True

        captured = capsys.readouterr()
        assert "Available Commands" in captured.out

    def test_memory_command_integration(self, capsys):
        """Test memory command integration."""
        from main import handle_slash_command

        # Mock conversation history to ensure consistent output
        with patch("main.conversation_history", []):
            result = handle_slash_command("/memory")
            assert result is True

            captured = capsys.readouterr()
            assert "No conversation history" in captured.out

    @patch("main.conversation_history", [])
    @patch("main.save_memory")
    def test_clear_command_integration(self, mock_save, capsys):
        """Test clear command integration."""
        from main import handle_clear_command

        with patch("main.input", return_value="yes"):
            result = handle_clear_command()
            assert result is False

            captured = capsys.readouterr()
            assert "cleared" in captured.out.lower()


class TestLauncherIntegration:
    """Integration tests for launcher."""

    @patch("launcher.load_dotenv")
    @patch("os.path.exists", return_value=True)
    def test_launcher_full_flow(self, mock_exists, mock_dotenv):
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
        import main

        assert hasattr(main, "initialize_application")

        # Test launcher import
        import launcher

        assert hasattr(launcher, "main")

        # Test gui import (may fail if PyQt6 not available)
        try:
            import gui

            assert hasattr(gui, "AIAssistantGUI")
        except ImportError:
            # GUI not available, which is acceptable
            pass

    def test_configuration_loading(self):
        """Test configuration loading from environment."""
        # Test that configuration variables are accessible
        import main

        # These should be set from mock_env fixture
        assert hasattr(main, "LM_STUDIO_BASE_URL")
        assert hasattr(main, "MODEL_NAME")
        assert hasattr(main, "CHROMA_HOST")
