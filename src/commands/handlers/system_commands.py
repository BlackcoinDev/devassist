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
System Commands - Slash commands for system operations.

This module provides command handlers for system-level operations
including code search.
"""

from typing import List
from src.commands.registry import CommandRegistry
from src.tools.executors.system_tools import execute_code_search

__all__ = [
    "handle_search",
    "handle_shell",
]

# =============================================================================
# COMMAND HANDLERS
# =============================================================================


@CommandRegistry.register(
    "search",
    "Search code with ripgrep",
    category="system",
    aliases=["grep", "rg", "find-code"],
)
def handle_search(args: List[str]) -> None:
    """
    Handle /search command for code search using ripgrep.

    Usage:
        /search <pattern>                    - Search for pattern
        /search <pattern> --type py          - Search in Python files
        /search <pattern> --path src/        - Search in specific path
        /search <pattern> --limit 20         - Limit results
        /search <pattern> -i                 - Case-insensitive (default)
        /search <pattern> -s                 - Case-sensitive

    Examples:
        /search "def main"
        /search TODO --type py
        /search "class.*Error" --path src/
    """
    if not args:
        print("\n❌ Usage: /search <pattern> [options]")
        print("\nOptions:")
        print("  --type <ext>    File type (py, js, ts, rs, etc.)")
        print("  --path <dir>    Directory to search")
        print("  --limit <n>     Max results (default: 50)")
        print("  -s, --case      Case-sensitive search")
        print("\nExamples:")
        print("  /search 'def main'")
        print("  /search TODO --type py")
        print("  /search 'class.*Error' --path src/\n")
        return

    # Parse arguments
    pattern = None
    file_type = None
    path = "."
    max_results = 50
    case_sensitive = False

    i = 0
    pattern_parts = []

    while i < len(args):
        arg = args[i]

        if arg in ("--type", "-t") and i + 1 < len(args):
            file_type = args[i + 1]
            i += 2
        elif arg in ("--path", "-p") and i + 1 < len(args):
            path = args[i + 1]
            i += 2
        elif arg in ("--limit", "-l", "-n") and i + 1 < len(args):
            try:
                max_results = int(args[i + 1])
            except ValueError:
                print(f"\n❌ Invalid limit value: {args[i + 1]}\n")
                return
            i += 2
        elif arg in ("--case", "-s", "--case-sensitive"):
            case_sensitive = True
            i += 1
        elif arg in ("-i", "--ignore-case"):
            case_sensitive = False
            i += 1
        else:
            pattern_parts.append(arg)
            i += 1

    if not pattern_parts:
        print("\n❌ Search pattern is required\n")
        return

    pattern = " ".join(pattern_parts)

    # Execute search
    result = execute_code_search(
        pattern=pattern,
        path=path,
        file_type=file_type,
        max_results=max_results,
        case_sensitive=case_sensitive,
    )

    if "error" in result:
        print(f"\n❌ {result['error']}\n")
        return

    matches = result.get("matches", [])
    match_count = result.get("match_count", 0)
    total_found = result.get("total_found", 0)
    truncated = result.get("truncated", False)

    # Display header
    print(f"\n🔍 Search: '{pattern}'")
    if file_type:
        print(f"   Type: {file_type}")
    if path != ".":
        print(f"   Path: {path}")
    print("-" * 70)

    if not matches:
        print("No matches found")
    else:
        # Group matches by file
        current_file = None
        for match in matches:
            file = match.get("file", "")
            line = match.get("line", 0)
            content = match.get("content", "").strip()

            # Truncate long content
            if len(content) > 80:
                content = content[:77] + "..."

            if file != current_file:
                if current_file is not None:
                    print()  # Blank line between files
                print(f"📄 {file}")
                current_file = file

            print(f"   {line:4d}: {content}")

    print("-" * 70)
    if truncated:
        print(f"📊 Showing {match_count} of {total_found} matches (truncated)")
    else:
        print(f"📊 Found {match_count} matches")
    print()


@CommandRegistry.register(
    "shell",
    "Execute shell command (use with caution)",
    category="system",
    aliases=["sh", "exec", "run"],
)
def handle_shell(args: List[str]) -> None:
    """
    Handle /shell command to execute shell commands.

    This command is available but requires confirmation for safety.
    Dangerous commands (rm, sudo, etc.) are blocked.

    Usage:
        /shell <command>

    Examples:
        /shell ls -la
        /shell python --version
        /shell git status
    """
    if not args:
        print("\n❌ Usage: /shell <command>")
        print("\nExamples:")
        print("  /shell ls -la")
        print("  /shell python --version")
        print("  /shell git status")
        print("\n⚠️  Note: Dangerous commands (rm, sudo, etc.) are blocked.\n")
        return

    command = " ".join(args)

    # Import here to avoid circular imports
    from src.tools.executors.shell_tools import execute_shell

    # Check if running in GUI mode
    import os

    if os.getenv("DEVASSIST_INTERFACE", "cli").lower() == "gui":
        print("\n❌ Shell execution is disabled in GUI mode for security.\n")
        return

    print(f"\n⚡ Executing: {command}")
    print("-" * 50)

    result = execute_shell(command)

    if "error" in result:
        print(f"❌ {result['error']}")
    else:
        return_code = result.get("return_code", 0)
        stdout = result.get("stdout", "")
        stderr = result.get("stderr", "")

        if stdout:
            print(stdout.rstrip())

        if stderr:
            print(f"⚠️  stderr: {stderr.rstrip()}")

        if return_code == 0:
            print("-" * 50)
            print("✅ Command completed successfully")
        else:
            print("-" * 50)
            print(f"❌ Command failed with exit code {return_code}")

    print()


__all__ = ["handle_search", "handle_shell"]
