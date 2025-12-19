#!/usr/bin/env python3
"""
Comprehensive test suite for fix-markdown.py v0.2.0

Tests all three phases:
- Phase 1: Pymarkdown native fix (subprocess wrapper)
- Phase 2: Custom fixes (7 MD rules)
- Phase 3: Table alignment (MD060)
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add tests/lint directory to path for imports
tests_lint_path = Path(__file__).parent.parent / "lint"
sys.path.insert(0, str(tests_lint_path))

# Import from fix-markdown.py (Python sees it as fix_markdown module)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "fix_markdown",
    tests_lint_path / "fix-markdown.py"
)
fix_markdown = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fix_markdown)

# Import the classes and functions
FixConfig = fix_markdown.FixConfig
MarkdownFixer = fix_markdown.MarkdownFixer
TableAligner = fix_markdown.TableAligner
fix_markdown_file = fix_markdown.fix_markdown_file
run_pymarkdown_fix = fix_markdown.run_pymarkdown_fix


@pytest.fixture
def config():
    """Default test configuration."""
    return FixConfig(
        line_length=100,
        aggressive_mode=True,
        dry_run=False,
        verbose=False,
        config_file=".pymarkdown"
    )


@pytest.fixture
def fixer(config):
    """MarkdownFixer instance for testing."""
    return MarkdownFixer(config)


@pytest.fixture
def aligner(config):
    """TableAligner instance for testing."""
    return TableAligner(config)


# ============================================================================
# Phase 2 Tests: Custom Fixes
# ============================================================================

class TestMD047TrailingNewline:
    """MD047: Files should end with single trailing newline."""

    def test_add_missing_newline(self, fixer):
        content = "This file has no newline"
        result = fixer.fix_md047_trailing_newline(content)
        assert result == "This file has no newline\n"
        assert fixer.fixes_applied == 1

    def test_remove_multiple_newlines(self, fixer):
        content = "This file has too many\n\n\n"
        result = fixer.fix_md047_trailing_newline(content)
        assert result == "This file has too many\n"
        assert fixer.fixes_applied == 2  # Removed 2 extra newlines

    def test_preserve_single_newline(self, fixer):
        content = "This file is correct\n"
        result = fixer.fix_md047_trailing_newline(content)
        assert result == "This file is correct\n"
        assert fixer.fixes_applied == 0


class TestMD022HeadingBlanks:
    """MD022: Headings should be surrounded by blank lines."""

    def test_add_blank_before_heading(self, fixer):
        content = "Previous paragraph\n## Heading"
        result = fixer.fix_md022_heading_blanks(content)
        assert "Previous paragraph\n\n## Heading" in result
        assert fixer.fixes_applied >= 1

    def test_add_blank_after_heading(self, fixer):
        content = "## Heading\nNext paragraph"
        result = fixer.fix_md022_heading_blanks(content)
        assert "## Heading\n\nNext paragraph" in result
        assert fixer.fixes_applied >= 1

    def test_heading_already_surrounded(self, fixer):
        content = "Previous\n\n## Heading\n\nNext"
        result = fixer.fix_md022_heading_blanks(content)
        # Should not add extra blanks
        assert result.count('\n\n') == 2

    def test_multiple_heading_levels(self, fixer):
        content = "Text\n# H1\nText\n## H2\nText\n### H3\nText"
        result = fixer.fix_md022_heading_blanks(content)
        # All headings should have blanks
        assert "Text\n\n# H1\n\nText" in result
        assert "Text\n\n## H2\n\nText" in result


class TestMD031CodeBlockBlanks:
    """MD031: Code blocks should be surrounded by blank lines."""

    def test_add_blank_before_code(self, fixer):
        content = "Text before\n```python\ncode\n```"
        result = fixer.fix_md031_code_block_blanks(content)
        assert "Text before\n\n```python" in result

    def test_add_blank_after_code(self, fixer):
        content = "```python\ncode\n```\nText after"
        result = fixer.fix_md031_code_block_blanks(content)
        assert "```\n\nText after" in result

    def test_code_already_surrounded(self, fixer):
        content = "Text\n\n```python\ncode\n```\n\nText"
        result = fixer.fix_md031_code_block_blanks(content)
        # Should not add extra blanks
        original_blanks = content.count('\n\n')
        result_blanks = result.count('\n\n')
        assert result_blanks == original_blanks


class TestMD032ListBlanks:
    """MD032: Lists should be surrounded by blank lines."""

    def test_add_blank_before_list(self, fixer):
        content = "Paragraph\n- Item 1\n- Item 2"
        result = fixer.fix_md032_list_blanks(content)
        assert "Paragraph\n\n- Item 1" in result

    def test_add_blank_after_list(self, fixer):
        content = "- Item 1\n- Item 2\nParagraph"
        result = fixer.fix_md032_list_blanks(content)
        assert "- Item 2\n\nParagraph" in result

    def test_ordered_list(self, fixer):
        content = "Paragraph\n1. First\n2. Second\nParagraph"
        result = fixer.fix_md032_list_blanks(content)
        assert "Paragraph\n\n1. First" in result
        assert "2. Second\n\nParagraph" in result

    def test_list_already_surrounded(self, fixer):
        content = "Text\n\n- Item\n\nText"
        result = fixer.fix_md032_list_blanks(content)
        original_blanks = content.count('\n\n')
        result_blanks = result.count('\n\n')
        assert result_blanks == original_blanks


class TestMD026TrailingPunctuation:
    """MD026: Headings should not have trailing punctuation."""

    def test_remove_period(self, fixer):
        content = "## Heading with period."
        result = fixer.fix_md026_trailing_punctuation(content)
        assert result == "## Heading with period"
        assert fixer.fixes_applied == 1

    def test_remove_question_mark(self, fixer):
        content = "### What is this?"
        result = fixer.fix_md026_trailing_punctuation(content)
        assert result == "### What is this"

    def test_remove_multiple_punctuation(self, fixer):
        content = "# Title!!!"
        result = fixer.fix_md026_trailing_punctuation(content)
        assert result == "# Title"

    def test_preserve_mid_punctuation(self, fixer):
        content = "## U.S.A. Overview"
        result = fixer.fix_md026_trailing_punctuation(content)
        # Should keep periods in middle
        assert "U.S.A." in result

    def test_no_trailing_punctuation(self, fixer):
        content = "## Normal Heading"
        result = fixer.fix_md026_trailing_punctuation(content)
        assert result == "## Normal Heading"
        assert fixer.fixes_applied == 0


class TestMD040CodeLanguage:
    """MD040: Fenced code blocks should have language specified."""

    def test_detect_python_via_keywords(self, fixer):
        content = "```\ndef hello():\n    print('world')\n```"
        result = fixer.fix_md040_code_language(content)
        assert "```python" in result
        assert fixer.fixes_applied == 1

    def test_detect_python_via_shebang(self, fixer):
        content = "```\n#!/usr/bin/env python3\nprint('test')\n```"
        result = fixer.fix_md040_code_language(content)
        assert "```python" in result

    def test_detect_javascript(self, fixer):
        content = "```\nconst foo = 'bar';\nlet x = 5;\n```"
        result = fixer.fix_md040_code_language(content)
        assert "```javascript" in result

    def test_detect_bash(self, fixer):
        content = "```\n#!/bin/bash\necho 'hello'\n```"
        result = fixer.fix_md040_code_language(content)
        assert "```bash" in result

    def test_default_to_text(self, fixer):
        content = "```\nSome random content\nwithout code keywords\n```"
        result = fixer.fix_md040_code_language(content)
        assert "```text" in result

    def test_preserve_existing_language(self, fixer):
        content = "```rust\nfn main() {}\n```"
        result = fixer.fix_md040_code_language(content)
        # Should not match pattern (already has language)
        assert "```rust" in result


class TestMD013LineLength:
    """MD013: Lines should not exceed configured length."""

    def test_wrap_long_line(self, fixer):
        long_line = "This is a very long line that exceeds the maximum length " \
                   "of 100 characters and should be wrapped at word boundaries " \
                   "to maintain readability."
        content = long_line
        result = fixer.fix_md013_line_length(content)
        lines = result.split('\n')
        # All lines should be <= 100 chars
        assert all(len(line) <= 100 for line in lines)
        assert len(lines) > 1  # Should be wrapped

    def test_preserve_table_rows(self, fixer):
        table = "| Column A | Column B | Column C | Column D | Column E | " \
               "Column F | Column G | Column H |"
        result = fixer.fix_md013_line_length(table)
        # Table should not be wrapped (starts with |)
        assert result == table

    def test_preserve_headings(self, fixer):
        heading = "# " + "A" * 150  # Very long heading
        result = fixer.fix_md013_line_length(heading)
        # Headings should not be wrapped
        assert result == heading

    def test_preserve_code_blocks(self, fixer):
        content = "```python\n" + "x = " + "y" * 150 + "\n```"
        result = fixer.fix_md013_line_length(content)
        # Code inside blocks should not be wrapped
        assert "y" * 150 in result

    def test_preserve_list_indentation(self, fixer):
        # List item longer than 100 chars
        content = "- This is a list item that is quite long and exceeds " \
                 "the maximum line length so it should be wrapped but " \
                 "preserve indentation for continuation lines"
        result = fixer.fix_md013_line_length(content)
        lines = result.split('\n')
        # Continuation lines should be indented
        if len(lines) > 1:
            assert lines[1].startswith('  ')  # 2 spaces for "- "

    def test_short_lines_unchanged(self, fixer):
        content = "Short line\nAnother short line"
        result = fixer.fix_md013_line_length(content)
        assert result == content
        assert fixer.fixes_applied == 0


# ============================================================================
# Phase 3 Tests: Table Alignment
# ============================================================================

class TestTableAlignment:
    """MD060: Table pipes must be vertically aligned."""

    def test_align_simple_table(self, aligner):
        table = [
            "| A | B |",
            "|---|---|",
            "| 1 | 2 |",
            "| 100 | 200 |"
        ]
        content = '\n'.join(table)
        result = aligner.align_tables(content)

        # Check that pipes are aligned
        lines = result.split('\n')
        pipe_positions = [[i for i, c in enumerate(line) if c == '|']
                         for line in lines]

        # All rows should have same pipe positions
        assert len(set(tuple(p) for p in pipe_positions)) == 1
        assert aligner.fixes_applied == 1

    def test_align_table_with_varying_widths(self, aligner):
        table = [
            "| Name | Age | City |",
            "|------|-----|------|",
            "| Alice | 30 | NYC |",
            "| Bob | 25 | San Francisco |"
        ]
        content = '\n'.join(table)
        result = aligner.align_tables(content)

        lines = result.split('\n')
        # "San Francisco" should determine column width
        assert "San Francisco" in result
        # All pipes should align
        pipe_positions = [[i for i, c in enumerate(line) if c == '|']
                         for line in lines]
        assert len(set(tuple(p) for p in pipe_positions)) == 1

    def test_preserve_separator_row(self, aligner):
        table = [
            "| Col1 | Col2 |",
            "|------|------|",
            "| A | B |"
        ]
        content = '\n'.join(table)
        result = aligner.align_tables(content)

        # Separator should still be dashes
        assert "------" in result or "----" in result

    def test_table_already_aligned(self, aligner):
        table = [
            "| A   | B   |",
            "| --- | --- |",
            "| 1   | 2   |"
        ]
        content = '\n'.join(table)
        result = aligner.align_tables(content)

        # Should detect it's already aligned
        assert result == content or aligner.fixes_applied == 0

    def test_non_table_content_preserved(self, aligner):
        content = "This is not a table\n\nJust regular text"
        result = aligner.align_tables(content)
        assert result == content
        assert aligner.fixes_applied == 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestFullWorkflow:
    """Test complete fix_markdown_file workflow."""

    def test_fix_with_all_phases(self, config, tmp_path):
        """Test file with issues in all phases."""
        test_file = tmp_path / "test.md"
        content = """## Heading without blanks
Next paragraph
```
code without language
```
- List without blanks
Next paragraph
## Another heading.
| A | B |
|---|---|
| 1 | 2 |
| 100 | 200 |
"""
        test_file.write_text(content)

        config.dry_run = False
        results = fix_markdown_file(str(test_file), config)

        assert results.success
        # Should have fixes in phase 2 (headings, code, lists, punctuation)
        # and phase 3 (tables)
        total_fixes = results.details.get('total_fixes', 0)
        assert total_fixes > 0

        # Read result
        fixed_content = test_file.read_text()

        # Verify specific fixes
        assert "## Heading without blanks\n\n" in fixed_content  # MD022
        assert "```text\n" in fixed_content  # MD040
        assert "## Another heading\n" in fixed_content  # MD026 (no period)

    def test_dry_run_mode(self, config, tmp_path):
        """Test that dry-run doesn't modify files."""
        test_file = tmp_path / "test.md"
        original = "## Heading.\nNo blanks"
        test_file.write_text(original)

        config.dry_run = True
        results = fix_markdown_file(str(test_file), config)

        # File should be unchanged
        assert test_file.read_text() == original
        # But should report fixes
        assert results.details.get('total_fixes', 0) > 0

    def test_empty_file(self, config, tmp_path):
        """Test handling of empty file."""
        test_file = tmp_path / "empty.md"
        test_file.write_text("")

        results = fix_markdown_file(str(test_file), config)
        assert results.success
        # Should add trailing newline
        assert test_file.read_text() == "\n"

    def test_file_with_no_issues(self, config, tmp_path):
        """Test file that's already compliant."""
        test_file = tmp_path / "clean.md"
        content = """# Title

This is a paragraph.

## Section

Another paragraph.

```python
def hello():
    pass
```

Done.
"""
        test_file.write_text(content)

        results = fix_markdown_file(str(test_file), config)
        assert results.success
        # Might add trailing newline, but otherwise minimal fixes
        assert results.details.get('total_fixes', 0) <= 1


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_unicode_content(self, fixer):
        """Test handling of unicode characters."""
        content = "## Héading with émojis 🎉.\n\nContent with 中文字符"
        result = fixer.fix_md026_trailing_punctuation(content)
        assert "🎉" in result
        assert "中文字符" in result

    def test_very_long_table(self, aligner):
        """Test table with many rows."""
        rows = ["| A | B |", "|---|---|"]
        rows.extend([f"| {i} | {i*2} |" for i in range(100)])
        content = '\n'.join(rows)

        result = aligner.align_tables(content)
        lines = result.split('\n')
        assert len(lines) == 102  # header + separator + 100 rows

    def test_malformed_table(self, aligner):
        """Test table with inconsistent columns."""
        table = [
            "| A | B | C |",
            "|---|---|",  # Missing column
            "| 1 | 2 |"
        ]
        content = '\n'.join(table)

        # Should handle gracefully
        result = aligner.align_tables(content)
        assert result is not None

    def test_nested_code_blocks(self, fixer):
        """Test markdown containing nested code examples."""
        content = """```markdown
Example with code:
```python
def foo():
    pass
```
```"""
        # Should handle without crashing
        result = fixer.fix_md031_code_block_blanks(content)
        assert result is not None

    def test_mixed_line_endings(self, fixer):
        """Test content with mixed \n and \r\n."""
        content = "Line 1\nLine 2\r\nLine 3"
        # Should handle without crashing
        result = fixer.fix_md022_heading_blanks(content)
        assert result is not None


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Test performance with large files."""

    def test_large_file_performance(self, config, tmp_path):
        """Test processing a large markdown file."""
        test_file = tmp_path / "large.md"

        # Generate large file (1000 lines)
        lines = []
        for i in range(200):
            lines.extend([
                f"## Section {i}",
                f"Content for section {i}.",
                "",
                "```python",
                f"def func_{i}():",
                "    pass",
                "```",
                ""
            ])

        test_file.write_text('\n'.join(lines))

        import time
        start = time.time()
        results = fix_markdown_file(str(test_file), config)
        elapsed = time.time() - start

        assert results.success
        # Should complete in reasonable time (< 5 seconds for 1000 lines)
        assert elapsed < 5.0

    def test_many_tables(self, aligner):
        """Test alignment of many tables."""
        tables = []
        for i in range(50):
            tables.extend([
                f"## Table {i}",
                "",
                "| A | B | C |",
                "|---|---|---|",
                "| 1 | 2 | 3 |",
                ""
            ])

        content = '\n'.join(tables)
        result = aligner.align_tables(content)

        # Should handle without performance degradation
        assert result is not None
        assert len(result.split('\n')) == len(tables)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
