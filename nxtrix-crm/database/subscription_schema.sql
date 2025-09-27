-- =====================================
-- SUBSCRIPTION MANAGEMENT SCHEMA
-- =====================================
-- Comprehensive subscription tier management and feature gating

-- Add subscription fields to profiles table if not exists
DO $$
BEGIN
    -- Add subscription status if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='profiles' AND column_name='subscription_status') THEN
        ALTER TABLE public.profiles ADD COLUMN subscription_status TEXT DEFAULT 'trialing' 
        CHECK (subscription_status IN ('active', 'trialing', 'past_due', 'canceled', 'unpaid'));
    END IF;

    -- Add billing cycle tracking
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='profiles' AND column_name='billing_cycle_start') THEN
        ALTER TABLE public.profiles ADD COLUMN billing_cycle_start TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='profiles' AND column_name='billing_cycle_end') THEN
        ALTER TABLE public.profiles ADD COLUMN billing_cycle_end TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days');
    END IF;

    -- Add subscription metadata for custom configurations
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='profiles' AND column_name='subscription_metadata') THEN
        ALTER TABLE public.profiles ADD COLUMN subscription_metadata JSONB DEFAULT '{}';
    END IF;

    -- Add trial tracking
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='profiles' AND column_name='trial_end') THEN
        ALTER TABLE public.profiles ADD COLUMN trial_end TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

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

-- =====================================
-- SEED DATA FOR SUBSCRIPTION LIMITS
-- =====================================

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

-- =====================================
-- FUNCTIONS AND TRIGGERS
-- =====================================

-- Function to check if user has exceeded usage limits
CREATE OR REPLACE FUNCTION check_usage_limit(
    p_user_id UUID,
    p_usage_type TEXT
) RETURNS JSONB AS $$
DECLARE
    user_tier TEXT;
    usage_limit INTEGER;
    current_usage INTEGER;
    billing_start TIMESTAMP WITH TIME ZONE;
    billing_end TIMESTAMP WITH TIME ZONE;
    result JSONB;
BEGIN
    -- Get user's subscription tier and billing cycle
    SELECT subscription_tier, billing_cycle_start, billing_cycle_end
    INTO user_tier, billing_start, billing_end
    FROM public.profiles
    WHERE id = p_user_id;
    
    -- Get usage limit for this tier
    SELECT limit_value INTO usage_limit
    FROM public.subscription_limits
    WHERE tier = user_tier AND limit_type = p_usage_type;
    
    -- Get current usage for billing cycle
    SELECT COALESCE(usage_count, 0) INTO current_usage
    FROM public.subscription_usage
    WHERE user_id = p_user_id 
    AND usage_type = p_usage_type
    AND billing_cycle_start = billing_start;
    
    -- Build result
    result := jsonb_build_object(
        'has_access', (usage_limit = -1 OR current_usage < usage_limit),
        'current_usage', current_usage,
        'limit', usage_limit,
        'tier', user_tier,
        'unlimited', (usage_limit = -1)
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to increment usage counter
CREATE OR REPLACE FUNCTION increment_usage(
    p_user_id UUID,
    p_usage_type TEXT,
    p_amount INTEGER DEFAULT 1
) RETURNS BOOLEAN AS $$
DECLARE
    billing_start TIMESTAMP WITH TIME ZONE;
    billing_end TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Get user's billing cycle
    SELECT billing_cycle_start, billing_cycle_end
    INTO billing_start, billing_end
    FROM public.profiles
    WHERE id = p_user_id;
    
    -- Insert or update usage record
    INSERT INTO public.subscription_usage 
    (user_id, usage_type, usage_count, billing_cycle_start, billing_cycle_end)
    VALUES (p_user_id, p_usage_type, p_amount, billing_start, billing_end)
    ON CONFLICT (user_id, usage_type, billing_cycle_start)
    DO UPDATE SET 
        usage_count = subscription_usage.usage_count + p_amount,
        updated_at = NOW();
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to reset billing cycle and usage
CREATE OR REPLACE FUNCTION reset_billing_cycle(p_user_id UUID) RETURNS BOOLEAN AS $$
BEGIN
    -- Update billing cycle dates
    UPDATE public.profiles
    SET 
        billing_cycle_start = NOW(),
        billing_cycle_end = NOW() + INTERVAL '30 days',
        updated_at = NOW()
    WHERE id = p_user_id;
    
    -- Usage will automatically be tracked for new cycle
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- TRIGGERS
-- =====================================

-- Trigger to set initial billing cycle for new users
CREATE OR REPLACE FUNCTION set_initial_billing_cycle() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.billing_cycle_start IS NULL THEN
        NEW.billing_cycle_start := NOW();
        NEW.billing_cycle_end := NOW() + INTERVAL '30 days';
    END IF;
    
    -- Set trial end for new free users
    IF NEW.subscription_tier = 'free' AND NEW.trial_end IS NULL THEN
        NEW.trial_end := NOW() + INTERVAL '14 days';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to profiles table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'set_billing_cycle_trigger') THEN
        CREATE TRIGGER set_billing_cycle_trigger
            BEFORE INSERT ON public.profiles
            FOR EACH ROW EXECUTE FUNCTION set_initial_billing_cycle();
    END IF;
END $$;

-- Trigger to log subscription changes
CREATE OR REPLACE FUNCTION log_subscription_change() RETURNS TRIGGER AS $$
BEGIN
    IF OLD.subscription_tier IS DISTINCT FROM NEW.subscription_tier THEN
        INSERT INTO public.subscription_events 
        (user_id, event_type, previous_tier, new_tier, event_details)
        VALUES (
            NEW.id,
            CASE 
                WHEN NEW.subscription_tier = 'enterprise' THEN 'upgrade'
                WHEN NEW.subscription_tier = 'pro' AND OLD.subscription_tier = 'free' THEN 'upgrade'
                WHEN NEW.subscription_tier = 'free' AND OLD.subscription_tier IN ('pro', 'enterprise') THEN 'downgrade'
                ELSE 'tier_change'
            END,
            OLD.subscription_tier,
            NEW.subscription_tier,
            'Subscription tier changed'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply subscription change trigger
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'log_subscription_change_trigger') THEN
        CREATE TRIGGER log_subscription_change_trigger
            AFTER UPDATE ON public.profiles
            FOR EACH ROW EXECUTE FUNCTION log_subscription_change();
    END IF;
END $$;

-- =====================================
-- ROW LEVEL SECURITY
-- =====================================

-- Enable RLS on new tables
ALTER TABLE public.subscription_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feature_access_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.billing_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feature_overrides ENABLE ROW LEVEL SECURITY;

-- Subscription usage policies
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
END $$;

-- Feature access log policies
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own access log' AND tablename = 'feature_access_log') THEN
        CREATE POLICY "Users can view own access log" ON public.feature_access_log
            FOR SELECT USING (user_id = auth.uid());
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'System can log access' AND tablename = 'feature_access_log') THEN
        CREATE POLICY "System can log access" ON public.feature_access_log
            FOR INSERT WITH CHECK (true);
    END IF;
END $$;

-- Team members policies
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Team owners can manage members' AND tablename = 'team_members') THEN
        CREATE POLICY "Team owners can manage members" ON public.team_members
            FOR ALL USING (team_owner_id = auth.uid() OR member_id = auth.uid());
    END IF;
END $$;

-- Billing history policies
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own billing' AND tablename = 'billing_history') THEN
        CREATE POLICY "Users can view own billing" ON public.billing_history
            FOR SELECT USING (user_id = auth.uid());
    END IF;
END $$;

-- =====================================
-- INDEXES FOR PERFORMANCE
-- =====================================

-- Usage tracking indexes
CREATE INDEX IF NOT EXISTS idx_subscription_usage_user_billing ON public.subscription_usage(user_id, billing_cycle_start);
CREATE INDEX IF NOT EXISTS idx_subscription_usage_type ON public.subscription_usage(usage_type);

-- Feature access log indexes
CREATE INDEX IF NOT EXISTS idx_feature_access_log_user ON public.feature_access_log(user_id);
CREATE INDEX IF NOT EXISTS idx_feature_access_log_feature ON public.feature_access_log(feature_name);
CREATE INDEX IF NOT EXISTS idx_feature_access_log_time ON public.feature_access_log(accessed_at);

-- Subscription events indexes
CREATE INDEX IF NOT EXISTS idx_subscription_events_user ON public.subscription_events(user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_events_type ON public.subscription_events(event_type);

-- Team members indexes
CREATE INDEX IF NOT EXISTS idx_team_members_owner ON public.team_members(team_owner_id);
CREATE INDEX IF NOT EXISTS idx_team_members_member ON public.team_members(member_id);

-- Billing history indexes
CREATE INDEX IF NOT EXISTS idx_billing_history_user ON public.billing_history(user_id);
CREATE INDEX IF NOT EXISTS idx_billing_history_status ON public.billing_history(payment_status);

-- =====================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================

COMMENT ON TABLE public.subscription_usage IS 'Tracks feature usage per billing cycle for subscription enforcement';
COMMENT ON TABLE public.feature_access_log IS 'Logs all feature access attempts for compliance and analytics';
COMMENT ON TABLE public.subscription_events IS 'Audit trail of subscription changes and events';
COMMENT ON TABLE public.subscription_limits IS 'Configurable limits for each subscription tier';
COMMENT ON TABLE public.team_members IS 'Multi-user team management for enterprise subscriptions';
COMMENT ON TABLE public.billing_history IS 'Payment and billing transaction history';
COMMENT ON TABLE public.feature_overrides IS 'Manual feature flag overrides for specific users';

COMMENT ON FUNCTION check_usage_limit(UUID, TEXT) IS 'Check if user has exceeded usage limits for a feature';
COMMENT ON FUNCTION increment_usage(UUID, TEXT, INTEGER) IS 'Increment usage counter for billing cycle';
COMMENT ON FUNCTION reset_billing_cycle(UUID) IS 'Reset billing cycle and usage counters for user';