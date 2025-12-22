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
Project Linting Script v1.0.0
Runs comprehensive linting checks on all code in the project.

Dependencies: autopep8, flake8, mypy, vulture, codespell, bandit, shellcheck
Install with: pip install autopep8 flake8 mypy vulture codespell bandit && brew install shellcheck
"""

import os
import sys
import subprocess
import re
from pathlib import Path

# Directories to exclude from linting
EXCLUDED_DIRS = {
    "__pycache__",
    ".git",
    "venv",
    "node_modules",
    "faiss_index",
    "chroma_data",
    "blackcoin-more",
    ".pytest_cache",
}

# Required project files
REQUIRED_FILES = [
    "src/main.py",
    "src/gui.py",
    "launcher.py",
    "AGENTS.md",
    "README.md",
    "docs/MIGRATION.md",
]

# Expected project directories
EXPECTED_DIRS = ["venv", "tests"]


def run_command(cmd: str, description: str) -> bool:
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


def find_files(extension: str) -> list[str]:
    """Find all files with given extension, excluding certain directories."""
    files = []
    for root, dirs, filenames in os.walk("."):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for filename in filenames:
            if filename.endswith(extension):
                files.append(os.path.join(root, filename))
    return files


def find_shell_files() -> list[str]:
    """Find all shell script files."""
    files = []
    for root, dirs, filenames in os.walk("."):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for filename in filenames:
            if filename.endswith(".sh") or (
                filename.startswith(".") and "bash" in filename
            ):
                files.append(os.path.join(root, filename))
    return files


def lint_python(files: list[str]) -> bool:
    """Run all Python linting checks."""
    if not files:
        print("❌ No Python files found!")
        return False

    print(f"📁 Found {len(files)} Python files to lint")
    all_passed = True
    files_arg = " ".join(f'"{f}"' for f in files)

    # 1. Syntax check
    if not run_command(f"python3 -m py_compile {files_arg}", "Python syntax check"):
        all_passed = False

    # 2. Flake8
    if not run_command(
        f"flake8 --max-line-length=150 --extend-ignore=E203,W503,F541 {files_arg}",
        "Flake8 style check",
    ):
        all_passed = False

    # 3. Autopep8
    result = subprocess.run(
        f"autopep8 --diff --max-line-length=150 {files_arg}",
        shell=True,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and not result.stdout.strip():
        print("✅ Autopep8 formatting check passed")
    else:
        print("❌ Autopep8 found formatting issues:")
        print(result.stdout[:2000] if len(result.stdout) > 2000 else result.stdout)
        all_passed = False

    # 4. MyPy
    if not run_command(f"mypy --ignore-missing-imports {files_arg}", "MyPy type check"):
        all_passed = False

    # 4.5. Bandit Security Check
    if not run_command(f"bandit -r {files_arg} -c .bandit", "Bandit security check"):
        all_passed = False

    # 5. Vulture
    result = subprocess.run(
        f"vulture {files_arg} --ignore-decorators=register,patch,fixture",
        shell=True,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        error_lines = result.stdout.strip().split("\n")
        real_issues = [
            line
            for line in error_lines
            if not (
                "closeEvent" in line
                or "_default_params" in line
                or "handle_" in line
                or "execute_" in line
                or "handler" in line
                or "mock_" in line
                or re.search(r"\bh[0-9]\b", line)  # h1, h2, h3, etc.
            )
        ]
        if real_issues:
            print("❌ Vulture found dead code issues:")
            for issue in real_issues[:5]:
                print(f"   {issue}")
            all_passed = False
        else:
            print("✅ Vulture check passed (only false positives)")
    else:
        print("✅ Vulture dead code check passed")

    # 6. Codespell
    if not run_command(f"codespell {files_arg}", "Codespell spell check"):
        all_passed = False

    return all_passed


def lint_shell(files: list[str]) -> bool:
    """Run shell script linting."""
    if not files:
        print("ℹ️ No shell scripts found")
        return True

    print(f"📁 Found {len(files)} shell scripts to lint")
    files_arg = " ".join(f'"{f}"' for f in files)

    try:
        return run_command(f"shellcheck {files_arg}", "Shell script linting")
    except Exception:
        print("⚠️ Shellcheck not available, skipping")
        return True


def validate_structure() -> bool:
    """Validate required files and project structure."""
    all_passed = True

    print("\n📋 Required Files:")
    for file in REQUIRED_FILES:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_passed = False

    print("\n📁 Project Structure:")
    for dir_name in EXPECTED_DIRS:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"⚠️ {dir_name}/ directory missing")

    return all_passed


def main() -> bool:
    """Main function to run all linting checks."""
    print("🔧 Project Linting v1.0.0")
    print("=" * 50)

    # Change to project root
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)

    all_passed = True

    # 1. Python linting
    print("\n🐍 Python Files:")
    python_files = find_files(".py")
    if not lint_python(python_files):
        all_passed = False

    # 2. Shell script linting
    print("\n🐚 Shell Scripts:")
    shell_files = find_shell_files()
    if not lint_shell(shell_files):
        all_passed = False

    # 3. Structure validation
    if not validate_structure():
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All linting checks passed!")
    else:
        print("❌ Some checks failed. Please review the issues above.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
