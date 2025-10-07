# NXTRIX CRM - Supabase Database Schema
# Run these SQL commands in your Supabase SQL editor

-- Note: Supabase handles JWT secrets automatically, no manual configuration needed

-- Create users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company VARCHAR(255),
    phone VARCHAR(20),
    user_tier VARCHAR(20) DEFAULT 'free' CHECK (user_tier IN ('free', 'professional', 'enterprise')),
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    subscription_status VARCHAR(20) DEFAULT 'active',
    stripe_customer_id VARCHAR(255),
    trial_ends_at TIMESTAMP WITH TIME ZONE
);

-- Create deals table
CREATE TABLE IF NOT EXISTS public.deals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    property_type VARCHAR(100),
    address TEXT,
    value DECIMAL(15,2),
    -- Financial fields matching models.py Deal class
    purchase_price DECIMAL(15,2),
    arv DECIMAL(15,2),
    repair_costs DECIMAL(15,2),
    monthly_rent DECIMAL(15,2),
    closing_costs DECIMAL(15,2),
    annual_taxes DECIMAL(15,2),
    insurance DECIMAL(15,2),
    hoa_fees DECIMAL(15,2),
    vacancy_rate DECIMAL(5,2) DEFAULT 5.0,
    -- Property details
    neighborhood_grade VARCHAR(10) DEFAULT 'B',
    condition VARCHAR(50) DEFAULT 'Good',
    market_trend VARCHAR(50) DEFAULT 'Stable',
    ai_score INTEGER DEFAULT 0 CHECK (ai_score >= 0 AND ai_score <= 100),
    -- Deal management
    stage VARCHAR(50) DEFAULT 'prospect' CHECK (stage IN ('prospect', 'qualified', 'due_diligence', 'negotiation', 'closing', 'closed', 'lost')),
    probability INTEGER DEFAULT 50 CHECK (probability >= 0 AND probability <= 100),
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

-- Create clients table
CREATE TABLE IF NOT EXISTS public.clients (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    company VARCHAR(255),
    type VARCHAR(50) DEFAULT 'individual' CHECK (type IN ('individual', 'institutional', 'corporate', 'high_net_worth')),
    status VARCHAR(50) DEFAULT 'prospect' CHECK (status IN ('prospect', 'active', 'inactive', 'closed')),
    portfolio_value DECIMAL(15,2),
    risk_profile VARCHAR(20) CHECK (risk_profile IN ('conservative', 'moderate', 'aggressive')),
    investment_preferences TEXT[],
    address TEXT,
    notes TEXT,
    tags TEXT[],
    last_contact DATE,
    next_followup DATE,
    lead_score INTEGER DEFAULT 0 CHECK (lead_score >= 0 AND lead_score <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create investors table (matching models.py Investor class)
CREATE TABLE IF NOT EXISTS public.investors (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    investment_range_min DECIMAL(15,2),
    investment_range_max DECIMAL(15,2),
    preferred_markets TEXT,
    deal_types TEXT,
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    total_investments INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'Suspended')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create communications table
CREATE TABLE IF NOT EXISTS public.communications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    client_id UUID REFERENCES public.clients(id) ON DELETE CASCADE,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('email', 'call', 'meeting', 'sms', 'note')),
    subject VARCHAR(255),
    content TEXT,
    direction VARCHAR(10) CHECK (direction IN ('inbound', 'outbound')),
    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_response')),
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

-- Create portfolio table (matching models.py Portfolio class)
CREATE TABLE IF NOT EXISTS public.portfolio (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE NOT NULL,
    investor_id UUID REFERENCES public.investors(id) ON DELETE CASCADE,
    investment_amount DECIMAL(15,2),
    ownership_percentage DECIMAL(5,2),
    entry_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    exit_date TIMESTAMP WITH TIME ZONE,
    current_value DECIMAL(15,2),
    total_return DECIMAL(15,2),
    status VARCHAR(50) DEFAULT 'Active' CHECK (status IN ('Active', 'Exited', 'Pending')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create tasks table
CREATE TABLE IF NOT EXISTS public.tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    client_id UUID REFERENCES public.clients(id) ON DELETE CASCADE,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    due_date DATE,
    completed_at TIMESTAMP WITH TIME ZONE,
    estimated_hours DECIMAL(4,2),
    actual_hours DECIMAL(4,2),
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create workflows table
CREATE TABLE IF NOT EXISTS public.workflows (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    trigger_type VARCHAR(50) NOT NULL,
    trigger_conditions JSONB DEFAULT '{}',
    actions JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    execution_count INTEGER DEFAULT 0,
    last_executed TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create notifications table
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    is_read BOOLEAN DEFAULT FALSE,
    action_url TEXT,
    metadata JSONB DEFAULT '{}',
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create audit_logs table for tracking changes
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    table_name VARCHAR(50) NOT NULL,
    record_id UUID,
    action VARCHAR(20) NOT NULL CHECK (action IN ('insert', 'update', 'delete')),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create subscription_usage table for tracking feature usage
CREATE TABLE IF NOT EXISTS public.subscription_usage (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    feature VARCHAR(100) NOT NULL,
    usage_count INTEGER DEFAULT 1,
    usage_date DATE DEFAULT CURRENT_DATE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, feature, usage_date)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_deals_user_id ON public.deals(user_id);
CREATE INDEX IF NOT EXISTS idx_deals_stage ON public.deals(stage);
CREATE INDEX IF NOT EXISTS idx_deals_created_at ON public.deals(created_at);
CREATE INDEX IF NOT EXISTS idx_deals_purchase_price ON public.deals(purchase_price);
CREATE INDEX IF NOT EXISTS idx_deals_arv ON public.deals(arv);
CREATE INDEX IF NOT EXISTS idx_clients_user_id ON public.clients(user_id);
CREATE INDEX IF NOT EXISTS idx_clients_status ON public.clients(status);
CREATE INDEX IF NOT EXISTS idx_investors_user_id ON public.investors(user_id);
CREATE INDEX IF NOT EXISTS idx_investors_status ON public.investors(status);
CREATE INDEX IF NOT EXISTS idx_portfolio_user_id ON public.portfolio(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_deal_id ON public.portfolio(deal_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_investor_id ON public.portfolio(investor_id);
CREATE INDEX IF NOT EXISTS idx_communications_user_id ON public.communications(user_id);
CREATE INDEX IF NOT EXISTS idx_communications_client_id ON public.communications(client_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON public.tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON public.tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON public.notifications(is_read);

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.investors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolio ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.communications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_usage ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON public.users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.users FOR UPDATE USING (auth.uid() = id);

-- Deals policies
CREATE POLICY "Users can view own deals" ON public.deals FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own deals" ON public.deals FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own deals" ON public.deals FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own deals" ON public.deals FOR DELETE USING (auth.uid() = user_id);

-- Clients policies
CREATE POLICY "Users can view own clients" ON public.clients FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own clients" ON public.clients FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own clients" ON public.clients FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own clients" ON public.clients FOR DELETE USING (auth.uid() = user_id);

-- Investors policies
CREATE POLICY "Users can view own investors" ON public.investors FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own investors" ON public.investors FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own investors" ON public.investors FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own investors" ON public.investors FOR DELETE USING (auth.uid() = user_id);

-- Portfolio policies
CREATE POLICY "Users can view own portfolio" ON public.portfolio FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own portfolio" ON public.portfolio FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own portfolio" ON public.portfolio FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own portfolio" ON public.portfolio FOR DELETE USING (auth.uid() = user_id);

-- Communications policies
CREATE POLICY "Users can view own communications" ON public.communications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own communications" ON public.communications FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own communications" ON public.communications FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own communications" ON public.communications FOR DELETE USING (auth.uid() = user_id);

-- Tasks policies
CREATE POLICY "Users can view own tasks" ON public.tasks FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own tasks" ON public.tasks FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own tasks" ON public.tasks FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own tasks" ON public.tasks FOR DELETE USING (auth.uid() = user_id);

-- Workflows policies
CREATE POLICY "Users can view own workflows" ON public.workflows FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own workflows" ON public.workflows FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own workflows" ON public.workflows FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own workflows" ON public.workflows FOR DELETE USING (auth.uid() = user_id);

-- Notifications policies
CREATE POLICY "Users can view own notifications" ON public.notifications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own notifications" ON public.notifications FOR UPDATE USING (auth.uid() = user_id);

-- Audit logs policies (read-only for users)
CREATE POLICY "Users can view own audit logs" ON public.audit_logs FOR SELECT USING (auth.uid() = user_id);

-- Subscription usage policies
CREATE POLICY "Users can view own usage" ON public.subscription_usage FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own usage" ON public.subscription_usage FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_deals_updated_at BEFORE UPDATE ON public.deals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON public.clients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_investors_updated_at BEFORE UPDATE ON public.investors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_portfolio_updated_at BEFORE UPDATE ON public.portfolio FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_communications_updated_at BEFORE UPDATE ON public.communications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON public.tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON public.workflows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to handle new user registration
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, created_at)
    VALUES (NEW.id, NEW.email, NEW.created_at);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for automatic user profile creation
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Create function for user tier limits
CREATE OR REPLACE FUNCTION check_user_limits(user_id UUID, feature_name TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    user_tier TEXT;
    current_count INTEGER;
    limit_count INTEGER;
BEGIN
    -- Get user tier
    SELECT users.user_tier INTO user_tier FROM public.users WHERE id = user_id;
    
    -- Get current usage count for today
    SELECT COALESCE(usage_count, 0) INTO current_count 
    FROM public.subscription_usage 
    WHERE user_id = check_user_limits.user_id 
    AND feature = feature_name 
    AND usage_date = CURRENT_DATE;
    
    -- Set limits based on tier and feature
    CASE 
        WHEN user_tier = 'free' THEN
            CASE feature_name
                WHEN 'deals' THEN limit_count := 5;
                WHEN 'clients' THEN limit_count := 10;
                WHEN 'investors' THEN limit_count := 5;
                WHEN 'portfolio' THEN limit_count := 3;
                WHEN 'communications' THEN limit_count := 20;
                WHEN 'tasks' THEN limit_count := 10;
                ELSE limit_count := 999999;
            END CASE;
        WHEN user_tier = 'professional' THEN
            CASE feature_name
                WHEN 'deals' THEN limit_count := 50;
                WHEN 'clients' THEN limit_count := 100;
                WHEN 'investors' THEN limit_count := 50;
                WHEN 'portfolio' THEN limit_count := 25;
                WHEN 'communications' THEN limit_count := 500;
                WHEN 'tasks' THEN limit_count := 100;
                ELSE limit_count := 999999;
            END CASE;
        ELSE
            limit_count := 999999; -- Enterprise has no limits
    END CASE;
    
    RETURN current_count < limit_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Insert sample data for demo
INSERT INTO public.users (id, email, first_name, last_name, company, user_tier, is_admin) 
VALUES 
    ('00000000-0000-0000-0000-000000000001', 'demo@nxtrix.com', 'Demo', 'User', 'NXTRIX Demo', 'professional', FALSE),
    ('00000000-0000-0000-0000-000000000002', 'admin@nxtrix.com', 'Admin', 'User', 'NXTRIX', 'enterprise', TRUE)
ON CONFLICT (id) DO NOTHING;