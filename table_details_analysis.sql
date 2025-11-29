-- NXTRIX CRM - Get Complete Table Details
-- Run this to see all table structures and key information

-- 1. Show all your tables with column counts
SELECT 
    '📋 YOUR COMPLETE TABLE INVENTORY' as section,
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name AND table_schema = 'public') as columns
FROM information_schema.tables t
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- 2. Check your core NXTRIX tables status
SELECT 
    '✅ NXTRIX CORE TABLES STATUS' as section,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'profiles' AND table_schema = 'public') 
         THEN '✅ profiles table exists' 
         ELSE '❌ profiles table missing' END as profiles_status,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'deals' AND table_schema = 'public') 
         THEN '✅ deals table exists' 
         ELSE '❌ deals table missing' END as deals_status,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'investors' AND table_schema = 'public') 
         THEN '✅ investors table exists' 
         ELSE '❌ investors table missing' END as investors_status,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'buyer_leads' AND table_schema = 'public') 
         THEN '✅ buyer_leads table exists' 
         ELSE '❌ buyer_leads table missing' END as buyer_leads_status,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'seller_leads' AND table_schema = 'public') 
         THEN '✅ seller_leads table exists' 
         ELSE '❌ seller_leads table missing' END as seller_leads_status;

-- 3. Show your authentication/user management structure
SELECT 
    '🔐 AUTHENTICATION STRUCTURE' as section,
    c.table_name,
    c.column_name,
    c.data_type,
    c.is_nullable,
    c.column_default
FROM information_schema.columns c
WHERE c.table_schema = 'public' 
    AND c.table_name IN ('profiles', 'user_profiles', 'users')
ORDER BY c.table_name, c.ordinal_position;

-- 4. Show your deals table structure (critical for CRM)
SELECT 
    '💼 DEALS TABLE STRUCTURE' as section,
    c.column_name,
    c.data_type,
    COALESCE(c.character_maximum_length::text, c.numeric_precision::text, '') as max_length,
    c.is_nullable,
    c.column_default
FROM information_schema.columns c
WHERE c.table_schema = 'public' AND c.table_name = 'deals'
ORDER BY c.ordinal_position;

-- 5. Show your leads management structure
SELECT 
    '🎯 LEADS MANAGEMENT STRUCTURE' as section,
    c.table_name,
    c.column_name,
    c.data_type,
    c.is_nullable
FROM information_schema.columns c
WHERE c.table_schema = 'public' 
    AND c.table_name IN ('buyer_leads', 'seller_leads', 'lead_tasks', 'lead_score_history')
ORDER BY c.table_name, c.ordinal_position;

-- 6. Check if you have any data in key tables
SELECT 
    '📊 DATA CHECK' as section,
    'Run these queries individually to check data:' as note,
    'SELECT COUNT(*) as profile_count FROM profiles;' as profiles_query,
    'SELECT COUNT(*) as deals_count FROM deals;' as deals_query,
    'SELECT COUNT(*) as buyer_leads_count FROM buyer_leads;' as buyer_leads_query,
    'SELECT COUNT(*) as seller_leads_count FROM seller_leads;' as seller_leads_query;