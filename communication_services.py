"""
Real communication services integration for Twilio SMS and EmailJS
"""
import os
import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class EmailResult:
    """Result of email sending operation"""
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class SMSResult:
    """Result of SMS sending operation"""
    success: bool
    message_sid: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class TwilioSMSService:
    """Twilio SMS service integration"""
    
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.enabled = os.getenv('ENABLE_SMS_NOTIFICATIONS', 'false').lower() == 'true'
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            self.enabled = False
            print("⚠️ Twilio credentials missing - SMS functionality disabled")
    
    def send_sms(self, to_number: str, message: str) -> SMSResult:
        """Send SMS using Twilio API"""
        if not self.enabled:
            return SMSResult(
                success=False,
                error_message="SMS service not enabled or configured"
            )
        
        try:
            # Clean phone number
            to_number = self._clean_phone_number(to_number)
            
            # Twilio API endpoint
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
            
            # Prepare data
            data = {
                'From': self.from_number,
                'To': to_number,
                'Body': message
            }
            
            # Send request
            response = requests.post(
                url,
                data=data,
                auth=(self.account_sid, self.auth_token)
            )
            
            if response.status_code == 201:
                result = response.json()
                return SMSResult(
                    success=True,
                    message_sid=result.get('sid'),
                    timestamp=datetime.now()
                )
            else:
                error_data = response.json()
                return SMSResult(
                    success=False,
                    error_message=error_data.get('message', 'Unknown error')
                )
                
        except Exception as e:
            return SMSResult(
                success=False,
                error_message=f"SMS sending failed: {str(e)}"
            )
    
    def _clean_phone_number(self, phone: str) -> str:
        """Clean and format phone number"""
        # Remove all non-numeric characters
        cleaned = ''.join(filter(str.isdigit, phone))
        
        # Add country code if missing
        if len(cleaned) == 10:
            cleaned = '1' + cleaned
        
        # Add + prefix
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
            
        return cleaned
    
    def send_deal_alert_sms(self, to_number: str, deal_data: Dict[str, Any]) -> SMSResult:
        """Send a deal alert via SMS"""
        message = f"""🏠 DEAL ALERT!
        
Property: {deal_data.get('address', 'N/A')}
Price: ${deal_data.get('price', 0):,.0f}
ROI: {deal_data.get('roi', 0):.1f}%

Reply STOP to opt out.
"""
        return self.send_sms(to_number, message)

class EmailJSService:
    """EmailJS email service integration"""
    
    def __init__(self):
        self.service_id = os.getenv('EMAILJS_SERVICE_ID')
        self.template_id = os.getenv('EMAILJS_TEMPLATE_ID')
        self.template_user = os.getenv('EMAILJS_TEMPLATE_USER')
        self.public_key = os.getenv('EMAILJS_PUBLIC_KEY')
        self.private_key = os.getenv('EMAILJS_PRIVATE_KEY')
        self.enabled = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
        
        if not all([self.service_id, self.public_key]):
            self.enabled = False
            print("⚠️ EmailJS credentials missing - Email functionality disabled")
    
    def send_email(self, 
                   to_email: str, 
                   subject: str, 
                   message: str,
                   template_data: Optional[Dict[str, Any]] = None) -> EmailResult:
        """Send email using EmailJS API"""
        if not self.enabled:
            return EmailResult(
                success=False,
                error_message="Email service not enabled or configured"
            )
        
        try:
            # EmailJS API endpoint
            url = "https://api.emailjs.com/api/v1.0/email/send"
            
            # Prepare template parameters
            template_params = {
                'to_email': to_email,
                'subject': subject,
                'message': message,
                'from_name': 'NXTRIX Investment Platform',
                'reply_to': os.getenv('ADMIN_EMAIL', 'admin@nxtrix.com')
            }
            
            # Add custom template data
            if template_data:
                template_params.update(template_data)
            
            # Request payload
            payload = {
                'service_id': self.service_id,
                'template_id': self.template_id,
                'user_id': self.public_key,
                'template_params': template_params
            }
            
            # Add private key if available
            if self.private_key:
                payload['accessToken'] = self.private_key
            
            # Send request
            headers = {
                'Content-Type': 'application/json',
                'Origin': 'http://localhost'
            }
            
            response = requests.post(
                url, 
                data=json.dumps(payload),
                headers=headers
            )
            
            if response.status_code == 200:
                return EmailResult(
                    success=True,
                    message_id=f"emailjs_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.now()
                )
            else:
                return EmailResult(
                    success=False,
                    error_message=f"EmailJS API error: {response.text}"
                )
                
        except Exception as e:
            return EmailResult(
                success=False,
                error_message=f"Email sending failed: {str(e)}"
            )
    
    def send_template_email(self, 
                          to_email: str,
                          template_type: str,
                          variables: Dict[str, Any]) -> EmailResult:
        """Send email using predefined template"""
        
        # Template mappings
        templates = {
            'welcome': {
                'subject': 'Welcome to NXTRIX - Your Investment Journey Begins!',
                'template_id': self.template_user
            },
            'deal_alert': {
                'subject': 'New Investment Opportunity Available',
                'template_id': self.template_id  
            },
            'follow_up': {
                'subject': 'Following up on your investment inquiry',
                'template_id': self.template_user
            }
        }
        
        template_config = templates.get(template_type, templates['welcome'])
        
        return self.send_email(
            to_email=to_email,
            subject=template_config['subject'],
            message="",  # Template will handle the message
            template_data=variables
        )
    
    def send_deal_alert_email(self, 
                            to_email: str, 
                            deal_data: Dict[str, Any],
                            recipient_name: str = "Investor") -> EmailResult:
        """Send a deal alert via email"""
        
        template_data = {
            'recipient_name': recipient_name,
            'property_address': deal_data.get('address', 'N/A'),
            'asking_price': f"${deal_data.get('price', 0):,.0f}",
            'estimated_roi': f"{deal_data.get('roi', 0):.1f}%",
            'property_type': deal_data.get('type', 'Investment Property'),
            'deal_stage': deal_data.get('stage', 'Available'),
            'contact_phone': os.getenv('TWILIO_PHONE_NUMBER', ''),
            'contact_email': os.getenv('ADMIN_EMAIL', 'admin@nxtrix.com')
        }
        
        return self.send_template_email(
            to_email=to_email,
            template_type='deal_alert',
            variables=template_data
        )

class CommunicationManager:
    """Unified communication manager for SMS and Email"""
    
    def __init__(self):
        self.sms_service = TwilioSMSService()
        self.email_service = EmailJSService()
        self.delivery_log = []
    
    def send_notification(self, 
                         message: str,
                         email: Optional[str] = None,
                         phone: Optional[str] = None,
                         subject: str = "Notification",
                         notification_type: str = "general") -> Dict[str, Any]:
        """Send notification via email and/or SMS"""
        
        results = {
            'email_result': None,
            'sms_result': None,
            'success': False,
            'timestamp': datetime.now()
        }
        
        # Send email if email provided
        if email:
            email_result = self.email_service.send_email(
                to_email=email,
                subject=subject,
                message=message
            )
            results['email_result'] = email_result
            
            # Log delivery
            self.delivery_log.append({
                'type': 'email',
                'recipient': email,
                'success': email_result.success,
                'timestamp': email_result.timestamp,
                'message_id': email_result.message_id,
                'error': email_result.error_message
            })
        
        # Send SMS if phone provided
        if phone:
            sms_result = self.sms_service.send_sms(
                to_number=phone,
                message=message[:160]  # SMS character limit
            )
            results['sms_result'] = sms_result
            
            # Log delivery
            self.delivery_log.append({
                'type': 'sms',
                'recipient': phone,
                'success': sms_result.success,
                'timestamp': sms_result.timestamp,
                'message_id': sms_result.message_sid,
                'error': sms_result.error_message
            })
        
        # Overall success if at least one delivery succeeded
        results['success'] = (
            (results['email_result'] and results['email_result'].success) or
            (results['sms_result'] and results['sms_result'].success)
        )
        
        return results
    
    def send_deal_alert(self, 
                       deal_data: Dict[str, Any],
                       recipients: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Send deal alert to multiple recipients"""
        
        alert_results = []
        
        for recipient in recipients:
            name = recipient.get('name', 'Investor')
            email = recipient.get('email')
            phone = recipient.get('phone')
            
            # Send email alert
            if email:
                email_result = self.email_service.send_deal_alert_email(
                    to_email=email,
                    deal_data=deal_data,
                    recipient_name=name
                )
                
                alert_results.append({
                    'recipient': name,
                    'email': email,
                    'type': 'email',
                    'success': email_result.success,
                    'message_id': email_result.message_id,
                    'error': email_result.error_message
                })
            
            # Send SMS alert
            if phone:
                sms_result = self.sms_service.send_deal_alert_sms(
                    to_number=phone,
                    deal_data=deal_data
                )
                
                alert_results.append({
                    'recipient': name,
                    'phone': phone,
                    'type': 'sms',
                    'success': sms_result.success,
                    'message_id': sms_result.message_sid,
                    'error': sms_result.error_message
                })
        
        return alert_results
    
    def get_delivery_stats(self) -> Dict[str, Any]:
        """Get delivery statistics"""
        total_emails = len([log for log in self.delivery_log if log['type'] == 'email'])
        total_sms = len([log for log in self.delivery_log if log['type'] == 'sms'])
        
        successful_emails = len([log for log in self.delivery_log 
                               if log['type'] == 'email' and log['success']])
        successful_sms = len([log for log in self.delivery_log 
                            if log['type'] == 'sms' and log['success']])
        
        return {
            'total_emails_sent': total_emails,
            'total_sms_sent': total_sms,
            'successful_emails': successful_emails,
            'successful_sms': successful_sms,
            'email_success_rate': (successful_emails / total_emails * 100) if total_emails > 0 else 0,
            'sms_success_rate': (successful_sms / total_sms * 100) if total_sms > 0 else 0,
            'recent_deliveries': self.delivery_log[-10:]  # Last 10 deliveries
        }
    
    def test_services(self) -> Dict[str, Any]:
        """Test both email and SMS services"""
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@nxtrix.com')
        admin_phone = os.getenv('ADMIN_PHONE')  # Add this to your .env if you want SMS testing
        
        results = {
            'email_test': None,
            'sms_test': None,
            'timestamp': datetime.now()
        }
        
        # Test email service
        if self.email_service.enabled:
            results['email_test'] = self.email_service.send_email(
                to_email=admin_email,
                subject="NXTRIX CRM - Email Service Test",
                message="This is a test email from your NXTRIX CRM system. Email service is working correctly!"
            )
        else:
            results['email_test'] = EmailResult(
                success=False,
                error_message="Email service not configured"
            )
        
        # Test SMS service
        if self.sms_service.enabled and admin_phone:
            results['sms_test'] = self.sms_service.send_sms(
                to_number=admin_phone,
                message="NXTRIX CRM test: SMS service working!"
            )
        else:
            results['sms_test'] = SMSResult(
                success=False,
                error_message="SMS service not configured or no admin phone"
            )
        
        return results

# Initialize global communication manager
communication_manager = CommunicationManager()