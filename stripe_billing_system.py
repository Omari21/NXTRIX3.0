"""Stripe billing system module"""

class StripeBillingSystem:
    def __init__(self):
        self.enabled = True
    
    def create_subscription(self, user_id, plan):
        return {"success": True, "subscription_id": "demo_sub_123"}

billing_manager = StripeBillingSystem()