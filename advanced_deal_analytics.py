"""
Advanced Deal Analytics System for NXTRIX Platform
Phase 4: Comprehensive deal pipeline analytics with predictive modeling and market intelligence
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sqlite3
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import requests
import time
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class DealStage(Enum):
    """Deal pipeline stages"""
    LEAD = "Lead Generated"
    QUALIFIED = "Lead Qualified"
    ANALYSIS = "Under Analysis"
    OFFER_PREP = "Offer Preparation"
    OFFER_SUBMITTED = "Offer Submitted"
    NEGOTIATION = "In Negotiation"
    UNDER_CONTRACT = "Under Contract"
    DUE_DILIGENCE = "Due Diligence"
    CLOSING = "Closing Process"
    CLOSED = "Closed Deal"
    LOST = "Lost Deal"

class MarketTrend(Enum):
    """Market trend indicators"""
    STRONG_BUYER = "Strong Buyer's Market"
    BUYER = "Buyer's Market"
    BALANCED = "Balanced Market"
    SELLER = "Seller's Market"
    STRONG_SELLER = "Strong Seller's Market"

@dataclass
class DealAnalytics:
    """Enhanced deal analytics data structure"""
    deal_id: str
    property_address: str
    deal_stage: DealStage
    entry_date: datetime
    last_updated: datetime
    purchase_price: float
    estimated_arv: float
    rehab_costs: float
    holding_costs: float
    acquisition_costs: float
    expected_profit: float
    profit_margin: float
    deal_score: float
    time_in_stage: int
    conversion_probability: float
    market_conditions: Dict[str, Any]
    competitor_analysis: Dict[str, Any]
    financial_metrics: Dict[str, float]
    risk_factors: List[str]
    opportunity_score: float

@dataclass
class MarketIntelligence:
    """Market intelligence data structure"""
    area_code: str
    area_name: str
    median_home_price: float
    price_per_sqft: float
    days_on_market: int
    inventory_levels: int
    market_trend: MarketTrend
    price_trend_6m: float
    rental_yield: float
    population_growth: float
    employment_rate: float
    crime_index: float
    school_ratings: float
    walkability_score: int
    last_updated: datetime

class AdvancedDealAnalytics:
    """Advanced Deal Analytics Engine"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.initialize_analytics_tables()
        
    def initialize_analytics_tables(self):
        """Initialize analytics database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Deal analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deal_analytics (
                id TEXT PRIMARY KEY,
                property_address TEXT,
                deal_stage TEXT,
                entry_date TEXT,
                last_updated TEXT,
                purchase_price REAL,
                estimated_arv REAL,
                rehab_costs REAL,
                holding_costs REAL,
                acquisition_costs REAL,
                expected_profit REAL,
                profit_margin REAL,
                deal_score REAL,
                time_in_stage INTEGER,
                conversion_probability REAL,
                market_data TEXT,
                competitor_data TEXT,
                financial_metrics TEXT,
                risk_factors TEXT,
                opportunity_score REAL
            )
        ''')
        
        # Market intelligence table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_intelligence (
                area_code TEXT PRIMARY KEY,
                area_name TEXT,
                median_home_price REAL,
                price_per_sqft REAL,
                days_on_market INTEGER,
                inventory_levels INTEGER,
                market_trend TEXT,
                price_trend_6m REAL,
                rental_yield REAL,
                population_growth REAL,
                employment_rate REAL,
                crime_index REAL,
                school_ratings REAL,
                walkability_score INTEGER,
                last_updated TEXT
            )
        ''')
        
        # Deal stage history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deal_stage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deal_id TEXT,
                from_stage TEXT,
                to_stage TEXT,
                stage_date TEXT,
                time_in_previous_stage INTEGER,
                notes TEXT,
                FOREIGN KEY (deal_id) REFERENCES deal_analytics (id)
            )
        ''')
        
        # Market predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_code TEXT,
                prediction_date TEXT,
                predicted_price_change REAL,
                confidence_score REAL,
                prediction_horizon INTEGER,
                model_version TEXT,
                features_used TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def calculate_advanced_deal_score(self, deal_data: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Calculate advanced deal score with detailed breakdown"""
        
        # Financial metrics (40% weight)
        profit_margin = deal_data.get('profit_margin', 0)
        roi = deal_data.get('roi', 0)
        cash_flow = deal_data.get('monthly_cash_flow', 0)
        
        financial_score = min(100, (
            (profit_margin * 2) +  # 20% profit = 40 points
            (roi * 1.5) +          # 20% ROI = 30 points  
            (cash_flow / 10)       # $300 cash flow = 30 points
        ))
        
        # Market conditions (25% weight)
        market_trend = deal_data.get('market_trend', 'BALANCED')
        days_on_market = deal_data.get('days_on_market', 30)
        inventory_levels = deal_data.get('inventory_levels', 5)
        
        market_score = 50  # Base score
        if market_trend == 'BUYER':
            market_score += 30
        elif market_trend == 'STRONG_BUYER':
            market_score += 50
        elif market_trend == 'SELLER':
            market_score -= 20
        elif market_trend == 'STRONG_SELLER':
            market_score -= 40
            
        # Adjust for market dynamics
        market_score += max(0, (60 - days_on_market) / 2)  # Bonus for quick-moving market
        market_score += max(0, (6 - inventory_levels) * 5)  # Bonus for low inventory
        
        # Property fundamentals (20% weight)
        property_condition = deal_data.get('property_condition', 3)  # 1-5 scale
        location_score = deal_data.get('location_score', 3)  # 1-5 scale
        school_rating = deal_data.get('school_rating', 5)  # 1-10 scale
        
        property_score = (
            (property_condition * 10) +  # Max 50 points
            (location_score * 10) +      # Max 50 points
            (school_rating * 5)          # Max 50 points
        ) / 1.5  # Normalize to 100
        
        # Risk assessment (10% weight)
        risk_factors = deal_data.get('risk_factors', [])
        risk_score = 100
        for risk in risk_factors:
            if 'high' in risk.lower():
                risk_score -= 20
            elif 'medium' in risk.lower():
                risk_score -= 10
            elif 'low' in risk.lower():
                risk_score -= 5
        
        # Exit strategy (5% weight)
        exit_strategies = deal_data.get('exit_strategies', [])
        exit_score = len(exit_strategies) * 20  # 20 points per strategy
        exit_score = min(100, exit_score)
        
        # Calculate weighted final score
        final_score = (
            (financial_score * 0.40) +
            (market_score * 0.25) +
            (property_score * 0.20) +
            (risk_score * 0.10) +
            (exit_score * 0.05)
        )
        
        # Score breakdown
        breakdown = {
            'financial_score': financial_score,
            'market_score': market_score,
            'property_score': property_score,
            'risk_score': risk_score,
            'exit_score': exit_score,
            'final_score': final_score
        }
        
        return min(100, max(0, final_score)), breakdown
    
    def predict_deal_conversion(self, deal_data: Dict[str, Any]) -> Tuple[float, str]:
        """Predict probability of deal conversion using ML model"""
        
        # Feature engineering for ML model
        features = {
            'deal_score': deal_data.get('deal_score', 50),
            'profit_margin': deal_data.get('profit_margin', 0),
            'time_in_pipeline': deal_data.get('time_in_pipeline', 0),
            'market_conditions': self._encode_market_conditions(deal_data.get('market_trend', 'BALANCED')),
            'property_price': deal_data.get('purchase_price', 0),
            'rehab_percentage': deal_data.get('rehab_costs', 0) / max(deal_data.get('purchase_price', 1), 1),
            'days_on_market': deal_data.get('days_on_market', 30),
            'location_score': deal_data.get('location_score', 3)
        }
        
        # Simple rule-based prediction (in production, this would use trained ML model)
        base_probability = 0.3  # 30% base conversion rate
        
        # Adjust based on deal score
        score_adjustment = (features['deal_score'] - 50) * 0.01
        
        # Adjust based on profit margin
        profit_adjustment = min(0.3, features['profit_margin'] * 0.02)
        
        # Adjust based on time in pipeline (negative effect of time)
        time_penalty = min(0.2, features['time_in_pipeline'] * 0.01)
        
        # Market conditions adjustment
        market_adjustment = (features['market_conditions'] - 3) * 0.05
        
        # Calculate final probability
        conversion_probability = (
            base_probability + 
            score_adjustment + 
            profit_adjustment - 
            time_penalty + 
            market_adjustment
        )
        
        conversion_probability = max(0.05, min(0.95, conversion_probability))
        
        # Generate prediction explanation
        if conversion_probability >= 0.7:
            explanation = "High conversion probability - strong deal metrics and favorable conditions"
        elif conversion_probability >= 0.5:
            explanation = "Moderate conversion probability - decent deal with some concerns"
        elif conversion_probability >= 0.3:
            explanation = "Low conversion probability - significant challenges or weak metrics"
        else:
            explanation = "Very low conversion probability - major issues identified"
        
        return conversion_probability, explanation
    
    def _encode_market_conditions(self, market_trend: str) -> int:
        """Encode market conditions for ML model"""
        mapping = {
            'STRONG_BUYER': 1,
            'BUYER': 2,
            'BALANCED': 3,
            'SELLER': 4,
            'STRONG_SELLER': 5
        }
        return mapping.get(market_trend, 3)
    
    def get_market_intelligence(self, zip_code: str) -> MarketIntelligence:
        """Get market intelligence for specific area"""
        
        # In production, this would connect to real market data APIs
        # For now, generating realistic sample data
        
        sample_data = {
            'area_code': zip_code,
            'area_name': f"Market Area {zip_code}",
            'median_home_price': np.random.normal(350000, 75000),
            'price_per_sqft': np.random.normal(180, 40),
            'days_on_market': np.random.randint(15, 60),
            'inventory_levels': np.random.randint(2, 8),
            'market_trend': np.random.choice(list(MarketTrend)),
            'price_trend_6m': np.random.normal(5.2, 3.0),
            'rental_yield': np.random.normal(8.5, 2.0),
            'population_growth': np.random.normal(2.1, 1.5),
            'employment_rate': np.random.normal(95.2, 2.0),
            'crime_index': np.random.normal(3.2, 1.0),
            'school_ratings': np.random.normal(7.5, 1.5),
            'walkability_score': np.random.randint(40, 95),
            'last_updated': datetime.now()
        }
        
        return MarketIntelligence(**sample_data)
    
    def generate_pipeline_analytics(self, deals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive pipeline analytics"""
        
        if not deals:
            return {}
        
        # Convert deals to DataFrame for analysis
        df = pd.DataFrame(deals)
        
        # Pipeline stage analysis
        stage_counts = df['deal_stage'].value_counts()
        stage_conversion = self._calculate_stage_conversion_rates(df)
        
        # Time in stage analysis
        avg_time_by_stage = df.groupby('deal_stage')['time_in_stage'].mean()
        
        # Financial metrics
        total_pipeline_value = df['expected_profit'].sum()
        avg_deal_size = df['purchase_price'].mean()
        avg_profit_margin = df['profit_margin'].mean()
        
        # Velocity metrics
        deals_by_month = self._calculate_monthly_velocity(df)
        conversion_trends = self._calculate_conversion_trends(df)
        
        # Risk analysis
        high_risk_deals = len(df[df['deal_score'] < 40])
        medium_risk_deals = len(df[(df['deal_score'] >= 40) & (df['deal_score'] < 70)])
        low_risk_deals = len(df[df['deal_score'] >= 70])
        
        return {
            'stage_counts': stage_counts.to_dict(),
            'stage_conversion': stage_conversion,
            'avg_time_by_stage': avg_time_by_stage.to_dict(),
            'total_pipeline_value': total_pipeline_value,
            'avg_deal_size': avg_deal_size,
            'avg_profit_margin': avg_profit_margin,
            'deals_by_month': deals_by_month,
            'conversion_trends': conversion_trends,
            'risk_distribution': {
                'high_risk': high_risk_deals,
                'medium_risk': medium_risk_deals,
                'low_risk': low_risk_deals
            }
        }
    
    def _calculate_stage_conversion_rates(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate conversion rates between pipeline stages"""
        
        stages = [stage.value for stage in DealStage]
        conversions = {}
        
        for i, stage in enumerate(stages[:-2]):  # Exclude CLOSED and LOST
            current_stage_deals = len(df[df['deal_stage'] == stage])
            if i < len(stages) - 3:  # Has next stage
                next_stage = stages[i + 1]
                next_stage_deals = len(df[df['deal_stage'] == next_stage])
                if current_stage_deals > 0:
                    conversion_rate = (next_stage_deals / current_stage_deals) * 100
                    conversions[f"{stage}_to_{next_stage}"] = conversion_rate
        
        return conversions
    
    def _calculate_monthly_velocity(self, df: pd.DataFrame) -> Dict[str, int]:
        """Calculate deal velocity by month"""
        
        df['entry_date'] = pd.to_datetime(df['entry_date'])
        monthly_counts = df.groupby(df['entry_date'].dt.to_period('M')).size()
        
        return {str(period): count for period, count in monthly_counts.items()}
    
    def _calculate_conversion_trends(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate conversion trend analysis"""
        
        total_deals = len(df)
        closed_deals = len(df[df['deal_stage'] == DealStage.CLOSED.value])
        lost_deals = len(df[df['deal_stage'] == DealStage.LOST.value])
        
        if total_deals > 0:
            win_rate = (closed_deals / total_deals) * 100
            loss_rate = (lost_deals / total_deals) * 100
        else:
            win_rate = loss_rate = 0
        
        return {
            'overall_win_rate': win_rate,
            'overall_loss_rate': loss_rate,
            'active_pipeline': total_deals - closed_deals - lost_deals
        }

def show_advanced_deal_analytics(crm):
    """Display advanced deal analytics dashboard"""
    
    st.header("📊 Advanced Deal Analytics Dashboard")
    st.markdown("*Comprehensive pipeline analytics with predictive modeling and market intelligence*")
    
    # Initialize analytics engine
    analytics = AdvancedDealAnalytics()
    
    # Get sample deal data (in production, this would come from the CRM)
    deals_data = generate_sample_deals_data(crm)
    
    if not deals_data:
        st.info("📝 No deals found. Add some deals to see comprehensive analytics!")
        return
    
    # Generate analytics
    pipeline_analytics = analytics.generate_pipeline_analytics(deals_data)
    
    # Key metrics overview
    st.subheader("🎯 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_deals = len(deals_data)
        st.metric("Total Active Deals", total_deals)
    
    with col2:
        pipeline_value = pipeline_analytics.get('total_pipeline_value', 0)
        st.metric("Pipeline Value", f"${pipeline_value:,.0f}")
    
    with col3:
        avg_profit = pipeline_analytics.get('avg_profit_margin', 0)
        st.metric("Avg Profit Margin", f"{avg_profit:.1f}%")
    
    with col4:
        win_rate = pipeline_analytics.get('conversion_trends', {}).get('overall_win_rate', 0)
        st.metric("Win Rate", f"{win_rate:.1f}%")
    
    # Pipeline visualization
    st.subheader("📈 Deal Pipeline Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pipeline funnel chart
        stage_counts = pipeline_analytics.get('stage_counts', {})
        if stage_counts:
            fig_funnel = create_pipeline_funnel(stage_counts)
            st.plotly_chart(fig_funnel, use_container_width=True)
    
    with col2:
        # Deal score distribution
        scores = [deal['deal_score'] for deal in deals_data]
        fig_scores = create_deal_score_distribution(scores)
        st.plotly_chart(fig_scores, use_container_width=True)
    
    # Market intelligence section
    st.subheader("🌍 Market Intelligence")
    
    # Sample market data for demonstration
    sample_markets = ['12345', '23456', '34567', '45678']
    market_data = []
    
    for zip_code in sample_markets:
        market_intel = analytics.get_market_intelligence(zip_code)
        market_data.append({
            'Area': market_intel.area_code,
            'Median Price': f"${market_intel.median_home_price:,.0f}",
            'Price/SqFt': f"${market_intel.price_per_sqft:.0f}",
            'Days on Market': market_intel.days_on_market,
            'Market Trend': market_intel.market_trend.value,
            'Price Trend (6M)': f"{market_intel.price_trend_6m:+.1f}%",
            'Rental Yield': f"{market_intel.rental_yield:.1f}%"
        })
    
    df_market = pd.DataFrame(market_data)
    st.dataframe(df_market, use_container_width=True)
    
    # Predictive analytics section
    st.subheader("🔮 Predictive Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Deal Conversion Predictions**")
        for deal in deals_data[:5]:  # Show top 5 deals
            prob, explanation = analytics.predict_deal_conversion(deal)
            color = "🟢" if prob >= 0.7 else "🟡" if prob >= 0.4 else "🔴"
            st.write(f"{color} {deal['property_address']}: {prob:.1%} - {explanation}")
    
    with col2:
        st.markdown("**Market Trend Predictions**")
        st.info("📈 Market predictions indicate continued buyer-favorable conditions")
        st.info("🏠 Inventory levels expected to remain low through Q4")
        st.info("💰 Price appreciation forecast: 3-5% annually")
        st.info("🎯 Best opportunities in emerging neighborhoods")
    
    # Detailed analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Pipeline Details", "💰 Financial Analytics", "⏱️ Time Analytics", "🎯 Opportunity Analysis"])
    
    with tab1:
        show_pipeline_details(pipeline_analytics, deals_data)
    
    with tab2:
        show_financial_analytics(deals_data)
    
    with tab3:
        show_time_analytics(pipeline_analytics)
    
    with tab4:
        show_opportunity_analysis(deals_data, analytics)

def generate_sample_deals_data(crm) -> List[Dict[str, Any]]:
    """Generate sample deals data for analytics"""
    
    sample_deals = []
    stages = [stage.value for stage in DealStage]
    
    for i in range(20):  # Generate 20 sample deals
        deal = {
            'deal_id': f"DEAL_{i+1:03d}",
            'property_address': f"{100 + i*10} Sample St, City, ST",
            'deal_stage': np.random.choice(stages[:-2]),  # Exclude CLOSED/LOST for active pipeline
            'entry_date': datetime.now() - timedelta(days=np.random.randint(1, 180)),
            'last_updated': datetime.now() - timedelta(days=np.random.randint(1, 30)),
            'purchase_price': np.random.randint(80000, 400000),
            'estimated_arv': 0,
            'rehab_costs': np.random.randint(10000, 50000),
            'holding_costs': np.random.randint(2000, 8000),
            'acquisition_costs': np.random.randint(3000, 10000),
            'expected_profit': 0,
            'profit_margin': np.random.uniform(10, 35),
            'deal_score': np.random.uniform(30, 90),
            'time_in_stage': np.random.randint(1, 60),
            'conversion_probability': np.random.uniform(0.2, 0.8),
            'market_trend': np.random.choice(['BUYER', 'BALANCED', 'SELLER']),
            'days_on_market': np.random.randint(10, 90),
            'location_score': np.random.randint(1, 5),
            'roi': np.random.uniform(12, 28),
            'monthly_cash_flow': np.random.randint(200, 800)
        }
        
        # Calculate derived fields
        deal['estimated_arv'] = deal['purchase_price'] * np.random.uniform(1.2, 1.8)
        deal['expected_profit'] = deal['estimated_arv'] - deal['purchase_price'] - deal['rehab_costs'] - deal['holding_costs']
        deal['time_in_pipeline'] = (datetime.now() - deal['entry_date']).days
        
        sample_deals.append(deal)
    
    return sample_deals

def create_pipeline_funnel(stage_counts: Dict[str, int]) -> go.Figure:
    """Create pipeline funnel visualization"""
    
    stages = list(stage_counts.keys())
    counts = list(stage_counts.values())
    
    fig = go.Figure(go.Funnel(
        y=stages,
        x=counts,
        textinfo="value+percent initial"
    ))
    
    fig.update_layout(
        title="Deal Pipeline Funnel",
        height=400
    )
    
    return fig

def create_deal_score_distribution(scores: List[float]) -> go.Figure:
    """Create deal score distribution chart"""
    
    fig = go.Figure(data=[go.Histogram(
        x=scores,
        nbinsx=20,
        marker_color='lightblue',
        opacity=0.7
    )])
    
    fig.update_layout(
        title="Deal Score Distribution",
        xaxis_title="Deal Score",
        yaxis_title="Number of Deals",
        height=400
    )
    
    return fig

def show_pipeline_details(analytics: Dict[str, Any], deals: List[Dict[str, Any]]):
    """Show detailed pipeline analysis"""
    
    st.markdown("### 📋 Pipeline Stage Analysis")
    
    # Stage performance table
    stage_data = []
    for stage, count in analytics.get('stage_counts', {}).items():
        avg_time = analytics.get('avg_time_by_stage', {}).get(stage, 0)
        stage_data.append({
            'Stage': stage,
            'Deal Count': count,
            'Avg Time (Days)': f"{avg_time:.1f}",
            'Stage Health': "🟢 Healthy" if avg_time <= 30 else "🟡 Monitor" if avg_time <= 60 else "🔴 Bottleneck"
        })
    
    df_stages = pd.DataFrame(stage_data)
    st.dataframe(df_stages, use_container_width=True)

def show_financial_analytics(deals: List[Dict[str, Any]]):
    """Show financial analytics"""
    
    st.markdown("### 💰 Financial Performance Analysis")
    
    # Financial metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_investment = sum([deal['purchase_price'] + deal['rehab_costs'] for deal in deals])
        st.metric("Total Investment", f"${total_investment:,.0f}")
    
    with col2:
        total_expected_profit = sum([deal['expected_profit'] for deal in deals])
        st.metric("Expected Profit", f"${total_expected_profit:,.0f}")
    
    with col3:
        avg_roi = np.mean([deal['roi'] for deal in deals])
        st.metric("Average ROI", f"{avg_roi:.1f}%")

def show_time_analytics(analytics: Dict[str, Any]):
    """Show time-based analytics"""
    
    st.markdown("### ⏱️ Time & Velocity Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Average Time by Stage**")
        avg_times = analytics.get('avg_time_by_stage', {})
        for stage, time_days in avg_times.items():
            st.write(f"• {stage}: {time_days:.1f} days")
    
    with col2:
        st.markdown("**Velocity Trends**")
        monthly_deals = analytics.get('deals_by_month', {})
        if monthly_deals:
            fig = px.line(
                x=list(monthly_deals.keys()),
                y=list(monthly_deals.values()),
                title="Deal Flow by Month"
            )
            st.plotly_chart(fig, use_container_width=True)

def show_opportunity_analysis(deals: List[Dict[str, Any]], analytics):
    """Show opportunity analysis"""
    
    st.markdown("### 🎯 Opportunity Analysis")
    
    # High-opportunity deals
    high_score_deals = [deal for deal in deals if deal['deal_score'] >= 75]
    
    if high_score_deals:
        st.markdown("**🔥 High-Opportunity Deals**")
        for deal in high_score_deals[:5]:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"📍 {deal['property_address']}")
            with col2:
                st.write(f"💯 Score: {deal['deal_score']:.1f}")
            with col3:
                st.write(f"💰 Profit: ${deal['expected_profit']:,.0f}")
    
    # Improvement recommendations
    st.markdown("**📈 Improvement Recommendations**")
    st.info("🎯 Focus on deals with scores above 70 for highest success probability")
    st.info("⏰ Reduce time in 'Under Analysis' stage to improve velocity")
    st.info("🏠 Target buyer's market areas for better deal flow")
    st.info("📊 Increase average deal size to improve overall ROI")

if __name__ == "__main__":
    st.set_page_config(
        page_title="Advanced Deal Analytics",
        page_icon="📊",
        layout="wide"
    )
    
    # Mock CRM for testing
    class MockCRM:
        def __init__(self):
            self.deals = []
    
    mock_crm = MockCRM()
    show_advanced_deal_analytics(mock_crm)