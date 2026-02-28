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
Learning Commands - Add information to the knowledge base.

This module provides command handlers for learning information via
/learn, bulk importing codebases via /populate, and learning from web pages.
"""

from datetime import datetime

from typing import List
from src.commands.registry import CommandRegistry
from src.core.context import get_context
from src.core.context_utils import add_to_knowledge_base
from src.core.config import get_config, get_logger
from src.storage import cleanup_memory
from src.learning.auto_learn import (
    is_content_duplicate,
    register_content_hash,
    get_content_hash_for_string,
)

logger = get_logger()
_config = get_config()

# Local operation counter for URL learning
_operation_count = 0


def execute_learn_url(url: str) -> dict:
    """
    Fetch and learn content from a URL using Docling.

    This function leverages Docling's ability to fetch and parse web pages
    into structured markdown, which is then added to the knowledge base.
    """
    global _operation_count

    try:
        from docling.document_converter import DocumentConverter
        from langchain_core.documents import Document

        # Initialize converter
        converter = DocumentConverter()

        # Convert web content directly from URL
        # Docling handles fetching and HTML-to-Markdown conversion
        result = converter.convert(url)
        content = result.document.export_to_markdown()

        # Check for duplicate content
        content_hash = get_content_hash_for_string(content)
        if is_content_duplicate(content_hash):
            return {"skipped": True, "reason": "duplicate", "url": url}

        # Create metadata
        title = "Web Page"  # Docling might expose title, but safe default
        if hasattr(result.document, "title") and getattr(
            result.document, "title", None
        ):
            title = getattr(result.document, "title")

        doc = Document(
            page_content=content,
            metadata={
                "source": url,
                "title": title,
                "type": "web_page",
                "added_at": datetime.now().isoformat(),
            },
        )

        # Add to vector store using context
        ctx = get_context()
        if ctx.vectorstore:
            # Use the existing logic or direct add
            ctx.vectorstore.add_documents([doc])

            # Register hash to prevent duplicates
            register_content_hash(content_hash)

            # Periodic cleanup logic from handle_learn_command
            _operation_count += 1
            if _operation_count % 50 == 0:
                cleanup_memory()

            return {"success": True, "title": title, "url": url, "length": len(content)}
        else:
            return {"error": "Vector database not initialized"}

    except ImportError:
        return {"error": "docling library not installed"}
    except Exception as e:
        return {"error": str(e)}


__all__ = [
    "handle_learn",
    "handle_populate",
    "handle_web",
]

# =============================================================================
# COMMAND HANDLERS
# =============================================================================


@CommandRegistry.register(
    "learn", "Add information to knowledge base", category="learning"
)
def handle_learn(args: List[str]) -> None:
    """Handle /learn command."""
    ctx = get_context()

    if _config.verbose_logging:
        logger.debug(f"/learn command invoked with {len(args)} args")

    # Check if embeddings are available (needed for learning)
    if ctx.embeddings is None:
        print("\nEmbeddings not available. Ollama is required for learning features.\n")
        return

    # Get content from args
    content = " ".join(args) if args else ""

    if not content:
        print("\nUsage: /learn <information to remember>\n")
        return

    if _config.verbose_logging:
        logger.info(f"📚 Learning content: {len(content)} chars")

    # Use shared utility to add to knowledge base
    print(f"\n📚 Learning: {content}")

    # Check for duplicate content
    content_hash = get_content_hash_for_string(content)
    if is_content_duplicate(content_hash):
        print(f"⚠️  Already learned: {content[:50]}...\n")
        return

    success = add_to_knowledge_base(content)

    if success:
        # Register the hash to prevent duplicates
        register_content_hash(content_hash)
        if _config.verbose_logging:
            logger.info("   ✅ Successfully added to knowledge base")
        print(f"✅ Learned: {content[:50]}...\n")
    else:
        if _config.verbose_logging:
            logger.warning("   ❌ Failed to add to knowledge base")
        print("❌ Failed to learn information\n")


@CommandRegistry.register("populate", "Bulk import codebase", category="learning")
def handle_populate(args: List[str]) -> None:
    """Handle the /populate command to bulk import codebases."""
    import os
    from src.core.utils import chunk_text
    from src.core.context_utils import add_to_knowledge_base
    from langchain_core.documents import Document

    dir_path = " ".join(args) if args else "."

    if not dir_path:
        dir_path = "."

    # Expand path and verify it exists
    dir_path = os.path.expanduser(dir_path)
    if not os.path.exists(dir_path):
        print(f"\n❌ Error: Directory '{dir_path}' not found\n")
        return

    if not os.path.isdir(dir_path):
        print(f"\n❌ Error: '{dir_path}' is not a directory\n")
        return

    # Supported file extensions
    text_extensions = {
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".swift",
        ".kt",
        ".scala",
        ".r",
        ".m",
        ".md",
        ".txt",
        ".rst",
        ".adoc",
        ".tex",
        ".json",
        ".yaml",
        ".yml",
        ".xml",
        ".html",
        ".htm",
        ".css",
        ".scss",
        ".sass",
        ".less",
        ".sh",
        ".bash",
        ".zsh",
        ".fish",
        ".ps1",
        ".bat",
        ".cmd",
        ".sql",
        ".vim",
        ".el",
        ".clj",
        ".cljs",
        ".edn",
        ".erl",
        ".hrl",
        ".ex",
        ".exs",
        ".ml",
        ".mli",
        ".fs",
        ".fsx",
        ".fsi",
        ".hs",
        ".lhs",
        ".jl",
        ".lua",
        ".moon",
        ".nims",
        ".nim",
        ".cr",
        ".pony",
        ".zig",
        ".v",
        ".vlt",
        ".sv",
        ".svh",
        ".vhd",
        ".vhdl",
    }

    # Binary extensions to skip
    binary_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".ico",
        ".svg",
        ".webp",
        ".mp3",
        ".mp4",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".zip",
        ".tar",
        ".gz",
        ".bz2",
        ".7z",
        ".rar",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".bin",
        ".dat",
        ".db",
        ".sqlite",
        ".sqlite3",
    }

    # Directories to skip
    skip_dirs = {
        ".git",
        ".svn",
        ".hg",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        ".venv",
        "venv",
        "env",
        ".env",
        "dist",
        "build",
        ".idea",
        ".vscode",
        ".vs",
        "*.egg-info",
        ".eggs",
    }

    if _config.verbose_logging:
        logger.info(f"📁 Populating from directory: {dir_path}")

    print(f"\n📁 Scanning directory: {dir_path}")

    files_processed = 0
    files_skipped = 0
    chunks_added = 0
    errors = 0

    try:
        for root, dirs, files in os.walk(dir_path):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]

            for filename in files:
                # Skip hidden files
                if filename.startswith("."):
                    continue

                file_path = os.path.join(root, filename)

                # Check extension
                _, ext = os.path.splitext(filename)
                ext = ext.lower()

                if ext in binary_extensions:
                    files_skipped += 1
                    continue

                if ext not in text_extensions and not filename.endswith("Makefile"):
                    # Try to read as text anyway if no extension
                    if ext:
                        files_skipped += 1
                        continue

                # Try to read and process the file
                try:
                    # Check file size (skip files > 10MB)
                    file_size = os.path.getsize(file_path)
                    if file_size > 10 * 1024 * 1024:
                        if _config.verbose_logging:
                            logger.warning(f"   ⚠️ Skipping large file: {filename}")
                        files_skipped += 1
                        continue

                    # Try to read as UTF-8
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        # Try with different encoding
                        try:
                            with open(file_path, "r", encoding="latin-1") as f:
                                content = f.read()
                        except Exception:
                            files_skipped += 1
                            continue

                    # Skip empty files
                    if not content.strip():
                        continue

                    # Check for duplicate content
                    content_hash = get_content_hash_for_string(content)
                    if is_content_duplicate(content_hash):
                        if _config.verbose_logging:
                            logger.debug(f"   Skipping duplicate file: {filename}")
                        files_skipped += 1
                        continue

                    # Get relative path for metadata
                    rel_path = os.path.relpath(file_path, dir_path)

                    # Chunk the content
                    chunks = chunk_text(content)

                    # Create documents from chunks
                    for i, chunk in enumerate(chunks):
                        doc = Document(
                            page_content=chunk,
                            metadata={
                                "source": file_path,
                                "relative_path": rel_path,
                                "filename": filename,
                                "chunk_index": i,
                                "total_chunks": len(chunks),
                                "type": "code_file",
                            },
                        )

                        # Add to knowledge base
                        if add_to_knowledge_base(doc.page_content, doc.metadata):
                            chunks_added += 1

                    # Register hash after successful processing
                    register_content_hash(content_hash)
                    files_processed += 1

                    if _config.verbose_logging and files_processed % 10 == 0:
                        logger.info(f"   📄 Processed {files_processed} files...")

                except Exception as e:
                    if _config.verbose_logging:
                        logger.warning(f"   ⚠️ Error processing {filename}: {e}")
                    errors += 1

    except Exception as e:
        print(f"\n❌ Error scanning directory: {e}\n")
        return

    # Print summary
    print("\n✅ Population complete!")
    print(f"   📄 Files processed: {files_processed}")
    print(f"   📝 Chunks added: {chunks_added}")
    print(f"   ⏭️ Files skipped: {files_skipped}")
    if errors > 0:
        print(f"   ⚠️ Errors: {errors}")
    print()


@CommandRegistry.register("web", "Learn from webpage", category="learning")
def handle_web(args: List[str]) -> None:
    """
    Handle /web command to learn from a webpage.
    """
    url = args[0] if args else ""

    if not url:
        print("\nUsage: /web <url>\n")
        return

    if _config.verbose_logging:
        logger.info(f"🌐 /web command: Fetching URL {url}")

    print(f"\n🌐 Learning from URL: {url}")
    result = execute_learn_url(url)

    if "error" in result:
        if _config.verbose_logging:
            logger.warning(f"   ❌ URL learning failed: {result['error']}")
        print(f"\n❌ Error: {result['error']}\n")
    elif result.get("skipped"):
        print(f"\n⚠️  Already learned: {url}\n")
    elif result.get("success"):
        if _config.verbose_logging:
            logger.info("   ✅ Successfully learned from URL")
        print(f"\n✅ Successfully learned from {url}\n")


__all__ = ["handle_learn", "handle_populate", "handle_web"]
