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
Web Search Tools - Executors for internet search operations.

This module provides AI tool executors for searching the web using
DuckDuckGo's privacy-focused search engine.
"""

import logging
from typing import Dict, Any

from src.tools.registry import ToolRegistry
from src.core.config import get_config
from src.core.utils import standard_error
from src.core.constants import WEB_SEARCH_DEFAULT_MAX_RESULTS

logger = logging.getLogger(__name__)
_config = get_config()

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
def execute_web_search(
    query: str, max_results: int = WEB_SEARCH_DEFAULT_MAX_RESULTS
) -> Dict[str, Any]:
    """
    Execute web search using DuckDuckGo.

    Args:
        query: Search query string
        max_results: Maximum number of results (default: {WEB_SEARCH_DEFAULT_MAX_RESULTS})

    Returns:
        Dict with success status and search results
    """
    try:
        from ddgs import DDGS

        logger.debug("🔧 search_web: Starting")
        logger.debug(f"   Query: '{query}'")
        logger.debug(f"   Max results: {max_results}")

        if _config.show_tool_details:
            logger.info(
                f"🌍 search_web: Querying '{query}' (max {max_results} results)"
            )
        else:
            logger.debug("🔧 search_web: show_tool_details disabled")

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
            logger.debug(
                f"🔧 search_web: Enhanced query for crypto context: {enhanced_query}"
            )
        else:
            logger.debug(f"🔧 search_web: Using original query: {enhanced_query}")

        try:
            with DDGS() as ddgs:
                # Get results from DuckDuckGo
                raw_results = list(ddgs.text(enhanced_query, max_results=max_results))

            # Return results directly (no filtering)
            if _config.show_tool_details:
                logger.info(f"   📊 Found {len(raw_results)} results")
            logger.debug(f"✅ search_web: Found {len(raw_results)} results")
            return {
                "success": True,
                "result_count": len(raw_results),
                "results": raw_results,
            }
        except Exception as search_err:
            # If DDGS search fails, provide diagnostic info
            logger.error(
                f"❌ search_web: DDGS search execution error - {str(search_err)}"
            )
            return standard_error(
                f"Web search failed: {str(search_err)}. The ddgs package is installed but encountered an error."
            )

    except ImportError as ie:
        logger.error(f"❌ search_web: Failed to import duckduckgo_search - {str(ie)}")
        return standard_error("ddgs not installed. Run: pip install ddgs")
    except Exception as e:
        logger.error(f"❌ search_web: Web search failed - {e}")
        return standard_error(str(e))


async def execute_web_search_async(
    query: str, max_results: int = WEB_SEARCH_DEFAULT_MAX_RESULTS
) -> Dict[str, Any]:
    """Execute web search asynchronously using DuckDuckGo."""
    import asyncio

    try:
        from ddgs import DDGS

        logger.debug("🔧 search_web_async: Starting")
        logger.debug(f"   Query: '{query}'")

        def _do_search():
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=max_results))

        # Run search in thread to avoid blocking
        raw_results = await asyncio.to_thread(_do_search)

        logger.debug(f"✅ search_web_async: Found {len(raw_results)} results")
        return {
            "success": True,
            "result_count": len(raw_results),
            "results": raw_results,
        }

    except ImportError:
        return standard_error("ddgs not installed. Run: pip install ddgs")
    except Exception as e:
        logger.error(f"❌ search_web_async: Web search failed - {e}")
        return standard_error(str(e))


__all__ = ["execute_web_search", "execute_web_search_async"]
