#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def check_exact_lines(filename, start, end):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i in range(start-1, min(end, len(lines))):
            line = lines[i]
            print(f"Line {i+1:4d}: {repr(line)}")
            
            # Check indentation
            leading_spaces = len(line) - len(line.lstrip(' '))
            leading_tabs = len(line) - len(line.lstrip('\t'))
            print(f"        Spaces: {leading_spaces}, Tabs: {leading_tabs}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_exact_lines("streamlit_app.py", 2730, 2738)