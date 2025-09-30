#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tokenize
import io

def find_syntax_issue(filename):
    try:
        with open(filename, 'rb') as f:
            try:
                tokens = tokenize.tokenize(f.readline)
                for token in tokens:
                    pass  # Just iterate through all tokens
                print("File tokenizes successfully - no syntax errors found")
            except tokenize.TokenError as e:
                print(f"Token Error: {e}")
                return False
            except IndentationError as e:
                print(f"Indentation Error at line {e.lineno}: {e.msg}")
                return False
            except SyntaxError as e:
                print(f"Syntax Error at line {e.lineno}: {e.msg}")
                return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    find_syntax_issue("streamlit_app.py")