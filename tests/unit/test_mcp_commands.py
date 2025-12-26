#!/usr/bin/env python3
"""
Unit tests for MCP (Model Context Protocol) command handlers.

Tests cover:
- MCP command parsing and routing
- Server listing functionality
- Server connection handling
- Error cases and edge conditions
- Output formatting
"""

import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from src.commands.handlers.mcp_commands import handle_mcp_command


class TestMCPCommandParsing(unittest.TestCase):
    """Test MCP command parsing and validation."""

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_handle_mcp_command_no_args(self, mock_get_client):
        """Test /mcp with no arguments."""
        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("Usage:", output)
        self.assertIn("/mcp <list|connect>", output)

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_handle_mcp_command_invalid_subcommand(self, mock_get_client):
        """Test /mcp with invalid subcommand."""
        mock_get_client.return_value = MagicMock()

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("invalid")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("Unknown subcommand:", output)

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_handle_mcp_command_client_not_initialized(self, mock_get_client):
        """Test /mcp when MCP client is not initialized."""
        mock_get_client.return_value = None

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("list")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("MCP Client not initialized", output)
        self.assertIn("❌", output)


class TestMCPListServers(unittest.TestCase):
    """Test MCP server listing functionality."""

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_list_servers_no_servers(self, mock_get_client):
        """Test listing when no servers are connected."""
        mock_client = MagicMock()
        mock_client.servers = {}
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("list")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("No MCP servers connected", output)

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_list_servers_single_server(self, mock_get_client):
        """Test listing a single connected server."""
        mock_client = MagicMock()
        mock_client.servers = {"database": {"enabled": True}}
        mock_client.tools = {}
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("list")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("🔌 Connected Servers:", output)
        self.assertIn("database", output)
        self.assertIn("No tools discovered", output)

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_list_servers_multiple_servers(self, mock_get_client):
        """Test listing multiple connected servers."""
        mock_client = MagicMock()
        mock_client.servers = {
            "database": {"enabled": True},
            "web": {"enabled": True},
            "file": {"enabled": True},
        }
        mock_client.tools = {}
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("list")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("🔌 Connected Servers: 3", output)
        self.assertIn("database", output)
        self.assertIn("web", output)
        self.assertIn("file", output)

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_list_tools_no_tools(self, mock_get_client):
        """Test listing when no tools are discovered."""
        mock_client = MagicMock()
        mock_client.servers = {"database": {}}
        mock_client.tools = {}
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("list")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("No tools discovered", output)

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_list_tools_single_tool(self, mock_get_client):
        """Test listing a single discovered tool."""
        mock_client = MagicMock()
        mock_client.servers = {"database": {}}
        mock_client.tools = {"mcp_database_query": {}}
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("list")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("🛠️ Discovered Tools: 1", output)
        self.assertIn("mcp_database_query", output)

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_list_tools_multiple_tools(self, mock_get_client):
        """Test listing multiple discovered tools."""
        mock_client = MagicMock()
        mock_client.servers = {"database": {}, "web": {}}
        mock_client.tools = {
            "mcp_database_query": {},
            "mcp_database_insert": {},
            "mcp_web_fetch": {},
            "mcp_web_search": {},
        }
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("list")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("🛠️ Discovered Tools: 4", output)
        self.assertIn("mcp_database_query", output)
        self.assertIn("mcp_web_search", output)


class TestMCPConnect(unittest.TestCase):
    """Test MCP server connection functionality."""

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_connect_no_server_specified(self, mock_get_client):
        """Test /mcp connect without server name."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("connect")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("Usage:", output)
        self.assertIn("/mcp connect <server_name>", output)

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_connect_with_server_name(self, mock_get_client):
        """Test connecting to a specific server."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("connect database")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("Re-initializing MCP", output)
        self.assertIn("database", output)
        self.assertIn("Done", output)
        mock_client.initialize_sync.assert_called_once()

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_connect_initializes_client(self, mock_get_client):
        """Test that connect calls initialize_sync on client."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("connect myserver")

        sys.stdout = sys.__stdout__

        # Verify initialize_sync was called
        mock_client.initialize_sync.assert_called_once()

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_connect_with_multiple_words_in_name(self, mock_get_client):
        """Test connecting with server name and extra arguments."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        # Only the first word after "connect" is used as server name
        handle_mcp_command("connect database extra args")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("database", output)
        mock_client.initialize_sync.assert_called_once()


class TestMCPCommandIntegration(unittest.TestCase):
    """Test integration scenarios and edge cases."""

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_list_command_case_insensitive(self, mock_get_client):
        """Test that list command is case insensitive."""
        mock_client = MagicMock()
        mock_client.servers = {"test": {}}
        mock_client.tools = {}
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("LIST")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        # Should work even with uppercase
        self.assertIn("Connected Servers", output)

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_connect_command_case_insensitive(self, mock_get_client):
        """Test that connect command is case insensitive."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("CONNECT myserver")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        # Should work even with uppercase
        self.assertIn("Re-initializing MCP", output)
        mock_client.initialize_sync.assert_called_once()

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_empty_servers_and_tools(self, mock_get_client):
        """Test output when both servers and tools are empty."""
        mock_client = MagicMock()
        mock_client.servers = {}
        mock_client.tools = {}
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("list")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("No MCP servers connected", output)

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_command_with_whitespace(self, mock_get_client):
        """Test command parsing with extra whitespace."""
        mock_client = MagicMock()
        mock_client.servers = {}
        mock_client.tools = {}
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        # Test with extra spaces
        handle_mcp_command("   list   ")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        # Should handle whitespace gracefully
        self.assertNotEqual(len(output), 0)

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_connect_returns_proper_messages(self, mock_get_client):
        """Test that connect outputs consistent messages."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("connect testserver")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        # Should contain both start and completion messages
        self.assertIn("Re-initializing MCP", output)
        self.assertIn("testserver", output)
        self.assertIn("Done", output)

    @patch("src.commands.handlers.mcp_commands.get_mcp_client")
    def test_list_with_many_servers_and_tools(self, mock_get_client):
        """Test list output with many servers and tools."""
        mock_client = MagicMock()
        # Create many servers
        servers = {f"server_{i}": {} for i in range(10)}
        mock_client.servers = servers
        # Create many tools
        tools = {f"mcp_tool_{i}": {} for i in range(20)}
        mock_client.tools = tools
        mock_get_client.return_value = mock_client

        captured_output = StringIO()
        sys.stdout = captured_output

        handle_mcp_command("list")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        # Should show counts and list items
        self.assertIn("🔌 Connected Servers: 10", output)
        self.assertIn("🛠️ Discovered Tools: 20", output)


if __name__ == "__main__":
    unittest.main()
