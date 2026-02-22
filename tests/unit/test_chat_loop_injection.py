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

import unittest
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage
from src.core.chat_loop import ChatLoop


class TestChatLoopInjection(unittest.TestCase):
    @patch("src.core.chat_loop.get_context")
    @patch("src.core.chat_loop.ToolRegistry")
    @patch("src.core.chat_loop.save_memory")
    @patch("src.core.context_utils.get_relevant_context", return_value="")
    def test_file_read_injects_context(
        self, mock_rag, mock_save, mock_registry, mock_get_ctx
    ):
        """Test that read_file tool execution injects content as HumanMessage."""
        mock_ctx = MagicMock()
        mock_ctx.conversation_history = []
        mock_ctx.context_mode = "off"

        # Setup specific mock for tool binding
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_ctx.llm = mock_llm

        mock_get_ctx.return_value = mock_ctx

        # 1. AI decides to read a file
        tool_call = {
            "name": "read_file_content",
            "args": {"file_path": "test.txt"},
            "id": "call_1",
        }
        msg_tool_call = AIMessage(content="", tool_calls=[tool_call])

        # 2. AI responds after reading
        msg_final = AIMessage(content="The file contains hello world")

        mock_llm.invoke.side_effect = [msg_tool_call, msg_final]

        # 3. Tool executes successfully
        mock_registry.execute.return_value = {
            "success": True,
            "content": "SECRET_CONTENT_123",
            "file_path": "test.txt",
        }

        loop = ChatLoop()
        loop.run_iteration("read test.txt")

        # Verify history structure
        # 0: User "read test.txt"
        # 1: AI (tool call)
        # 2: ToolMessage (result JSON)
        # 3: HumanMessage (INJECTED CONTENT) <--- We want to verify this
        # 4: AI "The file contains..."

        self.assertEqual(len(mock_ctx.conversation_history), 5)

        injected_msg = mock_ctx.conversation_history[3]
        self.assertIsInstance(injected_msg, HumanMessage)
        self.assertIn("SECRET_CONTENT_123", injected_msg.content)
        self.assertIn("Output of reading file", injected_msg.content)


if __name__ == "__main__":
    unittest.main()
