#!/usr/bin/env python3
"""
Ultra-aggressive cleaning to fix all encoding issues
"""
import re

def ultra_clean():
    """Ultra-aggressive cleaning of streamlit_app.py"""
    
    try:
        # Read with multiple fallback encodings
        content = None
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open('streamlit_app.py', 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                break
            except:
                continue
        
        if content is None:
            print("❌ Could not read file with any encoding")
            return False
        
        # Ultra-aggressive character replacement
        # Keep only ASCII printable characters and safe Unicode
        cleaned_lines = []
        for line in content.split('\n'):
            # Remove all non-printable characters except newlines, tabs, spaces
            clean_line = re.sub(r'[^\x20-\x7E\t\n\r]', '', line)
            # Fix specific patterns we know about
            clean_line = clean_line.replace('a"', '"📋')  # Fix the expander issue
            cleaned_lines.append(clean_line)
        
        clean_content = '\n'.join(cleaned_lines)
        
        # Write back as clean UTF-8
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(clean_content)
        
        print("✅ Ultra-aggressive cleaning completed")
        
        # Test compilation
        try:
            compile(clean_content, 'streamlit_app.py', 'exec')
            print("✅ File compiles successfully after ultra-cleaning")
            return True
        except SyntaxError as e:
            print(f"⚠️ Syntax error at line {e.lineno}: {e.msg}")
            # Show the problematic line
            lines = clean_content.split('\n')
            if e.lineno <= len(lines):
                print(f"Problematic line: {repr(lines[e.lineno-1])}")
            return False
        
    except Exception as e:
        print(f"❌ Error during ultra-cleaning: {e}")
        return False

if __name__ == "__main__":
    ultra_clean()