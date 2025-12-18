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
Markdown Auto-Fix Script v0.1.0
Attempts to automatically fix common markdown linting issues.

Note: Some issues require manual review and fixing.
"""

import re
import os
from pathlib import Path


def fix_markdown_file(file_path):
    """Fix common markdown issues in a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix 1: Add blank lines after headings (MD022)
    # Pattern: heading followed by non-blank line
    content = re.sub(r'(###? .+?)\n([^\n])', r'\1\n\n\2', content)
    
    # Fix 2: Add language to code blocks (MD040)
    # Pattern: ``` without language
    content = re.sub(r'```\n([^`]+)\n```', r'```text\n\1\n```', content)
    
    # Fix 3: Add blank lines around code blocks (MD031)
    # Pattern: text followed by code block without blank line
    content = re.sub(r'([^\n])\n```', r'\1\n\n```', content)
    content = re.sub(r'```\n([^\n])', r'```\n\n\1', content)
    
    # Fix 4: Wrap long lines (MD013) - basic approach
    lines = content.split('\n')
    wrapped_lines = []
    for line in lines:
        if len(line) > 80 and not line.startswith(('|', '`', '#', '-')):
            # Simple wrapping for non-table, non-code, non-heading lines
            words = line.split(' ')
            if len(words) > 1:
                current_line = words[0]
                for word in words[1:]:
                    if len(current_line) + len(word) + 1 <= 80:
                        current_line += ' ' + word
                    else:
                        wrapped_lines.append(current_line)
                        current_line = word
                wrapped_lines.append(current_line)
            else:
                wrapped_lines.append(line)
        else:
            wrapped_lines.append(line)
    content = '\n'.join(wrapped_lines)
    
    # Only write if we made changes
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False


def main():
    """Fix markdown issues in all documentation files."""
    print("🔧 Auto-Fixing Markdown Issues")
    print("=" * 50)
    
    fixed_files = 0
    total_files = 0
    
    # Process all markdown files
    for root, dirs, files in os.walk("docs/"):
        for file in files:
            if file.endswith('.md'):
                total_files += 1
                file_path = os.path.join(root, file)
                print(f"📄 Processing {file_path}...")
                
                if fix_markdown_file(file_path):
                    fixed_files += 1
                    print(f"✅ Fixed issues in {file_path}")
                else:
                    print(f"⚠️ No auto-fixable issues in {file_path}")
    
    print(f"\n📊 Results:")
    print(f"   Files processed: {total_files}")
    print(f"   Files modified: {fixed_files}")
    print(f"   Files unchanged: {total_files - fixed_files}")
    
    if fixed_files > 0:
        print(f"\n🎉 Successfully auto-fixed {fixed_files} files!")
        print("Note: Some issues may require manual fixing.")
    else:
        print(f"\n⚠️ No auto-fixable issues found.")
        print("All remaining issues require manual review.")


if __name__ == "__main__":
    main()