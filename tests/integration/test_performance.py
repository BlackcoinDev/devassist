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
Performance and Stress tests for AI Assistant.

Focuses on:
- Startup latency
- Execution time of core utilities
- Handling of large inputs
"""

import time
import responses
from unittest.mock import MagicMock, patch
from src.core.context import reset_context, get_context
from src.core.context_utils import get_relevant_context, add_to_knowledge_base
from src.main import initialize_application


class TestPerformance:
    """Performance benchmarks for core components."""

    def setup_method(self):
        reset_context()

    def test_startup_performance(self):
        """Measure the time taken to initialize core components."""
        start_time = time.time()

        with (
            patch("src.main.initialize_database"),
            patch("src.main.initialize_llm"),
            patch("src.main.initialize_vectordb"),
            patch("src.main.initialize_user_memory"),
        ):
            initialize_application()

        duration = time.time() - start_time
        # Initialization with mocks should be very fast (< 100ms)
        assert duration < 0.1
        print(f"\n⏱️ Startup latency (mocked): {duration:.4f}s")

    @responses.activate
    @patch("src.core.context_utils.get_config")
    def test_context_retrieval_latency(self, mock_config):
        """Measure latency of context retrieval with mocked vectorstore."""
        mock_config_obj = MagicMock()
        mock_config_obj.chroma_host = "localhost"
        mock_config_obj.chroma_port = 8000
        mock_config.return_value = mock_config_obj

        # Mock ChromaDB API endpoints
        base_url = "http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections"
        responses.add(
            responses.GET,
            base_url,
            json=[{"name": "space_default", "id": "default-id"}],
            status=200,
        )
        responses.add(
            responses.POST,
            f"{base_url}/default-id/query",
            json={"documents": [["Result"]]},
            status=200,
        )

        ctx = get_context()
        ctx.vectorstore = MagicMock()

        # Mock embeddings to be slightly slow (simulating real usage)
        def slow_embed(*args, **kwargs):
            time.sleep(0.01)  # 10ms
            return [0.1] * 384

        ctx.embeddings = MagicMock()
        ctx.embeddings.embed_query.side_effect = slow_embed

        start_time = time.time()
        get_relevant_context("query")
        duration = time.time() - start_time

        # Should be consistent with the sleep + minimal overhead
        assert duration >= 0.01
        print(f"⏱️ Retrieval latency: {duration:.4f}s")

    @responses.activate
    @patch("src.core.context_utils.get_config")
    def test_large_input_resilience(self, mock_config):
        """Verify the system handles unusually large inputs without crashing."""
        # Setup configuration and mocks
        mock_config_obj = MagicMock()
        mock_config_obj.chroma_host = "localhost"
        mock_config_obj.chroma_port = 8000
        mock_config.return_value = mock_config_obj

        # Mock ChromaDB API endpoints
        base_url = "http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections"
        responses.add(
            responses.GET,
            base_url,
            json=[{"name": "space_default", "id": "default-id"}],
            status=200,
        )
        responses.add(
            responses.POST,
            f"{base_url}/default-id/upsert",
            json={"status": "success"},
            status=200,
        )

        ctx = get_context()
        ctx.vectorstore = MagicMock()
        ctx.embeddings = MagicMock()
        ctx.embeddings.embed_documents.return_value = [[0.1] * 384]

        # Create a 1MB string
        large_input = "a" * (1024 * 1024)

        # This should handle the string without crashing
        success = add_to_knowledge_base(large_input)
        assert success is True
        print(f"✅ Large input (1MB) handled successfully")

    @patch("src.core.context_utils.get_config")
    def test_memory_growth_performance(self, mock_config):
        """Measure performance degradation with increasing conversation history."""
        ctx = get_context()
        from langchain_core.messages import HumanMessage, AIMessage

        # Inject 1000 messages into history
        for i in range(500):
            ctx.conversation_history.append(HumanMessage(content=f"Message {i}"))
            ctx.conversation_history.append(AIMessage(content=f"Response {i}"))

        start_time = time.time()
        # Simulate processing that involves history (e.g. context construction)
        # Current main loop keeps last 20 messages
        llm_context_limit = 20
        enhanced_history = [ctx.conversation_history[0]] + ctx.conversation_history[
            -llm_context_limit:
        ]

        duration = time.time() - start_time
        assert len(enhanced_history) == 21
        assert duration < 0.005  # Should be near-instant
        print(f"⏱️ History slicing (1000 msgs): {duration:.6f}s")
