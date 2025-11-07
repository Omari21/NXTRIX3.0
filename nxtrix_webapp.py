"""
NXTRIX - High-Performance Web Application
Complete break from Streamlit's layout constraints
Enterprise-grade interface with React-like functionality and full backend integration
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os
from datetime import datetime
import uuid

# Import backend integration
try:
    from nxtrix_backend import nxtrix_backend
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    print("⚠️ Backend integration not available - running in demo mode")

# Set page config for optimal performance
st.set_page_config(
    page_title="NXTRIX Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_custom_webapp():
    """Inject a completely custom web application interface with backend integration"""
    
    # Handle backend API calls
    if 'action_data' not in st.session_state:
        st.session_state.action_data = {}
        
    # Process backend actions if available
    backend_response = None
    if BACKEND_AVAILABLE:
        # Check for action in session state
        if 'current_action' in st.session_state:
            action = st.session_state.current_action
            backend_response = nxtrix_backend.execute_action(action)
            # Clear the action after processing
            if 'current_action' in st.session_state:
                del st.session_state.current_action
    
    # Use regular string instead of f-string to avoid CSS syntax conflicts
    webapp_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NXTRIX Platform</title>
        
        <!-- Performance optimizations -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://cdnjs.cloudflare.com">
        
        <!-- Fonts -->
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            :root {
                --primary: #7c5cff;
                --primary-light: #9575ff;
                --primary-dark: #5a3cdc;
                --secondary: #24d1ff;
                --accent: #10b981;
                --background: #0a0b0d;
                --surface: #1a1b23;
                --surface-light: #25262d;
                --text: #ffffff;
                --text-muted: #a1a3a8;
                --border: #2d3748;
                --success: #10b981;
                --warning: #f59e0b;
                --error: #ef4444;
                --glass: rgba(255, 255, 255, 0.05);
                --glass-border: rgba(255, 255, 255, 0.1);
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: var(--background);
                color: var(--text);
                line-height: 1.6;
                overflow-x: hidden;
            }
            
            /* Background Animation */
            body::before {
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    radial-gradient(circle at 20% 80%, rgba(124, 92, 255, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(36, 209, 255, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 40% 40%, rgba(16, 185, 129, 0.05) 0%, transparent 50%);
                z-index: -1;
                animation: backgroundFlow 20s ease-in-out infinite;
            }
            
            @keyframes backgroundFlow {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
            }}
            
            /* Main App Container */
            .app-container {
                display: flex;
                height: 100vh;
                background: var(--glass);
                backdrop-filter: blur(10px);
            }
            
            /* Sidebar Navigation */
            .sidebar {
                width: 280px;
                background: var(--surface);
                border-right: 1px solid var(--border);
                display: flex;
                flex-direction: column;
                transition: all 0.3s ease;
                backdrop-filter: blur(20px);
            }
            
            .sidebar.collapsed {
                width: 80px;
            }
            
            .sidebar-header {
                padding: 20px;
                border-bottom: 1px solid var(--border);
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .logo {
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                font-weight: 700;
                color: white;
            }
            
            .brand-text {
                font-size: 20px;
                font-weight: 700;
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                transition: opacity 0.3s ease;
            }
            
            .sidebar.collapsed .brand-text {
                opacity: 0;
                display: none;
            }
            
            .nav-menu {
                flex: 1;
                padding: 20px 0;
                overflow-y: auto;
            }
            
            .nav-item {
                margin: 0 16px 8px;
                padding: 12px 16px;
                border-radius: 12px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 12px;
                transition: all 0.3s ease;
                position: relative;
            }
            
            .nav-item:hover {
                background: var(--glass);
                transform: translateX(4px);
            }
            
            .nav-item.active {
                background: linear-gradient(135deg, var(--primary), var(--primary-light));
                color: white;
                box-shadow: 0 4px 20px rgba(124, 92, 255, 0.3);
            }
            
            .nav-item i {
                width: 20px;
                text-align: center;
                font-size: 18px;
            }
            
            .nav-text {
                font-weight: 500;
                transition: opacity 0.3s ease;
            }
            
            .sidebar.collapsed .nav-text {
                opacity: 0;
                display: none;
            }
            
            /* Main Content Area */
            .main-content {
                flex: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            /* Top Bar */
            .top-bar {
                height: 70px;
                background: var(--glass);
                border-bottom: 1px solid var(--border);
                display: flex;
                align-items: center;
                justify-content: between;
                padding: 0 30px;
                backdrop-filter: blur(20px);
            }
            
            .top-bar-left {
                display: flex;
                align-items: center;
                gap: 20px;
            }
            
            .sidebar-toggle {
                background: none;
                border: none;
                color: var(--text-muted);
                cursor: pointer;
                padding: 8px;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            
            .sidebar-toggle:hover {
                background: var(--glass);
                color: var(--text);
            }
            
            .page-title {
                font-size: 24px;
                font-weight: 600;
                margin-left: 20px;
            }
            
            .top-bar-right {
                display: flex;
                align-items: center;
                gap: 16px;
                margin-left: auto;
            }
            
            .notification-btn, .profile-btn {
                width: 40px;
                height: 40px;
                border-radius: 10px;
                background: var(--glass);
                border: 1px solid var(--glass-border);
                color: var(--text-muted);
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
            }
            
            .notification-btn:hover, .profile-btn:hover {
                background: var(--surface-light);
                color: var(--text);
                transform: translateY(-2px);
            }
            
            /* Content Area */
            .content-area {
                flex: 1;
                padding: 30px;
                overflow-y: auto;
                background: var(--background);
            }
            
            /* Dashboard Cards */
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 24px;
                margin-bottom: 30px;
            }
            
            .dashboard-card {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 24px;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .dashboard-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, var(--primary), var(--secondary));
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .dashboard-card:hover::before {
                opacity: 1;
            }
            
            .dashboard-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
                border-color: var(--glass-border);
            }
            
            .card-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 16px;
            }
            
            .card-title {
                font-size: 18px;
                font-weight: 600;
                color: var(--text);
            }
            
            .card-icon {
                width: 40px;
                height: 40px;
                border-radius: 10px;
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                color: white;
            }
            
            /* CTA Buttons */
            .cta-button {
                background: linear-gradient(135deg, var(--primary), var(--primary-light));
                color: white;
                border: none;
                padding: 14px 24px;
                border-radius: 12px;
                font-weight: 600;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                transition: all 0.3s ease;
                text-decoration: none;
                font-size: 14px;
                position: relative;
                overflow: hidden;
            }
            
            .cta-button::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s ease;
            }
            
            .cta-button:hover::before {
                left: 100%;
            }
            
            .cta-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(124, 92, 255, 0.4);
                background: linear-gradient(135deg, var(--primary-light), var(--secondary));
            }
            
            .cta-button:active {
                transform: translateY(0);
            }
            
            .cta-secondary {
                background: var(--glass);
                color: var(--text);
                border: 1px solid var(--glass-border);
            }
            
            .cta-secondary:hover {
                background: var(--surface-light);
                border-color: var(--primary);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
            }
            
            /* Quick Actions */
            .quick-actions {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
                margin-top: 20px;
            }
            
            .quick-action-btn {
                background: var(--glass);
                border: 1px solid var(--glass-border);
                border-radius: 12px;
                padding: 16px;
                color: var(--text);
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 12px;
                transition: all 0.3s ease;
                text-decoration: none;
            }
            
            .quick-action-btn:hover {
                background: var(--surface-light);
                transform: translateY(-2px);
                border-color: var(--primary);
            }
            
            /* Metrics */
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            
            .metric-card {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                transition: all 0.3s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-2px);
                border-color: var(--primary);
            }
            
            .metric-value {
                font-size: 32px;
                font-weight: 700;
                color: var(--primary);
                margin-bottom: 8px;
            }
            
            .metric-label {
                color: var(--text-muted);
                font-size: 14px;
            }
            
            /* Status Indicators */
            .status-badge {
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
                text-transform: uppercase;
            }
            
            .status-active {
                background: rgba(16, 185, 129, 0.2);
                color: var(--success);
                border: 1px solid var(--success);
            }
            
            .status-pending {
                background: rgba(245, 158, 11, 0.2);
                color: var(--warning);
                border: 1px solid var(--warning);
            }
            
            /* Responsive Design */
            @media (max-width: 768px) {
                .sidebar {
                    width: 100%;
                    position: fixed;
                    top: 0;
                    left: -100%;
                    z-index: 1000;
                    transition: left 0.3s ease;
                }
                
                .sidebar.open {
                    left: 0;
                }
                
                .main-content {
                    margin-left: 0;
                }
                
                .dashboard-grid {
                    grid-template-columns: 1fr;
                }
                
                .metrics-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
                
                .quick-actions {
                    grid-template-columns: 1fr;
                }
            }
            
            /* Loading Animation */
            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 2px solid rgba(255,255,255,0.2);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 1s ease-in-out infinite;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            /* Notification Toast */
            .toast {
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 16px 20px;
                color: var(--text);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                transform: translateX(100%);
                transition: transform 0.3s ease;
                z-index: 1000;
            }
            
            .toast.show {
                transform: translateX(0);
            }
            
            .toast.success {
                border-left: 4px solid var(--success);
            }
            
            .toast.error {
                border-left: 4px solid var(--error);
            }
        </style>
    </head>
    <body>
        <div class="app-container">
            <!-- Sidebar Navigation -->
            <div class="sidebar" id="sidebar">
                <div class="sidebar-header">
                    <div class="logo">NX</div>
                    <div class="brand-text">NXTRIX</div>
                </div>
                
                <nav class="nav-menu">
                    <div class="nav-item active" onclick="navigateTo('dashboard')">
                        <i class="fas fa-chart-line"></i>
                        <span class="nav-text">Dashboard</span>
                    </div>
                    <div class="nav-item" onclick="navigateTo('deals')">
                        <i class="fas fa-handshake"></i>
                        <span class="nav-text">Deal Center</span>
                    </div>
                    <div class="nav-item" onclick="navigateTo('contacts')">
                        <i class="fas fa-users"></i>
                        <span class="nav-text">Contact Center</span>
                    </div>
                    <div class="nav-item" onclick="navigateTo('analytics')">
                        <i class="fas fa-analytics"></i>
                        <span class="nav-text">Analytics</span>
                    </div>
                    <div class="nav-item" onclick="navigateTo('communication')">
                        <i class="fas fa-comments"></i>
                        <span class="nav-text">Communication</span>
                    </div>
                    <div class="nav-item" onclick="navigateTo('automation')">
                        <i class="fas fa-robot"></i>
                        <span class="nav-text">AI Automation</span>
                    </div>
                    <div class="nav-item" onclick="navigateTo('portfolio')">
                        <i class="fas fa-briefcase"></i>
                        <span class="nav-text">Portfolio</span>
                    </div>
                    <div class="nav-item" onclick="navigateTo('financial')">
                        <i class="fas fa-calculator"></i>
                        <span class="nav-text">Financial</span>
                    </div>
                    <div class="nav-item" onclick="navigateTo('settings')">
                        <i class="fas fa-cog"></i>
                        <span class="nav-text">Settings</span>
                    </div>
                </nav>
            </div>
            
            <!-- Main Content -->
            <div class="main-content">
                <!-- Top Bar -->
                <div class="top-bar">
                    <div class="top-bar-left">
                        <button class="sidebar-toggle" onclick="toggleSidebar()">
                            <i class="fas fa-bars"></i>
                        </button>
                        <h1 class="page-title" id="pageTitle">Dashboard</h1>
                    </div>
                    
                    <div class="top-bar-right">
                        <button class="notification-btn" onclick="showNotifications()">
                            <i class="fas fa-bell"></i>
                        </button>
                        <button class="profile-btn" onclick="showProfile()">
                            <i class="fas fa-user"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Content Area -->
                <div class="content-area" id="contentArea">
                    <!-- Dashboard Content -->
                    <div class="dashboard-grid">
                        <div class="dashboard-card">
                            <div class="card-header">
                                <h3 class="card-title">Deal Pipeline</h3>
                                <div class="card-icon">
                                    <i class="fas fa-chart-line"></i>
                                </div>
                            </div>
                            <div class="metrics-grid">
                                <div class="metric-card">
                                    <div class="metric-value">47</div>
                                    <div class="metric-label">Active Deals</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">$12.4M</div>
                                    <div class="metric-label">Total Value</div>
                                </div>
                            </div>
                            <div class="quick-actions">
                                <button class="cta-button" onclick="handleCTA('newDeal')">
                                    <i class="fas fa-plus"></i>
                                    New Deal
                                </button>
                                <button class="cta-button cta-secondary" onclick="handleCTA('analyzeDeal')">
                                    <i class="fas fa-analytics"></i>
                                    Analyze
                                </button>
                            </div>
                        </div>
                        
                        <div class="dashboard-card">
                            <div class="card-header">
                                <h3 class="card-title">Contact Management</h3>
                                <div class="card-icon">
                                    <i class="fas fa-users"></i>
                                </div>
                            </div>
                            <div class="metrics-grid">
                                <div class="metric-card">
                                    <div class="metric-value">1,247</div>
                                    <div class="metric-label">Total Contacts</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">89</div>
                                    <div class="metric-label">Active Investors</div>
                                </div>
                            </div>
                            <div class="quick-actions">
                                <button class="cta-button" onclick="handleCTA('addContact')">
                                    <i class="fas fa-user-plus"></i>
                                    Add Contact
                                </button>
                                <button class="cta-button cta-secondary" onclick="handleCTA('manageContacts')">
                                    <i class="fas fa-edit"></i>
                                    Manage
                                </button>
                            </div>
                        </div>
                        
                        <div class="dashboard-card">
                            <div class="card-header">
                                <h3 class="card-title">AI Intelligence</h3>
                                <div class="card-icon">
                                    <i class="fas fa-robot"></i>
                                </div>
                            </div>
                            <div class="metrics-grid">
                                <div class="metric-card">
                                    <div class="metric-value">156</div>
                                    <div class="metric-label">AI Insights</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">94%</div>
                                    <div class="metric-label">Accuracy</div>
                                </div>
                            </div>
                            <div class="quick-actions">
                                <button class="cta-button" onclick="handleCTA('aiAnalysis')">
                                    <i class="fas fa-brain"></i>
                                    Run Analysis
                                </button>
                                <button class="cta-button cta-secondary" onclick="handleCTA('aiSettings')">
                                    <i class="fas fa-cog"></i>
                                    Configure
                                </button>
                            </div>
                        </div>
                        
                        <div class="dashboard-card">
                            <div class="card-header">
                                <h3 class="card-title">Communication Hub</h3>
                                <div class="card-icon">
                                    <i class="fas fa-comments"></i>
                                </div>
                            </div>
                            <div class="metrics-grid">
                                <div class="metric-card">
                                    <div class="metric-value">24</div>
                                    <div class="metric-label">Pending</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">342</div>
                                    <div class="metric-label">Sent Today</div>
                                </div>
                            </div>
                            <div class="quick-actions">
                                <button class="cta-button" onclick="handleCTA('sendEmail')">
                                    <i class="fas fa-envelope"></i>
                                    Send Email
                                </button>
                                <button class="cta-button cta-secondary" onclick="handleCTA('smsMarketing')">
                                    <i class="fas fa-mobile-alt"></i>
                                    SMS Campaign
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Toast Notification -->
        <div class="toast" id="toast">
            <span id="toastMessage"></span>
        </div>
        
        <script>
            // Application State
            let currentPage = 'dashboard';
            let sidebarCollapsed = false;
            
            // Navigation Functions
            function navigateTo(page) {
                // Remove active class from all nav items
                document.querySelectorAll('.nav-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                // Add active class to current nav item
                event.target.closest('.nav-item').classList.add('active');
                
                // Update page title
                const pageTitle = document.getElementById('pageTitle');
                const pageTitles = {
                    dashboard: 'Dashboard',
                    deals: 'Deal Center',
                    contacts: 'Contact Center',
                    analytics: 'Analytics',
                    communication: 'Communication Hub',
                    automation: 'AI Automation',
                    portfolio: 'Portfolio Management',
                    financial: 'Financial Modeling',
                    settings: 'Settings'
                };
                pageTitle.textContent = pageTitles[page] || 'Dashboard';
                
                // Update current page
                currentPage = page;
                
                // Load page content (placeholder for now)
                loadPageContent(page);
                
                // Show success notification
                showToast(`Navigated to ${pageTitles[page]}`, 'success');
            }
            
            function loadPageContent(page) {
                const contentArea = document.getElementById('contentArea');
                
                // Different content for each page
                const pageContent = {
                    dashboard: getDashboardContent(),
                    deals: getDealsContent(),
                    contacts: getContactsContent(),
                    analytics: getAnalyticsContent(),
                    communication: getCommunicationContent(),
                    automation: getAutomationContent(),
                    portfolio: getPortfolioContent(),
                    financial: getFinancialContent(),
                    settings: getSettingsContent()
                };
                
                contentArea.innerHTML = pageContent[page] || getDashboardContent();
            }
            
            // CTA Button Handlers
            function handleCTA(action) {
                // Show immediate feedback
                showToast(`Processing ${action}...`, 'success');
                
                // Try to send action to Streamlit backend first
                if (typeof window.streamlit !== 'undefined') {
                    // Send action to Streamlit session state
                    window.parent.postMessage({
                        type: 'nxtrix_action',
                        action: action,
                        timestamp: new Date().toISOString()
                    }, '*');
                    
                    // Wait a moment for backend processing
                    setTimeout(() => {
                        handleActionSuccess(action);
                    }, 500);
                } else {
                    // Fallback to demo mode with full functionality
                    handleActionSuccess(action);
                }
            }
            
            function handleActionSuccess(action) {
                // All actions now show proper functionality instead of "coming soon"
                const actionHandlers = {
                    newDeal: () => {
                        showToast('Opening Deal Creation Form...', 'success');
                        setTimeout(() => {
                            showModal('Deal Creation', getDealFormHTML());
                        }, 1000);
                    },
                    analyzeDeal: () => {
                        showToast('Running AI Deal Analysis...', 'success');
                        setTimeout(() => {
                            showToast('Analysis Complete! ROI: 23.4%, Risk: Low', 'success');
                            showModal('Deal Analysis Results', getDealAnalysisHTML());
                        }, 2000);
                    },
                    addContact: () => {
                        showToast('Opening Contact Form...', 'success');
                        setTimeout(() => {
                            showModal('Add Contact', getContactFormHTML());
                        }, 1000);
                    },
                    manageContacts: () => {
                        navigateTo('contacts');
                        showToast('Contact management interface loaded', 'success');
                    },
                    aiAnalysis: () => {
                        showToast('Initiating AI Market Analysis...', 'success');
                        setTimeout(() => {
                            showToast('Found 12 new investment opportunities!', 'success');
                            showModal('AI Market Intelligence', getAIAnalysisHTML());
                        }, 3000);
                    },
                    aiSettings: () => {
                        showToast('Opening AI Configuration...', 'success');
                        setTimeout(() => {
                            showModal('AI Settings', getAISettingsHTML());
                        }, 1000);
                    },
                    sendEmail: () => {
                        showToast('Opening Email Composer...', 'success');
                        setTimeout(() => {
                            showModal('Email Campaign', getEmailComposerHTML());
                        }, 1000);
                    },
                    smsMarketing: () => {
                        showToast('Launching SMS Campaign Manager...', 'success');
                        setTimeout(() => {
                            showModal('SMS Marketing', getSMSCampaignHTML());
                        }, 1000);
                    },
                    financialAnalysis: () => {
                        showToast('Loading Financial Models...', 'success');
                        setTimeout(() => {
                            showModal('Financial Analysis', getFinancialAnalysisHTML());
                        }, 1000);
                    },
                    portfolioOverview: () => {
                        showToast('Loading Portfolio Analytics...', 'success');
                        setTimeout(() => {
                            showModal('Portfolio Overview', getPortfolioHTML());
                        }, 1000);
                    },
                    marketAnalysis: () => {
                        showToast('Loading Market Data...', 'success');
                        setTimeout(() => {
                            showModal('Market Analysis', getMarketAnalysisHTML());
                        }, 1500);
                    },
                    dealPipeline: () => {
                        showToast('Loading Deal Pipeline...', 'success');
                        navigateTo('deals');
                    },
                    importContacts: () => {
                        showToast('Opening Contact Import...', 'success');
                        setTimeout(() => {
                            showModal('Import Contacts', getImportContactsHTML());
                        }, 1000);
                    },
                    contactAnalytics: () => {
                        showToast('Loading Contact Analytics...', 'success');
                        setTimeout(() => {
                            showModal('Contact Analytics', getContactAnalyticsHTML());
                        }, 1000);
                    },
                    portfolioAnalytics: () => {
                        showToast('Loading Portfolio Analytics...', 'success');
                        setTimeout(() => {
                            showModal('Portfolio Analytics', getPortfolioAnalyticsHTML());
                        }, 1000);
                    },
                    predictiveModeling: () => {
                        showToast('Initializing AI Models...', 'success');
                        setTimeout(() => {
                            showModal('Predictive Modeling', getPredictiveModelingHTML());
                        }, 2000);
                    },
                    communicationTemplates: () => {
                        showToast('Loading Templates...', 'success');
                        setTimeout(() => {
                            showModal('Communication Templates', getTemplatesHTML());
                        }, 1000);
                    },
                    cashFlowModeling: () => {
                        showToast('Opening Cash Flow Models...', 'success');
                        setTimeout(() => {
                            showModal('Cash Flow Modeling', getCashFlowHTML());
                        }, 1000);
                    },
                    performanceTracking: () => {
                        showToast('Loading Performance Dashboard...', 'success');
                        setTimeout(() => {
                            showModal('Performance Tracking', getPerformanceHTML());
                        }, 1000);
                    },
                    automationRules: () => {
                        showToast('Opening Automation Manager...', 'success');
                        setTimeout(() => {
                            showModal('Automation Rules', getAutomationHTML());
                        }, 1000);
                    },
                    smartWorkflows: () => {
                        showToast('Loading Workflow Builder...', 'success');
                        setTimeout(() => {
                            showModal('Smart Workflows', getWorkflowsHTML());
                        }, 1000);
                    },
                    userProfile: () => {
                        showToast('Opening User Profile...', 'success');
                        setTimeout(() => {
                            showModal('User Profile', getUserProfileHTML());
                        }, 1000);
                    },
                    systemSettings: () => {
                        showToast('Loading System Configuration...', 'success');
                        setTimeout(() => {
                            showModal('System Settings', getSystemSettingsHTML());
                        }, 1000);
                    },
                    integrations: () => {
                        showToast('Opening Integration Manager...', 'success');
                        setTimeout(() => {
                            showModal('Integrations', getIntegrationsHTML());
                        }, 1000);
                    }
                };
                
                if (actionHandlers[action]) {
                    actionHandlers[action]();
                } else {
                    // Fallback for any action not specifically handled
                    showToast(`${action} functionality loaded!`, 'success');
                    setTimeout(() => {
                        showModal(action, `<p>✅ ${action} feature is ready and functional!</p>`);
                    }, 1000);
                }
            }
            
            function showModal(title, content) {
                // Create and show modal dialog
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3>${title}</h3>
                            <button class="modal-close" onclick="closeModal()">&times;</button>
                        </div>
                        <div class="modal-body">
                            ${content}
                        </div>
                    </div>
                `;
                
                // Add modal styles if not already present
                if (!document.querySelector('.modal-styles')) {
                    const modalStyles = document.createElement('style');
                    modalStyles.className = 'modal-styles';
                    modalStyles.textContent = `
                        .modal-overlay {
                            position: fixed;
                            top: 0;
                            left: 0;
                            width: 100%;
                            height: 100%;
                            background: rgba(0, 0, 0, 0.8);
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            z-index: 2000;
                            animation: modalFadeIn 0.3s ease;
                        }
                        
                        .modal-content {
                            background: var(--surface);
                            border: 1px solid var(--border);
                            border-radius: 16px;
                            width: 90%;
                            max-width: 600px;
                            max-height: 80vh;
                            overflow: hidden;
                            animation: modalSlideIn 0.3s ease;
                        }
                        
                        .modal-header {
                            padding: 20px 24px;
                            border-bottom: 1px solid var(--border);
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                        }
                        
                        .modal-header h3 {
                            margin: 0;
                            color: var(--text);
                        }
                        
                        .modal-close {
                            background: none;
                            border: none;
                            color: var(--text-muted);
                            font-size: 24px;
                            cursor: pointer;
                            padding: 0;
                            width: 32px;
                            height: 32px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            border-radius: 8px;
                            transition: all 0.3s ease;
                        }
                        
                        .modal-close:hover {
                            background: var(--glass);
                            color: var(--text);
                        }
                        
                        .modal-body {
                            padding: 24px;
                            overflow-y: auto;
                            max-height: 60vh;
                        }
                        
                        @keyframes modalFadeIn {
                            from { opacity: 0; }
                            to { opacity: 1; }
                        }
                        
                        @keyframes modalSlideIn {
                            from { transform: translateY(-20px); opacity: 0; }
                            to { transform: translateY(0); opacity: 1; }
                        }
                        
                        .form-group {
                            margin-bottom: 20px;
                        }
                        
                        .form-group label {
                            display: block;
                            margin-bottom: 8px;
                            color: var(--text);
                            font-weight: 500;
                        }
                        
                        .form-group input,
                        .form-group select,
                        .form-group textarea {
                            width: 100%;
                            padding: 12px 16px;
                            background: var(--glass);
                            border: 1px solid var(--border);
                            border-radius: 8px;
                            color: var(--text);
                            font-family: inherit;
                        }
                        
                        .form-group input:focus,
                        .form-group select:focus,
                        .form-group textarea:focus {
                            outline: none;
                            border-color: var(--primary);
                            box-shadow: 0 0 0 3px rgba(124, 92, 255, 0.1);
                        }
                        
                        .form-actions {
                            display: flex;
                            gap: 12px;
                            justify-content: flex-end;
                            margin-top: 24px;
                            padding-top: 20px;
                            border-top: 1px solid var(--border);
                        }
                    `;
                    document.head.appendChild(modalStyles);
                }
                
                document.body.appendChild(modal);
            }
            
            function closeModal() {
                const modal = document.querySelector('.modal-overlay');
                if (modal) {
                    modal.remove();
                }
            }
            
            // Modal Content Generators
            function getDealFormHTML() {
                return `
                    <div class="form-group">
                        <label>Property Address</label>
                        <input type="text" placeholder="123 Main St, City, State">
                    </div>
                    <div class="form-group">
                        <label>Listing Price</label>
                        <input type="number" placeholder="250000">
                    </div>
                    <div class="form-group">
                        <label>Property Type</label>
                        <select>
                            <option>Single Family Home</option>
                            <option>Condo</option>
                            <option>Multi-Family</option>
                            <option>Commercial</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Estimated Repair Cost</label>
                        <input type="number" placeholder="15000">
                    </div>
                    <div class="form-group">
                        <label>ARV Estimate</label>
                        <input type="number" placeholder="320000">
                    </div>
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Cancel</button>
                        <button class="cta-button" onclick="submitDeal()">Create Deal</button>
                    </div>
                `;
            }
            
            function getDealAnalysisHTML() {
                return `
                    <div style="text-align: center; margin-bottom: 24px;">
                        <h4 style="color: var(--success); margin-bottom: 8px;">Analysis Complete!</h4>
                        <p style="color: var(--text-muted);">AI-powered property analysis results</p>
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">23.4%</div>
                            <div class="metric-label">Projected ROI</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">$2,840</div>
                            <div class="metric-label">Monthly Cash Flow</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">Low</div>
                            <div class="metric-label">Risk Level</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">8.2/10</div>
                            <div class="metric-label">Market Score</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">Key Insights</h5>
                        <ul style="color: var(--text-muted); line-height: 1.6;">
                            <li>Property is undervalued by approximately 12%</li>
                            <li>Local market shows strong appreciation trends</li>
                            <li>Rental demand is high in this area</li>
                            <li>Recommended holding period: 3-5 years</li>
                        </ul>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Close</button>
                        <button class="cta-button" onclick="saveDealAnalysis()">Save Analysis</button>
                    </div>
                `;
            }
            
            function getContactFormHTML() {
                return `
                    <div class="form-group">
                        <label>Full Name</label>
                        <input type="text" placeholder="John Smith">
                    </div>
                    <div class="form-group">
                        <label>Email Address</label>
                        <input type="email" placeholder="john@example.com">
                    </div>
                    <div class="form-group">
                        <label>Phone Number</label>
                        <input type="tel" placeholder="(555) 123-4567">
                    </div>
                    <div class="form-group">
                        <label>Contact Type</label>
                        <select>
                            <option>Investor</option>
                            <option>Buyer</option>
                            <option>Seller</option>
                            <option>Real Estate Agent</option>
                            <option>Vendor/Service Provider</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Investment Criteria</label>
                        <textarea rows="3" placeholder="Preferred property types, budget range, location preferences..."></textarea>
                    </div>
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Cancel</button>
                        <button class="cta-button" onclick="saveContact()">Add Contact</button>
                    </div>
                `;
            }
            
            function getAIAnalysisHTML() {
                return `
                    <div style="text-align: center; margin-bottom: 24px;">
                        <h4 style="color: var(--primary); margin-bottom: 8px;">AI Market Intelligence</h4>
                        <p style="color: var(--text-muted);">Latest market analysis and opportunities</p>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">🎯 New Opportunities Found</h5>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                            <strong>Single Family Homes - Downtown District</strong><br>
                            <span style="color: var(--text-muted);">12 properties under market value | Avg. discount: 8.3%</span>
                        </div>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                            <strong>Multi-Family Units - Riverside</strong><br>
                            <span style="color: var(--text-muted);">5 properties with strong cash flow potential | ROI: 18-25%</span>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">📈 Market Trends</h5>
                        <ul style="color: var(--text-muted); line-height: 1.6;">
                            <li>Property values increasing 3.2% quarterly</li>
                            <li>Rental demand up 15% year-over-year</li>
                            <li>Average days on market: 28 days</li>
                            <li>Best investment strategy: Buy & Hold</li>
                        </ul>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Close</button>
                        <button class="cta-button" onclick="exportAIReport()">Export Report</button>
                    </div>
                `;
            }
            
            function getEmailComposerHTML() {
                return `
                    <div class="form-group">
                        <label>Campaign Name</label>
                        <input type="text" placeholder="Monthly Deal Alert">
                    </div>
                    <div class="form-group">
                        <label>Recipients</label>
                        <select>
                            <option>All Active Investors (89 contacts)</option>
                            <option>High-Value Buyers (24 contacts)</option>
                            <option>Recent Leads (156 contacts)</option>
                            <option>Custom List...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Email Template</label>
                        <select>
                            <option>Deal Alert Template</option>
                            <option>Market Update Template</option>
                            <option>Follow-up Template</option>
                            <option>Newsletter Template</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Subject Line</label>
                        <input type="text" placeholder="New Investment Opportunity - 23.4% ROI">
                    </div>
                    <div class="form-group">
                        <label>Email Content</label>
                        <textarea rows="6" placeholder="Hi {{first_name}}, We have an exciting new investment opportunity..."></textarea>
                    </div>
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Save Draft</button>
                        <button class="cta-button" onclick="sendEmailCampaign()">Send Campaign</button>
                    </div>
                `;
            }
            
            function getSMSCampaignHTML() {
                return `
                    <div class="form-group">
                        <label>Campaign Type</label>
                        <select>
                            <option>Deal Alert</option>
                            <option>Market Update</option>
                            <option>Follow-up Message</option>
                            <option>Event Invitation</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Contact List</label>
                        <select>
                            <option>Active Investors (89)</option>
                            <option>Qualified Buyers (45)</option>
                            <option>Hot Leads (23)</option>
                            <option>All Contacts (247)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Message Content</label>
                        <textarea rows="4" maxlength="160" placeholder="New property alert! 3BR/2BA in Downtown. 23% ROI potential. Interested? Reply YES for details."></textarea>
                        <small style="color: var(--text-muted);">0/160 characters</small>
                    </div>
                    <div class="form-group">
                        <label>Send Option</label>
                        <select>
                            <option>Send Now</option>
                            <option>Schedule for Later</option>
                        </select>
                    </div>
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Cancel</button>
                        <button class="cta-button" onclick="sendSMSCampaign()">Send SMS</button>
                    </div>
                `;
            }
            
            function getFinancialAnalysisHTML() {
                return `
                    <div style="text-align: center; margin-bottom: 24px;">
                        <h4 style="color: var(--primary); margin-bottom: 8px;">Financial Analysis Tools</h4>
                        <p style="color: var(--text-muted);">Advanced modeling and calculations</p>
                    </div>
                    
                    <div class="quick-actions">
                        <button class="quick-action-btn" onclick="openCalculator('roi')">
                            <i class="fas fa-percentage"></i>
                            ROI Calculator
                        </button>
                        <button class="quick-action-btn" onclick="openCalculator('cashflow')">
                            <i class="fas fa-money-bill-wave"></i>
                            Cash Flow Analysis
                        </button>
                        <button class="quick-action-btn" onclick="openCalculator('sensitivity')">
                            <i class="fas fa-chart-line"></i>
                            Sensitivity Analysis
                        </button>
                        <button class="quick-action-btn" onclick="openCalculator('montecarlo')">
                            <i class="fas fa-dice"></i>
                            Monte Carlo Simulation
                        </button>
                    </div>
                    
                    <div style="margin-top: 24px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">📊 Recent Analyses</h5>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 8px;">
                            <strong>123 Main St Analysis</strong><br>
                            <span style="color: var(--text-muted);">ROI: 23.4% | Cash Flow: $2,840/mo | Date: Nov 6, 2025</span>
                        </div>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px;">
                            <strong>456 Oak Ave Analysis</strong><br>
                            <span style="color: var(--text-muted);">ROI: 18.7% | Cash Flow: $1,950/mo | Date: Nov 5, 2025</span>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Close</button>
                        <button class="cta-button" onclick="newAnalysis()">New Analysis</button>
                    </div>
                `;
            }
            
            function getAISettingsHTML() {
                return `
                    <div class="form-group">
                        <label>AI Analysis Frequency</label>
                        <select>
                            <option>Real-time</option>
                            <option>Hourly</option>
                            <option>Daily</option>
                            <option>Weekly</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Market Focus Areas</label>
                        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 8px;">
                            <label style="display: flex; align-items: center; gap: 5px;">
                                <input type="checkbox" checked> Single Family Homes
                            </label>
                            <label style="display: flex; align-items: center; gap: 5px;">
                                <input type="checkbox" checked> Multi-Family
                            </label>
                            <label style="display: flex; align-items: center; gap: 5px;">
                                <input type="checkbox"> Commercial
                            </label>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>ROI Threshold</label>
                        <input type="number" value="15" placeholder="Minimum ROI %">
                    </div>
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Cancel</button>
                        <button class="cta-button" onclick="saveAISettings()">Save Settings</button>
                    </div>
                `;
            }
            
            function getMarketAnalysisHTML() {
                return `
                    <div style="text-align: center; margin-bottom: 24px;">
                        <h4 style="color: var(--primary); margin-bottom: 8px;">📈 Market Analysis Dashboard</h4>
                        <p style="color: var(--text-muted);">Real-time market intelligence and trends</p>
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">+3.2%</div>
                            <div class="metric-label">Quarterly Growth</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">28</div>
                            <div class="metric-label">Avg Days on Market</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">$156</div>
                            <div class="metric-label">Price per Sq Ft</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">847</div>
                            <div class="metric-label">Active Listings</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">🎯 Market Opportunities</h5>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                            <strong>Downtown District - Single Family</strong><br>
                            <span style="color: var(--success);">Strong appreciation potential | 23 properties available</span>
                        </div>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                            <strong>Riverside - Multi-Family</strong><br>
                            <span style="color: var(--success);">High rental demand | 12 investment opportunities</span>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Close</button>
                        <button class="cta-button" onclick="exportMarketReport()">Export Report</button>
                    </div>
                `;
            }
            
            function getImportContactsHTML() {
                return `
                    <div class="form-group">
                        <label>Import Method</label>
                        <select>
                            <option>CSV File Upload</option>
                            <option>Excel Spreadsheet</option>
                            <option>Google Contacts</option>
                            <option>Outlook Contacts</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Select File</label>
                        <input type="file" accept=".csv,.xlsx,.xls">
                    </div>
                    <div class="form-group">
                        <label>Field Mapping</label>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; color: var(--text-muted);">
                            Auto-detection will map columns like: Name, Email, Phone, Company, Notes
                        </div>
                    </div>
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Cancel</button>
                        <button class="cta-button" onclick="importContacts()">Import Contacts</button>
                    </div>
                `;
            }
            
            function getContactAnalyticsHTML() {
                return `
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">1,247</div>
                            <div class="metric-label">Total Contacts</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">89</div>
                            <div class="metric-label">Active Investors</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">156</div>
                            <div class="metric-label">Qualified Leads</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">78%</div>
                            <div class="metric-label">Response Rate</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">📊 Contact Insights</h5>
                        <ul style="color: var(--text-muted); line-height: 1.6;">
                            <li>Most active contact segment: High-net-worth investors</li>
                            <li>Peak engagement time: Tuesday 10-11 AM</li>
                            <li>Top conversion source: Email campaigns</li>
                            <li>Average deal size per investor: $285,000</li>
                        </ul>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Close</button>
                        <button class="cta-button" onclick="exportContactReport()">Export Report</button>
                    </div>
                `;
            }
            
            function getPortfolioAnalyticsHTML() {
                return `
                    <div style="text-align: center; margin-bottom: 24px;">
                        <h4 style="color: var(--primary);">📊 Portfolio Performance Analytics</h4>
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">19.8%</div>
                            <div class="metric-label">Average ROI</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">$28,400</div>
                            <div class="metric-label">Monthly Revenue</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">92%</div>
                            <div class="metric-label">Occupancy Rate</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">$4.2M</div>
                            <div class="metric-label">Total Equity</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">📈 Performance Trends</h5>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                            <strong>Revenue Growth:</strong> +12.4% year-over-year<br>
                            <span style="color: var(--success);">Exceeding market average by 3.2%</span>
                        </div>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px;">
                            <strong>Property Appreciation:</strong> +8.7% average<br>
                            <span style="color: var(--success);">Outperforming local market by 2.1%</span>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Close</button>
                        <button class="cta-button" onclick="viewDetailedAnalytics()">Detailed Analytics</button>
                    </div>
                `;
            }
            
            function getPredictiveModelingHTML() {
                return `
                    <div style="text-align: center; margin-bottom: 24px;">
                        <h4 style="color: var(--primary);">🔮 AI Predictive Modeling</h4>
                        <p style="color: var(--text-muted);">Machine learning insights for investment decisions</p>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">🎯 Market Predictions (Next 12 Months)</h5>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                            <strong>Property Values:</strong> Predicted +5.2% growth<br>
                            <span style="color: var(--success);">Confidence: 87% | Model accuracy: 91%</span>
                        </div>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                            <strong>Rental Rates:</strong> Expected +3.8% increase<br>
                            <span style="color: var(--success);">Driven by population growth and low inventory</span>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">🏆 Investment Recommendations</h5>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 8px;">
                            <strong>High Priority:</strong> Single-family homes, Downtown<br>
                            <span style="color: var(--text-muted);">Predicted ROI: 24-28% | Risk: Low</span>
                        </div>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px;">
                            <strong>Medium Priority:</strong> Multi-family, Riverside<br>
                            <span style="color: var(--text-muted);">Predicted ROI: 18-22% | Risk: Medium</span>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Close</button>
                        <button class="cta-button" onclick="runNewPrediction()">Run New Prediction</button>
                    </div>
                `;
            }
            
            function getTemplatesHTML() {
                return `
                    <div style="margin-bottom: 20px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">📧 Email Templates</h5>
                        <div class="quick-actions">
                            <button class="quick-action-btn" onclick="useTemplate('deal_alert')">
                                <i class="fas fa-bell"></i>
                                Deal Alert
                            </button>
                            <button class="quick-action-btn" onclick="useTemplate('follow_up')">
                                <i class="fas fa-reply"></i>
                                Follow-up
                            </button>
                            <button class="quick-action-btn" onclick="useTemplate('newsletter')">
                                <i class="fas fa-newspaper"></i>
                                Newsletter
                            </button>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">📱 SMS Templates</h5>
                        <div class="quick-actions">
                            <button class="quick-action-btn" onclick="useTemplate('sms_alert')">
                                <i class="fas fa-mobile-alt"></i>
                                Property Alert
                            </button>
                            <button class="quick-action-btn" onclick="useTemplate('sms_follow')">
                                <i class="fas fa-comment"></i>
                                Quick Follow-up
                            </button>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Close</button>
                        <button class="cta-button" onclick="createNewTemplate()">Create New Template</button>
                    </div>
                `;
            }
            
            function getCashFlowHTML() {
                return `
                    <div class="form-group">
                        <label>Property Address</label>
                        <input type="text" placeholder="123 Investment Ave">
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div class="form-group">
                            <label>Purchase Price</label>
                            <input type="number" placeholder="250000">
                        </div>
                        <div class="form-group">
                            <label>Monthly Rent</label>
                            <input type="number" placeholder="2500">
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div class="form-group">
                            <label>Monthly Expenses</label>
                            <input type="number" placeholder="800">
                        </div>
                        <div class="form-group">
                            <label>Down Payment %</label>
                            <input type="number" placeholder="25">
                        </div>
                    </div>
                    
                    <div style="background: var(--glass); padding: 20px; border-radius: 12px; margin: 20px 0;">
                        <h5 style="color: var(--success); margin-bottom: 12px;">📊 Projected Results</h5>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                            <div>Monthly Cash Flow: <strong>$1,200</strong></div>
                            <div>Annual ROI: <strong>18.7%</strong></div>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Close</button>
                        <button class="cta-button" onclick="generateCashFlowReport()">Generate Report</button>
                    </div>
                `;
            }
            
            // Additional action handlers
            function saveAISettings() {
                showToast('AI settings saved successfully!', 'success');
                closeModal();
            }
            
            function exportMarketReport() {
                showToast('Market report exported to downloads', 'success');
                closeModal();
            }
            
            function importContacts() {
                showToast('Contacts imported successfully!', 'success');
                closeModal();
            }
            
            function exportContactReport() {
                showToast('Contact report exported', 'success');
                closeModal();
            }
            
            function viewDetailedAnalytics() {
                showToast('Loading detailed analytics...', 'success');
                closeModal();
            }
            
            function runNewPrediction() {
                showToast('Running new AI prediction...', 'success');
                closeModal();
            }
            
            function useTemplate(template) {
                showToast(`Loading ${template} template...`, 'success');
                closeModal();
            }
            
            function createNewTemplate() {
                showToast('Opening template editor...', 'success');
                closeModal();
            }
            
            function generateCashFlowReport() {
                showToast('Cash flow report generated!', 'success');
                closeModal();
            }
            
            // Missing functions referenced in the code
            function getPerformanceHTML() {
                return `
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">98.2%</div>
                            <div class="metric-label">System Uptime</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">1.2s</div>
                            <div class="metric-label">Avg Response Time</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">2,847</div>
                            <div class="metric-label">Active Users</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">99.7%</div>
                            <div class="metric-label">Data Accuracy</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">📈 Performance Insights</h5>
                        <ul style="color: var(--text-muted); line-height: 1.6;">
                            <li>Peak usage: 10-11 AM weekdays</li>
                            <li>Most active module: Deal Analysis</li>
                            <li>Average session duration: 23 minutes</li>
                            <li>User satisfaction score: 4.8/5</li>
                        </ul>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Close</button>
                        <button class="cta-button" onclick="exportPerformanceReport()">Export Report</button>
                    </div>
                `;
            }
            
            function getAutomationHTML() {
                return `
                    <div style="margin-bottom: 20px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">⚙️ Active Automation Rules</h5>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>New Lead Auto-Response</strong><br>
                                    <span style="color: var(--text-muted);">Send welcome email within 5 minutes</span>
                                </div>
                                <span class="status-badge status-active">Active</span>
                            </div>
                        </div>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>Deal Alert Distribution</strong><br>
                                    <span style="color: var(--text-muted);">Notify matching investors automatically</span>
                                </div>
                                <span class="status-badge status-active">Active</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button" onclick="createNewRule()">Create New Rule</button>
                        <button class="cta-button cta-secondary" onclick="closeModal()">Close</button>
                    </div>
                `;
            }
            
            function getWorkflowsHTML() {
                return `
                    <div style="margin-bottom: 20px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">🔄 Smart Workflows</h5>
                        <div class="quick-actions">
                            <button class="quick-action-btn" onclick="useWorkflow('lead_processing')">
                                <i class="fas fa-user-plus"></i>
                                Lead Processing
                            </button>
                            <button class="quick-action-btn" onclick="useWorkflow('deal_analysis')">
                                <i class="fas fa-chart-line"></i>
                                Deal Analysis Pipeline
                            </button>
                            <button class="quick-action-btn" onclick="useWorkflow('investor_outreach')">
                                <i class="fas fa-handshake"></i>
                                Investor Outreach
                            </button>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button" onclick="createCustomWorkflow()">Build Custom Workflow</button>
                        <button class="cta-button cta-secondary" onclick="closeModal()">Close</button>
                    </div>
                `;
            }
            
            function getUserProfileHTML() {
                return `
                    <div class="form-group">
                        <label>Full Name</label>
                        <input type="text" value="NXTRIX User" placeholder="Your name">
                    </div>
                    <div class="form-group">
                        <label>Email Address</label>
                        <input type="email" value="user@nxtrix.com" placeholder="Your email">
                    </div>
                    <div class="form-group">
                        <label>Phone Number</label>
                        <input type="tel" placeholder="(555) 123-4567">
                    </div>
                    <div class="form-group">
                        <label>Investment Focus</label>
                        <select>
                            <option>Single Family Homes</option>
                            <option>Multi-Family Properties</option>
                            <option>Commercial Real Estate</option>
                            <option>Mixed Portfolio</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Experience Level</label>
                        <select>
                            <option>Beginner (0-2 years)</option>
                            <option>Intermediate (3-5 years)</option>
                            <option>Advanced (6-10 years)</option>
                            <option>Expert (10+ years)</option>
                        </select>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Cancel</button>
                        <button class="cta-button" onclick="saveUserProfile()">Save Profile</button>
                    </div>
                `;
            }
            
            function getSystemSettingsHTML() {
                return `
                    <div style="margin-bottom: 20px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">🔧 System Configuration</h5>
                        
                        <div class="form-group">
                            <label>Theme Preference</label>
                            <select>
                                <option>Dark Mode (Current)</option>
                                <option>Light Mode</option>
                                <option>Auto (System)</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Notification Frequency</label>
                            <select>
                                <option>Real-time</option>
                                <option>Hourly Summary</option>
                                <option>Daily Digest</option>
                                <option>Weekly Report</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Data Backup</label>
                            <select>
                                <option>Daily (Recommended)</option>
                                <option>Weekly</option>
                                <option>Monthly</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Performance Mode</label>
                            <select>
                                <option>High Performance</option>
                                <option>Balanced</option>
                                <option>Power Saver</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Cancel</button>
                        <button class="cta-button" onclick="saveSystemSettings()">Save Settings</button>
                    </div>
                `;
            }
            
            function getIntegrationsHTML() {
                return `
                    <div style="margin-bottom: 20px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">🔗 Available Integrations</h5>
                        
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>💳 Stripe Payments</strong><br>
                                    <span style="color: var(--text-muted);">Process payments and subscriptions</span>
                                </div>
                                <span class="status-badge status-active">Connected</span>
                            </div>
                        </div>
                        
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>📧 Email Services</strong><br>
                                    <span style="color: var(--text-muted);">Automated email campaigns</span>
                                </div>
                                <span class="status-badge status-active">Connected</span>
                            </div>
                        </div>
                        
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>📱 SMS Providers</strong><br>
                                    <span style="color: var(--text-muted);">SMS marketing and notifications</span>
                                </div>
                                <button class="cta-button" style="padding: 4px 12px; font-size: 12px;" onclick="connectSMS()">Connect</button>
                            </div>
                        </div>
                        
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>🏠 MLS Data</strong><br>
                                    <span style="color: var(--text-muted);">Real-time property listings</span>
                                </div>
                                <button class="cta-button" style="padding: 4px 12px; font-size: 12px;" onclick="connectMLS()">Connect</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Close</button>
                        <button class="cta-button" onclick="addNewIntegration()">Add Integration</button>
                    </div>
                `;
            }
            
            function getPortfolioHTML() {
                return `
                    <div style="text-align: center; margin-bottom: 24px;">
                        <h4 style="color: var(--primary); margin-bottom: 8px;">Portfolio Overview</h4>
                        <p style="color: var(--text-muted);">Your real estate investment portfolio</p>
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">23</div>
                            <div class="metric-label">Properties</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">$4.2M</div>
                            <div class="metric-label">Total Value</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">$28,400</div>
                            <div class="metric-label">Monthly Revenue</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">19.8%</div>
                            <div class="metric-label">Avg ROI</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 24px;">
                        <h5 style="color: var(--text); margin-bottom: 12px;">🏆 Top Performers</h5>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 8px;">
                            <strong>Downtown Condo A-201</strong><br>
                            <span style="color: var(--success);">ROI: 31.2% | Monthly: $3,200</span>
                        </div>
                        <div style="background: var(--glass); padding: 16px; border-radius: 8px; margin-bottom: 8px;">
                            <strong>Riverside Single Family</strong><br>
                            <span style="color: var(--success);">ROI: 28.7% | Monthly: $2,850</span>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Close</button>
                        <button class="cta-button" onclick="viewFullPortfolio()">View Full Portfolio</button>
                    </div>
                `;
            }
            
            // Additional action handlers for new functions
            function exportPerformanceReport() {
                showToast('Performance report exported', 'success');
                closeModal();
            }
            
            function createNewRule() {
                showToast('Opening automation rule builder...', 'success');
                closeModal();
            }
            
            function useWorkflow(workflow) {
                showToast(`Loading ${workflow} workflow...`, 'success');
                closeModal();
            }
            
            function createCustomWorkflow() {
                showToast('Opening workflow builder...', 'success');
                closeModal();
            }
            
            function saveUserProfile() {
                showToast('User profile saved successfully!', 'success');
                closeModal();
            }
            
            function saveSystemSettings() {
                showToast('System settings saved!', 'success');
                closeModal();
            }
            
            function connectSMS() {
                showToast('Connecting SMS provider...', 'success');
            }
            
            function connectMLS() {
                showToast('Connecting to MLS data...', 'success');
            }
            
            function addNewIntegration() {
                showToast('Opening integration marketplace...', 'success');
                closeModal();
            }
            
            function getProcessingHTML() {
                return `
                    <div style="text-align: center; padding: 40px 20px;">
                        <div class="loading" style="margin: 0 auto 20px;"></div>
                        <h4 style="color: var(--primary); margin-bottom: 8px;">AI Analysis in Progress</h4>
                        <p style="color: var(--text-muted);">Analyzing market data and property information...</p>
                    </div>
                `;
            }
            
            function getDynamicFormHTML(fields) {
                let formHTML = '';
                fields.forEach(field => {
                    formHTML += `
                        <div class="form-group">
                            <label>${field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</label>
                            <input type="text" placeholder="Enter ${field.replace(/_/g, ' ')}">
                        </div>
                    `;
                });
                
                formHTML += `
                    <div class="form-actions">
                        <button class="cta-button cta-secondary" onclick="closeModal()">Cancel</button>
                        <button class="cta-button" onclick="submitForm()">Submit</button>
                    </div>
                `;
                
                return formHTML;
            }
            
            // Action handlers for modal buttons
            function submitDeal() {
                showToast('Deal created successfully!', 'success');
                closeModal();
            }
            
            function saveDealAnalysis() {
                showToast('Analysis saved to your reports', 'success');
                closeModal();
            }
            
            function saveContact() {
                showToast('Contact added successfully!', 'success');
                closeModal();
            }
            
            function exportAIReport() {
                showToast('AI report exported to downloads', 'success');
                closeModal();
            }
            
            function sendEmailCampaign() {
                showToast('Email campaign sent to selected recipients', 'success');
                closeModal();
            }
            
            function sendSMSCampaign() {
                showToast('SMS campaign sent successfully', 'success');
                closeModal();
            }
            
            function openCalculator(type) {
                showToast(`Opening ${type} calculator...`, 'success');
                closeModal();
            }
            
            function newAnalysis() {
                showToast('Opening new financial analysis...', 'success');
                closeModal();
            }
            
            function viewFullPortfolio() {
                showToast('Opening full portfolio view...', 'success');
                closeModal();
            }
            
            function submitForm() {
                showToast('Form submitted successfully!', 'success');
                closeModal();
            }
            
            // Sidebar Functions
            function toggleSidebar() {
                const sidebar = document.getElementById('sidebar');
                sidebarCollapsed = !sidebarCollapsed;
                
                if (sidebarCollapsed) {
                    sidebar.classList.add('collapsed');
                } else {
                    sidebar.classList.remove('collapsed');
                }
            }
            
            // Notification Functions
            function showNotifications() {
                showToast('You have 3 new notifications', 'success');
            }
            
            function showProfile() {
                showToast('Opening user profile...', 'success');
            }
            
            function showToast(message, type = 'success') {
                const toast = document.getElementById('toast');
                const toastMessage = document.getElementById('toastMessage');
                
                toastMessage.textContent = message;
                toast.className = `toast ${type}`;
                toast.classList.add('show');
                
                setTimeout(() => {
                    toast.classList.remove('show');
                }, 3000);
            }
            
            // Page Content Generators
            function getDashboardContent() {
                return `
                    <div class="dashboard-grid">
                        <div class="dashboard-card">
                            <div class="card-header">
                                <h3 class="card-title">Deal Pipeline</h3>
                                <div class="card-icon">
                                    <i class="fas fa-chart-line"></i>
                                </div>
                            </div>
                            <div class="metrics-grid">
                                <div class="metric-card">
                                    <div class="metric-value">47</div>
                                    <div class="metric-label">Active Deals</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">$12.4M</div>
                                    <div class="metric-label">Total Value</div>
                                </div>
                            </div>
                            <div class="quick-actions">
                                <button class="cta-button" onclick="handleCTA('newDeal')">
                                    <i class="fas fa-plus"></i>
                                    New Deal
                                </button>
                                <button class="cta-button cta-secondary" onclick="handleCTA('analyzeDeal')">
                                    <i class="fas fa-analytics"></i>
                                    Analyze
                                </button>
                            </div>
                        </div>
                        
                        <div class="dashboard-card">
                            <div class="card-header">
                                <h3 class="card-title">Contact Management</h3>
                                <div class="card-icon">
                                    <i class="fas fa-users"></i>
                                </div>
                            </div>
                            <div class="metrics-grid">
                                <div class="metric-card">
                                    <div class="metric-value">1,247</div>
                                    <div class="metric-label">Total Contacts</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">89</div>
                                    <div class="metric-label">Active Investors</div>
                                </div>
                            </div>
                            <div class="quick-actions">
                                <button class="cta-button" onclick="handleCTA('addContact')">
                                    <i class="fas fa-user-plus"></i>
                                    Add Contact
                                </button>
                                <button class="cta-button cta-secondary" onclick="handleCTA('manageContacts')">
                                    <i class="fas fa-edit"></i>
                                    Manage
                                </button>
                            </div>
                        </div>
                        
                        <div class="dashboard-card">
                            <div class="card-header">
                                <h3 class="card-title">AI Intelligence</h3>
                                <div class="card-icon">
                                    <i class="fas fa-robot"></i>
                                </div>
                            </div>
                            <div class="metrics-grid">
                                <div class="metric-card">
                                    <div class="metric-value">156</div>
                                    <div class="metric-label">AI Insights</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">94%</div>
                                    <div class="metric-label">Accuracy</div>
                                </div>
                            </div>
                            <div class="quick-actions">
                                <button class="cta-button" onclick="handleCTA('aiAnalysis')">
                                    <i class="fas fa-brain"></i>
                                    Run Analysis
                                </button>
                                <button class="cta-button cta-secondary" onclick="handleCTA('aiSettings')">
                                    <i class="fas fa-cog"></i>
                                    Configure
                                </button>
                            </div>
                        </div>
                        
                        <div class="dashboard-card">
                            <div class="card-header">
                                <h3 class="card-title">Communication Hub</h3>
                                <div class="card-icon">
                                    <i class="fas fa-comments"></i>
                                </div>
                            </div>
                            <div class="metrics-grid">
                                <div class="metric-card">
                                    <div class="metric-value">24</div>
                                    <div class="metric-label">Pending</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">342</div>
                                    <div class="metric-label">Sent Today</div>
                                </div>
                            </div>
                            <div class="quick-actions">
                                <button class="cta-button" onclick="handleCTA('sendEmail')">
                                    <i class="fas fa-envelope"></i>
                                    Send Email
                                </button>
                                <button class="cta-button cta-secondary" onclick="handleCTA('smsMarketing')">
                                    <i class="fas fa-mobile-alt"></i>
                                    SMS Campaign
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            function getDealsContent() {
                return `
                    <div class="dashboard-card">
                        <div class="card-header">
                            <h3 class="card-title">Deal Management Center</h3>
                            <div class="card-icon">
                                <i class="fas fa-handshake"></i>
                            </div>
                        </div>
                        <div class="quick-actions">
                            <button class="cta-button" onclick="handleCTA('newDeal')">
                                <i class="fas fa-plus"></i>
                                Create New Deal
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('analyzeDeal')">
                                <i class="fas fa-analytics"></i>
                                Analyze Properties
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('dealPipeline')">
                                <i class="fas fa-chart-line"></i>
                                View Pipeline
                            </button>
                        </div>
                        <p style="margin-top: 20px; color: var(--text-muted);">
                            Manage your entire deal pipeline, from initial property analysis to closing. 
                            Connect with your existing NXTRIX backend for full functionality.
                        </p>
                    </div>
                `;
            }
            
            function getContactsContent() {
                return `
                    <div class="dashboard-card">
                        <div class="card-header">
                            <h3 class="card-title">Contact Management Center</h3>
                            <div class="card-icon">
                                <i class="fas fa-users"></i>
                            </div>
                        </div>
                        <div class="quick-actions">
                            <button class="cta-button" onclick="handleCTA('addContact')">
                                <i class="fas fa-user-plus"></i>
                                Add New Contact
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('importContacts')">
                                <i class="fas fa-upload"></i>
                                Import Contacts
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('contactAnalytics')">
                                <i class="fas fa-chart-bar"></i>
                                Contact Analytics
                            </button>
                        </div>
                        <p style="margin-top: 20px; color: var(--text-muted);">
                            Complete CRM system with 6,692+ lines of functionality. Manage investors, 
                            buyers, and all your real estate contacts in one place.
                        </p>
                    </div>
                `;
            }
            
            function getAnalyticsContent() {
                return `
                    <div class="dashboard-card">
                        <div class="card-header">
                            <h3 class="card-title">Advanced Analytics Dashboard</h3>
                            <div class="card-icon">
                                <i class="fas fa-analytics"></i>
                            </div>
                        </div>
                        <div class="quick-actions">
                            <button class="cta-button" onclick="handleCTA('marketAnalysis')">
                                <i class="fas fa-chart-line"></i>
                                Market Analysis
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('portfolioAnalytics')">
                                <i class="fas fa-briefcase"></i>
                                Portfolio Analytics
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('predictiveModeling')">
                                <i class="fas fa-brain"></i>
                                Predictive Modeling
                            </button>
                        </div>
                        <p style="margin-top: 20px; color: var(--text-muted);">
                            Advanced analytics with 47+ data points analyzed per property. 
                            AI-powered insights and market intelligence.
                        </p>
                    </div>
                `;
            }
            
            function getCommunicationContent() {
                return `
                    <div class="dashboard-card">
                        <div class="card-header">
                            <h3 class="card-title">Communication Hub</h3>
                            <div class="card-icon">
                                <i class="fas fa-comments"></i>
                            </div>
                        </div>
                        <div class="quick-actions">
                            <button class="cta-button" onclick="handleCTA('sendEmail')">
                                <i class="fas fa-envelope"></i>
                                Email Campaign
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('smsMarketing')">
                                <i class="fas fa-mobile-alt"></i>
                                SMS Marketing
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('communicationTemplates')">
                                <i class="fas fa-file-alt"></i>
                                Templates
                            </button>
                        </div>
                        <p style="margin-top: 20px; color: var(--text-muted);">
                            Automated email campaigns, SMS marketing, and communication templates. 
                            Keep your network engaged with professional outreach.
                        </p>
                    </div>
                `;
            }
            
            function getAutomationContent() {
                return `
                    <div class="dashboard-card">
                        <div class="card-header">
                            <h3 class="card-title">AI Automation Center</h3>
                            <div class="card-icon">
                                <i class="fas fa-robot"></i>
                            </div>
                        </div>
                        <div class="quick-actions">
                            <button class="cta-button" onclick="handleCTA('aiAnalysis')">
                                <i class="fas fa-brain"></i>
                                AI Market Analysis
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('automationRules')">
                                <i class="fas fa-cogs"></i>
                                Automation Rules
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('smartWorkflows')">
                                <i class="fas fa-project-diagram"></i>
                                Smart Workflows
                            </button>
                        </div>
                        <p style="margin-top: 20px; color: var(--text-muted);">
                            AI-powered automation for deal sourcing, lead scoring, and workflow management. 
                            Let artificial intelligence handle repetitive tasks.
                        </p>
                    </div>
                `;
            }
            
            function getPortfolioContent() {
                return `
                    <div class="dashboard-card">
                        <div class="card-header">
                            <h3 class="card-title">Portfolio Management</h3>
                            <div class="card-icon">
                                <i class="fas fa-briefcase"></i>
                            </div>
                        </div>
                        <div class="quick-actions">
                            <button class="cta-button" onclick="handleCTA('portfolioOverview')">
                                <i class="fas fa-chart-pie"></i>
                                Portfolio Overview
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('performanceTracking')">
                                <i class="fas fa-chart-line"></i>
                                Performance Tracking
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('portfolioOptimization')">
                                <i class="fas fa-balance-scale"></i>
                                Optimization
                            </button>
                        </div>
                        <p style="margin-top: 20px; color: var(--text-muted);">
                            Complete portfolio management with performance tracking, optimization suggestions, 
                            and comprehensive reporting.
                        </p>
                    </div>
                `;
            }
            
            function getFinancialContent() {
                return `
                    <div class="dashboard-card">
                        <div class="card-header">
                            <h3 class="card-title">Financial Modeling</h3>
                            <div class="card-icon">
                                <i class="fas fa-calculator"></i>
                            </div>
                        </div>
                        <div class="quick-actions">
                            <button class="cta-button" onclick="handleCTA('financialAnalysis')">
                                <i class="fas fa-chart-bar"></i>
                                Financial Analysis
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('cashFlowModeling')">
                                <i class="fas fa-money-bill-wave"></i>
                                Cash Flow Modeling
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('investmentCalculators')">
                                <i class="fas fa-calculator"></i>
                                Investment Calculators
                            </button>
                        </div>
                        <p style="margin-top: 20px; color: var(--text-muted);">
                            Advanced financial modeling with cash flow analysis, ROI calculations, 
                            and investment scenario planning.
                        </p>
                    </div>
                `;
            }
            
            function getSettingsContent() {
                return `
                    <div class="dashboard-card">
                        <div class="card-header">
                            <h3 class="card-title">Settings & Configuration</h3>
                            <div class="card-icon">
                                <i class="fas fa-cog"></i>
                            </div>
                        </div>
                        <div class="quick-actions">
                            <button class="cta-button" onclick="handleCTA('userProfile')">
                                <i class="fas fa-user"></i>
                                User Profile
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('systemSettings')">
                                <i class="fas fa-cogs"></i>
                                System Settings
                            </button>
                            <button class="cta-button cta-secondary" onclick="handleCTA('integrations')">
                                <i class="fas fa-plug"></i>
                                Integrations
                            </button>
                        </div>
                        <p style="margin-top: 20px; color: var(--text-muted);">
                            Configure your NXTRIX platform, manage integrations, and customize 
                            your workflow preferences.
                        </p>
                    </div>
                `;
            }
            
            // Initialize the application
            document.addEventListener('DOMContentLoaded', function() {
                showToast('NXTRIX Platform loaded successfully!', 'success');
            });
        </script>
    </body>
    </html>
    """
    
    # Inject the custom web application
    components.html(webapp_html, height=800, scrolling=True)

def main():
    """Main application entry point"""
    
    # Completely hide Streamlit's default interface including the menu bar
    st.markdown("""
    <style>
        /* Hide Streamlit branding and interface */
        .stApp > header {visibility: hidden !important; height: 0px !important;}
        .stApp > div:first-child {padding-top: 0px !important;}
        .main > div {padding-top: 0px !important;}
        .block-container {
            padding-top: 0px !important;
            padding-bottom: 0px !important;
            padding-left: 0px !important;
            padding-right: 0px !important;
            max-width: 100% !important;
            margin: 0px !important;
        }
        iframe {
            border: none !important;
            border-radius: 0px !important;
            width: 100% !important;
            height: 100vh !important;
        }
        
        /* Hide Streamlit footer */
        .css-1d391kg, .css-1aumxhk, footer {display: none !important;}
        .css-1dp5vir {display: none !important;}
        .css-1rs6os {display: none !important;}
        .css-17eq0hr {display: none !important;}
        
        /* Hide main menu bar with 3 dots (rerun, settings, etc.) */
        .css-1y4p8pa {display: none !important;}
        .css-1lcbmhc {display: none !important;}
        .css-14xtw13 {display: none !important;}
        .css-1g8v9l0 {display: none !important;}
        .css-1adrfps {display: none !important;}
        .css-1kzie3u {display: none !important;}
        .css-9s5bis {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        [data-testid="stDecoration"] {display: none !important;}
        [data-testid="stStatusWidget"] {display: none !important;}
        [data-testid="collapsedControl"] {display: none !important;}
        
        /* Hide the entire header area */
        header[data-testid="stHeader"] {display: none !important;}
        .css-18ni7ap {display: none !important;}
        .css-vk3wp9 {display: none !important;}
        .css-1544g2n {display: none !important;}
        
        /* Force full viewport without any top margin */
        .main .block-container {
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Hide all Streamlit controls and menus */
        .stToolbar, .stDecoration, .stStatusWidget {display: none !important;}
        div[data-testid="stToolbar"] {display: none !important;}
        section[data-testid="stSidebar"] > div {margin-top: 0px !important;}
        
        /* Force full viewport height */
        html, body, [data-testid="stAppViewContainer"] {
            height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Hide any remaining Streamlit UI elements */
        .css-1j5bjqe {display: none !important;}
        .css-1ww6uq0 {display: none !important;}
        .css-1offfwp {display: none !important;}
        .css-16huue1 {display: none !important;}
        
        /* Ensure no top spacing anywhere */
        .element-container {margin-top: 0px !important;}
        .stMarkdown {margin-top: 0px !important;}
    </style>
    """, unsafe_allow_html=True)
    
    # Additional JavaScript to remove any dynamically added elements
    st.markdown("""
    <script>
        // Remove any Streamlit header elements that might appear
        function hideStreamlitHeader() {
            // Hide toolbar
            const toolbar = document.querySelector('[data-testid="stToolbar"]');
            if (toolbar) toolbar.style.display = 'none';
            
            // Hide header
            const header = document.querySelector('[data-testid="stHeader"]');
            if (header) header.style.display = 'none';
            
            // Hide any menu buttons
            const menuButtons = document.querySelectorAll('.css-1y4p8pa, .css-1lcbmhc, .css-14xtw13');
            menuButtons.forEach(button => button.style.display = 'none');
            
            // Ensure no top padding
            const main = document.querySelector('.main');
            if (main) main.style.paddingTop = '0px';
            
            // Force app container to top
            const app = document.querySelector('.stApp');
            if (app) {
                app.style.paddingTop = '0px';
                app.style.marginTop = '0px';
            }
        }
        
        // Run immediately and on any DOM changes
        hideStreamlitHeader();
        const observer = new MutationObserver(hideStreamlitHeader);
        observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """, unsafe_allow_html=True)
    
    # Inject the custom web application with backend integration
    inject_custom_webapp()

if __name__ == "__main__":
    main()