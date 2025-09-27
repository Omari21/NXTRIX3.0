-- Phase 4 & 5 Database Schema Additions for Existing Supabase Database
-- Only adds new tables that don't exist yet

-- ================================
-- PHASE 4: ADVANCED ANALYTICS TABLES
-- ================================

-- Deal analytics table - AI-powered deal analysis and insights
CREATE TABLE IF NOT EXISTS public.deal_analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    analysis_type TEXT NOT NULL CHECK (analysis_type IN ('market_comparison', 'risk_assessment', 'profitability', 'market_trends')),
    analysis_data JSONB NOT NULL DEFAULT '{}',
    confidence_score DECIMAL(5,2) CHECK (confidence_score >= 0 AND confidence_score <= 100),
    recommendations TEXT,
    market_factors JSONB DEFAULT '{}',
    risk_factors JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Market intelligence table - Market data and trends
CREATE TABLE IF NOT EXISTS public.market_intelligence (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    market_area TEXT NOT NULL,
    data_type TEXT NOT NULL CHECK (data_type IN ('price_trends', 'inventory_levels', 'absorption_rates', 'demographic_data')),
    data_period TEXT NOT NULL, -- e.g., '2024-Q1', 'Jan-2024', etc.
    data_value JSONB NOT NULL DEFAULT '{}',
    source TEXT,
    reliability_score DECIMAL(5,2) CHECK (reliability_score >= 0 AND reliability_score <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Deal stage history table - Track deal progression
CREATE TABLE IF NOT EXISTS public.deal_stage_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    previous_stage TEXT,
    new_stage TEXT NOT NULL,
    stage_duration_hours INTEGER,
    notes TEXT,
    user_id UUID REFERENCES public.profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Market predictions table - AI market forecasting
CREATE TABLE IF NOT EXISTS public.market_predictions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    market_area TEXT NOT NULL,
    prediction_type TEXT NOT NULL CHECK (prediction_type IN ('price_appreciation', 'rental_growth', 'market_cycle', 'demand_forecast')),
    prediction_period TEXT NOT NULL, -- e.g., '6_months', '1_year', '5_years'
    predicted_value JSONB NOT NULL DEFAULT '{}',
    confidence_level DECIMAL(5,2) CHECK (confidence_level >= 0 AND confidence_level <= 100),
    model_used TEXT,
    input_factors JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- PHASE 5: AUTOMATED DEAL SOURCING TABLES
-- ================================

-- Investor criteria table - Investor buy-box criteria
CREATE TABLE IF NOT EXISTS public.investor_criteria (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    investor_id UUID REFERENCES public.investors(id) ON DELETE CASCADE,
    criteria_name TEXT NOT NULL,
    min_price DECIMAL(12,2),
    max_price DECIMAL(12,2),
    property_types TEXT[], -- array of property types
    preferred_markets TEXT[], -- array of market areas
    min_roi DECIMAL(5,2),
    min_cap_rate DECIMAL(5,2),
    max_repair_costs DECIMAL(12,2),
    deal_types TEXT[], -- array of deal types
    additional_criteria JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Property leads table - Sourced property opportunities
CREATE TABLE IF NOT EXISTS public.property_leads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    address TEXT NOT NULL,
    property_type TEXT NOT NULL,
    estimated_value DECIMAL(12,2),
    asking_price DECIMAL(12,2),
    estimated_repair_costs DECIMAL(12,2),
    market_area TEXT,
    lead_source TEXT NOT NULL CHECK (lead_source IN ('mls', 'offmarket', 'auction', 'wholesaler', 'manual')),
    lead_quality_score INTEGER CHECK (lead_quality_score >= 0 AND lead_quality_score <= 100),
    property_details JSONB DEFAULT '{}',
    contact_info JSONB DEFAULT '{}',
    status TEXT DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'qualified', 'converted', 'rejected')),
    assigned_to UUID REFERENCES public.profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Deal alerts table - Automated deal matching notifications
CREATE TABLE IF NOT EXISTS public.deal_alerts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    investor_id UUID REFERENCES public.investors(id) ON DELETE CASCADE,
    property_lead_id UUID REFERENCES public.property_leads(id) ON DELETE CASCADE,
    criteria_id UUID REFERENCES public.investor_criteria(id) ON DELETE CASCADE,
    match_score DECIMAL(5,2) CHECK (match_score >= 0 AND match_score <= 100),
    alert_type TEXT DEFAULT 'property_match' CHECK (alert_type IN ('property_match', 'market_update', 'price_drop')),
    alert_status TEXT DEFAULT 'pending' CHECK (alert_status IN ('pending', 'sent', 'viewed', 'acted_upon')),
    alert_data JSONB DEFAULT '{}',
    sent_at TIMESTAMP WITH TIME ZONE,
    viewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sourcing activity table - Track sourcing performance
CREATE TABLE IF NOT EXISTS public.sourcing_activity (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id),
    activity_type TEXT NOT NULL CHECK (activity_type IN ('lead_generated', 'lead_qualified', 'deal_matched', 'investor_contacted')),
    property_lead_id UUID REFERENCES public.property_leads(id),
    investor_id UUID REFERENCES public.investors(id),
    activity_data JSONB DEFAULT '{}',
    result TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- INDEXES FOR PERFORMANCE
-- ================================

-- Deal analytics indexes
CREATE INDEX IF NOT EXISTS idx_deal_analytics_deal_id ON public.deal_analytics(deal_id);
CREATE INDEX IF NOT EXISTS idx_deal_analytics_type ON public.deal_analytics(analysis_type);
CREATE INDEX IF NOT EXISTS idx_deal_analytics_created_at ON public.deal_analytics(created_at);

-- Market intelligence indexes
CREATE INDEX IF NOT EXISTS idx_market_intelligence_area ON public.market_intelligence(market_area);
CREATE INDEX IF NOT EXISTS idx_market_intelligence_type ON public.market_intelligence(data_type);
CREATE INDEX IF NOT EXISTS idx_market_intelligence_period ON public.market_intelligence(data_period);

-- Deal stage history indexes
CREATE INDEX IF NOT EXISTS idx_deal_stage_history_deal_id ON public.deal_stage_history(deal_id);
CREATE INDEX IF NOT EXISTS idx_deal_stage_history_created_at ON public.deal_stage_history(created_at);

-- Market predictions indexes
CREATE INDEX IF NOT EXISTS idx_market_predictions_area ON public.market_predictions(market_area);
CREATE INDEX IF NOT EXISTS idx_market_predictions_type ON public.market_predictions(prediction_type);

-- Investor criteria indexes
CREATE INDEX IF NOT EXISTS idx_investor_criteria_investor_id ON public.investor_criteria(investor_id);
CREATE INDEX IF NOT EXISTS idx_investor_criteria_active ON public.investor_criteria(is_active);

-- Property leads indexes
CREATE INDEX IF NOT EXISTS idx_property_leads_status ON public.property_leads(status);
CREATE INDEX IF NOT EXISTS idx_property_leads_market_area ON public.property_leads(market_area);
CREATE INDEX IF NOT EXISTS idx_property_leads_source ON public.property_leads(lead_source);
CREATE INDEX IF NOT EXISTS idx_property_leads_created_at ON public.property_leads(created_at);

-- Deal alerts indexes
CREATE INDEX IF NOT EXISTS idx_deal_alerts_investor_id ON public.deal_alerts(investor_id);
CREATE INDEX IF NOT EXISTS idx_deal_alerts_property_lead_id ON public.deal_alerts(property_lead_id);
CREATE INDEX IF NOT EXISTS idx_deal_alerts_status ON public.deal_alerts(alert_status);
CREATE INDEX IF NOT EXISTS idx_deal_alerts_created_at ON public.deal_alerts(created_at);

-- Sourcing activity indexes
CREATE INDEX IF NOT EXISTS idx_sourcing_activity_user_id ON public.sourcing_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_sourcing_activity_type ON public.sourcing_activity(activity_type);
CREATE INDEX IF NOT EXISTS idx_sourcing_activity_created_at ON public.sourcing_activity(created_at);

-- ================================
-- CONDITIONAL TRIGGERS
-- ================================

-- Deal analytics updated_at trigger
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_deal_analytics_updated_at') THEN
        CREATE TRIGGER update_deal_analytics_updated_at
            BEFORE UPDATE ON public.deal_analytics
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- Market intelligence updated_at trigger
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_market_intelligence_updated_at') THEN
        CREATE TRIGGER update_market_intelligence_updated_at
            BEFORE UPDATE ON public.market_intelligence
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- Market predictions updated_at trigger
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_market_predictions_updated_at') THEN
        CREATE TRIGGER update_market_predictions_updated_at
            BEFORE UPDATE ON public.market_predictions
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- Investor criteria updated_at trigger
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_investor_criteria_updated_at') THEN
        CREATE TRIGGER update_investor_criteria_updated_at
            BEFORE UPDATE ON public.investor_criteria
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- Property leads updated_at trigger
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_property_leads_updated_at') THEN
        CREATE TRIGGER update_property_leads_updated_at
            BEFORE UPDATE ON public.property_leads
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- ================================
-- ROW LEVEL SECURITY POLICIES
-- ================================

-- Enable RLS on new tables
ALTER TABLE public.deal_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_intelligence ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deal_stage_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.investor_criteria ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.property_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deal_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sourcing_activity ENABLE ROW LEVEL SECURITY;

-- Deal analytics policies
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view all deal analytics' AND tablename = 'deal_analytics') THEN
        CREATE POLICY "Users can view all deal analytics" ON public.deal_analytics
            FOR SELECT USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can create deal analytics' AND tablename = 'deal_analytics') THEN
        CREATE POLICY "Users can create deal analytics" ON public.deal_analytics
            FOR INSERT WITH CHECK (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can update deal analytics' AND tablename = 'deal_analytics') THEN
        CREATE POLICY "Users can update deal analytics" ON public.deal_analytics
            FOR UPDATE USING (true);
    END IF;
END $$;

-- Market intelligence policies  
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view market intelligence' AND tablename = 'market_intelligence') THEN
        CREATE POLICY "Users can view market intelligence" ON public.market_intelligence
            FOR SELECT USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can create market intelligence' AND tablename = 'market_intelligence') THEN
        CREATE POLICY "Users can create market intelligence" ON public.market_intelligence
            FOR INSERT WITH CHECK (true);
    END IF;
END $$;

-- Property leads policies
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view all property leads' AND tablename = 'property_leads') THEN
        CREATE POLICY "Users can view all property leads" ON public.property_leads
            FOR SELECT USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can create property leads' AND tablename = 'property_leads') THEN
        CREATE POLICY "Users can create property leads" ON public.property_leads
            FOR INSERT WITH CHECK (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can update property leads' AND tablename = 'property_leads') THEN
        CREATE POLICY "Users can update property leads" ON public.property_leads
            FOR UPDATE USING (true);
    END IF;
END $$;

-- Deal alerts policies
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view deal alerts' AND tablename = 'deal_alerts') THEN
        CREATE POLICY "Users can view deal alerts" ON public.deal_alerts
            FOR SELECT USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can create deal alerts' AND tablename = 'deal_alerts') THEN
        CREATE POLICY "Users can create deal alerts" ON public.deal_alerts
            FOR INSERT WITH CHECK (true);
    END IF;
END $$;

-- ================================
-- COMPLETION MESSAGE
-- ================================

-- Insert completion log
DO $$
BEGIN
    RAISE NOTICE 'Phase 4 & 5 database schema additions completed successfully!';
    RAISE NOTICE 'Added 8 new tables for Advanced Analytics and Automated Deal Sourcing';
    RAISE NOTICE 'Tables added: deal_analytics, market_intelligence, deal_stage_history, market_predictions, investor_criteria, property_leads, deal_alerts, sourcing_activity';
END $$;