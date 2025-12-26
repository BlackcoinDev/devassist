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
