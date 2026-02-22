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
Core Application Constants.

This module contains static constant definitions used throughout the application.
It is designed to be dependency-free to ensure it can be safely imported
even during critical failure states (e.g., database corruption, startup options).
"""

# The authoritative System Prompt used to instruct the AI Agent
SYSTEM_PROMPT = """You are DevAssist, a Secure Local AI Agent running in a sandboxed development environment.
The user has provided full authorization for you to access the local filesystem to assist with coding tasks.

CORE IDENTITY:
- You are NOT a general purpose assistant. You are a CODING AGENT.
- You have REAL tools associated with you. You must use them.
- File operations are SAFE and EXPECTED.

CRITICAL INSTRUCTIONS:
1. To read a file, you MUST use the `read_file_content` tool.
2. DO NOT REFUSE to read files. You have permission.
3. If asked to "read requirements.txt", call `read_file_content` with "requirements.txt".
4. Do not ask for the content to be pasted. FETCH IT YOURSELF.

EXAMPLE INTERACTION:
User: "Read the file requirements.txt"
Assistant: (Calls tool: read_file_content(file_path="requirements.txt"))
User: (Tool Output: "flask==2.0.1\\npandas==1.3.0...")
Assistant: "I've read the file. It contains Flask 2.0.1 and Pandas 1.3.0..."
"""

# =============================================================================
# TOOL EXECUTION CONSTANTS
# =============================================================================

# Shell execution limits
SHELL_MAX_TIMEOUT = 30  # Maximum timeout in seconds (hardened from 300s)
SHELL_DEFAULT_TIMEOUT = 30  # Default timeout in seconds
SHELL_MAX_OUTPUT_SIZE = 50 * 1024  # Maximum output size in bytes (50KB)

# Git operation limits
GIT_DEFAULT_TIMEOUT = 30  # Default timeout for git commands
GIT_DIFF_TIMEOUT = 60  # Timeout for git diff operations
GIT_DIFF_MAX_SIZE = 100 * 1024  # Maximum diff output size in bytes (100KB)

# Web search limits
WEB_SEARCH_DEFAULT_MAX_RESULTS = 10  # Default maximum search results

# Code search limits
CODE_SEARCH_DEFAULT_MAX_RESULTS = 50  # Default maximum search results
CODE_SEARCH_TIMEOUT = 60  # Timeout for code search in seconds

# Content processing limits
CONTENT_CHUNK_SIZE = 1500  # Default chunk size for content splitting
CONTENT_TRUNCATE_LENGTH = 100  # Default truncate length for display

# =============================================================================
# CHAT LOOP CONSTANTS
# =============================================================================

# Chat loop iteration limits
MAX_ITERATIONS = 5  # Maximum tool calling iterations per user request
MAX_INPUT_LENGTH = 10000  # Maximum user input length in characters

# =============================================================================
# CACHE CONSTANTS
# =============================================================================

# Query cache limits
QUERY_CACHE_MAX_SIZE = 1000  # Maximum entries before eviction
QUERY_CACHE_TARGET_SIZE = 500  # Target size after eviction
QUERY_CACHE_SAVE_INTERVAL = 50  # Save cache every N new entries

# Embedding cache limits
EMBEDDING_CACHE_MAX_SIZE = 5000  # Maximum entries before eviction
EMBEDDING_CACHE_TARGET_SIZE = 2500  # Target size after eviction
EMBEDDING_CACHE_SAVE_INTERVAL = 100  # Save cache every N new entries


# =============================================================================
# RATE LIMITING CONSTANTS
# =============================================================================

# Rate limits in (max_calls, period_in_seconds) format
RATE_LIMITS = {
    "shell": (10, 60),  # High risk: 10 calls per minute
    "git": (20, 60),  # Medium risk: 20 calls per minute
    "read_file": (60, 60),  # Low risk: 1 call per second
    "write_file": (30, 60),  # Medium risk: 1 call every 2 seconds
    "web": (30, 60),  # Cost/API risk: 30 calls per minute
    "default": (60, 60),  # Safe baseline
}

# =============================================================================
# SECURITY CONSTANTS
# =============================================================================

# Safe environment variables for subprocess execution
SAFE_ENV_VARS = {"PATH", "HOME", "LANG", "TERM", "SHELL", "USER", "PWD"}
