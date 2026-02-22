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
Ground truth extraction from codebase.
Used by documentation validation and CI/CD.
"""

import subprocess
from pathlib import Path
import re


def get_test_count() -> int:
    """Return actual test count from pytest."""
    try:
        result = subprocess.run(
            ["uv", "run", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            raise RuntimeError(f"pytest failed: {result.stderr}")

        # Parse output to extract test count
        # Look for patterns like "735 items" or "735 tests collected"
        output = result.stdout

        # Try to find number patterns
        match = re.search(r"(\d+) (?:items|tests collected)", output)
        if match:
            return int(match.group(1))

        # Fallback: count "<Module" or "<Function" lines
        lines = output.split("\n")
        count = 0
        for line in lines:
            if "<Module" in line or "<Function" in line:
                count += 1

        return count if count > 0 else 0

    except (subprocess.TimeoutExpired, RuntimeError, Exception) as e:
        print(f"Warning: Could not get test count: {e}")
        return 0


def get_handler_count() -> int:
    """Return count of registered slash commands.

    Counts @CommandRegistry.register decorators in handler files.
    """
    handlers_dir = Path("src/commands/handlers")
    if not handlers_dir.exists():
        return 0

    count = 0
    for file in handlers_dir.iterdir():
        if file.is_file() and file.name.endswith(".py") and file.name != "__init__.py":
            try:
                content = file.read_text()
                # Count @CommandRegistry.register decorators
                count += content.count("@CommandRegistry.register")
            except Exception:
                pass

    return count


def get_tool_count() -> int:
    """Return count of registered AI tools.

    Counts @ToolRegistry.register decorators in executor files.
    """
    tools_dir = Path("src/tools/executors")
    if not tools_dir.exists():
        return 0

    count = 0
    for file in tools_dir.iterdir():
        if file.is_file() and file.name.endswith(".py") and file.name != "__init__.py":
            try:
                content = file.read_text()
                # Count @ToolRegistry.register decorators
                count += content.count("@ToolRegistry.register")
            except Exception:
                pass

    return count


def get_module_count() -> int:
    """Return count of src/ subdirectories."""
    src_dir = Path("src")
    if not src_dir.exists():
        return 0

    count = 0
    for item in src_dir.iterdir():
        if item.is_dir() and not item.name.startswith("_"):
            count += 1

    return count


def get_env_vars() -> list[str]:
    """Return list of environment variable names from .env.example."""
    env_example = Path(".env.example")
    if not env_example.exists():
        return []

    env_vars = []
    try:
        content = env_example.read_text()
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                var_name = line.split("=", 1)[0].strip()
                env_vars.append(var_name)

    except Exception as e:
        print(f"Warning: Could not read .env.example: {e}")

    return env_vars


def get_all_facts() -> dict:
    """Return all ground truth data as a dictionary."""
    return {
        "test_count": get_test_count(),
        "handler_count": get_handler_count(),
        "tool_count": get_tool_count(),
        "module_count": get_module_count(),
        "env_vars": get_env_vars(),
    }
