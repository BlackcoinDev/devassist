#!/usr/bin/env python3
"""
Web Search Tools - Executors for internet search operations.

This module provides AI tool executors for searching the web using
DuckDuckGo's privacy-focused search engine.
"""

import logging
from typing import Dict, Any

from src.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

# =============================================================================
# TOOL DEFINITIONS (OpenAI Function Calling Format)
# =============================================================================

SEARCH_WEB_DEFINITION = {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Search the public internet for current information using DuckDuckGo (privacy-focused)",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find information online",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 10)",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    },
}


# =============================================================================
# TOOL EXECUTORS
# =============================================================================


@ToolRegistry.register("search_web", SEARCH_WEB_DEFINITION)
def execute_web_search(query: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Execute web search using DuckDuckGo.

    Args:
        query: Search query string
        max_results: Maximum number of results (default: 10)

    Returns:
        Dict with success status and search results
    """
    try:
        from duckduckgo_search import DDGS

        print(f"🌍 Searching web for: '{query}'")

        # Improve search query for better results
        enhanced_query = query
        # Don't over-enhance if already crypto-related
        crypto_keywords = [
            "cryptocurrency",
            "crypto",
            "blockchain",
            "bitcoin",
            "coin",
            "token",
            "defi",
            "web3",
        ]
        has_crypto = any(keyword in query.lower() for keyword in crypto_keywords)
        if not has_crypto and ("coin" in query.lower() or "token" in query.lower()):
            # Add context for potential crypto queries
            enhanced_query = f"{query} cryptocurrency"

        try:
            with DDGS() as ddgs:
                # Get results from DuckDuckGo
                raw_results = list(ddgs.text(enhanced_query, max_results=max_results))

            # Return results directly (no filtering)
            return {
                "success": True,
                "result_count": len(raw_results),
                "results": raw_results,
            }
        except Exception as search_err:
            # If DDGS search fails, provide diagnostic info
            logger.error(f"DDGS search execution error: {str(search_err)}")
            return {
                "error": f"Web search failed: {str(search_err)}. The duckduckgo-search package is installed but encountered an error."
            }

    except ImportError as ie:
        logger.error(f"Failed to import duckduckgo_search: {str(ie)}")
        return {
            "error": "duckduckgo-search not installed. Run: pip install duckduckgo-search"
        }
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return {"error": str(e)}


__all__ = ["execute_web_search"]
