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


def run_markdown_lint(directory="docs/", exclude_patterns=None):
    """Run markdown linting on all .md files in the specified directory."""
    print("🔍 Running Markdown linting...")
    
    # Find all markdown files
    md_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    if not md_files:
        print("⚠️ No Markdown files found in", directory)
        return True
    
    print(f"📄 Found {len(md_files)} Markdown files to lint")
    
    # Run pymarkdown scan on all files
    files_arg = " ".join(f'"{f}"' for f in md_files)
    cmd = f"pymarkdown scan {files_arg}"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Markdown linting passed - no issues found")
            return True
        else:
            print("❌ Markdown linting found issues:")
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            return False
            
    except FileNotFoundError:
        print("⚠️ pymarkdownlnt not installed. Install with: pip install pymarkdownlnt")
        return False
    except Exception as e:
        print(f"❌ Error running markdown linting: {e}")
        return False


def main():
    """Main function to run all markdown linting."""
    print("🎯 Starting Markdown Linting Process")
    print("=" * 50)
    
    success = run_markdown_lint()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Markdown linting completed successfully!")
    else:
        print("❌ Markdown linting found issues that need attention.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)