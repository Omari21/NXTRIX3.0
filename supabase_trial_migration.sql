-- Add trial system columns to profiles table
-- Run this in Supabase SQL Editor

ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS trial_active BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS trial_started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS trial_expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days');

-- Update existing users to have trial data
UPDATE profiles 
SET trial_active = true,
    trial_started_at = created_at,
    trial_expires_at = created_at + INTERVAL '7 days'
WHERE trial_active IS NULL;

-- Verify the changes
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'profiles' 
AND column_name IN ('trial_active', 'trial_started_at', 'trial_expires_at');