"""
NXTRIX Platform - Production Database Authentication
Connects to your Supabase production database with 56 tables
"""

import streamlit as st
import hashlib
import secrets
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any
import uuid

# Database connection using Supabase credentials
def get_database_connection():
    """Connect to production Supabase database"""
    try:
        connection = psycopg2.connect(
            host=st.secrets["supabase"]["host"],
            database=st.secrets["supabase"]["database"],
            user=st.secrets["supabase"]["user"],
            password=st.secrets["supabase"]["password"],
            port=st.secrets["supabase"]["port"]
        )
        return connection
    except Exception as e:
        # Log error internally but don't show to users
        print(f"Database connection error: {e}")
        return None

# User authentication functions
def hash_password(password: str, salt: str = None) -> tuple:
    """Hash password with salt for secure storage"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    password_hash = hashlib.pbkdf2_hmac('sha256', 
                                       password.encode('utf-8'), 
                                       salt.encode('utf-8'), 
                                       100000)
    return password_hash.hex(), salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify password against stored hash"""
    password_hash, _ = hash_password(password, salt)
    return password_hash == stored_hash

def authenticate_user(email: str, password: str) -> Optional[Dict[Any, Any]]:
    """Authenticate user against production database"""
    conn = get_database_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get user from profiles table
            cur.execute("""
                SELECT id, email, password_hash, password_salt, 
                       subscription_tier, first_name, last_name, 
                       created_at, last_login_at
                FROM profiles 
                WHERE email = %s AND active = true
            """, (email,))
            
            user = cur.fetchone()
            
            if user and verify_password(password, user['password_hash'], user['password_salt']):
                # Update last login
                cur.execute("""
                    UPDATE profiles 
                    SET last_login_at = NOW() 
                    WHERE id = %s
                """, (user['id'],))
                conn.commit()
                
                return dict(user)
            
            return None
            
    except Exception as e:
        # Log error internally but don't show to users
        print(f"Authentication error: {e}")
        return None
    finally:
        conn.close()

def create_user(email: str, password: str, first_name: str, last_name: str, 
                subscription_tier: str = 'starter') -> Optional[str]:
    """Create new user in production database"""
    conn = get_database_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor() as cur:
            # Check if user already exists
            cur.execute("SELECT id FROM profiles WHERE email = %s", (email,))
            if cur.fetchone():
                st.error("❌ User already exists with this email")
                return None
            
            # Hash password
            password_hash, password_salt = hash_password(password)
            user_id = str(uuid.uuid4())
            
            # Insert new user
            cur.execute("""
                INSERT INTO profiles (
                    id, email, password_hash, password_salt, 
                    first_name, last_name, subscription_tier, 
                    created_at, active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), true)
            """, (user_id, email, password_hash, password_salt, 
                  first_name, last_name, subscription_tier))
            
            conn.commit()
            st.success("✅ Account created successfully!")
            return user_id
            
    except Exception as e:
        st.error(f"❌ Error creating user: {e}")
        return None
    finally:
        conn.close()

def get_user_subscription_info(user_id: str) -> Dict[str, Any]:
    """Get user's subscription and usage information"""
    conn = get_database_connection()
    if not conn:
        return {}
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get subscription info
            cur.execute("""
                SELECT su.*, sl.deal_limit, sl.lead_limit, sl.ai_analysis_limit
                FROM subscription_usage su
                JOIN subscription_limits sl ON su.subscription_tier = sl.tier_name
                WHERE su.user_id = %s
            """, (user_id,))
            
            subscription = cur.fetchone()
            return dict(subscription) if subscription else {}
            
    except Exception as e:
        st.error(f"❌ Error getting subscription info: {e}")
        return {}
    finally:
        conn.close()

def check_feature_access(user_id: str, feature: str) -> bool:
    """Check if user has access to a specific feature"""
    subscription_info = get_user_subscription_info(user_id)
    
    if not subscription_info:
        return False
    
    # Feature access logic based on subscription tier
    tier = subscription_info.get('subscription_tier', 'starter')
    
    feature_access = {
        'starter': ['basic_crm', 'deal_analysis', 'basic_reporting'],
        'professional': ['basic_crm', 'deal_analysis', 'basic_reporting', 
                        'advanced_analytics', 'ai_insights', 'automation'],
        'enterprise': ['basic_crm', 'deal_analysis', 'basic_reporting', 
                      'advanced_analytics', 'ai_insights', 'automation',
                      'custom_reports', 'api_access', 'priority_support']
    }
    
    return feature in feature_access.get(tier, [])

def production_login_form():
    """Production login form connecting to your database"""
    st.title("🏢 NXTRIX Platform v3.0")
    st.markdown("### � Professional Real Estate Platform")
    st.success("🎯 **Enterprise-Grade Investment Management**")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Create Account"])
    
    with tab1:
        with st.form("production_login"):
            email = st.text_input("Email Address", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_btn = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
            with col2:
                demo_btn = st.form_submit_button("👁️ Demo Mode", use_container_width=True)
        
        if login_btn and email and password:
            with st.spinner("🔍 Authenticating..."):
                user = authenticate_user(email, password)
                
                if user:
                    # Set session state
                    st.session_state['authenticated'] = True
                    st.session_state['user_id'] = user['id']
                    st.session_state['user_email'] = user['email']
                    st.session_state['user_name'] = f"{user['first_name']} {user['last_name']}"
                    st.session_state['subscription_tier'] = user['subscription_tier']
                    
                    st.success(f"✅ Welcome back, {user['first_name']}!")
                    st.success(f"🎯 Subscription: {user['subscription_tier'].title()}")
                    st.rerun()
                else:
                    # Check if database is available
                    conn = get_database_connection()
                    if conn:
                        conn.close()
                        st.error("❌ Invalid email or password")
                    else:
                        st.warning("⚠️ Unable to connect to database. Please try Demo Mode or contact support.")
                        st.info("🔧 **Demo Mode Available**: Click 'Demo Mode' to explore the platform")
        
        elif demo_btn:
            # Demo mode with limited access
            st.session_state['authenticated'] = True
            st.session_state['user_id'] = 'demo_user'
            st.session_state['user_email'] = 'demo@nxtrix.com'
            st.session_state['user_name'] = 'Demo User'
            st.session_state['subscription_tier'] = 'starter'
            st.success("✅ Demo mode activated!")
            st.info("🎯 **Demo Access**: Explore platform features with sample data")
            st.rerun()
    
    with tab2:
        with st.form("create_account"):
            st.markdown("#### Create Your NXTRIX Account")
            
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name")
                email_new = st.text_input("Email Address")
            with col2:
                last_name = st.text_input("Last Name") 
                password_new = st.text_input("Password", type="password")
            
            subscription_tier = st.selectbox("Subscription Tier", 
                                           ["starter", "professional", "enterprise"])
            
            create_btn = st.form_submit_button("🎯 Create Account", type="primary", use_container_width=True)
        
        if create_btn and all([first_name, last_name, email_new, password_new]):
            with st.spinner("🔄 Creating account..."):
                user_id = create_user(email_new, password_new, first_name, last_name, subscription_tier)
                
                if user_id:
                    st.success("🎉 Account created! Please login above.")
                    st.balloons()

def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current authenticated user information"""
    if not st.session_state.get('authenticated', False):
        return None
    
    return {
        'id': st.session_state.get('user_id'),
        'email': st.session_state.get('user_email'),
        'name': st.session_state.get('user_name'),
        'subscription_tier': st.session_state.get('subscription_tier')
    }

def logout_user():
    """Logout current user"""
    for key in ['authenticated', 'user_id', 'user_email', 'user_name', 'subscription_tier']:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("✅ Logged out successfully!")
    st.rerun()