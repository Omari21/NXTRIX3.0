#!/usr/bin/env python3
"""Script to fix corrupted emoji encoding in enhanced_crm.py"""

# Read the file
with open(r'C:\Users\Mania\OneDrive\Documents\NXTRIX3.0\nxtrix-crm\enhanced_crm.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the corrupted emojis in the navigation list
# The � character appears where emojis should be
original_content = content

# Fix each corrupted emoji individually
content = content.replace('"� Deal Management"', '"💼 Deal Management"')
content = content.replace('"�📞 Contact Management"', '"📞 Contact Management"')
content = content.replace('"� Communication Hub"', '"💬 Communication Hub"')  
content = content.replace('"�📊 Pipeline Analytics"', '"📊 Pipeline Analytics"')

if content != original_content:
    with open(r'C:\Users\Mania\OneDrive\Documents\NXTRIX3.0\nxtrix-crm\enhanced_crm.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed emoji encoding issues in navigation')
    print('✓ Deal Management emoji fixed')
    print('✓ Contact Management emoji fixed') 
    print('✓ Communication Hub emoji fixed')
    print('✓ Pipeline Analytics emoji fixed')
else:
    print('No changes needed')