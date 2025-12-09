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
All Linting Script v0.1
Runs comprehensive linting checks on all code types in the project.

Dependencies: autopep8, flake8, mypy, vulture, codespell, shellcheck
Install with: pip install autopep8 flake8 mypy vulture codespell && brew install shellcheck
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
    Main linting orchestrator that runs comprehensive checks across the entire project.

    Executes Python linting, shell script validation, configuration checks,
    and project structure validation in sequence.
    """
    print("🔧 All Code Linting v0.1")
    print("=" * 50)

    # Get project root directory
    project_root = Path(__file__).parent.parent.parent

    # Change to project root
    os.chdir(project_root)

    all_passed = True

    # 1. Python linting
    print("\n🐍 Python Files:")
    if not run_command("python tests/lint/lint-python.py", "Python linting"):
        all_passed = False

    # 2. Shell script linting (if shellcheck is available)
    print("\n🐚 Shell Scripts:")
    shell_files = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [
            d
            for d in dirs
            if d
            not in [
                "__pycache__",
                ".git",
                "venv",
                "node_modules",
                "blackcoin-more",
            ]
        ]
        for file in files:
            if file.endswith(".sh") or (file.startswith(".") and "bash" in file):
                shell_files.append(os.path.join(root, file))

    if shell_files:
        try:
            if not run_command(
                "shellcheck " + " ".join(f'"{f}"' for f in shell_files),
                "Shell script linting",
            ):
                all_passed = False
        except Exception:
            print("⚠️ Shellcheck not available, skipping shell script checks")
    else:
        print("ℹ️ No shell scripts found")

    # 3. Configuration file checks
    print("\n⚙️ Configuration Files:")

    # Check .env file exists and is readable
    if os.path.exists(".env"):
        try:
            with open(".env", "r") as f:
                f.read()  # Just check readability
            print("✅ .env file is readable")
        except Exception as e:
            print(f"❌ .env file error: {e}")
            all_passed = False
    else:
        print("⚠️ .env file not found")

    # Check for required files
    required_files = [
        "main.py",
        "gui.py",
        "launcher.py",
        "AGENTS.md",
        "README.md",
        "docs/MIGRATION.md",
    ]
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_passed = False

    # 4. Project structure check
    print("\n📁 Project Structure:")
    expected_dirs = ["venv", "test"]
    for dir_name in expected_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"⚠️ {dir_name}/ directory missing")

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All linting checks passed!")
        return True
    else:
        print("❌ Some checks failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
