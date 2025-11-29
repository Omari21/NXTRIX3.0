"""
Demo Mode Features for NXTRIX 3.0
Impressive demonstration capabilities for prospects
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

class DemoFeatures:
    def __init__(self):
        self.sample_deals = [
            {"name": "Downtown Office Complex", "value": 125000, "stage": "Negotiation", "probability": 85, "contact": "Sarah Johnson"},
            {"name": "Luxury Residential Tower", "value": 95000, "stage": "Proposal", "probability": 70, "contact": "Michael Chen"},
            {"name": "Tech Campus Expansion", "value": 78000, "stage": "Qualified", "probability": 60, "contact": "Alex Rivera"},
            {"name": "Retail Shopping Center", "value": 65000, "stage": "Negotiation", "probability": 90, "contact": "Emma Davis"},
            {"name": "Industrial Warehouse", "value": 45000, "stage": "Proposal", "probability": 50, "contact": "James Wilson"}
        ]
        
        self.sample_contacts = [
            {"name": "Sarah Johnson", "company": "Johnson Enterprises", "lead_score": 92, "last_contact": "2 hours ago"},
            {"name": "Michael Chen", "company": "Tech Innovations", "lead_score": 88, "last_contact": "1 day ago"},
            {"name": "Alex Rivera", "company": "Rivera Holdings", "lead_score": 85, "last_contact": "3 hours ago"},
            {"name": "Emma Davis", "company": "Davis Group", "lead_score": 82, "last_contact": "5 hours ago"},
            {"name": "James Wilson", "company": "Wilson Capital", "lead_score": 79, "last_contact": "2 days ago"}
        ]
    
    def toggle_demo_mode(self):
        """Toggle demo mode on/off"""
        if 'demo_mode' not in st.session_state:
            st.session_state.demo_mode = False
        
        st.markdown("### 🎬 Demo Mode Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎯 Quick Demo", use_container_width=True, type="primary"):
                self.run_quick_demo()
        
        with col2:
            if st.button("📊 Full Demo", use_container_width=True):
                self.run_full_demo()
        
        with col3:
            if st.button("🔄 Reset", use_container_width=True):
                self.reset_demo()
    
    def run_quick_demo(self):
        """Run quick 30-second demo"""
        st.session_state.demo_mode = True
        st.session_state.demo_type = "quick"
        
        st.success("🎯 Quick Demo Activated!")
        
        # Show key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Revenue", "$2.3M", "+18.5%")
        with col2:
            st.metric("Active Deals", "23", "+5")
        with col3:
            st.metric("Win Rate", "67%", "+12%")
        with col4:
            st.metric("Avg Deal Size", "$85K", "+8%")
        
        # Show top deals
        st.markdown("### 🔥 Hot Deals")
        for deal in self.sample_deals[:3]:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.text(deal['name'])
            with col2:
                st.text(f"${deal['value']:,}")
            with col3:
                st.text(deal['stage'])
            with col4:
                st.success(f"{deal['probability']}%")
    
    def run_full_demo(self):
        """Run comprehensive demo"""
        st.session_state.demo_mode = True
        st.session_state.demo_type = "full"
        
        st.success("📊 Full Demo Mode Activated!")
        
        # Comprehensive dashboard
        self.render_demo_dashboard()
        
        # Interactive features
        self.render_demo_interactions()
    
    def render_demo_dashboard(self):
        """Render impressive demo dashboard"""
        st.markdown("## 🚀 NXTRIX Enterprise Dashboard")
        st.markdown("*Showing sample data - your actual metrics will appear here*")
        
        # Revenue chart
        revenue_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Revenue': [180000, 195000, 220000, 235000, 270000, 290000],
            'Target': [200000, 210000, 220000, 240000, 260000, 280000]
        })
        
        fig = px.line(revenue_data, x='Month', y=['Revenue', 'Target'], 
                     title='Revenue vs Target',
                     color_discrete_sequence=['#6366f1', '#10b981'])
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Deal pipeline
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💼 Deal Pipeline")
            
            pipeline_data = pd.DataFrame({
                'Stage': ['Lead', 'Qualified', 'Proposal', 'Negotiation', 'Closed'],
                'Count': [15, 12, 8, 5, 3],
                'Value': [450000, 380000, 290000, 220000, 180000]
            })
            
            fig = px.bar(pipeline_data, x='Stage', y='Count', 
                        title='Deals by Stage',
                        color_discrete_sequence=['#8b5cf6'])
            
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Performance Trends")
            
            performance_data = pd.DataFrame({
                'Metric': ['Lead Conversion', 'Deal Velocity', 'Win Rate', 'Customer Satisfaction'],
                'Current': [23.5, 32, 67, 94],
                'Target': [25, 30, 65, 90]
            })
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Current',
                x=performance_data['Metric'],
                y=performance_data['Current'],
                marker_color='#6366f1'
            ))
            
            fig.add_trace(go.Bar(
                name='Target',
                x=performance_data['Metric'],
                y=performance_data['Target'],
                marker_color='#10b981'
            ))
            
            fig.update_layout(
                title='Performance vs Targets',
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                barmode='group'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def render_demo_interactions(self):
        """Render interactive demo features"""
        st.markdown("## 🎯 Interactive Features")
        
        tab1, tab2, tab3 = st.tabs(["🤖 AI Assistant", "📊 Live Analytics", "⚡ Quick Actions"])
        
        with tab1:
            st.markdown("### AI-Powered Insights")
            
            if st.button("🧠 Generate AI Insights", type="primary"):
                insights = [
                    "📈 Revenue is trending 18% above target this quarter",
                    "🎯 3 high-value deals require immediate attention",
                    "💡 Consider focusing on Tech sector - 89% win rate",
                    "📞 15 contacts haven't been reached in 7+ days",
                    "🚀 Q4 forecast: 23% growth potential identified"
                ]
                
                for insight in insights:
                    st.success(insight)
        
        with tab2:
            st.markdown("### Real-Time Analytics")
            
            if st.button("🔄 Refresh Live Data"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Active Users", "47", "+3")
                with col2:
                    st.metric("Today's Leads", "12", "+8")
                with col3:
                    st.metric("Conversions", "3", "+2")
                
                st.success("✅ Data refreshed in real-time")
        
        with tab3:
            st.markdown("### One-Click Actions")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📧 Send Campaign", use_container_width=True):
                    st.success("📧 Email campaign sent to 247 contacts!")
            
            with col2:
                if st.button("📋 Generate Report", use_container_width=True):
                    st.success("📋 Monthly report generated and emailed!")
            
            with col3:
                if st.button("🤝 Create Deal", use_container_width=True):
                    st.success("🤝 New deal created in pipeline!")
    
    def reset_demo(self):
        """Reset demo mode"""
        st.session_state.demo_mode = False
        if 'demo_type' in st.session_state:
            del st.session_state.demo_type
        
        st.info("🔄 Demo mode reset - returning to live data")
    
    def get_demo_data(self, data_type: str):
        """Get demo data for different types"""
        if data_type == "deals":
            return self.sample_deals
        elif data_type == "contacts":
            return self.sample_contacts
        else:
            return []

# Global demo features instance
demo_features = DemoFeatures()