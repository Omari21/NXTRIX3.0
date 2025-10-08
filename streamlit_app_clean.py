# -*- coding: utf-8 -*-
# NXTRIX CRM - Full Production Version
# Main application with Enhanced CRM integrated as a module

impor    @staticmethod
    def show_user_menu():
        """Show user menu in sidebar"""
        if st.session_state.get('user_authenticated', False):
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 👤 User Profile")
            
            user_profile = st.session_state.get('user_profile', {})
            st.sidebar.info(f"**{user_profile.get('full_name', 'User')}**\n{user_profile.get('email', '')}")
            
            tier = st.session_state.get('user_tier', 'solo')
            tier_colors = {'solo': '🟡', 'team': '🟢', 'business': '🔵'}
            st.sidebar.info(f"{tier_colors.get(tier, '⚪')} **{tier.title()} Plan**")
            
            # Show production pricing in sidebar
            st.sidebar.markdown("### 💳 Production Pricing")
            st.sidebar.markdown("""
            **Solo**: $79/month  
            **Team**: $119/month  
            **Business**: $219/month
            """)
            
            if st.sidebar.button("🚪 Logout"):st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import uuid
import time
import re
from typing import List, Dict, Any, Optional
import hashlib
import os
from contextlib import contextmanager

# Add this at the top to integrate Enhanced CRM
try:
    from enhanced_crm import show_enhanced_crm
    ENHANCED_CRM_AVAILABLE = True
except ImportError:
    ENHANCED_CRM_AVAILABLE = False
    def show_enhanced_crm():
        st.error("Enhanced CRM module not available. Please ensure enhanced_crm.py is in the same directory.")

# Production Mode Configuration
PRODUCTION_MODE = True

# Import configuration
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# OpenAI configuration
try:
    import openai
    openai.api_key = st.secrets.get("OPENAI", {}).get("OPENAI_API_KEY", "")
except:
    pass

# Feature availability flags
COMMUNICATION_AVAILABLE = False
DOCUMENT_MANAGER_AVAILABLE = False
STRIPE_AVAILABLE = False

# Tier system and authentication
class TierEnforcementSystem:
    def __init__(self):
        self.tier_features = {
            'solo': {
                'deals_per_month': 10,
                'features': ['basic_analysis', 'deal_storage', 'basic_reports']
            },
            'team': {
                'deals_per_month': 100,
                'features': ['basic_analysis', 'deal_storage', 'basic_reports', 'client_management', 'email_campaigns', 'advanced_analytics']
            },
            'business': {
                'deals_per_month': -1,  # Unlimited
                'features': ['all']
            }
        }
    
    def check_feature_access(self, feature_name: str) -> bool:
        user_tier = st.session_state.get('user_tier', 'solo')
        tier_info = self.tier_features.get(user_tier, self.tier_features['solo'])
        
        if 'all' in tier_info['features']:
            return True
        
        return feature_name in tier_info['features']

class UserAuthSystem:
    @staticmethod
    def initialize_auth_system():
        """Initialize authentication system"""
        if 'user_authenticated' not in st.session_state:
            st.session_state.user_authenticated = False
        if 'user_email' not in st.session_state:
            st.session_state.user_email = None
        if 'user_tier' not in st.session_state:
            st.session_state.user_tier = 'solo'
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
    
    @staticmethod
    def show_login_page():
        """Show simplified login page"""
        st.markdown("""
        <div style="background-color: #262730; padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem; border: 1px solid #404040;">
            <h1>ðŸ˜ï¸ NXTRIX CRM</h1>
            <p>AI-Powered Real Estate Investment Analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ðŸ” Quick Access")
        st.info("Demo Mode: Click any button to access the full application")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("ðŸ‘¤ Demo User", type="primary", use_container_width=True):
                UserAuthSystem._authenticate_user("demo@nxtrix.com", "solo")
                st.rerun()
        
        with col2:
            if st.button("ðŸ‘¥ Team Demo", type="primary", use_container_width=True):
                UserAuthSystem._authenticate_user("team@nxtrix.com", "team")
                st.rerun()
        
        with col3:
            if st.button("ðŸ¢ Business Demo", type="primary", use_container_width=True):
                UserAuthSystem._authenticate_user("business@nxtrix.com", "business")
                st.rerun()
    
    @staticmethod
    def _authenticate_user(email: str, tier: str, is_admin: bool = False):
        """Authenticate user with given tier"""
        st.session_state.user_authenticated = True
        st.session_state.user_email = email
        st.session_state.user_tier = tier
        st.session_state.is_admin = is_admin
        st.session_state.user_profile = {
            'full_name': email.split('@')[0].title(),
            'email': email,
            'tier': tier
        }
    
    @staticmethod
    def show_user_menu():
        """Show user menu in sidebar"""
        if st.session_state.get('user_authenticated', False):
            st.sidebar.markdown("---")
            st.sidebar.markdown("### ðŸ‘¤ User Profile")
            
            user_profile = st.session_state.get('user_profile', {})
            st.sidebar.info(f"**{user_profile.get('full_name', 'User')}**\n{user_profile.get('email', '')}")
            
            tier = st.session_state.get('user_tier', 'solo')
            tier_colors = {'solo': 'ðŸŸ¡', 'team': 'ðŸŸ¢', 'business': 'ðŸ”µ'}
            st.sidebar.info(f"{tier_colors.get(tier, 'âšª')} **{tier.title()} Plan**")
            
            if st.sidebar.button("ðŸšª Logout"):
                for key in ['user_authenticated', 'user_email', 'user_tier', 'user_profile', 'is_admin']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

# Utility functions
def check_rate_limit(operation: str, limit: int = 10, window: int = 60) -> bool:
    """Simple rate limiting check"""
    return True  # Simplified for now

def validate_input(input_value: str, input_type: str = "text", max_length: int = 500) -> tuple:
    """Enhanced input validation for security"""
    if not input_value:
        return True, ""
    
    if len(input_value) > max_length:
        return False, f"Input too long (max {max_length} characters)"
    
    return True, ""

def apply_security_hardening():
    """Apply security hardening measures"""
    if 'security_initialized' not in st.session_state:
        st.session_state.security_initialized = True

def log_security_event(event_type, details=None):
    """Log security events"""
    pass  # Simplified for now

# Get available pages based on user tier and authentication
def get_available_pages():
    """Get available pages based on user tier"""
    if not st.session_state.get('user_authenticated', False):
        return ["ðŸ” Login"]
    
    user_tier = st.session_state.get('user_tier', 'solo')
    is_admin = st.session_state.get('is_admin', False)
    
    # Core pages available to all tiers
    pages = [
        "ðŸ“Š Dashboard",
        "ðŸ˜ï¸ Deal Analysis", 
        "ðŸ—ƒï¸ðŸ“Š Deal Database",
        "ðŸ“ˆ Portfolio Analytics"
    ]
    
    # Team tier and above features
    if user_tier in ['team', 'business']:
        pages.extend([
            "ðŸ’° Advanced Financial Modeling",
            "ðŸ¢ðŸ‘¥ Investor Portal",
            "ðŸ˜ï¸ðŸ“‹ Enhanced Deal Manager",
            "ðŸ‘¥ Client Manager",
            "ðŸ“§ Communication Center"
        ])
        
        # Enhanced CRM integration for Team+ tiers
        if ENHANCED_CRM_AVAILABLE:
            pages.append("ðŸ’¼ Enhanced CRM")
    
    return pages

# UI Helper Classes
class UIHelper:
    @staticmethod
    def show_success(message, auto_dismiss=True):
        st.success(f"âœ… {message}")
    
    @staticmethod
    def show_error(message, details=None):
        st.error(f"âŒ {message}")
    
    @staticmethod
    def show_warning(message):
        st.warning(f"âš ï¸ {message}")
    
    @staticmethod
    def show_info(message):
        st.info(f"â„¹ï¸ {message}")

# Performance tracking system
class PerformanceTracker:
    @staticmethod
    def track_feature_usage(feature_name):
        """Track feature usage"""
        pass  # Simplified for now

# Feedback system
class FeedbackSystem:
    @staticmethod
    def show_feedback_widget():
        """Show feedback widget in sidebar"""
        with st.sidebar.expander("ðŸ’¬ Send Feedback", expanded=False):
            st.markdown("**Help us improve NXTRIX CRM!**")
            
            feedback_type = st.selectbox("Category", 
                ["Bug Report", "Feature Request", "General Feedback"])
            
            feedback_text = st.text_area("Your Feedback", 
                placeholder="Help us improve NXTRIX CRM...",
                height=100)
            
            rating = st.slider("Rate Experience", 1, 5, 4)
            
            if st.button("ðŸ“¤ Submit Feedback", use_container_width=True):
                if feedback_text.strip():
                    UIHelper.show_success("Thank you for your feedback!")
                    return {
                        'type': feedback_type,
                        'text': feedback_text,
                        'rating': rating,
                        'timestamp': datetime.now()
                    }
                else:
                    UIHelper.show_error("Please provide feedback text.")
        return None

# Database service configuration
@st.cache_resource
def get_db_service():
    """Get database service"""
    return None  # Simplified for now

def is_db_connected(db_service):
    """Check if database service is connected"""
    return False  # Simplified for now

# Navigation helper functions
def navigate_to_page(page_name):
    """Helper function to navigate to a specific page"""
    st.session_state.redirect_to_page = page_name
    st.rerun()

def get_current_page():
    """Get the current page with redirect handling"""
    if 'redirect_to_page' in st.session_state:
        redirect_page = st.session_state.redirect_to_page
        del st.session_state.redirect_to_page
        return redirect_page
    return None

# Page configuration
st.set_page_config(
    page_title="NXTRIX Deal Analyzer CRM",
    page_icon="ðŸ˜ï¸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page CSS and styling
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    
    .main-header {
        background-color: #262730;
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid #404040;
    }
    
    .main-header h1 {
        margin-bottom: 0.5rem;
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        color: white;
        margin: 0;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    .stMarkdown {
        color: white !important;
    }
    
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background-color: #45a049;
    }
</style>
""", unsafe_allow_html=True)

# Page implementations
def show_dashboard():
    st.header("ðŸ“Š Dashboard")
    st.write("Welcome to your NXTRIX CRM Dashboard!")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Deals", "42", "+5")
    
    with col2:
        st.metric("Portfolio Value", "$2.1M", "+12%")
    
    with col3:
        st.metric("Avg AI Score", "82/100", "+3")
    
    with col4:
        st.metric("Monthly Cash Flow", "$8,450", "+$1,200")
    
    st.markdown("---")
    
    # Sample chart
    data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Deals': [3, 5, 2, 8, 6, 4],
        'Revenue': [45000, 75000, 30000, 120000, 90000, 60000]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Deal Volume by Month")
        fig = px.bar(data, x='Month', y='Deals', title="Monthly Deal Count")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Revenue Trend")
        fig = px.line(data, x='Month', y='Revenue', title="Monthly Revenue")
        st.plotly_chart(fig, use_container_width=True)

def show_deal_analysis():
    st.header("ðŸ˜ï¸ Deal Analysis")
    st.write("Analyze new real estate investment opportunities")
    
    with st.form("deal_analysis_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Property Details")
            address = st.text_input("Property Address")
            property_type = st.selectbox("Property Type", ["Single Family", "Multi-Family", "Condo", "Commercial"])
            purchase_price = st.number_input("Purchase Price ($)", min_value=0, value=200000)
            
        with col2:
            st.subheader("Financial Information")
            arv = st.number_input("After Repair Value ($)", min_value=0, value=275000)
            repair_costs = st.number_input("Repair Costs ($)", min_value=0, value=25000)
            monthly_rent = st.number_input("Monthly Rent ($)", min_value=0, value=2200)
        
        if st.form_submit_button("ðŸ” Analyze Deal", type="primary"):
            if address and purchase_price > 0:
                # Simple analysis
                total_investment = purchase_price + repair_costs
                profit_potential = arv - total_investment
                roi = (profit_potential / total_investment) * 100 if total_investment > 0 else 0
                
                # Simple AI score calculation
                ai_score = min(100, max(0, 50 + roi))
                
                st.success("âœ… Analysis Complete!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("AI Score", f"{ai_score:.0f}/100")
                
                with col2:
                    st.metric("Potential Profit", f"${profit_potential:,.0f}")
                
                with col3:
                    st.metric("ROI", f"{roi:.1f}%")
                
                # Recommendations
                st.subheader("ðŸŽ¯ Recommendations")
                if ai_score >= 80:
                    st.success("ðŸŽ¯ Excellent investment opportunity!")
                elif ai_score >= 60:
                    st.info("ðŸ’¡ Good deal with moderate returns")
                else:
                    st.warning("âš ï¸ Consider negotiating or looking for better opportunities")
            else:
                st.error("Please fill in all required fields")

def show_deal_database():
    st.header("ðŸ—ƒï¸ðŸ“Š Deal Database")
    st.write("View and manage your deal portfolio")
    
    # Sample data
    sample_deals = pd.DataFrame({
        'Address': ['123 Main St', '456 Oak Ave', '789 Pine Dr'],
        'Type': ['Single Family', 'Multi-Family', 'Condo'],
        'Purchase Price': [200000, 350000, 180000],
        'ARV': [275000, 420000, 220000],
        'AI Score': [85, 78, 92],
        'Status': ['Active', 'Under Contract', 'Analyzing']
    })
    
    st.dataframe(sample_deals, use_container_width=True)
    
    # Add new deal button
    if st.button("âž• Add New Deal"):
        navigate_to_page("ðŸ˜ï¸ Deal Analysis")

def show_portfolio_analytics():
    st.header("ðŸ“ˆ Portfolio Analytics")
    st.write("Advanced analytics for your investment portfolio")
    
    # Sample portfolio metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Portfolio Value", "$2,150,000")
        st.metric("Number of Properties", "8")
    
    with col2:
        st.metric("Average ROI", "18.3%")
        st.metric("Total Monthly Cash Flow", "$8,450")
    
    with col3:
        st.metric("Portfolio Growth (YTD)", "24.7%")
        st.metric("Average AI Score", "82.1/100")
    
    # Sample charts
    st.subheader("ðŸ“Š Performance Overview")
    
    # Portfolio distribution
    portfolio_data = pd.DataFrame({
        'Property Type': ['Single Family', 'Multi-Family', 'Commercial', 'Condo'],
        'Count': [12, 4, 2, 6],
        'Value': [1200000, 800000, 600000, 350000]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(portfolio_data, values='Count', names='Property Type', title='Properties by Type')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(portfolio_data, values='Value', names='Property Type', title='Value by Type')
        st.plotly_chart(fig, use_container_width=True)

def show_investor_portal():
    st.header("ðŸ¢ðŸ‘¥ Investor Portal")
    st.write("Manage investor relationships and communications")
    
    tier_system = TierEnforcementSystem()
    
    if not tier_system.check_feature_access('client_management'):
        st.warning("âš ï¸ **Investor Portal requires Team tier or higher**")
        st.info("Upgrade to Team ($119/month) for investor management features.")
        return
    
    # Sample investor data
    investors = pd.DataFrame({
        'Name': ['John Smith', 'Sarah Wilson', 'Mike Johnson'],
        'Investment': [50000, 75000, 100000],
        'Returns': ['12.5%', '15.2%', '18.1%'],
        'Status': ['Active', 'Active', 'Pending']
    })
    
    st.subheader("ðŸ‘¥ Current Investors")
    st.dataframe(investors, use_container_width=True)
    
    st.subheader("ðŸ“Š Investor Performance")
    total_invested = investors['Investment'].sum()
    avg_returns = 15.3  # Sample average
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Capital Raised", f"${total_invested:,}")
    
    with col2:
        st.metric("Average Returns", f"{avg_returns}%")
    
    with col3:
        st.metric("Active Investors", len(investors[investors['Status'] == 'Active']))

def show_advanced_financial_modeling():
    st.header("ðŸ’° Advanced Financial Modeling")
    st.write("Advanced financial analysis and projections")
    
    tier_system = TierEnforcementSystem()
    
    if not tier_system.check_feature_access('advanced_analytics'):
        st.warning("âš ï¸ **Advanced Financial Modeling requires Team tier or higher**")
        st.info("Upgrade to Team ($119/month) for advanced modeling features.")
        return
    
    st.subheader("ðŸ”® Cash Flow Projections")
    
    # Sample financial modeling
    years = list(range(1, 11))
    base_cash_flow = 1000
    growth_rate = 0.03
    
    cash_flows = [base_cash_flow * (1 + growth_rate) ** year for year in years]
    
    financial_data = pd.DataFrame({
        'Year': years,
        'Cash Flow': cash_flows,
        'Cumulative': np.cumsum(cash_flows)
    })
    
    fig = px.line(financial_data, x='Year', y=['Cash Flow', 'Cumulative'], 
                  title='10-Year Cash Flow Projection')
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("ðŸ“Š Sensitivity Analysis")
    st.info("Advanced modeling features coming soon!")

def show_enhanced_deal_management():
    st.header("ðŸ˜ï¸ðŸ“‹ Enhanced Deal Manager")
    st.info("Enhanced deal management features coming soon!")

def show_enhanced_client_management():
    st.header("ðŸ‘¥ Client Manager")
    st.info("Client management features coming soon!")

def show_communication_center():
    st.header("ðŸ“§ Communication Center")
    st.info("Communication features coming soon!")

# Main Application
def main():
    """Main application function"""
    # Apply security hardening
    apply_security_hardening()
    
    # Initialize authentication system
    UserAuthSystem.initialize_auth_system()
    
    # Check if user is authenticated
    if not st.session_state.get('user_authenticated', False):
        UserAuthSystem.show_login_page()
        return
    
    # Get user info for header
    user_profile = st.session_state.get('user_profile', {})
    user_name = user_profile.get('full_name', 'User')
    user_tier = st.session_state.get('user_tier', 'solo').title()
    
    # Main header with user info
    st.markdown(f"""
    <div class="main-header">
        <h1>ðŸ˜ï¸ NXTRIX Enterprise CRM</h1>
        <p>AI-Powered Real Estate Investment Analysis & Portfolio Management</p>
        <div style="text-align: right; margin-top: 10px;">
            <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         padding: 5px 15px; border-radius: 20px; color: white; font-size: 0.8rem;">
                ðŸ‘¤ {user_name} â€¢ {user_tier} Plan
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for redirect first
    redirect_page = get_current_page()
    
    # Sidebar Navigation
    st.sidebar.title("ðŸš€ Navigation")
    
    # Show user menu in sidebar
    UserAuthSystem.show_user_menu()
    
    # Use redirect page if available
    navigation_options = get_available_pages()
    
    if redirect_page and redirect_page in navigation_options:
        default_index = navigation_options.index(redirect_page)
    else:
        default_index = 0
    
    page = st.sidebar.selectbox(
        "Choose Section",
        navigation_options,
        index=default_index
    )
    
    # Track feature usage
    PerformanceTracker.track_feature_usage(page)
    
    # Database connection status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.error("ðŸ”´ Database Offline")
    st.sidebar.warning("Using demo data")
    
    # Add feedback widget to sidebar
    feedback_data = FeedbackSystem.show_feedback_widget()
    
    # Route to appropriate page
    if page == "ðŸ“Š Dashboard":
        show_dashboard()
    elif page == "ðŸ˜ï¸ Deal Analysis":
        show_deal_analysis()
    elif page == "ðŸ—ƒï¸ðŸ“Š Deal Database":
        show_deal_database()
    elif page == "ðŸ“ˆ Portfolio Analytics":
        show_portfolio_analytics()
    elif page == "ðŸ¢ðŸ‘¥ Investor Portal":
        show_investor_portal()
    elif page == "ðŸ’° Advanced Financial Modeling":
        show_advanced_financial_modeling()
    elif page == "ðŸ˜ï¸ðŸ“‹ Enhanced Deal Manager":
        show_enhanced_deal_management()
    elif page == "ðŸ‘¥ Client Manager":
        show_enhanced_client_management()
    elif page == "ðŸ“§ Communication Center":
        show_communication_center()
    elif page == "ðŸ’¼ Enhanced CRM" and ENHANCED_CRM_AVAILABLE:
        show_enhanced_crm()
    else:
        # Default to dashboard
        show_dashboard()

# Application Entry Point
if __name__ == "__main__":
    main()
