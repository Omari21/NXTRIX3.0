"""
NXTRIX CRM - Launch Configuration
Separates Founder pricing from main CRM for clean public launch
"""

# =============================================================================
# LAUNCH CONFIGURATION
# =============================================================================

# Main CRM Configuration (Public Launch Ready)
PRODUCTION_MODE = True
SHOW_FOUNDER_PRICING_IN_CRM = False  # Keep False for public launch

# Founder Landing Page Configuration (Separate System)
FOUNDER_LANDING_ACTIVE = True  # Set to False to disable Founder signup
FOUNDER_PRICING_DEADLINE = "2025-12-31"  # When Founder pricing expires

# =============================================================================
# PRICING STRATEGY
# =============================================================================

class PricingConfig:
    """Centralized pricing configuration"""
    
    @staticmethod
    def get_main_crm_pricing():
        """Get pricing for main CRM (Public pricing only)"""
        return {
            "solo": {
                "monthly": {"price": 79, "features": "50 deals, 100 AI analyses, 1 user"},
                "annual": {"price": 790, "features": "Save $158/year"}
            },
            "team": {
                "monthly": {"price": 119, "features": "200 deals, 500 AI analyses, 5 users"},
                "annual": {"price": 1190, "features": "Save $238/year"}
            },
            "business": {
                "monthly": {"price": 219, "features": "Unlimited deals, AI & users"},
                "annual": {"price": 2190, "features": "Save $438/year"}
            }
        }
    
    @staticmethod
    def get_founder_pricing():
        """Get Founder pricing (Separate landing page only)"""
        return {
            "solo": {
                "monthly": {"price": 59, "original": 79, "savings": "25% OFF"},
                "annual": {"price": 590, "original": 790, "savings": "Save $200"}
            },
            "team": {
                "monthly": {"price": 89, "original": 119, "savings": "25% OFF"},
                "annual": {"price": 890, "original": 1190, "savings": "Save $300"}
            },
            "business": {
                "monthly": {"price": 149, "original": 219, "savings": "32% OFF"},
                "annual": {"price": 1490, "original": 2190, "savings": "Save $700"}
            }
        }

# =============================================================================
# FEATURE FLAGS
# =============================================================================

class FeatureFlags:
    """Control what features are visible where"""
    
    # Main CRM Features (Always Available)
    CRM_CORE_FEATURES = True
    CRM_PUBLIC_PRICING = True
    CRM_TRIAL_SIGNUP = True
    
    # Founder Features (Separate System)  
    FOUNDER_LANDING_PAGE = FOUNDER_LANDING_ACTIVE
    FOUNDER_PRICING_CHECKOUT = FOUNDER_LANDING_ACTIVE
    FOUNDER_VIP_FEATURES = FOUNDER_LANDING_ACTIVE
    
    # Admin Features
    ADMIN_FOUNDER_MANAGEMENT = True  # Manage existing Founder customers
    ADMIN_PRICING_TOGGLE = True      # Switch between pricing modes

# =============================================================================
# CUSTOMER MANAGEMENT
# =============================================================================

class CustomerSegmentation:
    """Handle different customer types"""
    
    @staticmethod
    def is_founder_customer(user_email):
        """Check if user signed up during Founder period"""
        # This would check database for Founder signup date
        # For now, check if they have Founder pricing in Stripe
        return False  # Implement database check
    
    @staticmethod
    def get_customer_pricing_tier(user_email):
        """Get what pricing tier customer should see"""
        if CustomerSegmentation.is_founder_customer(user_email):
            return "founder"
        else:
            return "public"

# =============================================================================
# LAUNCH STRATEGY SUMMARY
# =============================================================================

"""
RECOMMENDED IMPLEMENTATION:

1. MAIN CRM (streamlit_app.py):
   - Only shows PUBLIC pricing ($79/$119/$219)
   - Clean, professional, ready for mass market
   - No mention of Founder pricing
   - Uses stripe_system (public pricing)

2. FOUNDER LANDING PAGE (separate):
   - Dedicated founder signup page
   - Shows Founder pricing ($59/$89/$149) 
   - Limited time offer messaging
   - Uses stripe_founder_system (founder pricing)
   - You can disable this entirely when going public

3. EXISTING FOUNDER CUSTOMERS:
   - Keep their Stripe subscriptions at Founder rates
   - Full access to main CRM with all features
   - Their billing continues at locked-in prices
   - No difference in functionality

4. TRANSITION TO PUBLIC:
   - Set FOUNDER_LANDING_ACTIVE = False
   - Main CRM already shows public pricing
   - Founder customers keep their rates forever
   - Clean separation achieved

This approach gives you:
✅ Clean public launch
✅ Honor Founder commitments  
✅ Easy transition control
✅ Professional presentation
"""