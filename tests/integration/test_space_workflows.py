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
Integration tests for Space Workflows.

This suite verifies end-to-end space management operations:
- Creating and switching between spaces
- Verifying knowledge isolation between spaces
- Persistence of space settings
"""

import os
import responses
from unittest.mock import MagicMock, patch
from src.vectordb.spaces import (
    list_spaces,
    delete_space,
    switch_space,
    load_current_space,
)
from src.core.context import get_context, reset_context
from src.core.context_utils import add_to_knowledge_base, get_relevant_context


class TestSpaceWorkflows:
    """End-to-end space workflow testing."""

    def setup_method(self):
        """Reset context and remove temporary settings files."""
        reset_context()
        if os.path.exists("space_settings.json"):
            os.remove("space_settings.json")

        # Reset the ChromaDB client singleton to ensure mock config is used
        import src.vectordb.client as client_module

        client_module._client = None

        self.host = "localhost"
        self.port = 8000
        self.base_url = f"http://{self.host}:{self.port}/api/v2"
        self.coll_url = (
            f"{self.base_url}/tenants/default_tenant"
            f"/databases/default_database/collections"
        )

    def teardown_method(self):
        reset_context()
        if os.path.exists("space_settings.json"):
            os.remove("space_settings.json")

        # Reset the ChromaDB client singleton
        import src.vectordb.client as client_module

        client_module._client = None

    @responses.activate
    @patch("src.vectordb.client.get_config")
    @patch("src.core.context_utils.get_config")
    def test_complete_space_lifecycle(self, mock_utils_config, mock_client_config):
        """Test creating, switching, listing, and deleting spaces."""
        # 1. Setup mocks
        mock_config = MagicMock()
        mock_config.chroma_host = self.host
        mock_config.chroma_port = self.port
        mock_client_config.return_value = mock_config
        mock_utils_config.return_value = mock_config

        ctx = get_context()
        ctx.vectorstore = MagicMock()

        # 2. List initial spaces (should only be 'default')
        responses.add(responses.GET, self.coll_url, json=[], status=200)
        spaces = list_spaces()
        assert spaces == ["default"]

        # 3. Switch to a new space (creates it implicitly in our logic)
        assert switch_space("work") is True
        assert get_context().current_space == "work"
        assert os.path.exists("space_settings.json")

        # 4. List spaces again (should show 'default' and 'work')
        # We need to clear responses to re-add with new data
        responses.replace(
            responses.GET,
            self.coll_url,
            json=[{"name": "space_work", "id": "work-id"}],
            status=200,
        )
        spaces = list_spaces()
        assert "default" in spaces
        assert "work" in spaces

        # 5. Load current space after restart
        assert load_current_space() == "work"

        # 6. Delete the space
        delete_url = f"{self.coll_url}/space_work"
        responses.add(responses.DELETE, delete_url, status=200)
        assert delete_space("work") is True

    @responses.activate
    @patch("src.core.context_utils.get_config")
    @patch("src.vectordb.client.get_config")
    def test_knowledge_isolation_between_spaces(
        self, mock_client_config, mock_utils_config
    ):
        """Verify that knowledge in one space is not visible in another."""
        # 1. Setup mocks
        mock_config = MagicMock()
        mock_config.chroma_host = self.host
        mock_config.chroma_port = self.port
        mock_client_config.return_value = mock_config
        mock_utils_config.return_value = mock_config

        ctx = get_context()
        ctx.vectorstore = MagicMock()

        # Mock embeddings
        mock_embeddings = MagicMock()
        mock_embeddings.embed_query.return_value = [0.1] * 384
        mock_embeddings.embed_documents.return_value = [[0.1] * 384]
        ctx.embeddings = mock_embeddings

        # 2. Add knowledge to 'space-a'
        switch_space("space-a")

        # API mocks for adding knowledge
        responses.add(
            responses.GET,
            self.coll_url,
            json=[{"name": "space_space-a", "id": "a-id"}],
            status=200,
        )
        responses.add(responses.POST, f"{self.coll_url}/a-id/add", status=201)

        assert add_to_knowledge_base("Secret project code: Alpha") is True

        # 3. Verify knowledge exists in 'space-a'
        responses.add(
            responses.POST,
            f"{self.coll_url}/a-id/query",
            json={"documents": [["Secret project code: Alpha"]]},
            status=200,
        )
        context_a = get_relevant_context("project code")
        assert "Alpha" in context_a

        # 4. Switch to 'space-b'
        switch_space("space-b")

        # API mocks for space-b
        responses.replace(
            responses.GET,
            self.coll_url,
            json=[
                {"name": "space_space-a", "id": "a-id"},
                {"name": "space_space-b", "id": "b-id"},
            ],
            status=200,
        )
        # Empty query results for space-b
        responses.add(
            responses.POST,
            f"{self.coll_url}/b-id/query",
            json={"documents": [[]]},
            status=200,
        )

        # 5. Verify knowledge from 'space-a' is NOT in 'space-b'
        context_b = get_relevant_context("project code")
        assert "Alpha" not in context_b
        assert context_b == ""

    def test_delete_default_space_fails(self):
        """Test that the default space cannot be deleted."""
        assert delete_space("default") is False

    @responses.activate
    def test_persistence_of_space_selection(self):
        """Verify that the chosen space persists across application context resets."""
        ctx = get_context()
        ctx.vectorstore = MagicMock()
        switch_space("persistent-space")
        assert load_current_space() == "persistent-space"

        # Simulate app restart
        reset_context()
        assert load_current_space() == "persistent-space"
