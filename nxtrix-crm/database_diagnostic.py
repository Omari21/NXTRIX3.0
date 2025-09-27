"""
Database Connection Test & Diagnostic Tool
Tests Supabase connection and provides database status information
"""

import streamlit as st
from datetime import datetime
import traceback

def test_supabase_connection():
    """Test if Supabase connection is working properly"""
    try:
        # Try to get Supabase credentials from secrets
        url = st.secrets.get("SUPABASE", {}).get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE", {}).get("SUPABASE_KEY")
        
        if not url or not key:
            return False, "Supabase credentials not found in secrets.toml"
        
        # Try to create Supabase client
        from supabase import create_client
        supabase = create_client(url, key)
        
        # Try a simple query to test connection
        result = supabase.table('profiles').select('email').limit(1).execute()
        
        return True, f"✅ Supabase connected successfully. URL: {url[:50]}..."
        
    except Exception as e:
        return False, f"❌ Supabase connection failed: {str(e)}"

def test_local_sqlite():
    """Test if local SQLite database is accessible"""
    try:
        import sqlite3
        import os
        
        db_path = "crm_data.db"
        exists = os.path.exists(db_path)
        
        if not exists:
            return False, "❌ Local SQLite database file not found"
        
        # Try to connect and query
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        table_count = len(tables)
        return True, f"✅ SQLite database accessible with {table_count} tables"
        
    except Exception as e:
        return False, f"❌ SQLite connection failed: {str(e)}"

def show_database_diagnostic():
    """Show comprehensive database diagnostic information"""
    st.subheader("🔍 Database Connection Diagnostic")
    
    # Test Supabase
    st.markdown("### Supabase Connection Test")
    supabase_ok, supabase_msg = test_supabase_connection()
    if supabase_ok:
        st.success(supabase_msg)
    else:
        st.error(supabase_msg)
    
    # Test Local SQLite
    st.markdown("### Local SQLite Test")
    sqlite_ok, sqlite_msg = test_local_sqlite()
    if sqlite_ok:
        st.success(sqlite_msg)
    else:
        st.error(sqlite_msg)
    
    # Show current configuration
    st.markdown("### Current Configuration")
    
    # Production mode status
    from streamlit_app import PRODUCTION_MODE
    if PRODUCTION_MODE:
        st.info("📊 **Production Mode:** ON - Should use Supabase")
    else:
        st.info("🧪 **Beta Mode:** ON - Uses local storage/SQLite")
    
    # Show user authentication status
    st.markdown("### User Authentication Status")
    user_authenticated = st.session_state.get('user_authenticated', False)
    is_admin = st.session_state.get('is_admin', False)
    user_email = st.session_state.get('user_email', 'Not logged in')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("User Authenticated", "✅ Yes" if user_authenticated else "❌ No")
    with col2:
        st.metric("Admin Status", "🔑 Admin" if is_admin else "👤 User")  
    with col3:
        st.metric("Current Email", user_email)
    
    # Recommendations
    st.markdown("### 🎯 Recommendations")
    
    if PRODUCTION_MODE and not supabase_ok:
        st.warning("⚠️ **Action Required:** Production mode is enabled but Supabase connection failed. New user accounts will not be saved to the cloud database.")
        
        with st.expander("🔧 How to Fix Supabase Connection"):
            st.markdown("""
            **To fix Supabase connection:**
            
            1. **Check your `.streamlit/secrets.toml` file should contain:**
            ```toml
            [SUPABASE]
            SUPABASE_URL = "https://your-project.supabase.co"
            SUPABASE_KEY = "your-anon-key"
            ```
            
            2. **Get your credentials from Supabase dashboard:**
            - Go to your Supabase project
            - Navigate to Settings > API
            - Copy the URL and anon key
            
            3. **Verify your Supabase database has a 'profiles' table with proper schema**
            """)
    
    if supabase_ok:
        st.success("✅ **All Good:** Supabase connection is working. New user accounts will be saved to the cloud database.")

def show_user_account_test():
    """Test user account creation and retrieval"""
    st.subheader("👤 User Account Test")
    
    with st.expander("🧪 Test Account Operations"):
        st.markdown("**Test creating and retrieving user accounts:**")
        
        if st.button("🔍 Check demo@nxtrix.com"):
            try:
                # Try to find the demo account
                from streamlit_app import UserAuthSystem
                exists = UserAuthSystem._email_exists("demo@nxtrix.com")
                
                if exists:
                    st.success("✅ demo@nxtrix.com account found in database")
                else:
                    st.warning("⚠️ demo@nxtrix.com account not found - this might be expected in production")
                    
            except Exception as e:
                st.error(f"❌ Error checking account: {str(e)}")
        
        if st.button("📊 Show All User Accounts"):
            try:
                supabase_ok, _ = test_supabase_connection()
                if supabase_ok:
                    from supabase import create_client
                    url = st.secrets["SUPABASE"]["SUPABASE_URL"] 
                    key = st.secrets["SUPABASE"]["SUPABASE_KEY"]
                    supabase = create_client(url, key)
                    
                    # Check both tables for user accounts
                    profiles_result = None
                    user_profiles_result = None
                    
                    try:
                        profiles_result = supabase.table('profiles').select('email, full_name, created_at, subscription_tier').execute()
                    except:
                        pass
                    
                    try:
                        user_profiles_result = supabase.table('user_profiles').select('email, full_name, created_at, subscription_tier').execute()
                    except:
                        pass
                    
                    # Combine results
                    all_accounts = []
                    if profiles_result and profiles_result.data:
                        for account in profiles_result.data:
                            account['source_table'] = 'profiles'
                        all_accounts.extend(profiles_result.data)
                    
                    if user_profiles_result and user_profiles_result.data:
                        for account in user_profiles_result.data:
                            account['source_table'] = 'user_profiles'
                        all_accounts.extend(user_profiles_result.data)
                    
                    result = type('obj', (object,), {'data': all_accounts})()
                    
                    if result.data:
                        import pandas as pd
                        df = pd.DataFrame(result.data)
                        st.dataframe(df, use_container_width=True)
                        st.success(f"✅ Found {len(result.data)} user accounts in Supabase")
                    else:
                        st.info("ℹ️ No user accounts found in Supabase database")
                else:
                    st.error("❌ Cannot retrieve accounts - Supabase connection failed")
                    
            except Exception as e:
                st.error(f"❌ Error retrieving accounts: {str(e)}")
                st.code(traceback.format_exc())
        
        # Direct Account Creation Test
        st.markdown("### 🧪 Direct Account Creation Test")
        
        with st.expander("💡 **Test Account Creation Through App UI**"):
            st.markdown("""
            **Best way to test**: Create an account through the normal signup process:
            
            1. **Go to the main app** (close admin mode)
            2. **Click "Register"** or "Sign Up"
            3. **Fill out the form** with test data
            4. **Submit the form**
            5. **Come back here to check if it appeared in Supabase**
            
            This tests the complete flow including RLS policies.
            """)
        
        if st.button("🧪 Test Account Creation (Creates test@diagnostic.com)"):
            try:
                from streamlit_app import UserAuthSystem
                from datetime import datetime, timedelta
                
                # Test creating an account using the fixed system
                success, profile = UserAuthSystem._create_user_account(
                    full_name="Test User",
                    email="test@diagnostic.com", 
                    password="testpass123",
                    company="Test Company",
                    phone="123-456-7890",
                    plan="starter",
                    experience="beginner",
                    investor_type="individual",
                    goals=["Test goal"],
                    marketing_consent=True
                )
                
                if success:
                    st.success("✅ Test account created successfully!")
                    st.json(profile)
                else:
                    st.error("❌ Test account creation failed")
                    
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ Error testing account creation: {error_msg}")
                
                # Check if it's an RLS policy error
                if "row-level security policy" in error_msg.lower():
                    st.error("🚨 **Row Level Security (RLS) Policy Error Detected**")
                    
                    with st.expander("🔧 How to Fix RLS Policy Error"):
                        st.markdown("""
                        **The profiles table has Row Level Security enabled but no INSERT policy.**
                        
                        **To fix this, run these SQL commands in your Supabase SQL Editor:**
                        
                        ```sql
                        -- Option 1: Allow all authenticated users to insert their own profiles
                        CREATE POLICY "Users can insert their own profile" ON profiles
                            FOR INSERT WITH CHECK (auth.uid()::text = id::text);
                        
                        -- Option 2: Allow anyone to insert profiles (for public registration)
                        CREATE POLICY "Anyone can insert profiles" ON profiles
                            FOR INSERT WITH CHECK (true);
                        
                        -- Option 3: Temporarily disable RLS for testing (NOT recommended for production)
                        ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;
                        ```
                        
                        **Recommended: Use Option 2 for beta testing, then switch to Option 1 for production.**
                        """)
                        
                        if st.button("📋 Copy SQL Commands"):
                            st.code('''-- Allow anyone to insert profiles (for beta testing)
CREATE POLICY "Anyone can insert profiles" ON profiles
    FOR INSERT WITH CHECK (true);''')
                
                st.code(traceback.format_exc())
        
        # Table Analysis & Recommendation
        st.markdown("### � Table Structure Analysis")
        if st.button("� Analyze Both Tables & Get Recommendation"):
            try:
                from supabase import create_client
                url = st.secrets["SUPABASE"]["SUPABASE_URL"] 
                key = st.secrets["SUPABASE"]["SUPABASE_KEY"]
                supabase = create_client(url, key)
                
                st.info("🔍 Analyzing both tables to determine the correct schema...")
                
                tables_info = {}
                
                # Check profiles table
                try:
                    profiles_result = supabase.table('profiles').select('*').execute()
                    profiles_count = len(profiles_result.data) if profiles_result.data else 0
                    profiles_columns = list(profiles_result.data[0].keys()) if profiles_result.data else []
                    
                    tables_info['profiles'] = {
                        'exists': True,
                        'count': profiles_count,
                        'columns': profiles_columns,
                        'status': '✅ Exists'
                    }
                    st.success(f"✅ 'profiles' table: {profiles_count} records")
                    
                except Exception as e:
                    tables_info['profiles'] = {
                        'exists': False,
                        'error': str(e),
                        'status': f'❌ Error: {str(e)}'
                    }
                    st.error(f"❌ 'profiles' table: {str(e)}")
                
                # Check user_profiles table  
                try:
                    user_profiles_result = supabase.table('user_profiles').select('*').execute()
                    user_profiles_count = len(user_profiles_result.data) if user_profiles_result.data else 0
                    user_profiles_columns = list(user_profiles_result.data[0].keys()) if user_profiles_result.data else []
                    
                    tables_info['user_profiles'] = {
                        'exists': True,
                        'count': user_profiles_count,
                        'columns': user_profiles_columns,
                        'status': '✅ Exists'
                    }
                    st.success(f"✅ 'user_profiles' table: {user_profiles_count} records")
                    
                except Exception as e:
                    tables_info['user_profiles'] = {
                        'exists': False,
                        'error': str(e),
                        'status': f'❌ Error: {str(e)}'
                    }
                    st.error(f"❌ 'user_profiles' table: {str(e)}")
                
                # Analysis and Recommendation
                st.markdown("### 🎯 **Analysis & Recommendation**")
                
                if tables_info.get('profiles', {}).get('exists') and tables_info.get('user_profiles', {}).get('exists'):
                    st.warning("⚠️ **You have BOTH tables - this is likely causing confusion**")
                    
                    profiles_count = tables_info['profiles'].get('count', 0)
                    user_profiles_count = tables_info['user_profiles'].get('count', 0)
                    
                    if profiles_count > 0 and user_profiles_count > 0:
                        st.error("🚨 **PROBLEM**: Both tables have data - you need to consolidate!")
                        st.markdown("**Recommendation**: Pick one table and migrate all data to it")
                    elif profiles_count > 0:
                        st.info("📊 **Use 'profiles' table** - it has your data")
                        recommended_table = 'profiles'
                    elif user_profiles_count > 0:
                        st.info("📊 **Use 'user_profiles' table** - it has your data")
                        recommended_table = 'user_profiles'
                    else:
                        st.info("📊 **Both tables are empty** - pick one and delete the other")
                        recommended_table = 'profiles'  # Default choice
                    
                    # Show column comparison
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("profiles columns")
                        if tables_info['profiles'].get('columns'):
                            for col in tables_info['profiles']['columns']:
                                st.write(f"• {col}")
                        else:
                            st.write("No data to show columns")
                    
                    with col2:
                        st.subheader("user_profiles columns")
                        if tables_info['user_profiles'].get('columns'):
                            for col in tables_info['user_profiles']['columns']:
                                st.write(f"• {col}")
                        else:
                            st.write("No data to show columns")
                    
                    # Action buttons
                    st.markdown("### 🔧 **Fix Actions**")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("🔄 Switch to 'profiles'"):
                            st.session_state.use_user_profiles_table = False
                            st.success("✅ App will use 'profiles' table")
                            st.rerun()
                    
                    with col2:
                        if st.button("🔄 Switch to 'user_profiles'"):
                            st.session_state.use_user_profiles_table = True
                            st.success("✅ App will use 'user_profiles' table")
                            st.rerun()
                    
                    with col3:
                        if st.button("📋 Show SQL to clean up"):
                            st.code(f"""-- Option 1: Drop the unused table (CAREFUL!)
DROP TABLE IF EXISTS user_profiles;  -- or profiles

-- Option 2: Rename for clarity
ALTER TABLE user_profiles RENAME TO profiles_backup;

-- Option 3: Migrate data (example)
INSERT INTO profiles SELECT * FROM user_profiles;""", language='sql')
                
                elif tables_info.get('profiles', {}).get('exists'):
                    st.success("✅ **Only 'profiles' table exists - this is clean!**")
                    st.session_state.use_user_profiles_table = False
                    
                elif tables_info.get('user_profiles', {}).get('exists'):
                    st.success("✅ **Only 'user_profiles' table exists - this is clean!**")
                    st.session_state.use_user_profiles_table = True
                    
                else:
                    st.error("❌ **Neither table exists properly - check your Supabase connection**")
                    
            except Exception as e:
                st.error(f"❌ Table discovery failed: {str(e)}")

        # Schema Discovery
        st.markdown("### � Schema Discovery")
        
        table_choice = st.selectbox("Choose table to analyze:", ["profiles", "user_profiles"])
        
        if st.button(f"🔍 Discover {table_choice} Schema"):
            try:
                from supabase import create_client
                url = st.secrets["SUPABASE"]["SUPABASE_URL"] 
                key = st.secrets["SUPABASE"]["SUPABASE_KEY"]
                supabase = create_client(url, key)
                
                st.info(f"🔍 Testing which columns exist in the '{table_choice}' table...")
                
                # Try to get table schema by attempting to insert with various common fields
                test_fields = [
                    'id', 'email', 'full_name', 'created_at', 'updated_at',
                    'company', 'phone', 'subscription_tier', 'plan',
                    'experience_level', 'investor_type', 'marketing_consent',
                    'password_hash', 'is_active', 'trial_end_date'
                ]
                
                import uuid
                test_id = str(uuid.uuid4())
                
                # Test minimal insert first
                minimal_data = {
                    'id': test_id,
                    'email': f'schema-test-{test_id[:8]}@test.com'
                }
                
                try:
                    result = supabase.table(table_choice).insert(minimal_data).execute()
                    if result.data:
                        st.success("✅ Minimal insert successful with: id, email")
                        # Clean up
                        supabase.table(table_choice).delete().eq('id', test_id).execute()
                        
                        # Now test each additional field
                        existing_fields = ['id', 'email']
                        for field in ['full_name', 'created_at', 'updated_at', 'company', 'phone']:
                            test_data = minimal_data.copy()
                            if field in ['created_at', 'updated_at']:
                                test_data[field] = datetime.now().isoformat()
                            else:
                                test_data[field] = f'test_{field}'
                            
                            try:
                                test_result = supabase.table(table_choice).insert(test_data).execute()
                                if test_result.data:
                                    existing_fields.append(field)
                                    st.success(f"✅ {field} exists")
                                    # Clean up
                                    supabase.table(table_choice).delete().eq('id', test_id).execute()
                            except Exception as field_error:
                                if "Could not find" in str(field_error):
                                    st.warning(f"❌ {field} does NOT exist")
                                else:
                                    st.info(f"⚠️ {field}: {str(field_error)}")
                        
                        st.success(f"🎯 **Confirmed existing fields**: {existing_fields}")
                        
                    else:
                        st.error("❌ Even minimal insert failed - check RLS policies")
                        
                except Exception as insert_error:
                    if "row-level security policy" in str(insert_error).lower():
                        st.error("🚨 **RLS is still blocking inserts!**")
                        st.markdown("**You need to run this SQL in Supabase:**")
                        st.code(f"""CREATE POLICY "Enable insert for all users" ON {table_choice}
    FOR INSERT WITH CHECK (true);""", language='sql')
                    else:
                        st.error(f"❌ Schema test failed: {str(insert_error)}")
                        
            except Exception as e:
                st.error(f"❌ Schema discovery failed: {str(e)}")

        # RLS Policy Diagnostic
        st.markdown("### 🛡️ Row Level Security Diagnostic")
        if st.button("Check RLS Status"):
            try:
                from supabase import create_client
                url = st.secrets["SUPABASE"]["SUPABASE_URL"] 
                key = st.secrets["SUPABASE"]["SUPABASE_KEY"]
                supabase = create_client(url, key)
                
                st.info("🔍 Checking RLS policies for profiles table...")
                
                # First, let's check what columns actually exist
                st.markdown("**Step 1: Checking table schema**")
                try:
                    # Get existing records to see the actual schema
                    result = supabase.table('profiles').select('*').limit(1).execute()
                    st.success("✅ Profiles table is accessible")
                    
                    if result.data:
                        st.info("📋 Current table columns:")
                        columns = list(result.data[0].keys())
                        st.write(columns)
                    else:
                        st.info("📋 Table is empty, checking schema via insert attempt...")
                        
                except Exception as schema_error:
                    st.warning(f"⚠️ Schema check: {str(schema_error)}")
                
                # Try to check table structure
                try:
                    
                    # Try a direct insert to test RLS with minimal data
                    import uuid
                    test_id = str(uuid.uuid4())
                    
                    # Start with basic required fields only
                    test_data = {
                        'id': test_id,
                        'full_name': 'RLS Test User',
                        'email': f'rls-test-{test_id[:8]}@diagnostic.com'
                    }
                    
                    # Add additional fields that commonly exist
                    optional_fields = {
                        'company': 'Test Company',
                        'phone': '123-456-7890',
                        'subscription_tier': 'starter',
                        'experience_level': 'beginner',
                        'investor_type': 'individual',
                        'marketing_consent': True
                    }
                    
                    st.markdown("**Step 2: Testing RLS with minimal data**")
                    st.write("Testing with fields:", list(test_data.keys()))
                    
                    insert_result = supabase.table('profiles').insert(test_data).execute()
                    if insert_result.data:
                        st.success("✅ RLS allows inserts - No policy blocking")
                        st.info("♻️ Cleaning up test record...")
                        # Clean up the test record
                        supabase.table('profiles').delete().eq('id', test_id).execute()
                    else:
                        st.error("❌ Insert returned no data - check RLS policies")
                        
                except Exception as rls_error:
                    error_str = str(rls_error)
                    if "row-level security policy" in error_str.lower() or "42501" in error_str:
                        st.error("🚨 **RLS Policy is blocking inserts!**")
                        
                        st.markdown("""
                        **SOLUTION: Add an INSERT policy to your profiles table**
                        
                        Go to your Supabase Dashboard → SQL Editor and run:
                        """)
                        
                        sql_fix = '''-- Allow public registration (recommended for beta)
CREATE POLICY "Enable insert for all users" ON profiles
    FOR INSERT WITH CHECK (true);

-- OR for authenticated users only:
CREATE POLICY "Users can insert their own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid()::text = id::text);'''
                        
                        st.code(sql_fix, language='sql')
                        
                        if st.button("📋 Copy SQL Fix"):
                            st.success("SQL commands copied! Run these in Supabase SQL Editor.")
                            
                    else:
                        st.error(f"❌ Unknown insert error: {error_str}")
                        
            except Exception as e:
                st.error(f"❌ RLS diagnostic failed: {str(e)}")