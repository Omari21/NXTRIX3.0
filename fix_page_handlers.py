#!/usr/bin/env python3
"""
Fix and add complete page handlers for NXTRIX CRM
"""

def fix_and_add_page_handlers():
    """Fix syntax and add all missing page handlers"""
    
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find the page routing section
        lines = content.split('\n')
        modified_lines = []
        found_routing = False
        
        for i, line in enumerate(lines):
            # Look for the page routing section
            if 'if page ==' in line and 'Dashboard' in line:
                found_routing = True
                print(f"Found page routing at line {i+1}")
                
                # Replace entire routing section with complete handlers
                complete_routing = [
                    "    # === PAGE ROUTING SYSTEM ===",
                    '    if page == "📊 Dashboard" or page == "📊 Dashboard (Demo)":',
                    "        show_dashboard()",
                    '    elif page == "🏠 Deal Analysis" or page == "🏠 Deal Analysis (Demo)":',
                    "        show_deal_analysis()",
                    '    elif page == "💹 Advanced Financial Modeling" or page == "💹 Financial Modeling (Demo)":',
                    "        show_advanced_financial_modeling()",
                    '    elif page == "🗄️ Deal Database":',
                    "        show_deal_database()",
                    '    elif page == "📈 Portfolio Analytics":',
                    "        show_portfolio_analytics()",
                    '    elif page == "🏛️ Investor Portal":',
                    "        show_investor_portal()",
                    '    elif page == "🤝 Enhanced CRM":',
                    "        enhanced_crm_func = get_enhanced_crm()",
                    "        if enhanced_crm_func:",
                    "            enhanced_crm_func()",
                    "        else:",
                    '            st.error("❌ Enhanced CRM module failed to load")',
                    '    elif page == "🧠 AI Insights":',
                    "        show_ai_insights()",
                    '    elif page == "👥 Investor Matching":',
                    "        show_investor_matching()",
                    "",
                    "    # === AUTHENTICATION PAGES ===",
                    '    elif page == "🔐 Login / Register":',
                    "        show_authentication_ui()",
                    "",
                    "    # === AUTHENTICATED USER PAGES ===",
                    '    elif page == "🎯 Enhanced Deal Manager":',
                    "        show_enhanced_deal_manager()",
                    '    elif page == "👥 Client Manager":',
                    "        show_client_manager()",
                    '    elif page == "📞 Communication Center":',
                    "        show_communication_center()",
                    '    elif page == "⚡ Workflow Automation":',
                    "        show_workflow_automation()",
                    '    elif page == "📋 Task Management":',
                    "        show_task_management()",
                    '    elif page == "🎯 Lead Scoring":',
                    "        show_lead_scoring()",
                    '    elif page == "🔔 Smart Notifications":',
                    "        show_smart_notifications()",
                    '    elif page == "📊 Advanced Reporting":',
                    "        show_advanced_reporting()",
                    '    elif page == "🤖 AI Email Templates":',
                    "        show_ai_email_templates()",
                    '    elif page == "📱 SMS Marketing":',
                    "        show_sms_marketing()",
                    "",
                    "    # === ADMIN PAGES ===",
                    '    elif page == "🔧 Performance Dashboard":',
                    "        if st.session_state.get('is_admin', False):",
                    "            show_performance_dashboard()",
                    "        else:",
                    '            st.error("🚫 Admin access required")',
                    '    elif page == "🗄️ Database Health":',
                    "        if st.session_state.get('is_admin', False):",
                    "            show_database_health()",
                    "        else:",
                    '            st.error("🚫 Admin access required")',
                    '    elif page == "📊 System Monitor":',
                    "        if st.session_state.get('is_admin', False):",
                    "            show_system_monitor()",
                    "        else:",
                    '            st.error("🚫 Admin access required")',
                    '    elif page == "🔍 Database Diagnostic":',
                    "        if st.session_state.get('is_admin', False):",
                    "            show_database_diagnostic()",
                    "        else:",
                    '            st.error("🚫 Admin access required")',
                    "",
                    "    # === USER PROFILE ===",
                    '    elif page == "👤 Profile & Settings":',
                    "        show_user_profile()",
                    "",
                    "    else:",
                    '        st.error(f"❌ Page not found: {page}")'
                ]
                
                modified_lines.extend(complete_routing)
                
                # Skip the old routing lines
                j = i + 1
                while j < len(lines) and ('elif page ==' in lines[j] or 'if page ==' in lines[j] or lines[j].strip() == ""):
                    j += 1
                
                # Continue from after the old routing
                i = j - 1
                found_routing = True
                continue
                
            if not found_routing:
                modified_lines.append(line)
        
        # Write the modified content
        final_content = '\n'.join(modified_lines)
        
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print("✅ Successfully fixed and added complete page routing system")
        
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
    fix_and_add_page_handlers()