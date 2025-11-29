-- NXTRIX CRM - COMPLETE DATABASE SCHEMA EXPORT
-- This will show everything in a readable format for analysis
-- Copy and paste ALL results from this query

-- ========================================
-- COMPLETE SCHEMA ANALYSIS FOR NXTRIX CRM
-- ========================================

-- 1. EXECUTIVE SUMMARY
SELECT 
    '🏢 NXTRIX CRM DATABASE OVERVIEW' as section,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public') as total_tables,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'public') as total_columns,
    (SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_schema = 'public') as total_constraints,
    CURRENT_TIMESTAMP as analysis_time;

-- 2. ALL TABLES LIST
SELECT 
    '📋 TABLE INVENTORY' as section,
    ROW_NUMBER() OVER (ORDER BY table_name) as table_number,
    table_name,
    table_type,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name AND table_schema = 'public') as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- 3. COMPLETE TABLE STRUCTURES
SELECT 
    '🔍 DETAILED TABLE STRUCTURES' as section,
    t.table_name,
    c.ordinal_position as col_position,
    c.column_name,
    c.data_type,
    COALESCE(c.character_maximum_length::text, c.numeric_precision::text, '') as max_length,
    c.is_nullable,
    COALESCE(c.column_default, 'NULL') as default_value,
    CASE 
        WHEN pk.column_name IS NOT NULL THEN '🔑 PRIMARY KEY'
        WHEN fk.column_name IS NOT NULL THEN '🔗 FOREIGN KEY'
        ELSE ''
    END as key_type
FROM information_schema.tables t
JOIN information_schema.columns c ON t.table_name = c.table_name AND c.table_schema = 'public'
LEFT JOIN (
    SELECT DISTINCT
        kcu.table_name,
        kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
    WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema = 'public'
) pk ON c.table_name = pk.table_name AND c.column_name = pk.column_name
LEFT JOIN (
    SELECT DISTINCT
        kcu.table_name,
        kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
) fk ON c.table_name = fk.table_name AND c.column_name = fk.column_name
WHERE t.table_schema = 'public' AND t.table_type = 'BASE TABLE'
ORDER BY t.table_name, c.ordinal_position;

-- 4. ALL RELATIONSHIPS AND CONSTRAINTS
SELECT 
    '🔗 RELATIONSHIPS & CONSTRAINTS' as section,
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) as columns,
    COALESCE(ccu.table_name, '') as references_table,
    COALESCE(ccu.column_name, '') as references_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
LEFT JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
WHERE tc.table_schema = 'public'
GROUP BY tc.table_name, tc.constraint_name, tc.constraint_type, ccu.table_name, ccu.column_name
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;

-- 5. NXTRIX SPECIFIC TABLES CHECK
SELECT 
    '✅ NXTRIX CORE TABLES STATUS' as section,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users' AND table_schema = 'public') 
         THEN '✅ users table exists' 
         ELSE '❌ users table missing' END as users_status,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'deals' AND table_schema = 'public') 
         THEN '✅ deals table exists' 
         ELSE '❌ deals table missing' END as deals_status,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'clients' AND table_schema = 'public') 
         THEN '✅ clients table exists' 
         ELSE '❌ clients table missing' END as clients_status,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'investors' AND table_schema = 'public') 
         THEN '✅ investors table exists' 
         ELSE '❌ investors table missing' END as investors_status,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'leads' AND table_schema = 'public') 
         THEN '✅ leads table exists' 
         ELSE '❌ leads table missing' END as leads_status,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'portfolios' AND table_schema = 'public') 
         THEN '✅ portfolios table exists' 
         ELSE '❌ portfolios table missing' END as portfolios_status;

-- 6. AUTHENTICATION RELATED TABLES
SELECT 
    '🔐 AUTHENTICATION TABLES' as section,
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name AND table_schema = 'public') as columns,
    CASE WHEN table_name LIKE '%auth%' OR table_name LIKE '%user%' OR table_name LIKE '%profile%' 
         THEN '🔐 Authentication Related' 
         ELSE '📊 Business Data' END as table_type
FROM information_schema.tables t
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND (table_name LIKE '%auth%' OR table_name LIKE '%user%' OR table_name LIKE '%profile%' OR table_name LIKE '%session%')
ORDER BY table_name;

-- 7. RECORD COUNTS (if you want to see data volume)
SELECT 
    '📊 DATA VOLUME ANALYSIS' as section,
    'Run individually to see record counts' as instruction,
    'SELECT table_name, (xpath(''//row/c/text()'', query_to_xml(format(''SELECT COUNT(*) as c FROM %I'', table_name), false, true, '''')))[1]::text::int AS row_count FROM information_schema.tables WHERE table_schema = ''public'' AND table_type = ''BASE TABLE'';' as query_to_run;

-- 8. INDEXES ANALYSIS
SELECT 
    '⚡ INDEXES ANALYSIS' as section,
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename, indexname;