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
Complete Document Processing Implementation for qwen3-vl-30b

This example shows how to fully implement document parsing using qwen3-vl-30b's
multimodal capabilities for real document analysis.
"""

import base64
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import SecretStr


class QwenDocumentProcessor:
    """
    Document processor using qwen3-vl-30b's multimodal capabilities.

    This class demonstrates how to use qwen3-vl-30b for:
    - OCR (text extraction from images/documents)
    - Table extraction
    - Form field recognition
    - Layout analysis
    """

    def __init__(self):
        """Initialize the qwen3-vl-30b model for document processing."""
        self.llm = ChatOpenAI(
            base_url="http://192.168.0.203:1234/v1",
            api_key=SecretStr("lm-studio"),
            model="qwen3-vl-30b",
            temperature=0.1,  # Low temperature for consistent extraction
        )

    def encode_image_to_base64(self, image_path: str) -> str:
        """Convert image file to base64 string for qwen3-vl-30b."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def extract_text(self, document_path: str) -> Dict[str, Any]:
        """
        Extract all readable text from a document using qwen3-vl-30b.

        Args:
            document_path: Path to document file

        Returns:
            Dict containing extracted text and metadata
        """
        try:
            # For image-based documents, encode as base64
            if document_path.lower().endswith(
                (".png", ".jpg", ".jpeg", ".bmp", ".tiff")
            ):
                image_b64 = self.encode_image_to_base64(document_path)
                content = [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                    },
                    {
                        "type": "text",
                        "text": "Extract all readable text from this image. Return only the text content, "
                        "preserving the original formatting and structure as much as possible. "
                        "Do not add any commentary or explanations.",
                    },
                ]
            else:
                # For other document types, you would need to convert to image first
                # This is a placeholder for document-to-image conversion
                return {
                    "success": False,
                    "error": f"Document type not directly supported: {document_path}. Convert to image format first.",
                }

            messages = [HumanMessage(content=content)]  # type: ignore[arg-type]
            response = self.llm.invoke(messages)

            response_content = response.content
            if isinstance(response_content, str):
                content = response_content.strip()
            else:
                content = str(response_content)

            return {
                "success": True,
                "extract_type": "text",
                "content": content,
                "document_path": document_path,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def extract_tables(self, document_path: str) -> Dict[str, Any]:
        """
        Extract tables from a document using qwen3-vl-30b.

        Args:
            document_path: Path to document file

        Returns:
            Dict containing extracted tables
        """
        try:
            if document_path.lower().endswith(
                (".png", ".jpg", ".jpeg", ".bmp", ".tiff")
            ):
                image_b64 = self.encode_image_to_base64(document_path)
                content = [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                    },
                    {
                        "type": "text",
                        "text": """Extract all tables from this image. For each table found:

1. Identify the table structure (headers, rows, columns)
2. Extract the data in a structured JSON format
3. Preserve the original table layout and relationships

Return the results as a JSON array of table objects. If no tables are found, return an empty array.

Example format:
[
  {
    "table_id": 1,
    "headers": ["Column1", "Column2", "Column3"],
    "rows": [
      ["Data1", "Data2", "Data3"],
      ["Data4", "Data5", "Data6"]
    ]
  }
]""",
                    },
                ]

                messages = [HumanMessage(content=content)]  # type: ignore[arg-type]
                response = self.llm.invoke(messages)

                # Parse the JSON response (in a real implementation, you'd validate this)
                response_content = response.content
                if isinstance(response_content, str):
                    content_str = response_content.strip()
                else:
                    content_str = str(response_content)

                try:
                    import json

                    tables = json.loads(content_str)
                except (ImportError, ValueError):
                    tables = [{"raw_text": content_str}]

                return {
                    "success": True,
                    "extract_type": "tables",
                    "tables": tables,
                    "table_count": len(tables) if isinstance(tables, list) else 1,
                    "document_path": document_path,
                }
            else:
                return {
                    "success": False,
                    "error": f"Table extraction requires image format: {document_path}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_layout(self, document_path: str) -> Dict[str, Any]:
        """
        Analyze document layout and structure using qwen3-vl-30b.

        Args:
            document_path: Path to document file

        Returns:
            Dict containing layout analysis
        """
        try:
            if document_path.lower().endswith(
                (".png", ".jpg", ".jpeg", ".bmp", ".tiff")
            ):
                image_b64 = self.encode_image_to_base64(document_path)
                content = [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                    },
                    {
                        "type": "text",
                        "text": """Analyze the layout and structure of this document. Describe:

1. Main content areas and their positioning
2. Headers, footers, and navigation elements
3. Text blocks and their hierarchical structure
4. Images, charts, or graphical elements and their placement
5. Overall document organization and flow

Provide a detailed structural analysis that could be used for document processing or conversion.""",
                    },
                ]

                messages = [HumanMessage(content=content)]  # type: ignore[arg-type]
                response = self.llm.invoke(messages)

                response_content = response.content
                if isinstance(response_content, str):
                    analysis = response_content.strip()
                else:
                    analysis = str(response_content)

                return {
                    "success": True,
                    "extract_type": "layout",
                    "analysis": analysis,
                    "document_path": document_path,
                }
            else:
                return {
                    "success": False,
                    "error": f"Layout analysis requires image format: {document_path}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def process_document(
        self, file_path: str, extract_type: str
    ) -> Dict[str, Any]:
        """
        Main document processing method that routes to appropriate extraction method.

        Args:
            file_path: Path to the document
            extract_type: Type of extraction ("text", "tables", "forms", "layout")

        Returns:
            Dict with extraction results
        """
        if extract_type == "text":
            return self.extract_text(file_path)
        elif extract_type == "tables":
            return self.extract_tables(file_path)
        elif extract_type == "forms":
            # Forms extraction would be similar to tables but focused on form fields
            return self.extract_text(file_path)  # Placeholder
        elif extract_type == "layout":
            return self.analyze_layout(file_path)
        else:
            return {
                "success": False,
                "error": f"Unsupported extract_type: {extract_type}",
            }


# Example usage
if __name__ == "__main__":
    processor = QwenDocumentProcessor()

    # Example: Process a document image
    # result = processor.process_document("document_page1.png", "text")
    # print(f"Extracted text: {result}")

    print("QwenDocumentProcessor initialized. Ready for document analysis!")
    print("\nSupported extract types:")
    print("- text: Extract readable text")
    print("- tables: Extract table data as structured JSON")
    print("- forms: Extract form fields (placeholder)")
    print("- layout: Analyze document structure and positioning")
