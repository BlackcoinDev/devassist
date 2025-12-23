"""
Tests for Chat Loop Orchestrator.
"""
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from src.core.chat_loop import ChatLoop


class TestChatLoop:
    @patch("src.core.chat_loop.get_context")
    @patch("src.core.chat_loop.ToolRegistry")
    @patch("src.core.chat_loop.save_memory")
    @patch("src.main.get_relevant_context", return_value="")
    def test_run_iteration_no_tools(self, mock_rag, mock_save, mock_registry, mock_get_ctx):
        """Test simple iteration without tool calls."""
        mock_ctx = MagicMock()
        mock_ctx.conversation_history = []
        mock_ctx.context_mode = "off"
        mock_get_ctx.return_value = mock_ctx

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="Hello there!")
        mock_ctx.llm = mock_llm

        loop = ChatLoop()
        response = loop.run_iteration("Hi")

        assert response == "Hello there!"
        assert len(mock_ctx.conversation_history) == 2
        assert isinstance(mock_ctx.conversation_history[0], HumanMessage)
        assert isinstance(mock_ctx.conversation_history[1], AIMessage)

    @patch("src.core.chat_loop.get_context")
    @patch("src.core.chat_loop.ToolRegistry")
    @patch("src.core.chat_loop.save_memory")
    @patch("src.main.get_relevant_context", return_value="")
    def test_run_iteration_with_tool(self, mock_rag, mock_save, mock_registry, mock_get_ctx):
        """Test iteration with a tool call."""
        mock_ctx = MagicMock()
        mock_ctx.conversation_history = []
        mock_ctx.context_mode = "off"
        mock_get_ctx.return_value = mock_ctx

        mock_llm = MagicMock()
        # First call returns tool call
        tool_call = {"name": "test_tool", "args": {"a": 1}, "id": "123"}
        msg_with_tool = AIMessage(content="", tool_calls=[tool_call])

        # Second call returns final answer
        final_msg = AIMessage(content="Tool result is 2")

        mock_llm.invoke.side_effect = [msg_with_tool, final_msg]
        mock_ctx.llm = mock_llm

        mock_registry.execute.return_value = {"result": 2}

        loop = ChatLoop()
        response = loop.run_iteration("Run tool")

        assert response == "Tool result is 2"
        # History: Human, AI(tool), ToolResult, AI(final)
        assert len(mock_ctx.conversation_history) == 4
        assert isinstance(mock_ctx.conversation_history[2], ToolMessage)
