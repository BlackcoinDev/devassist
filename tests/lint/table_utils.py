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
Shared table utilities for markdown linting and fixing.

Provides common functions for:
- Table detection and parsing
- Column width calculations
- Pipe position validation
- MD060 compliance checking

Used by both lint-markdown.py and fix-markdown.py
"""

from typing import List, Tuple


def find_table_blocks(lines: List[str]) -> List[Tuple[int, int]]:
    """
    Find all table blocks in a list of lines.

    Returns list of (start_line, end_line) tuples (0-based indexing).
    A table block consists of consecutive lines that start with '|'.

    Args:
        lines: List of text lines

    Returns:
        List of (start_idx, end_idx) tuples for each table block
    """
    table_blocks = []
    i = 0

    while i < len(lines):
        if lines[i].strip().startswith("|"):
            # Found table start
            start_idx = i
            while i < len(lines) and lines[i].strip().startswith("|"):
                i += 1
            end_idx = i - 1
            table_blocks.append((start_idx, end_idx))
        else:
            i += 1

    return table_blocks


def parse_table_rows(table_lines: List[str]) -> List[List[str]]:
    """
    Parse table lines into a list of cell lists.

    Handles the standard markdown table format where cells are separated by '|'.

    Args:
        table_lines: Lines containing the table

    Returns:
        List of rows, where each row is a list of cell strings
    """
    rows = []
    for line in table_lines:
        cells = [cell.strip() for cell in line.split("|")]
        # Remove empty first/last cells from split (artifacts of | separators)
        if cells and not cells[0]:
            cells = cells[1:]
        if cells and not cells[-1]:
            cells = cells[:-1]
        rows.append(cells)

    return rows


def calculate_column_widths(
    rows: List[List[str]], use_visual_width: bool = False
) -> List[int]:
    """
    Calculate maximum width for each column.

    Args:
        rows: Table rows as returned by parse_table_rows
        use_visual_width: If True, use visual/display width (for fixing).
                         If False, use character count (for linting).

    Returns:
        List of maximum widths for each column
    """
    if not rows:
        return []

    num_cols = max(len(row) for row in rows)
    col_widths = [0] * num_cols

    for row in rows:
        for col_idx, cell in enumerate(row):
            if col_idx < num_cols:
                if use_visual_width:
                    width = visual_width(cell)
                else:
                    width = len(cell)
                col_widths[col_idx] = max(col_widths[col_idx], width)

    return col_widths


def calculate_expected_pipe_positions(col_widths: List[int]) -> List[int]:
    """
    Calculate expected pipe positions for MD060 compliance.

    Uses the "aligned" style where pipes are positioned at consistent
    character locations based on column content widths.

    Args:
        col_widths: Maximum character width for each column

    Returns:
        List of expected pipe positions (0-based character indices)
    """
    expected_pipes = []
    current_pos = 0

    # First pipe at position 0
    expected_pipes.append(0)
    current_pos += 1  # After first |

    # Add positions for each column
    for col_width in col_widths:
        # Content width + space before + space after + |
        current_pos += 1  # space before content
        current_pos += col_width  # content
        current_pos += 1  # space after content
        expected_pipes.append(current_pos)
        current_pos += 1  # after |

    return expected_pipes


def find_actual_pipe_positions(line: str) -> List[int]:
    """
    Find positions of all pipe characters in a line.

    Args:
        line: Text line to analyze

    Returns:
        List of pipe positions (0-based character indices)
    """
    return [pos for pos, char in enumerate(line) if char == "|"]


def visual_width(text: str) -> int:
    """
    Calculate visual/display width of text.

    Handles Unicode characters properly:
    - ASCII: 1 column each
    - Emojis: 2 columns each (✅, 🎉, etc.)
    - East Asian Wide: 2 columns each
    - Combining characters: 0 columns

    Args:
        text: Text to measure

    Returns:
        Visual width in character columns
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


def contains_unicode(text: str) -> bool:
    """
    Check if text contains Unicode characters (emojis, symbols, etc.).

    Args:
        text: Text to check

    Returns:
        True if text contains Unicode characters beyond basic ASCII
    """
    for char in text:
        code_point = ord(char)
        # Check for emoji ranges and other Unicode symbols
        if (
            code_point > 127  # Non-ASCII
            or (code_point >= 0x1F300 and code_point <= 0x1F9FF)  # Emojis
            or (code_point >= 0x2600 and code_point <= 0x27BF)
        ):  # Misc symbols
            return True
    return False


def detect_emoji_columns(rows: List[List[str]]) -> List[bool]:
    """
    Detect which columns contain emoji/Unicode characters.

    Args:
        rows: Table rows as returned by parse_table_rows

    Returns:
        List of booleans indicating which columns contain emojis
    """
    if not rows:
        return []

    num_cols = max(len(row) for row in rows)
    emoji_columns = [False] * num_cols

    for row in rows:
        for col_idx, cell in enumerate(row):
            if col_idx < num_cols and contains_unicode(cell):
                emoji_columns[col_idx] = True

    return emoji_columns


def validate_table_alignment(
    table_lines: List[str], start_line: int, file_path: str
) -> List[str]:
    """
    Validate that a table block has properly aligned pipes (MD060 compliance).

    This is the shared validation logic used by lint-markdown.py.

    Args:
        table_lines: Lines containing the table
        start_line: 1-based line number where table starts
        file_path: File path for error reporting

    Returns:
        List of error messages for MD060 violations
    """
    if not table_lines:
        return []

    errors = []

    # Parse table rows
    rows = parse_table_rows(table_lines)
    if not rows:
        return []

    # Calculate expected column widths (visual-based for emoji alignment)
    col_widths = calculate_column_widths(rows, use_visual_width=True)
    expected_pipes = calculate_expected_pipe_positions(col_widths)

    # Check each table line for proper alignment
    for line_idx, line in enumerate(table_lines):
        line_num = start_line + line_idx

        # Find actual pipe positions
        actual_pipes = find_actual_pipe_positions(line)

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
                f"{file_path}:{line_num}: 💡 Fix with: uv run python tests/lint/fix-markdown.py {file_path}"
            )

    return errors


def check_md060_compliance(content: str, file_path: str) -> List[str]:
    """
    Check MD060 compliance (table column alignment) in markdown content.

    Scans the entire content for table blocks and validates each one.

    Args:
        content: Markdown file content
        file_path: Path to the file for error reporting

    Returns:
        List of error messages for all MD060 violations in the file
    """
    lines = content.split("\n")
    table_blocks = find_table_blocks(lines)

    all_errors = []
    for start_idx, end_idx in table_blocks:
        table_lines = lines[start_idx : end_idx + 1]
        start_line = start_idx + 1  # Convert to 1-based line numbering

        errors = validate_table_alignment(table_lines, start_line, file_path)
        all_errors.extend(errors)

    return all_errors
