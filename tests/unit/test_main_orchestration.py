#!/usr/bin/env python3
"""
Unit tests for src/main.py orchestration and error handling logic.
Targeting gaps in initialize_application and the main chat loop.
"""

from src.main import (
    initialize_llm,
    initialize_vectordb,
    initialize_user_memory,
    initialize_application,
)


from unittest.mock import patch


class TestMainInitialization:
    """Test initialization failure modes."""

    @patch("src.main.ChatOpenAI", side_effect=Exception("LLM failure"))
    def test_initialize_llm_failure(self, mock_openai):
        """Test initialize_llm failure."""
        with patch("builtins.print") as mock_print:
            result = initialize_llm()
            assert result is False
            # Check that some error message was printed
            assert any("Failed" in str(call) or "failed" in str(call) for call in mock_print.call_args_list)

    @patch("src.main.HttpClient", side_effect=Exception("Vectordb failure"))
    def test_initialize_vectordb_failure(self, mock_client):
        """Test initialize_vectordb failure."""
        with patch("builtins.print") as mock_print:
            result = initialize_vectordb()
            assert result is False
            # Check that some error message was printed
            assert any("failed" in str(call).lower() for call in mock_print.call_args_list)

    @patch("src.main.MEM0_AVAILABLE", True)
    @patch("mem0.Memory")
    def test_initialize_user_memory_failure(self, mock_memory):
        """Test initialize_user_memory failure."""
        mock_memory.from_config.side_effect = Exception("Mem0 failure")
        with patch("src.main.print") as mock_print:
            result = initialize_user_memory()
            assert result is False
            mock_print.assert_any_call("⚠️ Failed to initialize Mem0: Mem0 failure")

    @patch("src.main.initialize_llm")
    @patch("src.main.initialize_vectordb")
    @patch("src.main.initialize_user_memory")
    def test_initialize_application_partial_success(self, mock_mem, mock_vdb, mock_llm):
        """Test initialize_application when LLM fails."""
        mock_llm.return_value = False
        result = initialize_application()
        assert result is False

    @patch("src.main.initialize_llm")
    @patch("src.main.initialize_vectordb")
    @patch("src.main.initialize_user_memory")
    @patch("sys.exit")
    def test_initialize_application_vdb_failure_exits(
        self, mock_exit, mock_mem, mock_vdb, mock_llm
    ):
        """Test initialize_application when VDB fails (it should exit)."""
        mock_llm.return_value = True
        mock_vdb.return_value = False
        initialize_application()
        mock_exit.assert_called_with(1)


class TestChatLoopErrorHandling:
    """Test error handling within the main chat loop."""

    @patch("src.main.initialize_application")
    @patch("builtins.input")
    @patch("builtins.print")
    @patch("src.main.save_memory")
    def test_main_loop_connection_error(
        self, mock_save, mock_print, mock_input, mock_init
    ):
        """Test main loop handling of ConnectionError."""
        from src.main import main

        mock_init.return_value = True

        # Simulate a loop that runs once with an error, then exits gracefully
        # Sequence: raise error, then return "q" to exit gracefully
        mock_input.side_effect = [ConnectionError("Server unreachable"), "q"]

        main()

        # The loop catches generic exceptions and prints "Error: {e}"
        # Then continues and handles the "q" to exit
        any_error_printed = any(
            "Error:" in str(call) for call in mock_print.call_args_list
        )
        assert any_error_printed, "Error message not found in print calls"

    @patch("src.main.initialize_application")
    @patch("builtins.input")
    @patch("builtins.print")
    @patch("src.main.save_memory")
    def test_main_loop_eof_error(self, mock_save, mock_print, mock_input, mock_init):
        """Test main loop handling of EOFError (graceful exit)."""
        from src.main import main

        mock_init.return_value = True
        mock_input.side_effect = EOFError()

        main()

        mock_save.assert_called()
        mock_print.assert_any_call("\n\n👋 Goodbye! Your conversation has been saved.")

    @patch("src.main.initialize_application")
    @patch("builtins.input")
    @patch("builtins.print")
    @patch("src.main.save_memory")
    def test_main_loop_keyboard_interrupt(
        self, mock_save, mock_print, mock_input, mock_init
    ):
        """Test main loop handling of KeyboardInterrupt."""
        from src.main import main

        mock_init.return_value = True
        mock_input.side_effect = KeyboardInterrupt()

        main()

        mock_save.assert_called()
        mock_print.assert_any_call("\n\n👋 Goodbye! Your conversation has been saved.")
