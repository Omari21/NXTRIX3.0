"""
Enterprise Authentication System for NXTRIX 3.0
Comprehensive user management, session handling, and security features
"""

import streamlit as st
import sqlite3
import hashlib
import secrets
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
import re
import json

class StreamlitAuth:
    def __init__(self):
        self.db_path = "nxtrix_users.db"
        self.init_database()
        
    def init_database(self):
        """Initialize user database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_uuid TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                company TEXT,
                phone TEXT,
                subscription_tier TEXT DEFAULT 'starter',
                subscription_status TEXT DEFAULT 'trial',
                trial_started TEXT,
                trial_ends TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT,
                is_active BOOLEAN DEFAULT 1,
                email_verified BOOLEAN DEFAULT 0,
                preferences TEXT DEFAULT '{}',
                usage_stats TEXT DEFAULT '{}'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_uuid TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT,
                ip_address TEXT,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_uuid) REFERENCES users (user_uuid)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${password_hash.hex()}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, hash_part = stored_hash.split('$')
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash.hex() == hash_part
        except:
            return False
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_password(self, password: str) -> List[str]:
        """Validate password strength"""
        errors = []
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        return errors
    
    def register_user(self, email: str, password: str, full_name: str, 
                     company: str = "", phone: str = "", subscription_tier: str = "starter") -> Dict[str, Any]:
        """Register new user"""
        try:
            # Validate inputs
            if not self.validate_email(email):
                return {"success": False, "error": "Invalid email format"}
            
            password_errors = self.validate_password(password)
            if password_errors:
                return {"success": False, "error": "; ".join(password_errors)}
            
            if not full_name.strip():
                return {"success": False, "error": "Full name is required"}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT email FROM users WHERE email = ?", (email.lower(),))
            if cursor.fetchone():
                conn.close()
                return {"success": False, "error": "Email already registered"}
            
            # Create user
            user_uuid = str(uuid.uuid4())
            password_hash = self.hash_password(password)
            trial_started = datetime.now().isoformat()
            trial_ends = (datetime.now() + timedelta(days=7)).isoformat()
            
            cursor.execute('''
                INSERT INTO users (user_uuid, email, password_hash, full_name, company, phone,
                                 subscription_tier, trial_started, trial_ends)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_uuid, email.lower(), password_hash, full_name, company, phone,
                  subscription_tier, trial_started, trial_ends))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True, 
                "user_uuid": user_uuid,
                "message": "Registration successful! 7-day trial started."
            }
            
        except Exception as e:
            return {"success": False, "error": f"Registration failed: {str(e)}"}
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user login"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_uuid, password_hash, full_name, subscription_tier, subscription_status,
                       trial_ends, is_active FROM users WHERE email = ?
            ''', (email.lower(),))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {"success": False, "error": "Invalid email or password"}
            
            user_uuid, stored_hash, full_name, tier, status, trial_ends, is_active = result
            
            if not is_active:
                return {"success": False, "error": "Account is deactivated"}
            
            if not self.verify_password(password, stored_hash):
                return {"success": False, "error": "Invalid email or password"}
            
            # Update last login
            self.update_last_login(user_uuid)
            
            return {
                "success": True,
                "user_uuid": user_uuid,
                "full_name": full_name,
                "email": email,
                "subscription_tier": tier,
                "subscription_status": status,
                "trial_ends": trial_ends
            }
            
        except Exception as e:
            return {"success": False, "error": f"Login failed: {str(e)}"}
    
    def update_last_login(self, user_uuid: str):
        """Update user's last login timestamp"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE user_uuid = ?",
                (datetime.now().isoformat(), user_uuid)
            )
            conn.commit()
            conn.close()
        except:
            pass
    
    def get_user_data(self, user_uuid: str) -> Dict[str, Any]:
        """Get complete user data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_uuid, email, full_name, company, phone, subscription_tier,
                       subscription_status, trial_started, trial_ends, created_at, last_login,
                       preferences, usage_stats
                FROM users WHERE user_uuid = ?
            ''', (user_uuid,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                columns = ['user_uuid', 'email', 'full_name', 'company', 'phone', 
                          'subscription_tier', 'subscription_status', 'trial_started', 
                          'trial_ends', 'created_at', 'last_login', 'preferences', 'usage_stats']
                
                user_data = dict(zip(columns, result))
                
                # Parse JSON fields
                try:
                    user_data['preferences'] = json.loads(user_data['preferences'] or '{}')
                    user_data['usage_stats'] = json.loads(user_data['usage_stats'] or '{}')
                except:
                    user_data['preferences'] = {}
                    user_data['usage_stats'] = {}
                
                return user_data
            
            return {}
            
        except Exception as e:
            st.error(f"Error loading user data: {str(e)}")
            return {}
    
    def create_session(self, user_uuid: str) -> str:
        """Create user session"""
        session_id = str(uuid.uuid4())
        expires_at = (datetime.now() + timedelta(days=30)).isoformat()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_sessions (session_id, user_uuid, expires_at)
                VALUES (?, ?, ?)
            ''', (session_id, user_uuid, expires_at))
            
            conn.commit()
            conn.close()
            
            return session_id
        except:
            return ""
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    def check_authentication(self) -> bool:
        """Check if user is authenticated - alias method"""
        return self.is_authenticated()
    
    def render_auth_interface(self):
        """Render authentication interface"""
        if 'authenticated' in st.session_state and st.session_state.authenticated:
            return st.session_state.user_data
        
        st.markdown("""
        <style>
        .auth-container {
            max-width: 400px;
            margin: 2rem auto;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
        }
        
        .auth-title {
            text-align: center;
            color: #ffffff;
            margin-bottom: 2rem;
            font-size: 28px;
            font-weight: 700;
        }
        
        .auth-subtitle {
            text-align: center;
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 2rem;
            font-size: 16px;
        }
        
        .plan-highlight {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            color: white;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
            
            with tab1:
                with st.form("login_form", clear_on_submit=True):
                    st.markdown('<div class="auth-title">Welcome Back</div>', unsafe_allow_html=True)
                    
                    email = st.text_input("📧 Email", placeholder="your@email.com")
                    password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                    
                    login_btn = st.form_submit_button("🚀 Sign In", use_container_width=True, type="primary")
                    
                    if login_btn and email and password:
                        result = self.authenticate_user(email, password)
                        
                        if result["success"]:
                            st.session_state.authenticated = True
                            st.session_state.user_data = result
                            st.session_state.session_id = self.create_session(result["user_uuid"])
                            st.success(f"Welcome back, {result['full_name']}!")
                            st.rerun()
                        else:
                            st.error(result["error"])
            
            with tab2:
                with st.form("signup_form", clear_on_submit=True):
                    st.markdown('<div class="auth-title">Start Your Journey</div>', unsafe_allow_html=True)
                    st.markdown('<div class="auth-subtitle">Join thousands of real estate professionals</div>', unsafe_allow_html=True)
                    
                    # Plan selection
                    selected_plan = st.selectbox("Choose Your Plan", 
                                               ["Starter ($89/month)", "Professional ($189/month)", "Enterprise ($349/month)"],
                                               index=1)
                    
                    # Plan descriptions
                    plan_descriptions = {
                        "Starter ($89/month)": "• 1,000 contacts • Unlimited deals • Email automation • Basic integrations • Email support",
                        "Professional ($189/month)": "• 10,000 contacts • Advanced analytics • Team collaboration • Voice AI features • Priority support",
                        "Enterprise ($349/month)": "• Unlimited contacts • AI-powered insights • White-label options • Custom integrations • 24/7 phone support"
                    }
                    
                    st.info(plan_descriptions[selected_plan])
                    
                    # User details
                    col1, col2 = st.columns(2)
                    with col1:
                        first_name = st.text_input("👤 First Name*", placeholder="John")
                        email = st.text_input("📧 Email*", placeholder="john@company.com")
                        password = st.text_input("🔒 Password*", type="password", placeholder="Strong password")
                    
                    with col2:
                        last_name = st.text_input("👤 Last Name*", placeholder="Smith")
                        company = st.text_input("🏢 Company", placeholder="Your Company")
                        confirm_password = st.text_input("🔒 Confirm Password*", type="password", placeholder="Repeat password")
                    
                    phone = st.text_input("📱 Phone", placeholder="+1 (555) 123-4567")
                    
                    # Terms and conditions
                    agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy*")
                    
                    signup_btn = st.form_submit_button("🚀 Start Free Trial", use_container_width=True, type="primary")
                    
                    if signup_btn:
                        if not all([first_name, last_name, email, password, confirm_password, agree_terms]):
                            st.error("Please fill in all required fields and accept the terms")
                        elif password != confirm_password:
                            st.error("Passwords do not match")
                        else:
                            full_name = f"{first_name} {last_name}"
                            tier = selected_plan.split()[0].lower()
                            
                            result = self.register_user(email, password, full_name, company, phone, tier)
                            
                            if result["success"]:
                                # Auto-login after registration
                                auth_result = self.authenticate_user(email, password)
                                if auth_result["success"]:
                                    st.session_state.authenticated = True
                                    st.session_state.user_data = auth_result
                                    st.session_state.session_id = self.create_session(auth_result["user_uuid"])
                                    st.success(f"Welcome to NXTRIX, {full_name}! Your 7-day trial has started.")
                                    st.rerun()
                            else:
                                st.error(result["error"])
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        return None
    
    def render_auth_page(self):
        """Render authentication page - main entry point"""
        if not self.is_authenticated():
            return self.render_auth_interface()
        return True
    
    @property
    def user_manager(self):
        """Get user manager instance"""
        return self
    
    def logout(self):
        """Logout current user"""
        if 'session_id' in st.session_state:
            # Invalidate session in database
            try:
                conn = sqlite3.connect("nxtrix_users.db")
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM user_sessions WHERE session_id = ?",
                    (st.session_state.session_id,)
                )
                conn.commit()
                conn.close()
            except Exception:
                pass
        
        # Clear session state
        for key in ['authenticated', 'user_data', 'session_id']:
            if key in st.session_state:
                del st.session_state[key]
        
        st.success("🔓 Logged out successfully!")
        st.rerun()
    
    def get_current_user(self):
        """Get current authenticated user data"""
        if 'authenticated' in st.session_state and st.session_state.authenticated:
            return st.session_state.get('user_data', {})
        return {}

# Global auth instance
auth = StreamlitAuth()

def require_auth(func):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        if 'authenticated' not in st.session_state or not st.session_state.authenticated:
            st.error("🔐 Authentication required")
            return auth.render_auth_interface()
        return func(*args, **kwargs)
    return wrapper

def get_current_user() -> Dict[str, Any]:
    """Get current authenticated user data"""
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        return st.session_state.get('user_data', {})
    return {}

def logout():
    """Logout current user"""
    if 'session_id' in st.session_state:
        # Invalidate session in database
        try:
            conn = sqlite3.connect("nxtrix_users.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE user_sessions SET is_active = 0 WHERE session_id = ?",
                (st.session_state.session_id,)
            )
            conn.commit()
            conn.close()
        except:
            pass
    
    # Clear session state
    for key in ['authenticated', 'user_data', 'session_id']:
        if key in st.session_state:
            del st.session_state[key]
    
    st.rerun()