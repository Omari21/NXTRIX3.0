"""
Email Marketing Automation System for NXTRIX CRM
Professional email templates, drip campaigns, and automated follow-ups
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid
import json

# Import real communication services
try:
    from communication_services import communication_manager, EmailResult, SMSResult
    REAL_SERVICES_AVAILABLE = True
except ImportError:
    REAL_SERVICES_AVAILABLE = False
    print("⚠️ Communication services not available - using simulation mode")

import sqlite3
import plotly.graph_objects as go
import plotly.express as px

class EmailType(Enum):
    """Email template types"""
    LEAD_WELCOME = "Lead Welcome"
    FOLLOW_UP = "Follow Up"
    DEAL_ANNOUNCEMENT = "Deal Announcement"
    INVESTOR_UPDATE = "Investor Update"
    PROPERTY_ALERT = "Property Alert"
    NEWSLETTER = "Newsletter"
    APPOINTMENT_REMINDER = "Appointment Reminder"
    CONTRACT_SENT = "Contract Sent"
    CLOSING_UPDATE = "Closing Update"
    CUSTOM = "Custom"

class CampaignStatus(Enum):
    """Campaign status options"""
    DRAFT = "Draft"
    ACTIVE = "Active"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"

class EmailStatus(Enum):
    """Individual email status"""
    PENDING = "Pending"
    SENT = "Sent"
    DELIVERED = "Delivered"
    OPENED = "Opened"
    CLICKED = "Clicked"
    REPLIED = "Replied"
    BOUNCED = "Bounced"
    FAILED = "Failed"

@dataclass
class EmailTemplate:
    """Email template with dynamic content"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email_type: EmailType = EmailType.CUSTOM
    subject: str = ""
    body_html: str = ""
    body_text: str = ""
    variables: List[str] = field(default_factory=list)  # Available merge variables
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'email_type': self.email_type.value,
            'subject': self.subject,
            'body_html': self.body_html,
            'body_text': self.body_text,
            'variables': self.variables,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class DripCampaign:
    """Automated email drip campaign"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    target_audience: str = ""  # Lead type, investor type, etc.
    status: CampaignStatus = CampaignStatus.DRAFT
    emails: List[Dict[str, Any]] = field(default_factory=list)  # Email sequence
    subscribers: List[str] = field(default_factory=list)  # Lead/contact IDs
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'target_audience': self.target_audience,
            'status': self.status.value,
            'emails': self.emails,
            'subscribers': self.subscribers,
            'trigger_conditions': self.trigger_conditions,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

@dataclass
class EmailSend:
    """Individual email send record"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str = ""
    campaign_id: Optional[str] = None
    recipient_id: str = ""  # Lead or contact ID
    recipient_email: str = ""
    recipient_name: str = ""
    subject: str = ""
    body_html: str = ""
    body_text: str = ""
    status: EmailStatus = EmailStatus.PENDING
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    bounce_reason: Optional[str] = None
    tracking_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'template_id': self.template_id,
            'campaign_id': self.campaign_id,
            'recipient_id': self.recipient_id,
            'recipient_email': self.recipient_email,
            'recipient_name': self.recipient_name,
            'subject': self.subject,
            'body_html': self.body_html,
            'body_text': self.body_text,
            'status': self.status.value,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None,
            'replied_at': self.replied_at.isoformat() if self.replied_at else None,
            'bounce_reason': self.bounce_reason,
            'tracking_id': self.tracking_id
        }

class EmailTemplateLibrary:
    """Pre-built email templates for real estate professionals"""
    
    @staticmethod
    def get_default_templates() -> List[EmailTemplate]:
        """Get collection of professional email templates"""
        templates = []
        
        # Lead Welcome Email
        templates.append(EmailTemplate(
            name="New Lead Welcome",
            email_type=EmailType.LEAD_WELCOME,
            subject="Welcome {first_name}! Let's discuss your real estate goals",
            body_html="""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Hi {first_name},</h2>
                    
                    <p>Thank you for your interest in creative finance real estate opportunities! I'm excited to help you achieve your investment goals.</p>
                    
                    <p>Based on your initial information:</p>
                    <ul>
                        <li><strong>Investment Focus:</strong> {investment_focus}</li>
                        <li><strong>Budget Range:</strong> {budget_range}</li>
                        <li><strong>Timeline:</strong> {timeline}</li>
                    </ul>
                    
                    <p>I'd love to schedule a quick 15-minute call to discuss your specific needs and show you some opportunities that match your criteria.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
                        <p><strong>Next Steps:</strong></p>
                        <p>Reply to this email with your preferred time for a call, or click the link below to schedule directly on my calendar.</p>
                    </div>
                    
                    <p style="text-align: center;">
                        <a href="{calendar_link}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Schedule Your Call</a>
                    </p>
                    
                    <p>Looking forward to working with you!</p>
                    
                    <p>Best regards,<br>
                    {agent_name}<br>
                    {company_name}<br>
                    {phone_number}<br>
                    {email_address}</p>
                </div>
            </body>
            </html>
            """,
            body_text="""Hi {first_name},

Thank you for your interest in creative finance real estate opportunities! I'm excited to help you achieve your investment goals.

Based on your initial information:
- Investment Focus: {investment_focus}
- Budget Range: {budget_range}  
- Timeline: {timeline}

I'd love to schedule a quick 15-minute call to discuss your specific needs and show you some opportunities that match your criteria.

Reply to this email with your preferred time for a call, or visit: {calendar_link}

Looking forward to working with you!

Best regards,
{agent_name}
{company_name}
{phone_number}
{email_address}""",
            variables=["first_name", "investment_focus", "budget_range", "timeline", "calendar_link", "agent_name", "company_name", "phone_number", "email_address"]
        ))
        
        # Follow-up Email
        templates.append(EmailTemplate(
            name="Follow-up - Property Opportunities",
            email_type=EmailType.FOLLOW_UP,
            subject="New properties matching your criteria, {first_name}",
            body_html="""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Hi {first_name},</h2>
                    
                    <p>I hope this email finds you well! I wanted to follow up on our previous conversation about your real estate investment goals.</p>
                    
                    <p>I have some <strong>exciting new opportunities</strong> that match your criteria:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #28a745; margin-top: 0;">🏠 Featured Property</h3>
                        <p><strong>Address:</strong> {property_address}<br>
                        <strong>Type:</strong> {property_type}<br>
                        <strong>Price:</strong> {asking_price}<br>
                        <strong>ARV:</strong> {arv}<br>
                        <strong>Estimated ROI:</strong> {roi}%</p>
                        
                        <p style="color: #28a745; font-weight: bold;">This deal offers excellent cash flow potential with minimal repairs needed!</p>
                    </div>
                    
                    <p>I'd love to discuss this opportunity and others that I have coming up. Are you available for a quick call this week?</p>
                    
                    <p style="text-align: center;">
                        <a href="{calendar_link}" style="background-color: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Book Your Call Now</a>
                    </p>
                    
                    <p>Best regards,<br>
                    {agent_name}<br>
                    {phone_number}</p>
                </div>
            </body>
            </html>
            """,
            body_text="""Hi {first_name},

I hope this email finds you well! I wanted to follow up on our previous conversation about your real estate investment goals.

I have some exciting new opportunities that match your criteria:

FEATURED PROPERTY:
Address: {property_address}
Type: {property_type}
Price: {asking_price}
ARV: {arv}
Estimated ROI: {roi}%

This deal offers excellent cash flow potential with minimal repairs needed!

I'd love to discuss this opportunity and others that I have coming up. Are you available for a quick call this week?

Book your call: {calendar_link}

Best regards,
{agent_name}
{phone_number}""",
            variables=["first_name", "property_address", "property_type", "asking_price", "arv", "roi", "calendar_link", "agent_name", "phone_number"]
        ))
        
        # Deal Announcement
        templates.append(EmailTemplate(
            name="New Deal Alert",
            email_type=EmailType.DEAL_ANNOUNCEMENT,
            subject="🔥 New Deal Alert: {property_type} with {roi}% ROI",
            body_html="""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #dc3545; color: white; padding: 15px; text-align: center; border-radius: 8px 8px 0 0;">
                        <h2 style="margin: 0;">🔥 EXCLUSIVE DEAL ALERT</h2>
                        <p style="margin: 5px 0 0 0;">Limited Time Opportunity</p>
                    </div>
                    
                    <div style="border: 2px solid #dc3545; border-top: none; border-radius: 0 0 8px 8px; padding: 20px;">
                        <h3 style="color: #dc3545; margin-top: 0;">Investment Opportunity Details</h3>
                        
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Property:</strong></td>
                                <td style="padding: 8px; border-bottom: 1px solid #eee;">{property_address}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Type:</strong></td>
                                <td style="padding: 8px; border-bottom: 1px solid #eee;">{property_type}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Purchase Price:</strong></td>
                                <td style="padding: 8px; border-bottom: 1px solid #eee; color: #28a745; font-weight: bold;">{asking_price}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>ARV:</strong></td>
                                <td style="padding: 8px; border-bottom: 1px solid #eee;">{arv}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Estimated Repairs:</strong></td>
                                <td style="padding: 8px; border-bottom: 1px solid #eee;">{repair_costs}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px;"><strong>Projected ROI:</strong></td>
                                <td style="padding: 8px; color: #dc3545; font-weight: bold; font-size: 18px;">{roi}%</td>
                            </tr>
                        </table>
                        
                        <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                            <p style="margin: 0;"><strong>⚡ Act Fast:</strong> This property won't last long at this price. First-come, first-served basis.</p>
                        </div>
                        
                        <p style="text-align: center;">
                            <a href="{deal_link}" style="background-color: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">VIEW FULL DETAILS</a>
                        </p>
                        
                        <p style="text-align: center; margin-top: 20px;">
                            <a href="{calendar_link}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Schedule Discussion</a>
                        </p>
                    </div>
                    
                    <p style="margin-top: 20px;">Questions? Reply to this email or call me directly at {phone_number}.</p>
                    
                    <p>Best regards,<br>
                    {agent_name}</p>
                </div>
            </body>
            </html>
            """,
            body_text="""🔥 EXCLUSIVE DEAL ALERT - Limited Time Opportunity

Investment Opportunity Details:
Property: {property_address}
Type: {property_type}
Purchase Price: {asking_price}
ARV: {arv}
Estimated Repairs: {repair_costs}
Projected ROI: {roi}%

⚡ Act Fast: This property won't last long at this price. First-come, first-served basis.

View full details: {deal_link}
Schedule discussion: {calendar_link}

Questions? Reply to this email or call me directly at {phone_number}.

Best regards,
{agent_name}""",
            variables=["property_address", "property_type", "asking_price", "arv", "repair_costs", "roi", "deal_link", "calendar_link", "phone_number", "agent_name"]
        ))
        
        return templates

class EmailAutomationManager:
    """Manages email templates, campaigns, and automation"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.templates: List[EmailTemplate] = []
        self.campaigns: List[DripCampaign] = []
        self.email_sends: List[EmailSend] = []
        self.init_database()
        self.load_data()
    
    def init_database(self):
        """Initialize email automation database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Email templates table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS email_templates (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        email_type TEXT,
                        subject TEXT,
                        body_html TEXT,
                        body_text TEXT,
                        variables TEXT,
                        is_active BOOLEAN,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
                
                # Drip campaigns table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS drip_campaigns (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        target_audience TEXT,
                        status TEXT,
                        emails TEXT,
                        subscribers TEXT,
                        trigger_conditions TEXT,
                        created_at TEXT,
                        started_at TEXT,
                        completed_at TEXT
                    )
                ''')
                
                # Email sends table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS email_sends (
                        id TEXT PRIMARY KEY,
                        template_id TEXT,
                        campaign_id TEXT,
                        recipient_id TEXT,
                        recipient_email TEXT,
                        recipient_name TEXT,
                        subject TEXT,
                        body_html TEXT,
                        body_text TEXT,
                        status TEXT,
                        scheduled_at TEXT,
                        sent_at TEXT,
                        opened_at TEXT,
                        clicked_at TEXT,
                        replied_at TEXT,
                        bounce_reason TEXT,
                        tracking_id TEXT
                    )
                ''')
                
                conn.commit()
                
        except Exception as e:
            st.error(f"Email database initialization error: {str(e)}")
    
    def load_data(self):
        """Load email data from database and session state"""
        # Load templates
        if 'email_templates' in st.session_state:
            self.templates = [EmailTemplate(**data) for data in st.session_state.email_templates]
        else:
            # Load default templates on first run
            self.templates = EmailTemplateLibrary.get_default_templates()
            self.save_data()
        
        # Load campaigns
        if 'drip_campaigns' in st.session_state:
            self.campaigns = [DripCampaign(**data) for data in st.session_state.drip_campaigns]
        
        # Load email sends
        if 'email_sends' in st.session_state:
            self.email_sends = [EmailSend(**data) for data in st.session_state.email_sends]
    
    def save_data(self):
        """Save email data to session state"""
        st.session_state.email_templates = [template.to_dict() for template in self.templates]
        st.session_state.drip_campaigns = [campaign.to_dict() for campaign in self.campaigns]
        st.session_state.email_sends = [send.to_dict() for send in self.email_sends]
    
    def create_template(self, template: EmailTemplate) -> str:
        """Create new email template"""
        self.templates.append(template)
        self.save_data()
        return template.id
    
    def update_template(self, template_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing template"""
        for template in self.templates:
            if template.id == template_id:
                for key, value in updates.items():
                    if hasattr(template, key):
                        setattr(template, key, value)
                template.updated_at = datetime.now()
                self.save_data()
                return True
        return False
    
    def delete_template(self, template_id: str) -> bool:
        """Delete email template"""
        for i, template in enumerate(self.templates):
            if template.id == template_id:
                self.templates.pop(i)
                self.save_data()
                return True
        return False
    
    def create_campaign(self, campaign: DripCampaign) -> str:
        """Create new drip campaign"""
        self.campaigns.append(campaign)
        self.save_data()
        return campaign.id
    
    def send_real_email(self, 
                       recipient_email: str,
                       template: EmailTemplate,
                       variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send actual email using communication services"""
        if not REAL_SERVICES_AVAILABLE:
            return {
                'success': False,
                'error': 'Real communication services not available',
                'simulation': True
            }
        
        try:
            # Personalize email content
            subject = template.subject
            body_text = template.body_text
            body_html = template.body_html
            
            if variables:
                for key, value in variables.items():
                    placeholder = f"{{{key}}}"
                    subject = subject.replace(placeholder, str(value))
                    body_text = body_text.replace(placeholder, str(value))
                    body_html = body_html.replace(placeholder, str(value))
            
            # Send email using EmailJS
            result = communication_manager.email_service.send_email(
                to_email=recipient_email,
                subject=subject,
                message=body_text  # EmailJS will use HTML template
            )
            
            # Record email send
            if result.success:
                email_send = EmailSend(
                    template_id=template.id,
                    recipient_email=recipient_email,
                    subject=subject,
                    content=body_text,
                    status=EmailStatus.SENT,
                    sent_at=datetime.now(),
                    tracking_id=result.message_id
                )
                self.email_sends.append(email_send)
                self.save_data()
            
            return {
                'success': result.success,
                'message_id': result.message_id,
                'error': result.error_message,
                'simulation': False
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Email sending failed: {str(e)}",
                'simulation': False
            }
    
    def send_bulk_emails(self, 
                        recipients: List[str],
                        template: EmailTemplate,
                        variables_list: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Send emails to multiple recipients"""
        results = []
        
        for i, recipient in enumerate(recipients):
            variables = variables_list[i] if variables_list and i < len(variables_list) else {}
            
            result = self.send_real_email(
                recipient_email=recipient,
                template=template,
                variables=variables
            )
            
            results.append({
                'recipient': recipient,
                **result
            })
        
        return results
    
    def send_deal_alert(self, 
                       recipients: List[Dict[str, str]], 
                       deal_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Send deal alert to multiple recipients using real services"""
        if not REAL_SERVICES_AVAILABLE:
            return [{
                'success': False,
                'error': 'Real communication services not available',
                'simulation': True
            } for _ in recipients]
        
        try:
            # Use communication manager for deal alerts
            alert_results = communication_manager.send_deal_alert(
                deal_data=deal_data,
                recipients=recipients
            )
            
            # Record successful sends
            for result in alert_results:
                if result['success'] and result['type'] == 'email':
                    email_send = EmailSend(
                        template_id="deal_alert",
                        recipient_email=result['email'],
                        subject="New Investment Opportunity Available",
                        content=f"Deal Alert: {deal_data.get('address', 'Property')}",
                        status=EmailStatus.SENT,
                        sent_at=datetime.now(),
                        tracking_id=result.get('message_id')
                    )
                    self.email_sends.append(email_send)
            
            self.save_data()
            return alert_results
            
        except Exception as e:
            return [{
                'success': False,
                'error': f"Deal alert failed: {str(e)}",
                'simulation': False
            } for _ in recipients]
    
    def test_email_service(self) -> Dict[str, Any]:
        """Test email service connectivity"""
        if not REAL_SERVICES_AVAILABLE:
            return {
                'success': False,
                'message': 'Communication services not available',
                'simulation': True
            }
        
        try:
            # Test services
            test_results = communication_manager.test_services()
            
            return {
                'success': test_results['email_test'].success if test_results['email_test'] else False,
                'message': 'Email service test completed',
                'details': test_results,
                'simulation': False
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Service test failed: {str(e)}",
                'simulation': False
            }
    
    def get_delivery_stats(self) -> Dict[str, Any]:
        """Get real delivery statistics from communication manager"""
        if not REAL_SERVICES_AVAILABLE:
            return {
                'total_emails_sent': 0,
                'total_sms_sent': 0,
                'email_success_rate': 0,
                'sms_success_rate': 0,
                'simulation': True
            }
        
        return communication_manager.get_delivery_stats()

    def get_email_analytics(self) -> Dict[str, Any]:
        """Get email performance analytics"""
        total_sent = len([e for e in self.email_sends if e.status == EmailStatus.SENT])
        total_opened = len([e for e in self.email_sends if e.opened_at])
        total_clicked = len([e for e in self.email_sends if e.clicked_at])
        total_replied = len([e for e in self.email_sends if e.replied_at])
        
        open_rate = (total_opened / total_sent * 100) if total_sent > 0 else 0
        click_rate = (total_clicked / total_sent * 100) if total_sent > 0 else 0
        reply_rate = (total_replied / total_sent * 100) if total_sent > 0 else 0
        
        return {
            'total_sent': total_sent,
            'total_opened': total_opened,
            'total_clicked': total_clicked,
            'total_replied': total_replied,
            'open_rate': open_rate,
            'click_rate': click_rate,
            'reply_rate': reply_rate
        }

# Global email automation manager
@st.cache_resource
def get_email_manager():
    """Get cached email automation manager"""
    return EmailAutomationManager()