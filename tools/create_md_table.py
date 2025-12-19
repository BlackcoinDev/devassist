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
MD060-Compliant Table Generator

This utility creates properly aligned markdown tables that comply with MD060 rules.
All pipes are vertically aligned, ensuring consistent formatting.

Usage:
    python create_md_table.py "Header1,Header2,Header3" "Row1Col1,Row1Col2,Row1Col3" "Row2Col1,Row2Col2,Row2Col3"
    
Or import as a module:
    from create_md_table import create_md060_table
    table = create_md060_table([headers], [rows])
"""

import sys
from typing import List


def create_md060_table(headers: List[str], rows: List[List[str]]) -> str:
    """
    Create an MD060-compliant markdown table with perfect pipe alignment.
    
    Args:
        headers: List of header strings
        rows: List of row lists, where each row is a list of cell strings
        
    Returns:
        Perfectly aligned markdown table string
        
    Example:
        >>> headers = ["Metric", "Before", "After", "Change"]
        >>> rows = [
        ...     ["Total Tests", "256", "**360**", "+104 tests (+41%)"],
        ...     ["Coverage", "50%", "**53%**", "+3%"],
        ... ]
        >>> print(create_md060_table(headers, rows))
    """
    # Validate input
    if not headers:
        raise ValueError("Headers cannot be empty")
    
    if not rows:
        # Return header-only table
        return create_table_from_data([headers])
    
    # Check all rows have same number of columns as headers
    for i, row in enumerate(rows):
        if len(row) != len(headers):
            raise ValueError(f"Row {i+1} has {len(row)} columns, expected {len(headers)}")
    
    # Combine all data for column width calculation
    all_data = [headers] + rows
    return create_table_from_data(all_data)


def create_table_from_data(data: List[List[str]]) -> str:
    """
    Create table from 2D data array with perfect alignment.
    
    Args:
        data: 2D list where data[0] is headers, data[1:] are rows
        
    Returns:
        Perfectly aligned markdown table
    """
    if not data:
        return ""
    
    # Calculate column widths
    num_columns = len(data[0])
    col_widths = [0] * num_columns
    
    for row in data:
        if len(row) != num_columns:
            raise ValueError(f"Inconsistent column count: expected {num_columns}, got {len(row)}")
        
        for col_idx, cell in enumerate(row):
            # Calculate display width (accounting for markdown formatting)
            display_width = len(cell)
            # Add extra space for bold/italic markers if present
            if cell.startswith('**') and cell.endswith('**'):
                display_width += 2  # Account for ** markers
            elif cell.startswith('*') and cell.endswith('*'):
                display_width += 2  # Account for * markers
            elif cell.startswith('`') and cell.endswith('`'):
                display_width += 2  # Account for ` markers
                
            if display_width > col_widths[col_idx]:
                col_widths[col_idx] = display_width
    
    # Build table rows
    table_lines = []
    
    # Header row
    header_cells = []
    for col_idx, cell in enumerate(data[0]):
        padded = pad_cell(cell, col_widths[col_idx])
        header_cells.append(padded)
    table_lines.append('| ' + ' | '.join(header_cells) + ' |')
    
    # Separator row
    separator_cells = []
    for width in col_widths:
        separator_cells.append('-' * width)
    table_lines.append('| ' + ' | '.join(separator_cells) + ' |')
    
    # Data rows
    for row in data[1:]:
        row_cells = []
        for col_idx, cell in enumerate(row):
            padded = pad_cell(cell, col_widths[col_idx])
            row_cells.append(padded)
        table_lines.append('| ' + ' | '.join(row_cells) + ' |')
    
    return '\n'.join(table_lines)


def pad_cell(cell: str, target_width: int) -> str:
    """
    Pad a cell to the target width, preserving markdown formatting.
    
    Args:
        cell: The cell content
        target_width: Desired width
        
    Returns:
        Padded cell string
    """
    # Calculate current display width
    current_width = len(cell)
    
    # Add padding if needed
    if current_width < target_width:
        padding_needed = target_width - current_width
        cell += ' ' * padding_needed
    
    return cell


def create_md060_table_from_csv(csv_data: str) -> str:
    """
    Create MD060 table from CSV data.
    
    Args:
        csv_data: CSV string with headers in first row
        
    Returns:
        Perfectly aligned markdown table
    """
    lines = csv_data.strip().split('\n')
    data = []
    
    for line in lines:
        # Handle quoted CSV values
        import csv
        from io import StringIO
        reader = csv.reader(StringIO(line))
        row = next(reader)
        data.append(row)
    
    return create_table_from_data(data)


def main():
    """Command-line interface for table generation."""
    if len(sys.argv) < 2:
        print('Usage: create_md_table.py "Header1,Header2,Header3" "Row1Col1,Row1Col2,Row1Col3" ...')
        print("\nExample:")
        print("  create_md_table.py \"Metric,Before,After,Change\" \"Total Tests,256,360,+104\" \"Coverage,50%,53%,+3%\"")
        return
    
    # Parse arguments
    headers = [h.strip() for h in sys.argv[1].split(',')]
    rows = []
    
    for arg in sys.argv[2:]:
        row = [cell.strip() for cell in arg.split(',')]
        rows.append(row)
    
    # Generate and print table
    table = create_md060_table(headers, rows)
    print(table)


if __name__ == "__main__":
    main()
