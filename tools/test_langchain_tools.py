#!/usr/bin/env python3
"""
Test LangChain tool binding with devstral-small-2507-mlx
"""

# os import removed as it's not used
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import SecretStr

# Initialize LLM
llm = ChatOpenAI(
    base_url="http://192.168.0.203:1234/v1",
    api_key=SecretStr("lm-studio"),
    model="devstral-small-2507-mlx",
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
print("LLM with tools bound")

# Test tool calling
response = llm_with_tools.invoke([HumanMessage(content="read the README file")])
print(f"Response: {response}")
print(f"Tool calls: {getattr(response, 'tool_calls', 'No tool_calls attribute')}")
print(f"Content: {response.content}")
