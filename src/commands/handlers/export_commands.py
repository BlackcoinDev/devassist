#!/usr/bin/env python3
"""
Export Commands - Export conversation history.

This module provides command handlers for exporting conversation
history in various formats (JSON, Markdown).
"""

import json
from typing import List
from datetime import datetime
from src.commands.registry import CommandRegistry
from src.core.context import get_context

# =============================================================================
# COMMAND HANDLERS
# =============================================================================


@CommandRegistry.register("export", "Export conversation", category="export")
def handle_export(args: List[str]) -> None:
    """Handle /export command to save conversation history."""
    ctx = get_context()

    if not ctx.conversation_history:
        print("\n📝 No conversation history to export.\n")
        return

    # Determine export format
    format_type = args[0].lower().strip() if args else "json"

    if format_type not in ["json", "markdown", "md"]:
        print(f"\n❌ Unsupported format: {format_type}")
        print("Supported formats: json, markdown (md)\n")
        return

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_export_{timestamp}.{format_type if format_type != 'markdown' else 'md'}"

    try:
        if format_type == "json":
            # Export as JSON
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_messages": len(ctx.conversation_history),
                "messages": [],
            }

            for i, msg in enumerate(ctx.conversation_history):
                msg_type = type(msg).__name__.replace("Message", "").lower()
                export_data["messages"].append(
                    {
                        "index": i + 1,
                        "type": msg_type,
                        "content": str(msg.content),
                        "timestamp": (
                            getattr(msg, "timestamp", datetime.now().isoformat())
                            if hasattr(msg, "timestamp")
                            else datetime.now().isoformat()
                        ),
                    }
                )

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

        elif format_type in ["markdown", "md"]:
            # Export as Markdown
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# Conversation Export\n\n")
                f.write(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Total Messages:** {len(ctx.conversation_history)}\n\n")
                f.write("---\n\n")

                for i, msg in enumerate(ctx.conversation_history):
                    msg_type = type(msg).__name__.replace("Message", "")
                    f.write(f"## Message {i + 1}: {msg_type}\n\n")
                    f.write(f"{msg.content}\n\n")
                    f.write("---\n\n")

        print(f"\n✅ Conversation exported to: {filename}")
        print(f"📊 Total messages: {len(ctx.conversation_history)}")
        print(f"📄 Format: {format_type.upper()}\n")

    except Exception as e:
        print(f"\n❌ Failed to export conversation: {e}\n")


__all__ = ["handle_export"]
