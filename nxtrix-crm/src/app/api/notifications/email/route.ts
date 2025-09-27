import { NextRequest, NextResponse } from 'next/server'
import emailjs from '@emailjs/nodejs'

export async function POST(request: NextRequest) {
  try {
    const { to, subject, message } = await request.json()

    const templateParams = {
      to_email: to,
      subject: subject,
      message: message,
      from_name: 'NxTrix CRM',
    }

    await emailjs.send(
      process.env.EMAILJS_SERVICE_ID!,
      process.env.EMAILJS_TEMPLATE_ID!,
      templateParams,
      {
        publicKey: process.env.EMAILJS_PUBLIC_KEY!,
        privateKey: process.env.EMAILJS_PRIVATE_KEY!,
      }
    )

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Email API error:', error)
    return NextResponse.json({ error: 'Failed to send email' }, { status: 500 })
  }
}