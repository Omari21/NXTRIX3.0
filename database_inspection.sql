-- NXTRIX CRM Database Schema Inspection
-- Copy and paste these commands into your Supabase SQL Editor

-- 1. Show all tables in your database
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- 2. Show detailed structure of all your tables
SELECT 
    t.table_name,
    c.column_name,
    c.data_type,
    c.character_maximum_length,
    c.is_nullable,
    c.column_default,
    CASE 
        WHEN pk.column_name IS NOT NULL THEN 'PRIMARY KEY'
        WHEN fk.column_name IS NOT NULL THEN 'FOREIGN KEY'
        ELSE ''
    END as key_type
FROM information_schema.tables t
LEFT JOIN information_schema.columns c ON t.table_name = c.table_name
LEFT JOIN information_schema.table_constraints tc ON t.table_name = tc.table_name AND tc.constraint_type = 'PRIMARY KEY'
LEFT JOIN information_schema.key_column_usage pk ON tc.constraint_name = pk.constraint_name AND c.column_name = pk.column_name
LEFT JOIN information_schema.key_column_usage fk ON c.table_name = fk.table_name AND c.column_name = fk.column_name
WHERE t.table_schema = 'public' 
    AND t.table_type = 'BASE TABLE'
ORDER BY t.table_name, c.ordinal_position;

-- 3. Show all constraints (Primary Keys, Foreign Keys, etc.)
SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
LEFT JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
WHERE tc.table_schema = 'public'
ORDER BY tc.table_name, tc.constraint_type;

-- 4. Check if specific NXTRIX tables exist
SELECT 
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
         ELSE '❌ investors table missing' END as investors_status;

-- 5. Count records in each table (if tables exist)
DO $$
DECLARE
    table_name text;
    query text;
    result integer;
BEGIN
    FOR table_name IN 
        SELECT t.table_name 
        FROM information_schema.tables t 
        WHERE t.table_schema = 'public' AND t.table_type = 'BASE TABLE'
    LOOP
        query := 'SELECT COUNT(*) FROM ' || table_name;
        EXECUTE query INTO result;
        RAISE NOTICE 'Table %: % records', table_name, result;
    END LOOP;
END $$;

-- 6. Show your specific NXTRIX schema details
SELECT 
    'NXTRIX Database Analysis' as analysis_type,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public') as total_tables,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'public') as total_columns,
    (SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_schema = 'public') as total_constraints;