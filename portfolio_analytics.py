"""
Enhanced Portfolio Analytics Module for NXTRIX Enterprise CRM
Provides comprehensive portfolio analysis, optimization, and performance tracking
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from models import Deal, Portfolio
from database import db_service

@dataclass
class PortfolioMetrics:
    """Advanced portfolio performance metrics"""
    total_value: float
    total_invested: float
    total_roi: float
    annual_return: float
    sharpe_ratio: float
    volatility: float
    max_drawdown: float
    diversification_score: float
    risk_score: float
    liquidity_score: float

@dataclass
class PropertyPerformance:
    """Individual property performance tracking"""
    deal_id: str
    property_address: str
    purchase_price: float
    current_value: float
    monthly_rent: float
    annual_income: float
    expenses: float
    net_income: float
    roi: float
    cap_rate: float
    cash_on_cash: float
    appreciation: float
    holding_period: int  # months
    performance_grade: str

class PortfolioAnalyzer:
    """Advanced portfolio analysis and optimization engine"""
    
    def __init__(self):
        self.deals = []
        self.portfolios = []
        
    def load_portfolio_data(self) -> List[Deal]:
        """Load all deals for portfolio analysis"""
        if db_service.is_connected():
            # Load all deals from database
            self.deals = db_service.get_deals()
            # Initialize portfolios as empty list for now
            # Future enhancement: implement proper portfolio management
            self.portfolios = []
        else:
            self.deals = []
            self.portfolios = []
        return self.deals
    
    def calculate_portfolio_metrics(self, deals: List[Deal]) -> PortfolioMetrics:
        """Calculate comprehensive portfolio performance metrics"""
        if not deals:
            return PortfolioMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        # Basic calculations
        total_invested = sum(deal.purchase_price for deal in deals)
        total_current_value = sum(deal.arv if deal.arv > 0 else deal.purchase_price * 1.05 for deal in deals)
        total_annual_income = sum(deal.monthly_rent * 12 if deal.monthly_rent else 0 for deal in deals)
        
        # ROI calculations
        total_roi = ((total_current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
        
        # Estimate annual return (simplified)
        avg_holding_period = sum(self._calculate_holding_period(deal) for deal in deals) / len(deals)
        annual_return = (total_roi / max(avg_holding_period / 12, 1)) if avg_holding_period > 0 else 0
        
        # Risk metrics (simplified calculations for demo)
        property_returns = [self._calculate_property_return(deal) for deal in deals]
        volatility = np.std(property_returns) if len(property_returns) > 1 else 0
        avg_return = np.mean(property_returns) if property_returns else 0
        sharpe_ratio = (avg_return / volatility) if volatility > 0 else 0
        
        # Diversification score (based on property types, locations, etc.)
        diversification_score = self._calculate_diversification_score(deals)
        
        # Risk and liquidity scores
        risk_score = self._calculate_risk_score(deals)
        liquidity_score = self._calculate_liquidity_score(deals)
        
        # Max drawdown (simplified)
        max_drawdown = max(0, max(property_returns) - min(property_returns)) if len(property_returns) > 1 else 0
        
        return PortfolioMetrics(
            total_value=total_current_value,
            total_invested=total_invested,
            total_roi=total_roi,
            annual_return=annual_return,
            sharpe_ratio=sharpe_ratio,
            volatility=volatility,
            max_drawdown=max_drawdown,
            diversification_score=diversification_score,
            risk_score=risk_score,
            liquidity_score=liquidity_score
        )
    
    def analyze_property_performance(self, deals: List[Deal]) -> List[PropertyPerformance]:
        """Analyze individual property performance"""
        performances = []
        
        for deal in deals:
            # Calculate performance metrics
            current_value = deal.arv if deal.arv > 0 else deal.purchase_price * 1.05
            annual_income = (deal.monthly_rent * 12) if deal.monthly_rent else 0
            estimated_expenses = annual_income * 0.3  # 30% expense ratio estimate
            net_income = annual_income - estimated_expenses
            
            roi = ((current_value - deal.purchase_price) / deal.purchase_price * 100) if deal.purchase_price > 0 else 0
            cap_rate = (net_income / current_value * 100) if current_value > 0 else 0
            cash_on_cash = (net_income / deal.purchase_price * 100) if deal.purchase_price > 0 else 0
            appreciation = ((current_value - deal.purchase_price) / deal.purchase_price * 100) if deal.purchase_price > 0 else 0
            
            holding_period = self._calculate_holding_period(deal)
            performance_grade = self._calculate_performance_grade(roi, cap_rate, cash_on_cash)
            
            performances.append(PropertyPerformance(
                deal_id=deal.id,
                property_address=deal.address,
                purchase_price=deal.purchase_price,
                current_value=current_value,
                monthly_rent=deal.monthly_rent or 0,
                annual_income=annual_income,
                expenses=estimated_expenses,
                net_income=net_income,
                roi=roi,
                cap_rate=cap_rate,
                cash_on_cash=cash_on_cash,
                appreciation=appreciation,
                holding_period=holding_period,
                performance_grade=performance_grade
            ))
        
        return performances
    
    def generate_optimization_recommendations(self, deals: List[Deal], metrics: PortfolioMetrics) -> List[Dict]:
        """Generate portfolio optimization recommendations"""
        recommendations = []
        
        # Diversification recommendations
        if metrics.diversification_score < 60:
            recommendations.append({
                "type": "Diversification",
                "priority": "High",
                "title": "Improve Geographic Diversification",
                "description": "Consider acquiring properties in different markets to reduce concentration risk.",
                "impact": "Could improve risk-adjusted returns by 15-25%"
            })
        
        # Performance optimization
        underperformers = [deal for deal in deals if self._calculate_property_return(deal) < 5]
        if underperformers:
            recommendations.append({
                "type": "Performance",
                "priority": "Medium", 
                "title": f"Review {len(underperformers)} Underperforming Properties",
                "description": "Consider renovation, refinancing, or disposition strategies.",
                "impact": f"Could improve portfolio ROI by {len(underperformers) * 2}%"
            })
        
        # Liquidity recommendations
        if metrics.liquidity_score < 40:
            recommendations.append({
                "type": "Liquidity",
                "priority": "Low",
                "title": "Improve Portfolio Liquidity",
                "description": "Consider adding REITs or more liquid real estate investments.",
                "impact": "Reduces portfolio risk and improves flexibility"
            })
        
        return recommendations
    
    def _calculate_holding_period(self, deal: Deal) -> int:
        """Calculate holding period in months"""
        if hasattr(deal, 'acquisition_date') and deal.acquisition_date:
            # If we have acquisition date, calculate actual holding period
            acquisition_date = datetime.strptime(deal.acquisition_date, "%Y-%m-%d") if isinstance(deal.acquisition_date, str) else deal.acquisition_date
            return max(1, (datetime.now() - acquisition_date).days // 30)
        else:
            # Default to 12 months if no date available
            return 12
    
    def _calculate_property_return(self, deal: Deal) -> float:
        """Calculate property return percentage"""
        current_value = deal.arv if deal.arv > 0 else deal.purchase_price * 1.05
        return ((current_value - deal.purchase_price) / deal.purchase_price * 100) if deal.purchase_price > 0 else 0
    
    def _calculate_diversification_score(self, deals: List[Deal]) -> float:
        """Calculate portfolio diversification score (0-100)"""
        if not deals:
            return 0
        
        # Simple diversification based on property types and locations
        property_types = set()
        cities = set()
        
        for deal in deals:
            if hasattr(deal, 'property_type') and deal.property_type:
                property_types.add(deal.property_type)
            if deal.address:
                # Extract city from address (simplified)
                cities.add(deal.address.split(',')[0].strip())
        
        # Score based on diversity
        type_diversity = min(len(property_types) * 20, 60)  # Max 60 points for property types
        geo_diversity = min(len(cities) * 10, 40)  # Max 40 points for geography
        
        return type_diversity + geo_diversity
    
    def _calculate_risk_score(self, deals: List[Deal]) -> float:
        """Calculate portfolio risk score (0-100, lower is better)"""
        if not deals:
            return 50
        
        # Risk factors: concentration, property age, market conditions
        risk_factors = []
        
        # Concentration risk
        total_value = sum(deal.arv if deal.arv > 0 else deal.purchase_price for deal in deals)
        max_property_weight = max((deal.arv if deal.arv > 0 else deal.purchase_price) / total_value for deal in deals) if total_value > 0 else 0
        concentration_risk = max_property_weight * 100
        
        # Market risk (simplified)
        market_risk = 30  # Base market risk
        
        # Average the risk factors
        avg_risk = (concentration_risk + market_risk) / 2
        return min(avg_risk, 100)
    
    def _calculate_liquidity_score(self, deals: List[Deal]) -> float:
        """Calculate portfolio liquidity score (0-100, higher is better)"""
        if not deals:
            return 50
        
        # Real estate is generally illiquid, base score around 30-40
        base_liquidity = 35
        
        # Adjust based on property types, locations, etc.
        # (In a real implementation, this would consider actual market conditions)
        return base_liquidity
    
    def _calculate_performance_grade(self, roi: float, cap_rate: float, cash_on_cash: float) -> str:
        """Calculate performance grade A-F based on key metrics"""
        # Weighted scoring
        score = (roi * 0.4 + cap_rate * 0.3 + cash_on_cash * 0.3)
        
        if score >= 15:
            return "A"
        elif score >= 12:
            return "B"
        elif score >= 8:
            return "C"
        elif score >= 5:
            return "D"
        else:
            return "F"

# Visualization functions for portfolio analytics
def create_portfolio_performance_chart(performances: List[PropertyPerformance]):
    """Create comprehensive portfolio performance visualization"""
    if not performances:
        return go.Figure()
    
    # Create performance comparison chart
    properties = [p.property_address[:30] + "..." if len(p.property_address) > 30 else p.property_address for p in performances]
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('ROI by Property', 'Cap Rate vs Cash-on-Cash', 'Property Values', 'Performance Grades'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"type": "domain"}]]
    )
    
    # ROI by property
    fig.add_trace(
        go.Bar(
            x=properties,
            y=[p.roi for p in performances],
            name="ROI %",
            marker_color='#4CAF50'
        ),
        row=1, col=1
    )
    
    # Cap Rate vs Cash-on-Cash scatter
    fig.add_trace(
        go.Scatter(
            x=[p.cap_rate for p in performances],
            y=[p.cash_on_cash for p in performances],
            mode='markers',
            name="Properties",
            text=properties,
            marker=dict(size=10, color='#2196F3')
        ),
        row=1, col=2
    )
    
    # Property values
    fig.add_trace(
        go.Bar(
            x=properties,
            y=[p.current_value for p in performances],
            name="Current Value",
            marker_color='#FF9800'
        ),
        row=2, col=1
    )
    
    # Performance grades
    grade_counts = {}
    for p in performances:
        grade_counts[p.performance_grade] = grade_counts.get(p.performance_grade, 0) + 1
    
    fig.add_trace(
        go.Pie(
            labels=list(grade_counts.keys()),
            values=list(grade_counts.values()),
            name="Grades"
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=800,
        showlegend=False,
        title_text="Portfolio Performance Analysis",
        title_font_size=20
    )
    
    return fig

def create_portfolio_metrics_dashboard(metrics: PortfolioMetrics):
    """Create portfolio metrics dashboard visualization"""
    
    # Create gauge charts for key metrics
    fig = make_subplots(
        rows=2, cols=3,
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]
        ],
        subplot_titles=('Total ROI', 'Annual Return', 'Sharpe Ratio', 'Diversification', 'Risk Score', 'Liquidity')
    )
    
    # Total ROI gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics.total_roi,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [-20, 40]},
               'bar': {'color': "#4CAF50"},
               'steps': [{'range': [-20, 0], 'color': "#ffebee"},
                        {'range': [0, 20], 'color': "#e8f5e8"},
                        {'range': [20, 40], 'color': "#c8e6c9"}],
               'threshold': {'line': {'color': "red", 'width': 4},
                           'thickness': 0.75, 'value': 90}},
        title={'text': "Total ROI (%)"}
    ), row=1, col=1)
    
    # Annual Return gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics.annual_return,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [0, 30]},
               'bar': {'color': "#2196F3"},
               'steps': [{'range': [0, 10], 'color': "#ffebee"},
                        {'range': [10, 20], 'color': "#e8f5e8"},
                        {'range': [20, 30], 'color': "#c8e6c9"}]},
        title={'text': "Annual Return (%)"}
    ), row=1, col=2)
    
    # Sharpe Ratio gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics.sharpe_ratio,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [0, 3]},
               'bar': {'color': "#FF9800"},
               'steps': [{'range': [0, 1], 'color': "#ffebee"},
                        {'range': [1, 2], 'color': "#e8f5e8"},
                        {'range': [2, 3], 'color': "#c8e6c9"}]},
        title={'text': "Sharpe Ratio"}
    ), row=1, col=3)
    
    # Diversification Score
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics.diversification_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "#9C27B0"},
               'steps': [{'range': [0, 40], 'color': "#ffebee"},
                        {'range': [40, 70], 'color': "#e8f5e8"},
                        {'range': [70, 100], 'color': "#c8e6c9"}]},
        title={'text': "Diversification Score"}
    ), row=2, col=1)
    
    # Risk Score (lower is better)
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics.risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "#F44336"},
               'steps': [{'range': [0, 30], 'color': "#c8e6c9"},
                        {'range': [30, 60], 'color': "#e8f5e8"},
                        {'range': [60, 100], 'color': "#ffebee"}]},
        title={'text': "Risk Score (Lower Better)"}
    ), row=2, col=2)
    
    # Liquidity Score
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics.liquidity_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "#00BCD4"},
               'steps': [{'range': [0, 30], 'color': "#ffebee"},
                        {'range': [30, 60], 'color': "#e8f5e8"},
                        {'range': [60, 100], 'color': "#c8e6c9"}]},
        title={'text': "Liquidity Score"}
    ), row=2, col=3)
    
    fig.update_layout(
        height=600,
        title_text="Portfolio Metrics Dashboard",
        title_font_size=20
    )
    
    return fig

def create_geographic_diversification_map(performances: List[PropertyPerformance]):
    """Create geographic diversification visualization"""
    if not performances:
        return go.Figure()
    
    # Extract city data (simplified - in production would use actual geocoding)
    city_data = {}
    for perf in performances:
        city = perf.property_address.split(',')[0].strip()
        if city not in city_data:
            city_data[city] = {'count': 0, 'total_value': 0, 'avg_roi': 0}
        
        city_data[city]['count'] += 1
        city_data[city]['total_value'] += perf.current_value
        city_data[city]['avg_roi'] += perf.roi
    
    # Calculate averages
    for city in city_data:
        city_data[city]['avg_roi'] /= city_data[city]['count']
    
    # Create bar chart for geographic distribution
    cities = list(city_data.keys())
    counts = [city_data[city]['count'] for city in cities]
    avg_rois = [city_data[city]['avg_roi'] for city in cities]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Properties by Location', 'Average ROI by Location'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig.add_trace(
        go.Bar(x=cities, y=counts, name="Property Count", marker_color='#4CAF50'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=cities, y=avg_rois, name="Avg ROI %", marker_color='#2196F3'),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        title_text="Geographic Portfolio Distribution",
        showlegend=False
    )
    
    return fig