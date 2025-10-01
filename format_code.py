#!/usr/bin/env python3
"""
Simple script to ensure consistent 4-space indentation in Python files.
"""
import os
import sys
import re


def fix_indentation(file_path):
    """Fix indentation to use 4 spaces consistently."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Count leading whitespace
        leading_whitespace = len(line) - len(line.lstrip())
        
        if leading_whitespace > 0:
            # Convert to 4-space indentation
            indent_level = leading_whitespace // 4
            if leading_whitespace % 4 != 0:
                # Round up to next 4-space boundary
                indent_level += 1
            
            # Create proper 4-space indentation
            new_indent = ' ' * (indent_level * 4)
            fixed_line = new_indent + line.lstrip()
        else:
            fixed_line = line
        
        fixed_lines.append(fixed_line)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print(f"Fixed indentation in {file_path}")


def main():
    """Main function to process Python files."""
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        # Find all Python files in current directory
        files = [f for f in os.listdir('.') if f.endswith('.py')]
    
    for file_path in files:
        if os.path.exists(file_path) and file_path.endswith('.py'):
            try:
                fix_indentation(file_path)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")


if __name__ == "__main__":
    main()

