#!/usr/bin/env python3
"""
Fix specific syntax errors in streamlit_app.py
"""

def fix_syntax_errors():
    """Fix known syntax errors"""
    
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix double quotes before emoji
        content = content.replace('expander(""📋', 'expander("📋')
        content = content.replace('expander(""', 'expander("')
        
        # Fix any other double quote issues
        content = content.replace('"""', '""')  # Remove triple quotes where they shouldn't be
        
        # Write back
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed syntax errors")
        
        # Test compilation
        try:
            compile(content, 'streamlit_app.py', 'exec')
            print("✅ File compiles successfully")
            return True
        except SyntaxError as e:
            print(f"⚠️ Remaining syntax error at line {e.lineno}: {e.msg}")
            lines = content.split('\n')
            if e.lineno <= len(lines):
                print(f"Line {e.lineno}: {repr(lines[e.lineno-1])}")
            return False
        
    except Exception as e:
        print(f"❌ Error fixing syntax: {e}")
        return False

if __name__ == "__main__":
    fix_syntax_errors()