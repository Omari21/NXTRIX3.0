const { createClient } = require('@supabase/supabase-js');

// Initialize Supabase client using environment variables
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY
);

// Generate secure temporary password
function generateTemporaryPassword(length = 12) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

// Format date for display
function formatDate(date) {
  return new Date(date).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

exports.handler = async (event, context) => {
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
      },
      body: '',
    };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    const { campaign_type, auth_token } = JSON.parse(event.body);

    // Simple auth check using environment variable
    if (auth_token !== process.env.ADMIN_AUTH_TOKEN) {
      return {
        statusCode: 401,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: 'Unauthorized' }),
      };
    }

    let results = { success: 0, failed: 0, errors: [] };

    if (campaign_type === 'login_credentials') {
      results = await sendLoginCredentials();
    } else if (campaign_type === 'launch_notification') {
      results = await sendLaunchNotifications();
    } else {
      throw new Error(`Unknown campaign type: ${campaign_type}`);
    }

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        success: true,
        campaign_type,
        results
      }),
    };

  } catch (error) {
    console.error('❌ Email campaign error:', error);
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        error: 'Campaign failed',
        details: error.message
      }),
    };
  }
};

async function sendLoginCredentials() {
  console.log('🔑 Sending login credentials to all paid founders...');
  
  const { data: founders, error } = await supabase
    .from('waitlist')
    .select('id, name, email, tier, billing')
    .eq('payment_status', 'paid')
    .eq('credentials_sent', false);

  if (error) {
    throw new Error(`Failed to fetch founders: ${error.message}`);
  }

  if (!founders || founders.length === 0) {
    return { success: 0, failed: 0, message: 'No founders need credentials' };
  }

  const results = { success: 0, failed: 0, errors: [] };
  const accessDate = new Date();
  accessDate.setDate(accessDate.getDate() + 14);

  for (const founder of founders) {
    try {
      const temporaryPassword = generateTemporaryPassword();
      
      const emailResponse = await fetch(`${process.env.URL}/.netlify/functions/send_email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'login_credentials',
          email: founder.email,
          data: {
            name: founder.name || 'NXTRIX Founder',
            email: founder.email,
            temporaryPassword,
            accessDate: formatDate(accessDate)
          }
        })
      });

      if (emailResponse.ok) {
        await supabase
          .from('waitlist')
          .update({
            credentials_sent: true,
            temporary_password: temporaryPassword,
            access_date: accessDate.toISOString(),
            updated_at: new Date().toISOString()
          })
          .eq('id', founder.id);

        console.log(`✅ Credentials sent to: ${founder.email}`);
        results.success++;
      } else {
        results.failed++;
        results.errors.push(`${founder.email}: Failed to send`);
      }
    } catch (error) {
      results.failed++;
      results.errors.push(`${founder.email}: ${error.message}`);
    }
  }

  return results;
}

async function sendLaunchNotifications() {
  console.log('🚀 Sending launch notifications to all paid founders...');
  
  const { data: founders, error } = await supabase
    .from('waitlist')
    .select('id, name, email, tier, billing')
    .eq('payment_status', 'paid')
    .eq('launch_notified', false);

  if (error) {
    throw new Error(`Failed to fetch founders: ${error.message}`);
  }

  if (!founders || founders.length === 0) {
    return { success: 0, failed: 0, message: 'No founders need launch notifications' };
  }

  const results = { success: 0, failed: 0, errors: [] };

  for (const founder of founders) {
    try {
      const emailResponse = await fetch(`${process.env.URL}/.netlify/functions/send_email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'launch_notification',
          email: founder.email,
          data: {
            name: founder.name || 'NXTRIX Founder',
            email: founder.email,
            tier: founder.tier || 'business',
            billing: founder.billing || 'monthly'
          }
        })
      });

      if (emailResponse.ok) {
        await supabase
          .from('waitlist')
          .update({
            launch_notified: true,
            updated_at: new Date().toISOString()
          })
          .eq('id', founder.id);

        console.log(`✅ Launch notification sent to: ${founder.email}`);
        results.success++;
      } else {
        results.failed++;
        results.errors.push(`${founder.email}: Failed to send`);
      }
    } catch (error) {
      results.failed++;
      results.errors.push(`${founder.email}: ${error.message}`);
    }
  }

  return results;
}