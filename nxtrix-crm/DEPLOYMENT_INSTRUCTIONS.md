"""
Manual Database Deployment Instructions for NxTrix CRM
Use this guide to deploy your schema through Supabase Dashboard
"""

# DATABASE DEPLOYMENT GUIDE
# ========================

## Method 1: Supabase Dashboard (Recommended)

1. **Go to Supabase Dashboard:**
   - Open: https://supabase.com/dashboard
   - Login to your account
   - Select your project: ucrtaeoocwymzlykxgrf

2. **Access SQL Editor:**
   - Click on "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Deploy Schema:**
   - Copy the entire contents of `database/master_schema.sql`
   - Paste it into the SQL Editor
   - Click "Run" button

4. **Verify Deployment:**
   - Go to "Table Editor" to see all created tables
   - Check that you have these key tables:
     * profiles
     * deals
     * investors
     * subscription_usage
     * subscription_limits
     * And many more...

## Method 2: Using psql (Advanced)

If you have PostgreSQL client installed:

```bash
# Get your connection string from Supabase Dashboard > Settings > Database
psql "postgresql://postgres:[YOUR_PASSWORD]@db.ucrtaeoocwymzlykxgrf.supabase.co:5432/postgres"

# Then run:
\i database/master_schema.sql
```

## Method 3: Python Script (Alternative)

Run the deploy_schema.py script we created:

```bash
python deploy_schema.py
```

## Post-Deployment Verification

After deployment, run this verification script to ensure everything is working: