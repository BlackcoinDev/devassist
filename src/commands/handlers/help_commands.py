#!/usr/bin/env python3
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
Help and Information Commands - Display help and model information.

This module provides command handlers for showing help text and
displaying current model configuration.
"""

from typing import List
from src.commands.registry import CommandRegistry
from src.core.config import get_config

# =============================================================================
# COMMAND HANDLERS
# =============================================================================


@CommandRegistry.register("help", "Show available commands", category="info")
def handle_help(args: List[str]) -> None:
    """Display available commands."""
    print("\n--- Available Commands ---")
    print("/memory       - Show conversation history")
    print("/vectordb     - Show vector database contents")
    print("/mem0         - Show personalized memory contents")
    print("/model        - Show current model information")
    print("/space <cmd>  - Space/workspace management (list/create/switch/delete)")
    print("/context <mode> - Control context integration (auto/on/off)")
    print("/learning <mode> - Control learning behavior (normal/strict/off)")
    print("/populate <path> - Add code files from directory to vector DB")
    print("/clear        - Clear conversation history")
    print("/learn <text> - Add information to knowledge base")
    print("/web <url>    - Learn content from a webpage")
    print("/export <fmt> - Export conversation (json/markdown)")
    print("/read <file>  - Read file contents")
    print("/write <file> - Write content to file")
    print("/list [dir]   - List directory contents")
    print("/pwd          - Show current directory")
    print("/search <pat> - Code search with ripgrep (aliases: /grep, /rg)")
    print("/shell <cmd>  - Execute shell command (CLI only)")
    print("/git-status   - Show git repository status (aliases: /gs, /status)")
    print("/git-log [n]  - Show commit history (aliases: /gl, /log)")
    print("/git-diff     - Show git changes (aliases: /gd, /diff)")
    print("/help         - Show this help message")
    print("")
    print("Regular commands (no slash needed):")
    print("quit    - Exit the application")
    print("exit    - Exit the application")
    print("q       - Exit the application")
    print("")
    print("Note: Quit commands work after AI finishes responding.")
    print("Use Ctrl+C for immediate interruption.")
    print("--- End Help ---\n")


@CommandRegistry.register("model", "Show current model information", category="info")
def handle_model_info(args: List[str]) -> None:
    """Show current model information."""
    config = get_config()

    print(f"\n🤖 Current Model: {config.model_name}")
    base_url_display = (
        config.lm_studio_url.replace("/v1", "") if config.lm_studio_url else "unknown"
    )
    print(f"🌐 API Endpoint: {base_url_display}")
    print(f"🎯 Temperature: {config.temperature}")
    print(f"📏 Max Input Length: {config.max_input_length}")
    print(f"💾 Context Window: {config.max_history_pairs} message pairs")
    print()


__all__ = ["handle_help", "handle_model_info"]
