#!/usr/bin/env python3
"""
Careful restoration and cleaning of streamlit_app.py
"""

def careful_restore():
    """Carefully restore and clean the streamlit app"""
    
    try:
        # Read the original full version with binary mode to preserve structure
        with open('full_streamlit_app.py', 'rb') as f:
            content = f.read()
        
        # Remove only null bytes, preserve everything else
        content = content.replace(b'\x00', b'')
        
        # Decode carefully
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            # Try with error replacement
            text_content = content.decode('utf-8', errors='replace')
            # Replace replacement characters with safe alternatives
            text_content = text_content.replace('\ufffd', '')
        
        # Only fix obvious syntax issues without being aggressive
        # Fix known problematic patterns
        lines = text_content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Check for unterminated strings and obvious issues
            if 'st.markdown("' in line and not line.count('"') % 2 == 0:
                # This might be a multi-line string, let's be careful
                # Look ahead to see if it's actually meant to be multi-line
                if i + 1 < len(lines) and '<' in lines[i + 1]:
                    # Looks like HTML content, make it a proper multi-line string
                    line = line.replace('st.markdown("', 'st.markdown("""')
                    # Find the end of this HTML block
                    for j in range(i + 1, min(i + 50, len(lines))):
                        if '</script>' in lines[j] or '</style>' in lines[j]:
                            lines[j] = lines[j] + '""")'
                            break
            
            fixed_lines.append(line)
        
        final_content = '\n'.join(fixed_lines)
        
        # Write the carefully restored version
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print("✅ Carefully restored streamlit_app.py")
        
        # Test compilation
        try:
            compile(final_content, 'streamlit_app.py', 'exec')
            print("✅ File compiles successfully!")
            return True
        except SyntaxError as e:
            print(f"⚠️ Syntax error at line {e.lineno}: {e.msg}")
            # Show context
            lines = final_content.split('\n')
            start = max(0, e.lineno - 3)
            end = min(len(lines), e.lineno + 2)
            for i in range(start, end):
                marker = ">>> " if i == e.lineno - 1 else "    "
                print(f"{marker}{i+1}: {lines[i]}")
            return False
        
    except Exception as e:
        print(f"❌ Error during careful restoration: {e}")
        return False

if __name__ == "__main__":
    careful_restore()