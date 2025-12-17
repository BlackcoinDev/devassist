#!/usr/bin/env python3
"""
Help and Information Commands - Display help and model information.

This module provides command handlers for showing help text and
displaying current model configuration.
"""

from typing import List
from src.commands.registry import CommandRegistry
from src.core.config import get_config, APP_VERSION

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
