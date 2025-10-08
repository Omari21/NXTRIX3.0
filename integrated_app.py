"""
NXTRIX CRM v3.0 - Integrated Application
Main application with Enhanced CRM integrated as a module
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import openai
import os
from supabase import create_client, Client
import uuid
from dataclasses import dataclass, asdict
import time
import traceback
import sys
from contextlib import contextmanager
from dotenv import load_dotenv
import bcrypt
import hashlib
import html
import secrets
import string
import re
from collections import defaultdict, deque

# Load environment variables
load_dotenv()

# Import Enhanced CRM as a module
try:
    from enhanced_crm import show_enhanced_crm, CRMManager
    ENHANCED_CRM_AVAILABLE = True
except ImportError:
    st.warning("Enhanced CRM module not available.")
    ENHANCED_CRM_AVAILABLE = False

# Import other modules with error handling
try:
    from database import db_service
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Initialize database connection
def init_database_connection():
    """Initialize database connection"""
    try:
        if DATABASE_AVAILABLE:
            # Initialize database service
            return True
        else:
            st.session_state['backend_connected'] = False
            return False
    except Exception as e:
        st.session_state['backend_connected'] = False
        return False

# Authentication placeholder functions
def show_authentication_ui():
    """Show authentication interface"""
    st.info("🔐 Authentication system - Full version coming soon!")
    
    # Simple demo mode toggle
    if st.button("🚀 Enter Demo Mode"):
        st.session_state['authenticated'] = True
        st.session_state['user_name'] = "Demo User"
        st.session_state['user_tier'] = 'professional'
        st.rerun()

# Page functions
def show_dashboard():
    """Show main dashboard"""
    st.header("🏠 NXTRIX Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Deals", "24", "+3")
    with col2:
        st.metric("Portfolio Value", "$2.4M", "+12%")
    with col3:
        st.metric("ROI Average", "18.5%", "+2.1%")
    with col4:
        st.metric("Closed Deals", "156", "+8")
    
    # Charts
    st.subheader("📈 Performance Overview")
    
    # Sample chart data
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['Deals', 'Revenue', 'ROI']
    )
    
    st.line_chart(chart_data)
    
    # Recent activity
    st.subheader("🕒 Recent Activity")
    
    activities = [
        "New deal added: 123 Main St",
        "Client meeting scheduled for tomorrow",
        "Portfolio analysis completed",
        "ROI report generated"
    ]
    
    for activity in activities:
        st.write(f"• {activity}")

def show_deal_analysis():
    """Show deal analysis tool"""
    st.header("🏠 Deal Analysis Tool")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Property Information")
        
        property_address = st.text_input("Property Address")
        purchase_price = st.number_input("Purchase Price ($)", min_value=0, value=200000)
        arv = st.number_input("After Repair Value (ARV) ($)", min_value=0, value=250000)
        repair_costs = st.number_input("Estimated Repair Costs ($)", min_value=0, value=25000)
        
        # Calculate basic metrics
        if purchase_price > 0:
            equity = arv - purchase_price - repair_costs
            roi = (equity / (purchase_price + repair_costs)) * 100 if (purchase_price + repair_costs) > 0 else 0
            
            st.metric("Potential Equity", f"${equity:,.0f}")
            st.metric("Estimated ROI", f"{roi:.1f}%")
    
    with col2:
        st.subheader("💰 Financial Analysis")
        
        # 70% Rule calculation
        max_offer = arv * 0.7 - repair_costs
        st.metric("Max Offer (70% Rule)", f"${max_offer:,.0f}")
        
        if purchase_price > 0 and max_offer > purchase_price:
            st.success("✅ Deal meets 70% rule!")
        elif purchase_price > 0:
            st.warning("⚠️ Deal exceeds 70% rule")
        
        # Additional metrics
        if purchase_price > 0:
            profit_margin = ((arv - purchase_price - repair_costs) / arv) * 100
            st.metric("Profit Margin", f"{profit_margin:.1f}%")

def show_financial_modeling():
    """Show advanced financial modeling"""
    st.header("💹 Advanced Financial Modeling")
    
    tab1, tab2, tab3 = st.tabs(["Cash Flow", "BRRRR Analysis", "Wholesale"])
    
    with tab1:
        st.subheader("📈 Cash Flow Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_rent = st.number_input("Monthly Rent", value=2000)
            vacancy_rate = st.slider("Vacancy Rate (%)", 0, 20, 5)
            property_mgmt = st.slider("Property Management (%)", 0, 15, 8)
            
        with col2:
            taxes = st.number_input("Annual Taxes", value=3000)
            insurance = st.number_input("Annual Insurance", value=1200)
            maintenance = st.number_input("Annual Maintenance", value=2400)
        
        # Calculate cash flow
        gross_income = monthly_rent * 12
        vacancy_loss = gross_income * (vacancy_rate / 100)
        mgmt_fee = gross_income * (property_mgmt / 100)
        expenses = taxes + insurance + maintenance
        net_operating_income = gross_income - vacancy_loss - mgmt_fee - expenses
        
        st.metric("Net Operating Income", f"${net_operating_income:,.0f}")
        st.metric("Monthly Cash Flow", f"${net_operating_income/12:,.0f}")
    
    with tab2:
        st.subheader("🔄 BRRRR Strategy Analysis")
        st.info("Buy, Rehab, Rent, Refinance, Repeat analysis coming soon!")
        
    with tab3:
        st.subheader("⚡ Wholesale Analysis")
        st.info("Wholesale deal analysis tools coming soon!")

def show_deal_database():
    """Show deal database"""
    st.header("💼 Deal Database")
    
    # Sample data
    deals_data = {
        'Property': ['123 Main St', '456 Oak Ave', '789 Pine Rd'],
        'Purchase Price': [200000, 150000, 180000],
        'ARV': [250000, 200000, 220000],
        'ROI': [18.5, 22.3, 15.8],
        'Status': ['Under Contract', 'Analyzing', 'Closed']
    }
    
    df = pd.DataFrame(deals_data)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Under Contract", "Analyzing", "Closed"])
    
    with col2:
        min_roi = st.slider("Minimum ROI (%)", 0, 50, 0)
    
    with col3:
        if st.button("📊 Export Data"):
            st.success("Export functionality coming soon!")
    
    # Display filtered data
    if status_filter != "All":
        df = df[df['Status'] == status_filter]
    
    df = df[df['ROI'] >= min_roi]
    
    st.dataframe(df, use_container_width=True)

def show_portfolio_analytics():
    """Show portfolio analytics"""
    st.header("📊 Portfolio Analytics")
    
    # Portfolio overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Properties", "12", "+2")
    with col2:
        st.metric("Portfolio Value", "$2.4M", "+8%")
    with col3:
        st.metric("Average ROI", "19.2%", "+1.5%")
    
    # Charts
    st.subheader("📈 Performance Trends")
    
    # Sample chart
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    revenue = [45000, 52000, 48000, 58000, 61000, 67000]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=revenue, mode='lines+markers', name='Revenue'))
    fig.update_layout(title="Monthly Revenue Trend", yaxis_title="Revenue ($)")
    
    st.plotly_chart(fig, use_container_width=True)

def show_communication_center():
    """Show communication center"""
    st.header("💬 Communication Center")
    
    tab1, tab2, tab3 = st.tabs(["Email", "SMS", "Notifications"])
    
    with tab1:
        st.subheader("📧 Email Marketing")
        st.info("Email automation tools coming soon!")
        
    with tab2:
        st.subheader("📱 SMS Marketing")
        st.info("SMS automation tools coming soon!")
        
    with tab3:
        st.subheader("🔔 Notifications")
        st.info("Notification center coming soon!")

def show_task_management():
    """Show task management"""
    st.header("📋 Task Management")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tasks", "23", "+5")
    with col2:
        st.metric("Completed", "18", "+3")
    with col3:
        st.metric("Pending", "5", "+2")
    with col4:
        st.metric("Overdue", "0", "0")
    
    # Task list
    st.subheader("📝 Recent Tasks")
    
    tasks = [
        {"Task": "Follow up with investor", "Priority": "High", "Due": "Today"},
        {"Task": "Property inspection", "Priority": "Medium", "Due": "Tomorrow"},
        {"Task": "Contract review", "Priority": "High", "Due": "This week"},
        {"Task": "Market analysis", "Priority": "Low", "Due": "Next week"}
    ]
    
    for task in tasks:
        with st.expander(f"{task['Task']} - {task['Priority']} Priority"):
            st.write(f"**Due:** {task['Due']}")
            col1, col2 = st.columns(2)
            with col1:
                st.button("✅ Complete", key=f"complete_{task['Task']}")
            with col2:
                st.button("✏️ Edit", key=f"edit_{task['Task']}")

def main():
    """Main application entry point"""
    # Configure Streamlit page
    st.set_page_config(
        page_title="NXTRIX CRM v3.0",
        page_icon="🏡",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
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
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize backend
    init_database_connection()
    
    # Check authentication
    if not st.session_state.get('authenticated', False):
        st.markdown("""
        <div class="main-header">
            <h1>🏡 NXTRIX CRM v3.0</h1>
            <p>Complete Real Estate Investment Management Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        show_authentication_ui()
        return
    
    # Main application
    st.sidebar.title("🚀 NXTRIX CRM")
    st.sidebar.success(f"✅ Welcome, {st.session_state.get('user_name', 'User')}!")
    
    # Main navigation
    page = st.sidebar.selectbox("Navigate to:", [
        "🏠 Dashboard",
        "🏠 Deal Analysis", 
        "💹 Financial Modeling",
        "💼 Deal Database",
        "📊 Portfolio Analytics",
        "🤝 Enhanced CRM",  # This is your enhanced CRM
        "💬 Communication Center",
        "📋 Task Management",
        "👤 User Profile"
    ])
    
    # Display current page
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🏠 Deal Analysis":
        show_deal_analysis()
    elif page == "💹 Financial Modeling":
        show_financial_modeling()
    elif page == "💼 Deal Database":
        show_deal_database()
    elif page == "📊 Portfolio Analytics":
        show_portfolio_analytics()
    elif page == "🤝 Enhanced CRM":
        if ENHANCED_CRM_AVAILABLE:
            show_enhanced_crm()
        else:
            st.error("Enhanced CRM module not available")
    elif page == "💬 Communication Center":
        show_communication_center()
    elif page == "📋 Task Management":
        show_task_management()
    elif page == "👤 User Profile":
        st.header("👤 User Profile")
        st.info("User profile management coming soon!")
    
    # Logout button
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()