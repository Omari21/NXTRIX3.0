#!/usr/bin/env python3
"""
Fix all remaining syntax errors in streamlit_app.py
"""

def fix_all_syntax():
    """Fix all syntax errors"""
    
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the specific string literal issue on line 279
        content = content.replace('st.warning(f")"U% {message}")', 'st.warning(f"⚠️ {message}")')
        
        # Fix any other malformed f-strings
        content = content.replace('f")"', 'f"⚠️')
        content = content.replace(')"U%', '⚠️')
        
        # Fix double quotes before emojis
        content = content.replace('expander(""📋', 'expander("📋')
        content = content.replace('(""', '("')
        
        # Write back
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed all syntax errors")
        
        # Test compilation
        try:
            compile(content, 'streamlit_app.py', 'exec')
            print("✅ File compiles successfully!")
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
    fix_all_syntax()