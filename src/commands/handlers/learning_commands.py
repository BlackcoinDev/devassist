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
Learning Commands - Add information to the knowledge base.

This module provides command handlers for learning information via
/learn, bulk importing codebases via /populate, and learning from web pages.
"""

import logging
from typing import List
from src.commands.registry import CommandRegistry
from src.core.context import get_context
from src.core.context_utils import add_to_knowledge_base
from src.core.config import get_config

logger = logging.getLogger(__name__)
_config = get_config()

__all__ = [
    "handle_learn",
    "handle_populate",
    "handle_web",
]

# =============================================================================
# COMMAND HANDLERS
# =============================================================================


@CommandRegistry.register(
    "learn", "Add information to knowledge base", category="learning"
)
def handle_learn(args: List[str]) -> None:
    """Handle /learn command."""
    ctx = get_context()

    if _config.verbose_logging:
        logger.debug(f"/learn command invoked with {len(args)} args")

    # Check if embeddings are available (needed for learning)
    if ctx.embeddings is None:
        print(
            "\nEmbeddings not available. Ollama is required for learning features.\n"
        )
        return

    # Get content from args
    content = " ".join(args) if args else ""

    if not content:
        print("\nUsage: /learn <information to remember>\n")
        return

    if _config.verbose_logging:
        logger.info(f"📚 Learning content: {len(content)} chars")

    # Use shared utility to add to knowledge base
    print(f"\n📚 Learning: {content}")
    success = add_to_knowledge_base(content)

    if success:
        if _config.verbose_logging:
            logger.info("   ✅ Successfully added to knowledge base")
        print(f"✅ Learned: {content[:50]}...\n")
    else:
        if _config.verbose_logging:
            logger.warning("   ❌ Failed to add to knowledge base")
        print("❌ Failed to learn information\n")


@CommandRegistry.register("populate", "Bulk import codebase", category="learning")
def handle_populate(args: List[str]) -> None:
    """
    Handle the /populate command to bulk import codebases.

    For now, this is a stub that calls the original function from main.py.
    Full extraction will be done in a future refactoring phase.
    """
    # Import the original function for now (backwards compatibility)
    from src.main import handle_populate_command

    dir_path = " ".join(args) if args else ""
    handle_populate_command(dir_path)


@CommandRegistry.register("web", "Learn from webpage", category="learning")
def handle_web(args: List[str]) -> None:
    """
    Handle /web command to learn from a webpage.

    For now, this is a stub that calls the original function from main.py.
    Full extraction will be done in a future refactoring phase.
    """
    # Import the original function for now (backwards compatibility)
    from src.main import execute_learn_url

    url = args[0] if args else ""

    if not url:
        print("\nUsage: /web <url>\n")
        return

    if _config.verbose_logging:
        logger.info(f"🌐 /web command: Fetching URL {url}")

    print(f"\n🌐 Learning from URL: {url}")
    result = execute_learn_url(url)

    if "error" in result:
        if _config.verbose_logging:
            logger.warning(f"   ❌ URL learning failed: {result['error']}")
        print(f"\n❌ Error: {result['error']}\n")
    elif result.get("success"):
        if _config.verbose_logging:
            logger.info("   ✅ Successfully learned from URL")
        print(f"\n✅ Successfully learned from {url}\n")


__all__ = ["handle_learn", "handle_populate", "handle_web"]
