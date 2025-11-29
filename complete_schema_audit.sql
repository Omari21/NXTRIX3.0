-- Complete database schema audit for NXTRIX profiles table
-- Copy and paste ALL results to show the full schema

-- 1. Show table structure
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default,
    character_maximum_length,
    numeric_precision,
    numeric_scale
FROM information_schema.columns 
WHERE table_name = 'profiles' 
ORDER BY ordinal_position;

-- 2. Show all constraints (updated query for newer PostgreSQL)
SELECT 
    conname AS constraint_name,
    contype AS constraint_type,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint 
WHERE conrelid = 'profiles'::regclass;

-- 3. Show indexes
SELECT 
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename = 'profiles';

-- 4. Show table info
SELECT 
    table_name,
    table_type,
    table_schema
FROM information_schema.tables 
WHERE table_name = 'profiles';

-- 5. Check if auth.users table exists (common Supabase setup)
SELECT 
    table_name,
    table_schema
FROM information_schema.tables 
WHERE table_name = 'users' 
   OR table_name LIKE '%user%'
ORDER BY table_schema, table_name;

-- 6. Show foreign key relationships
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name = 'profiles';

-- 7. Show Row Level Security status
SELECT 
    schemaname,
    tablename,
    rowsecurity,
    hasoids
FROM pg_tables 
WHERE tablename = 'profiles';