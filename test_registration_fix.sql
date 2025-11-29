-- 🧪 REGISTRATION TEST - Run this after the cleanup
-- This will test if registration constraints are fixed

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
    'test-registration@example.com',
    'Test Registration User',
    'free',
    true,
    now(),
    now() + interval '7 days'
);

-- Verify the test worked
SELECT 
    id,
    email,
    full_name,
    subscription_tier,
    trial_active,
    trial_started_at,
    trial_expires_at,
    created_at
FROM profiles 
WHERE email = 'test-registration@example.com';

-- Clean up the test record
DELETE FROM profiles WHERE email = 'test-registration@example.com';

-- Confirm cleanup
SELECT COUNT(*) as remaining_test_records 
FROM profiles 
WHERE email = 'test-registration@example.com';