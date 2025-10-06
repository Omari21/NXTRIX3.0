#!/usr/bin/env python3
"""
Fix UnboundLocalError in show_ai_insights function
"""

def fix_ai_insights():
    """Fix the UnboundLocalError in show_ai_insights function"""
    
    try:
        # Read the file with proper encoding handling
        with open('streamlit_app.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        # Fallback to different encoding
        with open('streamlit_app.py', 'r', encoding='latin-1') as f:
            content = f.read()
    
    lines = content.split('\n')
    
    # Find the problematic section
    for i, line in enumerate(lines):
        # Look for the line with the second assignment to real_insights
        if 'real_insights = [' in line and 'No portfolio data yet' in lines[i+1] if i+1 < len(lines) else False:
            print(f"Found problematic real_insights assignment at line {i+1}")
            
            # Look backwards to find the end of the if block
            for j in range(i-1, max(0, i-20), -1):
                if lines[j].strip() == ']':
                    print(f"Found end of first real_insights at line {j+1}")
                    # Insert else: before the second assignment
                    lines[i] = '        else:\n            ' + lines[i].strip()
                    
                    # Write the fixed content back
                    try:
                        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
                            f.write('\n'.join(lines))
                    except Exception:
                        with open('streamlit_app.py', 'w', encoding='latin-1') as f:
                            f.write('\n'.join(lines))
                    
                    print("✅ Fixed UnboundLocalError in show_ai_insights function")
                    return True
                    
            print("❌ Could not find the structure to fix")
            return False
    
    print("❌ Could not find the problematic pattern")
    return False

if __name__ == "__main__":
    fix_ai_insights()