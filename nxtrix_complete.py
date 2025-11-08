import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
from nxtrix_backend import NXTRIXDatabase

# Initialize database
@st.cache_resource
def get_database():
    db = NXTRIXDatabase()
    # Add sample data if empty
    if len(db.get_all_contacts()) == 0:
        db.add_sample_data()
    return db

db = get_database()

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

    # Get real data from database
    contacts = db.get_all_contacts()
    deals = db.get_all_deals()
    campaigns = db.get_all_campaigns()
    metrics = db.get_dashboard_metrics()

    # Prepare data for JavaScript
    contacts_json = json.dumps(contacts)
    deals_json = json.dumps(deals)
    campaigns_json = json.dumps(campaigns)
    metrics_json = json.dumps(metrics)

    # Handle form submissions
    if st.session_state.get('contact_to_add'):
        contact_data = st.session_state.contact_to_add
        try:
            db.add_contact(contact_data)
            st.success(f"Contact {contact_data['name']} added successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error adding contact: {str(e)}")
        finally:
            del st.session_state.contact_to_add

    if st.session_state.get('deal_to_add'):
        deal_data = st.session_state.deal_to_add
        try:
            db.add_deal(deal_data)
            st.success(f"Deal for {deal_data['property_address']} created successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error creating deal: {str(e)}")
        finally:
            del st.session_state.deal_to_add

    if st.session_state.get('campaign_to_add'):
        campaign_data = st.session_state.campaign_to_add
        try:
            campaign_id = db.create_campaign(campaign_data)
            if campaign_data.get('launch_now'):
                db.launch_campaign(campaign_id)
                st.success(f"Campaign '{campaign_data['name']}' launched successfully!")
            else:
                st.success(f"Campaign '{campaign_data['name']}' created successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error with campaign: {str(e)}")
        finally:
            del st.session_state.campaign_to_add

    # NXTRIX HTML with functional backend integration
    nxtrix_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NXTRIX - Advanced Real Estate Platform</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            :root {{
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
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: var(--background);
                color: var(--text);
                height: 100vh;
                overflow: hidden;
                position: relative;
            }}
            
            body::before {{
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    radial-gradient(circle at 20% 80%, rgba(124, 92, 255, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(36, 209, 255, 0.1) 0%, transparent 50%);
                z-index: -1;
            }}

            .app-container {{
                display: flex;
                height: 100vh;
                position: relative;
                z-index: 1;
            }}

            .sidebar {{
                width: 300px;
                background: var(--surface);
                backdrop-filter: blur(20px);
                border-right: 1px solid var(--border);
                padding: 24px;
                overflow-y: auto;
            }}

            .sidebar-header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid var(--border);
            }}

            .logo {{
                font-size: 2.2em;
                font-weight: 700;
                background: linear-gradient(135deg, var(--primary), var(--primary-light));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 8px;
            }}

            .tagline {{
                font-size: 0.9em;
                color: var(--text-muted);
            }}

            .nav-section {{
                margin-bottom: 25px;
            }}

            .section-title {{
                font-size: 0.85em;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 12px;
                font-weight: 600;
            }}

            .cta-button {{
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
            }}

            .cta-button:hover {{
                background: var(--primary);
                transform: translateX(5px);
                box-shadow: 0 4px 20px rgba(124, 92, 255, 0.3);
                border-color: var(--primary-light);
            }}

            .main-content {{
                flex: 1;
                padding: 24px;
                overflow-y: auto;
                background: rgba(255, 255, 255, 0.02);
            }}

            .content-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid var(--border);
            }}

            .page-title {{
                font-size: 2.4em;
                font-weight: 700;
                background: linear-gradient(135deg, var(--text), var(--secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}

            .breadcrumb {{
                color: var(--text-muted);
                font-size: 0.9em;
            }}

            .dashboard-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}

            .metric-card {{
                background: var(--surface);
                backdrop-filter: blur(20px);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                transition: all 0.3s ease;
                cursor: pointer;
            }}

            .metric-card:hover {{
                transform: translateY(-8px);
                box-shadow: 0 15px 35px rgba(124, 92, 255, 0.2);
                border-color: var(--primary);
            }}

            .metric-icon {{
                font-size: 2.5em;
                margin-bottom: 15px;
                opacity: 0.8;
            }}

            .metric-value {{
                font-size: 2.8em;
                font-weight: 700;
                color: var(--primary);
                margin: 10px 0;
            }}

            .metric-label {{
                font-size: 1.1em;
                color: var(--text);
                font-weight: 600;
            }}

            .metric-change {{
                font-size: 0.9em;
                margin-top: 8px;
                padding: 4px 8px;
                border-radius: 12px;
                background: var(--success);
                color: white;
            }}

            .action-button {{
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
            }}

            .action-button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(124, 92, 255, 0.4);
            }}

            .secondary-button {{
                background: var(--surface-light);
                color: var(--text);
                border: 1px solid var(--border);
                padding: 10px 20px;
                border-radius: 10px;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 5px;
            }}

            .secondary-button:hover {{
                background: var(--surface);
                border-color: var(--primary);
            }}

            .form-group {{
                margin-bottom: 20px;
            }}

            .form-label {{
                display: block;
                font-size: 14px;
                font-weight: 600;
                color: var(--text);
                margin-bottom: 5px;
            }}

            .form-input {{
                width: 100%;
                padding: 12px 16px;
                background: var(--surface-light);
                border: 1px solid var(--border);
                border-radius: 8px;
                color: var(--text);
                font-size: 14px;
            }}

            .form-input:focus {{
                outline: none;
                border-color: var(--primary);
                box-shadow: 0 0 10px rgba(124, 92, 255, 0.2);
            }}

            .data-table {{
                width: 100%;
                background: var(--surface);
                border-radius: 12px;
                overflow: hidden;
                margin: 20px 0;
            }}

            .data-table th, .data-table td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid var(--border);
            }}

            .data-table th {{
                background: var(--surface-light);
                font-weight: 600;
                color: var(--primary);
            }}

            .data-table tr:hover {{
                background: var(--surface-light);
            }}

            .badge {{
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
            }}

            .badge.active {{
                background: var(--success);
                color: white;
            }}

            .badge.investor {{
                background: var(--primary);
                color: white;
            }}

            .toast {{
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
            }}

            .toast.show {{
                transform: translateX(0);
            }}

            @media (max-width: 768px) {{
                .app-container {{
                    flex-direction: column;
                }}
                .sidebar {{
                    width: 100%;
                    height: auto;
                }}
                .dashboard-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="app-container">
            <div class="sidebar">
                <div class="sidebar-header">
                    <div class="logo">NXTRIX</div>
                    <div class="tagline">Advanced Real Estate Platform</div>
                </div>
                
                <nav>
                    <div class="nav-section">
                        <div class="section-title">Core Features</div>
                        <button class="cta-button" onclick="showDashboard()">
                            <span>🏡</span>
                            <span>Dashboard</span>
                        </button>
                        <button class="cta-button" onclick="showNewDealForm()">
                            <span>🏠</span>
                            <span>Create New Deal</span>
                        </button>
                        <button class="cta-button" onclick="showDealsView()">
                            <span>📊</span>
                            <span>View All Deals</span>
                        </button>
                        <button class="cta-button" onclick="showContactForm()">
                            <span>👥</span>
                            <span>Add Contact</span>
                        </button>
                        <button class="cta-button" onclick="showContactsView()">
                            <span>📋</span>
                            <span>View All Contacts</span>
                        </button>
                    </div>
                    
                    <div class="nav-section">
                        <div class="section-title">Marketing</div>
                        <button class="cta-button" onclick="showEmailMarketing()">
                            <span>📧</span>
                            <span>Email Campaigns</span>
                        </button>
                        <button class="cta-button" onclick="showCampaignsView()">
                            <span>📈</span>
                            <span>Campaign Results</span>
                        </button>
                    </div>
                </nav>
            </div>
            
            <div class="main-content" id="mainContent">
                <!-- Content will be loaded here -->
            </div>
        </div>
        
        <div class="toast" id="toast">
            <span id="toastMessage">Welcome to NXTRIX!</span>
        </div>
        
        <script>
            // Real data from backend
            const contacts = {contacts_json};
            const deals = {deals_json};
            const campaigns = {campaigns_json};
            const metrics = {metrics_json};
            
            console.log('NXTRIX Platform Loading with real data...');
            console.log('Contacts:', contacts.length);
            console.log('Deals:', deals.length);
            console.log('Metrics:', metrics);
            
            function showToast(message) {{
                const toast = document.getElementById('toast');
                const toastMessage = document.getElementById('toastMessage');
                
                if (toast && toastMessage) {{
                    toastMessage.textContent = message;
                    toast.classList.add('show');
                    
                    setTimeout(() => {{
                        toast.classList.remove('show');
                    }}, 3000);
                }}
            }}
            
            function formatCurrency(amount) {{
                return new Intl.NumberFormat('en-US', {{
                    style: 'currency',
                    currency: 'USD'
                }}).format(amount || 0);
            }}
            
            function formatDate(dateString) {{
                return new Date(dateString).toLocaleDateString();
            }}
            
            function showDashboard() {{
                const mainContent = document.getElementById('mainContent');
                mainContent.innerHTML = `
                    <div class="content-header">
                        <div>
                            <div class="page-title">Dashboard</div>
                            <div class="breadcrumb">Home > Dashboard</div>
                        </div>
                        <div>
                            <button class="action-button" onclick="showNewDealForm()">+ Add Deal</button>
                            <button class="action-button" onclick="showContactForm()">+ Add Contact</button>
                        </div>
                    </div>
                    
                    <div class="dashboard-grid">
                        <div class="metric-card">
                            <div class="metric-icon">💰</div>
                            <div class="metric-value">${{formatCurrency(metrics.total_value)}}</div>
                            <div class="metric-label">Total Deal Value</div>
                            <div class="metric-change">Real-time data</div>
                        </div>
                        
                        <div class="metric-card">
                            <div class="metric-icon">🏠</div>
                            <div class="metric-value">${{metrics.active_deals}}</div>
                            <div class="metric-label">Active Deals</div>
                            <div class="metric-change">+${{metrics.new_deals}} this month</div>
                        </div>
                        
                        <div class="metric-card">
                            <div class="metric-icon">👥</div>
                            <div class="metric-value">${{metrics.total_contacts}}</div>
                            <div class="metric-label">Total Contacts</div>
                            <div class="metric-change">+${{metrics.new_contacts}} this month</div>
                        </div>
                        
                        <div class="metric-card">
                            <div class="metric-icon">🎯</div>
                            <div class="metric-value">${{metrics.avg_roi}}%</div>
                            <div class="metric-label">Average ROI</div>
                            <div class="metric-change">Portfolio average</div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px;">
                        <div class="data-table" style="max-height: 300px; overflow-y: auto;">
                            <table style="width: 100%;">
                                <thead>
                                    <tr>
                                        <th colspan="3" style="text-align: center; padding: 15px;">Recent Deals</th>
                                    </tr>
                                    <tr>
                                        <th>Property</th>
                                        <th>Type</th>
                                        <th>ROI</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{deals.slice(0, 5).map(deal => `
                                        <tr>
                                            <td>${{deal.property_address}}</td>
                                            <td><span class="badge active">${{deal.deal_type}}</span></td>
                                            <td>${{deal.expected_roi}}%</td>
                                        </tr>
                                    `).join('')}}
                                </tbody>
                            </table>
                        </div>
                        
                        <div class="data-table" style="max-height: 300px; overflow-y: auto;">
                            <table style="width: 100%;">
                                <thead>
                                    <tr>
                                        <th colspan="3" style="text-align: center; padding: 15px;">Recent Contacts</th>
                                    </tr>
                                    <tr>
                                        <th>Name</th>
                                        <th>Type</th>
                                        <th>Score</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{contacts.slice(0, 5).map(contact => `
                                        <tr>
                                            <td>${{contact.name}}</td>
                                            <td><span class="badge investor">${{contact.contact_type}}</span></td>
                                            <td>${{contact.lead_score}}</td>
                                        </tr>
                                    `).join('')}}
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
                showToast('Dashboard loaded with real data');
            }}
            
            function showContactsView() {{
                const mainContent = document.getElementById('mainContent');
                mainContent.innerHTML = `
                    <div class="content-header">
                        <div>
                            <div class="page-title">All Contacts (${{contacts.length}})</div>
                            <div class="breadcrumb">Home > Contacts > View All</div>
                        </div>
                        <div>
                            <button class="action-button" onclick="showContactForm()">+ Add New Contact</button>
                            <button class="secondary-button" onclick="showDashboard()">← Back to Dashboard</button>
                        </div>
                    </div>
                    
                    <div class="data-table">
                        <table style="width: 100%;">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Phone</th>
                                    <th>Type</th>
                                    <th>Company</th>
                                    <th>Lead Score</th>
                                    <th>Added</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{contacts.map(contact => `
                                    <tr>
                                        <td style="font-weight: 600;">${{contact.name}}</td>
                                        <td>${{contact.email}}</td>
                                        <td>${{contact.phone || 'N/A'}}</td>
                                        <td><span class="badge investor">${{contact.contact_type}}</span></td>
                                        <td>${{contact.company || 'N/A'}}</td>
                                        <td><strong>${{contact.lead_score}}</strong></td>
                                        <td>${{formatDate(contact.created_at)}}</td>
                                    </tr>
                                `).join('')}}
                            </tbody>
                        </table>
                    </div>
                `;
                showToast(`Loaded ${{contacts.length}} contacts from database`);
            }}
            
            function showDealsView() {{
                const mainContent = document.getElementById('mainContent');
                mainContent.innerHTML = `
                    <div class="content-header">
                        <div>
                            <div class="page-title">All Deals (${{deals.length}})</div>
                            <div class="breadcrumb">Home > Deals > View All</div>
                        </div>
                        <div>
                            <button class="action-button" onclick="showNewDealForm()">+ Add New Deal</button>
                            <button class="secondary-button" onclick="showDashboard()">← Back to Dashboard</button>
                        </div>
                    </div>
                    
                    <div class="data-table">
                        <table style="width: 100%;">
                            <thead>
                                <tr>
                                    <th>Property Address</th>
                                    <th>Purchase Price</th>
                                    <th>Deal Type</th>
                                    <th>Expected ROI</th>
                                    <th>Status</th>
                                    <th>Contact</th>
                                    <th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{deals.map(deal => `
                                    <tr>
                                        <td style="font-weight: 600;">${{deal.property_address}}</td>
                                        <td>${{formatCurrency(deal.purchase_price)}}</td>
                                        <td><span class="badge active">${{deal.deal_type}}</span></td>
                                        <td><strong>${{deal.expected_roi}}%</strong></td>
                                        <td><span class="badge active">${{deal.status}}</span></td>
                                        <td>${{deal.contact_name || 'No Contact'}}</td>
                                        <td>${{formatDate(deal.created_at)}}</td>
                                    </tr>
                                `).join('')}}
                            </tbody>
                        </table>
                    </div>
                `;
                showToast(`Loaded ${{deals.length}} deals from database`);
            }}
            
            function showCampaignsView() {{
                const mainContent = document.getElementById('mainContent');
                mainContent.innerHTML = `
                    <div class="content-header">
                        <div>
                            <div class="page-title">Email Campaigns (${{campaigns.length}})</div>
                            <div class="breadcrumb">Home > Marketing > Campaigns</div>
                        </div>
                        <div>
                            <button class="action-button" onclick="showEmailMarketing()">+ New Campaign</button>
                            <button class="secondary-button" onclick="showDashboard()">← Back to Dashboard</button>
                        </div>
                    </div>
                    
                    <div class="data-table">
                        <table style="width: 100%;">
                            <thead>
                                <tr>
                                    <th>Campaign Name</th>
                                    <th>Subject</th>
                                    <th>Target Audience</th>
                                    <th>Status</th>
                                    <th>Sent Count</th>
                                    <th>Open Rate</th>
                                    <th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{campaigns.map(campaign => `
                                    <tr>
                                        <td style="font-weight: 600;">${{campaign.name}}</td>
                                        <td>${{campaign.subject}}</td>
                                        <td>${{campaign.target_audience}}</td>
                                        <td><span class="badge ${{campaign.status === 'sent' ? 'active' : 'investor'}}">${{campaign.status}}</span></td>
                                        <td>${{campaign.sent_count}}</td>
                                        <td>${{campaign.open_rate}}%</td>
                                        <td>${{formatDate(campaign.created_at)}}</td>
                                    </tr>
                                `).join('')}}
                            </tbody>
                        </table>
                    </div>
                `;
                showToast(`Loaded ${{campaigns.length}} campaigns from database`);
            }}
            
            function showContactForm() {{
                const mainContent = document.getElementById('mainContent');
                mainContent.innerHTML = `
                    <div class="content-header">
                        <div>
                            <div class="page-title">Add New Contact</div>
                            <div class="breadcrumb">Home > Contacts > Add New</div>
                        </div>
                        <div>
                            <button class="secondary-button" onclick="showContactsView()">← View All Contacts</button>
                        </div>
                    </div>
                    
                    <div style="max-width: 600px; margin: 0 auto;">
                        <form id="contactForm" onsubmit="submitContact(event)">
                            <div class="form-group">
                                <label class="form-label">Full Name *</label>
                                <input type="text" class="form-input" name="name" required placeholder="John Smith">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Email Address *</label>
                                <input type="email" class="form-input" name="email" required placeholder="john@example.com">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Phone Number</label>
                                <input type="tel" class="form-input" name="phone" placeholder="(555) 123-4567">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Contact Type</label>
                                <select class="form-input" name="contact_type">
                                    <option>Investor</option>
                                    <option>Seller</option>
                                    <option>Buyer</option>
                                    <option>Agent</option>
                                    <option>Contractor</option>
                                    <option>Lead</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Company</label>
                                <input type="text" class="form-input" name="company" placeholder="Company Name">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Lead Score (0-100)</label>
                                <input type="number" class="form-input" name="lead_score" min="0" max="100" value="50">
                            </div>
                            <div style="text-align: center; margin-top: 30px;">
                                <button type="submit" class="action-button">Add Contact</button>
                                <button type="button" class="secondary-button" onclick="showContactsView()">Cancel</button>
                            </div>
                        </form>
                    </div>
                `;
                showToast('Contact form ready');
            }}
            
            function showNewDealForm() {{
                const contactOptions = contacts.map(contact => 
                    `<option value="${{contact.id}}">${{contact.name}} (${{contact.email}})</option>`
                ).join('');
                
                const mainContent = document.getElementById('mainContent');
                mainContent.innerHTML = `
                    <div class="content-header">
                        <div>
                            <div class="page-title">Create New Deal</div>
                            <div class="breadcrumb">Home > Deals > Create New</div>
                        </div>
                        <div>
                            <button class="secondary-button" onclick="showDealsView()">← View All Deals</button>
                        </div>
                    </div>
                    
                    <div style="max-width: 600px; margin: 0 auto;">
                        <form id="dealForm" onsubmit="submitDeal(event)">
                            <div class="form-group">
                                <label class="form-label">Property Address *</label>
                                <input type="text" class="form-input" name="property_address" required placeholder="123 Main Street, City, State">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Purchase Price *</label>
                                <input type="number" class="form-input" name="purchase_price" required placeholder="350000">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Deal Type</label>
                                <select class="form-input" name="deal_type">
                                    <option>Fix & Flip</option>
                                    <option>Buy & Hold</option>
                                    <option>Wholesale</option>
                                    <option>Commercial</option>
                                    <option>BRRR</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Expected ROI (%)</label>
                                <input type="number" step="0.1" class="form-input" name="expected_roi" placeholder="25.5">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Associated Contact</label>
                                <select class="form-input" name="contact_id">
                                    <option value="">Select Contact (Optional)</option>
                                    ${{contactOptions}}
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">ARV (After Repair Value)</label>
                                <input type="number" class="form-input" name="arv" placeholder="450000">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Estimated Repair Costs</label>
                                <input type="number" class="form-input" name="repair_costs" placeholder="50000">
                            </div>
                            <div style="text-align: center; margin-top: 30px;">
                                <button type="submit" class="action-button">Create Deal</button>
                                <button type="button" class="secondary-button" onclick="showDealsView()">Cancel</button>
                            </div>
                        </form>
                    </div>
                `;
                showToast('Deal creation form ready');
            }}
            
            function showEmailMarketing() {{
                const mainContent = document.getElementById('mainContent');
                mainContent.innerHTML = `
                    <div class="content-header">
                        <div>
                            <div class="page-title">Email Marketing Campaign</div>
                            <div class="breadcrumb">Home > Marketing > New Campaign</div>
                        </div>
                        <div>
                            <button class="secondary-button" onclick="showCampaignsView()">← View All Campaigns</button>
                        </div>
                    </div>
                    
                    <div style="max-width: 600px; margin: 0 auto;">
                        <form id="campaignForm" onsubmit="submitCampaign(event)">
                            <div class="form-group">
                                <label class="form-label">Campaign Name *</label>
                                <input type="text" class="form-input" name="name" required placeholder="Q4 Investment Opportunities">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Subject Line *</label>
                                <input type="text" class="form-input" name="subject" required placeholder="Exclusive Real Estate Opportunities">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Email Content</label>
                                <textarea class="form-input" name="content" rows="5" placeholder="Dear [Name], We have exciting new opportunities..."></textarea>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Target Audience</label>
                                <select class="form-input" name="target_audience">
                                    <option>All Contacts (${{contacts.length}} contacts)</option>
                                    <option>Investors Only</option>
                                    <option>Potential Sellers</option>
                                    <option>High Lead Score (70+)</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label style="display: flex; align-items: center; gap: 8px;">
                                    <input type="checkbox" name="launch_now" style="transform: scale(1.2);">
                                    <span class="form-label" style="margin: 0;">Launch campaign immediately</span>
                                </label>
                            </div>
                            <div style="text-align: center; margin-top: 30px;">
                                <button type="submit" class="action-button">Create Campaign</button>
                                <button type="button" class="secondary-button" onclick="showCampaignsView()">Cancel</button>
                            </div>
                        </form>
                    </div>
                `;
                showToast('Campaign form ready');
            }}
            
            function submitContact(event) {{
                event.preventDefault();
                const formData = new FormData(event.target);
                const contactData = Object.fromEntries(formData.entries());
                
                // Convert lead_score to integer
                contactData.lead_score = parseInt(contactData.lead_score) || 50;
                
                // Show loading
                showToast('Adding contact...');
                
                // Submit via Streamlit
                fetch(window.location.href, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        action: 'add_contact',
                        data: contactData
                    }})
                }}).then(() => {{
                    showToast('Contact added successfully!');
                    setTimeout(() => location.reload(), 2000);
                }}).catch(() => {{
                    // Fallback: store in sessionStorage for Streamlit to pick up
                    sessionStorage.setItem('contact_to_add', JSON.stringify(contactData));
                    location.reload();
                }});
            }}
            
            function submitDeal(event) {{
                event.preventDefault();
                const formData = new FormData(event.target);
                const dealData = Object.fromEntries(formData.entries());
                
                // Convert numeric fields
                dealData.purchase_price = parseFloat(dealData.purchase_price) || 0;
                dealData.expected_roi = parseFloat(dealData.expected_roi) || 0;
                dealData.arv = parseFloat(dealData.arv) || 0;
                dealData.repair_costs = parseFloat(dealData.repair_costs) || 0;
                dealData.contact_id = dealData.contact_id || null;
                
                showToast('Creating deal...');
                
                // Submit via sessionStorage for Streamlit
                sessionStorage.setItem('deal_to_add', JSON.stringify(dealData));
                location.reload();
            }}
            
            function submitCampaign(event) {{
                event.preventDefault();
                const formData = new FormData(event.target);
                const campaignData = Object.fromEntries(formData.entries());
                
                // Handle checkbox
                campaignData.launch_now = formData.has('launch_now');
                
                showToast('Creating campaign...');
                
                // Submit via sessionStorage for Streamlit
                sessionStorage.setItem('campaign_to_add', JSON.stringify(campaignData));
                location.reload();
            }}
            
            // Handle data from sessionStorage
            if (sessionStorage.getItem('contact_to_add')) {{
                const contactData = JSON.parse(sessionStorage.getItem('contact_to_add'));
                sessionStorage.removeItem('contact_to_add');
                // Trigger Streamlit session state update
                window.parent.postMessage({{
                    type: 'streamlit:setSessionState',
                    data: {{ contact_to_add: contactData }}
                }}, '*');
            }}
            
            if (sessionStorage.getItem('deal_to_add')) {{
                const dealData = JSON.parse(sessionStorage.getItem('deal_to_add'));
                sessionStorage.removeItem('deal_to_add');
                window.parent.postMessage({{
                    type: 'streamlit:setSessionState',
                    data: {{ deal_to_add: dealData }}
                }}, '*');
            }}
            
            if (sessionStorage.getItem('campaign_to_add')) {{
                const campaignData = JSON.parse(sessionStorage.getItem('campaign_to_add'));
                sessionStorage.removeItem('campaign_to_add');
                window.parent.postMessage({{
                    type: 'streamlit:setSessionState',
                    data: {{ campaign_to_add: campaignData }}
                }}, '*');
            }}
            
            // Initialize dashboard
            document.addEventListener('DOMContentLoaded', function() {{
                console.log('NXTRIX Platform Ready with Backend Integration');
                showDashboard();
                showToast('NXTRIX Platform Loaded Successfully!');
            }});
        </script>
    </body>
    </html>
    """

    # Render the application
    components.html(nxtrix_html, height=800, scrolling=False)

if __name__ == "__main__":
    main()