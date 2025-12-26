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
System Tools - Executors for system-level operations.

This module provides AI tool executors for system operations including
code search using ripgrep.
"""

import os
import json
import logging
import subprocess
import shutil
from typing import Dict, Any, Optional, List

from src.tools.registry import ToolRegistry
from src.core.utils import standard_error
from src.core.constants import CODE_SEARCH_DEFAULT_MAX_RESULTS, CODE_SEARCH_TIMEOUT

logger = logging.getLogger(__name__)

# =============================================================================
# TOOL DEFINITIONS (OpenAI Function Calling Format)
# =============================================================================

CODE_SEARCH_DEFINITION = {
    "type": "function",
    "function": {
        "name": "code_search",
        "description": (
            "Search for code patterns using ripgrep (rg). "
            "Supports regex patterns, file type filtering, and returns "
            "matches with file paths, line numbers, and content. "
            "Requires ripgrep to be installed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The regex pattern to search for",
                },
                "path": {
                    "type": "string",
                    "description": "Directory or file to search in (default: current directory)",
                    "default": ".",
                },
                "file_type": {
                    "type": "string",
                    "description": (
                        "File type to filter by (e.g., 'py', 'js', 'ts', 'rs'). "
                        "Uses ripgrep's --type flag."
                    ),
                },
                "max_results": {
                    "type": "integer",
                    "description": (
                        f"Maximum number of matches to return (default: {CODE_SEARCH_DEFAULT_MAX_RESULTS}, max: 200)"
                    ),
                    "default": CODE_SEARCH_DEFAULT_MAX_RESULTS,
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Case-sensitive search (default: false)",
                    "default": False,
                },
            },
            "required": ["pattern"],
        },
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _check_ripgrep() -> bool:
    """Check if ripgrep is installed and available."""
    return shutil.which("rg") is not None


def _parse_rg_json_output(output: str) -> List[Dict[str, Any]]:
    """
    Parse ripgrep JSON output into structured matches.

    Args:
        output: Raw ripgrep JSON output (one JSON object per line)

    Returns:
        List of match dictionaries
    """
    matches = []

    for line in output.strip().split("\n"):
        if not line:
            continue

        try:
            data = json.loads(line)

            # Only process 'match' type entries
            if data.get("type") != "match":
                continue

            match_data = data.get("data", {})
            path = match_data.get("path", {}).get("text", "")
            line_number = match_data.get("line_number", 0)
            lines = match_data.get("lines", {}).get("text", "").rstrip("\n")

            # Get match positions for context
            submatches = match_data.get("submatches", [])
            match_text = ""
            if submatches:
                match_text = submatches[0].get("match", {}).get("text", "")

            matches.append(
                {
                    "file": path,
                    "line": line_number,
                    "content": lines,
                    "match": match_text,
                }
            )

        except json.JSONDecodeError:
            # Skip malformed lines
            continue

    return matches


# =============================================================================
# TOOL EXECUTORS
# =============================================================================


@ToolRegistry.register("code_search", CODE_SEARCH_DEFINITION)
def execute_code_search(
    pattern: str,
    path: str = ".",
    file_type: Optional[str] = None,
    max_results: int = 50,
    case_sensitive: bool = False,
) -> Dict[str, Any]:
    """
    Search for code patterns using ripgrep.

    Args:
        pattern: Regex pattern to search for
        path: Directory or file to search in
        file_type: Optional file type filter (e.g., 'py', 'js')
        max_results: Maximum matches to return
        case_sensitive: Whether search is case-sensitive

    Returns:
        Dict with success status and list of matches
    """
    # Validate pattern
    if not pattern:
        return standard_error("Search pattern cannot be empty")

    # Check ripgrep is installed
    if not _check_ripgrep():
        return {
            "error": "ripgrep (rg) is required but not installed. "
            "Please install ripgrep: https://github.com/BurntSushi/ripgrep"
        }

    # Validate max_results
    if max_results < 1:
        max_results = CODE_SEARCH_DEFAULT_MAX_RESULTS
    elif max_results > 200:
        max_results = 200

    # Security: Validate path is within current directory
    current_dir = os.getcwd()
    search_path = os.path.abspath(os.path.join(current_dir, path))

    if not search_path.startswith(current_dir):
        return standard_error("Access denied: Cannot search outside current directory")

    if not os.path.exists(search_path):
        return standard_error(f"Path not found: {path}")

    # Build ripgrep command
    # Using --json for structured output
    args = [
        "rg",
        "--json",  # JSON output for parsing
        f"--max-count={max_results}",  # Limit per file
        "--no-heading",  # No file headers
    ]

    # Case sensitivity
    if not case_sensitive:
        args.append("--ignore-case")

    # File type filter
    if file_type:
        args.append(f"--type={file_type}")

    # Pattern and path
    args.append(pattern)
    args.append(search_path)

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=CODE_SEARCH_TIMEOUT,
            cwd=current_dir,
        )

        # ripgrep returns 1 for no matches (not an error)
        if result.returncode not in (0, 1):
            return standard_error(f"ripgrep failed: {result.stderr}")

        # Parse JSON output
        matches = _parse_rg_json_output(result.stdout)

        # Apply global max_results limit
        total_found = len(matches)
        if len(matches) > max_results:
            matches = matches[:max_results]
            truncated = True
        else:
            truncated = False

        # Convert absolute paths to relative
        for match in matches:
            if match["file"].startswith(current_dir):
                match["file"] = os.path.relpath(match["file"], current_dir)

        return {
            "success": True,
            "pattern": pattern,
            "path": path,
            "file_type": file_type,
            "case_sensitive": case_sensitive,
            "match_count": len(matches),
            "total_found": total_found,
            "truncated": truncated,
            "matches": matches,
        }

    except subprocess.TimeoutExpired:
        return standard_error("Code search timed out after 60 seconds")

    except Exception as e:
        logger.error(f"Error in code search: {e}")
        return standard_error(str(e))


__all__ = ["execute_code_search"]
