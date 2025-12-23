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
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from src.core.context import get_context
from src.tools.registry import ToolRegistry
from src.tools.approval import ToolApprovalManager
from src.storage.memory import save_memory, trim_history
from src.core.config import get_config

logger = logging.getLogger(__name__)


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

    def run_iteration(self, user_input: str) -> str:
        """
        Process a single user input through the AI loop.

        Args:
            user_input: The text input from the user.

        Returns:
            str: The final response from the AI.
        """
        if self.config.verbose_logging:
            logger.info(f"🔄 ChatLoop: Starting iteration for input: '{user_input[:50]}...'")

        # 1. Add user message to history
        self.ctx.conversation_history.append(HumanMessage(content=user_input))

        # 2. Get context (RAG)
        from src.main import get_relevant_context
        if self.ctx.context_mode != "off":
            context = get_relevant_context(user_input)
            if context:
                if self.config.verbose_logging:
                    logger.info(f"📚 ChatLoop: Injected context ({len(context)} chars)")
                self.ctx.conversation_history.append(SystemMessage(content=f"Relevant context: {context}"))

        # 3. Enter the Tool Loop (Maximum 5 iterations to prevent infinite loops)
        max_iterations = 5
        final_answer = "No response from AI."

        for i in range(max_iterations):
            try:
                if self.config.verbose_logging:
                    logger.debug(f"🤖 ChatLoop: AI Turn {i + 1}/{max_iterations}")

                # Call LLM
                if not self.ctx.llm:
                    return "❌ Error: LLM not initialized."

                if self.config.verbose_logging:
                    logger.info("🤖 Sending prompt to LLM...")

                start_time = time.time()
                response = self.ctx.llm.invoke(self.ctx.conversation_history)
                elapsed = time.time() - start_time

                if self.config.verbose_logging:
                    logger.info(f"📥 LLM Response received in {elapsed:.2f}s")

                # SHOW_TOKEN_USAGE
                if self.config.show_token_usage and getattr(response, "usage_metadata", None):
                    usage = response.usage_metadata
                    logger.info(f"🔄 Token Usage: {usage.get('input_tokens', 0)} prompt + {usage.get('output_tokens', 0)} completion")

                # SHOW_LLM_REASONING
                if self.config.show_llm_reasoning and getattr(response, "additional_kwargs", None):
                    reasoning = response.additional_kwargs.get("reasoning_content")
                    if reasoning:
                        logger.info(f"🧠 LLM Reasoning: {reasoning}")

                self.ctx.conversation_history.append(response)

                # Check for tool calls
                tool_calls = getattr(response, "tool_calls", [])
                if not tool_calls:
                    final_answer = response.content
                    break

                if self.config.show_tool_details:
                    logger.info(f"🔧 LLM Generated {len(tool_calls)} Tool Call(s)")

                # Execute tool calls
                for tool_call in tool_calls:
                    name = tool_call["name"]
                    args = tool_call["args"]
                    call_id = tool_call.get("id")

                    # Check Approval with advanced policy
                    result = self._handle_tool_execution(name, args)

                    # Add result to history as ToolMessage
                    self.ctx.conversation_history.append(ToolMessage(
                        content=json.dumps(result),
                        tool_call_id=call_id
                    ))

            except Exception as e:
                logger.error(f"Error in chat loop iteration: {e}")
                return f"❌ Error: {str(e)}"

        # 4. Final Cleanup
        # Trim and Save
        self.ctx.conversation_history = trim_history(
            self.ctx.conversation_history,
            self.config.max_history_pairs
        )
        save_memory(self.ctx.conversation_history)

        return str(final_answer)

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
                approved = choice in ['y', 'yes']

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
