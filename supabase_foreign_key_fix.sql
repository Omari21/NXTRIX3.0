-- Fix foreign key constraint issue
-- Run this in Supabase SQL Editor

-- Option 1: Remove the foreign key constraint (QUICK FIX for testing)
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_id_fkey;

-- Option 2: Check what foreign keys exist
SELECT 
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
  AND tc.table_name='profiles';

-- Option 3: Alternative - Make profiles independent
-- ALTER TABLE profiles ALTER COLUMN id DROP NOT NULL;
-- ALTER TABLE profiles ALTER COLUMN id SET DEFAULT gen_random_uuid();

-- Check if there's a users table
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name = 'users';