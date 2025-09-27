-- NxTrix CRM Database Schema Extensions - PHASE 3B & 3D
-- AI Enhancement and Advanced Automation Extensions
-- Updated: September 16, 2025

-- =====================================
-- PHASE 3B: AI ENHANCEMENT TABLES
-- =====================================

-- AI deal analysis results table
CREATE TABLE IF NOT EXISTS public.ai_deal_analysis (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    deal_id UUID,
    analysis_type TEXT NOT NULL, -- 'gpt_analysis', 'automated_scoring', 'risk_assessment'
    analysis_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    input_data JSONB DEFAULT '{}',
    ai_response JSONB DEFAULT '{}',
    confidence_score DECIMAL(5,2),
    analysis_summary TEXT,
    key_insights JSONB DEFAULT '{}',
    risk_factors JSONB DEFAULT '{}',
    recommendations JSONB DEFAULT '{}',
    model_version TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Natural language search history
CREATE TABLE IF NOT EXISTS public.search_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID,
    search_query TEXT NOT NULL,
    search_type TEXT NOT NULL, -- 'natural_language', 'filtered', 'ai_recommended'
    search_results JSONB DEFAULT '{}',
    result_count INTEGER DEFAULT 0,
    search_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    execution_time_ms INTEGER,
    filters_applied JSONB DEFAULT '{}'
);

-- Investment recommendations table
CREATE TABLE IF NOT EXISTS public.investment_recommendations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    property_lead_id UUID REFERENCES public.property_leads(lead_id) ON DELETE CASCADE,
    investor_id UUID,
    recommendation_type TEXT NOT NULL, -- 'ai_generated', 'criteria_match', 'market_based'
    recommendation_score DECIMAL(5,2) NOT NULL,
    reasoning TEXT,
    key_factors JSONB DEFAULT '{}',
    risk_assessment JSONB DEFAULT '{}',
    financial_projections JSONB DEFAULT '{}',
    market_analysis JSONB DEFAULT '{}',
    generated_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_date TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'active', -- 'active', 'expired', 'accepted', 'rejected'
    investor_feedback TEXT,
    feedback_date TIMESTAMP WITH TIME ZONE
);

-- AI model performance tracking
CREATE TABLE IF NOT EXISTS public.ai_model_performance (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    performance_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    accuracy_score DECIMAL(5,2),
    precision_score DECIMAL(5,2),
    recall_score DECIMAL(5,2),
    f1_score DECIMAL(5,2),
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    false_positives INTEGER DEFAULT 0,
    false_negatives INTEGER DEFAULT 0,
    average_confidence DECIMAL(5,2),
    training_data_size INTEGER,
    performance_metrics JSONB DEFAULT '{}'
);

-- Deal scoring history
CREATE TABLE IF NOT EXISTS public.deal_scoring_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    deal_id UUID,
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
-- PHASE 3D: ADVANCED AUTOMATION TABLES
-- =====================================

-- Automation rules (already created in automation system, but ensuring consistency)
CREATE TABLE IF NOT EXISTS public.automation_rules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    trigger_type TEXT NOT NULL, -- 'deal_status_change', 'time_based', 'data_change', 'manual'
    trigger_conditions JSONB DEFAULT '{}',
    actions JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_executed TIMESTAMP WITH TIME ZONE,
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0
);

-- Email templates
CREATE TABLE IF NOT EXISTS public.email_templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    template_type TEXT NOT NULL, -- 'deal_update', 'investor_alert', 'follow_up', 'marketing'
    variables JSONB DEFAULT '[]',
    html_content TEXT,
    is_active BOOLEAN DEFAULT true,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE
);

-- Document templates
CREATE TABLE IF NOT EXISTS public.document_templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    template_type TEXT NOT NULL, -- 'contract', 'analysis', 'report', 'invoice', 'letter'
    content TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    document_format TEXT DEFAULT 'pdf', -- 'pdf', 'docx', 'html'
    is_active BOOLEAN DEFAULT true,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    usage_count INTEGER DEFAULT 0
);

-- Generated documents tracking
CREATE TABLE IF NOT EXISTS public.generated_documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    template_id UUID REFERENCES public.document_templates(id) ON DELETE SET NULL,
    deal_id UUID,
    document_name TEXT NOT NULL,
    document_type TEXT NOT NULL,
    file_path TEXT,
    file_size INTEGER,
    generated_by UUID,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    download_count INTEGER DEFAULT 0,
    last_downloaded TIMESTAMP WITH TIME ZONE,
    variables_used JSONB DEFAULT '{}',
    status TEXT DEFAULT 'generated' -- 'generated', 'sent', 'signed', 'archived'
);

-- Email campaigns
CREATE TABLE IF NOT EXISTS public.email_campaigns (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    template_id UUID REFERENCES public.email_templates(id) ON DELETE SET NULL,
    recipient_list JSONB DEFAULT '[]',
    recipient_filters JSONB DEFAULT '{}',
    schedule_time TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'draft', -- 'draft', 'scheduled', 'sending', 'sent', 'paused', 'cancelled'
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sent_at TIMESTAMP WITH TIME ZONE,
    sent_count INTEGER DEFAULT 0,
    delivered_count INTEGER DEFAULT 0,
    opened_count INTEGER DEFAULT 0,
    clicked_count INTEGER DEFAULT 0,
    bounced_count INTEGER DEFAULT 0,
    unsubscribed_count INTEGER DEFAULT 0
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
    execution_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0
);

-- Workflow steps
CREATE TABLE IF NOT EXISTS public.workflow_steps (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    workflow_id UUID REFERENCES public.automation_workflows(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    step_type TEXT NOT NULL, -- 'email', 'task', 'document', 'api_call', 'delay', 'condition'
    step_name TEXT NOT NULL,
    step_config JSONB DEFAULT '{}',
    conditions JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Automation execution log
CREATE TABLE IF NOT EXISTS public.automation_execution_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    automation_type TEXT NOT NULL, -- 'rule', 'workflow', 'campaign'
    automation_id UUID,
    execution_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    execution_end TIMESTAMP WITH TIME ZONE,
    status TEXT NOT NULL, -- 'started', 'completed', 'failed', 'partially_completed'
    trigger_data JSONB DEFAULT '{}',
    execution_details JSONB DEFAULT '{}',
    error_message TEXT,
    steps_completed INTEGER DEFAULT 0,
    total_steps INTEGER DEFAULT 0,
    execution_time_ms INTEGER
);

-- Tasks created by automation
CREATE TABLE IF NOT EXISTS public.automated_tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    automation_id UUID,
    automation_type TEXT, -- 'rule', 'workflow'
    task_title TEXT NOT NULL,
    task_description TEXT,
    assigned_to UUID,
    due_date TIMESTAMP WITH TIME ZONE,
    priority TEXT DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    status TEXT DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'cancelled'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    deal_id UUID,
    related_entity_type TEXT,
    related_entity_id UUID
);

-- API integrations tracking
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
-- INDEXES FOR PERFORMANCE
-- =====================================

-- AI Enhancement indexes
CREATE INDEX IF NOT EXISTS idx_ai_deal_analysis_deal_id ON public.ai_deal_analysis(deal_id);
CREATE INDEX IF NOT EXISTS idx_ai_deal_analysis_type ON public.ai_deal_analysis(analysis_type);
CREATE INDEX IF NOT EXISTS idx_ai_deal_analysis_date ON public.ai_deal_analysis(analysis_date);

CREATE INDEX IF NOT EXISTS idx_search_history_user_id ON public.search_history(user_id);
CREATE INDEX IF NOT EXISTS idx_search_history_date ON public.search_history(search_date);

CREATE INDEX IF NOT EXISTS idx_investment_recommendations_property ON public.investment_recommendations(property_lead_id);
CREATE INDEX IF NOT EXISTS idx_investment_recommendations_investor ON public.investment_recommendations(investor_id);
CREATE INDEX IF NOT EXISTS idx_investment_recommendations_score ON public.investment_recommendations(recommendation_score);

CREATE INDEX IF NOT EXISTS idx_deal_scoring_deal_id ON public.deal_scoring_history(deal_id);
CREATE INDEX IF NOT EXISTS idx_deal_scoring_date ON public.deal_scoring_history(scoring_date);

-- Automation indexes
CREATE INDEX IF NOT EXISTS idx_automation_rules_active ON public.automation_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_automation_rules_trigger ON public.automation_rules(trigger_type);

CREATE INDEX IF NOT EXISTS idx_email_templates_type ON public.email_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_email_templates_active ON public.email_templates(is_active);

CREATE INDEX IF NOT EXISTS idx_document_templates_type ON public.document_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_document_templates_active ON public.document_templates(is_active);

CREATE INDEX IF NOT EXISTS idx_generated_documents_template ON public.generated_documents(template_id);
CREATE INDEX IF NOT EXISTS idx_generated_documents_deal ON public.generated_documents(deal_id);

CREATE INDEX IF NOT EXISTS idx_email_campaigns_status ON public.email_campaigns(status);
CREATE INDEX IF NOT EXISTS idx_email_campaigns_schedule ON public.email_campaigns(schedule_time);

CREATE INDEX IF NOT EXISTS idx_campaign_recipients_campaign ON public.campaign_recipients(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_recipients_status ON public.campaign_recipients(status);

CREATE INDEX IF NOT EXISTS idx_workflow_steps_workflow ON public.workflow_steps(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_steps_order ON public.workflow_steps(step_order);

CREATE INDEX IF NOT EXISTS idx_automation_log_type ON public.automation_execution_log(automation_type);
CREATE INDEX IF NOT EXISTS idx_automation_log_status ON public.automation_execution_log(status);
CREATE INDEX IF NOT EXISTS idx_automation_log_date ON public.automation_execution_log(execution_start);

CREATE INDEX IF NOT EXISTS idx_automated_tasks_assigned ON public.automated_tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_automated_tasks_status ON public.automated_tasks(status);
CREATE INDEX IF NOT EXISTS idx_automated_tasks_due ON public.automated_tasks(due_date);

-- =====================================
-- UPDATED_AT TRIGGERS
-- =====================================

-- Create triggers for updated_at columns
DO $$
BEGIN
    -- AI Enhancement triggers
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

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_automation_workflows_updated_at') THEN
        CREATE TRIGGER update_automation_workflows_updated_at BEFORE UPDATE ON public.automation_workflows
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_user_automation_preferences_updated_at') THEN
        CREATE TRIGGER update_user_automation_preferences_updated_at BEFORE UPDATE ON public.user_automation_preferences
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- =====================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================

-- Enable RLS for all new tables
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

-- ================================
-- RLS POLICIES FOR NEW TABLES
-- ================================

-- AI Deal Analysis policies
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view all ai deal analysis' AND tablename = 'ai_deal_analysis') THEN
        CREATE POLICY "Users can view all ai deal analysis" ON public.ai_deal_analysis
            FOR SELECT USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can create ai deal analysis' AND tablename = 'ai_deal_analysis') THEN
        CREATE POLICY "Users can create ai deal analysis" ON public.ai_deal_analysis
            FOR INSERT WITH CHECK (true);
    END IF;
END $$;

-- Automation Rules policies
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view all automation rules' AND tablename = 'automation_rules') THEN
        CREATE POLICY "Users can view all automation rules" ON public.automation_rules
            FOR SELECT USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can create automation rules' AND tablename = 'automation_rules') THEN
        CREATE POLICY "Users can create automation rules" ON public.automation_rules
            FOR INSERT WITH CHECK (true);
    END IF;
END $$;

-- Email Templates policies
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view all email templates' AND tablename = 'email_templates') THEN
        CREATE POLICY "Users can view all email templates" ON public.email_templates
            FOR SELECT USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can create email templates' AND tablename = 'email_templates') THEN
        CREATE POLICY "Users can create email templates" ON public.email_templates
            FOR INSERT WITH CHECK (true);
    END IF;
END $$;

-- Investment Recommendations policies
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view all investment recommendations' AND tablename = 'investment_recommendations') THEN
        CREATE POLICY "Users can view all investment recommendations" ON public.investment_recommendations
            FOR SELECT USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can create investment recommendations' AND tablename = 'investment_recommendations') THEN
        CREATE POLICY "Users can create investment recommendations" ON public.investment_recommendations
            FOR INSERT WITH CHECK (true);
    END IF;
END $$;

-- =====================================
-- SAMPLE DATA FOR DEMONSTRATION
-- =====================================

-- Sample AI model performance data
INSERT INTO public.ai_model_performance (model_name, model_version, accuracy_score, precision_score, recall_score, f1_score, total_predictions, correct_predictions)
VALUES 
    ('GPT-4 Deal Analyzer', 'v1.0', 85.5, 82.3, 88.7, 85.4, 1000, 855),
    ('ROI Predictor ML', 'v2.1', 92.1, 89.4, 94.8, 92.0, 2500, 2303),
    ('Risk Assessment AI', 'v1.5', 78.9, 75.6, 82.3, 78.8, 1500, 1184)
ON CONFLICT DO NOTHING;

-- Sample email templates
INSERT INTO public.email_templates (id, name, subject, body, template_type, variables)
VALUES 
    (gen_random_uuid(), 'Deal Alert Template', 'New Investment Opportunity: {{deal_address}}', 
     'Hi {{investor_name}},\n\nWe found a new investment opportunity that matches your criteria:\n\nProperty: {{deal_address}}\nPrice: {{purchase_price}}\nExpected ROI: {{roi}}%\n\nBest regards,\nNxTrix Team',
     'investor_alert', '["investor_name", "deal_address", "purchase_price", "roi"]'),
    
    (gen_random_uuid(), 'Deal Status Update', 'Deal Update: {{deal_address}}', 
     'Hi {{investor_name}},\n\nYour deal at {{deal_address}} has been updated:\n\nNew Status: {{new_status}}\nNext Steps: {{next_steps}}\n\nBest regards,\nNxTrix Team',
     'deal_update', '["investor_name", "deal_address", "new_status", "next_steps"]')
ON CONFLICT DO NOTHING;

-- Sample document templates
INSERT INTO public.document_templates (id, name, template_type, content, variables)
VALUES 
    (gen_random_uuid(), 'Investment Analysis Report', 'analysis', 
     'INVESTMENT ANALYSIS REPORT\n\nProperty: {{deal_address}}\nDate: {{analysis_date}}\n\nFINANCIAL SUMMARY\nPurchase Price: {{purchase_price}}\nAfter Repair Value: {{arv}}\nRepair Costs: {{repair_costs}}\nExpected ROI: {{roi}}%\n\nRECOMMENDATION\n{{recommendation}}',
     '["deal_address", "analysis_date", "purchase_price", "arv", "repair_costs", "roi", "recommendation"]'),
     
    (gen_random_uuid(), 'Purchase Contract', 'contract',
     'REAL ESTATE PURCHASE CONTRACT\n\nBuyer: {{buyer_name}}\nSeller: {{seller_name}}\nProperty: {{property_address}}\nPurchase Price: {{purchase_price}}\nClosing Date: {{closing_date}}\n\nTerms and Conditions:\n{{contract_terms}}',
     '["buyer_name", "seller_name", "property_address", "purchase_price", "closing_date", "contract_terms"]')
ON CONFLICT DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE public.ai_deal_analysis IS 'Stores AI-generated analysis results for deals including GPT insights and automated scoring';
COMMENT ON TABLE public.investment_recommendations IS 'AI-generated investment recommendations matched to investor criteria';
COMMENT ON TABLE public.automation_rules IS 'User-defined automation rules for CRM workflows';
COMMENT ON TABLE public.email_campaigns IS 'Email marketing campaigns with tracking and analytics';
COMMENT ON TABLE public.generated_documents IS 'Tracking table for all documents generated from templates';
COMMENT ON TABLE public.automation_execution_log IS 'Comprehensive log of all automation executions for monitoring and debugging';