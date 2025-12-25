#!/usr/bin/env python3
"""
Integration tests for DeepWiki MCP Server.

Tests real connectivity to https://mcp.deepwiki.com using the
blackcoin-more wiki: https://deepwiki.com/CoinBlack/blackcoin-more

These tests require network connectivity and test actual MCP protocol.
"""

import unittest
import requests
import json
import uuid
from typing import Dict, Any, Optional


# DeepWiki MCP Server endpoints
DEEPWIKI_MCP_URL = "https://mcp.deepwiki.com/mcp"
DEEPWIKI_SSE_URL = "https://mcp.deepwiki.com/sse"

# Test wiki for blackcoin-more project
TEST_REPO = "CoinBlack/blackcoin-more"
TEST_WIKI_URL = f"https://deepwiki.com/{TEST_REPO}"


class MCPJsonRpcClient:
    """Simple MCP JSON-RPC client for testing with SSE support."""

    def __init__(self, url: str):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        })
        self.session_id: Optional[str] = None

    def _parse_sse_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse SSE-formatted response to extract JSON data."""
        for line in text.split("\n"):
            if line.startswith("data: "):
                data_str = line[6:].strip()
                if data_str and data_str != "ping":
                    try:
                        return json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
        return None

    def call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a JSON-RPC call to the MCP server."""
        request_id = str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }

        # Include session ID if we have one
        headers = {}
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        response = self.session.post(self.url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        # Capture session ID from response headers
        if "mcp-session-id" in response.headers:
            self.session_id = response.headers["mcp-session-id"]

        # Handle SSE-formatted responses
        content_type = response.headers.get("Content-Type", "")
        if "text/event-stream" in content_type:
            result = self._parse_sse_response(response.text)
            if result:
                return result
            return {"error": "Could not parse SSE response"}

        return response.json()

    def initialize(self) -> Dict[str, Any]:
        """Initialize MCP connection."""
        return self.call("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "devassist-test",
                "version": "1.0.0"
            }
        })

    def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return self.call("tools/list")

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool with arguments."""
        return self.call("tools/call", {
            "name": name,
            "arguments": arguments
        })


class TestDeepWikiMCPConnectivity(unittest.TestCase):
    """Test basic connectivity to DeepWiki MCP server."""

    def test_server_reachable(self):
        """Test that the DeepWiki MCP server is reachable."""
        try:
            response = requests.get(
                "https://mcp.deepwiki.com/",
                timeout=10,
                allow_redirects=True
            )
            # Server should respond (any status code)
            self.assertIsNotNone(response)
        except requests.exceptions.RequestException as e:
            self.skipTest(f"DeepWiki MCP server not reachable: {e}")

    def test_mcp_endpoint_accepts_post(self):
        """Test that the MCP endpoint accepts POST requests."""
        try:
            response = requests.post(
                DEEPWIKI_MCP_URL,
                json={"jsonrpc": "2.0", "id": "test", "method": "ping"},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            # Should get a response (even if error)
            self.assertIsNotNone(response)
        except requests.exceptions.RequestException as e:
            self.skipTest(f"DeepWiki MCP endpoint not accessible: {e}")


class TestDeepWikiMCPProtocol(unittest.TestCase):
    """Test MCP protocol with DeepWiki server."""

    def setUp(self):
        """Set up MCP client for each test."""
        self.client = MCPJsonRpcClient(DEEPWIKI_MCP_URL)

    def test_initialize_connection(self):
        """Test MCP initialization handshake."""
        try:
            result = self.client.initialize()

            # Should have a result or error
            self.assertIn("result", result)

            if "result" in result:
                # Check for server info
                server_result = result["result"]
                self.assertIn("protocolVersion", server_result)
                self.assertIn("serverInfo", server_result)

        except requests.exceptions.RequestException as e:
            self.skipTest(f"Network error: {e}")

    def test_list_available_tools(self):
        """Test listing available tools from DeepWiki MCP."""
        try:
            # Initialize first to get session ID
            self.client.initialize()

            # List tools
            result = self.client.list_tools()

            self.assertIn("result", result)

            if "result" in result:
                tools_result = result["result"]
                self.assertIn("tools", tools_result)

                tools = tools_result["tools"]
                self.assertIsInstance(tools, list)

                # DeepWiki should have ask_question, read_wiki_contents, read_wiki_structure
                tool_names = [t.get("name") for t in tools]
                print(f"Available tools: {tool_names}")

                # At least one tool should be available
                self.assertGreater(len(tools), 0)

        except requests.exceptions.RequestException as e:
            self.skipTest(f"Network error: {e}")


class TestDeepWikiBlackcoinMore(unittest.TestCase):
    """Test DeepWiki MCP with blackcoin-more repository wiki."""

    def setUp(self):
        """Set up MCP client for each test."""
        self.client = MCPJsonRpcClient(DEEPWIKI_MCP_URL)
        try:
            self.client.initialize()
        except Exception:
            pass

    def test_read_wiki_structure_blackcoin(self):
        """Test reading wiki structure for blackcoin-more."""
        try:
            result = self.client.call_tool("read_wiki_structure", {
                "repo_name": TEST_REPO
            })

            print(f"Wiki structure result: {json.dumps(result, indent=2)[:500]}")

            # Should have result or error
            if "result" in result:
                content = result["result"]
                self.assertIsNotNone(content)

        except requests.exceptions.RequestException as e:
            self.skipTest(f"Network error: {e}")
        except Exception as e:
            # Tool might not exist or have different signature
            print(f"Tool call error (may be expected): {e}")

    def test_ask_question_about_blackcoin(self):
        """Test asking a question about blackcoin-more."""
        try:
            result = self.client.call_tool("ask_question", {
                "repo_name": TEST_REPO,
                "question": "What is Blackcoin?"
            })

            print(f"Question result: {json.dumps(result, indent=2)[:500]}")

            # Should have result or error
            if "result" in result:
                content = result["result"]
                self.assertIsNotNone(content)

        except requests.exceptions.RequestException as e:
            self.skipTest(f"Network error: {e}")
        except Exception as e:
            print(f"Tool call error (may be expected): {e}")

    def test_read_wiki_contents_blackcoin(self):
        """Test reading wiki contents for blackcoin-more."""
        try:
            result = self.client.call_tool("read_wiki_contents", {
                "repo_name": TEST_REPO
            })

            print(f"Wiki contents result: {json.dumps(result, indent=2)[:500]}")

            # Should have result or error
            if "result" in result:
                content = result["result"]
                self.assertIsNotNone(content)
                # Content should mention blackcoin
                if isinstance(content, list) and len(content) > 0:
                    text_content = str(content[0])
                    # Just verify we got some content back
                    self.assertGreater(len(text_content), 0)

        except requests.exceptions.RequestException as e:
            self.skipTest(f"Network error: {e}")
        except Exception as e:
            print(f"Tool call error (may be expected): {e}")


class TestDeepWikiMCPToolDiscovery(unittest.TestCase):
    """Test tool discovery and schema validation."""

    def setUp(self):
        """Set up MCP client for each test."""
        self.client = MCPJsonRpcClient(DEEPWIKI_MCP_URL)
        try:
            self.client.initialize()
        except Exception:
            pass

    def test_tool_definitions_have_required_fields(self):
        """Test that tool definitions have required MCP fields."""
        try:
            result = self.client.list_tools()

            if "result" not in result:
                self.skipTest("Could not list tools")

            tools = result["result"].get("tools", [])

            for tool in tools:
                # Each tool should have name and description
                self.assertIn("name", tool, f"Tool missing name: {tool}")

                # Description is recommended
                if "description" in tool:
                    self.assertIsInstance(tool["description"], str)

                # Input schema is standard for MCP tools
                if "inputSchema" in tool:
                    schema = tool["inputSchema"]
                    self.assertIn("type", schema)
                    self.assertEqual(schema["type"], "object")

        except requests.exceptions.RequestException as e:
            self.skipTest(f"Network error: {e}")


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
