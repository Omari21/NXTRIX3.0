#!/usr/bin/env python3
"""
Add missing page handlers for all new navigation options
"""

def add_missing_page_handlers():
    """Add page handlers for all new navigation options"""
    
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find the page routing section and add missing handlers
        lines = content.split('\n')
        modified_lines = []
        
        for i, line in enumerate(lines):
            modified_lines.append(line)
            
            # Add new handlers after the last existing page handler
            if 'elif page == "👥 Investor Matching":' in line:
                print(f"Found last page handler at line {i+1}, adding new handlers")
                
                new_handlers = [
                    "",
                    "    # === AUTHENTICATION PAGES ===",
                    '    elif page == "🔐 Login / Register":',
                    "        show_authentication_ui()",
                    "",
                    '    elif page == "📊 Dashboard (Demo)":',
                    "        show_dashboard()  # Demo version",
                    "",
                    '    elif page == "🏠 Deal Analysis (Demo)":',
                    "        show_deal_analysis()  # Demo version", 
                    "",
                    '    elif page == "💹 Financial Modeling (Demo)":',
                    "        show_advanced_financial_modeling()  # Demo version",
                    "",
                    "    # === AUTHENTICATED USER PAGES ===",
                    '    elif page == "🎯 Enhanced Deal Manager":',
                    "        show_enhanced_deal_manager()",
                    "",
                    '    elif page == "👥 Client Manager":',
                    "        show_client_manager()",
                    "",
                    '    elif page == "📞 Communication Center":',
                    "        show_communication_center()",
                    "",
                    '    elif page == "⚡ Workflow Automation":',
                    "        show_workflow_automation()",
                    "",
                    '    elif page == "📋 Task Management":',
                    "        show_task_management()",
                    "",
                    '    elif page == "🎯 Lead Scoring":',
                    "        show_lead_scoring()",
                    "",
                    '    elif page == "🔔 Smart Notifications":',
                    "        show_smart_notifications()",
                    "",
                    '    elif page == "📊 Advanced Reporting":',
                    "        show_advanced_reporting()",
                    "",
                    '    elif page == "🤖 AI Email Templates":',
                    "        show_ai_email_templates()",
                    "",
                    '    elif page == "📱 SMS Marketing":',
                    "        show_sms_marketing()",
                    "",
                    "    # === ADMIN PAGES ===",
                    '    elif page == "🔧 Performance Dashboard":',
                    "        if st.session_state.get('is_admin', False):",
                    "            show_performance_dashboard()",
                    "        else:",
                    '            st.error("🚫 Admin access required")',
                    "",
                    '    elif page == "🗄️ Database Health":',
                    "        if st.session_state.get('is_admin', False):",
                    "            show_database_health()",
                    "        else:",
                    '            st.error("🚫 Admin access required")',
                    "",
                    '    elif page == "📊 System Monitor":',
                    "        if st.session_state.get('is_admin', False):",
                    "            show_system_monitor()",
                    "        else:",
                    '            st.error("🚫 Admin access required")',
                    "",
                    '    elif page == "🔍 Database Diagnostic":',
                    "        if st.session_state.get('is_admin', False):",
                    "            show_database_diagnostic()",
                    "        else:",
                    '            st.error("🚫 Admin access required")',
                    "",
                    "    # === USER PROFILE ===",
                    '    elif page == "👤 Profile & Settings":',
                    "        show_user_profile()",
                    ""
                ]
                
                # Add new handlers after current line
                modified_lines.extend(new_handlers)
        
        # Write the modified content
        final_content = '\n'.join(modified_lines)
        
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print("✅ Successfully added all missing page handlers")
        
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
    add_missing_page_handlers()