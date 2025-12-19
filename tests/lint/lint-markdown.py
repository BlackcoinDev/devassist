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
Markdown Linting Script v0.1.0
Runs comprehensive linting checks on Markdown files in the project.

Dependencies: pymarkdownlnt
Install with: pip install pymarkdownlnt
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List

# Import shared table utilities
import importlib.util

table_utils_spec = importlib.util.spec_from_file_location(
    "table_utils", os.path.join(os.path.dirname(__file__), "table_utils.py")
)
if table_utils_spec and table_utils_spec.loader:
    table_utils = importlib.util.module_from_spec(table_utils_spec)
    table_utils_spec.loader.exec_module(table_utils)
else:
    # Fallback - shouldn't happen
    raise ImportError("Could not load table_utils module")


def validate_table_alignment(
    table_lines: List[str], start_line: int, file_path: str
) -> List[str]:
    """
    Validate that a table block has properly aligned pipes.

    Args:
        table_lines: Lines containing the table
        start_line: 1-based line number where table starts
        file_path: File path for error reporting

    Returns:
        List of error messages for this table
    """
    if not table_lines:
        return []

    errors = []

    # Parse all rows to determine column structure
    rows = []
    for line in table_lines:
        cells = [cell.strip() for cell in line.split("|")]
        # Remove empty first/last cells from split
        if cells and not cells[0]:
            cells = cells[1:]
        if cells and not cells[-1]:
            cells = cells[:-1]
        rows.append(cells)

    if not rows:
        return []

    # Calculate expected column widths (character-based, not visual)
    num_cols = max(len(row) for row in rows)
    col_widths = [0] * num_cols

    for row in rows:
        for col_idx, cell in enumerate(row):
            if col_idx < num_cols:
                char_width = len(cell)
                col_widths[col_idx] = max(col_widths[col_idx], char_width)

    # Check each table line for proper alignment
    for line_idx, line in enumerate(table_lines):
        line_num = start_line + line_idx

        # Find actual pipe positions
        actual_pipes = []
        for pos, char in enumerate(line):
            if char == "|":
                actual_pipes.append(pos)

        # Calculate expected pipe positions
        expected_pipes = []
        current_pos = 0

        # First pipe at position 0
        expected_pipes.append(0)
        current_pos += 1  # After first |

        # Add positions for each column
        for col_idx in range(num_cols):
            # Content width + space before + space after + |
            current_pos += 1  # space before content
            current_pos += col_widths[col_idx]  # content
            current_pos += 1  # space after content
            expected_pipes.append(current_pos)
            current_pos += 1  # after |

        # Check if pipes match (allowing for reasonable tolerance)
        if len(actual_pipes) != len(expected_pipes):
            errors.append(
                f"{file_path}:{line_num}: MD060 Table column alignment violation - "
                f"incorrect number of pipes (expected {len(expected_pipes)}, found {len(actual_pipes)})"
            )
            continue

        # Check individual pipe positions (allow 1-character tolerance)
        max_tolerance = 1
        misaligned = False
        for expected, actual in zip(expected_pipes, actual_pipes):
            if abs(expected - actual) > max_tolerance:
                misaligned = True
                break

        if misaligned:
            errors.append(
                f"{file_path}:{line_num}: MD060 Table column alignment violation - pipes misaligned"
            )
            errors.append(
                f"{file_path}:{line_num}: Expected pipe positions: {expected_pipes}"
            )
            errors.append(
                f"{file_path}:{line_num}: Actual pipe positions: {actual_pipes}"
            )
            errors.append(
                f"{file_path}:{line_num}: 💡 Fix with: python tests/lint/fix-markdown.py {file_path}"
            )

    return errors


def run_markdown_lint(directory=".", exclude_patterns=None):
    """Run markdown linting on all .md files in the specified directory."""
    print("🔍 Running Markdown linting...")

    # Find all markdown files
    md_files = []
    if os.path.isfile(directory):
        # If directory is actually a file, lint just that file
        if directory.endswith(".md"):
            md_files = [directory]
    else:
        # Directory traversal - exclude directories like Python linting does
        for root, dirs, files in os.walk(directory):
            # Skip certain directories (same as Python linting)
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
                    ".pytest_cache",
                ]
            ]
            for file in files:
                if file.endswith(".md"):
                    md_files.append(os.path.join(root, file))

    if not md_files:
        print("⚠️ No Markdown files found in", directory)
        return True

    print(f"📄 Found {len(md_files)} Markdown files to lint")

    all_passed = True
    all_md060_errors = []

    # 1. Run MD060 table alignment checks first
    print("\n📊 Checking MD060 table column alignment...")
    for md_file in md_files:
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            md060_errors = table_utils.check_md060_compliance(content, md_file)
            if md060_errors:
                all_md060_errors.extend(md060_errors)
                all_passed = False

        except Exception as e:
            print(f"❌ Error reading {md_file}: {e}")
            all_passed = False

    if all_md060_errors:
        print("❌ MD060 table alignment violations found:")
        for error in all_md060_errors:
            print(f"  {error}")
    else:
        print("✅ MD060 table alignment check passed")

    # 2. Run pymarkdown scan on all files
    # Separate files by directory for different config files
    docs_files = [f for f in md_files if "/docs/" in f or f.startswith("docs/")]
    other_files = [f for f in md_files if not ("/docs/" in f or f.startswith("docs/"))]

    pymarkdown_errors = []

    # Process docs/ files with docs config (higher line length)
    if docs_files:
        files_arg = " ".join(f'"{f}"' for f in docs_files)
        cmd = f"pymarkdown --config .pymarkdown-docs scan {files_arg}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                pymarkdown_errors.append(result.stdout)
            if result.stderr:
                pymarkdown_errors.append(f"Errors: {result.stderr}")
        except FileNotFoundError:
            pymarkdown_errors.append("pymarkdown not found")
        except Exception as e:
            pymarkdown_errors.append(f"Error processing docs files: {e}")

    # Process other files with main config
    if other_files:
        files_arg = " ".join(f'"{f}"' for f in other_files)
        cmd = f"pymarkdown --config .pymarkdown scan {files_arg}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                pymarkdown_errors.append(result.stdout)
            if result.stderr:
                pymarkdown_errors.append(f"Errors: {result.stderr}")
        except FileNotFoundError:
            pymarkdown_errors.append("pymarkdown not found")
        except Exception as e:
            pymarkdown_errors.append(f"Error processing other files: {e}")

    # Handle results
    if pymarkdown_errors and any(
        "pymarkdown not found" in error for error in pymarkdown_errors
    ):
        print(
            "\n⚠️ pymarkdownlnt not installed. Install with: pip install pymarkdownlnt"
        )
        all_passed = False
    elif pymarkdown_errors:
        all_passed = False
        print("\n❌ PyMarkdown linting found issues:")
        for error in pymarkdown_errors:
            if error.strip():
                print(error)
    else:
        print("\n✅ PyMarkdown linting passed - no issues found")

    return all_passed

    return all_passed


def main():
    """Main function to run all markdown linting."""
    print("🎯 Starting Markdown Linting Process")
    print("=" * 50)

    # Handle command line arguments
    import argparse

    parser = argparse.ArgumentParser(
        description="Lint Markdown files for style and MD060 compliance"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Directories or files to lint (default: entire project)",
    )
    args = parser.parse_args()

    # Lint all specified paths
    all_success = True
    for path in args.paths:
        print(f"\n📁 Linting: {path}")
        success = run_markdown_lint(path)
        if not success:
            all_success = False

    print("\n" + "=" * 50)
    if all_success:
        print("🎉 Markdown linting completed successfully!")
    else:
        print("❌ Markdown linting found issues that need attention.")

    return all_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
