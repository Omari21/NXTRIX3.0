-- Email automation database migration
-- Run this SQL in your Supabase SQL editor

-- Add email tracking columns to waitlist table
ALTER TABLE waitlist 
ADD COLUMN IF NOT EXISTS credentials_sent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS launch_notified BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS temporary_password TEXT,
ADD COLUMN IF NOT EXISTS access_date TIMESTAMPTZ;

-- Create email_logs table for tracking all email communications
CREATE TABLE IF NOT EXISTS email_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    message_id TEXT,
    error_message TEXT,
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_email_logs_email ON email_logs(email);
CREATE INDEX IF NOT EXISTS idx_email_logs_type ON email_logs(type);
CREATE INDEX IF NOT EXISTS idx_waitlist_credentials_sent ON waitlist(credentials_sent);
CREATE INDEX IF NOT EXISTS idx_waitlist_launch_notified ON waitlist(launch_notified);

-- Enable RLS
ALTER TABLE email_logs ENABLE ROW LEVEL SECURITY;

-- Allow service role to manage email logs
CREATE POLICY "Service role can manage email logs" ON email_logs
    FOR ALL USING (auth.role() = 'service_role');

-- Update existing records
UPDATE waitlist 
SET credentials_sent = FALSE, launch_notified = FALSE 
WHERE credentials_sent IS NULL OR launch_notified IS NULL;