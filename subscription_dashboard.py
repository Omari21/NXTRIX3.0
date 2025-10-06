"""
Subscription Management Dashboard
Admin interface for managing subscriptions, billing, and feature access
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from subscription_manager import SubscriptionManager, SubscriptionTier
from feature_access_control import FeatureAccessControl, access_control

# Optional PostgreSQL import with error handling
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    # Create placeholder for psycopg2 when not available
    class RealDictCursor:
        pass

from typing import Dict, List, Any, Optional

class SubscriptionDashboard:
    """Admin dashboard for subscription management"""
    
    def __init__(self):
        self.sub_manager = SubscriptionManager()
        self.access_control = FeatureAccessControl()
        
    def show_admin_dashboard(self):
        """Main admin dashboard interface"""
        st.title("🏢 Subscription Management Dashboard")
        
        # Check admin access
        if not self._check_admin_access():
            st.error("Access denied. Admin privileges required.")
            return
            
        # Dashboard tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", 
            "👥 Users", 
            "💳 Billing", 
            "📈 Analytics", 
            "⚙️ Settings"
        ])
        
        with tab1:
            self._show_overview_tab()
            
        with tab2:
            self._show_users_tab()
            
        with tab3:
            self._show_billing_tab()
            
        with tab4:
            self._show_analytics_tab()
            
        with tab5:
            self._show_settings_tab()

    def _check_admin_access(self) -> bool:
        """Check if current user has admin access"""
        user_id = st.session_state.get('user_id')
        if not user_id:
            return False
            
        # Check if user has admin role
        try:
            conn = self.sub_manager.conn
            if not conn:
                return False
                
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT role, subscription_tier 
                    FROM profiles 
                    WHERE id = %s
                """, (user_id,))
                
                user_data = cur.fetchone()
                return user_data and (
                    user_data['role'] == 'admin' or 
                    user_data['subscription_tier'] == 'enterprise'
                )
                
        except Exception:
            return False

    def _show_overview_tab(self):
        """Show subscription overview metrics"""
        st.subheader("📊 Subscription Overview")
        
        # Get subscription metrics
        metrics = self._get_subscription_metrics()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Users",
                f"{metrics['total_users']:,}",
                f"+{metrics['new_users_this_month']:,} this month"
            )
            
        with col2:
            st.metric(
                "Active Subscriptions",
                f"{metrics['active_subscriptions']:,}",
                f"{metrics['subscription_growth']:+.1%} growth"
            )
            
        with col3:
            st.metric(
                "Monthly Revenue",
                f"${metrics['monthly_revenue']:,.2f}",
                f"{metrics['revenue_growth']:+.1%} vs last month"
            )
            
        with col4:
            st.metric(
                "Churn Rate",
                f"{metrics['churn_rate']:.1%}",
                f"{metrics['churn_change']:+.1%} vs last month"
            )
        
        # Subscription distribution pie chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Subscription Distribution")
            tier_data = metrics['tier_distribution']
            
            fig = px.pie(
                values=list(tier_data.values()),
                names=list(tier_data.keys()),
                title="Users by Subscription Tier"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Usage Statistics")
            usage_data = metrics['usage_stats']
            
            # Usage bar chart
            usage_df = pd.DataFrame([
                {"Feature": k.replace("_", " ").title(), "Usage": v}
                for k, v in usage_data.items()
            ])
            
            fig = px.bar(
                usage_df,
                x="Feature",
                y="Usage",
                title="Feature Usage This Month"
            )
            fig.update_xaxis(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

    def _show_users_tab(self):
        """Show user management interface"""
        st.subheader("👥 User Management")
        
        # User search and filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("🔍 Search users", placeholder="Email or name")
            
        with col2:
            tier_filter = st.selectbox(
                "Filter by tier",
                options=["All", "Free", "Pro", "Enterprise"]
            )
            
        with col3:
            status_filter = st.selectbox(
                "Filter by status",
                options=["All", "Active", "Trialing", "Canceled", "Past Due"]
            )
        
        # Get filtered users
        users_data = self._get_users_data(search_term, tier_filter, status_filter)
        
        if users_data:
            # Display users table
            users_df = pd.DataFrame(users_data)
            
            # Add action buttons
            st.subheader("Users")
            
            for idx, user in enumerate(users_data):
                with st.expander(f"{user['name']} ({user['email']})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Tier:** {user['subscription_tier'].title()}")
                        st.write(f"**Status:** {user['subscription_status'].title()}")
                        st.write(f"**Joined:** {user['created_at'].strftime('%Y-%m-%d')}")
                        
                    with col2:
                        st.write(f"**Role:** {user['role'].title()}")
                        if user['trial_end']:
                            st.write(f"**Trial Ends:** {user['trial_end'].strftime('%Y-%m-%d')}")
                        st.write(f"**Last Active:** {user.get('last_active', 'N/A')}")
                        
                    with col3:
                        # User management actions
                        if st.button(f"Upgrade User", key=f"upgrade_{user['id']}"):
                            self._show_upgrade_user_modal(user['id'])
                            
                        if st.button(f"View Usage", key=f"usage_{user['id']}"):
                            self._show_user_usage(user['id'])
                            
                        if st.button(f"Reset Trial", key=f"trial_{user['id']}"):
                            self._reset_user_trial(user['id'])
        else:
            st.info("No users found matching the criteria")

    def _show_billing_tab(self):
        """Show billing and payment management"""
        st.subheader("💳 Billing Management")
        
        # Billing overview
        billing_data = self._get_billing_data()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Revenue",
                f"${billing_data['total_revenue']:,.2f}",
                f"+${billing_data['revenue_this_month']:,.2f} this month"
            )
            
        with col2:
            st.metric(
                "Failed Payments",
                f"{billing_data['failed_payments']:,}",
                f"{billing_data['failure_rate']:.1%} failure rate"
            )
            
        with col3:
            st.metric(
                "Pending Invoices",
                f"{billing_data['pending_invoices']:,}",
                f"${billing_data['pending_amount']:,.2f} value"
            )
        
        # Recent transactions
        st.subheader("Recent Transactions")
        transactions = self._get_recent_transactions()
        
        if transactions:
            transactions_df = pd.DataFrame(transactions)
            st.dataframe(
                transactions_df[['user_email', 'amount', 'status', 'created_at']],
                use_container_width=True
            )
        
        # Revenue chart
        st.subheader("Revenue Trend")
        revenue_data = self._get_revenue_trend()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=revenue_data['dates'],
            y=revenue_data['revenue'],
            mode='lines+markers',
            name='Revenue'
        ))
        fig.update_layout(title="Monthly Revenue Trend")
        st.plotly_chart(fig, use_container_width=True)

    def _show_analytics_tab(self):
        """Show subscription analytics"""
        st.subheader("📈 Subscription Analytics")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        analytics_data = self._get_analytics_data(start_date, end_date)
        
        # Cohort analysis
        st.subheader("User Cohorts")
        cohort_data = analytics_data['cohort_analysis']
        
        if cohort_data:
            cohort_df = pd.DataFrame(cohort_data)
            fig = px.imshow(
                cohort_df,
                title="User Retention by Cohort",
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Feature adoption
        st.subheader("Feature Adoption")
        feature_data = analytics_data['feature_adoption']
        
        feature_df = pd.DataFrame([
            {"Feature": k.replace("_", " ").title(), "Adoption Rate": f"{v:.1%}"}
            for k, v in feature_data.items()
        ])
        
        fig = px.bar(
            feature_df,
            x="Feature",
            y="Adoption Rate",
            title="Feature Adoption Rates"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Usage patterns
        st.subheader("Usage Patterns")
        usage_patterns = analytics_data['usage_patterns']
        
        # Daily usage heatmap
        usage_df = pd.DataFrame(usage_patterns)
        fig = px.line(
            usage_df,
            x="hour",
            y="usage_count",
            title="Hourly Usage Patterns"
        )
        st.plotly_chart(fig, use_container_width=True)

    def _show_settings_tab(self):
        """Show system settings and configuration"""
        st.subheader("⚙️ System Settings")
        
        # Subscription tier settings
        st.subheader("Subscription Tier Configuration")
        
        # Load current limits
        current_limits = self._get_current_limits()
        
        for tier in ["free", "pro", "enterprise"]:
            with st.expander(f"{tier.title()} Tier Settings"):
                st.write(f"Configure limits for {tier.title()} tier:")
                
                tier_limits = current_limits.get(tier, {})
                
                col1, col2 = st.columns(2)
                
                with col1:
                    deals_limit = st.number_input(
                        "Deals per month",
                        value=tier_limits.get('deals_per_month', 0),
                        min_value=-1,
                        key=f"{tier}_deals"
                    )
                    
                    investors_limit = st.number_input(
                        "Investors per month",
                        value=tier_limits.get('investors_per_month', 0),
                        min_value=-1,
                        key=f"{tier}_investors"
                    )
                    
                    ai_limit = st.number_input(
                        "AI queries per month",
                        value=tier_limits.get('ai_queries_per_month', 0),
                        min_value=-1,
                        key=f"{tier}_ai"
                    )
                    
                with col2:
                    automation_limit = st.number_input(
                        "Automation rules",
                        value=tier_limits.get('automation_rules', 0),
                        min_value=-1,
                        key=f"{tier}_automation"
                    )
                    
                    email_limit = st.number_input(
                        "Email campaigns per month",
                        value=tier_limits.get('email_campaigns_per_month', 0),
                        min_value=-1,
                        key=f"{tier}_email"
                    )
                    
                    storage_limit = st.number_input(
                        "Storage (GB)",
                        value=float(tier_limits.get('storage_gb', 0)),
                        min_value=-1.0,
                        key=f"{tier}_storage"
                    )
                
                if st.button(f"Update {tier.title()} Limits", key=f"update_{tier}"):
                    self._update_tier_limits(tier, {
                        'deals_per_month': deals_limit,
                        'investors_per_month': investors_limit,
                        'ai_queries_per_month': ai_limit,
                        'automation_rules': automation_limit,
                        'email_campaigns_per_month': email_limit,
                        'storage_gb': storage_limit
                    })
        
        # System maintenance
        st.subheader("System Maintenance")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Reset All Trial Periods"):
                self._reset_all_trials()
                
        with col2:
            if st.button("Generate Usage Report"):
                self._generate_usage_report()
                
        with col3:
            if st.button("Export User Data"):
                self._export_user_data()

    def _get_subscription_metrics(self) -> Dict[str, Any]:
        """Get subscription overview metrics"""
        try:
            conn = self.sub_manager.conn
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Total users
                cur.execute("SELECT COUNT(*) as total FROM profiles")
                total_users = cur.fetchone()['total']
                
                # New users this month
                cur.execute("""
                    SELECT COUNT(*) as new_users 
                    FROM profiles 
                    WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)
                """)
                new_users = cur.fetchone()['new_users']
                
                # Active subscriptions
                cur.execute("""
                    SELECT COUNT(*) as active 
                    FROM profiles 
                    WHERE subscription_status = 'active'
                """)
                active_subs = cur.fetchone()['active']
                
                # Tier distribution
                cur.execute("""
                    SELECT subscription_tier, COUNT(*) as count
                    FROM profiles
                    GROUP BY subscription_tier
                """)
                tier_dist = {row['subscription_tier']: row['count'] for row in cur.fetchall()}
                
                return {
                    'total_users': total_users,
                    'new_users_this_month': new_users,
                    'active_subscriptions': active_subs,
                    'subscription_growth': 0.15,  # Mock data
                    'monthly_revenue': 15000.00,  # Mock data
                    'revenue_growth': 0.08,  # Mock data
                    'churn_rate': 0.05,  # Mock data
                    'churn_change': -0.02,  # Mock data
                    'tier_distribution': tier_dist,
                    'usage_stats': {
                        'deals_created': 1250,
                        'ai_queries': 3400,
                        'documents_generated': 890,
                        'email_campaigns': 156
                    }
                }
                
        except Exception as e:
            st.error(f"Error loading metrics: {e}")
            return {}

    def _get_users_data(self, search: str, tier_filter: str, status_filter: str) -> List[Dict]:
        """Get filtered users data"""
        try:
            conn = self.sub_manager.conn
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT 
                        id, name, email, role, subscription_tier, 
                        subscription_status, created_at, trial_end
                    FROM profiles
                    WHERE 1=1
                """
                params = []
                
                if search:
                    query += " AND (name ILIKE %s OR email ILIKE %s)"
                    params.extend([f"%{search}%", f"%{search}%"])
                    
                if tier_filter != "All":
                    query += " AND subscription_tier = %s"
                    params.append(tier_filter.lower())
                    
                if status_filter != "All":
                    query += " AND subscription_status = %s"
                    params.append(status_filter.lower())
                
                query += " ORDER BY created_at DESC LIMIT 50"
                
                cur.execute(query, params)
                return cur.fetchall()
                
        except Exception as e:
            st.error(f"Error loading users: {e}")
            return []

    def _get_billing_data(self) -> Dict[str, Any]:
        """Get billing overview data"""
        # Mock billing data - replace with actual billing system integration
        return {
            'total_revenue': 125000.00,
            'revenue_this_month': 15000.00,
            'failed_payments': 23,
            'failure_rate': 0.05,
            'pending_invoices': 12,
            'pending_amount': 3600.00
        }

    def _get_recent_transactions(self) -> List[Dict]:
        """Get recent billing transactions"""
        # Mock transaction data
        return [
            {
                'user_email': 'user1@example.com',
                'amount': '$97.00',
                'status': 'Succeeded',
                'created_at': '2025-09-15'
            },
            {
                'user_email': 'user2@example.com',
                'amount': '$297.00',
                'status': 'Failed',
                'created_at': '2025-09-14'
            }
        ]

    def _get_revenue_trend(self) -> Dict[str, List]:
        """Get revenue trend data"""
        # Mock revenue trend
        return {
            'dates': ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06'],
            'revenue': [8000, 9500, 11000, 12500, 14000, 15000]
        }

    def _get_analytics_data(self, start_date, end_date) -> Dict[str, Any]:
        """Get analytics data for date range"""
        # Mock analytics data
        return {
            'cohort_analysis': [
                [1.0, 0.8, 0.6, 0.5],
                [1.0, 0.85, 0.7, 0.6],
                [1.0, 0.9, 0.75, 0.65]
            ],
            'feature_adoption': {
                'deal_tracker': 0.95,
                'ai_analysis': 0.65,
                'automation': 0.45,
                'reports': 0.80
            },
            'usage_patterns': [
                {'hour': i, 'usage_count': 50 + i * 10 + (i % 3) * 20}
                for i in range(24)
            ]
        }

    def _get_current_limits(self) -> Dict[str, Dict]:
        """Get current subscription limits"""
        try:
            conn = self.sub_manager.conn
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT tier, limit_type, limit_value
                    FROM subscription_limits
                    WHERE is_active = true
                """)
                
                limits = {}
                for row in cur.fetchall():
                    tier = row['tier']
                    if tier not in limits:
                        limits[tier] = {}
                    limits[tier][row['limit_type']] = row['limit_value']
                
                return limits
                
        except Exception:
            return {}

    def _update_tier_limits(self, tier: str, limits: Dict[str, Any]):
        """Update subscription tier limits"""
        try:
            conn = self.sub_manager.conn
            with conn.cursor() as cur:
                for limit_type, limit_value in limits.items():
                    cur.execute("""
                        UPDATE subscription_limits 
                        SET limit_value = %s, updated_at = NOW()
                        WHERE tier = %s AND limit_type = %s
                    """, (limit_value, tier, limit_type))
                
                conn.commit()
                st.success(f"Updated {tier.title()} tier limits")
                
        except Exception as e:
            st.error(f"Error updating limits: {e}")

    def show_user_subscription_widget(self, user_id: str):
        """Show subscription widget for regular users"""
        subscription = self.sub_manager.get_user_subscription(user_id)
        
        if not subscription:
            st.error("Unable to load subscription information")
            return
            
        st.subheader(f"💎 Your {subscription.tier.value.title()} Plan")
        
        # Plan details
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Status:** {subscription.status.title()}")
            st.write(f"**Billing Cycle:** {subscription.billing_cycle_start.strftime('%m/%d')} - {subscription.billing_cycle_end.strftime('%m/%d')}")
            
        with col2:
            if subscription.trial_end:
                days_left = (subscription.trial_end - datetime.now()).days
                if days_left > 0:
                    st.write(f"**Trial:** {days_left} days remaining")
                else:
                    st.write("**Trial:** Expired")
        
        # Usage summary
        if subscription.tier != SubscriptionTier.ENTERPRISE:
            st.subheader("📊 Usage This Month")
            
            usage_items = [
                ('deals_per_month', 'Deals', '📈'),
                ('ai_queries_per_month', 'AI Queries', '🤖'),
                ('email_campaigns_per_month', 'Email Campaigns', '📧')
            ]
            
            for usage_type, label, icon in usage_items:
                current = subscription.current_usage.get(usage_type, 0)
                limit = getattr(subscription.limits, usage_type)
                
                if limit > 0:
                    progress = min(current / limit, 1.0)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"{icon} **{label}:** {current:,} / {limit:,}")
                        st.progress(progress)
                    with col2:
                        if progress > 0.8:
                            st.warning("⚠️")
        
        # Upgrade options
        if subscription.tier != SubscriptionTier.ENTERPRISE:
            st.subheader("🚀 Upgrade Your Plan")
            
            if subscription.tier == SubscriptionTier.FREE:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Upgrade to Pro - $97/month"):
                        self._handle_upgrade(user_id, "pro")
                with col2:
                    if st.button("Upgrade to Enterprise - $297/month"):
                        self._handle_upgrade(user_id, "enterprise")
            else:
                if st.button("Upgrade to Enterprise - $297/month"):
                    self._handle_upgrade(user_id, "enterprise")

    def _handle_upgrade(self, user_id: str, new_tier: str):
        """Handle subscription upgrade"""
        if self.sub_manager.upgrade_subscription(user_id, SubscriptionTier(new_tier)):
            st.success(f"Successfully upgraded to {new_tier.title()}!")
            st.rerun()
        else:
            st.error("Upgrade failed. Please try again.")

# Global dashboard instance
subscription_dashboard = SubscriptionDashboard()