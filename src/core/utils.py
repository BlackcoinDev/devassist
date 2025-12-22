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
Core utility functions extracted from main.py

This module contains utility functions that don't depend on global state
and can be safely imported by other modules.
"""

from typing import List


def chunk_text(content: str) -> List[str]:
    """
    Intelligently split text content into manageable chunks for vector storage.

    Uses intelligent chunking to preserve semantic meaning and code structure.
    This is crucial for effective retrieval-augmented generation (RAG).

    Args:
        content: The text content to be chunked (typically code or documentation)

    Returns:
        List of text chunks, each ~1500 characters with overlap for continuity
    """
    try:
        # Try to use LangChain's RecursiveCharacterTextSplitter if available
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,  # Optimal size for context retention
            chunk_overlap=200,  # Ensures semantic continuity
            separators=[
                "\n\n",
                "\n",
                " ",
                "",
            ],  # Split hierarchy: paragraphs > lines > words > chars
            keep_separator=True,  # Preserve code formatting
        )

        return text_splitter.split_text(content)
    except ImportError:
        # Fallback to simple chunking if langchain is not available
        chunk_size = 1500
        chunks = []

        # Split by paragraphs first to maintain coherence
        paragraphs = content.split("\n\n")

        current_chunk = ""
        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size, save current chunk
            if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph

        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


def validate_file_path(file_path: str, current_dir: str) -> bool:
    """
    Validate that a file path is within the allowed directory.

    Args:
        file_path: The file path to validate
        current_dir: The current working directory

    Returns:
        True if path is valid, False otherwise
    """
    import os

    full_path = os.path.abspath(file_path)
    return full_path.startswith(current_dir)


def get_file_size_info(file_path: str) -> tuple[int, str]:
    """
    Get file size information.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (file_size, formatted_size_string)
    """
    import os

    file_size = os.path.getsize(file_path)

    # Format size nicely
    if file_size < 1024:
        size_str = f"{file_size} bytes"
    elif file_size < 1024 * 1024:
        size_str = ".1f"
    else:
        size_str = ".1f"

    return file_size, size_str


def truncate_content(content: str, max_length: int = 100) -> str:
    """
    Truncate content for display purposes.

    Args:
        content: The content to truncate
        max_length: Maximum length to display

    Returns:
        Truncated content with ellipsis if needed
    """
    if len(content) <= max_length:
        return content
    return content[: max_length - 3] + "..."
