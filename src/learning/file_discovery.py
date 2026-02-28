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
"""File discovery module for finding markdown files."""

import logging
import os
from pathlib import Path
from typing import Optional

from src.learning.config import AutoLearnConfig

logger = logging.getLogger(__name__)


def discover_markdown_files(
    start_dir: str, max_size_mb: int = 5, include_dirs: Optional[list[str]] = None
) -> list[Path]:
    """
    Discover markdown files in specific directories only.

    Only scans:
    - Root folder (*.md files in project root only, not subdirectories)
    - docs/ folder (all *.md files recursively)

    Args:
        start_dir: Project root directory path
        max_size_mb: Maximum file size in MB (default: 5MB)
        include_dirs: List of directories to scan (default: [".", "docs"])

    Returns:
        List of Path objects for discovered markdown files
    """
    if max_size_mb is None:
        config = AutoLearnConfig()
        max_size_mb = config.auto_learn_max_file_size_mb

    # Only scan these directories
    if include_dirs is None:
        include_dirs = [".", "docs"]

    max_size_bytes = max_size_mb * 1024 * 1024
    discovered_files: list[Path] = []

    if not os.path.exists(start_dir):
        logger.warning(f"Start directory does not exist: {start_dir}")
        return discovered_files

    if not os.path.isdir(start_dir):
        logger.warning(f"Start path is not a directory: {start_dir}")
        return discovered_files

    for include_dir in include_dirs:
        target_dir = os.path.join(start_dir, include_dir)

        if not os.path.exists(target_dir):
            logger.debug(f"Include directory does not exist: {target_dir}")
            continue

        if include_dir == ".":
            # Root folder: only get *.md files directly in root (not subdirectories)
            for filename in os.listdir(target_dir):
                if filename.lower().endswith((".md", ".markdown")):
                    file_path = os.path.join(target_dir, filename)
                    if os.path.isfile(file_path):
                        try:
                            file_size = os.path.getsize(file_path)
                            if file_size <= max_size_bytes:
                                discovered_files.append(Path(file_path).resolve())
                                logger.debug(f"Found markdown file: {file_path}")
                            else:
                                logger.debug(f"Skipping large file: {file_path}")
                        except (OSError, PermissionError) as e:
                            logger.warning(f"Error accessing file {file_path}: {e}")
        else:
            # Other folders: scan recursively
            for root, dirs, files in os.walk(target_dir):
                for filename in files:
                    if filename.lower().endswith((".md", ".markdown")):
                        file_path = os.path.join(root, filename)
                        try:
                            file_size = os.path.getsize(file_path)
                            if file_size <= max_size_bytes:
                                discovered_files.append(Path(file_path).resolve())
                                logger.debug(f"Found markdown file: {file_path}")
                            else:
                                logger.debug(f"Skipping large file: {file_path}")
                        except (OSError, PermissionError) as e:
                            logger.warning(f"Error accessing file {file_path}: {e}")

    logger.info(f"Discovered {len(discovered_files)} markdown files from {start_dir}")
    return discovered_files
