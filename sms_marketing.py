"""
SMS Marketing Campaign System for NXTRIX CRM
Bulk SMS messaging for Business plan users
"""

import streamlit as st
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid
import re

class CampaignStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"

class ContactListType(Enum):
    INVESTORS = "investors"
    LEADS = "leads"
    CLIENTS = "clients"
    CUSTOM = "custom"

@dataclass
class SMSCampaign:
    """SMS campaign data structure"""
    id: str
    name: str
    message: str
    contact_list_id: str
    scheduled_time: Optional[datetime] = None
    status: CampaignStatus = CampaignStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    sent_count: int = 0
    delivered_count: int = 0
    failed_count: int = 0
    click_count: int = 0
    opt_out_count: int = 0

@dataclass
class ContactList:
    """Contact list data structure"""
    id: str
    name: str
    list_type: ContactListType
    contacts: List[Dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.now)

class SMSMarketingManager:
    """SMS marketing campaign management system"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.init_database()
        
        # Initialize Twilio if available
        try:
            if hasattr(st, 'secrets') and 'TWILIO' in st.secrets:
                from twilio.rest import Client
                self.twilio_client = Client(
                    st.secrets["TWILIO"]["ACCOUNT_SID"],
                    st.secrets["TWILIO"]["AUTH_TOKEN"]
                )
                self.twilio_phone = st.secrets["TWILIO"]["PHONE_NUMBER"]
                self.twilio_available = True
            else:
                self.twilio_available = False
        except Exception as e:
            self.twilio_available = False
            st.warning(f"Twilio not configured for SMS campaigns: {e}")
    
    def init_database(self):
        """Initialize SMS campaign database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # SMS campaigns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sms_campaigns (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    message TEXT NOT NULL,
                    contact_list_id TEXT NOT NULL,
                    scheduled_time TIMESTAMP,
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sent_count INTEGER DEFAULT 0,
                    delivered_count INTEGER DEFAULT 0,
                    failed_count INTEGER DEFAULT 0,
                    click_count INTEGER DEFAULT 0,
                    opt_out_count INTEGER DEFAULT 0
                )
            ''')
            
            # Contact lists table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sms_contact_lists (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    list_type TEXT NOT NULL,
                    contacts TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # SMS delivery tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sms_delivery_log (
                    id TEXT PRIMARY KEY,
                    campaign_id TEXT NOT NULL,
                    phone_number TEXT NOT NULL,
                    message_sid TEXT,
                    status TEXT DEFAULT 'queued',
                    delivered_at TIMESTAMP,
                    failed_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Opt-out management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sms_opt_outs (
                    phone_number TEXT PRIMARY KEY,
                    opted_out_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    campaign_id TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error initializing SMS campaign database: {e}")
    
    def create_campaign(self, name: str, message: str, contact_list_id: str,
                       scheduled_time: Optional[datetime] = None) -> str:
        """Create a new SMS campaign"""
        try:
            campaign = SMSCampaign(
                id=str(uuid.uuid4()),
                name=name,
                message=message,
                contact_list_id=contact_list_id,
                scheduled_time=scheduled_time
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sms_campaigns 
                (id, name, message, contact_list_id, scheduled_time, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                campaign.id,
                campaign.name,
                campaign.message,
                campaign.contact_list_id,
                campaign.scheduled_time.isoformat() if campaign.scheduled_time else None,
                campaign.status.value,
                campaign.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            return campaign.id
            
        except Exception as e:
            st.error(f"Error creating SMS campaign: {e}")
            return ""
    
    def create_contact_list(self, name: str, list_type: ContactListType,
                           contacts: List[Dict[str, Any]]) -> str:
        """Create a new contact list"""
        try:
            contact_list = ContactList(
                id=str(uuid.uuid4()),
                name=name,
                list_type=list_type,
                contacts=contacts
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sms_contact_lists (id, name, list_type, contacts, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                contact_list.id,
                contact_list.name,
                contact_list.list_type.value,
                json.dumps(contact_list.contacts),
                contact_list.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            return contact_list.id
            
        except Exception as e:
            st.error(f"Error creating contact list: {e}")
            return ""
    
    def get_campaigns(self, status: Optional[CampaignStatus] = None) -> List[SMSCampaign]:
        """Get SMS campaigns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM sms_campaigns"
            params = []
            
            if status:
                query += " WHERE status = ?"
                params.append(status.value)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            campaigns = []
            for row in rows:
                campaign = SMSCampaign(
                    id=row[0],
                    name=row[1],
                    message=row[2],
                    contact_list_id=row[3],
                    scheduled_time=datetime.fromisoformat(row[4]) if row[4] else None,
                    status=CampaignStatus(row[5]),
                    created_at=datetime.fromisoformat(row[6]),
                    sent_count=row[7],
                    delivered_count=row[8],
                    failed_count=row[9],
                    click_count=row[10],
                    opt_out_count=row[11]
                )
                campaigns.append(campaign)
            
            conn.close()
            return campaigns
            
        except Exception as e:
            st.error(f"Error retrieving campaigns: {e}")
            return []
    
    def get_contact_lists(self) -> List[ContactList]:
        """Get contact lists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM sms_contact_lists ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            contact_lists = []
            for row in rows:
                contact_list = ContactList(
                    id=row[0],
                    name=row[1],
                    list_type=ContactListType(row[2]),
                    contacts=json.loads(row[3]),
                    created_at=datetime.fromisoformat(row[4])
                )
                contact_lists.append(contact_list)
            
            conn.close()
            return contact_lists
            
        except Exception as e:
            st.error(f"Error retrieving contact lists: {e}")
            return []
    
    def send_campaign(self, campaign_id: str) -> bool:
        """Send SMS campaign"""
        if not self.twilio_available:
            st.error("🚫 SMS sending requires Twilio configuration")
            return False
        
        try:
            # Get campaign details
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM sms_campaigns WHERE id = ?", (campaign_id,))
            campaign_row = cursor.fetchone()
            
            if not campaign_row:
                st.error("Campaign not found")
                return False
            
            # Get contact list
            cursor.execute("SELECT contacts FROM sms_contact_lists WHERE id = ?", (campaign_row[3],))
            contacts_row = cursor.fetchone()
            
            if not contacts_row:
                st.error("Contact list not found")
                return False
            
            contacts = json.loads(contacts_row[0])
            message = campaign_row[2]
            
            # Update campaign status
            cursor.execute("UPDATE sms_campaigns SET status = ? WHERE id = ?", 
                         (CampaignStatus.SENDING.value, campaign_id))
            conn.commit()
            
            sent_count = 0
            failed_count = 0
            
            # Send to each contact
            for contact in contacts:
                phone = contact.get('phone', '').strip()
                if not phone:
                    continue
                
                # Check opt-out status
                cursor.execute("SELECT phone_number FROM sms_opt_outs WHERE phone_number = ?", (phone,))
                if cursor.fetchone():
                    continue  # Skip opted-out numbers
                
                try:
                    # Personalize message
                    personalized_message = self._personalize_message(message, contact)
                    
                    # Send via Twilio
                    twilio_message = self.twilio_client.messages.create(
                        body=personalized_message,
                        from_=self.twilio_phone,
                        to=phone
                    )
                    
                    # Log delivery
                    cursor.execute('''
                        INSERT INTO sms_delivery_log 
                        (id, campaign_id, phone_number, message_sid, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        str(uuid.uuid4()),
                        campaign_id,
                        phone,
                        twilio_message.sid,
                        'sent',
                        datetime.now().isoformat()
                    ))
                    
                    sent_count += 1
                    
                except Exception as e:
                    # Log failure
                    cursor.execute('''
                        INSERT INTO sms_delivery_log 
                        (id, campaign_id, phone_number, status, failed_reason, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        str(uuid.uuid4()),
                        campaign_id,
                        phone,
                        'failed',
                        str(e),
                        datetime.now().isoformat()
                    ))
                    
                    failed_count += 1
            
            # Update campaign with results
            cursor.execute('''
                UPDATE sms_campaigns 
                SET status = ?, sent_count = ?, failed_count = ?
                WHERE id = ?
            ''', (
                CampaignStatus.COMPLETED.value,
                sent_count,
                failed_count,
                campaign_id
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            st.error(f"Error sending campaign: {e}")
            return False
    
    def _personalize_message(self, message: str, contact: Dict[str, Any]) -> str:
        """Personalize SMS message with contact data"""
        personalized = message
        
        # Replace common placeholders
        replacements = {
            '{name}': contact.get('name', 'there'),
            '{first_name}': contact.get('first_name', contact.get('name', 'there')),
            '{company}': contact.get('company', ''),
            '{city}': contact.get('city', ''),
            '{investment_amount}': contact.get('investment_amount', ''),
        }
        
        for placeholder, value in replacements.items():
            if value:
                personalized = personalized.replace(placeholder, str(value))
        
        # Add opt-out message
        personalized += "\n\nReply STOP to opt out."
        
        return personalized
    
    def get_campaign_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get campaign info
            cursor.execute("SELECT * FROM sms_campaigns WHERE id = ?", (campaign_id,))
            campaign = cursor.fetchone()
            
            if not campaign:
                return {}
            
            # Get delivery stats
            cursor.execute('''
                SELECT status, COUNT(*) FROM sms_delivery_log 
                WHERE campaign_id = ? GROUP BY status
            ''', (campaign_id,))
            
            delivery_stats = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'campaign_name': campaign[1],
                'total_sent': campaign[7],
                'delivered': delivery_stats.get('delivered', 0),
                'failed': delivery_stats.get('failed', 0),
                'pending': delivery_stats.get('sent', 0),
                'delivery_rate': (delivery_stats.get('delivered', 0) / max(campaign[7], 1)) * 100,
                'status': campaign[5]
            }
            
        except Exception as e:
            st.error(f"Error getting campaign analytics: {e}")
            return {}

def show_sms_marketing():
    """Show SMS marketing interface"""
    st.header("📱 SMS Marketing Campaigns")
    st.write("Bulk SMS messaging for targeted marketing campaigns.")
    
    # Check tier access - Business plan only
    user_tier = st.session_state.get('user_tier', 'solo')
    if user_tier != 'business':
        st.warning("🔒 SMS Marketing Campaigns are available for Business plan only.")
        if user_tier == 'solo':
            st.info("Upgrade to Business plan to unlock bulk SMS campaigns!")
        else:
            st.info("Upgrade to Business plan to access SMS marketing features!")
        return
    
    # Initialize SMS manager
    if 'sms_marketing_manager' not in st.session_state:
        st.session_state.sms_marketing_manager = SMSMarketingManager()
    
    sms_manager = st.session_state.sms_marketing_manager
    
    # Main interface tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📱 Campaigns",
        "👥 Contact Lists",
        "📊 Analytics",
        "⚙️ Settings"
    ])
    
    with tab1:
        show_sms_campaigns(sms_manager)
    
    with tab2:
        show_contact_lists(sms_manager)
    
    with tab3:
        show_sms_analytics(sms_manager)
    
    with tab4:
        show_sms_settings(sms_manager)

def show_sms_campaigns(sms_manager: SMSMarketingManager):
    """Show SMS campaigns interface"""
    st.subheader("📱 SMS Campaigns")
    
    # Create new campaign
    with st.expander("➕ Create New Campaign", expanded=False):
        with st.form("create_sms_campaign"):
            campaign_name = st.text_input("Campaign Name", placeholder="Holiday Property Alert")
            
            # Get available contact lists
            contact_lists = sms_manager.get_contact_lists()
            if contact_lists:
                contact_list_options = [(cl.name, cl.id) for cl in contact_lists]
                selected_list = st.selectbox("Contact List", contact_list_options,
                                           format_func=lambda x: f"{x[0]} ({len([cl for cl in contact_lists if cl.id == x[1]][0].contacts)} contacts)")
                
                message = st.text_area("Message (160 chars recommended)", 
                                     placeholder="🏠 New investment opportunity in Dallas! 12% cap rate, $150K. Interested? Call now: (555) 123-4567",
                                     max_chars=1600, height=100)
                
                # Message preview and character count
                if message:
                    char_count = len(message + "\n\nReply STOP to opt out.")
                    if char_count <= 160:
                        st.success(f"✅ Single SMS ({char_count}/160 characters)")
                    else:
                        segments = (char_count + 152) // 153  # SMS segment calculation
                        st.warning(f"⚠️ {segments} SMS segments ({char_count} characters)")
                
                # Scheduling options
                send_immediately = st.checkbox("Send immediately", value=True)
                scheduled_time = None
                if not send_immediately:
                    col1, col2 = st.columns(2)
                    with col1:
                        schedule_date = st.date_input("Schedule Date", min_value=datetime.now().date())
                    with col2:
                        schedule_time = st.time_input("Schedule Time")
                    
                    scheduled_time = datetime.combine(schedule_date, schedule_time)
                
                create_button = st.form_submit_button("📱 Create Campaign", type="primary")
                
                if create_button and campaign_name and message and selected_list:
                    campaign_id = sms_manager.create_campaign(
                        name=campaign_name,
                        message=message,
                        contact_list_id=selected_list[1],
                        scheduled_time=scheduled_time
                    )
                    
                    if campaign_id:
                        st.success(f"✅ Campaign '{campaign_name}' created successfully!")
                        
                        if send_immediately:
                            with st.spinner("📱 Sending SMS campaign..."):
                                if sms_manager.send_campaign(campaign_id):
                                    st.success("🚀 Campaign sent successfully!")
                                else:
                                    st.error("❌ Failed to send campaign")
                        else:
                            st.info(f"📅 Campaign scheduled for {scheduled_time.strftime('%m/%d/%Y %H:%M')}")
                        
                        st.rerun()
            else:
                st.warning("📋 Create a contact list first before creating campaigns.")
    
    # Show existing campaigns
    campaigns = sms_manager.get_campaigns()
    
    if campaigns:
        st.markdown("### 📋 Your Campaigns")
        
        for campaign in campaigns:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{campaign.name}**")
                    st.caption(f"Created: {campaign.created_at.strftime('%m/%d/%Y %H:%M')}")
                
                with col2:
                    status_colors = {
                        CampaignStatus.DRAFT: "🟡",
                        CampaignStatus.SCHEDULED: "🔵",
                        CampaignStatus.SENDING: "🟠",
                        CampaignStatus.COMPLETED: "🟢",
                        CampaignStatus.PAUSED: "⚪",
                        CampaignStatus.FAILED: "🔴"
                    }
                    st.markdown(f"{status_colors.get(campaign.status, '⚪')} {campaign.status.value.title()}")
                    if campaign.scheduled_time:
                        st.caption(f"Scheduled: {campaign.scheduled_time.strftime('%m/%d/%Y %H:%M')}")
                
                with col3:
                    if campaign.sent_count > 0:
                        delivery_rate = (campaign.delivered_count / campaign.sent_count) * 100
                        st.metric("Sent", campaign.sent_count)
                        st.caption(f"{delivery_rate:.1f}% delivered")
                    else:
                        st.caption("Not sent yet")
                
                with col4:
                    if campaign.status == CampaignStatus.DRAFT:
                        if st.button("📱 Send", key=f"send_{campaign.id}"):
                            with st.spinner("Sending..."):
                                if sms_manager.send_campaign(campaign.id):
                                    st.success("Sent!")
                                    st.rerun()
                
                # Show message preview
                with st.expander(f"👀 Preview: {campaign.message[:50]}..."):
                    st.text_area("Message", campaign.message, height=100, disabled=True, key=f"msg_{campaign.id}")
                
                st.markdown("---")
    else:
        st.info("📭 No SMS campaigns yet. Create your first campaign above!")

def show_contact_lists(sms_manager: SMSMarketingManager):
    """Show contact lists management"""
    st.subheader("👥 Contact Lists")
    
    # Create new contact list
    with st.expander("➕ Create New Contact List", expanded=False):
        with st.form("create_contact_list"):
            list_name = st.text_input("List Name", placeholder="High Net Worth Investors")
            list_type = st.selectbox("List Type", [
                ("Investors", ContactListType.INVESTORS),
                ("Leads", ContactListType.LEADS),
                ("Clients", ContactListType.CLIENTS),
                ("Custom", ContactListType.CUSTOM)
            ], format_func=lambda x: x[0])[1]
            
            # Contact input methods
            input_method = st.radio("How do you want to add contacts?", [
                "Manual Entry",
                "CSV Upload",
                "Import from CRM"
            ])
            
            contacts = []
            
            if input_method == "Manual Entry":
                st.markdown("**Add Contacts:**")
                num_contacts = st.number_input("Number of contacts to add", min_value=1, max_value=50, value=5)
                
                for i in range(int(num_contacts)):
                    st.markdown(f"**Contact {i+1}:**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        name = st.text_input(f"Name", key=f"name_{i}", placeholder="John Smith")
                    with col2:
                        phone = st.text_input(f"Phone", key=f"phone_{i}", placeholder="+1234567890")
                    with col3:
                        company = st.text_input(f"Company", key=f"company_{i}", placeholder="ABC Investments")
                    
                    if name and phone:
                        contacts.append({
                            "name": name,
                            "phone": phone,
                            "company": company
                        })
            
            elif input_method == "CSV Upload":
                st.markdown("**Upload CSV File:**")
                st.info("CSV should have columns: name, phone, company, city")
                uploaded_file = st.file_uploader("Choose CSV file", type="csv")
                
                if uploaded_file:
                    import pandas as pd
                    try:
                        df = pd.read_csv(uploaded_file)
                        st.dataframe(df.head())
                        
                        for _, row in df.iterrows():
                            contact = {}
                            for col in ['name', 'phone', 'company', 'city']:
                                if col in df.columns:
                                    contact[col] = str(row[col]) if pd.notna(row[col]) else ""
                            if contact.get('phone'):
                                contacts.append(contact)
                        
                        st.success(f"✅ Loaded {len(contacts)} contacts from CSV")
                    except Exception as e:
                        st.error(f"Error reading CSV: {e}")
            
            elif input_method == "Import from CRM":
                st.info("🚧 CRM import feature coming soon!")
            
            create_list_button = st.form_submit_button("📋 Create Contact List", type="primary")
            
            if create_list_button and list_name and contacts:
                list_id = sms_manager.create_contact_list(list_name, list_type, contacts)
                if list_id:
                    st.success(f"✅ Contact list '{list_name}' created with {len(contacts)} contacts!")
                    st.rerun()
    
    # Show existing contact lists
    contact_lists = sms_manager.get_contact_lists()
    
    if contact_lists:
        st.markdown("### 📋 Your Contact Lists")
        
        for contact_list in contact_lists:
            with st.expander(f"📋 {contact_list.name} ({len(contact_list.contacts)} contacts)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"Type: {contact_list.list_type.value.title()}")
                    st.caption(f"Created: {contact_list.created_at.strftime('%m/%d/%Y')}")
                
                with col2:
                    st.metric("Total Contacts", len(contact_list.contacts))
                
                # Show sample contacts
                if contact_list.contacts:
                    st.markdown("**Sample Contacts:**")
                    import pandas as pd
                    df = pd.DataFrame(contact_list.contacts[:10])  # Show first 10
                    st.dataframe(df, use_container_width=True)
                    
                    if len(contact_list.contacts) > 10:
                        st.caption(f"... and {len(contact_list.contacts) - 10} more contacts")
    else:
        st.info("📭 No contact lists yet. Create your first list above!")

def show_sms_analytics(sms_manager: SMSMarketingManager):
    """Show SMS campaign analytics"""
    st.subheader("📊 SMS Campaign Analytics")
    
    campaigns = sms_manager.get_campaigns()
    
    if campaigns:
        # Overall metrics
        total_sent = sum(c.sent_count for c in campaigns)
        total_delivered = sum(c.delivered_count for c in campaigns)
        total_failed = sum(c.failed_count for c in campaigns)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Campaigns", len(campaigns))
        with col2:
            st.metric("Messages Sent", total_sent)
        with col3:
            delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
            st.metric("Delivery Rate", f"{delivery_rate:.1f}%")
        with col4:
            st.metric("Failed Messages", total_failed)
        
        # Campaign performance
        st.markdown("### 📈 Campaign Performance")
        
        completed_campaigns = [c for c in campaigns if c.status == CampaignStatus.COMPLETED]
        
        if completed_campaigns:
            import pandas as pd
            import plotly.express as px
            
            # Prepare data for charts
            campaign_data = []
            for campaign in completed_campaigns:
                campaign_data.append({
                    'name': campaign.name,
                    'sent': campaign.sent_count,
                    'delivered': campaign.delivered_count,
                    'failed': campaign.failed_count,
                    'delivery_rate': (campaign.delivered_count / campaign.sent_count * 100) if campaign.sent_count > 0 else 0,
                    'date': campaign.created_at.date()
                })
            
            df = pd.DataFrame(campaign_data)
            
            # Campaign delivery rates
            fig_delivery = px.bar(df, x='name', y='delivery_rate',
                                title="Campaign Delivery Rates (%)")
            st.plotly_chart(fig_delivery, use_container_width=True)
            
            # Messages sent over time
            if len(df) > 1:
                fig_timeline = px.line(df, x='date', y='sent',
                                     title="Messages Sent Over Time")
                st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Individual campaign details
        st.markdown("### 📋 Campaign Details")
        
        for campaign in campaigns:
            if campaign.sent_count > 0:
                analytics = sms_manager.get_campaign_analytics(campaign.id)
                
                with st.expander(f"📱 {campaign.name} Analytics"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Sent", analytics.get('total_sent', 0))
                    with col2:
                        st.metric("Delivered", analytics.get('delivered', 0))
                    with col3:
                        st.metric("Delivery Rate", f"{analytics.get('delivery_rate', 0):.1f}%")
    else:
        st.info("📊 No campaign data available. Create and send campaigns to see analytics!")

def show_sms_settings(sms_manager: SMSMarketingManager):
    """Show SMS settings"""
    st.subheader("⚙️ SMS Settings")
    
    # Twilio configuration status
    st.markdown("### 📞 Twilio Configuration")
    if sms_manager.twilio_available:
        st.success("✅ Twilio configured and ready")
        st.caption("SMS campaigns can be sent")
    else:
        st.error("❌ Twilio not configured")
        st.caption("Configure Twilio credentials in Streamlit secrets to enable SMS sending")
    
    # Compliance and opt-out management
    st.markdown("### 📋 Compliance & Opt-Outs")
    
    # Show opt-out statistics
    try:
        conn = sqlite3.connect(sms_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sms_opt_outs")
        opt_out_count = cursor.fetchone()[0]
        conn.close()
        
        st.metric("Total Opt-Outs", opt_out_count)
        
        if opt_out_count > 0:
            st.info("💡 Opted-out numbers are automatically excluded from future campaigns")
    except:
        st.caption("No opt-out data available")
    
    # Best practices
    st.markdown("### 💡 SMS Best Practices")
    st.markdown("""
    **Legal Compliance:**
    - ✅ Only send to numbers that have opted in
    - ✅ Include clear opt-out instructions
    - ✅ Honor opt-out requests immediately
    - ✅ Keep records of consent
    
    **Message Optimization:**
    - 📱 Keep messages under 160 characters when possible
    - ⏰ Send during business hours (9 AM - 6 PM)
    - 🎯 Personalize messages with recipient names
    - 📞 Include clear contact information
    
    **Campaign Strategy:**
    - 🔄 Test messages with small groups first
    - 📊 Track delivery and response rates
    - ⚡ Create urgency without being spammy
    - 🎯 Segment lists for targeted messaging
    """)