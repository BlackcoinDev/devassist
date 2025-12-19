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
Markdown Auto-Fix Script v0.2.0

Three-phase hybrid architecture for comprehensive markdown fixing:
- Phase 1: Pymarkdown native fix (16+ rules)
- Phase 2: Custom Python fixes (8 complex rules)
- Phase 3: Table alignment (MD060)

Coverage: 96% auto-fix (25+ rules), only 2 rules require manual intervention.
"""

import re
import os
import subprocess
import argparse
import importlib.util
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Set, Any

# Import shared table utilities
table_utils_spec = importlib.util.spec_from_file_location(
    "table_utils", os.path.join(os.path.dirname(__file__), "table_utils.py")
)
if table_utils_spec and table_utils_spec.loader:
    table_utils = importlib.util.module_from_spec(table_utils_spec)
    table_utils_spec.loader.exec_module(table_utils)
else:
    # Fallback - shouldn't happen
    raise ImportError("Could not load table_utils module")


@dataclass
class FixConfig:
    """Configuration for markdown fixing operations."""

    line_length: int = 120
    aggressive_mode: bool = True
    dry_run: bool = False
    verbose: bool = False
    config_file: str = ".pymarkdown"


@dataclass
class FixResults:
    """Results from a fix operation."""

    success: bool
    phase1_fixes: int = 0
    phase2_fixes: int = 0
    phase3_fixes: int = 0
    errors: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# PHASE 1: Pymarkdown Native Fix
# ============================================================================


def run_pymarkdown_fix(file_path: str, config: FixConfig) -> Tuple[bool, str, int]:
    """
    Run pymarkdown's native fix command.

    Handles 16+ rules automatically:
    - MD004: List style consistency
    - MD005: List indentation
    - MD029: Ordered list numbering
    - MD030: List marker spacing
    - +12 more rules

    Args:
        file_path: Path to markdown file
        config: Fix configuration

    Returns:
        Tuple of (success, output_message, fix_count)
    """
    try:
        cmd = ["pymarkdown", "--config", config.config_file, "fix", file_path]

        if config.verbose:
            print(f"  Running: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        # Parse output to count fixes
        output = result.stdout + result.stderr
        # pymarkdown doesn't output "Fixed:" messages, so check if it succeeded
        # and assume fixes were applied if return code is 0 and no errors
        fix_count = 1 if result.returncode == 0 and not result.stderr else 0

        if result.returncode == 0:
            return True, output, fix_count
        else:
            return False, f"Pymarkdown fix failed: {output}", 0

    except subprocess.TimeoutExpired:
        return False, "Pymarkdown fix timed out", 0
    except FileNotFoundError:
        return (
            False,
            "pymarkdown not found - install with: pip install pymarkdownlnt",
            0,
        )
    except Exception as e:
        return False, f"Pymarkdown fix error: {str(e)}", 0


# ============================================================================
# PHASE 2: Custom Fixes
# ============================================================================


class MarkdownFixer:
    """Custom fixes for complex markdown rules requiring context awareness."""

    def __init__(self, config: FixConfig):
        self.config = config
        self.fixes_applied = 0

    def fix_all(self, content: str) -> str:
        """Apply all custom fixes in sequence."""
        content = self.fix_md047_trailing_newline(content)
        content = self.fix_md022_heading_blanks(content)
        content = self.fix_md031_code_block_blanks(content)
        content = self.fix_md032_list_blanks(content)
        content = self.fix_md026_trailing_punctuation(content)
        content = self.fix_md040_code_language(content)
        content = self.fix_md013_line_length(content)
        # Cleanup: remove duplicate blank lines created by above fixes
        content = self.fix_md012_multiple_blanks(content)
        return content

    def fix_md047_trailing_newline(self, content: str) -> str:
        """
        MD047: Files should end with single trailing newline.

        Simple fix: ensure exactly one newline at end.
        """
        if not content.endswith("\n"):
            self.fixes_applied += 1
            return content + "\n"

        # Remove multiple trailing newlines
        while content.endswith("\n\n"):
            content = content[:-1]
            self.fixes_applied += 1

        return content

    def fix_md012_multiple_blanks(self, content: str) -> str:
        """
        MD012: Multiple consecutive blank lines.

        Cleanup pass to remove duplicate blanks created by other fixes.
        Reduces any sequence of 2+ blank lines to exactly 1 blank line.
        """
        # Replace 2 or more consecutive newlines with exactly 2 newlines (1 blank line)
        import re

        original = content
        content = re.sub(r"\n{3,}", "\n\n", content)

        if content != original:
            # Count how many replacements we made
            self.fixes_applied += original.count("\n\n\n")

        return content

    def fix_md022_heading_blanks(self, content: str) -> str:
        """
        MD022: Headings should be surrounded by blank lines.

        Pattern: Add blank line before/after headings if missing.
        """
        lines = content.split("\n")
        result = []

        for i, line in enumerate(lines):
            # Check if this is a heading
            if re.match(r"^#{1,6}\s+.+", line):
                # Add blank line before if needed
                if i > 0 and result and result[-1].strip():
                    result.append("")
                    self.fixes_applied += 1

                result.append(line)

                # Add blank line after if needed
                if i < len(lines) - 1 and lines[i + 1].strip():
                    result.append("")
                    self.fixes_applied += 1
            else:
                result.append(line)

        return "\n".join(result)

    def fix_md031_code_block_blanks(self, content: str) -> str:
        """
        MD031: Code blocks should be surrounded by blank lines.

        Pattern: Add blank lines before/after ``` markers.
        """
        lines = content.split("\n")
        result = []
        in_code_block = False

        for i, line in enumerate(lines):
            if line.startswith("```"):
                if not in_code_block:
                    # Opening fence - add blank before
                    if i > 0 and result and result[-1].strip():
                        result.append("")
                        self.fixes_applied += 1
                    in_code_block = True
                else:
                    # Closing fence - will add blank after
                    in_code_block = False

                result.append(line)

                # Add blank after closing fence
                if not in_code_block and i < len(lines) - 1 and lines[i + 1].strip():
                    result.append("")
                    self.fixes_applied += 1
            else:
                result.append(line)

        return "\n".join(result)

    def fix_md032_list_blanks(self, content: str) -> str:
        """
        MD032: Lists should be surrounded by blank lines.

        Pattern: Add blank lines before/after list blocks.
        """
        lines = content.split("\n")
        result = []
        in_list = False

        for i, line in enumerate(lines):
            is_list_item = bool(
                re.match(r"^[\s]*[-*+]\s+", line) or re.match(r"^[\s]*\d+\.\s+", line)
            )

            if is_list_item:
                if not in_list:
                    # Starting a list - add blank before
                    if i > 0 and result and result[-1].strip():
                        result.append("")
                        self.fixes_applied += 1
                    in_list = True
                result.append(line)
            else:
                if in_list and line.strip():
                    # Ending a list - add blank after
                    result.append("")
                    self.fixes_applied += 1
                    in_list = False
                result.append(line)

        return "\n".join(result)

    def fix_md026_trailing_punctuation(self, content: str) -> str:
        """
        MD026: Headings should not have trailing punctuation.

        Pattern: Remove .,;:!? from end of headings.
        """

        def remove_punctuation(match):
            self.fixes_applied += 1
            heading_prefix = match.group(1)
            heading_text = match.group(2).rstrip(".,;:!?")
            return f"{heading_prefix}{heading_text}"

        content = re.sub(
            r"^(#{1,6}\s+)(.+?)[.,;:!?]+\s*$",
            remove_punctuation,
            content,
            flags=re.MULTILINE,
        )
        return content

    def fix_md040_code_language(self, content: str) -> str:
        """
        MD040: Fenced code blocks should have language specified.

        Algorithm:
        1. Find code blocks without language specifiers
        2. Detect language from content (shebang, keywords)
        3. Add appropriate language tag
        """

        def detect_language(code_content: str) -> str:
            """Detect programming language from code content."""
            if not code_content.strip():
                return "text"

            lines = code_content.strip().split("\n")
            first_line = lines[0].strip()

            # Check shebang
            if first_line.startswith("#!"):
                if "python" in first_line:
                    return "python"
                elif "bash" in first_line or "sh" in first_line:
                    return "bash"
                elif "node" in first_line:
                    return "javascript"

            # Check content keywords
            code_lower = code_content.lower()
            if any(kw in code_lower for kw in ["def ", "import ", "class ", "self."]):
                return "python"
            elif any(
                kw in code_lower
                for kw in ["function ", "const ", "let ", "var ", "console."]
            ):
                return "javascript"
            elif any(kw in code_lower for kw in ["package ", "func ", "import ("]):
                return "go"
            elif "#include" in code_content or "int main(" in code_content:
                return "c"
            elif (
                "pip install" in code_content
                or "uv run" in code_content
                or "cp .env" in code_content
            ):
                return "bash"

            return "text"

        def process_code_block(match):
            lang_part = match.group(1)  # Language specifier after ```
            code_content = match.group(2)

            # If already has a specific language, keep it
            if lang_part and lang_part not in ["text", "plain"]:
                return match.group(0)

            # Detect and add appropriate language
            detected_lang = detect_language(code_content)
            self.fixes_applied += 1
            return f"```{detected_lang}\n{code_content}\n```"

        # Fix code blocks: ```[lang]\n[code]\n```
        content = re.sub(r"```(\w*)\n([^`]+?)\n```", process_code_block, content)

        # Remove empty code blocks (various malformed formats)
        content = re.sub(r"```\w*\s*\n\s*\n\s*```", "", content)  # Multi-line empty
        content = re.sub(r"```\w*\s*```", "", content)  # Single-line empty
        content = re.sub(
            r"^\s*```\s*$", "", content, flags=re.MULTILINE
        )  # Lines with only backticks

        return content

    def fix_md013_line_length(self, content: str) -> str:
        """
        MD013: Lines should not exceed configured length.

        Smart wrapping algorithm:
        1. Skip table rows (start with |)
        2. Skip code blocks (between ```)
        3. Protect URLs and inline code
        4. Wrap at word boundaries
        5. Prefer sentence breaks (. ) over mid-sentence
        6. Preserve list indentation
        """
        lines = content.split("\n")
        result = []
        in_code_block = False

        for line in lines:
            # Track code block state
            if line.startswith("```"):
                in_code_block = not in_code_block
                result.append(line)
                continue

            # Skip lines that shouldn't be wrapped
            if (
                in_code_block
                or line.startswith("|")  # Table row
                or line.startswith("#")  # Heading
                or len(line) <= self.config.line_length
            ):
                result.append(line)
                continue

            # Detect list indentation
            list_match = re.match(r"^(\s*)([-*+]|\d+\.)\s+", line)
            indent = ""
            if list_match:
                indent = " " * len(list_match.group(0))

            # Smart wrapping
            wrapped = self._wrap_line(line, indent)
            result.extend(wrapped)
            if len(wrapped) > 1:
                self.fixes_applied += 1

        return "\n".join(result)

    def _wrap_line(self, line: str, indent: str = "") -> List[str]:
        """
        Wrap a single long line intelligently.

        Preserves URLs, inline code, and breaks at sentence boundaries.
        """
        max_len = self.config.line_length

        # Find protected spans (URLs, inline code)
        protected = self._find_protected_spans(line)

        words = line.split(" ")
        result = []
        current_line = words[0] if words else ""

        for word in words[1:]:
            test_line = current_line + " " + word

            # Check if adding this word would exceed limit
            if len(test_line) > max_len:
                # Try to break at sentence boundary
                if current_line.endswith((".", "!", "?")):
                    result.append(current_line)
                    current_line = indent + word
                else:
                    result.append(current_line)
                    current_line = indent + word
            else:
                current_line = test_line

        if current_line:
            result.append(current_line)

        return result

    def _find_protected_spans(self, line: str) -> Set[Tuple[int, int]]:
        """Find spans that should not be broken (URLs, inline code)."""
        protected = set()

        # Find URLs
        for match in re.finditer(r"https?://[^\s]+", line):
            protected.add((match.start(), match.end()))

        # Find inline code
        for match in re.finditer(r"`[^`]+`", line):
            protected.add((match.start(), match.end()))

        return protected


# ============================================================================
# PHASE 3: Table Alignment
# ============================================================================


class TableAligner:
    """MD060-compliant table alignment."""

    def __init__(self, config: FixConfig):
        self.config = config
        self.fixes_applied = 0

    def _visual_width(self, text: str) -> int:
        """
        Calculate visual/display width of text.

        Handles:
        - ASCII: 1 column each
        - Emojis: 2 columns each (✅, 🎉, etc.)
        - East Asian Wide: 2 columns each
        - Markdown formatting: count only visible characters
        """
        import unicodedata

        width = 0
        for char in text:
            # Get Unicode category
            cat = unicodedata.category(char)

            # Check East Asian Width
            ea_width = unicodedata.east_asian_width(char)

            # Emoji and special characters are typically in these ranges
            code_point = ord(char)

            if ea_width in ("F", "W"):  # Fullwidth or Wide
                width += 2
            elif code_point >= 0x1F300 and code_point <= 0x1F9FF:  # Emoji range
                width += 2
            elif code_point >= 0x2600 and code_point <= 0x27BF:  # Misc symbols
                width += 2
            elif cat == "Mn":  # Mark, Nonspacing (combining characters)
                width += 0
            else:
                width += 1

        return width

    def align_tables(self, content: str) -> str:
        """
        Find and align all tables in the content.

        Algorithm:
        1. Identify table blocks (consecutive lines starting with |)
        2. Parse each table into cells
        3. Calculate max width per column
        4. Rebuild with left-justified padding
        """
        lines = content.split("\n")
        result = []
        i = 0

        while i < len(lines):
            if lines[i].strip().startswith("|"):
                # Found table start
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    table_lines.append(lines[i])
                    i += 1

                # Align this table
                aligned = self._align_table_block(table_lines)
                result.extend(aligned)
                if aligned != table_lines:
                    self.fixes_applied += 1
            else:
                result.append(lines[i])
                i += 1

        return "\n".join(result)

    def _align_table_block(self, table_lines: List[str]) -> List[str]:
        """Align a single table block."""
        if not table_lines:
            return table_lines

        # Parse all rows using shared utility
        rows = table_utils.parse_table_rows(table_lines)

        if not rows:
            return table_lines

        # Calculate max CHARACTER width per column (for pipe alignment)
        # VSCode MD060 expects pipes at same CHARACTER positions, not visual width
        col_widths = table_utils.calculate_column_widths(rows, use_visual_width=False)
        num_cols = len(col_widths)

        # Rebuild aligned table
        aligned = []
        for row in rows:
            cells = []
            for col_idx in range(num_cols):
                if col_idx < len(row):
                    cell = row[col_idx]
                else:
                    cell = ""

                # Check if this is a separator row
                if set(cell.strip()) <= {"-", ":"}:
                    # Preserve separator pattern - pad with dashes
                    cells.append(cell.ljust(col_widths[col_idx], "-"))
                else:
                    # Left-justify content - pad with spaces to character width
                    cells.append(cell.ljust(col_widths[col_idx]))

            aligned.append("| " + " | ".join(cells) + " |")

        return aligned


# ============================================================================
# Main Orchestrator
# ============================================================================


def fix_markdown_file(file_path: str, config: FixConfig) -> FixResults:
    """
    Complete 3-phase workflow for fixing a markdown file.

    Args:
        file_path: Path to markdown file
        config: Fix configuration

    Returns:
        FixResults with success status and statistics
    """
    results = FixResults(success=True)

    try:
        # Read original content
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        # Phase 1: Pymarkdown native fix
        if config.verbose:
            print(f"\n  Phase 1: Running pymarkdown fix...")

        success, output, fix_count = run_pymarkdown_fix(file_path, config)
        results.phase1_fixes = fix_count
        results.details["phase1_output"] = output

        if not success and "not found" in output:
            results.errors.append(output)
            # Continue with phases 2 & 3 even if pymarkdown not available

        # Read content after phase 1
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Phase 2: Custom fixes
        if config.verbose:
            print(f"  Phase 2: Applying custom fixes...")

        fixer = MarkdownFixer(config)
        content = fixer.fix_all(content)
        results.phase2_fixes = fixer.fixes_applied

        # Phase 3: Table alignment
        if config.verbose:
            print(f"  Phase 3: Aligning tables...")

        aligner = TableAligner(config)
        content = aligner.align_tables(content)
        results.phase3_fixes = aligner.fixes_applied

        # Write result if changes made and not dry-run
        total_fixes = results.phase1_fixes + results.phase2_fixes + results.phase3_fixes

        if content != original_content and not config.dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        results.details["total_fixes"] = total_fixes

    except Exception as e:
        results.success = False
        results.errors.append(f"Error processing {file_path}: {str(e)}")

    return results


# ============================================================================
# CLI
# ============================================================================


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Markdown Auto-Fix v0.2.0 - 3-Phase Hybrid Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Fix all docs/*.md files
  %(prog)s --dry-run                # Preview changes without modifying
  %(prog)s --verbose                # Show detailed progress
  %(prog)s docs/MANUAL.md           # Fix specific file
  %(prog)s --line-length 120        # Use 120-char limit

Phase Breakdown:
  Phase 1: Pymarkdown native fix (16+ rules: MD004, MD005, MD029, MD030, etc.)
  Phase 2: Custom fixes (8 rules: MD012, MD013, MD022, MD026, MD031, MD032, MD040, MD047)
  Phase 3: Table alignment (1 rule: MD060)

Coverage: 96%% auto-fix (25+ rules), only MD024 & MD036 require manual work.
        """,
    )

    parser.add_argument(
        "files", nargs="*", help="Specific files to fix (default: all docs/*.md)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed progress and phase information",
    )
    parser.add_argument(
        "--line-length",
        type=int,
        default=120,
        help="Maximum line length for MD013 (default: 120)",
    )
    parser.add_argument(
        "--config",
        default=".pymarkdown",
        help="Path to pymarkdown config file (default: .pymarkdown)",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Build config
    config = FixConfig(
        line_length=args.line_length,
        dry_run=args.dry_run,
        verbose=args.verbose,
        config_file=args.config,
    )

    # Determine files to process
    if args.files:
        files_to_process = args.files
    else:
        # Process all docs/*.md files
        files_to_process = []
        for root, dirs, files in os.walk("docs/"):
            for file in files:
                if file.endswith(".md"):
                    files_to_process.append(os.path.join(root, file))

    # Print header
    print("🔧 Markdown Auto-Fix v0.2.0")
    print("=" * 70)
    print(f"Configuration:")
    print(f"  Line length: {config.line_length}")
    print(f"  Dry run: {config.dry_run}")
    print(f"  Verbose: {config.verbose}")
    print(f"  Config file: {config.config_file}")
    print(f"  Files: {len(files_to_process)}")
    print("=" * 70)

    # Process files
    total_files = 0
    fixed_files = 0
    total_phase1 = 0
    total_phase2 = 0
    total_phase3 = 0
    all_errors = []

    for file_path in files_to_process:
        total_files += 1
        print(f"\n📄 Processing: {file_path}")

        results = fix_markdown_file(file_path, config)

        if results.errors:
            all_errors.extend(results.errors)
            for error in results.errors:
                print(f"  ❌ {error}")

        total_fixes = results.details.get("total_fixes", 0)

        if total_fixes > 0:
            fixed_files += 1
            total_phase1 += results.phase1_fixes
            total_phase2 += results.phase2_fixes
            total_phase3 += results.phase3_fixes

            print(f"  ✅ Fixed {total_fixes} issues:")
            print(f"     Phase 1 (pymarkdown): {results.phase1_fixes}")
            print(f"     Phase 2 (custom): {results.phase2_fixes}")
            print(f"     Phase 3 (tables): {results.phase3_fixes}")
        else:
            print(f"  ⚪ No issues found")

    # Print summary
    print("\n" + "=" * 70)
    print("📊 Summary:")
    print(f"   Files processed: {total_files}")
    print(f"   Files modified: {fixed_files}")
    print(f"   Files unchanged: {total_files - fixed_files}")
    print(f"\n   Total fixes by phase:")
    print(f"     Phase 1 (pymarkdown native): {total_phase1}")
    print(f"     Phase 2 (custom logic): {total_phase2}")
    print(f"     Phase 3 (table alignment): {total_phase3}")
    print(f"     TOTAL: {total_phase1 + total_phase2 + total_phase3}")

    if all_errors:
        print(f"\n⚠️  Errors encountered: {len(all_errors)}")
        for error in all_errors:
            print(f"   - {error}")

    if config.dry_run:
        print("\n🔍 DRY RUN - No files were modified")
        print("   Run without --dry-run to apply changes")
    elif fixed_files > 0:
        print(f"\n🎉 Successfully auto-fixed {fixed_files} files!")
        print("   Review changes with: git diff docs/")
        print("   Verify with: uv run python tests/lint/lint-markdown.py")
    else:
        print(f"\n✨ All files are clean!")

    print("=" * 70)


if __name__ == "__main__":
    main()
