-- Run this FIRST in Supabase SQL Editor to enable extensions
-- If you get permission errors, that's okay - the tables will still work

-- Enable UUID extension (usually already enabled in Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable CITEXT extension for case-insensitive text (optional)
-- If this fails, the tables use regular TEXT instead
CREATE EXTENSION IF NOT EXISTS "citext";

-- Check if extensions are enabled
SELECT 
    extname as extension_name,
    extversion as version
FROM pg_extension 
WHERE extname IN ('uuid-ossp', 'citext');

-- If citext is enabled, you can optionally update the email column:
-- ALTER TABLE public.investors ALTER COLUMN email TYPE CITEXT;