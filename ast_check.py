#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast

def check_syntax_errors(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the file with AST
        try:
            ast.parse(content)
            print("File syntax is valid!")
            return True
        except SyntaxError as e:
            print(f"Syntax Error at line {e.lineno}, column {e.offset}: {e.msg}")
            if e.text:
                print(f"Problematic line: {e.text.strip()}")
            return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

if __name__ == "__main__":
    check_syntax_errors("streamlit_app.py")