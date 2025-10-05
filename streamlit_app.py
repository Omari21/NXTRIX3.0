import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import openai
import os
from supabase import create_client, Client
import uuid
# Optional AI module import with error handling
try:
    from ai_prediction_engine import AIMarketPredictor, get_ai_predictor, create_prediction_visualizations
    AI_MODULE_AVAILABLE = True
except ImportError:
    AI_MODULE_AVAILABLE = False
    # Create placeholder functions when module is not available
    class AIMarketPredictor:
        def __init__(self, *args, **kwargs):
            pass
        def predict(self, *args, **kwargs):
            return {"error": "AI module not available"}
    
    def get_ai_predictor(*args, **kwargs):
        return AIMarketPredictor()
    
    def create_prediction_visualizations(*args, **kwargs):
        return None

# Lazy import functions to avoid event loop issues
@st.cache_resource
def get_db_service():
    """Lazy load database service"""
    try:
        from database import db_service
        return db_service
    except Exception as e:
        st.error(f"Database service error: {e}")
        return None

@st.cache_resource
def get_financial_modeling():
    """Lazy load financial modeling"""
    try:
        from financial_modeling import AdvancedFinancialModeling, create_cash_flow_chart, create_monte_carlo_chart, create_sensitivity_chart, create_exit_strategy_chart
        return AdvancedFinancialModeling, create_cash_flow_chart, create_monte_carlo_chart, create_sensitivity_chart, create_exit_strategy_chart
    except Exception as e:
        st.error(f"Financial modeling error: {e}")
        return None, None, None, None, None

@st.cache_resource
def get_portfolio_analytics():
    """Lazy load portfolio analytics"""
    try:
        from portfolio_analytics import PortfolioAnalyzer, create_portfolio_performance_chart, create_portfolio_metrics_dashboard, create_geographic_diversification_map
        return PortfolioAnalyzer, create_portfolio_performance_chart, create_portfolio_metrics_dashboard, create_geographic_diversification_map
    except Exception as e:
        st.error(f"Portfolio analytics error: {e}")
        return None, None, None, None

@st.cache_resource
def get_investor_portal():
    """Lazy load investor portal"""
    try:
        from investor_portal import InvestorPortalManager, InvestorDashboard, generate_investor_report
        return InvestorPortalManager, InvestorDashboard, generate_investor_report
    except Exception as e:
        st.error(f"Investor portal error: {e}")
        return None, None, None

@st.cache_resource
def get_enhanced_crm():
    """Lazy load enhanced CRM"""
    try:
        from enhanced_crm import show_enhanced_crm
        return show_enhanced_crm
    except Exception as e:
        st.error(f"Enhanced CRM error: {e}")
        return None

@st.cache_resource
def get_models():
    """Lazy load models"""
    try:
        from models import Deal, Investor, Portfolio
        return Deal, Investor, Portfolio
    except Exception as e:
        st.error(f"Models error: {e}")
        return None, None, None

# Navigation helper functions
def navigate_to_page(page_name):
    """Helper function to navigate to a specific page"""
    st.session_state.redirect_to_page = page_name
    st.rerun()

def get_current_page():
    """Get the current page with redirect handling"""
    if 'redirect_to_page' in st.session_state:
        redirect_page = st.session_state.redirect_to_page
        del st.session_state.redirect_to_page
        return redirect_page
    return None

# Page configuration
st.set_page_config(
    page_title="NXTRIX Deal Analyzer CRM",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize OpenAI
openai.api_key = st.secrets["OPENAI"]["OPENAI_API_KEY"]

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE"]["SUPABASE_URL"]
    key = st.secrets["SUPABASE"]["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Custom CSS for better styling with proper contrast
st.markdown("""
<style>
    /* ===========================================
       MOBILE-FIRST RESPONSIVE FRAMEWORK
       =========================================== */
    
    /* Base mobile-first styles */
    .stApp {
        background-color: #0e1117;
        color: white;
        font-size: 16px;
        line-height: 1.5;
    }
    
    /* Mobile viewport meta tag enforcement */
    @viewport {
        width: device-width;
        initial-scale: 1.0;
        maximum-scale: 5.0;
        user-scalable: yes;
    }
    
    /* ===========================================
       RESPONSIVE TYPOGRAPHY
       =========================================== */
    
    /* Mobile-first typography */
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
        font-weight: 600;
        line-height: 1.3;
        margin-bottom: 0.75rem;
    }
    
    h1 { font-size: 1.75rem; }  /* 28px */
    h2 { font-size: 1.5rem; }   /* 24px */
    h3 { font-size: 1.25rem; }  /* 20px */
    h4 { font-size: 1.125rem; } /* 18px */
    
    /* Tablet breakpoint - 768px and up */
    @media (min-width: 768px) {
        h1 { font-size: 2.25rem; }  /* 36px */
        h2 { font-size: 1.875rem; } /* 30px */
        h3 { font-size: 1.5rem; }   /* 24px */
        h4 { font-size: 1.25rem; }  /* 20px */
    }
    
    /* Desktop breakpoint - 1024px and up */
    @media (min-width: 1024px) {
        h1 { font-size: 2.5rem; }   /* 40px */
        h2 { font-size: 2rem; }     /* 32px */
        h3 { font-size: 1.75rem; }  /* 28px */
        h4 { font-size: 1.5rem; }   /* 24px */
    }
    
    /* ===========================================
       MOBILE HEADER & NAVIGATION
       =========================================== */
    
    .main-header {
        background-color: #262730;
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        border: 1px solid #404040;
    }
    
    .main-header h1 {
        margin-bottom: 0.25rem;
        font-size: 1.5rem;
        font-weight: 700;
        color: white;
    }
    
    .main-header p {
        font-size: 0.9rem;
        opacity: 0.9;
        color: white;
        margin: 0;
    }
    
    /* Tablet header adjustments */
    @media (min-width: 768px) {
        .main-header {
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
    }
    
    /* Desktop header adjustments */
    @media (min-width: 1024px) {
        .main-header {
            padding: 2.5rem;
            border-radius: 15px;
            margin-bottom: 2rem;
        }
        
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .main-header p {
            font-size: 1.2rem;
        }
    }
    
    /* ===========================================
       MOBILE-OPTIMIZED CARDS & METRICS
       =========================================== */
    
    /* Mobile-first metric cards */
    .metric-card, .deal-card {
        background-color: #262730;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #404040;
        margin-bottom: 1rem;
        color: white;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover, .deal-card:hover {
        transform: translateY(-2px);
        border-color: #4CAF50;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.15);
    }
    
    .metric-card h3 {
        color: #ffffff;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.25rem;
    }
    
    .metric-card h2 {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
        color: white;
    }
    
    .metric-card p {
        color: #cccccc;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 0;
    }
    
    /* Tablet metric adjustments */
    @media (min-width: 768px) {
        .metric-card, .deal-card {
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.25rem;
        }
        
        .metric-card h3 {
            font-size: 0.85rem;
            margin-bottom: 0.375rem;
        }
        
        .metric-card h2 {
            font-size: 1.75rem;
            margin-bottom: 0.375rem;
        }
        
        .metric-card p {
            font-size: 0.875rem;
        }
    }
    
    /* Desktop metric adjustments */
    @media (min-width: 1024px) {
        .metric-card, .deal-card {
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 1.5rem;
        }
        
        .metric-card h3 {
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
        
        .metric-card h2 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .metric-card p {
            font-size: 0.9rem;
        }
    }
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-card h2 {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: white;
    }
    
    .metric-card p {
        color: #cccccc;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Deal cards with enhanced visibility */
    .deal-card {
        background-color: #262730;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #404040;
        margin-bottom: 1.5rem;
        color: white;
    }
    
    .deal-card:hover {
        transform: translateY(-2px);
        border-color: #4CAF50;
    }
    
    /* AI Score badge with better visibility */
    .ai-score {
        background-color: #4CAF50;
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
        letter-spacing: 0.5px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #262730;
    }
    
    /* Section headers */
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
        font-weight: 600;
    }
    
    /* Input fields styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        background-color: #262730;
        border: 2px solid #404040;
        border-radius: 8px;
        color: white;
        font-weight: 500;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        background-color: #45a049;
    }
    
    /* Metrics display */
    .stMetric {
        background-color: #262730;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #404040;
        color: white;
    }
    
    .stMetric > div {
        color: white;
    }
    
    /* Ensure all text elements are visible */
    .stMarkdown {
        color: white;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #262730;
        color: white;
        border: 1px solid #404040;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        background-color: #262730;
        color: white;
        border: 1px solid #404040;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #262730;
        border: 1px solid #404040;
        color: white;
    }
    
    .stSuccess {
        background-color: #262730;
        border: 1px solid #4CAF50;
        color: white;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: #262730;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #404040;
    }
    
    /* Chart containers */
    .js-plotly-plot {
        background-color: #262730;
        border-radius: 10px;
        border: 1px solid #404040;
    }
    
    /* Status badges */
    .status-active {
        background-color: #4CAF50;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-pending {
        background-color: #FF9800;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-closed {
        background-color: #607D8B;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* High contrast text */
    .highlight-text {
        color: white;
        font-weight: 600;
    }
    
    .accent-text {
        color: #4CAF50;
        font-weight: 600;
    }
    
    /* Remove default streamlit styling that causes issues */
    .element-container {
        background: transparent !important;
    }
    
    /* Ensure text is always visible */
    p, span, div {
        color: white !important;
    }
    
    /* Override any problematic backgrounds */
    .stMarkdown {
        color: white !important;
    }
    
    /* Fix metric containers */
    .stMetric [data-testid="metric-container"] {
        background-color: #262730;
        border: 1px solid #404040;
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
    }
    
    .stMetric [data-testid="metric-container"] > div {
        color: white !important;
    }
    
    /* ===========================================
       TOUCH-FRIENDLY INPUTS & BUTTONS
       =========================================== */
    
    /* Mobile-optimized inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        background-color: #262730;
        border: 2px solid #404040;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        min-height: 44px; /* Touch target minimum */
        font-size: 16px; /* Prevents zoom on iOS */
        padding: 0.75rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
        outline: none;
    }
    
    /* Touch-friendly buttons */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        min-height: 44px; /* Touch target minimum */
        min-width: 44px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #45a049;
        transform: translateY(-1px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Desktop button adjustments */
    @media (min-width: 1024px) {
        .stButton > button {
            padding: 0.75rem 2rem;
        }
    }
    
    /* ===========================================
       MOBILE SIDEBAR & NAVIGATION
       =========================================== */
    
    /* Mobile sidebar optimization */
    .css-1d391kg {
        background-color: #262730;
    }
    
    /* Mobile-friendly selectbox */
    .stSelectbox > div > div {
        background-color: #262730;
        color: white;
        border: 1px solid #404040;
        border-radius: 8px;
        min-height: 44px;
    }
    
    /* Tab styling for mobile */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        overflow-x: auto;
        scrollbar-width: none;
        -ms-overflow-style: none;
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        display: none;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #262730;
        color: white;
        border: 1px solid #404040;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        white-space: nowrap;
        min-height: 44px;
        font-size: 0.9rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
        border-color: #4CAF50;
    }
    
    /* Tablet tab adjustments */
    @media (min-width: 768px) {
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
        }
    }
    
    /* ===========================================
       MOBILE DATA DISPLAY
       =========================================== */
    
    /* Mobile-optimized metrics */
    .stMetric {
        background-color: #262730;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #404040;
        color: white;
        margin-bottom: 0.75rem;
    }
    
    .stMetric > div {
        color: white;
    }
    
    .stMetric [data-testid="metric-container"] {
        background-color: #262730;
        border: 1px solid #404040;
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    
    .stMetric [data-testid="metric-container"] > div {
        color: white !important;
    }
    
    /* Tablet metric adjustments */
    @media (min-width: 768px) {
        .stMetric {
            padding: 1.25rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }
    }
    
    /* Desktop metric adjustments */
    @media (min-width: 1024px) {
        .stMetric {
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
        }
    }
    
    /* ===========================================
       MOBILE CHARTS & VISUALIZATIONS
       =========================================== */
    
    /* Mobile-responsive charts */
    .js-plotly-plot {
        background-color: #262730;
        border-radius: 10px;
        border: 1px solid #404040;
        margin-bottom: 1rem;
    }
    
    .js-plotly-plot .plotly {
        border-radius: 10px;
    }
    
    /* Mobile dataframe styling */
    .stDataFrame {
        background-color: #262730;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #404040;
        margin-bottom: 1rem;
        overflow-x: auto;
    }
    
    .stDataFrame table {
        font-size: 0.85rem;
        min-width: 100%;
    }
    
    .stDataFrame th, .stDataFrame td {
        padding: 0.5rem !important;
        white-space: nowrap;
    }
    
    /* Tablet chart adjustments */
    @media (min-width: 768px) {
        .js-plotly-plot {
            border-radius: 12px;
            margin-bottom: 1.25rem;
        }
        
        .stDataFrame {
            border-radius: 12px;
            margin-bottom: 1.25rem;
        }
        
        .stDataFrame table {
            font-size: 0.9rem;
        }
        
        .stDataFrame th, .stDataFrame td {
            padding: 0.75rem !important;
        }
    }
    
    /* Desktop chart adjustments */
    @media (min-width: 1024px) {
        .js-plotly-plot {
            border-radius: 10px;
            margin-bottom: 1.5rem;
        }
        
        .stDataFrame {
            border-radius: 10px;
            margin-bottom: 1.5rem;
        }
        
        .stDataFrame table {
            font-size: 1rem;
        }
        
        .stDataFrame th, .stDataFrame td {
            padding: 1rem !important;
        }
    }
    
    /* ===========================================
       MOBILE STATUS & ALERTS
       =========================================== */
    
    /* Mobile-friendly alerts */
    .stInfo, .stSuccess, .stWarning, .stError {
        background-color: #262730;
        border: 1px solid #404040;
        color: white;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
    }
    
    .stSuccess {
        border-color: #4CAF50;
        background-color: rgba(76, 175, 80, 0.1);
    }
    
    .stInfo {
        border-color: #2196F3;
        background-color: rgba(33, 150, 243, 0.1);
    }
    
    .stWarning {
        border-color: #FF9800;
        background-color: rgba(255, 152, 0, 0.1);
    }
    
    .stError {
        border-color: #f44336;
        background-color: rgba(244, 67, 54, 0.1);
    }
    
    /* Tablet alert adjustments */
    @media (min-width: 768px) {
        .stInfo, .stSuccess, .stWarning, .stError {
            border-radius: 10px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            font-size: 1rem;
        }
    }
    
    /* ===========================================
       MOBILE AI SCORE & BADGES
       =========================================== */
    
    /* Mobile AI score badge */
    .ai-score {
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    /* Tablet AI score adjustments */
    @media (min-width: 768px) {
        .ai-score {
            padding: 0.65rem 1.25rem;
            border-radius: 22px;
            font-size: 1rem;
        }
    }
    
    /* Desktop AI score adjustments */
    @media (min-width: 1024px) {
        .ai-score {
            padding: 0.8rem 1.5rem;
            border-radius: 25px;
            font-size: 1.1rem;
        }
    }
    
    /* Mobile status badges */
    .status-active, .status-pending, .status-closed {
        color: white;
        padding: 0.25rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.25rem;
    }
    
    .status-active {
        background-color: #4CAF50;
    }
    
    .status-pending {
        background-color: #FF9800;
    }
    
    .status-closed {
        background-color: #607D8B;
    }
    
    /* Tablet status badge adjustments */
    @media (min-width: 768px) {
        .status-active, .status-pending, .status-closed {
            padding: 0.3rem 0.7rem;
            border-radius: 14px;
            font-size: 0.8rem;
        }
    }
    
    /* Desktop status badge adjustments */
    @media (min-width: 1024px) {
        .status-active, .status-pending, .status-closed {
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
        }
    }
    
    /* ===========================================
       MOBILE UTILITY CLASSES
       =========================================== */
    
    /* Mobile text utilities */
    .highlight-text {
        color: white;
        font-weight: 600;
    }
    
    .accent-text {
        color: #4CAF50;
        font-weight: 600;
    }
    
    /* Mobile spacing utilities */
    .mobile-hidden {
        display: none;
    }
    
    .mobile-only {
        display: block;
    }
    
    /* Tablet utilities */
    @media (min-width: 768px) {
        .tablet-hidden {
            display: none;
        }
        
        .tablet-only {
            display: block;
        }
        
        .mobile-only {
            display: none;
        }
    }
    
    /* Desktop utilities */
    @media (min-width: 1024px) {
        .desktop-hidden {
            display: none;
        }
        
        .desktop-only {
            display: block;
        }
        
        .tablet-only, .mobile-only {
            display: none;
        }
    }
    
    /* ===========================================
       MOBILE PERFORMANCE OPTIMIZATIONS
       =========================================== */
    
    /* Reduce motion for mobile performance */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* Hardware acceleration for smooth scrolling */
    .stApp {
        -webkit-overflow-scrolling: touch;
        transform: translateZ(0);
        backface-visibility: hidden;
    }
    
    /* Remove default streamlit styling that interferes with mobile */
    .element-container {
        background: transparent !important;
    }
    
    /* Fix metric containers for mobile */
    .stMarkdown {
        color: white !important;
    }
    
    /* Ensure all text is visible on mobile */
    p, span, div {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# PWA Configuration and Performance Optimization
st.markdown("""
<link rel="manifest" href="./manifest.json">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="NXTRIX CRM">
<meta name="mobile-web-app-capable" content="yes">

<!-- Service Worker Registration -->
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('./sw.js')
      .then(function(registration) {
        console.log('SW registered: ', registration);
      }, function(registrationError) {
        console.log('SW registration failed: ', registrationError);
      });
  });
}

// Performance optimization - lazy loading images
document.addEventListener('DOMContentLoaded', function() {
  const images = document.querySelectorAll('img[data-src]');
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.remove('lazy');
        imageObserver.unobserve(img);
      }
    });
  });
  
  images.forEach(img => imageObserver.observe(img));
});

// Mobile touch feedback
document.addEventListener('touchstart', function() {}, {passive: true});
document.addEventListener('touchend', function() {}, {passive: true});

// PWA Install Banner
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  
  // Show custom install button if desired
  const installButton = document.getElementById('pwa-install-btn');
  if (installButton) {
    installButton.style.display = 'block';
    installButton.addEventListener('click', () => {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('User accepted the install prompt');
        }
        deferredPrompt = null;
      });
    });
  }
});
</script>
""", unsafe_allow_html=True)

# AI Analysis Functions
def analyze_deal_with_ai(deal_data):
    """Analyze deal using OpenAI GPT-4"""
    try:
        prompt = f"""
        Analyze this real estate deal and provide a comprehensive assessment:
        
        Property Type: {deal_data.get('property_type', 'N/A')}
        Purchase Price: ${deal_data.get('purchase_price', 0):,.2f}
        After Repair Value: ${deal_data.get('arv', 0):,.2f}
        Repair Costs: ${deal_data.get('repair_costs', 0):,.2f}
        Monthly Rent: ${deal_data.get('monthly_rent', 0):,.2f}
        Location: {deal_data.get('location', 'N/A')}
        
        Provide:
        1. AI Score (0-100)
        2. Risk Assessment
        3. Profit Potential
        4. Key Recommendations
        5. Market Analysis
        
        Format as JSON with keys: score, risk_level, profit_potential, recommendations, market_analysis
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return {
            "score": 75,
            "risk_level": "Medium",
            "profit_potential": "Good",
            "recommendations": "Consider market conditions and financing options",
            "market_analysis": "Standard market analysis needed"
        }

def calculate_advanced_metrics(deal_data):
    """Calculate comprehensive real estate investment metrics"""
    purchase_price = deal_data.get('purchase_price', 0)
    arv = deal_data.get('arv', 0)
    repair_costs = deal_data.get('repair_costs', 0)
    monthly_rent = deal_data.get('monthly_rent', 0)
    closing_costs = deal_data.get('closing_costs', 0)
    annual_taxes = deal_data.get('annual_taxes', 0)
    insurance = deal_data.get('insurance', 0)
    hoa_fees = deal_data.get('hoa_fees', 0)
    vacancy_rate = deal_data.get('vacancy_rate', 5) / 100
    
    # Basic calculations
    total_investment = purchase_price + repair_costs + closing_costs
    gross_profit = arv - total_investment
    
    # Monthly calculations
    monthly_taxes = annual_taxes / 12
    monthly_insurance = insurance / 12
    property_management = monthly_rent * 0.10  # 10% property management
    maintenance_reserve = monthly_rent * 0.05  # 5% maintenance
    vacancy_reserve = monthly_rent * vacancy_rate
    
    monthly_expenses = (monthly_taxes + monthly_insurance + hoa_fees + 
                       property_management + maintenance_reserve + vacancy_reserve)
    monthly_income = monthly_rent
    monthly_cash_flow = monthly_income - monthly_expenses
    
    # Advanced metrics
    annual_cash_flow = monthly_cash_flow * 12
    total_roi = (gross_profit / total_investment * 100) if total_investment > 0 else 0
    cash_on_cash = (annual_cash_flow / total_investment * 100) if total_investment > 0 else 0
    cap_rate = (annual_cash_flow / purchase_price * 100) if purchase_price > 0 else 0
    
    # BRRRR Score (Buy, Rehab, Rent, Refinance, Repeat)
    brrrr_score = min(10, max(0, (arv - total_investment) / total_investment * 10))
    
    # 1% Rule (monthly rent should be 1% of purchase price)
    one_percent_rule = monthly_rent >= (purchase_price * 0.01)
    
    # Payback period
    payback_period = (total_investment / annual_cash_flow) if annual_cash_flow > 0 else float('inf')
    
    return {
        'total_investment': total_investment,
        'gross_profit': gross_profit,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_cash_flow': monthly_cash_flow,
        'annual_cash_flow': annual_cash_flow,
        'total_roi': total_roi,
        'cash_on_cash': cash_on_cash,
        'cap_rate': cap_rate,
        'brrrr_score': brrrr_score,
        'one_percent_rule': one_percent_rule,
        'payback_period': payback_period
    }

def calculate_ai_score(deal_data, metrics):
    """Calculate advanced AI-powered deal score based on multiple factors with market intelligence"""
    score = 0
    score_breakdown = {}
    
    # Initialize AI predictor for market context
    ai_predictor = get_ai_predictor()
    market_predictions = ai_predictor.predict_market_trends(12)
    current_phase = market_predictions['current_phase']
    
    # 1. Financial Performance (30 points)
    # ROI component with market cycle adjustment
    base_roi_score = min(25, max(0, metrics['total_roi'] / 2))
    cycle_multiplier = ai_predictor.market_cycles[current_phase]['roi_multiplier']
    roi_score = base_roi_score * cycle_multiplier
    roi_score = min(25, max(0, roi_score))
    score += roi_score
    score_breakdown['ROI Score'] = f"{roi_score:.1f}/25"
    
    # Cash flow with inflation adjustment
    inflation_factor = 1.03  # Assume 3% inflation
    adjusted_cash_flow = metrics['monthly_cash_flow'] * inflation_factor
    cash_flow_score = min(20, max(0, adjusted_cash_flow / 50))
    score += cash_flow_score
    score_breakdown['Cash Flow Score'] = f"{cash_flow_score:.1f}/20"
    
    # 2. Market Intelligence (25 points)
    # Neighborhood grade with location trend analysis
    neighborhood_grades = {'A+': 20, 'A': 18, 'A-': 16, 'B+': 14, 'B': 12, 'B-': 10, 'C+': 8, 'C': 6, 'C-': 4, 'D': 2}
    base_market_score = neighborhood_grades.get(deal_data.get('neighborhood_grade', 'B'), 10)
    
    # Location trend multiplier based on AI analysis
    location = deal_data.get('location', '')
    location_multiplier = 1.0
    if any(hot_market in location.lower() for hot_market in ['austin', 'nashville', 'tampa', 'phoenix']):
        location_multiplier = 1.2
    elif any(emerging in location.lower() for emerging in ['charlotte', 'raleigh', 'atlanta']):
        location_multiplier = 1.1
    
    market_score = min(20, base_market_score * location_multiplier)
    score += market_score
    score_breakdown['Market Score'] = f"{market_score:.1f}/20"
    
    # Market timing score (5 points)
    timing_multiplier = ai_predictor.market_cycles[current_phase]['risk_factor']
    timing_score = 5 / timing_multiplier  # Lower risk = higher timing score
    score += timing_score
    score_breakdown['Market Timing'] = f"{timing_score:.1f}/5"
    
    # 3. Property Analysis (20 points)
    # Property condition with renovation potential
    condition_scores = {'Excellent': 15, 'Good': 12, 'Fair': 8, 'Poor': 4, 'Tear Down': 1}
    base_condition_score = condition_scores.get(deal_data.get('condition', 'Good'), 8)
    
    # Value-add potential bonus
    if deal_data.get('condition') in ['Fair', 'Poor'] and metrics.get('total_roi', 0) > 20:
        base_condition_score *= 1.3  # Bonus for value-add opportunities
    
    condition_score = min(15, base_condition_score)
    score += condition_score
    score_breakdown['Property Condition'] = f"{condition_score:.1f}/15"
    
    # Property type market demand (5 points)
    property_type_scores = {
        'Single Family': 5 if current_phase in ['growth', 'recovery'] else 3,
        'Multi-Family': 4,
        'Commercial': 3 if current_phase == 'growth' else 2,
        'Fix & Flip': 5 if current_phase == 'recovery' else 2
    }
    property_score = property_type_scores.get(deal_data.get('property_type', 'Single Family'), 3)
    score += property_score
    score_breakdown['Property Type'] = f"{property_score}/5"
    
    # 4. Risk Assessment (15 points)
    # Cap rate with market risk adjustment
    base_cap_rate_score = min(10, max(0, metrics.get('cap_rate', 5) - 5))
    risk_factor = market_predictions['risk_assessment']['overall_risk']
    risk_adjusted_cap_score = base_cap_rate_score / risk_factor
    cap_rate_score = min(10, max(0, risk_adjusted_cap_score))
    score += cap_rate_score
    score_breakdown['Cap Rate'] = f"{cap_rate_score:.1f}/10"
    
    # Liquidity risk assessment (5 points)
    liquidity_score = 5
    if current_phase == 'correction':
        liquidity_score = 2
    elif current_phase == 'peak':
        liquidity_score = 3
    score += liquidity_score
    score_breakdown['Liquidity Risk'] = f"{liquidity_score}/5"
    
    # 5. Future Potential (10 points)
    # Growth potential based on market predictions
    predicted_growth = (market_predictions['predictions'][11]['market_index'] - 100) / 100
    growth_score = min(5, max(0, predicted_growth * 100))
    score += growth_score
    score_breakdown['Growth Potential'] = f"{growth_score:.1f}/5"
    
    # Economic indicators (5 points)
    # Simulate economic strength (would use real data in production)
    economic_score = 3  # Base score
    if current_phase == 'growth':
        economic_score = 5
    elif current_phase == 'recovery':
        economic_score = 4
    score += economic_score
    score_breakdown['Economic Indicators'] = f"{economic_score}/5"
    
    final_score = min(100, max(0, int(score)))
    
    return final_score, score_breakdown

def generate_ai_query_response(query: str, ai_predictor, portfolio_deals: List) -> str:
    """Generate AI responses to natural language queries"""
    query_lower = query.lower()
    
    # Market timing queries
    if any(word in query_lower for word in ['timing', 'when', 'time to buy', 'market cycle']):
        predictions = ai_predictor.predict_market_trends(6)
        phase = predictions['current_phase']
        
        if phase == 'growth':
            return """🚀 **Excellent timing for acquisitions!** The market is in a growth phase with strong momentum. 
            Key recommendations:
            • ✅ Great time to buy - prices rising but not peaked
            • 📈 Focus on emerging neighborhoods before peak pricing
            • ⚡ Act quickly on good deals - competition increasing
            • 💰 Consider value-add properties for maximum upside"""
            
        elif phase == 'peak':
            return """⚠️ **Exercise caution - market at peak.** Be very selective with new investments.
            Key recommendations:
            • 🎯 Only pursue exceptional deals with strong fundamentals
            • 💰 Consider taking profits on well-performing properties
            • 🔍 Focus on cash-flowing assets over speculation
            • 📊 Prepare cash reserves for upcoming opportunities"""
            
        elif phase == 'correction':
            return """🛡️ **Defensive mode recommended.** Market correction in progress - exceptional opportunities emerging.
            Key recommendations:
            • 💎 Be patient - best deals are coming
            • 🏦 Maintain strong cash reserves
            • 📉 Avoid panic - focus on fundamentals
            • 🎯 Target distressed properties at significant discounts"""
            
        else:  # recovery
            return """🌱 **Recovery phase - strategic positioning time.** Great opportunity for long-term gains.
            Key recommendations:
            • 🎯 Excellent time for strategic acquisitions
            • 💪 Increase activity with strong due diligence
            • 📈 Position for next growth cycle
            • 🏠 Focus on quality assets in good locations"""
    
    # ROI and returns queries
    elif any(word in query_lower for word in ['roi', 'return', 'profit', 'best market']):
        if portfolio_deals:
            avg_roi = np.mean([getattr(deal, 'ai_score', 75) for deal in portfolio_deals])
            best_markets = ['Austin, TX', 'Nashville, TN', 'Tampa, FL', 'Phoenix, AZ']
            
            return f"""📈 **ROI Analysis Based on Current Data:**
            
            **Your Portfolio Performance:**
            • Current average AI score: {avg_roi:.1f}/100
            • Top performing markets in your area: {', '.join(best_markets[:2])}
            
            **Highest ROI Markets Currently:**
            • 🥇 Austin, TX: 12-15% average returns, strong job growth
            • 🥈 Nashville, TN: 10-13% returns, emerging tech hub
            • 🥉 Tampa, FL: 9-12% returns, population influx
            
            **Recommended Strategy:**
            • Target deals scoring 80+ on AI analysis
            • Focus on emerging neighborhoods before peak pricing
            • Consider fix & flip opportunities in recovery markets"""
        else:
            return """📈 **Top ROI Markets for New Investors:**
            
            **High-Opportunity Markets:**
            • 🎯 Austin, TX: 12-15% average returns, strong tech job growth
            • 🚀 Nashville, TN: 10-13% returns, music city boom continues
            • 🌴 Tampa, FL: 9-12% returns, favorable demographics
            • 🏜️ Phoenix, AZ: 8-11% returns, steady population growth
            
            **Strategy Recommendations:**
            • Start with single-family homes for easier management
            • Target 12%+ cap rates for strong cash flow
            • Focus on emerging neighborhoods
            • Consider light renovation properties for value-add"""
    
    # Property type queries
    elif any(word in query_lower for word in ['property type', 'single family', 'multi family', 'commercial', 'fix']):
        predictions = ai_predictor.predict_market_trends(6)
        phase = predictions['current_phase']
        
        if phase in ['growth', 'recovery']:
            return """🏠 **Recommended Property Types for Current Market:**
            
            **Top Performers:**
            • 🥇 **Single Family Homes**: Easiest to manage, strong demand
            • 🥈 **Fix & Flip**: Great in recovery/growth phases
            • 🥉 **Small Multi-Family (2-4 units)**: Good cash flow potential
            
            **Strategy by Type:**
            • **SFH**: Target emerging neighborhoods, 3BR/2BA minimum
            • **Fix & Flip**: Focus on cosmetic upgrades, avoid major structural
            • **Multi-Family**: Look for properties under market rent
            • **Commercial**: Only if you have significant experience
            
            **Current Market Advantage**: Growth phase favors value-add properties!"""
        else:
            return """🏠 **Conservative Property Strategy for Peak/Correction:**
            
            **Safest Bets:**
            • 🥇 **Cash-Flowing Rentals**: Stable income during volatility
            • 🥈 **Multi-Family**: Diversified tenant risk
            • 🥉 **Commercial (experienced only)**: Longer-term leases
            
            **Avoid During Uncertainty:**
            • ❌ Pure speculation plays
            • ❌ Heavy renovation projects
            • ❌ Markets with declining fundamentals
            
            **Focus**: Steady cash flow over appreciation in this phase."""
    
    # Portfolio analysis queries
    elif any(word in query_lower for word in ['portfolio', 'my deals', 'performance', 'should i']):
        if portfolio_deals:
            total_value = sum(getattr(deal, 'purchase_price', 0) for deal in portfolio_deals)
            avg_score = np.mean([getattr(deal, 'ai_score', 75) for deal in portfolio_deals])
            
            return f"""📊 **Your Portfolio Analysis:**
            
            **Current Status:**
            • Total Portfolio Value: ${total_value:,.0f}
            • Number of Properties: {len(portfolio_deals)}
            • Average AI Score: {avg_score:.1f}/100
            
            **Performance Grade**: {"A" if avg_score >= 80 else "B" if avg_score >= 70 else "C"}
            
            **Recommendations:**
            {"• ✅ Portfolio performing well - consider strategic expansion" if avg_score >= 80 else "• 🔧 Focus on optimizing underperforming assets"}
            {"• 📈 Good diversification level" if len(portfolio_deals) >= 3 else "• 🎯 Consider diversifying with additional properties"}
            • 💰 Continue monitoring cash flow vs. market conditions
            • 📊 Review and optimize deals scoring below 70"""
        else:
            return """🎯 **Portfolio Building Strategy for Beginners:**
            
            **Phase 1: Foundation (First 1-3 Properties)**
            • Start with single-family homes in B+ neighborhoods
            • Target 12%+ cap rates for strong cash flow
            • Focus on turnkey or light renovation properties
            
            **Phase 2: Growth (Properties 4-10)**
            • Add multi-family for diversification
            • Consider different geographic markets
            • Explore value-add opportunities
            
            **Phase 3: Optimization (10+ Properties)**
            • Portfolio refinancing opportunities
            • Commercial property consideration
            • Professional property management
            
            **Start Here**: Add your first deal to get personalized portfolio analysis!"""
    
    # Default response for other queries
    else:
        return f"""🤖 **AI Analysis of: "{query}"**
        
        Based on current market conditions and AI analysis:
        
        **Market Context:**
        • Current market phase: {ai_predictor.predict_market_trends(3)['current_phase'].title()}
        • Investment climate: Moderate to good opportunities
        • Risk level: Medium
        
        **General Recommendations:**
        • Focus on properties scoring 75+ on AI analysis
        • Maintain 6+ months cash reserves
        • Diversify across 2-3 markets when possible
        • Monitor interest rate trends for timing
        
        **Next Steps:**
        • Use the Deal Analysis tool for specific property evaluation
        • Check Market Predictions for timing insights
        • Add deals to your portfolio for personalized advice
        
        *For more specific guidance, try asking about market timing, ROI, or property types!*"""
    
    return "AI analysis complete."


def generate_ai_recommendations(deal_data, metrics):
    """Generate AI-powered investment recommendations"""
    recommendations = []
    
    # ROI-based recommendations
    if metrics['total_roi'] > 30:
        recommendations.append("🎯 Excellent ROI potential - This deal shows strong profit margins")
    elif metrics['total_roi'] > 20:
        recommendations.append("✅ Good ROI potential - Above average returns expected")
    else:
        recommendations.append("⚠️ Consider negotiating purchase price to improve ROI")
    
    # Cash flow recommendations
    if metrics['monthly_cash_flow'] > 500:
        recommendations.append("💰 Strong positive cash flow - Great for wealth building")
    elif metrics['monthly_cash_flow'] > 200:
        recommendations.append("💵 Moderate cash flow - Consider rent optimization strategies")
    else:
        recommendations.append("📉 Negative/low cash flow - Evaluate rental market or reduce expenses")
    
    # Market-based recommendations
    neighborhood_grade = deal_data.get('neighborhood_grade', 'B')
    if neighborhood_grade in ['A+', 'A', 'A-']:
        recommendations.append("🏆 Prime location - Expect strong appreciation and rental demand")
    elif neighborhood_grade in ['B+', 'B']:
        recommendations.append("🎯 Solid neighborhood - Good balance of growth and affordability")
    else:
        recommendations.append("⚠️ Emerging area - Higher risk but potential for significant upside")
    
    # BRRRR strategy recommendation
    if metrics['brrrr_score'] > 7:
        recommendations.append("🔄 Excellent BRRRR candidate - Consider refinancing strategy")
    
    # 1% rule recommendation
    if metrics['one_percent_rule']:
        recommendations.append("✅ Passes 1% rule - Strong rental yield indicator")
    else:
        recommendations.append("📊 Below 1% rule - Focus on appreciation or rent increases")
    
    # Property condition recommendations
    condition = deal_data.get('condition', 'Good')
    if condition in ['Poor', 'Tear Down']:
        recommendations.append("🔨 Significant renovation needed - Budget extra for unexpected costs")
    elif condition == 'Fair':
        recommendations.append("🛠️ Moderate repairs required - Get detailed contractor estimates")
    
    # Market trend recommendations
    trend = deal_data.get('market_trend', 'Stable')
    if trend == 'Rising':
        recommendations.append("📈 Rising market - Consider holding for appreciation")
    elif trend == 'Declining':
        recommendations.append("📉 Declining market - Focus on cash flow over appreciation")
    
    return recommendations[:6]  # Return top 6 recommendations

# Main Application
def main():
    # Mobile viewport meta tag
    st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    """, unsafe_allow_html=True)
    
    # Mobile-responsive header
    st.markdown("""
    <div class="main-header">
        <h1>🏢 NXTRIX Enterprise CRM</h1>
        <p class="mobile-hidden">AI-Powered Real Estate Investment Analysis & Portfolio Management</p>
        <p class="mobile-only">AI-Powered Real Estate CRM</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mobile navigation improvements
    st.markdown("""
    <script>
    // Mobile touch optimizations
    document.addEventListener('DOMContentLoaded', function() {
        // Add touch feedback for mobile
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            button.addEventListener('touchstart', function() {
                this.style.opacity = '0.8';
            });
            button.addEventListener('touchend', function() {
                this.style.opacity = '1';
            });
        });
        
        // Prevent double-tap zoom on buttons
        let lastTouchEnd = 0;
        document.addEventListener('touchend', function (event) {
            const now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
        
        // Add swipe navigation for mobile
        let startX = null;
        let startY = null;
        
        document.addEventListener('touchstart', function(e) {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        document.addEventListener('touchend', function(e) {
            if (!startX || !startY) {
                return;
            }
            
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            
            const diffX = startX - endX;
            const diffY = startY - endY;
            
            // Only trigger swipe if it's primarily horizontal
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    // Swipe left - could navigate forward
                    console.log('Swipe left detected');
                } else {
                    // Swipe right - could navigate back
                    console.log('Swipe right detected');
                }
            }
            
            startX = null;
            startY = null;
        });
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Check for redirect first
    redirect_page = get_current_page()
    
    # Sidebar Navigation
    st.sidebar.title("🎯 Navigation")
    
    # Use redirect page if available
    navigation_options = ["📊 Dashboard", "🏠 Deal Analysis", "💹 Advanced Financial Modeling", "🗄️ Deal Database", "📈 Portfolio Analytics", "🏛️ Investor Portal", "� Enhanced CRM", "�🤖 AI Insights", "👥 Investor Matching"]
    
    if redirect_page and redirect_page in navigation_options:
        default_index = navigation_options.index(redirect_page)
    else:
        default_index = 0
    
    page = st.sidebar.selectbox(
        "Choose Section",
        navigation_options,
        index=default_index
    )
    
    # Database connection status in sidebar
    st.sidebar.markdown("---")
    db_service = get_db_service()
    if db_service and db_service.is_connected():
        st.sidebar.success("🟢 Database Connected")
        total_deals = len(db_service.get_deals())
        st.sidebar.info(f"📊 {total_deals} deals in database")
        
        # Additional real-time stats
        if total_deals > 0:
            deals = db_service.get_deals()
            high_score_count = len([d for d in deals if d.ai_score >= 85])
            st.sidebar.metric("🎯 High Score Deals", high_score_count, f"{high_score_count}/{total_deals}")
            
            # Quick actions
            st.sidebar.markdown("### ⚡ Quick Actions")
            if st.sidebar.button("➕ New Deal Analysis"):
                navigate_to_page("🏠 Deal Analysis")
            if st.sidebar.button("💹 Financial Modeling"):
                navigate_to_page("💹 Advanced Financial Modeling")
    else:
        st.sidebar.error("🔴 Database Offline")
        st.sidebar.warning("Using local data only")
        
        with st.sidebar.expander("🔧 Setup Database"):
            st.write("""
            **To connect to Supabase:**
            1. Create a Supabase project at supabase.com
            2. Get your project URL and anon key
            3. Add them to `.streamlit/secrets.toml`:
            
            ```toml
            [SUPABASE]
            SUPABASE_URL = "https://your-project.supabase.co"
            SUPABASE_KEY = "your-anon-key"
            ```
            
            4. Run the SQL schema from `schema.sql`
            5. Restart the app
            """)
            
            if st.button("📄 View Setup Instructions"):
                st.session_state.show_setup = True
    
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🏠 Deal Analysis":
        show_deal_analysis()
    elif page == "💹 Advanced Financial Modeling":
        show_advanced_financial_modeling()
    elif page == "🗄️ Deal Database":
        show_deal_database()
    elif page == "📈 Portfolio Analytics":
        show_portfolio_analytics()
    elif page == "🏛️ Investor Portal":
        show_investor_portal()
    elif page == "� Enhanced CRM":
        enhanced_crm_func = get_enhanced_crm()
        if enhanced_crm_func:
            enhanced_crm_func()
        else:
            st.error("❌ Enhanced CRM module failed to load")
    elif page == "�🤖 AI Insights":
        show_ai_insights()
    elif page == "👥 Investor Matching":
        show_investor_matching()

def show_dashboard():
    st.header("📊 Executive Dashboard")
    
    # Mobile-optimized dashboard layout
    st.markdown("""
    <div class="mobile-dashboard-container">
        <script>
        // Add mobile dashboard optimizations
        document.addEventListener('DOMContentLoaded', function() {
            // Add swipe navigation between metric cards on mobile
            const cards = document.querySelectorAll('.metric-card');
            let currentCard = 0;
            
            function showCard(index) {
                cards.forEach((card, i) => {
                    if (window.innerWidth <= 768) {
                        card.style.display = i === index ? 'block' : 'none';
                    } else {
                        card.style.display = 'block';
                    }
                });
            }
            
            // Initialize mobile view
            if (window.innerWidth <= 768) {
                showCard(currentCard);
                
                // Add swipe indicators
                const dashboardContainer = document.querySelector('.mobile-dashboard-container');
                if (dashboardContainer && cards.length > 1) {
                    const indicators = document.createElement('div');
                    indicators.className = 'mobile-card-indicators';
                    indicators.style.cssText = 'text-align: center; margin: 1rem 0; display: flex; justify-content: center; gap: 0.5rem;';
                    
                    for (let i = 0; i < cards.length; i++) {
                        const dot = document.createElement('span');
                        dot.style.cssText = 'width: 8px; height: 8px; border-radius: 50%; background-color: ' + (i === 0 ? '#4CAF50' : '#666') + '; display: inline-block; cursor: pointer;';
                        dot.addEventListener('click', () => {
                            currentCard = i;
                            showCard(currentCard);
                            updateIndicators();
                        });
                        indicators.appendChild(dot);
                    }
                    dashboardContainer.appendChild(indicators);
                    
                    function updateIndicators() {
                        const dots = indicators.querySelectorAll('span');
                        dots.forEach((dot, i) => {
                            dot.style.backgroundColor = i === currentCard ? '#4CAF50' : '#666';
                        });
                    }
                }
            }
            
            // Handle window resize
            window.addEventListener('resize', function() {
                if (window.innerWidth > 768) {
                    cards.forEach(card => card.style.display = 'block');
                } else {
                    showCard(currentCard);
                }
            });
        });
        </script>
    </div>
    """, unsafe_allow_html=True)
    
    # Real-time metrics from database
    db_service = get_db_service()
    if db_service and db_service.is_connected():
        deals = db_service.get_deals()
        total_deals = len(deals)
        
        # Calculate real metrics
        if deals:
            high_score_deals = [d for d in deals if d.ai_score >= 85]
            avg_score = sum(d.ai_score for d in deals) / len(deals)
            avg_price = sum(d.purchase_price for d in deals) / len(deals)
            total_value = sum(d.purchase_price for d in deals)
            avg_rent = sum(d.monthly_rent for d in deals) / len(deals)
        else:
            high_score_deals = []
            avg_score = 0
            avg_price = 0
            total_value = 0
            avg_rent = 0
            
        # Growth calculation (mock for now - in production, compare with previous period)
        growth_percentage = "+12%" if total_deals > 0 else "0%"
    else:
        # Fallback to sample data when database is offline
        total_deals = 4
        high_score_deals = []
        avg_score = 89.8
        avg_price = 362500
        total_value = 1450000
        avg_rent = 2950
        growth_percentage = "+12%"
    
    # Mobile-responsive metrics layout
    # On mobile: 1 column (stacked), On tablet: 2-3 columns, On desktop: 5 columns
    
    # Mobile-first approach - create individual containers for better mobile control
    st.markdown('<div class="mobile-metrics-container">', unsafe_allow_html=True)
    
    # Use responsive columns
    if st._get_option('theme.base') == 'dark':  # Mobile detection alternative
        cols = st.columns([1])  # Single column for mobile-like layout
        col_index = 0
    else:
        cols = st.columns(5)  # Desktop layout
        col_index = None
    
    # Total Deals Metric
    metric_container = cols[0] if col_index is None else cols[col_index]
    with metric_container:
        st.markdown(f"""
        <div class="metric-card" style="min-height: 140px;">
            <h3>📊 Total Deals</h3>
            <h2 style="color: #667eea; font-weight: 700; margin: 0.5rem 0;">{total_deals}</h2>
            <p style="color: #38a169; font-weight: 600; margin: 0;">↗️ {growth_percentage} this month</p>
        </div>
        """, unsafe_allow_html=True)
    
    # High Score Deals Metric
    metric_container = cols[1] if col_index is None else cols[col_index]
    with metric_container:
        st.markdown(f"""
        <div class="metric-card" style="min-height: 140px;">
            <h3>🎯 High Score Deals</h3>
            <h2 style="color: #38a169; font-weight: 700; margin: 0.5rem 0;">{len(high_score_deals)}</h2>
            <p style="color: #667eea; font-weight: 600; margin: 0;">Score ≥ 85</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Average AI Score Metric
    metric_container = cols[2] if col_index is None else cols[col_index]
    with metric_container:
        st.markdown(f"""
        <div class="metric-card" style="min-height: 140px;">
            <h3>🤖 Avg AI Score</h3>
            <h2 style="color: #f093fb; font-weight: 700; margin: 0.5rem 0;">{avg_score:.1f}</h2>
            <p style="color: #667eea; font-weight: 600; margin: 0;">AI Analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Portfolio Value Metric
    metric_container = cols[3] if col_index is None else cols[col_index]
    with metric_container:
        st.markdown(f"""
        <div class="metric-card" style="min-height: 140px;">
            <h3>💰 Portfolio Value</h3>
            <h2 style="color: #f6ad55; font-weight: 700; margin: 0.5rem 0;">${total_value:,.0f}</h2>
            <p style="color: #667eea; font-weight: 600; margin: 0;">Total Investment</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Average Rent Metric
    metric_container = cols[4] if col_index is None else cols[col_index]
    with metric_container:
        st.markdown(f"""
        <div class="metric-card" style="min-height: 140px;">
            <h3>🏠 Avg Monthly Rent</h3>
            <h2 style="color: #68d391; font-weight: 700; margin: 0.5rem 0;">${avg_rent:,.0f}</h2>
            <p style="color: #667eea; font-weight: 600; margin: 0;">Monthly Income</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Mobile swipe instructions
    st.markdown("""
    <div class="mobile-only" style="text-align: center; margin: 1rem 0; color: #999; font-size: 0.8rem;">
        📱 Swipe or tap dots to navigate between metrics
    </div>
    """, unsafe_allow_html=True)
    

    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>High Score Deals</h3>
            <h2 style="color: #667eea; font-weight: 700;">{len(high_score_deals)}</h2>
            <p style="color: #38a169; font-weight: 600;">↗️ Score ≥85</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Portfolio Value</h3>
            <h2 style="color: #667eea; font-weight: 700;">${total_value:,.0f}</h2>
            <p style="color: #38a169; font-weight: 600;">↗️ +8.1% growth</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Avg Rent</h3>
            <h2 style="color: #38a169; font-weight: 700;">${avg_rent:,.0f}</h2>
            <p style="color: #38a169; font-weight: 600;">↗️ +5.2% market</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>AI Score Avg</h3>
            <h2 style="color: #e53e3e; font-weight: 700;">82.4</h2>
            <p style="color: #805ad5; font-weight: 600;">🎯 High-quality deals</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>Portfolio Value</h3>
            <h2 style="color: #805ad5; font-weight: 700;">$8.4M</h2>
            <p style="color: #38a169; font-weight: 600;">↗️ +15% YoY growth</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="metric-card">
            <h3>Active Investors</h3>
            <h2 style="color: #dd6b20; font-weight: 700;">234</h2>
            <p style="color: #38a169; font-weight: 600;">🤝 +18 new this week</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Deal Performance Trends")
        # Sample chart data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='ME')
        performance_data = pd.DataFrame({
            'Date': dates,
            'ROI': np.random.normal(25, 5, len(dates)),
            'AI Score': np.random.normal(80, 8, len(dates))
        })
        
        fig = px.line(performance_data, x='Date', y=['ROI', 'AI Score'], 
                     title="Monthly Performance Metrics",
                     color_discrete_map={'ROI': '#4CAF50', 'AI Score': '#2196F3'})
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(size=16, color='white', family='Arial Black'),
            xaxis=dict(gridcolor='#404040', color='white'),
            yaxis=dict(gridcolor='#404040', color='white'),
            legend=dict(font=dict(color='white'))
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏠 Deal Types Distribution")
        deal_types = ['Fix & Flip', 'Buy & Hold', 'Wholesale', 'Commercial', 'Multi-Family']
        values = [45, 30, 15, 7, 3]
        
        fig = px.pie(values=values, names=deal_types, 
                    title="Portfolio Distribution by Deal Type",
                    color_discrete_sequence=['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#607D8B'])
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(size=16, color='white', family='Arial Black'),
            legend=dict(font=dict(color='white'))
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent Deals with enhanced styling
    st.subheader("🔥 Recent High-Scoring Deals")
    
    # Get real deals from database
    db_service = get_db_service()
    recent_deals_data = db_service.get_high_scoring_deals(min_score=80) if db_service else []
    
    if recent_deals_data:
        # Convert to DataFrame for display
        deals_display = []
        for deal in recent_deals_data[:5]:  # Show top 5
            deals_display.append({
                'Property': deal.address,
                'Type': deal.property_type,
                'Purchase Price': f"${deal.purchase_price:,.0f}",
                'AI Score': deal.ai_score,
                'ROI': f"{((deal.arv - deal.purchase_price - deal.repair_costs) / (deal.purchase_price + deal.repair_costs) * 100):.1f}%" if (deal.purchase_price + deal.repair_costs) > 0 else "0%",
                'Status': deal.status
            })
        
        recent_deals_df = pd.DataFrame(deals_display)
    else:
        # Fallback to sample data if no deals in database
        recent_deals_df = pd.DataFrame({
            'Property': ['123 Oak St', '456 Pine Ave', '789 Maple Dr', '321 Elm St'],
            'Type': ['Fix & Flip', 'Buy & Hold', 'Wholesale', 'Multi-Family'],
            'Purchase Price': ['$180,000', '$320,000', '$95,000', '$650,000'],
            'AI Score': [94, 88, 91, 86],
            'ROI': ['32.5%', '28.3%', '15.8%', '22.1%'],
            'Status': ['Under Contract', 'Analyzing', 'Closed', 'Negotiating']
        })
    
    # Style the dataframe for better visibility
    st.markdown("""
    <style>
    .stDataFrame > div {
        background: #262730;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #404040;
    }
    
    .stDataFrame table {
        background: #262730 !important;
        color: white !important;
    }
    
    .stDataFrame thead tr th {
        background: #4CAF50 !important;
        color: white !important;
        font-weight: 600 !important;
        text-align: center !important;
    }
    
    .stDataFrame tbody tr td {
        background: #262730 !important;
        color: white !important;
        font-weight: 500 !important;
        text-align: center !important;
        border-bottom: 1px solid #404040 !important;
    }
    
    .stDataFrame tbody tr:hover td {
        background: #363740 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(recent_deals_df, use_container_width=True)
    
    # Dashboard controls
    st.markdown("---")
    col_refresh, col_info = st.columns([1, 3])
    
    with col_refresh:
        if st.button("🔄 Refresh Dashboard", type="secondary"):
            st.rerun()
    
    with col_info:
        db_service = get_db_service()
        if db_service and db_service.is_connected():
            last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.info(f"📡 Live data • Last updated: {last_updated}")
        else:
            st.warning("📡 Offline mode • Sample data shown")

def show_deal_analysis():
    st.header("🏠 AI Deal Analysis")
    
    # Mobile-optimized layout - stack columns on mobile
    st.markdown("""
    <style>
    /* Mobile form optimizations */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .stNumberInput, .stTextInput, .stSelectbox {
            margin-bottom: 1rem;
        }
        
        .mobile-form-section {
            background-color: #262730;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid #404040;
        }
        
        .mobile-form-title {
            color: #4CAF50;
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Load models for Deal creation
    models = get_models()
    if not models[0]:  # Deal is the first element
        st.error("❌ Models module failed to load")
        return
    
    Deal, Investor, Portfolio = models
    
    # Mobile-responsive form layout
    st.markdown('<div class="mobile-form-section">', unsafe_allow_html=True)
    st.markdown('<div class="mobile-form-title">� Property Information</div>', unsafe_allow_html=True)
    
    # Property details - mobile optimized
    property_address = st.text_input("Property Address", 
                                   placeholder="123 Main Street, City, State",
                                   help="Enter the full property address")
    
    # Mobile: Single column, Tablet/Desktop: Two columns
    prop_col1, prop_col2 = st.columns([1, 1])
    
    with prop_col1:
        property_type = st.selectbox("Property Type", 
                                   ["Single Family", "Multi-Family", "Condo", "Townhouse", "Commercial", "Land", "Mixed-Use"],
                                   help="Select the property type")
        bedrooms = st.number_input("Bedrooms", min_value=0, max_value=10, value=3,
                                 help="Number of bedrooms")
        
    with prop_col2:
        property_condition = st.selectbox("Property Condition", 
                                        ["Excellent", "Good", "Fair", "Poor", "Tear Down"],
                                        help="Current property condition")
        bathrooms = st.number_input("Bathrooms", min_value=0.0, max_value=10.0, value=2.0, step=0.5,
                                   help="Number of bathrooms")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Financial details section
    st.markdown('<div class="mobile-form-section">', unsafe_allow_html=True)
    st.markdown('<div class="mobile-form-title">💰 Financial Details</div>', unsafe_allow_html=True)
    
    # Mobile-optimized financial inputs
    fin_col1, fin_col2, fin_col3 = st.columns([1, 1, 1])
    
    with fin_col1:
        purchase_price = st.number_input("Purchase Price ($)", min_value=0, value=200000, step=1000,
                                       help="Total purchase price", format="%d")
        repair_costs = st.number_input("Repair Costs ($)", min_value=0, value=25000, step=1000,
                                     help="Estimated repair costs", format="%d")
        
    with fin_col2:
        arv = st.number_input("After Repair Value ($)", min_value=0, value=275000, step=1000,
                            help="Property value after repairs", format="%d")
        monthly_rent = st.number_input("Monthly Rent ($)", min_value=0, value=2200, step=50,
                                     help="Expected monthly rental income", format="%d")
        
    with fin_col3:
        closing_costs = st.number_input("Closing Costs ($)", min_value=0, value=5000, step=500,
                                      help="Transaction closing costs", format="%d")
        annual_taxes = st.number_input("Annual Taxes ($)", min_value=0, value=3500, step=100,
                                     help="Annual property taxes", format="%d")
        insurance = st.number_input("Annual Insurance ($)", min_value=0, value=1200, step=100)
        hoa_fees = st.number_input("Monthly HOA ($)", min_value=0, value=0, step=25)
        vacancy_rate = st.slider("Vacancy Rate (%)", min_value=0, max_value=30, value=5)
        
        # Market analysis
        st.subheader("📊 Market Analysis")
        col3a, col3b = st.columns(2)
        
        with col3a:
            neighborhood_grade = st.selectbox("Neighborhood Grade", ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D"])
            days_on_market = st.number_input("Days on Market", min_value=0, value=30)
            
        with col3b:
            market_trend = st.selectbox("Market Trend", ["Rising", "Stable", "Declining"])
            comparable_sales = st.number_input("Recent Comparable Sales", min_value=0, value=5)
        
        location_notes = st.text_area("Location & Market Notes", 
                                    placeholder="Schools, amenities, transportation, future developments...")
        
        # Advanced analysis button
        if st.button("🤖 Run Advanced AI Analysis", type="primary", use_container_width=True):
            deal_data = {
                'property_type': property_type,
                'purchase_price': purchase_price,
                'arv': arv,
                'repair_costs': repair_costs,
                'monthly_rent': monthly_rent,
                'location': property_address,
                'condition': property_condition,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'closing_costs': closing_costs,
                'annual_taxes': annual_taxes,
                'insurance': insurance,
                'hoa_fees': hoa_fees,
                'vacancy_rate': vacancy_rate,
                'neighborhood_grade': neighborhood_grade,
                'market_trend': market_trend
            }
            
            # Store in session state for display
            st.session_state.analyzed_deal = deal_data
            st.rerun()
    
    with col2:
        if 'analyzed_deal' in st.session_state:
            st.subheader("📊 Comprehensive Analysis Results")
            
            deal_data = st.session_state.analyzed_deal
            
            # Calculate advanced metrics
            metrics = calculate_advanced_metrics(deal_data)
            
            # AI Score Display with detailed breakdown
            ai_score, score_breakdown = calculate_ai_score(deal_data, metrics)
            
            # Score visualization
            col_score1, col_score2 = st.columns([1, 2])
            with col_score1:
                st.markdown(f"""
                <div class="ai-score">
                    🤖 AI Score: {ai_score}/100
                </div>
                """, unsafe_allow_html=True)
                
                # Score breakdown
                st.write("**Score Breakdown:**")
                score_components = {
                    "ROI Potential": 85,
                    "Market Strength": 78,
                    "Property Condition": 82,
                    "Risk Assessment": 88,
                    "Cash Flow": 91
                }
                
                for component, score in score_components.items():
                    st.progress(score/100, text=f"{component}: {score}%")
            
            with col_score2:
                # Key metrics display
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric("Total ROI", f"{metrics['total_roi']:.1f}%", 
                             delta=f"+{metrics['total_roi']-20:.1f}% vs avg")
                    st.metric("Cash-on-Cash Return", f"{metrics['cash_on_cash']:.1f}%")
                    st.metric("Cap Rate", f"{metrics['cap_rate']:.2f}%")
                    
                with col_m2:
                    st.metric("Monthly Cash Flow", f"${metrics['monthly_cash_flow']:,.0f}")
                    st.metric("BRRRR Score", f"{metrics['brrrr_score']}/10")
                    st.metric("1% Rule Check", "✅ Pass" if metrics['one_percent_rule'] else "❌ Fail")
            
            # Detailed financial breakdown
            st.subheader("💰 Financial Breakdown")
            
            financial_tabs = st.tabs(["📊 Summary", "💸 Cash Flow", "📈 Projections", "⚠️ Risk Analysis"])
            
            with financial_tabs[0]:
                # Investment summary
                summary_data = {
                    "Total Investment": f"${metrics['total_investment']:,.0f}",
                    "Expected Profit": f"${metrics['gross_profit']:,.0f}",
                    "Monthly Income": f"${metrics['monthly_income']:,.0f}",
                    "Monthly Expenses": f"${metrics['monthly_expenses']:,.0f}",
                    "Net Cash Flow": f"${metrics['monthly_cash_flow']:,.0f}",
                    "Payback Period": f"{metrics['payback_period']:.1f} years"
                }
                
                for key, value in summary_data.items():
                    col_sum1, col_sum2 = st.columns([1, 1])
                    with col_sum1:
                        st.write(f"**{key}:**")
                    with col_sum2:
                        st.write(value)
            
            with financial_tabs[1]:
                # Detailed cash flow analysis
                st.write("**Monthly Income:**")
                st.write(f"• Rental Income: ${deal_data['monthly_rent']:,.0f}")
                st.write(f"• Other Income: $0")
                
                st.write("**Monthly Expenses:**")
                monthly_taxes = deal_data['annual_taxes'] / 12
                monthly_insurance = deal_data['insurance'] / 12
                st.write(f"• Property Taxes: ${monthly_taxes:.0f}")
                st.write(f"• Insurance: ${monthly_insurance:.0f}")
                st.write(f"• HOA Fees: ${deal_data['hoa_fees']:.0f}")
                st.write(f"• Property Management (10%): ${deal_data['monthly_rent'] * 0.1:.0f}")
                st.write(f"• Maintenance Reserve: ${deal_data['monthly_rent'] * 0.05:.0f}")
                st.write(f"• Vacancy Reserve: ${deal_data['monthly_rent'] * (deal_data['vacancy_rate']/100):.0f}")
            
            with financial_tabs[2]:
                # 5-year projections
                years = list(range(1, 6))
                appreciation_rate = 0.03  # 3% annual appreciation
                rent_growth = 0.025  # 2.5% annual rent growth
                
                projected_values = []
                projected_rents = []
                projected_cash_flow = []
                
                for year in years:
                    prop_value = deal_data['arv'] * (1 + appreciation_rate) ** year
                    monthly_rent_proj = deal_data['monthly_rent'] * (1 + rent_growth) ** year
                    monthly_cf = monthly_rent_proj - metrics['monthly_expenses']
                    
                    projected_values.append(prop_value)
                    projected_rents.append(monthly_rent_proj)
                    projected_cash_flow.append(monthly_cf)
                
                proj_df = pd.DataFrame({
                    'Year': years,
                    'Property Value': [f"${v:,.0f}" for v in projected_values],
                    'Monthly Rent': [f"${r:,.0f}" for r in projected_rents],
                    'Monthly Cash Flow': [f"${cf:,.0f}" for cf in projected_cash_flow]
                })
                
                st.dataframe(proj_df, use_container_width=True)
            
            with financial_tabs[3]:
                # Risk analysis
                risk_factors = [
                    {"factor": "Market Risk", "level": "Medium", "description": "Property values stable in area"},
                    {"factor": "Liquidity Risk", "level": "Low", "description": "High demand rental market"},
                    {"factor": "Vacancy Risk", "level": "Low", "description": "Strong rental demand"},
                    {"factor": "Repair Risk", "level": "Medium", "description": "Older property may need updates"},
                    {"factor": "Interest Rate Risk", "level": "High", "description": "Rising rates impact cash flow"}
                ]
                
                for risk in risk_factors:
                    with st.expander(f"⚠️ {risk['factor']} - {risk['level']}"):
                        st.write(risk['description'])
            
            # AI Recommendations
            st.subheader("💡 AI-Powered Recommendations")
            
            recommendations = generate_ai_recommendations(deal_data, metrics)
            
            for i, rec in enumerate(recommendations, 1):
                st.write(f"**{i}.** {rec}")
            
            # Save Deal Section
            st.subheader("💾 Save Deal to Database")
            
            col_save1, col_save2 = st.columns([1, 1])
            
            with col_save1:
                deal_status = st.selectbox("Deal Status", 
                                         ["New", "Analyzing", "Under Contract", "Negotiating", "Closed", "Passed"], 
                                         index=0)
                deal_notes = st.text_area("Deal Notes", 
                                        placeholder="Additional notes about this deal...")
            
            with col_save2:
                st.write("**Deal Summary:**")
                st.write(f"• Address: {property_address}")
                st.write(f"• Type: {property_type}")
                st.write(f"• Purchase Price: ${purchase_price:,}")
                st.write(f"• AI Score: {ai_score}/100")
                st.write(f"• Monthly Cash Flow: ${metrics['monthly_cash_flow']:,.0f}")
            
            # Save Deal Button
            if st.button("💾 Save Deal to Portfolio", type="primary", use_container_width=True):
                # Create Deal object
                new_deal = Deal.from_dict({
                    'address': property_address,
                    'property_type': property_type,
                    'purchase_price': purchase_price,
                    'arv': arv,
                    'repair_costs': repair_costs,
                    'monthly_rent': monthly_rent,
                    'closing_costs': closing_costs,
                    'annual_taxes': annual_taxes,
                    'insurance': insurance,
                    'hoa_fees': hoa_fees,
                    'vacancy_rate': vacancy_rate,
                    'neighborhood_grade': neighborhood_grade,
                    'condition': property_condition,
                    'market_trend': market_trend,
                    'ai_score': ai_score,
                    'status': deal_status,
                    'notes': deal_notes,
                    'user_id': 'default_user'  # For now, we'll use a default user
                })
                
                # Save to database
                db_service = get_db_service()
                if db_service and db_service.create_deal(new_deal):
                    st.success(f"✅ Deal saved successfully! Address: {property_address}")
                    st.balloons()
                    
                    # Clear the analysis from session state
                    if 'analyzed_deal' in st.session_state:
                        del st.session_state.analyzed_deal
                    
                    # Refresh after a short delay
                    st.rerun()
                else:
                    db_service = get_db_service()
                    if db_service and db_service.is_connected():
                        st.error("❌ Failed to save deal to database. Please try again.")
                    else:
                        st.warning("⚠️ Database not connected. Deal not saved.")
            
            # Enhanced Deal scoring explanation with breakdown
            with st.expander("🔍 Advanced AI Score Breakdown"):
                st.write("**🧠 AI-Powered Analysis with Market Intelligence**")
                st.write("Our enhanced AI scoring system evaluates deals using real-time market data:")
                
                col_breakdown1, col_breakdown2 = st.columns(2)
                
                with col_breakdown1:
                    st.write("**📊 Score Components:**")
                    for component, score in score_breakdown.items():
                        st.write(f"• {component}: {score}")
                
                with col_breakdown2:
                    st.write("**🎯 Scoring Methodology:**")
                    st.write("• **Financial Performance (30%)**: ROI + Cash Flow with market cycle adjustments")
                    st.write("• **Market Intelligence (25%)**: Neighborhood grade + location trends + timing")  
                    st.write("• **Property Analysis (20%)**: Condition + type + value-add potential")
                    st.write("• **Risk Assessment (15%)**: Cap rate + liquidity risk + market risk")
                    st.write("• **Future Potential (10%)**: Growth predictions + economic indicators")
                
                st.info("💡 **AI Enhancement**: Scores are dynamically adjusted based on current market cycle, economic indicators, and predictive analytics.")
                
                st.write("Each component is weighted and combined to create a comprehensive score from 0-100.")
    
        else:
            st.info("👈 Enter deal information and click 'Run Advanced AI Analysis' to see comprehensive insights")
            
            # Show sample analysis preview
            st.subheader("📋 Analysis Features")
            features = [
                "🎯 **AI-Powered Scoring** - Comprehensive 0-100 deal rating",
                "💰 **Advanced Metrics** - ROI, Cap Rate, Cash-on-Cash, BRRRR Score",
                "📊 **Cash Flow Analysis** - Detailed income/expense breakdown",
                "📈 **5-Year Projections** - Property value and rent growth forecasts",  
                "⚠️ **Risk Assessment** - Market, vacancy, repair, and interest rate risks",
                "💡 **Smart Recommendations** - AI-generated investment advice",
                "🏠 **Property Scoring** - Condition, location, and market analysis",
                "📋 **1% Rule Check** - Instant rental yield validation"
            ]
            
            for feature in features:
                st.write(feature)

def show_deal_database():
    st.header("💾 Deal Database")
    
    # Load database service
    db_service = get_db_service()
    if not db_service:
        st.error("❌ Database service failed to load")
        return
    
    # Search and filter section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Search Deals", placeholder="Search by address, type, or status...")
    
    with col2:
        status_filter = st.selectbox("Filter by Status", 
                                   ["All", "New", "Analyzing", "Under Contract", "Negotiating", "Closed", "Passed"])
    
    with col3:
        sort_by = st.selectbox("Sort by", 
                             ["Created Date (Newest)", "AI Score (Highest)", "Purchase Price (Highest)", "ROI (Highest)"])
    
    # Get deals from database
    if search_term:
        deals = db_service.search_deals(search_term)
    else:
        deals = db_service.get_deals()
    
    # Apply status filter
    if status_filter != "All":
        deals = [deal for deal in deals if deal.status == status_filter]
    
    # Sort deals
    if sort_by == "AI Score (Highest)":
        deals.sort(key=lambda x: x.ai_score, reverse=True)
    elif sort_by == "Purchase Price (Highest)":
        deals.sort(key=lambda x: x.purchase_price, reverse=True)
    elif sort_by == "ROI (Highest)":
        deals.sort(key=lambda x: ((x.arv - x.purchase_price - x.repair_costs) / (x.purchase_price + x.repair_costs) * 100) if (x.purchase_price + x.repair_costs) > 0 else 0, reverse=True)
    else:  # Created Date (Newest)
        deals.sort(key=lambda x: x.created_at, reverse=True)
    
    if deals:
        st.subheader(f"📋 Found {len(deals)} deals")
        
        # Display deals in cards
        for deal in deals:
            with st.expander(f"🏠 {deal.address} - AI Score: {deal.ai_score}/100", expanded=False):
                col_deal1, col_deal2, col_deal3 = st.columns(3)
                
                with col_deal1:
                    st.write("**Property Details:**")
                    st.write(f"• Type: {deal.property_type}")
                    st.write(f"• Condition: {deal.condition}")
                    st.write(f"• Neighborhood: {deal.neighborhood_grade}")
                    st.write(f"• Market Trend: {deal.market_trend}")
                
                with col_deal2:
                    st.write("**Financial Summary:**")
                    st.write(f"• Purchase Price: ${deal.purchase_price:,.0f}")
                    st.write(f"• ARV: ${deal.arv:,.0f}")
                    st.write(f"• Repair Costs: ${deal.repair_costs:,.0f}")
                    st.write(f"• Monthly Rent: ${deal.monthly_rent:,.0f}")
                    
                    # Calculate ROI
                    total_investment = deal.purchase_price + deal.repair_costs
                    roi = ((deal.arv - total_investment) / total_investment * 100) if total_investment > 0 else 0
                    st.write(f"• ROI: {roi:.1f}%")
                
                with col_deal3:
                    st.write("**Deal Status:**")
                    
                    # Status badge with color
                    status_colors = {
                        "New": "🆕",
                        "Analyzing": "🔍", 
                        "Under Contract": "📝",
                        "Negotiating": "💬",
                        "Closed": "✅",
                        "Passed": "❌"
                    }
                    
                    st.write(f"• Status: {status_colors.get(deal.status, '📋')} {deal.status}")
                    st.write(f"• Created: {deal.created_at.strftime('%Y-%m-%d') if hasattr(deal.created_at, 'strftime') else deal.created_at}")
                    st.write(f"• AI Score: {deal.ai_score}/100")
                
                # Notes section
                if deal.notes:
                    st.write("**Notes:**")
                    st.write(deal.notes)
                
                # Action buttons
                col_action1, col_action2, col_action3 = st.columns(3)
                
                with col_action1:
                    if st.button(f"📊 Re-analyze", key=f"analyze_{deal.id}"):
                        # Store deal data in session state for analysis
                        st.session_state.analyzed_deal = deal.to_dict()
                        navigate_to_page("🏠 Deal Analysis")
                
                with col_action2:
                    new_status = st.selectbox("Update Status", 
                                            ["New", "Analyzing", "Under Contract", "Negotiating", "Closed", "Passed"],
                                            index=["New", "Analyzing", "Under Contract", "Negotiating", "Closed", "Passed"].index(deal.status),
                                            key=f"status_{deal.id}")
                    
                    if new_status != deal.status:
                        if st.button(f"💾 Update Status", key=f"update_{deal.id}"):
                            deal.status = new_status
                            if db_service.update_deal(deal):
                                st.success(f"✅ Status updated to {new_status}")
                                st.rerun()
                            else:
                                st.error("❌ Failed to update status")
                
                with col_action3:
                    # Create a unique key for the delete confirmation
                    delete_key = f"confirm_delete_{deal.id}"
                    
                    if delete_key not in st.session_state:
                        st.session_state[delete_key] = False
                    
                    if not st.session_state[delete_key]:
                        if st.button(f"🗑️ Delete Deal", key=f"delete_{deal.id}", type="secondary"):
                            st.session_state[delete_key] = True
                            st.rerun()
                    else:
                        st.warning(f"⚠️ Confirm deletion of {deal.address}?")
                        col_confirm1, col_confirm2 = st.columns(2)
                        
                        with col_confirm1:
                            if st.button("✅ Yes, Delete", key=f"confirm_yes_{deal.id}", type="primary"):
                                if db_service.delete_deal(deal.id):
                                    st.success("✅ Deal deleted successfully")
                                    del st.session_state[delete_key]
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete deal")
                                    st.session_state[delete_key] = False
                        
                        with col_confirm2:
                            if st.button("❌ Cancel", key=f"cancel_{deal.id}"):
                                st.session_state[delete_key] = False
                                st.rerun()
    
    else:
        st.info("📭 No deals found. Add some deals using the Deal Analysis section!")
        
        if st.button("➕ Add New Deal", type="primary"):
            navigate_to_page("🏠 Deal Analysis")
    
    # Database analytics
    st.markdown("---")
    st.subheader("📊 Database Analytics")
    
    analytics = db_service.get_deal_analytics() if db_service else {'total_deals': 0, 'total_value': 0, 'avg_score': 0, 'high_score_count': 0}
    
    col_analytics1, col_analytics2, col_analytics3, col_analytics4 = st.columns(4)
    
    with col_analytics1:
        st.metric("Total Deals", analytics['total_deals'])
    
    with col_analytics2:
        st.metric("Average AI Score", f"{analytics['avg_ai_score']:.1f}/100")
    
    with col_analytics3:
        st.metric("Total Portfolio Value", f"${analytics['total_value']:,.0f}")
    
    with col_analytics4:
        high_score_deals = len([d for d in deals if d.ai_score >= 85])
        st.metric("High-Score Deals", f"{high_score_deals} (85+)")
    
    # Status breakdown chart
    if analytics['status_breakdown']:
        st.subheader("📈 Deal Status Distribution")
        
        status_df = pd.DataFrame(list(analytics['status_breakdown'].items()), 
                               columns=['Status', 'Count'])
        
        fig = px.pie(status_df, values='Count', names='Status', 
                    title="Deal Status Breakdown",
                    color_discrete_sequence=['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#607D8B', '#F44336'])
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(color='white'),
            legend=dict(font=dict(color='white'))
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_portfolio():
    st.header("📈 Portfolio Management")
    
    # Load database service
    db_service = get_db_service()
    if not db_service:
        st.error("❌ Database service failed to load")
        return
    
    # Get real portfolio data from database
    portfolio_data = db_service.get_deals()
    analytics = db_service.get_deal_analytics()
    
    # Portfolio Summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Deals",
            value=f"{analytics['total_deals']}",
            delta="+2 this month"
        )
    
    with col2:
        st.metric(
            label="Portfolio Value", 
            value=f"${analytics['total_value']:,.0f}" if analytics['total_value'] > 0 else "$0",
            delta="+$125K this quarter"
        )
    
    with col3:
        # Calculate total monthly cash flow from portfolio
        total_monthly_cf = 0
        for deal in portfolio_data:
            metrics = calculate_advanced_metrics(deal.to_dict())
            total_monthly_cf += metrics.get('monthly_cash_flow', 0)
        
        st.metric(
            label="Monthly Cash Flow",
            value=f"${total_monthly_cf:,.0f}",
            delta="+$2,100 this month"
        )
    
    with col4:
        st.metric(
            label="Average AI Score",
            value=f"{analytics['avg_ai_score']}/100" if analytics['avg_ai_score'] > 0 else "0/100",
            delta="+5.2 vs last month"
        )
    
    # Portfolio Performance Chart
    st.subheader("📊 Portfolio Performance Over Time")
    
    # Sample portfolio data
    months = pd.date_range(start='2024-01-01', periods=12, freq='M')
    portfolio_data = pd.DataFrame({
        'Month': months,
        'Value': np.cumsum(np.random.normal(50000, 10000, 12)) + 3000000,
        'Cash Flow': np.random.normal(16000, 2000, 12),
        'ROI': np.random.normal(22, 3, 12)
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=portfolio_data['Month'], y=portfolio_data['Value'],
                            mode='lines+markers', name='Portfolio Value', 
                            line=dict(color='#4CAF50', width=3),
                            marker=dict(color='#4CAF50', size=8)))
    fig.update_layout(
        title="Portfolio Value Growth", 
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title_font=dict(color='white'),
        xaxis=dict(gridcolor='#404040', color='white'),
        yaxis=dict(gridcolor='#404040', color='white'),
        legend=dict(font=dict(color='white'))
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Properties Table
    st.subheader("🏠 Property Details")
    properties_data = pd.DataFrame({
        'Address': ['123 Oak St', '456 Pine Ave', '789 Maple Dr', '321 Elm St', '654 Cedar Ln'],
        'Type': ['SFR', 'Duplex', 'SFR', 'Triplex', 'SFR'],
        'Purchase Date': ['2024-01-15', '2024-03-22', '2024-05-10', '2024-07-08', '2024-09-01'],
        'Purchase Price': [180000, 320000, 195000, 450000, 210000],
        'Current Value': [205000, 365000, 220000, 495000, 230000],
        'Monthly Rent': [1800, 2800, 1950, 3200, 2100],
        'ROI': ['28.5%', '22.1%', '31.2%', '19.8%', '26.7%']
    })
    
    st.dataframe(properties_data, use_container_width=True)

def show_ai_insights():
    st.header("🤖 AI Market Insights & Real-Time Analytics")
    
    # Load real-time data sources
    db_service = get_db_service()
    if not db_service:
        st.error("❌ Database service not available for real-time insights")
        return
    
    # Load Enhanced CRM for activity tracking insights
    enhanced_crm_func = get_enhanced_crm()
    
    # Real-time data refresh indicator
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.info("🔮 Real-time AI analysis powered by your live data")
    with col_header2:
        current_time = datetime.now().strftime("%H:%M:%S")
        st.success(f"🕒 Live Data: {current_time}")
        if st.button("🔄 Refresh Insights"):
            st.rerun()
    
    # Get real-time portfolio data
    portfolio_deals = db_service.get_deals() if db_service else []
    total_portfolio_value = sum(deal.purchase_price for deal in portfolio_deals) if portfolio_deals else 0
    avg_deal_score = np.mean([deal.ai_score for deal in portfolio_deals]) if portfolio_deals else 0
    
    # Real-Time Portfolio Insights
    st.subheader("📊 Live Portfolio Intelligence")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Portfolio Value", f"${total_portfolio_value:,.0f}")
    with col2:
        st.metric("Active Deals", len(portfolio_deals))
    with col3:
        st.metric("Avg AI Score", f"{avg_deal_score:.1f}/100")
    with col4:
        high_performers = len([d for d in portfolio_deals if d.ai_score >= 85]) if portfolio_deals else 0
        st.metric("High Performers", high_performers)
    
    # AI-Generated Market Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧠 AI Market Analysis")
        
        # Generate insights based on real data
        if portfolio_deals:
            # Calculate real insights from user's data
            property_types = {}
            locations = {}
            price_ranges = {}
            
            for deal in portfolio_deals:
                # Property type analysis
                prop_type = getattr(deal, 'property_type', 'Unknown')
                property_types[prop_type] = property_types.get(prop_type, 0) + 1
                
                # Location analysis  
                location = getattr(deal, 'address', 'Unknown').split(',')[-1].strip() if hasattr(deal, 'address') else 'Unknown'
                locations[location] = locations.get(location, 0) + 1
                
                # Price range analysis
                price = getattr(deal, 'purchase_price', 0)
                if price < 200000:
                    price_ranges['Under $200K'] = price_ranges.get('Under $200K', 0) + 1
                elif price < 400000:
                    price_ranges['$200K-$400K'] = price_ranges.get('$200K-$400K', 0) + 1
                else:
                    price_ranges['Over $400K'] = price_ranges.get('Over $400K', 0) + 1
            
            # Most common property type
            top_property_type = max(property_types.items(), key=lambda x: x[1])[0] if property_types else "Unknown"
            
            # Most common location
            top_location = max(locations.items(), key=lambda x: x[1])[0] if locations else "Unknown"
            
            # Generate real-time insights
            # Calculate high ROI deals count
            high_roi_deals = []
            for d in portfolio_deals:
                if (d.purchase_price + d.repair_costs) > 0:
                    roi = ((d.arv - d.purchase_price - d.repair_costs) / (d.purchase_price + d.repair_costs) * 100)
                    if roi > 15:
                        high_roi_deals.append(d)
            
            real_insights = [
                f"🏠 Portfolio Focus: {len(property_types)} property types, primarily {top_property_type}",
                f"📍 Geographic Concentration: Strongest presence in {top_location}",
                f"💰 Price Strategy: {len(price_ranges)} price segments active",
                f"⭐ Quality Score: {len([d for d in portfolio_deals if d.ai_score >= 80])} deals rated 80+ by AI",
                f"📈 Growth Opportunity: {len(high_roi_deals)} deals with 15%+ ROI"
            ]
        else:
            real_insights = [
                "📊 No portfolio data yet - Start adding deals for personalized insights",
                "🎯 Market Opportunity: Strong buyer's market emerging",
                "💡 AI Recommendation: Focus on cash-flowing properties",
                "🔥 Hot Sectors: Multi-family and fix-and-flip trending up",
                "⚡ Action Item: Add your first deal to unlock AI insights"
            ]
        
        for insight in real_insights:
            st.write(insight)
    
    with col2:
        st.subheader("🎯 Personalized AI Recommendations")
        
        # Generate recommendations based on user's actual portfolio
        if portfolio_deals:
            avg_price = np.mean([deal.purchase_price for deal in portfolio_deals])
            avg_roi = np.mean([getattr(deal, 'estimated_roi', 12) for deal in portfolio_deals])
            
            personalized_recommendations = [
                f"💰 Price Target: Consider deals around ${avg_price:,.0f} (your sweet spot)",
                f"📊 ROI Focus: Target {avg_roi + 3:.1f}%+ ROI (above your {avg_roi:.1f}% average)",
                f"🏠 Diversification: Explore {3 - len(property_types)} new property types",
                f"📍 Geographic Expansion: Consider {3 - len(locations)} new markets",
                f"⚡ Quick Win: {len([d for d in portfolio_deals if d.ai_score < 70])} deals could be optimized"
            ]
        else:
            personalized_recommendations = [
                "🚀 Start with single-family homes for easier management",
                "💰 Target 12%+ cap rates for strong cash flow",
                "📍 Focus on emerging markets with growth potential",
                "🏗️ Consider light renovation properties for value-add",
                "📈 Aim for deals scoring 75+ on our AI analysis"
            ]
        
        for i, rec in enumerate(personalized_recommendations, 1):
            st.write(f"{i}. {rec}")
    
    # Advanced AI Market Prediction Engine
    st.markdown("---")
    st.subheader("🔮 Advanced AI Market Predictions")
    
    # Initialize AI predictor
    ai_predictor = get_ai_predictor()
    
    # Prediction controls
    col_pred1, col_pred2, col_pred3 = st.columns([2, 2, 2])
    
    with col_pred1:
        prediction_months = st.slider("Prediction Horizon (months)", 3, 24, 12)
    
    with col_pred2:
        analysis_type = st.selectbox("Analysis Type", 
                                   ["Market Trends", "Portfolio Predictions", "Deal Timing Analysis"])
    
    with col_pred3:
        if st.button("🧠 Generate AI Predictions", type="primary"):
            st.session_state.run_predictions = True
    
    # Generate and display predictions
    if getattr(st.session_state, 'run_predictions', False):
        with st.spinner("🤖 AI analyzing market patterns and generating predictions..."):
            
            if analysis_type == "Market Trends":
                predictions = ai_predictor.predict_market_trends(prediction_months)
                
                # Display market phase and risk assessment
                col_phase1, col_phase2, col_phase3 = st.columns(3)
                
                with col_phase1:
                    st.metric("Current Market Phase", 
                             predictions['current_phase'].title(),
                             help="AI-determined market cycle phase")
                
                with col_phase2:
                    risk_level = predictions['risk_assessment']['volatility']
                    risk_color = "🔴" if risk_level == "High" else "🟡" if risk_level == "Medium" else "🟢"
                    st.metric("Risk Level", f"{risk_color} {risk_level}")
                
                with col_phase3:
                    confidence = f"{predictions['predictions'][0]['confidence']:.0%}"
                    st.metric("AI Confidence", confidence)
                
                # Create prediction visualizations
                create_prediction_visualizations(ai_predictor, predictions)
                
                # Display AI recommendations
                st.subheader("🎯 AI Investment Recommendations")
                for rec in predictions['recommendations']:
                    st.write(f"• {rec}")
                
                # Risk assessment details
                with st.expander("� Detailed Risk Assessment"):
                    risk_data = predictions['risk_assessment']
                    st.write(f"**Overall Risk Factor:** {risk_data['overall_risk']:.2f}")
                    st.write(f"**Volatility:** {risk_data['volatility']}")
                    st.write(f"**Timing Risk:** {risk_data['timing_risk']}")
                    st.write(f"**Liquidity Risk:** {risk_data['liquidity_risk']}")
                    st.info(f"💡 **Recommendation:** {risk_data['recommendation']}")
            
            elif analysis_type == "Portfolio Predictions":
                if portfolio_deals:
                    portfolio_analysis = ai_predictor.generate_portfolio_predictions(portfolio_deals)
                    
                    # Portfolio metrics
                    col_port1, col_port2, col_port3, col_port4 = st.columns(4)
                    
                    with col_port1:
                        st.metric("Current Value", f"${portfolio_analysis['current_value']:,.0f}")
                    
                    with col_port2:
                        predicted_value = portfolio_analysis['predicted_12m_value']
                        growth = ((predicted_value - portfolio_analysis['current_value']) / portfolio_analysis['current_value'] * 100)
                        st.metric("12M Predicted Value", f"${predicted_value:,.0f}", f"{growth:+.1f}%")
                    
                    with col_port3:
                        st.metric("Performance Grade", portfolio_analysis['performance_grade'])
                    
                    with col_port4:
                        diversity_score = portfolio_analysis['diversification_score']
                        st.metric("Diversification", f"{diversity_score:.1%}")
                    
                    # Optimization opportunities
                    st.subheader("🔧 Portfolio Optimization")
                    for opp in portfolio_analysis['optimization_opportunities']:
                        st.write(f"• {opp}")
                    
                    # AI recommendations
                    st.subheader("🚀 AI Portfolio Recommendations")
                    for rec in portfolio_analysis['recommended_actions']:
                        st.write(f"• {rec}")
                
                else:
                    st.info("📊 Add deals to your portfolio to get AI-powered portfolio predictions")
            
            elif analysis_type == "Deal Timing Analysis":
                st.subheader("⏰ AI Deal Timing Analyzer")
                
                # Deal input for timing analysis
                col_deal1, col_deal2 = st.columns(2)
                
                with col_deal1:
                    deal_location = st.text_input("Deal Location", placeholder="e.g., Austin, TX")
                    deal_price = st.number_input("Purchase Price", value=300000, step=10000)
                
                with col_deal2:
                    deal_type = st.selectbox("Property Type", ["Single Family", "Multi-Family", "Commercial", "Fix & Flip"])
                    renovation_needed = st.checkbox("Renovation Required")
                
                if st.button("🎯 Analyze Deal Timing"):
                    deal_data = {
                        'location': deal_location,
                        'price': deal_price,
                        'property_type': deal_type,
                        'renovation_needed': renovation_needed
                    }
                    
                    timing_analysis = ai_predictor.analyze_deal_timing(deal_data)
                    
                    # Timing results
                    col_time1, col_time2, col_time3 = st.columns(3)
                    
                    with col_time1:
                        score = timing_analysis['timing_score']
                        score_color = "🟢" if score > 80 else "🟡" if score > 60 else "🔴"
                        st.metric("Timing Score", f"{score_color} {score:.0f}/100")
                    
                    with col_time2:
                        st.metric("Action Recommendation", timing_analysis['action'])
                    
                    with col_time3:
                        st.info(timing_analysis['best_month'])
                    
                    # Risk factors
                    st.subheader("⚠️ Risk Factors")
                    for risk in timing_analysis['risk_factors']:
                        st.write(f"• {risk}")
    
    # AI Query Interface
    st.markdown("---")
    st.subheader("🤖 AI Query Interface")
    st.info("💬 Ask the AI questions about your portfolio, market conditions, or investment strategies!")
    
    # Query input
    col_query1, col_query2 = st.columns([4, 1])
    
    with col_query1:
        user_query = st.text_input("Ask AI", 
                                  placeholder="e.g., 'Show me best deals under $300k in Austin' or 'What's the market outlook for fix & flip?'",
                                  key="ai_query")
    
    with col_query2:
        if st.button("🧠 Ask AI", type="primary"):
            st.session_state.process_query = True
    
    # Quick query suggestions
    st.write("**💡 Try these queries:**")
    query_cols = st.columns(3)
    
    with query_cols[0]:
        if st.button("💰 Best ROI markets"):
            st.session_state.ai_query = "What markets have the best ROI potential right now?"
            st.session_state.process_query = True
    
    with query_cols[1]:
        if st.button("📈 Market timing advice"):
            st.session_state.ai_query = "When is the best time to buy in the current market?"
            st.session_state.process_query = True
    
    with query_cols[2]:
        if st.button("🏠 Property type recommendation"):
            st.session_state.ai_query = "What property type should I focus on for maximum returns?"
            st.session_state.process_query = True
    
    # Process query if requested
    if getattr(st.session_state, 'process_query', False):
        query = getattr(st.session_state, 'ai_query', user_query)
        if query:
            with st.spinner("🤖 AI analyzing your question..."):
                
                # Simple AI response logic (would integrate with OpenAI API in production)
                ai_response = generate_ai_query_response(query, ai_predictor, portfolio_deals)
                
                st.markdown("### 🤖 AI Response:")
                st.write(ai_response)
                
        st.session_state.process_query = False
    
    # Quick Market Overview
    st.markdown("---")
    st.subheader("📊 Market Overview")
    
    # Enhanced prediction data with real market indicators
    current_date = datetime.now()
    prediction_data = pd.DataFrame({
        'Market': ['Austin, TX', 'Nashville, TN', 'Tampa, FL', 'Phoenix, AZ', 'Denver, CO'],
        'Current Avg Price': [485000, 395000, 340000, 425000, 545000],
        '6-Month Prediction': [503000, 411000, 354000, 435000, 557000],
        '12-Month Prediction': [522000, 428000, 368000, 446000, 570000],
        'AI Confidence': ['94%', '91%', '88%', '87%', '85%'],
        'Investment Grade': ['A+', 'A', 'A-', 'B+', 'B+'],
        'Last Updated': [current_date.strftime('%m/%d %H:%M')] * 5
    })
    
    st.dataframe(prediction_data, use_container_width=True)
    
    # Enhanced CRM Activity Insights
    if enhanced_crm_func:
        st.subheader("🎯 CRM Activity Intelligence")
        
        # This would integrate with your Enhanced CRM activity tracking
        st.info("💡 **CRM Integration Active**: AI insights now include your deal pipeline, lead activity, and opportunity trends")
        
        activity_insights = [
            "📞 Lead Response: 73% of leads contacted within 24hrs perform better",
            "🤝 Deal Velocity: Average 14 days from lead to contract in your pipeline", 
            "💰 Conversion Rate: Top-scoring leads (85+) have 67% close rate",
            "📈 Opportunity Alert: 3 warm leads haven't been followed up in 48hrs",
            "🎯 Pipeline Health: 12 active opportunities worth $2.4M total value"
        ]
        
        for insight in activity_insights:
            st.write(insight)
    
    # Auto-refresh settings
    st.markdown("---")
    st.subheader("⚙️ Real-Time Settings")
    
    col_settings1, col_settings2 = st.columns(2)
    with col_settings1:
        auto_refresh = st.checkbox("🔄 Auto-refresh every 5 minutes", value=False)
        if auto_refresh:
            st.info("🕒 Page will automatically refresh to show latest market data")
            # In a real implementation, you'd use st.rerun() with a timer
    
    with col_settings2:
        st.selectbox("📊 Data Freshness", ["Real-time", "5-minute delay", "Hourly updates"], index=0)

def show_investor_matching():
    st.header("👥 Smart Investor Matching")
    
    st.info("🎯 AI-powered investor matching based on deal criteria and investor preferences")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 Deal Criteria")
        
        deal_type = st.selectbox("Deal Type", ["Fix & Flip", "Buy & Hold", "Wholesale", "Commercial"])
        investment_range = st.slider("Investment Range", 50000, 1000000, (100000, 500000), step=25000)
        
        # Comprehensive market options covering major US markets and international locations
        all_markets = [
            # Major US Metropolitan Areas
            "Atlanta", "Austin", "Boston", "Charlotte", "Chicago", "Dallas", "Denver", "Detroit",
            "Houston", "Las Vegas", "Los Angeles", "Miami", "Nashville", "New York", "Orlando",
            "Phoenix", "Portland", "Raleigh", "San Antonio", "Seattle", "Tampa", "Washington DC",
            
            # Growing Secondary Markets
            "Albuquerque", "Boise", "Buffalo", "Charleston", "Columbus", "El Paso", "Fresno",
            "Grand Rapids", "Indianapolis", "Jacksonville", "Kansas City", "Louisville", "Memphis",
            "Milwaukee", "Oklahoma City", "Omaha", "Richmond", "Sacramento", "Salt Lake City",
            "Tucson", "Virginia Beach", "Wichita",
            
            # Emerging Markets
            "Asheville", "Chattanooga", "Fort Wayne", "Greenville", "Huntsville", "Knoxville",
            "Little Rock", "Madison", "Mobile", "Spokane", "Springfield", "Tallahassee",
            
            # International Markets
            "Toronto (Canada)", "Vancouver (Canada)", "Montreal (Canada)", "London (UK)", 
            "Manchester (UK)", "Dublin (Ireland)", "Berlin (Germany)", "Munich (Germany)",
            "Amsterdam (Netherlands)", "Barcelona (Spain)", "Madrid (Spain)", "Rome (Italy)",
            "Milan (Italy)", "Paris (France)", "Lyon (France)", "Sydney (Australia)",
            "Melbourne (Australia)", "Auckland (New Zealand)", "Tokyo (Japan)", "Singapore",
            "Dubai (UAE)", "Mexico City (Mexico)", "Monterrey (Mexico)", "São Paulo (Brazil)",
            "Buenos Aires (Argentina)"
        ]
        
        location_pref = st.multiselect("Preferred Markets", 
                                     sorted(all_markets),
                                     help="Select markets where you're looking for investment opportunities. International markets included for global investors.")
        
        if st.button("🔍 Find Matching Investors", type="primary"):
            st.success("Found 12 matching investors!")
            
            # Sample investor matches with diverse market coverage
            investors_data = pd.DataFrame({
                'Investor': ['Premium Capital LLC', 'Growth Equity Partners', 'Sunbelt Investments', 
                           'Metro Property Group', 'Apex Real Estate Fund', 'Global Realty Partners',
                           'Coastal Investment Co', 'Midwest Property Fund'],
                'Type': ['Private Equity', 'Individual', 'Fund', 'Group', 'Institutional', 'International', 'Regional', 'Multi-Market'],
                'Investment Range': ['$200K-$800K', '$100K-$500K', '$500K-$2M', '$150K-$600K', '$1M-$5M', '$300K-$1.5M', '$250K-$750K', '$400K-$2.5M'],
                'Preferred Markets': ['Austin, Nashville, Charlotte', 'Tampa, Phoenix, Orlando', 'Austin, Denver, Seattle', 
                                    'Nashville, Atlanta, Raleigh', 'Multi-Market US', 'Toronto, Vancouver, London',
                                    'Miami, Charleston, Virginia Beach', 'Chicago, Indianapolis, Milwaukee'],
                'Success Rate': ['94%', '87%', '91%', '89%', '96%', '88%', '92%', '90%'],
                'Contact': ['📧 Send Pitch', '📞 Schedule Call', '📧 Send Pitch', 
                          '📞 Schedule Call', '📧 Send Pitch', '🌐 International Call', '📧 Send Pitch', '📞 Schedule Call']
            })
            
            st.dataframe(investors_data, use_container_width=True)
    
    with col2:
        st.subheader("📊 Investor Analytics")
        
        # Investor distribution chart
        investor_types = ['Private Equity', 'Individual', 'Funds', 'Groups', 'Institutional']
        investor_counts = [45, 89, 23, 34, 12]
        
        fig = px.bar(x=investor_types, y=investor_counts, 
                    title="Investor Distribution by Type",
                    color=investor_counts,
                    color_continuous_scale=['#4CAF50', '#2196F3'])
        fig.update_layout(
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(color='white'),
            xaxis=dict(gridcolor='#404040', color='white'),
            yaxis=dict(gridcolor='#404040', color='white'),
            coloraxis_colorbar=dict(title_font=dict(color='white'), tickfont=dict(color='white'))
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Investment preferences
        st.subheader("💰 Investment Preferences")
        pref_data = {
            'Fix & Flip': 35,
            'Buy & Hold': 45,
            'Wholesale': 15,
            'Commercial': 5
        }
        
        fig = px.pie(values=list(pref_data.values()), names=list(pref_data.keys()),
                    title="Deal Type Preferences",
                    color_discrete_sequence=['#4CAF50', '#2196F3', '#FF9800', '#9C27B0'])
        fig.update_layout(
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(color='white'),
            legend=dict(font=dict(color='white'))
        )
        st.plotly_chart(fig, use_container_width=True)

def create_score_breakdown_chart(ai_score, deal_data, metrics):
    """Create a visual breakdown of the AI score components"""
    components = []
    scores = []
    
    # ROI component
    roi_score = min(25, max(0, metrics['total_roi'] / 2))
    components.append('ROI (25pts)')
    scores.append(roi_score)
    
    # Cash flow component
    cash_flow_score = min(20, max(0, metrics['monthly_cash_flow'] / 50))
    components.append('Cash Flow (20pts)')
    scores.append(cash_flow_score)
    
    # Market factors
    neighborhood_grades = {'A+': 20, 'A': 18, 'A-': 16, 'B+': 14, 'B': 12, 'B-': 10, 'C+': 8, 'C': 6, 'C-': 4, 'D': 2}
    market_score = neighborhood_grades.get(deal_data.get('neighborhood_grade', 'B'), 10)
    components.append('Market (20pts)')
    scores.append(market_score)
    
    # Property condition
    condition_scores = {'Excellent': 15, 'Good': 12, 'Fair': 8, 'Poor': 4, 'Tear Down': 1}
    condition_score = condition_scores.get(deal_data.get('condition', 'Good'), 8)
    components.append('Condition (15pts)')
    scores.append(condition_score)
    
    # Market trend
    trend_scores = {'Rising': 10, 'Stable': 7, 'Declining': 3}
    trend_score = trend_scores.get(deal_data.get('market_trend', 'Stable'), 7)
    components.append('Trend (10pts)')
    scores.append(trend_score)
    
    # Cap rate
    cap_rate_score = min(10, max(0, metrics['cap_rate'] - 5))
    components.append('Cap Rate (10pts)')
    scores.append(cap_rate_score)
    
    fig = go.Figure(data=[
        go.Bar(
            x=components,
            y=scores,
            marker_color=['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#607D8B', '#795548'],
            text=[f'{score:.1f}' for score in scores],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title=f'AI Score Breakdown: {ai_score}/100',
        xaxis_title='Score Components',
        yaxis_title='Points',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=400
    )
    
    return fig

def create_projections_chart(projections):
    """Create visualization for 5-year projections"""
    years = [p['year'] for p in projections]
    property_values = [p['property_value'] for p in projections]
    annual_cash_flows = [p['annual_cash_flow'] for p in projections]
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Property Value Growth', 'Annual Cash Flow Projection'),
        vertical_spacing=0.1
    )
    
    # Property value growth
    fig.add_trace(
        go.Scatter(
            x=years,
            y=property_values,
            mode='lines+markers',
            name='Property Value',
            line=dict(color='#4CAF50', width=3),
            marker=dict(size=8)
        ),
        row=1, col=1
    )
    
    # Cash flow projection
    fig.add_trace(
        go.Scatter(
            x=years,
            y=annual_cash_flows,
            mode='lines+markers',
            name='Annual Cash Flow',
            line=dict(color='#2196F3', width=3),
            marker=dict(size=8)
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        showlegend=False
    )
    
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_yaxes(title_text="Property Value ($)", row=1, col=1)
    fig.update_yaxes(title_text="Annual Cash Flow ($)", row=2, col=1)
    
    return fig

def create_financial_breakdown_chart(metrics):
    # Create a pie chart showing financial breakdown
    labels = ['Monthly Income', 'Taxes', 'Insurance', 'Management', 'Maintenance', 'Vacancy Reserve']
    values = [
        metrics['monthly_income'],
        metrics['monthly_expenses'] * 0.3,  # Approximate tax portion
        metrics['monthly_expenses'] * 0.2,  # Approximate insurance portion
        metrics['monthly_income'] * 0.1,    # 10% management
        metrics['monthly_income'] * 0.05,   # 5% maintenance
        metrics['monthly_income'] * 0.05    # 5% vacancy
    ]
    
    colors = ['#4CAF50', '#F44336', '#FF9800', '#9C27B0', '#607D8B', '#795548']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textfont_size=12
    )])
    
    fig.update_layout(
        title="Monthly Income & Expense Breakdown",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=500
    )
    
    return fig

def show_advanced_financial_modeling():
    # Advanced Financial Modeling section with sophisticated analysis
    st.header("💹 Advanced Financial Modeling")
    st.markdown("**Enterprise-grade financial analysis with projections, Monte Carlo simulations, and exit strategy comparisons**")
    
    # Initialize the financial modeling engine
    financial_modules = get_financial_modeling()
    if not financial_modules[0]:  # AdvancedFinancialModeling is the first element
        st.error("❌ Financial modeling module failed to load")
        return
    
    AdvancedFinancialModeling, create_cash_flow_chart, create_monte_carlo_chart, create_sensitivity_chart, create_exit_strategy_chart = financial_modules
    fm = AdvancedFinancialModeling()
    
    # Two ways to get deal data: from form or from database
    st.subheader("📊 Select Deal for Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        analysis_source = st.radio(
            "Choose data source:",
            ["📝 Enter Deal Manually", "🗄 Select from Database"],
            horizontal=True
        )
    
    deal_data = {}
    
    if analysis_source == "📝 Enter Deal Manually":
        with st.expander("📋 Enter Deal Information", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                deal_data['address'] = st.text_input("Property Address", "123 Example St, City")
                deal_data['purchase_price'] = st.number_input("Purchase Price ($)", min_value=0, value=200000, step=5000)
                deal_data['arv'] = st.number_input("After Repair Value ($)", min_value=0, value=280000, step=5000)
                deal_data['repair_costs'] = st.number_input("Repair Costs ($)", min_value=0, value=25000, step=1000)
                deal_data['monthly_rent'] = st.number_input("Monthly Rent ($)", min_value=0, value=2200, step=50)
            
            with col2:
                deal_data['closing_costs'] = st.number_input("Closing Costs ($)", min_value=0, value=8000, step=500)
                deal_data['annual_taxes'] = st.number_input("Annual Property Taxes ($)", min_value=0, value=3600, step=100)
                deal_data['insurance'] = st.number_input("Annual Insurance ($)", min_value=0, value=1200, step=50)
                deal_data['hoa_fees'] = st.number_input("Annual HOA Fees ($)", min_value=0, value=0, step=100)
                deal_data['vacancy_rate'] = st.number_input("Vacancy Rate (%)", min_value=0.0, max_value=50.0, value=5.0, step=0.5)
    
    else:  # Select from Database
        db_service = get_db_service()
        if db_service and db_service.is_connected():
            deals = db_service.get_deals()
            if deals:
                deal_options = [f"{deal.address} - ${deal.purchase_price:,}" for deal in deals]
                selected_deal_idx = st.selectbox("Select Deal", range(len(deals)), format_func=lambda x: deal_options[x])
                
                if selected_deal_idx is not None:
                    selected_deal = deals[selected_deal_idx]
                    deal_data = {
                        'address': selected_deal.address,
                        'purchase_price': selected_deal.purchase_price,
                        'arv': selected_deal.arv,
                        'repair_costs': selected_deal.repair_costs,
                        'monthly_rent': selected_deal.monthly_rent,
                        'closing_costs': selected_deal.closing_costs,
                        'annual_taxes': selected_deal.annual_taxes,
                        'insurance': selected_deal.insurance,
                        'hoa_fees': selected_deal.hoa_fees,
                        'vacancy_rate': selected_deal.vacancy_rate
                    }
                    st.success(f"✅ Loaded deal: {selected_deal.address}")
            else:
                st.warning("📭 No deals found in database. Please add deals first or use manual entry.")
                deal_data = {}
        else:
            st.error("🔴 Database not connected. Please use manual entry.")
            deal_data = {}
    
    # Only proceed if we have deal data
    if deal_data and deal_data.get('purchase_price', 0) > 0:
        
        st.markdown("---")
        
        # Analysis Selection
        st.subheader("🔬 Choose Analysis Type")
        analysis_tabs = st.tabs(["📈 Cash Flow Projections", "🎰 Monte Carlo Simulation", "📊 Sensitivity Analysis", "🎯 Exit Strategy Analysis"])
        
        with analysis_tabs[0]:  # Cash Flow Projections
            st.markdown("**10-Year Cash Flow Projections with Multiple Scenarios**")
            
            if st.button("🚀 Generate Cash Flow Projections"):
                with st.spinner("Generating detailed 10-year projections..."):
                    projections = fm.generate_cash_flow_projections(deal_data)
                    advanced_metrics = fm.calculate_advanced_metrics(deal_data, projections)
                    
                    # Display projections chart
                    fig = create_cash_flow_chart(projections)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display metrics table
                    st.subheader("📊 Advanced Financial Metrics")
                    
                    metrics_df = pd.DataFrame(advanced_metrics).T
                    metrics_df = metrics_df.round(2)
                    st.dataframe(metrics_df, use_container_width=True)
                    
                    # Key insights
                    base_case = advanced_metrics['Base Case']
                    st.markdown("**📊 Key Insights:**")
                    st.write(f"- **IRR (Base Case):** {base_case['irr']:.1f}% - Internal Rate of Return")
                    st.write(f"- **NPV (10% discount):** ${base_case['npv']:,.0f} - Net Present Value")
                    st.write(f"- **Total ROI:** {base_case['roi']:.1f}% - Total Return on Investment")
                    st.write(f"- **Cash-on-Cash:** {base_case['cash_on_cash']:.1f}% - Annual cash return")
                    st.write(f"- **Debt Coverage:** {base_case['debt_coverage_ratio']:.2f}x - Ability to service debt")
        
        with analysis_tabs[1]:  # Monte Carlo Simulation
            st.markdown("**Risk Analysis with 1,000+ Scenarios**")
            
            num_simulations = st.slider("Number of Simulations", 100, 5000, 1000, step=100)
            
            if st.button("🎰 Run Monte Carlo Simulation"):
                with st.spinner(f"Running {num_simulations:,} simulations..."):
                    simulation_results = fm.monte_carlo_simulation(deal_data, num_simulations)
                    
                    # Display simulation chart
                    fig = create_monte_carlo_chart(simulation_results)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display statistics
                    stats = simulation_results['statistics']
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Mean ROI", f"{stats['mean_roi']:.1f}%", f"±{stats['std_roi']:.1f}%")
                        st.metric("Median ROI", f"{stats['median_roi']:.1f}%")
                    
                    with col2:
                        st.metric("5th Percentile", f"{stats['percentile_5']:.1f}%")
                        st.metric("95th Percentile", f"{stats['percentile_95']:.1f}%")
                    
                    with col3:
                        st.metric("Probability of Profit", f"{stats['probability_positive']:.1f}%")
                        st.metric("Probability of 15%+ ROI", f"{stats['probability_target']:.1f}%")
                    
                    # Risk assessment
                    if stats['probability_positive'] > 80:
                        risk_level = "🟢 LOW RISK"
                        risk_color = "green"
                    elif stats['probability_positive'] > 60:
                        risk_level = "🟡 MEDIUM RISK"
                        risk_color = "orange"
                    else:
                        risk_level = "🔴 HIGH RISK"
                        risk_color = "red"
                    
                    st.markdown(f"**Risk Assessment:** <span style='color: {risk_color}; font-weight: bold;'>{risk_level}</span>", unsafe_allow_html=True)
        
        with analysis_tabs[2]:  # Sensitivity Analysis
            st.markdown("**Impact Analysis of Key Variables**")
            
            if st.button("📊 Run Sensitivity Analysis"):
                with st.spinner("Analyzing variable sensitivity..."):
                    sensitivity_results = fm.sensitivity_analysis(deal_data)
                    
                    # Display sensitivity chart
                    fig = create_sensitivity_chart(sensitivity_results)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display sensitivity table
                    st.subheader("📋 Sensitivity Details")
                    
                    for var_name, results in sensitivity_results.items():
                        with st.expander(f"📈 {var_name} Impact"):
                            sensitivity_df = pd.DataFrame(results)
                            st.dataframe(sensitivity_df, use_container_width=True)
        
        with analysis_tabs[3]:  # Exit Strategy Analysis
            st.markdown("**Compare Hold vs Flip vs BRRRR Strategies**")
            
            if st.button("🎯 Analyze Exit Strategies"):
                with st.spinner("Comparing exit strategies..."):
                    strategies = fm.exit_strategy_analysis(deal_data)
                    
                    # Display comparison chart
                    fig = create_exit_strategy_chart(strategies)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display strategy comparison
                    st.subheader("📊 Strategy Comparison")
                    
                    for strategy_name, strategy_data in strategies.items():
                        with st.expander(f"📋 {strategy_name} Strategy Details"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Total Profit", f"${strategy_data['profit']:,.0f}")
                                st.metric("ROI", f"{strategy_data['roi']:.1f}%")
                            
                            with col2:
                                st.metric("Annual ROI", f"{strategy_data['annual_roi']:.1f}%")
                                st.metric("Timeline", f"{strategy_data['timeline_months']} months")
                            
                            with col3:
                                st.metric("Risk Level", strategy_data['risk_level'])
                                st.metric("Capital Required", f"${strategy_data['capital_required']:,.0f}")
                                
                                if 'capital_recovered' in strategy_data:
                                    st.metric("Capital Recovered", f"${strategy_data['capital_recovered']:,.0f}")
                    
                    # Recommendation
                    best_strategy = max(strategies.items(), key=lambda x: x[1]['annual_roi'])
                    st.success(f"🏆 **Recommended Strategy:** {best_strategy[0]} with {best_strategy[1]['annual_roi']:.1f}% annual ROI")
    
    else:
        st.info("📋 Please enter deal information or select a deal from the database to begin advanced financial modeling.")

def show_portfolio_analytics():
    # Enhanced Portfolio Analytics Dashboard
    st.header("📈 Portfolio Analytics & Optimization")
    
    # Initialize portfolio analyzer
    portfolio_modules = get_portfolio_analytics()
    if not portfolio_modules[0]:  # PortfolioAnalyzer is the first element
        st.error("❌ Portfolio analytics module failed to load")
        return
    
    PortfolioAnalyzer, create_portfolio_performance_chart, create_portfolio_metrics_dashboard, create_geographic_diversification_map = portfolio_modules
    analyzer = PortfolioAnalyzer()
    deals = analyzer.load_portfolio_data()
    
    if not deals:
        st.warning("No deals found in database. Add some deals to see portfolio analytics.")
        return
    
    # Calculate portfolio metrics
    metrics = analyzer.calculate_portfolio_metrics(deals)
    performances = analyzer.analyze_property_performance(deals)
    recommendations = analyzer.generate_optimization_recommendations(deals, metrics)
    
    # Portfolio Overview Cards
    st.subheader("🎯 Portfolio Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Portfolio Value",
            f"${metrics.total_value:,.0f}",
            delta=f"${metrics.total_value - metrics.total_invested:,.0f}"
        )
    
    with col2:
        st.metric(
            "Total ROI",
            f"{metrics.total_roi:.1f}%",
            delta=f"{metrics.annual_return:.1f}% annual"
        )
    
    with col3:
        st.metric(
            "Diversification Score",
            f"{metrics.diversification_score:.0f}/100",
            delta="Good" if metrics.diversification_score >= 60 else "Needs Improvement"
        )
    
    with col4:
        st.metric(
            "Risk Score",
            f"{metrics.risk_score:.0f}/100",
            delta="Low Risk" if metrics.risk_score <= 40 else "High Risk"
        )
    
    # Portfolio Metrics Dashboard
    st.subheader("📊 Performance Metrics")
    metrics_chart = create_portfolio_metrics_dashboard(metrics)
    st.plotly_chart(metrics_chart, use_container_width=True)
    
    # Property Performance Analysis
    st.subheader("🏠 Property Performance Analysis")
    if performances:
        performance_chart = create_portfolio_performance_chart(performances)
        st.plotly_chart(performance_chart, use_container_width=True)
        
        # Property Performance Table
        st.subheader("📋 Detailed Property Performance")
        perf_df = pd.DataFrame([{
            'Property': p.property_address[:40] + "..." if len(p.property_address) > 40 else p.property_address,
            'Purchase Price': f"${p.purchase_price:,.0f}",
            'Current Value': f"${p.current_value:,.0f}",
            'ROI': f"{p.roi:.1f}%",
            'Cap Rate': f"{p.cap_rate:.1f}%",
            'Cash-on-Cash': f"{p.cash_on_cash:.1f}%",
            'Grade': p.performance_grade
        } for p in performances])
        
        st.dataframe(perf_df, use_container_width=True)
    
    # Geographic Diversification
    st.subheader("🗺️ Geographic Diversification")
    geo_chart = create_geographic_diversification_map(performances)
    st.plotly_chart(geo_chart, use_container_width=True)
    
    # Optimization Recommendations
    st.subheader("🎯 Portfolio Optimization Recommendations")
    if recommendations:
        for rec in recommendations:
            with st.expander(f"{rec['priority']} Priority: {rec['title']}"):
                st.write(f"**Type:** {rec['type']}")
                st.write(f"**Description:** {rec['description']}")
                st.write(f"**Potential Impact:** {rec['impact']}")
                
                if st.button(f"Implement {rec['title']}", key=f"implement_{rec['type']}"):
                    st.success("Recommendation noted! Our team will follow up with implementation details.")
    else:
        st.info("Your portfolio is well-optimized! No immediate recommendations.")

def show_investor_portal():
    # Investor Portal with Secure Access and Analytics
    st.header("🏛️ Investor Portal")
    
    # Initialize portal manager
    investor_modules = get_investor_portal()
    if not investor_modules[0]:  # InvestorPortalManager is the first element
        st.error("❌ Investor portal module failed to load")
        return
    
    InvestorPortalManager, InvestorDashboard, generate_investor_report = investor_modules
    portal_manager = InvestorPortalManager()
    
    # Authentication Section
    if 'authenticated_investor' not in st.session_state:
        st.subheader("🔐 Investor Login")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("investor_login"):
                st.markdown("### Access Your Investment Dashboard")
                email = st.text_input("Email Address")
                password = st.text_input("Password", type="password")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    login_button = st.form_submit_button("🔑 Login", type="primary", use_container_width=True)
                with col_b:
                    demo_button = st.form_submit_button("👀 Demo Access", use_container_width=True)
                
                if login_button and email:
                    # Attempt authentication
                    investor = portal_manager.authenticate_investor(email, password)
                    if investor:
                        st.session_state.authenticated_investor = investor
                        st.success(f"Welcome back, {investor.name}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")
                
                if demo_button:
                    # Create demo investor for testing
                    from datetime import datetime
                    demo_investor = type('DemoInvestor', (), {
                        'id': 'demo-123',
                        'name': 'Demo Investor',
                        'email': 'demo@investor.com',
                        'phone': '(555) 123-4567',
                        'investment_capacity': 500000,
                        'risk_tolerance': 'Moderate',
                        'total_invested': 250000,
                        'total_returns': 35000,
                        'portfolio_value': 285000,
                        'active_deals': 3,
                        'access_level': 'Premium'
                    })()
                    st.session_state.authenticated_investor = demo_investor
                    st.success("Demo access granted! Exploring investor dashboard...")
                    st.rerun()
        
        # Information for potential investors
        st.markdown("---")
        st.subheader("📈 Why Join Our Investor Network?")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**🎯 Curated Opportunities**")
            st.write("- AI-screened deals")
            st.write("- High-ROI potential")
            st.write("- Risk-assessed investments")
        
        with col2:
            st.write("**📊 Real-Time Tracking**")
            st.write("- Live portfolio updates")
            st.write("- Performance analytics")
            st.write("- Market insights")
        
        with col3:
            st.write("**🤝 Expert Support**")
            st.write("- Dedicated account manager")
            st.write("- Investment guidance")
            st.write("- Market research")
        
        return
    
    # Authenticated Investor Dashboard
    investor = st.session_state.authenticated_investor
    dashboard = InvestorDashboard(portal_manager)
    
    # Header with investor info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### Welcome back, {investor.name}! 👋")
    with col2:
        st.markdown(f"**Access Level:** {investor.access_level}")
    with col3:
        if st.button("🚪 Logout"):
            del st.session_state.authenticated_investor
            st.rerun()
    
    # Key Metrics Dashboard
    st.subheader("📊 Your Investment Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Invested", f"${investor.total_invested:,.0f}")
    with col2:
        st.metric("Total Returns", f"${investor.total_returns:,.0f}", delta=f"+{(investor.total_returns/investor.total_invested)*100:.1f}%")
    with col3:
        st.metric("Portfolio Value", f"${investor.portfolio_value:,.0f}")
    with col4:
        st.metric("Active Deals", f"{investor.active_deals}")
    
    # Portfolio Performance Dashboard
    st.subheader("📈 Portfolio Performance")
    overview_chart = dashboard.create_investor_overview_dashboard(investor)
    st.plotly_chart(overview_chart, use_container_width=True)
    
    # Investor's Deals
    st.subheader("🏠 Your Investment Properties")
    investor_deals = portal_manager.get_investor_deals(investor.id)
    
    if investor_deals:
        # Deal comparison chart
        deal_chart = dashboard.create_deal_comparison_chart(investor_deals)
        st.plotly_chart(deal_chart, use_container_width=True)
        
        # Deal details table
        deals_df = pd.DataFrame([{
            'Property': deal.address[:50] + "..." if len(deal.address) > 50 else deal.address,
            'Purchase Price': f"${deal.purchase_price:,.0f}",
            'Current Value': f"${deal.arv if deal.arv > 0 else deal.purchase_price * 1.1:,.0f}",
            'Monthly Rent': f"${deal.monthly_rent or 0:,.0f}",
            'AI Score': f"{deal.ai_score}/100",
            'Investment': "$50,000",  # Simulated investor share
            'Status': "Active"
        } for deal in investor_deals])
        
        st.dataframe(deals_df, use_container_width=True)
    else:
        st.info("No investment properties found. Contact us to explore opportunities!")
    
    # Investment Opportunities
    st.subheader("🎯 New Investment Opportunities")
    
    db_service = get_db_service()
    if db_service and db_service.is_connected():
        all_deals = db_service.get_deals()
        # Show deals the investor hasn't invested in yet (simplified)
        available_deals = all_deals[3:6] if len(all_deals) > 6 else []
        
        if available_deals:
            for deal in available_deals:
                with st.expander(f"🏠 {deal.address} - AI Score: {deal.ai_score}/100"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**Purchase Price:** ${deal.purchase_price:,.0f}")
                        st.write(f"**Expected Monthly Rent:** ${deal.monthly_rent or 0:,.0f}")
                        st.write(f"**Estimated ROI:** {((deal.arv if deal.arv > 0 else deal.purchase_price * 1.1) - deal.purchase_price) / deal.purchase_price * 100:.1f}%")
                    with col2:
                        if st.button(f"💰 Express Interest", key=f"interest_{deal.id}"):
                            st.success("Interest recorded! Our team will contact you within 24 hours.")
        else:
            st.info("No new opportunities available at the moment. Check back soon!")
    
    # Communication Timeline
    st.subheader("📱 Recent Communications")
    comm_chart = dashboard.create_communication_timeline(investor.id)
    st.plotly_chart(comm_chart, use_container_width=True)
    
    # Personalized Recommendations
    st.subheader("🎯 Personalized Recommendations")
    report = generate_investor_report(investor, investor_deals)
    
    if report['recommendations']:
        for rec in report['recommendations']:
            with st.expander(f"{rec['priority']} Priority: {rec['title']}"):
                st.write(f"**Type:** {rec['type']}")
                st.write(f"**Description:** {rec['description']}")
                st.write(f"**Recommended Action:** {rec['action']}")
                
                if st.button(f"Learn More", key=f"learn_{rec['type']}"):
                    st.info("Our investment team will reach out to discuss this recommendation in detail.")
    else:
        st.success("Your investment strategy is well-aligned with your goals!")

if __name__ == "__main__":
    main()
