# Complete Markdown Linting Rules Reference

## 📋 Overview

This document provides a comprehensive reference for all markdown linting rules
(MDxxx) that may be encountered in the project, including which can be
auto-fixed and which require manual intervention.

## 🎯 Rule Categories

### ✅ Auto-Fixable Rules (7 rules)

These rules can be automatically fixed by the `fix-markdown.py` script:

| Rule | Name | Description | Auto-Fix Status |
| ------ | ------ | ------------- | ----------------- |
| **MD013** | Line length | Lines should not exceed 80 characters | ✅ Partially fixable |
| **MD022** | Blank lines around headings | Headings should be surrounded by blank lines | ✅ Fully fixable |
| **MD030** | List marker space | Spaces after list markers should be consistent | ❌ Manual fix required |
| **MD031** | Blank lines around code blocks | Code blocks should be surrounded by blank lines | ✅ Fully fixable |
| **MD032** | Blank lines around lists | Lists should be surrounded by blank lines | ✅ Partially fixable |
| **MD040** | Fenced code language | Fenced code blocks should have language specified | ✅ Fully fixable |
| **MD047** | Trailing newline | Files should end with single trailing newline | ✅ Fully fixable |

### ⚠️ Partially Auto-Fixable Rules (2 rules)

These rules can be partially auto-fixed but often require manual review:

| Rule | Name | Description | Notes |
| ------ | ------ | ------------- | ------- |
| **MD005** | List indent | Inconsistent indentation for list items at same level | Complex nested structures |
| **MD025** | Single H1 | Multiple top-level headings (should have single H1) | Document structure decision |

### ❌ Manual-Fix Required Rules (6 rules)

These rules require manual fixing due to complexity and context sensitivity:

| Rule | Name | Description | Complexity |
| ------ | ------ | ------------- | ------------ |
| **MD004** | List style | Inconsistent unordered list markers (`*`, `-`, `+`) | Medium |
| **MD024** | Duplicate headings | Multiple headings with same content | Medium |
| **MD026** | Trailing punctuation | Headings should not have trailing punctuation | Low |
| **MD029** | Ordered list prefix | Ordered list items should have sequential numbers | High |
| **MD036** | Emphasis as heading | Bold/italic emphasis used instead of proper headings | High |
| **MD060** | Table column alignment | Table pipes must be vertically aligned | Medium |

## 📚 Detailed Rule Reference

### MD004 - Inconsistent Unordered List Style

**Issue**: Mixed use of `*`, `-`, and `+` for unordered lists.

**Example**:

```markdown
❌ Wrong:
* Item one
- Item two  ❌ (inconsistent)
+ Item three ❌ (inconsistent)

✅ Correct:
- Item one
- Item two  ✅ (consistent)
- Item three ✅ (consistent)

```text

**Fix Strategy**: Choose one style and apply consistently throughout document.

### MD005 - Inconsistent List Indentation

**Issue**: List items at the same level have inconsistent indentation.

**Example**:

```markdown
❌ Wrong:
- Item 1
  - Nested item  ❌ (inconsistent indentation)
- Item 2
    - Another nested  ❌ (different indentation)

✅ Correct:
- Item 1
  - Nested item  ✅ (consistent 2-space indent)
- Item 2
  - Another nested  ✅ (consistent 2-space indent)

```text

**Fix Strategy**: Standardize on 2-space indentation for nested items.

### MD013 - Line Length

**Issue**: Lines exceed maximum length (typically 80 characters).

**Example**:

```markdown
❌ Wrong:
This line is way too long and exceeds the maximum line length of 80 characters,
which makes it difficult to read and maintain proper formatting standards.

✅ Correct:
This line is properly wrapped to maintain
readability and comply with line length
standards while preserving content meaning.

```text

**Fix Strategy**: Wrap long lines at logical breaks (spaces, punctuation).

### MD022 - Blank Lines Around Headings

**Issue**: Headings not properly separated by blank lines.

**Example**:

```markdown
❌ Wrong:
# Heading 1  ❌ (no blank line before)
Paragraph text...
## Heading 2  ❌ (no blank line after previous content)

✅ Correct:

# Heading 1  ✅ (blank line before)

Paragraph text...

## Heading 2  ✅ (blank line after previous content)

```text

**Fix Strategy**: Add blank lines before and after all headings.

### MD024 - Duplicate Headings

**Issue**: Multiple headings with identical text.

**Example**:

```markdown
❌ Wrong:
## Introduction

Content about introduction...

## Introduction  ❌ (duplicate)

More content...

✅ Correct:
## Introduction

Content about introduction...

## Advanced Topics  ✅ (unique)

More content...

```text

**Fix Strategy**: Make each heading unique while preserving semantic meaning.

### MD025 - Multiple Top-Level Headings

**Issue**: Multiple H1 (#) headings in same document.

**Example**:

```markdown
❌ Wrong:
# First Heading  ❌ (first H1)
Content...

# Second Heading  ❌ (second H1)
More content...

✅ Correct:
# Main Title  ✅ (single H1)

## Section 1  ✅ (use H2+)

Content...

## Section 2  ✅ (use H2+)

More content...

```text

**Fix Strategy**: Use single H1 for main title, H2+ for sections.

### MD026 - Trailing Punctuation in Headings

**Issue**: Headings end with punctuation marks.

**Example**:

```markdown
❌ Wrong:
### Heading with punctuation.  ❌ (trailing period)

### Heading with question mark?  ❌ (trailing question mark)

✅ Correct:
### Heading without punctuation  ✅

### Question heading  ✅ (no trailing punctuation)

```text

**Fix Strategy**: Remove trailing punctuation from headings.

### MD029 - Ordered List Prefix

**Issue**: Ordered list items don't use sequential numbers.

**Example**:

```markdown
❌ Wrong:
1. First item
1. Second item  ❌ (should be 2)
1. Third item   ❌ (should be 3)

✅ Correct:
1. First item
2. Second item  ✅
3. Third item   ✅

```text

**Fix Strategy**: Use sequential numbers starting from 1.

### MD030 - List Marker Space

**Issue**: Inconsistent spaces after list markers.

**Example**:

```markdown
❌ Wrong:
- Item one
-   Item two  ❌ (extra spaces)
- Item three

✅ Correct:
- Item one
- Item two   ✅ (consistent 1 space)
- Item three

```text

**Fix Strategy**: Standardize on 1 space after list markers.

### MD031 - Blank Lines Around Code Blocks

**Issue**: Code blocks not properly separated by blank lines.

**Example**:

```markdown
❌ Wrong:
Paragraph text

```python  ❌ (no blank line before)
def example():
    pass

```text
More text  ❌ (no blank line after)

✅ Correct:
Paragraph text

```python  ✅ (blank line before)
def example():
    pass

```text

More text  ✅ (blank line after)

```

**Fix Strategy**: Add blank lines before and after all code blocks.

### MD032 - Blank Lines Around Lists

**Issue**: Lists not properly separated by blank lines.

**Example**:

```markdown
❌ Wrong:
Paragraph text
- List item  ❌ (no blank line before)
- Another item
More text  ❌ (no blank line after)

✅ Correct:
Paragraph text

- List item  ✅ (blank line before)
- Another item

More text  ✅ (blank line after)

```text

**Fix Strategy**: Add blank lines before and after all lists.

### MD036 - Emphasis as Heading

**Issue**: Bold/italic used where headings would be better.

**Example**:

```markdown
❌ Wrong:
**Important Section**  ❌ (should be heading)

Content about this section...

✅ Correct:
## Important Section  ✅ (proper heading)

Content about this section...

```text

**Fix Strategy**: Convert emphasis to appropriate heading level.

### MD040 - Fenced Code Language

**Issue**: Code blocks missing language specification.

**Example**:

```markdown
❌ Wrong:

```  ❌ (no language)
def example():
    pass

```text

✅ Correct:

```python  ✅ (language specified)
def example():
    pass

```

```text

**Fix Strategy**: Add appropriate language identifier (python, javascript,
etc.).

### MD047 - Trailing Newline

**Issue**: Files don't end with newline character.

**Example**:

```markdown
❌ Wrong:
Content here...❌ (no newline at end)

✅ Correct:
Content here...
✅ (ends with newline)

```text

**Fix Strategy**: Ensure all files end with single newline character.

### MD060 - Table Column Alignment

**Issue**: Table pipes not vertically aligned.

**Example**:

```markdown
❌ Wrong:
| A | B |      [0, 3, 7]
|---|---|     [0, 3, 7]
| 1 | 2 |     [0, 3, 7]
| 10 | 20 |   [0, 5, 10] ❌ (misaligned)

✅ Correct:
| A   | B   |   [0, 5, 10]
| --- | --- |   [0, 5, 10]
| 1   | 2   |   [0, 5, 10]
| 10  | 20  |   [0, 5, 10] ✅ (aligned)

```

**Fix Strategy**: Use `create_md_table.py` tool for perfect alignment.

## 📊 Current Issue Distribution

**Total Issues**: 141

### Auto-Fixable Issues (60+ issues)

- **MD013**: 50 issues (line length)
- **MD031**: 9 issues (code block blanks)
- **MD032**: 6 issues (list blanks)
- **MD047**: 2 issues (trailing newlines)
- **MD022**: 1 issue (heading blanks)

### Manual-Fix Issues (81+ issues)

- **MD030**: 48 issues (list spacing)
- **MD036**: 11 issues (emphasis as headings)
- **MD004**: 8 issues (list style consistency)
- **MD029**: 3 issues (ordered list prefixes)
- **MD024**: 1 issue (duplicate headings)

### Already Resolved

- **MD060**: 0 issues ✅ (fully resolved)
- **MD005**: 0 issues ✅ (no indentation issues)
- **MD025**: 0 issues ✅ (proper H1 usage)

## 🎯 Recommended Fix Strategy

### 1. Run Auto-Fix First

```bash
python tests/lint/fix-markdown.py

```

### 2. Manual Fix Priority Order

1. **MD030** - List spacing (48 issues) - Most common
2. **MD036** - Emphasis as headings (11 issues) - Structural
3. **MD004** - List style consistency (8 issues) - Visual
4. **MD029** - Ordered list prefixes (3 issues) - Logical
5. **MD024** - Duplicate headings (1 issue) - Navigation

### 3. Table Creation

- **ALWAYS** use `tools/create_md_table.py`
- Never manually create tables
- Verify with `pymarkdown scan`

### 4. Document Structure

- Maintain single H1 per document (MD025)
- Use consistent list indentation (MD005)
- Standardize list markers (MD004)

## 🤖 AI Agent Guidelines

### For Auto-Fixable Issues

- Run auto-fix regularly during development
- Review changes before committing
- Handle edge cases manually
- Test with `pymarkdown scan`

### For Manual-Fix Issues

- Fix in batches by issue type
- Use search/replace for consistent patterns
- Test changes in isolation
- Maintain semantic meaning
- Preserve document structure

### For Table Creation

- **MANDATORY**: Use `create_md_table.py`
- Never manually create tables
- Verify MD060 compliance
- Test with sample data first

## 📋 Checklist for Zero Tolerance

- [ ] Run auto-fix on all markdown files
- [ ] Fix MD030 list spacing issues
- [ ] Convert MD036 emphasis to proper headings
- [ ] Standardize MD004 list markers
- [ ] Fix MD029 ordered list numbering
- [ ] Resolve MD024 duplicate headings
- [ ] Use `create_md_table.py` for all tables
- [ ] Verify with `pymarkdown scan`
- [ ] Achieve 0 issues across all files

## 🔍 Troubleshooting Guide

### Common Issues and Solutions

**Issue**: Auto-fix doesn't resolve all problems

- **Solution**: Manual review required for complex issues
- **Tool**: `pymarkdown scan filename.md` for detailed analysis

**Issue**: Tables still misaligned after auto-fix

- **Solution**: Use `create_md_table.py` for perfect alignment
- **Verification**: Check pipe positions manually

**Issue**: Line wrapping breaks code/formatting

- **Solution**: Exclude sensitive areas from auto-wrapping
- **Manual**: Handle long lines carefully

**Issue**: Multiple H1 headings detected

- **Solution**: Restructure document hierarchy
- **Best Practice**: Single H1 per document

**Issue**: Inconsistent list indentation

- **Solution**: Standardize on 2-space indentation
- **Tool**: Visual inspection with monospace font

## 📚 Resources

- **pymarkdownlnt documentation**: Comprehensive rule explanations
- **Markdown specification**: Official syntax guide
- **CommonMark**: Standard markdown reference
- **MD060 Table Guide**: `docs/TABLE_CREATION_GUIDE.md`

## 🎓 Best Practices

### General

- Run linting checks frequently
- Fix issues incrementally
- Document fix decisions
- Maintain consistency

### For Tables

- Always use `create_md_table.py`
- Test with sample data
- Verify alignment visually
- Preserve markdown formatting

### For Lists

- Choose consistent marker style
- Standardize indentation
- Maintain proper spacing
- Use appropriate nesting

### For Headings

- Single H1 per document
- Logical hierarchy (H1 → H2 → H3)
- No trailing punctuation
- Unique heading text

This comprehensive guide ensures all markdown documentation meets the **zero
tolerance** standard for quality and compliance across all MD rules!
