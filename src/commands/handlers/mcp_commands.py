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
MCP command handlers.
"""

from src.commands.registry import CommandRegistry
from src.core.context import get_mcp_client
from src.core.config import get_logger

logger = get_logger()

__all__ = [
    "handle_mcp_command",
]


@CommandRegistry.register(
    "mcp", "Manage Model Context Protocol servers (list, connect)", category="system"
)
def handle_mcp_command(args: str) -> None:
    """
    Handle /mcp command.
    Usage:
        /mcp list          - List connected servers and tools
        /mcp connect <name> - Connect to a specific server
    """
    if not args:
        print("Usage: /mcp <list|connect> [args]")
        return

    parts = args.split(maxsplit=1)
    subcommand = parts[0].lower()

    client = get_mcp_client()
    if not client:
        print("❌ MCP Client not initialized.")
        return

    if subcommand == "list":
        if not client.servers:
            print("No MCP servers connected.")
        else:
            print(f"🔌 Connected Servers: {len(client.servers)}")
            for name in client.servers:
                print(f"  - {name}")

            tools = client.tools
            if not tools:
                print("No tools discovered.")
            else:
                print(f"\n🛠️ Discovered Tools: {len(tools)}")
                for tool_name in tools:
                    print(f"  - {tool_name}")

    elif subcommand == "connect":
        if len(parts) < 2:
            print("Usage: /mcp connect <server_name>")
            return

        server_name = parts[1]
        print(f"Re-initializing MCP to connect to {server_name}...")
        client.initialize_sync()
        print("Done.")

    else:
        print(f"Unknown subcommand: {subcommand}")
