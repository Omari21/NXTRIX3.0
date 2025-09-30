#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def find_unmatched_quotes(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(filename, 'r', encoding='cp1252') as f:
            content = f.read()
    
    lines = content.split('\n')
    in_triple_quote = False
    quote_char = None
    start_line = None
    
    for i, line in enumerate(lines, 1):
        # Check for triple quotes
        j = 0
        while j < len(line) - 2:
            if line[j:j+3] in ['"""', "'''"]:
                if not in_triple_quote:
                    # Starting a triple quote
                    in_triple_quote = True
                    quote_char = line[j:j+3]
                    start_line = i
                    print(f"Opening triple quote {quote_char} at line {i}: {line.strip()}")
                    j += 3  # Skip past the opening quote
                elif line[j:j+3] == quote_char:
                    # Closing the same type of triple quote
                    in_triple_quote = False
                    print(f"Closing triple quote {quote_char} at line {i}: {line.strip()}")
                    quote_char = None
                    start_line = None
                    j += 3  # Skip past the closing quote
                else:
                    j += 1
            else:
                j += 1
    
    if in_triple_quote:
        print(f"\nERROR: Unclosed triple quote {quote_char} starting at line {start_line}")
        return False
    else:
        print("\nAll triple quotes are properly matched")
        return True

if __name__ == "__main__":
    success = find_unmatched_quotes("streamlit_app.py")
    if not success:
        exit(1)