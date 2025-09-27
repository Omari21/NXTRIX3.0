-- NxTrix CRM Database Schema - UPDATED FOR PHASE 4 & 5
-- Enterprise Real Estate Deal Analyzer with Advanced Analytics and Automated Deal Sourcing
-- Updated: September 15, 2025

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "citext";

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =====================================
-- PHASE 4: ADVANCED ANALYTICS TABLES
-- =====================================

-- Deal analytics table - Advanced deal tracking
CREATE TABLE IF NOT EXISTS public.deal_analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    property_address TEXT NOT NULL,
    deal_stage TEXT NOT NULL,
    entry_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    purchase_price DECIMAL(12,2),
    estimated_arv DECIMAL(12,2),
    rehab_costs DECIMAL(12,2),
    holding_costs DECIMAL(12,2),
    acquisition_costs DECIMAL(12,2),
    expected_profit DECIMAL(12,2),
    profit_margin DECIMAL(5,2),
    deal_score DECIMAL(5,2),
    time_in_stage INTEGER DEFAULT 0,
    conversion_probability DECIMAL(5,2),
    market_data JSONB DEFAULT '{}',
    competitor_data JSONB DEFAULT '{}',
    financial_metrics JSONB DEFAULT '{}',
    risk_factors JSONB DEFAULT '{}',
    opportunity_score DECIMAL(5,2)
);

-- Market intelligence table - Enhanced market data
CREATE TABLE IF NOT EXISTS public.market_intelligence (
    area_code TEXT PRIMARY KEY,
    area_name TEXT NOT NULL,
    median_home_price DECIMAL(12,2),
    price_per_sqft DECIMAL(8,2),
    days_on_market INTEGER,
    inventory_levels INTEGER,
    market_trend TEXT,
    price_trend_6m DECIMAL(5,2),
    rental_yield DECIMAL(5,2),
    population_growth DECIMAL(5,2),
    employment_rate DECIMAL(5,2),
    crime_index DECIMAL(5,2),
    school_ratings DECIMAL(3,1),
    walkability_score INTEGER,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Deal stage history table - Track deal progression
CREATE TABLE IF NOT EXISTS public.deal_stage_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    deal_id UUID REFERENCES public.deal_analytics(id) ON DELETE CASCADE,
    from_stage TEXT,
    to_stage TEXT NOT NULL,
    stage_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    time_in_previous_stage INTEGER DEFAULT 0,
    notes TEXT
);

-- Market predictions table - ML predictions
CREATE TABLE IF NOT EXISTS public.market_predictions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    area_code TEXT NOT NULL,
    prediction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    predicted_price_change DECIMAL(5,2),
    confidence_score DECIMAL(5,2),
    prediction_horizon INTEGER,
    model_version TEXT,
    features_used JSONB DEFAULT '{}'
);

-- =====================================
-- PHASE 5: AUTOMATED DEAL SOURCING TABLES
-- =====================================

-- Investor criteria table - Investment preferences
CREATE TABLE IF NOT EXISTS public.investor_criteria (
    investor_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    investor_name TEXT NOT NULL,
    min_price DECIMAL(12,2),
    max_price DECIMAL(12,2),
    preferred_property_types TEXT,
    target_locations TEXT,
    min_roi DECIMAL(5,2),
    min_cash_flow DECIMAL(8,2),
    max_rehab_budget DECIMAL(12,2),
    preferred_conditions TEXT,
    investment_strategy TEXT,
    deal_sources TEXT,
    alert_frequency TEXT DEFAULT 'daily',
    active BOOLEAN DEFAULT true,
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Property leads table - Sourced properties
CREATE TABLE IF NOT EXISTS public.property_leads (
    lead_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    property_address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip_code TEXT,
    property_type TEXT NOT NULL,
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    square_feet INTEGER,
    lot_size DECIMAL(8,2),
    year_built INTEGER,
    asking_price DECIMAL(12,2),
    estimated_arv DECIMAL(12,2),
    estimated_rehab DECIMAL(12,2),
    property_condition TEXT,
    days_on_market INTEGER,
    listing_agent TEXT,
    listing_agent_phone TEXT,
    deal_source TEXT,
    lead_source_contact TEXT,
    description TEXT,
    photos TEXT,
    discovered_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT DEFAULT 'new',
    notes TEXT
);

-- Deal alerts table - Automated notifications
CREATE TABLE IF NOT EXISTS public.deal_alerts (
    alert_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    investor_id UUID REFERENCES public.investor_criteria(investor_id) ON DELETE CASCADE,
    property_lead_id UUID REFERENCES public.property_leads(lead_id) ON DELETE CASCADE,
    match_score DECIMAL(5,2) NOT NULL,
    alert_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    alert_sent BOOLEAN DEFAULT false,
    investor_response TEXT,
    response_date TIMESTAMP WITH TIME ZONE
);

-- Deal sourcing activity table - Activity tracking
CREATE TABLE IF NOT EXISTS public.sourcing_activity (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    activity_type TEXT NOT NULL,
    description TEXT,
    property_lead_id UUID REFERENCES public.property_leads(lead_id) ON DELETE CASCADE,
    investor_id UUID REFERENCES public.investor_criteria(investor_id) ON DELETE CASCADE,
    activity_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    result TEXT,
    notes TEXT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_deals_status ON public.deals(status);
CREATE INDEX IF NOT EXISTS idx_deal_analytics_stage ON public.deal_analytics(deal_stage);
CREATE INDEX IF NOT EXISTS idx_property_leads_city ON public.property_leads(city);
CREATE INDEX IF NOT EXISTS idx_property_leads_status ON public.property_leads(status);
CREATE INDEX IF NOT EXISTS idx_deal_alerts_investor ON public.deal_alerts(investor_id);

-- Create triggers for updated_at (only if they don't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_deal_analytics_updated_at') THEN
        CREATE TRIGGER update_deal_analytics_updated_at BEFORE UPDATE ON public.deal_analytics
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_property_leads_updated_at') THEN
        CREATE TRIGGER update_property_leads_updated_at BEFORE UPDATE ON public.property_leads
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- Row Level Security (RLS) - Only enable for new tables
ALTER TABLE public.deal_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_intelligence ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deal_stage_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.investor_criteria ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.property_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deal_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sourcing_activity ENABLE ROW LEVEL SECURITY;

-- ================================
-- RLS POLICIES FOR NEW TABLES ONLY
-- ================================

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
END $$;

-- Market intelligence policies (read-only for most users)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view market intelligence' AND tablename = 'market_intelligence') THEN
        CREATE POLICY "Users can view market intelligence" ON public.market_intelligence
            FOR SELECT USING (true);
    END IF;
END $$;

-- Insert sample data (optional - remove in production)
-- Note: Only insert if your profiles table is empty
-- INSERT INTO public.profiles (id, email, full_name, role, tier) VALUES
--     ('00000000-0000-0000-0000-000000000001', 'admin@nxtrix.com', 'NxTrix Admin', 'admin', 'enterprise'),
--     ('00000000-0000-0000-0000-000000000002', 'analyst@nxtrix.com', 'Senior Analyst', 'analyst', 'pro')
-- ON CONFLICT (id) DO NOTHING;