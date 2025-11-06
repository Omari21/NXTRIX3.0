"""
NXTRIX Platform - Enterprise CRM Interface
Modern SaaS design inspired by Salesforce, Monday.com, and HubSpot
"""

import streamlit as st
import streamlit.components.v1 as components

def create_enterprise_app():
    """Create enterprise-grade CRM interface"""
    
    # Hide Streamlit elements completely
    st.markdown("""
    <style>
    /* Hide all Streamlit UI elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    .stDecoration {display: none;}
    
    /* Remove Streamlit padding */
    .main .block-container {
        padding-top: 0;
        padding-bottom: 0;
        padding-left: 0;
        padding-right: 0;
        max-width: none;
    }
    
    /* Full viewport */
    .main {
        background: #f8fafc;
        min-height: 100vh;
        padding: 0;
        margin: 0;
    }
    
    /* Hide Streamlit default elements */
    .stApp > div:first-child {
        display: none;
    }
    
    iframe {
        border: none;
        width: 100vw !important;
        height: 100vh !important;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 999999;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Enterprise CRM HTML
    enterprise_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NXTRIX - Enterprise CRM Platform</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', sans-serif;
                background: #f8fafc;
                color: #1e293b;
                overflow-x: hidden;
            }
            
            /* ============================================
               ENTERPRISE LAYOUT SYSTEM
               ============================================ */
            
            .app-container {
                display: flex;
                height: 100vh;
                width: 100vw;
            }
            
            /* SIDEBAR - Like Salesforce */
            .sidebar {
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
            
            .logo {
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
            
            .user-profile {
                padding: 20px;
                border-top: 1px solid #334155;
                background: rgba(15, 23, 42, 0.5);
            }
            
            .user-info {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .user-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 600;
            }
            
            .user-details h4 {
                font-size: 14px;
                color: white;
                margin-bottom: 2px;
            }
            
            .user-details p {
                font-size: 12px;
                color: #94a3b8;
            }
            
            /* MAIN CONTENT AREA */
            .main-content {
                flex: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            /* TOP BAR - Like Monday.com */
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
            
            .top-actions {
                display: flex;
                align-items: center;
                gap: 16px;
            }
            
            .search-box {
                position: relative;
                width: 320px;
            }
            
            .search-input {
                width: 100%;
                padding: 10px 16px 10px 40px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                background: #f8fafc;
                transition: all 0.2s;
            }
            
            .search-input:focus {
                outline: none;
                border-color: #3b82f6;
                background: white;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            .search-icon {
                position: absolute;
                left: 12px;
                top: 50%;
                transform: translateY(-50%);
                color: #94a3b8;
            }
            
            .notification-btn, .profile-btn {
                width: 40px;
                height: 40px;
                border: none;
                background: none;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #64748b;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .notification-btn:hover, .profile-btn:hover {
                background: #f1f5f9;
                color: #1e293b;
            }
            
            /* CONTENT AREA */
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
            
            .page-actions {
                display: flex;
                gap: 12px;
            }
            
            .btn {
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                border: none;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 8px;
                text-decoration: none;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                color: white;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }
            
            .btn-primary:hover {
                transform: translateY(-1px);
                box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
            }
            
            .btn-secondary {
                background: white;
                color: #64748b;
                border: 1px solid #e2e8f0;
            }
            
            .btn-secondary:hover {
                background: #f8fafc;
                border-color: #cbd5e1;
            }
            
            /* DASHBOARD GRID */
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
            
            .metric-change.negative {
                color: #dc2626;
            }
            
            /* DATA TABLE - Like HubSpot */
            .data-table-container {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
            
            .table-header {
                padding: 20px 24px;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .table-title {
                font-size: 18px;
                font-weight: 600;
                color: #1e293b;
            }
            
            .table-filters {
                display: flex;
                gap: 12px;
            }
            
            .filter-btn {
                padding: 8px 16px;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background: white;
                color: #64748b;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .filter-btn:hover, .filter-btn.active {
                background: #3b82f6;
                color: white;
                border-color: #3b82f6;
            }
            
            .data-table {
                width: 100%;
                border-collapse: collapse;
            }
            
            .data-table th {
                background: #f8fafc;
                padding: 16px 24px;
                text-align: left;
                font-size: 12px;
                font-weight: 600;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                border-bottom: 1px solid #e2e8f0;
            }
            
            .data-table td {
                padding: 16px 24px;
                border-bottom: 1px solid #f1f5f9;
                color: #1e293b;
                font-size: 14px;
            }
            
            .data-table tr:hover {
                background: #f8fafc;
            }
            
            .status-badge {
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
            
            .status-pending {
                background: #fef3c7;
                color: #d97706;
            }
            
            .status-closed {
                background: #fee2e2;
                color: #dc2626;
            }
            
            /* RESPONSIVE */
            @media (max-width: 1024px) {
                .sidebar {
                    width: 240px;
                }
                
                .content-area {
                    padding: 24px 20px;
                }
                
                .dashboard-grid {
                    grid-template-columns: 1fr;
                    gap: 16px;
                }
            }
            
            @media (max-width: 768px) {
                .sidebar {
                    transform: translateX(-100%);
                    position: fixed;
                    z-index: 1000;
                }
                
                .top-bar {
                    padding: 0 20px;
                }
                
                .search-box {
                    width: 200px;
                }
                
                .page-header {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 16px;
                }
                
                .page-title {
                    font-size: 24px;
                }
            }
        </style>
    </head>
    <body>
        <div class="app-container">
            <!-- SIDEBAR -->
            <div class="sidebar">
                <div class="sidebar-header">
                    <div class="logo">
                        <div class="logo-icon">
                            <i class="fas fa-building"></i>
                        </div>
                        <span>NXTRIX</span>
                    </div>
                </div>
                
                <nav class="nav-menu">
                    <div class="nav-section">
                        <div class="nav-section-title">Dashboard</div>
                        <a href="#" class="nav-item active">
                            <i class="nav-icon fas fa-chart-line"></i>
                            <span>Overview</span>
                        </a>
                        <a href="#" class="nav-item">
                            <i class="nav-icon fas fa-chart-pie"></i>
                            <span>Analytics</span>
                        </a>
                    </div>
                    
                    <div class="nav-section">
                        <div class="nav-section-title">CRM</div>
                        <a href="#" class="nav-item">
                            <i class="nav-icon fas fa-users"></i>
                            <span>Contacts</span>
                        </a>
                        <a href="#" class="nav-item">
                            <i class="nav-icon fas fa-handshake"></i>
                            <span>Deals</span>
                        </a>
                        <a href="#" class="nav-item">
                            <i class="nav-icon fas fa-building"></i>
                            <span>Companies</span>
                        </a>
                        <a href="#" class="nav-item">
                            <i class="nav-icon fas fa-tasks"></i>
                            <span>Activities</span>
                        </a>
                    </div>
                    
                    <div class="nav-section">
                        <div class="nav-section-title">Real Estate</div>
                        <a href="#" class="nav-item">
                            <i class="nav-icon fas fa-home"></i>
                            <span>Properties</span>
                        </a>
                        <a href="#" class="nav-item">
                            <i class="nav-icon fas fa-chart-bar"></i>
                            <span>Portfolio</span>
                        </a>
                        <a href="#" class="nav-item">
                            <i class="nav-icon fas fa-calculator"></i>
                            <span>Financial Modeling</span>
                        </a>
                    </div>
                    
                    <div class="nav-section">
                        <div class="nav-section-title">Automation</div>
                        <a href="#" class="nav-item">
                            <i class="nav-icon fas fa-robot"></i>
                            <span>Workflows</span>
                        </a>
                        <a href="#" class="nav-item">
                            <i class="nav-icon fas fa-envelope"></i>
                            <span>Email Campaigns</span>
                        </a>
                        <a href="#" class="nav-item">
                            <i class="nav-icon fas fa-brain"></i>
                            <span>AI Insights</span>
                        </a>
                    </div>
                </nav>
                
                <div class="user-profile">
                    <div class="user-info">
                        <div class="user-avatar">JD</div>
                        <div class="user-details">
                            <h4>John Doe</h4>
                            <p>Premium Plan</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- MAIN CONTENT -->
            <div class="main-content">
                <!-- TOP BAR -->
                <div class="top-bar">
                    <div class="breadcrumb">
                        <span>Dashboard</span>
                        <i class="fas fa-chevron-right"></i>
                        <span class="breadcrumb-item">Overview</span>
                    </div>
                    
                    <div class="top-actions">
                        <div class="search-box">
                            <i class="fas fa-search search-icon"></i>
                            <input type="text" class="search-input" placeholder="Search contacts, deals, properties...">
                        </div>
                        <button class="notification-btn">
                            <i class="fas fa-bell"></i>
                        </button>
                        <button class="profile-btn">
                            <i class="fas fa-user"></i>
                        </button>
                    </div>
                </div>
                
                <!-- CONTENT AREA -->
                <div class="content-area">
                    <div class="page-header">
                        <h1 class="page-title">Dashboard Overview</h1>
                        <div class="page-actions">
                            <button class="btn btn-secondary">
                                <i class="fas fa-download"></i>
                                Export
                            </button>
                            <button class="btn btn-primary">
                                <i class="fas fa-plus"></i>
                                New Deal
                            </button>
                        </div>
                    </div>
                    
                    <!-- METRICS DASHBOARD -->
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
                                <span>+12.5%</span>
                                <span style="color: #64748b; margin-left: 4px;">vs last month</span>
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
                                <span>+8.2%</span>
                                <span style="color: #64748b; margin-left: 4px;">vs last month</span>
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
                                <span>+15.8%</span>
                                <span style="color: #64748b; margin-left: 4px;">vs last month</span>
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
                            <div class="metric-change negative">
                                <i class="fas fa-arrow-down"></i>
                                <span>-2.1%</span>
                                <span style="color: #64748b; margin-left: 4px;">vs last month</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- DATA TABLE -->
                    <div class="data-table-container">
                        <div class="table-header">
                            <h3 class="table-title">Recent Deals</h3>
                            <div class="table-filters">
                                <button class="filter-btn active">All</button>
                                <button class="filter-btn">Active</button>
                                <button class="filter-btn">Pending</button>
                                <button class="filter-btn">Closed</button>
                            </div>
                        </div>
                        
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Deal Name</th>
                                    <th>Contact</th>
                                    <th>Property</th>
                                    <th>Value</th>
                                    <th>Stage</th>
                                    <th>Close Date</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>Downtown Condo Investment</strong></td>
                                    <td>Sarah Johnson</td>
                                    <td>123 Main St, Unit 4B</td>
                                    <td><strong>$450,000</strong></td>
                                    <td>Negotiation</td>
                                    <td>Dec 15, 2025</td>
                                    <td><span class="status-badge status-active">Active</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Office Building Acquisition</strong></td>
                                    <td>Michael Chen</td>
                                    <td>789 Business Ave</td>
                                    <td><strong>$2,100,000</strong></td>
                                    <td>Due Diligence</td>
                                    <td>Jan 30, 2026</td>
                                    <td><span class="status-badge status-active">Active</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Retail Space Investment</strong></td>
                                    <td>Emma Davis</td>
                                    <td>456 Shopping Center</td>
                                    <td><strong>$780,000</strong></td>
                                    <td>Proposal</td>
                                    <td>Dec 20, 2025</td>
                                    <td><span class="status-badge status-pending">Pending</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Warehouse Development</strong></td>
                                    <td>Robert Wilson</td>
                                    <td>321 Industrial Blvd</td>
                                    <td><strong>$3,500,000</strong></td>
                                    <td>Closed Won</td>
                                    <td>Nov 15, 2025</td>
                                    <td><span class="status-badge status-closed">Closed</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Luxury Apartment Complex</strong></td>
                                    <td>Jennifer Lee</td>
                                    <td>567 Luxury Lane</td>
                                    <td><strong>$1,250,000</strong></td>
                                    <td>Qualification</td>
                                    <td>Feb 28, 2026</td>
                                    <td><span class="status-badge status-active">Active</span></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Add interactivity
            document.addEventListener('DOMContentLoaded', function() {
                // Navigation items
                const navItems = document.querySelectorAll('.nav-item');
                navItems.forEach(item => {
                    item.addEventListener('click', function(e) {
                        e.preventDefault();
                        navItems.forEach(nav => nav.classList.remove('active'));
                        this.classList.add('active');
                    });
                });
                
                // Filter buttons
                const filterBtns = document.querySelectorAll('.filter-btn');
                filterBtns.forEach(btn => {
                    btn.addEventListener('click', function() {
                        filterBtns.forEach(filter => filter.classList.remove('active'));
                        this.classList.add('active');
                    });
                });
                
                // Search functionality
                const searchInput = document.querySelector('.search-input');
                searchInput.addEventListener('focus', function() {
                    this.parentElement.style.transform = 'scale(1.02)';
                });
                
                searchInput.addEventListener('blur', function() {
                    this.parentElement.style.transform = 'scale(1)';
                });
                
                // Notification animation
                const notificationBtn = document.querySelector('.notification-btn');
                setInterval(() => {
                    notificationBtn.style.animation = 'pulse 1s ease-in-out';
                    setTimeout(() => {
                        notificationBtn.style.animation = '';
                    }, 1000);
                }, 30000);
            });
        </script>
    </body>
    </html>
    """
    
    # Render the enterprise interface
    components.html(enterprise_html, height=800, scrolling=False)

# Apply the enterprise interface
create_enterprise_app()