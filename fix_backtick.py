#!/usr/bin/env python3
"""
Fix the backtick syntax error in streamlit_app.py
"""

def fix_syntax_error():
    """Fix the backtick character causing syntax error"""
    
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Fix the backtick issue
        content = content.replace('"}`', '"}')
        
        # Write the corrected content
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed backtick syntax error")
        
        # Test compilation
        try:
            compile(content, 'streamlit_app.py', 'exec')
            print("✅ File compiles successfully")
            return True
        except SyntaxError as e:
            print(f"⚠️ Syntax error still present: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_syntax_error()