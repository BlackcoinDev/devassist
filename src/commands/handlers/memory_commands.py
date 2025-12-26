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
Memory Management Commands - View and manage conversation history.

This module provides command handlers for viewing conversation history,
clearing memory, and displaying personalized Mem0 memories.
"""

from typing import List, cast
from langchain_core.messages import SystemMessage, BaseMessage

from src.commands.registry import CommandRegistry
from src.core.context import get_context
from src.core.config import get_config
from src.storage.memory import save_memory

__all__ = [
    "handle_memory",
    "handle_clear",
    "handle_mem0",
]

# =============================================================================
# COMMAND HANDLERS
# =============================================================================


@CommandRegistry.register("memory", "Show conversation history", category="memory")
def handle_memory(args: List[str]) -> None:
    """Show conversation history."""
    ctx = get_context()

    if not ctx.conversation_history:
        print("\n📝 No conversation history available.\n")
        return

    print(f"\n📝 Conversation History ({len(ctx.conversation_history)} messages):\n")
    for i, msg in enumerate(ctx.conversation_history):
        msg_type = type(msg).__name__.replace("Message", "")
        content = str(msg.content)
        content_preview = content[:100] + "..." if len(content) > 100 else content
        print(f"{i + 1:2d}. {msg_type}: {content_preview}")
    print()


@CommandRegistry.register("clear", "Clear conversation history", category="memory")
def handle_clear(args: List[str]) -> None:
    """Handle /clear command."""
    ctx = get_context()

    confirm = input(
        "Are you sure you want to clear all conversation history? (yes/no): "
    )
    if confirm.lower() in ["yes", "y"]:
        # Clear display and show confirmation
        print("\nConversation memory cleared. Starting fresh.\n")

        # Add a new system message for the fresh start
        ctx.conversation_history = cast(
            List[BaseMessage], [SystemMessage(content="Lets get some coding done..")]
        )
        save_memory(ctx.conversation_history)
    else:
        print("\n❌ Clear cancelled\n")


@CommandRegistry.register("mem0", "Show personalized memory", category="memory")
def handle_mem0(args: List[str]) -> None:
    """
    Display information about the current Mem0 personalized memory contents.

    Shows user memory statistics and sample memories from the Mem0 system.
    """
    ctx = get_context()
    config = get_config()

    if ctx.user_memory is None:
        print("\n❌ Mem0 not available.\n")
        return

    try:
        print("\n--- Mem0 Personalized Memory Contents ---")

        # Get all memories for the user
        memories = ctx.user_memory.get_all(user_id="default_user")
        results_count = len(memories.get("results", []))

        if config.verbose_logging:
            print(f"🧠 Mem0: Retrieved {results_count} memories")

        if not memories or not memories.get("results"):
            print("📊 No personalized memories stored yet.")
            print("Memories are automatically created from your conversations.")
            return

        results = memories["results"]
        print(f"📊 Memories: {len(results)}")
        print("👤 User ID: user")

        if results:
            print("\n🧠 Sample Memories:")
            for i, memory in enumerate(results[:5]):  # Show first 5
                content = memory.get("memory", "No content")
                if len(content) > 200:
                    content = content[:200] + "..."
                print(f"  {i + 1}. {content}")

            if len(results) > 5:
                print(f"  ... and {len(results) - 5} more")

    except Exception as e:
        print(f"\n❌ Failed to retrieve Mem0 contents: {e}\n")


__all__ = ["handle_memory", "handle_clear", "handle_mem0"]
