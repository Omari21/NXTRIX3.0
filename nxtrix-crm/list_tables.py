#!/usr/bin/env python3
"""
Quick Database Table List - See what's currently in your Supabase
"""

import streamlit as st
from supabase import create_client, Client

def list_tables():
    """List all tables in the database"""
    url = st.secrets["SUPABASE"]["SUPABASE_URL"]
    key = st.secrets["SUPABASE"]["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    
    try:
        # Query information_schema to get table list
        result = supabase.rpc('sql', {
            'query': "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
        }).execute()
        
        tables = [row['table_name'] for row in result.data]
        print(f"📋 Found {len(tables)} tables in your database:")
        for table in tables:
            print(f"  • {table}")
            
    except Exception as e:
        # Fallback - try to list tables by attempting to query them
        print("Using fallback method to detect tables...")
        
        potential_tables = [
            'profiles', 'deals', 'investors', 'deal_scores', 'portfolios',
            'subscription_usage', 'subscription_limits', 'billing_history',
            'ai_deal_analysis', 'automation_rules', 'email_templates',
            'deal_notifications', 'portfolio_deals', 'deal_analytics',
            'market_intelligence', 'deal_stage_history'
        ]
        
        existing = []
        for table in potential_tables:
            try:
                supabase.table(table).select('*').limit(1).execute()
                existing.append(table)
            except:
                pass
        
        print(f"📋 Found {len(existing)} tables:")
        for table in existing:
            print(f"  ✅ {table}")

if __name__ == "__main__":
    list_tables()