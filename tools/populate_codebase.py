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
Script to populate the ChromaDB vector database with code and document files from a directory.

Usage:
    python tools/populate_codebase.py /path/to/code/directory [--dry-run] [--direct-api]

Options:
    --dry-run     : Validate files and show what would be processed without writing to DB
    --direct-api  : Use direct ChromaDB API instead of LangChain wrapper (more reliable)

This script will:
1. Recursively scan the directory for supported files (80+ types)
2. Extract content from documents (PDF, DOCX, RTF, EPUB) using specialized libraries
3. Filter out binary files and low-quality content automatically
4. Smart chunking with paragraph-aware boundaries (1500 chars)
5. Add all content to ChromaDB collection with rich metadata
6. Provide progress updates and comprehensive statistics

Vector Database: Uses ChromaDB (same as main application) with option for direct API
"""

import os
import sys
import warnings
import argparse
from pathlib import Path
from typing import List, Optional

# Suppress warnings
warnings.filterwarnings("ignore", message="Core Pydantic V1 functionality")

# Load environment
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Code file extensions to include
CODE_EXTENSIONS = {
    # Python
    ".py": "python",
    ".pyx": "cython",
    ".pyw": "python",
    ".pyi": "python-stub",
    # JavaScript/TypeScript
    ".js": "javascript",
    ".mjs": "javascript-esm",
    ".ts": "typescript",
    ".jsx": "react",
    ".tsx": "react-typescript",
    ".vue": "vue",
    ".svelte": "svelte",
    # C/C++
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c++": "cpp",
    ".c": "c",
    ".h": "c-header",
    ".hpp": "cpp-header",
    ".hxx": "cpp-header",
    # Java/Kotlin/Scala
    ".java": "java",
    ".kt": "kotlin",
    ".scala": "scala",
    ".groovy": "groovy",
    # .NET
    ".cs": "csharp",
    ".vb": "visual-basic",
    ".fs": "fsharp",
    # Web
    ".php": "php",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    # Ruby
    ".rb": "ruby",
    ".erb": "erb",
    # Go
    ".go": "go",
    # Rust
    ".rs": "rust",
    # Swift/Objective-C
    ".swift": "swift",
    ".m": "objective-c",
    ".mm": "objective-c++",
    # Functional languages
    ".hs": "haskell",
    ".ml": "ocaml",
    ".fsx": "fsharp-script",
    ".clj": "clojure",
    ".cljs": "clojurescript",
    ".elm": "elm",
    ".ex": "elixir",
    ".exs": "elixir-script",
    # Scripting languages
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "zsh",
    ".fish": "fish",
    ".ps1": "powershell",
    ".bat": "batch",
    ".cmd": "batch",
    # Data/Config formats
    ".json": "json",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "config",
    ".conf": "config",
    ".properties": "properties",
    ".csv": "csv",
    ".tsv": "tsv",
    # Documentation
    ".md": "markdown",
    ".markdown": "markdown",
    ".rst": "restructuredtext",
    ".adoc": "asciidoc",
    ".tex": "latex",
    ".bib": "bibtex",
    # Plain text and documents
    ".txt": "text",
    ".rtf": "rich-text",
    ".doc": "word-document",
    ".docx": "word-document-xml",
    ".odt": "open-document-text",
    ".pdf": "pdf",  # Note: PDF content extraction may require additional libraries
    ".epub": "epub",
    ".mobi": "mobi",
    # Databases
    ".sql": "sql",
    ".sqlite": "sqlite",
    # Build systems
    "Makefile": "makefile",
    ".mk": "makefile",
    "CMakeLists.txt": "cmake",
    ".cmake": "cmake",
    "build.gradle": "gradle",
    ".gradle": "gradle",
    "pom.xml": "maven",
    # Other languages
    ".r": "r",
    ".R": "r",
    ".jl": "julia",
    ".pl": "perl",
    ".pm": "perl-module",
    ".lua": "lua",
    ".dart": "dart",
    ".nim": "nim",
    ".cr": "crystal",
    ".v": "vlang",
    # WebAssembly
    ".wat": "webassembly-text",
    ".wasm": "webassembly-binary",
    # Shell/Template
    ".tpl": "template",
    ".template": "template",
    ".j2": "jinja2",
}


def get_language_from_extension(file_path: str) -> str:
    """Get programming language from file extension."""
    ext = Path(file_path).suffix.lower()
    return CODE_EXTENSIONS.get(ext, "unknown")


def should_include_file(file_path: str) -> bool:
    """Check if file should be included based on extension and name."""
    path = Path(file_path)

    # Skip common files/directories to ignore
    skip_patterns = [
        "__pycache__",
        ".git",
        ".svn",
        ".hg",
        "node_modules",
        "build",
        "dist",
        ".next",
        ".nuxt",
        ".vuepress",
        ".cache",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        ".venv",
        "venv",
        "env",
        ".env",
        ".DS_Store",
        "Thumbs.db",
        "*.pyc",
        "*.pyo",
        "*.class",
        "*.jar",
        "*.war",
        "*.exe",
        "*.dll",
        "*.so",
        "*.dylib",
        "*.log",
        "*.tmp",
        "*.swp",
        "*.bak",
        "*.orig",
        "*.rej",
        ".coverage",
        "coverage.xml",
        "*.lcov",
        ".nyc_output",
    ]

    # Check if file matches skip patterns
    for pattern in skip_patterns:
        if pattern in str(path) or (
            pattern.startswith("*.") and path.name.endswith(pattern[1:])
        ):
            return False

    # Include only files with known extensions
    return path.suffix.lower() in CODE_EXTENSIONS


def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks for optimal vector database retrieval.

    Uses intelligent boundary detection, preferring paragraph breaks over line breaks
    over word breaks to maintain semantic coherence.

    Args:
        text: The text content to chunk
        chunk_size: Maximum characters per chunk (default: 1500)
        overlap: Characters to overlap between chunks (default: 200)

    Returns:
        List of text chunks with overlap for better retrieval
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at natural boundaries for better chunks
        if end < len(text):
            # Prefer breaking at double newlines (paragraphs)
            last_para = text.rfind("\n\n", start, end)
            if last_para > start + chunk_size // 2:
                end = last_para + 2
            else:
                # Fall back to single newline
                last_newline = text.rfind("\n", start, end)
                if last_newline > start + chunk_size // 2:
                    end = last_newline + 1
                else:
                    # Fall back to word boundary
                    last_space = text.rfind(" ", start, end)
                    if last_space > start + chunk_size // 2:
                        end = last_space + 1

        chunk = text[start:end].strip()
        if chunk and len(chunk) > 50:  # Skip very small chunks
            chunks.append(chunk)

        start = max(start + 1, end - overlap)  # Ensure progress

    return chunks


def is_binary_file(file_path: str, sample_size: int = 1024) -> bool:
    """
    Determine if a file is binary by analyzing its content sample.

    Checks for null bytes and calculates the ratio of printable characters
    to detect binary vs text files.

    Args:
        file_path: Path to the file to check
        sample_size: Number of bytes to sample (default: 1024)

    Returns:
        True if file appears to be binary, False if text
    """
    try:
        with open(file_path, "rb") as f:
            sample = f.read(sample_size)
            # Check for null bytes or high ratio of non-text characters
            if b"\x00" in sample:
                return True
            # Count printable characters
            printable = sum(
                1 for byte in sample if 32 <= byte <= 126 or byte in b"\t\n\r"
            )
            return printable / len(sample) < 0.7  # Less than 70% printable
    except Exception:
        return True  # Assume binary if can't read


def extract_with_docling(file_path: str) -> str:
    """
    Extract content from document files using Docling.
    """
    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(file_path)
        return result.document.export_to_markdown()
    except ImportError:
        print("⚠️  docling not installed. Install with: pip install docling")
        return ""
    except Exception as e:
        print(f"⚠️  Error extracting content with Docling from {file_path}: {e}")
        return ""


def read_file_content(file_path: str, max_size: int = 1024 * 1024) -> str:
    """Read file content with size limit, binary detection, and format-specific extraction."""
    try:
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            print(f"⚠️  Skipping large file: {file_path} ({file_size} bytes)")
            return ""

        path = Path(file_path)
        ext = path.suffix.lower()

        # Handle special file formats
        # Handle special file formats via Docling
        if ext in [".pdf", ".docx", ".rtf", ".epub", ".odt", ".pptx", ".xlsx"]:
            extracted_content = extract_with_docling(file_path)
            if extracted_content:
                return extracted_content
            # Fall back to binary check if extraction failed

        # Skip binary files (including PDFs that failed extraction)
        if is_binary_file(file_path):
            print(f"⚠️  Skipping binary file: {file_path}")
            return ""

        # Try different encodings for text files
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
        content: Optional[str] = None

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding, errors="strict") as f:
                    content = f.read()
                    break
            except UnicodeDecodeError:
                continue

        if content is None:
            print(f"⚠️  Could not decode {file_path} with any encoding, skipping")
            return ""

        return content
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return ""


def add_batch_to_database(
    documents, vectorstore, collection, use_direct_api, embeddings
):
    """
    Add a batch of documents to the vector database using the appropriate method.

    Supports both LangChain Chroma wrapper and direct ChromaDB API for maximum
    reliability and performance.

    Args:
        documents: List of Document objects to add
        vectorstore: LangChain Chroma vectorstore (if using wrapper)
        collection: Direct ChromaDB collection (if using direct API)
        use_direct_api: Whether to use direct ChromaDB API
        embeddings: Embeddings model for generating vectors
    """
    try:
        if use_direct_api and collection is not None:
            # Direct ChromaDB API
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            ids = [
                f"{doc.metadata.get('file_path', 'unknown')}_{doc.metadata.get('chunk_index', i)}"
                for i, doc in enumerate(documents)
            ]

            # Generate embeddings
            embeddings_list = embeddings.embed_documents(texts)

            collection.add(
                documents=texts,
                embeddings=embeddings_list,
                metadatas=metadatas,
                ids=ids,
            )
        elif vectorstore is not None:
            # LangChain wrapper
            vectorstore.add_documents(documents)
        else:
            return False
        return True
    except Exception as e:
        print(f"❌ Failed to add batch: {e}")
        return False


def populate_codebase(
    directory_path: str, dry_run: bool = False, use_direct_api: bool = False
):
    """
    Populate the ChromaDB vector database with code and document files from a directory.

    Recursively scans the directory for supported file types, extracts content from
    documents, applies quality filtering, chunks text intelligently, and adds
    everything to the vector database with rich metadata.

    Args:
        directory_path: Path to the directory containing files to process
        dry_run: If True, validate and show what would be processed without writing
        use_direct_api: If True, use direct ChromaDB API instead of LangChain wrapper
    """
    print("🔍 Scanning codebase for files...")
    print(f"📁 Directory: {directory_path}")
    if dry_run:
        print("🔍 DRY RUN MODE - No data will be written to database")
    if use_direct_api:
        print("🔗 Using direct ChromaDB API (recommended for reliability)")
    print("=" * 60)

    # Import required libraries
    from chromadb import HttpClient
    from langchain_chroma import Chroma
    from langchain_ollama import OllamaEmbeddings
    from langchain_core.documents import Document
    from datetime import datetime
    from typing import Any

    # Configuration
    ollama_url = os.getenv("OLLAMA_BASE_URL")
    if not ollama_url:
        raise ValueError("OLLAMA_BASE_URL environment variable is required")

    embedding_model = os.getenv("EMBEDDING_MODEL")
    if not embedding_model:
        raise ValueError("EMBEDDING_MODEL environment variable is required")

    # Custom embeddings class to avoid invalid sampling parameters for embeddings
    class CustomOllamaEmbeddings(OllamaEmbeddings):
        @property
        def _default_params(self) -> dict[str, Any]:  # noqa: unused property override
            """Get the default parameters for calling Ollama, excluding sampling params for embeddings."""
            return {
                "num_ctx": self.num_ctx,
                "num_gpu": self.num_gpu,
                "num_thread": self.num_thread,
                "keep_alive": self.keep_alive,
            }

    try:
        # Initialize embeddings - using custom class to avoid sampling parameter warnings
        embeddings = CustomOllamaEmbeddings(model=embedding_model, base_url=ollama_url)
        print("✅ Connected to Ollama embeddings")

        # Configuration for ChromaDB
        chroma_host = os.getenv("CHROMA_HOST")
        if not chroma_host:
            raise ValueError("CHROMA_HOST environment variable is required")

        chroma_port_str = os.getenv("CHROMA_PORT")
        if not chroma_port_str:
            raise ValueError("CHROMA_PORT environment variable is required")
        chroma_port = int(chroma_port_str)
        collection_name = "codebase"  # Use a specific collection for codebase data

        # Initialize ChromaDB client
        chroma_client = HttpClient(host=chroma_host, port=chroma_port)

        # Load or create vector store/collection
        collection = None
        vectorstore = None

        try:
            if use_direct_api:
                # Use direct ChromaDB API for better reliability
                collection = chroma_client.get_or_create_collection(
                    name=collection_name,
                    metadata={"description": "Codebase knowledge base"},
                )
                initial_count = collection.count()
                print(
                    f"✅ Connected to ChromaDB collection (direct API) with {initial_count} documents"
                )
            else:
                # Use LangChain wrapper
                collection = chroma_client.get_or_create_collection(
                    name=collection_name,
                    metadata={"description": "Codebase knowledge base"},
                )
                vectorstore = Chroma(
                    client=chroma_client,
                    collection_name=collection_name,
                    embedding_function=embeddings,
                )
                initial_count = collection.count()
                print(
                    f"✅ Connected to ChromaDB collection with {initial_count} documents"
                )
        except Exception as e:
            print(f"❌ Failed to access ChromaDB collection: {e}")
            return

        # Scan directory for files
        directory = Path(directory_path)
        if not directory.exists():
            print(f"❌ Directory not found: {directory_path}")
            return

        files_to_process = []
        doc_files = []
        code_files = []

        for file_path in directory.rglob("*"):
            if file_path.is_file() and should_include_file(str(file_path)):
                file_str = str(file_path)
                # Prioritize documentation files
                if any(
                    ext in file_str.lower()
                    for ext in [".md", ".rst", ".txt", ".adoc", ".tex"]
                ):
                    doc_files.append(file_path)
                else:
                    code_files.append(file_path)

        # Process documentation first, then code
        files_to_process = doc_files + code_files

        print(f"📋 Found {len(files_to_process)} code files to process")
        print()

        # Process files
        total_chunks = 0
        processed_files = 0
        batch_size = 100  # Limit batch size to avoid payload too large errors
        document_batch = []

        for file_path in files_to_process:
            relative_path = file_path.relative_to(directory)
            content = read_file_content(str(file_path))

            if not content.strip():
                continue

            # Content quality check
            lines = content.split("\n")
            non_empty_lines = [line for line in lines if line.strip()]
            if len(non_empty_lines) < 3:  # Skip files with less than 3 lines of content
                print(f"⚠️  Skipping file with insufficient content: {relative_path}")
                continue

            # Skip files that are mostly comments or whitespace
            total_chars = len(content)
            code_chars = len("".join(non_empty_lines))
            if (
                total_chars > 0 and code_chars / total_chars < 0.1
            ):  # Less than 10% actual content
                print(
                    f"⚠️  Skipping file with mostly whitespace/comments: {relative_path}"
                )
                continue

            # Get file metadata
            language = get_language_from_extension(str(file_path))
            file_size = len(content)
            line_count = len(lines)
            mod_time = os.path.getmtime(file_path)

            # Chunk large files
            chunks = chunk_text(content)

            # Create documents with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                metadata = {
                    "source": "codebase",
                    "file_path": str(relative_path),
                    "language": language,
                    "file_size": file_size,
                    "line_count": line_count,
                    "modified_time": mod_time,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "added_at": str(datetime.now()),
                }

                doc = Document(page_content=chunk, metadata=metadata)
                documents.append(doc)

            # Add documents to batch
            if documents:
                document_batch.extend(documents)
                total_chunks += len(documents)
                processed_files += 1

                print(f"✅ {relative_path} ({language}) - {len(chunks)} chunks")

                # Process batch if it gets too large
                if len(document_batch) >= batch_size:
                    if not dry_run:
                        print(
                            f"💾 Adding batch of {len(document_batch)} chunks to vector database..."
                        )
                        success = add_batch_to_database(
                            document_batch,
                            vectorstore,
                            collection,
                            use_direct_api,
                            embeddings,
                        )
                        if success:
                            total_chunks += len(document_batch)
                        document_batch = []  # Clear batch only on success
                    else:
                        print(
                            f"🔍 Would add batch of {len(document_batch)} chunks (dry run)"
                        )
                        total_chunks += len(document_batch)
                        document_batch = []  # Clear batch in dry run

        # Process remaining documents in final batch
        if document_batch:
            if not dry_run:
                print(f"💾 Adding final batch of {len(document_batch)} chunks...")
                success = add_batch_to_database(
                    document_batch, vectorstore, collection, use_direct_api, embeddings
                )
                if success:
                    total_chunks += len(document_batch)
            else:
                print(
                    f"🔍 Would add final batch of {len(document_batch)} chunks (dry run)"
                )
                total_chunks += len(document_batch)

        # ChromaDB automatically persists changes - no manual save needed

        # Final statistics
        try:
            collection = chroma_client.get_collection(name=collection_name)
            final_count = collection.count()
        except Exception:
            final_count = total_chunks  # Fallback to processed count
        added_documents = final_count - initial_count

        print()
        print("=" * 60)
        print("🎉 Codebase population completed!")
        print("📊 Statistics:")
        print(f"   • Files processed: {processed_files}")
        print(f"   • Total chunks added: {total_chunks}")
        print(f"   • Documents in vector DB: {final_count}")
        print(f"   • New documents added: {added_documents}")
        print()
        print("💡 The AI can now reference your codebase in conversations!")
        print("   Try asking: 'show me the code for [function/class]'")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function with enhanced argument parsing."""
    parser = argparse.ArgumentParser(
        description="Populate ChromaDB with code and document files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/populate_codebase.py /path/to/codebase
  python tools/populate_codebase.py . --dry-run
  python tools/populate_codebase.py /src --direct-api
  python tools/populate_codebase.py ~/projects/myapp --dry-run --direct-api

Options:
  --dry-run     : Validate and show what would be processed (no DB writes)
  --direct-api  : Use direct ChromaDB API (recommended for reliability)
        """,
    )
    parser.add_argument("directory", help="Directory to scan for files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate files and show what would be processed without writing to DB",
    )
    parser.add_argument(
        "--direct-api",
        action="store_true",
        help="Use direct ChromaDB API instead of LangChain wrapper (more reliable)",
    )

    args = parser.parse_args()

    # Version compatibility check
    try:
        import chromadb

        print(f"✅ Using ChromaDB {chromadb.__version__}")
    except ImportError as e:
        print(f"❌ Missing required packages: {e}")
        print("Install with: pip install chromadb langchain-chroma")
        sys.exit(1)

    populate_codebase(args.directory, args.dry_run, args.direct_api)


if __name__ == "__main__":
    main()
