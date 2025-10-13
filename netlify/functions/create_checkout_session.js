const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const { createClient } = require('@supabase/supabase-js');

// Initialize Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL || 'https://ucrtaeoocwymzlykxgrf.supabase.co',
  process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVjcnRhZW9vY3d5bXpseWt4Z3JmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwNzM4MTIsImV4cCI6MjA2OTY0OTgxMn0.ZNjBkcR8vw00wmDcSYh-b1KdIel5233euuCToX-9-Lk'
);

// Founders pricing tiers
const FOUNDERS_PRICING = {
  solo: {
    monthly: 5900, // $59.00 in cents
    annual: 70800, // $708.00 in cents
    name: 'Solo Founders'
  },
  team: {
    monthly: 8900, // $89.00 in cents
    annual: 106800, // $1068.00 in cents
    name: 'Team Founders'
  },
  business: {
    monthly: 14900, // $149.00 in cents
    annual: 178800, // $1788.00 in cents
    name: 'Business Founders'
  }
};

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
      customer_email,
      customer_name,
      tier,
      billing,
      company,
      success_url,
      cancel_url
    } = JSON.parse(event.body);

    // Validate required fields
    if (!customer_email || !customer_name || !tier || !billing) {
      return {
        statusCode: 400,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ error: 'Missing required fields' }),
      };
    }

    // Validate tier and billing
    if (!FOUNDERS_PRICING[tier] || !FOUNDERS_PRICING[tier][billing]) {
      return {
        statusCode: 400,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ error: 'Invalid tier or billing type' }),
      };
    }

    const pricing = FOUNDERS_PRICING[tier];
    const amount = pricing[billing];
    const planName = pricing.name;

    console.log('💳 Creating Stripe checkout for:', {
      email: customer_email,
      tier,
      billing,
      amount: amount / 100
    });

    // Create or retrieve customer
    let customer;
    try {
      const customers = await stripe.customers.list({
        email: customer_email,
        limit: 1
      });

      if (customers.data.length > 0) {
        customer = customers.data[0];
        console.log('✅ Found existing customer:', customer.id);
      } else {
        customer = await stripe.customers.create({
          email: customer_email,
          name: customer_name,
          metadata: {
            company: company || '',
            plan: `${tier}-${billing}`,
            founders_pricing: 'true',
            signup_date: new Date().toISOString()
          }
        });
        console.log('✅ Created new customer:', customer.id);
      }
    } catch (customerError) {
      console.error('❌ Customer creation error:', customerError);
      throw new Error('Failed to create customer');
    }

    // Create checkout session
    const session = await stripe.checkout.sessions.create({
      customer: customer.id,
      payment_method_types: ['card'],
      line_items: [
        {
          price_data: {
            currency: 'usd',
            product_data: {
              name: `NXTRIX CRM - ${planName}`,
              description: `${billing === 'annual' ? 'Annual' : 'Monthly'} subscription with founders pricing`,
              images: ['https://nxtrix.com/logo.png'], // Add your logo URL
            },
            unit_amount: amount,
            recurring: billing === 'monthly' ? {
              interval: 'month',
            } : {
              interval: 'year',
            },
          },
          quantity: 1,
        },
      ],
      mode: 'subscription',
      success_url: success_url || `${process.env.URL || 'https://nxtrix.com'}/success.html?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: cancel_url || `${process.env.URL || 'https://nxtrix.com'}/cancel.html`,
      metadata: {
        customer_email,
        tier,
        billing,
        plan: `${tier}-${billing}`,
        founders_pricing: 'true'
      },
      subscription_data: {
        metadata: {
          customer_email,
          tier,
          billing,
          founders_pricing: 'true'
        }
      },
      allow_promotion_codes: true,
      billing_address_collection: 'required',
      customer_update: {
        address: 'auto',
        name: 'auto'
      }
    });

    // Update user record with Stripe data
    try {
      await supabase
        .from('waitlist')
        .update({
          stripe_customer_id: customer.id,
          stripe_session_id: session.id,
          payment_status: 'checkout_created',
          updated_at: new Date().toISOString()
        })
        .eq('email', customer_email);
    } catch (updateError) {
      console.warn('⚠️ Failed to update user record:', updateError);
      // Don't fail the checkout for this
    }

    console.log('✅ Checkout session created:', session.id);

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        success: true,
        url: session.url,
        session_id: session.id,
        customer_id: customer.id
      }),
    };

  } catch (error) {
    console.error('❌ Stripe checkout error:', error);
    
    return {
      statusCode: 500,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        error: 'Failed to create checkout session',
        details: error.message
      }),
    };
  }
};