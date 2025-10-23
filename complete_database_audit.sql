-- 🔍 NXTRIX COMPREHENSIVE DATABASE AUDIT & REDUNDANCY CHECK
-- This will identify EVERYTHING: tables, conflicts, redundancies, constraints, and issues
-- Run each section separately in Supabase SQL Editor

-- =============================================
-- 📋 SECTION 1: COMPLETE TABLE INVENTORY
-- =============================================
SELECT 
    '📋 ALL TABLES IN DATABASE' as audit_section,
    ROW_NUMBER() OVER (ORDER BY table_name) as table_number,
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name AND table_schema = 'public') as column_count,
    pg_size_pretty(pg_total_relation_size(('public.' || table_name)::regclass)) as table_size,
    (SELECT COUNT(*) 
     FROM information_schema.table_constraints 
     WHERE table_name = t.table_name AND table_schema = 'public') as constraint_count,
    CASE 
        WHEN table_name IN ('profiles', 'user_profiles', 'users', 'auth_users') THEN '🔐 AUTHENTICATION'
        WHEN table_name IN ('deals', 'deal_analytics', 'deal_notifications', 'deal_workflow') THEN '💼 DEAL MANAGEMENT'
        WHEN table_name IN ('buyer_leads', 'seller_leads', 'lead_tasks', 'leads') THEN '🎯 LEAD MANAGEMENT'
        WHEN table_name IN ('investors', 'investor_clients', 'portfolio', 'portfolios') THEN '💰 INVESTMENT'
        WHEN table_name LIKE '%email%' OR table_name LIKE '%sms%' OR table_name LIKE '%communication%' THEN '📧 COMMUNICATION'
        WHEN table_name LIKE '%ai%' OR table_name LIKE '%market%' OR table_name LIKE '%analytics%' THEN '🤖 AI & ANALYTICS'
        WHEN table_name LIKE '%subscription%' OR table_name LIKE '%billing%' OR table_name LIKE '%payment%' THEN '💳 BILLING'
        WHEN table_name LIKE '%notification%' OR table_name LIKE '%alert%' THEN '🔔 NOTIFICATIONS'
        ELSE '📊 OTHER/UNKNOWN'
    END as functional_category
FROM information_schema.tables t
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY 
    CASE 
        WHEN table_name IN ('profiles', 'user_profiles', 'users', 'auth_users') THEN 1
        WHEN table_name IN ('deals', 'deal_analytics', 'deal_notifications') THEN 2
        WHEN table_name IN ('buyer_leads', 'seller_leads', 'lead_tasks') THEN 3
        WHEN table_name IN ('investors', 'investor_clients', 'portfolio') THEN 4
        ELSE 5
    END,
    table_name;

-- =============================================
-- 🔍 SECTION 2: REDUNDANCY & CONFLICT DETECTION
-- =============================================

-- Check for duplicate/similar table names
SELECT 
    '⚠️ POTENTIAL DUPLICATE TABLES' as audit_section,
    t1.table_name as table_1,
    t2.table_name as table_2,
    'Similar naming pattern - potential redundancy' as issue_type
FROM information_schema.tables t1
JOIN information_schema.tables t2 ON (
    t1.table_name != t2.table_name 
    AND t1.table_schema = 'public' 
    AND t2.table_schema = 'public'
    AND (
        -- Check for singular/plural variations
        t1.table_name = t2.table_name || 's' OR
        t2.table_name = t1.table_name || 's' OR
        -- Check for similar prefixes
        LEFT(t1.table_name, LENGTH(t1.table_name)-1) = LEFT(t2.table_name, LENGTH(t2.table_name)-1) OR
        -- Check for variations like user/users/user_profile
        (t1.table_name LIKE '%user%' AND t2.table_name LIKE '%user%') OR
        (t1.table_name LIKE '%deal%' AND t2.table_name LIKE '%deal%') OR
        (t1.table_name LIKE '%lead%' AND t2.table_name LIKE '%lead%') OR
        (t1.table_name LIKE '%subscription%' AND t2.table_name LIKE '%subscription%')
    )
)
WHERE t1.table_name < t2.table_name
ORDER BY t1.table_name;

-- Check for duplicate column patterns across tables
SELECT 
    '🔄 COLUMN REDUNDANCY CHECK' as audit_section,
    c1.table_name as table_1,
    c2.table_name as table_2,
    c1.column_name as duplicate_column,
    c1.data_type as data_type_1,
    c2.data_type as data_type_2,
    CASE 
        WHEN c1.data_type != c2.data_type THEN '⚠️ SAME COLUMN, DIFFERENT TYPES'
        ELSE 'Same column, same type'
    END as conflict_status
FROM information_schema.columns c1
JOIN information_schema.columns c2 ON (
    c1.column_name = c2.column_name 
    AND c1.table_name != c2.table_name
    AND c1.table_schema = 'public' 
    AND c2.table_schema = 'public'
    AND c1.column_name NOT IN ('id', 'created_at', 'updated_at', 'user_id') -- Exclude common columns
)
WHERE c1.table_name < c2.table_name
ORDER BY c1.column_name, c1.table_name;

-- 2. Critical Tables Status Check
SELECT 
    '✅ CORE TABLES STATUS' as section,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'profiles' AND table_schema = 'public') 
         THEN '✅ profiles (Authentication)' 
         ELSE '❌ profiles missing' END as auth_status,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'deals' AND table_schema = 'public') 
         THEN '✅ deals (CRM Core)' 
         ELSE '❌ deals missing' END as deals_status,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'buyer_leads' AND table_schema = 'public') 
         THEN '✅ buyer_leads (Lead Gen)' 
         ELSE '❌ buyer_leads missing' END as leads_status,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'subscription_usage' AND table_schema = 'public') 
         THEN '✅ subscription_usage (Billing)' 
         ELSE '❌ subscription_usage missing' END as billing_status;

-- 3. Authentication Table Structure (CRITICAL)
WITH auth_structure AS (
    SELECT 
        '🔐 AUTHENTICATION STRUCTURE' as section,
        c.table_name,
        c.ordinal_position as pos,
        c.column_name,
        c.data_type,
        COALESCE(c.character_maximum_length::text, '') as max_length,
        c.is_nullable,
        COALESCE(c.column_default, 'NULL') as default_value,
        CASE 
            WHEN c.column_name LIKE '%password%' THEN '🔒 PASSWORD FIELD'
            WHEN c.column_name LIKE '%email%' THEN '📧 EMAIL FIELD'
            WHEN c.column_name LIKE '%tier%' OR c.column_name LIKE '%subscription%' THEN '💳 SUBSCRIPTION FIELD'
            WHEN c.column_name = 'id' THEN '🔑 PRIMARY KEY'
            ELSE ''
        END as field_type
    FROM information_schema.columns c
    WHERE c.table_schema = 'public' 
        AND c.table_name IN ('profiles', 'user_profiles', 'users')
)
SELECT * FROM auth_structure ORDER BY table_name, pos;

-- 4. Deals Table Structure (BUSINESS CRITICAL)
WITH deals_structure AS (
    SELECT 
        '💼 DEALS TABLE STRUCTURE' as section,
        c.ordinal_position as pos,
        c.column_name,
        c.data_type,
        COALESCE(c.character_maximum_length::text, c.numeric_precision::text, '') as max_length,
        c.is_nullable,
        COALESCE(c.column_default, 'NULL') as default_value,
        CASE 
            WHEN c.column_name LIKE '%user_id%' THEN '👤 USER REFERENCE'
            WHEN c.column_name LIKE '%price%' OR c.column_name LIKE '%value%' THEN '💰 FINANCIAL'
            WHEN c.column_name LIKE '%ai%' OR c.column_name LIKE '%score%' THEN '🤖 AI FEATURES'
            WHEN c.column_name = 'id' THEN '🔑 PRIMARY KEY'
            ELSE ''
        END as field_type
    FROM information_schema.columns c
    WHERE c.table_schema = 'public' AND c.table_name = 'deals'
)
SELECT * FROM deals_structure ORDER BY pos;

-- 5. Data Volume Check
WITH data_counts AS (
    SELECT 
        '📊 DATA VOLUME ANALYSIS' as section,
        'profiles' as table_name,
        (SELECT COUNT(*) FROM profiles) as record_count,
        '🔐 User Accounts' as description
    UNION ALL
    SELECT 
        '📊 DATA VOLUME ANALYSIS',
        'deals',
        (SELECT COUNT(*) FROM deals),
        '💼 Business Deals'
    UNION ALL
    SELECT 
        '📊 DATA VOLUME ANALYSIS',
        'buyer_leads',
        (SELECT COUNT(*) FROM buyer_leads),
        '🎯 Buyer Leads'
    UNION ALL
    SELECT 
        '📊 DATA VOLUME ANALYSIS',
        'seller_leads',
        (SELECT COUNT(*) FROM seller_leads),
        '🏠 Seller Leads'
    UNION ALL
    SELECT 
        '📊 DATA VOLUME ANALYSIS',
        'investors',
        (SELECT COUNT(*) FROM investors),
        '💰 Investor Database'
)
SELECT * FROM data_counts;

-- 6. Subscription & Billing Structure
WITH subscription_structure AS (
    SELECT 
        '💳 SUBSCRIPTION STRUCTURE' as section,
        c.table_name,
        c.column_name,
        c.data_type,
        c.is_nullable
    FROM information_schema.columns c
    WHERE c.table_schema = 'public' 
        AND (c.table_name LIKE '%subscription%' OR c.table_name LIKE '%billing%')
        AND c.table_name IN ('subscription_usage', 'subscription_limits', 'billing_history')
)
SELECT * FROM subscription_structure ORDER BY table_name, column_name;

-- 7. Production Readiness Summary
SELECT 
    '🚀 PRODUCTION READINESS SUMMARY' as section,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public') as total_tables,
    (SELECT COUNT(*) FROM profiles) as total_users,
    (SELECT COUNT(*) FROM deals) as total_deals,
    CASE 
        WHEN (SELECT COUNT(*) FROM profiles) > 0 THEN '✅ Has User Data'
        ELSE '⚠️ No User Data'
    END as user_data_status,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'profiles' AND column_name = 'password_hash') 
        THEN '✅ Password Security Ready'
        ELSE '⚠️ Check Password Security'
    END as security_status;