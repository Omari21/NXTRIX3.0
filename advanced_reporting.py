"""
Advanced Reporting & Analytics System for NXTRIX CRM
Comprehensive business intelligence with automated insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sqlite3
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
from dataclasses import dataclass
from enum import Enum

class ReportType(Enum):
    DEALS = "deals"
    LEADS = "leads"
    FINANCIAL = "financial"
    PERFORMANCE = "performance"
    MARKET = "market"
    TEAM = "team"

class TimeFrame(Enum):
    LAST_7_DAYS = "7_days"
    LAST_30_DAYS = "30_days"
    LAST_90_DAYS = "90_days"
    LAST_6_MONTHS = "6_months"
    LAST_12_MONTHS = "12_months"
    CUSTOM = "custom"

@dataclass
class ReportMetric:
    """Data structure for report metrics"""
    name: str
    value: float
    change: float
    change_direction: str
    format_type: str = "number"  # number, currency, percentage

class AdvancedReporting:
    """Advanced reporting and analytics system"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.init_reporting_tables()
    
    def init_reporting_tables(self):
        """Initialize reporting-specific database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # KPI tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kpi_metrics (
                    id TEXT PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    period_start TIMESTAMP NOT NULL,
                    period_end TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Report generation log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS report_log (
                    id TEXT PRIMARY KEY,
                    report_type TEXT NOT NULL,
                    parameters TEXT,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error initializing reporting database: {e}")
    
    def get_deal_metrics(self, timeframe: TimeFrame) -> Dict[str, ReportMetric]:
        """Get deal-related metrics"""
        try:
            start_date, end_date = self._get_date_range(timeframe)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total deals
            cursor.execute('''
                SELECT COUNT(*) FROM deals 
                WHERE date_added BETWEEN ? AND ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            total_deals = cursor.fetchone()[0]
            
            # Average AI score
            cursor.execute('''
                SELECT AVG(ai_score) FROM deals 
                WHERE date_added BETWEEN ? AND ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            avg_ai_score = cursor.fetchone()[0] or 0
            
            # Total deal value
            cursor.execute('''
                SELECT SUM(purchase_price) FROM deals 
                WHERE date_added BETWEEN ? AND ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            total_value = cursor.fetchone()[0] or 0
            
            # Average deal size
            avg_deal_size = total_value / total_deals if total_deals > 0 else 0
            
            # Get previous period for comparison
            prev_start = start_date - (end_date - start_date)
            prev_end = start_date
            
            cursor.execute('''
                SELECT COUNT(*) FROM deals 
                WHERE date_added BETWEEN ? AND ?
            ''', (prev_start.isoformat(), prev_end.isoformat()))
            prev_total_deals = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT SUM(purchase_price) FROM deals 
                WHERE date_added BETWEEN ? AND ?
            ''', (prev_start.isoformat(), prev_end.isoformat()))
            prev_total_value = cursor.fetchone()[0] or 0
            
            conn.close()
            
            # Calculate changes
            deal_change = ((total_deals - prev_total_deals) / prev_total_deals * 100) if prev_total_deals > 0 else 0
            value_change = ((total_value - prev_total_value) / prev_total_value * 100) if prev_total_value > 0 else 0
            
            return {
                'total_deals': ReportMetric(
                    name="Total Deals",
                    value=total_deals,
                    change=deal_change,
                    change_direction="up" if deal_change > 0 else "down"
                ),
                'avg_ai_score': ReportMetric(
                    name="Average AI Score",
                    value=avg_ai_score,
                    change=0,  # Would need historical tracking
                    change_direction="neutral"
                ),
                'total_value': ReportMetric(
                    name="Total Deal Value",
                    value=total_value,
                    change=value_change,
                    change_direction="up" if value_change > 0 else "down",
                    format_type="currency"
                ),
                'avg_deal_size': ReportMetric(
                    name="Average Deal Size",
                    value=avg_deal_size,
                    change=0,
                    change_direction="neutral",
                    format_type="currency"
                )
            }
            
        except Exception as e:
            st.error(f"Error getting deal metrics: {e}")
            return {}
    
    def get_lead_metrics(self, timeframe: TimeFrame) -> Dict[str, ReportMetric]:
        """Get lead-related metrics"""
        try:
            start_date, end_date = self._get_date_range(timeframe)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if leads table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='leads'")
            if not cursor.fetchone():
                conn.close()
                return {}
            
            # Total leads
            cursor.execute('''
                SELECT COUNT(*) FROM leads 
                WHERE created_at BETWEEN ? AND ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            total_leads = cursor.fetchone()[0]
            
            # Hot leads (score >= 80)
            cursor.execute('''
                SELECT COUNT(*) FROM leads 
                WHERE created_at BETWEEN ? AND ? AND score >= 80
            ''', (start_date.isoformat(), end_date.isoformat()))
            hot_leads = cursor.fetchone()[0]
            
            # Conversion rate (leads to deals - approximate)
            conversion_rate = (hot_leads / total_leads * 100) if total_leads > 0 else 0
            
            conn.close()
            
            return {
                'total_leads': ReportMetric(
                    name="Total Leads",
                    value=total_leads,
                    change=0,
                    change_direction="neutral"
                ),
                'hot_leads': ReportMetric(
                    name="Hot Leads",
                    value=hot_leads,
                    change=0,
                    change_direction="neutral"
                ),
                'conversion_rate': ReportMetric(
                    name="Lead Quality Rate",
                    value=conversion_rate,
                    change=0,
                    change_direction="neutral",
                    format_type="percentage"
                )
            }
            
        except Exception as e:
            st.error(f"Error getting lead metrics: {e}")
            return {}
    
    def get_financial_metrics(self, timeframe: TimeFrame) -> Dict[str, ReportMetric]:
        """Get financial performance metrics"""
        try:
            start_date, end_date = self._get_date_range(timeframe)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total investment potential
            cursor.execute('''
                SELECT SUM(purchase_price), AVG(cap_rate), AVG(cash_on_cash_return)
                FROM deals WHERE date_added BETWEEN ? AND ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            result = cursor.fetchone()
            total_investment = result[0] or 0
            avg_cap_rate = result[1] or 0
            avg_coc_return = result[2] or 0
            
            # Projected annual income
            cursor.execute('''
                SELECT SUM(monthly_rent * 12) FROM deals 
                WHERE date_added BETWEEN ? AND ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            projected_income = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_investment': ReportMetric(
                    name="Total Investment Value",
                    value=total_investment,
                    change=0,
                    change_direction="neutral",
                    format_type="currency"
                ),
                'avg_cap_rate': ReportMetric(
                    name="Average Cap Rate",
                    value=avg_cap_rate,
                    change=0,
                    change_direction="neutral",
                    format_type="percentage"
                ),
                'avg_coc_return': ReportMetric(
                    name="Average CoC Return",
                    value=avg_coc_return,
                    change=0,
                    change_direction="neutral",
                    format_type="percentage"
                ),
                'projected_income': ReportMetric(
                    name="Projected Annual Income",
                    value=projected_income,
                    change=0,
                    change_direction="neutral",
                    format_type="currency"
                )
            }
            
        except Exception as e:
            st.error(f"Error getting financial metrics: {e}")
            return {}
    
    def generate_deals_chart(self, timeframe: TimeFrame) -> go.Figure:
        """Generate deals analysis chart"""
        try:
            start_date, end_date = self._get_date_range(timeframe)
            
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query('''
                SELECT date_added, ai_score, purchase_price, property_address as address
                FROM deals 
                WHERE date_added BETWEEN ? AND ?
                ORDER BY date_added
            ''', conn, params=[start_date.isoformat(), end_date.isoformat()])
            conn.close()
            
            if df.empty:
                fig = go.Figure()
                fig.add_annotation(text="No data available for selected timeframe", 
                                 xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
                return fig
            
            # Convert date column
            df['date_added'] = pd.to_datetime(df['date_added'])
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Deals Over Time', 'AI Score Distribution', 
                              'Price vs AI Score', 'Deal Value Distribution'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Deals over time
            daily_deals = df.groupby(df['date_added'].dt.date).size().reset_index()
            daily_deals.columns = ['date', 'count']
            
            fig.add_trace(
                go.Scatter(x=daily_deals['date'], y=daily_deals['count'],
                          mode='lines+markers', name='Daily Deals'),
                row=1, col=1
            )
            
            # AI Score histogram
            fig.add_trace(
                go.Histogram(x=df['ai_score'], nbinsx=20, name='AI Score Distribution'),
                row=1, col=2
            )
            
            # Price vs AI Score scatter
            fig.add_trace(
                go.Scatter(x=df['ai_score'], y=df['purchase_price'],
                          mode='markers', name='Price vs Score',
                          text=df['address'],
                          hovertemplate='AI Score: %{x}<br>Price: $%{y:,.0f}<br>%{text}'),
                row=2, col=1
            )
            
            # Price distribution
            fig.add_trace(
                go.Histogram(x=df['purchase_price'], nbinsx=20, name='Price Distribution'),
                row=2, col=2
            )
            
            fig.update_layout(height=800, showlegend=False, title_text="Deal Analysis Dashboard")
            return fig
            
        except Exception as e:
            st.error(f"Error generating deals chart: {e}")
            return go.Figure()
    
    def generate_financial_chart(self, timeframe: TimeFrame) -> go.Figure:
        """Generate financial performance chart"""
        try:
            start_date, end_date = self._get_date_range(timeframe)
            
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query('''
                SELECT date_added, cap_rate, cash_on_cash_return, monthly_rent, purchase_price
                FROM deals 
                WHERE date_added BETWEEN ? AND ?
                ORDER BY date_added
            ''', conn, params=[start_date.isoformat(), end_date.isoformat()])
            conn.close()
            
            if df.empty:
                fig = go.Figure()
                fig.add_annotation(text="No financial data available", 
                                 xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
                return fig
            
            # Create financial performance dashboard
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Cap Rate Distribution', 'Cash-on-Cash Returns', 
                              'Monthly Rent vs Price', 'Return Metrics Over Time'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Cap rate histogram
            fig.add_trace(
                go.Histogram(x=df['cap_rate'], nbinsx=20, name='Cap Rate %'),
                row=1, col=1
            )
            
            # Cash-on-cash return histogram
            fig.add_trace(
                go.Histogram(x=df['cash_on_cash_return'], nbinsx=20, name='CoC Return %'),
                row=1, col=2
            )
            
            # Rent vs Price scatter
            fig.add_trace(
                go.Scatter(x=df['purchase_price'], y=df['monthly_rent'],
                          mode='markers', name='Rent vs Price',
                          hovertemplate='Price: $%{x:,.0f}<br>Monthly Rent: $%{y:,.0f}'),
                row=2, col=1
            )
            
            # Returns over time
            df['date_added'] = pd.to_datetime(df['date_added'])
            df_sorted = df.sort_values('date_added')
            
            fig.add_trace(
                go.Scatter(x=df_sorted['date_added'], y=df_sorted['cap_rate'],
                          mode='lines+markers', name='Cap Rate Trend'),
                row=2, col=2
            )
            
            fig.update_layout(height=800, showlegend=False, title_text="Financial Performance Dashboard")
            return fig
            
        except Exception as e:
            st.error(f"Error generating financial chart: {e}")
            return go.Figure()
    
    def _get_date_range(self, timeframe: TimeFrame) -> Tuple[datetime, datetime]:
        """Get date range for timeframe"""
        end_date = datetime.now()
        
        if timeframe == TimeFrame.LAST_7_DAYS:
            start_date = end_date - timedelta(days=7)
        elif timeframe == TimeFrame.LAST_30_DAYS:
            start_date = end_date - timedelta(days=30)
        elif timeframe == TimeFrame.LAST_90_DAYS:
            start_date = end_date - timedelta(days=90)
        elif timeframe == TimeFrame.LAST_6_MONTHS:
            start_date = end_date - timedelta(days=180)
        elif timeframe == TimeFrame.LAST_12_MONTHS:
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)  # Default
        
        return start_date, end_date
    
    def export_report_data(self, report_type: ReportType, timeframe: TimeFrame) -> pd.DataFrame:
        """Export report data as DataFrame"""
        try:
            start_date, end_date = self._get_date_range(timeframe)
            
            conn = sqlite3.connect(self.db_path)
            
            if report_type == ReportType.DEALS:
                df = pd.read_sql_query('''
                    SELECT * FROM deals 
                    WHERE date_added BETWEEN ? AND ?
                    ORDER BY date_added DESC
                ''', conn, params=[start_date.isoformat(), end_date.isoformat()])
            
            elif report_type == ReportType.LEADS:
                # Try to get leads data if table exists
                try:
                    df = pd.read_sql_query('''
                        SELECT * FROM leads 
                        WHERE created_at BETWEEN ? AND ?
                        ORDER BY created_at DESC
                    ''', conn, params=[start_date.isoformat(), end_date.isoformat()])
                except:
                    df = pd.DataFrame()  # Return empty if table doesn't exist
            
            else:
                df = pd.DataFrame()  # Default empty
            
            conn.close()
            return df
            
        except Exception as e:
            st.error(f"Error exporting report data: {e}")
            return pd.DataFrame()

def show_advanced_reporting():
    """Show advanced reporting interface"""
    st.header("📊 Advanced Reporting & Analytics")
    st.write("Comprehensive business intelligence and performance insights.")
    
    # Initialize reporting system
    if 'reporting_system' not in st.session_state:
        st.session_state.reporting_system = AdvancedReporting()
    
    reporting = st.session_state.reporting_system
    
    # Time frame selector
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        timeframe = st.selectbox("📅 Select Time Frame", [
            ("Last 7 Days", TimeFrame.LAST_7_DAYS),
            ("Last 30 Days", TimeFrame.LAST_30_DAYS),
            ("Last 90 Days", TimeFrame.LAST_90_DAYS),
            ("Last 6 Months", TimeFrame.LAST_6_MONTHS),
            ("Last 12 Months", TimeFrame.LAST_12_MONTHS)
        ], format_func=lambda x: x[0])[1]
    
    with col2:
        report_type = st.selectbox("📋 Report Type", [
            ("All Reports", "all"),
            ("Deal Analysis", "deals"),
            ("Lead Analytics", "leads"),
            ("Financial Performance", "financial")
        ], format_func=lambda x: x[0])[1]
    
    with col3:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Report tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Executive Summary",
        "🏠 Deal Analytics",
        "💰 Financial Performance",
        "📊 Export & Reports"
    ])
    
    with tab1:
        show_executive_summary(reporting, timeframe)
    
    with tab2:
        show_deal_analytics(reporting, timeframe)
    
    with tab3:
        show_financial_performance(reporting, timeframe)
    
    with tab4:
        show_export_reports(reporting, timeframe)

def show_executive_summary(reporting: AdvancedReporting, timeframe: TimeFrame):
    """Show executive summary dashboard"""
    st.subheader("📈 Executive Summary")
    
    # Get all metrics
    deal_metrics = reporting.get_deal_metrics(timeframe)
    lead_metrics = reporting.get_lead_metrics(timeframe)
    financial_metrics = reporting.get_financial_metrics(timeframe)
    
    # Key Performance Indicators
    st.markdown("### 🎯 Key Performance Indicators")
    
    if deal_metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            metric = deal_metrics['total_deals']
            delta_color = "normal" if metric.change_direction == "up" else "inverse"
            st.metric(
                metric.name,
                f"{int(metric.value)}",
                delta=f"{metric.change:.1f}%" if metric.change != 0 else None,
                delta_color=delta_color
            )
        
        with col2:
            metric = deal_metrics['total_value']
            st.metric(
                metric.name,
                f"${metric.value:,.0f}",
                delta=f"{metric.change:.1f}%" if metric.change != 0 else None
            )
        
        with col3:
            metric = deal_metrics['avg_deal_size']
            st.metric(metric.name, f"${metric.value:,.0f}")
        
        with col4:
            metric = deal_metrics['avg_ai_score']
            st.metric(metric.name, f"{metric.value:.1f}/100")
    
    # Lead metrics if available
    if lead_metrics:
        st.markdown("### 👥 Lead Performance")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            metric = lead_metrics['total_leads']
            st.metric(metric.name, f"{int(metric.value)}")
        
        with col2:
            metric = lead_metrics['hot_leads']
            st.metric(metric.name, f"{int(metric.value)}")
        
        with col3:
            metric = lead_metrics['conversion_rate']
            st.metric(metric.name, f"{metric.value:.1f}%")
    
    # Financial overview
    if financial_metrics:
        st.markdown("### 💰 Financial Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            metric = financial_metrics['total_investment']
            st.metric(metric.name, f"${metric.value:,.0f}")
        
        with col2:
            metric = financial_metrics['projected_income']
            st.metric(metric.name, f"${metric.value:,.0f}")
        
        with col3:
            metric = financial_metrics['avg_cap_rate']
            st.metric(metric.name, f"{metric.value:.2f}%")
        
        with col4:
            metric = financial_metrics['avg_coc_return']
            st.metric(metric.name, f"{metric.value:.2f}%")
    
    # Performance insights
    st.markdown("### 🔍 Key Insights")
    insights = []
    
    if deal_metrics:
        total_deals = deal_metrics['total_deals'].value
        avg_score = deal_metrics['avg_ai_score'].value
        
        if total_deals > 0:
            if avg_score >= 80:
                insights.append("🎯 **Excellent Deal Quality**: Your average AI score is above 80, indicating high-quality deal sourcing.")
            elif avg_score >= 60:
                insights.append("📈 **Good Deal Flow**: Solid deal quality with room for improvement in sourcing criteria.")
            else:
                insights.append("⚠️ **Focus on Quality**: Consider refining your deal sourcing to improve average AI scores.")
    
    if financial_metrics:
        avg_cap_rate = financial_metrics['avg_cap_rate'].value
        if avg_cap_rate >= 8:
            insights.append("💰 **Strong Returns**: Your deals show excellent cap rates above 8%.")
        elif avg_cap_rate >= 6:
            insights.append("📊 **Solid Performance**: Good cap rates in the 6-8% range.")
    
    if not insights:
        insights.append("📊 **Getting Started**: Add more deals to see personalized insights and recommendations.")
    
    for insight in insights:
        st.markdown(insight)

def show_deal_analytics(reporting: AdvancedReporting, timeframe: TimeFrame):
    """Show detailed deal analytics"""
    st.subheader("🏠 Deal Analytics Dashboard")
    
    # Generate and display deals chart
    fig = reporting.generate_deals_chart(timeframe)
    st.plotly_chart(fig, use_container_width=True, key="deal_analytics_tab_chart")
    
    # Deal summary statistics
    st.markdown("### 📊 Deal Summary")
    deal_metrics = reporting.get_deal_metrics(timeframe)
    
    if deal_metrics:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Volume Metrics**")
            st.markdown(f"• Total Deals: {int(deal_metrics['total_deals'].value)}")
            st.markdown(f"• Average AI Score: {deal_metrics['avg_ai_score'].value:.1f}/100")
        
        with col2:
            st.markdown("**Value Metrics**")
            st.markdown(f"• Total Value: ${deal_metrics['total_value'].value:,.0f}")
            st.markdown(f"• Average Deal Size: ${deal_metrics['avg_deal_size'].value:,.0f}")

def show_financial_performance(reporting: AdvancedReporting, timeframe: TimeFrame):
    """Show financial performance analytics"""
    st.subheader("💰 Financial Performance")
    
    # Generate and display financial chart
    fig = reporting.generate_financial_chart(timeframe)
    st.plotly_chart(fig, use_container_width=True, key="financial_performance_tab_chart")
    
    # Financial summary
    st.markdown("### 💡 Financial Insights")
    financial_metrics = reporting.get_financial_metrics(timeframe)
    
    if financial_metrics:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Investment Metrics**")
            st.markdown(f"• Total Investment: ${financial_metrics['total_investment'].value:,.0f}")
            st.markdown(f"• Projected Income: ${financial_metrics['projected_income'].value:,.0f}")
        
        with col2:
            st.markdown("**Return Metrics**")
            st.markdown(f"• Average Cap Rate: {financial_metrics['avg_cap_rate'].value:.2f}%")
            st.markdown(f"• Average CoC Return: {financial_metrics['avg_coc_return'].value:.2f}%")

def show_export_reports(reporting: AdvancedReporting, timeframe: TimeFrame):
    """Show report export options"""
    st.subheader("📊 Export & Custom Reports")
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📥 Quick Exports")
        
        if st.button("📊 Export Deal Data"):
            df = reporting.export_report_data(ReportType.DEALS, timeframe)
            if not df.empty:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="💾 Download Deal Data (CSV)",
                    data=csv,
                    file_name=f"deal_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                st.success(f"✅ Deal data ready for download ({len(df)} records)")
            else:
                st.warning("No deal data available for export")
        
        if st.button("👥 Export Lead Data"):
            df = reporting.export_report_data(ReportType.LEADS, timeframe)
            if not df.empty:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="💾 Download Lead Data (CSV)",
                    data=csv,
                    file_name=f"lead_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                st.success(f"✅ Lead data ready for download ({len(df)} records)")
            else:
                st.info("No lead data available for export")
    
    with col2:
        st.markdown("### 🎨 Custom Reports")
        st.info("🚧 Custom report builder coming soon!")
        st.markdown("""
        **Planned Features:**
        - Custom date ranges
        - Advanced filtering
        - Scheduled reports
        - PDF export
        - Email delivery
        """)
    
    # Data preview
    st.markdown("### 👀 Data Preview")
    preview_type = st.selectbox("Select data to preview", [
        ("Deal Data", ReportType.DEALS),
        ("Lead Data", ReportType.LEADS)
    ], format_func=lambda x: x[0])
    
    if st.button("🔍 Show Preview"):
        df = reporting.export_report_data(preview_type[1], timeframe)
        if not df.empty:
            st.dataframe(df.head(20), use_container_width=True)
            st.caption(f"Showing first 20 of {len(df)} records")
        else:
            st.info("No data available for preview")