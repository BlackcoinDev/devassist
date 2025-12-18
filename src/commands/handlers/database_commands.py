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
Database Commands - Display vector database information.

This module provides command handlers for viewing ChromaDB vector
database contents and statistics.
"""

from typing import List
from datetime import datetime
import logging

from src.commands.registry import CommandRegistry
from src.core.context import get_context
from src.core.config import get_config
from src.vectordb import get_space_collection_name

logger = logging.getLogger(__name__)

from src.core.context_utils import _get_api_session

# =============================================================================
# COMMAND HANDLERS
# =============================================================================


@CommandRegistry.register("vectordb", "Show vector database contents", category="database")
def handle_vectordb(args: List[str]) -> None:
    """Display vector database contents."""
    """
    Display information about the current vector database contents.

    Shows collection statistics, chunk count, unique sources, and content insights
    from the ChromaDB vector database. Provides insights into the AI's knowledge base.
    """
    ctx = get_context()
    config = get_config()

    if ctx.vectorstore is None:
        print("\n❌ Vector database not available.\n")
        return

    # Initialize variables that may be used in error handling
    collection_name = get_space_collection_name(ctx.current_space)
    collection_id = None

    try:
        print("\n--- Vector Database Contents ---")

        # Try to get documents from ChromaDB via direct API
        try:
            # Find collection for current space
            # collection_name and collection_id are already initialized above

            list_url = f"http://{config.chroma_host}:{config.chroma_port}/api/v2/tenants/default_tenant/databases/default_database/collections"
            api_session = _get_api_session()
            list_response = api_session.get(list_url, timeout=10)

            if list_response.status_code == 200:
                collections = list_response.json()
                for coll in collections:
                    if coll.get("name") == collection_name:
                        collection_id = coll.get("id")
                        break

            if not collection_id:
                print(f"❌ No collection found for current space '{ctx.current_space}'")
                print("The space may not have any documents yet.")
                return

            logger.info(
                f"Using collection for space {ctx.current_space}: {collection_name} (ID: {collection_id})"
            )

            # Get collection statistics
            count_url = (
                f"http://{config.chroma_host}:{config.chroma_port}/api/v2/"
                f"tenants/default_tenant/databases/default_database/"
                f"collections/{collection_id}/count"
            )
            count_response = api_session.get(count_url, timeout=10)

            if count_response.status_code == 200:
                count_data = count_response.json()
                chunk_count = (
                    count_data
                    if isinstance(count_data, int)
                    else count_data.get("count", 0)
                )
                print(f"📊 Collection: {collection_name}")
                print(f"📈 Chunks: {chunk_count}")
                print(f"🏢 Space: {ctx.current_space}")

                if chunk_count > 0:
                    try:
                        # Get metadata for statistics
                        chroma_client = ctx.vectorstore._client
                        collection = chroma_client.get_collection(collection_name)
                        results = collection.get(
                            limit=min(chunk_count, 1000),  # Sample up to 1000 for stats
                            include=["metadatas"],
                        )

                        if results and "metadatas" in results and results["metadatas"]:
                            metadatas = results["metadatas"]

                            # Analyze metadata for insights
                            sources = set()
                            content_types = set()
                            dates = []

                            for metadata in metadatas:
                                if metadata:
                                    if "source" in metadata:
                                        sources.add(metadata["source"])
                                    if "content_type" in metadata:
                                        content_types.add(metadata["content_type"])
                                    if "added_at" in metadata:
                                        try:
                                            # Parse date
                                            dates.append(metadata["added_at"])
                                        except Exception:
                                            pass

                            print(f"\n📋 Statistics:")
                            print(f"   📄 Unique Sources: {len(sources)}")
                            if sources:
                                print(
                                    f"   🔗 Sources: {', '.join(list(sources)[:5])}{'...' if len(sources) > 5 else ''}"
                                )

                            if content_types:
                                print(
                                    f"   📝 Content Types: {', '.join(content_types)}"
                                )

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
                                        print(
                                            f"   📅 Date Range: {earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}"
                                        )
                                except Exception:
                                    pass

                            # Show recent additions (last 3 by date)
                            # Show sample sources
                            sample_sources = []
                            for metadata in metadatas[:5]:  # Check first 5 for examples
                                if metadata and metadata.get("source"):
                                    sample_sources.append(
                                        (
                                            metadata.get("source"),
                                            metadata.get("added_at", "unknown"),
                                        )
                                    )
                                    if len(sample_sources) >= 3:
                                        break

                            if sample_sources:
                                print(f"\n🕒 Sample Sources:")
                                for i, (source, added_at) in enumerate(sample_sources):
                                    print(f"   {i + 1}. {source} (added: {added_at})")

                        else:
                            print("\n📋 Statistics: Unable to retrieve metadata")

                    except Exception as e:
                        print(f"\n❌ Error retrieving statistics: {e}")
                else:
                    print(f"\n  No chunks found in the knowledge base.")
                    print(
                        f"  Use /learn to add information or /populate to add codebases."
                    )
            else:
                print(f"Failed to retrieve chunks: HTTP {count_response.status_code}")
                print("Vector database connection may have issues.")

            print("--- End Vector Database ---")

        except Exception as e:
            print(f"❌ Error displaying vector database: {str(e)}")

            # Get collection statistics instead of all documents
            count_url = (
                f"http://{config.chroma_host}:{config.chroma_port}/api/v2/"
                f"tenants/default_tenant/databases/default_database/"
                f"collections/{collection_id}/count"
            )
            count_response = api_session.get(count_url, timeout=10)

            if count_response.status_code == 200:
                count_data = count_response.json()
                count = (
                    count_data
                    if isinstance(count_data, int)
                    else count_data.get("count", 0)
                )
                print(f"📊 Collection: {collection_name}")
                print(f"📈 Documents: {count}")
                print(f"🏢 Space: {ctx.current_space}")

                if count > 0:
                    print("\n📄 Sample Documents:")
                    try:
                        # Try to get sample documents using ChromaDB client
                        # directly
                        chroma_client = ctx.vectorstore._client
                        collection = chroma_client.get_collection(collection_name)
                        results = collection.get(
                            limit=3, include=["documents", "metadatas"]
                        )

                        if results and "documents" in results and results["documents"]:
                            docs = results["documents"]
                            metadatas = results.get("metadatas") or [{}] * len(docs)

                            # First 3 documents
                            for i, doc in enumerate(docs[:3]):
                                metadata = metadatas[i] if i < len(metadatas) else {}
                                if isinstance(doc, str):
                                    # Clean up the preview - remove excessive
                                    # whitespace and binary-looking content
                                    preview = doc.strip()
                                    # Check for binary content, PDF metadata,
                                    # or placeholder text
                                    if (
                                        any(
                                            indicator in preview.lower()
                                            for indicator in [
                                                "<source>",
                                                "</source>",
                                                "<translation",
                                                "<<",
                                                ">>",
                                                "/type",
                                                "/pages",
                                                "xref",
                                                "trailer",
                                                "startxref",
                                            ]
                                        )
                                        or any(
                                            ord(c) < 32 and c not in "\n\t"
                                            for c in preview[:100]
                                        )
                                        or preview.startswith("[Binary file:")
                                        or "[Binary file:" in preview
                                    ):
                                        preview = "[Binary file - content not shown]"
                                    elif len(preview) > 200:
                                        preview = preview[:200] + "..."
                                    elif not preview:
                                        preview = "[empty content]"

                                    source = (
                                        metadata.get("source", "unknown")
                                        if metadata
                                        else "unknown"
                                    )
                                    added_at = (
                                        metadata.get("added_at", "unknown")
                                        if metadata
                                        else "unknown"
                                    )
                                    print(f"  {i + 1}. {source} (added: {added_at})")
                                    print(f"      Preview: {preview}")
                                else:
                                    print(
                                        f"  {i + 1}. [Non-text document: {type(doc)}]"
                                    )
                        else:
                            print("  No documents found in collection")
                    except Exception as e:
                        print(f"  Could not retrieve sample documents: {str(e)[:100]}")
                        print(
                            "  (This is normal for some document types or if the collection is empty)"
                        )
                    print()
            else:
                print("❌ Could not retrieve collection statistics")

    except Exception as e:
        print(f"❌ Error accessing vector database: {e}")


__all__ = ["handle_vectordb"]
