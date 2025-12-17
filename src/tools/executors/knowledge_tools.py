#!/usr/bin/env python3
"""
Knowledge Management Tools - Executors for AI learning and search operations.

This module provides AI tool executors for adding information to the knowledge
base and searching the learned information using semantic search.
"""

import logging
from typing import Dict, Any, Optional

from src.tools.registry import ToolRegistry
from src.core.context_utils import add_to_knowledge_base, get_relevant_context

logger = logging.getLogger(__name__)

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

        # Use shared utility to add to knowledge base
        success = add_to_knowledge_base(information, metadata)

        if success:
            return {
                "success": True,
                "information_length": len(information),
                "learned": True,
            }
        else:
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

        # Use shared utility for context retrieval
        context = get_relevant_context(query, k=limit)

        return {
            "success": True,
            "query": query,
            "results": context,
            "result_count": len(context) if context else 0,
        }

    except Exception as e:
        logger.error(f"Error searching knowledge: {e}")
        return {"error": str(e)}


__all__ = ["execute_learn_information", "execute_search_knowledge"]
