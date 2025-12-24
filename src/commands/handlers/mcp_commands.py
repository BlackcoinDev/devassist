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
