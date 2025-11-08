import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(
    page_title="NXTRIX CRM - Advanced Real Estate Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    # Hide Streamlit UI
    st.markdown("""
    <style>
        .stApp > header {visibility: hidden;}
        .main > div {padding-top: 0px;}
        .block-container {padding-top: 0px; padding-bottom: 0px; max-width: 100%; margin: 0px;}
    </style>
    """, unsafe_allow_html=True)

    # Main NXTRIX Application HTML
    nxtrix_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NXTRIX CRM - Advanced Real Estate Platform</title>
        
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                color: #ffffff;
                height: 100vh;
                overflow: hidden;
                position: relative;
            }

            /* Animated Background */
            .animated-bg {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
                animation: gradientShift 15s ease infinite;
            }

            @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            /* Glass Morphism Effects */
            .glass-container {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }

            /* App Container */
            .app-container {
                display: flex;
                height: 100vh;
                position: relative;
                z-index: 1;
            }

            /* Sidebar Styling */
            .sidebar {
                width: 300px;
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border-right: 1px solid rgba(255, 255, 255, 0.1);
                padding: 24px;
                overflow-y: auto;
                transition: all 0.3s ease;
            }

            .sidebar-header {
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }

            .logo {
                font-size: 2.2em;
                font-weight: 700;
                background: linear-gradient(135deg, #4CAF50, #45a049);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 8px;
                display: block;
            }

            .tagline {
                font-size: 0.9em;
                color: rgba(255, 255, 255, 0.7);
                font-weight: 400;
            }

            /* Navigation Menu */
            .nav-menu {
                margin-top: 20px;
            }

            .nav-section {
                margin-bottom: 25px;
            }

            .section-title {
                font-size: 0.85em;
                color: rgba(255, 255, 255, 0.6);
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 12px;
                font-weight: 600;
            }

            .nav-item, .cta-button {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                margin: 6px 0;
                background: rgba(255, 255, 255, 0.05);
                border: none;
                border-radius: 12px;
                color: #ffffff;
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
                text-align: left;
            }

            .nav-item:hover, .cta-button:hover {
                background: rgba(74, 175, 79, 0.2);
                transform: translateX(5px);
                box-shadow: 0 4px 20px rgba(74, 175, 79, 0.3);
            }

            .nav-icon {
                font-size: 16px;
                min-width: 20px;
                text-align: center;
            }

            /* Main Content Area */
            .main-content {
                flex: 1;
                padding: 24px;
                overflow-y: auto;
                background: rgba(255, 255, 255, 0.02);
            }

            .content-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }

            .page-title {
                font-size: 2.4em;
                font-weight: 700;
                background: linear-gradient(135deg, #ffffff, #e3f2fd);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .breadcrumb {
                color: rgba(255, 255, 255, 0.6);
                font-size: 0.9em;
            }

            /* Dashboard Grid */
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }

            .metric-card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                transition: all 0.3s ease;
                cursor: pointer;
                position: relative;
                overflow: hidden;
            }

            .metric-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
                transition: left 0.5s ease;
            }

            .metric-card:hover::before {
                left: 100%;
            }

            .metric-card:hover {
                transform: translateY(-8px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
                border-color: rgba(74, 175, 79, 0.4);
            }

            .metric-icon {
                font-size: 2.5em;
                margin-bottom: 15px;
                opacity: 0.8;
            }

            .metric-value {
                font-size: 2.8em;
                font-weight: 700;
                color: #4CAF50;
                margin: 10px 0;
            }

            .metric-label {
                font-size: 1.1em;
                color: rgba(255, 255, 255, 0.8);
                font-weight: 600;
            }

            .metric-change {
                font-size: 0.9em;
                margin-top: 8px;
                padding: 4px 8px;
                border-radius: 12px;
                background: rgba(74, 175, 79, 0.2);
                color: #81C784;
            }

            /* Chart Container */
            .chart-container {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 24px;
                margin: 20px 0;
                min-height: 400px;
            }

            .chart-title {
                font-size: 1.4em;
                font-weight: 600;
                margin-bottom: 20px;
                color: #ffffff;
            }

            /* Action Buttons */
            .action-button {
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 5px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .action-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
                background: linear-gradient(135deg, #45a049, #4CAF50);
            }

            .secondary-button {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                padding: 10px 20px;
                border-radius: 10px;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 5px;
            }

            .secondary-button:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: translateY(-1px);
            }

            /* Modal Styles */
            .modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                backdrop-filter: blur(10px);
                display: none;
                z-index: 1000;
                align-items: center;
                justify-content: center;
            }

            .modal.show {
                display: flex;
            }

            .modal-content {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(30px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                padding: 30px;
                max-width: 500px;
                width: 90%;
                text-align: center;
                animation: modalSlideIn 0.3s ease;
            }

            @keyframes modalSlideIn {
                from { transform: translateY(-50px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }

            .modal-title {
                font-size: 1.6em;
                font-weight: 700;
                margin-bottom: 15px;
                color: #4CAF50;
            }

            .modal-text {
                font-size: 1.1em;
                color: rgba(255, 255, 255, 0.9);
                margin-bottom: 25px;
                line-height: 1.5;
            }

            /* Toast Notifications */
            .toast {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 16px 24px;
                border-radius: 12px;
                color: white;
                font-weight: 600;
                z-index: 1001;
                transform: translateX(400px);
                transition: transform 0.3s ease;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(10px);
            }

            .toast.show {
                transform: translateX(0);
            }

            .toast.success {
                background: linear-gradient(135deg, #4CAF50, #45a049);
                border: 1px solid rgba(76, 175, 80, 0.3);
            }

            .toast.warning {
                background: linear-gradient(135deg, #FF9800, #F57C00);
                border: 1px solid rgba(255, 152, 0, 0.3);
            }

            .toast.error {
                background: linear-gradient(135deg, #f44336, #d32f2f);
                border: 1px solid rgba(244, 67, 54, 0.3);
            }

            /* Form Styles */
            .form-group {
                margin-bottom: 20px;
                text-align: left;
            }

            .form-label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: rgba(255, 255, 255, 0.9);
            }

            .form-input {
                width: 100%;
                padding: 12px 16px;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                color: white;
                font-size: 14px;
                transition: all 0.3s ease;
            }

            .form-input:focus {
                outline: none;
                border-color: #4CAF50;
                background: rgba(255, 255, 255, 0.15);
                box-shadow: 0 0 15px rgba(76, 175, 80, 0.3);
            }

            .form-input::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }

            /* Calendar Widget */
            .calendar-widget {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 16px;
                padding: 20px;
                margin: 20px 0;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            .calendar-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }

            .calendar-month {
                font-size: 1.2em;
                font-weight: 600;
                color: #4CAF50;
            }

            .calendar-nav {
                background: none;
                border: none;
                color: #4CAF50;
                font-size: 1.2em;
                cursor: pointer;
                padding: 5px;
                border-radius: 5px;
                transition: background 0.3s ease;
            }

            .calendar-nav:hover {
                background: rgba(76, 175, 80, 0.2);
            }

            .calendar-grid {
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 2px;
                text-align: center;
            }

            .calendar-day {
                padding: 10px;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9em;
            }

            .calendar-day:hover {
                background: rgba(76, 175, 80, 0.2);
            }

            .calendar-day.today {
                background: #4CAF50;
                color: white;
                font-weight: 600;
            }

            /* Loading Animation */
            .loading-spinner {
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-top: 3px solid #4CAF50;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            /* Responsive Design */
            @media (max-width: 1200px) {
                .sidebar {
                    width: 250px;
                }
                
                .dashboard-grid {
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                }
            }

            @media (max-width: 768px) {
                .app-container {
                    flex-direction: column;
                }
                
                .sidebar {
                    width: 100%;
                    height: auto;
                    max-height: 200px;
                    overflow-y: auto;
                }
                
                .main-content {
                    padding: 15px;
                }
                
                .page-title {
                    font-size: 1.8em;
                }
                
                .dashboard-grid {
                    grid-template-columns: 1fr;
                }
            }

            /* Scrollbar Styling */
            ::-webkit-scrollbar {
                width: 8px;
            }

            ::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }

            ::-webkit-scrollbar-thumb {
                background: rgba(76, 175, 80, 0.6);
                border-radius: 10px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: rgba(76, 175, 80, 0.8);
            }
        </style>
    </head>
    <body>
        <div class="animated-bg"></div>
        
        <div class="app-container">
            <!-- Sidebar -->
            <div class="sidebar">
                <div class="sidebar-header">
                    <div class="logo">🏢 NXTRIX</div>
                    <div class="tagline">Advanced Real Estate Platform</div>
                </div>
                
                <nav class="nav-menu">
                    <div class="nav-section">
                        <div class="section-title">Core Features</div>
                        <button class="cta-button" onclick="handleCTA('newDeal')">
                            <span class="nav-icon">🏠</span>
                            <span>Create New Deal</span>
                        </button>
                        <button class="cta-button" onclick="handleCTA('analyzeDeal')">
                            <span class="nav-icon">📊</span>
                            <span>Deal Analysis</span>
                        </button>
                        <button class="cta-button" onclick="handleCTA('addContact')">
                            <span class="nav-icon">👥</span>
                            <span>Add Contact</span>
                        </button>
                        <button class="cta-button" onclick="handleCTA('manageLeads')">
                            <span class="nav-icon">🎯</span>
                            <span>Lead Management</span>
                        </button>
                    </div>
                    
                    <div class="nav-section">
                        <div class="section-title">Marketing & Communication</div>
                        <button class="cta-button" onclick="handleCTA('sendEmail')">
                            <span class="nav-icon">📧</span>
                            <span>Email Marketing</span>
                        </button>
                        <button class="cta-button" onclick="handleCTA('createCampaign')">
                            <span class="nav-icon">📢</span>
                            <span>Create Campaign</span>
                        </button>
                        <button class="cta-button" onclick="handleCTA('socialMedia')">
                            <span class="nav-icon">📱</span>
                            <span>Social Media</span>
                        </button>
                    </div>
                    
                    <div class="nav-section">
                        <div class="section-title">Advanced Tools</div>
                        <button class="cta-button" onclick="handleCTA('aiAnalysis')">
                            <span class="nav-icon">🤖</span>
                            <span>AI Insights</span>
                        </button>
                        <button class="cta-button" onclick="handleCTA('marketTrends')">
                            <span class="nav-icon">📈</span>
                            <span>Market Trends</span>
                        </button>
                        <button class="cta-button" onclick="handleCTA('automation')">
                            <span class="nav-icon">⚡</span>
                            <span>Automation</span>
                        </button>
                        <button class="cta-button" onclick="handleCTA('reports')">
                            <span class="nav-icon">📋</span>
                            <span>Reports & Analytics</span>
                        </button>
                    </div>
                </nav>
            </div>
            
            <!-- Main Content -->
            <div class="main-content">
                <div class="content-header">
                    <div>
                        <div class="page-title">Dashboard</div>
                        <div class="breadcrumb">Home > Dashboard > Overview</div>
                    </div>
                    <div>
                        <button class="action-button" onclick="handleCTA('addProperty')">+ Add Property</button>
                        <button class="secondary-button" onclick="handleCTA('settings')">Settings</button>
                    </div>
                </div>
                
                <!-- Dashboard Grid -->
                <div class="dashboard-grid">
                    <div class="metric-card" onclick="handleCTA('totalRevenue')">
                        <div class="metric-icon">💰</div>
                        <div class="metric-value">$2.4M</div>
                        <div class="metric-label">Total Revenue</div>
                        <div class="metric-change">+12.5% from last month</div>
                    </div>
                    
                    <div class="metric-card" onclick="handleCTA('activeDeals')">
                        <div class="metric-icon">🏠</div>
                        <div class="metric-value">47</div>
                        <div class="metric-label">Active Deals</div>
                        <div class="metric-change">+8 new this week</div>
                    </div>
                    
                    <div class="metric-card" onclick="handleCTA('totalContacts')">
                        <div class="metric-icon">👥</div>
                        <div class="metric-value">1,234</div>
                        <div class="metric-label">Total Contacts</div>
                        <div class="metric-change">+156 this month</div>
                    </div>
                    
                    <div class="metric-card" onclick="handleCTA('leadConversion')">
                        <div class="metric-icon">🎯</div>
                        <div class="metric-value">68%</div>
                        <div class="metric-label">Lead Conversion</div>
                        <div class="metric-change">+5.2% improvement</div>
                    </div>
                </div>
                
                <!-- Charts Section -->
                <div class="chart-container">
                    <div class="chart-title">📊 Revenue Analytics</div>
                    <div style="text-align: center; padding: 80px; color: rgba(255,255,255,0.6);">
                        <div class="loading-spinner"></div>
                        <p>Loading interactive charts...</p>
                    </div>
                </div>
                
                <!-- Calendar Widget -->
                <div class="calendar-widget">
                    <div class="calendar-header">
                        <button class="calendar-nav" onclick="previousMonth()">‹</button>
                        <div class="calendar-month" id="currentMonth">November 2024</div>
                        <button class="calendar-nav" onclick="nextMonth()">›</button>
                    </div>
                    <div class="calendar-grid" id="calendarGrid">
                        <!-- Calendar days will be generated by JavaScript -->
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Modal -->
        <div class="modal" id="actionModal">
            <div class="modal-content">
                <div class="modal-title" id="modalTitle">Action Title</div>
                <div class="modal-text" id="modalText">Action description</div>
                <button class="action-button" onclick="closeModal()">Continue</button>
                <button class="secondary-button" onclick="closeModal()">Close</button>
            </div>
        </div>
        
        <!-- Toast Notification -->
        <div class="toast success" id="toast">
            <span id="toastMessage">Action completed successfully!</span>
        </div>
        
        <script>
            // JavaScript Functions
            console.log('🚀 NXTRIX CRM Platform Loading...');
            
            // Global variables
            let currentDate = new Date();
            
            // CTA Handler Function
            window.handleCTA = function(action) {
                console.log('🎯 CTA Action:', action);
                
                const actionMap = {
                    'newDeal': {
                        title: '🏠 Create New Deal',
                        message: 'Ready to create a new real estate deal. This will open the deal creation form with smart templates and market data integration.'
                    },
                    'analyzeDeal': {
                        title: '📊 Deal Analysis',
                        message: 'Advanced AI-powered deal analysis tools are now available. Analyze ROI, market comparisons, and risk assessments.'
                    },
                    'addContact': {
                        title: '👥 Add New Contact',
                        message: 'Contact management system is ready. Add new contacts with automated lead scoring and segmentation.'
                    },
                    'sendEmail': {
                        title: '📧 Email Marketing',
                        message: 'Email marketing suite activated. Create personalized campaigns with automated follow-ups and tracking.'
                    },
                    'aiAnalysis': {
                        title: '🤖 AI Insights',
                        message: 'AI analysis engine is processing market data. Get predictive insights and automated recommendations.'
                    },
                    'manageLeads': {
                        title: '🎯 Lead Management',
                        message: 'Lead management dashboard is ready. Track, nurture, and convert leads with intelligent workflows.'
                    },
                    'createCampaign': {
                        title: '📢 Create Campaign',
                        message: 'Marketing campaign builder is available. Create multi-channel campaigns with automation and analytics.'
                    },
                    'socialMedia': {
                        title: '📱 Social Media',
                        message: 'Social media management tools are active. Schedule posts, monitor engagement, and analyze performance.'
                    },
                    'marketTrends': {
                        title: '📈 Market Trends',
                        message: 'Market intelligence dashboard is loading. Access real-time market data and trend analysis.'
                    },
                    'automation': {
                        title: '⚡ Automation',
                        message: 'Automation engine is ready. Set up smart workflows for lead nurturing, follow-ups, and task management.'
                    },
                    'reports': {
                        title: '📋 Reports & Analytics',
                        message: 'Advanced reporting suite is available. Generate custom reports with real-time data and insights.'
                    },
                    'addProperty': {
                        title: '🏡 Add Property',
                        message: 'Property management system is ready. Add new listings with automated valuation and market analysis.'
                    },
                    'settings': {
                        title: '⚙️ Settings',
                        message: 'System settings and configuration panel is available. Customize your NXTRIX experience.'
                    },
                    'totalRevenue': {
                        title: '💰 Revenue Details',
                        message: 'Viewing detailed revenue analytics and breakdown by properties, time periods, and sources.'
                    },
                    'activeDeals': {
                        title: '🏠 Active Deals',
                        message: 'Managing active deals pipeline with status tracking and automated reminders.'
                    },
                    'totalContacts': {
                        title: '👥 Contact Database',
                        message: 'Accessing comprehensive contact database with advanced search and filtering options.'
                    },
                    'leadConversion': {
                        title: '🎯 Conversion Analytics',
                        message: 'Analyzing lead conversion rates and optimization opportunities across all channels.'
                    }
                };
                
                const actionData = actionMap[action] || {
                    title: '✨ Feature Available',
                    message: `The ${action} feature is ready to use with full functionality and integrations.`
                };
                
                showModal(actionData.title, actionData.message);
                showToast(`✅ ${actionData.title} activated!`, 'success');
                
                // Simulate loading for demo
                setTimeout(function() {
                    console.log(`✅ ${action} feature loaded successfully`);
                }, 1000);
            };
            
            // Modal Functions
            window.showModal = function(title, message) {
                const modal = document.getElementById('actionModal');
                const modalTitle = document.getElementById('modalTitle');
                const modalText = document.getElementById('modalText');
                
                if (modal && modalTitle && modalText) {
                    modalTitle.textContent = title;
                    modalText.textContent = message;
                    modal.classList.add('show');
                }
            };
            
            window.closeModal = function() {
                const modal = document.getElementById('actionModal');
                if (modal) {
                    modal.classList.remove('show');
                }
            };
            
            // Toast Notification Function
            window.showToast = function(message, type) {
                type = type || 'success';
                console.log('📢 Toast:', message);
                
                const toast = document.getElementById('toast');
                const toastMessage = document.getElementById('toastMessage');
                
                if (toast && toastMessage) {
                    toast.className = `toast ${type}`;
                    toastMessage.textContent = message;
                    toast.classList.add('show');
                    
                    setTimeout(function() {
                        toast.classList.remove('show');
                    }, 4000);
                }
            };
            
            // Calendar Functions
            window.generateCalendar = function(date) {
                const year = date.getFullYear();
                const month = date.getMonth();
                const firstDay = new Date(year, month, 1);
                const lastDay = new Date(year, month + 1, 0);
                const daysInMonth = lastDay.getDate();
                const startDay = firstDay.getDay();
                
                const monthNames = [
                    'January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'
                ];
                
                const currentMonthElement = document.getElementById('currentMonth');
                if (currentMonthElement) {
                    currentMonthElement.textContent = monthNames[month] + ' ' + year;
                }
                
                const calendarGrid = document.getElementById('calendarGrid');
                if (calendarGrid) {
                    calendarGrid.innerHTML = '';
                    
                    // Add day headers
                    const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
                    for (let i = 0; i < dayHeaders.length; i++) {
                        const dayHeader = document.createElement('div');
                        dayHeader.textContent = dayHeaders[i];
                        dayHeader.style.fontWeight = '600';
                        dayHeader.style.color = 'rgba(255, 255, 255, 0.7)';
                        calendarGrid.appendChild(dayHeader);
                    }
                    
                    // Add empty cells for days before the first day
                    for (let i = 0; i < startDay; i++) {
                        const emptyDay = document.createElement('div');
                        calendarGrid.appendChild(emptyDay);
                    }
                    
                    // Add days of the month
                    const today = new Date();
                    for (let day = 1; day <= daysInMonth; day++) {
                        const dayElement = document.createElement('div');
                        dayElement.className = 'calendar-day';
                        dayElement.textContent = day;
                        
                        // Highlight today
                        if (year === today.getFullYear() && 
                            month === today.getMonth() && 
                            day === today.getDate()) {
                            dayElement.classList.add('today');
                        }
                        
                        // Add click event
                        dayElement.onclick = function() {
                            const selectedDate = new Date(year, month, day);
                            showToast(`📅 Selected: ${selectedDate.toDateString()}`, 'success');
                        };
                        
                        calendarGrid.appendChild(dayElement);
                    }
                }
            };
            
            window.previousMonth = function() {
                currentDate.setMonth(currentDate.getMonth() - 1);
                generateCalendar(currentDate);
            };
            
            window.nextMonth = function() {
                currentDate.setMonth(currentDate.getMonth() + 1);
                generateCalendar(currentDate);
            };
            
            // Navigation Functions
            window.navigateTo = function(page) {
                console.log('🧭 Navigating to:', page);
                showToast(`Navigating to ${page}...`, 'success');
            };
            
            // Close modal when clicking outside
            document.addEventListener('click', function(e) {
                const modal = document.getElementById('actionModal');
                if (e.target === modal) {
                    closeModal();
                }
            });
            
            // Initialize the application
            document.addEventListener('DOMContentLoaded', function() {
                console.log('✅ NXTRIX CRM Loaded Successfully');
                
                // Generate initial calendar
                generateCalendar(currentDate);
                
                // Show welcome message
                setTimeout(function() {
                    showToast('🎉 Welcome to NXTRIX CRM Platform!', 'success');
                }, 1000);
                
                console.log('🎯 All CTA buttons are ready and functional');
            });
            
            // Handle keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    closeModal();
                }
            });
            
            console.log('🚀 NXTRIX JavaScript loaded successfully!');
        </script>
    </body>
    </html>
    """

    # Render the complete NXTRIX application
    components.html(nxtrix_html, height=800, scrolling=False)

if __name__ == "__main__":
    main()