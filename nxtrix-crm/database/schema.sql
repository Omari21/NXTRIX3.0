-- NxTrix CRM Database Schema
-- Enterprise Real Estate Deal Analyzer

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "citext";

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email CITEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'analyst' CHECK (role IN ('admin', 'analyst', 'investor', 'agent')),
    company TEXT,
    phone TEXT,
    avatar_url TEXT,
    subscription_tier TEXT NOT NULL DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Deals table - Core deal management
CREATE TABLE IF NOT EXISTS public.deals (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    property_address TEXT NOT NULL,
    purchase_price DECIMAL(12,2) NOT NULL DEFAULT 0,
    after_repair_value DECIMAL(12,2) NOT NULL DEFAULT 0,
    repair_costs DECIMAL(12,2) NOT NULL DEFAULT 0,
    monthly_rent DECIMAL(8,2) DEFAULT 0,
    monthly_expenses DECIMAL(8,2) DEFAULT 0,
    deal_type TEXT NOT NULL CHECK (deal_type IN ('flip', 'rental', 'wholesale', 'brrrr')),
    status TEXT NOT NULL DEFAULT 'analyzing' CHECK (status IN ('analyzing', 'approved', 'rejected', 'pending')),
    roi DECIMAL(5,2) NOT NULL DEFAULT 0,
    cap_rate DECIMAL(5,2),
    cash_on_cash_return DECIMAL(5,2),
    profit_potential DECIMAL(12,2) NOT NULL DEFAULT 0,
    deal_score INTEGER NOT NULL DEFAULT 0 CHECK (deal_score >= 0 AND deal_score <= 100),
    created_by UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    assigned_to UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    property_details JSONB DEFAULT '{}',
    financial_analysis JSONB DEFAULT '{}',
    market_analysis JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Investors table - Investor profiles and buy-box criteria
CREATE TABLE IF NOT EXISTS public.investors (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    email CITEXT NOT NULL,
    phone TEXT,
    investment_criteria JSONB NOT NULL DEFAULT '{}',
    notifications_enabled BOOLEAN DEFAULT true,
    preferred_contact_method TEXT DEFAULT 'email' CHECK (preferred_contact_method IN ('email', 'sms', 'both')),
    investment_budget JSONB DEFAULT '{"min_amount": 0, "max_amount": 1000000}',
    experience_level TEXT DEFAULT 'beginner' CHECK (experience_level IN ('beginner', 'intermediate', 'expert')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Deal scores table - Detailed scoring breakdown
CREATE TABLE IF NOT EXISTS public.deal_scores (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    overall_score INTEGER NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    financial_score INTEGER NOT NULL CHECK (financial_score >= 0 AND financial_score <= 100),
    market_score INTEGER NOT NULL CHECK (market_score >= 0 AND market_score <= 100),
    risk_score INTEGER NOT NULL CHECK (risk_score >= 0 AND risk_score <= 100),
    time_sensitivity_score INTEGER NOT NULL CHECK (time_sensitivity_score >= 0 AND time_sensitivity_score <= 100),
    factors JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Deal notifications table - Track investor notifications
CREATE TABLE IF NOT EXISTS public.deal_notifications (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    investor_id UUID REFERENCES public.investors(id) ON DELETE CASCADE,
    notification_type TEXT NOT NULL CHECK (notification_type IN ('email', 'sms', 'push')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
    sent_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Portfolio tracking table
CREATE TABLE IF NOT EXISTS public.portfolios (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    total_properties INTEGER DEFAULT 0,
    total_value DECIMAL(15,2) DEFAULT 0,
    monthly_income DECIMAL(10,2) DEFAULT 0,
    monthly_expenses DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Portfolio properties junction table
CREATE TABLE IF NOT EXISTS public.portfolio_deals (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    portfolio_id UUID REFERENCES public.portfolios(id) ON DELETE CASCADE,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(portfolio_id, deal_id)
);

-- Market data table for comparable sales and trends
CREATE TABLE IF NOT EXISTS public.market_data (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    property_address TEXT NOT NULL,
    sale_price DECIMAL(12,2),
    sale_date DATE,
    square_feet INTEGER,
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    lot_size DECIMAL(10,2),
    year_built INTEGER,
    property_type TEXT,
    data_source TEXT DEFAULT 'ATTOM',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_deals_created_by ON public.deals(created_by);
CREATE INDEX IF NOT EXISTS idx_deals_status ON public.deals(status);
CREATE INDEX IF NOT EXISTS idx_deals_deal_type ON public.deals(deal_type);
CREATE INDEX IF NOT EXISTS idx_deals_deal_score ON public.deals(deal_score DESC);
CREATE INDEX IF NOT EXISTS idx_deals_created_at ON public.deals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_investors_user_id ON public.investors(user_id);
CREATE INDEX IF NOT EXISTS idx_deal_notifications_deal_id ON public.deal_notifications(deal_id);
CREATE INDEX IF NOT EXISTS idx_deal_notifications_investor_id ON public.deal_notifications(investor_id);
CREATE INDEX IF NOT EXISTS idx_market_data_address ON public.market_data(property_address);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_deals_updated_at BEFORE UPDATE ON public.deals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_investors_updated_at BEFORE UPDATE ON public.investors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_portfolios_updated_at BEFORE UPDATE ON public.portfolios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.investors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deal_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deal_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolio_deals ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- Deals policies
CREATE POLICY "Users can view all deals" ON public.deals
    FOR SELECT USING (true);

CREATE POLICY "Users can create deals" ON public.deals
    FOR INSERT WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Users can update own deals" ON public.deals
    FOR UPDATE USING (auth.uid() = created_by OR auth.uid() = assigned_to);

-- Investors policies  
CREATE POLICY "Users can view all investors" ON public.investors
    FOR SELECT USING (true);

CREATE POLICY "Users can create investors" ON public.investors
    FOR INSERT WITH CHECK (true);

-- Insert sample data (optional)
-- This would be removed in production
INSERT INTO public.profiles (id, email, name, role, company, subscription_tier) VALUES
    ('00000000-0000-0000-0000-000000000001', 'admin@nxtrix.com', 'NxTrix Admin', 'admin', 'NxTrix', 'enterprise'),
    ('00000000-0000-0000-0000-000000000002', 'analyst@nxtrix.com', 'Senior Analyst', 'analyst', 'NxTrix', 'pro')
ON CONFLICT (id) DO NOTHING;