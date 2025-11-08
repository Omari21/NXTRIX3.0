import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NXTRIX - Advanced Real Estate Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    # Hide Streamlit UI
    st.markdown("""
    <style>
        .stApp > header {visibility: hidden !important; height: 0px !important;}
        .stApp > div:first-child {padding-top: 0px !important;}
        .main > div {padding-top: 0px !important;}
        [data-testid="stMainMenu"] {display: none !important;}
        [data-testid="stHeader"] {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        button[data-testid="stBaseButton-headerNoPadding"] {display: none !important;}
        .block-container {
            padding-top: 0px !important;
            padding-bottom: 0px !important;
            padding-left: 0px !important;
            padding-right: 0px !important;
            max-width: 100% !important;
            margin: 0px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Streamlined NXTRIX HTML
    nxtrix_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NXTRIX - Advanced Real Estate Platform</title>
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
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: var(--background);
                color: var(--text);
                height: 100vh;
                overflow: hidden;
                position: relative;
            }
            
            /* Animated background with your preferred colors */
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
            
            @keyframes backgroundFlow {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }

            /* Glass Morphism Effects */
            .glass-container {
                background: var(--glass);
                backdrop-filter: blur(20px);
                border: 1px solid var(--glass-border);
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

            /* Sidebar */
            .sidebar {
                width: 300px;
                background: var(--surface);
                backdrop-filter: blur(20px);
                border-right: 1px solid var(--border);
                padding: 24px;
                overflow-y: auto;
            }

            .sidebar-header {
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid var(--border);
            }

            .logo {
                font-size: 2.2em;
                font-weight: 700;
                background: linear-gradient(135deg, var(--primary), var(--primary-light));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 8px;
            }

            .tagline {
                font-size: 0.9em;
                color: var(--text-muted);
            }

            /* Navigation */
            .nav-section {
                margin-bottom: 25px;
            }

            .section-title {
                font-size: 0.85em;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 12px;
                font-weight: 600;
            }

            .cta-button {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                margin: 6px 0;
                background: var(--surface-light);
                border: none;
                border-radius: 12px;
                color: var(--text);
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
                text-align: left;
                border: 1px solid transparent;
            }

            .cta-button:hover {
                background: var(--primary);
                transform: translateX(5px);
                box-shadow: 0 4px 20px rgba(124, 92, 255, 0.3);
                border-color: var(--primary-light);
            }

            .nav-icon {
                font-size: 16px;
                min-width: 20px;
                text-align: center;
            }

            /* Main Content */
            .main-content {
                flex: 1;
                padding: 24px;
                overflow-y: auto;
                background: var(--glass);
            }

            .content-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid var(--border);
            }

            .page-title {
                font-size: 2.4em;
                font-weight: 700;
                background: linear-gradient(135deg, var(--text), var(--secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .breadcrumb {
                color: var(--text-muted);
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
                background: var(--surface);
                backdrop-filter: blur(20px);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                transition: all 0.3s ease;
                cursor: pointer;
                position: relative;
                overflow: hidden;
            }

            .metric-card:hover {
                transform: translateY(-8px);
                box-shadow: 0 15px 35px rgba(124, 92, 255, 0.2);
                border-color: var(--primary);
                background: var(--surface-light);
            }

            .metric-icon {
                font-size: 2.5em;
                margin-bottom: 15px;
                opacity: 0.8;
            }

            .metric-value {
                font-size: 2.8em;
                font-weight: 700;
                color: var(--primary);
                margin: 10px 0;
            }

            .metric-label {
                font-size: 1.1em;
                color: var(--text);
                font-weight: 600;
            }

            .metric-change {
                font-size: 0.9em;
                margin-top: 8px;
                padding: 4px 8px;
                border-radius: 12px;
                background: var(--success);
                color: white;
            }

            /* Action Buttons */
            .action-button {
                background: linear-gradient(135deg, var(--primary), var(--primary-dark));
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
                box-shadow: 0 8px 25px rgba(124, 92, 255, 0.4);
            }

            .secondary-button {
                background: var(--surface-light);
                color: var(--text);
                border: 1px solid var(--border);
                padding: 10px 20px;
                border-radius: 10px;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 5px;
            }

            .secondary-button:hover {
                background: var(--surface);
                border-color: var(--primary);
            }

            /* Chart Container */
            .chart-container {
                background: var(--surface);
                backdrop-filter: blur(20px);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 24px;
                margin: 20px 0;
                min-height: 300px;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
            }

            /* Toast */
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
                background: linear-gradient(135deg, var(--primary), var(--primary-dark));
                box-shadow: 0 8px 25px rgba(124, 92, 255, 0.3);
            }

            .toast.show {
                transform: translateX(0);
            }

            /* Modal */
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
                background: var(--surface);
                backdrop-filter: blur(30px);
                border: 1px solid var(--border);
                border-radius: 20px;
                padding: 30px;
                max-width: 600px;
                width: 90%;
                text-align: left;
                max-height: 80vh;
                overflow-y: auto;
            }

            .modal-title {
                font-size: 1.6em;
                font-weight: 700;
                margin-bottom: 15px;
                color: var(--primary);
            }

            .modal-text {
                font-size: 1.1em;
                color: var(--text-muted);
                margin-bottom: 25px;
                line-height: 1.5;
            }

            /* Feature Interface Styles */
            .feature-interface {
                margin-top: 20px;
            }

            .feature-form {
                display: grid;
                gap: 15px;
                margin: 20px 0;
            }

            .form-group {
                display: flex;
                flex-direction: column;
            }

            .form-label {
                font-size: 14px;
                font-weight: 600;
                color: var(--text);
                margin-bottom: 5px;
            }

            .form-input {
                padding: 10px 12px;
                background: var(--surface-light);
                border: 1px solid var(--border);
                border-radius: 8px;
                color: var(--text);
                font-size: 14px;
            }

            .form-input:focus {
                outline: none;
                border-color: var(--primary);
                box-shadow: 0 0 10px rgba(124, 92, 255, 0.2);
            }

            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }

            .feature-card {
                background: var(--surface-light);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 15px;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .feature-card:hover {
                border-color: var(--primary);
                background: var(--surface);
            }

            .feature-card h4 {
                color: var(--primary);
                margin-bottom: 8px;
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                .app-container {
                    flex-direction: column;
                }
                .sidebar {
                    width: 100%;
                    height: auto;
                    max-height: 200px;
                }
                .dashboard-grid {
                    grid-template-columns: 1fr;
                }
            }

            /* Scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
            }
            ::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.1);
            }
            ::-webkit-scrollbar-thumb {
                background: rgba(76, 175, 80, 0.6);
                border-radius: 10px;
            }
        </style>
    </head>
    <body>
        <div class="app-container">
            <!-- Sidebar -->
            <div class="sidebar">
                <div class="sidebar-header">
                    <div class="logo">🏢 NXTRIX</div>
                    <div class="tagline">Advanced Real Estate Platform</div>
                </div>
                
                <nav>
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
                    <div>
                        <h3 style="color: #4CAF50; margin-bottom: 15px;">📊 Revenue Analytics</h3>
                        <p style="color: rgba(255,255,255,0.7);">Interactive charts and analytics dashboard</p>
                        <button class="action-button" onclick="handleCTA('viewCharts')" style="margin-top: 20px;">
                            View Detailed Analytics
                        </button>
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
        <div class="toast" id="toast">
            <span id="toastMessage">Action completed successfully!</span>
        </div>
        
        <script>
            // IMMEDIATE FUNCTION DEFINITIONS
            console.log('🚀 NXTRIX Platform Loading...');
            
            // CTA Handler Function - Now redirects to actual feature pages
            window.handleCTA = function(action) {
                console.log('🎯 CTA Action:', action);
                showToast(`🔄 Loading ${action} feature...`);
                
                // Hide the main content and show the feature page
                document.querySelector('.main-content').style.display = 'none';
                
                // Create or show feature page
                let featurePage = document.getElementById('featurePage');
                if (!featurePage) {
                    featurePage = document.createElement('div');
                    featurePage.id = 'featurePage';
                    featurePage.style.cssText = `
                        flex: 1;
                        padding: 24px;
                        overflow-y: auto;
                        background: var(--glass);
                    `;
                    document.querySelector('.app-container').appendChild(featurePage);
                }
                
                featurePage.style.display = 'block';
                featurePage.innerHTML = getFeaturePageHTML(action);
                
                // Update browser history
                window.history.pushState({feature: action}, '', `#${action}`);
            };
            
            // Feature page HTML generator
            function getFeaturePageHTML(action) {
                const featurePages = {
                    'newDeal': `
                        <div class="content-header">
                            <div>
                                <div class="page-title">🏠 Create New Deal</div>
                                <div class="breadcrumb">Dashboard > Deals > Create New</div>
                            </div>
                            <button class="secondary-button" onclick="goBack()">← Back to Dashboard</button>
                        </div>
                        
                        <div style="max-width: 800px;">
                            <div style="background: var(--surface); padding: 30px; border-radius: 16px; border: 1px solid var(--border);">
                                <h3 style="color: var(--primary); margin-bottom: 20px;">Deal Information</h3>
                                
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                                    <div class="form-group">
                                        <label class="form-label">Property Address *</label>
                                        <input type="text" class="form-input" placeholder="123 Main Street, City, State" id="propertyAddress">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Purchase Price *</label>
                                        <input type="number" class="form-input" placeholder="500000" id="purchasePrice">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Deal Type</label>
                                        <select class="form-input" id="dealType">
                                            <option>Fix & Flip</option>
                                            <option>Buy & Hold</option>
                                            <option>Wholesale</option>
                                            <option>Commercial</option>
                                            <option>BRRRR</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Expected ROI (%)</label>
                                        <input type="number" class="form-input" placeholder="25" id="expectedRoi">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Down Payment</label>
                                        <input type="number" class="form-input" placeholder="100000" id="downPayment">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Estimated Rehab Cost</label>
                                        <input type="number" class="form-input" placeholder="50000" id="rehabCost">
                                    </div>
                                </div>
                                
                                <div style="margin-bottom: 30px;">
                                    <label class="form-label">Deal Notes</label>
                                    <textarea class="form-input" style="height: 100px; resize: vertical;" placeholder="Enter any additional details about this deal..." id="dealNotes"></textarea>
                                </div>
                                
                                <div style="text-align: center;">
                                    <button class="action-button" onclick="createDeal()" style="margin-right: 10px;">Create Deal</button>
                                    <button class="secondary-button" onclick="saveDraft()">Save as Draft</button>
                                </div>
                            </div>
                            
                            <div style="background: var(--surface); padding: 20px; border-radius: 16px; border: 1px solid var(--border); margin-top: 20px;">
                                <h4 style="color: var(--primary); margin-bottom: 15px;">🤖 AI Deal Insights</h4>
                                <p style="color: var(--text-muted);">Our AI will analyze your deal automatically and provide insights on:</p>
                                <ul style="color: var(--text-muted); margin-left: 20px; margin-top: 10px;">
                                    <li>Market comparables and pricing analysis</li>
                                    <li>ROI projections and cash flow modeling</li>
                                    <li>Risk assessment and mitigation strategies</li>
                                    <li>Optimal financing recommendations</li>
                                </ul>
                            </div>
                        </div>
                    `,
                    'analyzeDeal': `
                        <div class="content-header">
                            <div>
                                <div class="page-title">📊 Deal Analysis Center</div>
                                <div class="breadcrumb">Dashboard > Analytics > Deal Analysis</div>
                            </div>
                            <button class="secondary-button" onclick="goBack()">← Back to Dashboard</button>
                        </div>
                        
                        <div style="margin-bottom: 30px;">
                            <div style="background: var(--surface); padding: 20px; border-radius: 16px; border: 1px solid var(--border);">
                                <h3 style="color: var(--primary); margin-bottom: 20px;">Select Property to Analyze</h3>
                                <div style="display: grid; grid-template-columns: 1fr auto; gap: 15px; align-items: end;">
                                    <div class="form-group">
                                        <label class="form-label">Property Address</label>
                                        <input type="text" class="form-input" placeholder="Enter property address or select from deals" id="analyzeAddress">
                                    </div>
                                    <button class="action-button" onclick="runFullAnalysis()">Analyze Property</button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="feature-grid" style="grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));">
                            <div class="feature-card" onclick="runSpecificAnalysis('roi')" style="cursor: pointer; padding: 20px;">
                                <h4 style="color: var(--primary);">📈 ROI Analysis</h4>
                                <p style="color: var(--text-muted); margin: 10px 0;">Calculate projected returns, cash flow, and profitability metrics</p>
                                <div style="margin-top: 15px;">
                                    <div style="color: var(--success); font-size: 0.9em;">• Cash-on-cash return</div>
                                    <div style="color: var(--success); font-size: 0.9em;">• Cap rate calculation</div>
                                    <div style="color: var(--success); font-size: 0.9em;">• IRR projections</div>
                                </div>
                            </div>
                            
                            <div class="feature-card" onclick="runSpecificAnalysis('market')" style="cursor: pointer; padding: 20px;">
                                <h4 style="color: var(--primary);">🏘️ Market Analysis</h4>
                                <p style="color: var(--text-muted); margin: 10px 0;">Compare with neighborhood comps and market trends</p>
                                <div style="margin-top: 15px;">
                                    <div style="color: var(--success); font-size: 0.9em;">• Comparable sales data</div>
                                    <div style="color: var(--success); font-size: 0.9em;">• Market trend analysis</div>
                                    <div style="color: var(--success); font-size: 0.9em;">• Price per sq ft metrics</div>
                                </div>
                            </div>
                            
                            <div class="feature-card" onclick="runSpecificAnalysis('risk')" style="cursor: pointer; padding: 20px;">
                                <h4 style="color: var(--primary);">⚠️ Risk Assessment</h4>
                                <p style="color: var(--text-muted); margin: 10px 0;">Identify potential risks and mitigation strategies</p>
                                <div style="margin-top: 15px;">
                                    <div style="color: var(--warning); font-size: 0.9em;">• Market volatility risk</div>
                                    <div style="color: var(--warning); font-size: 0.9em;">• Liquidity assessment</div>
                                    <div style="color: var(--warning); font-size: 0.9em;">• Regulatory compliance</div>
                                </div>
                            </div>
                            
                            <div class="feature-card" onclick="runSpecificAnalysis('financing')" style="cursor: pointer; padding: 20px;">
                                <h4 style="color: var(--primary);">💰 Financing Options</h4>
                                <p style="color: var(--text-muted); margin: 10px 0;">Find optimal financing strategies and loan products</p>
                                <div style="margin-top: 15px;">
                                    <div style="color: var(--secondary); font-size: 0.9em;">• Loan comparison tool</div>
                                    <div style="color: var(--secondary); font-size: 0.9em;">• Interest rate analysis</div>
                                    <div style="color: var(--secondary); font-size: 0.9em;">• Payment scenarios</div>
                                </div>
                            </div>
                        </div>
                        
                        <div id="analysisResults" style="margin-top: 30px; display: none;">
                            <div style="background: var(--surface); padding: 25px; border-radius: 16px; border: 1px solid var(--border);">
                                <h3 style="color: var(--primary); margin-bottom: 20px;">Analysis Results</h3>
                                <div id="resultsContent"></div>
                            </div>
                        </div>
                    `,
                    'addContact': `
                        <div class="content-header">
                            <div>
                                <div class="page-title">👥 Contact Management</div>
                                <div class="breadcrumb">Dashboard > CRM > Add Contact</div>
                            </div>
                            <button class="secondary-button" onclick="goBack()">← Back to Dashboard</button>
                        </div>
                        
                        <div style="max-width: 900px;">
                            <div style="background: var(--surface); padding: 30px; border-radius: 16px; border: 1px solid var(--border);">
                                <h3 style="color: var(--primary); margin-bottom: 20px;">Contact Information</h3>
                                
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                                    <div class="form-group">
                                        <label class="form-label">First Name *</label>
                                        <input type="text" class="form-input" placeholder="John" id="firstName">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Last Name *</label>
                                        <input type="text" class="form-input" placeholder="Smith" id="lastName">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Email Address *</label>
                                        <input type="email" class="form-input" placeholder="john@example.com" id="contactEmail">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Phone Number</label>
                                        <input type="tel" class="form-input" placeholder="(555) 123-4567" id="contactPhone">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Contact Type *</label>
                                        <select class="form-input" id="contactType">
                                            <option>Investor</option>
                                            <option>Seller</option>
                                            <option>Buyer</option>
                                            <option>Real Estate Agent</option>
                                            <option>Contractor</option>
                                            <option>Lender</option>
                                            <option>Attorney</option>
                                            <option>Other</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Lead Source</label>
                                        <select class="form-input" id="leadSource">
                                            <option>Website</option>
                                            <option>Referral</option>
                                            <option>Social Media</option>
                                            <option>Networking Event</option>
                                            <option>Cold Outreach</option>
                                            <option>Marketing Campaign</option>
                                        </select>
                                    </div>
                                </div>
                                
                                <div style="margin-bottom: 25px;">
                                    <label class="form-label">Notes</label>
                                    <textarea class="form-input" style="height: 100px; resize: vertical;" placeholder="Add any relevant notes about this contact..." id="contactNotes"></textarea>
                                </div>
                                
                                <div style="text-align: center;">
                                    <button class="action-button" onclick="saveContact()">Add Contact</button>
                                    <button class="secondary-button" onclick="saveContactDraft()">Save Draft</button>
                                </div>
                            </div>
                            
                            <div style="background: var(--surface); padding: 20px; border-radius: 16px; border: 1px solid var(--border); margin-top: 20px;">
                                <h4 style="color: var(--primary); margin-bottom: 15px;">🤖 AI Lead Scoring</h4>
                                <p style="color: var(--text-muted);">Our AI will automatically score this lead based on:</p>
                                <ul style="color: var(--text-muted); margin-left: 20px; margin-top: 10px;">
                                    <li>Contact type and investment potential</li>
                                    <li>Lead source quality and conversion rates</li>
                                    <li>Interaction history and engagement</li>
                                    <li>Market activity and timing</li>
                                </ul>
                            </div>
                        </div>
                    `,
                    'sendEmail': `
                        <div class="content-header">
                            <div>
                                <div class="page-title">📧 Email Marketing Center</div>
                                <div class="breadcrumb">Dashboard > Marketing > Email Campaigns</div>
                            </div>
                            <button class="secondary-button" onclick="goBack()">← Back to Dashboard</button>
                        </div>
                        
                        <div style="max-width: 1000px;">
                            <div style="background: var(--surface); padding: 30px; border-radius: 16px; border: 1px solid var(--border);">
                                <h3 style="color: var(--primary); margin-bottom: 20px;">Create Email Campaign</h3>
                                
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                                    <div class="form-group">
                                        <label class="form-label">Campaign Name *</label>
                                        <input type="text" class="form-input" placeholder="Q4 Investment Opportunities" id="campaignName">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Subject Line *</label>
                                        <input type="text" class="form-input" placeholder="Exclusive Real Estate Opportunities" id="emailSubject">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Target Audience</label>
                                        <select class="form-input" id="targetAudience">
                                            <option>All Contacts (1,234)</option>
                                            <option>Active Investors (456)</option>
                                            <option>Potential Sellers (234)</option>
                                            <option>Qualified Buyers (123)</option>
                                            <option>Custom Segment</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Send Time</label>
                                        <select class="form-input" id="sendTime">
                                            <option>Send Now</option>
                                            <option>Schedule for Later</option>
                                            <option>Best Time (AI Optimized)</option>
                                        </select>
                                    </div>
                                </div>
                                
                                <div style="margin-bottom: 25px;">
                                    <label class="form-label">Email Template</label>
                                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 10px;">
                                        <div class="feature-card" onclick="selectTemplate('investment')" style="cursor: pointer; padding: 15px; text-align: center;">
                                            <h5 style="color: var(--primary);">💼 Investment Opportunity</h5>
                                            <p style="font-size: 0.9em; color: var(--text-muted);">Showcase new deals</p>
                                        </div>
                                        <div class="feature-card" onclick="selectTemplate('market')" style="cursor: pointer; padding: 15px; text-align: center;">
                                            <h5 style="color: var(--primary);">📊 Market Update</h5>
                                            <p style="font-size: 0.9em; color: var(--text-muted);">Market insights</p>
                                        </div>
                                        <div class="feature-card" onclick="selectTemplate('newsletter')" style="cursor: pointer; padding: 15px; text-align: center;">
                                            <h5 style="color: var(--primary);">📰 Newsletter</h5>
                                            <p style="font-size: 0.9em; color: var(--text-muted);">Monthly updates</p>
                                        </div>
                                        <div class="feature-card" onclick="selectTemplate('custom')" style="cursor: pointer; padding: 15px; text-align: center;">
                                            <h5 style="color: var(--primary);">✨ Custom</h5>
                                            <p style="font-size: 0.9em; color: var(--text-muted);">Build from scratch</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <div style="text-align: center;">
                                    <button class="action-button" onclick="createCampaign()">Create Campaign</button>
                                    <button class="secondary-button" onclick="previewCampaign()">Preview</button>
                                    <button class="secondary-button" onclick="saveCampaignDraft()">Save Draft</button>
                                </div>
                            </div>
                        </div>
                    `,
                    'aiAnalysis': `
                        <div class="content-header">
                            <div>
                                <div class="page-title">🤖 AI Market Intelligence</div>
                                <div class="breadcrumb">Dashboard > AI > Market Insights</div>
                            </div>
                            <button class="secondary-button" onclick="goBack()">← Back to Dashboard</button>
                        </div>
                        
                        <div class="feature-grid" style="grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); margin-bottom: 30px;">
                            <div class="feature-card" onclick="generateAIReport('market')" style="cursor: pointer; padding: 25px;">
                                <h4 style="color: var(--primary);">📊 Market Trends Analysis</h4>
                                <p style="color: var(--text-muted); margin: 15px 0;">Get AI-powered insights on current market conditions and future predictions</p>
                                <div style="margin-top: 15px;">
                                    <div style="color: var(--success); font-size: 0.9em;">• Price trend predictions</div>
                                    <div style="color: var(--success); font-size: 0.9em;">• Inventory level analysis</div>
                                    <div style="color: var(--success); font-size: 0.9em;">• Seasonal patterns</div>
                                </div>
                                <button class="action-button" style="margin-top: 15px; width: 100%;">Generate Report</button>
                            </div>
                            
                            <div class="feature-card" onclick="generateAIReport('properties')" style="cursor: pointer; padding: 25px;">
                                <h4 style="color: var(--primary);">🏠 Property Recommendations</h4>
                                <p style="color: var(--text-muted); margin: 15px 0;">AI-curated investment opportunities based on your criteria</p>
                                <div style="margin-top: 15px;">
                                    <div style="color: var(--success); font-size: 0.9em;">• ROI potential scoring</div>
                                    <div style="color: var(--success); font-size: 0.9em;">• Risk-adjusted returns</div>
                                    <div style="color: var(--success); font-size: 0.9em;">• Market timing insights</div>
                                </div>
                                <button class="action-button" style="margin-top: 15px; width: 100%;">Find Properties</button>
                            </div>
                            
                            <div class="feature-card" onclick="generateAIReport('pricing')" style="cursor: pointer; padding: 25px;">
                                <h4 style="color: var(--primary);">💲 Automated Valuation</h4>
                                <p style="color: var(--text-muted); margin: 15px 0;">Get instant property valuations using AI and market data</p>
                                <div style="margin-top: 15px;">
                                    <div style="color: var(--success); font-size: 0.9em;">• Comparative market analysis</div>
                                    <div style="color: var(--success); font-size: 0.9em;">• Rental income estimates</div>
                                    <div style="color: var(--success); font-size: 0.9em;">• Appreciation forecasts</div>
                                </div>
                                <button class="action-button" style="margin-top: 15px; width: 100%;">Value Property</button>
                            </div>
                            
                            <div class="feature-card" onclick="generateAIReport('leads')" style="cursor: pointer; padding: 25px;">
                                <h4 style="color: var(--primary);">🎯 Lead Intelligence</h4>
                                <p style="color: var(--text-muted); margin: 15px 0;">AI-powered lead scoring and prioritization system</p>
                                <div style="margin-top: 15px;">
                                    <div style="color: var(--success); font-size: 0.9em;">• Lead scoring algorithm</div>
                                    <div style="color: var(--success); font-size: 0.9em;">• Conversion probability</div>
                                    <div style="color: var(--success); font-size: 0.9em;">• Optimal contact timing</div>
                                </div>
                                <button class="action-button" style="margin-top: 15px; width: 100%;">Analyze Leads</button>
                            </div>
                        </div>
                        
                        <div id="aiResults" style="display: none;">
                            <div style="background: var(--surface); padding: 25px; border-radius: 16px; border: 1px solid var(--border);">
                                <h3 style="color: var(--primary); margin-bottom: 20px;">AI Analysis Results</h3>
                                <div id="aiResultsContent"></div>
                            </div>
                        </div>
                    `
                };
                
                return featurePages[action] || `
                    <div class="content-header">
                        <div>
                            <div class="page-title">✨ ${action.charAt(0).toUpperCase() + action.slice(1)}</div>
                            <div class="breadcrumb">Dashboard > ${action}</div>
                        </div>
                        <button class="secondary-button" onclick="goBack()">← Back to Dashboard</button>
                    </div>
                    <div style="background: var(--surface); padding: 30px; border-radius: 16px; border: 1px solid var(--border); text-align: center;">
                        <h3 style="color: var(--primary);">Feature Coming Soon</h3>
                        <p style="color: var(--text-muted);">This feature is currently under development.</p>
                        <button class="action-button" onclick="goBack()" style="margin-top: 20px;">Return to Dashboard</button>
                    </div>
                `;
            }
            
            // Navigation function
            window.goBack = function() {
                const featurePage = document.getElementById('featurePage');
                if (featurePage) {
                    featurePage.style.display = 'none';
                }
                document.querySelector('.main-content').style.display = 'block';
                window.history.pushState({}, '', '#dashboard');
                showToast('📊 Returned to dashboard');
            };
            
            // Modal Functions
            window.showModal = function(title, content) {
                const modal = document.getElementById('actionModal');
                const modalTitle = document.getElementById('modalTitle');
                const modalText = document.getElementById('modalText');
                
                if (modal && modalTitle && modalText) {
                    modalTitle.textContent = title;
                    modalText.innerHTML = content; // Use innerHTML for rich content
                    modal.classList.add('show');
                }
            };
            
            window.closeModal = function() {
                const modal = document.getElementById('actionModal');
                if (modal) {
                    modal.classList.remove('show');
                }
            };
            
            // Feature Action Functions
            window.submitNewDeal = function() {
                const address = document.getElementById('propertyAddress')?.value || '';
                const price = document.getElementById('purchasePrice')?.value || '';
                const type = document.getElementById('dealType')?.value || '';
                const roi = document.getElementById('expectedRoi')?.value || '';
                
                if (address && price) {
                    showToast(`✅ Deal created for ${address} - $${price}`);
                    closeModal();
                    setTimeout(() => {
                        showToast('🔄 Running market analysis...');
                    }, 2000);
                } else {
                    showToast('⚠️ Please fill in required fields', 'warning');
                }
            };
            
            window.submitContact = function() {
                const name = document.getElementById('contactName')?.value || '';
                const email = document.getElementById('contactEmail')?.value || '';
                const phone = document.getElementById('contactPhone')?.value || '';
                const type = document.getElementById('contactType')?.value || '';
                
                if (name && email) {
                    showToast(`✅ Contact ${name} added successfully`);
                    closeModal();
                    setTimeout(() => {
                        showToast('🤖 AI lead scoring in progress...');
                    }, 1500);
                } else {
                    showToast('⚠️ Please fill in name and email', 'warning');
                }
            };
            
            window.launchCampaign = function() {
                const campaign = document.getElementById('campaignName')?.value || '';
                const subject = document.getElementById('emailSubject')?.value || '';
                
                if (campaign && subject) {
                    showToast(`✅ Campaign "${campaign}" launched!`);
                    closeModal();
                    setTimeout(() => {
                        showToast('📈 Campaign analytics available');
                    }, 3000);
                } else {
                    showToast('⚠️ Please fill in campaign details', 'warning');
                }
            };
            
            window.previewEmail = function() {
                showToast('📧 Opening email preview...');
                closeModal();
            };
            
            window.runAnalysis = function(type) {
                const analysisTypes = {
                    'roi': 'ROI Analysis',
                    'market': 'Market Comparison',
                    'risk': 'Risk Assessment', 
                    'financing': 'Financing Analysis'
                };
                
                showToast(`🔄 Running ${analysisTypes[type]}...`);
                closeModal();
                
                setTimeout(() => {
                    showToast(`✅ ${analysisTypes[type]} complete!`);
                }, 2500);
            };
            
            window.generateInsight = function(type) {
                const insightTypes = {
                    'market': 'Market Trends Report',
                    'properties': 'Property Recommendations',
                    'pricing': 'Pricing Analysis',
                    'leads': 'Lead Scoring Update'
                };
                
                showToast(`🤖 Generating ${insightTypes[type]}...`);
                closeModal();
                
                setTimeout(() => {
                    showToast(`✅ ${insightTypes[type]} ready!`);
                }, 2000);
            };
            
            // Enhanced functions for full-page interfaces
            window.createDeal = function() {
                const address = document.getElementById('propertyAddress')?.value;
                const price = document.getElementById('purchasePrice')?.value;
                
                if (!address || !price) {
                    showToast('⚠️ Please fill in required fields', 'warning');
                    return;
                }
                
                showToast('🔄 Creating deal...', 'info');
                setTimeout(() => {
                    showToast('✅ Deal created successfully! Added to your pipeline.', 'success');
                    // Clear form
                    document.getElementById('propertyAddress').value = '';
                    document.getElementById('purchasePrice').value = '';
                    if(document.getElementById('expectedRoi')) document.getElementById('expectedRoi').value = '';
                    if(document.getElementById('dealNotes')) document.getElementById('dealNotes').value = '';
                }, 1500);
            };
            
            window.saveDraft = function() {
                showToast('💾 Deal saved as draft', 'info');
            };
            
            window.saveContact = function() {
                const firstName = document.getElementById('firstName')?.value;
                const email = document.getElementById('contactEmail')?.value;
                
                if (!firstName || !email) {
                    showToast('⚠️ Please fill in required fields', 'warning');
                    return;
                }
                
                showToast('🔄 Adding contact...', 'info');
                setTimeout(() => {
                    showToast('✅ Contact added successfully! Lead score: 85/100', 'success');
                    // Clear form
                    document.getElementById('firstName').value = '';
                    if(document.getElementById('lastName')) document.getElementById('lastName').value = '';
                    document.getElementById('contactEmail').value = '';
                    if(document.getElementById('contactPhone')) document.getElementById('contactPhone').value = '';
                    if(document.getElementById('contactNotes')) document.getElementById('contactNotes').value = '';
                }, 1500);
            };
            
            window.saveContactDraft = function() {
                showToast('💾 Contact saved as draft', 'info');
            };
            
            window.createCampaign = function() {
                const name = document.getElementById('campaignName')?.value;
                const subject = document.getElementById('emailSubject')?.value;
                
                if (!name || !subject) {
                    showToast('⚠️ Please fill in required fields', 'warning');
                    return;
                }
                
                showToast('🔄 Creating campaign...', 'info');
                setTimeout(() => {
                    showToast('✅ Campaign created! Scheduled for optimal send time.', 'success');
                    document.getElementById('campaignName').value = '';
                    document.getElementById('emailSubject').value = '';
                }, 1500);
            };
            
            window.previewCampaign = function() {
                showToast('👀 Opening campaign preview...', 'info');
            };
            
            window.saveCampaignDraft = function() {
                showToast('💾 Campaign saved as draft', 'info');
            };
            
            window.selectTemplate = function(type) {
                showToast(`📧 Selected ${type} template`, 'info');
                // Highlight selected template
                document.querySelectorAll('.feature-card').forEach(card => {
                    card.style.border = '1px solid var(--border)';
                });
                event.target.closest('.feature-card').style.border = '2px solid var(--primary)';
            };
            
            window.runFullAnalysis = function() {
                const address = document.getElementById('analyzeAddress')?.value;
                if (!address) {
                    showToast('⚠️ Please enter a property address', 'warning');
                    return;
                }
                
                showToast('🔄 Running comprehensive analysis...', 'info');
                setTimeout(() => {
                    const resultsDiv = document.getElementById('analysisResults');
                    const contentDiv = document.getElementById('resultsContent');
                    
                    if (resultsDiv && contentDiv) {
                        contentDiv.innerHTML = `
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                                <div style="background: var(--glass); padding: 20px; border-radius: 12px; border: 1px solid var(--border);">
                                    <h4 style="color: var(--success); margin-bottom: 10px;">📈 ROI Analysis</h4>
                                    <div style="color: var(--text-muted);">
                                        <div>Projected ROI: <strong style="color: var(--success);">28.5%</strong></div>
                                        <div>Cash Flow: <strong style="color: var(--success);">$2,400/month</strong></div>
                                        <div>Cap Rate: <strong>6.8%</strong></div>
                                    </div>
                                </div>
                                <div style="background: var(--glass); padding: 20px; border-radius: 12px; border: 1px solid var(--border);">
                                    <h4 style="color: var(--secondary); margin-bottom: 10px;">🏘️ Market Comparison</h4>
                                    <div style="color: var(--text-muted);">
                                        <div>Avg. Price/SF: <strong>$185</strong></div>
                                        <div>This Property: <strong style="color: var(--success);">$165/SF</strong></div>
                                        <div>Market Score: <strong>92/100</strong></div>
                                    </div>
                                </div>
                                <div style="background: var(--glass); padding: 20px; border-radius: 12px; border: 1px solid var(--border);">
                                    <h4 style="color: var(--warning); margin-bottom: 10px;">⚠️ Risk Assessment</h4>
                                    <div style="color: var(--text-muted);">
                                        <div>Overall Risk: <strong style="color: var(--warning);">Medium</strong></div>
                                        <div>Market Volatility: <strong>Low</strong></div>
                                        <div>Liquidity: <strong>High</strong></div>
                                    </div>
                                </div>
                            </div>
                        `;
                        
                        resultsDiv.style.display = 'block';
                        showToast('✅ Analysis complete! Results generated.', 'success');
                    }
                }, 2000);
            };
            
            window.runSpecificAnalysis = function(type) {
                const typeMap = {
                    'roi': 'ROI and cash flow analysis',
                    'market': 'Market comparison analysis', 
                    'risk': 'Risk assessment analysis',
                    'financing': 'Financing options analysis'
                };
                
                showToast(`🔄 Running ${typeMap[type]}...`, 'info');
                setTimeout(() => {
                    showToast(`✅ ${typeMap[type]} complete!`, 'success');
                }, 1500);
            };
            
            window.generateAIReport = function(type) {
                const typeMap = {
                    'market': 'Market trends analysis',
                    'properties': 'Property recommendations',
                    'pricing': 'Automated valuation',
                    'leads': 'Lead intelligence analysis'
                };
                
                showToast(`🤖 Generating ${typeMap[type]}...`, 'info');
                setTimeout(() => {
                    const resultsDiv = document.getElementById('aiResults');
                    const contentDiv = document.getElementById('aiResultsContent');
                    
                    if (resultsDiv && contentDiv) {
                        let reportContent = '';
                        switch(type) {
                            case 'market':
                                reportContent = `
                                    <h4 style="color: var(--primary);">📊 Market Trends Report</h4>
                                    <div style="background: var(--glass); padding: 20px; border-radius: 12px; margin-top: 15px;">
                                        <p><strong>Market Outlook:</strong> Favorable conditions for investors</p>
                                        <p><strong>Price Trend:</strong> +3.2% appreciation expected over next 12 months</p>
                                        <p><strong>Inventory Levels:</strong> Low supply driving competitive market</p>
                                        <p><strong>Recommended Action:</strong> Good time to buy, hold for appreciation</p>
                                    </div>
                                `;
                                break;
                            case 'properties':
                                reportContent = `
                                    <h4 style="color: var(--primary);">🏠 AI Property Recommendations</h4>
                                    <div style="background: var(--glass); padding: 20px; border-radius: 12px; margin-top: 15px;">
                                        <div style="border-left: 3px solid var(--success); padding-left: 15px; margin-bottom: 15px;">
                                            <strong>1234 Oak Avenue</strong> - ROI Score: 94/100<br>
                                            <span style="color: var(--text-muted);">$485K • 3BR/2BA • Projected ROI: 31%</span>
                                        </div>
                                        <div style="border-left: 3px solid var(--success); padding-left: 15px; margin-bottom: 15px;">
                                            <strong>567 Pine Street</strong> - ROI Score: 89/100<br>
                                            <span style="color: var(--text-muted);">$320K • 2BR/1BA • Projected ROI: 28%</span>
                                        </div>
                                    </div>
                                `;
                                break;
                            case 'pricing':
                                reportContent = `
                                    <h4 style="color: var(--primary);">💲 Automated Valuation Model</h4>
                                    <div style="background: var(--glass); padding: 20px; border-radius: 12px; margin-top: 15px;">
                                        <p><strong>Estimated Value:</strong> $425,000 - $445,000</p>
                                        <p><strong>Confidence Level:</strong> 87%</p>
                                        <p><strong>Rental Income:</strong> $2,100 - $2,400/month</p>
                                        <p><strong>Value Trend:</strong> Stable with slight upward trajectory</p>
                                    </div>
                                `;
                                break;
                            case 'leads':
                                reportContent = `
                                    <h4 style="color: var(--primary);">🎯 Lead Intelligence Report</h4>
                                    <div style="background: var(--glass); padding: 20px; border-radius: 12px; margin-top: 15px;">
                                        <div style="margin-bottom: 15px;">
                                            <strong>High Priority Leads (Score 80+):</strong> 12 contacts<br>
                                            <span style="color: var(--text-muted);">Recommended: Contact within 24 hours</span>
                                        </div>
                                        <div style="margin-bottom: 15px;">
                                            <strong>Medium Priority Leads (Score 60-79):</strong> 28 contacts<br>
                                            <span style="color: var(--text-muted);">Recommended: Follow up this week</span>
                                        </div>
                                        <div>
                                            <strong>Nurture Leads (Score <60):</strong> 45 contacts<br>
                                            <span style="color: var(--text-muted);">Recommended: Monthly check-ins</span>
                                        </div>
                                    </div>
                                `;
                                break;
                        }
                        
                        contentDiv.innerHTML = reportContent;
                        resultsDiv.style.display = 'block';
                        showToast(`✅ ${typeMap[type]} generated!`, 'success');
                    }
                }, 2000);
            };
            
            // Toast Function
            window.showToast = function(message, type = 'success') {
                console.log('📢 Toast:', message);
                
                const toast = document.getElementById('toast');
                const toastMessage = document.getElementById('toastMessage');
                
                if (toast && toastMessage) {
                    toastMessage.textContent = message;
                    
                    // Update toast styling based on type
                    if (type === 'warning') {
                        toast.style.background = 'linear-gradient(135deg, var(--warning), #e97600)';
                    } else if (type === 'error') {
                        toast.style.background = 'linear-gradient(135deg, var(--error), #dc2626)';
                    } else {
                        toast.style.background = 'linear-gradient(135deg, var(--primary), var(--primary-dark))';
                    }
                    
                    toast.classList.add('show');
                    
                    setTimeout(function() {
                        toast.classList.remove('show');
                    }, 4000);
                }
            };
            
            // Close modal when clicking outside
            document.addEventListener('click', function(e) {
                const modal = document.getElementById('actionModal');
                if (e.target === modal) {
                    closeModal();
                }
            });
            
            // Initialize
            document.addEventListener('DOMContentLoaded', function() {
                console.log('✅ NXTRIX Platform Loaded Successfully');
                showToast('🎉 Welcome to NXTRIX CRM Platform!');
            });
            
            // Handle ESC key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    closeModal();
                }
            });
            
            console.log('🚀 NXTRIX Functions Ready');
        </script>
    </body>
    </html>
    """

    # Render the streamlined NXTRIX application
    components.html(nxtrix_html, height=800, scrolling=False)

if __name__ == "__main__":
    main()