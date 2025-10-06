#!/usr/bin/env python3
"""
Fix triple quotes in the complete CRM file
"""

def fix_triple_quotes(filename):
    print(f"Fixing triple quotes in {filename}...")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count triple quotes
        triple_count = content.count('"""')
        print(f"Found {triple_count} triple quotes")
        
        if triple_count % 2 != 0:
            print("❌ Odd number of triple quotes detected!")
            
            # Find potential issues
            lines = content.split('\n')
            in_string = False
            quote_positions = []
            
            for i, line in enumerate(lines):
                if '"""' in line:
                    quote_positions.append((i+1, line.strip()))
            
            print(f"\nTriple quote positions:")
            for line_num, line_content in quote_positions:
                print(f"Line {line_num}: {line_content}")
                
            # Try to fix by adding a closing quote at the end if needed
            if triple_count % 2 != 0:
                print("\n🔧 Attempting to fix by adding closing quote...")
                content += '\n"""'
                print("✅ Added closing triple quote")
                
                # Write fixed version
                fixed_filename = filename.replace('.py', '_FIXED.py')
                with open(fixed_filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed version saved as {fixed_filename}")
                return fixed_filename
        else:
            print("✅ Triple quotes are balanced")
            return filename
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🔧 FIXING COMPLETE CRM FILE")
    print("="*50)
    
    fixed_file = fix_triple_quotes("streamlit_app_clean.py")
    
    if fixed_file:
        print(f"\n🧪 Testing syntax of fixed file...")
        import subprocess
        result = subprocess.run(['python', '-m', 'py_compile', fixed_file], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Syntax is now valid!")
            print(f"🚀 Ready to deploy: {fixed_file}")
        else:
            print(f"❌ Still has syntax errors: {result.stderr}")
    else:
        print("❌ Could not fix the file")