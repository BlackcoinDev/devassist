#!/usr/bin/env python3
# flake8: noqa: F841
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
Legacy Command Handlers - Commands that haven't been migrated to the new system yet.

This module contains command handlers that are still using the old pattern.
They will be gradually migrated to use @CommandRegistry.register() decorators.
"""

import os
import json
from typing import List


# Import core components

from src.core.context import (
    get_context,
    get_current_space,
    set_current_space,
    get_context_mode,
    set_context_mode,
    get_learning_mode,
    set_learning_mode,
)
from src.core.config import get_config
from src.storage.memory import save_memory
from src.vectordb import get_space_collection_name, ensure_space_collection
from src.tools.executors.document_tools import execute_parse_document
from src.tools.executors.knowledge_tools import execute_learn_information
from src.tools.executors.file_tools import (
    execute_read_file,
    execute_write_file,
    execute_list_directory,
)

# Import for type hints

from langchain_core.messages import SystemMessage

# =============================================================================

# LEGACY COMMAND HANDLERS

# =============================================================================


def handle_read_command(file_path: str) -> None:
    """
    Handle /read command - Read file contents.

    Args:
        file_path: Path to file to read
    """
    if not file_path:
        print("\n❌ Please specify a file path. Example: /read README.md\n")
        return

    # Use the tool executor for file reading
    result = execute_read_file(file_path)

    if result.get("error"):
        print(f"\n❌ Error reading file: {result['error']}\n")
        return

    content = result.get("content", "")
    file_info = result.get("file_info", {})

    if config.verbose_logging:
        print(f"📄 File: {file_info.get('name', file_path)}")
        print(f"📊 Size: {file_info.get('size', 'unknown')} bytes")
        print(f"📝 Lines: {file_info.get('lines', 'unknown')}")
        print(f"📁 Type: {file_info.get('type', 'unknown')}")
        print()

    # Display content with line numbers
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        print(f"{i:4d}: {line}")

    print(f"\n📄 Displayed {len(lines)} lines from {file_path}\n")


def handle_write_command(args: str) -> None:
    """
    Handle /write command - Write content to a file.

    Args:
        args: Arguments in format "filename:content"
    """
    if not args or ":" not in args:
        print("\n❌ Usage: /write filename:content")
        print("Example: /write test.txt:Hello World")
        return

    try:
        file_path, content = args.split(":", 1)
        file_path = file_path.strip()
        content = content.strip()

        if not file_path or not content:
            print("\n❌ Both filename and content are required")
            return

        # Use the tool executor for file writing
        result = execute_write_file(file_path, content)

        if result.get("success"):
            print(f"\n✅ File '{file_path}' written successfully")
            print(f"📄 Wrote {len(content)} characters\n")
        else:
            print(f"\n❌ Error writing file: {result.get('error', 'Unknown error')}\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")


def handle_list_command(dir_path: str = "") -> None:
    """
    Handle /list command - List directory contents.

    Args:
        dir_path: Directory path to list (default: current directory)
    """
    try:
        # Use the tool executor for directory listing
        result = execute_list_directory(dir_path)

        if result.get("error"):
            print(f"\n❌ Error: {result['error']}\n")
            return

        items = result.get("items", [])
        dir_path = result.get("path", ".")

        if not items:
            print(f"\n📂 Directory '{dir_path}' is empty\n")
            return

        # Display directory contents
        print(f"\n📂 Contents of '{dir_path}':\n")

        # Sort items: directories first, then files
        dirs = [item for item in items if item["type"] == "directory"]
        files = [item for item in items if item["type"] == "file"]

        # Sort alphabetically
        dirs.sort(key=lambda x: x["name"].lower())
        files.sort(key=lambda x: x["name"].lower())

        # Display directories
        if dirs:
            print("📁 Directories:")
            for item in dirs:
                size = item.get("size", "?")
                print(f"  {item['name']}/ (size: {size})")
            print()

        # Display files
        if files:
            print("📄 Files:")
            for item in files:
                size = item.get("size", "?")
                print(f"  {item['name']} (size: {size})")
            print()

        print(f"📊 Total: {len(dirs)} directories, {len(files)} files\n")

    except Exception as e:
        print(f"\n❌ Error listing directory: {e}\n")


def handle_pwd_command() -> None:
    """Handle /pwd command - Show current working directory."""
    try:
        cwd = os.getcwd()
        print(f"\n📍 Current directory: {cwd}\n")
    except Exception as e:
        print(f"\n❌ Error getting current directory: {e}\n")


def show_memory() -> None:
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


def handle_clear_command() -> bool:
    """Handle /clear command - Clear conversation history."""
    ctx = get_context()

    confirm = input(
        "Are you sure you want to clear all conversation history? (yes/no): "
    )
    if confirm.lower() in ["yes", "y"]:
        # Clear display and show confirmation
        print("\nConversation memory cleared. Starting fresh.\n")

        # Add a new system message for the fresh start
        ctx.conversation_history = [
            SystemMessage(content="Lets get some coding done..")
        ]
        save_memory(ctx.conversation_history)
        return True
    else:
        print("\n❌ Clear cancelled\n")
        return False


def handle_learn_command(content: str) -> None:
    """
    Handle /learn command - Teach AI new information.

    Args:
        content: Information to learn
    """
    if not content:
        print("\n❌ Please provide content to learn. Example: /learn Python is awesome")
        return

    ctx = get_context()
    config = get_config()

    if ctx.vectorstore is None:
        print("\n❌ Vector database not available. Cannot learn new information.\n")
        return

    try:
        # Use the tool executor for learning
        result = execute_learn_information(content)

        if result.get("success"):
            print(f"\n✅ Learned: {content[:100]}...")
            print(f"📚 Added to knowledge base in space: {get_current_space()}\n")
        else:
            error = result.get("error", "Unknown error")
            print(f"\n❌ Failed to learn: {error}\n")

    except Exception as e:
        print(f"\n❌ Error during learning: {e}\n")


def show_vectordb() -> None:
    """Show vector database statistics and contents."""
    ctx = get_context()
    config = get_config()

    if ctx.vectorstore is None:
        print("\n❌ Vector database not connected.\n")
        return

    try:
        collection_name = get_space_collection_name(get_current_space())

        # Get collection statistics
        collection = ctx.vectorstore.get_collection(collection_name)

        if collection is None:
            print(f"\n📚 Space '{get_current_space()}' has no knowledge base yet.")
            print("Use /learn or /populate to add knowledge.\n")
            return

        # Get collection count
        count = collection.count()

        print(f"\n📚 Knowledge Base: {get_current_space()}")
        print(f"📄 Documents: {count}")
        print(f"🔍 Collection: {collection_name}")
        print()

        # Show sample documents if available
        if count > 0:
            print("📝 Sample documents:")
            results = collection.get(limit=5)

            for i, doc in enumerate(results["documents"][:5], 1):
                content = doc[:150] + "..." if len(doc) > 150 else doc
                print(f"  {i}. {content}")

            if count > 5:
                print(f"  ... and {count - 5} more documents")
            print()

    except Exception as e:
        print(f"\n❌ Error accessing vector database: {e}\n")


def show_mem0() -> None:
    """Display information about the current Mem0 personalized memory contents."""
    ctx = get_context()
    config = get_config()

    if ctx.user_memory is None:
        print("\n❌ Mem0 not available.\n")
        return

    try:
        print("\n--- Mem0 Personalized Memory Contents ---")

        # Get all memories for the user
        memories = ctx.user_memory.get_all(user_id="default_user")

        if config.verbose_logging:
            print(f"🧠 Mem0: Retrieved {len(memories.get('results', []))} memories")

        if not memories or not memories.get("results"):
            print("📊 No personalized memories stored yet.")
            print("Memories are automatically created from your conversations.")
            return

        results = memories["results"]
        print(f"📊 Memories: {len(results)}")
        print(f"👤 User ID: user")

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


def handle_populate_command(dir_path: str) -> None:
    """
    Handle /populate command - Import documents from a directory.

    Args:
        dir_path: Directory path to import from
    """
    ctx = get_context()
    config = get_config()

    if ctx.vectorstore is None:
        print("\n❌ Vector database not available. Cannot populate knowledge base.\n")
        return

    if not dir_path:
        print("\n❌ Please specify a directory. Example: /populate documents/\n")
        return

    try:
        # Normalize path and check if it exists
        dir_path = os.path.abspath(dir_path)

        if not os.path.isdir(dir_path):
            print(f"\n❌ Directory not found: {dir_path}\n")
            return

        print(f"\n🔍 Scanning directory: {dir_path}")

        # Count files first
        file_count = 0
        supported_extensions = {
            ".pdf",
            ".docx",
            ".rtf",
            ".epub",
            ".xlsx",
            ".txt",
            ".md",
            ".rst",
            ".json",
            ".xml",
            ".csv",
            ".py",
            ".js",
            ".java",
            ".cpp",
            ".c",
            ".go",
            ".rs",
            ".html",
            ".htm",
            ".css",
        }

        for root, dirs, files in os.walk(dir_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in supported_extensions:
                    file_count += 1

        if file_count == 0:
            print(f"\n❌ No supported files found in {dir_path}")
            print("Supported extensions:", ", ".join(sorted(supported_extensions)))
            return

        print(f"📄 Found {file_count} supported files")
        print(f"📚 Populating knowledge base in space: {get_current_space()}")
        print("⏳ This may take a few minutes...\n")

        # Process files
        processed_count = 0
        skipped_count = 0

        for root, dirs, files in os.walk(dir_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in supported_extensions:
                    continue

                file_path = os.path.join(root, file)

                try:
                    # Use the document parsing tool
                    result = execute_parse_document(file_path, "text")

                    if result.get("success"):
                        content = result.get("content", "")

                        if (
                            content and len(content.strip()) > 50
                        ):  # Minimum content threshold
                            # Add to knowledge base
                            learn_result = execute_learn_information(content)

                            if learn_result.get("success"):
                                processed_count += 1
                                if processed_count % 5 == 0:
                                    print(f"✅ Processed {processed_count} files...")
                            else:
                                skipped_count += 1
                        else:
                            skipped_count += 1
                    else:
                        skipped_count += 1

                except Exception as e:
                    print(f"❌ Error processing {file}: {e}")
                    skipped_count += 1

        print(f"\n🎉 Population complete!")
        print(f"✅ Processed: {processed_count} files")
        print(f"❌ Skipped: {skipped_count} files")
        print(f"📚 Total knowledge base size: {processed_count + skipped_count} items")
        print()

    except Exception as e:
        print(f"\n❌ Error during population: {e}\n")


def show_model_info() -> None:
    """Show current AI model information."""
    ctx = get_context()
    config = get_config()

    print("\n--- AI Model Information ---")
    print(f"🤖 Model: {config.model_name}")
    print(f"🌐 API: {config.lm_studio_url}")
    print(f"🔥 Temperature: {config.temperature}")
    print(f"💬 Max Input Length: {config.max_input_length}")

    if ctx.llm:
        print(f"✅ Connected to: {config.model_name}")
    else:
        print("❌ Not connected to AI model")

    print()


def handle_context_command(args: List[str]) -> None:
    """
    Handle /context command - Control context integration.

    Args:
        args: Context mode (auto, on, off)
    """
    if not args:
        # Show current context mode
        config = get_config()
        print(f"\n📊 Current context mode: {get_context_mode()}")
        print("Available modes: auto, on, off")
        print("Usage: /context <mode>\n")
        return

    mode = args[0].lower()
    valid_modes = ["auto", "on", "off"]

    if mode not in valid_modes:
        print(f"\n❌ Invalid mode: {mode}")
        print("Valid modes: auto, on, off\n")
        return

    # Update context mode
    config = get_config()
    set_context_mode(mode)
    print(f"\n✅ Context mode set to: {mode}\n")


def handle_learning_command(args: List[str]) -> None:
    """
    Handle /learning command - Control learning behavior.

    Args:
        args: Learning mode (normal, strict, off)
    """
    if not args:
        # Show current learning mode
        config = get_config()
        print(f"\n📚 Current learning mode: {get_learning_mode()}")
        print("Available modes: normal, strict, off")
        print("Usage: /learning <mode>\n")
        return

    mode = args[0].lower()
    valid_modes = ["normal", "strict", "off"]

    if mode not in valid_modes:
        print(f"\n❌ Invalid mode: {mode}")
        print("Valid modes: normal, strict, off\n")
        return

    # Update learning mode
    config = get_config()
    set_learning_mode(mode)
    print(f"\n✅ Learning mode set to: {mode}\n")


def handle_space_command(cmd_args: str) -> None:
    """
    Handle /space command - Manage knowledge spaces.

    Args:
        cmd_args: Space command arguments
    """
    if not cmd_args:
        print("\n❌ Please specify a space command.")
        print("Usage: /space <list|create|switch|delete> [name]\n")
        return

    parts = cmd_args.split()
    if not parts:
        print("\n❌ Invalid space command\n")
        return

    command = parts[0].lower()
    space_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    ctx = get_context()
    config = get_config()

    try:
        if command == "list":
            # List all spaces
            from src.vectordb import list_spaces

            spaces = list_spaces()

            print(f"\n📚 Knowledge Spaces ({len(spaces)}):")
            for i, space in enumerate(spaces, 1):
                active_marker = "✅ " if space == get_current_space() else "   "
                print(f"{i}. {active_marker}{space}")

            print(f"\n📍 Current space: {get_current_space()}\n")

        elif command == "create":
            if not space_name:
                print(
                    "\n❌ Please specify a space name. Example: /space create myproject\n"
                )
                return

            # Create new space
            ensure_space_collection(space_name)
            print(f"\n✅ Created space: {space_name}\n")

        elif command == "switch":
            if not space_name:
                print(
                    "\n❌ Please specify a space name. Example: /space switch myproject\n"
                )
                return

            # Switch to space
            from src.vectordb import switch_space, save_current_space

            if switch_space(space_name):
                set_current_space(space_name)
                save_current_space()
                print(f"\n✅ Switched to space: {space_name}\n")
            else:
                print(f"\n❌ Failed to switch to space: {space_name}\n")

        elif command == "delete":
            if not space_name:
                print(
                    "\n❌ Please specify a space name. Example: /space delete myproject\n"
                )
                return

            if space_name == "default":
                print("\n❌ Cannot delete the default space\n")
                return

            if space_name == get_current_space():
                print(
                    "\n❌ Cannot delete the current space. Switch to another space first.\n"
                )
                return

            # Delete space
            from src.vectordb import delete_space

            if delete_space(space_name):
                print(f"\n✅ Deleted space: {space_name}\n")
            else:
                print(f"\n❌ Failed to delete space: {space_name}\n")

        else:
            print(f"\n❌ Unknown space command: {command}\n")

    except Exception as e:
        print(f"\n❌ Error managing spaces: {e}\n")


def handle_export_command(format_type: str = "json") -> None:
    """
    Handle /export command - Export conversation history.

    Args:
        format_type: Export format (json, txt, md)
    """
    ctx = get_context()

    if not ctx.conversation_history:
        print("\n📝 No conversation history to export.\n")
        return

    valid_formats = ["json", "txt", "md"]
    if format_type not in valid_formats:
        print(f"\n❌ Invalid format: {format_type}")
        print("Valid formats: json, txt, md\n")
        return

    try:
        # Create export directory if it doesn't exist
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)

        # Generate filename with timestamp
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{export_dir}/conversation_{timestamp}.{format_type}"

        if format_type == "json":
            # Export as JSON
            export_data = []
            for msg in ctx.conversation_history:
                msg_data = {
                    "type": type(msg).__name__,
                    "content": str(msg.content),
                    "timestamp": datetime.now().isoformat(),
                }
                export_data.append(msg_data)

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

        elif format_type == "txt":
            # Export as plain text
            with open(filename, "w", encoding="utf-8") as f:
                for msg in ctx.conversation_history:
                    msg_type = type(msg).__name__.replace("Message", "")
                    f.write(f"[{msg_type}] {msg.content}\n\n")

        elif format_type == "md":
            # Export as Markdown
            with open(filename, "w", encoding="utf-8") as f:
                f.write("# Conversation Export\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")

                for msg in ctx.conversation_history:
                    msg_type = type(msg).__name__.replace("Message", "")
                    content = str(msg.content)
                    f.write(f"### {msg_type}\n\n")
                    f.write(f"{content}\n\n")
                    f.write("---\n\n")

        print(f"\n✅ Exported conversation to: {filename}")
        print(f"📄 Format: {format_type}")
        print(f"💬 Messages: {len(ctx.conversation_history)}\n")

    except Exception as e:
        print(f"\n❌ Error exporting conversation: {e}\n")


__all__ = [
    "handle_read_command",
    "handle_write_command",
    "handle_list_command",
    "handle_pwd_command",
    "show_memory",
    "handle_clear_command",
    "handle_learn_command",
    "show_vectordb",
    "show_mem0",
    "handle_populate_command",
    "show_model_info",
    "handle_context_command",
    "handle_learning_command",
    "handle_space_command",
    "handle_export_command",
]
