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
# Test fixtures and sample data for AI Assistant tests

# Sample conversation messages for testing (future use)
SAMPLE_MESSAGES = [  # noqa: F841 # vulture: noqa
    {"type": "SystemMessage", "content": "You are a helpful AI assistant."},
    {"type": "HumanMessage", "content": "Hello, how are you?"},
    {
        "type": "AIMessage",
        "content": "I'm doing well, thank you for asking! How can I help you today?",
    },
    {"type": "HumanMessage", "content": "Can you explain what this code does?"},
    {
        "type": "AIMessage",
        "content": "I'd be happy to help explain the code. Could you share the specific code you'd like me to analyze?",
    },
]

# Sample slash commands for testing (future use)
SAMPLE_COMMANDS = [  # noqa: F841 # vulture: noqa
    "/help",
    "/memory",
    "/clear",
    "/vectordb",
    "/mem0",
    "/model",
    "/context auto",
    "/learning normal",
    "/space list",
    "/export json",
]

# Sample environment configuration for testing (future use)
TEST_ENV_CONFIG = {  # noqa: F841 # vulture: noqa
    "LM_STUDIO_URL": "http://localhost:1234/v1",
    "LM_STUDIO_KEY": "test-key-12345",
    "MODEL_NAME": "qwen3-vl-30b",
    "CHROMA_HOST": "localhost",
    "CHROMA_PORT": "8000",
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "EMBEDDING_MODEL": "qwen3-embedding:latest",
    "DB_TYPE": "sqlite",
    "DB_PATH": ":memory:",
    "MAX_HISTORY_PAIRS": "10",
    "TEMPERATURE": "0.7",
    "MAX_INPUT_LENGTH": "1000",
}

# Sample vector database content for testing (future use)
SAMPLE_VECTOR_CONTENT = [  # noqa: F841 # vulture: noqa
    {
        "id": "doc_1",
        "content": "This is a sample document about Python programming.",
        "metadata": {
            "source": "test.py",
            "language": "python",
            "added_at": "2024-01-01T00:00:00Z",
        },
    },
    {
        "id": "doc_2",
        "content": "LangChain is a framework for developing applications powered by language models.",
        "metadata": {
            "source": "readme.md",
            "language": "markdown",
            "added_at": "2024-01-01T00:00:00Z",
        },
    },
]

# Sample file system structure for testing (future use)
SAMPLE_FILE_STRUCTURE = {  # noqa: F841 # vulture: noqa
    "src": {
        "main.py": "# Main application file",
        "gui.py": "# GUI application file",
        "launcher.py": "# Application launcher",
    },
    "tests": {
        "unit": {
            "test_main.py": "# Unit tests for main.py",
            "test_gui.py": "# Unit tests for gui.py",
        },
        "integration": {"test_integration.py": "# Integration tests"},
    },
    "docs": {
        "README.md": "# AI Assistant\n\nA helpful AI assistant application.",
        "AGENTS.md": "# Agent Guidelines\n\nTesting guidelines and procedures.",
    },
}
