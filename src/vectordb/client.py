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
ChromaDB client wrapper for DevAssist.

This module provides a unified interface for ChromaDB operations,
eliminating the 10+ duplicated API URL patterns in the codebase.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.core.config import get_config

logger = logging.getLogger(__name__)


class ChromaDBClient:
    """
    Unified ChromaDB HTTP API client.

    This class consolidates all ChromaDB API operations into a single
    interface, eliminating duplicated URL construction and error handling.

    Attributes:
        host: ChromaDB server hostname
        port: ChromaDB server port
        base_url: Base URL for API calls
        session: Requests session with retry logic
    """

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        """
        Initialize ChromaDB client.

        Args:
            host: ChromaDB server host (defaults to config)
            port: ChromaDB server port (defaults to config)
        """
        config = get_config()
        self.host = host or config.chroma_host
        self.port = port or config.chroma_port
        self.base_url = f"http://{self.host}:{self.port}/api/v2"
        self.collections_url = f"{self.base_url}/tenants/default_tenant/databases/default_database/collections"
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy, pool_connections=10, pool_maxsize=20
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def list_collections(self, timeout: int = 10) -> List[Dict[str, Any]]:  # type: ignore
        """
        List all collections in the database.

        Returns:
            List of collection dictionaries with 'id' and 'name' keys

        Raises:
            requests.RequestException: If API call fails
        """
        logger.debug(f"   Listing collections (timeout={timeout} seconds)...")
        logger.debug(f"   Collections URL: {self.collections_url}")

        try:
            response = self.session.get(self.collections_url, timeout=timeout)
            logger.debug(f"   Response status: {response.status_code}")
            if response.status_code == 200:
                logger.debug(f"   Found {len(response.json())} collections")
                return response.json()
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []

    def get_collection_id(self, name: str, timeout: int = 10) -> Optional[str]:
        """
        Get collection ID by name.

        Args:
            name: Collection name to find

        Returns:
            Collection ID string or None if not found
        """
        collections = self.list_collections(timeout)
        for coll in collections:
            if coll.get("name") == name:
                return coll.get("id")
        return None

    def create_collection(self, name: str, timeout: int = 10) -> Optional[str]:
        """
        Create a new collection.

        Args:
            name: Name for the new collection

        Returns:
            Collection ID if created, None on failure
        """
        try:
            payload = {"name": name}
            response = self.session.post(
                self.collections_url, json=payload, timeout=timeout
            )
            if response.status_code in (200, 201):
                data = response.json()
                return data.get("id")
            logger.warning(
                f"Failed to create collection '{name}': HTTP {response.status_code}"
            )
            return None
        except Exception as e:
            logger.error(f"Error creating collection '{name}': {e}")
            return None

    def delete_collection(self, name: str, timeout: int = 10) -> bool:
        """
        Delete a collection by name.

        Args:
            name: Name of collection to delete

        Returns:
            True if deleted, False otherwise
        """
        try:
            delete_url = f"{self.collections_url}/{name}"
            response = self.session.delete(delete_url, timeout=timeout)
            if response.status_code in (200, 204):
                logger.info(f"Deleted collection: {name}")
                return True
            logger.warning(
                f"Failed to delete collection '{name}': HTTP {response.status_code}"
            )
            return False
        except Exception as e:
            logger.error(f"Error deleting collection '{name}': {e}")
            return False

    def query_collection(
        self,
        collection_id: str,
        query_embedding: List[float],
        n_results: int = 3,
        timeout: int = 10,
    ) -> Tuple[List[str], List[Dict]]:
        """
        Query a collection by embedding vector.

        Args:
            collection_id: ID of collection to query
            query_embedding: Embedding vector for similarity search
            n_results: Number of results to return

        Returns:
            Tuple of (documents, metadatas) lists
        """
        try:
            query_url = f"{self.collections_url}/{collection_id}/query"
            payload = {"query_embeddings": [query_embedding], "n_results": n_results}
            response = self.session.post(query_url, json=payload, timeout=timeout)

            if response.status_code == 200:
                data = response.json()
                documents: list[str] = []
                metadatas: list[dict] = []

                if "documents" in data and data["documents"]:
                    documents = data["documents"][0] if data["documents"] else []
                if "metadatas" in data and data["metadatas"]:
                    metadatas = data["metadatas"][0] if data["metadatas"] else []

                return documents, metadatas

            logger.warning(f"Query failed: HTTP {response.status_code}")
            return [], []

        except Exception as e:
            logger.error(f"Error querying collection: {e}")
            return [], []

    def add_documents(
        self,
        collection_id: str,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
        timeout: int = 30,
    ) -> bool:
        """
        Add documents to a collection.

        Args:
            collection_id: ID of collection
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs

        Returns:
            True if successful, False otherwise
        """
        try:
            add_url = f"{self.collections_url}/{collection_id}/add"
            payload = {
                "documents": documents,
                "embeddings": embeddings,
            }
            if metadatas:
                payload["metadatas"] = metadatas
            if ids:
                payload["ids"] = ids
            else:
                # Generate IDs if not provided
                import uuid

                payload["ids"] = [str(uuid.uuid4()) for _ in documents]

            response = self.session.post(add_url, json=payload, timeout=timeout)
            return response.status_code in (200, 201)

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False

    def get_collection_count(self, collection_id: str, timeout: int = 10) -> int:
        """
        Get the number of documents in a collection.

        Args:
            collection_id: ID of collection

        Returns:
            Document count, or 0 on error
        """
        try:
            count_url = f"{self.collections_url}/{collection_id}/count"
            response = self.session.get(count_url, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            return 0
        except Exception as e:
            logger.error(f"Error getting collection count: {e}")
            return 0

    def health_check(self, timeout: int = 5) -> bool:
        """
        Check if ChromaDB server is reachable.

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/", timeout=timeout)
            return response.status_code == 200
        except Exception:
            return False


# Module-level singleton
_client: Optional[ChromaDBClient] = None


def get_chromadb_client() -> ChromaDBClient:
    """
    Get the ChromaDB client singleton.

    Returns:
        ChromaDBClient: Shared client instance
    """
    global _client
    if _client is None:
        _client = ChromaDBClient()
    return _client
