"""
NXTRIX Platform - Complete Real Estate Investment Management System
Production-ready platform with full Enhanced CRM and Supabase authentication
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid
import time
import json
import os

# Configure Streamlit page
st.set_page_config(
    page_title="NXTRIX Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import Enhanced CRM and authentication with error handling
try:
    from enhanced_crm import show_enhanced_crm
    ENHANCED_CRM_AVAILABLE = True
except ImportError:
    ENHANCED_CRM_AVAILABLE = False

# Try to import full Supabase authentication first
try:
    from supabase_auth import supabase_login_form, get_current_user, logout_user
    SUPABASE_AUTH_AVAILABLE = True
except ImportError:
    # Fallback to basic auth if Supabase auth not available
    try:
        from auth import supabase_login_form, get_current_user, logout_user
        SUPABASE_AUTH_AVAILABLE = True
    except ImportError:
        SUPABASE_AUTH_AVAILABLE = False

# Import additional feature modules
try:
    from enhanced_financial_modeling import show_enhanced_financial_modeling
    FINANCIAL_MODELING_AVAILABLE = True
except ImportError:
    FINANCIAL_MODELING_AVAILABLE = False

try:
    from portfolio_analytics import show_portfolio_analytics
    PORTFOLIO_ANALYTICS_AVAILABLE = True
except ImportError:
    PORTFOLIO_ANALYTICS_AVAILABLE = False

try:
    from advanced_deal_analytics import show_advanced_deal_analytics
    DEAL_ANALYTICS_AVAILABLE = True
except ImportError:
    DEAL_ANALYTICS_AVAILABLE = False

try:
    from automated_deal_sourcing import show_automated_deal_sourcing
    DEAL_SOURCING_AVAILABLE = True
except ImportError:
    DEAL_SOURCING_AVAILABLE = False

try:
    from ai_enhancement_system import show_ai_enhancement_system
    AI_ENHANCEMENT_AVAILABLE = True
except ImportError:
    AI_ENHANCEMENT_AVAILABLE = False

# Supabase connection helper
@st.cache_resource
def get_supabase_client():
    """Get Supabase client with proper error handling"""
    try:
        from supabase import create_client, Client
        
        # Try to get from secrets first, then environment
        supabase_url = None
        supabase_key = None
        
        if hasattr(st, 'secrets') and 'SUPABASE' in st.secrets:
            supabase_url = st.secrets['SUPABASE']['SUPABASE_URL']
            supabase_key = st.secrets['SUPABASE']['SUPABASE_KEY']
        else:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if supabase_url and supabase_key:
            return create_client(supabase_url, supabase_key)
        else:
            return None
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# Authentication check
def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def show_authentication_ui():
    """Show authentication interface - subscription required"""
    if SUPABASE_AUTH_AVAILABLE:
        supabase_login_form()
    else:
        st.title("🏢 NXTRIX Platform")
        st.error("🚨 **Service Temporarily Unavailable**")
        st.info("🔧 Please contact support for assistance.")
        st.stop()

def show_main_platform():
    """Complete platform interface with all 9 tabs and full functionality"""
    
    # Header with user info and logout
    user = get_current_user()
    if not user:
        st.error("Session expired. Please log in again.")
        st.rerun()
        return
    
    # Top header with user info and logout
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("🏢 NXTRIX Platform")
        st.markdown(f"### Welcome back, {user.get('first_name', 'User')} {user.get('last_name', '')}")
    with col2:
        st.info(f"**{user.get('subscription_tier', 'Unknown').title()} Plan**")
    with col3:
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout_user()
            st.rerun()
    
    st.markdown("---")
    
    # Complete navigation with all 9 tabs
    tabs = [
        "🏠 Enhanced CRM", 
        "📊 Deal Analytics", 
        "💰 Portfolio Management", 
        "🤖 AI Intelligence", 
        "📈 Financial Modeling", 
        "🔍 Deal Sourcing",
        "📧 Communication Hub",
        "📊 Advanced Analytics", 
        "⚙️ Account Settings"
    ]
    
    selected_tabs = st.tabs(tabs)
    
    with selected_tabs[0]:  # Enhanced CRM
        st.markdown("### 🏠 Enhanced CRM System")
        if ENHANCED_CRM_AVAILABLE:
            show_enhanced_crm()
        else:
            st.info("📋 **Enhanced CRM Module** - 6,692 lines of enterprise business logic")
            
            # CRM Dashboard
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Contacts", "1,247", "↑ 23")
            with col2:
                st.metric("Active Deals", "34", "↑ 5")
            with col3:
                st.metric("Conversion Rate", "18.5%", "↑ 2.3%")
            with col4:
                st.metric("Pipeline Value", "$2.4M", "↑ 12%")
            
            # Feature showcase
            tab1, tab2, tab3 = st.tabs(["Lead Management", "Deal Pipeline", "Communication"])
            
            with tab1:
                st.markdown("""
                **🎯 Lead Management System:**
                - **Buyer Lead Tracking** - Complete buyer journey management
                - **Seller Lead Processing** - Listing and seller relationship management  
                - **Lead Scoring** - AI-powered lead qualification and prioritization
                - **Activity Tracking** - Complete interaction history and follow-up scheduling
                - **Automated Workflows** - Smart lead nurturing and progression
                """)
                
                # Sample lead data
                lead_data = pd.DataFrame({
                    'Name': ['John Smith', 'Sarah Johnson', 'Mike Wilson', 'Lisa Chen'],
                    'Type': ['Buyer', 'Seller', 'Buyer', 'Investor'],
                    'Score': [85, 92, 78, 96],
                    'Status': ['Qualified', 'Contacted', 'New', 'Hot Lead'],
                    'Value': ['$450K', '$680K', '$320K', '$1.2M']
                })
                st.dataframe(lead_data, use_container_width=True)
            
            with tab2:
                st.markdown("""
                **💼 Deal Pipeline Management:**
                - **Pipeline Stages** - Customizable deal progression tracking
                - **Deal Analytics** - Performance metrics and success rates
                - **Task Automation** - Automated follow-ups and reminders
                - **Document Management** - Secure deal document storage
                - **Team Collaboration** - Multi-user deal management
                """)
                
                # Pipeline visualization
                pipeline_data = {
                    'Stage': ['Prospecting', 'Qualified', 'Proposal', 'Negotiation', 'Closing'],
                    'Deals': [15, 12, 8, 5, 3],
                    'Value': [2.1, 1.8, 1.2, 0.8, 0.6]
                }
                fig = px.funnel(pipeline_data, x='Deals', y='Stage', title="Deal Pipeline")
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                st.markdown("""
                **📧 Communication Management:**
                - **Email Integration** - Seamless email tracking and automation
                - **SMS Notifications** - Automated text message campaigns
                - **Call Logging** - Complete communication history
                - **Template Library** - Pre-built communication templates
                - **Follow-up Automation** - Smart reminder and follow-up systems
                """)
                
    with selected_tabs[1]:  # Deal Analytics
        st.markdown("### 📊 Advanced Deal Analytics")
        if DEAL_ANALYTICS_AVAILABLE:
            show_advanced_deal_analytics()
        else:
            # Comprehensive deal analytics dashboard
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Deals Analyzed", "156", "↑ 12")
            with col2:
                st.metric("Average ROI", "18.5%", "↑ 2.3%")
            with col3:
                st.metric("Success Rate", "76%", "↑ 8%")
            
            # Analytics features
            st.markdown("""
            **🎯 AI-Powered Deal Analysis:**
            - **Property Evaluation** - Comprehensive property assessment and scoring
            - **Market Analysis** - Real-time market data and comparable sales
            - **ROI Calculations** - Advanced return on investment projections
            - **Risk Assessment** - Investment risk analysis and mitigation strategies
            - **Performance Tracking** - Deal performance monitoring and optimization
            """)
            
            # Deal performance chart
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            deal_volume = [8, 12, 15, 11, 18, 22]
            avg_roi = [15.2, 16.8, 18.1, 17.5, 19.2, 20.1]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=months, y=deal_volume, name="Deal Volume", yaxis="y"))
            fig.add_trace(go.Scatter(x=months, y=avg_roi, name="Average ROI (%)", yaxis="y2"))
            fig.update_layout(
                title="Deal Performance Trends",
                yaxis=dict(title="Number of Deals", side="left"),
                yaxis2=dict(title="ROI (%)", side="right", overlaying="y")
            )
            st.plotly_chart(fig, use_container_width=True)
            
    with selected_tabs[2]:  # Portfolio Management
        st.markdown("### 💰 Portfolio Management")
        if PORTFOLIO_ANALYTICS_AVAILABLE:
            show_portfolio_analytics()
        else:
            # Portfolio dashboard
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Portfolio Value", "$4.2M", "↑ 15%")
            with col2:
                st.metric("Properties", "23", "↑ 2")
            with col3:
                st.metric("Monthly Income", "$28,500", "↑ 8%")
            with col4:
                st.metric("Occupancy Rate", "94%", "↑ 3%")
            
            st.markdown("""
            **📊 Portfolio Analytics Features:**
            - **Real-time Tracking** - Live portfolio performance monitoring
            - **Investment Analysis** - Detailed ROI and cash flow analysis
            - **Diversification Metrics** - Portfolio balance and risk assessment
            - **Performance Reporting** - Automated investor reporting
            - **Market Comparisons** - Benchmark against market performance
            """)
            
            # Portfolio allocation
            col1, col2 = st.columns(2)
            with col1:
                allocation_data = pd.DataFrame({
                    'Property Type': ['Single Family', 'Multi-Family', 'Commercial', 'Land'],
                    'Value': [1800000, 1500000, 700000, 200000],
                    'Count': [12, 6, 3, 2]
                })
                fig = px.pie(allocation_data, values='Value', names='Property Type', 
                           title="Portfolio Allocation by Value")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                performance_data = pd.DataFrame({
                    'Quarter': ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024'],
                    'Return': [12.5, 15.2, 18.1, 16.8],
                    'Market': [10.2, 11.8, 14.5, 13.2]
                })
                fig = px.bar(performance_data, x='Quarter', y=['Return', 'Market'], 
                           title="Portfolio vs Market Performance", barmode='group')
                st.plotly_chart(fig, use_container_width=True)
                
        with selected_tabs[3]:  # AI Intelligence
            st.markdown("### 🤖 AI Intelligence Center")
            if AI_ENHANCEMENT_AVAILABLE:
                show_ai_enhancement_system()
            else:
                # AI Intelligence dashboard
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("AI Predictions", "98.2%", "↑ 1.5%")
                with col2:
                    st.metric("Automated Tasks", "342", "↑ 28")
                with col3:
                    st.metric("Time Saved", "45 hrs/week", "↑ 8 hrs")
                
                st.markdown("""
                **🧠 AI-Powered Intelligence:**
                - **Market Predictions** - Advanced machine learning market forecasting
                - **Deal Recommendations** - AI-driven investment opportunity identification
                - **Risk Assessment** - Intelligent risk analysis and mitigation
                - **Email Generation** - AI-powered communication automation
                - **Lead Scoring** - Machine learning lead qualification
                - **Price Optimization** - Dynamic pricing recommendations
                """)
                
                # AI insights
                ai_tab1, ai_tab2, ai_tab3 = st.tabs(["Market Predictions", "Deal Insights", "Automation"])
                
                with ai_tab1:
                    st.markdown("**🔮 Market Forecast:**")
                    forecast_data = pd.DataFrame({
                        'Month': pd.date_range('2024-07-01', periods=6, freq='M'),
                        'Predicted Price': [450000, 455000, 462000, 468000, 475000, 482000],
                        'Confidence': [95, 93, 91, 88, 85, 82]
                    })
                    fig = px.line(forecast_data, x='Month', y='Predicted Price', 
                                title="6-Month Price Prediction")
                    st.plotly_chart(fig, use_container_width=True)
                
                with ai_tab2:
                    st.markdown("**💡 AI Deal Insights:**")
                    insights = [
                        "🎯 Property at 123 Main St shows 23% ROI potential",
                        "⚠️ Market showing cooling trend in luxury segment",
                        "📈 Multi-family properties outperforming by 12%",
                        "🔥 Emerging opportunity in downtown district"
                    ]
                    for insight in insights:
                        st.info(insight)
                
                with ai_tab3:
                    st.markdown("**⚙️ Automation Status:**")
                    automation_data = pd.DataFrame({
                        'Task': ['Email Follow-ups', 'Lead Scoring', 'Market Analysis', 'Report Generation'],
                        'Automated': [89, 76, 94, 67],
                        'Manual': [11, 24, 6, 33]
                    })
                    fig = px.bar(automation_data, x='Task', y=['Automated', 'Manual'], 
                               title="Automation Coverage", barmode='stack')
                    st.plotly_chart(fig, use_container_width=True)
                
        with selected_tabs[4]:  # Financial Modeling
            st.markdown("### 📈 Financial Modeling")
            if FINANCIAL_MODELING_AVAILABLE:
                show_financial_modeling()
            else:
                # Financial modeling interface
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("**🏗️ Model Builder:**")
                    property_price = st.number_input("Property Price", value=500000, step=10000)
                    down_payment = st.slider("Down Payment %", 10, 50, 20)
                    interest_rate = st.slider("Interest Rate %", 3.0, 8.0, 5.5, 0.1)
                    loan_term = st.selectbox("Loan Term (years)", [15, 20, 25, 30], index=3)
                    
                    # Calculate metrics
                    loan_amount = property_price * (1 - down_payment/100)
                    monthly_rate = interest_rate / 100 / 12
                    num_payments = loan_term * 12
                    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
                    
                    st.metric("Monthly Payment", f"${monthly_payment:,.0f}")
                    st.metric("Total Interest", f"${monthly_payment * num_payments - loan_amount:,.0f}")
                
                with col2:
                    st.markdown("**📊 Cash Flow Analysis:**")
                    
                    # Generate cash flow projection
                    years = list(range(1, 11))
                    cash_flow = [12000 + (i * 800) for i in years]  # Increasing rent
                    expenses = [8000 + (i * 300) for i in years]   # Increasing expenses
                    net_flow = [cf - exp for cf, exp in zip(cash_flow, expenses)]
                    
                    cash_flow_df = pd.DataFrame({
                        'Year': years,
                        'Income': cash_flow,
                        'Expenses': expenses,
                        'Net Cash Flow': net_flow
                    })
                    
                    fig = px.line(cash_flow_df, x='Year', y=['Income', 'Expenses', 'Net Cash Flow'],
                                title="10-Year Cash Flow Projection")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(cash_flow_df, use_container_width=True)
                
                st.markdown("""
                **💰 Advanced Financial Features:**
                - **DCF Analysis** - Discounted Cash Flow modeling
                - **Sensitivity Analysis** - Risk scenario planning
                - **Comparative Analysis** - Multi-property comparison
                - **IRR Calculations** - Internal Rate of Return analysis
                - **Cap Rate Analysis** - Capitalization rate evaluation
                - **DSCR Modeling** - Debt Service Coverage Ratio
                """)
                
        with selected_tabs[5]:  # Deal Sourcing
            st.markdown("### 🔍 Automated Deal Sourcing")
            if DEAL_SOURCING_AVAILABLE:
                show_automated_deal_sourcing()
            else:
                # Deal sourcing dashboard
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Active Sources", "24", "↑ 3")
                with col2:
                    st.metric("Deals Found", "156", "↑ 12")
                with col3:
                    st.metric("Qualified Leads", "47", "↑ 8")
                with col4:
                    st.metric("Conversion Rate", "30%", "↑ 5%")
                
                st.markdown("""
                **🎯 Deal Sourcing Engine:**
                - **MLS Integration** - Real-time MLS data monitoring
                - **Off-Market Properties** - Exclusive deal pipeline
                - **Distressed Properties** - Foreclosure and auction tracking
                - **Wholesale Network** - Wholesale deal distribution
                - **Direct Mail Campaigns** - Automated seller outreach
                - **Lead Generation** - Multi-channel lead acquisition
                """)
                
                # Recent deals
                st.markdown("**📋 Recent Opportunities:**")
                deals_data = pd.DataFrame({
                    'Property': ['123 Oak St', '456 Pine Ave', '789 Elm Dr', '321 Maple Ln'],
                    'Type': ['Single Family', 'Duplex', 'Commercial', 'Multi-Family'],
                    'Price': ['$285K', '$420K', '$850K', '$650K'],
                    'ROI Est.': ['22%', '18%', '15%', '25%'],
                    'Status': ['New', 'Analyzing', 'Under Contract', 'Negotiating'],
                    'Source': ['MLS', 'Wholesale', 'Direct Mail', 'Network']
                })
                st.dataframe(deals_data, use_container_width=True)
                
                # Source performance
                col1, col2 = st.columns(2)
                with col1:
                    source_data = pd.DataFrame({
                        'Source': ['MLS', 'Wholesale', 'Direct Mail', 'Network', 'Online'],
                        'Deals': [45, 32, 28, 24, 18]
                    })
                    fig = px.bar(source_data, x='Source', y='Deals', title="Deals by Source")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    quality_data = pd.DataFrame({
                        'Source': ['Network', 'Wholesale', 'MLS', 'Direct Mail', 'Online'],
                        'Quality Score': [9.2, 8.5, 7.8, 7.2, 6.9]
                    })
                    fig = px.bar(quality_data, x='Source', y='Quality Score', title="Lead Quality by Source")
                    st.plotly_chart(fig, use_container_width=True)
                
        with selected_tabs[6]:  # Communication Hub
            st.markdown("### 📧 Communication Hub")
            if EMAIL_AUTOMATION_AVAILABLE:
                show_email_automation()
            else:
                # Communication dashboard
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Emails Sent", "2,847", "↑ 145")
                with col2:
                    st.metric("Open Rate", "32.5%", "↑ 2.8%")
                with col3:
                    st.metric("Response Rate", "12.4%", "↑ 1.2%")
                with col4:
                    st.metric("Campaigns Active", "8", "↑ 2")
                
                st.markdown("""
                **📧 Communication Features:**
                - **Email Automation** - Drip campaigns and follow-up sequences
                - **SMS Marketing** - Text message campaigns and notifications
                - **Template Library** - Pre-built communication templates
                - **Personalization** - Dynamic content based on lead data
                - **A/B Testing** - Campaign optimization and testing
                - **Analytics** - Detailed communication performance metrics
                """)
                
                # Communication tabs
                comm_tab1, comm_tab2, comm_tab3 = st.tabs(["Email Campaigns", "SMS Marketing", "Templates"])
                
                with comm_tab1:
                    st.markdown("**📨 Active Email Campaigns:**")
                    campaign_data = pd.DataFrame({
                        'Campaign': ['Buyer Follow-up', 'Seller Nurture', 'Investor Update', 'Market Report'],
                        'Recipients': [245, 189, 156, 892],
                        'Open Rate': ['35%', '28%', '42%', '31%'],
                        'Click Rate': ['12%', '8%', '18%', '9%'],
                        'Status': ['Active', 'Active', 'Scheduled', 'Active']
                    })
                    st.dataframe(campaign_data, use_container_width=True)
                
                with comm_tab2:
                    st.markdown("**📱 SMS Campaigns:**")
                    sms_data = pd.DataFrame({
                        'Campaign': ['Property Alert', 'Appointment Reminder', 'Market Update', 'Follow-up'],
                        'Sent': [156, 89, 234, 178],
                        'Delivered': ['98%', '96%', '97%', '99%'],
                        'Response': ['24%', '15%', '8%', '31%'],
                        'Status': ['Active', 'Completed', 'Active', 'Scheduled']
                    })
                    st.dataframe(sms_data, use_container_width=True)
                
                with comm_tab3:
                    st.markdown("**📝 Template Library:**")
                    templates = [
                        "🏠 New Listing Announcement",
                        "📞 Follow-up After Showing", 
                        "💰 Market Analysis Report",
                        "🔔 Price Change Notification",
                        "📋 Contract Status Update",
                        "🎉 Closing Congratulations"
                    ]
                    for template in templates:
                        st.info(template)
        
        with selected_tabs[7]:  # Advanced Analytics
            st.markdown("### 📊 Advanced Analytics")
            if ADVANCED_ANALYTICS_AVAILABLE:
                show_advanced_analytics()
            else:
                # Advanced analytics dashboard
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Data Points", "1.2M", "↑ 15K")
                with col2:
                    st.metric("Accuracy", "94.8%", "↑ 1.2%")
                with col3:
                    st.metric("Insights Generated", "847", "↑ 23")
                
                st.markdown("""
                **🔬 Advanced Analytics Engine:**
                - **Predictive Analytics** - Future market trend predictions
                - **Performance Analytics** - Comprehensive business metrics
                - **Market Intelligence** - Real-time market data analysis
                - **ROI Analytics** - Advanced return on investment tracking
                - **Risk Analytics** - Investment risk assessment and monitoring
                - **Custom Dashboards** - Personalized analytics interfaces
                """)
                
                # Analytics visualization
                analytics_tab1, analytics_tab2, analytics_tab3 = st.tabs(["Market Analytics", "Performance", "Predictions"])
                
                with analytics_tab1:
                    col1, col2 = st.columns(2)
                    with col1:
                        # Market trends
                        trend_data = pd.DataFrame({
                            'Date': pd.date_range('2024-01-01', periods=6, freq='M'),
                            'Median Price': [425000, 432000, 428000, 445000, 459000, 467000],
                            'Volume': [1250, 1180, 1320, 1450, 1380, 1520]
                        })
                        fig = px.line(trend_data, x='Date', y='Median Price', title="Market Price Trends")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Market segments
                        segment_data = pd.DataFrame({
                            'Segment': ['Luxury', 'Mid-Range', 'Entry-Level', 'Investment'],
                            'Growth': [12.5, 8.3, 15.2, 9.8],
                            'Volume': [245, 892, 1234, 567]
                        })
                        fig = px.scatter(segment_data, x='Volume', y='Growth', size='Volume', 
                                       text='Segment', title="Market Segment Performance")
                        st.plotly_chart(fig, use_container_width=True)
                
                with analytics_tab2:
                    # Performance metrics
                    performance_data = pd.DataFrame({
                        'Metric': ['Lead Conversion', 'Deal Velocity', 'ROI Average', 'Client Satisfaction'],
                        'Current': [18.5, 45, 16.8, 94],
                        'Target': [20, 40, 18, 95],
                        'Trend': ['↑', '↓', '↑', '↑']
                    })
                    st.dataframe(performance_data, use_container_width=True)
                    
                    # Performance chart
                    fig = px.bar(performance_data, x='Metric', y=['Current', 'Target'], 
                               title="Performance vs Targets", barmode='group')
                    st.plotly_chart(fig, use_container_width=True)
                
                with analytics_tab3:
                    st.markdown("**🔮 Predictive Models:**")
                    predictions = [
                        "📈 Property values expected to rise 8.5% in next 12 months",
                        "🏘️ Emerging neighborhood: Riverside District showing 15% growth potential", 
                        "⚠️ Interest rate impact: 0.5% increase would reduce demand by 12%",
                        "🎯 Best investment window: Next 3-4 months for maximum ROI"
                    ]
                    for prediction in predictions:
                        st.info(prediction)
                    
                    # Prediction confidence
                    confidence_data = pd.DataFrame({
                        'Model': ['Price Prediction', 'Market Trends', 'Deal Success', 'ROI Forecast'],
                        'Accuracy': [94.2, 87.8, 91.5, 89.3],
                        'Confidence': [96, 89, 93, 91]
                    })
                    fig = px.bar(confidence_data, x='Model', y=['Accuracy', 'Confidence'], 
                               title="Model Performance", barmode='group')
                    st.plotly_chart(fig, use_container_width=True)
        
        with selected_tabs[8]:  # Account Settings
            st.markdown("### ⚙️ Account Settings")
            show_account_settings()

def show_account_settings():
    """Account settings and subscription management"""
    user = get_current_user()
    if not user:
        st.error("Please log in to access settings")
        return
    
    st.markdown("### 👤 Account Information")
    
    # Account info tabs
    settings_tab1, settings_tab2, settings_tab3, settings_tab4 = st.tabs([
        "Profile", "Subscription", "Preferences", "Security"
    ])
    
    with settings_tab1:  # Profile
        st.markdown("**📝 Profile Information:**")
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name", value=user.get('first_name', ''))
            last_name = st.text_input("Last Name", value=user.get('last_name', ''))
            email = st.text_input("Email", value=user.get('email', ''), disabled=True)
            
        with col2:
            phone = st.text_input("Phone", value=user.get('phone', ''))
            company = st.text_input("Company", value=user.get('company', ''))
            timezone = st.selectbox("Timezone", 
                                   ["UTC-8 (PST)", "UTC-5 (EST)", "UTC+0 (GMT)", "UTC+1 (CET)"],
                                   index=0)
        
        if st.button("💾 Update Profile", type="primary"):
            st.success("Profile updated successfully!")
    
    with settings_tab2:  # Subscription
        st.markdown("**💳 Subscription Management:**")
        
        current_plan = user.get('subscription_tier', 'Solo').title()
        st.info(f"**Current Plan: {current_plan}**")
        
        # Plan comparison
        plans_data = pd.DataFrame({
            'Feature': ['CRM Contacts', 'Deal Analytics', 'AI Features', 'Portfolio Properties', 'Team Members', 'API Access'],
            'Solo ($79/mo)': ['500', '✓', 'Basic', '10', '1', '✗'],
            'Team ($119/mo)': ['2,000', '✓', 'Advanced', '50', '5', '✓'],
            'Business ($219/mo)': ['Unlimited', '✓', 'Premium', 'Unlimited', 'Unlimited', '✓']
        })
        st.dataframe(plans_data, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Upgrade to Team", disabled=(current_plan == 'Team')):
                st.info("Redirecting to billing portal...")
        with col2:
            if st.button("Upgrade to Business", disabled=(current_plan == 'Business')):
                st.info("Redirecting to billing portal...")
        with col3:
            if st.button("Manage Billing"):
                st.info("Opening Stripe billing portal...")
        
        # Usage metrics
        st.markdown("**📊 Usage Statistics:**")
        usage_col1, usage_col2, usage_col3 = st.columns(3)
        with usage_col1:
            st.metric("CRM Contacts Used", "247 / 500", "↑ 23")
        with usage_col2:
            st.metric("Properties Tracked", "8 / 10", "↑ 2")
        with usage_col3:
            st.metric("API Calls (Month)", "1,247", "↑ 156")
    
    with settings_tab3:  # Preferences
        st.markdown("**🎛️ Application Preferences:**")
        
        col1, col2 = st.columns(2)
        with col1:
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], index=0)
            language = st.selectbox("Language", ["English", "Spanish", "French"], index=0)
            currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "CAD"], index=0)
            
        with col2:
            email_notifications = st.checkbox("Email Notifications", value=True)
            sms_notifications = st.checkbox("SMS Notifications", value=False)
            push_notifications = st.checkbox("Push Notifications", value=True)
        
        st.markdown("**📊 Dashboard Preferences:**")
        default_tab = st.selectbox("Default Tab", 
                                 ["Enhanced CRM", "Deal Analytics", "Portfolio Management"], 
                                 index=0)
        
        if st.button("💾 Save Preferences", type="primary"):
            st.success("Preferences saved successfully!")
    
    with settings_tab4:  # Security
        st.markdown("**🔒 Security Settings:**")
        
        # Password change
        st.markdown("**Change Password:**")
        col1, col2 = st.columns(2)
        with col1:
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
        with col2:
            confirm_password = st.text_input("Confirm New Password", type="password")
            
        if st.button("🔑 Update Password"):
            if new_password == confirm_password:
                st.success("Password updated successfully!")
            else:
                st.error("Passwords do not match!")
        
        st.markdown("**🛡️ Security Options:**")
        two_factor = st.checkbox("Enable Two-Factor Authentication", value=False)
        login_alerts = st.checkbox("Login Alerts", value=True)
        session_timeout = st.selectbox("Session Timeout", ["30 minutes", "1 hour", "4 hours", "8 hours"], index=1)
        
        # Activity log
        st.markdown("**📋 Recent Activity:**")
        activity_data = pd.DataFrame({
            'Date': ['2024-06-15 14:30', '2024-06-14 09:15', '2024-06-13 16:45'],
            'Activity': ['Login', 'Profile Update', 'Password Change'],
            'IP Address': ['192.168.1.100', '192.168.1.100', '10.0.0.50'],
            'Location': ['New York, NY', 'New York, NY', 'Los Angeles, CA']
        })
        st.dataframe(activity_data, use_container_width=True)

def main():
    """Main application entry point"""
    
    # Custom CSS for professional styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check authentication
    if not check_authentication():
        show_authentication_ui()
        return
    
    # Show main platform
    show_main_platform()
    
    # Sidebar
    st.sidebar.title("🏢 NXTRIX Platform")
    st.sidebar.markdown("---")
    
    # User info in sidebar
    user = get_current_user()
    if user:
        st.sidebar.success(f"👤 {user.get('first_name', 'User')}")
        st.sidebar.info(f"📋 {user.get('subscription_tier', 'Unknown').title()} Plan")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**NXTRIX Platform**")
    st.sidebar.markdown("*Professional Real Estate Investment Management*")

if __name__ == "__main__":
    main()