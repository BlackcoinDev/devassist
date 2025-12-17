#!/usr/bin/env python3
"""
Document Processing Tools - Executors for document parsing and analysis.

This module provides AI tool executors for parsing various document types
using Docling's unified pipeline for high-fidelity extraction.
"""

import os
import logging
from typing import Dict, Any

from src.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

# =============================================================================
# TOOL DEFINITIONS (OpenAI Function Calling Format)
# =============================================================================

PARSE_DOCUMENT_DEFINITION = {
    "type": "function",
    "function": {
        "name": "parse_document",
        "description": "Parse and extract structured content from documents (PDF, DOCX, images, etc.) using Docling",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the document file to parse (relative to current directory)",
                },
                "extract_type": {
                    "type": "string",
                    "enum": ["text", "tables", "forms", "layout"],
                    "description": "Compatibility parameter (Docling extracts all content as structured Markdown)",
                },
            },
            "required": ["file_path"],
        },
    },
}


# =============================================================================
# TOOL EXECUTORS
# =============================================================================


@ToolRegistry.register("parse_document", PARSE_DOCUMENT_DEFINITION)
def execute_parse_document(file_path: str, extract_type: str = "text") -> Dict[str, Any]:
    """
    Execute document parsing tool using Docling's unified pipeline.

    This function leverages Docling for high-fidelity extraction of structured
    content from various document types including PDFs, Office documents, images,
    and text files.

    SUPPORTED DOCUMENT TYPES:
    - PDFs: Native text extraction with layout preservation
    - Images: PNG, JPG, JPEG, BMP, TIFF (with OCR)
    - Office: DOCX, XLSX, PPTX
    - Text: TXT, MD, RST, JSON, XML, CSV
    - And 80+ other file types

    EXTRACTION TYPES (compatibility parameter):
    - "text": Extract readable text with layout preservation
    - "tables": Identify and extract tabular data
    - "forms": Recognize form fields
    - "layout": Analyze document structure

    Note: Docling extracts all content types in a single pass, so extract_type
    is primarily for API compatibility.

    Args:
        file_path: Path to document file relative to current directory
        extract_type: Type of extraction (default: "text")

    Returns:
        Dict with success status and extracted content
    """
    try:
        # Security check - ensure file is within current directory
        current_dir = os.getcwd()
        full_path = os.path.abspath(file_path)

        if not full_path.startswith(current_dir):
            return {"error": "Access denied: File outside current directory"}

        if not os.path.exists(full_path):
            return {"error": f"File not found: {file_path}"}

        # Process document using Docling unified pipeline
        try:
            from docling.document_converter import DocumentConverter

            # Initialize converter
            converter = DocumentConverter()

            # Convert document
            result = converter.convert(full_path)

            # Export to markdown (excellent for LLM consumption)
            content = result.document.export_to_markdown()

            file_ext = os.path.splitext(full_path)[1].lower()

            return {
                "success": True,
                "file_path": file_path,
                "extract_type": extract_type,  # Kept for API compatibility
                "file_type": file_ext,
                "content": content,
                "analysis": content,  # Content is the analysis in this case
                "note": "Processed via Docling Unified Pipeline",
            }

        except ImportError:
            return {
                "success": False,
                "error": "docling library not installed. Please install with: pip install docling",
            }
        except Exception as e:
            logger.error(f"Docling processing failed for {file_path}: {e}")
            return {"success": False, "error": f"Docling processing failed: {str(e)}"}

    except Exception as e:
        logger.error(f"Document parsing failed for {file_path}: {e}")
        return {"error": f"Document parsing failed: {str(e)}"}


__all__ = ["execute_parse_document"]
