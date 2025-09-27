-- GENERATE COMPLETE TABLE STRUCTURE BACKUP
-- Copy and paste this into Supabase SQL Editor to get CREATE TABLE statements for all your current tables
-- This will generate the exact SQL needed to recreate your current database structure

-- Function to generate CREATE TABLE statements
DO $$
DECLARE
    table_record RECORD;
    column_record RECORD;
    constraint_record RECORD;
    create_statement TEXT;
BEGIN
    -- Loop through all tables in public schema
    FOR table_record IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
    LOOP
        -- Start CREATE TABLE statement
        create_statement := 'CREATE TABLE IF NOT EXISTS public.' || table_record.tablename || ' (' || chr(10);
        
        -- Add columns
        FOR column_record IN
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' 
                AND table_name = table_record.tablename
            ORDER BY ordinal_position
        LOOP
            create_statement := create_statement || '    ' || column_record.column_name || ' ';
            
            -- Add data type
            IF column_record.data_type = 'character varying' THEN
                IF column_record.character_maximum_length IS NOT NULL THEN
                    create_statement := create_statement || 'VARCHAR(' || column_record.character_maximum_length || ')';
                ELSE
                    create_statement := create_statement || 'TEXT';
                END IF;
            ELSIF column_record.data_type = 'character' THEN
                create_statement := create_statement || 'CHAR(' || column_record.character_maximum_length || ')';
            ELSIF column_record.data_type = 'uuid' THEN
                create_statement := create_statement || 'UUID';
            ELSIF column_record.data_type = 'timestamp with time zone' THEN
                create_statement := create_statement || 'TIMESTAMP WITH TIME ZONE';
            ELSIF column_record.data_type = 'numeric' THEN
                create_statement := create_statement || 'DECIMAL';
            ELSIF column_record.data_type = 'boolean' THEN
                create_statement := create_statement || 'BOOLEAN';
            ELSIF column_record.data_type = 'integer' THEN
                create_statement := create_statement || 'INTEGER';
            ELSIF column_record.data_type = 'jsonb' THEN
                create_statement := create_statement || 'JSONB';
            ELSE
                create_statement := create_statement || UPPER(column_record.data_type);
            END IF;
            
            -- Add NOT NULL constraint
            IF column_record.is_nullable = 'NO' THEN
                create_statement := create_statement || ' NOT NULL';
            END IF;
            
            -- Add DEFAULT value
            IF column_record.column_default IS NOT NULL THEN
                create_statement := create_statement || ' DEFAULT ' || column_record.column_default;
            END IF;
            
            create_statement := create_statement || ',' || chr(10);
        END LOOP;
        
        -- Remove last comma and add closing parenthesis
        create_statement := rtrim(create_statement, ',' || chr(10)) || chr(10) || ');' || chr(10) || chr(10);
        
        -- Output the CREATE TABLE statement
        RAISE NOTICE '%', create_statement;
    END LOOP;
END $$;