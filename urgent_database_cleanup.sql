-- 🚨 URGENT DATABASE CLEANUP - PHASE 1: REGISTRATION FIX
-- Run these in Supabase SQL Editor to fix registration issues

-- =============================================
-- 1. FIX FOREIGN KEY CONSTRAINT BLOCKING REGISTRATION
-- =============================================

-- Remove the foreign key constraint that requires auth.users linkage
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_id_fkey;

-- Make profiles.id independent (not requiring auth.users)
-- This allows custom registration without Supabase Auth

-- =============================================
-- 2. REMOVE REDUNDANT USER TABLES
-- =============================================

-- Drop user_profiles table (redundant with profiles)
DROP TABLE IF EXISTS user_profiles CASCADE;

-- =============================================
-- 3. CLEAN UP EXCESSIVE CONSTRAINTS
-- =============================================

-- Remove problematic subscription tier constraints
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_subscription_tier_check;
ALTER TABLE subscription_limits DROP CONSTRAINT IF EXISTS subscription_limits_tier_check;

-- Remove deal analyzer role constraint that might be too restrictive
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_deal_analyzer_role_check;

-- =============================================
-- 4. VERIFY TRIAL SYSTEM COLUMNS EXIST
-- =============================================

-- Check if trial columns were added properly
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'profiles' 
AND column_name IN ('trial_active', 'trial_started_at', 'trial_expires_at')
ORDER BY column_name;

-- =============================================
-- 5. TEST REGISTRATION COMPATIBILITY
-- =============================================

-- Test if we can insert a profile without auth.users requirement
INSERT INTO profiles (
    id, 
    email, 
    full_name, 
    subscription_tier,
    trial_active,
    trial_started_at,
    trial_expires_at
) VALUES (
    gen_random_uuid(),
    'test@example.com',
    'Test User',
    'free',
    true,
    now(),
    now() + interval '7 days'
);

-- Clean up test (remove the test record)
DELETE FROM profiles WHERE email = 'test@example.com';