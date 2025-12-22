"""
Main chat loop functionality

This module contains the core interactive chat loop extracted from main.py
to improve modularity and reduce the size of the main module.
"""

import logging
import time
from typing import List
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
    BaseMessage,
)

# Import security
from src.security.input_sanitizer import InputSanitizer
from src.security.exceptions import SecurityError
from src.core.config import get_config

# Display functions will be imported locally to avoid circular imports

module_logger = logging.getLogger(__name__)
_config = get_config()


class ChatLoop:
    """Main chat loop handler with all conversation logic."""

    def __init__(
        self,
        llm,
        vectorstore,
        embeddings,
        conversation_history: List,
        get_relevant_context,
        handle_slash_command,
        save_memory,
        execute_tool_call=None,
        user_memory=None,
        logger=None,
    ):
        """Initialize chat loop with required dependencies."""
        self.llm = llm
        self.vectorstore = vectorstore
        self.embeddings = embeddings
        self.conversation_history = conversation_history
        self.get_relevant_context = get_relevant_context
        self.handle_slash_command = handle_slash_command
        self.save_memory = save_memory
        self.execute_tool_call = execute_tool_call
        self.user_memory = user_memory
        self.logger = logger

        # Configuration constants (will be passed in)
        self.MAX_INPUT_LENGTH = 10000  # Should be configurable
        self.VERBOSE_LOGGING = False  # Should be configurable

    def run(self) -> bool:
        """
        Run the main chat loop.

        Returns:
            bool: True if exited normally, False if there was an error
        """
        # Simple welcome message to avoid circular imports
        print("🤖 AI Assistant Chat Interface")
        print("Type your message or 'quit' to exit")
        print()

        # Main interaction loop
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                # Process the input
                should_exit = self._process_user_input(user_input)
                if should_exit:
                    break

            except ConnectionError as e:
                # Log connection error as expected by tests
                if self.logger:
                    self.logger.error(f"Connection error: {e}")
                print("Connection error: Server unreachable")
                print("Please ensure LM Studio is running and accessible.")
                continue
            except KeyboardInterrupt:
                # Save memory and show goodbye message as expected by tests
                self.save_memory(self.conversation_history)
                print("\n\n👋 Goodbye! Your conversation has been saved.")
                break
            except EOFError:
                # Save memory and show goodbye message as expected by tests
                self.save_memory(self.conversation_history)
                print("\n\n👋 Goodbye! Your conversation has been saved.")
                break
            except Exception as e:
                print(f"\n💥 Fatal error in chat loop: {e}")
                return False

        # Save conversation on exit
        try:
            self.save_memory(self.conversation_history)
            print(f"💾 Saved {len(self.conversation_history)} messages")
        except Exception as e:
            print(f"⚠️ Failed to save conversation: {e}")

        return True

    def _process_user_input(self, user_input: str) -> bool:
        """
        Process a single user input.

        Args:
            user_input: The user's input string

        Returns:
            bool: True if should exit, False to continue
        """
        if _config.verbose_logging:
            module_logger.debug(f"Processing input: {len(user_input)} chars")

        # Security: Sanitize user input
        try:
            sanitized_input = InputSanitizer.sanitize_text(user_input)
            if sanitized_input is None:
                print("❌ Error: Input cannot be None")
                return False
            user_input = sanitized_input
        except SecurityError as e:
            print(f"Security Alert: {e}")
            print("Please enter valid input without dangerous content.")
            return False

        # Handle forced tool calls (web search detection)
        if self._handle_forced_tool_call(user_input):
            return False

        # Skip empty input
        if not user_input:
            return False

        # Handle quit commands
        if self._handle_quit_commands(user_input):
            return True

        # Handle slash commands
        if self._handle_slash_commands(user_input):
            return False

        # Validate input length
        if len(user_input) > self.MAX_INPUT_LENGTH:
            print(
                f"\nError: Input exceeds maximum length of {self.MAX_INPUT_LENGTH} characters."
            )
            return False

        # Process regular conversation
        return self._process_conversation(user_input)

    def _handle_forced_tool_call(self, user_input: str) -> bool:
        """Handle forced tool calls (simplified version)."""
        # For now, just return False - tool calling can be added later
        return False

    def _handle_quit_commands(self, user_input: str) -> bool:
        """Handle quit/exit commands."""
        if user_input.lower() in ["quit", "exit", "q"]:
            self.save_memory(self.conversation_history)
            print("\n👋 Goodbye! Your conversation has been saved.")
            return True

        if any(quit_cmd in user_input.lower() for quit_cmd in ["quit", "exit"]):
            self.save_memory(self.conversation_history)
            print("\n👋 Goodbye! Your conversation has been saved.")
            return True

        return False

    def _handle_slash_commands(self, user_input: str) -> bool:
        """Handle slash commands."""
        if user_input.startswith("/"):
            if self.handle_slash_command(user_input):
                return True  # Command handled
            else:
                print(f"\nUnknown command: {user_input}")
                print("Type /help for available commands\n")
                return True
        return False

    def _process_conversation(self, user_input: str) -> bool:
        """Process regular conversation input."""
        # Add user message to history
        self.conversation_history.append(HumanMessage(content=user_input))

        # Get context from vector database and user memory
        context = self._get_context(user_input)

        # Generate AI response
        response = self._generate_ai_response(user_input, context)

        # Display response
        self._display_response(response)

        # Add AI response to history
        self.conversation_history.append(AIMessage(content=response))

        # Periodic cleanup
        self._periodic_cleanup()

        print()  # Add blank line
        return False

    def _get_context(self, user_input: str) -> str:
        """Get relevant context from vector database and user memory."""
        context = ""

        if _config.verbose_logging:
            module_logger.debug("Retrieving context from knowledge base...")

        # Get context from vector database
        if self.vectorstore:
            context = self.get_relevant_context(user_input)
            if _config.verbose_logging and context:
                module_logger.debug(
                    f"   📚 Retrieved {len(context)} chars from vector DB"
                )

        # Add user memory context
        if self.user_memory:
            try:
                mem_results = self.user_memory.search(
                    user_input, user_id="default_user"
                )

                mem_list = []
                if isinstance(mem_results, dict) and "results" in mem_results:
                    results = mem_results["results"]
                    if isinstance(results, list):
                        mem_list = [
                            r.get("memory", "") for r in results if isinstance(r, dict)
                        ]
                elif isinstance(mem_results, list):
                    mem_list = [
                        r.get("memory", "") for r in mem_results if isinstance(r, dict)
                    ]

                if mem_list:
                    mem_str = "\n".join(mem_list)
                    context += f"\n\n[User Context & Preferences]:\n{mem_str}"
                    if _config.verbose_logging:
                        module_logger.debug(
                            f"   🧠 Retrieved {len(mem_list)} memories from Mem0"
                        )

            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Mem0 search error: {e}")

        return context

    def _generate_ai_response(self, user_input: str, context: str) -> str:
        """Generate AI response with context."""
        # Build messages for LLM
        system_message = SystemMessage(
            content="""You are an advanced AI assistant with access to various tools.
You can use tools to help answer questions and perform tasks. Be helpful and provide detailed responses."""
        )

        messages: List[BaseMessage] = [system_message]

        # Add context if available
        if context:
            context_message = SystemMessage(
                content=f"Relevant context from knowledge base:\n{context}"
            )
            messages.append(context_message)

        # Add recent conversation history (limit to prevent token overflow)
        max_history = 20  # Default: keep last 10 exchanges (20 messages)
        recent_messages = (
            self.conversation_history[-max_history:]
            if len(self.conversation_history) > max_history
            else self.conversation_history
        )
        messages.extend(recent_messages)

        if _config.show_llm_reasoning:
            module_logger.info(
                f"🧠 LLM: Generating response with {len(messages)} messages"
            )
            if context:
                module_logger.info(f"   📋 Context: {len(context)} chars provided")

        # Get AI response
        print("🤔 Thinking...", end="", flush=True)
        start_time = time.time()
        response = self.llm.invoke(messages)
        elapsed = time.time() - start_time
        print("\r" + " " * 20 + "\r", end="", flush=True)  # Clear thinking message

        if _config.show_llm_reasoning:
            module_logger.info(f"   ⏱️ Response generated in {elapsed:.2f}s")

        # Log token usage if available
        if _config.show_token_usage:
            if hasattr(response, "response_metadata") and response.response_metadata:
                metadata = response.response_metadata
                if "token_usage" in metadata:
                    usage = metadata["token_usage"]
                    prompt_tokens = usage.get("prompt_tokens", "?")
                    completion_tokens = usage.get("completion_tokens", "?")
                    module_logger.info(
                        f"   📊 Tokens: {prompt_tokens} prompt, {completion_tokens} completion"
                    )
                elif "usage" in metadata:
                    usage = metadata["usage"]
                    prompt_tokens = usage.get("prompt_tokens", "?")
                    completion_tokens = usage.get("completion_tokens", "?")
                    module_logger.info(
                        f"   📊 Tokens: {prompt_tokens} prompt, {completion_tokens} completion"
                    )

        # Handle tool calls
        if hasattr(response, "tool_calls") and response.tool_calls:
            if _config.show_tool_details:
                module_logger.info(
                    f"   🔧 Tool calls detected: {len(response.tool_calls)}"
                )

            # Execute each tool call
            from src.tools import ToolRegistry

            tool_results = []

            for tc in response.tool_calls:
                tool_name = (
                    tc.get("name", "unknown")
                    if isinstance(tc, dict)
                    else getattr(tc, "name", "unknown")
                )
                if _config.show_tool_details:
                    module_logger.info(f"      • Executing: {tool_name}")

                tool_start = time.time()
                result = ToolRegistry.execute_tool_call(tc)
                tool_elapsed = time.time() - tool_start

                if _config.show_tool_details:
                    success = (
                        "error" not in result.get("result", {})
                        if isinstance(result.get("result"), dict)
                        else True
                    )
                    status = "✅" if success else "❌"
                    module_logger.info(
                        f"        {status} Completed in {tool_elapsed:.2f}s"
                    )

                tool_results.append(result)

            # Add tool results as ToolMessages to messages for follow-up LLM call
            if tool_results:
                for tc, tr in zip(response.tool_calls, tool_results):
                    tool_call_id = (
                        tc.get("id", "")
                        if isinstance(tc, dict)
                        else getattr(tc, "id", "")
                    )
                    result_content = str(tr.get("result", {}))
                    tool_message = ToolMessage(
                        content=result_content, tool_call_id=tool_call_id
                    )
                    messages.append(tool_message)

                # Make follow-up LLM call with tool results
                if _config.show_llm_reasoning:
                    module_logger.info(
                        f"🧠 LLM: Generating follow-up response with {len(messages)} messages"
                    )

                follow_up_start = time.time()
                response = self.llm.invoke(messages)
                follow_up_elapsed = time.time() - follow_up_start

                if _config.show_llm_reasoning:
                    module_logger.info(
                        f"   ⏱️ Follow-up response generated in {follow_up_elapsed:.2f}s"
                    )

                # Log token usage for follow-up if available
                if _config.show_token_usage:
                    if (
                        hasattr(response, "response_metadata")
                        and response.response_metadata
                    ):
                        metadata = response.response_metadata
                        if "token_usage" in metadata:
                            usage = metadata["token_usage"]
                            prompt_tokens = usage.get("prompt_tokens", "?")
                            completion_tokens = usage.get("completion_tokens", "?")
                            module_logger.info(
                                f"   📊 Follow-up tokens: {prompt_tokens} prompt, {completion_tokens} completion"
                            )
                        elif "usage" in metadata:
                            usage = metadata["usage"]
                            prompt_tokens = usage.get("prompt_tokens", "?")
                            completion_tokens = usage.get("completion_tokens", "?")
                            module_logger.info(
                                f"   📊 Follow-up tokens: {prompt_tokens} prompt, {completion_tokens} completion"
                            )

                return (
                    response.content
                    or "Tool execution completed but no final response generated."
                )

        return response.content

    def _display_response(self, response: str):
        """Display AI response with formatting."""
        try:
            from rich.console import Console
            from rich.markdown import Markdown

            console = Console()
            print("AI Assistant:")
            console.print(Markdown(response))
        except ImportError:
            print("AI Assistant:", response)

    def _periodic_cleanup(self):
        """Perform periodic cleanup tasks."""
        # This could be enhanced to include actual cleanup logic
        pass


def run_main_chat_loop():
    """
    Run the main chat loop with all dependencies.

    This function sets up all the necessary dependencies and runs the chat loop.
    """
    # Import all required dependencies locally to avoid circular imports
    from src.main import (
        llm,
        vectorstore,
        embeddings,
        conversation_history,
        get_relevant_context,
        handle_slash_command,
        save_memory,
    )
    from src.main import user_memory, logger

    # Tool calling not implemented in this simplified version
    execute_tool_call = None

    # Create and run chat loop
    chat_loop = ChatLoop(
        llm=llm,
        vectorstore=vectorstore,
        embeddings=embeddings,
        conversation_history=conversation_history,
        get_relevant_context=get_relevant_context,
        handle_slash_command=handle_slash_command,
        save_memory=save_memory,
        execute_tool_call=execute_tool_call,
        user_memory=user_memory,
        logger=logger,
    )

    return chat_loop.run()
