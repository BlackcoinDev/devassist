"""
Display and UI utilities

This module contains functions for displaying information to the user,
formatting output, and handling user interface elements.
"""

import sys
from typing import List
from langchain_core.messages import BaseMessage

# Import configuration
from src.core.config import APP_VERSION
from src.main import (
    MODEL_NAME,
    LM_STUDIO_BASE_URL,
    CHROMA_HOST,
    CHROMA_PORT,
    EMBEDDING_MODEL,
    CURRENT_SPACE,
    conversation_history,
)
from src.vectordb import get_space_collection_name


def show_welcome():
    """
    Display application startup information and load workspace configuration.

    Shows the application header, basic usage instructions, and loads the
    current workspace (space) that was last used. Spaces provide isolated
    knowledge bases for different projects or contexts.
    """
    # Load the workspace that was last active first (needed for display)
    from src.main import load_current_space

    global CURRENT_SPACE
    CURRENT_SPACE = load_current_space()

    # Display clean startup banner
    print("")
    print("=" * 60)
    print(f"      AI Assistant Chat Interface v{APP_VERSION}")
    print("=" * 60)

    # Show configuration summary
    print(f"📍 Python: {sys.version.split()[0]} | Model: {MODEL_NAME}")
    print(f"🔗 LM Studio: {LM_STUDIO_BASE_URL}")
    print(f"🗄️  ChromaDB: {CHROMA_HOST}:{CHROMA_PORT}")
    print(f"🧠 Embeddings: {EMBEDDING_MODEL}")

    # Show memory status
    msg_count = len(conversation_history)
    print(f"💾 Memory: SQLite ({msg_count} messages loaded)")

    # Show current space
    print(
        f"🌐 Space: {CURRENT_SPACE} (collection: {
            get_space_collection_name(CURRENT_SPACE)
        })"
    )
    print("")

    # Show usage hints
    print("Hello! I'm ready to help you.")
    print("Commands: 'quit', 'exit', or 'q' to exit")
    print("Type /help for all available commands")
    print("")


def format_conversation_history(
    messages: List[BaseMessage], max_display: int = 10
) -> str:
    """
    Format conversation history for display.

    Args:
        messages: List of conversation messages
        max_display: Maximum number of messages to display

    Returns:
        Formatted conversation history string
    """
    if not messages:
        return "No conversation history"

    lines = []
    recent_messages = (
        messages[-max_display:] if len(messages) > max_display else messages
    )

    for i, msg in enumerate(recent_messages, 1):
        role = msg.type.upper()
        content = str(msg.content)
        if len(content) > 100:
            content = content[:97] + "..."
        lines.append(f"{len(messages) - max_display + i}. {role}: {content}")

    return "\n".join(lines)


def show_memory_status():
    """Display current memory status."""
    msg_count = len(conversation_history)
    print(f"\n🧠 Memory: {msg_count} messages stored")
    if msg_count > 0:
        print("-" * 40)
        print(format_conversation_history(conversation_history, 5))
        print("-" * 40)
    print()


def show_command_result(success: bool, message: str):
    """
    Display the result of a command execution.

    Args:
        success: Whether the command succeeded
        message: Result message to display
    """
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")


def format_file_info(file_path: str, file_size: int) -> str:
    """
    Format file information for display.

    Args:
        file_path: Path to the file
        file_size: Size of the file in bytes

    Returns:
        Formatted file information string
    """
    from src.core.utils import get_file_size_info

    _, size_str = get_file_size_info(file_path)
    return f"📄 {file_path} ({size_str})"
