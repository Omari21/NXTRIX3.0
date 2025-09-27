-- SIMPLE TABLE STRUCTURE BACKUP
-- Copy this into Supabase SQL Editor to see your current database structure
-- Run each section separately to get organized output

-- =====================================
-- 1. LIST ALL YOUR CURRENT TABLES
-- =====================================
SELECT 
    tablename as "Table Name",
    tableowner as "Owner"
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- =====================================  
-- 2. DETAILED COLUMN INFORMATION
-- =====================================
SELECT 
    table_name as "Table",
    column_name as "Column", 
    data_type as "Data Type",
    character_maximum_length as "Max Length",
    is_nullable as "Nullable",
    column_default as "Default Value"
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

-- =====================================
-- 3. FOREIGN KEY RELATIONSHIPS  
-- =====================================
SELECT
    tc.table_name as "Table", 
    kcu.column_name as "Column", 
    ccu.table_name as "References Table",
    ccu.column_name as "References Column"
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_schema = 'public'
ORDER BY tc.table_name;

-- =====================================
-- 4. INDEXES ON YOUR TABLES
-- =====================================
SELECT
    tablename as "Table",
    indexname as "Index Name", 
    indexdef as "Index Definition"
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- =====================================
-- 5. ROW LEVEL SECURITY POLICIES
-- =====================================
SELECT 
    tablename as "Table",
    policyname as "Policy Name",
    cmd as "Command",
    roles as "Roles"
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- =====================================
-- 6. RECORD COUNTS (OPTIONAL)
-- Uncomment lines below to see how much data you have
-- =====================================

/*
-- Check if standard CRM tables exist and count records
SELECT 'profiles' as table_name, 
       CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'profiles' AND table_schema = 'public')
            THEN (SELECT COUNT(*)::text FROM public.profiles)
            ELSE 'Table does not exist'
       END as record_count
UNION ALL
SELECT 'deals' as table_name,
       CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'deals' AND table_schema = 'public')
            THEN (SELECT COUNT(*)::text FROM public.deals)
            ELSE 'Table does not exist'
       END as record_count
UNION ALL  
SELECT 'investors' as table_name,
       CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'investors' AND table_schema = 'public')
            THEN (SELECT COUNT(*)::text FROM public.investors)
            ELSE 'Table does not exist'
       END as record_count
ORDER BY table_name;
*/