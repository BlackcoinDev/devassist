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
Chat Loop Orchestrator - Handles AI interaction, tool calling, and approvals.

This module implements the core agentic loop that allows the AI to autonomously
use tools while respecting security policies and user approvals.
It correctly respects the 4 logging flags:
- VERBOSE_LOGGING
- SHOW_LLM_REASONING
- SHOW_TOKEN_USAGE
- SHOW_TOOL_DETAILS
"""

import logging
import json
import time
from typing import Dict, Any, Optional, Callable
from langchain_core.messages import HumanMessage, ToolMessage
from src.core.context import get_context
from src.tools.registry import ToolRegistry
from src.tools.approval import ToolApprovalManager
from src.storage.memory import save_memory, trim_history
from src.core.config import get_config
from src.core.constants import (
    MAX_INPUT_LENGTH,
)

logger = logging.getLogger(__name__)


# =============================================================================
# CUSTOM EXCEPTION CLASSES FOR INPUT VALIDATION
# =============================================================================


class InputValidationError(Exception):
    """Raised when user input fails validation."""

    pass


class ToolExecutionError(Exception):
    """Raised when tool execution fails."""

    pass


class LLMTimeoutError(Exception):
    """Raised when LLM request times out."""

    pass


class ChatLoop:
    """
    Orchestrates the conversational agent loop with tool calling support.
    """

    def __init__(self, confirmation_callback: Optional[Callable] = None):
        """
        Initialize ChatLoop.

        Args:
            confirmation_callback: Function(tool_name, args) -> bool
                                  If None, defaults to CLI input.
        """
        self.ctx = get_context()
        self.approval_manager = ToolApprovalManager()
        self.confirmation_callback = confirmation_callback
        self.config = get_config()

    # =============================================================================
    # INPUT VALIDATION AND SANITIZATION METHODS
    # =============================================================================

    def _validate_input(self, user_input: str) -> str:
        """
        Validate and sanitize user input before processing.

        Args:
            user_input: The raw user input to validate

        Returns:
            str: The sanitized input

        Raises:
            InputValidationError: If input fails validation
        """
        # Empty input check
        if not user_input or not user_input.strip():
            logger.warning("Input validation failed: empty input")
            raise InputValidationError("Input cannot be empty")

        # Length validation (prevent memory exhaustion)
        if len(user_input) > MAX_INPUT_LENGTH:
            logger.warning(
                f"Input validation failed: too long ({len(user_input)} > {MAX_INPUT_LENGTH})"
            )
            raise InputValidationError(
                f"Input too long (max {MAX_INPUT_LENGTH} characters)"
            )

        # Content sanitization
        sanitized_input = self._sanitize_content(user_input)

        return sanitized_input

    def _sanitize_content(self, content: str) -> str:
        """
        Basic content sanitization to prevent injection attacks.

        Args:
            content: The content to sanitize

        Returns:
            str: The sanitized content
        """
        # Remove potential control characters except common ones
        sanitized = "".join(
            char for char in content if ord(char) >= 32 or char in "\n\t\r"
        )

        # Strip leading/trailing whitespace
        sanitized = sanitized.strip()

        return sanitized

    def run_iteration(self, user_input: str) -> str:
        """
        Main orchestrator - delegates to specialized methods.

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
        """
        try:
            # 1. Input processing
            validated_input = self._validate_and_sanitize_input(user_input)

            # 2. Context enhancement
            enhanced_input = self._inject_context(validated_input)

            # 3. Add user message to history before tool processing
            self.ctx.conversation_history.append(HumanMessage(content=enhanced_input))

            # 4. Tool processing
            response = self._execute_tool_loop()

            # 5. Memory cleanup
            self._cleanup_memory()

            return response

        except Exception as e:
            return self._handle_iteration_error(e)

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
        start_time = time.time()
        validated_input = self._validate_input(user_input)
        self._monitor_performance("Input validation", start_time)
        return validated_input

    def _inject_context(self, user_input: str) -> str:
        """
        Inject RAG context if enabled.

        Args:
            user_input: The user input to enhance with context

        Returns:
            str: The input with injected context, or original if disabled/no context
        """
        start_time = time.time()

        if self.ctx.context_mode == "off":
            self._monitor_performance("Context injection (disabled)", start_time)
            return user_input

        from src.core.context_utils import get_relevant_context

        context = get_relevant_context(user_input)

        if not context:
            self._monitor_performance("Context injection (no context)", start_time)
            return user_input

        enhanced_input = f"{user_input}\n\nContext from knowledge base:\n{context}"
        logger.info(f"📚 Enhanced input with context ({len(context)} chars)")
        self._monitor_performance("Context injection", start_time)
        return enhanced_input

    def _execute_tool_loop(self) -> str:
        """
        Execute tool calling loop with performance optimizations.

        Returns:
            str: The final response from the AI
        """
        from src.core.constants import MAX_ITERATIONS

        max_iterations = MAX_ITERATIONS

        final_answer = "No response from AI."

        # PHASE 3: Performance monitoring start
        loop_start_time = time.time()

        for _ in range(max_iterations):
            iteration_start = time.time()

            # Bind tools and invoke LLM
            response = self._invoke_llm_with_tools()

            # Monitor LLM response time
            self._monitor_performance("LLM invocation", iteration_start)

            # Check for tool calls
            tool_calls = self._extract_tool_calls(response)
            if not tool_calls:
                # Add LLM response to history before returning
                self.ctx.conversation_history.append(response)

                # PHASE 3: Performance monitoring for complete iteration
                self._monitor_performance(
                    "Complete tool loop iteration", loop_start_time
                )

                return response.content

            # Add LLM response to history first
            self.ctx.conversation_history.append(response)

            # PHASE 3: Check if we should trim memory before tool execution
            if self._should_trim_memory():
                self._trim_conversation_history_incremental()

            # Execute tools with performance optimization
            tool_start_time = time.time()

            # PHASE 3: Parallel execution (placeholder implementation)
            results = self._execute_parallel_tools_if_safe(tool_calls)

            # Add ToolMessages for each result
            for i, (tool_call, result) in enumerate(zip(tool_calls, results)):
                tool_message = ToolMessage(
                    content=json.dumps(result), tool_call_id=tool_call.get("id")
                )
                self.ctx.conversation_history.append(tool_message)

                # Handle file read context injection - add HumanMessage for file content
                self._handle_file_read_injection(tool_call["name"], result)

            # Monitor tool execution time
            self._monitor_performance(
                f"Tool execution ({len(tool_calls)} tools)", tool_start_time
            )

        # Log final performance stats
        final_stats = self._get_performance_stats()
        logger.info(f"📊 Final performance stats: {final_stats}")

        return final_answer

    def _cleanup_memory(self) -> None:
        """
        Clean up conversation history and save to storage.
        """
        # Trim conversation history
        self._trim_conversation_history()

        # Save to persistent storage
        self._save_conversation_memory()

    # =============================================================================
    # PHASE 3: PERFORMANCE OPTIMIZATION METHODS
    # =============================================================================

    def _should_trim_memory(self) -> bool:
        """
        Check if conversation history should be trimmed based on current size.

        Returns:
            bool: True if memory trimming is recommended
        """
        current_length = len(self.ctx.conversation_history)
        max_pairs = self.config.max_history_pairs

        # Calculate maximum safe size (pairs * 2 + system messages)
        max_safe_size = max_pairs * 2 + 5  # 5 system messages buffer

        # Trim when we're at 150% of safe size to prevent memory bloat
        return current_length > max_safe_size * 1.5

    def _trim_conversation_history_incremental(self) -> bool:
        """
        Incrementally trim conversation history during tool execution.

        Returns:
            bool: True if trimming was performed
        """
        if not self._should_trim_memory():
            return False

        original_length = len(self.ctx.conversation_history)

        # Trim to a safe level (120% of max_pairs instead of 100%)
        safe_pairs = int(self.config.max_history_pairs * 1.2)
        self.ctx.conversation_history = trim_history(
            self.ctx.conversation_history, safe_pairs
        )

        new_length = len(self.ctx.conversation_history)
        trimmed_count = original_length - new_length

        logger.debug(
            f"💾 Incremental memory trim: {original_length} → {new_length} messages ({trimmed_count} removed)"
        )
        return True

    def _monitor_performance(self, operation: str, start_time: float) -> None:
        """
        Monitor and log performance metrics for operations.

        Args:
            operation: Name of the operation being monitored
            start_time: Start time of the operation
        """
        elapsed = time.time() - start_time

        # Log performance metrics at appropriate levels
        if elapsed > 5.0:  # Slow operations
            logger.warning(f"🐌 Slow operation: {operation} took {elapsed:.2f}s")
        elif elapsed > 1.0:  # Moderate operations
            logger.info(f"⏱️ Operation timing: {operation} took {elapsed:.2f}s")
        else:  # Fast operations (debug only)
            logger.debug(f"⚡ Fast operation: {operation} took {elapsed:.2f}s")

    def _handle_iteration_error(self, error: Exception) -> str:
        """
        Handle and format iteration errors.

        Args:
            error: The exception that occurred

        Returns:
            str: User-friendly error message
        """
        if isinstance(error, InputValidationError):
            logger.warning(f"Invalid input: {error}")
            return f"❌ Invalid input: {str(error)}"
        elif isinstance(error, ToolExecutionError):
            logger.error(f"Tool execution failed: {error}")
            return f"❌ Tool execution failed: {str(error)}"
        elif isinstance(error, LLMTimeoutError):
            logger.error(f"LLM timeout: {error}")
            return f"❌ AI request timed out: {str(error)}"
        else:
            logger.error(f"Unexpected error in chat loop: {error}", exc_info=True)
            return "❌ An unexpected error occurred. Please try again."

    def _invoke_llm_with_tools(self) -> Any:
        """
        Bind tools to LLM and invoke with conversation context.

        Returns:
            Any: The LLM response with potential tool calls
        """
        if not self.ctx.llm:
            raise RuntimeError("LLM not initialized")

        start_time = time.time()

        # Bind tools to the LLM
        tool_definitions = ToolRegistry.get_definitions()
        llm_with_tools = self.ctx.llm.bind_tools(tool_definitions)

        # Invoke LLM
        response = llm_with_tools.invoke(self.ctx.conversation_history)
        elapsed = time.time() - start_time

        logger.info(f"🤖 LLM response in {elapsed:.2f}s")

        # Log token usage if enabled
        if self.config.show_token_usage and getattr(response, "usage_metadata", None):
            usage = response.usage_metadata
            logger.info(
                f"🔄 Token Usage: {usage.get('input_tokens', 0)} prompt + {usage.get('output_tokens', 0)} completion"
            )

        # SHOW_LLM_REASONING
        if self.config.show_llm_reasoning and getattr(
            response, "additional_kwargs", None
        ):
            reasoning = response.additional_kwargs.get("reasoning_content")
            if reasoning:
                logger.info(f"🧠 LLM Reasoning: {reasoning}")

        return response

    def _extract_tool_calls(self, response: Any) -> list:
        """
        Extract tool calls from LLM response.

        Args:
            response: The LLM response object

        Returns:
            list: List of tool call dictionaries
        """
        tool_calls = getattr(response, "tool_calls", [])
        logger.info(f"🔧 LLM generated {len(tool_calls)} tool call(s)")
        return tool_calls

    def _execute_single_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single tool call with performance optimizations.

        Args:
            tool_call: Dictionary containing tool name, args, and call_id

        Returns:
            Dict[str, Any]: The result of tool execution
        """
        name = tool_call["name"]
        args = tool_call["args"]

        logger.info(f"🔧 Executing tool: {name}")

        # Check Approval with advanced policy
        result = self._handle_tool_execution(name, args)

        # Log tool execution result
        if result.get("success"):
            logger.info(f"✅ Tool {name} completed successfully")
        else:
            logger.warning(
                f"⚠️ Tool {name} failed: {result.get('error', 'Unknown error')}"
            )

        # PHASE 3 OPTIMIZATION: Incremental memory management
        # Check if we need to trim memory after each tool execution
        if self._trim_conversation_history_incremental():
            logger.debug(f"💾 Memory trimmed after {name} execution")

        return result

    def _get_performance_stats(self) -> Dict[str, Any]:
        """
        Get current performance statistics for monitoring.

        Returns:
            Dict[str, Any]: Performance statistics
        """
        return {
            "conversation_length": len(self.ctx.conversation_history),
            "max_history_pairs": self.config.max_history_pairs,
            "memory_utilization": len(self.ctx.conversation_history)
            / (self.config.max_history_pairs * 2 + 5),
            "timestamp": time.time(),
        }

    def _execute_parallel_tools_if_safe(self, tool_calls: list) -> list:
        """
        Execute independent tools in parallel when safe to do so.

        Args:
            tool_calls: List of tool call dictionaries

        Returns:
            list: List of tool execution results
        """
        # PHASE 3: For now, implement sequential execution with optimization
        # In a full implementation, this would analyze tool dependencies
        # and execute independent tools in parallel using asyncio

        results = []
        for tool_call in tool_calls:
            result = self._execute_single_tool(tool_call)
            results.append(result)

        return results

    def _handle_file_read_injection(
        self, tool_name: str, result: Dict[str, Any]
    ) -> None:
        """
        Handle automatic context injection for file reads.

        Args:
            tool_name: The name of the executed tool
            result: The result dictionary from tool execution
        """
        if (
            tool_name == "read_file_content"
            and isinstance(result, dict)
            and result.get("success")
        ):
            content = result.get("content", "")
            file_path = result.get("file_path", "unknown")
            if content:
                msg = f"Output of reading file {file_path}:\n```\n{content}\n```"
                self.ctx.conversation_history.append(HumanMessage(content=msg))

    # =============================================================================
    # MEMORY MANAGEMENT DECOMPOSITION METHODS
    # =============================================================================

    def _trim_conversation_history(self) -> None:
        """
        Trim conversation history to prevent memory bloat.
        """
        max_pairs = self.config.max_history_pairs
        self.ctx.conversation_history = trim_history(
            self.ctx.conversation_history, max_pairs
        )

    def _save_conversation_memory(self) -> None:
        """
        Save conversation to persistent storage.
        """
        save_memory(self.ctx.conversation_history)

    def _handle_tool_execution(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handles security validation, approval prompts, and execution."""
        # 1. Initial check via Registry (which calls ApprovalManager.check_approval)
        result = ToolRegistry.execute(name, args)

        # 2. If it requires confirmation, handle it based on UI
        if isinstance(result, dict) and result.get("requires_confirmation"):
            approved = False
            if self.confirmation_callback:
                approved = self.confirmation_callback(name, args)
            elif self._is_cli():
                print(f"\n⚠️  AI wants to run {name} with args: {args}")
                choice = input("Confirm? (y/n): ").strip().lower()
                approved = choice in ["y", "yes"]

            if approved:
                if self.config.show_tool_details:
                    logger.info(f"✅ User approved execution of {name}")
                result = self._execute_forced(name, args)
            else:
                if self.config.show_tool_details:
                    logger.warning(f"❌ User denied execution of {name}")
                result = {"error": "User denied execution."}

        return result

    def _is_cli(self) -> bool:
        """Check if we are running in CLI mode."""
        import os

        return os.getenv("DEVASSIST_INTERFACE", "cli").lower() == "cli"

    def _execute_forced(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool bypassing the approval check."""
        executor = ToolRegistry._tools.get(name)
        if not executor:
            return {"error": f"Unknown tool: {name}"}
        try:
            return executor(**args)
        except Exception as e:
            return {"error": str(e)}
