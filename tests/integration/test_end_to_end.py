#!/usr/bin/env python3
"""
End-to-End integration tests for AI Assistant.

Simulates a full user session from startup to shutdown, 
verifying the integrity of the main loop and its components.
"""

import pytest
from unittest.mock import MagicMock, patch, call
from src.core.context import reset_context, get_context
from src.main import main, initialize_application, conversation_history
from langchain_core.messages import SystemMessage


class TestEndToEnd:
    """Full application lifecycle tests."""

    def setup_method(self):
        """Reset context before each test."""
        reset_context()

    @patch('src.main.initialize_application')
    @patch('src.main.input')
    @patch('src.main.print')
    @patch('src.main.save_memory')
    @patch('src.main.llm')
    @patch('src.main.vectorstore', None)
    @patch('src.main.user_memory', None)
    def test_basic_session_flow(self, mock_llm, mock_save, mock_print, mock_input, mock_init):
        """Test a simple session with two messages and a quit command."""
        # 1. Setup mocks
        mock_init.return_value = True

        # Seed history
        get_context().conversation_history.append(SystemMessage(content="Hello"))

        # Sequence of user inputs:
        # 1. A greeting
        # 2. A question
        # 3. Quit command
        mock_input.side_effect = ["Hello AI", "How are you?", "quit"]

        # Mock LLM responses
        mock_response1 = MagicMock()
        mock_response1.content = "Hello there! I'm your AI assistant."
        mock_response2 = MagicMock()
        mock_response2.content = "I'm doing great, thank you for asking! How can I help you today?"
        mock_llm.invoke.side_effect = [mock_response1, mock_response2]

        # 2. Run the chat loop (mocked so it doesn't loop forever)
        # We need to handle the infinite loop. Since we provided 'quit', it should break.
        main()

        # 3. Verifications
        assert mock_input.call_count == 3
        assert mock_llm.invoke.called

        # Verify history was saved at the end
        assert mock_save.called

        # Verify messages in conversation history
        from src.main import conversation_history as main_history
        assert len(main_history) == 5
        assert main_history[1].content == "Hello AI"
        assert main_history[2].content == "Hello there! I'm your AI assistant."

    @patch('src.main.initialize_application')
    @patch('src.main.input')
    @patch('src.main.print')
    @patch('src.main.handle_slash_command')
    @patch('src.main.save_memory')
    @patch('src.main.llm')
    @patch('src.main.vectorstore', None)
    @patch('src.main.user_memory', None)
    def test_slash_command_flow(self, mock_llm, mock_save, mock_handle, mock_print, mock_input, mock_init):
        """Test that slash commands are intercepted and handled without LLM."""
        mock_init.return_value = True

        # Seed history
        get_context().conversation_history.append(SystemMessage(content="Hello"))

        # Sequence:
        # 1. Slash command
        # 2. Exit
        mock_input.side_effect = ["/help", "q"]
        mock_handle.return_value = True

        main()

        # Verify slash command was handled
        mock_handle.assert_called_with("/help")
        # Verify no LLM call was made (since slash command intercepts)
        assert not mock_llm.invoke.called

    @patch('src.main.initialize_application')
    @patch('src.main.input')
    @patch('src.main.print')
    @patch('src.main.save_memory')
    @patch('src.main.vectorstore', None)
    @patch('src.main.user_memory', None)
    def test_empty_input_handling(self, mock_save, mock_print, mock_input, mock_init):
        """Verify that empty inputs don't trigger AI calls."""
        mock_init.return_value = True

        # Seed history
        get_context().conversation_history.append(SystemMessage(content="Hello"))

        # Sequence:
        # 1. Empty string
        # 2. Whitespace
        # 3. Exit
        mock_input.side_effect = ["", "   ", "exit"]

        main()

        # Verify zero messages were added beyond initial system msg
        from src.main import conversation_history as main_history
        assert len(main_history) == 1
