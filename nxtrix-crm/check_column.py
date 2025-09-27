#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def check_column(filename, line_num, col_num):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if line_num <= len(lines):
                line = lines[line_num - 1]
                print(f"Line {line_num}: {repr(line)}")
                print(f"Length: {len(line)}")
                print(f"Column {col_num}: {repr(line[col_num-1:col_num+3]) if col_num <= len(line) else 'Beyond line length'}")
                
                # Show character by character around that position
                start = max(0, col_num - 10)
                end = min(len(line), col_num + 10)
                print(f"Context around column {col_num}:")
                for i in range(start, end):
                    char = line[i] if i < len(line) else 'EOL'
                    marker = ' ^' if i == col_num - 1 else '  '
                    print(f"  {i+1:3d}: {repr(char)}{marker}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_column("streamlit_app.py", 2735, 56)