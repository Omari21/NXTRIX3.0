# Clean navigation section to replace the corrupted one

CLEAN_NAVIGATION_CODE = '''
    # Check for redirect first
    redirect_page = get_current_page()
    
    # Sidebar Navigation
    st.sidebar.title("🎯 Navigation")
    
    # Use redirect page if available, otherwise use selectbox
    if redirect_page:
        page = redirect_page
        # Set the selectbox to match the redirected page
        current_index = 0
        navigation_options = [
            "📊 Dashboard", 
            "🏠 Deal Analysis", 
            "💹 Advanced Financial Modeling", 
            "🗄️ Deal Database", 
            "📈 Portfolio", 
            "🤖 AI Insights", 
            "👥 Investor Matching"
        ]
        if redirect_page in navigation_options:
            current_index = navigation_options.index(redirect_page)
        
        page = st.sidebar.selectbox(
            "Choose Section",
            navigation_options,
            index=current_index
        )
    else:
        page = st.sidebar.selectbox(
            "Choose Section",
            ["📊 Dashboard", "🏠 Deal Analysis", "💹 Advanced Financial Modeling", "🗄️ Deal Database", "📈 Portfolio", "🤖 AI Insights", "👥 Investor Matching"]
        )
'''

CLEAN_NAVIGATION_CONDITIONS = '''
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🏠 Deal Analysis":
        show_deal_analysis()
    elif page == "💹 Advanced Financial Modeling":
        show_advanced_financial_modeling()
    elif page == "🗄️ Deal Database":
        show_deal_database()
    elif page == "📈 Portfolio":
        show_portfolio()
    elif page == "🤖 AI Insights":
        show_ai_insights()
    elif page == "👥 Investor Matching":
        show_investor_matching()
'''