# MD060-Compliant Table Creation Guide for AI Agents

## 🎯 Purpose

This guide ensures AI agents create properly formatted markdown tables that
comply with **MD060** (table column alignment) rules. All tables must have
vertically aligned pipes for consistent formatting.

## 🚀 Quick Start

### Command Line Usage

```bash

# Create a simple table

python tools/create_md_table.py "Metric,Before,After,Change" "Total
Tests,256,360,+104" "Coverage,50%,53%,+3%"

```text

### Python Module Usage

```python
from tools.create_md_table import create_md060_table

headers = ["Metric", "Before", "After", "Change"]
rows = [
    ["Total Tests", "256", "**360**", "+104 tests (+41%)"],
    ["Coverage", "50%", "**53%**", "+3%"],
]

table = create_md060_table(headers, rows)
print(table)

## ✅ MD060 Compliance Rules

### What MD060 Requires

1. **Vertical Pipe Alignment**: All pipes (`|`) must be at identical character

positions in every row

1. **Consistent Column Widths**: Each column must have the same width across all

rows

1. **Proper Separator**: Separator row must align with header and content

### Visual Example

```markdown

✅ CORRECT (MD060 Compliant):
| Metric          | Before   | After   | Change            | [0, 23, 34, 44, 64] |
| --------------- | -------- | ------- | ----------------- | [0, 23, 34, 44, 64] |
| **Total Tests** | 256      | **360** | +104 tests (+41%) | [0, 23, 34, 44, 64] |

❌ INCORRECT (MD060 Violation):
| Metric          | Before   | After   | Change                                      | [0, 9, 18, 26, 35] |
| --------------- | -------- | ------- | -------------------------------------------- | [0, 9, 18, 26, 35] |
| **Total Tests** | 256      | **360** | +104...  [0, 18, 24, 34, 54] ❌ (misaligned) | ------------------ |

## 📋 Table Creation Guidelines

### 1. Always Use the Table Generator

**❌ Never manually create tables** - always use `create_md_table.py`

**✅ Always use the tool** for guaranteed MD060 compliance

### 2. Data Preparation

#### Simple Data

```python
headers = ["Header1", "Header2", "Header3"]
rows = [
    ["Row1Col1", "Row1Col2", "Row1Col3"],
    ["Row2Col1", "Row2Col2", "Row2Col3"],
]

```text

#### Complex Data with Formatting

```python
headers = ["Module", "Coverage", "Status"]
rows = [
    ["`launcher.py`", "98%", "✅"],           # Code formatting
    ["**`config.py`**", "100%", "✅"],       # Bold + code
    ["`memory_commands.py`", "100%", "✅"], # Just code
]

```text

### 3. Handling Special Cases

#### Empty Cells

```python
rows = [
    ["Item1", "Value1", ""],    # Empty cell
    ["Item2", "", "Value2"],    # Empty middle cell
]

```text

#### Long Content

```python
rows = [
    ["Description", "This is a very long description that will be properly
padded to maintain alignment"],
    ["Short", "Short"],
]

```text

#### Numeric Data

```python
rows = [
    ["Metric1", "1234", "5678"],
    ["Metric2", "90", "12345"],  # Different digit counts
]

## 🎨 Advanced Features

### Markdown Formatting Support

The table generator automatically handles:

- **Bold**: `**text**` → **text**
- **Italic**: `*text*` → *text*
- **Code**: `` `code` `` → `code`
- **Bold Code**: `**`code`**` → **`code`**
- **Emoji**: `✅`, `❌`, `🎉`

### Column Width Calculation

The tool automatically:

1. Calculates maximum width needed for each column
2. Accounts for markdown formatting characters
3. Pads all cells to consistent widths
4. Ensures perfect pipe alignment

## 🔧 Integration with AI Workflows

### For Content Generation Agents

```python

# When generating reports with tables

def generate_coverage_report():
    # Collect data
    modules = get_module_data()
    
    # Prepare table data
    headers = ["Module", "Coverage", "Tests", "Status"]
    rows = []
    
    for module in modules:
        row = [
            f"`{module.name}.py`",
            f"{module.coverage}%",
            f"{module.tests}",
            "✅" if module.coverage >= 90 else "⚠️"
        ]
        rows.append(row)
    
    # Generate MD060-compliant table
    table = create_md060_table(headers, rows)
    
    # Include in markdown report
    report = f"""

# Coverage Report

{table}

*Generated: {datetime.now()}*
"""
    return report

```text

### For Documentation Agents

```python

# When creating API documentation

def generate_api_table(endpoints):
    headers = ["Endpoint", "Method", "Description", "Status"]
    rows = []
    
    for endpoint in endpoints:
        row = [
            f"`{endpoint.path}`",
            endpoint.method.upper(),
            endpoint.description,
            "✅ Active" if endpoint.active else "❌ Deprecated"
        ]
        rows.append(row)
    
    return create_md060_table(headers, rows)

```text

## 📊 Common Table Patterns

### Comparison Tables

```python

headers = ["Metric", "Before", "After", "Change", "Status"]
rows = [
    ["Total Tests", "256", "**360**", "+104 (+41%)", "✅ Improved"],
    ["Coverage", "50%", "**53%**", "+3%", "✅ Improved"],
    ["Modules ≥90%", "9", "**16**", "+7 (+78%)", "✅ Excellent"],
]

```text

### Status Tables

```python

headers = ["#", "Component", "Status", "Version", "Last Updated"]
rows = [
    ["1", "`core/context.py`", "✅ Active", "v1.2.3", "2025-12-18"],
    ["2", "`storage/database.py`", "✅ Active", "v1.1.5", "2025-12-15"],
    ["3", "`legacy_commands.py`", "⚠️ Deprecated", "v0.9.8", "2025-11-20"],
]

```text

### Feature Matrices

```python

headers = ["Feature", "CLI", "GUI", "API", "Notes"]
rows = [
    ["Learning Commands", "✅", "✅", "✅", "All interfaces supported"],
    ["VectorDB Integration", "✅", "✅", "❌", "API planned Q1 2026"],
    ["Multi-Space Support", "✅", "✅", "✅", "Full support"],
]

```text

## 🎯 Validation and Testing

### Verify Table Compliance

```bash

# Check if your table is MD060 compliant

echo "your_table_here" | pymarkdown scan - | grep MD060 || echo "✅ MD060
Compliant!"

```text

### Test Table Alignment

```python

# Programmatic validation

def validate_table_alignment(table_str):
    lines = table_str.split('\n')
    pipe_positions = []
    
    for line in lines:
        if line.startswith('|') and line.endswith('|'):
            positions = [i for i, char in enumerate(line) if char == '|']
            pipe_positions.append(positions)
    
    # Check if all pipe positions are identical
    if len(set(tuple(p) for p in pipe_positions)) == 1:
        return True, "✅ Perfectly aligned"
    else:
        return False, f"❌ Misaligned: {pipe_positions}"

```text

## ❌ Common Mistakes to Avoid

### 1. Manual Table Creation

```markdown

❌ Don't do this:
| A   | B   |
| --- | --- |
| 1   | 2   |

```text

### 2. Inconsistent Column Counts

```python

❌ Wrong:
headers = ["A", "B", "C"]
rows = [
    ["1", "2"],           # Missing column!
    ["3", "4", "5"],     # Correct count
]

```text

### 3. Ignoring Markdown Formatting

```python

❌ Wrong:
rows = [
    ["**Bold Text**", "Normal"],  # Bold affects width!
    ["Short", "Long text"],       # Different widths
]

```text

### 4. Mixing Data Types Without Planning

```python

❌ Wrong:
rows = [
    ["Short", "123456789012345678901234567890"],  # Very different lengths
    ["Medium Length", "123"],
]

## 📚 Best Practices

### 1. Plan Column Structure First

- Determine all possible content lengths
- Consider markdown formatting impact
- Plan for future data growth

### 2. Use Consistent Formatting

- Apply bold/italic consistently
- Use code formatting for technical terms
- Standardize emoji usage

### 3. Test Before Committing

- Validate with `pymarkdown scan`
- Check visual alignment
- Verify readability

### 4. Document Table Purpose

- Add descriptive captions
- Include context when needed
- Explain complex data

## 🎓 Training Examples

### Example 1: Simple Status Table

**Input**:

```python
headers = ["Component", "Status", "Version"]
rows = [
    ["Core Engine", "✅ Active", "v2.1.0"],
    ["VectorDB Client", "✅ Active", "v1.5.2"],
    ["Legacy Commands", "⚠️ Deprecated", "v0.9.8"],
]

```text

**Output**:

```markdown
| Component          | Status       | Version  |
| ------------------ | ------------- | -------- |
| Core Engine        | ✅ Active     | v2.1.0   |
| VectorDB Client    | ✅ Active     | v1.5.2   |
| Legacy Commands    | ⚠️ Deprecated | v0.9.8   |

```text

### Example 2: Complex Data Table

**Input**:

```python
headers = ["Metric", "Current", "Target", "Progress", "Status"]
rows = [
    ["Test Coverage", "53%", "90%", "▰▰▰▰▰▱▱▱▱ 53%", "✅ On Track"],
    ["Documentation", "85%", "100%", "▰▰▰▰▰▰▰▰▰▱ 85%", "✅ On Track"],
    ["Performance", "95%", "95%", "▰▰▰▰▰▰▰▰▰▰ 95%", "✅ Complete"],
]

```text

**Output**:

```markdown
| Metric          | Current | Target | Progress                    | Status     |
| --------------- | ------- | ------ | ---------------------------- | --------- |
| Test Coverage   | 53%     | 90%    | ▰▰▰▰▰▱▱▱▱ 53%               | ✅ On Track|
| Documentation   | 85%     | 100%   | ▰▰▰▰▰▰▰▰▰▱ 85%              | ✅ On Track|
| Performance     | 95%     | 95%    | ▰▰▰▰▰▰▰▰▰▰ 95%              | ✅ Complete|

## 🔍 Troubleshooting

### Issue: Table Looks Misaligned

**Cause**: Manual editing after generation

**Solution**: Regenerate the table using the tool

### Issue: Pipes Don't Align in Editor

**Cause**: Different fonts/monospace settings

**Solution**: Use monospace font and verify with `pymarkdown scan`

### Issue: Content Gets Truncated

**Cause**: Very long content in one cell

**Solution**: Break content into multiple rows or abbreviate

### Issue: Markdown Formatting Breaks Alignment

**Cause**: Uneven markdown character counts

**Solution**: Let the tool handle formatting automatically

## 📋 Checklist for AI Agents

- [ ] Always use `create_md_table.py` for table creation
- [ ] Prepare data as lists of lists
- [ ] Include all markdown formatting in cell content
- [ ] Verify column counts match headers
- [ ] Test table with `pymarkdown scan`
- [ ] Check visual alignment in preview
- [ ] Document table purpose and context

## 🎯 Zero Tolerance Policy

**All tables must be MD060 compliant** - no exceptions!

- **Automated Creation**: Use the provided tool
- **Automated Validation**: Run linting checks
- **Manual Review**: Verify critical tables
- **Continuous Improvement**: Update tool as needed

By following this guide, AI agents ensure all markdown tables are perfectly
formatted, professionally aligned, and fully compliant with MD060 standards.
