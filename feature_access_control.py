"""
Feature Access Control Layer for NxTrix CRM
Enforces subscription tier restrictions across all modules
"""

import streamlit as st
try:
    from subscription_manager import (
        SubscriptionManager, 
        require_subscription, 
        track_usage,
        get_user_tier,
        is_feature_available,
        SubscriptionTier
    )
except ImportError:
    # Fallback for missing subscription manager
    class SubscriptionManager:
        def __init__(self):
            pass
        def get_user_tier(self, user_id):
            return "free"
        def is_feature_available(self, feature, user_id):
            return True
    
    def require_subscription(tier):
        def decorator(func):
            return func
        return decorator
    
    def track_usage(feature):
        def decorator(func):
            return func
        return decorator
    
    def get_user_tier(user_id):
        return "free"
    
    def is_feature_available(feature, user_id):
        return True
    
    class SubscriptionTier:
        FREE = "free"
        PRO = "pro" 
        ENTERPRISE = "enterprise"

import functools
from typing import Any, Callable, Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureAccessControl:
    """Central feature access control manager"""
    
    def __init__(self):
        self.sub_manager = SubscriptionManager()
        self.restricted_features = self._define_restricted_features()
        
    def _define_restricted_features(self) -> Dict[str, Dict[str, Any]]:
        """Define feature restrictions by subscription tier"""
        return {
            # Basic CRM features
            "deal_tracker": {
                "tiers": ["free", "pro", "enterprise"],
                "usage_limit": "deals_per_month",
                "description": "Basic deal tracking and management"
            },
            "investor_management": {
                "tiers": ["free", "pro", "enterprise"],
                "usage_limit": "investors_per_month",
                "description": "Investor profile management"
            },
            "contact_management": {
                "tiers": ["free", "pro", "enterprise"],
                "usage_limit": None,
                "description": "Contact and relationship management"
            },
            
            # Analytics features
            "basic_analytics": {
                "tiers": ["free", "pro", "enterprise"],
                "usage_limit": None,
                "description": "Basic reporting and analytics"
            },
            "advanced_analytics": {
                "tiers": ["pro", "enterprise"],
                "usage_limit": None,
                "description": "Advanced analytics and insights"
            },
            "deal_analytics": {
                "tiers": ["pro", "enterprise"],
                "usage_limit": None,
                "description": "Deal performance analytics"
            },
            "advanced_deal_analytics": {
                "tiers": ["enterprise"],
                "usage_limit": None,
                "description": "Enterprise-level deal analytics"
            },
            "market_intelligence": {
                "tiers": ["enterprise"],
                "usage_limit": None,
                "description": "Market data and intelligence"
            },
            
            # AI Enhancement features
            "ai_deal_analysis": {
                "tiers": ["pro", "enterprise"],
                "usage_limit": "ai_queries_per_month",
                "description": "AI-powered deal analysis"
            },
            "ai_scoring": {
                "tiers": ["pro", "enterprise"],
                "usage_limit": "ai_queries_per_month",
                "description": "Automated deal scoring"
            },
            "ai_recommendations": {
                "tiers": ["enterprise"],
                "usage_limit": "ai_queries_per_month",
                "description": "AI investment recommendations"
            },
            "natural_language_search": {
                "tiers": ["pro", "enterprise"],
                "usage_limit": "ai_queries_per_month",
                "description": "Natural language search capabilities"
            },
            
            # Automation features
            "basic_automation": {
                "tiers": ["pro", "enterprise"],
                "usage_limit": "automation_rules",
                "description": "Basic workflow automation"
            },
            "advanced_automation": {
                "tiers": ["enterprise"],
                "usage_limit": "automation_rules",
                "description": "Advanced automation workflows"
            },
            "email_campaigns": {
                "tiers": ["pro", "enterprise"],
                "usage_limit": "email_campaigns_per_month",
                "description": "Email marketing campaigns"
            },
            "advanced_email_marketing": {
                "tiers": ["enterprise"],
                "usage_limit": "email_campaigns_per_month",
                "description": "Advanced email marketing features"
            },
            
            # Document features
            "basic_document_generation": {
                "tiers": ["free", "pro", "enterprise"],
                "usage_limit": "document_generations_per_month",
                "description": "Basic document generation"
            },
            "document_generation": {
                "tiers": ["pro", "enterprise"],
                "usage_limit": "document_generations_per_month",
                "description": "Advanced document generation"
            },
            "advanced_document_templates": {
                "tiers": ["enterprise"],
                "usage_limit": "document_generations_per_month",
                "description": "Custom document templates"
            },
            
            # Reporting features
            "basic_reports": {
                "tiers": ["free", "pro", "enterprise"],
                "usage_limit": None,
                "description": "Basic reporting capabilities"
            },
            "advanced_reports": {
                "tiers": ["pro", "enterprise"],
                "usage_limit": None,
                "description": "Advanced reporting and insights"
            },
            "custom_reports": {
                "tiers": ["enterprise"],
                "usage_limit": None,
                "description": "Custom report builder"
            },
            
            # Portal features
            "investor_portal": {
                "tiers": ["pro", "enterprise"],
                "usage_limit": None,
                "description": "Investor self-service portal"
            },
            "deal_pipeline": {
                "tiers": ["pro", "enterprise"],
                "usage_limit": None,
                "description": "Deal pipeline management"
            },
            "deal_sourcing": {
                "tiers": ["enterprise"],
                "usage_limit": None,
                "description": "Automated deal sourcing"
            },
            
            # Enterprise features
            "api_access": {
                "tiers": ["enterprise"],
                "usage_limit": "api_calls_per_month",
                "description": "API access and integrations"
            },
            "admin_dashboard": {
                "tiers": ["enterprise"],
                "usage_limit": None,
                "description": "Administrative dashboard"
            },
            "team_management": {
                "tiers": ["enterprise"],
                "usage_limit": "team_members",
                "description": "Team and user management"
            },
            "role_permissions": {
                "tiers": ["enterprise"],
                "usage_limit": None,
                "description": "Role-based permissions"
            },
            "data_export": {
                "tiers": ["enterprise"],
                "usage_limit": None,
                "description": "Data export capabilities"
            },
            "integration_hub": {
                "tiers": ["enterprise"],
                "usage_limit": None,
                "description": "Third-party integrations"
            }
        }

    def check_feature_access(self, feature_name: str, user_id: str = None) -> bool:
        """Check if current user has access to a feature"""
        if not user_id:
            user_id = st.session_state.get('user_id')
            
        if not user_id:
            return False
            
        # Get user's current tier
        subscription = self.sub_manager.get_user_subscription(user_id)
        if not subscription:
            return False
            
        # Check if feature exists in our restrictions
        if feature_name not in self.restricted_features:
            return True  # Feature not restricted
            
        feature_config = self.restricted_features[feature_name]
        user_tier = subscription.tier.value
        
        # Check if user's tier has access to this feature
        return user_tier in feature_config["tiers"]

    def check_usage_limit(self, feature_name: str, user_id: str = None) -> tuple[bool, int, int]:
        """Check usage limits for a feature"""
        if not user_id:
            user_id = st.session_state.get('user_id')
            
        if not user_id:
            return False, 0, 0
            
        feature_config = self.restricted_features.get(feature_name, {})
        usage_type = feature_config.get("usage_limit")
        
        if not usage_type:
            return True, 0, -1  # No usage limit
            
        return self.sub_manager.check_usage_limit(user_id, usage_type)

    def show_upgrade_prompt(self, feature_name: str, required_tier: str = "pro"):
        """Show upgrade prompt for restricted features"""
        feature_config = self.restricted_features.get(feature_name, {})
        description = feature_config.get("description", feature_name)
        
        st.warning(f"🔒 **{description}** requires a {required_tier.title()} subscription")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Upgrade Now", key=f"upgrade_{feature_name}"):
                self.show_pricing_modal()
                
        with col2:
            if st.button("📞 Contact Sales", key=f"contact_{feature_name}"):
                self.show_contact_modal()
                
        with col3:
            if st.button("ℹ️ Learn More", key=f"learn_{feature_name}"):
                self.show_feature_details(feature_name)

    def show_pricing_modal(self):
        """Show pricing comparison modal"""
        st.session_state.show_pricing = True
        
    def show_contact_modal(self):
        """Show contact sales modal"""
        st.session_state.show_contact = True
        
    def show_feature_details(self, feature_name: str):
        """Show feature details modal"""
        st.session_state.feature_details = feature_name

    def get_feature_matrix(self) -> Dict[str, Any]:
        """Get complete feature matrix for pricing page"""
        tiers = {
            "free": {"name": "Free", "price": 0, "features": []},
            "pro": {"name": "Professional", "price": 97, "features": []},
            "enterprise": {"name": "Enterprise", "price": 297, "features": []}
        }
        
        for feature_name, config in self.restricted_features.items():
            for tier in config["tiers"]:
                tiers[tier]["features"].append({
                    "name": feature_name,
                    "description": config["description"],
                    "usage_limit": config.get("usage_limit")
                })
                
        return tiers

# Decorators for easy feature gating
def require_tier(tier: str):
    """Decorator to require specific subscription tier"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_id' not in st.session_state:
                st.error("Please log in to access this feature")
                st.stop()
                
            user_tier = get_user_tier(st.session_state.user_id)
            
            tier_hierarchy = {"free": 0, "pro": 1, "enterprise": 2}
            
            if tier_hierarchy.get(user_tier.value, 0) < tier_hierarchy.get(tier, 0):
                access_control = FeatureAccessControl()
                access_control.show_upgrade_prompt("advanced_feature", tier)
                st.stop()
                
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_feature(feature_name: str):
    """Decorator to require specific feature access"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_id' not in st.session_state:
                st.error("Please log in to access this feature")
                st.stop()
                
            access_control = FeatureAccessControl()
            
            if not access_control.check_feature_access(feature_name):
                # Determine required tier
                feature_config = access_control.restricted_features.get(feature_name, {})
                tiers = feature_config.get("tiers", ["enterprise"])
                required_tier = min(tiers, key=lambda x: {"free": 0, "pro": 1, "enterprise": 2}[x])
                
                access_control.show_upgrade_prompt(feature_name, required_tier)
                st.stop()
                
            return func(*args, **kwargs)
        return wrapper
    return decorator

def track_feature_usage(usage_type: str):
    """Decorator to track feature usage and enforce limits"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_id' not in st.session_state:
                return func(*args, **kwargs)
                
            access_control = FeatureAccessControl()
            user_id = st.session_state.user_id
            
            # Check usage limits
            has_access, current, limit = access_control.check_usage_limit("", user_id)
            
            if not has_access:
                st.error(f"Usage limit reached: {current}/{limit} for this billing cycle")
                access_control.show_upgrade_prompt("usage_limit")
                st.stop()
                
            # Execute function
            result = func(*args, **kwargs)
            
            # Track usage
            access_control.sub_manager.increment_usage(user_id, usage_type)
            
            return result
        return wrapper
    return decorator

# Usage monitoring functions
def show_usage_dashboard(user_id: str):
    """Show usage dashboard for current user"""
    access_control = FeatureAccessControl()
    subscription = access_control.sub_manager.get_user_subscription(user_id)
    
    if not subscription:
        st.error("Unable to load subscription information")
        return
        
    st.subheader(f"📊 Usage Dashboard - {subscription.tier.value.title()} Plan")
    
    # Show billing cycle info
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Billing Cycle Start", subscription.billing_cycle_start.strftime("%Y-%m-%d"))
    with col2:
        st.metric("Billing Cycle End", subscription.billing_cycle_end.strftime("%Y-%m-%d"))
    
    # Show usage for each metric
    usage_metrics = [
        ("deals_per_month", "Deals Created", "📈"),
        ("investors_per_month", "Investors Added", "👥"),
        ("ai_queries_per_month", "AI Queries", "🤖"),
        ("email_campaigns_per_month", "Email Campaigns", "📧"),
        ("document_generations_per_month", "Documents Generated", "📄")
    ]
    
    for usage_type, label, icon in usage_metrics:
        limit = getattr(subscription.limits, usage_type)
        current = subscription.current_usage.get(usage_type, 0)
        
        if limit > 0:  # Skip unlimited features
            usage_pct = (current / limit * 100) if limit > 0 else 0
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                st.metric(f"{icon} {label}", f"{current:,}")
            with col2:
                st.progress(usage_pct / 100)
            with col3:
                st.metric("Limit", f"{limit:,}" if limit != -1 else "Unlimited")
                
            # Show warning if approaching limit
            if usage_pct > 80:
                st.warning(f"⚠️ Approaching {label.lower()} limit")

def show_feature_comparison():
    """Show feature comparison table"""
    access_control = FeatureAccessControl()
    feature_matrix = access_control.get_feature_matrix()
    
    st.subheader("📋 Feature Comparison")
    
    # Create comparison table
    features_data = []
    all_features = set()
    
    # Collect all features
    for tier_data in feature_matrix.values():
        for feature in tier_data["features"]:
            all_features.add(feature["name"])
    
    # Build comparison matrix
    for feature_name in sorted(all_features):
        row = {"Feature": feature_name.replace("_", " ").title()}
        
        for tier in ["free", "pro", "enterprise"]:
            tier_features = [f["name"] for f in feature_matrix[tier]["features"]]
            row[feature_matrix[tier]["name"]] = "✅" if feature_name in tier_features else "❌"
            
        features_data.append(row)
    
    st.table(features_data)

# Module-specific access controls
class DealTrackerAccess:
    """Access control for Deal Tracker module"""
    
    @staticmethod
    @require_feature("deal_tracker")
    @track_feature_usage("deals_per_month")
    def create_deal():
        """Protected deal creation"""
        pass
    
    @staticmethod
    @require_feature("deal_tracker")
    def view_deals():
        """Protected deal viewing"""
        pass

class AIEnhancementAccess:
    """Access control for AI Enhancement features"""
    
    @staticmethod
    @require_feature("ai_deal_analysis")
    @track_feature_usage("ai_queries_per_month")
    def analyze_deal():
        """Protected AI deal analysis"""
        pass
    
    @staticmethod
    @require_feature("ai_scoring")
    @track_feature_usage("ai_queries_per_month")
    def score_deal():
        """Protected AI deal scoring"""
        pass
    
    @staticmethod
    @require_feature("ai_recommendations")
    @track_feature_usage("ai_queries_per_month")
    def get_recommendations():
        """Protected AI recommendations"""
        pass

class AutomationAccess:
    """Access control for Automation features"""
    
    @staticmethod
    @require_feature("basic_automation")
    @track_feature_usage("automation_rules")
    def create_automation():
        """Protected automation creation"""
        pass
    
    @staticmethod
    @require_feature("email_campaigns")
    @track_feature_usage("email_campaigns_per_month")
    def create_campaign():
        """Protected email campaign creation"""
        pass

# Global access control instance
access_control = FeatureAccessControl()