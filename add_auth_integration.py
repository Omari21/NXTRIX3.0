#!/usr/bin/env python3
"""
Add authentication integration and expanded navigation to streamlit_app.py
"""

def add_auth_integration():
    """Add authentication integration to main function"""
    
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find the main function and add authentication
        lines = content.split('\n')
        modified_lines = []
        in_main_function = False
        auth_added = False
        
        for i, line in enumerate(lines):
            modified_lines.append(line)
            
            # Look for the main function
            if 'def main():' in line:
                in_main_function = True
                print(f"Found main function at line {i+1}")
            
            # Add authentication right before navigation
            if (in_main_function and not auth_added and 
                ('redirect_page = get_current_page()' in line or 'Navigation' in line)):
                
                print(f"Adding authentication integration before line {i+1}")
                auth_code = [
                    "",
                    "    # === AUTHENTICATION INTEGRATION ===",
                    "    # Initialize authentication state",
                    "    if 'user_authenticated' not in st.session_state:",
                    "        st.session_state.user_authenticated = False",
                    "        st.session_state.user_email = None", 
                    "        st.session_state.user_tier = 'free'",
                    "        st.session_state.is_admin = False",
                    "",
                    "    # Show authentication UI if not authenticated",
                    "    if not st.session_state.user_authenticated:",
                    "        show_authentication_ui()",
                    "        return  # Don't show the rest of the app until authenticated",
                    ""
                ]
                
                # Insert authentication code before current line
                modified_lines = modified_lines[:-1] + auth_code + [line]
                auth_added = True
        
        # Now update navigation options
        for i, line in enumerate(modified_lines):
            if 'navigation_options = [' in line and 'Dashboard' in line:
                print(f"Updating navigation options at line {i+1}")
                
                # Replace with dynamic navigation
                nav_code = [
                    "    # Define navigation options based on user authentication and permissions",
                    "    if st.session_state.get('user_authenticated', False):",
                    "        # Full navigation for authenticated users",
                    "        navigation_options = [",
                    '            "📊 Dashboard",',
                    '            "🏠 Deal Analysis",', 
                    '            "💹 Advanced Financial Modeling",',
                    '            "🗄️ Deal Database",',
                    '            "📈 Portfolio Analytics",',
                    '            "🏛️ Investor Portal",',
                    '            "🤝 Enhanced CRM",',
                    '            "🎯 Enhanced Deal Manager",',
                    '            "👥 Client Manager",', 
                    '            "📞 Communication Center",',
                    '            "⚡ Workflow Automation",',
                    '            "📋 Task Management",',
                    '            "🎯 Lead Scoring",',
                    '            "🔔 Smart Notifications",',
                    '            "📊 Advanced Reporting",',
                    '            "🤖 AI Email Templates",',
                    '            "📱 SMS Marketing",',
                    '            "🧠 AI Insights",',
                    '            "👥 Investor Matching"',
                    "        ]",
                    "",
                    "        # Add admin pages if user is admin",
                    "        if st.session_state.get('is_admin', False):",
                    "            navigation_options.extend([",
                    '                "🔧 Performance Dashboard",',
                    '                "🗄️ Database Health",', 
                    '                "📊 System Monitor",',
                    '                "🔍 Database Diagnostic"',
                    "            ])",
                    "",            
                    "        # Add user profile option",
                    '        navigation_options.append("👤 Profile & Settings")',
                    "",        
                    "    else:",
                    "        # Limited navigation for non-authenticated users",
                    "        navigation_options = [",
                    '            "🔐 Login / Register",',
                    '            "📊 Dashboard (Demo)",',
                    '            "🏠 Deal Analysis (Demo)",',
                    '            "💹 Financial Modeling (Demo)"',
                    "        ]"
                ]
                
                # Replace the navigation line
                modified_lines[i] = '\n'.join(nav_code)
                break
        
        # Write the modified content
        final_content = '\n'.join(modified_lines)
        
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print("✅ Successfully added authentication integration and expanded navigation")
        
        # Test compilation
        try:
            compile(final_content, 'streamlit_app.py', 'exec')
            print("✅ File compiles successfully")
            return True
        except SyntaxError as e:
            print(f"⚠️ Syntax error: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    add_auth_integration()