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
Knowledge Management Tools - Executors for AI learning and search operations.

This module provides AI tool executors for adding information to the knowledge
base and searching the learned information using semantic search.
"""

import logging
import time
from typing import Dict, Any, Optional

from src.tools.registry import ToolRegistry
from src.core.context_utils import add_to_knowledge_base, get_relevant_context
from src.core.config import get_config

logger = logging.getLogger(__name__)
_config = get_config()

# =============================================================================
# TOOL DEFINITIONS (OpenAI Function Calling Format)
# =============================================================================

LEARN_INFORMATION_DEFINITION = {
    "type": "function",
    "function": {
        "name": "learn_information",
        "description": "Add new information to the AI's knowledge base for future conversations",
        "parameters": {
            "type": "object",
            "properties": {
                "information": {
                    "type": "string",
                    "description": "The information to learn and remember",
                },
                "metadata": {
                    "type": "object",
                    "description": "Optional metadata about the information",
                    "properties": {
                        "source": {"type": "string"},
                        "category": {"type": "string"},
                    },
                },
            },
            "required": ["information"],
        },
    },
}

SEARCH_KNOWLEDGE_DEFINITION = {
    "type": "function",
    "function": {
        "name": "search_knowledge",
        "description": "Search the AI's learned knowledge base for relevant information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to find relevant learned information",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}


# =============================================================================
# TOOL EXECUTORS
# =============================================================================


@ToolRegistry.register("learn_information", LEARN_INFORMATION_DEFINITION)
def execute_learn_information(
    information: str, metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute learn information tool - add information to knowledge base.

    Args:
        information: Text content to learn
        metadata: Optional metadata dict

    Returns:
        Dict with success status and learning details
    """
    try:
        if not information.strip():
            return {"error": "Information cannot be empty"}

        if _config.show_tool_details:
            logger.info(f"🔧 learn_information: Adding {len(information)} chars to knowledge base")
            if metadata:
                logger.info(f"   📋 Metadata: {metadata}")

        start_time = time.time()

        # Use shared utility to add to knowledge base
        success = add_to_knowledge_base(information, metadata)

        elapsed = time.time() - start_time

        if success:
            if _config.show_tool_details:
                logger.info(f"   ✅ Successfully learned in {elapsed:.2f}s")
            return {
                "success": True,
                "information_length": len(information),
                "learned": True,
            }
        else:
            if _config.show_tool_details:
                logger.warning(f"   ❌ Failed to add to knowledge base")
            return {"error": "Failed to add information to knowledge base"}

    except Exception as e:
        logger.error(f"Error learning information: {e}")
        return {"error": str(e)}


@ToolRegistry.register("search_knowledge", SEARCH_KNOWLEDGE_DEFINITION)
def execute_search_knowledge(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Execute knowledge search tool - search the learned knowledge base.

    Args:
        query: Search query string
        limit: Maximum number of results

    Returns:
        Dict with success status and search results
    """
    try:
        if not query.strip():
            return {"error": "Query cannot be empty"}

        if _config.show_tool_details:
            logger.info(f"🔧 search_knowledge: Query='{query[:50]}...' limit={limit}")

        start_time = time.time()

        # Use shared utility for context retrieval
        context = get_relevant_context(query, k=limit)

        elapsed = time.time() - start_time
        result_count = len(context) if context else 0

        if _config.show_tool_details:
            logger.info(f"   📊 Found {result_count} results in {elapsed:.2f}s")

        return {
            "success": True,
            "query": query,
            "results": context,
            "result_count": result_count,
        }

    except Exception as e:
        logger.error(f"Error searching knowledge: {e}")
        return {"error": str(e)}


__all__ = ["execute_learn_information", "execute_search_knowledge"]
