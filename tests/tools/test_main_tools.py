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
Test tool calling in main.py context
"""

# os import removed as it's not used
import sys
from src.main import execute_tool_call

sys.path.append(".")

# Test tool call dict (LangChain format)
tool_call = {
    "name": "read_file",
    "args": {"file_path": "README.md"},
    "id": "12345",
    "type": "tool_call",
}

print("Testing execute_tool_call with read_file...")
result = execute_tool_call(tool_call)
print(f"Result: {result}")

# Test with current directory
tool_call2 = {
    "name": "get_current_directory",
    "args": {},
    "id": "67890",
    "type": "tool_call",
}

print("\nTesting execute_tool_call with get_current_directory...")
result2 = execute_tool_call(tool_call2)
print(f"Result: {result2}")
