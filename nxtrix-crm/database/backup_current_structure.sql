-- SUPABASE TABLE STRUCTURE BACKUP SCRIPT
-- Copy and paste this into your Supabase SQL Editor to see your current table structure
-- This will show you all tables, columns, and constraints currently in your database

-- =====================================
-- SHOW ALL CURRENT TABLES
-- =====================================
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- =====================================
-- SHOW ALL COLUMNS FOR EACH TABLE
-- =====================================
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default,
    character_maximum_length
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

-- =====================================
-- SHOW ALL FOREIGN KEY CONSTRAINTS
-- =====================================
SELECT
    tc.table_name, 
    kcu.column_name, 
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
    AND tc.table_schema = 'public';

-- =====================================
-- SHOW ALL INDEXES
-- =====================================
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- =====================================
-- SHOW ALL TRIGGERS
-- =====================================
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;

-- =====================================
-- SHOW ROW LEVEL SECURITY POLICIES
-- =====================================
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- =====================================
-- COUNT RECORDS IN EACH TABLE
-- =====================================
-- Note: This will show you how much data you have in each table
-- Uncomment the lines below if you want to see record counts

/*
SELECT 'profiles' as table_name, COUNT(*) as record_count FROM public.profiles
UNION ALL
SELECT 'deals' as table_name, COUNT(*) as record_count FROM public.deals
UNION ALL
SELECT 'investors' as table_name, COUNT(*) as record_count FROM public.investors
UNION ALL
SELECT 'deal_scores' as table_name, COUNT(*) as record_count FROM public.deal_scores
UNION ALL
SELECT 'deal_notifications' as table_name, COUNT(*) as record_count FROM public.deal_notifications
UNION ALL
SELECT 'portfolios' as table_name, COUNT(*) as record_count FROM public.portfolios
UNION ALL
SELECT 'portfolio_deals' as table_name, COUNT(*) as record_count FROM public.portfolio_deals
UNION ALL
SELECT 'market_data' as table_name, COUNT(*) as record_count FROM public.market_data
ORDER BY table_name;
*/