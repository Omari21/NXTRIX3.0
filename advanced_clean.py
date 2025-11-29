#!/usr/bin/env python3
"""
Advanced cleaning for streamlit_app.py to fix encoding and character issues
"""
import re

def advanced_clean():
    """Advanced cleaning of streamlit_app.py"""
    
    try:
        # Read with error handling
        with open('streamlit_app.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Fix common encoding issues
        # Replace problematic Unicode characters
        content = re.sub(r'[^\x00-\x7F\u00A0-\uFFFF]', '', content)  # Remove invalid chars
        content = content.replace('\u0092', "'")  # Replace with proper apostrophe
        content = content.replace('\u201c', '"')  # Replace with proper quotes
        content = content.replace('\u201d', '"')  # Replace with proper quotes
        content = content.replace('\u2019', "'")  # Replace with proper apostrophe
        content = content.replace('\u2013', '-')  # Replace en dash
        content = content.replace('\u2014', '--') # Replace em dash
        
        # Fix specific problematic patterns
        content = re.sub(r'"a"[^\w\s]*Technical Details"', '"📋 Technical Details"', content)
        content = re.sub(r'"[^\w\s]*Technical Details"', '"📋 Technical Details"', content)
        
        # Remove null bytes and other problematic characters
        content = re.sub(r'\x00', '', content)
        content = re.sub(r'[\x80-\x9F]', '', content)  # Remove Windows-1252 control chars
        
        # Write back cleaned content
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Advanced cleaning completed")
        
        # Test compilation
        try:
            compile(content, 'streamlit_app.py', 'exec')
            print("✅ File compiles successfully after cleaning")
            return True
        except SyntaxError as e:
            print(f"⚠️ Syntax error at line {e.lineno}: {e.msg}")
            return False
        
    except Exception as e:
        print(f"❌ Error during advanced cleaning: {e}")
        return False

if __name__ == "__main__":
    advanced_clean()