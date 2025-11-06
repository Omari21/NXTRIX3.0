"""
Stripe Payment Integration for NXTRIX CRM
Handles subscription creation, upgrades, and billing management
"""

import streamlit as st
import os
from datetime import datetime, timedelta
import json

# Safe Stripe import with error handling
try:
    import stripe
    STRIPE_IMPORT_SUCCESS = True
    STRIPE_IMPORT_ERROR = None
except Exception as e:
    STRIPE_IMPORT_SUCCESS = False
    STRIPE_IMPORT_ERROR = str(e)
    # Create a dummy stripe module to prevent further errors
    class DummyStripe:
        api_key = None
        class apps:
            Secret = None
    stripe = DummyStripe()

class StripePaymentSystem:
    """Complete Stripe integration for subscription management"""
    
    def __init__(self, founder_pricing=True):
        """Initialize Stripe with production keys"""
        self.stripe_available = False
        
        # Check if Stripe import was successful
        if not STRIPE_IMPORT_SUCCESS:
            # Silently handle missing Stripe in production
            return
            
        try:
            # Set the API key first
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            
            # Check for the specific Stripe library issue
            try:
                # This will fail if stripe.apps.Secret is None
                if hasattr(stripe.apps, 'Secret') and stripe.apps.Secret is not None:
                    # Test Stripe initialization
                    if stripe.api_key:
                        stripe.Product.list(limit=1)
                        self.stripe_available = True
                    else:
                        if 'stripe_key_warning_shown' not in st.session_state and os.getenv('STREAMLIT_ENV') != 'production':
                            st.info("ℹ️ Payment processing will be available once configured")
                            st.session_state.stripe_key_warning_shown = True
                else:
                    # Silently handle missing Stripe configuration in production
                    stripe.api_key = None
            except AttributeError:
                # Silently handle Stripe initialization issues in production
                stripe.api_key = None
            except Exception as e:
                # Silently handle Stripe connection issues in production
                stripe.api_key = None
                
            self.publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
            self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
            self.founder_pricing = founder_pricing
            
        except Exception as e:
            # Silently handle Stripe initialization errors in production
            stripe.api_key = None
            self.stripe_available = False
        
        # Pricing configuration - switches between Founder and Regular pricing
        if founder_pricing:
            # Founder VIP Pricing (Current Launch)
            self.PRICING_CONFIG = {
                'solo': {
                    'monthly': {'price_id': os.getenv('STRIPE_SOLO_MONTHLY_PRICE_ID'), 'amount': 5900},  # $59.00
                    'annual': {'price_id': os.getenv('STRIPE_SOLO_ANNUAL_PRICE_ID'), 'amount': 59000}   # $590.00
                },
                'team': {
                    'monthly': {'price_id': os.getenv('STRIPE_TEAM_MONTHLY_PRICE_ID'), 'amount': 8900},  # $89.00
                    'annual': {'price_id': os.getenv('STRIPE_TEAM_ANNUAL_PRICE_ID'), 'amount': 89000}   # $890.00
                },
                'business': {
                    'monthly': {'price_id': os.getenv('STRIPE_BUSINESS_MONTHLY_PRICE_ID'), 'amount': 14900},  # $149.00
                    'annual': {'price_id': os.getenv('STRIPE_BUSINESS_ANNUAL_PRICE_ID'), 'amount': 149000}   # $1,490.00
                }
            }
        else:
            # Regular Public Pricing (Future)
            self.PRICING_CONFIG = {
                'solo': {
                    'monthly': {'price_id': os.getenv('STRIPE_SOLO_REGULAR_MONTHLY_PRICE_ID'), 'amount': 7900},  # $79.00
                    'annual': {'price_id': os.getenv('STRIPE_SOLO_REGULAR_ANNUAL_PRICE_ID'), 'amount': 79000}   # $790.00
                },
                'team': {
                    'monthly': {'price_id': os.getenv('STRIPE_TEAM_REGULAR_MONTHLY_PRICE_ID'), 'amount': 11900},  # $119.00
                    'annual': {'price_id': os.getenv('STRIPE_TEAM_REGULAR_ANNUAL_PRICE_ID'), 'amount': 119000}   # $1,190.00
                },
                'business': {
                    'monthly': {'price_id': os.getenv('STRIPE_BUSINESS_REGULAR_MONTHLY_PRICE_ID'), 'amount': 21900},  # $219.00
                    'annual': {'price_id': os.getenv('STRIPE_BUSINESS_REGULAR_ANNUAL_PRICE_ID'), 'amount': 219000}   # $2,190.00
                }
            }
    
    def is_stripe_available(self):
        """Check if Stripe is properly configured and available"""
        return STRIPE_IMPORT_SUCCESS and self.stripe_available and stripe.api_key is not None
    
    @property
    def stripe(self):
        """Expose stripe module for direct access when needed"""
        if self.is_stripe_available():
            return stripe
        return None
    
    def create_customer(self, email, name, phone=None):
        """Create a new Stripe customer"""
        try:
            if not self.is_stripe_available():
                # Silently return None if Stripe not available
                return None
                
            customer = stripe.Customer.create(
                email=email,
                name=name,
                phone=phone,
                metadata={
                    'source': 'nxtrix_crm',
                    'signup_date': datetime.now().isoformat()
                }
            )
            return customer
        except stripe.error.StripeError as e:
            # Silently handle Stripe errors in production
            return None
    
    def create_subscription(self, customer_id, plan_tier, billing_frequency='monthly'):
        """Create a new subscription"""
        try:
            # Get the correct price ID
            price_config = self.PRICING_CONFIG[plan_tier][billing_frequency]
            
            if not price_config['price_id']:
                # Silently handle missing price configuration
                return None
            
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{
                    'price': price_config['price_id']
                }],
                metadata={
                    'plan_tier': plan_tier,
                    'billing_frequency': billing_frequency,
                    'founder_pricing': 'true'
                },
                trial_period_days=7,  # 7-day free trial
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent']
            )
            
            return subscription
        except stripe.error.StripeError as e:
            # Silently handle Stripe errors in production
            return None
    
    def create_checkout_session(self, customer_email, plan_tier, billing_frequency='monthly'):
        """Create a Stripe Checkout session for subscription signup"""
        try:
            if not self.is_stripe_available():
                # Silently return None if Stripe not configured
                return None
                
            price_config = self.PRICING_CONFIG[plan_tier][billing_frequency]
            
            if not price_config['price_id']:
                # Silently handle missing price configuration
                return None
            
            checkout_session = stripe.checkout.Session.create(
                customer_email=customer_email,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_config['price_id'],
                    'quantity': 1
                }],
                mode='subscription',
                success_url=f"{os.getenv('CRM_URL')}?session_id={{CHECKOUT_SESSION_ID}}&success=true",
                cancel_url=f"{os.getenv('CRM_URL')}?success=false",
                metadata={
                    'plan_tier': plan_tier,
                    'billing_frequency': billing_frequency,
                    'founder_pricing': 'true'
                },
                subscription_data={
                    'trial_period_days': 7,
                    'metadata': {
                        'plan_tier': plan_tier,
                        'billing_frequency': billing_frequency
                    }
                }
            )
            
            return checkout_session
        except stripe.error.StripeError as e:
            st.error(f"Error creating checkout session: {str(e)}")
            return None
    
    def get_customer_subscriptions(self, customer_email):
        """Get all subscriptions for a customer"""
        try:
            # Check if Stripe is properly initialized
            if not self.is_stripe_available():
                return []
            
            # Additional check for the specific Secret attribute issue
            if not hasattr(stripe.apps, 'Secret') or stripe.apps.Secret is None:
                if os.getenv('STREAMLIT_ENV') != 'production':
                    st.info("ℹ️ Payment system temporarily unavailable")
                return []
            
            customers = stripe.Customer.list(email=customer_email)
            if not customers.data:
                return []
            
            customer = customers.data[0]
            subscriptions = stripe.Subscription.list(customer=customer.id)
            return subscriptions.data
        except AttributeError as e:
            # Silently handle missing Stripe configuration in production
            return []
        except Exception as e:
            # Silently handle payment data errors in production
            return []
        except stripe.error.StripeError as e:
            st.error(f"Error fetching subscriptions: {str(e)}")
            return []
    
    def upgrade_subscription(self, subscription_id, new_plan_tier, billing_frequency='monthly'):
        """Upgrade an existing subscription"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            price_config = self.PRICING_CONFIG[new_plan_tier][billing_frequency]
            
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'NXTRIX CRM - {new_plan_tier.title()} Plan'
                        },
                        'unit_amount': price_config['amount'],
                        'recurring': {
                            'interval': 'month' if billing_frequency == 'monthly' else 'year'
                        }
                    }
                }],
                metadata={
                    'plan_tier': new_plan_tier,
                    'billing_frequency': billing_frequency,
                    'upgraded_at': datetime.now().isoformat()
                },
                proration_behavior='immediate_prorations'
            )
            
            return updated_subscription
        except stripe.error.StripeError as e:
            st.error(f"Error upgrading subscription: {str(e)}")
            return None
    
    def cancel_subscription(self, subscription_id, at_period_end=True):
        """Cancel a subscription"""
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = stripe.Subscription.delete(subscription_id)
            
            return subscription
        except stripe.error.StripeError as e:
            st.error(f"Error canceling subscription: {str(e)}")
            return None
    
    def show_upgrade_button(self, current_plan, target_plan, billing_frequency='monthly'):
        """Show Stripe checkout button for plan upgrades"""
        user_email = st.session_state.get('user_profile', {}).get('email', '')
        
        if not user_email:
            st.error("Please log in to upgrade your plan")
            return
        
        price_config = self.PRICING_CONFIG[target_plan][billing_frequency]
        amount_display = f"${price_config['amount']/100:.0f}"
        period = "month" if billing_frequency == 'monthly' else "year"
        
        if st.button(f"🚀 Upgrade to {target_plan.title()} - {amount_display}/{period}", 
                    use_container_width=True, type="primary"):
            
            # Create checkout session
            checkout_session = self.create_checkout_session(
                user_email, target_plan, billing_frequency
            )
            
            if checkout_session:
                # Redirect to Stripe Checkout
                st.markdown(f"""
                <script>
                window.open('{checkout_session.url}', '_blank');
                </script>
                """, unsafe_allow_html=True)
                
                st.success(f"Redirecting to secure payment for {target_plan.title()} plan...")
                st.info("Complete your payment to activate the new plan immediately!")
    
    def handle_successful_payment(self, session_id):
        """Handle successful payment and update user tier"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            subscription = stripe.Subscription.retrieve(session.subscription)
            
            # Update user tier in session state
            plan_tier = subscription.metadata.get('plan_tier', 'solo')
            st.session_state.user_tier = plan_tier
            st.session_state.user_profile['plan'] = plan_tier
            st.session_state.user_profile['subscription_id'] = subscription.id
            st.session_state.user_profile['customer_id'] = session.customer
            
            return True
        except stripe.error.StripeError as e:
            st.error(f"Error processing successful payment: {str(e)}")
            return False
    
    def get_billing_portal_url(self, customer_id):
        """Create billing portal session for customer to manage their subscription"""
        try:
            portal_session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=os.getenv('CRM_URL')
            )
            return portal_session.url
        except stripe.error.StripeError as e:
            st.error(f"Error creating billing portal: {str(e)}")
            return None
    
    def show_billing_management(self):
        """Show billing management interface"""
        customer_id = st.session_state.get('user_profile', {}).get('customer_id')
        
        if customer_id:
            st.subheader("💳 Billing Management")
            
            if st.button("🏢 Manage Billing & Subscriptions", use_container_width=True):
                portal_url = self.get_billing_portal_url(customer_id)
                if portal_url:
                    st.markdown(f"""
                    <script>
                    window.open('{portal_url}', '_blank');
                    </script>
                    """, unsafe_allow_html=True)
                    st.success("Opening billing portal...")
        else:
            st.info("Complete your subscription setup to access billing management.")

# Global instance with PUBLIC pricing (Founder pricing separate)
stripe_system = StripePaymentSystem(founder_pricing=False)

# Separate Founder pricing system for pre-launch landing page
stripe_founder_system = StripePaymentSystem(founder_pricing=True)