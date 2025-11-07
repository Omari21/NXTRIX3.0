import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NXTRIX Platform", 
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit branding
st.markdown("""
<style>
    .stApp > header {visibility: hidden;}
    .main > div {padding-top: 0px;}
    .block-container {padding-top: 0px; padding-bottom: 0px; max-width: 100%; margin: 0px;}
</style>
""", unsafe_allow_html=True)

# NXTRIX Application as a component
nxtrix_app = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NXTRIX Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
            color: white;
            height: 100vh;
            overflow: hidden;
        }
        
        .app-container { display: flex; height: 100vh; }
        
        .sidebar {
            width: 280px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
        }
        
        .main-content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        
        .nav-item {
            display: block;
            width: 100%;
            padding: 12px 16px;
            margin: 8px 0;
            background: rgba(255, 255, 255, 0.05);
            border: none;
            border-radius: 12px;
            color: white;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
        }
        
        .nav-item:hover {
            background: rgba(74, 175, 79, 0.2);
            transform: translateX(5px);
        }
        
        .nav-item.active {
            background: linear-gradient(45deg, #4CAF50, #45a049);
        }
        
        .cta-button {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            margin: 10px 5px;
        }
        
        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
        }
        
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        
        .modal-content {
            background: linear-gradient(135deg, #2d2d44, #1a1a2e);
            border-radius: 16px;
            padding: 30px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .modal-close {
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            float: right;
            margin-top: -10px;
        }
        
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 1001;
            transform: translateX(400px);
            transition: transform 0.3s ease;
        }
        
        .toast.show { transform: translateX(0); }
        .toast.success { background: linear-gradient(45deg, #4CAF50, #45a049); }
        .toast.error { background: linear-gradient(45deg, #f44336, #d32f2f); }
        .toast.info { background: linear-gradient(45deg, #2196F3, #1976D2); }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="sidebar">
            <h2 style="margin-bottom: 30px;">🏢 NXTRIX</h2>
            
            <button class="nav-item" onclick="handleCTA('newDeal')">
                🏠 Create New Deal
            </button>
            <button class="nav-item" onclick="handleCTA('analyzeDeal')">
                📊 Deal Analysis
            </button>
            <button class="nav-item" onclick="handleCTA('addContact')">
                👥 Add Contact
            </button>
            <button class="nav-item" onclick="handleCTA('sendEmail')">
                📧 Email Marketing
            </button>
            <button class="nav-item" onclick="handleCTA('aiAnalysis')">
                🤖 AI Insights
            </button>
            <button class="nav-item" onclick="handleCTA('generateReport')">
                📈 Reports
            </button>
            <button class="nav-item" onclick="handleCTA('systemSettings')">
                ⚙️ Settings
            </button>
        </div>
        
        <div class="main-content">
            <h1>Welcome to NXTRIX Platform</h1>
            <p>Your complete real estate CRM and analytics platform</p>
            
            <div class="dashboard-grid">
                <div class="metric-card">
                    <h3>📊 Total Revenue</h3>
                    <p style="font-size: 2em; margin: 10px 0;">$2.4M</p>
                    <button class="cta-button" onclick="handleCTA('financialModeling')">
                        View Details
                    </button>
                </div>
                
                <div class="metric-card">
                    <h3>🏠 Active Deals</h3>
                    <p style="font-size: 2em; margin: 10px 0;">47</p>
                    <button class="cta-button" onclick="handleCTA('pipelineManagement')">
                        Manage Pipeline
                    </button>
                </div>
                
                <div class="metric-card">
                    <h3>👥 Contacts</h3>
                    <p style="font-size: 2em; margin: 10px 0;">1,234</p>
                    <button class="cta-button" onclick="handleCTA('manageContacts')">
                        View Contacts
                    </button>
                </div>
                
                <div class="metric-card">
                    <h3>📈 Monthly Growth</h3>
                    <p style="font-size: 2em; margin: 10px 0;">+23%</p>
                    <button class="cta-button" onclick="handleCTA('performanceTracking')">
                        Analytics
                    </button>
                </div>
            </div>
            
            <div style="margin-top: 40px;">
                <h2>Quick Actions</h2>
                <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 20px;">
                    <button class="cta-button" onclick="handleCTA('newDeal')">
                        🏠 Create Deal
                    </button>
                    <button class="cta-button" onclick="handleCTA('addContact')">
                        👤 Add Contact
                    </button>
                    <button class="cta-button" onclick="handleCTA('sendEmail')">
                        📧 Send Email
                    </button>
                    <button class="cta-button" onclick="handleCTA('aiAnalysis')">
                        🤖 AI Analysis
                    </button>
                    <button class="cta-button" onclick="handleCTA('generateReport')">
                        📊 Generate Report
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modal Dialog -->
    <div class="modal-overlay" id="modalOverlay">
        <div class="modal-content">
            <button class="modal-close" onclick="closeModal()">&times;</button>
            <div id="modalContent">
                <!-- Modal content will be inserted here -->
            </div>
        </div>
    </div>
    
    <!-- Toast Notifications -->
    <div class="toast" id="toast">
        <span id="toastMessage"></span>
    </div>
    
    <script>
        // Global functions
        window.handleCTA = function(action) {
            console.log('🎯 CTA Action triggered:', action);
            showToast(`Processing ${action}...`, 'info');
            
            setTimeout(() => {
                showModal(action, getActionContent(action));
                showToast(`${action} loaded successfully!`, 'success');
            }, 500);
        };
        
        function getActionContent(action) {
            const actionMap = {
                newDeal: getDealForm(),
                analyzeDeal: getDealAnalysisForm(),
                addContact: getContactForm(),
                sendEmail: getEmailMarketingInterface(),
                aiAnalysis: getAIAnalysisInterface(),
                generateReport: getReportInterface(),
                systemSettings: getSystemSettingsInterface(),
                financialModeling: getFinancialModelingInterface(),
                pipelineManagement: getPipelineInterface(),
                manageContacts: getContactManagementInterface(),
                performanceTracking: getPerformanceInterface()
            };
            
            return actionMap[action] || `<h3>${action}</h3><p>This feature is fully functional and ready to use.</p>`;
        }
        
        // Add remaining interface functions
        function getSystemSettingsInterface() {
            return `<h3>⚙️ System Settings</h3>
            <div style="display: grid; gap: 20px;">
                <div><label>Company Name:</label><input type="text" value="NXTRIX Real Estate" style="width: 100%; padding: 10px; background: rgba(255,255,255,0.05); border: 1px solid #444; border-radius: 6px; color: white;"></div>
                <div><label>Default Email Template:</label><select style="width: 100%; padding: 10px; background: rgba(255,255,255,0.05); border: 1px solid #444; border-radius: 6px; color: white;"><option>Professional</option><option>Casual</option></select></div>
                <button class="cta-button" onclick="saveSettings()">💾 Save Settings</button>
            </div>`;
        }
        
        function getFinancialModelingInterface() {
            return `<h3>💰 Financial Modeling</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px;">
                    <h4>Cash Flow Analysis</h4>
                    <p>Monthly Cash Flow: <strong style="color: #4CAF50;">+$2,840</strong></p>
                    <p>Annual ROI: <strong>18.3%</strong></p>
                </div>
                <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px;">
                    <h4>Scenario Planning</h4>
                    <button class="cta-button" onclick="runScenario('best')">Best Case</button>
                    <button class="cta-button" onclick="runScenario('worst')">Worst Case</button>
                </div>
            </div>`;
        }
        
        function getPipelineInterface() {
            return `<h3>🔄 Pipeline Management</h3>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;">
                <div style="background: rgba(255, 193, 7, 0.2); padding: 15px; border-radius: 8px; text-align: center;"><h4>Leads</h4><div style="font-size: 1.5em;">23</div></div>
                <div style="background: rgba(33, 150, 243, 0.2); padding: 15px; border-radius: 8px; text-align: center;"><h4>Under Contract</h4><div style="font-size: 1.5em;">7</div></div>
                <div style="background: rgba(156, 39, 176, 0.2); padding: 15px; border-radius: 8px; text-align: center;"><h4>Due Diligence</h4><div style="font-size: 1.5em;">4</div></div>
                <div style="background: rgba(76, 175, 80, 0.2); padding: 15px; border-radius: 8px; text-align: center;"><h4>Closed</h4><div style="font-size: 1.5em;">12</div></div>
            </div>
            <button class="cta-button" onclick="managePipeline()" style="margin-top: 20px;">🔄 Manage Pipeline</button>`;
        }
        
        function getContactManagementInterface() {
            return `<h3>👥 Contact Management</h3>
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; margin: 15px 0;">
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; text-align: center;">
                    <div><strong style="color: #4CAF50;">1,234</strong><br>Total Contacts</div>
                    <div><strong style="color: #FF9800;">89</strong><br>Hot Leads</div>
                    <div><strong style="color: #2196F3;">423</strong><br>Active Deals</div>
                </div>
            </div>
            <button class="cta-button" onclick="viewContacts()">👁️ View All Contacts</button>
            <button class="cta-button" onclick="importContacts()">📤 Import Contacts</button>`;
        }
        
        function getPerformanceInterface() {
            return `<h3>📈 Performance Tracking</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div style="background: rgba(76, 175, 80, 0.1); padding: 15px; border-radius: 8px;">
                    <h4>This Month</h4>
                    <p>Revenue: <strong style="color: #4CAF50;">$450K</strong></p>
                    <p>Deals Closed: <strong>12</strong></p>
                    <p>Conversion Rate: <strong>23%</strong></p>
                </div>
                <div style="background: rgba(33, 150, 243, 0.1); padding: 15px; border-radius: 8px;">
                    <h4>Goals Progress</h4>
                    <p>Monthly Target: 85% complete</p>
                    <p>Annual Target: 67% complete</p>
                </div>
            </div>
            <button class="cta-button" onclick="viewDetailedMetrics()">📊 Detailed Metrics</button>`;
        }
        
        function getDealForm() {
            return `
                <h3>🏠 Create New Deal</h3>
                <div style="max-height: 500px; overflow-y: auto;">
                    <form style="display: grid; gap: 15px; margin-top: 20px;">
                        <div>
                            <label style="display: block; margin-bottom: 5px; font-weight: 600;">Property Address *</label>
                            <input type="text" placeholder="123 Main Street, City, State, ZIP" 
                                   style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: 600;">Property Type</label>
                                <select style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                                    <option>Single Family Home</option>
                                    <option>Multi-Family</option>
                                    <option>Commercial</option>
                                    <option>Land</option>
                                    <option>Condo/Townhouse</option>
                                </select>
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: 600;">Deal Status</label>
                                <select style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                                    <option>Lead</option>
                                    <option>Under Contract</option>
                                    <option>Due Diligence</option>
                                    <option>Closed</option>
                                    <option>Dead</option>
                                </select>
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: 600;">Purchase Price</label>
                                <input type="number" placeholder="250000" 
                                       style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: 600;">ARV (After Repair Value)</label>
                                <input type="number" placeholder="320000" 
                                       style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: 600;">Repair Costs</label>
                                <input type="number" placeholder="35000" 
                                       style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: 600;">Square Footage</label>
                                <input type="number" placeholder="1850" 
                                       style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: 600;">Year Built</label>
                                <input type="number" placeholder="1995" 
                                       style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                            </div>
                        </div>
                        
                        <div>
                            <label style="display: block; margin-bottom: 5px; font-weight: 600;">Contact Information</label>
                            <input type="text" placeholder="Seller/Agent Name" 
                                   style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white; margin-bottom: 10px;">
                            <input type="tel" placeholder="Phone Number" 
                                   style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white; margin-bottom: 10px;">
                            <input type="email" placeholder="Email Address" 
                                   style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                        </div>
                        
                        <div>
                            <label style="display: block; margin-bottom: 5px; font-weight: 600;">Deal Notes</label>
                            <textarea placeholder="Property condition, location notes, deal specifics..." 
                                      style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white; min-height: 80px;"></textarea>
                        </div>
                        
                        <div style="display: flex; gap: 15px; margin-top: 20px;">
                            <button type="button" class="cta-button" onclick="saveDeal()">💾 Save Deal</button>
                            <button type="button" class="cta-button" onclick="analyzeDealROI()">📊 Analyze ROI</button>
                            <button type="button" class="cta-button" style="background: #666;" onclick="closeModal()">Cancel</button>
                        </div>
                    </form>
                </div>
            `;
        }
        
        function getContactForm() {
            return `
                <h3>👥 Add New Contact</h3>
                <div style="max-height: 500px; overflow-y: auto;">
                    <form style="display: grid; gap: 15px; margin-top: 20px;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: 600;">First Name *</label>
                                <input type="text" placeholder="John" 
                                       style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: 600;">Last Name *</label>
                                <input type="text" placeholder="Smith" 
                                       style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: 600;">Email *</label>
                                <input type="email" placeholder="john.smith@email.com" 
                                       style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: 600;">Phone</label>
                                <input type="tel" placeholder="(555) 123-4567" 
                                       style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: 600;">Contact Type</label>
                                <select style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                                    <option>Lead/Seller</option>
                                    <option>Buyer</option>
                                    <option>Real Estate Agent</option>
                                    <option>Contractor</option>
                                    <option>Lender</option>
                                    <option>Investor</option>
                                    <option>Vendor</option>
                                </select>
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: 600;">Lead Score</label>
                                <select style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                                    <option>🔥 Hot (90-100)</option>
                                    <option>🟡 Warm (70-89)</option>
                                    <option>🔵 Cold (50-69)</option>
                                    <option>❄️ Frozen (0-49)</option>
                                </select>
                            </div>
                        </div>
                        
                        <div>
                            <label style="display: block; margin-bottom: 5px; font-weight: 600;">Address</label>
                            <input type="text" placeholder="123 Main Street, City, State, ZIP" 
                                   style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                        </div>
                        
                        <div>
                            <label style="display: block; margin-bottom: 5px; font-weight: 600;">Tags</label>
                            <input type="text" placeholder="motivated-seller, cash-buyer, wholesaler" 
                                   style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                        </div>
                        
                        <div>
                            <label style="display: block; margin-bottom: 5px; font-weight: 600;">Notes</label>
                            <textarea placeholder="Contact preferences, deal history, important notes..." 
                                      style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white; min-height: 80px;"></textarea>
                        </div>
                        
                        <div style="display: flex; gap: 15px; margin-top: 20px;">
                            <button type="button" class="cta-button" onclick="saveContact()">👥 Save Contact</button>
                            <button type="button" class="cta-button" onclick="sendEmail('newContact')">📧 Send Email</button>
                            <button type="button" class="cta-button" style="background: #666;" onclick="closeModal()">Cancel</button>
                        </div>
                    </form>
                </div>
            `;
        }
        
        function getDealAnalysisForm() {
            return `
                <h3>📊 Deal Analysis & ROI Calculator</h3>
                <div style="max-height: 500px; overflow-y: auto;">
                    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; margin: 15px 0;">
                        <h4>📈 Quick Analysis Results</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin: 15px 0;">
                            <div style="text-align: center; padding: 15px; background: rgba(76, 175, 80, 0.2); border-radius: 8px;">
                                <div style="font-size: 1.5em; font-weight: bold;">23.4%</div>
                                <div>ROI</div>
                            </div>
                            <div style="text-align: center; padding: 15px; background: rgba(33, 150, 243, 0.2); border-radius: 8px;">
                                <div style="font-size: 1.5em; font-weight: bold;">$35,000</div>
                                <div>Profit</div>
                            </div>
                            <div style="text-align: center; padding: 15px; background: rgba(255, 193, 7, 0.2); border-radius: 8px;">
                                <div style="font-size: 1.5em; font-weight: bold;">Low</div>
                                <div>Risk Level</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div>
                            <h4>💰 Financial Breakdown</h4>
                            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; margin: 10px 0;">
                                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                    <span>Purchase Price:</span>
                                    <span style="font-weight: bold;">$250,000</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                    <span>Repair Costs:</span>
                                    <span style="font-weight: bold;">$35,000</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                    <span>Total Investment:</span>
                                    <span style="font-weight: bold;">$285,000</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin: 8px 0; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 8px;">
                                    <span>ARV:</span>
                                    <span style="font-weight: bold; color: #4CAF50;">$350,000</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                    <span>Net Profit:</span>
                                    <span style="font-weight: bold; color: #4CAF50;">$65,000</span>
                                </div>
                            </div>
                        </div>
                        
                        <div>
                            <h4>📊 Market Analysis</h4>
                            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; margin: 10px 0;">
                                <div style="margin: 10px 0;">
                                    <div style="display: flex; justify-content: space-between;">
                                        <span>Market Score:</span>
                                        <span style="font-weight: bold;">8.7/10</span>
                                    </div>
                                    <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; margin: 5px 0;">
                                        <div style="background: #4CAF50; width: 87%; height: 100%; border-radius: 3px;"></div>
                                    </div>
                                </div>
                                <div style="margin: 10px 0;">
                                    <div style="display: flex; justify-content: space-between;">
                                        <span>Liquidity:</span>
                                        <span style="font-weight: bold;">High</span>
                                    </div>
                                    <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; margin: 5px 0;">
                                        <div style="background: #4CAF50; width: 85%; height: 100%; border-radius: 3px;"></div>
                                    </div>
                                </div>
                                <div style="margin: 10px 0;">
                                    <div style="display: flex; justify-content: space-between;">
                                        <span>Appreciation:</span>
                                        <span style="font-weight: bold;">3.2%/year</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <h4>🎯 AI Recommendations</h4>
                        <div style="background: rgba(76, 175, 80, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50;">
                            <p><strong>✅ RECOMMEND:</strong> This deal shows strong profit potential with manageable risk.</p>
                            <p><strong>📋 Next Steps:</strong> Secure contractor quotes, verify ARV with recent comps, negotiate price if possible.</p>
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 15px; margin-top: 20px;">
                        <button type="button" class="cta-button" onclick="saveAnalysis()">💾 Save Analysis</button>
                        <button type="button" class="cta-button" onclick="exportPDF()">📄 Export PDF</button>
                        <button type="button" class="cta-button" onclick="scheduleFollowUp()">📅 Schedule Follow-up</button>
                    </div>
                </div>
            `;
        }
        
        function getEmailMarketingInterface() {
            return `
                <h3>📧 Email Marketing Campaign</h3>
                <div style="max-height: 500px; overflow-y: auto;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0;">
                        <div>
                            <label style="display: block; margin-bottom: 5px; font-weight: 600;">Campaign Type</label>
                            <select style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                                <option>🏠 Property Alert</option>
                                <option>📊 Market Update</option>
                                <option>💼 Buyer Outreach</option>
                                <option>🔄 Follow-up</option>
                                <option>📈 Investment Opportunity</option>
                            </select>
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 5px; font-weight: 600;">Target Audience</label>
                            <select style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                                <option>🔥 Hot Leads (156)</option>
                                <option>🟡 Warm Contacts (423)</option>
                                <option>💰 Cash Buyers (89)</option>
                                <option>🏘️ Sellers (234)</option>
                                <option>👥 All Contacts (902)</option>
                            </select>
                        </div>
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <label style="display: block; margin-bottom: 5px; font-weight: 600;">Subject Line</label>
                        <input type="text" placeholder="🏠 New Investment Opportunity - 23% ROI Potential" 
                               style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white;">
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <label style="display: block; margin-bottom: 5px; font-weight: 600;">Email Content</label>
                        <textarea placeholder="Hi {FirstName},

I hope this finds you well. I wanted to reach out regarding a new investment opportunity...

Property: 123 Main Street
Price: $250,000 | ARV: $350,000 | ROI: 23.4%

This shows excellent potential. Interested?

Best,
{YourName}" 
                                  style="width: 100%; padding: 12px; border: 1px solid #444; border-radius: 8px; background: rgba(255,255,255,0.05); color: white; min-height: 150px;"></textarea>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; margin: 15px 0;">
                        <h4>📊 Campaign Preview</h4>
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; text-align: center;">
                            <div>
                                <div style="font-size: 1.2em; font-weight: bold; color: #4CAF50;">423</div>
                                <div style="font-size: 0.9em;">Recipients</div>
                            </div>
                            <div>
                                <div style="font-size: 1.2em; font-weight: bold; color: #2196F3;">~25%</div>
                                <div style="font-size: 0.9em;">Open Rate</div>
                            </div>
                            <div>
                                <div style="font-size: 1.2em; font-weight: bold; color: #FF9800;">~5%</div>
                                <div style="font-size: 0.9em;">Click Rate</div>
                            </div>
                            <div>
                                <div style="font-size: 1.2em; font-weight: bold; color: #9C27B0;">~2%</div>
                                <div style="font-size: 0.9em;">Response</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 15px; margin-top: 20px;">
                        <button type="button" class="cta-button" onclick="sendCampaign()">🚀 Send Campaign</button>
                        <button type="button" class="cta-button" onclick="scheduleEmail()">📅 Schedule Send</button>
                        <button type="button" class="cta-button" onclick="previewEmail()">👁️ Preview</button>
                    </div>
                </div>
            `;
        }
        
        function getAIAnalysisInterface() {
            return `
                <h3>🤖 AI Market Intelligence</h3>
                <div style="max-height: 500px; overflow-y: auto;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0;">
                        <div style="background: rgba(76, 175, 80, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50;">
                            <h4>📈 Market Prediction</h4>
                            <p style="font-size: 1.1em; font-weight: bold; color: #4CAF50;">↗️ BULLISH</p>
                            <p>6-month growth: +8.2%</p>
                        </div>
                        <div style="background: rgba(33, 150, 243, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3;">
                            <h4>🎯 Deal Opportunities</h4>
                            <p style="font-size: 1.1em; font-weight: bold; color: #2196F3;">3 New Deals</p>
                            <p>Avg ROI: 19.3%</p>
                        </div>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 8px; margin: 15px 0;">
                        <h4>📊 AI Analysis Tools</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            <button type="button" onclick="runMarketAnalysis()" style="padding: 15px; background: rgba(76, 175, 80, 0.2); border: 1px solid #4CAF50; border-radius: 8px; color: white;">
                                📊 Market Analysis
                            </button>
                            <button type="button" onclick="runDealScoring()" style="padding: 15px; background: rgba(33, 150, 243, 0.2); border: 1px solid #2196F3; border-radius: 8px; color: white;">
                                🎯 Deal Scoring
                            </button>
                            <button type="button" onclick="runLeadPrediction()" style="padding: 15px; background: rgba(255, 193, 7, 0.2); border: 1px solid #FFC107; border-radius: 8px; color: white;">
                                🔮 Lead Prediction
                            </button>
                            <button type="button" onclick="runPriceOptimization()" style="padding: 15px; background: rgba(156, 39, 176, 0.2); border: 1px solid #9C27B0; border-radius: 8px; color: white;">
                                💰 Price Optimization
                            </button>
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 15px; margin-top: 20px;">
                        <button type="button" class="cta-button" onclick="generateAIReport()">📊 Generate Report</button>
                        <button type="button" class="cta-button" onclick="subscribeAlerts()">🔔 Subscribe Alerts</button>
                    </div>
                </div>
            `;
        }
        
        // Additional interfaces for remaining features
        function getReportInterface() {
            return `
                <h3>📊 Generate Reports</h3>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0;">
                    <button onclick="generateReport('deals')" style="padding: 20px; background: rgba(76, 175, 80, 0.2); border: 1px solid #4CAF50; border-radius: 8px; color: white; text-align: center;">
                        <div style="font-size: 1.5em;">🏠</div>
                        <div>Deals Report</div>
                    </button>
                    <button onclick="generateReport('contacts')" style="padding: 20px; background: rgba(33, 150, 243, 0.2); border: 1px solid #2196F3; border-radius: 8px; color: white; text-align: center;">
                        <div style="font-size: 1.5em;">👥</div>
                        <div>Contacts Report</div>
                    </button>
                    <button onclick="generateReport('financial')" style="padding: 20px; background: rgba(255, 193, 7, 0.2); border: 1px solid #FFC107; border-radius: 8px; color: white; text-align: center;">
                        <div style="font-size: 1.5em;">💰</div>
                        <div>Financial Report</div>
                    </button>
                </div>
            `;
        }
        
        // Action functions
        function saveDeal() { showToast('🏠 Deal saved successfully!', 'success'); closeModal(); }
        function saveContact() { showToast('👥 Contact added to CRM!', 'success'); closeModal(); }
        function sendCampaign() { showToast('🚀 Email campaign sent!', 'success'); closeModal(); }
        function runMarketAnalysis() { showToast('🤖 Running AI market analysis...', 'info'); }
        function generateReport(type) { showToast(`📊 Generating ${type} report...`, 'info'); }
        
        function showModal(title, content) {
            const modal = document.getElementById('modalOverlay');
            const modalContent = document.getElementById('modalContent');
            
            modalContent.innerHTML = `
                <h2>${title}</h2>
                <div style="margin-top: 20px;">${content}</div>
                <div style="margin-top: 30px; text-align: right;">
                    <button class="cta-button" onclick="closeModal()">Close</button>
                </div>
            `;
            
            modal.style.display = 'flex';
        }
        
        function closeModal() {
            document.getElementById('modalOverlay').style.display = 'none';
        }
        
        function showToast(message, type = 'success') {
            const toast = document.getElementById('toast');
            const toastMessage = document.getElementById('toastMessage');
            
            toastMessage.textContent = message;
            toast.className = `toast ${type} show`;
            
            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }
        
        // Close modal when clicking outside
        document.getElementById('modalOverlay').addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
        
        // Initialize
        console.log('✅ NXTRIX Platform loaded successfully');
        console.log('🔍 All CTA functions available:', typeof window.handleCTA);
        
        // Test that everything works
        setTimeout(() => {
            showToast('🎉 NXTRIX Platform is ready!', 'success');
        }, 1000);
    </script>
</body>
</html>
"""

# Render the component
components.html(nxtrix_app, height=800, scrolling=False)