export class NotificationService {
  private static twilioClient: any = null
  
  static initializeTwilio() {
    // This would be initialized server-side with Twilio SDK
    // For now, we'll use API calls
  }

  static async sendSMSNotification(to: string, message: string): Promise<boolean> {
    try {
      // This would make a server-side API call to send SMS via Twilio
      const response = await fetch('/api/notifications/sms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ to, message }),
      })
      
      return response.ok
    } catch (error) {
      console.error('Failed to send SMS:', error)
      return false
    }
  }

  static async sendEmailNotification(to: string, subject: string, message: string): Promise<boolean> {
    try {
      const response = await fetch('/api/notifications/email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ to, subject, message }),
      })
      
      return response.ok
    } catch (error) {
      console.error('Failed to send email:', error)
      return false
    }
  }

  static async notifyInvestorsOfNewDeal(deal: any, investors: any[]): Promise<void> {
    const dealMessage = `🏠 New High-Value Deal Alert!\n\n` +
      `📍 ${deal.property_address}\n` +
      `💰 Price: $${deal.purchase_price.toLocaleString()}\n` +
      `📈 ROI: ${deal.roi.toFixed(1)}%\n` +
      `⭐ Deal Score: ${deal.deal_score}/100\n\n` +
      `View details: ${process.env.FRONTEND_URL}/deals/${deal.id}`

    const emailSubject = `🔥 High ROI Deal Alert - ${deal.property_address}`
    
    const notifications = investors.map(async (investor) => {
      const promises = []
      
      if (investor.preferred_contact_method === 'sms' || investor.preferred_contact_method === 'both') {
        promises.push(this.sendSMSNotification(investor.phone, dealMessage))
      }
      
      if (investor.preferred_contact_method === 'email' || investor.preferred_contact_method === 'both') {
        promises.push(this.sendEmailNotification(investor.email, emailSubject, dealMessage))
      }
      
      return Promise.all(promises)
    })

    await Promise.all(notifications)
  }

  static formatDealNotification(deal: any): string {
    return `🏠 Deal Alert: ${deal.property_address}\n` +
           `💰 $${deal.purchase_price.toLocaleString()}\n` +
           `📈 ${deal.roi.toFixed(1)}% ROI\n` +
           `⭐ Score: ${deal.deal_score}/100`
  }
}