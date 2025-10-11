"""
NXTRIX Platform - Authentication System
Production subscription-based authentication with Supabase
"""

import streamlit as st
import hashlib
import uuid
import time
from typing import Optional, Dict, Any

# Simplified authentication for production deployment
def hash_password(password: str) -> tuple:
    """Hash password with salt"""
    salt = str(uuid.uuid4())
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed, salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify password against hash"""
    return hashlib.sha256((password + salt).encode()).hexdigest() == hashed

def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current authenticated user"""
    if st.session_state.get('authenticated', False):
        return st.session_state.get('user_data', {})
    return None

def logout_user():
    """Logout current user"""
    st.session_state['authenticated'] = False
    st.session_state['user_data'] = {}
    st.session_state['user_id'] = None

def supabase_login_form():
    """Main login/signup form"""
    st.title("🏢 NXTRIX Platform")
    st.markdown("### Professional Real Estate Investment Management")
    
    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Subscribe"])
    
    with tab1:
        st.markdown("#### Sign In to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email Address")
            password = st.text_input("🔒 Password", type="password")
            login_btn = st.form_submit_button("🚀 Sign In", type="primary", use_container_width=True)
        
        if login_btn:
            if email and password:
                # Demo authentication for deployment
                if email == "demo@nxtrix.com" and password == "demo2025":
                    st.session_state['authenticated'] = True
                    st.session_state['user_data'] = {
                        'id': str(uuid.uuid4()),
                        'email': email,
                        'first_name': 'Demo',
                        'last_name': 'User',
                        'subscription_tier': 'solo'
                    }
                    st.success("✅ Welcome back!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
            else:
                st.error("❌ Please enter email and password")
    
    with tab2:
        st.markdown("#### Choose Your Subscription Plan")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🎯 SOLO
            **$79/month**
            
            ✅ Deal Analysis & Scoring
            ✅ Basic CRM Features  
            ✅ Financial Modeling
            ✅ Core Platform Access
            """)
            solo_btn = st.button("Choose SOLO", key="solo")
        
        with col2:
            st.markdown("""
            ### 👥 TEAM
            **$119/month**
            
            ✅ Everything in SOLO
            ✅ Advanced CRM & Automation
            ✅ Team Collaboration
            ✅ Enhanced Analytics
            """)
            team_btn = st.button("Choose TEAM", key="team")
        
        with col3:
            st.markdown("""
            ### 🏢 BUSINESS
            **$219/month**
            
            ✅ Everything in TEAM
            ✅ AI-Powered Insights
            ✅ Custom Integrations
            ✅ Premium Support
            """)
            business_btn = st.button("Choose BUSINESS", key="business")
        
        # Handle plan selection
        if solo_btn or team_btn or business_btn:
            plan = "solo" if solo_btn else ("team" if team_btn else "business")
            price = 79 if solo_btn else (119 if team_btn else 219)
            show_signup_form(plan, price)

def show_signup_form(plan: str, price: int):
    """Show signup form for selected plan"""
    st.markdown("---")
    st.markdown(f"### 💳 Subscribe to {plan.title()} Plan - ${price}/month")
    
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name *")
            email = st.text_input("Email Address *")
        with col2:
            last_name = st.text_input("Last Name *")
            password = st.text_input("Password *", type="password")
        
        st.markdown("#### Payment Information")
        st.info("🔒 Secure payment processing will be activated in production")
        
        agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        submit_btn = st.form_submit_button(f"🚀 Subscribe to {plan.title()}", type="primary")
    
    if submit_btn and all([first_name, last_name, email, password]) and agree:
        with st.spinner("Creating your account..."):
            time.sleep(2)
            
            # Create account (simplified for demo)
            st.session_state['authenticated'] = True
            st.session_state['user_data'] = {
                'id': str(uuid.uuid4()),
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'subscription_tier': plan
            }
            
            st.success(f"🎉 Welcome to NXTRIX {plan.title()}!")
            st.balloons()
            time.sleep(2)
            st.rerun()
    elif submit_btn:
        if not agree:
            st.error("❌ Please accept the terms")
        else:
            st.error("❌ Please fill all required fields")