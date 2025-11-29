"""
WOW Factor Features for NXTRIX 3.0
Advanced features that differentiate from competitors
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
import random

class WowFeatures:
    def __init__(self):
        self.competitive_data = {
            "NXTRIX": {"features": 95, "ease_of_use": 92, "ai_features": 98, "value": 89},
            "Salesforce": {"features": 85, "ease_of_use": 65, "ai_features": 70, "value": 60},
            "HubSpot": {"features": 80, "ease_of_use": 75, "ai_features": 65, "value": 70},
            "Pipedrive": {"features": 70, "ease_of_use": 80, "ai_features": 45, "value": 75}
        }
    
    def render_competitive_analysis(self):
        """Render competitive analysis radar chart"""
        st.markdown("### 🎯 Competitive Analysis")
        st.markdown("See how NXTRIX compares to major CRM platforms:")
        
        categories = ['Features', 'Ease of Use', 'AI Capabilities', 'Value for Money']
        
        fig = go.Figure()
        
        for platform, scores in self.competitive_data.items():
            values = list(scores.values())
            values.append(values[0])  # Close the radar chart
            
            color = "#6366f1" if platform == "NXTRIX" else f"rgba({random.randint(100,200)}, {random.randint(100,200)}, {random.randint(100,200)}, 0.6)"
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill='toself',
                name=platform,
                line=dict(color=color, width=3 if platform == "NXTRIX" else 2)
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100]),
                bgcolor="rgba(0,0,0,0)"
            ),
            showlegend=True,
            title="Platform Comparison",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_live_market_pulse(self):
        """Render live market pulse indicator"""
        st.markdown("### 📊 Live Market Pulse")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Market temperature gauge
            market_temp = 78  # Sample value
            st.metric(
                "Market Temperature",
                f"{market_temp}°",
                "🔥 Hot Market" if market_temp > 75 else "❄️ Cool Market"
            )
        
        with col2:
            st.metric("Active Listings", "2,347", "+12%")
        
        with col3:
            st.metric("Avg Price/SqFt", "$285", "+3.2%")
        
        # Market trends
        trend_data = pd.DataFrame({
            'Hour': list(range(24)),
            'Activity': [random.randint(50, 100) for _ in range(24)]
        })
        
        fig = px.line(trend_data, x='Hour', y='Activity', 
                     title='Today\'s Market Activity',
                     color_discrete_sequence=['#6366f1'])
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_ai_insights_preview(self):
        """Render AI insights preview"""
        st.markdown("### 🤖 AI Insights Preview")
        
        insights = [
            {
                "type": "opportunity",
                "title": "High-Value Lead Detected",
                "description": "John Smith shows 89% buying probability based on behavior analysis",
                "confidence": 89,
                "action": "Schedule immediate follow-up"
            },
            {
                "type": "market",
                "title": "Market Opportunity",
                "description": "Downtown area showing 15% price increase trend",
                "confidence": 82,
                "action": "Review inventory in this area"
            },
            {
                "type": "deal",
                "title": "Deal Risk Alert",
                "description": "ABC Corp deal showing signs of stagnation",
                "confidence": 76,
                "action": "Immediate intervention recommended"
            }
        ]
        
        for insight in insights:
            icon = "🎯" if insight["type"] == "opportunity" else "📈" if insight["type"] == "market" else "⚠️"
            color = "#10b981" if insight["type"] == "opportunity" else "#6366f1" if insight["type"] == "market" else "#f59e0b"
            
            st.markdown(f"""
            <div style="
                background: rgba(255, 255, 255, 0.02);
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 16px;
                margin: 12px 0;
            ">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                    <span style="font-size: 20px;">{icon}</span>
                    <strong style="color: {color};">{insight['title']}</strong>
                    <span style="
                        background: {color}20;
                        color: {color};
                        padding: 2px 8px;
                        border-radius: 12px;
                        font-size: 12px;
                        margin-left: auto;
                    ">{insight['confidence']}% confidence</span>
                </div>
                <div style="color: rgba(255,255,255,0.8); margin-bottom: 8px;">
                    {insight['description']}
                </div>
                <div style="color: {color}; font-weight: 500; font-size: 14px;">
                    💡 {insight['action']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_demo_mode_toggle(self):
        """Render demo mode controls"""
        st.markdown("### 🎬 Demo Mode")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎯 Enable Demo Data", use_container_width=True):
                st.session_state.demo_mode = True
                st.success("✅ Demo mode activated! Sample data loaded.")
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset to Live Data", use_container_width=True):
                st.session_state.demo_mode = False
                st.success("✅ Live mode activated! Real data restored.")
                st.rerun()
        
        # Demo features preview
        if st.session_state.get('demo_mode', False):
            st.info("🎬 Demo mode active - showing sample data")
            
            demo_features = [
                "📊 Sample analytics with impressive metrics",
                "💼 Mock deals showing negotiation stages",
                "👥 Example contacts with lead scores",
                "📧 Email campaign success stories",
                "🎯 AI insights with predictions"
            ]
            
            for feature in demo_features:
                st.markdown(f"• {feature}")

# Global wow features instance
wow_features = WowFeatures()