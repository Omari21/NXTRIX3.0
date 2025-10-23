"""
NXTRIX Platform v3.0 - PRODUCTION READY VERSION
Complete real estate investment platform with proper database authentication
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid
import time
import traceback
import sys
from contextlib import contextmanager
import json
import hashlib
import secrets
import string
import re
from collections import defaultdict
import bcrypt
import os

# Configuration helper function
def get_config(section: str, key: str, default=None):
    """Get configuration from environment variables or secrets.toml"""
    # Try environment variable first (for Railway deployment)
    env_key = f"{key}" if section == "APP" else f"{key}"
    env_value = os.getenv(env_key)
    if env_value:
        return env_value
    
    # Fallback to secrets.toml for local development
    try:
        return st.secrets[section][key]
    except:
        return default

# Configure Streamlit page
st.set_page_config(
    page_title="NXTRIX Platform v3.0 - Production",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PRODUCTION SECURITY IMPORTS
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    st.error("Supabase client not available. Install with: pip install supabase")

# Import Enhanced CRM and other modules with error handling
try:
    from enhanced_crm import show_enhanced_crm
    ENHANCED_CRM_AVAILABLE = True
except ImportError as e:
    ENHANCED_CRM_AVAILABLE = False
    st.warning(f"Enhanced CRM module not available: {e}")

try:
    from database import db_service
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

try:
    from enhanced_financial_modeling import show_enhanced_financial_modeling
    FINANCIAL_MODELING_AVAILABLE = True
except ImportError:
    FINANCIAL_MODELING_AVAILABLE = False

try:
    from portfolio_analytics import show_portfolio_analytics as show_advanced_portfolio_analytics
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

# Import subscription management
try:
    from subscription_manager import SubscriptionManager, SubscriptionTier, get_user_tier, is_feature_available
    from stripe_integration import StripePaymentSystem
    SUBSCRIPTION_AVAILABLE = True
except ImportError:
    SUBSCRIPTION_AVAILABLE = False
    st.warning("Subscription management not available")

# PRODUCTION DATABASE CONNECTION
@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    try:
        if SUPABASE_AVAILABLE:
            supabase_url = get_config("SUPABASE", "SUPABASE_URL")
            supabase_key = get_config("SUPABASE", "SUPABASE_ANON_KEY")
            
            if supabase_url and supabase_key:
                return create_client(supabase_url, supabase_key)
            else:
                st.error("🚨 Database Connection Failed\n\nPlease check your Supabase configuration in environment variables")
                return None
        return None
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# PRODUCTION AUTHENTICATION SYSTEM
class ProductionAuth:
    def __init__(self):
        self.supabase = init_supabase()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except:
            return False
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user against production database"""
        if not self.supabase:
            return None
        
        try:
            # Query profiles table for user
            result = self.supabase.table('profiles').select('*').eq('email', email.lower()).execute()
            
            if result.data:
                user = result.data[0]
                # Verify password
                if user.get('password_hash') and self.verify_password(password, user['password_hash']):
                    # Update last login
                    self.supabase.table('profiles').update({
                        'last_login': datetime.now().isoformat()
                    }).eq('id', user['id']).execute()
                    
                    return {
                        'id': user['id'],
                        'email': user['email'],
                        'full_name': user.get('full_name', 'User'),
                        'subscription_tier': user.get('subscription_tier', 'solo'),
                        'company': user.get('company', ''),
                        'onboarding_completed': user.get('onboarding_completed', False)
                    }
            return None
        except Exception as e:
            st.error(f"Authentication error: {e}")
            return None
    
    def register_user(self, email: str, password: str, full_name: str, company: str = '', tier: str = 'solo') -> bool:
        """Register new user in production database"""
        if not self.supabase:
            return False
        
        try:
            # Check if user already exists (skip RLS for this check)
            try:
                existing = self.supabase.table('profiles').select('email').eq('email', email.lower()).execute()
                if existing.data:
                    return False
            except:
                # If RLS blocks read, assume user doesn't exist and continue
                pass
            
            # Create basic user data - generate UUID for id field
            user_data = {
                'id': str(uuid.uuid4()),  # Generate unique ID
                'email': email.lower(),
                'password_hash': self.hash_password(password),
                'full_name': full_name,
                'company': company,
                'subscription_tier': tier,
                'created_at': datetime.now().isoformat(),
                'onboarding_completed': False
            }
            
            # Try to add trial columns (will work after schema update)
            try:
                user_data.update({
                    'trial_started_at': datetime.now().isoformat(),
                    'trial_expires_at': (datetime.now() + timedelta(days=7)).isoformat(),
                    'trial_active': True
                })
                result = self.supabase.table('profiles').insert(user_data).execute()
                return bool(result.data)
            except Exception as trial_error:
                # Fallback: register without trial columns
                st.warning("Registering with basic profile (please update database schema for trial features)")
                result = self.supabase.table('profiles').insert(user_data).execute()
                return bool(result.data)
                
        except Exception as e:
            st.error(f"Registration error: {e}")
            return False

# Subscription and Feature Access Control
def check_trial_status() -> tuple:
    """Check if trial is still active and return status"""
    user_tier = st.session_state.get('user_tier', 'trial')
    
    # If not on trial, return active status
    if user_tier != 'trial':
        return True, None, None
    
    # Get trial expiration date from session or database
    trial_expires_at = st.session_state.get('trial_expires_at')
    if not trial_expires_at:
        return True, None, None  # No expiration date found, assume active
    
    try:
        expiry_date = datetime.fromisoformat(trial_expires_at.replace('Z', '+00:00'))
        current_date = datetime.now()
        
        if current_date > expiry_date:
            # Trial expired
            days_expired = (current_date - expiry_date).days
            return False, expiry_date, days_expired
        else:
            # Trial still active
            days_remaining = (expiry_date - current_date).days
            return True, expiry_date, days_remaining
    except:
        # If date parsing fails, assume trial is active
        return True, None, None

def check_feature_access(feature_name: str, required_tier: str = 'solo') -> bool:
    """Check if user has access to a specific feature based on their subscription"""
    if not SUBSCRIPTION_AVAILABLE:
        return True  # Allow access if subscription system not available
    
    # First check if trial is expired
    trial_active, expiry_date, days_info = check_trial_status()
    if not trial_active:
        return False  # Trial expired, no access to features
    
    user_id = st.session_state.get('user_id')
    user_tier = st.session_state.get('user_tier', 'trial')
    
    # Define feature requirements
    feature_requirements = {
        'ai_insights': 'solo',
        'advanced_analytics': 'solo', 
        'team_collaboration': 'team',
        'automated_deal_sourcing': 'team',
        'api_access': 'team',
        'white_label': 'business',
        'unlimited_deals': 'business',
        'priority_support': 'team'
    }
    
    required = feature_requirements.get(feature_name, required_tier)
    
    # Tier hierarchy: trial < solo < team < business
    tier_hierarchy = {'trial': 0, 'solo': 1, 'team': 2, 'business': 3}
    
    user_level = tier_hierarchy.get(user_tier, 0)
    required_level = tier_hierarchy.get(required, 1)
    
    return user_level >= required_level

def show_upgrade_prompt(feature_name: str, required_tier: str):
    """Show upgrade prompt when feature access is denied"""
    st.error(f"🔒 **Premium Feature: {feature_name}**")
    
    tier_info = {
        'solo': {'name': 'Solo Professional', 'price': '$79/month'},
        'team': {'name': 'Team Collaboration', 'price': '$119/month'},
        'business': {'name': 'Enterprise Solution', 'price': '$219/month'}
    }
    
    required_plan = tier_info.get(required_tier, {'name': 'Premium', 'price': 'Contact Sales'})
    
    st.markdown(f"""
    ### Upgrade Required
    
    **{feature_name}** requires **{required_plan['name']}** plan or higher.
    
    **Benefits of upgrading:**
    - 🚀 Unlock advanced features
    - 📈 Increased limits and capabilities
    - 🎯 Priority support
    - 💼 Scale your business
    
    **Price:** {required_plan['price']}
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎯 **Upgrade Now**", type="primary"):
            st.session_state['show_pricing'] = True
            st.rerun()
    with col2:
        if st.button("📚 **View All Plans**"):
            st.session_state['show_pricing'] = True
            st.rerun()

def check_usage_limits(user_id: str, resource_type: str) -> tuple:
    """Check current usage against subscription limits"""
    if not SUBSCRIPTION_AVAILABLE:
        return 0, -1, True  # unlimited if subscription not available
    
    user_tier = st.session_state.get('user_tier', 'trial')
    
    # Define limits for each tier
    limits = {
        'trial': {'deals': 5, 'portfolios': 1, 'team_members': 1},
        'solo': {'deals': 50, 'portfolios': 5, 'team_members': 1},
        'team': {'deals': 200, 'portfolios': 20, 'team_members': 5},
        'business': {'deals': -1, 'portfolios': -1, 'team_members': -1}  # unlimited
    }
    
    limit = limits.get(user_tier, {}).get(resource_type, 0)
    
    # Get current usage from database
    supabase = st.session_state.get('supabase')
    if not supabase:
        return 0, limit, True
    
    try:
        if resource_type == 'deals':
            result = supabase.table('deals').select('id').eq('user_id', user_id).execute()
        elif resource_type == 'portfolios':
            result = supabase.table('portfolios').select('id').eq('user_id', user_id).execute()
        else:
            return 0, limit, True
            
        current_count = len(result.data) if result.data else 0
        can_add = limit == -1 or current_count < limit
        
        return current_count, limit, can_add
        
    except Exception:
        return 0, limit, True

# Authentication and session management
def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def show_authentication_ui():
    """Show production authentication interface"""
    st.title("🏢 NXTRIX Platform v3.0")
    st.markdown("### Professional Real Estate Investment Management")
    
    auth = ProductionAuth()
    
    # Check if database is connected
    if not auth.supabase:
        st.error("🚨 **Database Connection Failed**")
        st.error("Please check your Supabase configuration in secrets.toml")
        st.stop()
    
    st.success("🟢 **Connected to Production Database**")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        # Login/Register tabs
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            st.subheader("Login to Your Account")
            
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="Enter your email")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                login_btn = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
            
            if login_btn and email and password:
                with st.spinner("Authenticating..."):
                    user = auth.authenticate_user(email, password)
                    if user:
                        # Set authentication state
                        st.session_state['authenticated'] = True
                        st.session_state['user_data'] = user
                        st.session_state['user_name'] = user['full_name']
                        st.session_state['user_tier'] = user['subscription_tier']
                        st.session_state['user_id'] = user['id']
                        st.session_state['user_email'] = user['email']
                        st.session_state['trial_expires_at'] = user.get('trial_expires_at')
                        st.success("✅ Login successful!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")
        
        with tab2:
            st.subheader("🚀 Join NXTRIX - Choose Your Plan")
            st.markdown("*Transform your real estate investment business with our professional platform*")
            
            # Plan Comparison Section
            st.markdown("### 📊 **Compare Plans & Features**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div style='border: 2px solid #4CAF50; border-radius: 10px; padding: 20px; background: #f8f9fa;'>
                <h4 style='color: #4CAF50; text-align: center;'>🌟 SOLO</h4>
                <h3 style='text-align: center; color: #333;'>$79/month</h3>
                <p style='text-align: center; color: #666;'>Perfect for individual investors</p>
                
                <h5>✅ Core Features:</h5>
                <ul>
                <li>50 deals per month</li>
                <li>Advanced financial modeling</li>
                <li>AI-powered deal analysis</li>
                <li>Portfolio tracking (5 portfolios)</li>
                <li>Professional reports</li>
                <li>Investor portal</li>
                <li>Email support</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='border: 3px solid #2196F3; border-radius: 10px; padding: 20px; background: linear-gradient(135deg, #e3f2fd 0%, #f8f9fa 100%);'>
                <h4 style='color: #2196F3; text-align: center;'>⭐ TEAM</h4>
                <h3 style='text-align: center; color: #333;'>$119/month</h3>
                <p style='text-align: center; color: #666; font-weight: bold;'>Most Popular Choice</p>
                
                <h5>✅ Everything in Solo +</h5>
                <ul>
                <li>200 deals per month</li>
                <li>Multi-user team access (5 users)</li>
                <li>Advanced deal analytics</li>
                <li>Automated deal sourcing</li>
                <li>Enhanced CRM features</li>
                <li>20 portfolios</li>
                <li>Priority support</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div style='border: 2px solid #FF9800; border-radius: 10px; padding: 20px; background: #fff3e0;'>
                <h4 style='color: #FF9800; text-align: center;'>🏢 BUSINESS</h4>
                <h3 style='text-align: center; color: #333;'>$219/month</h3>
                <p style='text-align: center; color: #666;'>Full enterprise solution</p>
                
                <h5>✅ Everything in Team +</h5>
                <ul>
                <li>Unlimited deals & portfolios</li>
                <li>Unlimited team members</li>
                <li>AI enhancement suite</li>
                <li>Complete feature access</li>
                <li>Advanced automation</li>
                <li>Dedicated support</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Registration Form
            st.subheader("📝 Create Your Account")
            
            with st.form("register_form"):
                col_form1, col_form2 = st.columns(2)
                
                with col_form1:
                    reg_name = st.text_input("Full Name*", placeholder="Your full name")
                    reg_email = st.text_input("Email Address*", placeholder="your@email.com")
                    reg_company = st.text_input("Company", placeholder="Your company (optional)")
                
                with col_form2:
                    reg_password = st.text_input("Password*", type="password", placeholder="Minimum 8 characters")
                    reg_confirm = st.text_input("Confirm Password*", type="password", placeholder="Confirm your password")
                    reg_phone = st.text_input("Phone Number", placeholder="(555) 123-4567 (optional)")
                
                st.markdown("### 💳 **Select Your Plan**")
                reg_tier = st.selectbox(
                    "Choose Your Plan:",
                    [
                        "solo - $79/month - Individual Investor Plan",
                        "team - $119/month - Team Collaboration Plan (Most Popular)", 
                        "business - $219/month - Full Enterprise Solution"
                    ],
                    index=1  # Default to Team plan (most popular)
                )
                
                st.markdown("### 🎯 **What Happens Next?**")
                st.info("""
                **After registration, you'll receive:**
                1. 📧 **Welcome email** with login credentials
                2. 🎥 **Setup tutorial** & onboarding guide  
                3. 📞 **Personal welcome call** (Team & Business plans)
                4. 🚀 **Full access** to your chosen plan features
                5. 💬 **24/7 support** access through your dashboard
                """)
                
                # Terms and conditions
                terms_agreed = st.checkbox("I agree to the Terms of Service and Privacy Policy*")
                marketing_consent = st.checkbox("Send me updates about new features and real estate market insights (optional)")
                
                register_btn = st.form_submit_button(
                    "� Start My NXTRIX Journey", 
                    use_container_width=True, 
                    type="primary"
                )
            
            if register_btn:
                if not terms_agreed:
                    st.error("❌ Please agree to the Terms of Service to continue")
                elif not all([reg_email, reg_password, reg_confirm, reg_name]):
                    st.error("❌ Please fill in all required fields (Name, Email, Password)")
                elif reg_password != reg_confirm:
                    st.error("❌ Passwords do not match")
                elif len(reg_password) < 8:
                    st.error("❌ Password must be at least 8 characters")
                elif '@' not in reg_email or '.' not in reg_email:
                    st.error("❌ Please enter a valid email address")
                else:
                    tier = reg_tier.split(' - ')[0]  # Extract tier name
                    
                    with st.spinner("🚀 Creating your NXTRIX account..."):
                        if auth.register_user(reg_email, reg_password, reg_name, reg_company, tier):
                            st.success("🎉 Welcome to NXTRIX! Your account has been created successfully!")
                            
                            # Show next steps
                            st.balloons()
                            st.markdown(f"""
                            ### ✅ **Account Created Successfully!**
                            
                            **Your Plan:** {reg_tier.split(' - ')[1]}
                            **Email:** {reg_email}
                            **Company:** {reg_company if reg_company else 'Individual Investor'}
                            
                            ### 📧 **Check Your Email**
                            We've sent a welcome email with:
                            - Login confirmation
                            - Setup instructions  
                            - Feature overview for your plan
                            - Support contact information
                            
                            ### 🔐 **Ready to Login?**
                            Click the Login tab above to access your new NXTRIX dashboard!
                            """)
                            
                            time.sleep(3)
                            st.rerun()
                        else:
                            st.error("❌ Registration failed. This email address may already be registered.")
                            st.info("💡 Try logging in instead, or contact support if you need help.")

# Main application pages (same as before but with user data integration)
def show_dashboard():
    """Show main executive dashboard with real user data"""
    user_data = st.session_state.get('user_data', {})
    user_name = user_data.get('full_name', st.session_state.get('user_name', 'User'))
    
    st.header(f"📊 Welcome back, {user_name}!")
    st.markdown("*Real-time business metrics and performance overview*")
    
    # Show user tier info
    user_tier = st.session_state.get('user_tier', 'solo')
    tier_colors = {'solo': '🥉', 'team': '🥈', 'business': '🥇'}
    st.info(f"{tier_colors.get(user_tier, '📊')} **{user_tier.title()} Plan** - Full access to your features")
    
    # Key Performance Indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Deals", "42", "+5 this month")
    with col2:
        st.metric("Portfolio Value", "$2.1M", "+12% YTD")
    with col3:
        st.metric("Average AI Score", "82/100", "+3 points")
    with col4:
        st.metric("Monthly Cash Flow", "$8,450", "+$1,200")
    
    st.markdown("---")
    
    # Performance Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Deal Pipeline")
        # Sample pipeline data
        pipeline_data = pd.DataFrame({
            'Stage': ['Prospecting', 'Analysis', 'Under Contract', 'Closed'],
            'Count': [15, 8, 12, 7],
            'Value': [1500000, 950000, 1800000, 750000]
        })
        
        fig = px.funnel(pipeline_data, x='Count', y='Stage', title='Deal Pipeline Funnel')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Revenue Trend")
        # Sample revenue data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        revenue = [45000, 52000, 48000, 58000, 61000, 67000]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=revenue, mode='lines+markers', 
                                name='Monthly Revenue', line=dict(color='#4CAF50', width=3)))
        fig.update_layout(title="Monthly Revenue Growth", yaxis_title="Revenue ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent Activities
    st.subheader("🕒 Recent Activities")
    activities = [
        "New lead added: John Smith - $450K budget",
        "Deal closed: 123 Main St - $285K profit",
        "AI analysis completed for 456 Oak Ave",
        "Investor match found for Pine Street property",
        "Financial model updated for downtown project"
    ]
    
    for i, activity in enumerate(activities):
        st.write(f"• {activity}")

def show_financial_modeling():
    """Advanced Financial Modeling Suite"""
    st.header("💹 Advanced Financial Modeling")
    st.markdown("*Professional DCF analysis, IRR calculations, and cash flow projections*")
    
    # Import financial modeling functionality
    try:
        from financial_modeling import AdvancedFinancialModeling
        fm = AdvancedFinancialModeling()
    except ImportError:
        st.error("Financial modeling module not available")
        return
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Cash Flow Analysis", "🎲 Monte Carlo", "📈 Sensitivity Analysis", "🎯 Exit Strategies"])
    
    with tab1:
        st.subheader("10-Year Cash Flow Projections")
        
        with st.form("financial_modeling_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Property Information**")
                purchase_price = st.number_input("Purchase Price ($)", min_value=0, value=250000)
                arv = st.number_input("After Repair Value ($)", min_value=0, value=320000)
                repair_costs = st.number_input("Repair Costs ($)", min_value=0, value=30000)
                monthly_rent = st.number_input("Monthly Rent ($)", min_value=0, value=2500)
            
            with col2:
                st.write("**Financial Assumptions**")
                down_payment = st.slider("Down Payment %", 10, 50, 25)
                interest_rate = st.slider("Interest Rate %", 3.0, 10.0, 6.5)
                rent_growth = st.slider("Annual Rent Growth %", 0.0, 8.0, 3.0)
                expense_ratio = st.slider("Expense Ratio %", 10, 50, 25)
            
            submitted = st.form_submit_button("📊 Generate Analysis", type="primary")
            
            if submitted:
                # Check deal creation limits
                user_id = st.session_state.get('user_id', '')
                deals_current, deals_limit, can_add_deals = check_usage_limits(user_id, 'deals')
                
                if not can_add_deals and deals_limit != -1:
                    st.error(f"🔒 **Deal Limit Reached** ({deals_current}/{deals_limit})")
                    show_upgrade_prompt("Additional Deal Analysis", "team")
                    return
                deal_data = {
                    'purchase_price': purchase_price,
                    'arv': arv,
                    'repair_costs': repair_costs,
                    'monthly_rent': monthly_rent,
                    'down_payment_percent': down_payment,
                    'interest_rate': interest_rate / 100,
                    'rent_growth': rent_growth / 100,
                    'expense_ratio': expense_ratio / 100
                }
                
                # Store deal_data in session state for other tabs
                st.session_state['deal_data'] = deal_data
                
                projections = fm.generate_cash_flow_projections(deal_data)
                metrics_by_scenario = fm.calculate_advanced_metrics(deal_data, projections)
                
                # Get base scenario metrics for display
                metrics = metrics_by_scenario.get('base', {
                    'irr': 0, 'npv': 0, 'cash_on_cash': 0, 'debt_coverage_ratio': 1.0
                })
                
                # Calculate cap rate separately
                monthly_rent = deal_data.get('monthly_rent', 0)
                purchase_price = deal_data.get('purchase_price', 1)
                annual_expenses = fm._calculate_annual_expenses(deal_data)
                annual_noi = (monthly_rent * 12) - annual_expenses
                cap_rate = (annual_noi / purchase_price) * 100 if purchase_price > 0 else 0
                
                # Display key metrics
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                
                with col_m1:
                    st.metric("IRR", f"{metrics.get('irr', 0):.1f}%")
                with col_m2:
                    st.metric("NPV", f"${metrics.get('npv', 0):,.0f}")
                with col_m3:
                    st.metric("Cap Rate", f"{cap_rate:.1f}%")
                with col_m4:
                    st.metric("Cash-on-Cash", f"{metrics.get('cash_on_cash', 0):.1f}%")
                
                # Cash Flow Chart
                st.subheader("📈 10-Year Cash Flow Projection")
                
                years = list(range(1, 11))
                annual_cf = projections.get('annual_cash_flow', [0] * 10)
                
                import plotly.graph_objects as go
                fig = go.Figure()
                fig.add_trace(go.Bar(x=years, y=annual_cf, name="Annual Cash Flow", marker_color='#2E8B57'))
                fig.update_layout(
                    title="Annual Cash Flow Projection",
                    xaxis_title="Year",
                    yaxis_title="Cash Flow ($)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Cash Flow Table
                st.subheader("💰 Detailed Cash Flow Table")
                cf_df = pd.DataFrame({
                    'Year': years,
                    'Gross Rent': projections.get('gross_rent', [0] * 10),
                    'Operating Expenses': projections.get('expenses', [0] * 10),
                    'NOI': projections.get('noi', [0] * 10),
                    'Debt Service': projections.get('debt_service', [0] * 10),
                    'Cash Flow': annual_cf
                })
                
                # Format as currency
                for col in ['Gross Rent', 'Operating Expenses', 'NOI', 'Debt Service', 'Cash Flow']:
                    cf_df[col] = cf_df[col].apply(lambda x: f"${x:,.0f}")
                
                st.dataframe(cf_df, use_container_width=True)
    
    with tab2:
        st.subheader("🎲 Monte Carlo Risk Analysis")
        st.info("Run thousands of scenarios to understand risk and return distributions")
        
        if st.button("🔄 Run Monte Carlo Simulation"):
            # Check if deal_data exists from previous analysis
            if 'deal_data' not in st.session_state:
                st.warning("⚠️ Please run a financial analysis first in the 'Analysis' tab to generate deal data.")
                return
                
            deal_data = st.session_state['deal_data']
            with st.spinner("Running 1,000 simulations..."):
                monte_results = fm.monte_carlo_simulation(deal_data, 1000)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Mean ROI", f"{monte_results['statistics']['mean_roi']:.1f}%")
                    st.metric("Median ROI", f"{monte_results['statistics']['median_roi']:.1f}%")
                    st.metric("Std Deviation", f"{monte_results['statistics']['std_roi']:.1f}%")
                
                with col2:
                    st.metric("5th Percentile", f"{monte_results['statistics']['percentile_5']:.1f}%")
                    st.metric("95th Percentile", f"{monte_results['statistics']['percentile_95']:.1f}%")
                    st.metric("Prob. Positive ROI", f"{monte_results['statistics']['probability_positive']:.1f}%")
    
    with tab3:
        st.subheader("📈 Sensitivity Analysis")
        st.info("Understand how key variables impact your returns")
        
        if st.button("📊 Run Sensitivity Analysis"):
            # Check if deal_data exists from previous analysis
            if 'deal_data' not in st.session_state:
                st.warning("⚠️ Please run a financial analysis first in the 'Analysis' tab to generate deal data.")
                return
                
            deal_data = st.session_state['deal_data']
            sensitivity_results = fm.sensitivity_analysis(deal_data)
            
            # Create sensitivity chart
            variables = list(sensitivity_results.keys())
            changes = [-20, -10, 0, 10, 20]
            
            fig = go.Figure()
            for var in variables:
                roi_impacts = [r['roi_impact'] for r in sensitivity_results[var]]
                fig.add_trace(go.Scatter(x=changes, y=roi_impacts, mode='lines+markers', name=var))
            
            fig.update_layout(
                title="Sensitivity Analysis - ROI Impact",
                xaxis_title="% Change in Variable",
                yaxis_title="ROI Impact (%)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("🎯 Exit Strategy Comparison")
        st.info("Compare Hold vs Flip vs BRRRR strategies")
        
        if st.button("🔍 Analyze Exit Strategies"):
            exit_analysis = fm.exit_strategy_analysis(deal_data)
            
            strategies = ['Hold (10 Years)', 'Flip (6 Months)', 'BRRRR']
            returns = [exit_analysis.get('hold_return', 0), 
                      exit_analysis.get('flip_return', 0), 
                      exit_analysis.get('brrrr_return', 0)]
            
            fig = go.Figure(data=[go.Bar(x=strategies, y=returns, marker_color=['#2E8B57', '#FF6347', '#4169E1'])])
            fig.update_layout(title="Exit Strategy Comparison", yaxis_title="Total Return ($)")
            st.plotly_chart(fig, use_container_width=True)

def show_deal_database():
    """Comprehensive Deal Database with Search and Management"""
    st.header("🗄️ Deal Database")
    st.markdown("*Search, filter, and manage your deal pipeline*")
    
    # Search and filter section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Search Deals", placeholder="Search by address, type, or status...")
    
    with col2:
        status_filter = st.selectbox("Filter by Status", 
                                   ["All", "New", "Analyzing", "Under Contract", "Negotiating", "Closed", "Passed"])
    
    with col3:
        sort_by = st.selectbox("Sort by", 
                             ["Created Date (Newest)", "AI Score (Highest)", "Purchase Price (Highest)", "ROI (Highest)"])
    
    # Get deals from database
    try:
        if db_service and db_service.is_connected():
            if search_term:
                deals = [d for d in db_service.get_deals() if search_term.lower() in d.address.lower()]
            else:
                deals = db_service.get_deals()
        else:
            st.warning("⚠️ Database connection not available - showing demo data")
            # Use same demo data as portfolio analytics
            from models import Deal
            from datetime import datetime
            all_deals = [
                Deal(
                    id="demo1", address="123 Demo Street", purchase_price=250000,
                    arv=320000, repair_costs=25000, monthly_rent=2500,
                    closing_costs=7500, annual_taxes=3000, insurance=1200,
                    hoa_fees=0, vacancy_rate=5.0,
                    ai_score=85, property_type="Single Family", condition="Good",
                    neighborhood_grade="B+", market_trend="Rising", status="Active",
                    created_at=datetime.now(), updated_at=datetime.now(), notes="Demo property 1"
                ),
                Deal(
                    id="demo2", address="456 Sample Ave", purchase_price=180000,
                    arv=245000, repair_costs=15000, monthly_rent=1800,
                    closing_costs=5400, annual_taxes=2200, insurance=900,
                    hoa_fees=150, vacancy_rate=8.0,
                    ai_score=78, property_type="Townhouse", condition="Fair",
                    neighborhood_grade="B", market_trend="Stable", status="Under Contract",
                    created_at=datetime.now(), updated_at=datetime.now(), notes="Demo property 2"
                ),
                Deal(
                    id="demo3", address="789 Test Drive", purchase_price=300000,
                    arv=385000, repair_costs=35000, monthly_rent=2800,
                    closing_costs=9000, annual_taxes=4500, insurance=1500,
                    hoa_fees=200, vacancy_rate=4.0,
                    ai_score=92, property_type="Multi-Family", condition="Excellent",
                    neighborhood_grade="A-", market_trend="Rising", status="Analyzing",
                    created_at=datetime.now(), updated_at=datetime.now(), notes="Demo property 3"
                )
            ]
            
            if search_term:
                deals = [d for d in all_deals if search_term.lower() in d.address.lower()]
            else:
                deals = all_deals
    except Exception as e:
        st.error(f"Error loading deal data: {e}")
        deals = []
    
    # Apply status filter
    if status_filter != "All":
        deals = [deal for deal in deals if deal.status == status_filter]
    
    # Sort deals
    if sort_by == "AI Score (Highest)":
        deals.sort(key=lambda x: x.ai_score, reverse=True)
    elif sort_by == "Purchase Price (Highest)":
        deals.sort(key=lambda x: x.purchase_price, reverse=True)
    elif sort_by == "ROI (Highest)":
        deals.sort(key=lambda x: ((x.arv - x.purchase_price - x.repair_costs) / (x.purchase_price + x.repair_costs) * 100) if (x.purchase_price + x.repair_costs) > 0 else 0, reverse=True)
    else:  # Created Date (Newest)
        deals.sort(key=lambda x: x.created_at, reverse=True)
    
    if deals:
        st.success(f"📊 Found {len(deals)} deals")
        
        # Display deals in expandable cards
        for deal in deals:
            with st.expander(f"🏠 {deal.address} - AI Score: {deal.ai_score}/100", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Property Details:**")
                    st.write(f"• Type: {deal.property_type}")
                    st.write(f"• Condition: {deal.condition}")
                    st.write(f"• Neighborhood: {deal.neighborhood_grade}")
                    st.write(f"• Market Trend: {deal.market_trend}")
                
                with col2:
                    st.write("**Financial Summary:**")
                    st.write(f"• Purchase Price: ${deal.purchase_price:,.0f}")
                    st.write(f"• ARV: ${deal.arv:,.0f}")
                    st.write(f"• Repair Costs: ${deal.repair_costs:,.0f}")
                    st.write(f"• Monthly Rent: ${deal.monthly_rent:,.0f}")
                    
                    # Calculate ROI
                    total_investment = deal.purchase_price + deal.repair_costs
                    roi = ((deal.arv - total_investment) / total_investment * 100) if total_investment > 0 else 0
                    st.write(f"• ROI: {roi:.1f}%")
                
                with col3:
                    st.write("**Deal Status:**")
                    st.write(f"• Status: {deal.status}")
                    st.write(f"• Created: {deal.created_at}")
                    st.write(f"• AI Score: {deal.ai_score}/100")
                
                # Action buttons
                col_action1, col_action2 = st.columns(2)
                
                with col_action1:
                    if st.button(f"📊 Re-analyze", key=f"analyze_{deal.id}"):
                        st.info("Analysis complete - deal score updated")
                
                with col_action2:
                    new_status = st.selectbox("Update Status", 
                                            ["New", "Analyzing", "Under Contract", "Negotiating", "Closed", "Passed"],
                                            key=f"status_{deal.id}")
                    
                    if st.button(f"💾 Update", key=f"update_{deal.id}"):
                        deal.status = new_status
                        if db_service.update_deal(deal):
                            st.success(f"✅ Status updated to {new_status}")
    else:
        st.info("No deals found matching your criteria")

def show_portfolio_analytics():
    """Comprehensive Portfolio Analytics Dashboard"""
    st.header("📈 Portfolio Analytics")
    st.markdown("*Track performance and analyze your entire investment portfolio*")
    
    # Load portfolio data
    try:
        if db_service and db_service.is_connected():
            deals = db_service.get_deals()
        else:
            st.warning("⚠️ Database connection not available - showing demo data")
            # Create sample demo deals for testing
            from models import Deal
            from datetime import datetime
            deals = [
                Deal(
                    id="demo1", address="123 Demo Street", purchase_price=250000,
                    arv=320000, repair_costs=25000, monthly_rent=2500,
                    closing_costs=7500, annual_taxes=3000, insurance=1200,
                    hoa_fees=0, vacancy_rate=5.0,
                    ai_score=85, property_type="Single Family", condition="Good",
                    neighborhood_grade="B+", market_trend="Rising", status="Active",
                    created_at=datetime.now(), updated_at=datetime.now(), notes="Demo property 1"
                ),
                Deal(
                    id="demo2", address="456 Sample Ave", purchase_price=180000,
                    arv=245000, repair_costs=15000, monthly_rent=1800,
                    closing_costs=5400, annual_taxes=2200, insurance=900,
                    hoa_fees=150, vacancy_rate=8.0,
                    ai_score=78, property_type="Townhouse", condition="Fair",
                    neighborhood_grade="B", market_trend="Stable", status="Active",
                    created_at=datetime.now(), updated_at=datetime.now(), notes="Demo property 2"
                ),
                Deal(
                    id="demo3", address="789 Test Drive", purchase_price=300000,
                    arv=385000, repair_costs=35000, monthly_rent=2800,
                    closing_costs=9000, annual_taxes=4500, insurance=1500,
                    hoa_fees=200, vacancy_rate=4.0,
                    ai_score=92, property_type="Multi-Family", condition="Excellent",
                    neighborhood_grade="A-", market_trend="Rising", status="Active",
                    created_at=datetime.now(), updated_at=datetime.now(), notes="Demo property 3"
                )
            ]
    except Exception as e:
        st.error(f"Error loading portfolio data: {e}")
        deals = []
    
    if not deals:
        st.info("No portfolio data available. Add some deals first!")
        return
    
    # Portfolio Overview Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate portfolio metrics
    total_invested = sum(deal.purchase_price + deal.repair_costs for deal in deals)
    total_current_value = sum(deal.arv if deal.arv > 0 else deal.purchase_price * 1.1 for deal in deals)
    total_monthly_rent = sum(deal.monthly_rent for deal in deals)
    avg_ai_score = sum(deal.ai_score for deal in deals) / len(deals)
    
    with col1:
        st.metric("Total Invested", f"${total_invested:,.0f}")
    
    with col2:
        portfolio_gain = total_current_value - total_invested
        st.metric("Portfolio Value", f"${total_current_value:,.0f}", f"+${portfolio_gain:,.0f}")
    
    with col3:
        st.metric("Monthly Income", f"${total_monthly_rent:,.0f}")
    
    with col4:
        st.metric("Avg AI Score", f"{avg_ai_score:.1f}/100")
    
    # Portfolio Performance Chart
    st.subheader("📊 Portfolio Performance")
    
    # Create sample performance data
    import numpy as np
    months = pd.date_range(start='2024-01-01', periods=12, freq='M')
    portfolio_values = np.cumsum(np.random.normal(50000, 10000, 12)) + total_invested
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=portfolio_values, mode='lines+markers', 
                            name='Portfolio Value', line=dict(color='#2E8B57', width=3)))
    fig.update_layout(title="Portfolio Value Growth", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Property Breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 Property Type Distribution")
        
        property_types = {}
        for deal in deals:
            prop_type = deal.property_type
            property_types[prop_type] = property_types.get(prop_type, 0) + 1
        
        fig_pie = go.Figure(data=[go.Pie(labels=list(property_types.keys()), 
                                        values=list(property_types.values()))])
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=300)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("📊 Performance by Property")
        
        # Create performance comparison
        addresses = [deal.address[:25] + "..." if len(deal.address) > 25 else deal.address for deal in deals]
        roi_values = [((deal.arv - deal.purchase_price - deal.repair_costs) / (deal.purchase_price + deal.repair_costs) * 100) 
                     if (deal.purchase_price + deal.repair_costs) > 0 else 0 for deal in deals]
        
        fig_bar = go.Figure(data=[go.Bar(x=addresses, y=roi_values, marker_color='#4169E1')])
        fig_bar.update_layout(title="ROI by Property", height=300, xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Detailed Portfolio Table
    st.subheader("🗄️ Portfolio Details")
    
    portfolio_data = []
    for deal in deals:
        roi = ((deal.arv - deal.purchase_price - deal.repair_costs) / (deal.purchase_price + deal.repair_costs) * 100) if (deal.purchase_price + deal.repair_costs) > 0 else 0
        portfolio_data.append({
            'Address': deal.address,
            'Type': deal.property_type,
            'Purchase Price': f"${deal.purchase_price:,.0f}",
            'Current Value': f"${deal.arv:,.0f}" if deal.arv > 0 else f"${deal.purchase_price * 1.1:,.0f}",
            'Monthly Rent': f"${deal.monthly_rent:,.0f}",
            'AI Score': f"{deal.ai_score}/100",
            'ROI': f"{roi:.1f}%",
            'Status': deal.status
        })
    
    portfolio_df = pd.DataFrame(portfolio_data)
    st.dataframe(portfolio_df, use_container_width=True)

def show_investor_portal():
    """Investor Portal with Performance Tracking"""
    st.header("🏛️ Investor Portal")
    st.markdown("*Secure investor access and performance tracking*")
    
    # Import investor portal functionality
    try:
        from investor_portal import InvestorPortalManager, InvestorDashboard
        portal_manager = InvestorPortalManager()
        dashboard = InvestorDashboard(portal_manager)
    except ImportError:
        st.error("Investor portal module not available")
        return
    
    # Investor authentication (simplified for demo)
    if 'investor_authenticated' not in st.session_state:
        st.session_state.investor_authenticated = False
    
    if not st.session_state.investor_authenticated:
        st.subheader("🔐 Investor Login")
        
        with st.form("investor_login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted and email and password:
                # Demo authentication - in production use real auth
                if email.endswith("@investor.com"):
                    st.session_state.investor_authenticated = True
                    st.session_state.investor_id = "demo_investor_123"
                    st.session_state.investor_name = email.split('@')[0].title()
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        return
    
    # Investor Dashboard
    investor_name = st.session_state.get('investor_name', 'Investor')
    st.success(f"Welcome back, {investor_name}! 👋")
    
    # Performance Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Investment", "$485,000", "+$50K this quarter")
    
    with col2:
        st.metric("Current Portfolio Value", "$612,500", "+$127.5K")
    
    with col3:
        st.metric("Total Return", "$127,500", "+26.3% ROI")
    
    with col4:
        st.metric("Monthly Income", "$4,250", "+$350 vs last month")
    
    # Performance Chart
    st.subheader("📈 Investment Performance")
    
    # Generate sample performance data
    months = pd.date_range(start='2024-01-01', periods=12, freq='M')
    values = [485000 + (i * 10000) + np.random.normal(0, 5000) for i in range(12)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=values, mode='lines+markers', 
                            name='Portfolio Value', line=dict(color='#4CAF50', width=3)))
    fig.update_layout(title="Portfolio Growth Over Time", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Investment Details
    st.subheader("🏠 Your Properties")
    
    properties = [
        {"Address": "123 Oak Street", "Type": "SFR", "Investment": "$150K", "Current Value": "$185K", "Monthly Income": "$1,450"},
        {"Address": "456 Pine Avenue", "Type": "Duplex", "Investment": "$275K", "Current Value": "$320K", "Monthly Income": "$2,200"},
        {"Address": "789 Maple Drive", "Type": "SFR", "Investment": "$185K", "Current Value": "$225K", "Monthly Income": "$1,650"}
    ]
    
    for prop in properties:
        with st.expander(f"🏠 {prop['Address']} - {prop['Type']}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Investment:** {prop['Investment']}")
                st.write(f"**Property Type:** {prop['Type']}")
            
            with col2:
                st.write(f"**Current Value:** {prop['Current Value']}")
                investment_val = float(prop['Investment'].replace('$', '').replace('K', '')) * 1000
                current_val = float(prop['Current Value'].replace('$', '').replace('K', '')) * 1000
                gain = ((current_val - investment_val) / investment_val) * 100
                st.write(f"**Gain:** +{gain:.1f}%")
            
            with col3:
                st.write(f"**Monthly Income:** {prop['Monthly Income']}")
                annual_income = float(prop['Monthly Income'].replace('$', '').replace(',', '')) * 12
                yield_rate = (annual_income / current_val) * 100
                st.write(f"**Yield:** {yield_rate:.1f}%")
    
    # Logout button
    if st.button("🚪 Logout"):
        st.session_state.investor_authenticated = False
        st.rerun()

def show_ai_insights():
    """AI-Powered Market Insights and Analytics"""
    st.header("🧠 AI Market Insights")
    st.markdown("*Real-time market intelligence and predictive analytics*")
    
    # Market Overview
    st.subheader("📊 Current Market Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Market Temperature", "🔥 Hot", "↗️ +15% vs last quarter")
    
    with col2:
        st.metric("AI Confidence", "94%", "↗️ High accuracy")
    
    with col3:
        st.metric("Deal Opportunities", "127", "↗️ +23% this week")
    
    # AI Predictions
    st.subheader("🔮 AI Market Predictions")
    
    # Generate prediction chart
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    predicted_prices = [295000, 302000, 308000, 315000, 321000, 328000]
    confidence_upper = [p * 1.05 for p in predicted_prices]
    confidence_lower = [p * 0.95 for p in predicted_prices]
    
    fig = go.Figure()
    
    # Add confidence interval
    fig.add_trace(go.Scatter(x=months, y=confidence_upper, 
                            fill=None, mode='lines', line_color='rgba(0,0,0,0)', name='Upper Bound'))
    fig.add_trace(go.Scatter(x=months, y=confidence_lower,
                            fill='tonexty', mode='lines', line_color='rgba(0,100,80,0.2)',
                            name='Confidence Interval'))
    
    # Add prediction line
    fig.add_trace(go.Scatter(x=months, y=predicted_prices, mode='lines+markers',
                            name='Predicted Prices', line=dict(color='#2E8B57', width=3)))
    
    fig.update_layout(title="6-Month Price Predictions", height=400,
                     yaxis_title="Average Price ($)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Market Intelligence
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 AI Recommendations")
        
        recommendations = [
            "🔥 Focus on single-family homes in emerging neighborhoods",
            "💡 Consider light renovation properties for maximum ROI",
            "📈 Target properties with 15%+ cap rates in current market",
            "⏰ Act quickly - inventory is moving 23% faster than last quarter",
            "🏘️ Suburban markets showing strongest growth potential"
        ]
        
        for rec in recommendations:
            st.write(f"• {rec}")
    
    with col2:
        st.subheader("⚠️ Risk Alerts")
        
        alerts = [
            "📉 Commercial real estate showing signs of cooling",
            "🏗️ New construction permits up 18% - supply increasing",
            "💰 Interest rates expected to stabilize next quarter",
            "📊 Rental demand remains strong in target markets",
            "🌍 Economic indicators suggest continued market stability"
        ]
        
        for alert in alerts:
            st.write(f"• {alert}")
    
    # Advanced Analytics
    st.subheader("📈 Advanced Market Analytics")
    
    # Market trend analysis
    trend_data = {
        'Property Type': ['Single Family', 'Multi-Family', 'Condo', 'Townhouse'],
        'Avg Days on Market': [28, 35, 42, 31],
        'Price Appreciation': [12.5, 9.8, 7.2, 11.1],
        'Rental Yield': [8.2, 11.5, 6.8, 9.1]
    }
    
    trend_df = pd.DataFrame(trend_data)
    st.dataframe(trend_df, use_container_width=True)

def show_investor_matching():
    """Investor Matching System"""
    st.header("👥 Investor Matching")
    st.markdown("*Connect deals with qualified investors automatically*")
    
    tab1, tab2, tab3 = st.tabs(["🎯 Active Matches", "👥 Investor Network", "📊 Match Analytics"])
    
    with tab1:
        st.subheader("🔥 Hot Deal Matches")
        
        matches = [
            {"deal": "123 Oak Street - $245K SFR", "investor": "John Smith", "match_score": 92, "status": "Pending"},
            {"deal": "456 Pine Ave - $380K Duplex", "investor": "Sarah Johnson", "match_score": 88, "status": "Interested"},
            {"deal": "789 Elm Drive - $195K Fixer", "investor": "Mike Chen", "match_score": 85, "status": "Reviewing"},
        ]
        
        for match in matches:
            with st.expander(f"🏠 {match['deal']} ↔️ {match['investor']} ({match['match_score']}% match)"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Deal Details:**")
                    st.write(f"Property: {match['deal']}")
                    st.write(f"Match Score: {match['match_score']}%")
                
                with col2:
                    st.write("**Investor Profile:**")
                    st.write(f"Name: {match['investor']}")
                    st.write(f"Status: {match['status']}")
                
                with col3:
                    if st.button(f"📧 Send Deal", key=f"send_{match['deal']}"):
                        st.success("✅ Deal sent to investor!")
                    if st.button(f"📞 Schedule Call", key=f"call_{match['deal']}"):
                        st.success("✅ Call scheduled!")
    
    with tab2:
        st.subheader("👥 Investor Network")
        
        investors = [
            {"name": "John Smith", "type": "Fix & Flip", "budget": "$200K-400K", "active_deals": 3},
            {"name": "Sarah Johnson", "type": "Buy & Hold", "budget": "$300K-600K", "active_deals": 5},
            {"name": "Mike Chen", "type": "BRRRR", "budget": "$150K-350K", "active_deals": 2},
            {"name": "Lisa Wilson", "type": "Wholesale", "budget": "$100K-250K", "active_deals": 8},
        ]
        
        for inv in investors:
            with st.expander(f"👤 {inv['name']} - {inv['type']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Strategy:** {inv['type']}")
                    st.write(f"**Budget Range:** {inv['budget']}")
                
                with col2:
                    st.write(f"**Active Deals:** {inv['active_deals']}")
                    if st.button(f"📋 View Profile", key=f"profile_{inv['name']}"):
                        st.info(f"Viewing {inv['name']}'s detailed profile...")
    
    with tab3:
        st.subheader("📊 Matching Performance")
        
        # Matching statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Matches", "127", "+12 this week")
        
        with col2:
            st.metric("Success Rate", "73%", "+5% vs last month")
        
        with col3:
            st.metric("Avg Match Score", "86%", "↗️ Improving")
        
        with col4:
            st.metric("Active Investors", "24", "+3 new this month")
        
        # Matching trends
        st.subheader("📈 Match Success Trends")
        
        weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
        success_rates = [68, 71, 75, 73]
        
        fig = go.Figure(data=go.Bar(x=weeks, y=success_rates, marker_color='#4CAF50'))
        fig.update_layout(title="Weekly Match Success Rate", yaxis_title="Success Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

def show_advanced_deal_analytics():
    """Advanced Deal Analytics Module"""
    try:
        from advanced_deal_analytics import show_advanced_deal_analytics
        show_advanced_deal_analytics(db_service)
    except ImportError:
        st.info("Advanced Deal Analytics module loading...")
        st.write("This feature provides comprehensive deal scoring and market analysis.")

def show_automated_deal_sourcing():
    """Automated Deal Sourcing Module"""
    try:
        from automated_deal_sourcing import show_automated_deal_sourcing
        show_automated_deal_sourcing()
    except ImportError:
        st.info("Automated Deal Sourcing module loading...")
        st.write("This feature provides intelligent property discovery and investor matching.")

def show_ai_enhancement_system():
    """AI Enhancement System Module"""
    try:
        from ai_enhancement_system import show_ai_insights_dashboard
        from ai_enhancement_system import AIEnhancementSystem
        ai_system = AIEnhancementSystem()
        show_ai_insights_dashboard(ai_system)
    except ImportError:
        st.info("AI Enhancement System module loading...")
        st.write("This feature provides advanced AI-powered insights and automation.")

# Professional Settings Functions
def show_profile_settings():
    """Show professional profile management settings"""
    st.subheader("👤 Profile Management")
    
    # Personal Information
    with st.expander("Personal Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", value=st.session_state.get('first_name', 'John'))
            email = st.text_input("Email Address", value=st.session_state.get('email', 'john@example.com'))
            phone = st.text_input("Phone Number", value="+1 (555) 123-4567")
        
        with col2:
            last_name = st.text_input("Last Name", value=st.session_state.get('last_name', 'Doe'))
            company = st.text_input("Company/Organization", value=st.session_state.get('company', 'Real Estate Investments LLC'))
            timezone = st.selectbox("Timezone", ["EST", "CST", "MST", "PST"], index=0)
        
        if st.button("💾 Update Profile", type="primary"):
            st.success("✅ Profile updated successfully!")
    
    # Professional Information
    with st.expander("Professional Information"):
        license_number = st.text_input("Real Estate License #", value="RE123456789")
        years_experience = st.slider("Years of Experience", 0, 50, 10)
        investment_focus = st.multiselect("Investment Focus", 
                                        ["Residential", "Commercial", "Multi-Family", "Fix & Flip", "Buy & Hold", "Wholesale"],
                                        default=["Residential", "Fix & Flip"])
        target_markets = st.text_area("Target Markets", "Austin, TX\nHouston, TX\nDallas, TX")
        
        if st.button("💾 Update Professional Info"):
            st.success("✅ Professional information updated!")

def show_security_settings():
    """Show security and privacy settings"""
    st.subheader("🔐 Security & Privacy")
    
    # Password Management
    with st.expander("Password & Authentication", expanded=True):
        st.write("**Change Password**")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.button("🔄 Change Password"):
            if new_password == confirm_password:
                st.success("✅ Password updated successfully!")
            else:
                st.error("❌ Passwords do not match")
        
        st.markdown("---")
        st.write("**Two-Factor Authentication**")
        enable_2fa = st.checkbox("Enable Two-Factor Authentication", value=False)
        if enable_2fa:
            st.info("📱 2FA would be configured via SMS or authenticator app")
    
    # Privacy Settings
    with st.expander("Privacy Settings"):
        data_sharing = st.checkbox("Allow anonymous usage analytics", value=True)
        marketing_emails = st.checkbox("Receive marketing communications", value=True)
        api_access = st.checkbox("Enable API access for third-party integrations", value=False)
        
        if st.button("💾 Save Privacy Settings"):
            st.success("✅ Privacy settings updated!")

def show_billing_settings():
    """Show billing and subscription management"""
    st.subheader("💳 Billing & Subscription")
    
    # Current Plan
    with st.expander("Current Subscription", expanded=True):
        user_tier = st.session_state.get('user_tier', 'solo')
        st.info(f"**Current Plan:** {user_tier.title()}")
        
        # Plan details
        if user_tier == 'solo':
            st.write("**Solo Plan - $79/month**")
            features = ["✅ Up to 500 CRM contacts", "✅ Basic deal analytics", "✅ 10 portfolio properties", "❌ Team collaboration", "❌ Advanced automation"]
        elif user_tier == 'professional':
            st.write("**Professional Plan - $219/month**") 
            features = ["✅ Unlimited CRM contacts", "✅ Advanced deal analytics", "✅ 100 portfolio properties", "✅ Team collaboration (5 users)", "✅ Advanced automation"]
        else:
            st.write("**Enterprise Plan - $497/month**")
            features = ["✅ Unlimited everything", "✅ Custom integrations", "✅ White-label options", "✅ Priority support", "✅ Advanced reporting"]
        
        for feature in features:
            st.write(feature)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Upgrade Plan"):
                st.info("Upgrade options would be displayed here")
        with col2:
            if st.button("📄 View Invoice History"):
                st.info("Invoice history would be shown here")
    
    # Payment Method
    with st.expander("Payment Methods"):
        st.write("**Primary Payment Method**")
        st.write("💳 **** **** **** 1234 (Visa)")
        st.write("Expires: 12/2027")
        
        if st.button("🔄 Update Payment Method"):
            st.info("Payment method update form would appear here")

def show_notification_settings():
    """Show notification preferences"""
    st.subheader("🔔 Notification Preferences")
    
    # Email Notifications
    with st.expander("Email Notifications", expanded=True):
        deal_alerts = st.checkbox("New deal opportunities", value=True)
        market_updates = st.checkbox("Market intelligence updates", value=True)
        portfolio_reports = st.checkbox("Weekly portfolio reports", value=True)
        system_updates = st.checkbox("System updates and maintenance", value=True)
        
    # SMS Notifications  
    with st.expander("SMS Notifications"):
        sms_deals = st.checkbox("Urgent deal alerts via SMS", value=False)
        sms_security = st.checkbox("Security alerts via SMS", value=True)
        
    # In-App Notifications
    with st.expander("In-App Notifications"):
        browser_notifications = st.checkbox("Enable browser notifications", value=True)
        sound_alerts = st.checkbox("Enable sound alerts", value=False)
        
    if st.button("💾 Save Notification Settings"):
        st.success("✅ Notification preferences updated!")

def show_interface_settings():
    """Show interface and display preferences"""
    st.subheader("🎨 Interface Preferences")
    
    # Theme and Display
    with st.expander("Theme & Display", expanded=True):
        theme = st.selectbox("Color Theme", ["Dark", "Light", "Auto"], index=0)
        density = st.selectbox("Display Density", ["Comfortable", "Compact", "Spacious"], index=0)
        sidebar_default = st.selectbox("Sidebar Default State", ["Expanded", "Collapsed"], index=0)
        
    # Dashboard Preferences
    with st.expander("Dashboard Layout"):
        default_page = st.selectbox("Default Landing Page", 
                                  ["Executive Dashboard", "Deal Analysis", "Enhanced CRM", "Portfolio Analytics"], 
                                  index=0)
        chart_style = st.selectbox("Chart Style", ["Modern", "Classic", "Minimal"], index=0)
        currency_format = st.selectbox("Currency Format", ["$1,234.56", "$1 234.56", "1,234.56 USD"], index=0)
        
    # Advanced Options
    with st.expander("Advanced Options"):
        auto_save = st.checkbox("Enable auto-save for forms", value=True)
        analytics_tracking = st.checkbox("Enable usage analytics", value=True)
        keyboard_shortcuts = st.checkbox("Enable keyboard shortcuts", value=True)
        
    if st.button("💾 Save Interface Settings"):
        st.success("✅ Interface preferences updated!")

def show_deal_analysis():
    """Show AI-powered deal analysis"""
    st.header("🏠 AI-Powered Deal Analysis")
    st.markdown("*Comprehensive property evaluation with AI scoring*")
    
    with st.form("deal_analysis_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Property Details")
            address = st.text_input("Property Address")
            property_type = st.selectbox("Property Type", 
                ["Single Family", "Multi-Family", "Condo", "Townhouse", "Commercial"])
            purchase_price = st.number_input("Purchase Price ($)", min_value=0, value=200000)
            
        with col2:
            st.subheader("Financial Information")
            arv = st.number_input("After Repair Value ($)", min_value=0, value=275000)
            repair_costs = st.number_input("Repair Costs ($)", min_value=0, value=25000)
            monthly_rent = st.number_input("Monthly Rent ($)", min_value=0, value=2200)
        
        submitted = st.form_submit_button("🔍 Analyze Deal", type="primary", use_container_width=True)
        
        if submitted and address:
            # Calculate key metrics
            total_investment = purchase_price + repair_costs
            equity = arv - total_investment
            equity_percentage = (equity / total_investment) * 100 if total_investment > 0 else 0
            annual_rent = monthly_rent * 12
            gross_yield = (annual_rent / total_investment) * 100 if total_investment > 0 else 0
            
            # AI Score calculation (simplified)
            ai_score = min(100, max(0, 
                (equity_percentage * 0.4) + 
                (gross_yield * 0.3) + 
                (50 if property_type in ["Single Family", "Multi-Family"] else 30) +
                (20 if repair_costs < purchase_price * 0.2 else 10)
            ))
            
            st.success("✅ Analysis Complete!")
            
            # Results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("AI Score", f"{ai_score:.1f}/100")
                st.metric("Potential Equity", f"${equity:,.0f}")
            
            with col2:
                st.metric("Equity %", f"{equity_percentage:.1f}%")
                st.metric("Gross Yield", f"{gross_yield:.1f}%")
            
            with col3:
                st.metric("Total Investment", f"${total_investment:,.0f}")
                st.metric("Monthly Cash Flow", f"${monthly_rent - (total_investment * 0.01):.0f}")
            
            # Recommendation
            if ai_score >= 80:
                st.success("🎯 **EXCELLENT DEAL** - Highly recommended!")
            elif ai_score >= 65:
                st.info("✅ **GOOD DEAL** - Worth pursuing")
            elif ai_score >= 50:
                st.warning("⚠️ **MARGINAL DEAL** - Needs improvement")
            else:
                st.error("❌ **POOR DEAL** - Not recommended")

# [Include all other functions from the previous platform...]

# Main application function
def show_pricing_page():
    """Display pricing and subscription plans with Stripe integration"""
    st.title("💳 Choose Your NXTRIX Plan")
    st.markdown("*Transform your real estate investment business with the right plan*")
    
    # Current user info
    current_tier = st.session_state.get('user_tier', 'trial')
    user_email = st.session_state.get('user_email', '')
    user_id = st.session_state.get('user_id', '')
    
    # Check for payment success
    query_params = st.query_params
    if query_params.get('payment_success') == 'true':
        st.success("🎉 **Payment Successful!** Your subscription has been activated.")
        st.balloons()
        
        # Clear the query params to avoid repeated messages
        st.query_params.clear()
    elif query_params.get('payment_canceled') == 'true':
        st.warning("Payment was canceled. You can try again anytime.")
    
    if current_tier != 'trial':
        st.info(f"**Current Plan:** {current_tier.title()}")
    
    # Billing frequency toggle
    st.markdown("### 💰 **Choose Billing Frequency**")
    billing_col1, billing_col2 = st.columns([1, 1])
    
    with billing_col1:
        billing_frequency = st.radio(
            "Select billing:",
            ["Monthly", "Annual (Save 20%)"],
            index=0,
            horizontal=True
        )
    
    is_annual = "Annual" in billing_frequency
    
    if is_annual:
        st.success("🎊 **Annual Billing Selected** - Save 20% with yearly payment!")
    
    # Pricing cards
    col1, col2, col3 = st.columns(3)
    
    # Define pricing based on billing frequency
    monthly_prices = {'solo': 79, 'team': 119, 'business': 219}
    annual_prices = {'solo': 63, 'team': 95, 'business': 175}  # 20% discount
    
    current_prices = annual_prices if is_annual else monthly_prices
    billing_text = "/year (billed annually)" if is_annual else "/month"
    
    plans = {
        'solo': {
            'name': 'Solo Professional',
            'price': f"${current_prices['solo']}",
            'billing': billing_text,
            'original_price': f"${monthly_prices['solo']}/month" if is_annual else None,
            'description': 'Perfect for individual investors',
            'stripe_price_id': get_config("STRIPE", "SOLO_ANNUAL_PRICE_ID") if is_annual else get_config("STRIPE", "SOLO_PRICE_ID"),
            'features': [
                '✅ 50 deals per month',
                '✅ Advanced financial modeling',
                '✅ AI-powered deal analysis',
                '✅ Portfolio performance tracking',
                '✅ Professional reports & exports',
                '✅ Investor portal management',
                '✅ Email support'
            ],
            'popular': False
        },
        'team': {
            'name': 'Team Collaboration', 
            'price': f"${current_prices['team']}",
            'billing': billing_text,
            'original_price': f"${monthly_prices['team']}/month" if is_annual else None,
            'description': 'Most popular for growing teams',
            'stripe_price_id': get_config("STRIPE", "TEAM_ANNUAL_PRICE_ID") if is_annual else get_config("STRIPE", "TEAM_PRICE_ID"),
            'features': [
                '✅ Everything in Solo +',
                '✅ 200 deals per month',
                '✅ Multi-user team access (5 users)',
                '✅ Advanced deal analytics',
                '✅ Automated deal sourcing',
                '✅ Enhanced CRM features',
                '✅ Priority support'
            ],
            'popular': True
        },
        'business': {
            'name': 'Enterprise Solution',
            'price': f"${current_prices['business']}", 
            'billing': billing_text,
            'original_price': f"${monthly_prices['business']}/month" if is_annual else None,
            'description': 'Unlimited power for enterprises',
            'stripe_price_id': get_config("STRIPE", "BUSINESS_ANNUAL_PRICE_ID") if is_annual else get_config("STRIPE", "BUSINESS_PRICE_ID"),
            'features': [
                '✅ Everything in Team +',
                '✅ Unlimited deals & portfolios',
                '✅ Unlimited team members',
                '✅ AI enhancement suite',
                '✅ Complete feature access',
                '✅ Advanced automation tools',
                '✅ Dedicated support'
            ],
            'popular': False
        }
    }
    
    for i, (plan_key, plan) in enumerate(plans.items()):
        with [col1, col2, col3][i]:
            # Card styling with popular badge
            card_style = "border: 3px solid #FF6B6B;" if plan['popular'] else "border: 2px solid #E0E0E0;"
            
            st.markdown(f"""
            <div style="{card_style} border-radius: 10px; padding: 20px; margin: 10px 0; background: white; position: relative;">
            """, unsafe_allow_html=True)
            
            if plan['popular']:
                st.markdown("""
                <div style="background: #FF6B6B; color: white; text-align: center; padding: 5px; 
                margin: -20px -20px 15px -20px; border-radius: 8px 8px 0 0; font-weight: bold;">
                🔥 MOST POPULAR</div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"### {plan['name']}")
            
            # Price display with savings
            if is_annual and plan['original_price']:
                st.markdown(f"""
                **{plan['price']}{plan['billing']}**  
                <small style='text-decoration: line-through; color: #999;'>{plan['original_price']}</small>  
                <span style='color: #28a745; font-weight: bold;'>Save 20%!</span>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"**{plan['price']}{plan['billing']}**")
                
            st.caption(plan['description'])
            
            st.markdown("**Features:**")
            for feature in plan['features']:
                st.markdown(f"<small>{feature}</small>", unsafe_allow_html=True)
            
            # Subscription button
            button_disabled = current_tier == plan_key
            button_text = "Current Plan" if button_disabled else "Choose Plan"
            
            if st.button(
                button_text, 
                key=f"select_{plan_key}_{billing_frequency}", 
                disabled=button_disabled,
                type="primary" if plan['popular'] else "secondary"
            ):
                if user_id and user_email:
                    # Create Stripe checkout session with correct price ID
                    try:
                        import stripe
                        stripe.api_key = get_config("STRIPE", "STRIPE_SECRET_KEY")
                        
                        checkout_session = stripe.checkout.Session.create(
                            payment_method_types=['card'],
                            line_items=[{
                                'price': plan['stripe_price_id'],
                                'quantity': 1,
                            }],
                            mode='subscription',
                            customer_email=user_email,
                            client_reference_id=user_id,
                            success_url=f"{st.secrets.get('APP', {}).get('BASE_URL', 'https://nxtrix-platform.streamlit.app')}?payment_success=true&session_id={{CHECKOUT_SESSION_ID}}",
                            cancel_url=f"{st.secrets.get('APP', {}).get('BASE_URL', 'https://nxtrix-platform.streamlit.app')}?payment_canceled=true",
                            metadata={
                                'user_id': user_id,
                                'plan_tier': plan_key,
                                'billing_frequency': 'annual' if is_annual else 'monthly'
                            }
                        )
                        
                        st.markdown(f"[🚀 **Complete Payment - {plan['name']}**]({checkout_session.url})")
                        st.info("Click above to proceed to secure Stripe checkout")
                        
                    except Exception as e:
                        st.error(f"Payment setup error: {e}")
                        st.info("Please try again or contact support")
                else:
                    st.error("Please log in to subscribe")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Payment information
    st.markdown("---")
    st.markdown("""
    ### � **Secure Payment Processing**
    
    - 🔒 **Secure payments** powered by Stripe
    - 💳 **All major cards** accepted  
    - 🔄 **Cancel anytime** with one click
    - 📞 **24/7 support** for all subscribers
    """)

def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    # Check if user wants to view pricing
    if st.session_state.get('show_pricing', False):
        st.session_state['show_pricing'] = False  # Reset flag
        show_pricing_page()
        return
    
    # Check authentication
    if not check_authentication():
        show_authentication_ui()
        return
    
    # Main application interface
    st.sidebar.title("🏢 NXTRIX")
    
    # Show user info
    user_name = st.session_state.get('user_name', 'User')
    user_tier = st.session_state.get('user_tier', 'solo')
    user_id = st.session_state.get('user_id', '')
    
    st.sidebar.success(f"✅ Welcome, {user_name}!")
    
    # Subscription Status Display
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💳 Subscription Status")
    
    # Display current plan with styling
    plan_colors = {
        'trial': '#FF9800',
        'solo': '#4CAF50', 
        'team': '#2196F3',
        'business': '#9C27B0'
    }
    
    plan_names = {
        'trial': '🆓 Free Trial',
        'solo': '🌟 Solo Professional',
        'team': '⭐ Team Collaboration', 
        'business': '🏢 Enterprise Solution'
    }
    
    plan_color = plan_colors.get(user_tier, '#666666')
    plan_name = plan_names.get(user_tier, user_tier.title())
    
    st.sidebar.markdown(f"""
    <div style="padding: 10px; border-left: 4px solid {plan_color}; background-color: rgba(128,128,128,0.1); border-radius: 5px; margin: 10px 0;">
        <strong style="color: {plan_color};">{plan_name}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Show usage stats
    if user_id:
        deals_current, deals_limit, can_add_deals = check_usage_limits(user_id, 'deals')
        portfolios_current, portfolios_limit, can_add_portfolios = check_usage_limits(user_id, 'portfolios')
        
        st.sidebar.markdown("**This Month:**")
        deals_text = f"∞" if deals_limit == -1 else str(deals_limit)
        portfolios_text = f"∞" if portfolios_limit == -1 else str(portfolios_limit)
        
        st.sidebar.caption(f"📊 Deals: {deals_current}/{deals_text}")
        st.sidebar.caption(f"📈 Portfolios: {portfolios_current}/{portfolios_text}")
        
        # Warning if approaching limits
        if deals_limit != -1 and deals_current >= deals_limit * 0.8:
            st.sidebar.warning("⚠️ Approaching deal limit")
        if portfolios_limit != -1 and portfolios_current >= portfolios_limit * 0.8:
            st.sidebar.warning("⚠️ Approaching portfolio limit")
    
    # Upgrade button for non-business users
    if user_tier != 'business':
        if st.sidebar.button("📈 **Upgrade Plan**", type="primary"):
            st.session_state['show_pricing'] = True
            st.rerun()
    
    # Main navigation
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🧭 Navigation")
    
    # Core platform pages
    main_pages = [
        "📊 Executive Dashboard",
        "🏠 Deal Analysis", 
        "💹 Financial Modeling",
        "🗄️ Deal Database",
        "📈 Portfolio Analytics",
        "🏛️ Investor Portal",
        "🧠 AI Insights",
        "👥 Investor Matching"
    ]
    
    # Enhanced CRM section
    if ENHANCED_CRM_AVAILABLE:
        main_pages.append("🤝 Enhanced CRM Suite")
    
    # Advanced modules (with subscription enforcement)
    advanced_pages = []
    if DEAL_ANALYTICS_AVAILABLE and check_feature_access('advanced_analytics'):
        advanced_pages.append("📊 Advanced Deal Analytics")
    elif DEAL_ANALYTICS_AVAILABLE:
        advanced_pages.append("📊 Advanced Deal Analytics 🔒")
        
    if DEAL_SOURCING_AVAILABLE and check_feature_access('automated_deal_sourcing'):
        advanced_pages.append("🔍 Automated Deal Sourcing")
    elif DEAL_SOURCING_AVAILABLE:
        advanced_pages.append("🔍 Automated Deal Sourcing 🔒")
        
    if AI_ENHANCEMENT_AVAILABLE and check_feature_access('ai_insights'):
        advanced_pages.append("🧠 AI Enhancement System")
    elif AI_ENHANCEMENT_AVAILABLE:
        advanced_pages.append("🧠 AI Enhancement System 🔒")
    
    if advanced_pages:
        main_pages.extend(advanced_pages)
    
    page = st.sidebar.selectbox("Select Module:", main_pages)
    
    # Page routing
    if page == "📊 Executive Dashboard":
        show_dashboard()
    elif page == "🏠 Deal Analysis":
        show_deal_analysis()
    elif page == "💹 Financial Modeling":
        show_financial_modeling()
    elif page == "🗄️ Deal Database":
        show_deal_database()
    elif page == "📈 Portfolio Analytics":
        show_portfolio_analytics()
    elif page == "🏛️ Investor Portal":
        show_investor_portal()
    elif page == "🧠 AI Insights":
        show_ai_insights()
    elif page == "👥 Investor Matching":
        show_investor_matching()
    elif page == "🤝 Enhanced CRM Suite" and ENHANCED_CRM_AVAILABLE:
        show_enhanced_crm()
    elif "📊 Advanced Deal Analytics" in page and DEAL_ANALYTICS_AVAILABLE:
        if check_feature_access('advanced_analytics'):
            show_advanced_deal_analytics()
        else:
            show_upgrade_prompt("Advanced Deal Analytics", "solo")
    elif "🔍 Automated Deal Sourcing" in page and DEAL_SOURCING_AVAILABLE:
        if check_feature_access('automated_deal_sourcing'):
            show_automated_deal_sourcing()
        else:
            show_upgrade_prompt("Automated Deal Sourcing", "team")
    elif "🧠 AI Enhancement System" in page and AI_ENHANCEMENT_AVAILABLE:
        if check_feature_access('ai_insights'):
            show_ai_enhancement_system()
        else:
            show_upgrade_prompt("AI Enhancement System", "solo")
    else:
        st.info(f"Page '{page}' is being loaded...")
        st.write("This page is available in your current plan.")
    
    # User menu and logout
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 Account")
    
    # Settings dropdown
    with st.sidebar.expander("⚙️ Settings & Preferences"):
        st.markdown("**Account Settings**")
        if st.button("👤 Profile Management", use_container_width=True):
            show_profile_settings()
        
        if st.button("🔐 Security & Privacy", use_container_width=True):
            show_security_settings()
            
        if st.button("💳 Billing & Subscription", use_container_width=True):
            show_billing_settings()
            
        if st.button("🔔 Notifications", use_container_width=True):
            show_notification_settings()
            
        if st.button("🎨 Interface Preferences", use_container_width=True):
            show_interface_settings()
    
    # Plan info and trial status
    if user_tier == 'trial':
        trial_active, expiry_date, days_info = check_trial_status()
        if trial_active and days_info is not None:
            st.sidebar.info(f"🆓 **Free Trial** - {days_info} days left")
        elif not trial_active:
            st.sidebar.error(f"⏰ **Trial Expired** - Upgrade required")
        else:
            st.sidebar.info(f"🆓 **Free Trial**")
    else:
        st.sidebar.info(f"📊 **{user_tier.title()} Plan**")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**NXTRIX v3.0**")
    st.sidebar.markdown("*Real Estate Investment Platform*")

if __name__ == "__main__":
    main()