"""
Market Intelligence Module for NXTRIX Advanced Analytics
Real-time market data integration and predictive market analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import sqlite3
import warnings
warnings.filterwarnings('ignore')

class MarketCondition(Enum):
    """Market condition classifications"""
    STRONG_BUYERS = "Strong Buyer's Market"
    BUYERS = "Buyer's Market"
    BALANCED = "Balanced Market"
    SELLERS = "Seller's Market"
    STRONG_SELLERS = "Strong Seller's Market"

class PropertyCategory(Enum):
    """Property category types"""
    SINGLE_FAMILY = "Single Family"
    CONDOS = "Condominiums"
    TOWNHOMES = "Townhomes"
    MULTI_FAMILY = "Multi-Family"
    LUXURY = "Luxury Properties"

@dataclass
class MarketMetrics:
    """Market metrics data structure"""
    area_name: str
    zip_code: str
    median_price: float
    price_per_sqft: float
    days_on_market: int
    months_of_inventory: float
    list_to_sale_ratio: float
    price_trend_30d: float
    price_trend_90d: float
    price_trend_1y: float
    sales_volume: int
    new_listings: int
    pending_sales: int
    market_condition: MarketCondition
    last_updated: datetime

@dataclass
class NeighborhoodInsights:
    """Neighborhood insights and amenities"""
    area_name: str
    walkability_score: int
    transit_score: int
    bike_score: int
    crime_index: float
    school_ratings: Dict[str, float]
    employment_rate: float
    population_growth: float
    median_income: float
    rental_vacancy_rate: float
    rental_yield: float
    development_projects: List[str]
    amenities: List[str]

class MarketIntelligenceEngine:
    """Advanced market intelligence and analysis engine"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.initialize_market_tables()
    
    def initialize_market_tables(self):
        """Initialize market intelligence database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Market metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_name TEXT,
                zip_code TEXT,
                median_price REAL,
                price_per_sqft REAL,
                days_on_market INTEGER,
                months_of_inventory REAL,
                list_to_sale_ratio REAL,
                price_trend_30d REAL,
                price_trend_90d REAL,
                price_trend_1y REAL,
                sales_volume INTEGER,
                new_listings INTEGER,
                pending_sales INTEGER,
                market_condition TEXT,
                last_updated TEXT,
                UNIQUE(zip_code, last_updated)
            )
        ''')
        
        # Neighborhood insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS neighborhood_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_name TEXT,
                zip_code TEXT,
                walkability_score INTEGER,
                transit_score INTEGER,
                bike_score INTEGER,
                crime_index REAL,
                school_ratings TEXT,
                employment_rate REAL,
                population_growth REAL,
                median_income REAL,
                rental_vacancy_rate REAL,
                rental_yield REAL,
                development_projects TEXT,
                amenities TEXT,
                last_updated TEXT,
                UNIQUE(zip_code)
            )
        ''')
        
        # Market predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zip_code TEXT,
                prediction_date TEXT,
                horizon_months INTEGER,
                predicted_price_change REAL,
                confidence_interval_low REAL,
                confidence_interval_high REAL,
                market_condition_prediction TEXT,
                key_factors TEXT,
                confidence_score REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_market_metrics(self, zip_code: str) -> MarketMetrics:
        """Get current market metrics for area"""
        
        # In production, this would integrate with real APIs like:
        # - MLS data feeds
        # - Zillow API
        # - Realtor.com API
        # - CoreLogic API
        # For demo, generating realistic sample data
        
        return self._generate_sample_market_data(zip_code)
    
    def get_neighborhood_insights(self, zip_code: str) -> NeighborhoodInsights:
        """Get neighborhood insights and amenities"""
        
        # In production, this would integrate with:
        # - Walk Score API
        # - Crime data APIs
        # - School district APIs
        # - Census data
        # - Local development databases
        
        return self._generate_sample_neighborhood_data(zip_code)
    
    def _generate_sample_market_data(self, zip_code: str) -> MarketMetrics:
        """Generate realistic sample market data"""
        
        np.random.seed(hash(zip_code) % 2**32)  # Consistent data for same zip
        
        # Base market metrics with realistic variations
        base_price = np.random.normal(350000, 100000)
        base_price = max(150000, base_price)  # Minimum price floor
        
        market_data = MarketMetrics(
            area_name=f"Market Area {zip_code}",
            zip_code=zip_code,
            median_price=base_price,
            price_per_sqft=base_price / np.random.normal(1800, 300),
            days_on_market=np.random.randint(15, 75),
            months_of_inventory=np.random.uniform(1.5, 8.0),
            list_to_sale_ratio=np.random.uniform(0.92, 1.08),
            price_trend_30d=np.random.normal(0.5, 2.0),
            price_trend_90d=np.random.normal(2.0, 4.0),
            price_trend_1y=np.random.normal(8.0, 6.0),
            sales_volume=np.random.randint(50, 300),
            new_listings=np.random.randint(40, 250),
            pending_sales=np.random.randint(30, 200),
            market_condition=self._determine_market_condition(
                np.random.uniform(1.5, 8.0),  # months of inventory
                np.random.randint(15, 75)     # days on market
            ),
            last_updated=datetime.now()
        )
        
        return market_data
    
    def _generate_sample_neighborhood_data(self, zip_code: str) -> NeighborhoodInsights:
        """Generate realistic sample neighborhood data"""
        
        np.random.seed(hash(zip_code + "neighborhood") % 2**32)
        
        return NeighborhoodInsights(
            area_name=f"Neighborhood {zip_code}",
            walkability_score=np.random.randint(30, 95),
            transit_score=np.random.randint(20, 85),
            bike_score=np.random.randint(25, 90),
            crime_index=np.random.uniform(1.0, 8.0),
            school_ratings={
                "elementary": np.random.uniform(6.0, 10.0),
                "middle": np.random.uniform(5.5, 9.5),
                "high": np.random.uniform(5.0, 9.0)
            },
            employment_rate=np.random.uniform(92.0, 98.0),
            population_growth=np.random.uniform(-1.0, 8.0),
            median_income=np.random.normal(65000, 25000),
            rental_vacancy_rate=np.random.uniform(2.0, 12.0),
            rental_yield=np.random.uniform(6.0, 12.0),
            development_projects=[
                "New Shopping Complex (2024)",
                "Transit Station Expansion",
                "Mixed-Use Development"
            ] if np.random.random() > 0.5 else [],
            amenities=[
                "Parks & Recreation",
                "Shopping Centers",
                "Restaurants",
                "Public Transportation",
                "Healthcare Facilities",
                "Schools"
            ]
        )
    
    def _determine_market_condition(self, months_inventory: float, days_on_market: int) -> MarketCondition:
        """Determine market condition based on key metrics"""
        
        if months_inventory <= 2.0 and days_on_market <= 20:
            return MarketCondition.STRONG_SELLERS
        elif months_inventory <= 3.0 and days_on_market <= 30:
            return MarketCondition.SELLERS
        elif months_inventory <= 5.0 and days_on_market <= 45:
            return MarketCondition.BALANCED
        elif months_inventory <= 7.0 and days_on_market <= 60:
            return MarketCondition.BUYERS
        else:
            return MarketCondition.STRONG_BUYERS
    
    def generate_market_predictions(self, zip_code: str, horizon_months: int = 12) -> Dict[str, Any]:
        """Generate market predictions using trend analysis"""
        
        current_metrics = self.get_market_metrics(zip_code)
        
        # Simple trend-based prediction (in production, would use ML models)
        base_trend = current_metrics.price_trend_1y / 100
        
        # Adjust for market conditions
        condition_multiplier = {
            MarketCondition.STRONG_SELLERS: 1.2,
            MarketCondition.SELLERS: 1.1,
            MarketCondition.BALANCED: 1.0,
            MarketCondition.BUYERS: 0.9,
            MarketCondition.STRONG_BUYERS: 0.8
        }
        
        adjusted_trend = base_trend * condition_multiplier[current_metrics.market_condition]
        
        # Project forward
        predicted_change = adjusted_trend * (horizon_months / 12)
        confidence_score = max(0.5, min(0.95, 0.8 - abs(predicted_change) * 0.1))
        
        # Confidence interval
        margin_error = abs(predicted_change) * 0.3
        confidence_low = predicted_change - margin_error
        confidence_high = predicted_change + margin_error
        
        return {
            'predicted_price_change': predicted_change * 100,  # Convert to percentage
            'confidence_score': confidence_score,
            'confidence_interval': (confidence_low * 100, confidence_high * 100),
            'key_factors': [
                f"Current market condition: {current_metrics.market_condition.value}",
                f"Inventory levels: {current_metrics.months_of_inventory:.1f} months",
                f"Recent price trend: {current_metrics.price_trend_1y:+.1f}%",
                f"Market velocity: {current_metrics.days_on_market} days on market"
            ],
            'investment_recommendation': self._generate_investment_recommendation(current_metrics, predicted_change)
        }
    
    def _generate_investment_recommendation(self, metrics: MarketMetrics, predicted_change: float) -> str:
        """Generate investment recommendation based on market analysis"""
        
        if predicted_change > 0.08 and metrics.market_condition in [MarketCondition.BALANCED, MarketCondition.BUYERS]:
            return "🟢 Strong Buy - Favorable conditions with growth potential"
        elif predicted_change > 0.04 and metrics.days_on_market < 45:
            return "🟡 Buy - Positive outlook with moderate growth expected"
        elif predicted_change > -0.02 and metrics.market_condition == MarketCondition.BALANCED:
            return "🟡 Hold/Watch - Stable market, monitor for opportunities"
        elif predicted_change < -0.05 or metrics.market_condition == MarketCondition.STRONG_SELLERS:
            return "🔴 Caution - Consider waiting for better conditions"
        else:
            return "🟡 Neutral - Mixed signals, evaluate individual deals carefully"
    
    def compare_markets(self, zip_codes: List[str]) -> pd.DataFrame:
        """Compare multiple markets side by side"""
        
        comparison_data = []
        
        for zip_code in zip_codes:
            metrics = self.get_market_metrics(zip_code)
            neighborhood = self.get_neighborhood_insights(zip_code)
            predictions = self.generate_market_predictions(zip_code)
            
            comparison_data.append({
                'ZIP Code': zip_code,
                'Area': metrics.area_name,
                'Median Price': f"${metrics.median_price:,.0f}",
                'Price/SqFt': f"${metrics.price_per_sqft:.0f}",
                'Days on Market': metrics.days_on_market,
                'Market Condition': metrics.market_condition.value,
                '1Y Price Trend': f"{metrics.price_trend_1y:+.1f}%",
                'Predicted Change': f"{predictions['predicted_price_change']:+.1f}%",
                'Investment Grade': predictions['investment_recommendation'],
                'Walkability': neighborhood.walkability_score,
                'School Rating': f"{np.mean(list(neighborhood.school_ratings.values())):.1f}",
                'Crime Index': f"{neighborhood.crime_index:.1f}",
                'Rental Yield': f"{neighborhood.rental_yield:.1f}%"
            })
        
        return pd.DataFrame(comparison_data)

def show_market_intelligence():
    """Display market intelligence dashboard"""
    
    st.header("🌍 Market Intelligence Dashboard")
    st.markdown("*Real-time market analysis and predictive insights*")
    
    # Initialize market intelligence engine
    market_engine = MarketIntelligenceEngine()
    
    # Market analysis input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        zip_codes_input = st.text_input(
            "Enter ZIP codes (comma-separated)",
            value="12345, 23456, 34567",
            help="Enter ZIP codes to analyze market conditions"
        )
    
    with col2:
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Single Market Deep Dive", "Multi-Market Comparison", "Trend Analysis"]
        )
    
    if zip_codes_input:
        zip_codes = [zip_code.strip() for zip_code in zip_codes_input.split(",")]
        
        if analysis_type == "Single Market Deep Dive" and len(zip_codes) >= 1:
            show_single_market_analysis(market_engine, zip_codes[0])
        
        elif analysis_type == "Multi-Market Comparison":
            show_multi_market_comparison(market_engine, zip_codes)
        
        elif analysis_type == "Trend Analysis":
            show_trend_analysis(market_engine, zip_codes)

def show_single_market_analysis(engine: MarketIntelligenceEngine, zip_code: str):
    """Show detailed analysis for a single market"""
    
    st.subheader(f"📊 Deep Dive Analysis - ZIP {zip_code}")
    
    # Get market data
    metrics = engine.get_market_metrics(zip_code)
    neighborhood = engine.get_neighborhood_insights(zip_code)
    predictions = engine.generate_market_predictions(zip_code)
    
    # Key metrics overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Median Price", f"${metrics.median_price:,.0f}")
        st.metric("Price/SqFt", f"${metrics.price_per_sqft:.0f}")
    
    with col2:
        st.metric("Days on Market", f"{metrics.days_on_market}")
        st.metric("Months Inventory", f"{metrics.months_of_inventory:.1f}")
    
    with col3:
        trend_color = "normal" if abs(metrics.price_trend_1y) < 5 else "inverse" if metrics.price_trend_1y < 0 else "normal"
        st.metric("1Y Price Trend", f"{metrics.price_trend_1y:+.1f}%", delta=None)
        st.metric("Sales Volume", f"{metrics.sales_volume}")
    
    with col4:
        st.metric("Market Condition", metrics.market_condition.value)
        st.metric("List/Sale Ratio", f"{metrics.list_to_sale_ratio:.2f}")
    
    # Market predictions
    st.subheader("🔮 Market Predictions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        pred_change = predictions['predicted_price_change']
        color = "🟢" if pred_change > 3 else "🟡" if pred_change > -2 else "🔴"
        st.write(f"**12-Month Prediction:** {color} {pred_change:+.1f}%")
        st.write(f"**Confidence:** {predictions['confidence_score']:.0%}")
        st.write(f"**Range:** {predictions['confidence_interval'][0]:+.1f}% to {predictions['confidence_interval'][1]:+.1f}%")
    
    with col2:
        st.write("**Key Factors:**")
        for factor in predictions['key_factors']:
            st.write(f"• {factor}")
    
    st.info(f"**Investment Recommendation:** {predictions['investment_recommendation']}")
    
    # Neighborhood insights
    st.subheader("🏘️ Neighborhood Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Livability Scores**")
        st.write(f"🚶 Walkability: {neighborhood.walkability_score}/100")
        st.write(f"🚌 Transit: {neighborhood.transit_score}/100")
        st.write(f"🚴 Bike Score: {neighborhood.bike_score}/100")
        st.write(f"🛡️ Safety Index: {10 - neighborhood.crime_index:.1f}/10")
    
    with col2:
        st.write("**Economics & Demographics**")
        st.write(f"💼 Employment Rate: {neighborhood.employment_rate:.1f}%")
        st.write(f"📈 Population Growth: {neighborhood.population_growth:+.1f}%")
        st.write(f"💰 Median Income: ${neighborhood.median_income:,.0f}")
        st.write(f"🏠 Rental Yield: {neighborhood.rental_yield:.1f}%")
    
    with col3:
        st.write("**School Ratings**")
        for level, rating in neighborhood.school_ratings.items():
            st.write(f"🎓 {level.title()}: {rating:.1f}/10")
        st.write(f"🏠 Rental Vacancy: {neighborhood.rental_vacancy_rate:.1f}%")
    
    # Market trend chart
    st.subheader("📈 Price Trend Analysis")
    
    # Generate sample historical data
    dates = pd.date_range(end=datetime.now(), periods=24, freq='M')
    base_price = metrics.median_price
    
    # Simulate historical price data
    price_history = []
    for i, date in enumerate(dates):
        # Add some realistic price movement
        trend_factor = 1 + (metrics.price_trend_1y / 100) * (i / len(dates))
        noise = np.random.normal(1, 0.02)  # 2% random variation
        price = base_price * trend_factor * noise
        price_history.append(price)
    
    price_df = pd.DataFrame({
        'Date': dates,
        'Median Price': price_history
    })
    
    fig = px.line(price_df, x='Date', y='Median Price', 
                  title=f'24-Month Price Trend - ZIP {zip_code}')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def show_multi_market_comparison(engine: MarketIntelligenceEngine, zip_codes: List[str]):
    """Show comparison of multiple markets"""
    
    st.subheader("🔍 Multi-Market Comparison")
    
    if len(zip_codes) > 5:
        st.warning("⚠️ Limiting analysis to first 5 ZIP codes for optimal performance")
        zip_codes = zip_codes[:5]
    
    # Generate comparison data
    comparison_df = engine.compare_markets(zip_codes)
    
    # Display comparison table
    st.dataframe(comparison_df, use_container_width=True)
    
    # Comparison charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Price comparison
        metrics_data = []
        for zip_code in zip_codes:
            metrics = engine.get_market_metrics(zip_code)
            metrics_data.append({
                'ZIP': zip_code,
                'Median Price': metrics.median_price,
                'Days on Market': metrics.days_on_market
            })
        
        df_metrics = pd.DataFrame(metrics_data)
        
        fig_price = px.bar(df_metrics, x='ZIP', y='Median Price',
                          title='Median Price Comparison')
        st.plotly_chart(fig_price, use_container_width=True)
    
    with col2:
        # Market velocity comparison
        fig_velocity = px.bar(df_metrics, x='ZIP', y='Days on Market',
                             title='Market Velocity (Days on Market)')
        st.plotly_chart(fig_velocity, use_container_width=True)

def show_trend_analysis(engine: MarketIntelligenceEngine, zip_codes: List[str]):
    """Show trend analysis across markets"""
    
    st.subheader("📊 Market Trend Analysis")
    
    trend_data = []
    
    for zip_code in zip_codes[:3]:  # Limit for performance
        metrics = engine.get_market_metrics(zip_code)
        predictions = engine.generate_market_predictions(zip_code)
        
        trend_data.append({
            'ZIP Code': zip_code,
            'Current Trend (1Y)': metrics.price_trend_1y,
            'Predicted Trend (12M)': predictions['predicted_price_change'],
            'Market Condition': metrics.market_condition.value,
            'Confidence': predictions['confidence_score']
        })
    
    trend_df = pd.DataFrame(trend_data)
    
    # Trend comparison chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=trend_df['ZIP Code'],
        y=trend_df['Current Trend (1Y)'],
        name='Historical (1Y)',
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        x=trend_df['ZIP Code'],
        y=trend_df['Predicted Trend (12M)'],
        name='Predicted (12M)',
        marker_color='orange'
    ))
    
    fig.update_layout(
        title='Price Trend Comparison: Historical vs Predicted',
        xaxis_title='ZIP Code',
        yaxis_title='Price Change (%)',
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Trend analysis table
    st.dataframe(trend_df, use_container_width=True)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Market Intelligence",
        page_icon="🌍",
        layout="wide"
    )
    
    show_market_intelligence()