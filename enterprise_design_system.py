"""
Enterprise Design System for NXTRIX 3.0
Professional UI components, glass-morphism effects, and enterprise-grade styling
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid

class EnterpriseDesign:
    def __init__(self):
        self.primary_color = "#6366f1"
        self.secondary_color = "#8b5cf6"
        self.accent_color = "#06b6d4"
        self.success_color = "#10b981"
        self.warning_color = "#f59e0b"
        self.error_color = "#ef4444"
        
    def inject_enterprise_css(self):
        """Inject enterprise-grade CSS styling"""
        st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Root Variables */
        :root {
            --primary: #6366f1;
            --primary-light: #818cf8;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --accent: #06b6d4;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --background: #0a0b0d;
            --surface: #1a1b23;
            --surface-light: #25262d;
            --text: #ffffff;
            --text-muted: #a1a3a8;
            --border: #2d3748;
            --glass: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
        }

        /* Global Styling */
        .stApp {
            background: linear-gradient(135deg, #0a0b0d 0%, #1a1b23 50%, #0a0b0d 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Glass Morphism Effects */
        .glass-container {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            backdrop-filter: blur(20px);
            padding: 24px;
            margin: 16px 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        /* Enterprise Metric Cards */
        .metric-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(20px);
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 48px rgba(99, 102, 241, 0.2);
            border-color: rgba(99, 102, 241, 0.3);
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4);
        }
        
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 8px;
            line-height: 1.2;
        }
        
        .metric-label {
            font-size: 14px;
            color: rgba(255,255,255,0.7);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-trend {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-top: 12px;
            font-size: 14px;
            font-weight: 600;
        }
        
        .trend-positive { color: #10b981; }
        .trend-negative { color: #ef4444; }
        
        /* Enterprise Data Tables */
        .enterprise-table {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            overflow: hidden;
            margin: 16px 0;
        }
        
        .table-header {
            background: rgba(255, 255, 255, 0.05);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding: 16px;
            font-weight: 600;
            font-size: 14px;
            color: #ffffff;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .table-row {
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding: 16px;
            transition: all 0.2s ease;
            cursor: pointer;
        }
        
        .table-row:hover {
            background: rgba(99, 102, 241, 0.1);
            transform: translateX(4px);
        }
        
        .table-row:last-child {
            border-bottom: none;
        }
        
        /* Enterprise Sidebar */
        .enterprise-sidebar {
            background: linear-gradient(180deg, #1a1b2e 0%, #16213e 100%);
            border-right: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(20px);
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            border-radius: 8px;
            margin: 4px 8px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            color: rgba(255,255,255,0.8);
            text-decoration: none;
        }
        
        .nav-item:hover {
            background: rgba(99, 102, 241, 0.1);
            transform: translateX(6px);
            color: #ffffff;
        }
        
        .nav-item.active {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: #ffffff;
        }
        
        .nav-item.active::before {
            content: '';
            position: absolute;
            left: -8px;
            top: 50%;
            transform: translateY(-50%);
            width: 4px;
            height: 24px;
            background: #ffffff;
            border-radius: 2px;
        }
        
        /* Enterprise Forms */
        .enterprise-form {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 24px;
            backdrop-filter: blur(20px);
            margin: 16px 0;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 8px;
        }
        
        .form-input {
            width: 100%;
            padding: 12px 16px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            color: #ffffff;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #6366f1;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
            background: rgba(255, 255, 255, 0.08);
        }
        
        /* Enterprise Buttons */
        .btn-primary {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            color: #ffffff;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 12px 24px;
            color: #ffffff;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }
        
        /* Search Bar */
        .search-container {
            position: relative;
            margin: 16px 0;
        }
        
        .search-input {
            width: 100%;
            padding: 16px 24px 16px 48px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            color: #ffffff;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #6366f1;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
            background: rgba(255, 255, 255, 0.08);
        }
        
        .search-icon {
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            color: rgba(255, 255, 255, 0.5);
        }
        
        /* Status Badges */
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-active {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        
        .status-pending {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        
        .status-inactive {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        
        /* Notification System */
        .notification {
            background: rgba(255, 255, 255, 0.02);
            border-left: 4px solid var(--primary);
            border-radius: 6px;
            padding: 12px 16px;
            margin: 8px 0;
            backdrop-filter: blur(20px);
        }
        
        .notification.success {
            border-left-color: var(--success);
        }
        
        .notification.warning {
            border-left-color: var(--warning);
        }
        
        .notification.error {
            border-left-color: var(--error);
        }
        
        /* Progress Indicators */
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #6366f1, #8b5cf6);
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        /* Animations */
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        
        .animate-slide-up {
            animation: slideInUp 0.3s ease-out;
        }
        
        .animate-fade-in {
            animation: fadeIn 0.3s ease-out;
        }
        
        /* Mobile Responsiveness */
        @media (max-width: 768px) {
            .metric-card {
                padding: 16px;
            }
            
            .metric-value {
                font-size: 24px;
            }
            
            .glass-container {
                padding: 16px;
            }
            
            .table-row {
                padding: 12px;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def create_enterprise_metrics_grid(self, metrics: List[Dict[str, Any]]):
        """Create enterprise-style metrics grid"""
        cols = st.columns(len(metrics))
        
        for i, metric in enumerate(metrics):
            with cols[i]:
                self.render_metric_card(
                    metric.get('label', ''),
                    metric.get('value', ''),
                    metric.get('change', ''),
                    metric.get('trend', 'positive')
                )
    
    def render_metric_card(self, label: str, value: str, change: str = "", trend: str = "positive"):
        """Render enterprise metric card"""
        trend_class = f"trend-{trend}"
        trend_icon = "↗️" if trend == "positive" else "↘️" if trend == "negative" else "➡️"
        
        st.markdown(f"""
        <div class="metric-card animate-fade-in">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
            {f'<div class="metric-trend {trend_class}">{trend_icon} {change}</div>' if change else ''}
        </div>
        """, unsafe_allow_html=True)
    
    def render_enhanced_metric_cards(self, metrics_data: Dict[str, Any]):
        """Render enhanced metric cards with animations"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.render_metric_card("Total Revenue", "$125,430", "+12.5%", "positive")
        
        with col2:
            self.render_metric_card("Active Deals", "47", "+8", "positive")
        
        with col3:
            self.render_metric_card("Conversion Rate", "23.4%", "+2.1%", "positive")
        
        with col4:
            self.render_metric_card("Avg Deal Size", "$8,450", "-1.2%", "negative")
    
    def render_advanced_search(self) -> Dict[str, Any]:
        """Render advanced search with enterprise styling"""
        search_results = {}
        
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                search_query = st.text_input(
                    "🔍 Search", 
                    placeholder="Search contacts, deals, companies...",
                    key="enterprise_search"
                )
            
            with col2:
                search_filter = st.selectbox(
                    "Filter by:",
                    ["All", "Contacts", "Deals", "Companies", "Notes"],
                    key="search_filter"
                )
            
            with col3:
                date_range = st.selectbox(
                    "Date range:",
                    ["All time", "Today", "This week", "This month", "This quarter"],
                    key="date_range"
                )
            
            # Advanced filters
            with st.expander("🔧 Advanced Filters", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    deal_stages = st.multiselect(
                        "Deal Stages",
                        ["Lead", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
                    )
                
                with col2:
                    deal_value_range = st.slider(
                        "Deal Value Range",
                        0, 1000000, (0, 1000000),
                        step=10000,
                        format="$%d"
                    )
                
                with col3:
                    contact_sources = st.multiselect(
                        "Contact Sources",
                        ["Website", "Referral", "Cold Call", "Social Media", "Event", "Advertisement"]
                    )
        
        return {
            "query": search_query,
            "filter": search_filter,
            "date_range": date_range,
            "deal_stages": deal_stages,
            "deal_value_range": deal_value_range,
            "contact_sources": contact_sources
        }
    
    def render_enterprise_data_table(self, data: List[Dict[str, Any]], columns: List[str], 
                                   selectable: bool = True) -> List[str]:
        """Render enterprise-style data table"""
        if not data:
            st.info("No data available")
            return []
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        if selectable:
            # Add selection column
            selected_items = []
            
            # Header with select all
            cols = st.columns([1] + [3] * len(columns))
            with cols[0]:
                select_all = st.checkbox("Select All", key="select_all_header")
            
            for i, col in enumerate(columns):
                with cols[i + 1]:
                    st.markdown(f"**{col}**")
            
            # Data rows
            for idx, row in df.iterrows():
                cols = st.columns([1] + [3] * len(columns))
                
                with cols[0]:
                    selected = st.checkbox("", key=f"select_{idx}", value=select_all)
                    if selected:
                        selected_items.append(str(row.get('id', idx)))
                
                for i, col in enumerate(columns):
                    with cols[i + 1]:
                        st.text(str(row.get(col, "")))
            
            return selected_items
        else:
            st.dataframe(df[columns], use_container_width=True)
            return []
    
    def render_bulk_actions_bar(self, selected_items: List[str]):
        """Render bulk actions bar"""
        if not selected_items:
            return
        
        st.markdown(f"""
        <div class="glass-container">
            <div style="display: flex; align-items: center; gap: 16px;">
                <span style="color: var(--text);">{len(selected_items)} items selected</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("📧 Send Email", use_container_width=True):
                st.session_state.bulk_email = True
        
        with col2:
            if st.button("🏷️ Add Tags", use_container_width=True):
                st.session_state.bulk_tags = True
        
        with col3:
            if st.button("📋 Update Stage", use_container_width=True):
                st.session_state.bulk_stage = True
        
        with col4:
            if st.button("📤 Export", use_container_width=True):
                st.session_state.bulk_export = True
        
        with col5:
            if st.button("🗑️ Delete", use_container_width=True, type="secondary"):
                st.session_state.bulk_delete = True
    
    def render_activity_timeline(self):
        """Render activity timeline"""
        st.markdown("### 📋 Recent Activity")
        
        activities = [
            {"time": "2 min ago", "user": "John Doe", "action": "updated deal", "target": "ABC Corp Deal", "icon": "💼", "type": "deal"},
            {"time": "15 min ago", "user": "Jane Smith", "action": "sent email to", "target": "Mike Johnson", "icon": "📧", "type": "email"},
            {"time": "1 hour ago", "user": "System", "action": "auto-assigned lead", "target": "New Lead #1234", "icon": "🤖", "type": "system"},
            {"time": "3 hours ago", "user": "Sarah Wilson", "action": "closed deal", "target": "XYZ Solutions", "icon": "🎉", "type": "deal"},
            {"time": "5 hours ago", "user": "Mike Davis", "action": "created contact", "target": "New Contact", "icon": "👤", "type": "contact"},
        ]
        
        for activity in activities:
            priority_colors = {
                "deal": "#6366f1",
                "email": "#06b6d4", 
                "system": "#8b5cf6",
                "contact": "#10b981"
            }
            
            color = priority_colors.get(activity['type'], "#6b7280")
            
            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.02);
                border-left: 4px solid {color};
                border-radius: 6px;
                padding: 12px 16px;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 12px;
                transition: all 0.2s ease;
            " onmouseover="this.style.background='rgba(255,255,255,0.05)'" 
               onmouseout="this.style.background='rgba(255,255,255,0.02)'">
                <span style="font-size: 20px;">{activity['icon']}</span>
                <div style="flex: 1;">
                    <div style="color: #ffffff; font-size: 14px; font-weight: 500;">
                        <strong>{activity['user']}</strong> {activity['action']} <strong>{activity['target']}</strong>
                    </div>
                    <div style="color: rgba(255,255,255,0.6); font-size: 12px; margin-top: 2px;">
                        {activity['time']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_notification_center(self, show_notifications: bool = True):
        """Render notification center"""
        if not show_notifications:
            return
        
        st.markdown("### 🔔 Notifications")
        
        notifications = [
            {"type": "deal", "message": "Deal 'ABC Corp' moved to Negotiation", "time": "5 min ago", "priority": "high", "icon": "💼"},
            {"type": "email", "message": "Email campaign completed - 85% open rate", "time": "1 hour ago", "priority": "medium", "icon": "📧"},
            {"type": "task", "message": "Follow up with John Smith due today", "time": "2 hours ago", "priority": "high", "icon": "📋"},
            {"type": "system", "message": "Monthly report generated successfully", "time": "1 day ago", "priority": "low", "icon": "📊"},
        ]
        
        for notif in notifications:
            priority_colors = {"high": "#ef4444", "medium": "#f59e0b", "low": "#6b7280"}
            priority_color = priority_colors[notif['priority']]
            
            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.02);
                border-left: 4px solid {priority_color};
                border-radius: 6px;
                padding: 12px 16px;
                margin-bottom: 8px;
                transition: all 0.2s ease;
            " onmouseover="this.style.background='rgba(255,255,255,0.05)'" 
               onmouseout="this.style.background='rgba(255,255,255,0.02)'">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 18px;">{notif['icon']}</span>
                    <div style="flex: 1;">
                        <div style="color: #ffffff; font-size: 14px;">{notif['message']}</div>
                        <div style="color: rgba(255,255,255,0.6); font-size: 12px; margin-top: 4px;">{notif['time']}</div>
                    </div>
                    <div style="
                        background: {priority_color}20;
                        color: {priority_color};
                        padding: 2px 8px;
                        border-radius: 12px;
                        font-size: 10px;
                        font-weight: 600;
                        text-transform: uppercase;
                    ">{notif['priority']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Global enterprise design instance
enterprise_design = EnterpriseDesign()
