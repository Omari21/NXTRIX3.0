-- NXTRIX CRM - Incremental Schema Update
-- Use this if you want to add missing columns to existing tables

-- Add missing columns to deals table if they don't exist
DO $$ 
BEGIN
    -- Add stage column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'deals' AND column_name = 'stage') THEN
        ALTER TABLE public.deals ADD COLUMN stage VARCHAR(50) DEFAULT 'prospect' 
        CHECK (stage IN ('prospect', 'qualified', 'due_diligence', 'negotiation', 'closing', 'closed', 'lost'));
    END IF;
    
    -- Add financial columns if they don't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'deals' AND column_name = 'purchase_price') THEN
        ALTER TABLE public.deals ADD COLUMN purchase_price DECIMAL(15,2);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'deals' AND column_name = 'arv') THEN
        ALTER TABLE public.deals ADD COLUMN arv DECIMAL(15,2);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'deals' AND column_name = 'repair_costs') THEN
        ALTER TABLE public.deals ADD COLUMN repair_costs DECIMAL(15,2);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'deals' AND column_name = 'monthly_rent') THEN
        ALTER TABLE public.deals ADD COLUMN monthly_rent DECIMAL(15,2);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'deals' AND column_name = 'closing_costs') THEN
        ALTER TABLE public.deals ADD COLUMN closing_costs DECIMAL(15,2);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'deals' AND column_name = 'annual_taxes') THEN
        ALTER TABLE public.deals ADD COLUMN annual_taxes DECIMAL(15,2);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'deals' AND column_name = 'insurance') THEN
        ALTER TABLE public.deals ADD COLUMN insurance DECIMAL(15,2);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'deals' AND column_name = 'hoa_fees') THEN
        ALTER TABLE public.deals ADD COLUMN hoa_fees DECIMAL(15,2);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'deals' AND column_name = 'vacancy_rate') THEN
        ALTER TABLE public.deals ADD COLUMN vacancy_rate DECIMAL(5,2) DEFAULT 5.0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'deals' AND column_name = 'neighborhood_grade') THEN
        ALTER TABLE public.deals ADD COLUMN neighborhood_grade VARCHAR(10) DEFAULT 'B';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'deals' AND column_name = 'condition') THEN
        ALTER TABLE public.deals ADD COLUMN condition VARCHAR(50) DEFAULT 'Good';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'deals' AND column_name = 'market_trend') THEN
        ALTER TABLE public.deals ADD COLUMN market_trend VARCHAR(50) DEFAULT 'Stable';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'deals' AND column_name = 'ai_score') THEN
        ALTER TABLE public.deals ADD COLUMN ai_score INTEGER DEFAULT 0 CHECK (ai_score >= 0 AND ai_score <= 100);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'deals' AND column_name = 'probability') THEN
        ALTER TABLE public.deals ADD COLUMN probability INTEGER DEFAULT 50 CHECK (probability >= 0 AND probability <= 100);
    END IF;
END $$;

-- Create indexes safely
CREATE INDEX IF NOT EXISTS idx_deals_stage ON public.deals(stage);
CREATE INDEX IF NOT EXISTS idx_deals_purchase_price ON public.deals(purchase_price);
CREATE INDEX IF NOT EXISTS idx_deals_arv ON public.deals(arv);

-- Enable RLS on deals table
ALTER TABLE public.deals ENABLE ROW LEVEL SECURITY;

-- Create or replace policies
DROP POLICY IF EXISTS "Users can view own deals" ON public.deals;
DROP POLICY IF EXISTS "Users can insert own deals" ON public.deals;
DROP POLICY IF EXISTS "Users can update own deals" ON public.deals;
DROP POLICY IF EXISTS "Users can delete own deals" ON public.deals;

CREATE POLICY "Users can view own deals" ON public.deals FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own deals" ON public.deals FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own deals" ON public.deals FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own deals" ON public.deals FOR DELETE USING (auth.uid() = user_id);