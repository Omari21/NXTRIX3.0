# 🏗️ Database Setup Instructions

## Execute in Supabase SQL Editor (in this exact order):

### Step 1: Core Deal Analyzer Tables
```sql
-- Copy and paste contents of: deal-analyzer-additions.sql
-- This creates: deals, investors, portfolios, market_data, AI analysis tables
```

### Step 2: Schema Enhancements  
```sql
-- Copy and paste contents of: schema-enhancements.sql
-- This adds: investor matching logic, automatic notifications, performance views
```

### Step 3: Verify Installation
```sql
-- Check if tables were created successfully
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('deals', 'investors', 'portfolios', 'deal_scores', 'market_data');

-- Should return 5 rows
```

## ⚠️ Important Notes:

1. **Execute deal-analyzer-additions.sql FIRST** - Creates core tables
2. **Then execute schema-enhancements.sql** - Adds integrations and optimizations
3. **Your existing CRM tables remain unchanged** - No data loss
4. **New tables integrate seamlessly** - Foreign key relationships established

## 🎯 After Database Setup:

✅ Ready for Phase 2 implementation:
- OpenAI deal scoring
- Automated investor matching  
- Twilio SMS notifications
- Stripe subscription management
- Advanced analytics dashboard

## 🔧 Troubleshooting:

If you get constraint errors:
- Make sure your existing `profiles` table has the required auth.users relationships
- Check that UUID extensions are enabled: `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`