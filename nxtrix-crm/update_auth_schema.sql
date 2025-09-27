-- =====================================
-- AUTHENTICATION SCHEMA UPDATE
-- Ensure profiles table has all needed columns for authentication
-- =====================================

-- Add missing authentication columns to profiles table
DO $$
BEGIN
    -- Add password_hash column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'password_hash') THEN
        ALTER TABLE public.profiles ADD COLUMN password_hash TEXT;
    END IF;
    
    -- Add email column if it doesn't exist (should already exist from Supabase Auth)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'email') THEN
        ALTER TABLE public.profiles ADD COLUMN email TEXT UNIQUE;
    END IF;
    
    -- Add full_name column if it doesn't exist (was causing the original error)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'full_name') THEN
        ALTER TABLE public.profiles ADD COLUMN full_name TEXT;
    END IF;
    
    -- Add company column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'company') THEN
        ALTER TABLE public.profiles ADD COLUMN company TEXT;
    END IF;
    
    -- Add phone column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'phone') THEN
        ALTER TABLE public.profiles ADD COLUMN phone TEXT;
    END IF;
    
    -- Add experience_level column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'experience_level') THEN
        ALTER TABLE public.profiles ADD COLUMN experience_level TEXT;
    END IF;
    
    -- Add investor_type column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'investor_type') THEN
        ALTER TABLE public.profiles ADD COLUMN investor_type TEXT;
    END IF;
    
    -- Add business_goals column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'business_goals') THEN
        ALTER TABLE public.profiles ADD COLUMN business_goals TEXT;
    END IF;
    
    -- Add marketing_consent column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'marketing_consent') THEN
        ALTER TABLE public.profiles ADD COLUMN marketing_consent BOOLEAN DEFAULT false;
    END IF;
    
    -- Add is_active column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'is_active') THEN
        ALTER TABLE public.profiles ADD COLUMN is_active BOOLEAN DEFAULT true;
    END IF;
    
    -- Add last_login column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'last_login') THEN
        ALTER TABLE public.profiles ADD COLUMN last_login TIMESTAMP WITH TIME ZONE;
    END IF;
    
    -- Add trial_end_date column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'trial_end_date') THEN
        ALTER TABLE public.profiles ADD COLUMN trial_end_date TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '14 days');
    END IF;
    
END $$;

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);

-- Create index on password_hash for authentication
CREATE INDEX IF NOT EXISTS idx_profiles_password_hash ON public.profiles(password_hash);

SELECT 'Authentication schema updated successfully!' as status;