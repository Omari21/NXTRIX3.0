#!/usr/bin/env python3
"""
Simple fix for the syntax error
"""

def fix_syntax_simple():
    """Simple fix for the meta tag syntax error"""
    
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Replace the problematic section
        content = content.replace(
            '    """\n    # Initialize backend connection\n    init_database_connection()\n\n, unsafe_allow_html=True)',
            '    """, unsafe_allow_html=True)\n    \n    # Initialize backend connection\n    init_database_connection()'
        )
        
        # Write the corrected content
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Applied simple syntax fix")
        
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
    fix_syntax_simple()