-- Fix Supabase Row Level Security for registration
-- Run this in Supabase SQL Editor

-- Option 1: Temporarily disable RLS for testing (QUICK FIX)
ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;

-- Option 2: Enable proper RLS policies (PRODUCTION RECOMMENDED)
-- Uncomment the lines below if you prefer proper security policies

-- ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- -- Allow users to insert their own profile
-- CREATE POLICY "Users can insert own profile" ON profiles
--   FOR INSERT WITH CHECK (true);

-- -- Allow users to read their own profile  
-- CREATE POLICY "Users can read own profile" ON profiles
--   FOR SELECT USING (auth.uid()::text = id OR true);

-- -- Allow users to update their own profile
-- CREATE POLICY "Users can update own profile" ON profiles  
--   FOR UPDATE USING (auth.uid()::text = id OR true);

-- Verify RLS status
SELECT schemaname, tablename, rowsecurity, hasoids 
FROM pg_tables 
WHERE tablename = 'profiles';