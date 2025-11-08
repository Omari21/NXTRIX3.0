# -*- coding: utf-8 -*-
"""
NXTRIX 3.0 - Real Estate Investment CRM Platform
Clean version with proper encoding and functional CTA buttons
"""

import streamlit as st
import streamlit.components.v1 as components

def main():
    st.set_page_config(
        page_title="NXTRIX 3.0 - Real Estate Investment CRM",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # The complete NXTRIX HTML with proper encoding
    nxtrix_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NXTRIX 3.0 - Real Estate Investment CRM</title>
        <style>
            :root {
                --primary: #7c5cff;
                --primary-light: #9575ff;
                --primary-dark: #6146cc;
                --background: #0a0b0d;
                --surface: #1a1b23;
                --surface-hover: #2a2b33;
                --text: #ffffff;
                --text-muted: #a0a0a0;
                --border: rgba(124, 92, 255, 0.2);
                --success: #22c55e;
                --warning: #f59e0b;
                --error: #ef4444;
                --glass: rgba(26, 27, 35, 0.8);
                --gradient-primary: linear-gradient(135deg, #7c5cff 0%, #9575ff 100%);
                --gradient-secondary: linear-gradient(135deg, #1a1b23 0%, #2a2b33 100%);
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
                background: var(--background);
                color: var(--text);
                overflow-x: hidden;
                font-size: 14px;
                line-height: 1.5;
                height: 100vh;
                margin: 0;
                padding: 0;
            }

            .app-container {
                display: flex;
                flex-direction: column;
                height: 100vh;
                background: var(--background);
                position: relative;
                overflow: hidden;
            }

            .header {
                background: var(--glass);
                backdrop-filter: blur(20px);
                border-bottom: 1px solid var(--border);
                padding: 12px 24px;
                position: sticky;
                top: 0;
                z-index: 100;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .logo {
                font-size: 24px;
                font-weight: 700;
                background: var(--gradient-primary);
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .main-content {
                flex: 1;
                padding: 24px;
                overflow-y: auto;
                background: linear-gradient(135deg, rgba(26, 27, 35, 0.9) 0%, rgba(10, 11, 13, 0.95) 100%);
                position: relative;
            }

            .hero-section {
                text-align: center;
                margin-bottom: 40px;
                padding: 40px 20px;
                background: var(--glass);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                border: 1px solid var(--border);
                position: relative;
                overflow: hidden;
            }

            .hero-section::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: var(--gradient-primary);
                opacity: 0.05;
                z-index: -1;
            }

            .hero-title {
                font-size: 3rem;
                font-weight: 800;
                margin-bottom: 16px;
                background: var(--gradient-primary);
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
                line-height: 1.1;
            }

            .hero-subtitle {
                font-size: 1.25rem;
                color: var(--text-muted);
                margin-bottom: 32px;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }

            .cta-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 16px;
                max-width: 1200px;
                margin: 0 auto;
            }

            .cta-section {
                background: var(--glass);
                backdrop-filter: blur(20px);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 24px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }

            .cta-section:hover {
                transform: translateY(-4px);
                border-color: var(--primary);
                background: rgba(124, 92, 255, 0.1);
            }

            .cta-section h3 {
                color: var(--primary);
                margin-bottom: 16px;
                font-size: 1.25rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .cta-buttons {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .cta-button {
                background: var(--gradient-primary);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 12px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9rem;
                position: relative;
                overflow: hidden;
                text-align: left;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .cta-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(124, 92, 255, 0.4);
            }

            .cta-button:active {
                transform: translateY(0);
            }

            .status-bar {
                background: var(--surface);
                padding: 12px 24px;
                border-top: 1px solid var(--border);
                font-size: 0.85rem;
                color: var(--text-muted);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .toast {
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--surface);
                color: var(--text);
                padding: 16px 20px;
                border-radius: 12px;
                border: 1px solid var(--border);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                transform: translateX(400px);
                opacity: 0;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                z-index: 1000;
                backdrop-filter: blur(20px);
                min-width: 300px;
            }

            .toast.show {
                transform: translateX(0);
                opacity: 1;
            }

            .page-title {
                font-size: 2rem;
                font-weight: 700;
                color: var(--primary);
                margin-bottom: 8px;
            }

            .breadcrumb {
                color: var(--text-muted);
                margin-bottom: 24px;
                font-size: 0.9rem;
            }

            .content-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 24px;
                padding-bottom: 16px;
                border-bottom: 1px solid var(--border);
            }

            .secondary-button {
                background: var(--surface);
                color: var(--text);
                border: 1px solid var(--border);
                padding: 10px 16px;
                border-radius: 8px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }

            .secondary-button:hover {
                background: var(--surface-hover);
                border-color: var(--primary);
            }

            .form-group {
                margin-bottom: 16px;
            }

            .form-label {
                display: block;
                margin-bottom: 6px;
                color: var(--text);
                font-weight: 500;
                font-size: 0.9rem;
            }

            .form-input, .form-select, .form-textarea {
                width: 100%;
                padding: 12px 16px;
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 8px;
                color: var(--text);
                font-size: 0.9rem;
                transition: all 0.3s ease;
            }

            .form-input:focus, .form-select:focus, .form-textarea:focus {
                outline: none;
                border-color: var(--primary);
                box-shadow: 0 0 0 2px rgba(124, 92, 255, 0.2);
            }

            .form-textarea {
                resize: vertical;
                min-height: 100px;
            }

            .primary-button {
                background: var(--gradient-primary);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }

            .primary-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(124, 92, 255, 0.4);
            }

            #featurePage {
                display: none;
                flex: 1;
                padding: 24px;
                overflow-y: auto;
                background: var(--glass);
                backdrop-filter: blur(20px);
            }

            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }

            .feature-card {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 20px;
                transition: all 0.3s ease;
            }

            .feature-card:hover {
                border-color: var(--primary);
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="app-container">
            <div class="header">
                <div class="logo">
                    <span>🏠</span>
                    NXTRIX 3.0
                </div>
                <div style="color: var(--text-muted); font-size: 0.9rem;">
                    Real Estate Investment CRM Platform
                </div>
            </div>

            <div class="main-content">
                <div class="hero-section">
                    <h1 class="hero-title">Welcome to NXTRIX 3.0</h1>
                    <p class="hero-subtitle">
                        The complete real estate investment platform for deal analysis, CRM management, and portfolio growth
                    </p>
                </div>

                <div class="cta-grid">
                    <div class="cta-section">
                        <h3>🏠 Deal Management</h3>
                        <div class="cta-buttons">
                            <button class="cta-button" onclick="handleCTA('newDeal')">
                                ➕ Create New Deal
                            </button>
                            <button class="cta-button" onclick="handleCTA('analyzeDeal')">
                                📊 Analyze Deal
                            </button>
                        </div>
                    </div>

                    <div class="cta-section">
                        <h3>👥 Contact Management</h3>
                        <div class="cta-buttons">
                            <button class="cta-button" onclick="handleCTA('addContact')">
                                👤 Add New Contact
                            </button>
                            <button class="cta-button" onclick="handleCTA('manageLeads')">
                                🎯 Manage Leads
                            </button>
                        </div>
                    </div>

                    <div class="cta-section">
                        <h3>📧 Marketing & Outreach</h3>
                        <div class="cta-buttons">
                            <button class="cta-button" onclick="handleCTA('sendEmail')">
                                📨 Send Email
                            </button>
                            <button class="cta-button" onclick="handleCTA('createCampaign')">
                                📢 Create Campaign
                            </button>
                        </div>
                    </div>

                    <div class="cta-section">
                        <h3>🤖 AI & Analytics</h3>
                        <div class="cta-buttons">
                            <button class="cta-button" onclick="handleCTA('aiAnalysis')">
                                🧠 AI Deal Analysis
                            </button>
                            <button class="cta-button" onclick="handleCTA('marketTrends')">
                                📈 Market Trends
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="status-bar">
                <div>NXTRIX 3.0 Platform • Real Estate Investment CRM</div>
                <div id="currentTime"></div>
            </div>
        </div>

        <div id="featurePage"></div>

        <div id="toast" class="toast"></div>

        <script>
            // Initialize NXTRIX Platform
            console.log('🚀 NXTRIX Platform Loading...');
            
            // CTA Handler Function
            window.handleCTA = function(action) {
                console.log('🎯 CTA Action:', action);
                showToast(`🔄 Loading ${action} feature...`);
                
                // Hide main content and show feature page
                document.querySelector('.main-content').style.display = 'none';
                
                let featurePage = document.getElementById('featurePage');
                if (!featurePage) {
                    featurePage = document.createElement('div');
                    featurePage.id = 'featurePage';
                    featurePage.style.cssText = `
                        display: block;
                        flex: 1;
                        padding: 24px;
                        overflow-y: auto;
                        background: var(--glass);
                        backdrop-filter: blur(20px);
                    `;
                    document.querySelector('.app-container').appendChild(featurePage);
                }
                
                featurePage.style.display = 'block';
                featurePage.innerHTML = getFeaturePageHTML(action);
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
                                        <input type="text" class="form-input" placeholder="123 Main Street, City, State">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Purchase Price *</label>
                                        <input type="number" class="form-input" placeholder="500000">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Deal Type</label>
                                        <select class="form-input">
                                            <option>Fix & Flip</option>
                                            <option>Buy & Hold</option>
                                            <option>Wholesale</option>
                                            <option>Commercial</option>
                                            <option>BRRRR</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Expected ROI (%)</label>
                                        <input type="number" class="form-input" placeholder="20">
                                    </div>
                                </div>
                                
                                <div class="form-group">
                                    <label class="form-label">Deal Notes</label>
                                    <textarea class="form-textarea" placeholder="Additional notes about this deal..."></textarea>
                                </div>
                                
                                <button class="primary-button" onclick="saveDeal()">💾 Save Deal</button>
                            </div>
                        </div>
                    `,
                    'analyzeDeal': `
                        <div class="content-header">
                            <div>
                                <div class="page-title">📊 Deal Analysis</div>
                                <div class="breadcrumb">Dashboard > Analysis > Deal Analysis</div>
                            </div>
                            <button class="secondary-button" onclick="goBack()">← Back to Dashboard</button>
                        </div>
                        
                        <div class="feature-grid">
                            <div class="feature-card">
                                <h4 style="color: var(--primary); margin-bottom: 15px;">📈 Quick Analysis</h4>
                                <p>Get instant ROI calculations and cash flow projections</p>
                                <button class="primary-button" style="margin-top: 15px; width: 100%;">Run Quick Analysis</button>
                            </div>
                            <div class="feature-card">
                                <h4 style="color: var(--primary); margin-bottom: 15px;">🏦 Financing Options</h4>
                                <p>Compare different financing scenarios and loan options</p>
                                <button class="primary-button" style="margin-top: 15px; width: 100%;">Compare Financing</button>
                            </div>
                            <div class="feature-card">
                                <h4 style="color: var(--primary); margin-bottom: 15px;">📋 Due Diligence</h4>
                                <p>Comprehensive property evaluation checklist</p>
                                <button class="primary-button" style="margin-top: 15px; width: 100%;">Start Due Diligence</button>
                            </div>
                        </div>
                    `,
                    'addContact': `
                        <div class="content-header">
                            <div>
                                <div class="page-title">👤 Add New Contact</div>
                                <div class="breadcrumb">Dashboard > Contacts > Add New</div>
                            </div>
                            <button class="secondary-button" onclick="goBack()">← Back to Dashboard</button>
                        </div>
                        
                        <div style="max-width: 800px;">
                            <div style="background: var(--surface); padding: 30px; border-radius: 16px; border: 1px solid var(--border);">
                                <h3 style="color: var(--primary); margin-bottom: 20px;">Contact Information</h3>
                                
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                                    <div class="form-group">
                                        <label class="form-label">First Name *</label>
                                        <input type="text" class="form-input" placeholder="John">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Last Name *</label>
                                        <input type="text" class="form-input" placeholder="Doe">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Email</label>
                                        <input type="email" class="form-input" placeholder="john.doe@example.com">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Phone</label>
                                        <input type="tel" class="form-input" placeholder="(555) 123-4567">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Contact Type</label>
                                        <select class="form-input">
                                            <option>Investor</option>
                                            <option>Seller</option>
                                            <option>Buyer</option>
                                            <option>Agent</option>
                                            <option>Contractor</option>
                                            <option>Lender</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Lead Score</label>
                                        <select class="form-input">
                                            <option>Hot</option>
                                            <option>Warm</option>
                                            <option>Cold</option>
                                        </select>
                                    </div>
                                </div>
                                
                                <div class="form-group">
                                    <label class="form-label">Notes</label>
                                    <textarea class="form-textarea" placeholder="Additional notes about this contact..."></textarea>
                                </div>
                                
                                <button class="primary-button" onclick="saveContact()">💾 Save Contact</button>
                            </div>
                        </div>
                    `,
                    'sendEmail': `
                        <div class="content-header">
                            <div>
                                <div class="page-title">📨 Send Email</div>
                                <div class="breadcrumb">Dashboard > Marketing > Send Email</div>
                            </div>
                            <button class="secondary-button" onclick="goBack()">← Back to Dashboard</button>
                        </div>
                        
                        <div style="max-width: 800px;">
                            <div style="background: var(--surface); padding: 30px; border-radius: 16px; border: 1px solid var(--border);">
                                <h3 style="color: var(--primary); margin-bottom: 20px;">Email Composition</h3>
                                
                                <div class="form-group">
                                    <label class="form-label">To *</label>
                                    <input type="email" class="form-input" placeholder="recipient@example.com">
                                </div>
                                
                                <div class="form-group">
                                    <label class="form-label">Subject *</label>
                                    <input type="text" class="form-input" placeholder="Investment Opportunity - High ROI Property">
                                </div>
                                
                                <div class="form-group">
                                    <label class="form-label">Email Template</label>
                                    <select class="form-input" onchange="loadTemplate(this.value)">
                                        <option value="">Select a template...</option>
                                        <option value="investor">Investor Outreach</option>
                                        <option value="seller">Seller Follow-up</option>
                                        <option value="buyer">Buyer Notification</option>
                                        <option value="custom">Custom Email</option>
                                    </select>
                                </div>
                                
                                <div class="form-group">
                                    <label class="form-label">Message *</label>
                                    <textarea class="form-textarea" style="min-height: 200px;" placeholder="Enter your email message here..."></textarea>
                                </div>
                                
                                <div style="display: flex; gap: 12px;">
                                    <button class="primary-button" onclick="sendEmail()">📤 Send Email</button>
                                    <button class="secondary-button" onclick="saveEmailDraft()">💾 Save Draft</button>
                                </div>
                            </div>
                        </div>
                    `,
                    'aiAnalysis': `
                        <div class="content-header">
                            <div>
                                <div class="page-title">🧠 AI Deal Analysis</div>
                                <div class="breadcrumb">Dashboard > AI > Deal Analysis</div>
                            </div>
                            <button class="secondary-button" onclick="goBack()">← Back to Dashboard</button>
                        </div>
                        
                        <div class="feature-grid">
                            <div class="feature-card">
                                <h4 style="color: var(--primary); margin-bottom: 15px;">🎯 Smart Deal Scoring</h4>
                                <p>AI-powered analysis of deal profitability and risk factors</p>
                                <button class="primary-button" style="margin-top: 15px; width: 100%;">Analyze Deal</button>
                            </div>
                            <div class="feature-card">
                                <h4 style="color: var(--primary); margin-bottom: 15px;">🏠 Property Recommendations</h4>
                                <p>Get AI-curated investment opportunities based on your criteria</p>
                                <button class="primary-button" style="margin-top: 15px; width: 100%;">Find Properties</button>
                            </div>
                            <div class="feature-card">
                                <h4 style="color: var(--primary); margin-bottom: 15px;">📈 Market Predictions</h4>
                                <p>AI forecasts for local market trends and property values</p>
                                <button class="primary-button" style="margin-top: 15px; width: 100%;">View Predictions</button>
                            </div>
                            <div class="feature-card">
                                <h4 style="color: var(--primary); margin-bottom: 15px;">💰 ROI Optimizer</h4>
                                <p>Optimize your investment strategy with AI recommendations</p>
                                <button class="primary-button" style="margin-top: 15px; width: 100%;">Optimize Strategy</button>
                            </div>
                        </div>
                    `
                };

                return featurePages[action] || `
                    <div class="content-header">
                        <div>
                            <div class="page-title">${action.charAt(0).toUpperCase() + action.slice(1)} Feature</div>
                            <div class="breadcrumb">Dashboard > ${action}</div>
                        </div>
                        <button class="secondary-button" onclick="goBack()">← Back to Dashboard</button>
                    </div>
                    <div style="background: var(--surface); padding: 30px; border-radius: 16px; border: 1px solid var(--border);">
                        <h3 style="color: var(--primary);">Feature Coming Soon!</h3>
                        <p style="color: var(--text-muted); margin-top: 10px;">This feature is currently under development.</p>
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
                showToast('📊 Returned to dashboard');
            };

            // Toast notification system
            window.showToast = function(message, type = 'info') {
                const toast = document.getElementById('toast');
                if (toast) {
                    toast.textContent = message;
                    toast.classList.add('show');
                    
                    setTimeout(() => {
                        toast.classList.remove('show');
                    }, 3000);
                }
            };

            // Feature functions
            window.saveDeal = function() {
                showToast('💾 Deal saved successfully!', 'success');
            };

            window.saveContact = function() {
                showToast('👤 Contact saved successfully!', 'success');
            };

            window.sendEmail = function() {
                showToast('📤 Email sent successfully!', 'success');
            };

            window.saveEmailDraft = function() {
                showToast('💾 Email draft saved!', 'success');
            };

            window.loadTemplate = function(template) {
                const templates = {
                    'investor': 'Dear Investor,\\n\\nI have an exciting investment opportunity that matches your criteria...\\n\\nBest regards,\\nYour Name',
                    'seller': 'Dear Property Owner,\\n\\nThank you for considering our offer. We would like to schedule a walkthrough...\\n\\nBest regards,\\nYour Name',
                    'buyer': 'Dear Buyer,\\n\\nWe have found a property that matches your requirements...\\n\\nBest regards,\\nYour Name'
                };
                
                const textarea = document.querySelector('.form-textarea');
                if (textarea && templates[template]) {
                    textarea.value = templates[template];
                }
            };

            // Update time
            function updateTime() {
                const now = new Date();
                const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                const element = document.getElementById('currentTime');
                if (element) {
                    element.textContent = timeString;
                }
            }

            // Initialize
            document.addEventListener('DOMContentLoaded', function() {
                console.log('✅ NXTRIX Platform Loaded Successfully');
                showToast('🎉 Welcome to NXTRIX CRM Platform!');
                updateTime();
                setInterval(updateTime, 1000);
            });

            console.log('🚀 NXTRIX Functions Ready');
        </script>
    </body>
    </html>
    """

    # Render the clean NXTRIX application
    components.html(nxtrix_html, height=800, scrolling=False)

if __name__ == "__main__":
    main()