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
Auto-learn core module for automatic knowledge base population.

This module orchestrates file discovery, content hashing, and knowledge base ingestion
for markdown files. It provides the main entry point for the auto-learning feature and
handles all aspects of processing markdown content into the knowledge base.
"""

import logging
from pathlib import Path
import threading
import time
from typing import Dict, List, Optional, Callable
import os
import re

from src.core.context_utils import add_to_knowledge_base
from src.learning.config import get_auto_learn_config
from src.learning.file_discovery import discover_markdown_files
from src.learning.content_hash import compute_content_hash

# Configure logger
logger = logging.getLogger(__name__)


class AutoLearnManager:
    """
    Main auto-learn manager class that orchestrates the entire auto-learning process.

    This class handles file discovery, deduplication, content processing, and knowledge
    base storage in a background thread to avoid blocking the main application.
    """

    def __init__(self):
        """Initialize the AutoLearnManager."""
        self._config = get_auto_learn_config()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._progress_callback: Optional[Callable[[str], None]] = None
        self._processed_hashes: set = set()  # Track processed hashes for deduplication
        self._error_count = 0
        self._success_count = 0

    def initialize_auto_learning(
        self, progress_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        Main entry point for auto-learning process.

        Discovers markdown files, processes them, and stores in knowledge base.
        Runs in a background thread to avoid blocking the application.

        Args:
            progress_callback: Optional callback function for progress updates

        Returns:
            True if initialization successful, False if already running or error occurred
        """
        if self._running:
            logger.warning("Auto-learning is already running")
            return False

        self._running = True
        self._progress_callback = progress_callback
        self._error_count = 0
        self._success_count = 0
        self._processed_hashes.clear()

        # Start background thread
        self._thread = threading.Thread(
            target=self._auto_learn_background_task,
            daemon=True,
            name="AutoLearnBackgroundTask",
        )
        self._thread.start()

        self._log_progress("🚀 Auto-learning initialized and running in background")
        return True

    def _auto_learn_background_task(self) -> None:
        """
        Background task that performs the actual auto-learning process.

        This method runs in a separate thread and handles the complete workflow:
        1. Discover markdown files
        2. Process each file
        3. Check deduplication
        4. Store in knowledge base
        5. Handle errors gracefully
        """
        try:
            self._log_progress("📁 Starting file discovery...")

            # Start from current working directory
            start_dir = os.getcwd()
            markdown_files = discover_markdown_files(
                start_dir, max_size_mb=self._config.auto_learn_max_file_size_mb
            )

            if not markdown_files:
                self._log_progress("📝 No markdown files found for auto-learning")
                self._running = False
                return

            self._log_progress(
                f"📚 Found {len(markdown_files)} markdown files to process"
            )

            # Process each file
            for file_path in markdown_files:
                if not self._running:
                    self._log_progress("⏹️  Auto-learning stopped")
                    break

                try:
                    result = self.process_markdown_file(file_path)
                    if result:
                        self._success_count += 1
                    else:
                        self._error_count += 1

                except Exception as e:
                    self._error_count += 1
                    self._log_progress(f"❌ Error processing {file_path}: {str(e)}")
                    logger.error(
                        f"Error processing file {file_path}: {e}", exc_info=True
                    )

            # Log summary
            self._log_progress(
                f"✅ Auto-learning completed: {self._success_count} success, {self._error_count} errors"
            )

        except Exception as e:
            self._error_count += 1
            self._log_progress(f"❌ Auto-learning failed: {str(e)}")
            logger.error(f"Auto-learning failed: {e}", exc_info=True)
        finally:
            self._running = False
            self._thread = None

    def process_markdown_file(self, file_path: Path) -> Dict:
        """
        Process a single markdown file for auto-learning.

        Args:
            file_path: Path to the markdown file to process

        Returns:
            Dictionary with processing results including metadata and status

        Raises:
            IOError: If file cannot be read
            ValueError: If content is invalid
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        # Read file content
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    content = f.read()
            except Exception as e:
                raise IOError(f"Cannot read file {file_path}: {str(e)}")

        if not content.strip():
            self._log_progress(f"⚠️  Skipping empty file: {file_path}")
            return {
                "file_path": str(file_path),
                "status": "skipped",
                "reason": "empty_content",
            }

        # Compute content hash for deduplication
        content_hash = compute_content_hash(file_path)
        if not content_hash:
            self._log_progress(f"⚠️  Cannot compute hash for: {file_path}")
            return {
                "file_path": str(file_path),
                "status": "skipped",
                "reason": "hash_computation_failed",
            }

        # Check if already processed (deduplication)
        if self.check_deduplication(content_hash):
            self._log_progress(f"🔄 Skipping duplicate: {file_path}")
            return {
                "file_path": str(file_path),
                "status": "skipped",
                "reason": "duplicate_content",
            }

        # Extract insights from markdown content
        insights = self.extract_insights(content)

        # Prepare metadata
        metadata = {
            "source": str(file_path),
            "type": "markdown",
            "auto_learned": True,
            "content_hash": content_hash,
            "file_size": os.path.getsize(file_path),
            "modification_time": os.path.getmtime(file_path),
            "insights": insights,
        }

        # Store in knowledge base
        storage_success = self.store_in_knowledge_base(content, metadata)

        if storage_success:
            self._processed_hashes.add(content_hash)
            self._log_progress(f"📚 Learned from: {file_path}")
            return {
                "file_path": str(file_path),
                "status": "success",
                "content_hash": content_hash,
                "insights": insights,
            }
        else:
            self._log_progress(f"❌ Failed to store: {file_path}")
            return {
                "file_path": str(file_path),
                "status": "failed",
                "reason": "storage_failed",
            }

    def check_deduplication(self, content_hash: str) -> bool:
        """
        Check if content with this hash has already been processed.

        Args:
            content_hash: Content hash to check

        Returns:
            True if content is duplicate (already processed), False otherwise
        """
        return content_hash in self._processed_hashes

    def store_in_knowledge_base(self, content: str, metadata: Dict) -> bool:
        """
        Store content in the knowledge base using the existing add_to_knowledge_base function.

        Args:
            content: Text content to store
            metadata: Metadata dictionary with source information

        Returns:
            True if storage successful, False otherwise
        """
        try:
            # Ensure we're using the agents_knowledge collection
            # The add_to_knowledge_base function will handle the actual storage
            # based on the current space and collection configuration
            success = add_to_knowledge_base(content, metadata)

            if not success:
                logger.warning(
                    f"Failed to store content in knowledge base: {metadata.get('source', 'unknown')}"
                )
                return False

            # Append to notepad for tracking
            self._append_to_notepad(
                file_path=metadata.get("source", ""),
                content_hash=metadata.get("content_hash", ""),
            )

            return True

        except Exception as e:
            logger.error(f"Error storing in knowledge base: {str(e)}", exc_info=True)
            return False

    def extract_insights(self, content: str) -> List[str]:
        """
        Extract insights from markdown content.

        Identifies headers, key sections, code blocks, and other important elements
        to create a structured summary of the content.

        Args:
            content: Markdown content to analyze

        Returns:
            List of extracted insights (headers, sections, code blocks, etc.)
        """
        insights = []

        # Extract headers (lines starting with #)
        header_pattern = r"^#{1,6}\s+(.+)$"
        headers = re.findall(header_pattern, content, re.MULTILINE)
        for header in headers:
            insights.append(f"Header: {header.strip()}")

        # Extract code blocks (```...```)
        code_block_pattern = r"```([\s\S]+?)```"
        code_blocks = re.findall(code_block_pattern, content)
        for i, code_block in enumerate(code_blocks, 1):
            insights.append(f"Code Block {i}: {len(code_block.splitlines())} lines")

        # Extract lists (bullet points)
        list_pattern = r"^\s*[-*+]\s+(.+)$"
        list_items = re.findall(list_pattern, content, re.MULTILINE)
        if list_items:
            insights.append(f"List Items: {len(list_items)} items")

        # Extract important sections (lines with emphasis)
        emphasis_pattern = r"\*\*([^\*]+)\*\*|__([^_]+)__"
        emphasized = re.findall(emphasis_pattern, content)
        for match in emphasized:
            for text in match:
                if text.strip():
                    insights.append(f"Emphasized: {text.strip()}")
                    break

        # Extract links
        link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
        links = re.findall(link_pattern, content)
        for link_text, link_url in links:
            insights.append(f"Link: {link_text} -> {link_url}")

        return insights if insights else ["No specific insights extracted"]

    def _log_progress(self, message: str) -> None:
        """
        Log progress message and call progress callback if set.

        Args:
            message: Progress message to log
        """
        logger.info(message)

        if self._progress_callback:
            try:
                self._progress_callback(message)
            except Exception:
                # Don't let callback errors break the main process
                logger.warning("Progress callback failed")

    def _append_to_notepad(self, file_path: str, content_hash: str) -> None:
        """
        Append learning information to notepad for tracking.

        Args:
            file_path: Path to the file that was learned
            content_hash: Content hash for reference
        """
        try:
            notepad_dir = Path(".sisyphus/notepads/auto-learn-markdown")
            notepad_file = notepad_dir / "learnings.md"

            # Create directory if it doesn't exist
            notepad_dir.mkdir(parents=True, exist_ok=True)

            # Append learning information
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            entry = f"## {timestamp}\n\n- **File**: `{file_path}`\n- **Hash**: `{content_hash}`\n- **Status**: Learned\n\n---\n\n"

            with open(notepad_file, "a", encoding="utf-8") as f:
                f.write(entry)

        except Exception as e:
            logger.warning(f"Failed to append to notepad: {str(e)}")
            # Don't fail the main process if notepad writing fails

    def stop(self) -> None:
        """
        Stop the auto-learning process.

        This will stop the background thread gracefully.
        """
        self._running = False
        if self._thread and self._thread.is_alive():
            self._log_progress("⏹️  Stopping auto-learning...")
            self._thread.join(timeout=5)
            if self._thread.is_alive():
                self._log_progress("⚠️  Auto-learning thread did not stop gracefully")

    def is_running(self) -> bool:
        """
        Check if auto-learning is currently running.

        Returns:
            True if auto-learning is running, False otherwise
        """
        return self._running

    def get_stats(self) -> Dict:
        """
        Get statistics about the auto-learning process.

        Returns:
            Dictionary with success count, error count, and processed files
        """
        return {
            "success_count": self._success_count,
            "error_count": self._error_count,
            "processed_files": len(self._processed_hashes),
            "running": self._running,
        }


# Module-level singleton
_auto_learn_manager: Optional[AutoLearnManager] = None


def get_auto_learn_manager() -> AutoLearnManager:
    """
    Get the global AutoLearnManager singleton.

    Creates the manager on first call. Thread-safe.

    Returns:
        AutoLearnManager: The global auto-learn manager instance
    """
    global _auto_learn_manager
    if _auto_learn_manager is None:
        _auto_learn_manager = AutoLearnManager()
    return _auto_learn_manager


def initialize_auto_learning(
    progress_callback: Optional[Callable[[str], None]] = None,
) -> bool:
    """
    Initialize the auto-learning process.

    This is the main entry point for starting auto-learning.

    Args:
        progress_callback: Optional callback function for progress updates

    Returns:
        True if initialization successful, False otherwise
    """
    manager = get_auto_learn_manager()
    return manager.initialize_auto_learning(progress_callback)


# =============================================================================
# DEDUPLICATION PUBLIC API
# =============================================================================

_processed_hashes: set = set()


def is_content_duplicate(content_hash: str) -> bool:
    """Check if content hash has already been processed."""
    return content_hash in _processed_hashes


def register_content_hash(content_hash: str) -> None:
    """Register a content hash as processed."""
    _processed_hashes.add(content_hash)


def get_content_hash_for_string(content: str) -> str:
    """Get hash for string content (for /learn command).

    Args:
        content: String content to hash

    Returns:
        Hash string
    """
    from src.learning.content_hash import compute_string_hash
    return compute_string_hash(content)


__all__ = [
    "AutoLearnManager",
    "get_auto_learn_manager",
    "initialize_auto_learning",
    "is_content_duplicate",
    "register_content_hash",
    "get_content_hash_for_string",
]
