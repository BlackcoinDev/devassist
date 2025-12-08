#!/usr/bin/env python3
# MIT License
# Copyright (c) 2025 BlackcoinDev

"""
Example: Unified Document Processing with Docling

This script demonstrates how to use the Docling library to process various document formats
(PDF, DOCX, XLSX, HTML, Images, etc.) using a single unified pipeline.

Docling provides high-quality text extraction that preserves layout structure and exports
to clean Markdown, making it ideal for LLM ingestion (RAG).

Usage:
    python tools/docling_example.py <path_to_document>
"""

import sys
import logging
from typing import Optional

# Check if docling is installed
try:
    from docling.document_converter import DocumentConverter
except ImportError:
    print("❌ Docling is not installed.")
    print("Please install it with: pip install docling")
    sys.exit(1)

# Configure logging to see Docling's progress
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_document(file_path: str) -> Optional[str]:
    """
    Process a document and return its Markdown representation.
    """
    try:
        logger.info(f"🚀 Initializing DocumentConverter for: {file_path}")

        # Initialize the converter
        # You can pass allowed_formats if you want to restrict types
        converter = DocumentConverter()

        # Convert the document
        # This handles file type detection, parsing, OCR (if needed), and
        # structure analysis
        logger.info("⏳ Converting...")
        result = converter.convert(file_path)

        # Docling's `result.document` holds the rich structured model.
        # We export to Markdown for easy readability and LLM usage.
        markdown_content = result.document.export_to_markdown()

        logger.info("✅ Conversion successful!")
        return markdown_content

    except Exception as e:
        logger.error(f"❌ Error processing document: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/docling_example.py <file_path_or_url>")
        print("\nExamples:")
        print("  python tools/docling_example.py README.md")
        print("  python tools/docling_example.py https://example.com")
        sys.exit(1)

    input_source = sys.argv[1]

    # Process
    content = process_document(input_source)

    if content:
        print("\n" + "=" * 40)
        print("📄 Document Content (Markdown Preview)")
        print("=" * 40 + "\n")

        # Print first 2000 chars to avoid flooding terminal
        print(content[:2000])

        if len(content) > 2000:
            print(f"\n... (and {len(content) - 2000} more characters)")

        print("\n" + "=" * 40)


if __name__ == "__main__":
    main()
