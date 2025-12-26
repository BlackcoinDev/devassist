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
Database Commands - Display vector database information.

This module provides command handlers for viewing ChromaDB vector
database contents and statistics.
"""

from src.core.context_utils import _get_api_session
from typing import List, Dict, Optional
from datetime import datetime
import logging

from src.commands.registry import CommandRegistry
from src.core.context import get_context
from src.core.config import get_config
from src.vectordb import get_space_collection_name

logger = logging.getLogger()

__all__ = [
    "handle_vectordb",
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _find_collection_for_space(collection_name: str, ctx, config) -> Optional[str]:
    """Find collection ID for current space via API."""
    try:
        list_url = f"http://{config.chroma_host}:{config.chroma_port}/api/v2/tenants/default_tenant/databases/default_database/collections"
        api_session = _get_api_session()
        list_response = api_session.get(list_url, timeout=10)

        if list_response.status_code == 200:
            collections = list_response.json()
            for coll in collections:
                if coll.get("name") == collection_name:
                    return coll.get("id")
        return None
    except Exception as e:
        logger.warning(f"Error finding collection: {e}")
        return None


def _get_collection_count(collection_id: str, config) -> Optional[int]:
    """Get document count from collection."""
    try:
        count_url = (
            f"http://{config.chroma_host}:{config.chroma_port}/api/v2/"
            "tenants/default_tenant/databases/default_database/"
            f"collections/{collection_id}/count"
        )
        api_session = _get_api_session()
        count_response = api_session.get(count_url, timeout=10)

        if count_response.status_code == 200:
            count_data = count_response.json()
            return (
                count_data
                if isinstance(count_data, int)
                else count_data.get("count", 0)
            )
        return None
    except Exception as e:
        logger.warning(f"Error getting collection count: {e}")
        return None


def _analyze_collection_metadata(
    collection_name: str, chunk_count: int, ctx
) -> Dict[str, object]:
    """Analyze metadata from collection for statistics."""
    stats: Dict[str, object] = {
        "sources": set(),
        "content_types": set(),
        "date_range": None,
        "sample_sources": [],
    }

    try:
        if (
            ctx.vectorstore is None
            or not hasattr(ctx.vectorstore, "_client")
            or ctx.vectorstore._client is None
        ):
            return stats

        chroma_client = ctx.vectorstore._client
        collection = chroma_client.get_collection(collection_name)
        results = collection.get(
            limit=min(chunk_count, 1000),  # Sample up to 1000 for stats
            include=["metadatas"],
        )

        if results and "metadatas" in results and results["metadatas"]:
            metadatas = results["metadatas"]
            dates: List[str] = []

            for metadata in metadatas:
                if metadata:
                    if "source" in metadata:
                        sources_set = stats["sources"]
                        if isinstance(sources_set, set):
                            sources_set.add(metadata["source"])
                    if "content_type" in metadata:
                        content_types_set = stats["content_types"]
                        if isinstance(content_types_set, set):
                            content_types_set.add(metadata["content_type"])
                    if "added_at" in metadata:
                        dates.append(metadata["added_at"])

            # Calculate date range
            if dates:
                try:
                    date_objs = [
                        datetime.fromisoformat(d.replace("Z", "+00:00"))
                        for d in dates
                        if d
                    ]
                    if date_objs:
                        earliest = min(date_objs)
                        latest = max(date_objs)
                        stats["date_range"] = (earliest, latest)
                except Exception:
                    pass

            # Get sample sources
            sample_sources_list = stats["sample_sources"]
            if isinstance(sample_sources_list, list):
                for metadata in metadatas[:5]:
                    if metadata and metadata.get("source"):
                        sample_sources_list.append(
                            (
                                metadata.get("source"),
                                metadata.get("added_at", "unknown"),
                            )
                        )
                        if len(sample_sources_list) >= 3:
                            break
    except Exception as e:
        logger.warning(f"Error analyzing metadata: {e}")

    return stats


def _format_statistics_output(
    collection_name: str, chunk_count: int, current_space: str, stats: Dict[str, object]
) -> str:
    """Format statistics for display."""
    output = f"📊 Collection: {collection_name}\n"
    output += f"📈 Chunks: {chunk_count}\n"
    output += f"🏢 Space: {current_space}\n\n"

    if chunk_count > 0:
        output += "📋 Statistics:\n"
        sources = stats.get("sources", set())
        content_types = stats.get("content_types", set())
        date_range = stats.get("date_range")
        sample_sources = stats.get("sample_sources", [])

        if isinstance(sources, set):
            output += f"   📄 Unique Sources: {len(sources)}\n"
            if sources:
                sources_list = ", ".join(list(sources)[:5])
                sources_str = sources_list + ("..." if len(sources) > 5 else "")
                output += f"   🔗 Sources: {sources_str}\n"

        if isinstance(content_types, set) and content_types:
            output += f"   📝 Content Types: {', '.join(content_types)}\n"

        if date_range and isinstance(date_range, tuple):
            earliest, latest = date_range
            output += f"   📅 Date Range: {earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}\n"

        if isinstance(sample_sources, list) and sample_sources:
            output += "\n🕒 Sample Sources:\n"
            for i, (source, added_at) in enumerate(sample_sources):
                output += f"   {i + 1}. {source} (added: {added_at})\n"
    else:
        output += "  No chunks found in the knowledge base.\n"
        output += "  Use /learn to add information or /populate to add codebases.\n"

    return output


# =============================================================================
# COMMAND HANDLERS
# =============================================================================


@CommandRegistry.register(
    "vectordb", "Show vector database contents", category="database"
)
def handle_vectordb(args: List[str]) -> None:
    """
    Display information about the current vector database contents.

    Shows collection statistics, chunk count, unique sources, and content insights
    from the ChromaDB vector database. Provides insights into the AI's knowledge base.
    """
    ctx = get_context()
    config = get_config()

    print("\n--- Vector Database Contents ---")

    # Get collection name for current space
    collection_name = get_space_collection_name(ctx.current_space)

    # Find the collection
    collection_id = _find_collection_for_space(collection_name, ctx, config)
    if not collection_id:
        print(f"❌ No collection found for current space '{ctx.current_space}'")
        print("The space may not have any documents yet.")
        return

    logger.info(
        f"Using collection for space {ctx.current_space}: {collection_name} (ID: {collection_id})"
    )

    # Get document count
    chunk_count = _get_collection_count(collection_id, config)
    if chunk_count is None:
        print("Failed to retrieve chunks from collection")
        print("Vector database connection may have issues.")
        return

    # Analyze metadata and get statistics
    stats = _analyze_collection_metadata(collection_name, chunk_count, ctx)

    # Format and display output
    output = _format_statistics_output(
        collection_name, chunk_count, ctx.current_space, stats
    )
    print(output)

    print("--- End Vector Database ---")


__all__ = ["handle_vectordb"]
