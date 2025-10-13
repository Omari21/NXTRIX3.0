"""
NxTrix CRM Subscription Tier Management System
Comprehensive feature gating and access control for SaaS tiers

Subscription Tiers:
- Free: Basic deal tracking, limited analytics (5 deals/month)
- Pro: Advanced analytics, AI insights, automation (50 deals/month)  
- Enterprise: Full features, unlimited usage, API access
"""

import streamlit as st
import functools
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json

# Optional PostgreSQL import with error handling - DISABLED for Supabase API
try:
    # Temporarily disable PostgreSQL imports to prevent connection attempts
    # import psycopg2
    # from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = False
    print("🟡 PostgreSQL connections disabled - using Supabase API instead")
except ImportError:
    PSYCOPG2_AVAILABLE = False
    # Create placeholder for psycopg2 when not available
    class RealDictCursor:
        pass

class SubscriptionTier(Enum):
    FREE = "free"
    SOLO = "solo"
    TEAM = "team" 
    BUSINESS = "business"

class FeatureCategory(Enum):
    CORE = "core"
    ANALYTICS = "analytics"
    AI_ENHANCED = "ai_enhanced"
    AUTOMATION = "automation"
    INTEGRATIONS = "integrations"
    ADMIN = "admin"

@dataclass
class FeatureLimits:
    """Defines usage limits for each subscription tier"""
    deals_per_month: int
    investors_per_month: int
    ai_queries_per_month: int
    automation_rules: int
    email_campaigns_per_month: int
    document_generations_per_month: int
    api_calls_per_month: int
    storage_gb: float
    team_members: int

@dataclass
class SubscriptionInfo:
    """User subscription information"""
    user_id: str
    tier: SubscriptionTier
    status: str  # 'active', 'trialing', 'past_due', 'canceled', 'unpaid'
    trial_end: Optional[datetime]
    billing_cycle_start: datetime
    billing_cycle_end: datetime
    features_enabled: List[str]
    current_usage: Dict[str, int]
    limits: FeatureLimits

class SubscriptionManager:
    """Central subscription management and feature gating"""
    
    def __init__(self):
        self.conn = self._get_db_connection()
        self.tier_limits = self._define_tier_limits()
        self.feature_matrix = self._define_feature_matrix()
        
    def _get_db_connection(self):
        """Get database connection using Supabase credentials"""
        if not PSYCOPG2_AVAILABLE:
            # Silently return None - no user-facing warnings
            return None
            
        try:
            return psycopg2.connect(
                host=st.secrets["supabase"]["host"],
                database=st.secrets["supabase"]["database"],
                user=st.secrets["supabase"]["user"],
                password=st.secrets["supabase"]["password"],
                port=st.secrets["supabase"]["port"]
            )
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return None

    def _define_tier_limits(self) -> Dict[SubscriptionTier, FeatureLimits]:
        """Define usage limits for each subscription tier"""
        return {
            SubscriptionTier.FREE: FeatureLimits(
                deals_per_month=5,
                investors_per_month=10,
                ai_queries_per_month=10,
                automation_rules=0,
                email_campaigns_per_month=0,
                document_generations_per_month=5,
                api_calls_per_month=0,
                storage_gb=1.0,
                team_members=1
            ),
            SubscriptionTier.SOLO: FeatureLimits(
                deals_per_month=50,
                investors_per_month=100,
                ai_queries_per_month=100,
                automation_rules=10,
                email_campaigns_per_month=20,
                document_generations_per_month=50,
                api_calls_per_month=1000,
                storage_gb=10.0,
                team_members=1
            ),
            SubscriptionTier.TEAM: FeatureLimits(
                deals_per_month=200,
                investors_per_month=500,
                ai_queries_per_month=500,
                automation_rules=50,
                email_campaigns_per_month=100,
                document_generations_per_month=200,
                api_calls_per_month=5000,
                storage_gb=50.0,
                team_members=10
            ),
            SubscriptionTier.BUSINESS: FeatureLimits(
                deals_per_month=-1,  # Unlimited
                investors_per_month=-1,
                ai_queries_per_month=-1,
                automation_rules=-1,
                email_campaigns_per_month=-1,
                document_generations_per_month=-1,
                api_calls_per_month=-1,
                storage_gb=-1,
                team_members=-1
            )
        }

    def _define_feature_matrix(self) -> Dict[SubscriptionTier, List[str]]:
        """Define which features are available for each tier"""
        return {
            SubscriptionTier.FREE: [
                # Core Features
                "deal_tracker",
                "basic_investor_management", 
                "basic_analytics",
                "contact_management",
                "basic_document_generation",
                "basic_reports"
            ],
            SubscriptionTier.SOLO: [
                # All Free features plus:
                "deal_tracker",
                "basic_investor_management",
                "advanced_investor_management", 
                "basic_analytics",
                "advanced_analytics",
                "deal_analytics",
                "contact_management",
                "ai_deal_analysis",
                "ai_scoring",
                "natural_language_search",
                "basic_automation",
                "email_campaigns",
                "document_generation",
                "basic_reports",
                "advanced_reports",
                "investor_portal",
                "activity_tracking",
                "deal_pipeline"
            ],
            SubscriptionTier.TEAM: [
                # All Solo features plus:
                "deal_tracker",
                "basic_investor_management",
                "advanced_investor_management",
                "basic_analytics", 
                "advanced_analytics",
                "deal_analytics",
                "advanced_deal_analytics",
                "market_intelligence",
                "contact_management",
                "ai_deal_analysis",
                "ai_scoring",
                "ai_recommendations",
                "natural_language_search",
                "basic_automation",
                "advanced_automation",
                "workflow_automation",
                "email_campaigns",
                "advanced_email_marketing",
                "document_generation",
                "advanced_document_templates",
                "basic_reports",
                "advanced_reports",
                "custom_reports",
                "investor_portal",
                "activity_tracking",
                "deal_pipeline",
                "deal_sourcing",
                "team_management",
                "user_permissions",
                "collaboration_tools"
            ],
            SubscriptionTier.BUSINESS: [
                # All Team features plus:
                "deal_tracker",
                "basic_investor_management",
                "advanced_investor_management",
                "basic_analytics", 
                "advanced_analytics",
                "deal_analytics",
                "advanced_deal_analytics",
                "market_intelligence",
                "contact_management",
                "ai_deal_analysis",
                "ai_scoring",
                "ai_recommendations",
                "natural_language_search",
                "basic_automation",
                "advanced_automation",
                "workflow_automation",
                "email_campaigns",
                "advanced_email_marketing",
                "document_generation",
                "advanced_document_templates",
                "basic_reports",
                "advanced_reports",
                "custom_reports",
                "investor_portal",
                "activity_tracking",
                "deal_pipeline",
                "deal_sourcing",
                "api_access",
                "admin_dashboard",
                "team_management",
                "role_permissions",
                "data_export",
                "integration_hub"
            ]
        }

    def get_user_subscription(self, user_id: str) -> Optional[SubscriptionInfo]:
        """Get current subscription information for user"""
        if not self.conn:
            return None
            
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get user profile with subscription info
                cur.execute("""
                    SELECT 
                        id,
                        subscription_tier,
                        subscription_status,
                        trial_end,
                        billing_cycle_start,
                        billing_cycle_end,
                        subscription_metadata
                    FROM profiles 
                    WHERE id = %s
                """, (user_id,))
                
                user_data = cur.fetchone()
                if not user_data:
                    return None
                
                # Get current usage for billing cycle
                usage = self._get_current_usage(user_id)
                
                tier = SubscriptionTier(user_data['subscription_tier'])
                limits = self.tier_limits[tier]
                features = self.feature_matrix[tier]
                
                return SubscriptionInfo(
                    user_id=user_id,
                    tier=tier,
                    status=user_data.get('subscription_status', 'trialing'),
                    trial_end=user_data.get('trial_end'),
                    billing_cycle_start=user_data.get('billing_cycle_start', datetime.now()),
                    billing_cycle_end=user_data.get('billing_cycle_end', datetime.now() + timedelta(days=30)),
                    features_enabled=features,
                    current_usage=usage,
                    limits=limits
                )
                
        except Exception as e:
            st.error(f"Error getting subscription info: {e}")
            return None

    def _get_current_usage(self, user_id: str) -> Dict[str, int]:
        """Get current usage statistics for billing cycle"""
        if not self.conn:
            return {}
            
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get usage from subscription_usage table
                cur.execute("""
                    SELECT 
                        usage_type,
                        usage_count,
                        billing_cycle_start
                    FROM subscription_usage 
                    WHERE user_id = %s 
                    AND billing_cycle_start <= NOW()
                    AND billing_cycle_end >= NOW()
                """, (user_id,))
                
                usage_records = cur.fetchall()
                usage = {}
                
                for record in usage_records:
                    usage[record['usage_type']] = record['usage_count']
                
                return usage
                
        except Exception as e:
            # If table doesn't exist yet, return empty usage
            return {}

    def check_feature_access(self, user_id: str, feature: str) -> bool:
        """Check if user has access to specific feature"""
        subscription = self.get_user_subscription(user_id)
        if not subscription:
            return False
            
        # Check if subscription is active
        if subscription.status not in ['active', 'trialing']:
            return False
            
        # Check if feature is in tier's feature list
        return feature in subscription.features_enabled

    def check_usage_limit(self, user_id: str, usage_type: str) -> tuple[bool, int, int]:
        """
        Check if user has reached usage limit
        Returns: (has_access, current_usage, limit)
        """
        subscription = self.get_user_subscription(user_id)
        if not subscription:
            return False, 0, 0
            
        current_usage = subscription.current_usage.get(usage_type, 0)
        limit = getattr(subscription.limits, usage_type, 0)
        
        # -1 means unlimited (Enterprise tier)
        if limit == -1:
            return True, current_usage, -1
            
        return current_usage < limit, current_usage, limit

    def increment_usage(self, user_id: str, usage_type: str, amount: int = 1) -> bool:
        """Increment usage counter for billing cycle"""
        if not self.conn:
            return False
            
        try:
            with self.conn.cursor() as cur:
                # Get current billing cycle
                subscription = self.get_user_subscription(user_id)
                if not subscription:
                    return False
                
                # Insert or update usage record
                cur.execute("""
                    INSERT INTO subscription_usage 
                    (user_id, usage_type, usage_count, billing_cycle_start, billing_cycle_end)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, usage_type, billing_cycle_start)
                    DO UPDATE SET 
                        usage_count = subscription_usage.usage_count + %s,
                        updated_at = NOW()
                """, (
                    user_id, usage_type, amount,
                    subscription.billing_cycle_start,
                    subscription.billing_cycle_end,
                    amount
                ))
                
                self.conn.commit()
                return True
                
        except Exception as e:
            st.error(f"Error updating usage: {e}")
            return False

    def upgrade_subscription(self, user_id: str, new_tier: SubscriptionTier) -> bool:
        """Upgrade user subscription tier"""
        if not self.conn:
            return False
            
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    UPDATE profiles 
                    SET 
                        subscription_tier = %s,
                        subscription_status = 'active',
                        updated_at = NOW()
                    WHERE id = %s
                """, (new_tier.value, user_id))
                
                self.conn.commit()
                
                # Log subscription change
                self._log_subscription_event(user_id, 'upgrade', new_tier.value)
                return True
                
        except Exception as e:
            st.error(f"Error upgrading subscription: {e}")
            return False

    def _log_subscription_event(self, user_id: str, event_type: str, details: str):
        """Log subscription events for audit trail"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO subscription_events
                    (user_id, event_type, event_details, created_at)
                    VALUES (%s, %s, %s, NOW())
                """, (user_id, event_type, details))
                self.conn.commit()
        except Exception:
            pass  # Non-critical logging

    def get_tier_comparison(self, show_founder_pricing=False) -> Dict[str, Any]:
        """Get feature comparison matrix for pricing page"""
        # STRATEGIC CHANGE: Founder pricing now separate from main CRM
        # Main CRM only shows public pricing for clean launch
        is_founder_pricing = show_founder_pricing  # Controlled externally
        
        # APPROVED PRICING STRATEGY:
        # Solo: $79/month or $790/year (62% profit margin)
        # Team: $119/month or $1,070/year (79% profit margin)  
        # Business: $219/month or $1,970/year (91% profit margin)
        
        if is_founder_pricing:
            return {
                "tiers": {
                    "free": {
                        "name": "Free",
                        "price": 0,
                        "billing": "Forever",
                        "features": self.feature_matrix[SubscriptionTier.FREE],
                        "limits": self.tier_limits[SubscriptionTier.FREE].__dict__
                    },
                    "solo": {
                        "name": "Solo", 
                        "price": 59,
                        "annual_price": 708,
                        "billing": "per month",
                        "annual_billing": "per year (save $300)",
                        "founder_discount": "40% OFF Launch Price",
                        "regular_price": 79,
                        "features": self.feature_matrix[SubscriptionTier.SOLO],
                        "limits": self.tier_limits[SubscriptionTier.SOLO].__dict__
                    },
                    "team": {
                        "name": "Team",
                        "price": 89,
                        "annual_price": 1068,
                        "billing": "per month",
                        "annual_billing": "per year (save $600)",
                        "founder_discount": "45% OFF Launch Price", 
                        "regular_price": 119,
                        "features": self.feature_matrix[SubscriptionTier.TEAM],
                        "limits": self.tier_limits[SubscriptionTier.TEAM].__dict__
                    },
                    "business": {
                        "name": "Business",
                        "price": 149,
                        "annual_price": 1788,
                        "billing": "per month",
                        "annual_billing": "per year (save $1,000)",
                        "founder_discount": "32% OFF Launch Price",
                        "regular_price": 219,
                        "features": self.feature_matrix[SubscriptionTier.BUSINESS],
                        "limits": self.tier_limits[SubscriptionTier.BUSINESS].__dict__
                    }
                }
            }
        else:
            # Public launch pricing with optimized annual rates
            return {
                "tiers": {
                    "free": {
                        "name": "Free",
                        "price": 0,
                        "billing": "Forever",
                        "features": self.feature_matrix[SubscriptionTier.FREE],
                        "limits": self.tier_limits[SubscriptionTier.FREE].__dict__
                    },
                    "solo": {
                        "name": "Solo", 
                        "price": 79,
                        "annual_price": 790,  # 17% discount - optimal profit margin
                        "annual_savings": 158,
                        "billing": "per month",
                        "annual_billing": "per year (save $158)",
                        "daily_cost": "$2.17/day",
                        "profit_margin": "62%",
                        "features": self.feature_matrix[SubscriptionTier.SOLO],
                        "limits": self.tier_limits[SubscriptionTier.SOLO].__dict__
                    },
                    "team": {
                        "name": "Team",
                        "price": 119,
                        "annual_price": 1070,  # 25% discount - sweet spot pricing
                        "annual_savings": 358,
                        "billing": "per month",
                        "annual_billing": "per year (save $358)",
                        "daily_cost": "$2.93/day per user",
                        "profit_margin": "79%",
                        "features": self.feature_matrix[SubscriptionTier.TEAM],
                        "limits": self.tier_limits[SubscriptionTier.TEAM].__dict__
                    },
                    "business": {
                        "name": "Business",
                        "price": 219,
                        "annual_price": 1970,  # 25% discount - maximum value
                        "annual_savings": 658,
                        "billing": "per month", 
                        "annual_billing": "per year (save $658)",
                        "daily_cost": "$5.40/day for unlimited",
                        "profit_margin": "91%",
                        "features": self.feature_matrix[SubscriptionTier.BUSINESS],
                        "limits": self.tier_limits[SubscriptionTier.BUSINESS].__dict__
                    }
                }
            }

# Decorator for feature gating
def require_subscription(feature: str, usage_type: str = None):
    """Decorator to enforce subscription requirements"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get current user (assumes Streamlit session state)
            if 'user_id' not in st.session_state:
                st.error("Please log in to access this feature")
                st.stop()
                
            user_id = st.session_state.user_id
            sub_manager = SubscriptionManager()
            
            # Check feature access
            if not sub_manager.check_feature_access(user_id, feature):
                st.error(f"This feature requires a higher subscription tier")
                _show_upgrade_prompt(feature)
                st.stop()
            
            # Check usage limits if specified
            if usage_type:
                has_access, current, limit = sub_manager.check_usage_limit(user_id, usage_type)
                if not has_access:
                    st.error(f"Usage limit reached: {current}/{limit} for this billing cycle")
                    _show_upgrade_prompt(feature)
                    st.stop()
                    
                # Increment usage after successful access
                sub_manager.increment_usage(user_id, usage_type)
            
            return func(*args, **kwargs)
            
        return wrapper
    return decorator

def _show_upgrade_prompt(feature: str):
    """Show upgrade prompt for restricted features"""
    st.info("🚀 **Upgrade to unlock this feature!**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("View Pricing Plans"):
            st.session_state.show_pricing = True
            
    with col2:
        if st.button("Start Free Trial"):
            st.session_state.start_trial = True
            
    with col3:
        if st.button("Contact Sales"):
            st.session_state.contact_sales = True

# Usage tracking decorator
def track_usage(usage_type: str):
    """Decorator to automatically track feature usage"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_id' in st.session_state:
                sub_manager = SubscriptionManager()
                sub_manager.increment_usage(st.session_state.user_id, usage_type)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Context manager for bulk operations
class BulkOperationContext:
    """Context manager for bulk operations with usage tracking"""
    
    def __init__(self, user_id: str, usage_type: str, operation_count: int):
        self.user_id = user_id
        self.usage_type = usage_type
        self.operation_count = operation_count
        self.sub_manager = SubscriptionManager()
        
    def __enter__(self):
        # Check if user can perform bulk operation
        has_access, current, limit = self.sub_manager.check_usage_limit(
            self.user_id, self.usage_type
        )
        
        if limit != -1 and (current + self.operation_count) > limit:
            raise Exception(f"Bulk operation would exceed limit: {current + self.operation_count}/{limit}")
            
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:  # Success
            self.sub_manager.increment_usage(
                self.user_id, self.usage_type, self.operation_count
            )

# Utility functions
def get_user_tier(user_id: str) -> SubscriptionTier:
    """Get user's current subscription tier"""
    sub_manager = SubscriptionManager()
    subscription = sub_manager.get_user_subscription(user_id)
    return subscription.tier if subscription else SubscriptionTier.FREE

def is_feature_available(user_id: str, feature: str) -> bool:
    """Check if feature is available for user"""
    sub_manager = SubscriptionManager()
    return sub_manager.check_feature_access(user_id, feature)

def get_usage_stats(user_id: str) -> Dict[str, Any]:
    """Get current usage statistics for user"""
    sub_manager = SubscriptionManager()
    subscription = sub_manager.get_user_subscription(user_id)
    
    if not subscription:
        return {}
        
    return {
        "tier": subscription.tier.value,
        "status": subscription.status,
        "usage": subscription.current_usage,
        "limits": subscription.limits.__dict__,
        "trial_end": subscription.trial_end
    }

def format_limit(limit: int) -> str:
    """Format limit for display (handle unlimited)"""
    return "Unlimited" if limit == -1 else f"{limit:,}"

def calculate_usage_percentage(current: int, limit: int) -> float:
    """Calculate usage percentage"""
    if limit == -1:  # Unlimited
        return 0.0
    return (current / limit * 100) if limit > 0 else 0.0