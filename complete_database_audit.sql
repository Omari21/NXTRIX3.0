-- NXTRIX CRM - COMPLETE DATABASE AUDIT
-- Run this single query to get EVERYTHING we need

-- 1. Complete Table Inventory
SELECT 
    '📋 COMPLETE TABLE INVENTORY' as section,
    ROW_NUMBER() OVER (ORDER BY table_name) as num,
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name AND table_schema = 'public') as columns,
    CASE 
        WHEN table_name IN ('profiles', 'user_profiles', 'users') THEN '🔐 Authentication'
        WHEN table_name IN ('deals', 'deal_analytics', 'deal_notifications') THEN '💼 Deal Management'
        WHEN table_name IN ('buyer_leads', 'seller_leads', 'lead_tasks') THEN '🎯 Lead Management'
        WHEN table_name IN ('investors', 'investor_clients', 'portfolio') THEN '💰 Investment Management'
        WHEN table_name LIKE '%email%' OR table_name LIKE '%sms%' THEN '📧 Communication'
        WHEN table_name LIKE '%ai%' OR table_name LIKE '%market%' THEN '🤖 AI & Analytics'
        WHEN table_name LIKE '%subscription%' OR table_name LIKE '%billing%' THEN '💳 Billing & Subscriptions'
        ELSE '📊 Other'
    END as category
FROM information_schema.tables t
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY 
    CASE 
        WHEN table_name IN ('profiles', 'user_profiles', 'users') THEN 1
        WHEN table_name IN ('deals', 'deal_analytics', 'deal_notifications') THEN 2
        WHEN table_name IN ('buyer_leads', 'seller_leads', 'lead_tasks') THEN 3
        WHEN table_name IN ('investors', 'investor_clients', 'portfolio') THEN 4
        ELSE 5
    END,
    table_name;

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