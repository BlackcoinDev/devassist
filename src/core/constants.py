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
SHELL_MAX_TIMEOUT = 300  # Maximum timeout in seconds
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
