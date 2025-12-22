#!/usr/bin/env python3
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
Git Commands - Slash commands for git operations.

This module provides command handlers for git repository operations
including status, log, and diff.
"""

from typing import List
from src.commands.registry import CommandRegistry
from src.tools.executors.git_tools import (
    execute_git_status,
    execute_git_diff,
    execute_git_log,
)

# =============================================================================
# COMMAND HANDLERS
# =============================================================================


@CommandRegistry.register(
    "git-status",
    "Show git repository status",
    category="git",
    aliases=["gs", "status"]
)
def handle_git_status(args: List[str]) -> None:
    """Handle /git-status command to show repository status."""
    result = execute_git_status()

    if "error" in result:
        print(f"\n❌ {result['error']}\n")
        return

    branch = result.get("branch", "unknown")
    is_clean = result.get("is_clean", False)
    staged = result.get("staged", [])
    unstaged = result.get("unstaged", [])
    untracked = result.get("untracked", [])

    print(f"\n🌿 Branch: {branch}")
    print("-" * 50)

    if is_clean:
        print("✅ Working tree is clean")
    else:
        if staged:
            print(f"\n📦 Staged ({len(staged)}):")
            for file in staged[:10]:  # Limit display
                print(f"   {file}")
            if len(staged) > 10:
                print(f"   ... and {len(staged) - 10} more")

        if unstaged:
            print(f"\n📝 Unstaged ({len(unstaged)}):")
            for file in unstaged[:10]:
                print(f"   {file}")
            if len(unstaged) > 10:
                print(f"   ... and {len(unstaged) - 10} more")

        if untracked:
            print(f"\n❓ Untracked ({len(untracked)}):")
            for file in untracked[:10]:
                print(f"   {file}")
            if len(untracked) > 10:
                print(f"   ... and {len(untracked) - 10} more")

    print("-" * 50)
    print(f"📊 Summary: {len(staged)} staged, {len(unstaged)} unstaged, {len(untracked)} untracked\n")


@CommandRegistry.register(
    "git-log",
    "Show git commit history",
    category="git",
    aliases=["gl", "log"]
)
def handle_git_log(args: List[str]) -> None:
    """
    Handle /git-log command to show commit history.

    Usage:
        /git-log [limit] [file]
        /git-log 20
        /git-log 5 src/main.py
    """
    limit = 10
    file_path = None

    # Parse arguments
    if args:
        # First arg could be a number (limit) or a file path
        try:
            limit = int(args[0])
            if len(args) > 1:
                file_path = " ".join(args[1:])
        except ValueError:
            # First arg is a file path
            file_path = " ".join(args)

    result = execute_git_log(limit=limit, file_path=file_path)

    if "error" in result:
        print(f"\n❌ {result['error']}\n")
        return

    commits = result.get("commits", [])
    commit_count = result.get("commit_count", 0)

    if file_path:
        print(f"\n📜 Commit History for: {file_path}")
    else:
        print("\n📜 Commit History")
    print("-" * 70)

    if not commits:
        print("No commits found")
    else:
        for commit in commits:
            hash_short = commit.get("hash", "???????")
            author = commit.get("author", "Unknown")
            date = commit.get("date", "")
            message = commit.get("message", "")

            # Truncate long messages
            if len(message) > 50:
                message = message[:47] + "..."

            print(f"  {hash_short} | {date} | {author[:15]:<15} | {message}")

    print("-" * 70)
    print(f"📊 Showing {commit_count} commits\n")


@CommandRegistry.register(
    "git-diff",
    "Show git diff",
    category="git",
    aliases=["gd", "diff"]
)
def handle_git_diff(args: List[str]) -> None:
    """
    Handle /git-diff command to show changes.

    Usage:
        /git-diff              - Show unstaged changes
        /git-diff --staged     - Show staged changes
        /git-diff file.py      - Show changes for specific file
        /git-diff --staged file.py
    """
    staged = False
    file_path = None

    # Parse arguments
    remaining_args = []
    for arg in args:
        if arg in ("--staged", "-s", "--cached"):
            staged = True
        else:
            remaining_args.append(arg)

    if remaining_args:
        file_path = " ".join(remaining_args)

    result = execute_git_diff(file_path=file_path, staged=staged)

    if "error" in result:
        print(f"\n❌ {result['error']}\n")
        return

    has_changes = result.get("has_changes", False)
    diff_type = "Staged" if staged else "Unstaged"

    if file_path:
        print(f"\n📝 {diff_type} Changes for: {file_path}")
    else:
        print(f"\n📝 {diff_type} Changes")
    print("-" * 50)

    if not has_changes:
        print(result.get("message", "No changes"))
    else:
        diff_content = result.get("diff", "")
        truncated = result.get("truncated", False)

        # Print diff with some basic colorization hints
        for line in diff_content.split("\n")[:100]:  # Limit lines
            if line.startswith("+") and not line.startswith("+++"):
                print(f"  {line}")  # Added lines
            elif line.startswith("-") and not line.startswith("---"):
                print(f"  {line}")  # Removed lines
            elif line.startswith("@@"):
                print(f"  {line}")  # Hunk headers
            else:
                print(f"  {line}")

        if truncated or diff_content.count("\n") > 100:
            print("  ... (output truncated)")

    print("-" * 50)
    print()


__all__ = ["handle_git_status", "handle_git_log", "handle_git_diff"]
