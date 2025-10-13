const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const { createClient } = require('@supabase/supabase-js');

// Initialize Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL || 'https://ucrtaeoocwymzlykxgrf.supabase.co',
  process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY
);

exports.handler = async (event, context) => {
  // Only allow POST requests
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  const sig = event.headers['stripe-signature'];
  let stripeEvent;

  try {
    // Verify webhook signature
    stripeEvent = stripe.webhooks.constructEvent(
      event.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    console.error('❌ Webhook signature verification failed:', err.message);
    return {
      statusCode: 400,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: 'Invalid signature' }),
    };
  }

  console.log('🎣 Received webhook:', stripeEvent.type);

  try {
    switch (stripeEvent.type) {
      case 'checkout.session.completed':
        await handleCheckoutCompleted(stripeEvent.data.object);
        break;
      
      case 'invoice.payment_succeeded':
        await handlePaymentSucceeded(stripeEvent.data.object);
        break;
      
      case 'customer.subscription.created':
        await handleSubscriptionCreated(stripeEvent.data.object);
        break;
      
      case 'customer.subscription.updated':
        await handleSubscriptionUpdated(stripeEvent.data.object);
        break;
      
      case 'customer.subscription.deleted':
        await handleSubscriptionCancelled(stripeEvent.data.object);
        break;
      
      default:
        console.log(`⚠️ Unhandled event type: ${stripeEvent.type}`);
    }

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ received: true }),
    };

  } catch (error) {
    console.error('❌ Webhook processing error:', error);
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: 'Webhook processing failed' }),
    };
  }
};

async function handleCheckoutCompleted(session) {
  console.log('✅ Checkout completed:', session.id);
  
  const customerEmail = session.customer_details?.email || session.metadata?.customer_email;
  
  if (!customerEmail) {
    console.error('❌ No customer email found in session');
    return;
  }

  // Get user details for email personalization
  const { data: userData, error: fetchError } = await supabase
    .from('waitlist')
    .select('name, tier, billing')
    .eq('email', customerEmail)
    .single();

  // Update user record
  const { error } = await supabase
    .from('waitlist')
    .update({
      payment_status: 'paid',
      stripe_subscription_id: session.subscription,
      access_granted: true,
      paid_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })
    .eq('email', customerEmail);

  if (error) {
    console.error('❌ Failed to update user payment status:', error);
  } else {
    console.log('✅ Updated payment status for:', customerEmail);
    
    // Send welcome email automatically
    if (userData && !fetchError) {
      try {
        const emailResponse = await fetch(`${process.env.URL}/.netlify/functions/send_email`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            type: 'welcome',
            email: customerEmail,
            data: {
              name: userData.name || 'NXTRIX Founder',
              email: customerEmail,
              tier: userData.tier || 'business',
              billing: userData.billing || 'monthly'
            }
          })
        });

        if (emailResponse.ok) {
          console.log('✅ Welcome email sent successfully to:', customerEmail);
        } else {
          console.error('❌ Failed to send welcome email:', await emailResponse.text());
        }
      } catch (emailError) {
        console.error('❌ Welcome email error:', emailError);
      }
    }
  }
}

async function handlePaymentSucceeded(invoice) {
  console.log('💰 Payment succeeded:', invoice.id);
  
  const subscription = await stripe.subscriptions.retrieve(invoice.subscription);
  const customer = await stripe.customers.retrieve(subscription.customer);
  
  // Update user record with successful payment
  const { error } = await supabase
    .from('waitlist')
    .update({
      payment_status: 'active',
      last_payment_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })
    .eq('stripe_customer_id', customer.id);

  if (error) {
    console.error('❌ Failed to update payment record:', error);
  } else {
    console.log('✅ Updated payment record for customer:', customer.id);
  }
}

async function handleSubscriptionCreated(subscription) {
  console.log('🎯 Subscription created:', subscription.id);
  
  const customer = await stripe.customers.retrieve(subscription.customer);
  
  const { error } = await supabase
    .from('waitlist')
    .update({
      stripe_subscription_id: subscription.id,
      subscription_status: subscription.status,
      access_granted: true,
      updated_at: new Date().toISOString()
    })
    .eq('stripe_customer_id', customer.id);

  if (error) {
    console.error('❌ Failed to update subscription record:', error);
  } else {
    console.log('✅ Updated subscription record for customer:', customer.id);
  }
}

async function handleSubscriptionUpdated(subscription) {
  console.log('🔄 Subscription updated:', subscription.id);
  
  const customer = await stripe.customers.retrieve(subscription.customer);
  
  const { error } = await supabase
    .from('waitlist')
    .update({
      subscription_status: subscription.status,
      updated_at: new Date().toISOString()
    })
    .eq('stripe_customer_id', customer.id);

  if (error) {
    console.error('❌ Failed to update subscription status:', error);
  }
}

async function handleSubscriptionCancelled(subscription) {
  console.log('❌ Subscription cancelled:', subscription.id);
  
  const customer = await stripe.customers.retrieve(subscription.customer);
  
  const { error } = await supabase
    .from('waitlist')
    .update({
      subscription_status: 'cancelled',
      access_granted: false,
      updated_at: new Date().toISOString()
    })
    .eq('stripe_customer_id', customer.id);

  if (error) {
    console.error('❌ Failed to update cancellation record:', error);
  } else {
    console.log('✅ Updated cancellation record for customer:', customer.id);
  }
}