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
Test configuration and shared fixtures for AI Assistant tests.

This module provides shared test fixtures and configuration for the entire test suite.
Fixtures are automatically available to all test functions without explicit imports.

Command Line Options:
- --run-gui-tests: Enable GUI tests (normally skipped to prevent crashes)

Fixtures:
- mock_vectorstore: Mocked ChromaDB vector store
- mock_llm: Mocked language model for AI interactions
- mock_embeddings: Mocked text embeddings for vectorization
"""

import pytest
from unittest.mock import MagicMock
import os

# Load environment variables from .env file for tests
try:
    from dotenv import load_dotenv

    # Load from project root
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    # dotenv not available, continue with system environment
    pass


@pytest.fixture
def mock_vectorstore():
    """Mock vectorstore for testing.

    Provides a mocked ChromaDB vector store with common methods
    pre-configured to avoid actual database operations.

    Returns:
        MagicMock: Configured vectorstore mock
    """
    mock_vs = MagicMock()
    mock_vs.add_documents = MagicMock()
    return mock_vs


@pytest.fixture
def mock_llm():
    """Mock LLM for testing.

    Provides a mocked language model that simulates streaming responses
    without requiring actual API calls to external services.

    Returns:
        MagicMock: Configured LLM mock with streaming capability
    """
    mock_llm = MagicMock()
    mock_llm.stream = MagicMock(return_value=["Test response"])
    return mock_llm


@pytest.fixture
def mock_embeddings():
    """Mock embeddings for testing.

    Provides mocked text embedding functionality to avoid
    expensive vectorization operations during testing.

    Returns:
        MagicMock: Configured embeddings mock with query and document methods
    """
    mock_emb = MagicMock()
    mock_emb.embed_query = MagicMock(return_value=[0.1, 0.2, 0.3])
    mock_emb.embed_documents = MagicMock(return_value=[[0.1, 0.2, 0.3]])
    return mock_emb



