#!/usr/bin/env python3
"""
Quick fix for UnboundLocalError in show_deal_database function
"""

def fix_streamlit_app():
    """Fix the UnboundLocalError in streamlit_app.py"""
    
    # Read the file
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix the problematic pattern
    # The issue is a missing "else:" before the second deals assignment
    
    problematic_pattern = """    # Get deals from database
    if search_term:
        deals = db_service.search_deals(search_term)

        deals = db_service.get_deals()"""
    
    fixed_pattern = """    # Get deals from database
    if search_term:
        deals = db_service.search_deals(search_term)
    else:
        deals = db_service.get_deals()"""
    
    if problematic_pattern in content:
        print("Found problematic pattern, fixing...")
        content = content.replace(problematic_pattern, fixed_pattern)
        
        # Write the fixed content back
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed UnboundLocalError in show_deal_database function")
        return True
    else:
        print("❌ Problematic pattern not found exactly, checking for variations...")
        
        # Check for the key indicators
        if "deals = db_service.search_deals(search_term)" in content and "deals = db_service.get_deals()" in content:
            lines = content.split('\n')
            
            # Find the lines and fix them
            for i, line in enumerate(lines):
                if "deals = db_service.search_deals(search_term)" in line:
                    print(f"Found search_deals at line {i+1}")
                    # Look for the next few lines
                    for j in range(i+1, min(i+5, len(lines))):
                        if "deals = db_service.get_deals()" in lines[j]:
                            print(f"Found get_deals at line {j+1}")
                            # Check if there's an else before it
                            if j > 0 and "else:" not in lines[j-1]:
                                print("Adding missing else:")
                                # Insert else before this line
                                lines[j] = "    else:\n" + lines[j]
                                
                                # Write the fixed content
                                with open('streamlit_app.py', 'w', encoding='utf-8') as f:
                                    f.write('\n'.join(lines))
                                
                                print("✅ Fixed UnboundLocalError by adding missing else:")
                                return True
                            break
            
        print("❌ Could not automatically fix the issue")
        return False

if __name__ == "__main__":
    fix_streamlit_app()