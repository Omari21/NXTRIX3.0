"""
NXTRIX Platform - Enterprise CRM Application (Fixed Version)
Direct HTML embedding for reliable production deployment
"""

import streamlit as st

# Configure Streamlit page
st.set_page_config(
    page_title="NXTRIX - Enterprise CRM Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    """Main application entry point with reliable HTML rendering"""
    
    # Hide Streamlit UI elements and apply enterprise styling
    st.markdown("""
    <style>
    /* Hide Streamlit interface completely */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    .stDecoration {display: none;}
    .stToolbar {display: none;}
    
    /* Remove all padding and margins */
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: none !important;
    }
    
    .main {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Hide sidebar */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
    
    /* Enterprise CRM Styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body, html {
        font-family: 'Inter', sans-serif;
        background: #f8fafc;
        color: #1e293b;
        overflow-x: hidden;
    }
    
    .enterprise-container {
        display: flex;
        height: 100vh;
        width: 100vw;
        background: #f8fafc;
    }
    
    /* SIDEBAR */
    .enterprise-sidebar {
        width: 280px;
        background: #1e293b;
        color: white;
        display: flex;
        flex-direction: column;
        box-shadow: 4px 0 12px rgba(0,0,0,0.1);
        z-index: 1000;
    }
    
    .sidebar-header {
        padding: 24px 20px;
        border-bottom: 1px solid #334155;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    }
    
    .enterprise-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 20px;
        font-weight: 700;
        color: white;
    }
    
    .logo-icon {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 18px;
    }
    
    .nav-menu {
        flex: 1;
        padding: 24px 0;
        overflow-y: auto;
    }
    
    .nav-section {
        margin-bottom: 32px;
    }
    
    .nav-section-title {
        padding: 0 20px 12px;
        font-size: 11px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 20px;
        color: #cbd5e1;
        text-decoration: none;
        transition: all 0.2s;
        border-left: 3px solid transparent;
        cursor: pointer;
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
    
    .nav-icon {
        width: 20px;
        text-align: center;
    }
    
    /* MAIN CONTENT */
    .main-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    
    .top-bar {
        height: 72px;
        background: white;
        border-bottom: 1px solid #e2e8f0;
        padding: 0 32px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .breadcrumb {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #64748b;
        font-size: 14px;
    }
    
    .breadcrumb-item {
        color: #1e293b;
        font-weight: 500;
    }
    
    .content-area {
        flex: 1;
        padding: 32px;
        overflow-y: auto;
        background: #f8fafc;
    }
    
    .page-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 32px;
    }
    
    .page-title {
        font-size: 28px;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 24px;
        margin-bottom: 32px;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .metric-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
    }
    
    .metric-title {
        font-size: 14px;
        font-weight: 500;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 18px;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
    }
    
    .metric-change {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 14px;
        font-weight: 500;
    }
    
    .metric-change.positive {
        color: #059669;
    }
    
    .btn {
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        border: none;
        cursor: pointer;
        transition: all 0.2s;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        text-decoration: none;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
    }
    
    .status-indicator {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-active {
        background: #dcfce7;
        color: #059669;
    }
    
    .status-trial {
        background: #fef3c7;
        color: #d97706;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .enterprise-sidebar {
            width: 240px;
        }
        
        .content-area {
            padding: 20px;
        }
        
        .dashboard-grid {
            grid-template-columns: 1fr;
            gap: 16px;
        }
        
        .page-title {
            font-size: 24px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Enterprise CRM Interface
    st.markdown("""
    <div class="enterprise-container">
        <!-- SIDEBAR -->
        <div class="enterprise-sidebar">
            <div class="sidebar-header">
                <div class="enterprise-logo">
                    <div class="logo-icon">
                        <i class="fas fa-building"></i>
                    </div>
                    <span>NXTRIX</span>
                </div>
            </div>
            
            <nav class="nav-menu">
                <div class="nav-section">
                    <div class="nav-section-title">Dashboard</div>
                    <div class="nav-item active">
                        <i class="nav-icon fas fa-chart-line"></i>
                        <span>Overview</span>
                    </div>
                    <div class="nav-item">
                        <i class="nav-icon fas fa-chart-pie"></i>
                        <span>Analytics</span>
                    </div>
                </div>
                
                <div class="nav-section">
                    <div class="nav-section-title">CRM</div>
                    <div class="nav-item">
                        <i class="nav-icon fas fa-users"></i>
                        <span>Contacts</span>
                    </div>
                    <div class="nav-item">
                        <i class="nav-icon fas fa-handshake"></i>
                        <span>Deals</span>
                    </div>
                    <div class="nav-item">
                        <i class="nav-icon fas fa-building"></i>
                        <span>Companies</span>
                    </div>
                    <div class="nav-item">
                        <i class="nav-icon fas fa-tasks"></i>
                        <span>Activities</span>
                    </div>
                </div>
                
                <div class="nav-section">
                    <div class="nav-section-title">Real Estate</div>
                    <div class="nav-item">
                        <i class="nav-icon fas fa-home"></i>
                        <span>Properties</span>
                    </div>
                    <div class="nav-item">
                        <i class="nav-icon fas fa-chart-bar"></i>
                        <span>Portfolio</span>
                    </div>
                    <div class="nav-item">
                        <i class="nav-icon fas fa-calculator"></i>
                        <span>Financial Modeling</span>
                    </div>
                </div>
                
                <div class="nav-section">
                    <div class="nav-section-title">Automation</div>
                    <div class="nav-item">
                        <i class="nav-icon fas fa-robot"></i>
                        <span>Workflows</span>
                    </div>
                    <div class="nav-item">
                        <i class="nav-icon fas fa-envelope"></i>
                        <span>Email Campaigns</span>
                    </div>
                    <div class="nav-item">
                        <i class="nav-icon fas fa-brain"></i>
                        <span>AI Insights</span>
                    </div>
                </div>
            </nav>
        </div>
        
        <!-- MAIN CONTENT -->
        <div class="main-content">
            <div class="top-bar">
                <div class="breadcrumb">
                    <span>Dashboard</span>
                    <i class="fas fa-chevron-right"></i>
                    <span class="breadcrumb-item">Overview</span>
                </div>
                <div>
                    <span class="status-indicator status-trial">7-Day Trial</span>
                </div>
            </div>
            
            <div class="content-area">
                <div class="page-header">
                    <h1 class="page-title">Dashboard Overview</h1>
                    <button class="btn">
                        <i class="fas fa-plus"></i>
                        New Deal
                    </button>
                </div>
                
                <div class="dashboard-grid">
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">Total Revenue</span>
                            <div class="metric-icon" style="background: linear-gradient(135deg, #059669, #047857);">
                                <i class="fas fa-dollar-sign"></i>
                            </div>
                        </div>
                        <div class="metric-value">$2.4M</div>
                        <div class="metric-change positive">
                            <i class="fas fa-arrow-up"></i>
                            <span>+12.5% vs last month</span>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">Active Deals</span>
                            <div class="metric-icon" style="background: linear-gradient(135deg, #3b82f6, #1d4ed8);">
                                <i class="fas fa-handshake"></i>
                            </div>
                        </div>
                        <div class="metric-value">47</div>
                        <div class="metric-change positive">
                            <i class="fas fa-arrow-up"></i>
                            <span>+8.2% vs last month</span>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">Properties</span>
                            <div class="metric-icon" style="background: linear-gradient(135deg, #8b5cf6, #7c3aed);">
                                <i class="fas fa-home"></i>
                            </div>
                        </div>
                        <div class="metric-value">23</div>
                        <div class="metric-change positive">
                            <i class="fas fa-arrow-up"></i>
                            <span>+15.8% vs last month</span>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">Conversion Rate</span>
                            <div class="metric-icon" style="background: linear-gradient(135deg, #f59e0b, #d97706);">
                                <i class="fas fa-percentage"></i>
                            </div>
                        </div>
                        <div class="metric-value">24.5%</div>
                        <div class="metric-change positive">
                            <i class="fas fa-arrow-up"></i>
                            <span>+3.2% vs last month</span>
                        </div>
                    </div>
                </div>
                
                <div style="background: white; border-radius: 12px; padding: 24px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <h3 style="margin-bottom: 20px; color: #1e293b;">🎯 Welcome to NXTRIX Enterprise CRM</h3>
                    <p style="color: #64748b; margin-bottom: 16px;">Your professional real estate investment platform is now running with enterprise-grade interface design.</p>
                    <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                        <span class="status-indicator status-active">✅ Production Ready</span>
                        <span class="status-indicator status-active">✅ Enterprise Design</span>
                        <span class="status-indicator status-active">✅ Mobile Responsive</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()