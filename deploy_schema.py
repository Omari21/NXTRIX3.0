#!/usr/bin/env python3
"""
Database Schema Deployment Script for NxTrix CRM
Deploys the master_schema.sql to Supabase database
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
import streamlit as st

def deploy_schema():
    """Deploy the master schema to Supabase database"""
    
    # Get credentials from Streamlit secrets
    try:
        url = st.secrets["SUPABASE"]["SUPABASE_URL"]
        key = st.secrets["SUPABASE"]["SUPABASE_KEY"]
        print(f"Connecting to Supabase: {url}")
    except Exception as e:
        print(f"Error loading secrets: {e}")
        return False
    
    # Create Supabase client
    try:
        supabase: Client = create_client(url, key)
        print("✅ Connected to Supabase successfully")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False
    
    # Read the master schema file
    schema_path = Path(__file__).parent / "database" / "master_schema.sql"
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        return False
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        print(f"✅ Loaded schema file ({len(schema_sql)} characters)")
    except Exception as e:
        print(f"❌ Failed to read schema file: {e}")
        return False
    
    # Split the schema into individual statements (basic approach)
    # This splits on ';' but is more sophisticated for PostgreSQL
    statements = []
    current_statement = ""
    in_function = False
    
    for line in schema_sql.split('\n'):
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('--'):
            continue
            
        # Track if we're inside a function definition
        if 'CREATE OR REPLACE FUNCTION' in line.upper() or 'CREATE FUNCTION' in line.upper():
            in_function = True
        elif line.upper().startswith('$$') and in_function:
            in_function = not in_function
            
        current_statement += line + '\n'
        
        # If we hit a semicolon and we're not in a function, this is the end of a statement
        if line.endswith(';') and not in_function:
            if current_statement.strip():
                statements.append(current_statement.strip())
            current_statement = ""
    
    # Add any remaining statement
    if current_statement.strip():
        statements.append(current_statement.strip())
    
    print(f"✅ Parsed {len(statements)} SQL statements")
    
    # Execute statements one by one
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements, 1):
        if not statement.strip():
            continue
            
        try:
            # Use rpc call for complex SQL or try direct SQL execution
            # For schema deployment, we'll use the SQL execution
            result = supabase.rpc('sql', {'query': statement})
            print(f"✅ Statement {i}/{len(statements)} executed successfully")
            success_count += 1
            
        except Exception as e:
            print(f"⚠️  Statement {i}/{len(statements)} failed: {str(e)[:100]}...")
            error_count += 1
            
            # Some statements might fail if they already exist - that's ok
            if any(phrase in str(e).lower() for phrase in ['already exists', 'duplicate', 'conflict']):
                print(f"   (This is normal - resource already exists)")
                success_count += 1
                error_count -= 1
    
    print(f"\n🎯 Deployment Summary:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Failed: {error_count}")
    print(f"   📊 Total: {len(statements)}")
    
    if error_count == 0:
        print("\n🚀 Database schema deployment completed successfully!")
        return True
    else:
        print(f"\n⚠️  Deployment completed with {error_count} errors")
        return False

if __name__ == "__main__":
    print("🗄️  NxTrix CRM Database Schema Deployment")
    print("=" * 50)
    
    success = deploy_schema()
    
    if success:
        print("\n✅ Ready to test your application!")
        sys.exit(0)
    else:
        print("\n❌ Please check the errors above and try again")
        sys.exit(1)