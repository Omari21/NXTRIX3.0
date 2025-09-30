#!/usr/bin/env python3
"""
Quick fix script to add unique keys to all plotly_chart elements
"""

import re

def fix_plotly_charts():
    """Add unique keys to all plotly charts in streamlit_app.py"""
    
    # Read the file
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Counter for unique keys
    chart_counter = 1
    
    # Find all plotly_chart instances without keys
    def replace_plotly_chart(match):
        nonlocal chart_counter
        full_match = match.group(0)
        
        # If it already has a key parameter, don't modify
        if 'key=' in full_match:
            return full_match
        
        # Add unique key
        key = f"plotly_chart_{chart_counter}"
        chart_counter += 1
        
        # Insert key parameter before the closing parenthesis
        if full_match.endswith(')'):
            return full_match[:-1] + f', key="{key}")'
        else:
            return full_match + f', key="{key}"'
    
    # Pattern to match st.plotly_chart calls
    pattern = r'st\.plotly_chart\([^)]+\)'
    
    # Replace all matches
    new_content = re.sub(pattern, replace_plotly_chart, content)
    
    # Write back to file
    with open('streamlit_app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Added unique keys to {chart_counter - 1} plotly charts")

if __name__ == "__main__":
    fix_plotly_charts()