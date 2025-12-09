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
Test the parse_document tool implementation
"""

import sys
from src.main import execute_parse_document

sys.path.append(".")


def test_parse_document():
    """Test the parse_document tool with different scenarios"""

    print("Testing parse_document tool...")

    # Test 1: Non-existent file
    print("\n1. Testing non-existent file:")
    result = execute_parse_document("nonexistent.pdf", "text")
    print(f"Result: {result}")

    # Test 2: Unsupported file type
    print("\n2. Testing unsupported file type:")
    result = execute_parse_document("src.main.py", "text")
    print(f"Result: {result}")

    # Test 3: Valid parameters (will show placeholder)
    print("\n3. Testing valid parameters (placeholder):")
    result = execute_parse_document("README.md", "text")
    print(f"Result: {result}")

    # Test 4: Different extract types
    print("\n4. Testing different extract types:")
    for extract_type in ["text", "tables", "forms", "layout"]:
        result = execute_parse_document("README.md", extract_type)
        print(f"  {extract_type}: {result.get('extract_type', 'error')}")


if __name__ == "__main__":
    test_parse_document()
