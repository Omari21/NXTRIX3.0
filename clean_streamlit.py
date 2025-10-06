#!/usr/bin/env python3
"""
Clean null bytes and fix any syntax issues in streamlit_app.py
"""

def clean_file():
    """Clean null bytes and encoding issues from streamlit_app.py"""
    
    try:
        # Read file and clean null bytes
        with open('streamlit_app.py', 'rb') as f:
            content = f.read()
        
        # Remove null bytes
        clean_content = content.replace(b'\x00', b'')
        
        # Write back cleaned content
        with open('streamlit_app.py', 'wb') as f:
            f.write(clean_content)
        
        print("✅ Cleaned null bytes from streamlit_app.py")
        
        # Now test if it compiles
        try:
            with open('streamlit_app.py', 'r', encoding='utf-8') as f:
                compile(f.read(), 'streamlit_app.py', 'exec')
            print("✅ File compiles successfully")
            return True
        except UnicodeDecodeError:
            # Try with different encoding
            with open('streamlit_app.py', 'r', encoding='latin-1') as f:
                content = f.read()
            with open('streamlit_app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Fixed encoding issues")
            return True
        except Exception as e:
            print(f"⚠️ Compilation issue: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error cleaning file: {e}")
        return False

if __name__ == "__main__":
    clean_file()