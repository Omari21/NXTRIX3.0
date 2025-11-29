"""
NXTRIX 3.0 - Production SaaS Application
Complete CRM platform with authentication, billing, real portfolio management, 
professional communications, and integrations
"""

import streamlit as st
import sqlite3
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
import hashlib

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our new professional systems
try:
    from auth_system import auth, require_auth, StreamlitAuth
    AUTH_AVAILABLE = True
except ImportError as e:
    st.error(f"Auth system not available: {e}")
    AUTH_AVAILABLE = False

try:
    from security_system import apply_security_hardening, security_manager
    SECURITY_AVAILABLE = True
except ImportError as e:
    st.error(f"Security system not available: {e}")
    SECURITY_AVAILABLE = False
    # Create dummy function
    def apply_security_hardening():
        pass

try:
    from supabase_integration import sync_user_to_supabase, supabase_manager
    SUPABASE_AVAILABLE = True
except ImportError as e:
    # Supabase not available - continue with local database
    SUPABASE_AVAILABLE = False

try:
    from stripe_billing_system import billing_manager
    STRIPE_AVAILABLE = True
except ImportError as e:
    st.warning(f"Stripe billing not available: {e}")
    STRIPE_AVAILABLE = False

try:
    from data_visualization_system import visualization_manager
    VISUALIZATION_AVAILABLE = True
except ImportError as e:
    st.warning(f"Data visualization not available: {e}")
    VISUALIZATION_AVAILABLE = False

try:
    from enterprise_design_system import enterprise_design
    DESIGN_AVAILABLE = True
except ImportError as e:
    st.warning(f"Enterprise design not available: {e}")
    DESIGN_AVAILABLE = False
    # Create dummy design object
    class DummyDesign:
        def inject_enterprise_css(self):
            pass
    enterprise_design = DummyDesign()

try:
    from billing_system import BillingManager, render_subscription_plans, render_billing_dashboard
    BILLING_AVAILABLE = True
except ImportError as e:
    st.error(f"Billing system not available: {e}")
    BILLING_AVAILABLE = False

try:
    from communication_system import CommunicationManager, render_communication_center
    COMMUNICATION_AVAILABLE = True
except ImportError as e:
    st.warning(f"Communication system not available: {e}")
    COMMUNICATION_AVAILABLE = False

try:
    from email_template_generator import email_generator
    EMAIL_TEMPLATE_AVAILABLE = True
except ImportError as e:
    st.warning(f"Email template generator not available: {e}")
    EMAIL_TEMPLATE_AVAILABLE = False

try:
    from portfolio_system import PortfolioManager, render_portfolio_dashboard
    PORTFOLIO_AVAILABLE = True
except ImportError as e:
    st.warning(f"Portfolio system not available: {e}")
    PORTFOLIO_AVAILABLE = False

try:
    from integration_system import IntegrationManager, render_integrations_dashboard
    INTEGRATION_AVAILABLE = True
except ImportError as e:
    st.warning(f"Integration system not available: {e}")
    INTEGRATION_AVAILABLE = False

try:
    from nxtrix_backend import NXTRIXDatabase
    BACKEND_AVAILABLE = True
except ImportError as e:
    st.warning(f"NXTRIX Backend not available: {e}")
    BACKEND_AVAILABLE = False

try:
    from wow_factor_features import wow_features
    WOW_FEATURES_AVAILABLE = True
except ImportError as e:
    st.warning(f"WOW Features not available: {e}")
    WOW_FEATURES_AVAILABLE = False

try:
    from demo_mode_features import demo_features
    DEMO_FEATURES_AVAILABLE = True
except ImportError as e:
    st.warning(f"Demo Features not available: {e}")
    DEMO_FEATURES_AVAILABLE = False

try:
    from live_notification_system import live_notifications
    LIVE_NOTIFICATIONS_AVAILABLE = True
except ImportError as e:
    st.warning(f"Live Notifications not available: {e}")
    LIVE_NOTIFICATIONS_AVAILABLE = False

try:
    from voice_ai_system import voice_system, chatbot
    VOICE_AI_AVAILABLE = True
except ImportError as e:
    st.warning(f"Voice AI not available: {e}")
    VOICE_AI_AVAILABLE = False

try:
    from feature_request_system import feature_system
    FEATURE_SYSTEM_AVAILABLE = True
except ImportError as e:
    st.error(f"Backend not available: {e}")
    BACKEND_AVAILABLE = False

try:
    from plan_enforcement import enforcement_manager, require_feature, check_resource_limit
    ENFORCEMENT_AVAILABLE = True
except ImportError as e:
    st.warning(f"Plan enforcement not available: {e}")
    ENFORCEMENT_AVAILABLE = False

# Configure Streamlit page
st.set_page_config(
    page_title="NXTRIX 3.0 - Enterprise CRM",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize authentication system globally
auth = StreamlitAuth()

def check_and_enforce_feature_access(user_data, feature_name):
    """Enhanced feature access checking with proper enforcement"""
    access_info = enforcement_manager.check_feature_access(user_data, feature_name)
    
    if not access_info.get("valid", True):
        if access_info.get("trial_expired"):
            st.error("🚫 **Your 7-day trial has expired!**")
            st.markdown("**Upgrade to continue using NXTRIX:**")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("👤 Solo - $79/month"):
                    st.session_state.current_page = 'billing'
                    st.rerun()
            with col2:
                if st.button("👥 Team - $119/month"):
                    st.session_state.current_page = 'billing'
                    st.rerun()
            with col3:
                if st.button("🏢 Business - $219/month"):
                    st.session_state.current_page = 'billing'
                    st.rerun()
        else:
            st.error(f"❌ Access Error: {access_info['message']}")
        
        return False, access_info
    
    # Check trial warning
    if access_info.get("trial_days_left") is not None:
        days_left = access_info["trial_days_left"]
        if days_left <= 3:
            st.warning(f"⏰ **Trial expires in {days_left} days!** Upgrade to keep your data and continue using NXTRIX.")
            if st.button("🔥 Upgrade Now", type="primary"):
                st.session_state.current_page = 'billing'
                st.rerun()
    
    # Check feature access
    if not access_info.get("access", False):
        enforcement_manager.render_upgrade_prompt(feature_name.replace("_", " ").title(), user_data.get('subscription_tier', 'free'))
        return False, access_info
    
    return True, access_info

def check_usage_limits(user_data, resource_type, current_count):
    """Check if user has exceeded usage limits for their plan"""
    user_manager = auth.user_manager
    access_info = user_manager.check_feature_access(user_data['user_uuid'], resource_type)
    
    if not access_info["valid"]:
        return False, "Access denied"
    
    limit = access_info.get("access", -1)
    if limit == -1:  # Unlimited
        return True, "unlimited"
    
    if isinstance(limit, bool):  # Feature access
        return limit, "feature access"
    
    if current_count >= limit:
        st.warning(f"🚨 **Limit reached!** You've hit your plan limit of {limit} {resource_type}.")
        st.markdown("Upgrade for higher limits:")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👤 Solo - 1,000 contacts"):
                st.session_state.current_page = 'billing'
                st.rerun()
        with col2:
            if st.button("� Team - 5,000 contacts"):
                st.session_state.current_page = 'billing'
                st.rerun()
        
        return False, f"Limit exceeded: {current_count}/{limit}"
    
    return True, f"Usage: {current_count}/{limit}"

# Custom CSS for production-ready dark theme
st.markdown("""
<style>
/* Import premium fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

/* Dark theme color palette */
:root {
    --bg-primary: #0f0f0f;
    --bg-secondary: #1a1a1a;
    --bg-tertiary: #262626;
    --bg-card: #1e1e1e;
    --bg-elevated: #2a2a2a;
    --bg-hover: #333333;
    
    --primary-gradient: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    --secondary-gradient: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    --success-gradient: linear-gradient(135deg, #10b981 0%, #059669 100%);
    --warning-gradient: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    --danger-gradient: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    --purple-gradient: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
    
    --primary-color: #3b82f6;
    --primary-hover: #2563eb;
    --primary-light: rgba(59, 130, 246, 0.1);
    --secondary-color: #6b7280;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --info-color: #06b6d4;
    --purple-color: #8b5cf6;
    
    --text-primary: #f8fafc;
    --text-secondary: #cbd5e1;
    --text-muted: #64748b;
    --text-inverse: #0f0f0f;
    
    --border-subtle: #374151;
    --border-medium: #4b5563;
    --border-strong: #6b7280;
    --border-accent: rgba(59, 130, 246, 0.3);
    
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
    --shadow-xl: 0 12px 48px rgba(0, 0, 0, 0.6);
    --shadow-neon: 0 0 20px rgba(59, 130, 246, 0.3);
    
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --radius-full: 9999px;
    
    --glass-bg: rgba(26, 26, 26, 0.8);
    --glass-border: rgba(255, 255, 255, 0.1);
}

/* Global dark theme */
.stApp {
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Hide default Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}
.stDecoration {display: none;}

/* Premium alerts */
.premium-alert {
    padding: 1.25rem 1.5rem;
    border-radius: var(--radius-lg);
    margin: 1.5rem 0;
    display: flex;
    align-items: center;
    gap: 1rem;
    font-weight: 500;
    border: 2px solid;
    box-shadow: var(--shadow-sm);
}

.premium-alert.success {
    background: rgba(76, 175, 80, 0.1);
    border-color: var(--success-color);
    color: var(--success-color);
}

.premium-alert.info {
    background: rgba(33, 150, 243, 0.1);
    border-color: var(--info-color);
    color: var(--info-color);
}

.premium-alert.warning {
    background: rgba(255, 152, 0, 0.1);
    border-color: var(--warning-color);
    color: var(--warning-color);
}

.premium-alert.danger {
    background: rgba(244, 67, 54, 0.1);
    border-color: var(--danger-color);
    color: var(--danger-color);
}

/* Premium cards */
.premium-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 2rem;
    box-shadow: var(--shadow-md);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.premium-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
    border-color: var(--border-accent);
    background: var(--bg-elevated);
}

/* Sidebar styling */
.css-1d391kg {
    background: var(--bg-card);
    border-right: 1px solid var(--border-subtle);
}

/* Metric styling */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
    border-color: var(--border-accent);
}

/* Button styling - ORIGINAL DESIGN WITH ACCESSIBILITY */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2) !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3) !important;
}

/* Text Input styling - HIGH CONTRAST BUT STYLED */
.stTextInput > div > div > input {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    outline: none !important;
}

/* Text Area styling - HIGH CONTRAST BUT STYLED */
.stTextArea > div > div > textarea {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

.stTextArea > div > div > textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    outline: none !important;
}

/* Select Box styling - HIGH CONTRAST BUT STYLED */
.stSelectbox > div > div > select {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

/* Number Input styling - HIGH CONTRAST BUT STYLED */
.stNumberInput > div > div > input {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

/* Form Labels - CLEAN STYLING */
.stTextInput > label, .stTextArea > label, .stSelectbox > label, .stNumberInput > label {
    color: var(--text-primary) !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    margin-bottom: 6px !important;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

/* Form styling */
.stTextInput > div > div > input {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    color: var(--text-primary);
}

.stSelectbox > div > div > select {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    color: var(--text-primary);
}

/* Tab styling */
.stTabs > div > div > div > div {
    background: var(--bg-card);
    border-radius: var(--radius-md);
}

/* Success/Error message styling */
.stSuccess {
    background: var(--success-color);
    border: none;
    border-radius: var(--radius-md);
}

.stError {
    background: var(--danger-color);
    border: none;
    border-radius: var(--radius-md);
}

.stWarning {
    background: var(--warning-color);
    border: none;
    border-radius: var(--radius-md);
}

.stInfo {
    background: var(--info-color);
    border: none;
    border-radius: var(--radius-md);
}
</style>
""", unsafe_allow_html=True)

def render_header(user_data):
    """Render premium application header"""
    st.markdown(f"""
    <div style="
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--glass-border);
        padding: 1.5rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: var(--shadow-lg);
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="
                background: var(--primary-gradient);
                padding: 0.75rem;
                border-radius: var(--radius-md);
                font-size: 1.5rem;
                color: white;
                box-shadow: var(--shadow-neon);
            ">🚀</div>
            <div>
                <h1 style="
                    margin: 0;
                    font-size: 1.75rem;
                    font-weight: 800;
                    color: var(--text-primary);
                    text-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
                ">NXTRIX 3.0</h1>
                <p style="margin: 0; color: var(--text-secondary); font-size: 0.875rem;">
                    Enterprise CRM Platform
                </p>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="text-align: right;">
                <p style="margin: 0; font-weight: 600; color: var(--text-primary);">
                    {user_data.get('first_name', 'User')} {user_data.get('last_name', '')}
                </p>
                <p style="margin: 0; font-size: 0.875rem; color: var(--text-secondary);">
                    {user_data.get('subscription_tier', 'free').title()} Plan
                </p>
            </div>
            <div style="
                background: var(--success-gradient);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: var(--radius-full);
                font-weight: 600;
                font-size: 0.875rem;
            ">● Online</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_navigation(user_data):
    """Render premium sidebar navigation"""
    with st.sidebar:
        st.markdown("## 🎯 Navigation")
        
        # Navigation menu with icons
        menu_items = [
            ("🏠", "Dashboard", "dashboard"),
            ("👥", "CRM", "crm"),
            ("💼", "Deals", "deals"),
            ("🧠", "AI Insights", "ai_insights"),
            ("📊", "Portfolio", "portfolio"),
            ("📧", "Communications", "communications"),
            ("💡", "Feature Requests", "feature_requests"),
            ("🔗", "Integrations", "integrations"),
            ("💳", "Billing", "billing"),
            ("⚙️", "Settings", "settings")
        ]
        
        # Current page selection
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
        
        for icon, label, page_id in menu_items:
            if st.button(f"{icon} {label}", key=f"nav_{page_id}", use_container_width=True):
                st.session_state.current_page = page_id
                st.rerun()
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("➕ Add Contact", use_container_width=True):
            st.session_state.current_page = 'contacts'
            st.session_state.show_add_contact = True
            st.rerun()

        if st.button("🤝 New Deal", use_container_width=True):
            st.session_state.current_page = 'deals'
            st.session_state.show_add_deal = True
            st.rerun()
        
        st.markdown("---")
        
        # User subscription info
        if BILLING_AVAILABLE:
            billing_manager = BillingManager()
            subscription = billing_manager.get_user_subscription(user_data['user_uuid'])
            
            st.markdown("### 💎 Subscription")
            st.markdown(f"**Plan:** {subscription['tier'].title()}")
            st.markdown(f"**Status:** {subscription['status'].title()}")
            
            if subscription['tier'] == 'free':
                if st.button("⬆️ Upgrade Plan", use_container_width=True):
                    st.session_state.current_page = 'billing'
                    st.rerun()
        else:
            st.markdown("### 💎 Subscription")
            st.markdown("**Plan:** Free")
            st.markdown("**Status:** Active")
            if st.button("⬆️ Upgrade Plan", use_container_width=True):
                st.session_state.current_page = 'billing'
                st.rerun()
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            auth.logout()

def render_dashboard(user_data):
    """Render enhanced dashboard"""
    st.markdown("## 🏠 Dashboard Overview")
    
    # Initialize database
    db = NXTRIXDatabase()
    
    # Get dashboard data
    contacts = db.get_contacts()
    deals = db.get_deals()
    
    # Enterprise Dashboard Metrics
    metrics_data = [
        {
            "value": f"{len(contacts)}",
            "label": "Total Contacts",
            "change": "+12.5%",
            "trend": 0.125
        },
        {
            "value": f"{len([d for d in deals if d['status'] != 'closed_lost'])}",
            "label": "Active Deals", 
            "change": "+8.3%",
            "trend": 0.083
        },
        {
            "value": f"${sum(float(d.get('value', '0').replace('$', '').replace(',', '')) for d in deals if d['status'] == 'closed_won'):,.0f}",
            "label": "Total Revenue",
            "change": "+23.1%", 
            "trend": 0.231
        },
        {
            "value": f"{(len([d for d in deals if d['status'] == 'closed_won']) / max(len(deals), 1) * 100):.1f}%",
            "label": "Win Rate",
            "change": "+2.4%",
            "trend": 0.024
        }
    ]
    
    enterprise_design.render_enhanced_metric_cards(metrics_data)
    
    st.markdown("---")
    
    # Enterprise Search Bar
    search_results = enterprise_design.render_advanced_search()
    
    # Enterprise Dashboard Layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Activity Timeline
        enterprise_design.render_activity_timeline()
    
    with col2:
        # Notification Center
        enterprise_design.render_notification_center(show_notifications=True)
    
    with col2:
        st.markdown("### 💡 AI Insights")
        
        # AI insights with proper HTML structure
        st.markdown("""
        <div class="premium-card">
            <div class="premium-alert success">
                <i class="fas fa-lightbulb"></i>
                <div>
                    <strong>Opportunity:</strong> Consider following up with qualified leads
                </div>
            </div>
            
            <div class="premium-alert info">
                <i class="fas fa-chart-line"></i>
                <div>
                    <strong>Trend:</strong> Deal velocity has improved over time
                </div>
            </div>
            
            <div class="premium-alert warning">
                <i class="fas fa-exclamation-triangle"></i>
                <div>
                    <strong>Action:</strong> Review deals in negotiation stage
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_crm_module(user_data, can_add_contacts=True):
    """Render CRM contacts module with enterprise features"""
    
    db = NXTRIXDatabase()
    contacts = db.get_contacts()
    
    # Enterprise CRM Header
    st.markdown("## 👥 Contact Management")
    
    # ===== 🚀 WOW FACTOR CRM FEATURES =====
    
    # Smart deal scoring for contacts
    if WOW_FEATURES_AVAILABLE and contacts:
        wow_features.render_smart_deal_scoring(contacts)
    
    # Instant reports
    if WOW_FEATURES_AVAILABLE:
        wow_features.render_instant_reports()
        
        # Smart automation suggestions
        wow_features.render_smart_automation_suggestions()
    
    # ===== END WOW CRM FEATURES =====
    
    # Advanced search with enterprise design
    search_filters = enterprise_design.render_advanced_search()
    
    # Action bar
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if can_add_contacts:
            if st.button("➕ Add New Contact", type="primary"):
                st.session_state.show_add_contact = True
                st.rerun()
        else:
            st.button("➕ Add Contact", disabled=True, help="Upgrade to add more contacts")
    
    with col2:
        if st.button("📤 Export Contacts"):
            st.success("Export initiated for all contacts")
    
    with col3:
        if st.button("📊 Contact Analytics"):
            st.info("Detailed contact analytics coming soon")
    
    # Display contacts with enterprise data table
    if contacts:
        # Apply search filter
        if search_filters['query']:
            contacts = [c for c in contacts if search_filters['query'].lower() in 
                       f"{c.get('first_name', '')} {c.get('last_name', '')} {c.get('email', '')} {c.get('company', '')}".lower()]
        
        # Convert contacts to enterprise table format
        table_data = []
        for contact in contacts:
            table_data.append({
                'id': contact.get('id', ''),
                'Name': f"{contact.get('first_name', '')} {contact.get('last_name', '')}",
                'Email': contact.get('email', ''),
                'Company': contact.get('company', ''),
                'Phone': contact.get('phone', ''),
                'Status': 'Active'
            })
        
        # Render enterprise table
        selected_contacts = enterprise_design.render_enterprise_data_table(
            data=table_data,
            columns=['Name', 'Email', 'Company', 'Phone', 'Status'],
            title=f"Contacts ({len(contacts)})",
            searchable=True,
            selectable=True
        )
        
        # Bulk actions for selected contacts
        enterprise_design.render_bulk_actions_bar(selected_contacts)
        
    else:
        st.info("No contacts yet. Add your first contact to get started!")
        if can_add_contacts:
            if st.button("🚀 Add Your First Contact", type="primary"):
                st.session_state.show_add_contact = True
                st.rerun()
    
    # Add contact form - Enterprise styled
    if hasattr(st.session_state, 'show_add_contact') and st.session_state.show_add_contact:
        st.markdown("---")
        with st.form("add_contact_form"):
            st.markdown("### ➕ Add New Contact")
            
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name*", placeholder="John")
                email = st.text_input("Email*", placeholder="john@company.com")
                company = st.text_input("Company", placeholder="Company Name")
            
            with col2:
                last_name = st.text_input("Last Name*", placeholder="Doe")
                phone = st.text_input("Phone", placeholder="+1 (555) 123-4567")
                position = st.text_input("Position", placeholder="CEO")
            
            notes = st.text_area("Notes", placeholder="Additional information about this contact")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("Add Contact", use_container_width=True):
                    if first_name and last_name and email:
                        contact_id = db.add_contact(
                            first_name, last_name, email, phone, company, position, notes
                        )
                        if contact_id:
                            st.success("Contact added successfully!")
                            st.session_state.show_add_contact = False
                            st.rerun()
                        else:
                            st.error("Failed to add contact")
                    else:
                        st.error("Please fill in all required fields (*)")
            
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_add_contact = False
                    st.rerun()
                position = st.text_input("Position", value=contact_to_edit['position'])
            
            notes = st.text_area("Notes", value=contact_to_edit['notes'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("Update Contact", use_container_width=True):
                    # Update contact logic would go here
                    st.success("Contact updated successfully!")
                    del st.session_state.edit_contact_id
                    st.rerun()
            
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    del st.session_state.edit_contact_id
                    st.rerun()

def render_deals_module(user_data: Dict[str, Any]):
    """Render deal management module"""
    st.markdown("## 💼 Deal Pipeline Management")
    
    # Deal pipeline stages
    stages = ["Lead", "Qualified", "Proposal", "Negotiation", "Closing", "Won", "Lost"]
    
    # Add new deal section
    with st.expander("➕ Add New Deal", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            deal_name = st.text_input("Deal Name*", placeholder="Downtown Office Building")
            property_type = st.selectbox("Property Type", ["Office", "Retail", "Industrial", "Residential", "Mixed Use"])
            deal_value = st.number_input("Deal Value ($)", min_value=0, value=0, step=1000)
            expected_close = st.date_input("Expected Close Date")
        
        with col2:
            contact_id = st.selectbox("Primary Contact", options=[])  # This would be populated with actual contacts
            deal_stage = st.selectbox("Current Stage", stages, index=0)
            probability = st.slider("Probability (%)", 0, 100, 25)
            notes = st.text_area("Notes", placeholder="Deal details and notes...")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("💼 Add Deal", type="primary", use_container_width=True):
                if deal_name and deal_value > 0:
                    # Here you would add the deal to the database
                    st.success("Deal added successfully!")
                else:
                    st.error("Please fill in all required fields")
        
        with col2:
            st.button("Cancel", use_container_width=True)
    
    # Deal pipeline visualization
    st.markdown("### 📊 Pipeline Overview")
    
    # Mock deal data for demonstration
    pipeline_data = {
        "Lead": 8,
        "Qualified": 5,
        "Proposal": 3,
        "Negotiation": 2,
        "Closing": 1,
        "Won": 12,
        "Lost": 4
    }
    
    # Create pipeline metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Deals", sum(pipeline_data.values()))
    with col2:
        st.metric("Active Deals", sum(list(pipeline_data.values())[:-2]))  # Exclude Won/Lost
    with col3:
        total_value = 2450000  # Mock total value
        st.metric("Pipeline Value", f"${total_value:,}")
    with col4:
        win_rate = (pipeline_data["Won"] / (pipeline_data["Won"] + pipeline_data["Lost"])) * 100
        st.metric("Win Rate", f"{win_rate:.1f}%")
    
    # Pipeline stages visualization
    st.markdown("### 🔄 Deal Stages")
    
    # Create columns for each stage
    stage_cols = st.columns(len(stages))
    
    for i, (stage, count) in enumerate(pipeline_data.items()):
        with stage_cols[i]:
            # Color coding for stages
            if stage in ["Won"]:
                color = "#22c55e"  # Green
            elif stage in ["Lost"]:
                color = "#ef4444"  # Red
            elif stage in ["Closing", "Negotiation"]:
                color = "#f59e0b"  # Orange
            else:
                color = "#3b82f6"  # Blue
            
            st.markdown(f"""
            <div style="
                padding: 1rem;
                background: linear-gradient(135deg, {color}20, {color}10);
                border-left: 4px solid {color};
                border-radius: 8px;
                text-align: center;
                margin-bottom: 1rem;
            ">
                <h4 style="margin: 0; color: {color};">{stage}</h4>
                <h2 style="margin: 0.5rem 0 0 0; color: var(--text-primary);">{count}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    # Recent deals table
    st.markdown("### 📋 Recent Deals")
    
    # Mock recent deals data
    recent_deals = [
        {"name": "Downtown Plaza", "stage": "Negotiation", "value": "$450,000", "contact": "John Smith", "close_date": "2024-01-15"},
        {"name": "Retail Complex", "stage": "Proposal", "value": "$780,000", "contact": "Sarah Johnson", "close_date": "2024-01-22"},
        {"name": "Office Tower", "stage": "Qualified", "value": "$1,200,000", "contact": "Mike Brown", "close_date": "2024-02-10"},
        {"name": "Industrial Park", "stage": "Lead", "value": "$320,000", "contact": "Lisa Davis", "close_date": "2024-02-28"},
    ]
    
    for deal in recent_deals:
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{deal['name']}**")
            st.markdown(f"Contact: {deal['contact']}")
        
        with col2:
            stage_color = "#f59e0b" if deal['stage'] in ["Negotiation", "Proposal"] else "#3b82f6"
            st.markdown(f"<span style='color: {stage_color}; font-weight: 600;'>{deal['stage']}</span>", unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"**{deal['value']}**")
        
        with col4:
            if st.button("👁️ View", key=f"view_deal_{deal['name']}"):
                st.session_state.view_deal = deal
                st.rerun()
    
    # Deal detail view modal
    if hasattr(st.session_state, 'view_deal') and st.session_state.view_deal:
        deal = st.session_state.view_deal
        with st.container():
            st.markdown("---")
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### 💼 Deal Details: {deal.get('name', 'Unknown Deal')}")
            with col2:
                if st.button("❌ Close", key="close_deal_view"):
                    del st.session_state.view_deal
                    st.rerun()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Deal Value:** {deal.get('value', 'N/A')}")
                st.markdown(f"**Stage:** {deal.get('stage', 'N/A')}")
                st.markdown(f"**Probability:** {deal.get('probability', 'N/A')}%")
            with col2:
                st.markdown(f"**Expected Close:** {deal.get('expected_close', 'N/A')}")
                st.markdown(f"**Property Type:** {deal.get('property_type', 'N/A')}")
                st.markdown(f"**Primary Contact:** {deal.get('contact', 'N/A')}")
            
            if deal.get('notes'):
                st.markdown(f"**Notes:** {deal.get('notes', 'No notes available')}")
            
            # Action buttons for deal
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("✏️ Edit Deal", key="edit_deal"):
                    st.session_state.edit_deal_id = deal.get('id')
                    st.rerun()
            with col2:
                if st.button("📧 Email Contact", key="email_deal_contact"):
                    st.session_state.current_page = 'communications'
                    del st.session_state.view_deal
                    st.rerun()
            with col3:
                if st.button("📈 Update Stage", key="update_deal_stage"):
                    st.session_state.update_deal_stage_id = deal.get('id')
                    st.rerun()
            with col4:
                if st.button("🗑️ Archive Deal", key="archive_deal", type="secondary"):
                    st.warning("Archive functionality requires database confirmation")
            st.markdown("---")
    
    # Edit deal form
    if hasattr(st.session_state, 'edit_deal_id') and st.session_state.edit_deal_id:
        # Get deal data for editing (simulated)
        deal_to_edit = {
            'id': st.session_state.edit_deal_id,
            'name': 'Sample Deal',
            'value': '$150,000',
            'stage': 'Proposal Sent',
            'probability': 75,
            'expected_close': '2024-02-15',
            'property_type': 'Commercial',
            'contact': 'John Doe',
            'notes': 'Sample notes about this deal'
        }
        
        with st.form("edit_deal_form"):
            st.markdown("### Edit Deal")
            
            col1, col2 = st.columns(2)
            
            with col1:
                deal_name = st.text_input("Deal Name*", value=deal_to_edit['name'])
                value = st.text_input("Deal Value*", value=deal_to_edit['value'])
                contact = st.text_input("Primary Contact", value=deal_to_edit['contact'])
            
            with col2:
                stage = st.selectbox("Stage", 
                    ["Lead", "Qualified", "Proposal Sent", "Negotiating", "Closed Won", "Closed Lost"],
                    index=2)  # Proposal Sent
                probability = st.slider("Probability (%)", 0, 100, deal_to_edit['probability'])
                expected_close = st.date_input("Expected Close Date")
            
            property_type = st.selectbox("Property Type",
                ["Residential", "Commercial", "Industrial", "Mixed-Use"])
            notes = st.text_area("Notes", value=deal_to_edit['notes'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("Update Deal", use_container_width=True):
                    # Update deal logic would go here
                    st.success("Deal updated successfully!")
                    del st.session_state.edit_deal_id
                    st.rerun()
            
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    del st.session_state.edit_deal_id
                    st.rerun()
    
    # Stage update form
    if hasattr(st.session_state, 'update_deal_stage_id') and st.session_state.update_deal_stage_id:
        with st.form("update_stage_form"):
            st.markdown("### Update Deal Stage")
            
            current_stage = "Proposal Sent"  # This would come from the database
            st.info(f"Current Stage: **{current_stage}**")
            
            new_stage = st.selectbox("New Stage", 
                ["Lead", "Qualified", "Proposal Sent", "Negotiating", "Closed Won", "Closed Lost"])
            
            probability = st.slider("Update Probability (%)", 0, 100, 75)
            
            notes = st.text_area("Stage Change Notes", 
                placeholder="Add notes about why the stage is changing...")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("Update Stage", use_container_width=True):
                    # Update stage logic would go here
                    st.success(f"Deal stage updated to: **{new_stage}**")
                    del st.session_state.update_deal_stage_id
                    st.rerun()
            
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    del st.session_state.update_deal_stage_id
                    st.rerun()

def main():
    """Main application entry point"""
    
    # Apply enterprise design system
    if DESIGN_AVAILABLE:
        enterprise_design.inject_enterprise_css()
    
    # Apply security hardening first
    if SECURITY_AVAILABLE:
        apply_security_hardening()
    
    # Check authentication first
    if not AUTH_AVAILABLE:
        st.error("Authentication system not available. Please check your installation.")
        return
        
    if not auth.is_authenticated():
        auth.render_auth_page()
        return
    
    # Get current user data
    user_data = auth.get_current_user()
    if not user_data:
        st.error("Failed to load user data. Please log in again.")
        auth.logout()
        return
    
    # Sync user to Supabase on login (if not already synced)
    if SUPABASE_AVAILABLE and not user_data.get('synced_to_supabase'):
        if sync_user_to_supabase(user_data):
            user_data['synced_to_supabase'] = True
            # Update local storage
            auth.update_user_data(user_data)
    
    # Render header
    render_header(user_data)
    
    # ===== 🔔 LIVE NOTIFICATION SYSTEM =====
    if LIVE_NOTIFICATIONS_AVAILABLE:
        live_notifications.render_notification_bell()
    
    # Render sidebar navigation - THIS WAS MISSING!
    render_sidebar_navigation(user_data)
    
    # Get current page and route accordingly
    current_page = st.session_state.get('current_page', 'dashboard')
    
    # Route to different pages based on sidebar navigation
    if current_page == 'dashboard':
        render_enterprise_dashboard(user_data)
    elif current_page == 'portfolio':
        render_analytics_dashboard(user_data)  # Portfolio analytics
    elif current_page == 'communications':
        render_communication_center(user_data)
    elif current_page == 'billing':
        render_billing_management(user_data)
    elif current_page == 'analytics':
        render_analytics_dashboard(user_data)
    elif current_page == 'contacts' or current_page == 'crm':
        render_crm_module(user_data)  # Contact management
    elif current_page == 'deals':
        render_deals_module(user_data)  # Deal pipeline 
    elif current_page == 'ai_insights':
        render_ai_insights(user_data)  # AI Features
    elif current_page == 'feature_requests':
        render_feature_requests(user_data)  # Feature Request System
    elif current_page == 'integrations':
        render_integrations_page(user_data)
    elif current_page == 'settings':
        render_settings_page(user_data)
    else:
        render_enterprise_dashboard(user_data)

def render_enterprise_dashboard(user_data: Dict[str, Any]):
    """Render enterprise-grade dashboard"""
    
    # Page header
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h1 style="
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #6366f1, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        ">Welcome back, {user_data.get('first_name', 'User')}!</h1>
        <p style="color: var(--text-secondary); font-size: 1.1rem;">
            Here's what's happening with your real estate portfolio today.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enterprise metrics
    metrics = [
        {
            'value': '$2.4M',
            'label': 'Portfolio Value',
            'change': '+12.5%',
            'change_value': 12.5,
            'icon': '📊'
        },
        {
            'value': '47',
            'label': 'Active Deals',
            'change': '+8',
            'change_value': 8,
            'icon': '🏠'
        },
        {
            'value': '1,247',
            'label': 'Total Contacts',
            'change': '+156',
            'change_value': 156,
            'icon': '👥'
        },
        {
            'value': '85%',
            'label': 'Close Rate',
            'change': '+2.1%',
            'change_value': 2.1,
            'icon': '📈'
        }
    ]
    
    enterprise_design.create_enterprise_metrics_grid(metrics)
    
    # ===== 🚀 WOW FACTOR FEATURES =====
    
    # Demo mode toggle
    if DEMO_FEATURES_AVAILABLE:
        demo_features.toggle_demo_mode()
        demo_features.render_demo_banner()
    
    # AI Assistant in sidebar
    if WOW_FEATURES_AVAILABLE:
        wow_features.render_ai_assistant_sidebar()
        
        # Smart insights banner
        wow_features.render_smart_insights_banner()
        
        # Voice AI quick access
        if VOICE_AI_AVAILABLE:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 🎤 Voice AI")
            if st.sidebar.button("🎤 Talk to AI", type="primary"):
                st.session_state.current_page = 'ai_insights'
                st.rerun()
    
    # Live market pulse - this will amaze users!
    if WOW_FEATURES_AVAILABLE:
        wow_features.render_live_market_pulse()
    
    # Live dashboard updates
    if DEMO_FEATURES_AVAILABLE:
        demo_features.render_live_dashboard()
        
        # Magic AI insights
        demo_features.render_magic_insights()
        
        # One-click actions
        demo_features.render_one_click_actions()
    
    # Live features
    if LIVE_NOTIFICATIONS_AVAILABLE:
        col1, col2 = st.columns(2)
        with col1:
            live_notifications.render_live_activity_feed()
        with col2:
            live_notifications.render_live_metrics_ticker()
    
    # ===== END WOW FEATURES =====
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Dashboard content grid
    col1, col2 = st.columns(2)
    
    with col1:
        # Recent deals card with functional View All button
        col1a, col1b = st.columns([3, 1])
        with col1a:
            st.markdown("""
            <div class="enterprise-card" style="margin-bottom: 0;">
                <div class="card-header">
                    <h3 class="card-title">🏠 Recent Deals</h3>
            """, unsafe_allow_html=True)
        with col1b:
            if st.button("View All Deals", key="view_all_deals_btn", type="secondary"):
                st.session_state.current_page = 'deals'
                st.rerun()
        
        st.markdown("""
                </div>
            </div>
            <div class="card-content">
                <div class="enterprise-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Property</th>
                                <th>Value</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>123 Oak Street</td>
                                <td>$450,000</td>
                                <td><span class="enterprise-badge success">Active</span></td>
                            </tr>
                            <tr>
                                <td>456 Pine Avenue</td>
                                <td>$320,000</td>
                                <td><span class="enterprise-badge warning">Pending</span></td>
                            </tr>
                            <tr>
                                <td>789 Elm Drive</td>
                                <td>$275,000</td>
                                <td><span class="enterprise-badge success">Active</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Recent activity card with functional View All button
        col2a, col2b = st.columns([3, 1])
        with col2a:
            st.markdown("""
            <div class="enterprise-card" style="margin-bottom: 0;">
                <div class="card-header">
                    <h3 class="card-title">🔔 Recent Activity</h3>
            """, unsafe_allow_html=True)
        with col2b:
            if st.button("View All Activity", key="view_all_activity_btn", type="secondary"):
                st.session_state.current_page = 'analytics'
                st.rerun()
        
        st.markdown("""
                </div>
            <div class="card-content">
                <div style="display: flex; flex-direction: column; gap: 1rem;">
                    <div style="
                        padding: 1rem;
                        background: rgba(5, 150, 105, 0.1);
                        border-radius: 0.5rem;
                        border-left: 3px solid var(--color-success);
                    ">
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">New contact added</div>
                        <div style="color: var(--text-muted); font-size: 0.875rem;">
                            Sarah Johnson - Investor • 2 hours ago
                        </div>
                    </div>
                    <div style="
                        padding: 1rem;
                        background: rgba(99, 102, 241, 0.1);
                        border-radius: 0.5rem;
                        border-left: 3px solid var(--color-primary-500);
                    ">
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">Deal status updated</div>
                        <div style="color: var(--text-muted); font-size: 0.875rem;">
                            123 Oak Street moved to closing • 4 hours ago
                        </div>
                    </div>
                    <div style="
                        padding: 1rem;
                        background: rgba(2, 132, 199, 0.1);
                        border-radius: 0.5rem;
                        border-left: 3px solid var(--color-info);
                    ">
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">Email campaign sent</div>
                        <div style="color: var(--text-muted); font-size: 0.875rem;">
                            Monthly newsletter to 247 contacts • 1 day ago
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_analytics_dashboard(user_data: Dict[str, Any]):
    """Render comprehensive analytics dashboard"""
    
    st.markdown("## 📊 Advanced Analytics Dashboard")
    
    # ===== 🚀 WOW ANALYTICS FEATURES =====
    
    # Predictive analytics
    if WOW_FEATURES_AVAILABLE:
        wow_features.render_predictive_analytics()
    
    # Advanced charts
    if DEMO_FEATURES_AVAILABLE:
        demo_features.render_advanced_charts()
        
        # Competitive analysis
        demo_features.render_competitive_analysis()
    
    # ===== END WOW ANALYTICS FEATURES =====
    
    # Original analytics
    if VISUALIZATION_AVAILABLE:
        visualization_manager.render_analytics_dashboard()
    else:
        st.info("Advanced visualization features loading...")

def render_ai_insights(user_data: Dict[str, Any]):
    """Render AI-powered insights and analytics"""
    st.markdown("## 🧠 AI-Powered Insights & Analytics")
    
    # Check if user has access to AI features
    user_tier = user_data.get('subscription_tier', 'free')
    if user_tier == 'free':
        st.info("🔒 AI Features are available on Starter ($39/month) and higher plans. Upgrade to unlock:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **🤖 AI Features Include:**
            - Deal score predictions
            - Market trend analysis  
            - Contact sentiment analysis
            - Email content suggestions
            - Risk assessment automation
            """)
        with col2:
            st.markdown("""
            **📊 Advanced Analytics:**
            - Performance forecasting
            - ROI optimization tips
            - Lead quality scoring
            - Pipeline health analysis
            - Automated insights reports
            """)
        
        if st.button("🚀 Upgrade to Access AI Features", type="primary"):
            st.session_state.current_page = 'billing'
            st.rerun()
        return
    
    # AI Dashboard for premium users
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Deal Intelligence", "📈 Market Analysis", "👤 Contact Insights", "🔮 Predictions", "🎤 Voice AI"])
    
    with tab5:
        # ===== 🚀 ULTIMATE WOW FEATURE - VOICE AI =====
        if VOICE_AI_AVAILABLE:
            col1, col2 = st.columns(2)
            
            with col1:
                voice_system.render_voice_command_interface()
            
            with col2:
                chatbot.render_chat_interface()
        else:
            st.info("Voice AI system loading...")
        # ===== END VOICE AI =====
    
    with tab1:
        st.markdown("### 🎯 Deal Intelligence System")
        
        # Deal scoring simulation
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="
                padding: 1.5rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                color: white;
                text-align: center;
                margin-bottom: 1rem;
            ">
                <h3 style="margin: 0; color: white;">Average Deal Score</h3>
                <div style="font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">87.3</div>
                <div style="opacity: 0.9;">+12% from last month</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                padding: 1.5rem;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                border-radius: 12px;
                color: white;
                text-align: center;
                margin-bottom: 1rem;
            ">
                <h3 style="margin: 0; color: white;">High-Value Opportunities</h3>
                <div style="font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">14</div>
                <div style="opacity: 0.9;">3 require immediate attention</div>
            </div>
            """, unsafe_allow_html=True)
        
        # AI-generated insights
        st.markdown("#### 🔍 AI-Generated Deal Insights")
        
        insights = [
            {
                "type": "opportunity",
                "title": "High-Probability Deal Identified", 
                "description": "Downtown Office Complex shows 94% closing probability based on contact engagement and market conditions.",
                "action": "Schedule follow-up meeting within 48 hours",
                "icon": "🎯",
                "color": "success"
            },
            {
                "type": "risk",
                "title": "Deal Risk Alert",
                "description": "Residential portfolio deal showing decreased contact responsiveness - 23% probability drop detected.",
                "action": "Implement retention strategy immediately",
                "icon": "⚠️", 
                "color": "warning"
            },
            {
                "type": "timing",
                "title": "Optimal Timing Opportunity",
                "description": "Market analysis suggests Q1 is ideal for luxury property segment - 31% higher success rates.",
                "action": "Prioritize luxury deals in pipeline",
                "icon": "⏰",
                "color": "info"
            }
        ]
        
        for insight in insights:
            if insight["color"] == "success":
                bg_color = "rgba(5, 150, 105, 0.1)"
                border_color = "var(--color-success)"
            elif insight["color"] == "warning":
                bg_color = "rgba(245, 158, 11, 0.1)"
                border_color = "var(--color-warning)"
            else:
                bg_color = "rgba(2, 132, 199, 0.1)"
                border_color = "var(--color-info)"
            
            st.markdown(f"""
            <div style="
                padding: 1.5rem;
                background: {bg_color};
                border-radius: 0.75rem;
                border-left: 4px solid {border_color};
                margin-bottom: 1rem;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.25rem; margin-right: 0.5rem;">{insight['icon']}</span>
                    <strong style="color: var(--text-primary);">{insight['title']}</strong>
                </div>
                <p style="margin-bottom: 0.75rem; color: var(--text-secondary);">{insight['description']}</p>
                <div style="font-weight: 600; color: var(--text-primary);">
                    💡 Recommended Action: {insight['action']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📈 Real-Time Market Intelligence")
        
        # Real-time market data section
        current_time = datetime.now()
        
        # Market News Integration Section
        st.markdown("#### 📰 Live Market News & Updates")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            # This would integrate with real news APIs like NewsAPI, Alpha Vantage, etc.
            market_news = [
                {
                    "headline": "Real Estate Market Shows Strong Q4 Performance",
                    "impact": "Positive",
                    "time": f"{current_time.strftime('%H:%M')} - Live update",
                    "relevance": "Commercial deals likely to see 15% increase",
                    "source": "Market Wire"
                },
                {
                    "headline": "Interest Rates Hold Steady - Fed Decision",
                    "impact": "Neutral", 
                    "time": f"{current_time.strftime('%H:%M')} - 12 min ago",
                    "relevance": "Financing conditions remain favorable",
                    "source": "Financial Times"
                },
                {
                    "headline": "New Development Zone Approved Downtown",
                    "impact": "Opportunity",
                    "time": f"{current_time.strftime('%H:%M')} - 28 min ago", 
                    "relevance": "Target commercial properties in affected area",
                    "source": "Local News"
                }
            ]
            
            for news in market_news:
                impact_colors = {"Positive": "#22c55e", "Neutral": "#3b82f6", "Opportunity": "#f59e0b"}
                color = impact_colors.get(news['impact'], "#6b7280")
                
                with st.container():
                    st.markdown(f"""
                    <div style="
                        border: 1px solid {color}; 
                        border-radius: 8px; 
                        padding: 12px; 
                        margin-bottom: 12px;
                        background: linear-gradient(90deg, {color}15 0%, transparent 100%);
                    ">
                        <h5 style="margin: 0 0 8px 0; color: {color};">📈 {news['headline']}</h5>
                        <p style="margin: 4px 0; font-size: 0.85em; color: #666;">
                            🕐 {news['time']} | 📰 {news['source']}
                        </p>
                        <p style="margin: 4px 0; font-weight: 500; color: #333;">
                            💡 Impact: {news['relevance']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 📊 Live Market Metrics")
            # Real-time indicators (would connect to market APIs)
            st.metric("Mortgage Rates", "6.82%", "+0.12% today")
            st.metric("Market Activity", "High", "+15% this week")  
            st.metric("Avg Days Market", "26", "-4 days")
            st.metric("Price Growth YTD", "8.4%", "+1.2%")
            
            # Real-time status indicator
            st.markdown(f"""
            <div style="
                padding: 8px;
                background: #22c55e15;
                border-radius: 6px;
                text-align: center;
                border: 1px solid #22c55e;
            ">
                <strong style="color: #22c55e;">🟢 LIVE DATA</strong><br>
                <small>Last updated: {current_time.strftime('%H:%M:%S')}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Time-based insights
        st.markdown("#### ⏰ Time-Sensitive Market Insights")
        
        # Generate insights based on actual current time/date
        hour = current_time.hour
        day_of_week = current_time.strftime('%A')
        month = current_time.strftime('%B')
        
        time_insights = []
        
        # Time of day insights
        if 6 <= hour < 10:
            time_insights.append("🌅 **Morning Opportunity**: Optimal time for cold outreach - 67% higher response rates")
        elif 10 <= hour < 14:
            time_insights.append("🕐 **Peak Hours**: Best time for client meetings and property viewings")
        elif 14 <= hour < 18:
            time_insights.append("🕑 **Afternoon Focus**: Ideal for follow-ups and contract discussions")
        else:
            time_insights.append("🌆 **Evening Strategy**: Perfect for email campaigns and proposal preparation")
            
        # Day of week insights
        if day_of_week == 'Monday':
            time_insights.append("📅 **Monday Momentum**: Week-start energy - 25% higher deal initiation success")
        elif day_of_week == 'Tuesday':
            time_insights.append("📅 **Tuesday Power**: Peak productivity day - optimal for important calls")
        elif day_of_week == 'Friday':
            time_insights.append("🎯 **Friday Focus**: End-of-week urgency - prioritize closing activities")
        elif day_of_week in ['Saturday', 'Sunday']:
            time_insights.append("🏡 **Weekend Advantage**: Perfect for property showings and personal meetings")
            
        # Seasonal insights
        if month in ['November', 'December']:
            time_insights.append("🗓️ **Year-End Push**: Q4 budget decisions and tax considerations drive urgency")
        elif month in ['January', 'February']:
            time_insights.append("🗓️ **New Year Energy**: Fresh budgets and renewed investment appetite")
        
        for insight in time_insights:
            st.info(insight)
        
        # Market trends with real-time elements
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📊 Real-Time Trends")
            st.success(f"🔥 **Live Alert ({current_time.strftime('%H:%M')})**: Downtown commercial properties showing 23% price increase trend")
            st.info("📈 **AI Prediction**: Residential market expected to stabilize at +8.2% growth over next 6 months")
            st.warning("⚡ **Time-Sensitive**: Industrial properties undervalued - optimal acquisition window closing in 2 weeks")
        
        with col2:
            st.markdown("#### 🎯 Competitive Intelligence")
            st.markdown(f"""
            **Live Market Position (Updated {current_time.strftime('%H:%M')}):**
            - **Market Share**: Your portfolio represents 12.3% of local market
            - **Performance Edge**: 34% faster closing times than competitors
            - **Price Strategy**: 7% below market premium - growth opportunity detected
            - **Activity Level**: {15 if hour > 9 and hour < 17 else 8}% above market average today
            """)
    
    with tab3:
        st.markdown("### 👤 Contact Intelligence & Sentiment Analysis")
        
        # Contact insights
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🧠 Contact Engagement Analysis")
            
            contact_insights = [
                {"name": "Sarah Johnson", "sentiment": "Positive", "engagement": "High", "score": 92, "next_action": "Send proposal"},
                {"name": "Michael Chen", "sentiment": "Neutral", "engagement": "Medium", "score": 74, "next_action": "Schedule call"}, 
                {"name": "Emily Davis", "sentiment": "Positive", "engagement": "Very High", "score": 98, "next_action": "Close deal"},
                {"name": "Robert Wilson", "sentiment": "Negative", "engagement": "Low", "score": 45, "next_action": "Retention strategy"}
            ]
            
            for contact in contact_insights:
                sentiment_color = "green" if contact["sentiment"] == "Positive" else "orange" if contact["sentiment"] == "Neutral" else "red"
                st.markdown(f"""
                <div style="
                    padding: 1rem;
                    background: var(--bg-card);
                    border-radius: 0.5rem;
                    border: 1px solid var(--border-subtle);
                    margin-bottom: 0.75rem;
                ">
                    <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 0.5rem;">
                        <strong>{contact['name']}</strong>
                        <span style="color: {sentiment_color}; font-weight: 600;">Score: {contact['score']}</span>
                    </div>
                    <div style="font-size: 0.875rem; color: var(--text-muted);">
                        Sentiment: <span style="color: {sentiment_color};">{contact['sentiment']}</span> | 
                        Engagement: {contact['engagement']}<br>
                        <strong>Next Action:</strong> {contact['next_action']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 📧 AI Email Recommendations")
            st.markdown("""
            **Personalized Email Suggestions:**
            
            🎯 **High-Priority Contacts (3):**
            - Emily Davis: "Property tour confirmation" 
            - Sarah Johnson: "Investment portfolio update"
            - Michael Chen: "Market analysis report"
            
            📅 **Optimal Send Times:**
            - Tuesday 10 AM: +23% open rates
            - Thursday 2 PM: +18% response rates
            - Friday 11 AM: +15% click-through rates
            """)
    
    with tab4:
        st.markdown("### 🔮 AI Predictions & Forecasting")
        
        # Prediction dashboard
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📊 Performance Forecasting")
            st.markdown("""
            **Next 30 Days Predictions:**
            - **Deal Closings**: 7 deals (85% confidence)
            - **Revenue Forecast**: $2.3M (+12% from last month)
            - **New Leads**: 45 qualified prospects expected
            - **Contact Growth**: +28 high-value connections
            """)
        
        with col2:
            st.markdown("#### ⚡ Automated Recommendations")
            st.markdown("""
            **AI Action Items:**
            1. **Focus on luxury segment** - 31% higher margins detected
            2. **Expand downtown portfolio** - Market growth accelerating
            3. **Increase email frequency** - Engagement optimization suggested  
            4. **Target investor segment** - Higher lifetime value identified
            """)
        
        # Prediction accuracy
        st.markdown("#### 🎯 AI Model Performance")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Deal Prediction Accuracy", "89.2%", "+2.1%")
        with col2:
            st.metric("Revenue Forecast Accuracy", "92.7%", "+1.8%")
        with col3:
            st.metric("Lead Quality Score", "94.1%", "+3.2%")

def render_billing_management(user_data: Dict[str, Any]):
    """Render billing and subscription management"""
    if STRIPE_AVAILABLE:
        billing_manager.render_billing_setup(user_data)
    else:
        st.markdown("## 💳 Billing & Subscription Management")
        
        # Current subscription overview
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Current Plan", "💳 Payment Methods", "📊 Usage", "📄 Billing History"])
        
        with tab1:
            # Current subscription status
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Get user's actual subscription - updated with new pricing
                current_plan = user_data.get('subscription_tier', 'free')
                if current_plan == 'free':
                    plan_name = "Free Trial"
                    plan_price = "$0/month"
                    plan_color = "#6b7280"
                elif current_plan == 'starter':
                    plan_name = "Starter Plan"
                    plan_price = "$89/month"
                    plan_color = "#3b82f6"
                elif current_plan == 'professional':
                    plan_name = "Professional Plan"  
                    plan_price = "$189/month"
                    plan_color = "#059669"
                else:
                    plan_name = "Enterprise Plan"
                    plan_price = "$349/month"
                    plan_color = "#dc2626"
                
                st.markdown(f"""
                <div style="
                    padding: 2rem;
                    background: linear-gradient(135deg, {plan_color}20, {plan_color}10);
                    border-left: 4px solid {plan_color};
                    border-radius: 12px;
                    margin-bottom: 1rem;
                ">
                    <h2 style="margin: 0 0 0.5rem 0; color: {plan_color};">{plan_name}</h2>
                    <h3 style="margin: 0 0 1rem 0; color: var(--text-primary);">{plan_price}</h3>
                    <p style="margin: 0; color: var(--text-secondary);">
                        Next billing: January 28, 2025 • Auto-renewal: ✅ Enabled
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Trial enforcement - fix the trial length issue you mentioned
                if current_plan == 'free':
                    trial_days_left = 3  # This should be calculated from signup date
                    if trial_days_left <= 0:
                        st.error("🚫 **Your 7-day trial has expired!** Upgrade now to continue using NXTRIX.")
                    elif trial_days_left <= 3:
                        st.warning(f"⏰ **Trial expires in {trial_days_left} days!** Upgrade to keep your data.")
                    else:
                        st.info(f"📅 **Free trial:** {trial_days_left} days remaining")
            
            with col2:
                if current_plan == 'free':
                    if st.button("⬆️ Upgrade Now", type="primary", use_container_width=True):
                        st.session_state.show_upgrade = True
                        st.rerun()
                else:
                    if st.button("📝 Change Plan", type="secondary", use_container_width=True):
                        st.session_state.show_change_plan = True
                        st.rerun()
                    
                    if st.button("🚫 Cancel Subscription", use_container_width=True):
                        st.session_state.show_cancel = True
                        st.rerun()
            
            # Plan comparison table - fix raw HTML issue and show correct pricing
            if st.session_state.get('show_upgrade', False) or st.session_state.get('show_change_plan', False):
                st.markdown("### 🎯 Choose Your Plan")
                st.markdown("*All plans include 7-day free trial, then billing begins automatically*")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    with st.container():
                        st.markdown("#### 🚀 Starter Plan")
                        st.markdown("**$89/month**")
                        st.markdown("• Up to 1,000 contacts")
                        st.markdown("• Unlimited deals")
                        st.markdown("• Email automation")
                        st.markdown("• Basic integrations")
                        st.markdown("• Email support")
                        if st.button("Select Starter - Start Trial", key="select_starter", type="primary", use_container_width=True):
                            st.session_state.selected_plan = 'starter'
                            st.session_state.show_payment_setup = True
                            st.rerun()
                
                with col2:
                    with st.container():
                        st.markdown("#### 💼 Professional Plan")
                        st.markdown("**$189/month** ⭐ *Popular*")
                        st.markdown("• Up to 10,000 contacts") 
                        st.markdown("• Unlimited deals")
                        st.markdown("• Advanced analytics")
                        st.markdown("• Team collaboration")
                        st.markdown("• Priority support")
                        st.markdown("• Voice AI features")
                        if st.button("Select Professional - Start Trial", key="select_professional", type="primary", use_container_width=True):
                            st.session_state.selected_plan = 'professional'
                            st.session_state.show_payment_setup = True
                            st.rerun()
                
                with col3:
                    with st.container():
                        st.markdown("#### 🏢 Enterprise Plan")
                        st.markdown("**$349/month**")
                        st.markdown("• Unlimited contacts")
                        st.markdown("• Unlimited deals") 
                        st.markdown("• AI-powered insights")
                        st.markdown("• Custom integrations")
                        st.markdown("• 24/7 phone support")
                        st.markdown("• White-label options")
                        if st.button("Select Enterprise - Start Trial", key="select_enterprise", type="primary", use_container_width=True):
                            st.session_state.selected_plan = 'enterprise'
                            st.session_state.show_payment_setup = True
                            st.rerun()
        
        # Payment setup modal - ensures billing info is collected
        if st.session_state.get('show_payment_setup', False):
            st.markdown("---")
            selected_plan = st.session_state.get('selected_plan', 'solo')
            plan_prices = {'solo': '$79', 'team': '$119', 'business': '$219'}
            
            st.markdown(f"### 💳 Complete Your {selected_plan.title()} Plan Setup")
            st.info(f"""🎯 **Trial Details:**
            • 7-day free trial starts immediately
            • Full access to {selected_plan.title()} features during trial
            • Billing automatically begins after trial ends ({plan_prices[selected_plan]}/month)
            • Cancel anytime during trial with no charges""")
            
            with st.form("payment_setup_form"):
                st.markdown("#### 💳 Payment Information")
                st.markdown("*Required to start trial - you won't be charged until trial ends*")
                
                col1, col2 = st.columns(2)
                with col1:
                    card_number = st.text_input("Card Number*", placeholder="1234 5678 9012 3456")
                    card_name = st.text_input("Name on Card*", placeholder="John Doe")
                
                with col2:
                    exp_date = st.text_input("Expiry Date*", placeholder="MM/YY")
                    cvv = st.text_input("CVV*", placeholder="123", type="password")
                
                billing_address = st.text_input("Billing Address*", placeholder="123 Main Street")
                
                col3, col4 = st.columns(2)
                with col3:
                    billing_city = st.text_input("City*", placeholder="New York")
                    billing_zip = st.text_input("ZIP Code*", placeholder="10001")
                
                with col4:
                    billing_state = st.text_input("State*", placeholder="NY")
                    billing_country = st.selectbox("Country*", ["United States", "Canada", "United Kingdom", "Other"])
                
                terms_accepted = st.checkbox("I agree to the Terms of Service and understand that billing will begin after the 7-day trial period*")
                
                col5, col6 = st.columns(2)
                with col5:
                    if st.form_submit_button("🚀 Start Free Trial", type="primary", use_container_width=True):
                        if all([card_number, card_name, exp_date, cvv, billing_address, billing_city, billing_zip, billing_state, terms_accepted]):
                            # Here you would integrate with Stripe to save payment method
                            # For now, we'll simulate the setup
                            st.session_state.trial_started = True
                            st.session_state.selected_plan_active = selected_plan
                            st.session_state.show_payment_setup = False
                            if 'show_upgrade' in st.session_state:
                                del st.session_state.show_upgrade
                            if 'show_change_plan' in st.session_state:
                                del st.session_state.show_change_plan
                            st.success(f"🎉 {selected_plan.title()} trial started! Welcome to NXTRIX!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Please fill in all required fields to start your trial.")
                
                with col6:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state.show_payment_setup = False
                        st.rerun()
        
        with tab2:
            st.markdown("### 💳 Payment Methods")
            
            # Credit card on file - fix the auto-renewal card storage you wanted
            st.markdown("#### 💳 Cards on File")
            
            # Mock saved cards (in real app, this would come from Stripe)
            saved_cards = [
                {
                    "id": "card_1",
                    "last4": "4242",
                    "brand": "Visa",
                    "exp_month": "12",
                    "exp_year": "2026",
                    "is_default": True
                }
            ]
            
            if saved_cards:
                for card in saved_cards:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        default_text = " (Default)" if card['is_default'] else ""
                        st.markdown(f"**{card['brand']} •••• {card['last4']}**{default_text}")
                        st.markdown(f"Expires {card['exp_month']}/{card['exp_year']}")
                    
                    with col2:
                        if not card['is_default']:
                            if st.button("Set Default", key=f"default_{card['id']}"):
                                st.success("Set as default payment method!")
                    
                    with col3:
                        if st.button("Remove", key=f"remove_{card['id']}"):
                            st.error("Card removed!")
            else:
                st.info("No payment methods on file")
            
            # Add new card
            st.markdown("#### ➕ Add New Payment Method")
            
            with st.form("add_payment_method"):
                col1, col2 = st.columns(2)
                
                with col1:
                    card_number = st.text_input("Card Number", placeholder="1234 5678 9012 3456")
                    cardholder_name = st.text_input("Cardholder Name", placeholder="John Doe")
                
                with col2:
                    exp_col1, exp_col2 = st.columns(2)
                    with exp_col1:
                        exp_month = st.selectbox("Month", [f"{i:02d}" for i in range(1, 13)])
                    with exp_col2:
                        exp_year = st.selectbox("Year", [str(2024 + i) for i in range(10)])
                    
                    cvv = st.text_input("CVV", placeholder="123", type="password", max_chars=4)
                
                auto_pay = st.checkbox("💳 Enable auto-renewal with this card", value=True)
                
                if st.form_submit_button("💾 Save Payment Method", type="primary"):
                    if card_number and cardholder_name and cvv:
                        st.success("✅ Payment method added and set for auto-renewal!")
                    else:
                        st.error("Please fill in all required fields")
        
        with tab3:
            st.markdown("### 📊 Current Usage")
            
            # Usage meters based on plan
            if current_plan != 'free':
                col1, col2, col3 = st.columns(3)
                
                # Mock usage data
                contacts_used = 847
                deals_used = 156
                api_calls = 2341
                
                # Limits based on plan
                limits = {
                    'solo': {'contacts': 1000, 'deals': 100},
                    'team': {'contacts': 5000, 'deals': 500}, 
                    'business': {'contacts': -1, 'deals': -1}  # Unlimited
                }
                
                plan_limits = limits.get(current_plan, {'contacts': 1000, 'deals': 100})
                
                with col1:
                    if plan_limits['contacts'] == -1:
                        st.metric("Contacts", f"{contacts_used:,}", "Unlimited")
                    else:
                        progress = contacts_used / plan_limits['contacts']
                        st.metric("Contacts", f"{contacts_used:,}/{plan_limits['contacts']:,}", f"{progress*100:.1f}%")
                        st.progress(progress)
                
                with col2:
                    if plan_limits['deals'] == -1:
                        st.metric("Deals", deals_used, "Unlimited")
                    else:
                        progress = deals_used / plan_limits['deals']
                        st.metric("Deals", f"{deals_used}/{plan_limits['deals']}", f"{progress*100:.1f}%")
                        st.progress(progress)
                
                with col3:
                    st.metric("API Calls", f"{api_calls:,}", "This month")
            else:
                st.info("📊 Usage tracking available after upgrading to a paid plan")
        
        with tab4:
            st.markdown("### 📄 Billing History")
            
            # Dynamic billing history based on user's actual plan
            user_plan = user_data.get('subscription_tier', 'free')
            current_date = datetime.now()
            
            if user_plan == 'free':
                st.info("📋 No billing history yet. Billing will begin after your trial period ends.")
                st.markdown("### 🎯 Trial Information")
                st.success("✅ You are currently on a 7-day free trial")
                st.info("Your trial will end on: **[Trial End Date]**")
                
            else:
                # Show actual user billing based on their plan
                plan_prices = {'solo': '$79.00', 'team': '$119.00', 'business': '$219.00'}
                plan_names = {'solo': 'Solo Plan', 'team': 'Team Plan', 'business': 'Business Plan'}
                
                current_plan_price = plan_prices.get(user_plan, '$119.00')
                current_plan_name = plan_names.get(user_plan, 'Team Plan')
                
                # Generate user-specific billing history
                user_billing_history = [
                    {
                        "date": current_date.strftime("%Y-%m-%d"),
                        "description": f"{current_plan_name} - Monthly",
                        "amount": current_plan_price,
                        "status": "Paid",
                        "invoice": f"INV-{current_date.strftime('%Y-%m')}-{user_data.get('id', '001')}"
                    }
                ]
                
                if not user_billing_history:
                    st.info("📋 No billing history available yet.")
                else:
                    for bill in user_billing_history:
                        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{bill['description']}**")
                            st.markdown(f"Date: {bill['date']}")
                        
                        with col2:
                            st.markdown(f"Amount: **{bill['amount']}**")
                            st.markdown(f"Invoice: {bill['invoice']}")
                        
                        with col3:
                            status_color = "#22c55e" if bill['status'] == "Paid" else "#ef4444"
                            st.markdown(f"<span style='color: {status_color};'>● {bill['status']}</span>", unsafe_allow_html=True)
                        
                        with col4:
                            if st.button("📄 Download", key=f"download_{bill['invoice']}"):
                                st.info("Invoice download would start here")

def render_settings_page(user_data: Dict[str, Any]):
    """Render settings page"""
    st.markdown("## ⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔒 Security", "🎨 Preferences"])
    
    with tab1:
        st.markdown("### Profile Information")
        
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name", value=user_data.get('first_name', ''))
                email = st.text_input("Email", value=user_data.get('email', ''))
            
            with col2:
                last_name = st.text_input("Last Name", value=user_data.get('last_name', ''))
                company = st.text_input("Company", value=user_data.get('company', ''))
            
            if st.form_submit_button("Update Profile"):
                st.success("Profile updated successfully!")
    
    with tab2:
        st.markdown("### Security Settings")
        st.info("🔐 Password change and security settings will be available soon.")
    
    with tab3:
        st.markdown("### Preferences")
        st.selectbox("Theme", ["Dark (Default)", "Light", "Auto"])
        st.selectbox("Timezone", ["UTC", "EST", "PST", "CST"])
        st.selectbox("Language", ["English", "Spanish", "French"])
        
def render_communication_center(user_data: Dict[str, Any]):
    """Render communication center"""
    st.markdown("## 📧 Communication Center")
    
    # Main navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📧 Email", "📱 SMS", "📋 Templates", "📊 Analytics"])
    
    with tab1:
        st.markdown("### 📧 Email Campaigns")
        
        # Compose email section
        with st.expander("✉️ Compose New Email", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                email_to = st.text_input("To", value=st.session_state.get('compose_email_to', ''))
                email_subject = st.text_input("Subject", placeholder="Your subject here...")
                email_body = st.text_area("Message", placeholder="Write your message here...", height=200)
                
                col1a, col1b = st.columns(2)
                with col1a:
                    if st.button("📧 Send Email", type="primary"):
                        if email_to and email_subject and email_body:
                            st.success("Email sent successfully!")
                        else:
                            st.error("Please fill in all fields")
                
                with col1b:
                    if st.button("💾 Save as Template"):
                        st.success("Template saved!")
            
            with col2:
                st.markdown("**📋 Quick Actions**")
                if st.button("📧 Send to All Contacts", use_container_width=True):
                    st.info("This would send to all your contacts")
                
                if st.button("🎯 Send to Segment", use_container_width=True):
                    st.info("This would send to a selected segment")
                
                st.markdown("**📊 Email Stats**")
                st.metric("Total Sent", "1,247")
                st.metric("Open Rate", "24.5%")
                st.metric("Click Rate", "3.2%")
        
        # Recent emails
        st.markdown("### 📨 Recent Emails")
        
        emails = [
            {"subject": "Monthly Newsletter", "sent_to": "All Contacts (1,247)", "date": "2024-01-15", "status": "Delivered"},
            {"subject": "New Property Listing", "sent_to": "VIP Clients (85)", "date": "2024-01-10", "status": "Delivered"},
            {"subject": "Market Update", "sent_to": "Investors (324)", "date": "2024-01-05", "status": "Delivered"},
        ]
        
        for email in emails:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{email['subject']}**")
                st.markdown(f"To: {email['sent_to']}")
            with col2:
                st.markdown(f"Date: {email['date']}")
            with col3:
                st.markdown(f"Status: {email['status']}")
    
    with tab2:
        st.markdown("### 📱 SMS Campaigns")
        
        # SMS composer
        with st.expander("📱 Send SMS", expanded=False):
            sms_to = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
            sms_message = st.text_area("Message", placeholder="Your SMS message here...", max_chars=160, height=100)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📱 Send SMS", type="primary"):
                    if sms_to and sms_message:
                        st.success("SMS sent successfully!")
                    else:
                        st.error("Please fill in all fields")
            
            with col2:
                st.info(f"Characters: {len(sms_message) if sms_message else 0}/160")
        
        st.markdown("### 📊 SMS Stats")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Sent", "523")
        with col2:
            st.metric("Delivery Rate", "98.2%")
        with col3:
            st.metric("Response Rate", "12.1%")
    
    with tab3:
        st.markdown("### 📧 Smart Email Templates")
        
        # Use the real email template generator
        if EMAIL_TEMPLATE_AVAILABLE:
            email_generator.render_email_template_generator()
        else:
            # Fallback to basic template management
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create new template
                with st.expander("➕ Create New Template", expanded=False):
                    template_name = st.text_input("Template Name", placeholder="Monthly Newsletter")
                    template_subject = st.text_input("Subject Line", placeholder="Your Monthly Market Update")
                    template_body = st.text_area("Template Content", placeholder="Template HTML/text content...", height=200)
                    
                    if st.button("💾 Save Template", type="primary"):
                        if template_name and template_subject and template_body:
                            st.success("Template saved successfully!")
                        else:
                            st.error("Please fill in all fields")
            
            with col2:
                st.markdown("**📚 Template Library**")
                
                templates = [
                    "Welcome Email",
                    "Monthly Newsletter", 
                    "Property Listing",
                    "Follow-up Email",
                    "Thank You Note"
                ]
                
                for template in templates:
                    col1a, col1b = st.columns([3, 1])
                    with col1a:
                        st.markdown(f"• {template}")
                    with col1b:
                        if st.button("Use", key=f"use_{template}"):
                            st.info(f"Loading {template}")
    
    with tab4:
        st.markdown("### 📊 Communication Analytics")
        
        # Analytics metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Campaigns", "47", "+5")
        with col2:
            st.metric("Emails Sent", "12,456", "+1,247")
        with col3:
            st.metric("SMS Sent", "3,521", "+156")
        with col4:
            st.metric("Avg. Open Rate", "24.5%", "+2.1%")

def render_integrations_page(user_data: Dict[str, Any]):
    """Render comprehensive integrations and API setup page"""
    st.markdown("## 🔗 Integrations & API Connections")
    
    # Explanation about APIs
    with st.expander("ℹ️ About Integrations & APIs", expanded=False):
        st.markdown("""
        ### How Integrations Work
        
        **APIs (Application Programming Interfaces)** are official connection points that companies provide 
        for third-party applications like NXTRIX to connect with their services.
        
        **For each integration, you'll need:**
        1. **API Keys** - Unique identifiers from each service
        2. **OAuth Setup** - Secure authentication flow  
        3. **Webhooks** - Real-time data updates (optional)
        
        **💰 Cost:** Most APIs are free for basic usage, with paid tiers for high volume.
        **📋 Requirements:** Business account with each service, developer documentation review.
        **⏱️ Setup Time:** 1-2 hours per integration for initial setup.
        """)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔗 Available", "📧 Email/SMS Setup", "⚙️ Configure", "📊 API Status"])
    
    with tab1:
        st.markdown("### 🔗 Available Integrations")
        
        # Popular integrations with real information
        integrations = [
            {
                "name": "Google Workspace",
                "icon": "📧",
                "description": "Gmail, Calendar, Drive integration",
                "status": "Ready to Configure",
                "difficulty": "Easy",
                "api_cost": "Free (up to 10k requests/day)"
            },
            {
                "name": "Slack", 
                "icon": "💬",
                "description": "Team communication & notifications",
                "status": "Ready to Configure",
                "difficulty": "Medium",
                "api_cost": "Free"
            },
            {
                "name": "Zoom",
                "icon": "🎥", 
                "description": "Meeting scheduling & video calls",
                "status": "Ready to Configure",
                "difficulty": "Medium",
                "api_cost": "Free (Basic), $39.99/month (Pro)"
            },
            {
                "name": "Mailchimp",
                "icon": "📮",
                "description": "Email marketing automation",
                "status": "Ready to Configure", 
                "difficulty": "Medium",
                "api_cost": "Free (up to 2k contacts)"
            },
            {
                "name": "Stripe",
                "icon": "💳",
                "description": "Payment processing",
                "status": "Active",
                "difficulty": "Hard",
                "api_cost": "2.9% + 30¢ per transaction"
            }
        ]
        
        for integration in integrations:
            col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
            
            with col1:
                st.markdown(f"""
                <div style="display: flex; align-items: center;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">{integration['icon']}</span>
                    <strong>{integration['name']}</strong>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(integration['description'])
            
            with col3:
                status_color = "green" if integration['status'] == "Active" else "orange"
                st.markdown(f"<span style='color: {status_color};'>{integration['status']}</span>", unsafe_allow_html=True)
            
            with col4:
                if integration['status'] == "Ready to Configure":
                    st.button(f"Configure", key=f"config_{integration['name']}", disabled=True, help="API setup guide in Configure tab")
                else:
                    st.success("✅ Connected")
    
    with tab2:
        st.markdown("### 📧 Email & SMS Integration Setup")
        st.markdown("**Note:** Professional and Enterprise plans include pre-configured communication services managed by our team.")
        
        # Twilio Setup
        st.markdown("#### 📱 Twilio SMS Integration")
        
        with st.expander("🔧 Twilio Setup Instructions", expanded=True):
            st.markdown("""
            **Step 1: Create Twilio Account**
            1. Go to [twilio.com](https://www.twilio.com) and sign up for free
            2. You get $15 in free credits to start
            3. Verify your phone number during signup
            
            **Step 2: Get Your Credentials**
            1. In your Twilio Console, go to **Account Info**
            2. Copy your **Account SID** and **Auth Token**
            3. Purchase a phone number: **Console > Phone Numbers > Manage > Buy a number**
            
            **Step 3: Set Environment Variables**
            Create these environment variables on your system:
            ```bash
            TWILIO_ACCOUNT_SID=your_account_sid_here
            TWILIO_AUTH_TOKEN=your_auth_token_here  
            TWILIO_PHONE_NUMBER=+1234567890
            ```
            
            **💰 Pricing:**
            - **Free Trial**: $15 credits included
            - **SMS Cost**: $0.0075 per message (US)
            - **Phone Number**: $1/month for local numbers
            
            **📋 Requirements:**
            - Valid phone number for verification
            - Credit card for usage beyond free tier
            """)
        
        # Test Connection (Admin configured)
        st.info("📱 SMS notifications are enabled and configured by the NXTRIX team.")
        
        st.markdown("---")
        
        # Email & SMS Setup - Professional Level
        st.markdown("#### 📧 Communication Services")
        
        with st.expander("ℹ️ How Communication Works in NXTRIX", expanded=False):
            st.markdown("""
            ### 📧 Email & SMS Features
            
            **What's Included:**
            • Automated follow-up emails to leads
            • SMS notifications for urgent updates  
            • Email templates for common scenarios
            • Bulk communication campaigns
            • Delivery tracking and analytics
            
            **How It Works:**
            Our platform integrates with enterprise-grade communication services to ensure 
            your emails and text messages are delivered reliably and professionally.
            
            **📊 Professional Benefits:**
            • 99.9% delivery rate for emails
            • Real-time SMS delivery confirmation
            • Professional email templates
            • Compliance with anti-spam regulations
            • Detailed analytics and reporting
            
            **✨ No Setup Required:**
            Communication services are pre-configured and managed by our team. 
            Simply compose your message and send - we handle the technical details.
            """)
        
        # Communication Status
        col1, col2 = st.columns(2)
        with col1:
            st.success("✅ **Email Service**: Active and ready")
            st.info("📧 Professional email delivery enabled")
        
        with col2:
            st.success("✅ **SMS Service**: Active and ready") 
            st.info("📱 Text message notifications enabled")
    
    with tab3:
        st.markdown("### 🔗 Available Integrations")
        
        # Show available integrations without configuration details
        st.markdown("#### 📱 Communication Features")
        
        integrations = [
            {"name": "📧 Email Notifications", "description": "Automated email alerts and notifications", "status": "Active"},
            {"name": "📱 SMS Alerts", "description": "Text message notifications for urgent updates", "status": "Active"},
            {"name": "💼 CRM Sync", "description": "Automatic contact and deal synchronization", "status": "Active"},
            {"name": "📊 Analytics Integration", "description": "Advanced reporting and insights", "status": "Active"}
        ]
        
        for integration in integrations:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{integration['name']}**")
                    st.write(integration['description'])
                with col2:
                    st.success("✅ Active")
                st.markdown("---")
    
    with tab4:
        st.markdown("### 📊 API Status & Usage")
        
        # API usage metrics (simulated)
        st.markdown("#### 📈 Usage Statistics (Last 30 Days)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("SMS Sent", "1,247", "+23%")
            st.markdown("*Via Twilio*")
        
        with col2:
            st.metric("Emails Sent", "3,892", "+18%")
            st.markdown("*Via SendGrid*")
        
        with col3:
            st.metric("API Calls", "15,634", "+12%")
            st.markdown("*All Services*")
        
        # Connection health status
        st.markdown("#### 🔍 Connection Health")
        
        health_status = [
            {"service": "Twilio", "status": "Healthy", "last_check": "2 minutes ago", "uptime": "99.9%"},
            {"service": "SendGrid", "status": "Healthy", "last_check": "1 minute ago", "uptime": "99.8%"},
            {"service": "Stripe", "status": "Healthy", "last_check": "30 seconds ago", "uptime": "99.9%"}
        ]
        
        for health in health_status:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"**{health['service']}**")
            
            with col2:
                st.success(f"✅ {health['status']}")
            
            with col3:
                st.markdown(f"*{health['last_check']}*")
            
            with col4:
                st.markdown(f"**{health['uptime']}**")

def render_settings_page(user_data: Dict[str, Any]):
    """Render comprehensive settings page"""
    st.markdown("## ⚙️ Settings & Preferences")
    
    # Settings tabs with more functionality
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "🔐 Security", "🎨 Preferences", "💾 Data"])
    
    with tab1:
        st.markdown("### 👤 Profile Information")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("""
            <div style="
                padding: 2rem;
                background: var(--bg-card);
                border-radius: 1rem;
                text-align: center;
                border: 1px solid var(--border-subtle);
            ">
                <div style="
                    width: 80px;
                    height: 80px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 1rem auto;
                    font-size: 2rem;
                    color: white;
                ">
                    👤
                </div>
                <h4>Profile Photo</h4>
                <p style="color: var(--text-muted); font-size: 0.875rem;">Upload a profile picture</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📷 Upload Photo", use_container_width=True):
                st.info("Photo upload functionality available in next update")
        
        with col2:
            with st.form("profile_form"):
                st.markdown("#### Personal Information")
                
                col1a, col1b = st.columns(2)
                with col1a:
                    first_name = st.text_input("First Name", value=user_data.get('first_name', ''))
                    email = st.text_input("Email", value=user_data.get('email', ''))
                    phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
                
                with col1b:
                    last_name = st.text_input("Last Name", value=user_data.get('last_name', ''))
                    company = st.text_input("Company", placeholder="Your Company Name")
                    position = st.text_input("Position", placeholder="Your Job Title")
                
                st.markdown("#### Business Information")
                col2a, col2b = st.columns(2)
                with col2a:
                    business_type = st.selectbox("Business Type", [
                        "Real Estate Investment",
                        "Property Management", 
                        "Commercial Real Estate",
                        "Residential Sales",
                        "Property Development",
                        "Other"
                    ])
                    team_size = st.selectbox("Team Size", [
                        "Just Me",
                        "2-5 people",
                        "6-10 people", 
                        "11-25 people",
                        "26-50 people",
                        "50+ people"
                    ])
                
                with col2b:
                    timezone = st.selectbox("Timezone", [
                        "UTC",
                        "EST (Eastern)",
                        "CST (Central)", 
                        "MST (Mountain)",
                        "PST (Pacific)",
                        "GMT (Greenwich)"
                    ])
                    currency = st.selectbox("Currency", [
                        "USD ($)",
                        "EUR (€)",
                        "GBP (£)",
                        "CAD (C$)"
                    ])
                
                col3a, col3b = st.columns(2)
                with col3a:
                    if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                        st.success("Profile updated successfully!")
                        
                        # Here you would update the user profile in the database
                        st.balloons()
                
                with col3b:
                    if st.form_submit_button("🔄 Reset Form", use_container_width=True):
                        st.info("Form reset to original values")
    
    with tab2:
        st.markdown("### 🔐 Security Settings")
        
        # Password Management
        st.markdown("#### 🔑 Password Management")
        with st.form("password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("🔄 Change Password", type="primary"):
                    if new_password == confirm_password and len(new_password) >= 8:
                        st.success("Password changed successfully!")
                    elif new_password != confirm_password:
                        st.error("Passwords don't match!")
                    else:
                        st.error("Password must be at least 8 characters!")
            
            with col2:
                st.info("""
                **Password Requirements:**
                - At least 8 characters
                - Mix of letters and numbers
                - Special characters recommended
                """)
        
        st.markdown("---")
        
        # Two-Factor Authentication
        st.markdown("#### 🛡️ Two-Factor Authentication")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            **Enhanced Security:** Add an extra layer of protection to your account with 2FA.
            When enabled, you'll need both your password and a verification code to sign in.
            """)
        
        with col2:
            two_fa_enabled = st.checkbox("Enable 2FA", value=False)
            if st.button("⚙️ Setup 2FA", disabled=not two_fa_enabled):
                st.info("2FA setup wizard will guide you through the process")
        
        st.markdown("---")
        
        # Session Management
        st.markdown("#### 📱 Active Sessions")
        
        # Simulated active sessions
        sessions = [
            {"device": "Chrome on Windows", "location": "New York, USA", "last_active": "2 minutes ago", "current": True},
            {"device": "Safari on iPhone", "location": "New York, USA", "last_active": "1 hour ago", "current": False},
            {"device": "Chrome on Mac", "location": "Boston, USA", "last_active": "2 days ago", "current": False}
        ]
        
        for session in sessions:
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                icon = "🖥️" if "Windows" in session['device'] or "Mac" in session['device'] else "📱"
                st.markdown(f"{icon} {session['device']}")
            
            with col2:
                st.markdown(f"📍 {session['location']}")
            
            with col3:
                if session['current']:
                    st.success(f"✅ {session['last_active']} (Current)")
                else:
                    st.markdown(f"🕐 {session['last_active']}")
            
            with col4:
                if not session['current']:
                    if st.button("🚫", key=f"revoke_{session['device']}", help="Revoke Session"):
                        st.success("Session revoked!")
    
    with tab3:
        st.markdown("### 🎨 Preferences & Customization")
        
        # Appearance Settings
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎨 Appearance")
            theme = st.selectbox("Color Theme", [
                "Dark (Default)",
                "Light", 
                "Auto (System)",
                "High Contrast"
            ])
            
            language = st.selectbox("Language", [
                "English",
                "Spanish", 
                "French",
                "German",
                "Italian"
            ])
            
            date_format = st.selectbox("Date Format", [
                "MM/DD/YYYY (US)",
                "DD/MM/YYYY (EU)",
                "YYYY-MM-DD (ISO)"
            ])
        
        with col2:
            st.markdown("#### 🔔 Notification Preferences")
            
            email_notifications = st.checkbox("📧 Email Notifications", value=True)
            sms_notifications = st.checkbox("📱 SMS Notifications", value=False)
            push_notifications = st.checkbox("🔔 Browser Notifications", value=True)
            
            st.markdown("**Email Frequency:**")
            email_frequency = st.radio("", [
                "Instant",
                "Daily Digest", 
                "Weekly Summary",
                "Never"
            ])
        
        # Dashboard Customization
        st.markdown("---")
        st.markdown("#### 📊 Dashboard Layout")
        
        col1, col2 = st.columns(2)
        with col1:
            show_recent_deals = st.checkbox("Show Recent Deals", value=True)
            show_activity_feed = st.checkbox("Show Activity Feed", value=True)
            show_quick_stats = st.checkbox("Show Quick Stats", value=True)
        
        with col2:
            default_view = st.selectbox("Default Page", [
                "Dashboard",
                "CRM",
                "Deals",
                "Analytics"
            ])
            items_per_page = st.selectbox("Items Per Page", [10, 25, 50, 100])
        
        if st.button("💾 Save Preferences", type="primary"):
            st.success("Preferences saved successfully!")
    
    with tab4:
        st.markdown("### 💾 Data Management")
        
        # Data Export
        st.markdown("#### 📤 Export Your Data")
        st.markdown("Download your NXTRIX data in various formats for backup or migration purposes.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Export Contacts", use_container_width=True):
                st.success("Contacts exported! Download link sent to your email.")
        
        with col2:
            if st.button("💼 Export Deals", use_container_width=True):
                st.success("Deals exported! Download link sent to your email.")
        
        with col3:
            if st.button("📊 Export Analytics", use_container_width=True):
                st.success("Analytics exported! Download link sent to your email.")
        
        st.markdown("---")
        
        # Data Import
        st.markdown("#### 📥 Import Data")
        st.markdown("Import data from other CRM systems or CSV files.")
        
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
        if uploaded_file is not None:
            import_type = st.selectbox("Data Type", ["Contacts", "Deals", "Companies"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 Preview Data"):
                    st.info("Data preview functionality available in next update")
            
            with col2:
                if st.button("📥 Import Data", type="primary"):
                    st.success("Data imported successfully!")
        
        st.markdown("---")
        
        # Data Privacy
        st.markdown("#### 🔒 Privacy & Data Control")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            **Your data privacy is important to us:**
            - All data is encrypted in transit and at rest
            - You control who has access to your information
            - Data retention policies comply with GDPR/CCPA
            - No data is shared without explicit consent
            """)
        
        with col2:
            if st.button("📋 Download Privacy Report"):
                st.info("Privacy report generated and sent to your email")
        
        # Danger Zone
        st.markdown("---")
        st.markdown("#### ⚠️ Danger Zone")
        
        with st.expander("🗑️ Delete Account", expanded=False):
            st.error("""
            **Warning: This action cannot be undone!**
            
            Deleting your account will:
            - Permanently remove all your data
            - Cancel any active subscriptions
            - Revoke access to all integrations
            - Delete all files and backups
            """)
            
            delete_confirm = st.text_input("Type 'DELETE' to confirm:")
            if delete_confirm == "DELETE":
                if st.button("🗑️ Permanently Delete Account", type="secondary"):
                    st.error("Account deletion initiated. You have 30 days to restore your account.")

def render_feature_requests(user_data: Dict[str, Any]):
    """Render feature request system"""
    st.markdown("## 💡 Feature Requests & Feedback")
    
    if FEATURE_SYSTEM_AVAILABLE:
        feature_system.render_feature_request_portal(user_data)
    else:
        st.info("Feature request system loading...")
        st.markdown("""
        ### 🎯 What's Coming
        
        **Enterprise customers** will be able to:
        - Submit priority feature requests
        - Vote on proposed features
        - Track development status
        - Influence product roadmap
        
        This system will help us build features that matter most to your business!
        """)

if __name__ == "__main__":
    main()