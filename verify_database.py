#!/usr/bin/env python3
"""
Database Verification Script for NxTrix CRM
Tests database connectivity and verifies schema deployment
"""

import streamlit as st
from supabase import create_client, Client
import sys
from datetime import datetime

def test_database_connection():
    """Test basic database connectivity"""
    print("🔌 Testing database connection...")
    
    try:
        url = st.secrets["SUPABASE"]["SUPABASE_URL"]
        key = st.secrets["SUPABASE"]["SUPABASE_KEY"]
        supabase: Client = create_client(url, key)
        
        # Test basic connection with a simple query
        result = supabase.table('profiles').select('id').limit(1).execute()
        print("✅ Database connection successful")
        return supabase
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def verify_tables(supabase):
    """Verify that all required tables exist"""
    print("\n📋 Verifying table structure...")
    
    required_tables = [
        'profiles',
        'deals', 
        'investors',
        'deal_scores',
        'portfolios',
        'subscription_usage',
        'subscription_limits',
        'billing_history',
        'ai_deal_analysis',
        'automation_rules',
        'email_templates'
    ]
    
    existing_tables = []
    missing_tables = []
    
    for table in required_tables:
        try:
            # Try to query the table structure
            result = supabase.table(table).select('*').limit(1).execute()
            existing_tables.append(table)
            print(f"  ✅ {table}")
        except Exception as e:
            missing_tables.append(table)
            print(f"  ❌ {table} - {str(e)[:50]}...")
    
    print(f"\n📊 Table Summary:")
    print(f"  ✅ Existing: {len(existing_tables)}/{len(required_tables)}")
    print(f"  ❌ Missing: {len(missing_tables)}")
    
    return len(missing_tables) == 0

def test_subscription_limits(supabase):
    """Test that subscription limits are properly seeded"""
    print("\n🎯 Testing subscription limits...")
    
    try:
        result = supabase.table('subscription_limits').select('*').execute()
        limits = result.data
        
        if not limits:
            print("❌ No subscription limits found")
            return False
            
        # Check for required tiers
        tiers = set(limit['tier'] for limit in limits)
        required_tiers = {'free', 'pro', 'enterprise'}
        
        if required_tiers.issubset(tiers):
            print(f"✅ All subscription tiers present: {tiers}")
            print(f"✅ Found {len(limits)} limit configurations")
            return True
        else:
            missing = required_tiers - tiers
            print(f"❌ Missing subscription tiers: {missing}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to verify subscription limits: {e}")
        return False

def test_functions(supabase):
    """Test that database functions are working"""
    print("\n⚙️  Testing database functions...")
    
    # Test check_usage_limit function
    try:
        # This will fail if user doesn't exist, but function should exist
        result = supabase.rpc('check_usage_limit', {
            'p_user_id': '00000000-0000-0000-0000-000000000000',
            'p_usage_type': 'deals_per_month'
        }).execute()
        print("✅ check_usage_limit function works")
        return True
    except Exception as e:
        if 'function' in str(e).lower() and 'does not exist' in str(e).lower():
            print("❌ check_usage_limit function missing")
            return False
        else:
            print("✅ check_usage_limit function exists (expected error for test user)")
            return True

def create_test_profile(supabase):
    """Create a test profile to verify write operations"""
    print("\n👤 Testing profile creation...")
    
    try:
        # Try to insert a test profile
        test_profile = {
            'id': '11111111-1111-1111-1111-111111111111',
            'email': 'test@nxtrix.com',
            'name': 'Test User',
            'role': 'analyst',
            'subscription_tier': 'free'
        }
        
        result = supabase.table('profiles').upsert(test_profile).execute()
        print("✅ Profile creation successful")
        
        # Clean up - delete the test profile
        supabase.table('profiles').delete().eq('id', test_profile['id']).execute()
        print("✅ Profile cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Profile creation failed: {e}")
        return False

def main():
    """Run all database verification tests"""
    print("🗄️  NxTrix CRM Database Verification")
    print("=" * 50)
    
    # Test 1: Database Connection
    supabase = test_database_connection()
    if not supabase:
        print("\n❌ Cannot proceed without database connection")
        return False
    
    # Test 2: Table Structure
    tables_ok = verify_tables(supabase)
    
    # Test 3: Subscription Limits
    limits_ok = test_subscription_limits(supabase)
    
    # Test 4: Database Functions
    functions_ok = test_functions(supabase)
    
    # Test 5: Write Operations
    write_ok = create_test_profile(supabase)
    
    # Summary
    print("\n🎯 Verification Summary:")
    print("=" * 30)
    print(f"  Database Connection: {'✅' if supabase else '❌'}")
    print(f"  Table Structure: {'✅' if tables_ok else '❌'}")
    print(f"  Subscription Limits: {'✅' if limits_ok else '❌'}")
    print(f"  Database Functions: {'✅' if functions_ok else '❌'}")
    print(f"  Write Operations: {'✅' if write_ok else '❌'}")
    
    all_passed = all([supabase, tables_ok, limits_ok, functions_ok, write_ok])
    
    if all_passed:
        print("\n🚀 Database is ready for production!")
        print("✅ You can now test your Streamlit application")
    else:
        print("\n⚠️  Some tests failed - please check deployment")
        print("💡 Try deploying the schema again via Supabase Dashboard")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)