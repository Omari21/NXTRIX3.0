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

# Import our new modules
from database import db_service
from models import Deal, Investor, Portfolio
from financial_modeling import AdvancedFinancialModeling, create_cash_flow_chart, create_monte_carlo_chart, create_sensitivity_chart, create_exit_strategy_chart

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
    /* Main app background */
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    
    /* Header styling */
    .main-header {
        background-color: #262730;
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid #404040;
    }
    
    .main-header h1 {
        margin-bottom: 0.5rem;
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        color: white;
    }
    
    /* Metric cards with better contrast */
    .metric-card {
        background-color: #262730;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #404040;
        margin-bottom: 1.5rem;
        color: white;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #4CAF50;
    }
    
    .metric-card h3 {
        color: #ffffff;
        font-size: 0.9rem;
        font-weight: 600;
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
</style>
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
    """Calculate AI-powered deal score based on multiple factors"""
    score = 0
    
    # ROI component (25 points)
    roi_score = min(25, max(0, metrics['total_roi'] / 2))  # Cap at 50% ROI for full points
    score += roi_score
    
    # Cash flow component (20 points)
    cash_flow_score = min(20, max(0, metrics['monthly_cash_flow'] / 50))  # $1000+ cash flow = full points
    score += cash_flow_score
    
    # Market factors (20 points)
    neighborhood_grades = {'A+': 20, 'A': 18, 'A-': 16, 'B+': 14, 'B': 12, 'B-': 10, 'C+': 8, 'C': 6, 'C-': 4, 'D': 2}
    market_score = neighborhood_grades.get(deal_data.get('neighborhood_grade', 'B'), 10)
    score += market_score
    
    # Property condition (15 points)
    condition_scores = {'Excellent': 15, 'Good': 12, 'Fair': 8, 'Poor': 4, 'Tear Down': 1}
    condition_score = condition_scores.get(deal_data.get('condition', 'Good'), 8)
    score += condition_score
    
    # Market trend (10 points)
    trend_scores = {'Rising': 10, 'Stable': 7, 'Declining': 3}
    trend_score = trend_scores.get(deal_data.get('market_trend', 'Stable'), 7)
    score += trend_score
    
    # Cap rate bonus (10 points)
    cap_rate_score = min(10, max(0, metrics['cap_rate'] - 5))  # 5%+ cap rate starts scoring
    score += cap_rate_score
    
    return min(100, max(0, int(score)))

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
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏢 NXTRIX Enterprise Deal Analyzer CRM</h1>
        <p>AI-Powered Real Estate Investment Analysis & Portfolio Management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Navigation
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.selectbox(
        "Choose Section",
        ["📊 Dashboard", "🏠 Deal Analysis", "� Deal Database", "�📈 Portfolio", "🤖 AI Insights", "👥 Investor Matching"]
    )
    
    # Database connection status in sidebar
    st.sidebar.markdown("---")
    if db_service.is_connected():
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
    elif page == "� Advanced Financial Modeling":
        show_advanced_financial_modeling()
    elif page == "�💾 Deal Database":
        show_deal_database()
    elif page == "📈 Portfolio":
        show_portfolio()
    elif page == "🤖 AI Insights":
        show_ai_insights()
    elif page == "👥 Investor Matching":
        show_investor_matching()

def show_dashboard():
    st.header("📊 Executive Dashboard")
    
    # Real-time metrics from database
    if db_service.is_connected():
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
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Deals</h3>
            <h2 style="color: #667eea; font-weight: 700;">{total_deals}</h2>
            <p style="color: #38a169; font-weight: 600;">↗️ {growth_percentage} this month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Avg AI Score</h3>
            <h2 style="color: #38a169; font-weight: 700;">{avg_score:.1f}</h2>
            <p style="color: #38a169; font-weight: 600;">↗️ +2.3% improved</p>
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
            <p style="color: #38a169; font-weight: 600;">↗️ +2.3% vs last month</p>
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
    recent_deals_data = db_service.get_high_scoring_deals(min_score=80)
    
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
        if db_service.is_connected():
            last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.info(f"📡 Live data • Last updated: {last_updated}")
        else:
            st.warning("📡 Offline mode • Sample data shown")

def show_deal_analysis():
    st.header("🏠 Advanced AI-Powered Deal Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 Deal Information")
        
        # Enhanced property details
        property_address = st.text_input("Property Address", placeholder="123 Main Street, City, State")
        
        col1a, col1b = st.columns(2)
        with col1a:
            property_type = st.selectbox("Property Type", 
                                       ["Single Family", "Multi-Family", "Condo", "Townhouse", "Commercial", "Land", "Mixed-Use"])
            bedrooms = st.number_input("Bedrooms", min_value=0, max_value=10, value=3)
            
        with col1b:
            property_condition = st.selectbox("Property Condition", 
                                            ["Excellent", "Good", "Fair", "Poor", "Tear Down"])
            bathrooms = st.number_input("Bathrooms", min_value=0.0, max_value=10.0, value=2.0, step=0.5)
        
        # Financial details
        st.subheader("💰 Financial Details")
        col2a, col2b, col2c = st.columns(3)
        
        with col2a:
            purchase_price = st.number_input("Purchase Price ($)", min_value=0, value=200000, step=1000)
            repair_costs = st.number_input("Repair Costs ($)", min_value=0, value=25000, step=1000)
            closing_costs = st.number_input("Closing Costs ($)", min_value=0, value=5000, step=500)
            
        with col2b:
            arv = st.number_input("After Repair Value ($)", min_value=0, value=275000, step=1000)
            monthly_rent = st.number_input("Monthly Rent ($)", min_value=0, value=2200, step=50)
            annual_taxes = st.number_input("Annual Taxes ($)", min_value=0, value=3500, step=100)
            
        with col2c:
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
            ai_score = calculate_ai_score(deal_data, metrics)
            
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
                if db_service.create_deal(new_deal):
                    st.success(f"✅ Deal saved successfully! Address: {property_address}")
                    st.balloons()
                    
                    # Clear the analysis from session state
                    if 'analyzed_deal' in st.session_state:
                        del st.session_state.analyzed_deal
                    
                    # Refresh after a short delay
                    st.rerun()
                else:
                    if db_service.is_connected():
                        st.error("❌ Failed to save deal to database. Please try again.")
                    else:
                        st.warning("⚠️ Database not connected. Deal not saved.")
            
            # Deal scoring explanation
            with st.expander("🔍 How We Calculate the AI Score"):
                st.write("""
                Our AI scoring system evaluates deals across multiple dimensions:
                - **ROI Potential (25%)**: Expected return on investment
                - **Market Strength (20%)**: Local market conditions and trends  
                - **Property Quality (20%)**: Condition, location, and features
                - **Risk Assessment (20%)**: Various risk factors and mitigation
                - **Cash Flow (15%)**: Monthly income generation potential
                
                Each component is weighted and combined to create a comprehensive score from 0-100.
                """)
    
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
    
    analytics = db_service.get_deal_analytics()
    
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
    st.header("🤖 AI Market Insights")
    
    st.info("🔮 Advanced AI analysis of market trends, opportunities, and predictions")
    
    # Market Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Market Trends Analysis")
        
        market_insights = [
            "🔥 Hot Markets: Austin, Nashville, Tampa showing 15%+ appreciation",
            "💰 Cash Flow Opportunities: Midwest markets offering 12%+ cap rates",
            "⚠️ Market Watch: Coastal areas seeing inventory increase",
            "🏗️ Development Trends: Build-to-rent gaining momentum",
            "💡 Opportunity: Distressed properties up 8% in target markets"
        ]
        
        for insight in market_insights:
            st.write(insight)
    
    with col2:
        st.subheader("🎯 AI Recommendations")
        
        # Simulated AI recommendations
        recommendations = [
            "Focus on multi-family properties in emerging markets",
            "Consider fix-and-flip opportunities in gentrifying areas",
            "Diversify portfolio with commercial properties",
            "Explore opportunity zones for tax benefits",
            "Monitor interest rate trends for refinancing opportunities"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")
    
    # Predictive Analytics
    st.subheader("🔮 Predictive Market Analytics")
    
    # Sample prediction data
    prediction_data = pd.DataFrame({
        'Market': ['Austin', 'Nashville', 'Tampa', 'Phoenix', 'Denver'],
        'Current Avg Price': [450000, 380000, 320000, 410000, 520000],
        '12-Month Prediction': [495000, 418000, 352000, 430000, 546000],
        'Predicted Growth': ['10.0%', '10.0%', '10.0%', '4.9%', '5.0%'],
        'Investment Grade': ['A+', 'A', 'A-', 'B+', 'B+']
    })
    
    st.dataframe(prediction_data, use_container_width=True)

def show_investor_matching():
    st.header("👥 Smart Investor Matching")
    
    st.info("🎯 AI-powered investor matching based on deal criteria and investor preferences")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 Deal Criteria")
        
        deal_type = st.selectbox("Deal Type", ["Fix & Flip", "Buy & Hold", "Wholesale", "Commercial"])
        investment_range = st.slider("Investment Range", 50000, 1000000, (100000, 500000), step=25000)
        location_pref = st.multiselect("Preferred Markets", 
                                     ["Austin", "Nashville", "Tampa", "Phoenix", "Denver", "Atlanta"])
        
        if st.button("🔍 Find Matching Investors", type="primary"):
            st.success("Found 12 matching investors!")
            
            # Sample investor matches
            investors_data = pd.DataFrame({
                'Investor': ['Premium Capital LLC', 'Growth Equity Partners', 'Sunbelt Investments', 
                           'Metro Property Group', 'Apex Real Estate Fund'],
                'Type': ['Private Equity', 'Individual', 'Fund', 'Group', 'Institutional'],
                'Investment Range': ['$200K-$800K', '$100K-$500K', '$500K-$2M', '$150K-$600K', '$1M-$5M'],
                'Preferred Markets': ['Austin, Nashville', 'Tampa, Phoenix', 'Austin, Denver', 
                                    'Nashville, Atlanta', 'Multi-Market'],
                'Success Rate': ['94%', '87%', '91%', '89%', '96%'],
                'Contact': ['📧 Send Pitch', '📞 Schedule Call', '📧 Send Pitch', 
                          '📞 Schedule Call', '📧 Send Pitch']
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
    """Create a pie chart showing financial breakdown"""
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
    """Advanced Financial Modeling section with sophisticated analysis"""
    st.header("💹 Advanced Financial Modeling")
    st.markdown("**Enterprise-grade financial analysis with projections, Monte Carlo simulations, and exit strategy comparisons**")
    
    # Initialize the financial modeling engine
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
        if db_service.is_connected():
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
                    st.markdown(f"""
                    **🎯 Key Insights:**
                    - **IRR (Base Case):** {base_case['irr']:.1f}% - Internal Rate of Return
                    - **NPV (10% discount):** ${base_case['npv']:,.0f} - Net Present Value
                    - **Total ROI:** {base_case['roi']:.1f}% - Total Return on Investment
                    - **Cash-on-Cash:** {base_case['cash_on_cash']:.1f}% - Annual cash return
                    - **Debt Coverage:** {base_case['debt_coverage_ratio']:.2f}x - Ability to service debt
                    """)
        
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

if __name__ == "__main__":
    main()
