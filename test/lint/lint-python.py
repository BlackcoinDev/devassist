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
Python Linting Script v0.1
Runs comprehensive linting checks on Python files in the project.

Dependencies: flake8, mypy, vulture, codespell
Install with: pip install flake8 mypy vulture codespell

Usage: python test/lint/lint-python.py
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🔍 Running {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} passed")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def main():
    """
    Main Python linting function that runs comprehensive checks on all Python files.

    Performs syntax validation, style checking, type checking, dead code detection,
    and spell checking across all Python files in the project.
    """
    print("🐍 Python Code Linting v0.1")
    print("=" * 50)

    # Get project root directory
    project_root = Path(__file__).parent.parent.parent

    # Change to project root
    os.chdir(project_root)

    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk("."):
        # Skip certain directories
        dirs[:] = [
            d
            for d in dirs
            if d
            not in [
                "__pycache__",
                ".git",
                "venv",
                "node_modules",
                "faiss_index",
                "chroma_data",
                "blackcoin-more",
            ]
        ]
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    if not python_files:
        print("❌ No Python files found!")
        return False

    print(f"📁 Found {len(python_files)} Python files to lint")

    # Run linting tools
    all_passed = True

    # 1. Syntax check with Python compiler
    if not run_command(
        "python3 -m py_compile " + " ".join(f'"{f}"' for f in python_files),
        "Python syntax check",
    ):
        all_passed = False

    # 2. Flake8 (style and error checking)
    if not run_command(
        "flake8 --max-line-length=150 --extend-ignore=E203,W503,F541 "
        + " ".join(f'"{f}"' for f in python_files),
        "Flake8 style check",
    ):
        all_passed = False

    # 3. MyPy (type checking) - if available
    try:
        import mypy  # noqa: F401

        if not run_command(
            "mypy --ignore-missing-imports " + " ".join(f'"{f}"' for f in python_files),
            "MyPy type check",
        ):
            all_passed = False
    except ImportError:
        print("⚠️ MyPy not installed, skipping type checking")

    # 4. Vulture (dead code detection) - if available
    try:
        import vulture  # noqa: F401

        result = subprocess.run(
            "vulture " + " ".join(f'"{f}"' for f in python_files),
            shell=True,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            # Check if the errors are just the known false positives
            error_lines = result.stdout.strip().split("\n")
            real_issues = [
                line
                for line in error_lines
                if not ("closeEvent" in line or "_default_params" in line)
            ]
            if real_issues:
                print("❌ Vulture found real dead code issues:")
                for issue in real_issues[:5]:  # Show first 5
                    print(f"   {issue}")
                all_passed = False
            else:
                print(
                    "✅ Vulture check passed (only false positives for framework overrides)"
                )
        else:
            print("✅ Vulture dead code check passed")
    except ImportError:
        print("⚠️ Vulture not installed, skipping dead code check")

    # 5. Codespell (spell checking) - if available
    try:
        import codespell_lib  # noqa: F401

        if not run_command(
            "codespell " + " ".join(f'"{f}"' for f in python_files),
            "Codespell spell check",
        ):
            all_passed = False
    except ImportError:
        print("⚠️ Codespell not installed, skipping spell check")

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All Python linting checks passed!")
        return True
    else:
        print("❌ Some linting checks failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
