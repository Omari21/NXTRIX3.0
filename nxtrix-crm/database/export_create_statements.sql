-- EXPORT CURRENT TABLE STRUCTURE
-- This will show you the exact CREATE TABLE statements for your current database
-- Copy and paste this into Supabase SQL Editor, then save the output

-- Get table creation info for profiles table
SELECT 
  'CREATE TABLE public.profiles (' ||
  string_agg(
    '    ' || column_name || ' ' || 
    CASE 
      WHEN data_type = 'character varying' THEN 
        CASE WHEN character_maximum_length IS NOT NULL 
             THEN 'VARCHAR(' || character_maximum_length || ')'
             ELSE 'TEXT' 
        END
      WHEN data_type = 'timestamp with time zone' THEN 'TIMESTAMP WITH TIME ZONE'
      WHEN data_type = 'uuid' THEN 'UUID'
      WHEN data_type = 'boolean' THEN 'BOOLEAN'
      WHEN data_type = 'integer' THEN 'INTEGER'
      WHEN data_type = 'numeric' THEN 'DECIMAL'
      WHEN data_type = 'jsonb' THEN 'JSONB'
      ELSE UPPER(data_type)
    END ||
    CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
    CASE WHEN column_default IS NOT NULL THEN ' DEFAULT ' || column_default ELSE '' END,
    ',' || chr(10)
    ORDER BY ordinal_position
  ) || chr(10) || ');' as create_statement
FROM information_schema.columns 
WHERE table_schema = 'public' AND table_name = 'profiles'
GROUP BY table_name;

-- Get table creation info for deals table  
SELECT 
  'CREATE TABLE public.deals (' ||
  string_agg(
    '    ' || column_name || ' ' || 
    CASE 
      WHEN data_type = 'character varying' THEN 
        CASE WHEN character_maximum_length IS NOT NULL 
             THEN 'VARCHAR(' || character_maximum_length || ')'
             ELSE 'TEXT' 
        END
      WHEN data_type = 'timestamp with time zone' THEN 'TIMESTAMP WITH TIME ZONE'
      WHEN data_type = 'uuid' THEN 'UUID'
      WHEN data_type = 'boolean' THEN 'BOOLEAN'
      WHEN data_type = 'integer' THEN 'INTEGER'
      WHEN data_type = 'numeric' THEN 'DECIMAL'
      WHEN data_type = 'jsonb' THEN 'JSONB'
      ELSE UPPER(data_type)
    END ||
    CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
    CASE WHEN column_default IS NOT NULL THEN ' DEFAULT ' || column_default ELSE '' END,
    ',' || chr(10)
    ORDER BY ordinal_position
  ) || chr(10) || ');' as create_statement
FROM information_schema.columns 
WHERE table_schema = 'public' AND table_name = 'deals'
GROUP BY table_name;

-- Get table creation info for investors table
SELECT 
  'CREATE TABLE public.investors (' ||
  string_agg(
    '    ' || column_name || ' ' || 
    CASE 
      WHEN data_type = 'character varying' THEN 
        CASE WHEN character_maximum_length IS NOT NULL 
             THEN 'VARCHAR(' || character_maximum_length || ')'
             ELSE 'TEXT' 
        END
      WHEN data_type = 'timestamp with time zone' THEN 'TIMESTAMP WITH TIME ZONE'
      WHEN data_type = 'uuid' THEN 'UUID'
      WHEN data_type = 'boolean' THEN 'BOOLEAN'
      WHEN data_type = 'integer' THEN 'INTEGER'
      WHEN data_type = 'numeric' THEN 'DECIMAL'
      WHEN data_type = 'jsonb' THEN 'JSONB'
      ELSE UPPER(data_type)
    END ||
    CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
    CASE WHEN column_default IS NOT NULL THEN ' DEFAULT ' || column_default ELSE '' END,
    ',' || chr(10)
    ORDER BY ordinal_position
  ) || chr(10) || ');' as create_statement
FROM information_schema.columns 
WHERE table_schema = 'public' AND table_name = 'investors'
GROUP BY table_name;

-- Show all table names so you can generate CREATE statements for any others
SELECT 'Tables you currently have:' as info;
SELECT '-- ' || tablename as table_list
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;