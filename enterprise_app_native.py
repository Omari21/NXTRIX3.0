"""
NXTRIX Platform - Enterprise CRM Application (Streamlit Native)
Professional interface using Streamlit native components with custom CSS
"""

import streamlit as st

# Configure Streamlit page
st.set_page_config(
    page_title="NXTRIX - Enterprise CRM Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

def apply_enterprise_styles():
    """Apply enterprise CSS styling"""
    st.markdown("""
    <style>
    /* Import Enterprise Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
        background: #f8fafc;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        padding-top: 2rem;
    }
    
    .sidebar .sidebar-content {
        background: transparent;
        color: white;
    }
    
    /* Enterprise Header */
    .enterprise-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 1rem 1rem;
        color: white;
        text-align: center;
    }
    
    .enterprise-logo {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .enterprise-tagline {
        color: rgba(255,255,255,0.8);
        font-size: 1rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.2s;
        text-align: center;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .metric-title {
        font-size: 0.875rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .metric-change {
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .metric-positive {
        color: #059669;
    }
    
    .metric-negative {
        color: #dc2626;
    }
    
    /* Content Cards */
    .content-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1rem;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0.25rem;
    }
    
    .status-active {
        background: #dcfce7;
        color: #059669;
    }
    
    .status-trial {
        background: #fef3c7;
        color: #d97706;
    }
    
    .status-premium {
        background: #ede9fe;
        color: #7c3aed;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
    }
    
    /* Data Tables */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    /* Navigation Items */
    .nav-item {
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        color: rgba(255,255,255,0.8);
        cursor: pointer;
        transition: all 0.2s;
        border-left: 3px solid transparent;
    }
    
    .nav-item:hover {
        background: rgba(59, 130, 246, 0.1);
        color: white;
        border-left-color: #3b82f6;
    }
    
    .nav-item.active {
        background: rgba(59, 130, 246, 0.15);
        color: white;
        border-left-color: #3b82f6;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

def create_sidebar_navigation():
    """Create enterprise sidebar navigation"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 1rem;">
            <div style="font-size: 1.5rem; font-weight: 700; color: white; margin-bottom: 0.5rem;">
                🏢 NXTRIX
            </div>
            <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">
                Enterprise CRM Platform
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**DASHBOARD**")
        if st.button("📊 Overview", key="nav_overview", use_container_width=True):
            st.session_state.active_page = "overview"
        if st.button("📈 Analytics", key="nav_analytics", use_container_width=True):
            st.session_state.active_page = "analytics"
        
        st.markdown("**CRM**")
        if st.button("👥 Contacts", key="nav_contacts", use_container_width=True):
            st.session_state.active_page = "contacts"
        if st.button("🤝 Deals", key="nav_deals", use_container_width=True):
            st.session_state.active_page = "deals"
        if st.button("🏢 Companies", key="nav_companies", use_container_width=True):
            st.session_state.active_page = "companies"
        if st.button("📋 Activities", key="nav_activities", use_container_width=True):
            st.session_state.active_page = "activities"
        
        st.markdown("**REAL ESTATE**")
        if st.button("🏠 Properties", key="nav_properties", use_container_width=True):
            st.session_state.active_page = "properties"
        if st.button("📊 Portfolio", key="nav_portfolio", use_container_width=True):
            st.session_state.active_page = "portfolio"
        if st.button("🧮 Financial Modeling", key="nav_financial", use_container_width=True):
            st.session_state.active_page = "financial"
        
        st.markdown("**AUTOMATION**")
        if st.button("🤖 Workflows", key="nav_workflows", use_container_width=True):
            st.session_state.active_page = "workflows"
        if st.button("📧 Email Campaigns", key="nav_email", use_container_width=True):
            st.session_state.active_page = "email"
        if st.button("🧠 AI Insights", key="nav_ai", use_container_width=True):
            st.session_state.active_page = "ai"
        
        st.markdown("---")
        st.markdown("""
        <div style="padding: 1rem; background: rgba(15, 23, 42, 0.5); border-radius: 8px; text-align: center;">
            <div style="color: white; font-weight: 600; margin-bottom: 0.25rem;">John Doe</div>
            <div style="color: rgba(255,255,255,0.7); font-size: 0.875rem;">Premium Plan</div>
        </div>
        """, unsafe_allow_html=True)

def create_enterprise_header():
    """Create enterprise header"""
    st.markdown("""
    <div class="enterprise-header">
        <div class="enterprise-logo">🏢 NXTRIX Enterprise</div>
        <div class="enterprise-tagline">Professional Real Estate Investment Platform</div>
    </div>
    """, unsafe_allow_html=True)

def create_dashboard_overview():
    """Create dashboard overview content"""
    
    # Top status bar
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("## Dashboard Overview")
    with col2:
        st.markdown('<span class="status-badge status-trial">🕐 7-Day Trial</span>', unsafe_allow_html=True)
    with col3:
        st.button("➕ New Deal", type="primary")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Total Revenue</div>
            <div class="metric-value">$2.4M</div>
            <div class="metric-change metric-positive">↗️ +12.5% vs last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Active Deals</div>
            <div class="metric-value">47</div>
            <div class="metric-change metric-positive">↗️ +8.2% vs last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Properties</div>
            <div class="metric-value">23</div>
            <div class="metric-change metric-positive">↗️ +15.8% vs last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Conversion Rate</div>
            <div class="metric-value">24.5%</div>
            <div class="metric-change metric-positive">↗️ +3.2% vs last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Welcome card
    st.markdown("""
    <div class="content-card">
        <h3 class="card-title">🎯 Welcome to NXTRIX Enterprise CRM</h3>
        <p style="color: #64748b; margin-bottom: 1rem;">Your professional real estate investment platform is now running with enterprise-grade interface design.</p>
        <div>
            <span class="status-badge status-active">✅ Production Ready</span>
            <span class="status-badge status-active">✅ Enterprise Design</span>
            <span class="status-badge status-active">✅ Mobile Responsive</span>
            <span class="status-badge status-premium">✨ Premium Features</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application"""
    
    # Initialize session state
    if 'active_page' not in st.session_state:
        st.session_state.active_page = "overview"
    
    # Apply styles
    apply_enterprise_styles()
    
    # Create sidebar
    create_sidebar_navigation()
    
    # Create header
    create_enterprise_header()
    
    # Main content based on active page
    if st.session_state.active_page == "overview":
        create_dashboard_overview()
    elif st.session_state.active_page == "analytics":
        st.markdown("## 📈 Analytics Dashboard")
        st.info("Analytics dashboard coming soon!")
    elif st.session_state.active_page == "contacts":
        st.markdown("## 👥 Contact Management")
        st.info("Contact management system coming soon!")
    elif st.session_state.active_page == "deals":
        st.markdown("## 🤝 Deal Pipeline")
        st.info("Deal pipeline management coming soon!")
    else:
        create_dashboard_overview()

if __name__ == "__main__":
    main()