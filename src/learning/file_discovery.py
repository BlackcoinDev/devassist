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
File discovery module for finding markdown files.

This module provides functionality to discover markdown files in a directory
structure with configurable filters and exclusions.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from src.learning.config import AutoLearnConfig

# Configure logger
logger = logging.getLogger(__name__)


def discover_markdown_files(
    start_dir: str, max_size_mb: int = 5, exclude_dirs: Optional[list[str]] = None
) -> list[Path]:
    """
    Discover markdown files in a directory structure.

    Args:
        start_dir: Directory path to start discovery from
        max_size_mb: Maximum file size in MB (default: 5MB from AutoLearnConfig)
        exclude_dirs: List of directory names to exclude

    Returns:
        List of Path objects for discovered markdown files

    Patterns:
        - *.md in root directory
        - docs/*.md
        - src/AGENTS.md
        - tests/AGENTS.md

    Exclusions:
        - .sisyphus/
        - __pycache__/
        - .git/
        - node_modules/
        - .venv/
    """
    # Use default max_size_mb from AutoLearnConfig if not provided
    if max_size_mb is None:
        config = AutoLearnConfig()
        max_size_mb = config.auto_learn_max_file_size_mb

    # Set default exclude directories
    if exclude_dirs is None:
        exclude_dirs = [".sisyphus", "__pycache__", ".git", "node_modules", ".venv"]

    # Convert max_size_mb to bytes
    max_size_bytes = max_size_mb * 1024 * 1024

    discovered_files: list[Path] = []

    # Check if start directory exists
    if not os.path.exists(start_dir):
        logger.warning(f"Start directory does not exist: {start_dir}")
        return discovered_files

    if not os.path.isdir(start_dir):
        logger.warning(f"Start path is not a directory: {start_dir}")
        return discovered_files

    # Walk through directory structure
    for root, dirs, files in os.walk(start_dir):
        # Remove excluded directories from traversal
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for filename in files:
            # Check for markdown extensions
            if filename.lower().endswith((".md", ".markdown")):
                file_path = os.path.join(root, filename)

                # Check file size
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > max_size_bytes:
                        logger.warning(
                            f"Skipping large file: {file_path} ({file_size / (1024 * 1024):.2f} MB)"
                        )
                        continue

                    # Add to discovered files
                    discovered_files.append(Path(file_path).resolve())
                    logger.debug(f"Found markdown file: {file_path}")

                except (OSError, PermissionError) as e:
                    logger.warning(f"Error accessing file {file_path}: {e}")
                    continue

    logger.info(f"Discovered {len(discovered_files)} markdown files from {start_dir}")
    return discovered_files
