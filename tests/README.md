# Markdown Linting and Auto-Fix Documentation

## 📋 Overview

This document explains the markdown linting system, including which rules can be auto-fixed and which require manual
intervention.

## 🔧 Auto-Fix Capabilities

The `fix-markdown.py` script can automatically fix these common issues:

### ✅ Auto-Fixable Rules

| Rule       | Description                                        | Example Fix                                     |
| ---------- | -------------------------------------------------- | ----------------------------------------------- |
| **MD022**  | Headings should be surrounded by blank lines       | Adds blank lines around headings                |
| **MD030**  | Spaces after list markers should be consistent     | Standardizes to 1 space after `-`, `*`, `+`     |
| **MD031**  | Code blocks should be surrounded by blank lines    | Adds blank lines around code blocks             |
| **MD032**  | Lists should be surrounded by blank lines          | Adds blank lines around lists                   |
| **MD040**  | Fenced code blocks should have language specified  | Adds `text` language to unspecified code blocks |
| **MD047**  | Files should end with single trailing newline      | Adds missing newline character                  |
| **MD013**  | Line length should be ≤ 80 characters              | Wraps long lines (basic wrapping)               |

### ⚠️ Partially Auto-Fixable Rules

| Rule      | Description                                  | Notes                          |
| --------- | -------------------------------------------- | ------------------------------ |
| **MD005** | Inconsistent indentation for list items      | Complex nested list structures |
| **MD025** | Multiple top-level headings (single H1)      | Document structure decision    |

## ❌ Manual-Fix Required Rules

These rules require manual fixing due to their complexity:

### 📋 MD060 - Table Column Alignment

**Issue**: Table pipes (`|`) must be vertically aligned across all rows.

**Why Manual Fix Required**:

- Requires analyzing multiple lines simultaneously
- Needs context-aware spacing calculations
- Content length varies between rows
- Risk of breaking table structure with automated fixes

**Example**:

```markdown
❌ Before (misaligned):
| Metric          | Before   | After   | Change                         | [0, 9, 18, 26, 35] |
| --------------- | -------- | ------- | ------------------------------ | [0, 9, 18, 26, 35] |
| **Total Tests** | 256      | **360** | +104...  [0, 18, 24, 34, 54] ❌ | ------------------ |

✅ After (aligned):
| Metric          | Before   | After   | Change            | [0, 23, 34, 44, 64]   |
| --------------- | -------- | ------- | ----------------- | [0, 23, 34, 44, 64]   |
| **Total Tests** | 256      | **360** | +104 tests (+41%) | [0, 23, 34, 44, 64] ✅ |

**Fix Approach**:

1. Calculate maximum width needed for each column
2. Pad all cells in each column to the same width
3. Ensure pipes are at identical character positions in every row

### 📋 MD030 - Spaces After List Markers

**Issue**: Inconsistent spaces after list markers (`-`, `*`, `+`).

**Why Manual Fix Required**:

- Mixed list styles in documents
- Context-dependent formatting decisions
- May require document-wide consistency changes
- Affects visual hierarchy and readability

**Example**:

```markdown

❌ Before:

- Item one
-   Item two  ❌ (extra spaces)
- Item three

✅ After:

- Item one
- Item two   ✅ (consistent 1 space)
- Item three

```text

### 📋 MD032 - Lists Should Be Surrounded by Blank Lines

**Issue**: Lists not properly separated from surrounding content.

**Why Manual Fix Required**:

- Context-dependent spacing decisions
- May affect document flow and readability
- Complex interactions with other elements
- Requires semantic understanding of content structure

**Example**:

```markdown

❌ Before:
This is a paragraph.

- List item one  ❌ (no blank line before)
- List item two

This is another paragraph.  ❌ (no blank line after)

✅ After:
This is a paragraph.

- List item one  ✅ (blank line before)
- List item two

This is another paragraph.  ✅ (blank line after)

```text

### 📋 MD005 - Inconsistent Indentation for List Items

**Issue**: List items at the same level have inconsistent indentation.

**Why Manual Fix Required**:

- Complex nested list structures
- Context-dependent indentation decisions
- May require restructuring of content hierarchy
- Affects visual organization and readability

**Example**:

```markdown

❌ Before:

- Item 1
  - Nested item  ❌ (inconsistent indentation)
- Item 2
    - Another nested  ❌ (different indentation)

✅ After:

- Item 1
  - Nested item  ✅ (consistent 2-space indent)
- Item 2
  - Another nested  ✅ (consistent 2-space indent)

```text

### 📋 MD025 - Multiple Top-Level Headings (Single H1)

**Issue**: Multiple H1 (#) headings in the same document.

**Why Manual Fix Required**:

- Document structure and hierarchy decisions
- Semantic meaning of top-level headings
- May require content reorganization
- Affects document outline and navigation

**Example**:

```markdown

❌ Before:

# First Heading  ❌ (first H1)

Content here...

# Second Heading  ❌ (second H1 - violates single-title rule)

More content...

✅ After:

# Main Title  ✅ (single H1)

## First Section  ✅ (use H2 for sections)

Content here...

## Second Section  ✅ (use H2 for sections)

More content...

```text

### 📋 MD047 - Files Should End with Single Trailing Newline

**Issue**: Files missing final newline character.

**Why Manual Fix Required**:

- File-level operation requiring file system access
- May affect multiple files simultaneously
- Risk of unintended file modifications
- Best handled by version control or editor settings

**Example**:

```markdown

❌ Before:
Content here...❌ (no newline at end)

✅ After:
Content here...
✅ (ends with newline)

```text

### 📋 MD036 - Emphasis Used Instead of Headings

**Issue**: Bold/italic emphasis used where headings would be more appropriate.

**Why Manual Fix Required**:

- Requires semantic understanding of content
- Context-dependent decision making
- May change document structure
- Affects readability and organization

**Example**:

```markdown

❌ Before:
**Important Section**

Some content here...

✅ After:

## Important Section

Some content here...

```text

### 📋 MD029 - Ordered List Item Prefix

**Issue**: Ordered list items should start with sequential numbers.

**Why Manual Fix Required**:

- Complex nested list structures
- Context-dependent numbering
- May require content reorganization
- Risk of breaking list semantics

**Example**:

```markdown

❌ Before:

1. First item
1. Second item  ❌ (should be 2)
1. Third item   ❌ (should be 3)

✅ After:

1. First item
2. Second item  ✅
3. Third item   ✅

```text

### 📋 MD024 - Multiple Headings with Same Content

**Issue**: Duplicate heading text found in document.

**Why Manual Fix Required**:

- Requires semantic understanding
- May need content restructuring
- Context-dependent resolution
- Affects document navigation

**Example**:

```markdown

❌ Before:

## Introduction

Content about introduction...

## Introduction  ❌ (duplicate)

More content...

✅ After:

## Introduction

Content about introduction...

## Advanced Topics  ✅ (unique)

More content...

### 📋 MD004 - Inconsistent Unordered List Style

**Issue**: Mixed use of `*`, `-`, and `+` for unordered lists.

**Why Manual Fix Required**:

- Document-wide consistency decisions
- May affect visual style
- Context-dependent choices
- Potential for large-scale changes

**Example**:

```markdown
❌ Before:

* Item one
- Item two  ❌ (inconsistent)
+ Item three ❌ (inconsistent)

✅ After:

- Item one
- Item two  ✅ (consistent)
- Item three ✅ (consistent)

```text

## 🎯 Recommended Workflow

### 1. Run Auto-Fix First

```bash
python tests/lint/fix-markdown.py
```text

### 2. Check Remaining Issues

```bash
python tests/lint/lint-markdown.py docs/
```text

### 3. Manual Fix Strategy

**Priority Order for Manual Fixes**:

1. **MD060** - Table alignment (most visible, affects readability)
2. **MD036** - Emphasis to headings (improves structure)
3. **MD029** - Ordered list prefixes (logical sequencing)
4. **MD024** - Duplicate headings (navigation clarity)
5. **MD004** - List style consistency (visual uniformity)

### 4. Verify Zero Tolerance

```bash
python tests/lint/lint-markdown.py docs/

# Should show: "✅ Markdown linting passed - no issues found"
```

## 📊 Issue Type Breakdown

**Current Distribution** (as of last check):

- **MD013** (Line length): 50 issues - Can be partially auto-fixed
- **MD030** (List spacing): 48 issues - **Manual fix required**
- **MD036** (Emphasis): 11 issues - **Manual fix required**
- **MD031** (Code blocks): 9 issues - Can be auto-fixed
- **MD004** (List style): 8 issues - **Manual fix required**
- **MD032** (List blanks): 6 issues - Can be partially auto-fixed
- **MD029** (Ordered lists): 3 issues - **Manual fix required**
- **MD025** (Multiple H1): 0 issues - **Manual fix required** (document structure)
- **MD005** (List indent): 0 issues - **Manual fix required** (complex nesting)
- **MD047** (Newlines): 2 issues - Can be auto-fixed
- **MD026** (Headings): 2 issues - Can be auto-fixed
- **MD024** (Duplicates): 1 issue - **Manual fix required**
- **MD022** (Heading blanks): 1 issue - Can be auto-fixed
- **MD060** (Tables): 0 issues - **Now fully resolved!** ✅

## 💡 Best Practices

### For Auto-Fixable Issues

- Run auto-fix regularly during development
- Commit auto-fixed changes separately
- Review auto-fixed changes for unintended consequences

### For Manual-Fix Issues

- Fix in batches by issue type
- Test changes in isolation
- Maintain documentation quality
- Preserve semantic meaning

### For Table Alignment (MD060)

- Use consistent column widths
- Align pipes vertically
- Pad shorter content with spaces
- Verify alignment visually

## 🔍 Troubleshooting

**Issue**: Auto-fix doesn't resolve all problems

- **Solution**: Manual review required for complex issues
- **Tools**: Use `pymarkdown scan filename.md` for detailed analysis

**Issue**: Tables still show as misaligned

- **Solution**: Check pipe positions with character counting
- **Tool**: `python -c "print([i for i,char in enumerate(line) if char=='|'])"`

**Issue**: Line wrapping breaks code/formatting

- **Solution**: Exclude code blocks and tables from auto-wrapping
- **Manual**: Handle long lines in sensitive areas carefully

## 📚 Resources

- **pymarkdownlnt documentation**: Comprehensive rule explanations
- **Markdown specification**: Official syntax guide
- **CommonMark**: Standard markdown reference

## 🎓 Learning Resources

Understanding which issues require manual fixing helps maintain:

- **Documentation quality**
- **Consistent formatting**
- **Readability standards**
- **Automation efficiency**

Manual fixes, while requiring more effort, often result in better overall document structure and clarity.
