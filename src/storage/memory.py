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
Conversation memory management for DevAssist.

This module provides functions for loading and saving conversation history
to the SQLite database, as well as history trimming to prevent memory bloat.
"""

import logging
from typing import List, Optional, Sequence

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

from src.core.config import get_config
from src.core.constants import SYSTEM_PROMPT
from src.core.context import get_context

logger = logging.getLogger(__name__)


def load_memory() -> List[BaseMessage]:
    """
    Load conversation history from SQLite database.

    This function enables conversation continuity across application restarts by:
    1. Reading message history from SQLite database
    2. Reconstructing LangChain message objects
    3. Providing fallback for new conversations

    Returns:
        List of BaseMessage objects representing the conversation history

    Message Types:
    - SystemMessage: AI system prompts and context
    - HumanMessage: User inputs and questions
    - AIMessage: AI responses and answers
    """
    config = get_config()
    ctx = get_context()

    try:
        if config.db_type == "sqlite" and ctx.db_conn and ctx.db_lock:
            # Load from SQLite database with thread safety
            with ctx.db_lock:
                cursor = ctx.db_conn.cursor()
                cursor.execute(
                    """
                    SELECT message_type, content FROM conversations
                    WHERE session_id = 'default'
                    ORDER BY timestamp ASC
                """
                )
                rows = cursor.fetchall()

            if not rows and config.verbose_logging:
                logger.debug(
                    "No conversation history found in database, starting fresh"
                )

            # Reconstruct message objects from database rows
            # We explicitly IGNORE stored SystemMessages to ensure the AI always
            # uses the latest definitions/capabilities defined in code.
            user_ai_history: List[BaseMessage] = []
            for msg_type, content in rows:
                if msg_type == "HumanMessage":
                    user_ai_history.append(HumanMessage(content=content))
                elif msg_type == "AIMessage":
                    user_ai_history.append(AIMessage(content=content))
                elif msg_type == "SystemMessage":
                    # Skip stored system prompts so we can inject the fresh one
                    pass
                else:
                    logger.warning(f"Unknown message type: {msg_type}, skipping")

            if config.verbose_logging:
                logger.debug(
                    f"Loaded {len(user_ai_history)} user/AI messages from database"
                )

            # Prepend the authoritative system prompt
            import json
            from src.tools.registry import ToolRegistry

            tool_json = json.dumps(ToolRegistry.get_definitions(), indent=2)

            system_prompt = SystemMessage(
                content=SYSTEM_PROMPT + f"\n\nAVAILABLE TOOLS:\n{tool_json}\n"
            )
            return [system_prompt] + user_ai_history

        else:
            # Database not available - return empty history for tests/development
            logger.warning(
                "SQLite database not available for loading conversation memory, using empty history"
            )
            return []

    except Exception as e:
        logger.warning(f"Failed to load memory: {e}, using empty history")
        # Return empty list instead of raising error to allow tests to run
        return []


def save_memory(history: Sequence[BaseMessage]) -> None:
    """
    Save conversation history to SQLite database.

    Thread-safe SQLite database operations for persistent storage.

    Args:
        history: List of conversation messages to save

    Raises:
        RuntimeError: If database is not available
    """
    config = get_config()
    ctx = get_context()

    try:
        if config.db_type == "sqlite" and ctx.db_conn and ctx.db_lock:
            # Save to SQLite database with thread safety
            with ctx.db_lock:
                cursor = ctx.db_conn.cursor()

                # Prepare data for bulk insert (handle None content)
                data_to_insert = [
                    ("default", type(msg).__name__, msg.content or "")
                    for msg in history
                ]

                # Use transaction for atomic DELETE + INSERT
                # This prevents data loss if crash occurs between operations
                try:
                    cursor.execute("BEGIN TRANSACTION")
                    cursor.execute(
                        "DELETE FROM conversations WHERE session_id = 'default'"
                    )
                    cursor.executemany(
                        """
                        INSERT INTO conversations (session_id, message_type, content)
                        VALUES (?, ?, ?)
                        """,
                        data_to_insert,
                    )
                    ctx.db_conn.commit()
                    if config.verbose_logging:
                        logger.debug(
                            f"Saved {len(data_to_insert)} messages to database"
                        )
                except Exception:
                    ctx.db_conn.rollback()
                    raise

        else:
            # Database not available - this should not happen in normal operation
            logger.error("SQLite database not available for saving conversation memory")
            raise RuntimeError("Database required but not available")

    except Exception as e:
        logger.error(f"Failed to save memory: {e}")
        raise  # Re-raise to ensure the error is not silently ignored


def trim_history(
    history: Sequence[BaseMessage], max_pairs: Optional[int] = None
) -> List[BaseMessage]:
    """
    Trim conversation history to prevent memory bloat and API token limits.

    LangChain sends full conversation history with each API call. Long conversations
    can exceed token limits and slow down responses. This function maintains recent
    context while preventing excessive memory usage.

    Args:
        history: Complete list of conversation messages
        max_pairs: Maximum number of user-assistant exchange pairs to keep.
                   If None, uses MAX_HISTORY_PAIRS from config.

    Returns:
        Trimmed history list containing system message + recent exchanges

    Trimming Logic:
    - Always keep the first message (system prompt)
    - Keep the last (max_pairs * 2) messages (user + AI pairs)
    - Total length = 1 + (max_pairs * 2)
    - Example: max_pairs=10 -> keep system + 20 recent messages
    """
    if max_pairs is None:
        max_pairs = get_config().max_history_pairs

    # Calculate maximum allowed length: system message + (pairs * 2 messages per pair)
    max_length = max_pairs * 2 + 1

    # Only trim if history exceeds the limit
    if len(history) > max_length:
        # Keep system message (index 0) + most recent messages
        return [history[0]] + list(history[-(max_pairs * 2):])

    # Return unchanged if within limits
    return list(history)
