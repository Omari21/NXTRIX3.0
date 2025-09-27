#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def check_mixed_indentation(filename, start, end):
    try:
        with open(filename, 'rb') as f:
            lines = f.read().split(b'\n')
        
        for i in range(start-1, min(end, len(lines))):
            line = lines[i]
            if line.strip():  # Only check non-empty lines
                # Check for mixed tabs and spaces
                has_tabs = b'\t' in line
                has_spaces = b' ' in line[:20]  # Check first 20 chars for indentation
                
                leading_whitespace = []
                for byte in line:
                    if byte == 32:  # space
                        leading_whitespace.append('S')
                    elif byte == 9:  # tab
                        leading_whitespace.append('T')
                    else:
                        break
                
                whitespace_pattern = ''.join(leading_whitespace)
                
                print(f"Line {i+1:4d}: {whitespace_pattern} -> {line[:50].decode('utf-8', errors='replace')}...")
                
                if has_tabs and has_spaces and whitespace_pattern:
                    print(f"  WARNING: Mixed tabs and spaces!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mixed_indentation("streamlit_app.py", 2720, 2740)