-- =====================================
-- SUBSCRIPTION MANAGEMENT TABLES
-- Missing tables for NxTrix CRM
-- =====================================

-- Usage tracking table for billing cycles
CREATE TABLE IF NOT EXISTS public.subscription_usage (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    usage_type TEXT NOT NULL, -- 'deals_per_month', 'ai_queries_per_month', etc.
    usage_count INTEGER DEFAULT 0,
    billing_cycle_start TIMESTAMP WITH TIME ZONE NOT NULL,
    billing_cycle_end TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, usage_type, billing_cycle_start)
);

-- Feature access log for compliance and analytics
CREATE TABLE IF NOT EXISTS public.feature_access_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    feature_name TEXT NOT NULL,
    access_granted BOOLEAN NOT NULL,
    subscription_tier TEXT NOT NULL,
    denial_reason TEXT,
    ip_address INET,
    user_agent TEXT,
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Subscription events for audit trail
CREATE TABLE IF NOT EXISTS public.subscription_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL, -- 'upgrade', 'downgrade', 'trial_start', 'trial_end', 'payment_failed', etc.
    event_details TEXT,
    previous_tier TEXT,
    new_tier TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Subscription limits and quotas
CREATE TABLE IF NOT EXISTS public.subscription_limits (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tier TEXT NOT NULL CHECK (tier IN ('free', 'pro', 'enterprise')),
    limit_type TEXT NOT NULL, -- 'deals_per_month', 'storage_gb', 'team_members', etc.
    limit_value INTEGER NOT NULL, -- -1 for unlimited
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tier, limit_type)
);

-- Team management for multi-user subscriptions
CREATE TABLE IF NOT EXISTS public.team_members (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    team_owner_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    member_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    permissions JSONB DEFAULT '{}',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    UNIQUE(team_owner_id, member_id)
);

-- Payment and billing history
CREATE TABLE IF NOT EXISTS public.billing_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    subscription_tier TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    currency TEXT DEFAULT 'USD',
    payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'succeeded', 'failed', 'refunded')),
    payment_method TEXT,
    stripe_payment_intent_id TEXT,
    stripe_subscription_id TEXT,
    billing_period_start TIMESTAMP WITH TIME ZONE,
    billing_period_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feature flag overrides for specific users
CREATE TABLE IF NOT EXISTS public.feature_overrides (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    feature_name TEXT NOT NULL,
    is_enabled BOOLEAN NOT NULL,
    override_reason TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES public.profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, feature_name)
);

-- Add subscription columns to profiles if they don't exist
DO $$
BEGIN
    -- Check if subscription_tier column exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'subscription_tier') THEN
        ALTER TABLE public.profiles ADD COLUMN subscription_tier TEXT NOT NULL DEFAULT 'free' 
            CHECK (subscription_tier IN ('free', 'pro', 'enterprise'));
    END IF;
    
    -- Check if subscription_status column exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'subscription_status') THEN
        ALTER TABLE public.profiles ADD COLUMN subscription_status TEXT DEFAULT 'trialing' 
            CHECK (subscription_status IN ('active', 'trialing', 'past_due', 'canceled', 'unpaid'));
    END IF;
    
    -- Check if billing cycle columns exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'billing_cycle_start') THEN
        ALTER TABLE public.profiles ADD COLUMN billing_cycle_start TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'billing_cycle_end') THEN
        ALTER TABLE public.profiles ADD COLUMN billing_cycle_end TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'trial_end') THEN
        ALTER TABLE public.profiles ADD COLUMN trial_end TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '14 days');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'subscription_metadata') THEN
        ALTER TABLE public.profiles ADD COLUMN subscription_metadata JSONB DEFAULT '{}';
    END IF;
END $$;

-- Enable RLS on new tables
ALTER TABLE public.subscription_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feature_access_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.billing_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feature_overrides ENABLE ROW LEVEL SECURITY;

-- RLS Policies for subscription tables
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own usage' AND tablename = 'subscription_usage') THEN
        CREATE POLICY "Users can view own usage" ON public.subscription_usage
            FOR SELECT USING (user_id = auth.uid());
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'System can manage usage' AND tablename = 'subscription_usage') THEN
        CREATE POLICY "System can manage usage" ON public.subscription_usage
            FOR ALL USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view all subscription limits' AND tablename = 'subscription_limits') THEN
        CREATE POLICY "Users can view all subscription limits" ON public.subscription_limits
            FOR SELECT USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own billing' AND tablename = 'billing_history') THEN
        CREATE POLICY "Users can view own billing" ON public.billing_history
            FOR SELECT USING (user_id = auth.uid());
    END IF;
END $$;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_subscription_usage_user_billing ON public.subscription_usage(user_id, billing_cycle_start);
CREATE INDEX IF NOT EXISTS idx_subscription_usage_type ON public.subscription_usage(usage_type);
CREATE INDEX IF NOT EXISTS idx_feature_access_log_user ON public.feature_access_log(user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_events_user ON public.subscription_events(user_id);

-- Insert default subscription limits
INSERT INTO public.subscription_limits (tier, limit_type, limit_value) VALUES
    -- Free tier limits
    ('free', 'deals_per_month', 5),
    ('free', 'investors_per_month', 10),
    ('free', 'ai_queries_per_month', 10),
    ('free', 'automation_rules', 0),
    ('free', 'email_campaigns_per_month', 0),
    ('free', 'document_generations_per_month', 5),
    ('free', 'api_calls_per_month', 0),
    ('free', 'storage_gb', 1),
    ('free', 'team_members', 1),
    
    -- Pro tier limits
    ('pro', 'deals_per_month', 50),
    ('pro', 'investors_per_month', 100),
    ('pro', 'ai_queries_per_month', 100),
    ('pro', 'automation_rules', 10),
    ('pro', 'email_campaigns_per_month', 20),
    ('pro', 'document_generations_per_month', 50),
    ('pro', 'api_calls_per_month', 1000),
    ('pro', 'storage_gb', 10),
    ('pro', 'team_members', 5),
    
    -- Enterprise tier (unlimited = -1)
    ('enterprise', 'deals_per_month', -1),
    ('enterprise', 'investors_per_month', -1),
    ('enterprise', 'ai_queries_per_month', -1),
    ('enterprise', 'automation_rules', -1),
    ('enterprise', 'email_campaigns_per_month', -1),
    ('enterprise', 'document_generations_per_month', -1),
    ('enterprise', 'api_calls_per_month', -1),
    ('enterprise', 'storage_gb', -1),
    ('enterprise', 'team_members', -1)
ON CONFLICT (tier, limit_type) DO NOTHING;

-- Add triggers for updated_at columns
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_subscription_usage_updated_at') THEN
        CREATE TRIGGER update_subscription_usage_updated_at BEFORE UPDATE ON public.subscription_usage
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_subscription_limits_updated_at') THEN
        CREATE TRIGGER update_subscription_limits_updated_at BEFORE UPDATE ON public.subscription_limits
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

SELECT 'Subscription management tables created successfully!' as status;