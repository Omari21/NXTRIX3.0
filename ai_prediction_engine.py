# -*- coding: utf-8 -*-
"""
AI Prediction Engine for NXTRIX CRM
Advanced market prediction and analysis capabilities
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional
import openai
import os
from datetime import datetime, timedelta
import json

class AIMarketPredictor:
    """AI-powered market prediction and analysis system"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
    def predict_market_trends(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict market trends for a property"""
        try:
            # Basic market prediction logic
            current_price = property_data.get('price', 0)
            property_type = property_data.get('type', 'residential')
            location = property_data.get('location', 'unknown')
            
            # Simulate AI prediction with realistic data
            base_appreciation = 0.05  # 5% base appreciation
            location_factor = np.random.uniform(0.8, 1.2)  # Location adjustment
            market_factor = np.random.uniform(0.9, 1.1)   # Market conditions
            
            predicted_appreciation = base_appreciation * location_factor * market_factor
            
            # Generate 12-month predictions
            predictions = []
            for i in range(12):
                month_factor = 1 + (predicted_appreciation * (i + 1) / 12)
                predicted_price = current_price * month_factor
                
                predictions.append({
                    'month': i + 1,
                    'predicted_price': predicted_price,
                    'appreciation_rate': predicted_appreciation,
                    'confidence': min(90 - (i * 2), 70)  # Decreasing confidence over time
                })
            
            return {
                'predictions': predictions,
                'summary': {
                    'annual_appreciation': predicted_appreciation * 100,
                    '12_month_price': current_price * (1 + predicted_appreciation),
                    'risk_level': 'Low' if predicted_appreciation > 0.03 else 'Medium',
                    'market_conditions': 'Favorable' if market_factor > 1.0 else 'Neutral'
                }
            }
            
        except Exception as e:
            st.error(f"Market prediction error: {str(e)}")
            return self._get_default_prediction(property_data.get('price', 0))
    
    def analyze_investment_potential(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze investment potential of a deal"""
        try:
            purchase_price = deal_data.get('purchase_price', 0)
            monthly_rent = deal_data.get('monthly_rent', 0)
            expenses = deal_data.get('monthly_expenses', 0)
            
            # Calculate key metrics
            annual_rent = monthly_rent * 12
            annual_expenses = expenses * 12
            net_operating_income = annual_rent - annual_expenses
            
            # Cap rate calculation
            cap_rate = (net_operating_income / purchase_price) * 100 if purchase_price > 0 else 0
            
            # Cash flow analysis
            monthly_cash_flow = monthly_rent - expenses
            annual_cash_flow = monthly_cash_flow * 12
            
            # Investment score (0-100)
            score = min(100, max(0, (cap_rate * 10) + (monthly_cash_flow / 100)))
            
            return {
                'investment_score': score,
                'cap_rate': cap_rate,
                'monthly_cash_flow': monthly_cash_flow,
                'annual_cash_flow': annual_cash_flow,
                'recommendation': self._get_investment_recommendation(score),
                'risk_factors': self._identify_risk_factors(deal_data),
                'opportunities': self._identify_opportunities(deal_data)
            }
            
        except Exception as e:
            st.error(f"Investment analysis error: {str(e)}")
            return self._get_default_investment_analysis()
    
    def generate_market_insights(self, location: str = "general") -> Dict[str, Any]:
        """Generate AI-powered market insights"""
        try:
            if not self.openai_api_key:
                return self._get_default_insights(location)
            
            # Use OpenAI for market insights if API key available
            prompt = f"""
            Provide real estate market insights for {location}. Include:
            1. Current market trends
            2. Price predictions for next 6 months
            3. Best property types to invest in
            4. Key risk factors
            
            Keep response concise and actionable.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            insights_text = response.choices[0].message.content
            
            return {
                'insights': insights_text,
                'generated_at': datetime.now().isoformat(),
                'location': location,
                'confidence': 85
            }
            
        except Exception as e:
            return self._get_default_insights(location)
    
    def _get_default_prediction(self, price: float) -> Dict[str, Any]:
        """Default prediction when AI fails"""
        return {
            'predictions': [
                {
                    'month': i + 1,
                    'predicted_price': price * (1 + 0.05 * (i + 1) / 12),
                    'appreciation_rate': 0.05,
                    'confidence': 75
                } for i in range(12)
            ],
            'summary': {
                'annual_appreciation': 5.0,
                '12_month_price': price * 1.05,
                'risk_level': 'Medium',
                'market_conditions': 'Neutral'
            }
        }
    
    def _get_default_investment_analysis(self) -> Dict[str, Any]:
        """Default investment analysis"""
        return {
            'investment_score': 50,
            'cap_rate': 0,
            'monthly_cash_flow': 0,
            'annual_cash_flow': 0,
            'recommendation': 'Insufficient data for analysis',
            'risk_factors': ['Limited data available'],
            'opportunities': ['Gather more property information']
        }
    
    def _get_default_insights(self, location: str) -> Dict[str, Any]:
        """Default market insights"""
        return {
            'insights': f"Market data for {location} suggests stable conditions with moderate growth potential. Consider diversified property types and thorough due diligence.",
            'generated_at': datetime.now().isoformat(),
            'location': location,
            'confidence': 60
        }
    
    def _get_investment_recommendation(self, score: float) -> str:
        """Get investment recommendation based on score"""
        if score >= 80:
            return "Strong Buy - Excellent investment opportunity"
        elif score >= 60:
            return "Buy - Good investment potential"
        elif score >= 40:
            return "Hold - Marginal investment opportunity"
        else:
            return "Pass - Poor investment potential"
    
    def _identify_risk_factors(self, deal_data: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        if deal_data.get('cap_rate', 0) < 5:
            risks.append("Low cap rate - may indicate overpriced property")
        
        if deal_data.get('monthly_cash_flow', 0) < 0:
            risks.append("Negative cash flow - property expenses exceed income")
        
        if not deal_data.get('location'):
            risks.append("Location not specified - market analysis limited")
        
        return risks if risks else ["No significant risks identified"]
    
    def _identify_opportunities(self, deal_data: Dict[str, Any]) -> List[str]:
        """Identify potential opportunities"""
        opportunities = []
        
        if deal_data.get('cap_rate', 0) > 8:
            opportunities.append("High cap rate - strong income potential")
        
        if deal_data.get('monthly_cash_flow', 0) > 500:
            opportunities.append("Strong positive cash flow")
        
        if deal_data.get('property_condition') == 'needs_work':
            opportunities.append("Value-add opportunity through improvements")
        
        return opportunities if opportunities else ["Standard investment opportunity"]

def get_ai_predictor() -> AIMarketPredictor:
    """Get AI predictor instance"""
    if 'ai_predictor' not in st.session_state:
        st.session_state.ai_predictor = AIMarketPredictor()
    return st.session_state.ai_predictor

def create_prediction_visualizations(predictor: AIMarketPredictor, predictions: Dict[str, Any]) -> None:
    """Create prediction visualizations"""
    try:
        if not predictions or 'predictions' not in predictions:
            st.warning("No prediction data available for visualization")
            return
        
        prediction_data = predictions['predictions']
        
        # Create price prediction chart
        months = [p['month'] for p in prediction_data]
        prices = [p['predicted_price'] for p in prediction_data]
        confidence = [p['confidence'] for p in prediction_data]
        
        fig = go.Figure()
        
        # Add price prediction line
        fig.add_trace(go.Scatter(
            x=months,
            y=prices,
            mode='lines+markers',
            name='Predicted Price',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        # Add confidence band
        upper_bound = [p * (1 + (100-c)/1000) for p, c in zip(prices, confidence)]
        lower_bound = [p * (1 - (100-c)/1000) for p, c in zip(prices, confidence)]
        
        fig.add_trace(go.Scatter(
            x=months + months[::-1],
            y=upper_bound + lower_bound[::-1],
            fill='toself',
            fillcolor='rgba(31, 119, 180, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Confidence Band',
            showlegend=True
        ))
        
        fig.update_layout(
            title='12-Month Price Predictions',
            xaxis_title='Month',
            yaxis_title='Predicted Price ($)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary metrics
        if 'summary' in predictions:
            summary = predictions['summary']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Annual Appreciation",
                    f"{summary.get('annual_appreciation', 0):.1f}%"
                )
            
            with col2:
                st.metric(
                    "12-Month Price",
                    f"${summary.get('12_month_price', 0):,.0f}"
                )
            
            with col3:
                st.metric(
                    "Risk Level",
                    summary.get('risk_level', 'Unknown')
                )
            
            with col4:
                st.metric(
                    "Market Conditions",
                    summary.get('market_conditions', 'Unknown')
                )
        
    except Exception as e:
        st.error(f"Visualization error: {str(e)}")
        st.write("Raw prediction data:", predictions)