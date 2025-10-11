"""
NXTRIX Platform - Unified Investment Management System
Production-ready real estate investment platform with subscription system
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

try:
    from auth import supabase_login_form, get_current_user, logout_user
    SUPABASE_AUTH_AVAILABLE = True
except ImportError:
    SUPABASE_AUTH_AVAILABLE = False

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
    """Main platform interface"""
    st.title("🏢 NXTRIX Platform")
    st.markdown("### Professional Real Estate Investment Management")
    
    # User welcome
    user = get_current_user()
    if user:
        st.success(f"Welcome back, {user.get('first_name', 'User')}!")
        
        # Main navigation
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏠 Enhanced CRM", 
            "📊 Analytics", 
            "💰 Portfolio", 
            "⚙️ Settings"
        ])
        
        with tab1:
            if ENHANCED_CRM_AVAILABLE:
                show_enhanced_crm()
            else:
                st.info("Enhanced CRM module loading...")
                
        with tab2:
            st.markdown("### 📊 Investment Analytics")
            st.info("Advanced analytics dashboard coming soon...")
            
        with tab3:
            st.markdown("### 💰 Portfolio Management")
            st.info("Portfolio analytics dashboard coming soon...")
            
        with tab4:
            st.markdown("### ⚙️ Account Settings")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Plan**: {user.get('subscription_tier', 'Unknown').title()}")
                st.info(f"**Email**: {user.get('email', 'Unknown')}")
            with col2:
                if st.button("🚪 Logout"):
                    logout_user()
                    st.rerun()

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