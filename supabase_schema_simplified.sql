# NXTRIX CRM - Supabase Database Schema (Simplified)
# Run these SQL commands in your Supabase SQL editor step by step

-- Step 1: Create the main users table
CREATE TABLE IF NOT EXISTS public.users (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company VARCHAR(255),
    phone VARCHAR(20),
    user_tier VARCHAR(20) DEFAULT 'free',
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    subscription_status VARCHAR(20) DEFAULT 'active',
    stripe_customer_id VARCHAR(255),
    trial_ends_at TIMESTAMP WITH TIME ZONE
);

-- Step 2: Create deals table
CREATE TABLE IF NOT EXISTS public.deals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    property_type VARCHAR(100),
    address TEXT,
    value DECIMAL(15,2),
    stage VARCHAR(50) DEFAULT 'prospect',
    probability INTEGER DEFAULT 50,
    expected_close_date DATE,
    actual_close_date DATE,
    source VARCHAR(100),
    tags TEXT[],
    notes TEXT,
    documents JSONB DEFAULT '[]',
    financial_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 3: Create clients table
CREATE TABLE IF NOT EXISTS public.clients (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    company VARCHAR(255),
    client_type VARCHAR(50) DEFAULT 'individual',
    status VARCHAR(50) DEFAULT 'prospect',
    portfolio_value DECIMAL(15,2),
    risk_profile VARCHAR(20),
    investment_preferences TEXT[],
    address TEXT,
    notes TEXT,
    tags TEXT[],
    last_contact DATE,
    next_followup DATE,
    lead_score INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 4: Create communications table
CREATE TABLE IF NOT EXISTS public.communications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    client_id UUID REFERENCES public.clients(id) ON DELETE CASCADE,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    comm_type VARCHAR(20) NOT NULL,
    subject VARCHAR(255),
    content TEXT,
    direction VARCHAR(10),
    status VARCHAR(20) DEFAULT 'completed',
    scheduled_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER,
    outcome TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    attachments JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 5: Create tasks table
CREATE TABLE IF NOT EXISTS public.tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    client_id UUID REFERENCES public.clients(id) ON DELETE CASCADE,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(10) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'pending',
    due_date DATE,
    completed_at TIMESTAMP WITH TIME ZONE,
    estimated_hours DECIMAL(4,2),
    actual_hours DECIMAL(4,2),
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 6: Enable Row Level Security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.communications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;

-- Step 7: Create RLS policies for users table
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
CREATE POLICY "Users can view own profile" ON public.users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.users FOR UPDATE USING (auth.uid() = id);

-- Step 8: Create RLS policies for deals table
DROP POLICY IF EXISTS "Users can view own deals" ON public.deals;
DROP POLICY IF EXISTS "Users can insert own deals" ON public.deals;
DROP POLICY IF EXISTS "Users can update own deals" ON public.deals;
DROP POLICY IF EXISTS "Users can delete own deals" ON public.deals;
CREATE POLICY "Users can view own deals" ON public.deals FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own deals" ON public.deals FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own deals" ON public.deals FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own deals" ON public.deals FOR DELETE USING (auth.uid() = user_id);

-- Step 9: Create RLS policies for clients table
DROP POLICY IF EXISTS "Users can view own clients" ON public.clients;
DROP POLICY IF EXISTS "Users can insert own clients" ON public.clients;
DROP POLICY IF EXISTS "Users can update own clients" ON public.clients;
DROP POLICY IF EXISTS "Users can delete own clients" ON public.clients;
CREATE POLICY "Users can view own clients" ON public.clients FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own clients" ON public.clients FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own clients" ON public.clients FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own clients" ON public.clients FOR DELETE USING (auth.uid() = user_id);

-- Step 10: Create RLS policies for communications table
DROP POLICY IF EXISTS "Users can view own communications" ON public.communications;
DROP POLICY IF EXISTS "Users can insert own communications" ON public.communications;
DROP POLICY IF EXISTS "Users can update own communications" ON public.communications;
DROP POLICY IF EXISTS "Users can delete own communications" ON public.communications;
CREATE POLICY "Users can view own communications" ON public.communications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own communications" ON public.communications FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own communications" ON public.communications FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own communications" ON public.communications FOR DELETE USING (auth.uid() = user_id);

-- Step 11: Create RLS policies for tasks table
DROP POLICY IF EXISTS "Users can view own tasks" ON public.tasks;
DROP POLICY IF EXISTS "Users can insert own tasks" ON public.tasks;
DROP POLICY IF EXISTS "Users can update own tasks" ON public.tasks;
DROP POLICY IF EXISTS "Users can delete own tasks" ON public.tasks;
CREATE POLICY "Users can view own tasks" ON public.tasks FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own tasks" ON public.tasks FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own tasks" ON public.tasks FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own tasks" ON public.tasks FOR DELETE USING (auth.uid() = user_id);

-- Step 12: Create function to handle new user registration
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, created_at)
    VALUES (NEW.id, NEW.email, NEW.created_at);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 13: Create trigger for automatic user profile creation
-- Drop existing trigger if it exists, then recreate
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Step 14: Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_deals_user_id ON public.deals(user_id);
CREATE INDEX IF NOT EXISTS idx_deals_stage ON public.deals(stage);
CREATE INDEX IF NOT EXISTS idx_clients_user_id ON public.clients(user_id);
CREATE INDEX IF NOT EXISTS idx_communications_user_id ON public.communications(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON public.tasks(user_id);

-- Step 15: Insert demo users (optional - for testing)
-- Note: These will only work if you create auth users first
-- You can skip this step and create users through your app instead

/*
INSERT INTO auth.users (id, email, encrypted_password, email_confirmed_at, created_at, updated_at)
VALUES 
    ('00000000-0000-0000-0000-000000000001', 'demo@nxtrix.com', crypt('demo123', gen_salt('bf')), NOW(), NOW(), NOW()),
    ('00000000-0000-0000-0000-000000000002', 'admin@nxtrix.com', crypt('admin123', gen_salt('bf')), NOW(), NOW(), NOW())
ON CONFLICT (id) DO NOTHING;
*/

-- Alternative: Just create the profile records and let users register normally
INSERT INTO public.users (id, email, first_name, last_name, company, user_tier, is_admin) 
VALUES 
    ('00000000-0000-0000-0000-000000000001', 'demo@nxtrix.com', 'Demo', 'User', 'NXTRIX Demo', 'professional', FALSE),
    ('00000000-0000-0000-0000-000000000002', 'admin@nxtrix.com', 'Admin', 'User', 'NXTRIX', 'enterprise', TRUE)
ON CONFLICT (id) DO NOTHING;