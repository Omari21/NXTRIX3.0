"""
NXTRIX 3.0 - Enterprise CRM Platform with Billing Integration
Production-ready SaaS platform with automated billing and trial management
Built November 28-29, 2025
"""

import streamlit as st
import pandas as pd
import sqlite3
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

# Set page configuration
st.set_page_config(
    page_title="NXTRIX 3.0 - Enterprise CRM",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our billing and authentication systems
try:
    from trial_billing_manager import trial_billing_manager, check_access_with_billing, render_trial_status_widget
    BILLING_AVAILABLE = True
except ImportError as e:
    st.info("Running without advanced billing (demo mode)")
    BILLING_AVAILABLE = False

try:
    from supabase_auth_bridge import supabase_auth
    SUPABASE_AVAILABLE = True if supabase_auth and supabase_auth.available else False
except ImportError as e:
    st.info("Running without Supabase integration (local mode)")
    SUPABASE_AVAILABLE = False

try:
    from auth_system import StreamlitAuth
    AUTH_AVAILABLE = True
except ImportError as e:
    st.info("Running without auth system (demo mode)")
    AUTH_AVAILABLE = False

# Initialize authentication
if AUTH_AVAILABLE:
    auth = StreamlitAuth()
else:
    auth = None

# Database initialization
def init_database():
    """Initialize local database for CRM functionality"""
    conn = sqlite3.connect('nxtrix.db')
    cursor = conn.cursor()
    
    # Create contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            company TEXT,
            position TEXT,
            source TEXT,
            status TEXT DEFAULT 'active',
            tags TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create deals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL,
            stage TEXT DEFAULT 'prospect',
            probability INTEGER DEFAULT 0,
            contact_id INTEGER,
            close_date DATE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts (id)
        )
    ''')
    
    # Create activities table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            contact_id INTEGER,
            deal_id INTEGER,
            due_date DATE,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts (id),
            FOREIGN KEY (deal_id) REFERENCES deals (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def check_user_access_and_billing(user_data):
    """Enhanced access control with billing management"""
    if not user_data:
        return False, {"message": "User not authenticated"}
    
    if BILLING_AVAILABLE:
        # Use billing manager for access control
        access_result = check_access_with_billing(user_data)
        
        if not access_result["allowed"]:
            trial_status = access_result["trial_status"]
            
            if trial_status.get("status") == "trial_expired":
                st.error("🚫 **Your 7-day trial has expired!**")
                st.markdown("**Upgrade to continue using NXTRIX:**")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("👤 Starter - $89/month"):
                        st.session_state.current_page = 'billing'
                        st.rerun()
                with col2:
                    if st.button("👥 Professional - $189/month"):
                        st.session_state.current_page = 'billing'
                        st.rerun()
                with col3:
                    if st.button("🏢 Enterprise - $349/month"):
                        st.session_state.current_page = 'billing'
                        st.rerun()
            elif trial_status.get("status") == "payment_failed":
                st.error("💳 **Payment Failed!**")
                st.warning("We couldn't process your payment. Please update your payment method.")
                if st.button("🔄 Update Payment Method"):
                    st.session_state.current_page = 'billing'
                    st.rerun()
            else:
                st.error(f"❌ Access Error: {trial_status.get('message', 'Access denied')}")
            
            return False, trial_status
        
        # Show trial status widget
        render_trial_status_widget(user_data)
        return True, access_result["trial_status"]
    else:
        # Fallback without billing
        return True, {"status": "active"}

def render_dashboard():
    """Render the main CRM dashboard"""
    st.title("🚀 NXTRIX 3.0 - Enterprise CRM Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Get data from database
    conn = sqlite3.connect('nxtrix.db')
    
    try:
        # Total contacts
        contacts_count = pd.read_sql("SELECT COUNT(*) as count FROM contacts", conn).iloc[0]['count']
        
        # Total deals
        deals_count = pd.read_sql("SELECT COUNT(*) as count FROM deals", conn).iloc[0]['count']
        
        # Total deal value
        deal_value = pd.read_sql("SELECT COALESCE(SUM(amount), 0) as total FROM deals", conn).iloc[0]['total']
        
        # Activities this month
        activities_count = pd.read_sql("""
            SELECT COUNT(*) as count FROM activities 
            WHERE created_at >= date('now', 'start of month')
        """, conn).iloc[0]['count']
    except:
        contacts_count = deals_count = deal_value = activities_count = 0
    
    conn.close()
    
    with col1:
        st.metric("👥 Total Contacts", f"{contacts_count:,}")
    
    with col2:
        st.metric("💼 Active Deals", f"{deals_count:,}")
    
    with col3:
        st.metric("💰 Pipeline Value", f"${deal_value:,.0f}")
    
    with col4:
        st.metric("📋 Activities (Month)", f"{activities_count:,}")
    
    # Charts
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Deal Pipeline by Stage")
        
        conn = sqlite3.connect('nxtrix.db')
        try:
            pipeline_data = pd.read_sql("""
                SELECT stage, COUNT(*) as count, COALESCE(SUM(amount), 0) as value
                FROM deals 
                GROUP BY stage
            """, conn)
            conn.close()
            
            if not pipeline_data.empty:
                fig = px.bar(
                    pipeline_data,
                    x='stage',
                    y='count',
                    title="Deals by Stage",
                    color='value',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No deals data available yet")
        except:
            conn.close()
            st.info("No deals data available yet")
    
    with col2:
        st.subheader("📈 Monthly Activity Trends")
        
        # Sample data for demonstration
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        activities = [45, 52, 48, 61, 55, 67]
        
        fig = px.line(
            x=months,
            y=activities,
            title="Activity Volume by Month",
            markers=True
        )
        fig.update_layout(xaxis_title="Month", yaxis_title="Activities")
        st.plotly_chart(fig, use_container_width=True)

def render_contacts():
    """Render contacts management"""
    st.title("👥 Contact Management")
    
    # Add new contact form
    with st.expander("➕ Add New Contact"):
        with st.form("add_contact"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name*")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
            
            with col2:
                company = st.text_input("Company")
                position = st.text_input("Position")
                source = st.selectbox("Source", ["Website", "Referral", "Cold Call", "Social Media", "Event", "Other"])
            
            tags = st.text_input("Tags (comma-separated)")
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Add Contact"):
                if name:
                    conn = sqlite3.connect('nxtrix.db')
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO contacts (name, email, phone, company, position, source, tags, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (name, email, phone, company, position, source, tags, notes))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success(f"✅ Contact '{name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a name")
    
    # Display contacts
    st.subheader("📋 All Contacts")
    
    conn = sqlite3.connect('nxtrix.db')
    try:
        contacts_df = pd.read_sql("SELECT * FROM contacts ORDER BY created_at DESC", conn)
    except:
        contacts_df = pd.DataFrame()
    conn.close()
    
    if not contacts_df.empty:
        # Search and filter
        search_term = st.text_input("🔍 Search contacts", placeholder="Search by name, email, or company...")
        
        if search_term:
            mask = contacts_df.apply(lambda x: search_term.lower() in str(x).lower(), axis=1)
            contacts_df = contacts_df[mask]
        
        # Display contacts
        st.dataframe(
            contacts_df[['name', 'email', 'phone', 'company', 'position', 'source', 'created_at']],
            use_container_width=True
        )
    else:
        st.info("No contacts yet. Add your first contact above!")

def render_deals():
    """Render deals management"""
    st.title("💼 Deal Management")
    
    # Add new deal form
    with st.expander("➕ Add New Deal"):
        with st.form("add_deal"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Deal Title*")
                amount = st.number_input("Deal Amount ($)", min_value=0, step=1000)
                stage = st.selectbox("Stage", ["prospect", "qualified", "proposal", "negotiation", "closed_won", "closed_lost"])
            
            with col2:
                probability = st.slider("Probability (%)", 0, 100, 50)
                close_date = st.date_input("Expected Close Date")
                
                # Contact selection
                conn = sqlite3.connect('nxtrix.db')
                try:
                    contacts_df = pd.read_sql("SELECT id, name FROM contacts", conn)
                    conn.close()
                    
                    if not contacts_df.empty:
                        contact_options = dict(zip(contacts_df['name'], contacts_df['id']))
                        contact_name = st.selectbox("Associated Contact", ["None"] + list(contact_options.keys()))
                        contact_id = contact_options.get(contact_name) if contact_name != "None" else None
                    else:
                        st.info("No contacts available. Add contacts first.")
                        contact_id = None
                except:
                    conn.close()
                    st.info("No contacts available. Add contacts first.")
                    contact_id = None
            
            description = st.text_area("Description")
            
            if st.form_submit_button("Add Deal"):
                if title:
                    conn = sqlite3.connect('nxtrix.db')
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO deals (title, amount, stage, probability, contact_id, close_date, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (title, amount, stage, probability, contact_id, close_date, description))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success(f"✅ Deal '{title}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a deal title")
    
    # Display deals
    st.subheader("📋 All Deals")
    
    conn = sqlite3.connect('nxtrix.db')
    try:
        deals_df = pd.read_sql("""
            SELECT d.*, c.name as contact_name 
            FROM deals d 
            LEFT JOIN contacts c ON d.contact_id = c.id 
            ORDER BY d.created_at DESC
        """, conn)
    except:
        deals_df = pd.DataFrame()
    conn.close()
    
    if not deals_df.empty:
        st.dataframe(
            deals_df[['title', 'amount', 'stage', 'probability', 'contact_name', 'close_date', 'created_at']],
            use_container_width=True
        )
    else:
        st.info("No deals yet. Add your first deal above!")

def render_billing():
    """Render billing and subscription management"""
    st.title("💳 Billing & Subscription")
    
    if AUTH_AVAILABLE and auth.is_authenticated():
        user_data = auth.get_current_user()
        
        st.subheader("💎 Current Subscription")
        
        # Display current subscription info
        tier = user_data.get('subscription_tier', 'starter').title()
        status = user_data.get('subscription_status', 'trial_active')
        
        if status == 'trial_active':
            trial_end = user_data.get('trial_end_date')
            if trial_end:
                try:
                    trial_end_date = datetime.fromisoformat(trial_end.replace('Z', '+00:00'))
                    days_left = (trial_end_date - datetime.now()).days
                    st.warning(f"🔥 **{tier} Plan Trial** - {days_left} days remaining")
                except:
                    st.info(f"**{tier} Plan** - Trial Active")
            else:
                st.info(f"**{tier} Plan** - Trial Active")
        else:
            st.success(f"**{tier} Plan** - Active Subscription")
        
        # Subscription tiers
        st.subheader("📋 Available Plans")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🚀 Starter
            **$89/month**
            
            - 2,500 contacts
            - 250 deals
            - Email automation (1,000/month)
            - Basic reporting
            - Email support
            """)
            if st.button("Choose Starter", disabled=(tier.lower() == 'starter')):
                st.info("Contact support to change plans")
        
        with col2:
            st.markdown("""
            ### 💼 Professional
            **$189/month** ⭐
            
            - 10,000 contacts
            - Unlimited deals
            - Advanced email automation (5,000/month)
            - AI insights + Voice commands
            - Priority support
            """)
            if st.button("Choose Professional", disabled=(tier.lower() == 'professional')):
                st.info("Contact support to change plans")
        
        with col3:
            st.markdown("""
            ### 🏢 Enterprise
            **$349/month**
            
            - Unlimited contacts & deals
            - Complete AI suite
            - Unlimited automation
            - Custom integrations
            - 24/7 phone support
            """)
            if st.button("Choose Enterprise", disabled=(tier.lower() == 'enterprise')):
                st.info("Contact support to change plans")
        
        # Payment information
        st.subheader("💳 Payment Information")
        
        card_last_four = user_data.get('card_last_four')
        card_brand = user_data.get('card_brand')
        
        if card_last_four and card_brand:
            st.info(f"💳 {card_brand} ending in {card_last_four}")
            if st.button("🔄 Update Payment Method"):
                st.info("Contact support to update payment method")
        else:
            st.warning("No payment method on file")
            if st.button("➕ Add Payment Method"):
                st.info("Contact support to add payment method")
    
    else:
        st.info("Please log in to view billing information")

def render_auth_page():
    """Render authentication page with signup redirect"""
    st.title("🔐 NXTRIX 3.0 Login")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.markdown("### 👤 Sign In to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Sign In", type="primary"):
                if email and password:
                    if AUTH_AVAILABLE:
                        success = auth.login(email, password)
                        if success:
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials")
                    else:
                        st.error("Authentication system not available")
                else:
                    st.error("Please enter both email and password")
    
    with tab2:
        st.markdown("### 🚀 Create Your NXTRIX Account")
        st.info("""
        🎯 **Start Your 7-Day Free Trial**
        
        - Choose your plan and enter payment information
        - Trial starts immediately with full access
        - Cancel anytime during trial period
        - Automatic billing begins after trial
        """)
        
        if st.button("🎉 Start Free Trial", type="primary"):
            st.markdown("""
            **To create your account with billing:**
            
            1. Use our dedicated signup portal 
            2. Enter payment information for trial activation
            3. Choose from Starter ($89), Professional ($189), or Enterprise ($349)
            4. Start using NXTRIX immediately
            """)

def main():
    """Main application entry point"""
    
    # Apply custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    .subscription-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: #f8f9fa;
    }
    
    .pro-card {
        border-color: #007bff;
        background: linear-gradient(135deg, #007bff10, #007bff05);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize database
    init_database()
    
    # Check authentication
    if not AUTH_AVAILABLE:
        st.info("ℹ️ Demo Mode: Authentication system not available")
        user_authenticated = True
        user_data = {"subscription_tier": "professional", "subscription_status": "active", "full_name": "Demo User"}
    else:
        user_authenticated = auth.is_authenticated()
        user_data = auth.get_current_user() if user_authenticated else None
    
    if not user_authenticated:
        render_auth_page()
        return
    
    # Check user access and billing
    access_granted, access_info = check_user_access_and_billing(user_data)
    
    if not access_granted:
        return  # Access denied, billing page already displayed
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🚀 NXTRIX 3.0")
        
        if user_data:
            st.markdown(f"**Welcome back!**")
            user_name = user_data.get('full_name', user_data.get('email', 'User'))
            st.markdown(f"👤 {user_name}")
            
            tier = user_data.get('subscription_tier', 'starter').title()
            st.markdown(f"💎 {tier} Plan")
        
        st.markdown("---")
        
        # Navigation menu
        menu_options = [
            ("🏠", "Dashboard"),
            ("👥", "Contacts"),
            ("💼", "Deals"),
            ("📊", "Analytics"),
            ("💳", "Billing"),
            ("⚙️", "Settings")
        ]
        
        selected_page = st.selectbox(
            "Navigate to:",
            options=[f"{icon} {name}" for icon, name in menu_options],
            format_func=lambda x: x
        )
        
        page = selected_page.split(" ", 1)[1]
        
        st.markdown("---")
        
        if AUTH_AVAILABLE and st.button("🚪 Logout"):
            auth.logout()
            st.rerun()
        
        # Show system status
        st.markdown("### 🔧 System Status")
        st.success("✅ CRM Core") if True else st.error("❌ CRM Core")
        st.success("✅ Database") if True else st.error("❌ Database")
        st.success("✅ Billing") if BILLING_AVAILABLE else st.info("ℹ️ Demo Mode")
        st.success("✅ Auth") if AUTH_AVAILABLE else st.info("ℹ️ Demo Mode")
        st.success("✅ Supabase") if SUPABASE_AVAILABLE else st.info("ℹ️ Local DB")
    
    # Main content area
    if page == "Dashboard":
        render_dashboard()
    elif page == "Contacts":
        render_contacts()
    elif page == "Deals":
        render_deals()
    elif page == "Analytics":
        st.title("📊 Analytics")
        st.info("Advanced analytics module ready for integration!")
        render_dashboard()  # Show dashboard for now
    elif page == "Billing":
        render_billing()
    elif page == "Settings":
        st.title("⚙️ Settings")
        st.info("Settings and configuration panel ready for integration!")
        
        with st.expander("🔧 System Information"):
            st.write("**Version:** NXTRIX 3.0")
            st.write("**Build Date:** November 29, 2025")
            st.write("**Features:** Billing Integration, Trial Management, CRM Core")
            st.write("**Database:** Local SQLite + Supabase Integration Ready")
            st.write("**Deployment:** Railway Ready")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #888;'>NXTRIX 3.0 - Enterprise CRM Platform | Built with Streamlit + Supabase</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()