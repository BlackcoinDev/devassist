"""
MCP Client Manager.

Handles connections to multiple MCP servers, tool discovery, and execution.
Uses a background thread with an asyncio loop to handle async transports
within a synchronous application.
"""

import asyncio
import json
import logging
import os
import threading
from typing import Any, Dict, List, Optional
from pathlib import Path

from src.mcp.transports.stdio import StdioTransport
from src.mcp.transports.http import HttpTransport
from src.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

class MCPClient:
    """
    Manages MCP server connections and tools.
    """

    def __init__(self):
        self.servers: Dict[str, Any] = {} # name -> transport
        self.tools: Dict[str, Dict] = {}  # mcp_server_tool -> definition
        self.config_path = Path("config/mcp_servers.json")
        
        # Start background loop
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        """Run the asyncio loop in a background thread."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def initialize_sync(self):
        """Synchronous wrapper for initialization."""
        future = asyncio.run_coroutine_threadsafe(self.initialize(), self._loop)
        try:
            return future.result(timeout=30)
        except Exception as e:
            logger.error(f"MCP initialization failed: {e}")

    async def initialize(self):
        """Load config and connect to enabled servers."""
        if not self.config_path.exists():
            logger.info("No MCP config found. Skipping initialization.")
            return

        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            for server_conf in config.get("servers", []):
                if server_conf.get("enabled", False):
                    await self.connect_server(server_conf)
                    
        except Exception as e:
            logger.error(f"Error initializing MCP client: {e}")

    async def connect_server(self, config: Dict[str, Any]):
        """Connect to a single server and register its tools."""
        name = config["name"]
        transport_type = config.get("transport", "stdio")
        
        try:
            transport = None
            if transport_type == "stdio":
                transport = StdioTransport(
                    command=config["command"],
                    args=config.get("args", []),
                    env=config.get("env")
                )
            elif transport_type == "http":
                transport = HttpTransport(
                    url=config["url"],
                    headers=config.get("headers")
                )
            
            if transport:
                await transport.connect()
                self.servers[name] = transport
                logger.info(f"✅ Connected to MCP server: {name}")
                
                # Discover tools
                await self._discover_tools(name, transport)
                
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {name}: {e}")

    async def _discover_tools(self, server_name: str, transport: Any):
        """List tools from server and register them."""
        # JSON-RPC listTools
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1,
            "params": {}
        }
        
        await transport.send_message(request)
        response = await transport.receive_message()
        
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            for tool in tools:
                tool_name = tool["name"]
                prefixed_name = f"mcp_{server_name}_{tool_name}"
                
                # Register locally for tracking
                self.tools[prefixed_name] = tool
                
                # Register with ToolRegistry
                self._register_tool(prefixed_name, tool, server_name, tool_name)
                
                logger.info(f"   🔧 Discovered tool: {prefixed_name}")

    def _register_tool(self, registered_name: str, tool_def: Dict, server_name: str, original_name: str):
        """Register tool with ToolRegistry."""
        
        # Create execution wrapper
        def executor(**kwargs):
            # Run in the background loop
            future = asyncio.run_coroutine_threadsafe(
                self.execute_tool(server_name, original_name, kwargs),
                self._loop
            )
            return future.result()

        # Update definition to include function name if missing
        if "function" not in tool_def:
             # Convert MCP tool def to OpenAI def if needed
             # MCP: {name, description, inputSchema}
             # OpenAI: {type: function, function: {name, description, parameters}}
             openai_def = {
                 "type": "function",
                 "function": {
                     "name": registered_name,
                     "description": tool_def.get("description", ""),
                     "parameters": tool_def.get("inputSchema", {})
                 }
             }
        else:
            openai_def = tool_def

        # Register dynamically
        ToolRegistry.register_dynamic(registered_name, openai_def, executor)

    async def execute_tool(self, server_name: str, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool on remote server."""
        transport = self.servers.get(server_name)
        if not transport:
            return {"error": f"Server {server_name} not connected"}

        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 2,
            "params": {
                "name": tool_name,
                "arguments": args
            }
        }
        
        await transport.send_message(request)
        response = await transport.receive_message()
        
        if response and "result" in response:
            return response["result"]
        elif response and "error" in response:
            return {"error": response["error"]}
        return {"error": "Empty response"}

    def close(self):
        """Close all connections and stop background thread."""
        # 1. Run async cleanup
        if self._loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self._cleanup(), self._loop)
            try:
                future.result(timeout=5)
            except Exception as e:
                logger.error(f"Error during MCP cleanup: {e}")

        # 2. Stop loop
        self._loop.call_soon_threadsafe(self._loop.stop)
        
        # 3. Join thread
        if self._thread.is_alive() and threading.current_thread() != self._thread:
             self._thread.join(timeout=2)

    async def _cleanup(self):
        """Async cleanup of transports."""
        for name, transport in self.servers.items():
            await transport.close()
        self.servers.clear()