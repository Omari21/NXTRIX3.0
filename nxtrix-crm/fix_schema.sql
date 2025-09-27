-- NXTRIX CRM Database Schema Fix
-- Run this in your Supabase SQL editor to fix the missing ai_score column

-- First, let's check if the tables exist and add missing columns
-- This is safe to run multiple times

-- Enable UUID extension (safe to run multiple times)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (to start fresh)
DROP TABLE IF EXISTS portfolio CASCADE;
DROP TABLE IF EXISTS investors CASCADE;
DROP TABLE IF EXISTS deals CASCADE;

-- Recreate Deals table with all required columns
CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    address TEXT NOT NULL,
    property_type TEXT NOT NULL,
    purchase_price DECIMAL(12,2) NOT NULL DEFAULT 0,
    arv DECIMAL(12,2) NOT NULL DEFAULT 0,
    repair_costs DECIMAL(12,2) NOT NULL DEFAULT 0,
    monthly_rent DECIMAL(10,2) NOT NULL DEFAULT 0,
    closing_costs DECIMAL(10,2) NOT NULL DEFAULT 0,
    annual_taxes DECIMAL(10,2) NOT NULL DEFAULT 0,
    insurance DECIMAL(10,2) NOT NULL DEFAULT 0,
    hoa_fees DECIMAL(10,2) NOT NULL DEFAULT 0,
    vacancy_rate DECIMAL(5,2) NOT NULL DEFAULT 5.0,
    neighborhood_grade TEXT NOT NULL DEFAULT 'B',
    condition TEXT NOT NULL DEFAULT 'Good',
    market_trend TEXT NOT NULL DEFAULT 'Stable',
    ai_score INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'New',
    notes TEXT,
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recreate Investors table
CREATE TABLE investors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    investment_range_min DECIMAL(12,2) NOT NULL DEFAULT 0,
    investment_range_max DECIMAL(12,2) NOT NULL DEFAULT 0,
    preferred_markets TEXT,
    deal_types TEXT,
    success_rate DECIMAL(5,2) NOT NULL DEFAULT 0,
    total_investments INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'Active',
    notes TEXT,
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recreate Portfolio table
CREATE TABLE portfolio (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    investor_id UUID REFERENCES investors(id) ON DELETE SET NULL,
    investment_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    ownership_percentage DECIMAL(5,2) NOT NULL DEFAULT 0,
    entry_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    exit_date TIMESTAMP WITH TIME ZONE,
    current_value DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_return DECIMAL(12,2) NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'Active',
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_deals_user_id ON deals(user_id);
CREATE INDEX idx_deals_status ON deals(status);
CREATE INDEX idx_deals_ai_score ON deals(ai_score);
CREATE INDEX idx_deals_created_at ON deals(created_at);

CREATE INDEX idx_investors_user_id ON investors(user_id);
CREATE INDEX idx_investors_status ON investors(status);
CREATE INDEX idx_investors_email ON investors(email);

CREATE INDEX idx_portfolio_user_id ON portfolio(user_id);
CREATE INDEX idx_portfolio_deal_id ON portfolio(deal_id);
CREATE INDEX idx_portfolio_investor_id ON portfolio(investor_id);
CREATE INDEX idx_portfolio_status ON portfolio(status);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_deals_updated_at BEFORE UPDATE ON deals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_investors_updated_at BEFORE UPDATE ON investors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_portfolio_updated_at BEFORE UPDATE ON portfolio FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE investors ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio ENABLE ROW LEVEL SECURITY;

-- Create policies for Row Level Security
CREATE POLICY "Allow all operations on deals" ON deals FOR ALL USING (true);
CREATE POLICY "Allow all operations on investors" ON investors FOR ALL USING (true);
CREATE POLICY "Allow all operations on portfolio" ON portfolio FOR ALL USING (true);

-- Insert sample data
INSERT INTO deals (address, property_type, purchase_price, arv, repair_costs, monthly_rent, ai_score, status) VALUES
('123 Oak Street, Austin TX', 'Single Family', 180000, 250000, 25000, 2200, 94, 'Under Contract'),
('456 Pine Avenue, Nashville TN', 'Duplex', 320000, 400000, 35000, 3200, 88, 'Analyzing'),
('789 Maple Drive, Tampa FL', 'Single Family', 95000, 150000, 15000, 1400, 91, 'Closed'),
('321 Elm Street, Phoenix AZ', 'Triplex', 650000, 800000, 45000, 5400, 86, 'Negotiating');

INSERT INTO investors (name, email, investment_range_min, investment_range_max, preferred_markets, deal_types, success_rate, total_investments, status) VALUES
('John Smith Capital', 'john@smithcapital.com', 200000, 800000, 'Austin, Nashville', 'Fix & Flip, Buy & Hold', 94.5, 12, 'Active'),
('Sarah Johnson Fund', 'sarah@johnsonfund.com', 100000, 500000, 'Tampa, Phoenix', 'Buy & Hold, Wholesale', 87.2, 8, 'Active'),
('Mike Chen Investments', 'mike@cheninvest.com', 500000, 2000000, 'Austin, Denver', 'Fix & Flip, Commercial', 91.8, 15, 'Active'),
('Lisa Rodriguez Group', 'lisa@rodriguezgroup.com', 150000, 600000, 'Nashville, Atlanta', 'Multi-Family, Buy & Hold', 89.3, 10, 'Active'),
('David Wilson Partners', 'david@wilsonpartners.com', 1000000, 5000000, 'Multi-Market', 'Commercial, Development', 96.1, 22, 'Active');

-- Verify the schema was created correctly
SELECT 'Tables created successfully' AS status;
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('deals', 'investors', 'portfolio') 
AND column_name = 'ai_score';