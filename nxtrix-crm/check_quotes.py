#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def check_quote_chars(filename, line_num):
    try:
        with open(filename, 'rb') as f:
            lines = f.read().split(b'\n')
            if line_num <= len(lines):
                line_bytes = lines[line_num - 1]
                print(f"Line {line_num} raw bytes: {line_bytes}")
                
                # Find all quote-like characters
                quote_positions = []
                for i, byte in enumerate(line_bytes):
                    if byte in [34, 39]:  # " and '
                        quote_positions.append((i, chr(byte), byte))
                
                print("Quote characters found:")
                for pos, char, byte_val in quote_positions:
                    print(f"  Position {pos}: '{char}' (byte {byte_val})")
                
                # Check for unusual quote characters
                for i, byte in enumerate(line_bytes):
                    if byte > 127:  # Non-ASCII
                        print(f"  Position {i}: Non-ASCII byte {byte} ({hex(byte)})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_quote_chars("streamlit_app.py", 2735)