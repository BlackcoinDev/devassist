#!/usr/bin/env python3
"""
Test Tool Calling with devstral-small-2507-mlx
"""

# os import removed as it's not used
from typing import List, Dict, Any
from openai import OpenAI

# Initialize OpenAI client for LM Studio
client = OpenAI(base_url="http://192.168.0.203:1234/v1", api_key="lm-studio")

# Define a simple tool with proper typing
tools: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current system time",
            "parameters": {"type": "object", "properties": {}},
        },
    }
]


def get_current_time():
    """Function to get current time"""
    from datetime import datetime

    return {"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


# Test 1: Ask for time (should trigger tool)
print("Test 1: Asking for current time")
response = client.chat.completions.create(
    model="devstral-small-2507-mlx",
    messages=[{"role": "user", "content": "What time is it right now?"}],
    tools=tools,  # type: ignore
)

print(f"Response: {response.choices[0].message}")
print(f"Tool calls: {response.choices[0].message.tool_calls}")
print(f"Content: {response.choices[0].message.content}")

# Test 2: If tool was called, execute it and get final response
if response.choices[0].message.tool_calls:
    print("\nTool was called! Executing...")

    # Execute the tool
    tool_call = response.choices[0].message.tool_calls[0]
    result = get_current_time()

    # Send result back to model
    messages = [
        {"role": "user", "content": "What time is it right now?"},
        {"role": "assistant", "tool_calls": [tool_call]},
        {"role": "tool", "content": str(result), "tool_call_id": tool_call.id},
    ]

    final_response = client.chat.completions.create(
        model="devstral-small-2507-mlx",
        messages=messages,  # type: ignore
    )

    print(f"Final response: {final_response.choices[0].message.content}")
else:
    print("\nNo tool calls - model responded directly")

# Test 3: Ask to read README file
print("\nTest 3: Asking to read README file")
read_tools = [
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

response3 = client.chat.completions.create(
    model="devstral-small-2507-mlx",
    messages=[{"role": "user", "content": "read the README file"}],
    tools=read_tools,  # type: ignore
)

print(f"Response: {response3.choices[0].message}")
print(f"Tool calls: {response3.choices[0].message.tool_calls}")
print(f"Content: {response3.choices[0].message.content}")

if response3.choices[0].message.tool_calls:
    print("\nRead file tool was called!")
else:
    print("\nNo tool calls for read file - model responded directly")
