const nodemailer = require('nodemailer');
const { createClient } = require('@supabase/supabase-js');

// Initialize Supabase client using environment variables
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY
);

// Email templates
const EMAIL_TEMPLATES = {
  welcome: {
    subject: '🎉 Welcome to NXTRIX - Your Founders Journey Begins!',
    html: (data) => `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to NXTRIX</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f8f9fa; }
          .container { max-width: 600px; margin: 0 auto; background: white; }
          .header { background: linear-gradient(135deg, #7c5cff, #24d1ff); padding: 40px 30px; text-align: center; }
          .header h1 { color: white; margin: 0; font-size: 32px; font-weight: 700; }
          .header p { color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 18px; }
          .content { padding: 40px 30px; }
          .highlight-box { background: #f0f9ff; border-left: 4px solid #10b981; padding: 20px; margin: 20px 0; border-radius: 8px; }
          .feature-list { list-style: none; padding: 0; }
          .feature-list li { padding: 10px 0; border-bottom: 1px solid #eee; display: flex; align-items: center; }
          .feature-list li:last-child { border-bottom: none; }
          .feature-list li::before { content: '✓'; background: #10b981; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px; font-weight: bold; font-size: 14px; }
          .cta-button { display: inline-block; background: linear-gradient(135deg, #7c5cff, #24d1ff); color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0; }
          .footer { background: #f8f9fa; padding: 30px; text-align: center; color: #6b7280; font-size: 14px; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>🚀 Welcome to NXTRIX!</h1>
            <p>Your founders spot is secured - let's build the future together</p>
          </div>
          
          <div class="content">
            <h2>Hi ${data.name}! 👋</h2>
            
            <p>Congratulations! You've just secured your spot as a NXTRIX founder. You're now part of an exclusive group that will shape the future of real estate investment technology.</p>
            
            <div class="highlight-box">
              <h3>🎯 Your Founders Benefits</h3>
              <ul class="feature-list">
                <li>Lifetime founders pricing locked forever</li>
                <li>Early access 30 days before public launch</li>
                <li>Direct line to our development team</li>
                <li>Priority feature requests and feedback</li>
                <li>Exclusive founders-only community access</li>
                <li>White-glove onboarding and training</li>
              </ul>
            </div>
            
            <h3>📅 What Happens Next</h3>
            <p><strong>Next 2 Weeks:</strong> We'll send you login credentials and early access details.</p>
            <p><strong>Launch - 30 Days:</strong> Your exclusive early access begins with full platform functionality.</p>
            <p><strong>Public Launch:</strong> Platform goes live to the public, but you keep your founders pricing forever.</p>
            
            <div style="text-align: center;">
              <a href="https://nxtrix.com" class="cta-button">Visit NXTRIX Homepage</a>
            </div>
            
            <h3>💬 Stay Connected</h3>
            <p>Have questions? Reply to this email or reach out to us at <a href="mailto:support@nxtrix.com">support@nxtrix.com</a></p>
            
            <p>We're incredibly excited to have you on this journey with us!</p>
            
            <p>Best regards,<br>
            <strong>The NXTRIX Team</strong><br>
            Building the future of real estate investment</p>
          </div>
          
          <div class="footer">
            <p>© 2025 NXTRIX. All rights reserved.</p>
            <p>You're receiving this email because you joined NXTRIX as a founder.</p>
          </div>
        </div>
      </body>
      </html>
    `
  },
  
  login_credentials: {
    subject: '🔑 Your NXTRIX Login Credentials - Early Access Starts Soon!',
    html: (data) => `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f8f9fa; }
          .container { max-width: 600px; margin: 0 auto; background: white; }
          .header { background: linear-gradient(135deg, #10b981, #059669); padding: 40px 30px; text-align: center; }
          .header h1 { color: white; margin: 0; font-size: 28px; font-weight: 700; }
          .content { padding: 40px 30px; }
          .credentials-box { background: #f0f9ff; border: 2px solid #10b981; padding: 25px; margin: 25px 0; border-radius: 12px; text-align: center; }
          .credential-value { font-family: 'Courier New', monospace; background: white; padding: 8px 12px; border-radius: 6px; border: 1px solid #d1d5db; margin-top: 5px; }
          .cta-button { display: inline-block; background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>🔑 Your NXTRIX Access</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Early access begins in 48 hours!</p>
          </div>
          
          <div class="content">
            <h2>Hi ${data.name}!</h2>
            
            <p>The moment you've been waiting for is here! Your NXTRIX early access begins in just 48 hours.</p>
            
            <div class="credentials-box">
              <h3 style="margin-top: 0; color: #10b981;">🚀 Your Login Credentials</h3>
              <div><strong>Login URL:</strong></div>
              <div class="credential-value">https://app.nxtrix.com</div>
              <div><strong>Email:</strong></div>
              <div class="credential-value">${data.email}</div>
              <div><strong>Temporary Password:</strong></div>
              <div class="credential-value">${data.temporaryPassword}</div>
            </div>
            
            <div style="text-align: center;">
              <a href="https://app.nxtrix.com" class="cta-button">Access NXTRIX Platform</a>
            </div>
            
            <p>Welcome to the future of real estate investment!</p>
            
            <p>Best regards,<br><strong>The NXTRIX Team</strong></p>
          </div>
        </div>
      </body>
      </html>
    `
  },

  launch_notification: {
    subject: '🎉 NXTRIX is LIVE! Your Platform is Ready',
    html: (data) => `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f8f9fa; }
          .container { max-width: 600px; margin: 0 auto; background: white; }
          .header { background: linear-gradient(135deg, #7c5cff, #24d1ff, #10b981); padding: 50px 30px; text-align: center; }
          .header h1 { color: white; margin: 0; font-size: 36px; font-weight: 700; }
          .content { padding: 40px 30px; }
          .cta-button { display: inline-block; background: linear-gradient(135deg, #7c5cff, #24d1ff); color: white; padding: 20px 40px; text-decoration: none; border-radius: 12px; font-weight: 600; margin: 20px 0; font-size: 18px; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>🚀 NXTRIX IS LIVE!</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 15px 0 0 0; font-size: 20px;">The future of real estate investment is here</p>
          </div>
          
          <div class="content">
            <div style="text-align: center; font-size: 48px; margin: 20px 0;">🎉🎊🚀</div>
            
            <h2>Congratulations, ${data.name}!</h2>
            
            <p><strong>Today marks a historic milestone</strong> - NXTRIX has officially launched to the public, and you were here from the beginning as a founder!</p>
            
            <div style="text-align: center; margin: 30px 0;">
              <a href="https://app.nxtrix.com" class="cta-button">Launch Your NXTRIX Platform</a>
            </div>
            
            <p>Thank you for believing in our vision and being part of this incredible journey. Let's revolutionize real estate investment together!</p>
            
            <p>Best regards,<br>
            <strong>The NXTRIX Team</strong><br>
            🏆 <em>Powered by Founders Like You</em></p>
          </div>
        </div>
      </body>
      </html>
    `
  }
};

// Configure email transporter using environment variables
function createTransporter() {
  return nodemailer.createTransporter({
    service: 'gmail',
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_APP_PASSWORD
    }
  });
}

exports.handler = async (event, context) => {
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
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
    const { type, email, data } = JSON.parse(event.body);

    if (!EMAIL_TEMPLATES[type]) {
      throw new Error(`Unknown email template: ${type}`);
    }

    const template = EMAIL_TEMPLATES[type];
    const transporter = createTransporter();

    const mailOptions = {
      from: `"NXTRIX Team" <${process.env.EMAIL_USER}>`,
      to: email,
      subject: template.subject,
      html: template.html(data)
    };

    console.log(`📧 Sending ${type} email to ${email}`);

    const result = await transporter.sendMail(mailOptions);

    // Log email sent to database
    await supabase
      .from('email_logs')
      .insert({
        email,
        type,
        status: 'sent',
        message_id: result.messageId,
        sent_at: new Date().toISOString()
      });

    console.log(`✅ Email sent successfully: ${result.messageId}`);

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        success: true,
        messageId: result.messageId,
        type
      }),
    };

  } catch (error) {
    console.error('❌ Email sending failed:', error);

    return {
      statusCode: 500,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        error: 'Failed to send email',
        details: error.message
      }),
    };
  }
};