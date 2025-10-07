#!/usr/bin/env python3
"""
Comprehensive fix for the main function
"""

def fix_main_function_comprehensive():
    """Completely fix the main function"""
    
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find the start of the main function
        main_start = content.find('def main():')
        if main_start == -1:
            print("❌ Could not find main function")
            return False
        
        # Find the end of the main function (next def or end of file)
        next_def = content.find('\ndef ', main_start + 1)
        if next_def == -1:
            next_def = content.find('\nif __name__ == "__main__":', main_start)
            if next_def == -1:
                next_def = len(content)
        
        # Create a clean main function
        new_main_function = '''def main():
    """
    Main function for NXTRIX CRM - Phase 3 with Backend Integration
    """
    
    # Mobile viewport meta tag
    st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    """, unsafe_allow_html=True)
    
    # Initialize backend connection
    init_database_connection()
    
    # Display connection status
    if st.session_state.get('backend_connected', False):
        st.sidebar.success("🟢 Backend Connected")
    else:
        st.sidebar.warning("🟡 Demo Mode (No Backend)")
    
    # Check authentication status
    if not st.session_state.get('authenticated', False):
        # Show authentication UI if not logged in
        show_authentication_ui()
        return
    
    # User is authenticated - show the main app
    st.sidebar.success(f"✅ Welcome, {st.session_state.get('first_name', 'User')}!")
    
    user_tier = st.session_state.get('user_tier', 'free')
    is_admin = st.session_state.get('is_admin', False)
    
    # Navigation options based on user tier and authentication
    navigation_options = []
    
    # Core pages available to all authenticated users
    navigation_options.extend([
        "📊 Dashboard",
        "🏠 Deal Analysis", 
        "💹 Advanced Financial Modeling",
        "🗄️ Deal Database",
        "📈 Portfolio Analytics",
        "🏛️ Investor Portal",
        "🤝 Enhanced CRM",
        "🧠 AI Insights",
        "👥 Investor Matching"
    ])
    
    # Professional and Enterprise features
    if user_tier in ['professional', 'enterprise']:
        navigation_options.extend([
            "🎯 Enhanced Deal Manager",
            "👥 Client Manager",
            "📞 Communication Center",
            "⚡ Workflow Automation",
            "📋 Task Management",
            "🎯 Lead Scoring",
            "🔔 Smart Notifications",
            "📊 Advanced Reporting",
            "🤖 AI Email Templates",
            "📱 SMS Marketing"
        ])
    
    # Admin-only features
    if is_admin:
        navigation_options.extend([
            "🔧 Performance Dashboard",
            "🗄️ Database Health",
            "📊 System Monitor", 
            "🔍 Database Diagnostic"
        ])
    
    # User profile always available
    navigation_options.append("👤 Profile & Settings")
    
    # Sidebar navigation
    st.sidebar.title("🚀 NXTRIX CRM")
    
    # Display user tier
    tier_colors = {
        "free": "🆓",
        "professional": "💼", 
        "enterprise": "🏢"
    }
    st.sidebar.info(f"{tier_colors.get(user_tier, '🆓')} {user_tier.title()} Plan")
    
    page = st.sidebar.selectbox("Navigate to:", navigation_options)
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        result = logout_user()
        if result["success"]:
            st.success(result["message"])
            st.rerun()
    
    # === PAGE ROUTING SYSTEM ===
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🏠 Deal Analysis":
        show_deal_analysis()
    elif page == "💹 Advanced Financial Modeling":
        show_advanced_financial_modeling()
    elif page == "🗄️ Deal Database":
        show_deal_database()
    elif page == "📈 Portfolio Analytics":
        show_portfolio_analytics()
    elif page == "🏛️ Investor Portal":
        show_investor_portal()
    elif page == "🤝 Enhanced CRM":
        enhanced_crm_func = get_enhanced_crm()
        if enhanced_crm_func:
            enhanced_crm_func()
        else:
            st.error("❌ Enhanced CRM module failed to load")
    elif page == "🧠 AI Insights":
        show_ai_insights()
    elif page == "👥 Investor Matching":
        show_investor_matching()
    
    # === AUTHENTICATED USER PAGES ===
    elif page == "🎯 Enhanced Deal Manager":
        show_enhanced_deal_manager()
    elif page == "👥 Client Manager":
        show_client_manager()
    elif page == "📞 Communication Center":
        show_communication_center()
    elif page == "⚡ Workflow Automation":
        show_workflow_automation()
    elif page == "📋 Task Management":
        show_task_management()
    elif page == "🎯 Lead Scoring":
        show_lead_scoring()
    elif page == "🔔 Smart Notifications":
        show_smart_notifications()
    elif page == "📊 Advanced Reporting":
        show_advanced_reporting()
    elif page == "🤖 AI Email Templates":
        show_ai_email_templates()
    elif page == "📱 SMS Marketing":
        show_sms_marketing()
    
    # === ADMIN PAGES ===
    elif page == "🔧 Performance Dashboard":
        if st.session_state.get('is_admin', False):
            show_performance_dashboard()
        else:
            st.error("🚫 Admin access required")
    elif page == "🗄️ Database Health":
        if st.session_state.get('is_admin', False):
            show_database_health()
        else:
            st.error("🚫 Admin access required")
    elif page == "📊 System Monitor":
        if st.session_state.get('is_admin', False):
            show_system_monitor()
        else:
            st.error("🚫 Admin access required")
    elif page == "🔍 Database Diagnostic":
        if st.session_state.get('is_admin', False):
            show_database_diagnostic()
        else:
            st.error("🚫 Admin access required")
    
    # === USER PROFILE ===
    elif page == "👤 Profile & Settings":
        show_user_profile()
    
    else:
        st.error(f"❌ Page not found: {page}")

'''
        
        # Replace the main function
        new_content = content[:main_start] + new_main_function + content[next_def:]
        
        # Write the updated content
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Successfully fixed main function")
        
        # Test compilation
        try:
            compile(new_content, 'streamlit_app.py', 'exec')
            print("✅ File compiles successfully")
            return True
        except SyntaxError as e:
            print(f"⚠️ Syntax error: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_main_function_comprehensive()