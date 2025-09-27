"""
Advanced AI Market Prediction Engine for NxTrix CRM
Provides sophisticated market analysis, trend prediction, and investment recommendations
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Tuple, Optional
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class AIMarketPredictor:
    """Advanced AI Market Prediction Engine"""
    
    def __init__(self):
        self.market_cycles = {
            'growth': {'duration': 24, 'roi_multiplier': 1.3, 'risk_factor': 0.8},
            'peak': {'duration': 6, 'roi_multiplier': 1.1, 'risk_factor': 1.2},
            'correction': {'duration': 12, 'roi_multiplier': 0.9, 'risk_factor': 1.5},
            'recovery': {'duration': 18, 'roi_multiplier': 1.2, 'risk_factor': 1.0}
        }
        
        # Initialize market data simulation (replace with real data later)
        self.historical_data = self._generate_market_simulation()
        
    def _generate_market_simulation(self) -> pd.DataFrame:
        """Generate realistic market simulation data for demonstration"""
        np.random.seed(42)  # For consistent results
        
        # Generate 5 years of monthly data
        dates = pd.date_range(start='2019-01-01', end='2024-12-31', freq='M')
        
        # Base market trends with seasonal variations
        trend = np.linspace(100, 140, len(dates))  # Overall upward trend
        seasonal = 5 * np.sin(2 * np.pi * np.arange(len(dates)) / 12)  # Seasonal cycle
        noise = np.random.normal(0, 3, len(dates))  # Market volatility
        
        market_index = trend + seasonal + noise
        
        # Generate correlated real estate metrics
        home_prices = market_index * 2500 + np.random.normal(0, 10000, len(dates))
        inventory_levels = 150 - (market_index - 100) * 0.8 + np.random.normal(0, 15, len(dates))
        days_on_market = 45 - (market_index - 100) * 0.2 + np.random.normal(0, 5, len(dates))
        
        return pd.DataFrame({
            'date': dates,
            'market_index': market_index,
            'avg_home_price': np.maximum(home_prices, 200000),  # Minimum price floor
            'inventory_months': np.maximum(inventory_levels, 1),  # Minimum inventory
            'days_on_market': np.maximum(days_on_market, 5),  # Minimum DOM
            'interest_rate': 3.5 + np.random.normal(0, 0.5, len(dates)),
            'economic_indicator': market_index + np.random.normal(0, 2, len(dates))
        })
    
    def predict_market_trends(self, months_ahead: int = 12) -> Dict:
        """Predict market trends for the next N months"""
        current_data = self.historical_data.iloc[-12:].mean()  # Last 12 months average
        
        # Analyze current market cycle phase
        recent_trend = self.historical_data.iloc[-6:]['market_index'].pct_change().mean()
        current_phase = self._determine_market_phase(recent_trend)
        
        # Generate predictions
        predictions = []
        current_index = self.historical_data.iloc[-1]['market_index']
        
        for month in range(1, months_ahead + 1):
            # Apply market cycle influences
            cycle_effect = self.market_cycles[current_phase]['roi_multiplier']
            trend_momentum = recent_trend * (1 - month * 0.05)  # Diminishing momentum
            seasonal_effect = 2 * np.sin(2 * np.pi * month / 12)
            
            predicted_change = (trend_momentum * cycle_effect + seasonal_effect / 100) * 100
            current_index += predicted_change + np.random.normal(0, 1)
            
            predictions.append({
                'month': month,
                'market_index': current_index,
                'confidence': max(0.5, 0.95 - month * 0.05),  # Decreasing confidence
                'trend': 'bullish' if predicted_change > 0 else 'bearish'
            })
        
        return {
            'current_phase': current_phase,
            'predictions': predictions,
            'risk_assessment': self._assess_market_risk(current_phase),
            'recommendations': self._generate_investment_recommendations(current_phase, predictions)
        }
    
    def _determine_market_phase(self, trend: float) -> str:
        """Determine current market cycle phase"""
        if trend > 0.02:
            return 'growth'
        elif trend > -0.01:
            return 'peak'
        elif trend > -0.03:
            return 'correction'
        else:
            return 'recovery'
    
    def _assess_market_risk(self, phase: str) -> Dict:
        """Assess current market risk factors"""
        base_risk = self.market_cycles[phase]['risk_factor']
        
        return {
            'overall_risk': base_risk,
            'volatility': 'High' if base_risk > 1.3 else 'Medium' if base_risk > 1.0 else 'Low',
            'timing_risk': 'High' if phase in ['peak', 'correction'] else 'Medium',
            'liquidity_risk': 'High' if phase == 'correction' else 'Low',
            'recommendation': self._get_risk_recommendation(base_risk)
        }
    
    def _get_risk_recommendation(self, risk_factor: float) -> str:
        """Get risk-based recommendation"""
        if risk_factor > 1.3:
            return "Exercise extreme caution. Consider defensive strategies and cash positions."
        elif risk_factor > 1.1:
            return "Moderate risk. Diversify portfolio and avoid overleveraging."
        else:
            return "Favorable conditions. Good time for strategic acquisitions."
    
    def _generate_investment_recommendations(self, phase: str, predictions: List) -> List[str]:
        """Generate AI-powered investment recommendations"""
        recommendations = []
        
        avg_trend = np.mean([p['market_index'] for p in predictions[:6]])
        
        if phase == 'growth':
            recommendations.extend([
                "🚀 Strong growth phase detected - Ideal time for acquisitions",
                "📈 Focus on value-add properties with renovation potential",
                "🏘️ Consider emerging neighborhoods before peak pricing",
                "⚡ Act quickly on good deals - competition is increasing"
            ])
        elif phase == 'peak':
            recommendations.extend([
                "⚠️ Market approaching peak - Be selective with new investments",
                "💰 Consider taking profits on well-performing properties",
                "🔍 Focus on cash-flowing assets over speculation",
                "📊 Prepare for potential market correction"
            ])
        elif phase == 'correction':
            recommendations.extend([
                "🛡️ Defensive strategy recommended - Preserve capital",
                "💎 Exceptional opportunities emerging for patient investors",
                "🏦 Ensure strong cash reserves for upcoming deals",
                "📉 Avoid panic selling - Focus on fundamentals"
            ])
        else:  # recovery
            recommendations.extend([
                "🌱 Recovery phase - Great time for strategic positioning",
                "🎯 Target distressed properties at significant discounts",
                "📈 Position for next growth cycle",
                "💪 Increase acquisition activity with strong due diligence"
            ])
        
        return recommendations
    
    def analyze_deal_timing(self, deal_data: Dict) -> Dict:
        """Analyze optimal timing for a specific deal"""
        location = deal_data.get('location', 'General Market')
        price = deal_data.get('price', 300000)
        
        # Simulate location-specific factors
        location_multiplier = np.random.uniform(0.9, 1.1)
        price_tier_factor = 1.1 if price < 250000 else 0.95 if price > 500000 else 1.0
        
        market_prediction = self.predict_market_trends(6)
        current_phase = market_prediction['current_phase']
        
        # Calculate timing score
        base_score = self.market_cycles[current_phase]['roi_multiplier'] * 100
        adjusted_score = base_score * location_multiplier * price_tier_factor
        
        timing_recommendation = {
            'timing_score': min(100, max(0, adjusted_score)),
            'action': self._get_timing_action(adjusted_score),
            'best_month': self._predict_best_timing(market_prediction['predictions']),
            'risk_factors': self._identify_deal_risks(deal_data, current_phase)
        }
        
        return timing_recommendation
    
    def _get_timing_action(self, score: float) -> str:
        """Get timing-based action recommendation"""
        if score > 110:
            return "🔥 EXCELLENT - Act immediately"
        elif score > 100:
            return "✅ GOOD - Proceed with confidence"
        elif score > 90:
            return "⚠️ FAIR - Negotiate aggressively"
        else:
            return "❌ POOR - Wait for better conditions"
    
    def _predict_best_timing(self, predictions: List) -> str:
        """Predict best timing for deal execution"""
        best_month = min(predictions[:6], key=lambda x: x['market_index'])
        return f"Month {best_month['month']} shows optimal conditions"
    
    def _identify_deal_risks(self, deal_data: Dict, phase: str) -> List[str]:
        """Identify specific risks for a deal"""
        risks = []
        
        if phase == 'peak':
            risks.append("Market peak timing risk")
        elif phase == 'correction':
            risks.append("Declining value risk")
        
        price = deal_data.get('price', 300000)
        if price > 500000:
            risks.append("High price tier volatility")
        
        if deal_data.get('renovation_needed', False):
            risks.append("Construction cost inflation risk")
        
        return risks if risks else ["Low risk profile"]
    
    def generate_portfolio_predictions(self, portfolio_deals: List) -> Dict:
        """Generate AI predictions for entire portfolio"""
        if not portfolio_deals:
            return {"status": "No portfolio data available"}
        
        market_trends = self.predict_market_trends(12)
        
        # Analyze portfolio composition
        total_value = sum(getattr(deal, 'purchase_price', 0) for deal in portfolio_deals)
        avg_score = np.mean([getattr(deal, 'ai_score', 75) for deal in portfolio_deals])
        
        # Generate portfolio-level predictions
        portfolio_analysis = {
            'current_value': total_value,
            'predicted_12m_value': total_value * market_trends['predictions'][11]['market_index'] / 100,
            'performance_grade': self._grade_portfolio_performance(avg_score),
            'optimization_opportunities': self._find_optimization_opportunities(portfolio_deals),
            'diversification_score': self._calculate_diversification(portfolio_deals),
            'recommended_actions': self._get_portfolio_recommendations(portfolio_deals, market_trends)
        }
        
        return portfolio_analysis
    
    def _grade_portfolio_performance(self, avg_score: float) -> str:
        """Grade portfolio performance"""
        if avg_score >= 90:
            return "A+ Exceptional"
        elif avg_score >= 80:
            return "A Good"
        elif avg_score >= 70:
            return "B Fair"
        else:
            return "C Needs Improvement"
    
    def _find_optimization_opportunities(self, portfolio_deals: List) -> List[str]:
        """Find portfolio optimization opportunities"""
        opportunities = []
        
        scores = [getattr(deal, 'ai_score', 75) for deal in portfolio_deals]
        low_performers = len([s for s in scores if s < 70])
        
        if low_performers > 0:
            opportunities.append(f"📊 {low_performers} deals scoring below 70 - Consider optimization")
        
        if len(portfolio_deals) < 5:
            opportunities.append("📈 Portfolio size opportunity - Consider diversification")
        
        return opportunities if opportunities else ["✅ Portfolio well-optimized"]
    
    def _calculate_diversification(self, portfolio_deals: List) -> float:
        """Calculate portfolio diversification score"""
        if len(portfolio_deals) < 2:
            return 0.3
        
        # Simulate diversification based on portfolio size and randomness
        base_score = min(0.9, len(portfolio_deals) * 0.15)
        return base_score + np.random.uniform(-0.1, 0.1)
    
    def _get_portfolio_recommendations(self, portfolio_deals: List, market_trends: Dict) -> List[str]:
        """Get AI recommendations for portfolio management"""
        recommendations = []
        phase = market_trends['current_phase']
        
        if phase == 'growth':
            recommendations.append("🚀 Expand portfolio during favorable growth phase")
        elif phase == 'peak':
            recommendations.append("💰 Consider profit-taking on best performers")
        
        avg_score = np.mean([getattr(deal, 'ai_score', 75) for deal in portfolio_deals])
        if avg_score < 75:
            recommendations.append("🔧 Focus on improving underperforming assets")
        
        if len(portfolio_deals) > 10:
            recommendations.append("⚖️ Consider portfolio consolidation for better management")
        
        return recommendations


def create_prediction_visualizations(predictor: AIMarketPredictor, predictions: Dict) -> None:
    """Create advanced prediction visualizations"""
    
    # Market Trend Prediction Chart
    st.subheader("🔮 AI Market Predictions")
    
    prediction_data = predictions['predictions']
    months = [p['month'] for p in prediction_data]
    indices = [p['market_index'] for p in prediction_data]
    confidence = [p['confidence'] for p in prediction_data]
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Market Index Prediction', 'Confidence Level', 'Risk Assessment', 'Investment Timing'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Market prediction line
    fig.add_trace(
        go.Scatter(x=months, y=indices, mode='lines+markers', name='Predicted Index',
                  line=dict(color='#00D4AA', width=3)),
        row=1, col=1
    )
    
    # Confidence area
    fig.add_trace(
        go.Scatter(x=months, y=confidence, mode='lines', fill='tonexty', name='Confidence',
                  line=dict(color='rgba(0,212,170,0.3)')),
        row=1, col=2
    )
    
    # Risk gauge
    risk_score = predictions['risk_assessment']['overall_risk'] * 50
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=risk_score,
            title={'text': "Risk Level"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "darkred" if risk_score > 70 else "orange" if risk_score > 40 else "green"},
                   'steps': [{'range': [0, 40], 'color': "lightgray"},
                            {'range': [40, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "red"}]},
        ),
        row=2, col=1
    )
    
    # Timing recommendation
    timing_colors = ['green' if p['trend'] == 'bullish' else 'red' for p in prediction_data[:6]]
    fig.add_trace(
        go.Bar(x=months[:6], y=[100 if p['trend'] == 'bullish' else -100 for p in prediction_data[:6]],
               marker_color=timing_colors, name='Timing Signal'),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False, title_text="AI Market Intelligence Dashboard")
    st.plotly_chart(fig, use_container_width=True)


# Global predictor instance
@st.cache_resource
def get_ai_predictor():
    """Get cached AI predictor instance"""
    return AIMarketPredictor()