#!/usr/bin/env python3
"""
Verify Stripe Configuration
Tests that all Price IDs are properly configured
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_stripe_config():
    """Verify all Stripe configuration is complete"""
    
    print("🔍 NXTRIX CRM - Stripe Configuration Verification")
    print("=" * 50)
    
    # Check basic Stripe keys
    stripe_keys = {
        'STRIPE_PUBLISHABLE_KEY': os.getenv('STRIPE_PUBLISHABLE_KEY'),
        'STRIPE_SECRET_KEY': os.getenv('STRIPE_SECRET_KEY'),
        'STRIPE_WEBHOOK_SECRET': os.getenv('STRIPE_WEBHOOK_SECRET')
    }
    
    print("\n📋 Basic Stripe Keys:")
    for key, value in stripe_keys.items():
        if value:
            print(f"✅ {key}: {value[:20]}...")
        else:
            print(f"❌ {key}: NOT SET")
    
    # Check Founder VIP Price IDs
    founder_prices = {
        'Solo Monthly': os.getenv('STRIPE_SOLO_MONTHLY_PRICE_ID'),
        'Solo Annual': os.getenv('STRIPE_SOLO_ANNUAL_PRICE_ID'),
        'Team Monthly': os.getenv('STRIPE_TEAM_MONTHLY_PRICE_ID'),
        'Team Annual': os.getenv('STRIPE_TEAM_ANNUAL_PRICE_ID'),
        'Business Monthly': os.getenv('STRIPE_BUSINESS_MONTHLY_PRICE_ID'),
        'Business Annual': os.getenv('STRIPE_BUSINESS_ANNUAL_PRICE_ID')
    }
    
    print("\n🎯 Founder VIP Price IDs:")
    all_founder_configured = True
    for plan, price_id in founder_prices.items():
        if price_id and price_id.startswith('price_'):
            print(f"✅ {plan}: {price_id}")
        else:
            print(f"❌ {plan}: NOT SET")
            all_founder_configured = False
    
    # Check Regular Price IDs
    regular_prices = {
        'Solo Monthly': os.getenv('STRIPE_SOLO_REGULAR_MONTHLY_PRICE_ID'),
        'Solo Annual': os.getenv('STRIPE_SOLO_REGULAR_ANNUAL_PRICE_ID'),
        'Team Monthly': os.getenv('STRIPE_TEAM_REGULAR_MONTHLY_PRICE_ID'),
        'Team Annual': os.getenv('STRIPE_TEAM_REGULAR_ANNUAL_PRICE_ID'),
        'Business Monthly': os.getenv('STRIPE_BUSINESS_REGULAR_MONTHLY_PRICE_ID'),
        'Business Annual': os.getenv('STRIPE_BUSINESS_REGULAR_ANNUAL_PRICE_ID')
    }
    
    print("\n💼 Regular Public Price IDs:")
    all_regular_configured = True
    for plan, price_id in regular_prices.items():
        if price_id and price_id.startswith('price_'):
            print(f"✅ {plan}: {price_id}")
        else:
            print(f"❌ {plan}: NOT SET")
            all_regular_configured = False
    
    # Test Stripe integration import
    print("\n🧪 Testing Stripe Integration:")
    try:
        from stripe_integration import stripe_system
        print(f"✅ Stripe integration imported successfully")
        print(f"✅ Founder pricing mode: {stripe_system.founder_pricing}")
        
        # Test price configuration access
        try:
            solo_monthly = stripe_system.PRICING_CONFIG['solo']['monthly']['price_id']
            if solo_monthly:
                print(f"✅ Solo monthly price configured: {solo_monthly}")
            else:
                print(f"❌ Solo monthly price not configured")
        except Exception as e:
            print(f"❌ Error accessing price config: {e}")
            
    except ImportError as e:
        print(f"❌ Failed to import stripe_integration: {e}")
    
    print("\n" + "=" * 50)
    
    # Summary
    if all(stripe_keys.values()) and all_founder_configured:
        print("🎉 SUCCESS: Your Stripe configuration is COMPLETE!")
        print("✅ Ready for production launch with Founder pricing")
    elif all(stripe_keys.values()) and not all_founder_configured:
        print("⚠️  PARTIAL: Basic Stripe setup complete, but some Price IDs missing")
    else:
        print("❌ INCOMPLETE: Missing basic Stripe configuration")
    
    print("\n🔗 CRM URL:", os.getenv('CRM_URL', 'NOT SET'))
    
    return all(stripe_keys.values()) and all_founder_configured

if __name__ == "__main__":
    verify_stripe_config()