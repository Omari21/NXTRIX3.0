-- 🔍 NXTRIX COMPREHENSIVE DATABASE AUDIT
-- Run each section separately in Supabase SQL Editor
-- This will show EVERYTHING and identify conflicts/redundancies

-- =============================================
-- 📋 SECTION 1: ALL TABLES OVERVIEW
-- =============================================
SELECT 
    'TABLE INVENTORY' as audit_section,
    ROW_NUMBER() OVER (ORDER BY table_name) as num,
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns 
     WHERE table_name = t.table_name AND table_schema = 'public') as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- =============================================
-- 🔍 SECTION 2: ALL COLUMNS FOR ALL TABLES
-- =============================================
SELECT 
    'COMPLETE COLUMN INVENTORY' as audit_section,
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default,
    ordinal_position
FROM information_schema.columns 
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

-- =============================================
-- ⚠️ SECTION 3: POTENTIAL DUPLICATE TABLES
-- =============================================
SELECT 
    'POTENTIAL DUPLICATES' as audit_section,
    table_name,
    'Check for redundancy' as note
FROM information_schema.tables
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
AND (
    table_name LIKE '%user%' OR
    table_name LIKE '%profile%' OR
    table_name LIKE '%deal%' OR
    table_name LIKE '%lead%' OR
    table_name LIKE '%subscription%' OR
    table_name LIKE '%auth%'
)
ORDER BY table_name;

-- =============================================
-- 🔗 SECTION 4: ALL FOREIGN KEY RELATIONSHIPS
-- =============================================
SELECT 
    'FOREIGN KEY RELATIONSHIPS' as audit_section,
    tc.table_name as source_table,
    kcu.column_name as source_column,
    ccu.table_name as target_table,
    ccu.column_name as target_column,
    tc.constraint_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu 
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_schema = 'public'
ORDER BY tc.table_name;

-- =============================================
-- 🔒 SECTION 5: ALL CONSTRAINTS
-- =============================================
SELECT 
    'ALL CONSTRAINTS' as audit_section,
    table_name,
    constraint_name,
    constraint_type
FROM information_schema.table_constraints
WHERE table_schema = 'public'
ORDER BY table_name, constraint_type;

-- =============================================
-- 🛡️ SECTION 6: ROW LEVEL SECURITY STATUS
-- =============================================
SELECT 
    'RLS STATUS' as audit_section,
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- =============================================
-- 🔍 SECTION 7: AUTHENTICATION TABLES FOCUS
-- =============================================
SELECT 
    'AUTH TABLES ANALYSIS' as audit_section,
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public'
AND table_name IN ('profiles', 'users', 'user_profiles', 'auth_users')
ORDER BY table_name, ordinal_position;

-- =============================================
-- 🔍 SECTION 8: TRIAL SYSTEM COLUMNS CHECK
-- =============================================
SELECT 
    'TRIAL SYSTEM STATUS' as audit_section,
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public'
AND column_name IN ('trial_active', 'trial_started_at', 'trial_expires_at', 'subscription_tier', 'subscription_status')
ORDER BY table_name, column_name;

-- =============================================
-- 🔍 SECTION 9: CRITICAL COLUMNS MISSING CHECK
-- =============================================
SELECT 
    'MISSING CRITICAL COLUMNS' as audit_section,
    'profiles' as table_name,
    CASE 
        WHEN NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'profiles' AND column_name = 'trial_active')
        THEN 'MISSING: trial_active column'
        ELSE 'EXISTS: trial_active'
    END as trial_active_status,
    CASE 
        WHEN NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'profiles' AND column_name = 'trial_started_at')
        THEN 'MISSING: trial_started_at column'
        ELSE 'EXISTS: trial_started_at'
    END as trial_started_status,
    CASE 
        WHEN NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'profiles' AND column_name = 'trial_expires_at')
        THEN 'MISSING: trial_expires_at column'
        ELSE 'EXISTS: trial_expires_at'
    END as trial_expires_status;

-- =============================================
-- 📊 SECTION 10: PRODUCTION READINESS SUMMARY
-- =============================================
SELECT 
    'PRODUCTION READINESS' as audit_section,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public') as total_tables,
    (SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_schema = 'public') as total_constraints,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'profiles' AND table_schema = 'public')
        THEN 'YES'
        ELSE 'NO'
    END as has_profiles_table,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'profiles' AND column_name = 'trial_active')
        THEN 'YES'
        ELSE 'NO'
    END as has_trial_system;