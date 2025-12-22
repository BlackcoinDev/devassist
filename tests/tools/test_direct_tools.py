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
Test tool calling with direct OpenAI API using the same system message as main.py
"""

# os import removed as it's not used
from openai import OpenAI
from openai.types.chat import ChatCompletionToolParam, ChatCompletionMessageParam

# Initialize OpenAI client for LM Studio
client = OpenAI(base_url="http://192.168.0.203:1234/v1", api_key="lm-studio")

# Define tools (same as main.py)
tools: list[ChatCompletionToolParam] = [
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

# System message (same as main.py)
system_message = """Lets get some coding done..

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

# Test with the same user message
messages: list[ChatCompletionMessageParam] = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": "read the README file"},
]

print("Testing with direct OpenAI API...")
response = client.chat.completions.create(
    model="qwen3-vl-30b",
    messages=messages,
    tools=tools,
)

print(f"Response: {response.choices[0].message}")
print(f"Tool calls: {response.choices[0].message.tool_calls}")
print(f"Content: {response.choices[0].message.content}")

if response.choices[0].message.tool_calls:
    print("SUCCESS: Tool was called!")
else:
    print("FAILED: No tool calls")
