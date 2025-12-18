#!/usr/bin/env python3

with open('docs/SEARCH.md', 'r') as f:
    content = f.read()

# The issue is around line 659 - let's find the exact pattern
# and replace 3 blank lines with 2 blank lines between code block and heading

# Find the specific pattern
old_pattern = '''   ```text




### LLM doesn't use the context'''

new_pattern = '''   ```text



### LLM doesn't use the context'''

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    print('Found and replaced the pattern!')
else:
    print('Pattern not found, trying alternative approach')
    # Try with different spacing
    old_pattern2 = '''   ```text





### LLM doesn't use the context'''
    new_pattern2 = '''   ```text



### LLM doesn't use the context'''
    if old_pattern2 in content:
        content = content.replace(old_pattern2, new_pattern2)
        print('Found and replaced the alternative pattern!')

with open('docs/SEARCH.md', 'w') as f:
    f.write(content)

print('Done!')