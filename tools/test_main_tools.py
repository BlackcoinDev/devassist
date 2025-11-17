#!/usr/bin/env python3
"""
Test tool calling in main.py context
"""

# os import removed as it's not used
import sys
from main import execute_tool_call

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
