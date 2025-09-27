#!/usr/bin/env python3
"""
Check profiles table structure
"""

import streamlit as st
from supabase import create_client, Client

def check_profiles_structure():
    """Check the actual structure of the profiles table"""
    url = st.secrets["SUPABASE"]["SUPABASE_URL"]
    key = st.secrets["SUPABASE"]["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    
    try:
        # Try to get one record to see the actual structure
        result = supabase.table('profiles').select('*').limit(1).execute()
        
        if result.data:
            print("✅ Profiles table structure (from existing data):")
            for key in result.data[0].keys():
                print(f"  • {key}")
        else:
            print("📋 No data in profiles table yet")
            
        # Try to insert a minimal profile to test
        test_profile = {
            'id': '22222222-2222-2222-2222-222222222222',
            'email': 'test2@nxtrix.com'
        }
        
        result = supabase.table('profiles').upsert(test_profile).execute()
        print("✅ Basic profile insertion works")
        
        # Clean up
        supabase.table('profiles').delete().eq('id', test_profile['id']).execute()
        print("✅ Profile cleanup successful")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_profiles_structure()