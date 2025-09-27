-- =====================================
-- NXTRIX CRM MASTER DATABASE SCHEMA
-- Complete SaaS Real Estate Investment Platform
-- Version: 3.0 - Comprehensive with Subscription Management
-- =====================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "citext";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================
-- CORE USER MANAGEMENT
-- =====================================

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email CITEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'analyst' CHECK (role IN ('admin', 'analyst', 'investor', 'agent')),
    company TEXT,
    phone TEXT,
    avatar_url TEXT,
    
    -- Subscription Management
    subscription_tier TEXT NOT NULL DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
    subscription_status TEXT DEFAULT 'trialing' CHECK (subscription_status IN ('active', 'trialing', 'past_due', 'canceled', 'unpaid')),
    billing_cycle_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    billing_cycle_end TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),
    trial_end TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '14 days'),
    subscription_metadata JSONB DEFAULT '{}',
    
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- =====================================
-- CORE BUSINESS ENTITIES
-- =====================================

-- Deals table - Core deal management
CREATE TABLE IF NOT EXISTS public.deals (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    property_address TEXT NOT NULL,
    purchase_price DECIMAL(12,2) NOT NULL DEFAULT 0,
    after_repair_value DECIMAL(12,2) NOT NULL DEFAULT 0,
    estimated_repair_cost DECIMAL(12,2) NOT NULL DEFAULT 0,
    market_rent DECIMAL(8,2) NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'New' CHECK (status IN ('New', 'Under Review', 'Approved', 'Rejected', 'Closed')),
    stage TEXT NOT NULL DEFAULT 'Sourcing' CHECK (stage IN ('Sourcing', 'Analysis', 'Due Diligence', 'Negotiation', 'Under Contract', 'Closing', 'Closed')),
    deal_type TEXT DEFAULT 'Fix and Flip' CHECK (deal_type IN ('Fix and Flip', 'Buy and Hold', 'Wholesale', 'BRRRR')),
    property_type TEXT DEFAULT 'Single Family' CHECK (property_type IN ('Single Family', 'Multi-Family', 'Commercial', 'Land', 'Condo')),
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
    investment_capacity DECIMAL(12,2) DEFAULT 0,
    risk_tolerance TEXT DEFAULT 'moderate' CHECK (risk_tolerance IN ('conservative', 'moderate', 'aggressive')),
    preferred_markets TEXT[] DEFAULT ARRAY[]::TEXT[],
    preferred_property_types TEXT[] DEFAULT ARRAY[]::TEXT[],
    investment_goals TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Deal scoring table
CREATE TABLE IF NOT EXISTS public.deal_scores (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    investor_id UUID REFERENCES public.investors(id) ON DELETE CASCADE,
    overall_score DECIMAL(3,2) DEFAULT 0 CHECK (overall_score >= 0 AND overall_score <= 10),
    roi_score DECIMAL(3,2) DEFAULT 0,
    location_score DECIMAL(3,2) DEFAULT 0,
    condition_score DECIMAL(3,2) DEFAULT 0,
    market_score DECIMAL(3,2) DEFAULT 0,
    risk_score DECIMAL(3,2) DEFAULT 0,
    scoring_criteria JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(deal_id, investor_id)
);

-- Deal notifications table
CREATE TABLE IF NOT EXISTS public.deal_notifications (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    investor_id UUID REFERENCES public.investors(id) ON DELETE CASCADE,
    notification_type TEXT NOT NULL CHECK (notification_type IN ('new_deal', 'price_drop', 'status_change', 'match_criteria')),
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT false,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);

-- Portfolio tracking
CREATE TABLE IF NOT EXISTS public.portfolios (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    investor_id UUID REFERENCES public.investors(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    total_invested DECIMAL(12,2) DEFAULT 0,
    current_value DECIMAL(12,2) DEFAULT 0,
    monthly_income DECIMAL(8,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Portfolio deals relationship
CREATE TABLE IF NOT EXISTS public.portfolio_deals (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    portfolio_id UUID REFERENCES public.portfolios(id) ON DELETE CASCADE,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    investment_amount DECIMAL(12,2) NOT NULL,
    ownership_percentage DECIMAL(5,2) DEFAULT 100,
    date_invested TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(portfolio_id, deal_id)
);

-- =====================================
-- PHASE 4: ADVANCED ANALYTICS
-- =====================================

-- Deal analytics for advanced reporting
CREATE TABLE IF NOT EXISTS public.deal_analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    analytics_type TEXT NOT NULL, -- 'performance', 'roi', 'market_comparison', 'risk_assessment'
    metrics JSONB NOT NULL DEFAULT '{}',
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    period_start TIMESTAMP WITH TIME ZONE,
    period_end TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES public.profiles(id),
    notes TEXT
);

-- Market intelligence data
CREATE TABLE IF NOT EXISTS public.market_intelligence (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    market_area TEXT NOT NULL, -- ZIP code, city, county
    data_type TEXT NOT NULL, -- 'pricing', 'inventory', 'days_on_market', 'price_trends'
    data_points JSONB NOT NULL DEFAULT '{}',
    data_source TEXT, -- 'MLS', 'Zillow', 'Rentals.com', etc.
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE,
    confidence_score DECIMAL(3,2) DEFAULT 0.5
);

-- Deal stage progression tracking
CREATE TABLE IF NOT EXISTS public.deal_stage_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    previous_stage TEXT,
    new_stage TEXT NOT NULL,
    changed_by UUID REFERENCES public.profiles(id),
    change_reason TEXT,
    stage_duration_days INTEGER,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Market predictions and forecasting
CREATE TABLE IF NOT EXISTS public.market_predictions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    market_area TEXT NOT NULL,
    prediction_type TEXT NOT NULL, -- 'price_forecast', 'rental_forecast', 'market_timing'
    prediction_data JSONB NOT NULL DEFAULT '{}',
    confidence_level DECIMAL(3,2) DEFAULT 0.5,
    prediction_period TEXT, -- '30_days', '90_days', '1_year'
    model_used TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- =====================================
-- PHASE 5: AUTOMATED DEAL SOURCING
-- =====================================

-- Enhanced investor criteria for automated matching
CREATE TABLE IF NOT EXISTS public.investor_criteria (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    investor_id UUID REFERENCES public.investors(id) ON DELETE CASCADE,
    criteria_name TEXT NOT NULL,
    property_types TEXT[] DEFAULT ARRAY[]::TEXT[],
    min_price DECIMAL(12,2),
    max_price DECIMAL(12,2),
    min_roi DECIMAL(5,2),
    max_risk_score DECIMAL(3,2),
    geographic_areas TEXT[] DEFAULT ARRAY[]::TEXT[],
    deal_types TEXT[] DEFAULT ARRAY[]::TEXT[],
    additional_filters JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    priority_level INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Property leads from automated sourcing
CREATE TABLE IF NOT EXISTS public.property_leads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source_type TEXT NOT NULL, -- 'MLS', 'foreclosure', 'auction', 'off_market'
    source_id TEXT, -- External ID from source system
    address TEXT NOT NULL,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    property_type TEXT,
    list_price DECIMAL(12,2),
    estimated_value DECIMAL(12,2),
    property_details JSONB DEFAULT '{}',
    lead_score DECIMAL(3,2) DEFAULT 0,
    status TEXT DEFAULT 'new' CHECK (status IN ('new', 'reviewing', 'interested', 'not_interested', 'converted')),
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Deal alerts for automated notifications
CREATE TABLE IF NOT EXISTS public.deal_alerts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    investor_id UUID REFERENCES public.investors(id) ON DELETE CASCADE,
    criteria_id UUID REFERENCES public.investor_criteria(id) ON DELETE CASCADE,
    property_lead_id UUID REFERENCES public.property_leads(id) ON DELETE CASCADE,
    alert_type TEXT NOT NULL, -- 'new_match', 'price_drop', 'criteria_update'
    match_score DECIMAL(3,2) DEFAULT 0,
    alert_data JSONB DEFAULT '{}',
    is_sent BOOLEAN DEFAULT false,
    sent_at TIMESTAMP WITH TIME ZONE,
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sourcing activity tracking
CREATE TABLE IF NOT EXISTS public.sourcing_activity (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    activity_type TEXT NOT NULL, -- 'search_executed', 'lead_discovered', 'alert_sent', 'conversion'
    source_type TEXT,
    criteria_used JSONB DEFAULT '{}',
    results_count INTEGER DEFAULT 0,
    processing_time_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed_by UUID REFERENCES public.profiles(id)
);

-- =====================================
-- PHASE 3B: AI ENHANCEMENT SYSTEM
-- =====================================

-- AI-powered deal analysis results
CREATE TABLE IF NOT EXISTS public.ai_deal_analysis (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    analysis_type TEXT NOT NULL, -- 'gpt_analysis', 'market_comparison', 'risk_assessment', 'roi_prediction'
    ai_model_used TEXT DEFAULT 'gpt-4',
    analysis_prompt TEXT,
    ai_response TEXT,
    confidence_score DECIMAL(3,2) DEFAULT 0.5,
    key_insights JSONB DEFAULT '{}',
    recommendations JSONB DEFAULT '{}',
    risk_factors JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES public.profiles(id)
);

-- Natural language search history
CREATE TABLE IF NOT EXISTS public.search_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    search_query TEXT NOT NULL,
    search_type TEXT DEFAULT 'deals', -- 'deals', 'investors', 'properties', 'market_data'
    processed_query TEXT, -- Processed/normalized version
    results_count INTEGER DEFAULT 0,
    search_filters JSONB DEFAULT '{}',
    response_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI-generated investment recommendations
CREATE TABLE IF NOT EXISTS public.investment_recommendations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    investor_id UUID REFERENCES public.investors(id) ON DELETE CASCADE,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    recommendation_type TEXT NOT NULL, -- 'high_match', 'portfolio_diversification', 'market_opportunity'
    ai_reasoning TEXT,
    confidence_score DECIMAL(3,2) DEFAULT 0.5,
    expected_roi DECIMAL(5,2),
    risk_level TEXT DEFAULT 'moderate',
    recommendation_data JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- AI model performance tracking
CREATE TABLE IF NOT EXISTS public.ai_model_performance (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    model_name TEXT NOT NULL,
    model_version TEXT,
    performance_metric TEXT NOT NULL, -- 'accuracy', 'response_time', 'user_satisfaction'
    metric_value DECIMAL(10,4),
    test_data_size INTEGER,
    evaluation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    evaluation_criteria JSONB DEFAULT '{}',
    notes TEXT
);

-- Deal scoring history for ML training
CREATE TABLE IF NOT EXISTS public.deal_scoring_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    property_address TEXT NOT NULL,
    scoring_algorithm TEXT NOT NULL, -- 'basic', 'advanced', 'ai_enhanced'
    financial_score DECIMAL(5,2),
    market_score DECIMAL(5,2),
    risk_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    scoring_factors JSONB DEFAULT '{}',
    market_data_used JSONB DEFAULT '{}',
    comparable_properties JSONB DEFAULT '{}',
    scoring_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    algorithm_version TEXT
);

-- =====================================
-- PHASE 3D: ADVANCED AUTOMATION SYSTEM
-- =====================================

-- Automation rules and workflows
CREATE TABLE IF NOT EXISTS public.automation_rules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    trigger_type TEXT NOT NULL, -- 'deal_status_change', 'time_based', 'data_change', 'manual'
    trigger_conditions JSONB DEFAULT '{}',
    action_type TEXT NOT NULL, -- 'send_email', 'create_task', 'update_deal', 'send_notification'
    action_parameters JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES public.profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_executed TIMESTAMP WITH TIME ZONE
);

-- Email templates for automation
CREATE TABLE IF NOT EXISTS public.email_templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    subject TEXT NOT NULL,
    body_html TEXT,
    body_text TEXT,
    template_variables JSONB DEFAULT '{}', -- Variables that can be replaced
    category TEXT DEFAULT 'general', -- 'deal_notification', 'investor_update', 'marketing'
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES public.profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document templates for automated generation
CREATE TABLE IF NOT EXISTS public.document_templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    document_type TEXT NOT NULL, -- 'contract', 'analysis_report', 'investor_packet', 'marketing_flyer'
    template_content TEXT, -- HTML or markdown template
    template_variables JSONB DEFAULT '{}',
    output_format TEXT DEFAULT 'pdf', -- 'pdf', 'docx', 'html'
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES public.profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generated documents tracking
CREATE TABLE IF NOT EXISTS public.generated_documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    template_id UUID REFERENCES public.document_templates(id),
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    document_name TEXT NOT NULL,
    file_path TEXT, -- Path to stored file
    file_size_bytes INTEGER,
    variables_used JSONB DEFAULT '{}',
    generated_by UUID REFERENCES public.profiles(id),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Email campaigns for marketing automation
CREATE TABLE IF NOT EXISTS public.email_campaigns (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    template_id UUID REFERENCES public.email_templates(id),
    target_criteria JSONB DEFAULT '{}', -- Criteria for selecting recipients
    schedule_type TEXT DEFAULT 'immediate', -- 'immediate', 'scheduled', 'drip', 'triggered'
    scheduled_for TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'draft', -- 'draft', 'scheduled', 'sending', 'sent', 'paused', 'completed'
    total_recipients INTEGER DEFAULT 0,
    emails_sent INTEGER DEFAULT 0,
    emails_delivered INTEGER DEFAULT 0,
    emails_opened INTEGER DEFAULT 0,
    emails_clicked INTEGER DEFAULT 0,
    created_by UUID REFERENCES public.profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Email campaign recipients tracking
CREATE TABLE IF NOT EXISTS public.campaign_recipients (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    campaign_id UUID REFERENCES public.email_campaigns(id) ON DELETE CASCADE,
    recipient_email TEXT NOT NULL,
    recipient_name TEXT,
    status TEXT DEFAULT 'pending', -- 'pending', 'sent', 'delivered', 'opened', 'clicked', 'bounced', 'unsubscribed'
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    bounce_reason TEXT,
    unsubscribe_reason TEXT
);

-- Automation workflows
CREATE TABLE IF NOT EXISTS public.automation_workflows (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    trigger_type TEXT NOT NULL,
    trigger_conditions JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_executed TIMESTAMP WITH TIME ZONE
);

-- Workflow steps
CREATE TABLE IF NOT EXISTS public.workflow_steps (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    workflow_id UUID REFERENCES public.automation_workflows(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    step_type TEXT NOT NULL, -- 'email', 'task', 'wait', 'condition', 'webhook'
    step_config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true
);

-- Automation execution log
CREATE TABLE IF NOT EXISTS public.automation_execution_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    automation_type TEXT NOT NULL, -- 'rule', 'workflow', 'campaign'
    automation_id UUID NOT NULL,
    execution_trigger TEXT,
    execution_context JSONB DEFAULT '{}',
    status TEXT NOT NULL, -- 'started', 'completed', 'failed', 'skipped'
    error_message TEXT,
    execution_time_ms INTEGER,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed_by UUID REFERENCES public.profiles(id)
);

-- Automated tasks
CREATE TABLE IF NOT EXISTS public.automated_tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    task_type TEXT NOT NULL,
    task_config JSONB DEFAULT '{}',
    schedule_pattern TEXT, -- Cron-like pattern
    next_execution TIMESTAMP WITH TIME ZONE,
    last_execution TIMESTAMP WITH TIME ZONE,
    execution_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API integrations
CREATE TABLE IF NOT EXISTS public.api_integrations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    integration_name TEXT NOT NULL,
    api_endpoint TEXT NOT NULL,
    api_method TEXT DEFAULT 'GET',
    api_headers JSONB DEFAULT '{}',
    api_params JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_called TIMESTAMP WITH TIME ZONE,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    average_response_time_ms INTEGER
);

-- User preferences for automation
CREATE TABLE IF NOT EXISTS public.user_automation_preferences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID,
    email_notifications BOOLEAN DEFAULT true,
    sms_notifications BOOLEAN DEFAULT false,
    push_notifications BOOLEAN DEFAULT true,
    notification_frequency TEXT DEFAULT 'immediate', -- 'immediate', 'hourly', 'daily', 'weekly'
    automation_categories JSONB DEFAULT '[]', -- Which types of automation to enable
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    timezone TEXT DEFAULT 'UTC',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- SUBSCRIPTION MANAGEMENT SYSTEM
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

-- =====================================
-- UTILITY FUNCTIONS
-- =====================================

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to set initial billing cycle for new users
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

-- Function to log subscription changes
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

-- =====================================
-- TRIGGERS
-- =====================================

-- Triggers for updated_at columns
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_profiles_updated_at') THEN
        CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_deals_updated_at') THEN
        CREATE TRIGGER update_deals_updated_at BEFORE UPDATE ON public.deals
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_investors_updated_at') THEN
        CREATE TRIGGER update_investors_updated_at BEFORE UPDATE ON public.investors
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_portfolios_updated_at') THEN
        CREATE TRIGGER update_portfolios_updated_at BEFORE UPDATE ON public.portfolios
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_investor_criteria_updated_at') THEN
        CREATE TRIGGER update_investor_criteria_updated_at BEFORE UPDATE ON public.investor_criteria
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_property_leads_updated_at') THEN
        CREATE TRIGGER update_property_leads_updated_at BEFORE UPDATE ON public.property_leads
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_automation_rules_updated_at') THEN
        CREATE TRIGGER update_automation_rules_updated_at BEFORE UPDATE ON public.automation_rules
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_email_templates_updated_at') THEN
        CREATE TRIGGER update_email_templates_updated_at BEFORE UPDATE ON public.email_templates
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_document_templates_updated_at') THEN
        CREATE TRIGGER update_document_templates_updated_at BEFORE UPDATE ON public.document_templates
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_email_campaigns_updated_at') THEN
        CREATE TRIGGER update_email_campaigns_updated_at BEFORE UPDATE ON public.email_campaigns
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_automation_workflows_updated_at') THEN
        CREATE TRIGGER update_automation_workflows_updated_at BEFORE UPDATE ON public.automation_workflows
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_user_automation_preferences_updated_at') THEN
        CREATE TRIGGER update_user_automation_preferences_updated_at BEFORE UPDATE ON public.user_automation_preferences
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_subscription_usage_updated_at') THEN
        CREATE TRIGGER update_subscription_usage_updated_at BEFORE UPDATE ON public.subscription_usage
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_subscription_limits_updated_at') THEN
        CREATE TRIGGER update_subscription_limits_updated_at BEFORE UPDATE ON public.subscription_limits
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- Subscription management triggers
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'set_billing_cycle_trigger') THEN
        CREATE TRIGGER set_billing_cycle_trigger
            BEFORE INSERT ON public.profiles
            FOR EACH ROW EXECUTE FUNCTION set_initial_billing_cycle();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'log_subscription_change_trigger') THEN
        CREATE TRIGGER log_subscription_change_trigger
            AFTER UPDATE ON public.profiles
            FOR EACH ROW EXECUTE FUNCTION log_subscription_change();
    END IF;
END $$;

-- =====================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.investors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deal_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deal_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolio_deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deal_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_intelligence ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deal_stage_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.investor_criteria ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.property_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deal_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sourcing_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_deal_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.search_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.investment_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_model_performance ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deal_scoring_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.automation_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.email_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.generated_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.email_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.campaign_recipients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.automation_workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.automation_execution_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.automated_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_automation_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feature_access_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.billing_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feature_overrides ENABLE ROW LEVEL SECURITY;

-- =====================================
-- RLS POLICIES
-- =====================================

-- Profiles policies
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own profile' AND tablename = 'profiles') THEN
        CREATE POLICY "Users can view own profile" ON public.profiles
            FOR SELECT USING (auth.uid() = id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can update own profile' AND tablename = 'profiles') THEN
        CREATE POLICY "Users can update own profile" ON public.profiles
            FOR UPDATE USING (auth.uid() = id);
    END IF;
END $$;

-- Deals policies
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view all deals' AND tablename = 'deals') THEN
        CREATE POLICY "Users can view all deals" ON public.deals
            FOR SELECT USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can create deals' AND tablename = 'deals') THEN
        CREATE POLICY "Users can create deals" ON public.deals
            FOR INSERT WITH CHECK (auth.uid() = created_by);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can update own deals' AND tablename = 'deals') THEN
        CREATE POLICY "Users can update own deals" ON public.deals
            FOR UPDATE USING (auth.uid() = created_by OR auth.uid() = assigned_to);
    END IF;
END $$;

-- Investors policies  
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view all investors' AND tablename = 'investors') THEN
        CREATE POLICY "Users can view all investors" ON public.investors
            FOR SELECT USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can create investors' AND tablename = 'investors') THEN
        CREATE POLICY "Users can create investors" ON public.investors
            FOR INSERT WITH CHECK (true);
    END IF;
END $$;

-- Subscription management policies
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

-- Additional policies for all other tables (simplified for brevity)
DO $$
BEGIN
    -- Allow users to view and manage their own data across all tables
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can manage their data' AND tablename = 'deal_analytics') THEN
        CREATE POLICY "Users can manage their data" ON public.deal_analytics FOR ALL USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can manage their data' AND tablename = 'market_intelligence') THEN
        CREATE POLICY "Users can manage their data" ON public.market_intelligence FOR ALL USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can manage their data' AND tablename = 'ai_deal_analysis') THEN
        CREATE POLICY "Users can manage their data" ON public.ai_deal_analysis FOR ALL USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can manage their data' AND tablename = 'automation_rules') THEN
        CREATE POLICY "Users can manage their data" ON public.automation_rules FOR ALL USING (true);
    END IF;
END $$;

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
-- INDEXES FOR PERFORMANCE
-- =====================================

-- Core business indexes
CREATE INDEX IF NOT EXISTS idx_deals_created_by ON public.deals(created_by);
CREATE INDEX IF NOT EXISTS idx_deals_status ON public.deals(status);
CREATE INDEX IF NOT EXISTS idx_deals_created_at ON public.deals(created_at);
CREATE INDEX IF NOT EXISTS idx_investors_user_id ON public.investors(user_id);
CREATE INDEX IF NOT EXISTS idx_deal_scores_deal_id ON public.deal_scores(deal_id);
CREATE INDEX IF NOT EXISTS idx_deal_scores_investor_id ON public.deal_scores(investor_id);

-- Analytics indexes
CREATE INDEX IF NOT EXISTS idx_deal_analytics_deal_id ON public.deal_analytics(deal_id);
CREATE INDEX IF NOT EXISTS idx_deal_analytics_type ON public.deal_analytics(analytics_type);
CREATE INDEX IF NOT EXISTS idx_market_intelligence_area ON public.market_intelligence(market_area);
CREATE INDEX IF NOT EXISTS idx_market_intelligence_type ON public.market_intelligence(data_type);

-- AI and automation indexes
CREATE INDEX IF NOT EXISTS idx_ai_deal_analysis_deal_id ON public.ai_deal_analysis(deal_id);
CREATE INDEX IF NOT EXISTS idx_automation_rules_trigger ON public.automation_rules(trigger_type);
CREATE INDEX IF NOT EXISTS idx_email_campaigns_status ON public.email_campaigns(status);

-- Subscription management indexes
CREATE INDEX IF NOT EXISTS idx_subscription_usage_user_billing ON public.subscription_usage(user_id, billing_cycle_start);
CREATE INDEX IF NOT EXISTS idx_subscription_usage_type ON public.subscription_usage(usage_type);
CREATE INDEX IF NOT EXISTS idx_feature_access_log_user ON public.feature_access_log(user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_events_user ON public.subscription_events(user_id);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_deals_search ON public.deals USING gin(to_tsvector('english', title || ' ' || property_address));
CREATE INDEX IF NOT EXISTS idx_investors_search ON public.investors USING gin(to_tsvector('english', name || ' ' || email));

-- =====================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================

COMMENT ON TABLE public.profiles IS 'User profiles with subscription management';
COMMENT ON TABLE public.deals IS 'Core real estate deals and properties';
COMMENT ON TABLE public.investors IS 'Investor profiles and investment criteria';
COMMENT ON TABLE public.deal_analytics IS 'Advanced analytics data for deals';
COMMENT ON TABLE public.ai_deal_analysis IS 'AI-powered deal analysis results';
COMMENT ON TABLE public.automation_rules IS 'Workflow automation rules and triggers';
COMMENT ON TABLE public.subscription_usage IS 'Usage tracking per billing cycle for subscription enforcement';
COMMENT ON TABLE public.subscription_limits IS 'Configurable limits for each subscription tier';

COMMENT ON FUNCTION check_usage_limit(UUID, TEXT) IS 'Check if user has exceeded usage limits for a feature';
COMMENT ON FUNCTION increment_usage(UUID, TEXT, INTEGER) IS 'Increment usage counter for billing cycle';
COMMENT ON FUNCTION reset_billing_cycle(UUID) IS 'Reset billing cycle and usage counters for user';

-- =====================================
-- SCHEMA VERSION AND COMPLETION
-- =====================================

-- Track schema version
INSERT INTO public.profiles (id, email, name, role, subscription_tier) VALUES
    ('00000000-0000-0000-0000-000000000000', 'system@nxtrix.com', 'System Account', 'admin', 'enterprise')
ON CONFLICT (id) DO NOTHING;

-- Schema deployment complete
SELECT 'NxTrix CRM Master Schema v3.0 deployed successfully!' as deployment_status;