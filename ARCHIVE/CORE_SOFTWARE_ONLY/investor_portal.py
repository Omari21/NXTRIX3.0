"""
Investor Portal Module for NXTRIX Enterprise CRM
Provides secure investor access, performance tracking, and communication tools
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from models import Deal, Investor, Portfolio
from database import db_service
import hashlib
import uuid

@dataclass
class InvestorProfile:
    """Enhanced investor profile with portal access"""
    id: str
    name: str
    email: str
    phone: str
    investment_capacity: float
    risk_tolerance: str  # Conservative, Moderate, Aggressive
    preferred_markets: List[str] = field(default_factory=list)
    preferred_property_types: List[str] = field(default_factory=list)
    investment_goals: List[str] = field(default_factory=list)
    total_invested: float = 0
    total_returns: float = 0
    portfolio_value: float = 0
    active_deals: int = 0
    join_date: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    access_level: str = "Standard"  # Standard, Premium, VIP
    communication_preferences: Dict = field(default_factory=dict)

@dataclass
class InvestorDealAccess:
    """Deal access control for investors"""
    investor_id: str
    deal_id: str
    access_type: str  # View, Invest, Full
    investment_amount: float = 0
    investment_date: Optional[datetime] = None
    ownership_percentage: float = 0
    status: str = "Active"  # Active, Exited, Pending

@dataclass
class InvestorCommunication:
    """Investor communication tracking"""
    id: str
    investor_id: str
    subject: str
    message: str
    communication_type: str  # Email, SMS, Portal, Call
    sent_date: datetime
    status: str  # Sent, Read, Responded
    deal_id: Optional[str] = None

class InvestorPortalManager:
    """Manages investor portal functionality and access control"""
    
    def __init__(self):
        self.current_investor = None
        self.session_token = None
        
    def authenticate_investor(self, email: str, password: str) -> Optional[InvestorProfile]:
        """Authenticate investor login (simplified for demo)"""
        # In production, this would use proper authentication
        # For demo, we'll simulate with existing investor data
        investors = db_service.get_investors() if db_service.is_connected() else []
        
        for investor in investors:
            if investor.email.lower() == email.lower():
                # Create enhanced profile
                profile = self._create_investor_profile(investor)
                self.current_investor = profile
                self.session_token = self._generate_session_token()
                return profile
        
        return None
    
    def _create_investor_profile(self, investor: Investor) -> InvestorProfile:
        """Convert basic investor to enhanced profile"""
        return InvestorProfile(
            id=investor.id,
            name=investor.name,
            email=investor.email,
            phone=investor.phone,
            investment_capacity=investor.investment_capacity,
            risk_tolerance=investor.risk_tolerance,
            preferred_markets=investor.preferred_markets,
            preferred_property_types=investor.preferred_property_types,
            investment_goals=investor.investment_goals,
            total_invested=self._calculate_total_invested(investor.id),
            total_returns=self._calculate_total_returns(investor.id),
            portfolio_value=self._calculate_portfolio_value(investor.id),
            active_deals=self._count_active_deals(investor.id)
        )
    
    def _generate_session_token(self) -> str:
        """Generate secure session token"""
        return hashlib.sha256(f"{uuid.uuid4()}{datetime.now()}".encode()).hexdigest()[:32]
    
    def _calculate_total_invested(self, investor_id: str) -> float:
        """Calculate total amount invested by investor"""
        # This would query actual investment records
        # For demo, return estimated amount
        return 250000.0
    
    def _calculate_total_returns(self, investor_id: str) -> float:
        """Calculate total returns for investor"""
        # This would calculate actual returns from investment records
        # For demo, return estimated returns
        return 35000.0
    
    def _calculate_portfolio_value(self, investor_id: str) -> float:
        """Calculate current portfolio value for investor"""
        return self._calculate_total_invested(investor_id) + self._calculate_total_returns(investor_id)
    
    def _count_active_deals(self, investor_id: str) -> int:
        """Count active deals for investor"""
        # For demo, return estimated count
        return 3
    
    def get_investor_deals(self, investor_id: str) -> List[Deal]:
        """Get deals accessible to specific investor"""
        if not db_service.is_connected():
            return []
        
        # In production, this would filter based on actual investor access
        # For demo, return all deals with simulated access control
        all_deals = db_service.get_deals()
        
        # Simulate investor access (first 3 deals)
        return all_deals[:3] if len(all_deals) >= 3 else all_deals
    
    def get_investor_performance_data(self, investor_id: str) -> Dict:
        """Get detailed performance data for investor"""
        deals = self.get_investor_deals(investor_id)
        
        # Calculate performance metrics
        total_invested = sum(50000 for _ in deals)  # Simulate $50k per deal
        # Calculate current value based on ARV (After Repair Value) or estimated appreciation
        total_current_value = sum(deal.arv if deal.arv > 0 else deal.purchase_price * 1.1 for deal in deals)
        
        monthly_performance = []
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(12):
            month_date = base_date + timedelta(days=30*i)
            # Simulate monthly returns with some volatility
            monthly_return = 500 + (i * 200) + ((-1)**i * 100)
            monthly_performance.append({
                'date': month_date,
                'value': total_invested + (i * 1000) + monthly_return,
                'return': monthly_return
            })
        
        return {
            'total_invested': total_invested,
            'current_value': total_current_value,
            'total_return': total_current_value - total_invested,
            'roi_percentage': ((total_current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0,
            'monthly_performance': monthly_performance,
            'deal_count': len(deals)
        }

class InvestorDashboard:
    """Creates investor-specific dashboards and visualizations"""
    
    def __init__(self, portal_manager: InvestorPortalManager):
        self.portal_manager = portal_manager
    
    def create_investor_overview_dashboard(self, investor: InvestorProfile) -> go.Figure:
        """Create comprehensive investor overview dashboard"""
        
        # Create subplots for overview metrics
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Portfolio Value Over Time', 'Investment Distribution', 'Monthly Returns', 'Performance Metrics'),
            specs=[
                [{"secondary_y": False}, {"type": "pie"}],
                [{"secondary_y": False}, {"type": "indicator"}]
            ]
        )
        
        # Portfolio value over time
        performance_data = self.portal_manager.get_investor_performance_data(investor.id)
        monthly_data = performance_data['monthly_performance']
        
        dates = [item['date'] for item in monthly_data]
        values = [item['value'] for item in monthly_data]
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values,
                mode='lines+markers',
                name='Portfolio Value',
                line=dict(color='#4CAF50', width=3),
                marker=dict(size=6)
            ),
            row=1, col=1
        )
        
        # Investment distribution (pie chart)
        fig.add_trace(
            go.Pie(
                labels=['Real Estate', 'Cash', 'Returns'],
                values=[investor.total_invested, 25000, investor.total_returns],
                hole=0.4,
                marker_colors=['#4CAF50', '#2196F3', '#FF9800']
            ),
            row=1, col=2
        )
        
        # Monthly returns
        returns = [item['return'] for item in monthly_data]
        fig.add_trace(
            go.Bar(
                x=dates,
                y=returns,
                name='Monthly Returns',
                marker_color='#2196F3'
            ),
            row=2, col=1
        )
        
        # Performance indicator
        roi_percentage = performance_data['roi_percentage']
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=roi_percentage,
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 50]},
                    'bar': {'color': "#4CAF50"},
                    'steps': [
                        {'range': [0, 10], 'color': "#ffebee"},
                        {'range': [10, 25], 'color': "#e8f5e8"},
                        {'range': [25, 50], 'color': "#c8e6c9"}
                    ],
                },
                title={'text': "Total ROI (%)"},
                delta={'reference': 15}
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text=f"Portfolio Overview - {investor.name}",
            title_font_size=20,
            showlegend=False
        )
        
        return fig
    
    def create_deal_comparison_chart(self, deals: List[Deal]) -> go.Figure:
        """Create deal comparison visualization for investor"""
        if not deals:
            return go.Figure()
        
        addresses = [deal.address[:30] + "..." if len(deal.address) > 30 else deal.address for deal in deals]
        purchase_prices = [deal.purchase_price for deal in deals]
        current_values = [deal.arv if deal.arv > 0 else deal.purchase_price * 1.1 for deal in deals]
        ai_scores = [deal.ai_score for deal in deals]
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Investment Value Comparison', 'AI Score Performance'),
            specs=[[{"secondary_y": True}, {"secondary_y": False}]]
        )
        
        # Investment comparison
        fig.add_trace(
            go.Bar(x=addresses, y=purchase_prices, name="Purchase Price", marker_color='#2196F3'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=addresses, y=current_values, name="Current Value", marker_color='#4CAF50'),
            row=1, col=1
        )
        
        # AI Scores
        fig.add_trace(
            go.Scatter(
                x=addresses, 
                y=ai_scores, 
                mode='markers+lines',
                name="AI Score",
                marker=dict(size=12, color='#FF9800'),
                line=dict(color='#FF9800', width=2)
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=500,
            title_text="Investment Portfolio Analysis",
            showlegend=True
        )
        
        return fig
    
    def create_communication_timeline(self, investor_id: str) -> go.Figure:
        """Create communication timeline for investor"""
        # Simulate communication data
        communications = [
            {"date": datetime.now() - timedelta(days=7), "type": "Email", "subject": "Monthly Portfolio Update"},
            {"date": datetime.now() - timedelta(days=14), "type": "Portal", "subject": "New Deal Opportunity"},
            {"date": datetime.now() - timedelta(days=21), "type": "Call", "subject": "Investment Review"},
            {"date": datetime.now() - timedelta(days=35), "type": "Email", "subject": "Quarterly Report"},
        ]
        
        dates = [comm["date"] for comm in communications]
        types = [comm["type"] for comm in communications]
        subjects = [comm["subject"] for comm in communications]
        
        fig = go.Figure()
        
        colors = {'Email': '#2196F3', 'Portal': '#4CAF50', 'Call': '#FF9800', 'SMS': '#9C27B0'}
        
        for comm_type in set(types):
            type_dates = [date for date, t in zip(dates, types) if t == comm_type]
            type_subjects = [subj for subj, t in zip(subjects, types) if t == comm_type]
            
            fig.add_trace(go.Scatter(
                x=type_dates,
                y=[comm_type] * len(type_dates),
                mode='markers',
                name=comm_type,
                marker=dict(size=15, color=colors.get(comm_type, '#757575')),
                text=type_subjects,
                hovertemplate='<b>%{y}</b><br>%{text}<br>%{x}<extra></extra>'
            ))
        
        fig.update_layout(
            title="Recent Communications",
            xaxis_title="Date",
            yaxis_title="Communication Type",
            height=300,
            hovermode='closest'
        )
        
        return fig

# Utility functions for investor portal
def generate_investor_report(investor: InvestorProfile, deals: List[Deal]) -> Dict:
    """Generate comprehensive investor report"""
    portal_manager = InvestorPortalManager()
    performance_data = portal_manager.get_investor_performance_data(investor.id)
    
    report = {
        'investor_info': {
            'name': investor.name,
            'total_invested': investor.total_invested,
            'total_returns': investor.total_returns,
            'portfolio_value': investor.portfolio_value,
            'roi_percentage': performance_data['roi_percentage']
        },
        'portfolio_summary': {
            'active_deals': len(deals),
            'avg_deal_size': investor.total_invested / len(deals) if deals else 0,
            'best_performing_deal': max(deals, key=lambda d: d.ai_score).address if deals else "N/A",
            'total_properties': len(deals)
        },
        'risk_analysis': {
            'risk_tolerance': investor.risk_tolerance,
            'diversification_score': calculate_investor_diversification(deals),
            'concentration_risk': calculate_concentration_risk(deals, investor.total_invested)
        },
        'recommendations': generate_investor_recommendations(investor, deals)
    }
    
    return report

def calculate_investor_diversification(deals: List[Deal]) -> float:
    """Calculate diversification score for investor's portfolio"""
    if not deals:
        return 0
    
    # Simple diversification based on locations and property types
    locations = set(deal.address.split(',')[0].strip() for deal in deals)
    property_types = set(getattr(deal, 'property_type', 'Residential') for deal in deals)
    
    geo_diversity = min(len(locations) * 25, 50)
    type_diversity = min(len(property_types) * 25, 50)
    
    return geo_diversity + type_diversity

def calculate_concentration_risk(deals: List[Deal], total_invested: float) -> float:
    """Calculate concentration risk for investor"""
    if not deals or total_invested == 0:
        return 0
    
    # Assume equal investment in each deal for simplification
    investment_per_deal = total_invested / len(deals)
    max_concentration = investment_per_deal / total_invested
    
    # Convert to risk percentage (higher concentration = higher risk)
    return max_concentration * 100

def generate_investor_recommendations(investor: InvestorProfile, deals: List[Deal]) -> List[Dict]:
    """Generate personalized recommendations for investor"""
    recommendations = []
    
    # Diversification recommendations
    if calculate_investor_diversification(deals) < 50:
        recommendations.append({
            "type": "Diversification",
            "priority": "Medium",
            "title": "Consider Geographic Diversification",
            "description": "Your portfolio could benefit from properties in additional markets.",
            "action": "Review available opportunities in new markets"
        })
    
    # Risk-based recommendations
    if investor.risk_tolerance == "Conservative" and len(deals) < 5:
        recommendations.append({
            "type": "Risk Management",
            "priority": "Low",
            "title": "Increase Portfolio Size",
            "description": "Consider additional investments to reduce individual property risk.",
            "action": "Evaluate 2-3 additional investment opportunities"
        })
    
    # Performance recommendations
    if deals:
        avg_ai_score = sum(deal.ai_score for deal in deals) / len(deals)
        if avg_ai_score < 80:
            recommendations.append({
                "type": "Performance",
                "priority": "High",
                "title": "Focus on Higher Quality Deals",
                "description": "Consider deals with AI scores above 85 for better returns.",
                "action": "Review premium deal opportunities"
            })
    
    return recommendations