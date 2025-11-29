-- Check and fix subscription tier constraint
-- Run this in Supabase SQL Editor

-- First, see what the current constraint allows
SELECT conname, consrc 
FROM pg_constraint 
WHERE conname LIKE '%subscription_tier%';

-- Check what values currently exist in the table
SELECT DISTINCT subscription_tier FROM profiles;

-- Option 1: Drop the constraint (QUICK FIX for testing)
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_subscription_tier_check;

-- Option 2: Update constraint to include 'trial' (PROPER FIX)
-- ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_subscription_tier_check;
-- ALTER TABLE profiles ADD CONSTRAINT profiles_subscription_tier_check 
--   CHECK (subscription_tier IN ('trial', 'solo', 'team', 'business'));

-- Verify constraint is removed
SELECT conname, consrc 
FROM pg_constraint 
WHERE conname LIKE '%subscription_tier%';