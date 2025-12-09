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
Test tool calling with a fresh conversation (no history)
"""

import sys
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import SecretStr

sys.path.append(".")

# Initialize LLM with tools bound
llm = ChatOpenAI(
    base_url="http://192.168.0.203:1234/v1",
    api_key=SecretStr("lm-studio"),
    model="qwen3-vl-30b",
    temperature=0.0,
)

# Define tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file in the current directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read (relative to current directory)",
                    }
                },
                "required": ["file_path"],
            },
        },
    }
]

# Bind tools
llm_with_tools = llm.bind_tools(tools)

# Create fresh conversation with tool instructions
system_content = """Lets get some coding done..

IMPORTANT: You have access to tools for file system operations. When users ask you to read files,
list directories, or perform any file operations, you MUST use the appropriate tools instead of
responding conversationally.

Available tools:
- read_file(file_path): Use this when users ask to read, view, or show file contents
- write_file(file_path, content): Use this when users ask to create or modify files
- list_directory(directory_path): Use this when users ask to list files or see directory contents
- get_current_directory(): Use this when users ask for current directory or pwd
- learn_information(info): Use this when users want to teach you information
- search_knowledge(query): Use this when users ask what you know or search learned info

CRITICAL: If a user says "read the README" or "show me the file", you MUST call the read_file tool.
Do not respond with text about not having access to files."""

messages = [
    SystemMessage(content=system_content),
    HumanMessage(content="read the README file"),
]

print("Testing with fresh conversation...")
response = llm_with_tools.invoke(messages)
print(f"Response: {response}")
print(f"Tool calls: {getattr(response, 'tool_calls', 'No tool_calls attribute')}")
print(f"Content: {response.content}")

if hasattr(response, "tool_calls") and response.tool_calls:
    print("SUCCESS: Tool was called in fresh conversation!")
else:
    print("FAILED: No tool calls even in fresh conversation")
