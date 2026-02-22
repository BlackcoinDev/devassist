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
Test suite for ChromaDB Client (src/vectordb/client.py).

Tests cover:
- Client initialization and URL configuration
- Collection operations (list, create, delete, count)
- Document operations (add, query)
- Health check and error handling
"""

import responses
from src.vectordb.client import ChromaDBClient, get_chromadb_client


class TestChromaDBClient:
    """Test ChromaDB HTTP client operations."""

    def setup_method(self):
        """Set up test environment."""
        self.host = "localhost"
        self.port = 8000
        self.client = ChromaDBClient(host=self.host, port=self.port)
        self.base_url = f"http://{self.host}:{self.port}/api/v2"
        self.coll_url = f"{self.base_url}/tenants/default_tenant/databases/default_database/collections"

    @responses.activate
    def test_list_collections(self):
        """Test listing collections from API."""
        mock_data = [{"id": "1", "name": "coll1"}, {"id": "2", "name": "coll2"}]
        responses.add(responses.GET, self.coll_url, json=mock_data, status=200)

        collections = self.client.list_collections()
        assert len(collections) == 2
        assert collections[0]["name"] == "coll1"

    @responses.activate
    def test_get_collection_id(self):
        """Test finding a collection ID by name."""
        mock_data = [{"id": "unique-id-123", "name": "target-coll"}]
        responses.add(responses.GET, self.coll_url, json=mock_data, status=200)

        coll_id = self.client.get_collection_id("target-coll")
        assert coll_id == "unique-id-123"

        # Not found
        assert self.client.get_collection_id("missing") is None

    @responses.activate
    def test_create_collection(self):
        """Test collection creation."""
        responses.add(
            responses.POST,
            self.coll_url,
            json={"id": "new-id", "name": "new-coll"},
            status=201,
        )

        coll_id = self.client.create_collection("new-coll")
        assert coll_id == "new-id"

    @responses.activate
    def test_delete_collection(self):
        """Test collection deletion."""
        del_url = f"{self.coll_url}/target-coll"
        responses.add(responses.DELETE, del_url, status=204)

        success = self.client.delete_collection("target-coll")
        assert success is True

    @responses.activate
    def test_query_collection(self):
        """Test querying documents by embedding."""
        query_url = f"{self.coll_url}/coll-id/query"
        mock_response = {
            "documents": [["doc1", "doc2"]],
            "metadatas": [[{"source": "f1"}, {"source": "f2"}]],
        }
        responses.add(responses.POST, query_url, json=mock_response, status=200)

        docs, meta = self.client.query_collection("coll-id", [0.1, 0.2])

        assert len(docs) == 2
        assert docs[0] == "doc1"
        assert meta[1]["source"] == "f2"

    @responses.activate
    def test_add_documents(self):
        """Test adding documents with embeddings."""
        add_url = f"{self.coll_url}/coll-id/add"
        responses.add(responses.POST, add_url, status=201)

        success = self.client.add_documents(
            collection_id="coll-id",
            documents=["text"],
            embeddings=[[0.1, 0.2]],
            metadatas=[{"src": "test"}],
        )
        assert success is True

    @responses.activate
    def test_get_collection_count(self):
        """Test getting document count."""
        count_url = f"{self.coll_url}/coll-id/count"
        responses.add(responses.GET, count_url, json=42, status=200)

        count = self.client.get_collection_count("coll-id")
        assert count == 42

    @responses.activate
    def test_health_check(self):
        """Test health check endpoint."""
        responses.add(responses.GET, f"{self.base_url}/", status=200)
        assert self.client.health_check() is True

        responses.add(responses.GET, f"{self.base_url}/", status=500)
        assert self.client.health_check() is False

    def test_singleton_logic(self):
        """Test singleton accessor."""
        client1 = get_chromadb_client()
        client2 = get_chromadb_client()
        assert client1 is client2

    @responses.activate
    def test_list_collections_api_failure(self):
        """Test list_collections error handling."""
        responses.add(responses.GET, self.coll_url, status=500)

        collections = self.client.list_collections()
        assert collections == []

    @responses.activate
    def test_list_collections_exception(self):
        """Test list_collections exception handling."""
        responses.add(responses.GET, self.coll_url, body=Exception("Network error"))

        collections = self.client.list_collections()
        assert collections == []

    @responses.activate
    def test_create_collection_failure(self):
        """Test create_collection error handling."""
        responses.add(responses.POST, self.coll_url, status=500)

        coll_id = self.client.create_collection("new-coll")
        assert coll_id is None

    @responses.activate
    def test_create_collection_exception(self):
        """Test create_collection exception handling."""
        responses.add(responses.POST, self.coll_url, body=Exception("Network error"))

        coll_id = self.client.create_collection("new-coll")
        assert coll_id is None

    @responses.activate
    def test_delete_collection_failure(self):
        """Test delete_collection error handling."""
        del_url = f"{self.coll_url}/target-coll"
        responses.add(responses.DELETE, del_url, status=500)

        success = self.client.delete_collection("target-coll")
        assert success is False

    @responses.activate
    def test_delete_collection_exception(self):
        """Test delete_collection exception handling."""
        del_url = f"{self.coll_url}/target-coll"
        responses.add(responses.DELETE, del_url, body=Exception("Network error"))

        success = self.client.delete_collection("target-coll")
        assert success is False

    @responses.activate
    def test_query_collection_failure(self):
        """Test query_collection error handling."""
        query_url = f"{self.coll_url}/coll-id/query"
        responses.add(responses.POST, query_url, status=500)

        docs, meta = self.client.query_collection("coll-id", [0.1, 0.2])
        assert docs == []
        assert meta == []

    @responses.activate
    def test_query_collection_exception(self):
        """Test query_collection exception handling."""
        query_url = f"{self.coll_url}/coll-id/query"
        responses.add(responses.POST, query_url, body=Exception("Network error"))

        docs, meta = self.client.query_collection("coll-id", [0.1, 0.2])
        assert docs == []
        assert meta == []

    @responses.activate
    def test_add_documents_failure(self):
        """Test add_documents error handling."""
        add_url = f"{self.coll_url}/coll-id/add"
        responses.add(responses.POST, add_url, status=500)

        success = self.client.add_documents(
            collection_id="coll-id",
            documents=["text"],
            embeddings=[[0.1, 0.2]],
            metadatas=[{"src": "test"}],
        )
        assert success is False

    @responses.activate
    def test_add_documents_exception(self):
        """Test add_documents exception handling."""
        add_url = f"{self.coll_url}/coll-id/add"
        responses.add(responses.POST, add_url, body=Exception("Network error"))

        success = self.client.add_documents(
            collection_id="coll-id",
            documents=["text"],
            embeddings=[[0.1, 0.2]],
            metadatas=[{"src": "test"}],
        )
        assert success is False

    @responses.activate
    def test_get_collection_count_failure(self):
        """Test get_collection_count error handling."""
        count_url = f"{self.coll_url}/coll-id/count"
        responses.add(responses.GET, count_url, status=500)

        count = self.client.get_collection_count("coll-id")
        assert count == 0

    @responses.activate
    def test_get_collection_count_exception(self):
        """Test get_collection_count exception handling."""
        count_url = f"{self.coll_url}/coll-id/count"
        responses.add(responses.GET, count_url, body=Exception("Network error"))

        count = self.client.get_collection_count("coll-id")
        assert count == 0

    @responses.activate
    def test_query_collection_empty_response(self):
        """Test query_collection with empty response."""
        query_url = f"{self.coll_url}/coll-id/query"
        responses.add(responses.POST, query_url, json={}, status=200)

        docs, meta = self.client.query_collection("coll-id", [0.1, 0.2])
        assert docs == []
        assert meta == []

    @responses.activate
    def test_query_collection_missing_fields(self):
        """Test query_collection with missing fields in response."""
        query_url = f"{self.coll_url}/coll-id/query"
        responses.add(
            responses.POST, query_url, json={"other_field": "value"}, status=200
        )

        docs, meta = self.client.query_collection("coll-id", [0.1, 0.2])
        assert docs == []
        assert meta == []

    @responses.activate
    def test_add_documents_without_optional_fields(self):
        """Test add_documents without optional fields."""
        add_url = f"{self.coll_url}/coll-id/add"
        responses.add(responses.POST, add_url, status=201)

        success = self.client.add_documents(
            collection_id="coll-id",
            documents=["text"],
            embeddings=[[0.1, 0.2]],
            metadatas=None,
            ids=None,
        )
        assert success is True
