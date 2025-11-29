"""
NXTRIX 3.0 - Enterprise CRM Platform with Billing Integration
Complete CRM system with automated billing, trial management, and payment processing
Built with Streamlit + Supabase integration
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
import time
import uuid
import hashlib
import secrets
import re
import json
from typing import Dict, Any, List, Optional
import numpy as np
from pathlib import Path
from io import BytesIO
import base64
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our billing and authentication systems
try:
    from supabase_auth_bridge import supabase_auth
    SUPABASE_AVAILABLE = True
except ImportError as e:
    st.error(f"Supabase connection not available: {e}")
    SUPABASE_AVAILABLE = False

# Configure Streamlit page
st.set_page_config(
    page_title="NXTRIX 3.0 - Enterprise CRM",
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global CSS styling
st.markdown("""
<style>
/* Main styling */
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid #667eea;
}

.trial-status {
    background: linear-gradient(90deg, #ffeaa7 0%, #fdcb6e 100%);
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

.billing-alert {
    background: linear-gradient(90deg, #ff7675 0%, #fd79a8 100%);
    padding: 1rem;
    border-radius: 8px;
    color: white;
    margin: 1rem 0;
}

.sidebar-content {
    padding: 1rem;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 600;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

# Simple Authentication System for Demo
class SimpleAuth:
    def __init__(self):
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_data' not in st.session_state:
            st.session_state.user_data = None

    def is_authenticated(self):
        return st.session_state.authenticated

    def get_current_user(self):
        return st.session_state.user_data

    def login(self, email, password):
        # Simple demo authentication
        if email and password:
            st.session_state.authenticated = True
            st.session_state.user_data = {
                'email': email,
                'full_name': email.split('@')[0].title(),
                'subscription_tier': 'trial',
                'trial_end_date': (datetime.now() + timedelta(days=7)).isoformat(),
                'trial_active': True,
                'billing_collected': True
            }
            return True
        return False

    def logout(self):
        st.session_state.authenticated = False
        st.session_state.user_data = None

    def render_auth_page(self):
        st.markdown('<div class="main-header"><h1>🚀 Welcome to NXTRIX 3.0</h1><p>Enterprise CRM with Automated Billing</p></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "🎯 Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                st.subheader("Login to Your Account")
                email = st.text_input("Email Address", placeholder="Enter your email")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                if st.form_submit_button("🚀 Login", type="primary"):
                    if self.login(email, password):
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")

        with tab2:
            st.subheader("🎯 Start Your 7-Day Free Trial")
            st.markdown("""
            ### 💳 Billing Information Required
            To start your trial, we need your payment information. **You won't be charged until your trial ends.**
            
            **Subscription Plans:**
            - **Starter**: $89/month (2,500 contacts, email automation)
            - **Professional**: $189/month (10,000 contacts, AI features) 
            - **Enterprise**: $349/month (Unlimited, complete AI suite)
            """)
            
            if st.button("🚀 Start Free Trial with Billing Setup", type="primary"):
                st.info("🔄 Redirecting to billing signup...")
                st.markdown("**In production, this would redirect to the billing signup form**")

# Initialize authentication
auth = SimpleAuth()

# Trial Status Manager
class TrialStatusManager:
    @staticmethod
    def check_trial_status(user_data):
        if not user_data or not user_data.get('trial_end_date'):
            return {"status": "error", "message": "Invalid user data"}
        
        trial_end = datetime.fromisoformat(user_data['trial_end_date'].replace('Z', '+00:00'))
        now = datetime.now()
        
        if now > trial_end:
            return {
                "status": "expired",
                "message": "Trial has expired",
                "trial_expired": True
            }
        
        days_left = (trial_end - now).days
        return {
            "status": "active", 
            "trial_days_left": days_left,
            "trial_end_date": trial_end.strftime("%B %d, %Y")
        }

    @staticmethod
    def render_trial_widget(user_data):
        trial_status = TrialStatusManager.check_trial_status(user_data)
        
        if trial_status.get('trial_expired'):
            st.markdown("""
            <div class="billing-alert">
            <h3>⚠️ Trial Expired</h3>
            <p>Your 7-day trial has ended. Please upgrade to continue using NXTRIX.</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("👤 Starter - $89/month"):
                    st.info("🔄 Upgrade to Starter plan")
            with col2:
                if st.button("👥 Professional - $189/month"):
                    st.info("🔄 Upgrade to Professional plan")
            with col3:
                if st.button("🏢 Enterprise - $349/month"):
                    st.info("🔄 Upgrade to Enterprise plan")
        else:
            days_left = trial_status.get('trial_days_left', 0)
            if days_left <= 3:
                st.markdown(f"""
                <div class="trial-status">
                <h4>⏰ Trial expires in {days_left} days</h4>
                <p>Trial ends on {trial_status.get('trial_end_date', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info(f"✅ Free trial active - {days_left} days remaining")

# Main CRM Application
class NXTRIXApp:
    def __init__(self):
        self.user_data = auth.get_current_user()

    def render_sidebar(self):
        with st.sidebar:
            st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
            
            # User info
            if self.user_data:
                st.markdown(f"### 👤 {self.user_data['full_name']}")
                st.markdown(f"**Plan:** {self.user_data.get('subscription_tier', 'trial').title()}")
                
                # Trial status
                TrialStatusManager.render_trial_widget(self.user_data)
                
                st.markdown("---")
                
                # Navigation
                st.markdown("### 🚀 Navigation")
                
                # Set default page
                if 'current_page' not in st.session_state:
                    st.session_state.current_page = 'dashboard'
                
                pages = {
                    'dashboard': '📊 Dashboard',
                    'contacts': '👥 Contacts', 
                    'deals': '💼 Deals',
                    'analytics': '📈 Analytics',
                    'billing': '💳 Billing',
                    'settings': '⚙️ Settings'
                }
                
                for page_key, page_name in pages.items():
                    if st.button(page_name, key=page_key, use_container_width=True):
                        st.session_state.current_page = page_key
                
                st.markdown("---")
                if st.button("🚪 Logout", use_container_width=True):
                    auth.logout()
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

    def render_dashboard(self):
        st.markdown('<div class="main-header"><h1>📊 NXTRIX Dashboard</h1></div>', unsafe_allow_html=True)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
            <h3>👥 Total Contacts</h3>
            <h2>1,247</h2>
            <p style="color: green;">↗️ +12% this month</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
            <h3>💼 Active Deals</h3>
            <h2>89</h2>
            <p style="color: green;">↗️ +8% this month</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
            <h3>💰 Revenue</h3>
            <h2>$124,567</h2>
            <p style="color: green;">↗️ +15% this month</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
            <h3>📈 Conversion</h3>
            <h2>23.4%</h2>
            <p style="color: green;">↗️ +3.2% this month</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Deal Pipeline")
            
            # Sample pipeline data
            stages = ['Lead', 'Qualified', 'Proposal', 'Negotiation', 'Closed Won']
            values = [45, 32, 18, 12, 8]
            
            fig = go.Figure(go.Funnel(
                y=stages,
                x=values,
                textinfo="value+percent initial",
                marker={"color": ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe"]}
            ))
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("💰 Revenue Trend")
            
            # Sample revenue data
            dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
            revenue = np.cumsum(np.random.normal(10000, 2000, len(dates)))
            
            fig = px.line(
                x=dates, 
                y=revenue,
                title="Monthly Revenue Growth",
                color_discrete_sequence=['#667eea']
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity
        st.subheader("📋 Recent Activity")
        
        activities = [
            {"time": "2 minutes ago", "activity": "New contact added: John Smith", "type": "contact"},
            {"time": "15 minutes ago", "activity": "Deal closed: $15,000 property investment", "type": "deal"},
            {"time": "1 hour ago", "activity": "Email campaign sent to 150 contacts", "type": "email"},
            {"time": "3 hours ago", "activity": "New lead from website form", "type": "lead"},
            {"time": "1 day ago", "activity": "Meeting scheduled with investor", "type": "meeting"}
        ]
        
        for activity in activities:
            icon = {"contact": "👤", "deal": "💼", "email": "📧", "lead": "🎯", "meeting": "📅"}
            st.write(f"{icon.get(activity['type'], '📋')} **{activity['time']}** - {activity['activity']}")

    def render_contacts(self):
        st.markdown('<div class="main-header"><h1>👥 Contact Management</h1></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("➕ Add New Contact", type="primary"):
                st.session_state.show_add_contact = True
        
        # Sample contacts data
        contacts_data = {
            'Name': ['John Smith', 'Sarah Johnson', 'Mike Wilson', 'Emma Davis', 'Robert Brown'],
            'Email': ['john@email.com', 'sarah@email.com', 'mike@email.com', 'emma@email.com', 'robert@email.com'],
            'Phone': ['+1-555-0101', '+1-555-0102', '+1-555-0103', '+1-555-0104', '+1-555-0105'],
            'Status': ['Hot Lead', 'Qualified', 'New', 'Nurturing', 'Converted'],
            'Last Contact': ['2024-11-28', '2024-11-27', '2024-11-26', '2024-11-25', '2024-11-24']
        }
        
        df_contacts = pd.DataFrame(contacts_data)
        
        # Search and filter
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term = st.text_input("🔍 Search contacts", placeholder="Name, email, or phone")
        with col2:
            status_filter = st.selectbox("Filter by Status", ['All'] + df_contacts['Status'].unique().tolist())
        with col3:
            sort_by = st.selectbox("Sort by", ['Name', 'Last Contact', 'Status'])
        
        # Display contacts table
        st.dataframe(df_contacts, use_container_width=True)
        
        # Add contact form
        if st.session_state.get('show_add_contact', False):
            with st.expander("➕ Add New Contact", expanded=True):
                with st.form("add_contact_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("Full Name*")
                        email = st.text_input("Email*")
                    with col2:
                        phone = st.text_input("Phone")
                        status = st.selectbox("Status", ['New', 'Hot Lead', 'Qualified', 'Nurturing'])
                    
                    notes = st.text_area("Notes")
                    
                    if st.form_submit_button("✅ Add Contact", type="primary"):
                        if name and email:
                            st.success(f"✅ Contact {name} added successfully!")
                            st.session_state.show_add_contact = False
                            st.rerun()
                        else:
                            st.error("❌ Name and email are required")

    def render_deals(self):
        st.markdown('<div class="main-header"><h1>💼 Deal Management</h1></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("➕ Add New Deal", type="primary"):
                st.session_state.show_add_deal = True
        
        # Sample deals data
        deals_data = {
            'Deal Name': ['123 Main St Investment', 'Downtown Office Complex', 'Retail Plaza', 'Warehouse Property', 'Residential Complex'],
            'Value': ['$250,000', '$1,200,000', '$850,000', '$500,000', '$750,000'],
            'Stage': ['Proposal', 'Negotiation', 'Due Diligence', 'Closed Won', 'Qualified'],
            'Probability': ['75%', '60%', '90%', '100%', '45%'],
            'Close Date': ['2024-12-15', '2025-01-30', '2024-12-05', '2024-11-20', '2025-02-15']
        }
        
        df_deals = pd.DataFrame(deals_data)
        
        # Deal pipeline visualization
        st.subheader("📊 Deal Pipeline Overview")
        
        pipeline_data = df_deals['Stage'].value_counts()
        fig = px.bar(
            x=pipeline_data.index,
            y=pipeline_data.values,
            title="Deals by Stage",
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Deals table
        st.subheader("📋 All Deals")
        st.dataframe(df_deals, use_container_width=True)
        
        # Add deal form
        if st.session_state.get('show_add_deal', False):
            with st.expander("➕ Add New Deal", expanded=True):
                with st.form("add_deal_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        deal_name = st.text_input("Deal Name*")
                        value = st.number_input("Deal Value ($)", min_value=0)
                    with col2:
                        stage = st.selectbox("Stage", ['Lead', 'Qualified', 'Proposal', 'Negotiation', 'Due Diligence', 'Closed Won', 'Closed Lost'])
                        close_date = st.date_input("Expected Close Date")
                    
                    description = st.text_area("Deal Description")
                    
                    if st.form_submit_button("✅ Add Deal", type="primary"):
                        if deal_name and value:
                            st.success(f"✅ Deal '{deal_name}' added successfully!")
                            st.session_state.show_add_deal = False
                            st.rerun()
                        else:
                            st.error("❌ Deal name and value are required")

    def render_analytics(self):
        st.markdown('<div class="main-header"><h1>📈 Advanced Analytics</h1></div>', unsafe_allow_html=True)
        
        # Time period selector
        col1, col2, col3 = st.columns(3)
        with col1:
            period = st.selectbox("Time Period", ['Last 30 days', 'Last 90 days', 'Last 6 months', 'Last year'])
        with col2:
            metric = st.selectbox("Primary Metric", ['Revenue', 'Deal Count', 'Conversion Rate', 'Contact Growth'])
        with col3:
            comparison = st.selectbox("Compare to", ['Previous Period', 'Same Period Last Year', 'Baseline'])
        
        # Key metrics dashboard
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Revenue", "$124,567", "+15.3%")
        with col2:
            st.metric("Conversion Rate", "23.4%", "+3.2%")
        with col3:
            st.metric("Avg Deal Size", "$28,456", "+8.7%")
        with col4:
            st.metric("Pipeline Value", "$2.1M", "+12.1%")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Revenue by Month")
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            revenue_by_month = [15000, 18000, 22000, 25000, 28000, 32000, 35000, 38000, 41000, 45000, 48000, 52000]
            
            fig = px.bar(x=months, y=revenue_by_month, color_discrete_sequence=['#667eea'])
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Lead Sources")
            sources = ['Website', 'Referrals', 'Cold Outreach', 'Social Media', 'Events']
            leads = [45, 25, 15, 10, 5]
            
            fig = px.pie(values=leads, names=sources, color_discrete_sequence=px.colors.sequential.Plasma)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance insights
        st.subheader("🎯 Performance Insights")
        
        insights = [
            {"icon": "📈", "title": "Revenue Growth", "description": "Revenue increased 15.3% compared to last month", "status": "positive"},
            {"icon": "🎯", "title": "Conversion Improvement", "description": "Lead to customer conversion rate improved by 3.2%", "status": "positive"},
            {"icon": "⏰", "title": "Sales Cycle", "description": "Average sales cycle decreased by 2 days", "status": "positive"},
            {"icon": "⚠️", "title": "Pipeline Risk", "description": "3 large deals are at risk of slipping this quarter", "status": "warning"}
        ]
        
        for insight in insights:
            if insight['status'] == 'positive':
                st.success(f"{insight['icon']} **{insight['title']}**: {insight['description']}")
            else:
                st.warning(f"{insight['icon']} **{insight['title']}**: {insight['description']}")

    def render_billing(self):
        st.markdown('<div class="main-header"><h1>💳 Billing & Subscription</h1></div>', unsafe_allow_html=True)
        
        # Current subscription info
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Current Subscription")
            
            trial_status = TrialStatusManager.check_trial_status(self.user_data)
            
            if trial_status.get('trial_expired'):
                st.error("⚠️ Your trial has expired. Please choose a subscription plan.")
            else:
                days_left = trial_status.get('trial_days_left', 0)
                st.info(f"✅ **Free Trial Active** - {days_left} days remaining")
                st.write(f"Trial ends on: {trial_status.get('trial_end_date', 'N/A')}")
        
        with col2:
            if st.button("🔄 Update Payment Method", type="primary"):
                st.info("🔄 Payment method update functionality")
        
        st.markdown("---")
        
        # Subscription plans
        st.subheader("🎯 Choose Your Plan")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **👤 Starter Plan**
            ### $89/month
            
            **Features:**
            - 2,500 contacts
            - 250 deals  
            - Email automation (1,000/month)
            - SMS credits (500/month)
            - Basic reporting
            - Email support
            
            *Perfect for small teams*
            """)
            
            if st.button("Choose Starter", key="starter_plan"):
                st.success("🔄 Upgrading to Starter plan...")
        
        with col2:
            st.markdown("""
            **👥 Professional Plan** ⭐
            ### $189/month
            
            **Features:**
            - 10,000 contacts
            - Unlimited deals
            - **🚀 FULL AI Insights + Voice Commands**
            - Advanced email automation (5,000/month)
            - SMS credits (2,000/month)
            - Advanced analytics
            - API access
            - Priority support
            
            *Most Popular Choice*
            """)
            
            if st.button("Choose Professional", key="pro_plan", type="primary"):
                st.success("🔄 Upgrading to Professional plan...")
        
        with col3:
            st.markdown("""
            **🏢 Enterprise Plan**
            ### $349/month
            
            **Features:**
            - Unlimited contacts & deals
            - **🤖 Complete AI Suite + Voice AI**
            - Unlimited email automation
            - Unlimited SMS credits
            - Custom integrations
            - White-label options
            - Dedicated account manager
            - 24/7 phone support
            
            *For large organizations*
            """)
            
            if st.button("Choose Enterprise", key="enterprise_plan"):
                st.success("🔄 Upgrading to Enterprise plan...")
        
        st.markdown("---")
        
        # Billing history
        st.subheader("📊 Billing History")
        
        billing_data = {
            'Date': ['2024-11-01', '2024-10-01', '2024-09-01'],
            'Amount': ['$89.00', '$89.00', '$89.00'],
            'Status': ['Paid', 'Paid', 'Paid'],
            'Invoice': ['INV-001', 'INV-002', 'INV-003']
        }
        
        df_billing = pd.DataFrame(billing_data)
        st.dataframe(df_billing, use_container_width=True)

    def render_settings(self):
        st.markdown('<div class="main-header"><h1>⚙️ Settings</h1></div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔔 Notifications", "🔐 Security"])
        
        with tab1:
            st.subheader("Profile Information")
            
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Full Name", value=self.user_data.get('full_name', ''))
                st.text_input("Email", value=self.user_data.get('email', ''))
            with col2:
                st.text_input("Phone", placeholder="Enter your phone number")
                st.selectbox("Time Zone", ['UTC', 'EST', 'CST', 'MST', 'PST'])
            
            if st.button("💾 Save Profile"):
                st.success("✅ Profile updated successfully!")
        
        with tab2:
            st.subheader("Notification Preferences")
            
            st.checkbox("📧 Email notifications for new leads", value=True)
            st.checkbox("📱 SMS notifications for urgent deals", value=False)
            st.checkbox("🔔 Browser notifications", value=True)
            st.checkbox("📊 Weekly performance reports", value=True)
            
            if st.button("💾 Save Notifications"):
                st.success("✅ Notification preferences updated!")
        
        with tab3:
            st.subheader("Security Settings")
            
            st.text_input("Current Password", type="password")
            st.text_input("New Password", type="password")
            st.text_input("Confirm New Password", type="password")
            
            st.checkbox("🔐 Enable two-factor authentication", value=False)
            
            if st.button("💾 Update Security"):
                st.success("✅ Security settings updated!")

    def run(self):
        """Main application runner"""
        
        # Check authentication
        if not auth.is_authenticated():
            auth.render_auth_page()
            return
        
        # Render sidebar
        self.render_sidebar()
        
        # Render main content based on current page
        current_page = st.session_state.get('current_page', 'dashboard')
        
        if current_page == 'dashboard':
            self.render_dashboard()
        elif current_page == 'contacts':
            self.render_contacts()
        elif current_page == 'deals':
            self.render_deals()
        elif current_page == 'analytics':
            self.render_analytics()
        elif current_page == 'billing':
            self.render_billing()
        elif current_page == 'settings':
            self.render_settings()

# Application Entry Point
def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_page = 'dashboard'
    
    # Run the application
    app = NXTRIXApp()
    app.run()

if __name__ == "__main__":
    main()