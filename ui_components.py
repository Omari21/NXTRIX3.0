"""
NXTRIX Platform - Premium UI/UX CSS Styling
Modern, professional design for real estate investment platform
"""

import streamlit as st

def apply_premium_styling():
    """Apply premium CSS styling to NXTRIX platform"""
    st.markdown("""
    <style>
    /* ============================================
       NXTRIX PREMIUM THEME - PROFESSIONAL DESIGN
       ============================================ */
    
    /* Import Modern Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* ============================================
       ROOT VARIABLES - DESIGN SYSTEM
       ============================================ */
    :root {
        --primary-color: #2563eb;
        --primary-dark: #1d4ed8;
        --primary-light: #3b82f6;
        --secondary-color: #10b981;
        --accent-color: #f59e0b;
        --danger-color: #ef4444;
        --warning-color: #f97316;
        
        --dark-bg: #0f172a;
        --dark-surface: #1e293b;
        --dark-card: #334155;
        --light-bg: #ffffff;
        --light-surface: #f8fafc;
        --light-card: #ffffff;
        
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --text-muted: #94a3b8;
        --text-inverse: #f8fafc;
        
        --border-light: #e2e8f0;
        --border-medium: #cbd5e1;
        --border-dark: #475569;
        
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
        
        --spacing-xs: 4px;
        --spacing-sm: 8px;
        --spacing-md: 16px;
        --spacing-lg: 24px;
        --spacing-xl: 32px;
        --spacing-2xl: 48px;
    }
    
    /* ============================================
       GLOBAL STYLES
       ============================================ */
    .main {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        min-height: 100vh;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ============================================
       HEADER & NAVIGATION
       ============================================ */
    .nxtrix-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
        padding: var(--spacing-lg);
        margin: -1rem -1rem var(--spacing-xl) -1rem;
        border-radius: 0 0 var(--radius-xl) var(--radius-xl);
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .nxtrix-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
        opacity: 0.3;
    }
    
    .nxtrix-logo {
        color: var(--text-inverse);
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .nxtrix-tagline {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        font-weight: 400;
        margin: var(--spacing-sm) 0 0 0;
        position: relative;
        z-index: 1;
    }
    
    /* ============================================
       CARDS & CONTAINERS
       ============================================ */
    .nxtrix-card {
        background: var(--light-card);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        margin: var(--spacing-md) 0;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-light);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .nxtrix-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
        border-color: var(--primary-light);
    }
    
    .nxtrix-card-header {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
        margin-bottom: var(--spacing-lg);
        padding-bottom: var(--spacing-md);
        border-bottom: 2px solid var(--border-light);
    }
    
    .nxtrix-card-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
        box-shadow: var(--shadow-md);
    }
    
    .nxtrix-card-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        flex: 1;
    }
    
    /* ============================================
       BUTTONS & INTERACTIONS
       ============================================ */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
        color: white;
        border: none;
        border-radius: var(--radius-md);
        padding: var(--spacing-md) var(--spacing-xl);
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-md);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-color) 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Success Button */
    .success-button {
        background: linear-gradient(135deg, var(--secondary-color) 0%, #059669 100%) !important;
    }
    
    /* Warning Button */
    .warning-button {
        background: linear-gradient(135deg, var(--accent-color) 0%, #d97706 100%) !important;
    }
    
    /* Danger Button */
    .danger-button {
        background: linear-gradient(135deg, var(--danger-color) 0%, #dc2626 100%) !important;
    }
    
    /* ============================================
       FORMS & INPUTS
       ============================================ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        border-radius: var(--radius-md);
        border: 2px solid var(--border-light);
        padding: var(--spacing-md);
        font-size: 1rem;
        transition: all 0.3s ease;
        background: var(--light-surface);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        outline: none;
    }
    
    /* ============================================
       METRICS & KPIs
       ============================================ */
    .metric-container {
        background: var(--light-card);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        text-align: center;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-light);
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin: 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin: var(--spacing-sm) 0 0 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    
    .metric-change {
        font-size: 0.85rem;
        font-weight: 600;
        margin: var(--spacing-xs) 0 0 0;
    }
    
    .metric-change.positive {
        color: var(--secondary-color);
    }
    
    .metric-change.negative {
        color: var(--danger-color);
    }
    
    /* ============================================
       TABLES & DATA
       ============================================ */
    .stDataFrame {
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-light);
    }
    
    .stDataFrame table {
        background: var(--light-card);
    }
    
    .stDataFrame th {
        background: var(--primary-color) !important;
        color: white !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.85rem;
        padding: var(--spacing-md) !important;
    }
    
    .stDataFrame td {
        padding: var(--spacing-md) !important;
        border-bottom: 1px solid var(--border-light);
    }
    
    .stDataFrame tr:hover {
        background: var(--light-surface);
    }
    
    /* ============================================
       SIDEBAR STYLING
       ============================================ */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--dark-bg) 0%, var(--dark-surface) 100%);
        border-right: 1px solid var(--border-dark);
    }
    
    .sidebar .sidebar-content {
        background: transparent;
        color: var(--text-inverse);
    }
    
    /* ============================================
       STATUS INDICATORS
       ============================================ */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: var(--spacing-xs);
        padding: var(--spacing-xs) var(--spacing-md);
        border-radius: var(--radius-sm);
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-active {
        background: rgba(16, 185, 129, 0.1);
        color: var(--secondary-color);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .status-pending {
        background: rgba(245, 158, 11, 0.1);
        color: var(--accent-color);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .status-inactive {
        background: rgba(239, 68, 68, 0.1);
        color: var(--danger-color);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* ============================================
       ANIMATIONS
       ============================================ */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
    
    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    .pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* ============================================
       CHARTS & VISUALIZATIONS
       ============================================ */
    .stPlotlyChart {
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-light);
        overflow: hidden;
        background: var(--light-card);
    }
    
    /* ============================================
       RESPONSIVE DESIGN
       ============================================ */
    @media (max-width: 768px) {
        .nxtrix-header {
            padding: var(--spacing-md);
            margin: -1rem -1rem var(--spacing-lg) -1rem;
        }
        
        .nxtrix-logo {
            font-size: 2rem;
        }
        
        .nxtrix-tagline {
            font-size: 1rem;
        }
        
        .nxtrix-card {
            padding: var(--spacing-md);
            margin: var(--spacing-sm) 0;
        }
        
        .metric-value {
            font-size: 2rem;
        }
    }
    
    /* ============================================
       UTILITY CLASSES
       ============================================ */
    .text-center { text-align: center; }
    .text-left { text-align: left; }
    .text-right { text-align: right; }
    
    .mb-0 { margin-bottom: 0; }
    .mb-1 { margin-bottom: var(--spacing-xs); }
    .mb-2 { margin-bottom: var(--spacing-sm); }
    .mb-3 { margin-bottom: var(--spacing-md); }
    .mb-4 { margin-bottom: var(--spacing-lg); }
    
    .mt-0 { margin-top: 0; }
    .mt-1 { margin-top: var(--spacing-xs); }
    .mt-2 { margin-top: var(--spacing-sm); }
    .mt-3 { margin-top: var(--spacing-md); }
    .mt-4 { margin-top: var(--spacing-lg); }
    
    .p-0 { padding: 0; }
    .p-1 { padding: var(--spacing-xs); }
    .p-2 { padding: var(--spacing-sm); }
    .p-3 { padding: var(--spacing-md); }
    .p-4 { padding: var(--spacing-lg); }
    
    .rounded { border-radius: var(--radius-md); }
    .rounded-lg { border-radius: var(--radius-lg); }
    .shadow { box-shadow: var(--shadow-md); }
    .shadow-lg { box-shadow: var(--shadow-lg); }
    
    /* ============================================
       PREMIUM FEATURES
       ============================================ */
    .premium-badge {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
        color: #92400e;
        padding: var(--spacing-xs) var(--spacing-sm);
        border-radius: var(--radius-sm);
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: inline-flex;
        align-items: center;
        gap: var(--spacing-xs);
        box-shadow: var(--shadow-sm);
    }
    
    .trial-banner {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #f59e0b;
        border-radius: var(--radius-lg);
        padding: var(--spacing-md);
        margin: var(--spacing-md) 0;
        text-align: center;
        box-shadow: var(--shadow-sm);
    }
    
    .trial-banner h3 {
        color: #92400e;
        margin: 0 0 var(--spacing-sm) 0;
        font-weight: 600;
    }
    
    .trial-banner p {
        color: #a16207;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

def create_header():
    """Create premium header for NXTRIX platform"""
    st.markdown("""
    <div class="nxtrix-header">
        <h1 class="nxtrix-logo">🏢 NXTRIX</h1>
        <p class="nxtrix-tagline">Professional Real Estate Investment Platform</p>
    </div>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, change=None, icon="📊"):
    """Create beautiful metric card"""
    change_html = ""
    if change:
        change_class = "positive" if change >= 0 else "negative"
        change_symbol = "↗" if change >= 0 else "↘"
        change_html = f'<p class="metric-change {change_class}">{change_symbol} {abs(change):.1f}%</p>'
    
    return f"""
    <div class="metric-container fade-in">
        <div style="font-size: 1.5rem; margin-bottom: 8px;">{icon}</div>
        <h2 class="metric-value">{value}</h2>
        <p class="metric-label">{title}</p>
        {change_html}
    </div>
    """

def create_card(title, content, icon="🔧"):
    """Create styled card container"""
    return f"""
    <div class="nxtrix-card fade-in">
        <div class="nxtrix-card-header">
            <div class="nxtrix-card-icon">{icon}</div>
            <h3 class="nxtrix-card-title">{title}</h3>
        </div>
        <div class="nxtrix-card-content">
            {content}
        </div>
    </div>
    """

def create_status_badge(status, text):
    """Create status indicator badge"""
    return f'<span class="status-indicator status-{status}">{text}</span>'

def create_premium_badge():
    """Create premium subscription badge"""
    return '<span class="premium-badge">✨ PREMIUM</span>'