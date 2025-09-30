#!/usr/bin/env python3
"""
Deploy authentication schema updates to Supabase
Ensures the profiles table has all necessary columns for secure authentication
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def deploy_auth_schema():
    """Deploy authentication schema updates to Supabase"""
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Use service role key for schema changes
    
    if not supabase_url or not supabase_service_key:
        print("❌ Missing Supabase credentials. Check your .env file.")
        return False
    
    try:
        # Connect to Supabase
        supabase = create_client(supabase_url, supabase_service_key)
        print("🔌 Connected to Supabase successfully!")
        
        # SQL script to update the profiles table schema
        auth_schema_sql = """
        -- Add missing authentication columns to profiles table
        DO $$
        BEGIN
            -- Add password_hash column if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name = 'profiles' AND column_name = 'password_hash') THEN
                ALTER TABLE public.profiles ADD COLUMN password_hash TEXT;
                RAISE NOTICE 'Added password_hash column';
            END IF;
            
            -- Add full_name column if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name = 'profiles' AND column_name = 'full_name') THEN
                ALTER TABLE public.profiles ADD COLUMN full_name TEXT;
                RAISE NOTICE 'Added full_name column';
            END IF;
            
            -- Add company column if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name = 'profiles' AND column_name = 'company') THEN
                ALTER TABLE public.profiles ADD COLUMN company TEXT;
                RAISE NOTICE 'Added company column';
            END IF;
            
            -- Add phone column if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name = 'profiles' AND column_name = 'phone') THEN
                ALTER TABLE public.profiles ADD COLUMN phone TEXT;
                RAISE NOTICE 'Added phone column';
            END IF;
            
            -- Add experience_level column if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name = 'profiles' AND column_name = 'experience_level') THEN
                ALTER TABLE public.profiles ADD COLUMN experience_level TEXT;
                RAISE NOTICE 'Added experience_level column';
            END IF;
            
            -- Add investor_type column if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name = 'profiles' AND column_name = 'investor_type') THEN
                ALTER TABLE public.profiles ADD COLUMN investor_type TEXT;
                RAISE NOTICE 'Added investor_type column';
            END IF;
            
            -- Add business_goals column if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name = 'profiles' AND column_name = 'business_goals') THEN
                ALTER TABLE public.profiles ADD COLUMN business_goals TEXT;
                RAISE NOTICE 'Added business_goals column';
            END IF;
            
            -- Add marketing_consent column if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name = 'profiles' AND column_name = 'marketing_consent') THEN
                ALTER TABLE public.profiles ADD COLUMN marketing_consent BOOLEAN DEFAULT false;
                RAISE NOTICE 'Added marketing_consent column';
            END IF;
            
            -- Add is_active column if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name = 'profiles' AND column_name = 'is_active') THEN
                ALTER TABLE public.profiles ADD COLUMN is_active BOOLEAN DEFAULT true;
                RAISE NOTICE 'Added is_active column';
            END IF;
            
            -- Add last_login column if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name = 'profiles' AND column_name = 'last_login') THEN
                ALTER TABLE public.profiles ADD COLUMN last_login TIMESTAMP WITH TIME ZONE;
                RAISE NOTICE 'Added last_login column';
            END IF;
            
            -- Add trial_end_date column if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name = 'profiles' AND column_name = 'trial_end_date') THEN
                ALTER TABLE public.profiles ADD COLUMN trial_end_date TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '14 days');
                RAISE NOTICE 'Added trial_end_date column';
            END IF;
            
        END $$;
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_profiles_email_auth ON public.profiles(email) WHERE email IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_profiles_password_hash ON public.profiles(password_hash) WHERE password_hash IS NOT NULL;
        """
        
        # Execute the schema update using RPC call
        print("🔄 Deploying authentication schema updates...")
        
        # Use the rpc method to execute raw SQL
        result = supabase.rpc('exec_sql', {'sql': auth_schema_sql}).execute()
        
        print("✅ Authentication schema deployed successfully!")
        print("📋 Schema updates completed:")
        print("   - Added password_hash column for secure authentication")
        print("   - Added full_name, company, phone columns for user profiles")
        print("   - Added experience_level, investor_type, business_goals columns")
        print("   - Added marketing_consent, is_active, last_login columns")
        print("   - Added trial_end_date column for trial management")
        print("   - Created performance indexes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deploying authentication schema: {str(e)}")
        print("💡 You may need to run this SQL manually in your Supabase dashboard:")
        print("   Go to SQL Editor and paste the schema from update_auth_schema.sql")
        return False

if __name__ == "__main__":
    print("🚀 NXTRIX CRM - Authentication Schema Deployment")
    print("=" * 50)
    
    success = deploy_auth_schema()
    
    if success:
        print("🎉 Schema deployment completed successfully!")
        print("🔐 Your authentication system is now secure and ready for production!")
    else:
        print("⚠️  Manual schema deployment may be required.")
        print("📖 Check the update_auth_schema.sql file for the SQL commands.")