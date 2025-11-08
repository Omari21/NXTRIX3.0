import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NXTRIX Debug",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit UI
st.markdown("""
<style>
    .stApp > header {visibility: hidden;}
    .main > div {padding-top: 0px;}
    .block-container {padding-top: 0px; padding-bottom: 0px; max-width: 100%; margin: 0px;}
</style>
""", unsafe_allow_html=True)

# Minimal NXTRIX test with the original design but simpler JavaScript
test_app = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NXTRIX Debug</title>
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
        
        .main-content { flex: 1; padding: 20px; overflow-y: auto; }
        
        .cta-button {
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
        
        .cta-button:hover {
            background: rgba(74, 175, 79, 0.2);
            transform: translateX(5px);
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
            cursor: pointer;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
        }
        
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            border-radius: 8px;
            background: #4CAF50;
            color: white;
            font-weight: 600;
            z-index: 1001;
            transform: translateX(400px);
            transition: transform 0.3s ease;
        }
        
        .toast.show { transform: translateX(0); }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="sidebar">
            <h2 style="margin-bottom: 30px;">🏢 NXTRIX</h2>
            
            <button class="cta-button" onclick="testCTA('newDeal')">
                🏠 Create New Deal
            </button>
            <button class="cta-button" onclick="testCTA('analyzeDeal')">
                📊 Deal Analysis
            </button>
            <button class="cta-button" onclick="testCTA('addContact')">
                👥 Add Contact
            </button>
            <button class="cta-button" onclick="testCTA('sendEmail')">
                📧 Email Marketing
            </button>
            <button class="cta-button" onclick="testCTA('aiAnalysis')">
                🤖 AI Insights
            </button>
        </div>
        
        <div class="main-content">
            <h1>NXTRIX Platform - Debug Version</h1>
            <p style="margin: 20px 0;">Testing CTA button functionality with minimal JavaScript</p>
            
            <div class="dashboard-grid">
                <div class="metric-card" onclick="testCTA('revenue')">
                    <h3>📊 Total Revenue</h3>
                    <p style="font-size: 2em; margin: 10px 0;">$2.4M</p>
                    <p>Click to test</p>
                </div>
                
                <div class="metric-card" onclick="testCTA('deals')">
                    <h3>🏠 Active Deals</h3>
                    <p style="font-size: 2em; margin: 10px 0;">47</p>
                    <p>Click to test</p>
                </div>
                
                <div class="metric-card" onclick="testCTA('contacts')">
                    <h3>👥 Contacts</h3>
                    <p style="font-size: 2em; margin: 10px 0;">1,234</p>
                    <p>Click to test</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Toast Notifications -->
    <div class="toast" id="toast">
        <span id="toastMessage"></span>
    </div>
    
    <script>
        // Simple, clean JavaScript without complex features
        console.log('🔍 NXTRIX Debug script loading...');
        
        // Main CTA function
        function testCTA(action) {
            console.log('🎯 CTA triggered:', action);
            showToast('✅ ' + action + ' button works!');
            
            // Simple alert for testing
            setTimeout(function() {
                alert('Success! ' + action + ' feature is working.');
            }, 1000);
        }
        
        // Toast function
        function showToast(message) {
            console.log('📢 Toast:', message);
            
            var toast = document.getElementById('toast');
            var toastMessage = document.getElementById('toastMessage');
            
            if (toast && toastMessage) {
                toastMessage.textContent = message;
                toast.classList.add('show');
                
                setTimeout(function() {
                    toast.classList.remove('show');
                }, 3000);
            }
        }
        
        // Initialize
        console.log('✅ Debug script loaded successfully');
        showToast('🎉 NXTRIX Debug ready!');
    </script>
</body>
</html>
"""

# Render the debug version
components.html(test_app, height=800, scrolling=False)