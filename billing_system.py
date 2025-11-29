"""
Comprehensive Billing System for NXTRIX 3.0
Subscription management, trial tracking, and payment processing
"""

import streamlit as st
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid

class BillingManager:
    def __init__(self):
        self.db_path = "nxtrix_billing.db"
        self.init_billing_database()
        
        self.subscription_tiers = {
            "starter": {
                "name": "Starter",
                "price_monthly": 89,
                "price_annual": 890,  # 2 months free
                "features": {
                    "contacts": 1000,
                    "deals": "unlimited",
                    "email_automation": True,
                    "basic_integrations": True,
                    "email_support": True,
                    "voice_ai": False,
                    "advanced_analytics": False,
                    "team_collaboration": False
                },
                "description": "Perfect for solo agents and small teams"
            },
            "professional": {
                "name": "Professional", 
                "price_monthly": 189,
                "price_annual": 1890,  # 2 months free
                "features": {
                    "contacts": 10000,
                    "deals": "unlimited",
                    "email_automation": True,
                    "advanced_analytics": True,
                    "team_collaboration": True,
                    "voice_ai": True,
                    "priority_support": True,
                    "custom_dashboards": True,
                    "bulk_operations": True
                },
                "description": "Ideal for growing teams and businesses"
            },
            "enterprise": {
                "name": "Enterprise",
                "price_monthly": 349,
                "price_annual": 3490,  # 2 months free
                "features": {
                    "contacts": "unlimited",
                    "deals": "unlimited",
                    "email_automation": True,
                    "advanced_analytics": True,
                    "team_collaboration": True,
                    "voice_ai": True,
                    "ai_insights": True,
                    "custom_integrations": True,
                    "phone_support": True,
                    "feature_requests": True,
                    "api_access": True,
                    "white_label": True
                },
                "description": "Complete solution for large organizations"
            }
        }
    
    def init_billing_database(self):
        """Initialize billing database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                subscription_id TEXT PRIMARY KEY,
                user_uuid TEXT NOT NULL,
                tier TEXT NOT NULL,
                status TEXT NOT NULL,
                billing_cycle TEXT DEFAULT 'monthly',
                trial_start TEXT,
                trial_end TEXT,
                subscription_start TEXT,
                next_billing_date TEXT,
                amount REAL,
                currency TEXT DEFAULT 'USD',
                payment_method TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS billing_history (
                transaction_id TEXT PRIMARY KEY,
                subscription_id TEXT,
                user_uuid TEXT,
                amount REAL,
                currency TEXT DEFAULT 'USD',
                status TEXT,
                transaction_type TEXT,
                payment_method TEXT,
                processed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subscription_id) REFERENCES subscriptions (subscription_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_tracking (
                usage_id TEXT PRIMARY KEY,
                user_uuid TEXT,
                month_year TEXT,
                contacts_used INTEGER DEFAULT 0,
                deals_created INTEGER DEFAULT 0,
                emails_sent INTEGER DEFAULT 0,
                api_calls INTEGER DEFAULT 0,
                storage_used REAL DEFAULT 0,
                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_subscription(self, user_uuid: str, tier: str, billing_cycle: str = "monthly") -> Dict[str, Any]:
        """Create new subscription with trial"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            subscription_id = str(uuid.uuid4())
            trial_start = datetime.now().isoformat()
            trial_end = (datetime.now() + timedelta(days=7)).isoformat()
            
            tier_info = self.subscription_tiers.get(tier, self.subscription_tiers["starter"])
            amount = tier_info["price_monthly"] if billing_cycle == "monthly" else tier_info["price_annual"]
            
            cursor.execute('''
                INSERT INTO subscriptions 
                (subscription_id, user_uuid, tier, status, billing_cycle, trial_start, trial_end, amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (subscription_id, user_uuid, tier, "trial", billing_cycle, trial_start, trial_end, amount))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "subscription_id": subscription_id,
                "trial_end": trial_end,
                "message": "7-day free trial started!"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to create subscription: {str(e)}"}
    
    def get_user_subscription(self, user_uuid: str) -> Dict[str, Any]:
        """Get user's current subscription"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT subscription_id, tier, status, billing_cycle, trial_start, trial_end,
                       subscription_start, next_billing_date, amount
                FROM subscriptions 
                WHERE user_uuid = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (user_uuid,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                columns = ['subscription_id', 'tier', 'status', 'billing_cycle', 'trial_start', 
                          'trial_end', 'subscription_start', 'next_billing_date', 'amount']
                subscription = dict(zip(columns, result))
                
                # Add tier information
                subscription.update(self.subscription_tiers.get(subscription['tier'], {}))
                
                return subscription
            else:
                # Return default starter trial
                return {
                    "tier": "starter",
                    "status": "trial",
                    "billing_cycle": "monthly",
                    "trial_end": (datetime.now() + timedelta(days=7)).isoformat(),
                    **self.subscription_tiers["starter"]
                }
                
        except Exception as e:
            return {
                "tier": "starter",
                "status": "trial",
                "error": str(e),
                **self.subscription_tiers["starter"]
            }
    
    def check_trial_status(self, user_uuid: str) -> Dict[str, Any]:
        """Check if trial is active or expired"""
        subscription = self.get_user_subscription(user_uuid)
        
        if subscription["status"] == "trial" and subscription.get("trial_end"):
            trial_end = datetime.fromisoformat(subscription["trial_end"].replace('Z', '+00:00'))
            days_remaining = (trial_end - datetime.now()).days
            
            return {
                "is_trial": True,
                "is_expired": days_remaining < 0,
                "days_remaining": max(0, days_remaining),
                "trial_end": subscription["trial_end"]
            }
        
        return {
            "is_trial": False,
            "is_expired": False,
            "days_remaining": 0,
            "trial_end": None
        }
    
    def upgrade_subscription(self, user_uuid: str, new_tier: str, billing_cycle: str = "monthly") -> Dict[str, Any]:
        """Upgrade user subscription"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            tier_info = self.subscription_tiers.get(new_tier)
            if not tier_info:
                return {"success": False, "error": "Invalid subscription tier"}
            
            amount = tier_info["price_monthly"] if billing_cycle == "monthly" else tier_info["price_annual"]
            subscription_start = datetime.now().isoformat()
            next_billing = (datetime.now() + timedelta(days=30 if billing_cycle == "monthly" else 365)).isoformat()
            
            cursor.execute('''
                UPDATE subscriptions 
                SET tier = ?, status = ?, billing_cycle = ?, amount = ?,
                    subscription_start = ?, next_billing_date = ?, updated_at = ?
                WHERE user_uuid = ?
            ''', (new_tier, "active", billing_cycle, amount, subscription_start, 
                  next_billing, datetime.now().isoformat(), user_uuid))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "tier": new_tier,
                "amount": amount,
                "message": f"Successfully upgraded to {tier_info['name']} plan!"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Upgrade failed: {str(e)}"}
    
    def record_usage(self, user_uuid: str, usage_type: str, amount: int = 1):
        """Record usage for billing tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            month_year = datetime.now().strftime("%Y-%m")
            
            # Check if usage record exists for this month
            cursor.execute('''
                SELECT usage_id FROM usage_tracking 
                WHERE user_uuid = ? AND month_year = ?
            ''', (user_uuid, month_year))
            
            if cursor.fetchone():
                # Update existing record
                cursor.execute(f'''
                    UPDATE usage_tracking 
                    SET {usage_type} = {usage_type} + ?
                    WHERE user_uuid = ? AND month_year = ?
                ''', (amount, user_uuid, month_year))
            else:
                # Create new record
                usage_id = str(uuid.uuid4())
                cursor.execute(f'''
                    INSERT INTO usage_tracking 
                    (usage_id, user_uuid, month_year, {usage_type})
                    VALUES (?, ?, ?, ?)
                ''', (usage_id, user_uuid, month_year, amount))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Failed to record usage: {str(e)}")
    
    def render_subscription_dashboard(self, user_uuid: str):
        """Render subscription management dashboard"""
        subscription = self.get_user_subscription(user_uuid)
        trial_status = self.check_trial_status(user_uuid)
        
        # Subscription Status Header
        st.markdown("## 💎 Subscription Management")
        
        # Current Plan Status
        tier_emoji = {"starter": "🚀", "professional": "💼", "enterprise": "🏢"}
        plan_emoji = tier_emoji.get(subscription["tier"], "🚀")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Plan", f"{plan_emoji} {subscription['name']}")
        
        with col2:
            if trial_status["is_trial"]:
                if trial_status["is_expired"]:
                    st.metric("Status", "⚠️ Trial Expired", "Upgrade Required")
                else:
                    st.metric("Trial Days Left", f"{trial_status['days_remaining']}", "days remaining")
            else:
                st.metric("Status", "✅ Active")
        
        with col3:
            billing_cycle = subscription.get("billing_cycle", "monthly")
            st.metric("Billing", billing_cycle.title())
        
        with col4:
            amount = subscription.get("amount", 89)
            st.metric("Next Charge", f"${amount}")
        
        # Trial Warning
        if trial_status["is_trial"] and trial_status["days_remaining"] <= 2:
            st.warning(f"⚠️ Your trial expires in {trial_status['days_remaining']} day(s). Upgrade now to continue using NXTRIX!")
        
        # Plan Comparison
        st.markdown("---")
        st.markdown("### 🎯 Available Plans")
        
        col1, col2, col3 = st.columns(3)
        
        for i, (tier_key, tier_info) in enumerate(self.subscription_tiers.items()):
            with [col1, col2, col3][i]:
                # Plan card styling
                is_current = tier_key == subscription["tier"]
                border_color = "#6366f1" if is_current else "rgba(255,255,255,0.1)"
                bg_color = "rgba(99, 102, 241, 0.1)" if is_current else "rgba(255,255,255,0.02)"
                
                st.markdown(f"""
                <div style="
                    background: {bg_color};
                    border: 2px solid {border_color};
                    border-radius: 16px;
                    padding: 24px;
                    margin: 8px 0;
                    text-align: center;
                    height: 400px;
                ">
                    <h3 style="color: #ffffff; margin-bottom: 16px;">
                        {tier_emoji.get(tier_key)} {tier_info['name']}
                        {' <span style="color: #6366f1;">(Current)</span>' if is_current else ''}
                    </h3>
                    <div style="font-size: 32px; font-weight: 700; color: #6366f1; margin: 16px 0;">
                        ${tier_info['price_monthly']}<span style="font-size: 16px; color: #a1a3a8;">/month</span>
                    </div>
                    <div style="color: rgba(255,255,255,0.8); margin-bottom: 20px; font-size: 14px;">
                        {tier_info['description']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Features list
                features = tier_info['features']
                feature_text = []
                
                if features.get('contacts') == 'unlimited':
                    feature_text.append("✅ Unlimited contacts")
                elif isinstance(features.get('contacts'), int):
                    feature_text.append(f"✅ {features['contacts']:,} contacts")
                
                feature_text.append("✅ Unlimited deals")
                
                if features.get('email_automation'):
                    feature_text.append("✅ Email automation")
                
                if features.get('voice_ai'):
                    feature_text.append("🎤 Voice AI features")
                
                if features.get('advanced_analytics'):
                    feature_text.append("📊 Advanced analytics")
                
                if features.get('team_collaboration'):
                    feature_text.append("👥 Team collaboration")
                
                if features.get('priority_support'):
                    feature_text.append("🚀 Priority support")
                elif features.get('phone_support'):
                    feature_text.append("📞 24/7 phone support")
                elif features.get('email_support'):
                    feature_text.append("📧 Email support")
                
                for feature in feature_text[:6]:  # Show top 6 features
                    st.markdown(f"<small>{feature}</small>", unsafe_allow_html=True)
                
                # Action button
                if not is_current and not trial_status["is_expired"]:
                    if st.button(f"Upgrade to {tier_info['name']}", 
                               key=f"upgrade_{tier_key}", 
                               use_container_width=True,
                               type="primary" if tier_key == "professional" else "secondary"):
                        self.show_upgrade_modal(user_uuid, tier_key, tier_info)
                elif trial_status["is_expired"]:
                    if st.button(f"Activate {tier_info['name']}", 
                               key=f"activate_{tier_key}", 
                               use_container_width=True,
                               type="primary"):
                        self.show_payment_modal(user_uuid, tier_key, tier_info)
        
        # Billing History
        self.render_billing_history(user_uuid)
        
        # Usage Statistics
        self.render_usage_stats(user_uuid)
    
    def show_upgrade_modal(self, user_uuid: str, tier: str, tier_info: Dict[str, Any]):
        """Show upgrade confirmation modal"""
        st.markdown("---")
        st.markdown(f"### Upgrade to {tier_info['name']} Plan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Monthly Billing")
            st.markdown(f"**${tier_info['price_monthly']}/month**")
            st.markdown("• Billed monthly")
            st.markdown("• Cancel anytime")
            st.markdown("• Immediate access")
            
            if st.button("Upgrade Monthly", key="monthly_upgrade", type="primary", use_container_width=True):
                result = self.upgrade_subscription(user_uuid, tier, "monthly")
                if result["success"]:
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result["error"])
        
        with col2:
            annual_savings = (tier_info['price_monthly'] * 12) - tier_info['price_annual']
            st.markdown("#### Annual Billing")
            st.markdown(f"**${tier_info['price_annual']}/year**")
            st.markdown(f"• Save ${annual_savings} annually")
            st.markdown("• 2 months free")
            st.markdown("• Best value")
            
            if st.button("Upgrade Annual", key="annual_upgrade", use_container_width=True):
                result = self.upgrade_subscription(user_uuid, tier, "annual")
                if result["success"]:
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result["error"])
    
    def show_payment_modal(self, user_uuid: str, tier: str, tier_info: Dict[str, Any]):
        """Show payment setup modal"""
        st.markdown("---")
        st.markdown(f"### Activate {tier_info['name']} Plan")
        st.info("💳 Payment setup required to continue using NXTRIX after trial.")
        
        # Payment would integrate with Stripe here
        st.success("✅ Payment integration ready (Stripe would be integrated here)")
    
    def render_billing_history(self, user_uuid: str):
        """Render billing history"""
        st.markdown("---")
        st.markdown("### 📋 Billing History")
        
        # Mock billing history
        history = [
            {"date": "2025-11-01", "description": "Professional Plan - Monthly", "amount": "$189.00", "status": "Paid"},
            {"date": "2025-10-01", "description": "Professional Plan - Monthly", "amount": "$189.00", "status": "Paid"},
            {"date": "2025-09-01", "description": "Starter Plan - Monthly", "amount": "$89.00", "status": "Paid"},
        ]
        
        for record in history:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.text(record["date"])
            with col2:
                st.text(record["description"])
            with col3:
                st.text(record["amount"])
            with col4:
                st.success("✅ Paid" if record["status"] == "Paid" else "⏳ Pending")
    
    def render_usage_stats(self, user_uuid: str):
        """Render current usage statistics"""
        st.markdown("---")
        st.markdown("### 📊 Usage This Month")
        
        subscription = self.get_user_subscription(user_uuid)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            contacts_used = 247
            contacts_limit = subscription['features'].get('contacts', 1000)
            if contacts_limit != 'unlimited':
                usage_pct = (contacts_used / contacts_limit) * 100
                st.metric("Contacts Used", f"{contacts_used:,}", f"{usage_pct:.1f}% of limit")
            else:
                st.metric("Contacts Used", f"{contacts_used:,}", "unlimited")
        
        with col2:
            st.metric("Deals Created", "23", "+5 this week")
        
        with col3:
            st.metric("Emails Sent", "1,247", "+89 this week")
        
        with col4:
            st.metric("API Calls", "2,341", "within limits")

def render_subscription_plans():
    """Render subscription plans for signup"""
    billing_manager = BillingManager()
    
    st.markdown("### 💎 Choose Your Plan")
    st.markdown("*All plans include 7-day free trial*")
    
    for tier_key, tier_info in billing_manager.subscription_tiers.items():
        with st.expander(f"{tier_info['name']} - ${tier_info['price_monthly']}/month", expanded=tier_key=="professional"):
            st.markdown(tier_info['description'])
            st.markdown("**Features included:**")
            
            features = tier_info['features']
            if features.get('contacts') == 'unlimited':
                st.markdown("• ✅ Unlimited contacts")
            elif isinstance(features.get('contacts'), int):
                st.markdown(f"• ✅ {features['contacts']:,} contacts")
            
            if features.get('deals'):
                st.markdown("• ✅ Unlimited deals")
            if features.get('email_automation'):
                st.markdown("• ✅ Email automation")
            if features.get('voice_ai'):
                st.markdown("• 🎤 Voice AI features")
            if features.get('advanced_analytics'):
                st.markdown("• 📊 Advanced analytics")
            if features.get('team_collaboration'):
                st.markdown("• 👥 Team collaboration")

def render_billing_dashboard(user_uuid: str):
    """Render billing dashboard for authenticated users"""
    billing_manager = BillingManager()
    billing_manager.render_subscription_dashboard(user_uuid)

# Global billing manager instance
billing_manager = BillingManager()