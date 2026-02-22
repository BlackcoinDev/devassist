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
Pytest fixtures for auto-learn functionality testing.

This module provides shared test fixtures for auto-learn markdown processing:
- mock_chroma_client: Mocked ChromaDB client for vector storage
- mock_embeddings: Mocked text embeddings for vectorization
- temp_md_files: Temporary markdown files for testing
- sample_md_content: Sample markdown content fixtures

Fixtures are importable from tests and follow the same patterns as conftest.py.
"""

import pytest
import tempfile
import os
from unittest.mock import MagicMock


@pytest.fixture
def mock_chroma_client():
    """Mock ChromaDB client for auto-learn testing.

    Provides a mocked ChromaDB client with common methods
    pre-configured to avoid actual database operations during
    auto-learn markdown processing tests.

    Returns:
        MagicMock: Configured ChromaDB client mock
    """
    mock_client = MagicMock()
    mock_client.create_collection = MagicMock()
    mock_client.get_collection = MagicMock()
    mock_client.add = MagicMock()
    mock_client.query = MagicMock()
    return mock_client


@pytest.fixture
def mock_embeddings():
    """Mock embeddings for auto-learn testing.

    Provides mocked text embedding functionality to avoid
    expensive vectorization operations during auto-learn
    markdown processing tests.

    Returns:
        MagicMock: Configured embeddings mock with query and document methods
    """
    mock_emb = MagicMock()
    mock_emb.embed_query = MagicMock(return_value=[0.1, 0.2, 0.3])
    mock_emb.embed_documents = MagicMock(
        return_value=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    )
    return mock_emb


@pytest.fixture
def temp_md_files():
    """Temporary markdown files for auto-learn testing.

    Creates a temporary directory with sample markdown files
    for testing auto-learn markdown processing functionality.

    Returns:
        tuple: (temp_dir_path, list_of_file_paths)
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample markdown files
        file_paths = []

        # Sample markdown file 1
        md_file1 = os.path.join(temp_dir, "sample1.md")
        with open(md_file1, "w", encoding="utf-8") as f:
            f.write(
                "# Sample Markdown 1\n\nThis is a test markdown file.\n\n## Features\n- Feature 1\n- Feature 2\n"
            )
        file_paths.append(md_file1)

        # Sample markdown file 2
        md_file2 = os.path.join(temp_dir, "sample2.md")
        with open(md_file2, "w", encoding="utf-8") as f:
            f.write(
                "# Sample Markdown 2\n\nAnother test markdown file.\n\n## Content\n- Content 1\n- Content 2\n"
            )
        file_paths.append(md_file2)

        yield (temp_dir, file_paths)


@pytest.fixture
def sample_md_content():
    """Sample markdown content fixtures for testing.

    Provides various markdown content samples for testing
    auto-learn markdown processing functionality.

    Returns:
        dict: Dictionary containing different markdown content samples
    """
    return {
        "simple": "# Simple Markdown\n\nThis is simple markdown content.\n",
        "complex": """# Complex Markdown

## Section 1

This is a complex markdown document with multiple sections.

### Subsection 1.1

- Item 1
- Item 2
- Item 3

## Section 2

More content here.

```python
def example():
    return "code block"
```

## Conclusion

Final thoughts.
""",
        "empty": "",
        "minimal": "# Minimal\n\nJust a title.",
        "with_code": """# Code Example

```python
import sys

def main():
    print("Hello World")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```
""",
    }
