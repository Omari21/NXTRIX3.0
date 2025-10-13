const { createClient } = require('@supabase/supabase-js');

// Initialize Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL || 'https://ucrtaeoocwymzlykxgrf.supabase.co',
  process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVjcnRhZW9vY3d5bXpseWt4Z3JmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwNzM4MTIsImV4cCI6MjA2OTY0OTgxMn0.ZNjBkcR8vw00wmDcSYh-b1KdIel5233euuCToX-9-Lk'
);

exports.handler = async (event, context) => {
  // Handle CORS preflight
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Origin',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
      },
      body: '',
    };
  }

  // Only allow POST requests
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    const {
      tier,
      billing,
      customer_email,
      name,
      company,
      investor_type,
      experience,
      notes
    } = JSON.parse(event.body);

    // Validate required fields
    if (!customer_email || !name || !tier) {
      return {
        statusCode: 400,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ error: 'Missing required fields: email, name, or tier' }),
      };
    }

    // Prepare signup data for database
    const signupData = {
      name: name.trim(),
      email: customer_email.trim().toLowerCase(),
      company: company || '',
      plan: `${tier}-${billing}`, // e.g., "team-monthly"
      tier: tier,
      billing: billing || 'monthly',
      investor_type: investor_type || '',
      experience: experience || '',
      notes: notes || '',
      status: 'pending_payment',
      founders_pricing: true,
      created_at: new Date().toISOString(),
      payment_status: 'pending'
    };

    console.log('💾 Saving signup data:', { ...signupData, email: '***@***' });

    // Save to Supabase waitlist table (creates or updates)
    const { data, error } = await supabase
      .from('waitlist')
      .upsert(signupData, { 
        onConflict: 'email',
        ignoreDuplicates: false 
      })
      .select();

    if (error) {
      console.error('❌ Supabase error:', error);
      
      // Handle common errors gracefully
      if (error.code === '23505') { // Duplicate key
        console.log('✅ User already exists, updating record');
        // This is actually success - user is updating their info
      } else {
        throw error;
      }
    }

    console.log('✅ Signup saved successfully:', data?.[0]?.id || 'existing user');

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        success: true,
        message: 'Signup data saved successfully',
        user_id: data?.[0]?.id,
        next_step: 'payment_setup'
      }),
    };

  } catch (error) {
    console.error('❌ Signup error:', error);
    
    return {
      statusCode: 500,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        error: 'Failed to save signup data',
        details: error.message
      }),
    };
  }
};