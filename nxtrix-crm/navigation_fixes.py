"""
Navigation fixes for NXTRIX CRM
This file contains code snippets to fix navigation and CTA button issues
"""

# Fixed navigation selectbox options (clean characters)
navigation_options = [
    "📊 Dashboard", 
    "🏠 Deal Analysis", 
    "💹 Advanced Financial Modeling", 
    "🗄 Deal Database", 
    "📈 Portfolio", 
    "🤖 AI Insights", 
    "👥 Investor Matching"
]

# Fixed navigation conditions
navigation_conditions = """
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🏠 Deal Analysis":
        show_deal_analysis()
    elif page == "💹 Advanced Financial Modeling":
        show_advanced_financial_modeling()
    elif page == "🗄 Deal Database":
        show_deal_database()
    elif page == "📈 Portfolio":
        show_portfolio()
    elif page == "🤖 AI Insights":
        show_ai_insights()
    elif page == "👥 Investor Matching":
        show_investor_matching()
"""

# Fixed sidebar navigation with redirect support
sidebar_navigation = """
    # Sidebar Navigation
    st.sidebar.title("🎯 Navigation")
    
    # Handle page redirects
    redirect_page = get_current_page()
    if redirect_page:
        page = redirect_page
    else:
        page = st.sidebar.selectbox(
            "Choose Section",
            ["📊 Dashboard", "🏠 Deal Analysis", "💹 Advanced Financial Modeling", "🗄 Deal Database", "📈 Portfolio", "🤖 AI Insights", "👥 Investor Matching"],
            key="main_navigation"
        )
"""