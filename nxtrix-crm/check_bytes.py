#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def check_line_bytes(filename, line_num):
    try:
        with open(filename, 'rb') as f:
            lines = f.read().split(b'\n')
            if line_num <= len(lines):
                line_bytes = lines[line_num - 1]
                print(f"Line {line_num} raw bytes: {line_bytes}")
                print(f"Line {line_num} decoded: {line_bytes.decode('utf-8', errors='replace')}")
                
                # Check for specific characters
                if b'"""' in line_bytes:
                    print("Found triple quotes in bytes")
                    # Count triple quotes
                    count = line_bytes.count(b'"""')
                    print(f"Number of triple quotes: {count}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_line_bytes("streamlit_app.py", 2735)