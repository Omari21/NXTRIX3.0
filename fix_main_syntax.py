#!/usr/bin/env python3
"""
Fix the meta tag syntax error in main function
"""

def fix_main_function_syntax():
    """Fix the syntax error in main function"""
    
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Fix the specific syntax error pattern
        old_pattern = '''    st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    """
    # Initialize backend connection
    init_database_connection()

, unsafe_allow_html=True)'''
        
        new_pattern = '''    st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    """, unsafe_allow_html=True)
    
    # Initialize backend connection
    init_database_connection()'''
        
        content = content.replace(old_pattern, new_pattern)
        
        # Write the corrected content
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed main function syntax error")
        
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
    fix_main_function_syntax()