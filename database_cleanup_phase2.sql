-- 🔧 DATABASE CLEANUP PHASE 2: REDUNDANCY REMOVAL
-- Run AFTER Phase 1 is complete and registration is working

-- =============================================
-- REMOVE DUPLICATE TABLES (MAJOR CLEANUP)
-- =============================================

-- 1. Remove redundant portfolio table (keep portfolios)
DROP TABLE IF EXISTS portfolio CASCADE;

-- 2. Remove redundant deal tracking tables
DROP TABLE IF EXISTS deal_stage_history CASCADE;
DROP TABLE IF EXISTS deal_status_history CASCADE;

-- 3. Simplify lead management - consider these removals:
-- DROP TABLE IF EXISTS deal_activities CASCADE; -- too many activity tables
-- DROP TABLE IF EXISTS deal_milestones CASCADE; -- redundant with activities

-- =============================================
-- OPTIMIZE MASSIVE TABLES
-- =============================================

-- buyer_leads has 66 columns - consider splitting into:
-- - buyer_leads_basic (core info)
-- - buyer_criteria (preferences) 
-- - buyer_deals (deal-specific data)

-- seller_leads has 65 columns - consider splitting into:
-- - seller_leads_basic (core info)
-- - property_details (property-specific data)
-- - deal_calculations (financial data)

-- =============================================
-- REMOVE UNUSED/REDUNDANT CONSTRAINTS
-- =============================================

-- Check which foreign keys are actually needed
SELECT 
    tc.table_name,
    tc.constraint_name,
    'Consider removing if causing registration issues' as recommendation
FROM information_schema.table_constraints tc
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_name IN ('profiles', 'user_limits', 'subscription_usage')
ORDER BY tc.table_name;

-- =============================================
-- MERGE USER_LIMITS INTO PROFILES
-- =============================================

-- Add user limits columns to profiles table
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS ai_tokens_used integer DEFAULT 0,
ADD COLUMN IF NOT EXISTS ai_tokens_limit integer DEFAULT 500,
ADD COLUMN IF NOT EXISTS csv_exports_used integer DEFAULT 0,
ADD COLUMN IF NOT EXISTS csv_exports_limit integer DEFAULT 10,
ADD COLUMN IF NOT EXISTS leads_limit integer DEFAULT 10,
ADD COLUMN IF NOT EXISTS team_members_limit integer DEFAULT 1;

-- Migrate data from user_limits to profiles
UPDATE profiles 
SET 
    ai_tokens_used = ul.ai_tokens_used,
    ai_tokens_limit = ul.ai_tokens_limit,
    csv_exports_used = ul.csv_exports_used,
    csv_exports_limit = ul.csv_exports_limit,
    leads_limit = ul.leads_limit,
    team_members_limit = ul.team_members
FROM user_limits ul 
WHERE profiles.id = ul.user_id;

-- Drop user_limits table after migration
-- DROP TABLE IF EXISTS user_limits CASCADE;