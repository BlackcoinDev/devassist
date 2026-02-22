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
Tests for MCP Client.
"""

import asyncio
from src.mcp.client import MCPClient


class TestMCPClient:
    def test_client_initialization(self):
        """Test that client starts the background thread."""
        client = MCPClient()
        assert client._thread.is_alive()

        # Cleanup
        client.close()
        assert not client._thread.is_alive()

    def test_sync_execution(self):
        """Test synchronous wrapper execution."""
        client = MCPClient()

        async def dummy_coro():
            return "success"

        future = asyncio.run_coroutine_threadsafe(dummy_coro(), client._loop)
        result = future.result()
        assert result == "success"

        client.close()
