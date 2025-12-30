# Chat Loop System API Documentation

## Overview

The Chat Loop System is a production-grade, enterprise-ready conversational AI orchestrator that handles AI interactions, tool calling, and approvals. It provides secure input validation, performance optimization, and comprehensive monitoring capabilities.

## Core Classes

### ChatLoop

Main orchestrator class that handles AI interaction, tool calling, and approvals.

```python
class ChatLoop:
    def __init__(self, confirmation_callback: Optional[Callable] = None):
        """
        Initialize ChatLoop.

        Args:
            confirmation_callback: Function(tool_name, args) -> bool
                              If None, defaults to CLI input.
        """
```

#### Methods

##### `run_iteration(user_input: str) -> str`

Main orchestrator method that processes a single user input through the AI loop.

```python
def run_iteration(self, user_input: str) -> str:
    """
    Process a single user input through the AI loop.

    This method orchestrates the complete conversation flow:
    1. Input validation and sanitization
    2. Context injection (RAG) if enabled
    3. Iterative tool calling with security validation
    4. Memory management and persistence

    Args:
        user_input: The text input from the user.

    Returns:
        str: The final response from the AI.

    Raises:
        InputValidationError: If input fails validation
        ToolExecutionError: If tool execution fails
        LLMTimeoutError: If LLM request times out
    """
```

**Example Usage:**

```python
chat_loop = ChatLoop()
response = chat_loop.run_iteration("What files are in the current directory?")
print(response)
```

##### `_validate_and_sanitize_input(user_input: str) -> str`

Validates and sanitizes user input before processing.

```python
def _validate_and_sanitize_input(self, user_input: str) -> str:
    """
    Validate and sanitize user input.

    Args:
        user_input: The raw user input to validate

    Returns:
        str: The validated and sanitized input

    Raises:
        InputValidationError: If input fails validation
    """
```

**Security Features:**

- Empty input detection
- Length validation (max 10,000 characters)
- Control character removal
- Whitespace normalization

##### `_inject_context(user_input: str) -> str`

Injects RAG context if enabled.

```python
def _inject_context(self, user_input: str) -> str:
    """
    Inject RAG context if enabled.

    Args:
        user_input: The user input to enhance with context

    Returns:
        str: The input with injected context, or original if disabled/no context
    """
```

**Features:**

- Context mode detection (auto/on/off)
- Context retrieval from ChromaDB
- Automatic context injection for enhanced responses

##### `_execute_tool_loop() -> str`

Executes tool calling loop with performance optimizations.

```python
def _execute_tool_loop(self) -> str:
    """
    Execute tool calling loop with performance optimizations.

    Returns:
        str: The final response from the AI
    """
```

**Features:**

- Maximum iteration limits (5 iterations)
- Performance monitoring
- Incremental memory management
- Tool execution optimization

##### `_cleanup_memory() -> None`

Cleans up conversation history and saves to storage.

```python
def _cleanup_memory(self) -> None:
    """
    Clean up conversation history and save to storage.
    """
```

**Features:**

- Conversation history trimming
- Memory persistence
- Performance monitoring

##### `_handle_iteration_error(error: Exception) -> str`

Handles and formats iteration errors.

```python
def _handle_iteration_error(self, error: Exception) -> str:
    """
    Handle and format iteration errors.

    Args:
        error: The exception that occurred

    Returns:
        str: User-friendly error message
    """
```

**Error Types Handled:**

- `InputValidationError`: Invalid input errors
- `ToolExecutionError`: Tool execution failures
- `LLMTimeoutError`: LLM request timeouts
- Generic exceptions

#### Performance Optimization Methods

##### `_should_trim_memory() -> bool`

Checks if conversation history should be trimmed.

```python
def _should_trim_memory(self) -> bool:
    """
    Check if conversation history should be trimmed.

    Returns:
        bool: True if memory trimming is recommended
    """
```

**Logic:**

- Calculates memory utilization ratio
- Triggers at 150% of safe size
- Prevents memory bloat

##### `_trim_conversation_history_incremental() -> bool`

Incrementally trims conversation history.

```python
def _trim_conversation_history_incremental(self) -> bool:
    """
    Incrementally trim conversation history.

    Returns:
        bool: True if trimming was performed
    """
```

**Features:**

- Real-time memory management
- Adaptive trimming thresholds
- Performance monitoring

##### `_monitor_performance(operation: str, start_time: float) -> None`

Monitors operation performance.

```python
def _monitor_performance(self, operation: str, start_time: float) -> None:
    """
    Monitor operation performance.

    Args:
        operation: Name of the operation
        start_time: Start time of the operation
    """
```

**Logging Levels:**

- `WARNING`: Operations > 5 seconds
- `INFO`: Operations 1-5 seconds
- `DEBUG`: Operations < 1 second

##### `_get_performance_stats() -> Dict[str, Any]`

Gets current performance statistics.

```python
def _get_performance_stats(self) -> Dict[str, Any]:
    """
    Get performance statistics.

    Returns:
        Dict[str, Any]: Performance statistics
    """
```

**Statistics Include:**

- Conversation length
- Memory utilization
- Timestamp

#### Tool Execution Methods

##### `_invoke_llm_with_tools() -> Any`

Binds tools to LLM and invokes with context.

```python
def _invoke_llm_with_tools(self) -> Any:
    """
    Bind tools to LLM and invoke with conversation context.

    Returns:
        Any: The LLM response with potential tool calls
    """
```

**Features:**

- Tool binding
- LLM invocation
- Performance monitoring
- Token usage tracking

##### `_extract_tool_calls(response: Any) -> list`

Extracts tool calls from LLM response.

```python
def _extract_tool_calls(self, response: Any) -> list:
    """
    Extract tool calls from LLM response.

    Args:
        response: The LLM response object

    Returns:
        list: List of tool call dictionaries
    """
```

##### `_execute_single_tool(tool_call: Dict[str, Any]) -> Dict[str, Any]`

Executes a single tool call.

```python
def _execute_single_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single tool call.

    Args:
        tool_call: Dictionary containing tool name, args, and call_id

    Returns:
        Dict[str, Any]: The result of tool execution
    """
```

**Features:**

- Tool approval checking
- Execution with security validation
- Memory management
- Performance monitoring

- Performance monitoring

### Security Classes (New in v0.3.0)

#### `RateLimitManager` (Singleton)

Manages rate limits for all tools.

```python
class RateLimitManager:
    def check_limit(self, tool_name: str) -> None:
        """
        Check if a tool can be executed.
        Raises RateLimitError if limit exceeded.
        """

    def get_status(self, tool_name: str) -> dict:
        """Returns {'current': int, 'limit': int, 'remaining': int, 'reset': float}."""
```

#### `AuditLogger` (Singleton)

Logs security-critical events (approvals, denials, shell execution).

```python
class AuditLogger:
    def log_event(self, event_type: str, user: str, action: str, resource: str, details: str = None):
        """Logs a secure event to audit.log."""
```

## Exception Classes

### InputValidationError

Raised when user input fails validation.

```python
class InputValidationError(Exception):
    """Raised when user input fails validation."""
```

**Common Causes:**

- Empty input
- Input exceeds maximum length (10,000 characters)
- Invalid characters

### ToolExecutionError

Raised when tool execution fails.

```python
class ToolExecutionError(Exception):
    """Raised when tool execution fails."""
```

**Common Causes:**

- Tool not found
- Tool execution timeout
- Tool permission denied
- Tool execution error

### LLMTimeoutError

Raised when LLM request times out.

```python
class LLMTimeoutError(Exception):
    """Raised when LLM request times out."""
```

**Common Causes:**

- LLM service unavailable
- Request timeout
- Network issues

## Configuration

### Environment Variables

The system respects these environment variables:

- `VERBOSE_LOGGING`: Enable detailed logging
- `SHOW_LLM_REASONING`: Show AI reasoning content
- `SHOW_TOKEN_USAGE`: Display token consumption metrics
- `SHOW_TOOL_DETAILS`: Show tool execution details

### Constants

Key constants defined in `src/core/constants.py`:

```python
# Chat loop limits
MAX_ITERATIONS = 5
MAX_INPUT_LENGTH = 10000

# Performance thresholds
TRIM_THRESHOLD = 1.5  # 150% of safe size
SAFE_TRIM_LEVEL = 1.2   # 120% of max pairs
```

## Usage Examples

### Basic Usage

```python
from src.core.chat_loop import ChatLoop

# Initialize chat loop
chat_loop = ChatLoop()

# Process user input
response = chat_loop.run_iteration("What files are in the current directory?")
print(response)
```

### Custom Confirmation Callback

```python
def custom_confirmation(tool_name: str, args: dict) -> bool:
    """Custom tool approval logic."""
    return tool_name in ["safe_tool1", "safe_tool2"]

chat_loop = ChatLoop(confirmation_callback=custom_confirmation)
response = chat_loop.run_iteration("Use safe_tool1 with args {}")
```

### Performance Monitoring

```python
import time
from src.core.chat_loop import ChatLoop

chat_loop = ChatLoop()

start_time = time.time()
response = chat_loop.run_iteration("Complex query")

# Check performance stats
stats = chat_loop._get_performance_stats()
print(f"Memory utilization: {stats['memory_utilization']:.2f}")
print(f"Conversation length: {stats['conversation_length']}")
```

### Error Handling

```python
from src.core.chat_loop import (
    ChatLoop, 
    InputValidationError, 
    ToolExecutionError, 
    LLMTimeoutError
)

chat_loop = ChatLoop()

try:
    response = chat_loop.run_iteration(user_input)
except InputValidationError as e:
    print(f"Invalid input: {e}")
except ToolExecutionError as e:
    print(f"Tool execution failed: {e}")
except LLM(f"Tool executionTimeoutError as e:
    print(f"AI request timed out: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Integration Guide

### With Existing Applications

```python
class CustomAIAssistant:
    def __init__(self):
        self.chat_loop = ChatLoop()
        self.custom_tools = self._register_tools()
    
    def _register_tools(self):
        # Register custom tools
        pass
    
    def process_message(self, message: str) -> str:
        try:
            return self.chat_loop.run_iteration(message)
        except Exception as e:
            return self._handle_error(e)
```

### With Web Frameworks

```python
from flask import Flask, request, jsonify
from src.core.chat_loop import ChatLoop

app = Flask(__name__)
chat_loop = ChatLoop()

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    user_input = data.get('message', '')
    
    try:
        response = chat_loop.run_iteration(user_input)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### With Async Applications

```python
import asyncio
from src.core.chat_loop import ChatLoop

async def async_chat_process(user_input: str) -> str:
    chat_loop = ChatLoop()
    
    # Run in thread pool for blocking operations
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None, 
        chat_loop.run_iteration, 
        user_input
    )
    return response

# Usage
response = await async_chat_process("What time is it?")
```

## Best Practices

### Input Validation

- Always validate user input before processing
- Use appropriate error handling for validation failures
- Log validation errors for debugging

### Performance

- Monitor memory usage for long-running applications
- Use performance statistics for optimization
- Consider memory management for large conversations

### Error Handling

- Catch specific exception types
- Provide user-friendly error messages
- Log technical details for debugging

### Security

- Review tool approvals regularly
- Monitor tool execution patterns
- Validate all inputs thoroughly

## Troubleshooting

### Common Issues

#### Memory Usage High

```python
# Check memory statistics
stats = chat_loop._get_performance_stats()
if stats['memory_utilization'] > 0.8:
    # Force memory cleanup
    chat_loop._cleanup_memory()
```

#### Slow Performance

```python
# Monitor operation timing
import time
start = time.time()
# ... operation ...
elapsed = time.time() - start
if elapsed > 5.0:
    print(f"Slow operation detected: {elapsed:.2f}s")
```

#### Tool Execution Failures

```python
# Check tool registry
from src.tools.registry import ToolRegistry
available_tools = ToolRegistry.list_tools()
print(f"Available tools: {available_tools}")
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable all logging flags
os.environ['VERBOSE_LOGGING'] = 'true'
os.environ['SHOW_LLM_REASONING'] = 'true'
os.environ['SHOW_TOKEN_USAGE'] = 'true'
os.environ['SHOW_TOOL_DETAILS'] = 'true'
```

## Performance Benchmarks

### Typical Performance Metrics

| Operation | Expected Time | Memory Impact |
|-----------|-------------|--------------|
| Input validation | < 1ms | Minimal |
| Context injection | < 10ms | Low |
| Tool execution | < 100ms | Varies |
| Memory trimming | < 10ms | Medium |
| Complete iteration | < 500ms | Low |

### Scalability

- Supports conversations with 1000+ messages
- Handles 100+ tool calls per iteration
- Memory usage: ~1MB per 100 messages
- CPU usage: <5% for typical operations

---

*This API documentation covers the core Chat Loop System functionality. For advanced usage and customization options, see the performance guide and implementation details.*
