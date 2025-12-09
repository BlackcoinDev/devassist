# AI Tool Calling Implementation Guide

## Overview

This guide explains the complete AI tool calling ecosystem in your AI assistant, featuring **8 powerful tools** that work together with **ChromaDB vector storage**, **Ollama embeddings**, and **qwen3-vl-30b's multimodal capabilities** to create an intelligent document processing and knowledge management system.

## How Tool Calling Works

### The Tool Calling Process

1. **Tool Definitions**: AI models receive structured descriptions of available tools
2. **Intent Recognition**: AI analyzes user requests and decides which tools to use
3. **Structured Calls**: AI responds with precise function calls (not natural language)
4. **Secure Execution**: Your application executes tools with proper validation
5. **Result Integration**: Tool results are fed back to AI for intelligent responses

### Complete Tool Integration Workflow

```
User: "Analyze this quarterly report and remember the key metrics"

AI Analysis: "User wants document analysis + knowledge storage"
AI Decision: "Chain parse_document → learn_information → search_knowledge"

🔧 Executing tool: parse_document
   Parameters: {"file_path": "Q3_report.pdf", "extract_type": "tables"}
   Result: {"success": true, "tables": [...], "table_count": 3}

🔧 Executing tool: learn_information
   Parameters: {"information": "Q3 metrics: Revenue +15%, Users +25%", "metadata": {"source": "Q3_report.pdf"}}
   Result: {"success": true, "learned": true}

🔧 Executing tool: search_knowledge
   Parameters: {"query": "Q3 performance metrics"}
   Result: {"results": [...], "result_count": 2}

AI Response: "I've analyzed your Q3 report and stored the key metrics. Revenue grew 15% and user base increased 25%."
```

#### Tool Result Flow & AI Usage

**1. Tool Execution & Result Storage:**
```python
# AI calls tool
🔧 Executing tool: read_file

# Tool executes and returns structured result
result = {"success": True, "content": "full file content...", "size": 125590}

# Result temporarily stored in tool_results list
tool_results.append(result)
```

**2. Result Integration into Conversation:**
```python
# Results formatted for AI comprehension
tool_message = "Tool execution results:\n"
tool_message += f"- read_file: {result}\n"

# Added to conversation history as HumanMessage
enhanced_history.append(HumanMessage(content=tool_message))
```

**3. AI Processing of Results:**
```python
# Tool results become part of LLM context window
final_response = llm.invoke(enhanced_history)  # Includes tool results

# AI analyzes structured data and generates informed response
# "Based on the file content, the document contains..."
```

**4. Result Lifecycle:**
- **During Execution**: Stored in Python variables (`tool_results`, `enhanced_history`)
- **During Response**: Integrated into LLM's thinking context
- **After Response**: Persisted in conversation history (SQLite database)
- **No File Storage**: Results exist only in memory/conversation during session

### Tool Ecosystem Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  qwen3-vl-30b   │───▶│   Tool Router   │
│                 │    │  (Multimodal)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ File Operations │    │ Document        │    │ Knowledge       │
│ (read/write/ls) │    │ Processing      │    │ Management      │
│                 │    │ (OCR/Tables)    │    │ (Learn/Search)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ChromaDB      │    │   Ollama        │    │   SQLite        │
│  (Vectors)      │    │ (Embeddings)    │    │ (Memory)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Implicit Capabilities (Non-Tool Features)
Some features work automatically in the background without the AI needing to call a tool:
*   **Personalized Memory (Mem0)**: Automatically captures user preferences. The AI doesn't call `save_preference`; the system does it on every message.
*   **Web Ingestion (`/web`)**: Triggered by user slash commands, not AI tool logic.


## Compatible AI Models

- **qwen3-vl-30b via LM Studio** ⭐⭐⭐ (Current model with tool calling support)

## Available Tools

### File System Tools

#### `read_file(file_path: string)` ⭐ **TESTED & WORKING**
Reads file contents with security restrictions.
- **Status**: ✅ **Fully tested with qwen3-vl-30b**
- **Security**: Only current directory, max 1MB file size
- **Returns**: File content, size, success status
- **Usage**: AI successfully reads and displays file contents

#### `write_file(file_path: string, content: string)` ⭐ **READY**
Writes content to files with automatic directory creation.
- **Status**: ✅ **Supported by qwen3-vl-30b**
- **Security**: Only current directory, path validation
- **Returns**: Success status, file size
- **Features**: Auto-creates directories as needed

#### `list_directory(directory_path?: string)` ⭐ **READY**
Lists directory contents.
- **Status**: ✅ **Supported by qwen3-vl-30b**
- **Default**: Current directory (".")
- **Security**: Only current directory tree
- **Returns**: File/directory list, total count
- **Output**: Sorted with file type indicators

#### `get_current_directory()` ⭐ **TESTED & WORKING**
Returns current working directory path.
- **Status**: ✅ **Successfully tested with qwen3-vl-30b**
- **Returns**: Absolute path string
- **Usage**: Confirmed working in tool call tests

### Document Processing Tools

#### `parse_document(file_path: string, extract_type: string)` ⭐ **READY**
Extracts structured data from documents using Docling's unified parsing pipeline.
- **Status**: ✅ **Supported by Docling**
- **Extract Types**: "text", "tables", "forms", "layout" (Note: Docling extracts full content including these features)
- **Supported Files**: PDFs, Office docs (DOCX/XLSX), RTF, EPUB, Images, HTML
- **Returns**: Markdown content with layout preservation
- **Integration**: Uses Docling for high-fidelity conversion

### Knowledge Management Tools

#### `learn_information(information: string, metadata?: object)` ⭐ **READY**
Adds information to AI's knowledge base.
- **Status**: ✅ **Supported by qwen3-vl-30b**
- **Parameters**: Information text, optional metadata
- **Returns**: Success status, information length
- **Integration**: Works with existing learning system and ChromaDB

#### `search_knowledge(query: string, limit?: number)` ⭐ **READY**
Searches learned knowledge for relevant information.
- **Status**: ✅ **Supported by qwen3-vl-30b**
- **Default limit**: 5 results maximum
- **Returns**: Search results, match count
- **Integration**: Uses semantic search with Ollama embeddings

#### `search_web(query: string)` ⭐ **READY**
Searches the public internet using DuckDuckGo.
- **Status**: ✅ **Supported by qwen3-vl-30b**
- **Capabilities**: Real-time web results, privacy-focused
- **Returns**: Top 5 search result snippets
- **Integration**: Uses `duckduckgo-search` library without API keys

## Implementation Steps

### Step 1: Choose Your AI Model

**For qwen3-vl-30b:**
```bash
# .env (your current configuration)
LM_STUDIO_URL=http://192.168.0.203:1234/v1
LM_STUDIO_KEY=lm-studio
MODEL_NAME=qwen3-vl-30b
```

### Step 2: Enable Tool Calling in Code

Modify the conversation loop in `main.py`:

```python
# Replace this (current streaming approach):
for chunk in llm.stream(enhanced_history):
    response += chunk.content

# With this (tool-enabled approach):
try:
    # Initial call with tools
    initial_response = llm.invoke(enhanced_history, tools=FILE_SYSTEM_TOOLS)

    if hasattr(initial_response, 'tool_calls') and initial_response.tool_calls:
        # Execute tool calls
        tool_results = []
        for tool_call in initial_response.tool_calls:
            print(f"🔧 Executing tool: {tool_call.function.name}")
            result = execute_tool_call(tool_call)
            tool_results.append(result)

        # Continue conversation with tool results
        tool_messages = [f"Tool {r['function_name']}: {r['result']}"]
        enhanced_history.extend([
            AIMessage(content=initial_response.content or "Using tools..."),
            HumanMessage(content="\n".join(tool_messages))
        ])

        # Get final response
        final_response = llm.invoke(enhanced_history)
        response = final_response.content or ""

    else:
        # No tools needed
        response = initial_response.content or ""

except Exception as e:
    # Fallback to regular streaming
    logger.warning(f"Tool calling failed: {e}")
    response = ""
    for chunk in llm.stream(enhanced_history):
        response += chunk.content
```

### Step 3: Test Tool Calling

1. **Run the demonstration:**
   ```bash
   python3 tools/tool_demo.py
   ```

2. **Test with your AI model:**
   ```bash
   python3 launcher.py --cli
   # Try: "read the README file"
   # Try: "list the files in the current directory"
   # Try: "create a test.txt file with hello world content"
   ```

## Security & Safety

### Sandboxing Features
- **Directory Restriction**: Tools only access current working directory
- **Path Validation**: Prevents `../../../` attacks
- **File Size Limits**: Maximum 1MB for file reading
- **Binary File Protection**: Rejects binary files with clear errors

### Error Handling
- **Graceful Failures**: Tool errors don't crash the application
- **Clear Error Messages**: Users understand what went wrong
- **Fallback Mode**: Reverts to regular conversation if tools fail
- **Audit Logging**: All tool executions are logged

## Advanced Usage

### Multi-Tool Operations
AI can chain multiple tools together:
```
User: "Analyze my code and create documentation"

AI executes:
1. list_directory() - Find code files
2. read_file() - Read main files
3. write_file() - Create documentation
4. learn_information() - Remember project structure
```

### Context-Aware Tool Usage
AI learns when to use tools:
- **File operations**: When user mentions specific files
- **Directory browsing**: When user asks about project structure
- **Knowledge search**: When user asks about learned information
- **Content creation**: When user requests file creation

### Custom Tool Development
To add new tools:

1. **Define tool schema** in `FILE_SYSTEM_TOOLS`
2. **Implement execution function** (e.g., `execute_custom_tool()`)
3. **Add to `execute_tool_call()`** routing
4. **Test thoroughly** with security considerations

## Troubleshooting

### Common Issues

**"Tool calling not working"**
- Verify your AI model supports tools
- Check API key and endpoint configuration
- Ensure model name is correct

**"Tools executing but failing"**
- Check file permissions in current directory
- Verify ChromaDB is running for knowledge tools
- Check for file size limits

**"Security errors"**
- Tools are restricted to current directory only
- Some operations may require additional permissions

### Debugging
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check the logs for:
- Tool call detection
- Parameter validation
- Execution results
- Error messages

## Performance Considerations

### Tool Call Efficiency
- **Batch Operations**: AI can request multiple tools in one call
- **Caching**: Results can be cached for repeated operations
- **Streaming**: Large file operations use streaming to prevent memory issues

### Rate Limiting
- **API Limits**: Respect your AI provider's rate limits
- **File Operations**: Large directory scans may take time
- **Concurrent Tools**: Multiple tools execute sequentially

## Development Utilities and Scripts

The `tools/` folder contains development utilities, examples, and test scripts for the tool calling system. These are not part of the core application but help with development, testing, and demonstration.

### Core Scripts

#### `populate_codebase.py` ⭐ **PRODUCTION READY**
- **Purpose**: Bulk import codebases and documents into ChromaDB vector database
- **Usage**: `python tools/populate_codebase.py /path/to/codebase [--dry-run] [--direct-api]`
- **Features**: Recursive scanning, multiple file types, batch processing, collection management
- **Status**: Production-ready for codebase ingestion

### Example Scripts

#### `vlm_document_processing_example.py`
- **Purpose**: Demonstrates document parsing using qwen3-vl-30b's multimodal capabilities
- **Usage**: Run as standalone example for document analysis workflows
- **Features**: Image processing, OCR, table extraction, form recognition
- **Status**: Educational example

#### `docling_example.py`
- **Purpose**: Demonstrates unified document processing with Docling
- **Usage**: `python tools/docling_example.py <file>`
- **Features**: High-fidelity conversion of PDF, Docx, HTML to Markdown
- **Status**: Educational example

#### `enable_tools_example.py`
- **Purpose**: Shows how to modify main.py to enable tool calling
- **Usage**: Reference code for integrating tool calling into conversation loops
- **Features**: Code snippets for tool integration
- **Status**: Integration guide

#### `integrated_document_workflow.py`
- **Purpose**: Demonstrates how document tools work with knowledge management
- **Usage**: End-to-end workflow example combining parsing, learning, and search
- **Features**: Complete document processing pipeline
- **Status**: Workflow demonstration

#### `tool_demo.py`
- **Purpose**: Interactive demonstration of tool calling capabilities
- **Usage**: `python tools/tool_demo.py` for hands-on testing
- **Features**: Live tool execution examples
- **Status**: Interactive demo

### Test Scripts

#### `test_tools.py`
- **Purpose**: Comprehensive test suite for all tool functions
- **Usage**: `python tools/test_tools.py` for automated testing
- **Features**: Unit tests for each tool, error handling validation
- **Status**: Test suite

#### `test_direct_tools.py`
- **Purpose**: Tests direct ChromaDB API integration for tools
- **Usage**: Validates vector database operations
- **Features**: Direct API testing, reliability checks
- **Status**: Integration tests

#### `test_langchain_tools.py`
- **Purpose**: Tests LangChain wrapper integration for tools
- **Usage**: Validates LangChain compatibility
- **Features**: Wrapper testing, compatibility checks
- **Status**: LangChain tests

#### `test_parse_document.py`
- **Purpose**: Specific tests for document parsing functionality
- **Usage**: `python tools/test_parse_document.py` for document processing tests
- **Features**: File type validation, extraction accuracy
- **Status**: Document parsing tests

#### `test_main_tools.py`
- **Purpose**: Tests tool integration with main application
- **Usage**: End-to-end testing with main.py
- **Features**: Full application integration tests
- **Status**: Main app tests

#### `test_fresh_conversation.py`
- **Purpose**: Tests tool calling in fresh conversation contexts
- **Usage**: Validates tool behavior without prior context
- **Features**: Clean slate testing, context isolation
- **Status**: Conversation tests

### Usage Notes

- **Production Use**: Only `populate_codebase.py` is intended for production use
- **Development**: Other scripts are for testing and development purposes
- **Dependencies**: All scripts require the same dependencies as main.py
- **Environment**: Ensure `.env` is configured for database connections
- **Testing**: Run test scripts to validate tool functionality before deployment

### Vector Database Management
- **Duplicate Prevention**: Use `/populate path --clear` to avoid duplicate documents
- **Collection Clearing**: `--clear` flag deletes existing collection before repopulating
- **Direct API**: Always used by default for optimal reliability and performance
- **Incremental Updates**: Without `--clear`, documents are added to existing collection
- **Storage Optimization**: Regular clearing prevents bloated databases

### GPU Memory Considerations
- **Current Model**: qwen3-vl-30b requires <8GB VRAM (optimal)
- **Large Models**: qwen3-vl-30b requires ~60GB VRAM + context overhead
- **Tool Overhead**: Each tool call increases memory usage
- **Context Growth**: Long conversations compound memory requirements
- **Optimization**: Use smaller models for better performance and stability

## Future Enhancements

### Planned Features
- **Tool Result Caching**: Speed up repeated operations
- **Custom Tool Builder**: GUI for creating user-defined tools
- **Vector DB Deduplication**: Automatic duplicate prevention in populate operations
- **Tool Chains**: Pre-defined sequences of tool operations
- **Advanced Security**: Per-operation permission controls

### Integration Opportunities
- **Code Analysis Tools**: AST parsing, complexity analysis
- **Version Control**: Git operations, diff analysis
- **Package Management**: Dependency analysis, updates
- **Documentation Generation**: Auto-docs from code analysis

---

**Ready to supercharge your AI assistant with tool calling capabilities!** 🚀

The infrastructure is complete and working with qwen3-vl-30b.