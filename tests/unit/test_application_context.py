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
Test suite for ApplicationContext (src/core/context.py).

Tests cover:
- Context initialization and lifecycle
- Dependency injection and accessors
- Configuration loading and validation
- LLM and vector database integration
"""

from unittest.mock import Mock, patch
from src.core.context import ApplicationContext, get_context, set_context, reset_context


class TestContextInitialization:
    """Test ApplicationContext initialization."""

    def test_context_creation(self):
        """Test that ApplicationContext can be created."""
        context = ApplicationContext()

        # Verify context was created
        assert context is not None
        assert isinstance(context, ApplicationContext)

    def test_context_with_config(self):
        """Test that context can be created with configuration."""
        with patch("src.core.config.Config") as mock_config:
            mock_config.return_value = Mock()

            context = ApplicationContext()

            # Verify context was created
            assert context is not None


class TestContextGetters:
    """Test ApplicationContext getter methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.context = ApplicationContext()
        set_context(self.context)

    def test_get_context_returns_singleton(self):
        """Test that get_context returns the same instance."""
        context1 = get_context()
        context2 = get_context()

        assert context1 is context2

    def test_get_context_returns_correct_type(self):
        """Test that get_context returns ApplicationContext instance."""
        context = get_context()
        assert isinstance(context, ApplicationContext)


class TestContextLifecycle:
    """Test ApplicationContext lifecycle management."""

    def test_context_cleanup(self):
        """Test that cleanup works properly."""
        context = ApplicationContext()
        set_context(context)

        # Cleanup should not raise errors
        reset_context()

        # After cleanup, a new default context is created by get_context()
        # This is the expected behavior
        new_context = get_context()
        assert new_context is not context
        assert isinstance(new_context, ApplicationContext)

    def test_context_reinitialize(self):
        """Test that context can be re-initialized."""
        # First context
        context1 = ApplicationContext()
        set_context(context1)

        # Reset
        reset_context()

        # Second context should work
        context2 = ApplicationContext()
        set_context(context2)

        assert get_context() is context2

    def test_context_thread_safety(self):
        """Test that context access is thread-safe using multiple threads."""
        import threading

        reset_context()

        contexts = []

        def get_ctx():
            contexts.append(get_context())

        threads = [threading.Thread(target=get_ctx) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(contexts) == 10
        first_ctx = contexts[0]
        for ctx in contexts:
            assert ctx is first_ctx

    def test_context_state_management(self):
        """Test that context state can be managed."""
        context = ApplicationContext()
        set_context(context)

        # Context should be available
        assert get_context() is context

        # Reset and verify - get_context() creates new default context
        reset_context()
        new_context = get_context()
        assert new_context is not context
        assert isinstance(new_context, ApplicationContext)


class TestContextMethods:
    """Test individual methods of ApplicationContext."""

    def test_reset_caches(self):
        ctx = ApplicationContext()
        ctx.embedding_cache["test"] = [1.0]
        ctx.query_cache["q"] = ["res"]
        ctx.reset_caches()
        assert len(ctx.embedding_cache) == 0
        assert len(ctx.query_cache) == 0

    def test_reset_conversation(self):
        ctx = ApplicationContext()
        ctx.conversation_history.append("msg")
        ctx.reset_conversation()
        assert len(ctx.conversation_history) == 0


class TestContextAccessors:
    """Test compatibility accessors for ApplicationContext."""

    def setup_method(self):
        reset_context()
        self.ctx = get_context()

    def test_llm_accessor(self):
        from src.core.context import get_llm, set_llm

        mock_llm = Mock()
        set_llm(mock_llm)
        assert get_llm() is mock_llm
        assert self.ctx.llm is mock_llm

    def test_vectorstore_accessor(self):
        from src.core.context import get_vectorstore, set_vectorstore

        mock_vs = Mock()
        set_vectorstore(mock_vs)
        assert get_vectorstore() is mock_vs
        assert self.ctx.vectorstore is mock_vs

    def test_embeddings_accessor(self):
        from src.core.context import get_embeddings, set_embeddings

        mock_emb = Mock()
        set_embeddings(mock_emb)
        assert get_embeddings() is mock_emb
        assert self.ctx.embeddings is mock_emb

    def test_chroma_client_accessor(self):
        from src.core.context import get_chroma_client, set_chroma_client

        mock_cli = Mock()
        set_chroma_client(mock_cli)
        assert get_chroma_client() is mock_cli
        assert self.ctx.chroma_client is mock_cli

    def test_user_memory_accessor(self):
        from src.core.context import get_user_memory, set_user_memory

        mock_mem = Mock()
        set_user_memory(mock_mem)
        assert get_user_memory() is mock_mem
        assert self.ctx.user_memory is mock_mem

    def test_db_conn_accessor(self):
        from src.core.context import get_db_conn, set_db_conn

        mock_conn = Mock()
        set_db_conn(mock_conn)
        assert get_db_conn() is mock_conn
        assert self.ctx.db_conn is mock_conn

    def test_db_lock_accessor(self):
        from src.core.context import get_db_lock, set_db_lock
        import threading

        lock = threading.Lock()
        set_db_lock(lock)
        assert get_db_lock() is lock
        assert self.ctx.db_lock is lock

    def test_conversation_history_accessor(self):
        from src.core.context import get_conversation_history, set_conversation_history

        hist = ["msg1", "msg2"]
        set_conversation_history(hist)
        assert get_conversation_history() == hist
        assert self.ctx.conversation_history == hist

    def test_modes_accessors(self):
        from src.core.context import (
            get_context_mode,
            set_context_mode,
            get_learning_mode,
            set_learning_mode,
            get_current_space,
            set_current_space,
        )

        set_context_mode("on")
        assert get_context_mode() == "on"

        set_learning_mode("strict")
        assert get_learning_mode() == "strict"

        set_current_space("research")
        assert get_current_space() == "research"

    def test_cache_accessors(self):
        from src.core.context import get_embedding_cache, get_query_cache

        self.ctx.embedding_cache["k"] = [0.1]
        self.ctx.query_cache["q"] = ["r"]
        assert get_embedding_cache()["k"] == [0.1]
        assert get_query_cache()["q"] == ["r"]
