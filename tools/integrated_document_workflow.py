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
Integrated Document Processing Workflow

This example shows how document processing tools work together with
the embedding and ChromaDB knowledge management system.
"""

import sys
from src.main import (
    execute_parse_document,
    execute_learn_information,
    execute_search_knowledge,
)

sys.path.append(".")


def demonstrate_integrated_workflow():
    """
    Demonstrate how document processing integrates with knowledge management.
    """

    print("🔄 Integrated Document Processing Workflow")
    print("=" * 50)

    # Step 1: Parse a document
    print("\n📄 Step 1: Parse Document")
    print("-" * 30)

    # Simulate parsing README.md for text extraction
    parse_result = execute_parse_document("README.md", "text")
    print(f"Parse result: {parse_result}")

    if parse_result.get("success"):
        extracted_content = parse_result.get("analysis", "Sample extracted content")

        # Step 2: Learn the extracted information
        print("\n🧠 Step 2: Store in Knowledge Base")
        print("-" * 30)

        learn_result = execute_learn_information(
            f"Document analysis of README.md: {extracted_content}",
            {
                "source": "README.md",
                "type": "document_analysis",
                "extract_type": "text",
            },
        )
        print(f"Learning result: {learn_result}")

        # Step 3: Search for related information
        print("\n🔍 Step 3: Query Knowledge Base")
        print("-" * 30)

        search_result = execute_search_knowledge("README document analysis")
        print(f"Search result: {search_result}")

        # Step 4: AI can now use this knowledge in responses
        print("\n🤖 Step 4: AI Response Integration")
        print("-" * 30)
        print("AI can now answer questions like:")
        print("- 'What does the README say about the project?'")
        print("- 'Show me the document structure'")
        print("- 'What features are documented?'")

    print("\n✅ Workflow Complete")
    print("Document processing → Knowledge storage → Semantic retrieval → AI responses")


if __name__ == "__main__":
    demonstrate_integrated_workflow()
