import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { to, message } = await request.json()

    // In production, use Twilio SDK server-side
    const twilioResponse = await fetch('https://api.twilio.com/2010-04-01/Accounts/' + process.env.TWILIO_ACCOUNT_SID + '/Messages.json', {
      method: 'POST',
      headers: {
        'Authorization': 'Basic ' + Buffer.from(process.env.TWILIO_ACCOUNT_SID + ':' + process.env.TWILIO_AUTH_TOKEN).toString('base64'),
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        From: process.env.TWILIO_PHONE_NUMBER!,
        To: to,
        Body: message,
      }),
    })

    if (twilioResponse.ok) {
      return NextResponse.json({ success: true })
    } else {
      console.error('Twilio error:', await twilioResponse.text())
      return NextResponse.json({ error: 'Failed to send SMS' }, { status: 500 })
    }
  } catch (error) {
    console.error('SMS API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}