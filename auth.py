"""
NXTRIX Platform - Production Authentication System
Real Supabase authentication with subscription management
"""

import streamlit as st
import hashlib
import uuid
import time
from typing import Optional, Dict, Any
from supabase import create_client, Client
import os

# Get Supabase client
@st.cache_resource
def get_supabase_client():
    """Get Supabase client with proper error handling"""
    try:
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

def hash_password(password: str) -> tuple:
    """Hash password with salt"""
    salt = str(uuid.uuid4())
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed, salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify password against hash"""
    return hashlib.sha256((password + salt).encode()).hexdigest() == hashed

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user against Supabase database"""
    supabase = get_supabase_client()
    if not supabase:
        return None
    
    try:
        # Get user from database
        response = supabase.table('profiles').select('*').eq('email', email).execute()
        
        if response.data and len(response.data) > 0:
            user = response.data[0]
            
            # Verify password
            if verify_password(password, user.get('password_hash', ''), user.get('password_salt', '')):
                # Check if user account is active and has valid subscription
                if user.get('active', False) and user.get('subscription_status') == 'active':
                    return user
                else:
                    st.error("❌ Account inactive or subscription expired. Please contact support.")
                    return None
            else:
                return None
        else:
            return None
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return None

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
    """Production login/signup form - no visible demo access"""
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
                with st.spinner("Authenticating..."):
                    user = authenticate_user(email, password)
                    if user:
                        st.session_state['authenticated'] = True
                        st.session_state['user_data'] = user
                        st.session_state['user_id'] = user['id']
                        st.success("✅ Welcome back!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")
            else:
                st.error("❌ Please enter email and password")
                
        # Hidden developer access (only visible in development)
        if os.getenv('ENVIRONMENT') == 'development' or st.secrets.get('APP', {}).get('ENVIRONMENT') == 'development':
            with st.expander("� Developer Testing"):
                st.info("**Demo Account**: demo@nxtrix.com / demo2025")
                if st.button("🎯 Quick Demo Access"):
                    user = authenticate_user("demo@nxtrix.com", "demo2025")
                    if user:
                        st.session_state['authenticated'] = True
                        st.session_state['user_data'] = user
                        st.session_state['user_id'] = user['id']
                        st.success("✅ Demo access granted!")
                        time.sleep(1)
                        st.rerun()
    
    with tab2:
        st.markdown("#### Choose Your Subscription Plan")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🎯 SOLO
            **$79/month**
            
            **Perfect for individual investors**
            
            ✅ **Deal Analysis & Scoring**
            - AI-powered property evaluation
            - ROI calculations & projections
            - Market comparables analysis
            - Investment performance tracking
            
            ✅ **Basic CRM Features**
            - Lead management (up to 100)
            - Contact organization
            - Basic pipeline tracking
            - Email integration
            
            ✅ **Financial Modeling**
            - Investment calculators
            - Cash flow projections
            - Basic reporting
            - Scenario planning
            
            ✅ **Core Platform Access**
            - Mobile responsive design
            - Email support
            - Standard updates
            - Document storage (5GB)
            """)
            solo_btn = st.button("Choose SOLO - $79/mo", key="solo", use_container_width=True)
        
        with col2:
            st.markdown("""
            ### 👥 TEAM
            **$119/month**
            
            **For growing real estate teams**
            
            ✅ **Everything in SOLO, plus:**
            
            ✅ **Advanced CRM & Automation**
            - Unlimited lead management
            - Advanced pipeline automation
            - Team collaboration tools
            - Custom fields & workflows
            - Advanced contact management
            
            ✅ **Enhanced Analytics**
            - Advanced deal analytics
            - Market intelligence reports
            - Portfolio performance tracking
            - Custom dashboards
            - Comparative market analysis
            
            ✅ **Team Features**
            - Multi-user access (up to 5 users)
            - Role-based permissions
            - Team activity tracking
            - Shared deal pipeline
            - Team performance metrics
            
            ✅ **Enhanced Support**
            - Priority email support
            - Advanced training materials
            - Document storage (25GB)
            """)
            team_btn = st.button("Choose TEAM - $119/mo", key="team", use_container_width=True)
        
        with col3:
            st.markdown("""
            ### 🏢 BUSINESS
            **$219/month**
            
            **For established real estate businesses**
            
            ✅ **Everything in TEAM, plus:**
            
            ✅ **AI-Powered Features**
            - Automated deal sourcing
            - Predictive market modeling
            - AI email automation
            - Advanced lead scoring
            - Market trend predictions
            
            ✅ **Client Management**
            - Professional investor portal
            - Automated client reporting
            - Investment presentations
            - Client communication tools
            - White-label options
            
            ✅ **Enterprise Features**
            - Custom integrations
            - Advanced security
            - API access
            - Unlimited users
            - Document storage (100GB)
            
            ✅ **Premium Support**
            - Dedicated account manager
            - Phone & video support
            - Custom training sessions
            - 24/7 priority support
            """)
            business_btn = st.button("Choose BUSINESS - $219/mo", key="business", use_container_width=True)
        
        # Handle plan selection
        if solo_btn or team_btn or business_btn:
            plan = "solo" if solo_btn else ("team" if team_btn else "business")
            price = 79 if solo_btn else (119 if team_btn else 219)
            show_signup_form(plan, price)

def show_signup_form(plan: str, price: int):
    """Show signup form for selected plan with real Supabase integration"""
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
        st.info("🔒 Stripe payment processing will be activated with your live keys")
        
        agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        submit_btn = st.form_submit_button(f"🚀 Subscribe to {plan.title()}", type="primary")
    
    if submit_btn and all([first_name, last_name, email, password]) and agree:
        with st.spinner("Creating your account..."):
            # Here you would integrate with your Stripe payment processing
            # For now, create account with subscription
            supabase = get_supabase_client()
            if supabase:
                try:
                    # Hash password
                    password_hash, password_salt = hash_password(password)
                    user_id = str(uuid.uuid4())
                    
                    # Create user account
                    user_data = {
                        'id': user_id,
                        'email': email,
                        'password_hash': password_hash,
                        'password_salt': password_salt,
                        'first_name': first_name,
                        'last_name': last_name,
                        'subscription_tier': plan,
                        'subscription_status': 'active',
                        'subscription_price': price,
                        'active': True
                    }
                    
                    response = supabase.table('profiles').insert(user_data).execute()
                    
                    if response.data:
                        st.success(f"🎉 Welcome to NXTRIX {plan.title()}!")
                        st.info("✅ Your account has been created successfully!")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ Account creation failed. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error creating account: {e}")
            else:
                st.error("❌ Database connection failed")
    elif submit_btn:
        if not agree:
            st.error("❌ Please accept the terms")
        else:
            st.error("❌ Please fill all required fields")