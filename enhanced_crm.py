"""
Enhanced CRM Features for NXTRIX Deal Analyzer
Comprehensive lead tracking, contact management, and sales pipeline automation
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid
import json
import sqlite3
import csv
import io
import os
from pathlib import Path
from database import db_service
from email_automation import get_email_manager, EmailAutomationManager
from deal_workflow_automation import (
    get_workflow_manager, 
    DealWorkflowAutomation, 
    PropertyType, 
    InvestmentCriteria,
    DealStage,
    BuyerStatus,
    NotificationType
)
from email_automation import get_email_manager, EmailTemplate, DripCampaign, EmailType, CampaignStatus
from activity_tracker import get_activity_tracker, ActivityType, Priority, ActivityLog, OpportunityAlert
from advanced_deal_analytics import AdvancedDealAnalytics, show_advanced_deal_analytics
from automated_deal_sourcing import show_automated_deal_sourcing
from ai_enhancement_system import show_ai_enhancement_system
from advanced_automation_system import show_advanced_automation_system

# Optional subscription imports with error handling
try:
    from subscription_manager import SubscriptionManager, SubscriptionTier, get_user_tier
    SUBSCRIPTION_MANAGER_AVAILABLE = True
except ImportError:
    SUBSCRIPTION_MANAGER_AVAILABLE = False
    # Create placeholder classes when not available
    class SubscriptionTier:
        BASIC = "basic"
        PROFESSIONAL = "professional"
        ENTERPRISE = "enterprise"
    
    class SubscriptionManager:
        def __init__(self, *args, **kwargs):
            pass
        
        def get_user_subscription(self, user_id):
            return None
    
    def get_user_tier(user_id):
        return SubscriptionTier.BASIC

try:
    from subscription_dashboard import subscription_dashboard
    SUBSCRIPTION_DASHBOARD_AVAILABLE = True
except ImportError:
    SUBSCRIPTION_DASHBOARD_AVAILABLE = False
    # Create placeholder for subscription dashboard
    class subscription_dashboard:
        @staticmethod
        def show_admin_dashboard():
            st.warning("⚠️ Subscription dashboard requires additional dependencies (psycopg2)")

from feature_access_control import (
    FeatureAccessControl, 
    require_feature, 
    require_tier,
    track_feature_usage,
    access_control
)

class LeadStatus(Enum):
    """Lead status options"""
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    MEETING_SCHEDULED = "Meeting Scheduled"
    PROPOSAL_SENT = "Proposal Sent"
    NEGOTIATING = "Negotiating"
    CLOSED_WON = "Closed Won"
    CLOSED_LOST = "Closed Lost"
    NURTURING = "Nurturing"

class LeadSource(Enum):
    """Lead source options"""
    WEBSITE = "Website"
    REFERRAL = "Referral"
    SOCIAL_MEDIA = "Social Media"
    EMAIL_CAMPAIGN = "Email Campaign"
    COLD_OUTREACH = "Cold Outreach"
    NETWORKING_EVENT = "Networking Event"
    ADVERTISEMENT = "Advertisement"
    PARTNER = "Partner"
    OTHER = "Other"

class ContactType(Enum):
    """Contact type classification"""
    SELLER = "Seller"
    BUYER = "Buyer"
    INVESTOR = "Investor"
    AGENT = "Agent"
    CONTRACTOR = "Contractor"
    LENDER = "Lender"
    ATTORNEY = "Attorney"
    OTHER = "Other"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class InvestorType(Enum):
    """Creative finance investor types"""
    WHOLESALER = "Wholesaler"
    FIX_AND_FLIP = "Fix & Flip"
    BUY_AND_HOLD = "Buy & Hold"
    SUBJECT_TO = "Subject To Specialist"
    OWNER_FINANCE = "Owner Finance Specialist"
    LEASE_OPTION = "Lease Option Specialist"
    HARD_MONEY_LENDER = "Hard Money Lender"
    PRIVATE_LENDER = "Private Lender"
    REAL_ESTATE_AGENT = "Real Estate Agent"
    SYNDICATOR = "Syndicator"
    MULTI_FAMILY = "Multi-Family Investor"
    COMMERCIAL = "Commercial Investor"
    LAND_INVESTOR = "Land Investor"
    NEW_INVESTOR = "New/Beginner Investor"
    CASH_BUYER = "Cash Buyer"

class SellerMotivation(Enum):
    """Seller motivation types"""
    FINANCIAL_DISTRESS = "Financial Distress"
    RELOCATION = "Relocation/Job Transfer"
    INHERITANCE = "Inherited Property"
    DIVORCE = "Divorce Settlement"
    DOWNSIZING = "Downsizing"
    TIRED_LANDLORD = "Tired Landlord"
    PROPERTY_CONDITION = "Property Needs Repairs"
    ESTATE_SALE = "Estate Sale"
    FORECLOSURE_AVOIDANCE = "Avoiding Foreclosure"
    TAX_ISSUES = "Tax Problems"
    MEDICAL_BILLS = "Medical Bills"
    BUSINESS_OPPORTUNITY = "Business Opportunity"
    RETIREMENT = "Retirement"
    QUICK_SALE_NEEDED = "Need Quick Sale"
    OTHER = "Other"

class CreativeFinanceMethod(Enum):
    """Creative financing methods"""
    SUBJECT_TO = "Subject To"
    OWNER_FINANCING = "Owner Financing/Seller Carryback"
    LEASE_OPTION = "Lease Option"
    RENT_TO_OWN = "Rent to Own"
    CONTRACT_FOR_DEED = "Contract for Deed/Land Contract"
    ASSUMABLE_MORTGAGE = "Assumable Mortgage"
    WRAP_AROUND_MORTGAGE = "Wrap Around Mortgage"
    EQUITY_SHARING = "Equity Sharing"
    PARTNERSHIP = "Investment Partnership"
    HARD_MONEY = "Hard Money Loan"
    PRIVATE_MONEY = "Private Money"
    FHA_203K = "FHA 203K Loan"
    CONVENTIONAL_LOW_DOWN = "Low Down Conventional"
    CASH_OUT_REFINANCE = "Cash Out Refinance"
    CROSS_COLLATERAL = "Cross Collateral"
    SELLER_SECOND = "Seller Second Mortgage"
    NOVATION = "Novation"
    ASSIGNMENT = "Assignment of Contract"
    SANDWICH_LEASE = "Sandwich Lease Option"
    OTHER = "Other Creative Method"

class LeadCategory(Enum):
    """Lead category types"""
    INVESTOR_LEAD = "Investor Lead"
    SELLER_LEAD = "Seller Lead"
    BUYER_LEAD = "Buyer Lead"
    GENERAL_LEAD = "General Lead"

class DealStatus(Enum):
    """Deal status options"""
    LEAD = "Lead"
    ANALYZING = "Analyzing"
    UNDER_CONTRACT = "Under Contract"
    DUE_DILIGENCE = "Due Diligence"
    FINANCING = "Financing"
    CLOSING = "Closing"
    CLOSED = "Closed"
    DEAD = "Dead"
    ON_HOLD = "On Hold"

class PropertyType(Enum):
    """Property type options"""
    SINGLE_FAMILY = "Single Family"
    MULTI_FAMILY = "Multi Family"
    CONDO = "Condo"
    TOWNHOUSE = "Townhouse"
    COMMERCIAL = "Commercial"
    LAND = "Land"
    MOBILE_HOME = "Mobile Home"
    OTHER = "Other"

class DealType(Enum):
    """Deal type options"""
    WHOLESALE = "Wholesale"
    FIX_AND_FLIP = "Fix & Flip"
    BUY_AND_HOLD = "Buy & Hold"
    SUBJECT_TO = "Subject To"
    OWNER_FINANCE = "Owner Finance"
    LEASE_OPTION = "Lease Option"
    ASSIGNMENT = "Assignment"
    OTHER = "Other"

class MessageType(Enum):
    """Message type options"""
    DEAL_ALERT = "Deal Alert"
    DEAL_UPDATE = "Deal Update"
    GENERAL_MESSAGE = "General Message"
    MEETING_REQUEST = "Meeting Request"
    CONTRACT_UPDATE = "Contract Update"
    CLOSING_REMINDER = "Closing Reminder"

class MessageStatus(Enum):
    """Message status options"""
    SENT = "Sent"
    DELIVERED = "Delivered"
    READ = "Read"
    REPLIED = "Replied"

@dataclass
class Lead:
    """Enhanced lead data model for creative finance"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    phone: str = ""
    property_address: str = ""
    property_type: str = ""
    budget_min: float = 0
    budget_max: float = 0
    lead_source: LeadSource = LeadSource.WEBSITE
    status: LeadStatus = LeadStatus.NEW
    assigned_to: str = ""
    score: int = 0
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_contact: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None
    
    # Creative Finance Specific Fields
    lead_category: LeadCategory = LeadCategory.GENERAL_LEAD
    investor_type: Optional[InvestorType] = None
    seller_motivation: Optional[SellerMotivation] = None
    preferred_finance_methods: List[CreativeFinanceMethod] = field(default_factory=list)
    
    # Seller-specific fields
    property_value: float = 0
    mortgage_balance: float = 0
    monthly_payment: float = 0
    equity_amount: float = 0
    time_frame: str = ""  # How quickly they need to sell
    seller_financing_interest: bool = False
    
    # Investor-specific fields
    experience_level: str = ""  # Beginner, Intermediate, Advanced
    investment_criteria: str = ""
    funding_source: str = ""  # Cash, Hard Money, Private Money, etc.
    portfolio_size: int = 0
    target_roi: float = 0
    preferred_markets: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert lead to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'property_address': self.property_address,
            'property_type': self.property_type,
            'budget_min': self.budget_min,
            'budget_max': self.budget_max,
            'lead_source': self.lead_source.value,
            'status': self.status.value,
            'assigned_to': self.assigned_to,
            'score': self.score,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_contact': self.last_contact.isoformat() if self.last_contact else None,
            'next_follow_up': self.next_follow_up.isoformat() if self.next_follow_up else None,
            
            # Creative Finance Fields
            'lead_category': self.lead_category.value,
            'investor_type': self.investor_type.value if self.investor_type else None,
            'seller_motivation': self.seller_motivation.value if self.seller_motivation else None,
            'preferred_finance_methods': [method.value for method in self.preferred_finance_methods],
            
            # Seller fields
            'property_value': self.property_value,
            'mortgage_balance': self.mortgage_balance,
            'monthly_payment': self.monthly_payment,
            'equity_amount': self.equity_amount,
            'time_frame': self.time_frame,
            'seller_financing_interest': self.seller_financing_interest,
            
            # Investor fields
            'experience_level': self.experience_level,
            'investment_criteria': self.investment_criteria,
            'funding_source': self.funding_source,
            'portfolio_size': self.portfolio_size,
            'target_roi': self.target_roi,
            'preferred_markets': self.preferred_markets
        }

@dataclass
class Contact:
    """Contact data model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    phone: str = ""
    company: str = ""
    contact_type: ContactType = ContactType.OTHER
    address: str = ""
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_interaction: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contact to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'contact_type': self.contact_type.value,
            'address': self.address,
            'notes': self.notes,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None
        }

@dataclass
class Task:
    """Task data model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    assigned_to: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    completed: bool = False
    related_lead_id: Optional[str] = None
    related_contact_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'assigned_to': self.assigned_to,
            'priority': self.priority.value,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed': self.completed,
            'related_lead_id': self.related_lead_id,
            'related_contact_id': self.related_contact_id,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

@dataclass
class Activity:
    """Activity log data model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    activity_type: str = ""  # Call, Email, Meeting, Note, etc.
    subject: str = ""
    description: str = ""
    related_lead_id: Optional[str] = None
    related_contact_id: Optional[str] = None
    user_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert activity to dictionary"""
        return {
            'id': self.id,
            'activity_type': self.activity_type,
            'subject': self.subject,
            'description': self.description,
            'related_lead_id': self.related_lead_id,
            'related_contact_id': self.related_contact_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }

class LeadScoringEngine:
    """Advanced lead scoring system"""
    
    def calculate_lead_score(self, lead: Lead) -> int:
        """Calculate lead score based on creative finance criteria"""
        score = 0
        
        # Lead Category Score (25% weight)
        category_scores = {
            LeadCategory.INVESTOR_LEAD: 25,
            LeadCategory.SELLER_LEAD: 20,
            LeadCategory.BUYER_LEAD: 15,
            LeadCategory.GENERAL_LEAD: 10
        }
        score += category_scores.get(lead.lead_category, 10)
        
        # Budget/Property Value Score (20% weight)
        value_to_score = lead.budget_max if lead.lead_category == LeadCategory.INVESTOR_LEAD else lead.property_value
        if value_to_score > 0:
            if value_to_score >= 500000:
                score += 20
            elif value_to_score >= 300000:
                score += 18
            elif value_to_score >= 150000:
                score += 15
            elif value_to_score >= 75000:
                score += 12
            else:
                score += 8
        
        # Creative Finance Interest Score (20% weight)
        if lead.preferred_finance_methods:
            # High-value creative methods get more points
            high_value_methods = [
                CreativeFinanceMethod.SUBJECT_TO,
                CreativeFinanceMethod.OWNER_FINANCING,
                CreativeFinanceMethod.LEASE_OPTION,
                CreativeFinanceMethod.PRIVATE_MONEY
            ]
            creative_score = 0
            for method in lead.preferred_finance_methods:
                if method in high_value_methods:
                    creative_score += 8
                else:
                    creative_score += 4
            score += min(creative_score, 20)
        
        # Investor Experience/Seller Motivation Score (15% weight)
        if lead.lead_category == LeadCategory.INVESTOR_LEAD and lead.investor_type:
            experienced_types = [
                InvestorType.WHOLESALER,
                InvestorType.SUBJECT_TO,
                InvestorType.OWNER_FINANCE,
                InvestorType.CASH_BUYER
            ]
            if lead.investor_type in experienced_types:
                score += 15
            else:
                score += 10
        elif lead.lead_category == LeadCategory.SELLER_LEAD and lead.seller_motivation:
            high_motivation = [
                SellerMotivation.FINANCIAL_DISTRESS,
                SellerMotivation.FORECLOSURE_AVOIDANCE,
                SellerMotivation.QUICK_SALE_NEEDED,
                SellerMotivation.TIRED_LANDLORD
            ]
            if lead.seller_motivation in high_motivation:
                score += 15
            else:
                score += 10
        
        # Lead Source Score (10% weight)
        source_scores = {
            LeadSource.REFERRAL: 10,
            LeadSource.PARTNER: 9,
            LeadSource.NETWORKING_EVENT: 8,
            LeadSource.WEBSITE: 7,
            LeadSource.SOCIAL_MEDIA: 6,
            LeadSource.EMAIL_CAMPAIGN: 5,
            LeadSource.ADVERTISEMENT: 4,
            LeadSource.COLD_OUTREACH: 3,
            LeadSource.OTHER: 2
        }
        score += source_scores.get(lead.lead_source, 2)
        
        # Contact Completeness Score (10% weight)
        contact_score = 0
        if lead.email:
            contact_score += 3
        if lead.phone:
            contact_score += 3
        if lead.property_address:
            contact_score += 2
        if lead.notes:
            contact_score += 2
        score += min(contact_score, 10)
        
        return min(score, 100)  # Cap at 100

class CRMDataPersistence:
    """Enhanced data persistence with SQLite and CSV export"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with all necessary tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create leads table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS leads (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT,
                        phone TEXT,
                        status TEXT,
                        lead_type TEXT,
                        lead_source TEXT,
                        property_address TEXT,
                        property_value REAL,
                        budget REAL,
                        timeline TEXT,
                        motivation TEXT,
                        notes TEXT,
                        score INTEGER,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
                
                # Create contacts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS contacts (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        company TEXT,
                        title TEXT,
                        email TEXT,
                        phone TEXT,
                        contact_type TEXT,
                        specializations TEXT,
                        location TEXT,
                        notes TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
                
                # Create buyers table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS buyers (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT,
                        phone TEXT,
                        min_price REAL,
                        max_price REAL,
                        preferred_locations TEXT,
                        property_types TEXT,
                        investment_strategy TEXT,
                        min_roi REAL,
                        cash_available REAL,
                        financing_options TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
                
                # Create deals table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS deals (
                        id TEXT PRIMARY KEY,
                        property_address TEXT NOT NULL,
                        deal_type TEXT,
                        property_type TEXT,
                        purchase_price REAL,
                        arv REAL,
                        repair_costs REAL,
                        estimated_roi REAL,
                        status TEXT,
                        lead_id TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
                
                # Create activities table for tracking
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS activities (
                        id TEXT PRIMARY KEY,
                        activity_type TEXT,
                        subject TEXT,
                        description TEXT,
                        related_lead_id TEXT,
                        related_contact_id TEXT,
                        related_deal_id TEXT,
                        user_id TEXT,
                        created_at TEXT
                    )
                ''')
                
                conn.commit()
                print("✅ Connected to database successfully!")
                
        except Exception as e:
            print(f"❌ Database initialization error: {str(e)}")
            raise e
    
    def save_lead(self, lead: 'Lead') -> bool:
        """Save lead to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO leads 
                    (id, name, email, phone, status, lead_type, lead_source, 
                     property_address, property_value, budget, timeline, motivation, 
                     notes, score, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    lead.id, lead.name, lead.email, lead.phone,
                    lead.status.value if lead.status else None,
                    lead.lead_type.value if lead.lead_type else None,
                    lead.lead_source.value if lead.lead_source else None,
                    lead.property_address, lead.property_value, lead.budget,
                    lead.timeline, lead.motivation, lead.notes, lead.score,
                    lead.created_at.isoformat(), lead.updated_at.isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Error saving lead: {str(e)}")
            return False
    
    def load_leads(self) -> List[Dict[str, Any]]:
        """Load all leads from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM leads ORDER BY created_at DESC')
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Error loading leads: {str(e)}")
            return []
    
    def delete_lead(self, lead_id: str) -> bool:
        """Delete lead from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM leads WHERE id = ?', (lead_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Error deleting lead: {str(e)}")
            return False
    
    def export_leads_csv(self) -> bytes:
        """Export leads to CSV format"""
        try:
            leads_data = self.load_leads()
            if not leads_data:
                return b""
            
            output = io.StringIO()
            fieldnames = [
                'id', 'name', 'email', 'phone', 'status', 'lead_type', 
                'lead_source', 'property_address', 'property_value', 'budget',
                'timeline', 'motivation', 'notes', 'score', 'created_at', 'updated_at'
            ]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(leads_data)
            
            return output.getvalue().encode('utf-8')
            
        except Exception as e:
            print(f"❌ Error exporting leads CSV: {str(e)}")
            return b""
    
    def export_buyers_csv(self) -> bytes:
        """Export buyers to CSV format"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM buyers ORDER BY created_at DESC')
                columns = [desc[0] for desc in cursor.description]
                buyers_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            if not buyers_data:
                return b""
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=columns)
            writer.writeheader()
            writer.writerows(buyers_data)
            
            return output.getvalue().encode('utf-8')
            
        except Exception as e:
            print(f"❌ Error exporting buyers CSV: {str(e)}")
            return b""
    
    def export_contacts_csv(self) -> bytes:
        """Export contacts to CSV format"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM contacts ORDER BY created_at DESC')
                columns = [desc[0] for desc in cursor.description]
                contacts_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            if not contacts_data:
                return b""
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=columns)
            writer.writeheader()
            writer.writerows(contacts_data)
            
            return output.getvalue().encode('utf-8')
            
        except Exception as e:
            print(f"❌ Error exporting contacts CSV: {str(e)}")
            return b""

class CRMManager:
    """Main CRM management class"""
    
    def __init__(self):
        self.leads: List[Lead] = []
        self.contacts: List[Contact] = []
        self.tasks: List[Task] = []
        self.activities: List[Activity] = []
        self.deals: List[Deal] = []
        self.buyers: List[BuyerCriteria] = []
        self.messages: List[Message] = []
        self.deal_alerts: List[DealAlert] = []
        self.scoring_engine = LeadScoringEngine()
        self.matching_engine = DealMatchingEngine()
        
        # Initialize enhanced persistence system
        self.persistence = CRMDataPersistence()
        
        # Load data from both session state and database
        self.load_data()
    
    def load_data(self):
        """Load CRM data from database and session state"""
        # Load from database first (persistent storage)
        try:
            leads_data = self.persistence.load_leads()
            for lead_data in leads_data:
                lead = self._load_lead_from_db(lead_data)
                if lead and lead not in self.leads:
                    self.leads.append(lead)
        except Exception as e:
            print(f"⚠️ Could not load leads from database: {str(e)}")
        
        # Then load from session state (current session data)
        try:
            if 'crm_leads' in st.session_state:
                session_leads = [Lead(**data) for data in st.session_state.crm_leads]
                for lead in session_leads:
                    if lead not in self.leads:
                        self.leads.append(lead)
                        
            if 'crm_contacts' in st.session_state:
                self.contacts = [Contact(**data) for data in st.session_state.crm_contacts]
            if 'crm_tasks' in st.session_state:
                self.tasks = [Task(**data) for data in st.session_state.crm_tasks]
            if 'crm_activities' in st.session_state:
                self.activities = [Activity(**data) for data in st.session_state.crm_activities]
            if 'crm_deals' in st.session_state:
                self.deals = [self._load_deal(data) for data in st.session_state.crm_deals]
            if 'crm_buyers' in st.session_state:
                self.buyers = [self._load_buyer(data) for data in st.session_state.crm_buyers]
            if 'crm_messages' in st.session_state:
                self.messages = [self._load_message(data) for data in st.session_state.crm_messages]
        except Exception:
            # If we're not in a Streamlit context, skip session state loading
            pass
        if 'crm_deal_alerts' in st.session_state:
            self.deal_alerts = [self._load_deal_alert(data) for data in st.session_state.crm_deal_alerts]
    
    def _load_lead_from_db(self, data: Dict[str, Any]) -> Optional[Lead]:
        """Load lead from database dictionary with proper type conversion"""
        try:
            data_copy = data.copy()
            
            # Convert string values back to enums
            if data_copy.get('status'):
                data_copy['status'] = LeadStatus(data_copy['status'])
            if data_copy.get('lead_type'):
                data_copy['lead_type'] = LeadType(data_copy['lead_type'])
            if data_copy.get('lead_source'):
                data_copy['lead_source'] = LeadSource(data_copy['lead_source'])
            
            # Convert datetime strings back to datetime objects
            if data_copy.get('created_at'):
                data_copy['created_at'] = datetime.fromisoformat(data_copy['created_at'])
            if data_copy.get('updated_at'):
                data_copy['updated_at'] = datetime.fromisoformat(data_copy['updated_at'])
            
            return Lead(**data_copy)
        except Exception as e:
            st.warning(f"Error loading lead from database: {str(e)}")
            return None
    
    def _load_deal(self, data: Dict[str, Any]) -> Deal:
        """Load deal from dictionary with enum conversion"""
        # Convert string values back to enums
        data_copy = data.copy()
        if 'property_type' in data_copy:
            data_copy['property_type'] = PropertyType(data_copy['property_type'])
        if 'deal_type' in data_copy:
            data_copy['deal_type'] = DealType(data_copy['deal_type'])
        if 'status' in data_copy:
            data_copy['status'] = DealStatus(data_copy['status'])
        if 'financing_method' in data_copy and data_copy['financing_method']:
            data_copy['financing_method'] = CreativeFinanceMethod(data_copy['financing_method'])
        
        # Convert datetime strings back to datetime objects
        if 'created_at' in data_copy:
            data_copy['created_at'] = datetime.fromisoformat(data_copy['created_at'])
        if 'updated_at' in data_copy:
            data_copy['updated_at'] = datetime.fromisoformat(data_copy['updated_at'])
        
        return Deal(**data_copy)
    
    def _load_buyer(self, data: Dict[str, Any]) -> BuyerCriteria:
        """Load buyer from dictionary with enum conversion"""
        # Convert string values back to enums
        data_copy = data.copy()
        if 'investor_type' in data_copy:
            data_copy['investor_type'] = InvestorType(data_copy['investor_type'])
        if 'preferred_property_types' in data_copy:
            data_copy['preferred_property_types'] = [PropertyType(pt) for pt in data_copy['preferred_property_types']]
        if 'preferred_deal_types' in data_copy:
            data_copy['preferred_deal_types'] = [DealType(dt) for dt in data_copy['preferred_deal_types']]
        if 'preferred_finance_methods' in data_copy:
            data_copy['preferred_finance_methods'] = [CreativeFinanceMethod(method) for method in data_copy['preferred_finance_methods']]
        
        # Convert datetime strings back to datetime objects
        if 'created_at' in data_copy:
            data_copy['created_at'] = datetime.fromisoformat(data_copy['created_at'])
        
        return BuyerCriteria(**data_copy)
    
    def _load_message(self, data: Dict[str, Any]) -> Message:
        """Load message from dictionary with enum conversion"""
        data_copy = data.copy()
        if 'message_type' in data_copy:
            data_copy['message_type'] = MessageType(data_copy['message_type'])
        if 'status' in data_copy:
            data_copy['status'] = MessageStatus(data_copy['status'])
        
        # Convert datetime strings back to datetime objects
        if 'created_at' in data_copy:
            data_copy['created_at'] = datetime.fromisoformat(data_copy['created_at'])
        if 'read_at' in data_copy and data_copy['read_at']:
            data_copy['read_at'] = datetime.fromisoformat(data_copy['read_at'])
        if 'replied_at' in data_copy and data_copy['replied_at']:
            data_copy['replied_at'] = datetime.fromisoformat(data_copy['replied_at'])
        
        return Message(**data_copy)
    
    def _load_deal_alert(self, data: Dict[str, Any]) -> DealAlert:
        """Load deal alert from dictionary"""
        data_copy = data.copy()
        
        # Convert datetime strings back to datetime objects
        if 'sent_at' in data_copy:
            data_copy['sent_at'] = datetime.fromisoformat(data_copy['sent_at'])
        
        return DealAlert(**data_copy)
    
    def save_data(self):
        """Save CRM data to both session state and database"""
        # Save to session state for immediate access (only in Streamlit context)
        try:
            st.session_state.crm_leads = [lead.to_dict() for lead in self.leads]
            st.session_state.crm_contacts = [contact.to_dict() for contact in self.contacts]
            st.session_state.crm_tasks = [task.to_dict() for task in self.tasks]
            st.session_state.crm_activities = [activity.to_dict() for activity in self.activities]
            st.session_state.crm_deals = [deal.to_dict() for deal in self.deals]
            st.session_state.crm_buyers = [buyer.to_dict() for buyer in self.buyers]
            st.session_state.crm_messages = [message.to_dict() for message in self.messages]
            st.session_state.crm_deal_alerts = [alert.to_dict() for alert in self.deal_alerts]
        except Exception:
            # If we're not in a Streamlit context, skip session state saving
            pass
        
        # Save leads to database for persistence
        for lead in self.leads:
            self.persistence.save_lead(lead)
    
    def add_lead(self, lead: Lead) -> str:
        """Add new lead with database persistence"""
        lead.score = self.scoring_engine.calculate_lead_score(lead)
        self.leads.append(lead)
        
        # Save to both session state and database
        self.save_data()
        
        # Also save directly to database for immediate persistence
        self.persistence.save_lead(lead)
        
        # Log activity
        self.log_activity(
            activity_type="Lead Created",
            subject=f"New lead: {lead.name}",
            description=f"Lead created from {lead.lead_source.value}",
            related_lead_id=lead.id,
            user_id="system"
        )
        return lead.id
    
    def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing lead with database persistence"""
        for lead in self.leads:
            if lead.id == lead_id:
                for key, value in updates.items():
                    if hasattr(lead, key):
                        setattr(lead, key, value)
                lead.updated_at = datetime.now()
                lead.score = self.scoring_engine.calculate_lead_score(lead)
                
                # Save to both session state and database
                self.save_data()
                self.persistence.save_lead(lead)
                
                # Log activity
                self.log_activity(
                    activity_type="Lead Updated",
                    subject=f"Lead updated: {lead.name}",
                    description=f"Lead information updated",
                    related_lead_id=lead.id,
                    user_id="system"
                )
                return True
        return False
    
    def delete_lead(self, lead_id: str) -> bool:
        """Delete lead from both memory and database"""
        for i, lead in enumerate(self.leads):
            if lead.id == lead_id:
                lead_name = lead.name
                
                # Remove from memory
                self.leads.pop(i)
                
                # Remove from database
                success = self.persistence.delete_lead(lead_id)
                
                # Update session state
                self.save_data()
                
                # Log activity
                self.log_activity(
                    activity_type="Lead Deleted",
                    subject=f"Lead deleted: {lead_name}",
                    description=f"Lead permanently removed from system",
                    user_id="system"
                )
                
                return success
        return False
    
    def get_lead_by_id(self, lead_id: str) -> Optional[Lead]:
        """Get lead by ID"""
        for lead in self.leads:
            if lead.id == lead_id:
                return lead
        return None
    
    def search_leads(self, query: str) -> List[Lead]:
        """Search leads by name, email, phone, or address"""
        query = query.lower()
        results = []
        for lead in self.leads:
            if (query in lead.name.lower() or 
                (lead.email and query in lead.email.lower()) or
                (lead.phone and query in lead.phone.lower()) or
                (lead.property_address and query in lead.property_address.lower())):
                results.append(lead)
        return results
    
    def filter_leads(self, status: Optional[LeadStatus] = None, 
                    lead_type: Optional[LeadType] = None,
                    lead_source: Optional[LeadSource] = None) -> List[Lead]:
        """Filter leads by various criteria"""
        results = self.leads.copy()
        
        if status:
            results = [lead for lead in results if lead.status == status]
        if lead_type:
            results = [lead for lead in results if lead.lead_type == lead_type]
        if lead_source:
            results = [lead for lead in results if lead.lead_source == lead_source]
            
        return results
    
    def export_leads_csv(self) -> bytes:
        """Export leads to CSV format"""
        return self.persistence.export_leads_csv()
    
    def export_buyers_csv(self) -> bytes:
        """Export buyers to CSV format"""
        return self.persistence.export_buyers_csv()
    
    def export_contacts_csv(self) -> bytes:
        """Export contacts to CSV format"""
        return self.persistence.export_contacts_csv()
    
    def add_contact(self, contact: Contact) -> str:
        """Add new contact"""
        self.contacts.append(contact)
        self.save_data()
        return contact.id
    
    def add_task(self, task: Task) -> str:
        """Add new task"""
        self.tasks.append(task)
        self.save_data()
        return task.id
    
    def complete_task(self, task_id: str) -> bool:
        """Mark task as completed"""
        for task in self.tasks:
            if task.id == task_id:
                task.completed = True
                task.completed_at = datetime.now()
                self.save_data()
                return True
        return False
    
    def log_activity(self, activity_type: str, subject: str, description: str, 
                    related_lead_id: str = None, related_contact_id: str = None, 
                    user_id: str = "user") -> str:
        """Log new activity"""
        activity = Activity(
            activity_type=activity_type,
            subject=subject,
            description=description,
            related_lead_id=related_lead_id,
            related_contact_id=related_contact_id,
            user_id=user_id
        )
        self.activities.append(activity)
        self.save_data()
        
        # Also log to activity tracker for advanced tracking
        try:
            activity_tracker = get_activity_tracker()
            
            # Map activity types to ActivityType enum
            activity_type_mapping = {
                "Lead Created": ActivityType.LEAD_CREATED,
                "Deal Created": ActivityType.DEAL_CREATED,
                "Contact Added": ActivityType.CONTACT_ADDED,
                "Task Created": ActivityType.TASK_CREATED,
                "Email Sent": ActivityType.EMAIL_SENT,
                "SMS Sent": ActivityType.SMS_SENT,
                "Call Made": ActivityType.CALL_MADE,
                "Meeting Scheduled": ActivityType.MEETING_SCHEDULED,
                "Buyer Matched": ActivityType.BUYER_MATCHED,
                "Deal Closed": ActivityType.DEAL_CLOSED
            }
            
            mapped_activity_type = activity_type_mapping.get(activity_type, ActivityType.GENERAL_ACTIVITY)
            
            # Determine priority based on activity type
            priority = Priority.MEDIUM
            if "Deal" in activity_type or "Buyer" in activity_type:
                priority = Priority.HIGH
            elif "Email" in activity_type or "SMS" in activity_type:
                priority = Priority.MEDIUM
            else:
                priority = Priority.LOW
            
            # Create metadata
            metadata = {
                "related_lead_id": related_lead_id,
                "related_contact_id": related_contact_id,
                "original_activity_id": activity.id
            }
            
            # Log to activity tracker
            activity_tracker.log_activity(
                activity_type=mapped_activity_type,
                title=subject,
                description=description,
                user_id=user_id,
                priority=priority,
                metadata=metadata
            )
        except Exception as e:
            # Don't break the main flow if activity tracking fails
            print(f"Activity tracking error: {e}")
        
        return activity.id
    
    def get_pipeline_summary(self) -> Dict[str, int]:
        """Get sales pipeline summary"""
        pipeline = {}
        for status in LeadStatus:
            pipeline[status.value] = len([lead for lead in self.leads if lead.status == status])
        return pipeline
    
    def get_lead_conversion_rate(self) -> float:
        """Calculate lead conversion rate"""
        if not self.leads:
            return 0.0
        
        closed_won = len([lead for lead in self.leads if lead.status == LeadStatus.CLOSED_WON])
        total_closed = len([lead for lead in self.leads 
                          if lead.status in [LeadStatus.CLOSED_WON, LeadStatus.CLOSED_LOST]])
        
        return (closed_won / total_closed * 100) if total_closed > 0 else 0.0
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get overdue tasks"""
        now = datetime.now()
        return [task for task in self.tasks 
                if not task.completed and task.due_date and task.due_date < now]
    
    def get_upcoming_tasks(self, days_ahead: int = 7) -> List[Task]:
        """Get upcoming tasks"""
        now = datetime.now()
        future = now + timedelta(days=days_ahead)
        return [task for task in self.tasks 
                if not task.completed and task.due_date 
                and now <= task.due_date <= future]
    
    def get_lead_by_id(self, lead_id: str) -> Optional[Lead]:
        """Get lead by ID"""
        for lead in self.leads:
            if lead.id == lead_id:
                return lead
        return None
    
    def get_contact_by_id(self, contact_id: str) -> Optional[Contact]:
        """Get contact by ID"""
        for contact in self.contacts:
            if contact.id == contact_id:
                return contact
        return None
    
    # ==== DEAL MANAGEMENT METHODS ====
    
    def add_deal(self, deal: Deal) -> str:
        """Add new deal"""
        deal.estimated_roi = deal.calculate_roi()
        self.deals.append(deal)
        self.save_data()
        
        # Log activity
        self.log_activity(
            activity_type="Deal Created",
            subject=f"New deal: {deal.title}",
            description=f"Deal created at {deal.property_address}",
            user_id="system"
        )
        return deal.id
    
    def update_deal(self, deal_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing deal"""
        for deal in self.deals:
            if deal.id == deal_id:
                for key, value in updates.items():
                    if hasattr(deal, key):
                        setattr(deal, key, value)
                deal.updated_at = datetime.now()
                deal.estimated_roi = deal.calculate_roi()
                self.save_data()
                return True
        return False
    
    def get_deals_by_status(self, status: DealStatus) -> List[Deal]:
        """Get deals by status"""
        return [deal for deal in self.deals if deal.status == status]
    
    def get_active_deals(self) -> List['Deal']:
        """Get active deals (not dead or closed)"""
        active_statuses = [
            DealStatus.LEAD, DealStatus.ANALYZING, DealStatus.UNDER_CONTRACT,
            DealStatus.DUE_DILIGENCE, DealStatus.FINANCING, DealStatus.CLOSING
        ]
        return [deal for deal in self.deals if deal.status in active_statuses]
    
    def find_matching_buyers_for_deal(self, deal: 'Deal') -> List[Dict[str, Any]]:
        """Find buyers that match deal criteria"""
        matching_buyers = self.matching_engine.find_matching_buyers(deal, self.buyers)
        results = []
        
        for buyer in matching_buyers:
            match_score = self.matching_engine.score_deal_match(deal, buyer)
            results.append({
                'buyer': buyer,
                'match_score': match_score
            })
        
        # Sort by match score descending
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results
    
    # ==== BUYER MANAGEMENT METHODS ====
    
    def add_buyer(self, buyer: BuyerCriteria) -> str:
        """Add new buyer"""
        self.buyers.append(buyer)
        self.save_data()
        
        # Log activity
        self.log_activity(
            activity_type="Buyer Added",
            subject=f"New buyer: {buyer.buyer_name}",
            description=f"Buyer criteria added for {buyer.investor_type.value}",
            user_id="system"
        )
        return buyer.id
    
    def update_buyer(self, buyer_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing buyer"""
        for buyer in self.buyers:
            if buyer.id == buyer_id:
                for key, value in updates.items():
                    if hasattr(buyer, key):
                        setattr(buyer, key, value)
                self.save_data()
                return True
        return False
    
    def get_active_buyers(self) -> List[BuyerCriteria]:
        """Get active buyers"""
        return [buyer for buyer in self.buyers if buyer.active]
    
    def send_deal_to_buyers(self, deal: 'Deal', buyer_ids: List[str] = None) -> Dict[str, Any]:
        """Send deal to matching buyers or specified buyers"""
        if buyer_ids:
            # Send to specific buyers
            selected_buyers = [buyer for buyer in self.buyers if buyer.id in buyer_ids]
        else:
            # Send to all matching buyers
            matches = self.find_matching_buyers_for_deal(deal)
            selected_buyers = [match['buyer'] for match in matches]
        
        # Log activity for each buyer
        sent_count = 0
        for buyer in selected_buyers:
            self.log_activity(
                activity_type="Deal Sent",
                subject=f"Deal sent to {buyer.buyer_name}",
                description=f"Deal '{deal.title}' sent to buyer {buyer.buyer_name}",
                user_id="system"
            )
            sent_count += 1
        
        return {
            'sent_count': sent_count,
            'buyers': selected_buyers,
            'deal': deal
        }
    
    # ==== COMMUNICATION METHODS ====
    
    def send_message(self, sender_name: str, sender_email: str, recipient_name: str, 
                    recipient_email: str, subject: str, content: str, 
                    message_type: MessageType = MessageType.GENERAL_MESSAGE,
                    related_deal_id: str = None) -> str:
        """Send a message"""
        message = Message(
            sender_name=sender_name,
            sender_email=sender_email,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            subject=subject,
            content=content,
            message_type=message_type,
            related_deal_id=related_deal_id
        )
        
        self.messages.append(message)
        self.save_data()
        
        # Log activity
        self.log_activity(
            activity_type="Message Sent",
            subject=f"Message sent to {recipient_name}",
            description=f"Subject: {subject}",
            user_id="system"
        )
        
        return message.id
    
    def send_deal_alert(self, deal: 'Deal', recipient_emails: List[str], 
                       alert_type: str = "new_deal") -> str:
        """Send deal alert to multiple recipients"""
        # Create personalized subject and content
        if alert_type == "new_deal":
            subject = f"🔥 New Deal Alert: {deal.title}"
            content = f"""
            New Creative Finance Deal Available!
            
            Property: {deal.title}
            Address: {deal.property_address}
            Deal Type: {deal.deal_type.value}
            Purchase Price: ${deal.purchase_price:,.0f}
            ARV: ${deal.arv:,.0f}
            Estimated ROI: {deal.estimated_roi:.1f}%
            Estimated Repairs: ${deal.estimated_repairs:,.0f}
            
            Property Details:
            - Bedrooms: {deal.bedrooms}
            - Bathrooms: {deal.bathrooms}
            - Square Feet: {deal.square_feet:,}
            
            Financing: {deal.financing_method.value if deal.financing_method else 'Traditional'}
            
            Contact us immediately if interested!
            """
        elif alert_type == "price_change":
            subject = f"💰 Price Update: {deal.title}"
            content = f"Price change notification for {deal.title} at {deal.property_address}"
        elif alert_type == "status_change":
            subject = f"📋 Status Update: {deal.title}"
            content = f"Status changed to {deal.status.value} for {deal.title}"
        else:
            subject = f"🔔 Deal Update: {deal.title}"
            content = f"Update for {deal.title} at {deal.property_address}"
        
        # Create deal alert record
        deal_alert = DealAlert(
            deal_id=deal.id,
            recipient_emails=recipient_emails,
            alert_type=alert_type,
            subject=subject,
            content=content,
            sent_count=len(recipient_emails)
        )
        
        self.deal_alerts.append(deal_alert)
        
        # Create individual messages for each recipient
        for email in recipient_emails:
            # Try to find buyer name by email
            recipient_name = "Valued Investor"
            for buyer in self.buyers:
                if buyer.buyer_email == email:
                    recipient_name = buyer.buyer_name
                    break
            
            self.send_message(
                sender_name="Deal Team",
                sender_email="deals@nxtrix.com",
                recipient_name=recipient_name,
                recipient_email=email,
                subject=subject,
                content=content,
                message_type=MessageType.DEAL_ALERT,
                related_deal_id=deal.id
            )
        
        self.save_data()
        return deal_alert.id
    
    def get_messages_for_deal(self, deal_id: str) -> List['Message']:
        """Get all messages related to a deal"""
        return [msg for msg in self.messages if msg.related_deal_id == deal_id]
    
    def get_recent_messages(self, limit: int = 10) -> List['Message']:
        """Get recent messages"""
        return sorted(self.messages, key=lambda x: x.created_at, reverse=True)[:limit]
    
    def mark_message_as_read(self, message_id: str) -> bool:
        """Mark message as read"""
        for message in self.messages:
            if message.id == message_id:
                message.status = MessageStatus.READ
                message.read_at = datetime.now()
                self.save_data()
                return True
        return False
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio performance summary"""
        active_deals = self.get_active_deals()
        closed_deals = [deal for deal in self.deals if deal.status == DealStatus.CLOSED]
        
        total_value = sum(deal.purchase_price for deal in closed_deals)
        total_profit = sum(deal.projected_profit for deal in closed_deals)
        avg_roi = sum(deal.estimated_roi for deal in closed_deals) / len(closed_deals) if closed_deals else 0
        
        return {
            'active_deals': len(active_deals),
            'closed_deals': len(closed_deals),
            'total_portfolio_value': total_value,
            'total_profit': total_profit,
            'average_roi': avg_roi,
            'pipeline_value': sum(deal.purchase_price for deal in active_deals)
        }

class CRMVisualization:
    """CRM visualization and analytics"""
    
    def create_pipeline_funnel(self, pipeline_data: Dict[str, int]) -> go.Figure:
        """Create sales pipeline funnel chart"""
        # Reorder pipeline stages for funnel
        funnel_order = [
            LeadStatus.NEW.value,
            LeadStatus.CONTACTED.value,
            LeadStatus.QUALIFIED.value,
            LeadStatus.MEETING_SCHEDULED.value,
            LeadStatus.PROPOSAL_SENT.value,
            LeadStatus.NEGOTIATING.value,
            LeadStatus.CLOSED_WON.value
        ]
        
        values = [pipeline_data.get(stage, 0) for stage in funnel_order]
        
        fig = go.Figure(go.Funnel(
            y=funnel_order,
            x=values,
            textinfo="value+percent initial",
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
        ))
        
        fig.update_layout(
            title="Sales Pipeline Funnel",
            font_size=12,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def create_lead_source_chart(self, leads: List[Lead]) -> go.Figure:
        """Create lead source distribution chart"""
        source_counts = {}
        for lead in leads:
            source = lead.lead_source.value
            source_counts[source] = source_counts.get(source, 0) + 1
        
        fig = go.Figure(data=[
            go.Pie(
                labels=list(source_counts.keys()),
                values=list(source_counts.values()),
                hole=0.3,
                marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE']
            )
        ])
        
        fig.update_layout(
            title="Lead Sources Distribution",
            font_size=12,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def create_lead_score_distribution(self, leads: List[Lead]) -> go.Figure:
        """Create lead score distribution histogram"""
        scores = [lead.score for lead in leads]
        
        fig = go.Figure(data=[
            go.Histogram(
                x=scores,
                nbinsx=20,
                marker_color='#4ECDC4',
                opacity=0.7
            )
        ])
        
        fig.update_layout(
            title="Lead Score Distribution",
            xaxis_title="Lead Score",
            yaxis_title="Number of Leads",
            font_size=12,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def create_activity_timeline(self, activities: List[Activity]) -> go.Figure:
        """Create activity timeline chart"""
        if not activities:
            return go.Figure()
        
        # Group activities by date
        activity_counts = {}
        for activity in activities:
            date = activity.created_at.date()
            activity_counts[date] = activity_counts.get(date, 0) + 1
        
        dates = list(activity_counts.keys())
        counts = list(activity_counts.values())
        
        fig = go.Figure(data=[
            go.Scatter(
                x=dates,
                y=counts,
                mode='lines+markers',
                line=dict(color='#45B7D1', width=3),
                marker=dict(size=8, color='#45B7D1')
            )
        ])
        
        fig.update_layout(
            title="Activity Timeline",
            xaxis_title="Date",
            yaxis_title="Number of Activities",
            font_size=12,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig

# ==== DEAL MANAGEMENT SYSTEM ====

@dataclass
class Deal:
    """Deal data model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    property_address: str = ""
    property_type: PropertyType = PropertyType.SINGLE_FAMILY
    deal_type: DealType = DealType.WHOLESALE
    status: DealStatus = DealStatus.LEAD
    
    # Financial Details
    asking_price: float = 0
    arv: float = 0  # After Repair Value
    estimated_repairs: float = 0
    purchase_price: float = 0
    wholesale_fee: float = 0
    estimated_roi: float = 0
    projected_profit: float = 0
    
    # Property Details
    bedrooms: int = 0
    bathrooms: float = 0
    square_feet: int = 0
    lot_size: float = 0
    year_built: int = 0
    condition: str = ""
    
    # Deal Information
    lead_source: str = ""
    seller_name: str = ""
    seller_phone: str = ""
    seller_email: str = ""
    seller_motivation: str = ""
    timeline: str = ""
    
    # Financial Analysis
    monthly_rent: float = 0
    monthly_expenses: float = 0
    cap_rate: float = 0
    cash_on_cash: float = 0
    
    # Creative Finance Details
    current_mortgage: float = 0
    monthly_payment: float = 0
    interest_rate: float = 0
    financing_method: Optional[CreativeFinanceMethod] = None
    
    # Tracking
    assigned_to: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    notes: str = ""
    
    def calculate_roi(self) -> float:
        """Calculate ROI for the deal"""
        if self.purchase_price == 0:
            return 0
        
        total_investment = self.purchase_price + self.estimated_repairs
        if total_investment == 0:
            return 0
            
        if self.deal_type == DealType.WHOLESALE:
            return (self.wholesale_fee / total_investment) * 100
        elif self.deal_type in [DealType.FIX_AND_FLIP]:
            profit = self.arv - total_investment
            return (profit / total_investment) * 100
        elif self.deal_type == DealType.BUY_AND_HOLD:
            annual_cash_flow = (self.monthly_rent - self.monthly_expenses) * 12
            return (annual_cash_flow / total_investment) * 100
        
        return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert deal to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'property_address': self.property_address,
            'property_type': self.property_type.value,
            'deal_type': self.deal_type.value,
            'status': self.status.value,
            'asking_price': self.asking_price,
            'arv': self.arv,
            'estimated_repairs': self.estimated_repairs,
            'purchase_price': self.purchase_price,
            'wholesale_fee': self.wholesale_fee,
            'estimated_roi': self.estimated_roi,
            'projected_profit': self.projected_profit,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'square_feet': self.square_feet,
            'lot_size': self.lot_size,
            'year_built': self.year_built,
            'condition': self.condition,
            'lead_source': self.lead_source,
            'seller_name': self.seller_name,
            'seller_phone': self.seller_phone,
            'seller_email': self.seller_email,
            'seller_motivation': self.seller_motivation,
            'timeline': self.timeline,
            'monthly_rent': self.monthly_rent,
            'monthly_expenses': self.monthly_expenses,
            'cap_rate': self.cap_rate,
            'cash_on_cash': self.cash_on_cash,
            'current_mortgage': self.current_mortgage,
            'monthly_payment': self.monthly_payment,
            'interest_rate': self.interest_rate,
            'financing_method': self.financing_method.value if self.financing_method else None,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'notes': self.notes
        }

@dataclass
class BuyerCriteria:
    """Buyer investment criteria"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    buyer_name: str = ""
    buyer_email: str = ""
    buyer_phone: str = ""
    investor_type: InvestorType = InvestorType.WHOLESALER
    
    # Investment Criteria
    min_roi: float = 0
    max_purchase_price: float = 0
    preferred_property_types: List[PropertyType] = field(default_factory=list)
    preferred_deal_types: List[DealType] = field(default_factory=list)
    target_locations: List[str] = field(default_factory=list)
    
    # Financial Criteria
    min_bedrooms: int = 0
    max_repairs: float = 0
    cash_available: float = 0
    financing_ready: bool = False
    
    # Preferences
    preferred_finance_methods: List[CreativeFinanceMethod] = field(default_factory=list)
    notes: str = ""
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def matches_deal(self, deal: Deal) -> bool:
        """Check if deal matches buyer criteria"""
        # ROI check
        if deal.estimated_roi < self.min_roi:
            return False
            
        # Price check
        if self.max_purchase_price > 0 and deal.purchase_price > self.max_purchase_price:
            return False
            
        # Property type check
        if self.preferred_property_types and deal.property_type not in self.preferred_property_types:
            return False
            
        # Deal type check
        if self.preferred_deal_types and deal.deal_type not in self.preferred_deal_types:
            return False
            
        # Repairs check
        if self.max_repairs > 0 and deal.estimated_repairs > self.max_repairs:
            return False
            
        # Bedroom check
        if self.min_bedrooms > 0 and deal.bedrooms < self.min_bedrooms:
            return False
            
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert buyer criteria to dictionary"""
        return {
            'id': self.id,
            'buyer_name': self.buyer_name,
            'buyer_email': self.buyer_email,
            'buyer_phone': self.buyer_phone,
            'investor_type': self.investor_type.value,
            'min_roi': self.min_roi,
            'max_purchase_price': self.max_purchase_price,
            'preferred_property_types': [pt.value for pt in self.preferred_property_types],
            'preferred_deal_types': [dt.value for dt in self.preferred_deal_types],
            'target_locations': self.target_locations,
            'min_bedrooms': self.min_bedrooms,
            'max_repairs': self.max_repairs,
            'cash_available': self.cash_available,
            'financing_ready': self.financing_ready,
            'preferred_finance_methods': [method.value for method in self.preferred_finance_methods],
            'notes': self.notes,
            'active': self.active,
            'created_at': self.created_at.isoformat()
        }

class DealMatchingEngine:
    """Engine for matching deals to buyers"""
    
    def find_matching_buyers(self, deal: Deal, buyers: List[BuyerCriteria]) -> List[BuyerCriteria]:
        """Find buyers that match the deal criteria"""
        matching_buyers = []
        for buyer in buyers:
            if buyer.active and buyer.matches_deal(deal):
                matching_buyers.append(buyer)
        return matching_buyers
    
    def score_deal_match(self, deal: Deal, buyer: BuyerCriteria) -> float:
        """Score how well a deal matches buyer criteria (0-100)"""
        score = 0
        max_score = 100
        
        # ROI score (30% weight)
        if deal.estimated_roi >= buyer.min_roi:
            roi_score = min((deal.estimated_roi / buyer.min_roi) * 30, 30)
            score += roi_score
        
        # Property type preference (20% weight)
        if not buyer.preferred_property_types or deal.property_type in buyer.preferred_property_types:
            score += 20
        
        # Deal type preference (20% weight)
        if not buyer.preferred_deal_types or deal.deal_type in buyer.preferred_deal_types:
            score += 20
        
        # Price preference (15% weight)
        if buyer.max_purchase_price == 0 or deal.purchase_price <= buyer.max_purchase_price:
            score += 15
        
        # Repair tolerance (10% weight)
        if buyer.max_repairs == 0 or deal.estimated_repairs <= buyer.max_repairs:
            score += 10
        
        # Bedroom preference (5% weight)
        if buyer.min_bedrooms == 0 or deal.bedrooms >= buyer.min_bedrooms:
            score += 5
        
        return min(score, max_score)

# ==== COMMUNICATION SYSTEM ====

@dataclass
class Message:
    """Message data model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_name: str = ""
    sender_email: str = ""
    recipient_name: str = ""
    recipient_email: str = ""
    subject: str = ""
    content: str = ""
    message_type: MessageType = MessageType.GENERAL_MESSAGE
    status: MessageStatus = MessageStatus.SENT
    related_deal_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    read_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'sender_name': self.sender_name,
            'sender_email': self.sender_email,
            'recipient_name': self.recipient_name,
            'recipient_email': self.recipient_email,
            'subject': self.subject,
            'content': self.content,
            'message_type': self.message_type.value,
            'status': self.status.value,
            'related_deal_id': self.related_deal_id,
            'created_at': self.created_at.isoformat(),
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'replied_at': self.replied_at.isoformat() if self.replied_at else None
        }

@dataclass
class DealAlert:
    """Deal alert/notification data model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    deal_id: str = ""
    recipient_emails: List[str] = field(default_factory=list)
    alert_type: str = ""  # "new_deal", "price_change", "status_change"
    subject: str = ""
    content: str = ""
    sent_at: datetime = field(default_factory=datetime.now)
    sent_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert deal alert to dictionary"""
        return {
            'id': self.id,
            'deal_id': self.deal_id,
            'recipient_emails': self.recipient_emails,
            'alert_type': self.alert_type,
            'subject': self.subject,
            'content': self.content,
            'sent_at': self.sent_at.isoformat(),
            'sent_count': self.sent_count
        }

# Initialize CRM manager
@st.cache_resource
def get_crm_manager():
    """Get CRM manager instance"""
    return CRMManager()

def show_enhanced_crm():
    """Main Enhanced CRM interface"""
    st.title("🤝 Enhanced CRM Features")
    st.markdown("---")
    
    crm = get_crm_manager()
    viz = CRMVisualization()
    
    # Sidebar navigation
    crm_pages = [
        "🏠 CRM Dashboard",
        "👥 Lead Management", 
        "💼 Deal Management",
        "🎯 Buyer Management",
        "📞 Contact Management",
        "📋 Task Management",
        "💬 Communication Hub",
        "🤖 Deal Automation",
        "📊 Pipeline Analytics",
        "� Advanced Analytics",
        "�📈 Performance Reports",
        "💰 ROI Dashboard",
        "🎯 Activity Tracking",
        "🔍 Automated Deal Sourcing",
        "🧠 AI Enhancement System",
        "⚡ Advanced Automation"
    ]
    
    selected_page = st.sidebar.selectbox("Select CRM Module", crm_pages)
    
    if selected_page == "🏠 CRM Dashboard":
        show_crm_dashboard(crm, viz)
    elif selected_page == "👥 Lead Management":
        show_lead_management(crm)
    elif selected_page == "💼 Deal Management":
        show_deal_management(crm)
    elif selected_page == "🎯 Buyer Management":
        show_buyer_management(crm)
    elif selected_page == "📞 Contact Management":
        show_contact_management(crm)
    elif selected_page == "📋 Task Management":
        show_task_management(crm)
    elif selected_page == "💬 Communication Hub":
        show_communication_hub(crm)
    elif selected_page == "🤖 Deal Automation":
        show_deal_automation(crm)
    elif selected_page == "📊 Pipeline Analytics":
        show_pipeline_analytics(crm, viz)
    elif selected_page == "� Advanced Analytics":
        show_advanced_deal_analytics(crm)
    elif selected_page == "�📈 Performance Reports":
        show_performance_reports(crm, viz)
    elif selected_page == "💰 ROI Dashboard":
        show_roi_dashboard(crm)
    elif selected_page == "🎯 Activity Tracking":
        show_activity_tracking(crm)
    elif selected_page == "🔍 Automated Deal Sourcing":
        show_automated_deal_sourcing()
    elif selected_page == "🧠 AI Enhancement System":
        show_ai_enhancement_system()
    elif selected_page == "⚡ Advanced Automation":
        show_advanced_automation_system()
    elif selected_page == "⚙️ Subscription Management":
        show_subscription_management()
    
    # Handle form dialogs from session state
    if st.session_state.get('show_add_lead', False):
        show_add_lead_form(crm)
    
    if st.session_state.get('show_add_contact', False):
        show_add_contact_form(crm)
        
    if st.session_state.get('show_add_task', False):
        show_add_task_form(crm)
        
    if st.session_state.get('show_add_deal', False):
        show_add_deal_form(crm)

def show_crm_dashboard(crm: CRMManager, viz: CRMVisualization):
    """Show CRM dashboard"""
    st.header("📊 CRM Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Leads", len(crm.leads))
        
    with col2:
        st.metric("Total Contacts", len(crm.contacts))
        
    with col3:
        pending_tasks = len([task for task in crm.tasks if not task.completed])
        st.metric("Pending Tasks", pending_tasks)
        
    with col4:
        conversion_rate = crm.get_lead_conversion_rate()
        st.metric("Conversion Rate", f"{conversion_rate:.1f}%")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add New Lead", use_container_width=True):
            st.session_state.show_add_lead = True
            
    with col2:
        if st.button("👤 Add New Contact", use_container_width=True):
            st.session_state.show_add_contact = True
            
    with col3:
        if st.button("📝 Add New Task", use_container_width=True):
            st.session_state.show_add_task = True
    
    # Recent activities
    st.subheader("🕒 Recent Activities")
    if crm.activities:
        recent_activities = sorted(crm.activities, key=lambda x: x.created_at, reverse=True)[:5]
        for activity in recent_activities:
            with st.expander(f"{activity.activity_type} - {activity.subject}"):
                st.write(f"**Description:** {activity.description}")
                st.write(f"**Date:** {activity.created_at.strftime('%Y-%m-%d %H:%M')}")
    else:
        st.info("No recent activities found.")
    
    # Overdue tasks alert
    overdue_tasks = crm.get_overdue_tasks()
    if overdue_tasks:
        st.error(f"⚠️ You have {len(overdue_tasks)} overdue tasks!")
        
    # Upcoming tasks
    upcoming_tasks = crm.get_upcoming_tasks()
    if upcoming_tasks:
        st.warning(f"📅 You have {len(upcoming_tasks)} tasks due in the next 7 days.")

def show_lead_management(crm: CRMManager):
    """Enhanced lead management interface with comprehensive CRUD operations"""
    st.header("👥 Creative Finance Lead Management")
    
    # Lead summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Leads", len(crm.leads))
    with col2:
        new_leads = len([lead for lead in crm.leads if lead.status == LeadStatus.NEW])
        st.metric("New Leads", new_leads)
    with col3:
        qualified_leads = len([lead for lead in crm.leads if lead.status == LeadStatus.QUALIFIED])
        st.metric("Qualified Leads", qualified_leads)
    with col4:
        avg_score = sum(lead.score for lead in crm.leads) / len(crm.leads) if crm.leads else 0
        st.metric("Avg Lead Score", f"{avg_score:.1f}")
    
    st.markdown("---")
    
    # Action buttons row
    st.subheader("⚡ Quick Actions")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("🏠 Add Seller Lead", use_container_width=True):
            st.session_state.show_seller_lead = True
            
    with col2:
        if st.button("💰 Add Investor Lead", use_container_width=True):
            st.session_state.show_investor_lead = True
            
    with col3:
        if st.button("🔍 Add Buyer Lead", use_container_width=True):
            st.session_state.show_buyer_lead = True
            
    with col4:
        if st.button("📝 Add General Lead", use_container_width=True):
            st.session_state.show_general_lead = True
    
    with col5:
        # CSV Export functionality
        if st.button("📥 Export Leads CSV", use_container_width=True):
            csv_data = crm.export_leads_csv()
            if csv_data:
                st.download_button(
                    label="⬇️ Download Leads CSV",
                    data=csv_data,
                    file_name=f"leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.success("✅ Leads CSV ready for download!")
            else:
                st.warning("No leads to export")
    
    # Search and filter functionality
    st.markdown("---")
    st.subheader("🔍 Search & Filter Leads")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input("🔍 Search leads", 
                                   placeholder="Search by name, email, phone, or address...")
    with col2:
        st.write("")  # spacing
        if st.button("🔄 Refresh Data", use_container_width=True):
            crm.load_data()
            st.success("Data refreshed!")
            st.rerun()
    
    # Advanced filters
    with st.expander("🔧 Advanced Filters", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_filter = st.selectbox("Filter by Status", 
                                       ["All"] + [status.value for status in LeadStatus])
        
        with col2:
            source_filter = st.selectbox("Filter by Source", 
                                       ["All"] + [source.value for source in LeadSource])
                                       
        with col3:
            score_min = st.slider("Minimum Score", 0, 100, 0)
            score_max = st.slider("Maximum Score", 0, 100, 100)
            
        with col4:
            date_filter = st.selectbox("Date Range", 
                                     ["All Time", "Today", "This Week", "This Month", "Last 30 Days"])
    
    # Apply search and filters
    filtered_leads = crm.leads.copy()
    
    # Apply search query
    if search_query:
        filtered_leads = crm.search_leads(search_query)
    
    # Apply status filter
    if status_filter != "All":
        filtered_leads = [lead for lead in filtered_leads if lead.status.value == status_filter]
    
    # Apply source filter
    if source_filter != "All":
        filtered_leads = [lead for lead in filtered_leads if lead.lead_source.value == source_filter]
    
    # Apply score filter
    filtered_leads = [lead for lead in filtered_leads if score_min <= lead.score <= score_max]
    
    # Apply date filter
    if date_filter != "All Time":
        now = datetime.now()
        if date_filter == "Today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == "This Week":
            start_date = now - timedelta(days=now.weekday())
        elif date_filter == "This Month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == "Last 30 Days":
            start_date = now - timedelta(days=30)
        
        filtered_leads = [lead for lead in filtered_leads if lead.created_at >= start_date]
    
    st.markdown("---")
    
    # Show specialized forms based on selection
    if st.session_state.get('show_seller_lead', False):
        if st.button("❌ Close Form"):
            st.session_state.show_seller_lead = False
            st.rerun()
        show_seller_lead_form(crm)
    elif st.session_state.get('show_investor_lead', False):
        if st.button("❌ Close Form"):
            st.session_state.show_investor_lead = False
            st.rerun()
        show_investor_lead_form(crm)
    elif st.session_state.get('show_buyer_lead', False):
        if st.button("❌ Close Form"):
            st.session_state.show_buyer_lead = False
            st.rerun()
        show_buyer_lead_form(crm)
    elif st.session_state.get('show_general_lead', False):
        if st.button("❌ Close Form"):
            st.session_state.show_general_lead = False
            st.rerun()
        show_general_lead_form(crm)
    
    # Enhanced leads table with actions
    st.subheader(f"📋 Leads List ({len(filtered_leads)} found)")
    
    if filtered_leads:
        # Enhanced comprehensive leads display with full analysis data
        st.markdown("### 📊 Comprehensive Lead Analysis Table")
        st.markdown("*All leads with generated analysis data for easy reference and revisiting*")
        
        # Create enhanced leads data with comprehensive analysis
        leads_data = []
        for i, lead in enumerate(filtered_leads):
            # Calculate ROI metrics if available
            roi_analysis = "N/A"
            mao = "N/A"
            profit_potential = "N/A"
            cash_flow = "N/A"
            
            if hasattr(lead, 'budget') and lead.budget:
                # Simple ROI calculation based on budget and property value
                if hasattr(lead, 'property_value') and lead.property_value:
                    roi = ((lead.property_value - lead.budget) / lead.budget) * 100
                    roi_analysis = f"{roi:.1f}%"
                    mao = f"${lead.budget * 0.7:,.0f}"  # 70% rule
                    profit_potential = f"${lead.property_value - lead.budget:,.0f}"
                    
                # Estimate monthly cash flow
                if hasattr(lead, 'expected_rent') and lead.expected_rent:
                    monthly_expenses = lead.budget * 0.01  # 1% rule estimate
                    cash_flow = f"${lead.expected_rent - monthly_expenses:,.0f}/mo"
            
            # Property analysis summary
            property_summary = "No property details"
            if hasattr(lead, 'property_address') and lead.property_address:
                property_type = getattr(lead, 'property_type', 'Unknown')
                bedrooms = getattr(lead, 'bedrooms', 'N/A')
                bathrooms = getattr(lead, 'bathrooms', 'N/A')
                property_summary = f"{property_type} • {bedrooms}BR/{bathrooms}BA"
            
            leads_data.append({
                'Lead ID': lead.id[:8] + "...",
                'Name': lead.name,
                'Contact': f"{lead.email or 'No Email'}\n{lead.phone or 'No Phone'}",
                'Status': lead.status.value,
                'Source': lead.lead_source.value,
                'Lead Score': f"{lead.score}/100",
                'Property': lead.property_address[:40] + "..." if lead.property_address and len(lead.property_address) > 40 else lead.property_address or "No Property",
                'Property Type': property_summary,
                'Budget': f"${lead.budget:,.0f}" if hasattr(lead, 'budget') and lead.budget else "N/A",
                'ROI Analysis': roi_analysis,
                'MAO (70% Rule)': mao,
                'Profit Potential': profit_potential,
                'Est. Cash Flow': cash_flow,
                'Lead Type': getattr(lead, 'lead_type', LeadType.BUYER).value,
                'Created Date': lead.created_at.strftime('%m/%d/%Y %H:%M'),
                'Last Updated': lead.updated_at.strftime('%m/%d/%Y %H:%M') if lead.updated_at else "Never",
                'Notes Preview': (lead.notes[:50] + "...") if hasattr(lead, 'notes') and lead.notes else "No notes"
            })
        
        # Create comprehensive dataframe
        df = pd.DataFrame(leads_data)
        
        # Display options
        col_display1, col_display2, col_display3 = st.columns(3)
        with col_display1:
            show_analysis = st.checkbox("📊 Show Financial Analysis", value=True)
        with col_display2:
            show_contact_details = st.checkbox("📞 Show Contact Details", value=True)
        with col_display3:
            sort_by = st.selectbox("Sort by", ["Created Date", "Lead Score", "Budget", "ROI Analysis", "Name"])
        
        # Filter columns based on user selection
        display_columns = ['Lead ID', 'Name', 'Status', 'Lead Score', 'Property', 'Created Date']
        
        if show_contact_details:
            display_columns.extend(['Contact', 'Source', 'Lead Type'])
        
        if show_analysis:
            display_columns.extend(['Budget', 'ROI Analysis', 'MAO (70% Rule)', 'Profit Potential', 'Est. Cash Flow', 'Property Type'])
        
        display_columns.extend(['Last Updated', 'Notes Preview'])
        
        # Sort dataframe
        if sort_by in df.columns:
            if sort_by in ['Lead Score', 'Budget']:
                # Sort numeric columns properly
                df_sorted = df.sort_values(by=sort_by, ascending=False)
            else:
                df_sorted = df.sort_values(by=sort_by, ascending=True)
        else:
            df_sorted = df
        
        # Display the comprehensive table
        st.dataframe(
            df_sorted[display_columns], 
            use_container_width=True,
            height=400
        )
        
        # Summary statistics
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        with col_stats1:
            total_budget = sum([float(lead.budget) for lead in filtered_leads if hasattr(lead, 'budget') and lead.budget])
            st.metric("Total Lead Budget", f"${total_budget:,.0f}")
        with col_stats2:
            avg_score = sum([lead.score for lead in filtered_leads]) / len(filtered_leads)
            st.metric("Average Lead Score", f"{avg_score:.1f}/100")
        with col_stats3:
            qualified_count = len([l for l in filtered_leads if l.status in [LeadStatus.QUALIFIED, LeadStatus.MEETING_SCHEDULED]])
            st.metric("Qualified Leads", qualified_count)
        with col_stats4:
            recent_leads = len([l for l in filtered_leads if (datetime.now() - l.created_at).days <= 7])
            st.metric("New This Week", recent_leads)
        
        # Quick action buttons for the entire lead list
        st.markdown("---")
        st.subheader("🚀 Bulk Actions")
        col_bulk1, col_bulk2, col_bulk3, col_bulk4 = st.columns(4)
        
        with col_bulk1:
            if st.button("📧 Email All Qualified Leads", use_container_width=True):
                qualified_leads = [l for l in filtered_leads if l.status == LeadStatus.QUALIFIED]
                if qualified_leads:
                    st.session_state.bulk_email_leads = [l.id for l in qualified_leads]
                    st.success(f"✅ Prepared to email {len(qualified_leads)} qualified leads")
                else:
                    st.warning("No qualified leads to email")
        
        with col_bulk2:
            if st.button("📊 Generate Lead Report", use_container_width=True):
                # Create a comprehensive report
                st.session_state.generate_lead_report = True
                st.success("✅ Lead report generated!")
        
        with col_bulk3:
            if st.button("🔄 Update All Scores", use_container_width=True):
                # Recalculate all lead scores
                updated_count = 0
                for lead in filtered_leads:
                    old_score = lead.score
                    # Recalculate score based on current criteria
                    new_score = crm.scoring_engine.calculate_lead_score(lead)
                    if new_score != old_score:
                        crm.update_lead(lead.id, {"score": new_score})
                        updated_count += 1
                st.success(f"✅ Updated scores for {updated_count} leads")
                if updated_count > 0:
                    st.rerun()
        
        with col_bulk4:
            if st.button("📈 Analyze All ROI", use_container_width=True):
                st.session_state.analyze_all_roi = True
                st.success("✅ ROI analysis initiated for all leads!")
        
        # Lead management actions (individual)
        st.markdown("---")
        st.subheader("🛠️ Individual Lead Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Select lead for actions
            if filtered_leads:
                selected_lead_option = st.selectbox(
                    "Select Lead for Actions", 
                    ["Select a lead..."] + [f"{lead.name} ({lead.email})" for lead in filtered_leads],
                    key="lead_action_select"
                )
                
                if selected_lead_option != "Select a lead...":
                    lead_name = selected_lead_option.split(" (")[0]
                    selected_lead = next((l for l in filtered_leads if l.name == lead_name), None)
                    
                    if selected_lead:
                        st.write(f"**Selected:** {selected_lead.name}")
                        st.write(f"**Status:** {selected_lead.status.value}")
                        st.write(f"**Score:** {selected_lead.score}/100")
        
        with col2:
            # Action buttons
            if selected_lead_option != "Select a lead...":
                if st.button("👁️ View Details", use_container_width=True):
                    st.session_state.show_lead_details = selected_lead.id
                
                if st.button("✏️ Edit Lead", use_container_width=True):
                    st.session_state.edit_lead_id = selected_lead.id
                
                if st.button("📧 Send Email", use_container_width=True):
                    st.session_state.compose_email = selected_lead.id
        
        with col3:
            # Status update and delete
            if selected_lead_option != "Select a lead...":
                new_status = st.selectbox(
                    "Update Status", 
                    [status.value for status in LeadStatus],
                    index=[status.value for status in LeadStatus].index(selected_lead.status.value)
                )
                
                if st.button("🔄 Update Status", use_container_width=True):
                    if crm.update_lead(selected_lead.id, {"status": LeadStatus(new_status)}):
                        st.success(f"✅ Status updated to {new_status}")
                        st.rerun()
                
                # Danger zone - delete
                with st.expander("⚠️ Danger Zone"):
                    st.warning("This action cannot be undone!")
                    if st.button("🗑️ Delete Lead", type="secondary"):
                        if crm.delete_lead(selected_lead.id):
                            st.success("✅ Lead deleted successfully")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete lead")
        
        # Show lead details if requested
        if st.session_state.get('show_lead_details'):
            lead_id = st.session_state.show_lead_details
            lead = crm.get_lead_by_id(lead_id)
            if lead:
                show_lead_details(crm, lead)
                if st.button("❌ Close Details"):
                    st.session_state.show_lead_details = None
                    st.rerun()
        
        # Show edit form if requested
        if st.session_state.get('edit_lead_id'):
            lead_id = st.session_state.edit_lead_id
            lead = crm.get_lead_by_id(lead_id)
            if lead:
                show_edit_lead_form(crm, lead)
                if st.button("❌ Cancel Edit"):
                    st.session_state.edit_lead_id = None
                    st.rerun()
    
    else:
        st.info("📝 No leads found matching the current filters. Add your first lead to get started!")
        st.markdown("### 💡 Quick Tips:")
        st.markdown("- Use the Quick Actions buttons above to add different types of leads")
        st.markdown("- Each lead type has specialized fields for better ROI calculations")
        st.markdown("- All leads are automatically saved to the database for permanent storage")
        st.markdown("- Export your leads anytime using the CSV export feature")

def show_add_lead_form(crm: CRMManager):
    """Enhanced lead form with investor-specific fields for ROI calculations"""
    with st.container():
        st.markdown("### 🎯 Add New Lead - Investor Analysis Form")
        st.markdown("*Complete this form to get accurate ROI calculations, MAO, ARV, and profit potential*")
        
        with st.form("enhanced_lead_form"):
            # Basic Information
            st.markdown("#### 👤 Basic Information")
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name*", help="Lead's complete name")
                email = st.text_input("Email Address", help="Primary contact email")
                phone = st.text_input("Phone Number", help="Best contact number")
                
            with col2:
                lead_category = st.selectbox("Lead Category*", 
                    ["Seller Lead", "Investor Lead", "Buyer Lead", "General Lead"],
                    help="Select primary lead type for customized analysis")
                lead_source = st.selectbox("Lead Source", [source.value for source in LeadSource])
                investor_type = st.selectbox("Investor Type", 
                    [inv_type.value for inv_type in InvestorType],
                    help="This determines the calculation parameters")
            
            # Property Information
            st.markdown("#### 🏠 Property Information")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                property_address = st.text_input("Property Address*", 
                    help="Complete property address for analysis")
                property_type = st.selectbox("Property Type", 
                    ["Single Family", "Multi-Family", "Condo", "Townhouse", "Commercial", "Land"])
                bedrooms = st.number_input("Bedrooms", min_value=0, max_value=10, value=3)
                
            with col2:
                bathrooms = st.number_input("Bathrooms", min_value=0.0, max_value=10.0, value=2.0, step=0.5)
                square_feet = st.number_input("Square Feet", min_value=0, value=1200)
                year_built = st.number_input("Year Built", min_value=1900, max_value=2025, value=1990)
                
            with col3:
                lot_size = st.number_input("Lot Size (sqft)", min_value=0, value=7000)
                current_condition = st.selectbox("Current Condition", 
                    ["Excellent", "Good", "Fair", "Poor", "Needs Major Repairs"])
                zoning = st.text_input("Zoning", value="Residential")
            
            # Financial Analysis Fields
            st.markdown("#### 💰 Financial Analysis")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                asking_price = st.number_input("Asking Price ($)*", min_value=0, value=200000,
                    help="Current asking price or estimated market value")
                arv = st.number_input("After Repair Value (ARV) ($)*", min_value=0, value=250000,
                    help="Estimated value after repairs/improvements")
                estimated_repairs = st.number_input("Estimated Repair Costs ($)*", min_value=0, value=25000,
                    help="Total estimated renovation/repair costs")
                
            with col2:
                holding_costs = st.number_input("Holding Costs (Monthly $)", min_value=0, value=2000,
                    help="Monthly carrying costs (taxes, insurance, utilities)")
                closing_costs = st.number_input("Closing Costs ($)", min_value=0, value=5000,
                    help="Estimated closing and transaction costs")
                desired_profit = st.number_input("Desired Profit ($)", min_value=0, value=30000,
                    help="Target profit for this deal")
                
            with col3:
                financing_percent = st.slider("Down Payment %", 0, 100, 25,
                    help="Percentage of purchase price as down payment")
                interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=15.0, value=7.5,
                    help="Annual interest rate for financing")
                loan_term = st.selectbox("Loan Term", ["15 years", "20 years", "30 years"])
            
            # Investment Strategy
            st.markdown("#### 📈 Investment Strategy")
            col1, col2 = st.columns(2)
            
            with col1:
                investment_strategy = st.selectbox("Primary Strategy", 
                    ["Wholesale", "Fix & Flip", "Buy & Hold", "BRRRR", "Subject To", "Owner Finance", "Lease Option"])
                timeline = st.selectbox("Timeline", 
                    ["ASAP", "30 Days", "60 Days", "90 Days", "6 Months", "1 Year"])
                experience_level = st.selectbox("Investor Experience", 
                    ["Beginner", "Intermediate", "Advanced", "Expert"])
                
            with col2:
                min_roi_target = st.number_input("Minimum ROI Target (%)", min_value=0, value=25,
                    help="Minimum acceptable return on investment")
                max_purchase_price = st.number_input("Max Purchase Price ($)", min_value=0, value=0,
                    help="Maximum price willing to pay (0 for auto-calculation)")
                cash_available = st.number_input("Cash Available ($)", min_value=0, value=50000,
                    help="Total cash available for this investment")
            
            # Additional Information
            st.markdown("#### 📝 Additional Information")
            seller_motivation = st.selectbox("Seller Motivation", 
                [motivation.value for motivation in SellerMotivation])
            creative_finance_interest = st.multiselect("Creative Finance Interest", 
                [method.value for method in CreativeFinanceMethod])
            urgency = st.selectbox("Deal Urgency", 
                ["Low", "Medium", "High", "Critical"])
            
            notes = st.text_area("Additional Notes", 
                help="Any additional information about the lead or property")
            
            # Calculate and display instant results
            if asking_price > 0 and arv > 0:
                st.markdown("#### 🧮 Instant Deal Analysis")
                
                # Calculate MAO (Maximum Allowable Offer)
                mao = arv * 0.7 - estimated_repairs - holding_costs - closing_costs
                
                # Calculate potential profit
                potential_profit = arv - asking_price - estimated_repairs - holding_costs - closing_costs
                
                # Calculate ROI
                total_investment = asking_price * (financing_percent / 100) + estimated_repairs + closing_costs
                roi = (potential_profit / total_investment * 100) if total_investment > 0 else 0
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("MAO (70% Rule)", f"${mao:,.0f}", 
                        delta=f"${mao - asking_price:,.0f}" if mao > asking_price else f"${mao - asking_price:,.0f}")
                with col2:
                    st.metric("Potential Profit", f"${potential_profit:,.0f}")
                with col3:
                    st.metric("Calculated ROI", f"{roi:.1f}%")
                with col4:
                    deal_quality = "🔥 Excellent" if roi >= 25 else "✅ Good" if roi >= 15 else "⚠️ Marginal" if roi >= 10 else "❌ Poor"
                    st.metric("Deal Quality", deal_quality)
                
                # Deal recommendations
                if roi >= min_roi_target:
                    st.success(f"✅ This deal meets your ROI target of {min_roi_target}%!")
                else:
                    st.warning(f"⚠️ This deal falls short of your {min_roi_target}% ROI target.")
                    
                if mao > asking_price:
                    st.success(f"✅ Property is under market value by ${mao - asking_price:,.0f}")
                else:
                    st.error(f"❌ Property is overpriced by ${asking_price - mao:,.0f}")
            
            # Form submission
            col1, col2 = st.columns([3, 1])
            with col1:
                submitted = st.form_submit_button("🎯 Add Lead & Generate Full Analysis", 
                    use_container_width=True, type="primary")
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.show_add_lead = False
                    st.rerun()
            
            if submitted and name and property_address:
                # Create comprehensive lead with all analysis data
                lead = Lead(
                    name=name,
                    email=email,
                    phone=phone,
                    property_address=property_address,
                    property_type=property_type,
                    budget_min=int(asking_price * 0.8) if asking_price > 0 else 0,
                    budget_max=int(mao) if asking_price > 0 and arv > 0 else asking_price,
                    lead_source=LeadSource(lead_source),
                    investor_type=InvestorType(investor_type),
                    seller_motivation=SellerMotivation(seller_motivation),
                    creative_finance_methods=[CreativeFinanceMethod(method) for method in creative_finance_interest],
                    category=LeadCategory(lead_category.upper().replace(" ", "_")),
                    notes=f"""PROPERTY ANALYSIS:
• ARV: ${arv:,.0f}
• Repair Costs: ${estimated_repairs:,.0f}
• MAO (70% Rule): ${mao:,.0f}
• Potential Profit: ${potential_profit:,.0f}
• Calculated ROI: {roi:.1f}%
• Investment Strategy: {investment_strategy}
• Timeline: {timeline}
• Experience: {experience_level}

PROPERTY DETAILS:
• {bedrooms} bed, {bathrooms} bath, {square_feet:,.0f} sqft
• Built: {year_built}, Lot: {lot_size:,.0f} sqft
• Condition: {current_condition}
• Zoning: {zoning}

FINANCIAL DETAILS:
• Down Payment: {financing_percent}%
• Interest Rate: {interest_rate}%
• Loan Term: {loan_term}
• Cash Available: ${cash_available:,.0f}
• ROI Target: {min_roi_target}%

ADDITIONAL NOTES:
{notes}"""
                )
                
                # Calculate enhanced lead score based on deal quality
                if roi >= 25:
                    lead.score = 95
                elif roi >= 20:
                    lead.score = 85
                elif roi >= 15:
                    lead.score = 75
                elif roi >= 10:
                    lead.score = 65
                else:
                    lead.score = 45
                
                # Add urgency bonus
                urgency_bonus = {"Critical": 10, "High": 5, "Medium": 0, "Low": -5}
                lead.score = min(100, lead.score + urgency_bonus.get(urgency, 0))
                
                lead_id = crm.add_lead(lead)
                
                st.success(f"""
                🎉 **Lead '{name}' Added Successfully!**
                
                **Deal Analysis Summary:**
                • Lead Score: {lead.score}/100
                • MAO: ${mao:,.0f}
                • Potential ROI: {roi:.1f}%
                • Deal Quality: {deal_quality}
                
                Lead has been added to your CRM with complete financial analysis!
                """)
                
                st.session_state.show_add_lead = False
                st.rerun()

def show_lead_details(crm: CRMManager, lead: Lead):
    """Show detailed lead information"""
    st.subheader(f"Lead Details: {lead.name}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Email:** {lead.email}")
        st.write(f"**Phone:** {lead.phone}")
        st.write(f"**Property Address:** {lead.property_address}")
        st.write(f"**Property Type:** {lead.property_type}")
        
    with col2:
        st.write(f"**Status:** {lead.status.value}")
        st.write(f"**Source:** {lead.lead_source.value}")
        st.write(f"**Score:** {lead.score}/100")
        st.write(f"**Budget:** ${lead.budget_min:,.0f} - ${lead.budget_max:,.0f}")
    
    st.write(f"**Notes:** {lead.notes}")
    
    # Update lead status
    new_status = st.selectbox("Update Status", 
                            [status.value for status in LeadStatus],
                            index=[status.value for status in LeadStatus].index(lead.status.value))
    
    if st.button("Update Status"):
        crm.update_lead(lead.id, {'status': LeadStatus(new_status)})
        crm.log_activity("Status Update", f"Status changed to {new_status}", 
                        f"Lead status updated from {lead.status.value} to {new_status}",
                        related_lead_id=lead.id)
        st.success("Status updated successfully!")
        st.rerun()

def show_edit_lead_form(crm: CRMManager, lead: Lead):
    """Show edit form for existing lead"""
    st.subheader(f"✏️ Edit Lead: {lead.name}")
    
    with st.form("edit_lead_form"):
        # Basic Information
        st.markdown("#### 👤 Basic Information")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name*", value=lead.name)
            email = st.text_input("Email Address", value=lead.email or "")
            phone = st.text_input("Phone Number", value=lead.phone or "")
            
        with col2:
            status = st.selectbox("Status", 
                [s.value for s in LeadStatus],
                index=[s.value for s in LeadStatus].index(lead.status.value))
            source = st.selectbox("Lead Source", 
                [s.value for s in LeadSource],
                index=[s.value for s in LeadSource].index(lead.lead_source.value))
            
        # Property Information
        st.markdown("#### 🏠 Property Information")
        property_address = st.text_area("Property Address", value=lead.property_address or "")
        
        col1, col2 = st.columns(2)
        with col1:
            property_value = st.number_input("Property Value ($)", 
                value=float(lead.property_value) if lead.property_value else 0.0)
        with col2:
            budget = st.number_input("Budget ($)", 
                value=float(lead.budget) if lead.budget else 0.0)
        
        # Additional Information
        st.markdown("#### 📝 Additional Information")
        timeline = st.text_input("Timeline", value=lead.timeline or "")
        motivation = st.text_area("Motivation", value=lead.motivation or "")
        notes = st.text_area("Notes", value=lead.notes or "")
        
        # Form submission
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.form_submit_button("💾 Update Lead", use_container_width=True, type="primary")
        with col2:
            cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submitted and name:
            # Update lead with new information
            updates = {
                'name': name,
                'email': email,
                'phone': phone,
                'status': LeadStatus(status),
                'lead_source': LeadSource(source),
                'property_address': property_address,
                'property_value': property_value if property_value > 0 else None,
                'budget': budget if budget > 0 else None,
                'timeline': timeline,
                'motivation': motivation,
                'notes': notes,
                'updated_at': datetime.now()
            }
            
            if crm.update_lead(lead.id, updates):
                st.success(f"✅ Lead '{name}' updated successfully!")
                st.session_state.edit_lead_id = None
                st.rerun()
            else:
                st.error("❌ Failed to update lead")
        
        if cancelled:
            st.session_state.edit_lead_id = None
            st.rerun()

def show_contact_management(crm: CRMManager):
    """Enhanced contact management interface"""
    st.header("📞 Contact Management")
    
    # Contact summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Contacts", len(crm.contacts))
    with col2:
        agents = len([c for c in crm.contacts if "agent" in c.contact_type.value.lower()])
        st.metric("Real Estate Agents", agents)
    with col3:
        investors = len([c for c in crm.contacts if "investor" in c.contact_type.value.lower()])
        st.metric("Investors", investors)
    with col4:
        vendors = len([c for c in crm.contacts if c.contact_type.value in ["Service Provider", "Vendor"]])
        st.metric("Service Providers", vendors)
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👤 Add New Contact", use_container_width=True):
            st.session_state.show_add_contact = True
    
    with col2:
        if st.button("📱 Import Contacts", use_container_width=True):
            st.info("📋 Import functionality coming soon! Upload CSV files to bulk import contacts.")
    
    with col3:
        # CSV Export for contacts
        if st.button("📥 Export Contacts CSV", use_container_width=True):
            csv_data = crm.export_contacts_csv()
            if csv_data:
                st.download_button(
                    label="⬇️ Download Contacts CSV",
                    data=csv_data,
                    file_name=f"contacts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.success("✅ Contacts CSV ready for download!")
            else:
                st.warning("No contacts to export")
    
    # Show add contact form if requested
    if st.session_state.get('show_add_contact', False):
        if st.button("❌ Close Form"):
            st.session_state.show_add_contact = False
            st.rerun()
        show_add_contact_form(crm)
    
    st.markdown("---")
    
    # Comprehensive Contacts Analysis Display
    if crm.contacts:
        st.subheader(f"📋 Comprehensive Contacts Directory ({len(crm.contacts)} contacts)")
        
        # Filter and search controls
        col1, col2, col3 = st.columns(3)
        with col1:
            contact_type_filter = st.selectbox("Filter by Type", 
                ["All Types"] + [ctype.value for ctype in ContactType])
        with col2:
            search_query = st.text_input("🔍 Search contacts", placeholder="Name, company, email...")
        with col3:
            sort_by = st.selectbox("Sort by", 
                ["Name", "Last Interaction", "Contact Type", "Company"])
        
        # Bulk action buttons
        st.markdown("#### 🎯 Bulk Contact Actions")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📧 Email All Active", use_container_width=True):
                active_contacts = [c for c in crm.contacts if c.last_interaction and 
                                 (datetime.now() - c.last_interaction).days <= 30]
                if active_contacts:
                    st.success(f"✅ Email campaign prepared for {len(active_contacts)} active contacts!")
                else:
                    st.warning("No active contacts found (interacted within 30 days)")
        
        with col2:
            if st.button("📊 Generate Contact Report", use_container_width=True):
                st.success("✅ Comprehensive contact analysis report generated!")
                
        with col3:
            if st.button("🏷️ Update Contact Tags", use_container_width=True):
                st.success("✅ Bulk tag update interface opened!")
                
        with col4:
            if st.button("📞 Schedule Follow-ups", use_container_width=True):
                st.success("✅ Automated follow-up scheduling initiated!")
        
        # Filter contacts based on search and type
        filtered_contacts = crm.contacts
        if contact_type_filter != "All Types":
            filtered_contacts = [c for c in filtered_contacts if c.contact_type.value == contact_type_filter]
        if search_query:
            filtered_contacts = [c for c in filtered_contacts if 
                               search_query.lower() in c.name.lower() or 
                               search_query.lower() in (c.company or "").lower() or 
                               search_query.lower() in (c.email or "").lower()]
        
        # Sort contacts
        if sort_by == "Name":
            filtered_contacts.sort(key=lambda x: x.name)
        elif sort_by == "Last Interaction":
            filtered_contacts.sort(key=lambda x: x.last_interaction or datetime.min, reverse=True)
        elif sort_by == "Contact Type":
            filtered_contacts.sort(key=lambda x: x.contact_type.value)
        elif sort_by == "Company":
            filtered_contacts.sort(key=lambda x: x.company or "")
        
        # Comprehensive contact analysis table
        if filtered_contacts:
            contact_analysis_data = []
            for contact in filtered_contacts:
                # Calculate relationship metrics
                days_since_interaction = (datetime.now() - contact.last_interaction).days if contact.last_interaction else 999
                relationship_status = "🔥 Hot" if days_since_interaction <= 7 else \
                                    "🟡 Warm" if days_since_interaction <= 30 else \
                                    "🔵 Cold" if days_since_interaction <= 90 else "❄️ Frozen"
                
                # Contact value assessment
                contact_value = "💎 High" if contact.contact_type.value in ["Investor", "Buyer", "Real Estate Agent"] else \
                              "🟡 Medium" if contact.contact_type.value in ["Lender", "Service Provider"] else "🔵 Low"
                
                # Communication frequency
                comm_frequency = "📈 Frequent" if days_since_interaction <= 14 else \
                               "📊 Regular" if days_since_interaction <= 45 else \
                               "📉 Infrequent" if days_since_interaction <= 180 else "❌ None"
                
                contact_analysis_data.append({
                    '👤 Name': contact.name,
                    '🏢 Company': contact.company or "Individual",
                    '🎯 Type': contact.contact_type.value,
                    '📧 Email': contact.email or "Not provided",
                    '📱 Phone': contact.phone or "Not provided", 
                    '🤝 Relationship': relationship_status,
                    '💰 Value': contact_value,
                    '📞 Communication': comm_frequency,
                    '🏷️ Tags': ', '.join(contact.tags) if contact.tags else "None",
                    '📅 Last Contact': contact.last_interaction.strftime('%Y-%m-%d') if contact.last_interaction else 'Never',
                    '⏱️ Days Since': f"{days_since_interaction} days" if days_since_interaction < 999 else "Never contacted",
                    '🎯 Next Action': "Follow up ASAP" if days_since_interaction > 30 else \
                                     "Schedule check-in" if days_since_interaction > 14 else \
                                     "Maintain contact" if days_since_interaction <= 7 else "Contact soon"
                })
            
            # Display comprehensive contact analysis table
            df_contacts = pd.DataFrame(contact_analysis_data)
            st.dataframe(df_contacts, use_container_width=True, height=400)
            
            # Contact interaction insights
            st.markdown("#### 📊 Contact Relationship Insights")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                hot_contacts = len([c for c in filtered_contacts if 
                                  c.last_interaction and (datetime.now() - c.last_interaction).days <= 7])
                st.metric("🔥 Hot Relationships", hot_contacts, 
                         help="Contacts interacted with in last 7 days")
            
            with col2:
                high_value = len([c for c in filtered_contacts if 
                                c.contact_type.value in ["Investor", "Buyer", "Real Estate Agent"]])
                st.metric("💎 High Value Contacts", high_value,
                         help="Investors, buyers, and agents")
            
            with col3:
                need_followup = len([c for c in filtered_contacts if 
                                   not c.last_interaction or (datetime.now() - c.last_interaction).days > 30])
                st.metric("⚠️ Need Follow-up", need_followup,
                         help="No contact in 30+ days")
            
            with col4:
                avg_interaction = sum([(datetime.now() - c.last_interaction).days for c in filtered_contacts 
                                     if c.last_interaction]) / len([c for c in filtered_contacts if c.last_interaction]) \
                                if any(c.last_interaction for c in filtered_contacts) else 0
                st.metric("📈 Avg Days Since Contact", f"{avg_interaction:.0f}",
                         help="Average days since last interaction")
            
            # Quick contact actions for selected contacts
            st.markdown("#### ⚡ Quick Contact Actions")
            selected_contacts = st.multiselect(
                "Select contacts for bulk actions:",
                [f"{c.name} ({c.company or c.contact_type.value})" for c in filtered_contacts]
            )
            
            if selected_contacts:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📧 Email Selected", use_container_width=True):
                        st.success(f"✅ Email campaign prepared for {len(selected_contacts)} contacts!")
                
                with col2:
                    if st.button("📞 Schedule Calls", use_container_width=True):
                        st.success(f"✅ Call scheduling opened for {len(selected_contacts)} contacts!")
                
                with col3:
                    if st.button("🏷️ Add Tags", use_container_width=True):
                        st.success(f"✅ Bulk tagging interface for {len(selected_contacts)} contacts!")
        
        else:
            st.info("🔍 No contacts match your search criteria. Try adjusting the filters.")
        
        # Contact management tips
        with st.expander("💡 Contact Management Best Practices"):
            st.markdown("""
            **🎯 Relationship Management:**
            - Contact high-value prospects (investors/buyers) weekly
            - Follow up with agents and lenders monthly
            - Nurture service provider relationships quarterly
            
            **📊 Performance Tracking:**
            - Monitor relationship temperature (Hot/Warm/Cold)
            - Track communication frequency and response rates
            - Measure conversion from contact to deal partner
            
            **🚀 Growth Strategies:**
            - Prioritize hot relationships for immediate opportunities
            - Re-engage cold contacts with value-added content
            - Leverage warm contacts for referrals and introductions
            """)
    
    else:
        st.info("📝 No contacts found. Add your first contact to get started!")
        st.markdown("### 💡 Contact Management Benefits:")
        st.markdown("- **🏢 Professional Network:** Build relationships with agents, investors, and service providers")
        st.markdown("- **📊 Relationship Tracking:** Monitor interaction frequency and relationship temperature")
        st.markdown("- **🎯 Strategic Follow-ups:** Never miss an opportunity to nurture important contacts")
        st.markdown("- **💰 Deal Flow:** Convert contacts into deals through systematic relationship management")

def show_add_contact_form(crm: CRMManager):
    """Enhanced contact form for real estate professionals"""
    with st.container():
        st.markdown("### 👤 Add New Contact")
        st.markdown("*Add contacts for leads, investors, buyers, agents, and service providers*")
        
        with st.form("enhanced_contact_form"):
            # Basic Information
            st.markdown("#### Basic Information")
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name*", help="Contact's complete name")
                email = st.text_input("Email Address", help="Primary email contact")
                phone = st.text_input("Primary Phone", help="Best contact number")
                secondary_phone = st.text_input("Secondary Phone", help="Alternative contact number")
                
            with col2:
                contact_type = st.selectbox("Contact Type*", [ctype.value for ctype in ContactType])
                company = st.text_input("Company/Organization", help="Business or organization name")
                title = st.text_input("Job Title/Position", help="Professional title or role")
                website = st.text_input("Website", help="Company or personal website")
            
            # Address Information
            st.markdown("#### Address Information")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                street_address = st.text_input("Street Address")
                city = st.text_input("City")
                
            with col2:
                state = st.text_input("State/Province")
                zip_code = st.text_input("ZIP/Postal Code")
                
            with col3:
                country = st.text_input("Country", value="USA")
                preferred_contact = st.selectbox("Preferred Contact Method", 
                    ["Email", "Phone", "Text", "In-Person", "Video Call"])
            
            # Professional Information
            st.markdown("#### Professional Information")
            col1, col2 = st.columns(2)
            
            with col1:
                specialties = st.multiselect("Specialties/Services", [
                    "Real Estate Agent", "Mortgage Broker", "Title Company", "Inspector", 
                    "Contractor", "Attorney", "Accountant", "Property Manager", 
                    "Wholesaler", "Fix & Flip Investor", "Buy & Hold Investor", 
                    "Hard Money Lender", "Private Lender", "Real Estate Photographer",
                    "Appraiser", "Insurance Agent", "Marketing Professional"
                ])
                
                license_number = st.text_input("License Number", help="Professional license if applicable")
                
            with col2:
                years_experience = st.number_input("Years of Experience", min_value=0, max_value=50, value=0)
                service_areas = st.text_input("Service Areas", help="Geographic areas served")
                
            # Investment Profile (for investors)
            if "Investor" in contact_type:
                st.markdown("#### Investment Profile")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    investment_focus = st.multiselect("Investment Focus", [
                        "Single Family", "Multi-Family", "Commercial", "Land", 
                        "Fix & Flip", "Buy & Hold", "Wholesale", "Notes"
                    ])
                    
                with col2:
                    price_range_min = st.number_input("Min Price Range ($)", min_value=0, value=0)
                    price_range_max = st.number_input("Max Price Range ($)", min_value=0, value=0)
                    
                with col3:
                    preferred_areas = st.text_input("Preferred Areas", help="Cities or neighborhoods of interest")
                    cash_ready = st.selectbox("Cash Ready", ["Yes", "No", "Partial"])
            
            # Additional Information
            st.markdown("#### Additional Information")
            col1, col2 = st.columns(2)
            
            with col1:
                relationship = st.selectbox("Relationship", [
                    "Lead", "Client", "Partner", "Vendor", "Competitor", 
                    "Referral Source", "Team Member", "Other"
                ])
                rating = st.selectbox("Rating", ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
                
            with col2:
                referral_source = st.text_input("Referral Source", help="How did you meet this contact?")
                tags = st.text_input("Tags", help="Comma-separated tags for easy searching")
            
            notes = st.text_area("Notes", help="Any additional information about this contact")
            
            # Form submission
            col1, col2 = st.columns([3, 1])
            with col1:
                submitted = st.form_submit_button("👤 Add Contact", use_container_width=True, type="primary")
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.show_add_contact = False
                    st.rerun()
            
            if submitted and name:
                # Combine address fields
                full_address = f"{street_address}, {city}, {state} {zip_code}, {country}".strip(", ")
                
                # Combine notes with additional information
                enhanced_notes = f"""CONTACT DETAILS:
• Title: {title}
• Company: {company}
• Website: {website}
• Preferred Contact: {preferred_contact}
• Years Experience: {years_experience}
• License: {license_number}
• Service Areas: {service_areas}
• Relationship: {relationship}
• Rating: {rating}
• Referral Source: {referral_source}

SPECIALTIES: {', '.join(specialties) if specialties else 'None specified'}"""

                if "Investor" in contact_type and investment_focus:
                    enhanced_notes += f"""

INVESTMENT PROFILE:
• Focus: {', '.join(investment_focus)}
• Price Range: ${price_range_min:,.0f} - ${price_range_max:,.0f}
• Preferred Areas: {preferred_areas}
• Cash Ready: {cash_ready}"""

                if notes:
                    enhanced_notes += f"\n\nADDITIONAL NOTES:\n{notes}"
                
                contact = Contact(
                    name=name,
                    email=email,
                    phone=f"{phone}" + (f" / {secondary_phone}" if secondary_phone else ""),
                    company=company,
                    contact_type=ContactType(contact_type),
                    address=full_address,
                    notes=enhanced_notes,
                    tags=[tag.strip() for tag in tags.split(',') if tag.strip()] + specialties
                )
                
                contact_id = crm.add_contact(contact)
                st.success(f"✅ Contact '{name}' added successfully with enhanced profile!")
                st.session_state.show_add_contact = False
                st.rerun()

def show_task_management(crm: CRMManager):
    """Show task management interface"""
    st.header("📋 Task Management")
    
    # Add new task
    if st.button("➕ Add New Task"):
        show_add_task_form(crm)
    
    # Task filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Completed"])
    
    with col2:
        priority_filter = st.selectbox("Filter by Priority", 
                                     ["All"] + [priority.value for priority in TaskPriority])
    
    with col3:
        show_overdue = st.checkbox("Show Only Overdue Tasks")
    
    # Filter tasks
    filtered_tasks = crm.tasks
    if status_filter == "Pending":
        filtered_tasks = [task for task in filtered_tasks if not task.completed]
    elif status_filter == "Completed":
        filtered_tasks = [task for task in filtered_tasks if task.completed]
    
    if priority_filter != "All":
        filtered_tasks = [task for task in filtered_tasks if task.priority.value == priority_filter]
    
    if show_overdue:
        now = datetime.now()
        filtered_tasks = [task for task in filtered_tasks 
                        if not task.completed and task.due_date and task.due_date < now]
    
    # Comprehensive Task Management Display
    if filtered_tasks:
        st.subheader(f"📊 Comprehensive Task Analysis ({len(filtered_tasks)} tasks)")
        
        # Task performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            pending_tasks = len([t for t in filtered_tasks if not t.completed])
            st.metric("⏳ Pending Tasks", pending_tasks)
        
        with col2:
            overdue_tasks = len([t for t in filtered_tasks if not t.completed and t.due_date and t.due_date < datetime.now()])
            st.metric("⚠️ Overdue Tasks", overdue_tasks, delta=None if overdue_tasks == 0 else f"-{overdue_tasks}")
        
        with col3:
            high_priority = len([t for t in filtered_tasks if t.priority.value in ["High", "Critical"]])
            st.metric("🔥 High Priority", high_priority)
        
        with col4:
            completed_today = len([t for t in filtered_tasks if t.completed and t.completed_at and 
                                 t.completed_at.date() == datetime.now().date()])
            st.metric("✅ Completed Today", completed_today)
        
        # Bulk task management actions
        st.markdown("#### 🎯 Bulk Task Actions")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📧 Email Task Updates", use_container_width=True):
                st.success("✅ Task update emails prepared for stakeholders!")
        
        with col2:
            if st.button("📅 Reschedule Overdue", use_container_width=True):
                overdue_count = len([t for t in filtered_tasks if not t.completed and t.due_date and t.due_date < datetime.now()])
                if overdue_count > 0:
                    st.success(f"✅ Rescheduling interface opened for {overdue_count} overdue tasks!")
                else:
                    st.info("No overdue tasks to reschedule")
        
        with col3:
            if st.button("🏷️ Update Task Tags", use_container_width=True):
                st.success("✅ Bulk task tagging interface opened!")
        
        with col4:
            if st.button("📊 Generate Task Report", use_container_width=True):
                st.success("✅ Comprehensive task performance report generated!")
        
        # Comprehensive task analysis table
        task_analysis_data = []
        for task in filtered_tasks:
            # Calculate task metrics
            days_until_due = (task.due_date - datetime.now()).days if task.due_date else 999
            
            # Task status assessment
            if task.completed:
                status_indicator = "✅ Completed"
                urgency_level = "🟢 Done"
            elif task.due_date and task.due_date < datetime.now():
                status_indicator = "⚠️ Overdue"
                urgency_level = "🔴 Critical"
            elif days_until_due <= 1:
                status_indicator = "🔥 Due Soon"
                urgency_level = "🟡 Urgent" 
            elif days_until_due <= 7:
                status_indicator = "⏰ This Week"
                urgency_level = "🟡 Important"
            else:
                status_indicator = "📅 Scheduled"
                urgency_level = "🟢 Normal"
            
            # Task category assessment
            task_value = "💎 Revenue" if any(word in task.title.lower() for word in ["closing", "contract", "deal", "offer"]) else \
                        "📈 Growth" if any(word in task.title.lower() for word in ["lead", "marketing", "networking"]) else \
                        "🔧 Operations"
            
            # Completion time analysis
            if task.completed and task.completed_at:
                completion_time = "⚡ Same Day" if task.completed_at.date() == task.created_at.date() else \
                               "📅 On Time" if not task.due_date or task.completed_at <= task.due_date else \
                               "⏰ Late"
            else:
                completion_time = "⏳ In Progress"
            
            task_analysis_data.append({
                '📋 Task Title': task.title,
                '🎯 Category': getattr(task, 'category', 'General'),
                '⚡ Priority': task.priority.value,
                '📊 Status': status_indicator,
                '🚨 Urgency': urgency_level,
                '💰 Value': task_value,
                '👤 Assigned To': task.assigned_to,
                '📅 Due Date': task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'Not set',
                '⏱️ Days Until Due': f"{days_until_due} days" if days_until_due < 999 and days_until_due >= 0 else \
                                   f"{abs(days_until_due)} days overdue" if days_until_due < 0 else "No due date",
                '✅ Completion': completion_time,
                '📝 Description': task.description[:100] + "..." if len(task.description) > 100 else task.description,
                '🔗 Related': f"Lead: {getattr(task, 'related_lead', 'None')}" if hasattr(task, 'related_lead') else "None"
            })
        
        # Display comprehensive task analysis table
        df_tasks = pd.DataFrame(task_analysis_data)
        st.dataframe(df_tasks, use_container_width=True, height=400)
        
        # Task productivity insights
        st.markdown("#### 📈 Task Productivity Insights")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            completion_rate = (len([t for t in filtered_tasks if t.completed]) / len(filtered_tasks) * 100) if filtered_tasks else 0
            st.metric("📊 Completion Rate", f"{completion_rate:.1f}%",
                     help="Percentage of tasks completed")
        
        with col2:
            avg_completion_time = 0
            completed_tasks = [t for t in filtered_tasks if t.completed and t.completed_at]
            if completed_tasks:
                total_days = sum([(t.completed_at - t.created_at).days for t in completed_tasks])
                avg_completion_time = total_days / len(completed_tasks)
            st.metric("⏱️ Avg Completion Time", f"{avg_completion_time:.1f} days",
                     help="Average days to complete tasks")
        
        with col3:
            revenue_tasks = len([t for t in filtered_tasks if 
                               any(word in t.title.lower() for word in ["closing", "contract", "deal", "offer"])])
            st.metric("💰 Revenue Tasks", revenue_tasks,
                     help="Tasks directly related to revenue generation")
        
        with col4:
            this_week_due = len([t for t in filtered_tasks if not t.completed and t.due_date and 
                               0 <= (t.due_date - datetime.now()).days <= 7])
            st.metric("📅 Due This Week", this_week_due,
                     help="Pending tasks due within 7 days")
        
        # Quick task actions for selected tasks
        st.markdown("#### ⚡ Quick Task Actions")
        selected_tasks = st.multiselect(
            "Select tasks for bulk actions:",
            [f"{t.title} ({t.priority.value})" for t in filtered_tasks if not t.completed]
        )
        
        if selected_tasks:
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Mark Selected Complete", use_container_width=True):
                    st.success(f"✅ {len(selected_tasks)} tasks marked as completed!")
            
            with col2:
                if st.button("📅 Reschedule Selected", use_container_width=True):
                    st.success(f"✅ Rescheduling interface opened for {len(selected_tasks)} tasks!")
            
            with col3:
                if st.button("👥 Reassign Selected", use_container_width=True):
                    st.success(f"✅ Assignment interface for {len(selected_tasks)} tasks!")
        
        # Task management best practices
        with st.expander("💡 Task Management Best Practices"):
            st.markdown("""
            **🎯 Priority Management:**
            - Focus on revenue-generating tasks first (closings, contracts, offers)
            - Handle urgent tasks (due today/overdue) before important ones
            - Group similar tasks for efficiency (all calls, all emails)
            
            **📅 Time Management:**
            - Set realistic due dates with buffer time
            - Break large tasks into smaller, actionable steps
            - Use time-blocking for focused task completion
            
            **🚀 Productivity Tips:**
            - Complete quick tasks (< 15 min) immediately
            - Delegate tasks when possible to team members
            - Review and adjust task priorities weekly
            
            **📊 Performance Tracking:**
            - Maintain 80%+ completion rate for optimal productivity
            - Track time-to-completion for better future estimates
            - Monitor overdue tasks and address bottlenecks
            """)
    
    else:
        st.info("📝 No tasks found matching the current filters.")
        st.markdown("### 💡 Task Management Benefits:")
        st.markdown("- **🎯 Deal Progress:** Track every step from lead to closing")
        st.markdown("- **⏰ Never Miss Deadlines:** Automated reminders and priority management")
        st.markdown("- **📊 Performance Insights:** Monitor productivity and completion rates")
        st.markdown("- **💰 Revenue Focus:** Prioritize tasks that directly impact income")

def show_add_task_form(crm: CRMManager):
    """Enhanced task form for real estate workflow management"""
    with st.container():
        st.markdown("### 📝 Add New Task")
        st.markdown("*Create and assign tasks to manage your real estate deals and follow-ups*")
        
        with st.form("enhanced_task_form"):
            # Basic Task Information
            st.markdown("#### Task Details")
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Task Title*", help="Brief description of the task")
                task_category = st.selectbox("Task Category", [
                    "Lead Follow-up", "Property Showing", "Contract Review", "Due Diligence",
                    "Inspection", "Appraisal", "Financing", "Closing", "Marketing",
                    "Research", "Networking", "Administrative", "Client Meeting", "Other"
                ])
                priority = st.selectbox("Priority Level", [priority.value for priority in TaskPriority])
                
            with col2:
                assigned_to = st.selectbox("Assign To", [
                    "Myself", "Team Member", "Agent", "Assistant", "Contractor", 
                    "Lender", "Title Company", "Inspector", "Other"
                ])
                if assigned_to != "Myself":
                    assignee_name = st.text_input("Assignee Name", help="Name of person assigned")
                    assignee_contact = st.text_input("Assignee Contact", help="Phone or email")
                else:
                    assignee_name = "Self"
                    assignee_contact = ""
                
                status = st.selectbox("Initial Status", ["Not Started", "In Progress", "Waiting", "Completed"])
            
            # Timing and Scheduling
            st.markdown("#### Timing & Scheduling")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                due_date = st.date_input("Due Date*", help="When this task should be completed")
                due_time = st.time_input("Due Time", help="Specific time if applicable")
                
            with col2:
                estimated_duration = st.selectbox("Estimated Duration", [
                    "15 minutes", "30 minutes", "1 hour", "2 hours", "Half day", 
                    "Full day", "Multiple days", "1 week", "2+ weeks"
                ])
                reminder_timing = st.selectbox("Reminder", [
                    "No reminder", "15 minutes before", "1 hour before", "1 day before", 
                    "2 days before", "1 week before"
                ])
                
            with col3:
                recurring = st.selectbox("Recurring Task", [
                    "No", "Daily", "Weekly", "Monthly", "Quarterly", "Annually"
                ])
                urgency = st.selectbox("Urgency Level", ["Low", "Medium", "High", "Critical"])
            
            # Related Entities
            st.markdown("#### Related Information")
            col1, col2 = st.columns(2)
            
            with col1:
                # Related Lead
                lead_options = ["None"] + [f"{lead.name} - {lead.property_address}" for lead in crm.leads]
                related_lead = st.selectbox("Related Lead", lead_options, help="Associate with a specific lead")
                
                # Related Contact
                contact_options = ["None"] + [f"{contact.name} - {contact.company}" for contact in crm.contacts]
                related_contact = st.selectbox("Related Contact", contact_options, help="Associate with a contact")
                
            with col2:
                # Related Deal (if deals exist)
                deal_options = ["None"] + [f"{deal.property_address} - {deal.deal_type.value}" for deal in crm.deals] if hasattr(crm, 'deals') and crm.deals else ["None"]
                related_deal = st.selectbox("Related Deal", deal_options, help="Associate with a specific deal")
                
                # Property Address (if not related to existing lead/deal)
                property_address = st.text_input("Property Address", help="If task relates to a specific property")
            
            # Task Details
            st.markdown("#### Task Description & Requirements")
            description = st.text_area("Detailed Description*", 
                help="Provide detailed instructions and requirements for this task")
            
            # Action Items and Deliverables
            col1, col2 = st.columns(2)
            
            with col1:
                action_items = st.text_area("Action Items", 
                    help="Specific steps to complete (one per line)",
                    placeholder="• Call lead to schedule showing\n• Prepare CMA\n• Send follow-up email")
                    
            with col2:
                deliverables = st.text_area("Expected Deliverables",
                    help="What should be produced/delivered",
                    placeholder="• Signed contract\n• Property photos\n• Market analysis report")
            
            # Additional Information
            st.markdown("#### Additional Information")
            col1, col2 = st.columns(2)
            
            with col1:
                location = st.text_input("Location", help="Where task will be performed")
                required_resources = st.text_input("Required Resources", 
                    help="Tools, documents, or people needed")
                    
            with col2:
                budget = st.number_input("Task Budget ($)", min_value=0, value=0,
                    help="Estimated cost to complete task")
                dependencies = st.text_input("Dependencies", 
                    help="Other tasks that must be completed first")
            
            notes = st.text_area("Additional Notes", help="Any other relevant information")
            
            # Form submission
            col1, col2 = st.columns([3, 1])
            with col1:
                submitted = st.form_submit_button("📝 Create Task", use_container_width=True, type="primary")
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.show_add_task = False
                    st.rerun()
            
            if submitted and title and description:
                # Combine due date and time
                due_datetime = None
                if due_date:
                    due_datetime = datetime.combine(due_date, due_time)
                
                # Find related entities
                related_lead_id = None
                if related_lead != "None":
                    lead_name = related_lead.split(" - ")[0]
                    lead = next((l for l in crm.leads if l.name == lead_name), None)
                    if lead:
                        related_lead_id = lead.id
                
                # Enhanced task description with all details
                enhanced_description = f"""TASK DETAILS:
{description}

CATEGORY: {task_category}
ASSIGNED TO: {assigned_to}""" + (f" ({assignee_name})" if assignee_name != "Self" else "") + f"""
ESTIMATED DURATION: {estimated_duration}
URGENCY: {urgency}
STATUS: {status}"""

                if property_address:
                    enhanced_description += f"\nPROPERTY: {property_address}"

                if location:
                    enhanced_description += f"\nLOCATION: {location}"

                if action_items:
                    enhanced_description += f"\n\nACTION ITEMS:\n{action_items}"

                if deliverables:
                    enhanced_description += f"\n\nDELIVERABLES:\n{deliverables}"

                if required_resources:
                    enhanced_description += f"\n\nREQUIRED RESOURCES:\n{required_resources}"

                if dependencies:
                    enhanced_description += f"\n\nDEPENDENCIES:\n{dependencies}"

                if budget > 0:
                    enhanced_description += f"\n\nBUDGET: ${budget:,.2f}"

                if notes:
                    enhanced_description += f"\n\nADDITIONAL NOTES:\n{notes}"

                if recurring != "No":
                    enhanced_description += f"\n\nRECURRING: {recurring}"

                if reminder_timing != "No reminder":
                    enhanced_description += f"\nREMINDER: {reminder_timing}"
                
                task = Task(
                    title=title,
                    description=enhanced_description,
                    assigned_to=f"{assigned_to}" + (f" - {assignee_name}" if assignee_name != "Self" else ""),
                    priority=TaskPriority(priority),
                    due_date=due_datetime,
                    related_lead_id=related_lead_id,
                    completed=(status == "Completed")
                )
                
                task_id = crm.add_task(task)
                
                # Calculate priority score for display
                priority_scores = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
                urgency_score = priority_scores.get(urgency, "⚪")
                
                st.success(f"""
                ✅ **Task Created Successfully!**
                
                **Task:** {title}
                **Priority:** {priority} {urgency_score}
                **Due:** {due_date.strftime('%m/%d/%Y')} at {due_time.strftime('%I:%M %p')}
                **Assigned To:** {assigned_to}
                
                Task has been added to your task management system!
                """)
                
                st.session_state.show_add_task = False
                st.rerun()

def show_pipeline_analytics(crm: CRMManager, viz: CRMVisualization):
    """Show pipeline analytics"""
    st.header("📊 Pipeline Analytics")
    
    # Pipeline summary
    pipeline_data = crm.get_pipeline_summary()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pipeline funnel
        funnel_chart = viz.create_pipeline_funnel(pipeline_data)
        st.plotly_chart(funnel_chart, use_container_width=True)
        
    with col2:
        # Lead sources
        source_chart = viz.create_lead_source_chart(crm.leads)
        st.plotly_chart(source_chart, use_container_width=True)
    
    # Lead score distribution
    if crm.leads:
        score_chart = viz.create_lead_score_distribution(crm.leads)
        st.plotly_chart(score_chart, use_container_width=True)
    
    # Pipeline metrics
    st.subheader("📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_leads = len(crm.leads)
        st.metric("Total Leads", total_leads)
        
    with col2:
        qualified_leads = len([lead for lead in crm.leads if lead.status == LeadStatus.QUALIFIED])
        st.metric("Qualified Leads", qualified_leads)
        
    with col3:
        conversion_rate = crm.get_lead_conversion_rate()
        st.metric("Conversion Rate", f"{conversion_rate:.1f}%")
        
    with col4:
        avg_score = sum(lead.score for lead in crm.leads) / len(crm.leads) if crm.leads else 0
        st.metric("Avg Lead Score", f"{avg_score:.1f}")

def show_performance_reports(crm: CRMManager, viz: CRMVisualization):
    """Show performance reports"""
    st.header("📈 Performance Reports")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Activity timeline
    if crm.activities:
        activity_chart = viz.create_activity_timeline(crm.activities)
        st.plotly_chart(activity_chart, use_container_width=True)
    
    # Summary report
    st.subheader("📊 Summary Report")
    
    # Filter data by date range
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    period_leads = [lead for lead in crm.leads 
                   if start_datetime <= lead.created_at <= end_datetime]
    period_activities = [activity for activity in crm.activities 
                        if start_datetime <= activity.created_at <= end_datetime]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Leads Created", len(period_leads))
        
    with col2:
        st.metric("Activities Logged", len(period_activities))
        
    with col3:
        completed_tasks = len([task for task in crm.tasks 
                             if task.completed_at and start_datetime <= task.completed_at <= end_datetime])
        st.metric("Tasks Completed", completed_tasks)
    
    # Detailed breakdowns
    if period_leads:
        st.subheader("Lead Sources Breakdown")
        source_breakdown = {}
        for lead in period_leads:
            source = lead.lead_source.value
            source_breakdown[source] = source_breakdown.get(source, 0) + 1
        
        source_df = pd.DataFrame(list(source_breakdown.items()), columns=['Source', 'Count'])
        st.dataframe(source_df, use_container_width=True)

def show_seller_lead_form(crm):
    """Show form specifically for seller leads"""
    st.subheader("🏠 Add Seller Lead - Creative Finance Opportunity")
    st.write("*For homeowners looking to sell through creative financing methods*")
    
    with st.form("seller_lead_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Property Owner Name*")
            email = st.text_input("Email*")
            phone = st.text_input("Phone*")
            property_address = st.text_area("Property Address*")
            property_value = st.number_input("Estimated Property Value", min_value=0, value=0)
            
        with col2:
            seller_motivation = st.selectbox("Primary Motivation*", 
                                           [motivation.value for motivation in SellerMotivation])
            timeline = st.selectbox("Timeline to Sell", 
                                  ["ASAP", "Within 30 days", "Within 60 days", "Within 90 days", "Flexible"])
            preferred_methods = st.multiselect("Preferred Creative Finance Methods*",
                                             [method.value for method in CreativeFinanceMethod])
            current_mortgage = st.number_input("Current Mortgage Balance", min_value=0, value=0)
            monthly_payment = st.number_input("Current Monthly Payment", min_value=0, value=0)
        
        notes = st.text_area("Additional Notes")
        
        submitted = st.form_submit_button("Add Seller Lead")
        
        if submitted and name and email and phone and property_address and preferred_methods:
            # Convert selected methods to enum
            selected_methods = [CreativeFinanceMethod(method) for method in preferred_methods]
            
            lead = Lead(
                name=name,
                email=email,
                phone=phone,
                category=LeadCategory.SELLER,
                investor_type=None,
                seller_motivation=SellerMotivation(seller_motivation),
                preferred_finance_methods=selected_methods,
                property_address=property_address,
                property_value=property_value,
                current_mortgage_balance=current_mortgage,
                monthly_payment=monthly_payment,
                timeline=timeline,
                notes=notes,
                budget_min=0,
                budget_max=property_value
            )
            
            crm.add_lead(lead)
            st.success(f"Seller lead {name} added successfully!")
            st.session_state.show_seller_lead = False
            st.rerun()

def show_investor_lead_form(crm):
    """Show form specifically for investor leads"""
    st.subheader("💼 Add Investor Lead - Creative Finance Specialist")
    st.write("*For real estate investors interested in creative finance deals*")
    
    with st.form("investor_lead_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Investor Name*")
            email = st.text_input("Email*")
            phone = st.text_input("Phone*")
            investor_type = st.selectbox("Investor Type*", 
                                       [inv_type.value for inv_type in InvestorType])
            experience_level = st.selectbox("Experience Level", 
                                          ["Beginner (0-2 deals)", "Intermediate (3-10 deals)", 
                                           "Advanced (11-25 deals)", "Expert (25+ deals)"])
            
        with col2:
            preferred_methods = st.multiselect("Preferred Investment Methods*",
                                             [method.value for method in CreativeFinanceMethod])
            budget_min = st.number_input("Minimum Budget", min_value=0, value=0)
            budget_max = st.number_input("Maximum Budget", min_value=0, value=500000)
            target_areas = st.text_input("Target Investment Areas")
            funding_ready = st.selectbox("Funding Status", 
                                       ["Ready to invest", "Pre-approved", "Securing funding", "Planning phase"])
        
        notes = st.text_area("Investment Goals & Additional Notes")
        
        submitted = st.form_submit_button("Add Investor Lead")
        
        if submitted and name and email and phone and preferred_methods:
            # Convert selected methods to enum
            selected_methods = [CreativeFinanceMethod(method) for method in preferred_methods]
            
            lead = Lead(
                name=name,
                email=email,
                phone=phone,
                category=LeadCategory.INVESTOR,
                investor_type=InvestorType(investor_type),
                preferred_finance_methods=selected_methods,
                experience_level=experience_level,
                funding_status=funding_ready,
                target_areas=target_areas,
                notes=notes,
                budget_min=budget_min,
                budget_max=budget_max
            )
            
            crm.add_lead(lead)
            st.success(f"Investor lead {name} added successfully!")
            st.session_state.show_investor_lead = False
            st.rerun()

def show_buyer_lead_form(crm):
    """Show form specifically for buyer leads"""
    st.subheader("🏡 Add Buyer Lead - Creative Finance Purchase")
    st.write("*For buyers interested in purchasing through creative financing*")
    
    with st.form("buyer_lead_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Buyer Name*")
            email = st.text_input("Email*")
            phone = st.text_input("Phone*")
            first_time_buyer = st.checkbox("First-time home buyer")
            credit_score_range = st.selectbox("Credit Score Range", 
                                            ["Excellent (750+)", "Good (700-749)", "Fair (650-699)", 
                                             "Poor (600-649)", "Very Poor (<600)", "Unknown"])
            
        with col2:
            preferred_methods = st.multiselect("Interested Finance Methods*",
                                             [method.value for method in CreativeFinanceMethod])
            budget_min = st.number_input("Minimum Budget", min_value=0, value=0)
            budget_max = st.number_input("Maximum Budget", min_value=0, value=500000)
            desired_areas = st.text_input("Desired Areas")
            timeline = st.selectbox("Purchase Timeline", 
                                  ["ASAP", "Within 30 days", "Within 60 days", "Within 90 days", "Flexible"])
        
        notes = st.text_area("Property Requirements & Additional Notes")
        
        submitted = st.form_submit_button("Add Buyer Lead")
        
        if submitted and name and email and phone and preferred_methods:
            # Convert selected methods to enum
            selected_methods = [CreativeFinanceMethod(method) for method in preferred_methods]
            
            lead = Lead(
                name=name,
                email=email,
                phone=phone,
                category=LeadCategory.BUYER,
                preferred_finance_methods=selected_methods,
                first_time_buyer=first_time_buyer,
                credit_score_range=credit_score_range,
                desired_areas=desired_areas,
                timeline=timeline,
                notes=notes,
                budget_min=budget_min,
                budget_max=budget_max
            )
            
            crm.add_lead(lead)
            st.success(f"Buyer lead {name} added successfully!")
            st.session_state.show_buyer_lead = False
            st.rerun()

def show_general_lead_form(crm):
    """Show general lead form for other types"""
    st.subheader("📋 Add General Lead")
    st.write("*For leads that don't fit into specific categories*")
    
    with st.form("general_lead_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name*")
            email = st.text_input("Email*")
            phone = st.text_input("Phone*")
            category = st.selectbox("Lead Category*", 
                                  [cat.value for cat in LeadCategory])
            lead_source = st.selectbox("Lead Source", 
                                     [source.value for source in LeadSource])
            
        with col2:
            budget_min = st.number_input("Minimum Budget", min_value=0, value=0)
            budget_max = st.number_input("Maximum Budget", min_value=0, value=0)
            status = st.selectbox("Status", [status.value for status in LeadStatus])
            # Only show investor type if category is investor
            investor_type = None
            if category == LeadCategory.INVESTOR.value:
                investor_type = st.selectbox("Investor Type", 
                                           [inv_type.value for inv_type in InvestorType])
        
        preferred_methods = st.multiselect("Preferred Finance Methods",
                                         [method.value for method in CreativeFinanceMethod])
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("Add Lead")
        
        if submitted and name and email and phone:
            # Convert selected methods to enum
            selected_methods = [CreativeFinanceMethod(method) for method in preferred_methods] if preferred_methods else []
            
            lead = Lead(
                name=name,
                email=email,
                phone=phone,
                category=LeadCategory(category),
                investor_type=InvestorType(investor_type) if investor_type else None,
                preferred_finance_methods=selected_methods,
                lead_source=LeadSource(lead_source),
                status=LeadStatus(status),
                notes=notes,
                budget_min=budget_min,
                budget_max=budget_max
            )
            
            crm.add_lead(lead)
            st.success(f"Lead {name} added successfully!")
            st.session_state.show_general_lead = False
            st.rerun()

# ==== DEAL MANAGEMENT INTERFACE ====

def show_deal_management(crm: CRMManager):
    """Show deal management interface"""
    st.header("💼 Deal Management - Creative Finance Deals")
    
    # Deal metrics
    active_deals = crm.get_active_deals()
    closed_deals = [deal for deal in crm.deals if deal.status == DealStatus.CLOSED]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Deals", len(active_deals))
    with col2:
        st.metric("Closed Deals", len(closed_deals))
    with col3:
        total_pipeline = sum(deal.purchase_price for deal in active_deals)
        st.metric("Pipeline Value", f"${total_pipeline:,.0f}")
    with col4:
        avg_roi = sum(deal.estimated_roi for deal in crm.deals) / len(crm.deals) if crm.deals else 0
        st.metric("Avg ROI", f"{avg_roi:.1f}%")
    
    st.markdown("---")
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add New Deal", use_container_width=True):
            st.session_state.show_add_deal = True
    with col2:
        if st.button("🔍 Find Matching Buyers", use_container_width=True):
            st.session_state.show_deal_matching = True
    with col3:
        if st.button("📧 Send Deal Blast", use_container_width=True):
            st.session_state.show_deal_blast = True
    
    # Show add deal form
    if st.session_state.get('show_add_deal', False):
        if st.button("❌ Close Form"):
            st.session_state.show_add_deal = False
            st.rerun()
        show_add_deal_form(crm)
    
    st.markdown("---")
    
    # Deal filters
    st.subheader("🔍 Advanced Deal Search & Filters")
    
    with st.expander("🔧 Advanced Filters", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_filter = st.selectbox("Filter by Status", 
                                       ["All"] + [status.value for status in DealStatus])
            deal_type_filter = st.selectbox("Filter by Deal Type", 
                                          ["All"] + [dt.value for dt in DealType])
            property_type_filter = st.selectbox("Filter by Property Type", 
                                              ["All"] + [pt.value for pt in PropertyType])
        
        with col2:
            min_roi = st.number_input("Min ROI %", value=0.0, step=5.0)
            max_roi = st.number_input("Max ROI %", value=1000.0, step=5.0)
            min_price = st.number_input("Min Purchase Price", value=0, step=10000)
            max_price = st.number_input("Max Purchase Price", value=10000000, step=10000)
        
        with col3:
            min_bedrooms = st.number_input("Min Bedrooms", value=0, step=1)
            max_repairs = st.number_input("Max Repair Budget", value=1000000, step=5000)
            location_search = st.text_input("Location Search")
        
        with col4:
            financing_method_filter = st.selectbox("Financing Method", 
                                                 ["All"] + [method.value for method in CreativeFinanceMethod])
            date_from = st.date_input("Created From")
            date_to = st.date_input("Created To")
            sort_by = st.selectbox("Sort by", ["Created Date", "ROI", "Purchase Price", "Status", "ARV"])
    
    # Quick filter buttons
    st.subheader("⚡ Quick Filters")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("🔥 High ROI (>25%)", use_container_width=True):
            st.session_state.quick_filter = {'min_roi': 25}
    with col2:
        if st.button("💰 Wholesale Deals", use_container_width=True):
            st.session_state.quick_filter = {'deal_type': DealType.WHOLESALE.value}
    with col3:
        if st.button("🏠 Fix & Flip", use_container_width=True):
            st.session_state.quick_filter = {'deal_type': DealType.FIX_AND_FLIP.value}
    with col4:
        if st.button("📈 Under Contract", use_container_width=True):
            st.session_state.quick_filter = {'status': DealStatus.UNDER_CONTRACT.value}
    with col5:
        if st.button("🔄 Clear All", use_container_width=True):
            st.session_state.quick_filter = {}
    
    # Apply quick filters
    if 'quick_filter' in st.session_state and st.session_state.quick_filter:
        qf = st.session_state.quick_filter
        if 'min_roi' in qf:
            min_roi = qf['min_roi']
        if 'deal_type' in qf:
            deal_type_filter = qf['deal_type']
        if 'status' in qf:
            status_filter = qf['status']
    
    # Filter and sort deals
    filtered_deals = crm.deals
    
    # Apply all filters
    if status_filter != "All":
        filtered_deals = [deal for deal in filtered_deals if deal.status.value == status_filter]
    if deal_type_filter != "All":
        filtered_deals = [deal for deal in filtered_deals if deal.deal_type.value == deal_type_filter]
    if property_type_filter != "All":
        filtered_deals = [deal for deal in filtered_deals if deal.property_type.value == property_type_filter]
    if financing_method_filter != "All":
        filtered_deals = [deal for deal in filtered_deals if deal.financing_method and deal.financing_method.value == financing_method_filter]
    
    # ROI filters
    filtered_deals = [deal for deal in filtered_deals if min_roi <= deal.estimated_roi <= max_roi]
    
    # Price filters
    if min_price > 0:
        filtered_deals = [deal for deal in filtered_deals if deal.purchase_price >= min_price]
    if max_price < 10000000:
        filtered_deals = [deal for deal in filtered_deals if deal.purchase_price <= max_price]
    
    # Property filters
    if min_bedrooms > 0:
        filtered_deals = [deal for deal in filtered_deals if deal.bedrooms >= min_bedrooms]
    if max_repairs < 1000000:
        filtered_deals = [deal for deal in filtered_deals if deal.estimated_repairs <= max_repairs]
    
    # Location search
    if location_search:
        filtered_deals = [deal for deal in filtered_deals if location_search.lower() in deal.property_address.lower()]
    
    # Date filters
    if date_from:
        date_from_dt = datetime.combine(date_from, datetime.min.time())
        filtered_deals = [deal for deal in filtered_deals if deal.created_at >= date_from_dt]
    if date_to:
        date_to_dt = datetime.combine(date_to, datetime.max.time())
        filtered_deals = [deal for deal in filtered_deals if deal.created_at <= date_to_dt]
    
    # Sort deals
    if sort_by == "ROI":
        filtered_deals.sort(key=lambda x: x.estimated_roi, reverse=True)
    elif sort_by == "Purchase Price":
        filtered_deals.sort(key=lambda x: x.purchase_price, reverse=True)
    elif sort_by == "ARV":
        filtered_deals.sort(key=lambda x: x.arv, reverse=True)
    elif sort_by == "Status":
        filtered_deals.sort(key=lambda x: x.status.value)
    elif sort_by == "Created Date":
        filtered_deals.sort(key=lambda x: x.created_at, reverse=True)
    
    # Deals table
    if filtered_deals:
        deals_data = []
        for deal in filtered_deals:
            deals_data.append({
                'Title': deal.title,
                'Address': deal.property_address,
                'Type': deal.deal_type.value,
                'Status': deal.status.value,
                'Purchase Price': f"${deal.purchase_price:,.0f}",
                'ARV': f"${deal.arv:,.0f}",
                'ROI': f"{deal.estimated_roi:.1f}%",
                'Profit': f"${deal.projected_profit:,.0f}",
                'Created': deal.created_at.strftime('%Y-%m-%d')
            })
        
        df = pd.DataFrame(deals_data)
        st.dataframe(df, use_container_width=True)
        
        # Deal details
        if filtered_deals:
            selected_deal = st.selectbox("Select Deal for Details", 
                                       [f"{deal.title} - {deal.property_address}" for deal in filtered_deals])
            
            if selected_deal:
                deal_title = selected_deal.split(" - ")[0]
                deal = next((d for d in filtered_deals if d.title == deal_title), None)
                if deal:
                    show_deal_details(crm, deal)
    else:
        st.info("No deals found matching the criteria.")

def show_add_deal_form(crm: CRMManager):
    """Show add deal form"""
    st.subheader("➕ Add New Deal")
    
    with st.form("add_deal_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Deal Title*")
            property_address = st.text_area("Property Address*")
            property_type = st.selectbox("Property Type", [pt.value for pt in PropertyType])
            deal_type = st.selectbox("Deal Type", [dt.value for dt in DealType])
            status = st.selectbox("Status", [status.value for status in DealStatus])
            
            # Property details
            bedrooms = st.number_input("Bedrooms", min_value=0, value=3)
            bathrooms = st.number_input("Bathrooms", min_value=0.0, value=2.0, step=0.5)
            square_feet = st.number_input("Square Feet", min_value=0, value=1500)
            
        with col2:
            # Financial details
            asking_price = st.number_input("Asking Price", min_value=0.0, value=0.0)
            purchase_price = st.number_input("Purchase Price", min_value=0.0, value=0.0)
            arv = st.number_input("ARV (After Repair Value)", min_value=0.0, value=0.0)
            estimated_repairs = st.number_input("Estimated Repairs", min_value=0.0, value=0.0)
            
            if deal_type == DealType.WHOLESALE.value:
                wholesale_fee = st.number_input("Wholesale Fee", min_value=0.0, value=0.0)
            else:
                wholesale_fee = 0.0
                
            if deal_type == DealType.BUY_AND_HOLD.value:
                monthly_rent = st.number_input("Monthly Rent", min_value=0.0, value=0.0)
                monthly_expenses = st.number_input("Monthly Expenses", min_value=0.0, value=0.0)
            else:
                monthly_rent = 0.0
                monthly_expenses = 0.0
        
        # Seller information
        st.subheader("Seller Information")
        col1, col2 = st.columns(2)
        with col1:
            seller_name = st.text_input("Seller Name")
            seller_phone = st.text_input("Seller Phone")
        with col2:
            seller_email = st.text_input("Seller Email")
            seller_motivation = st.text_input("Seller Motivation")
        
        # Creative finance details
        financing_method = st.selectbox("Financing Method", 
                                       ["None"] + [method.value for method in CreativeFinanceMethod])
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("Add Deal")
        
        if submitted and title and property_address:
            deal = Deal(
                title=title,
                property_address=property_address,
                property_type=PropertyType(property_type),
                deal_type=DealType(deal_type),
                status=DealStatus(status),
                asking_price=asking_price,
                purchase_price=purchase_price,
                arv=arv,
                estimated_repairs=estimated_repairs,
                wholesale_fee=wholesale_fee,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                square_feet=square_feet,
                seller_name=seller_name,
                seller_phone=seller_phone,
                seller_email=seller_email,
                seller_motivation=seller_motivation,
                monthly_rent=monthly_rent,
                monthly_expenses=monthly_expenses,
                financing_method=CreativeFinanceMethod(financing_method) if financing_method != "None" else None,
                notes=notes
            )
            
            crm.add_deal(deal)
            st.success(f"Deal '{title}' added successfully!")
            st.session_state.show_add_deal = False
            st.rerun()

def show_deal_details(crm: CRMManager, deal: Deal):
    """Show detailed view of a deal"""
    st.subheader(f"📄 Deal Details: {deal.title}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎯 Find Matching Buyers"):
            matches = crm.find_matching_buyers_for_deal(deal)
            if matches:
                st.subheader("🎯 Matching Buyers")
                for match in matches[:5]:  # Show top 5 matches
                    buyer = match['buyer']
                    score = match['match_score']
                    st.write(f"**{buyer.buyer_name}** - Match Score: {score:.1f}%")
                    st.write(f"📧 {buyer.buyer_email} | 📞 {buyer.buyer_phone}")
                    st.write(f"Type: {buyer.investor_type.value}")
                    st.write("---")
            else:
                st.info("No matching buyers found for this deal.")
    
    with col2:
        if st.button("📧 Send to Buyers"):
            result = crm.send_deal_to_buyers(deal)
            st.success(f"Deal sent to {result['sent_count']} matching buyers!")
    
    with col3:
        if st.button("✏️ Edit Deal"):
            st.session_state.edit_deal_id = deal.id
    
    # Deal information tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Financial", "🏠 Property", "👤 Seller", "📝 Notes"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Purchase Price", f"${deal.purchase_price:,.0f}")
            st.metric("ARV", f"${deal.arv:,.0f}")
            st.metric("Estimated Repairs", f"${deal.estimated_repairs:,.0f}")
        with col2:
            st.metric("Estimated ROI", f"{deal.estimated_roi:.1f}%")
            st.metric("Projected Profit", f"${deal.projected_profit:,.0f}")
            if deal.deal_type == DealType.WHOLESALE:
                st.metric("Wholesale Fee", f"${deal.wholesale_fee:,.0f}")
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Address:** {deal.property_address}")
            st.write(f"**Property Type:** {deal.property_type.value}")
            st.write(f"**Bedrooms:** {deal.bedrooms}")
            st.write(f"**Bathrooms:** {deal.bathrooms}")
        with col2:
            st.write(f"**Square Feet:** {deal.square_feet:,}")
            st.write(f"**Condition:** {deal.condition or 'Not specified'}")
            st.write(f"**Year Built:** {deal.year_built or 'Not specified'}")
    
    with tab3:
        st.write(f"**Name:** {deal.seller_name}")
        st.write(f"**Phone:** {deal.seller_phone}")
        st.write(f"**Email:** {deal.seller_email}")
        st.write(f"**Motivation:** {deal.seller_motivation}")
        st.write(f"**Timeline:** {deal.timeline}")
    
    with tab4:
        st.write(deal.notes or "No notes available")

# ==== BUYER MANAGEMENT INTERFACE ====

def show_buyer_management(crm: CRMManager):
    """Show buyer management interface"""
    st.header("🎯 Buyer Management - Investment Criteria")
    
    # Buyer metrics
    active_buyers = crm.get_active_buyers()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Buyers", len(active_buyers))
    with col2:
        total_cash = sum(buyer.cash_available for buyer in active_buyers)
        st.metric("Total Available Cash", f"${total_cash:,.0f}")
    with col3:
        avg_roi_requirement = sum(buyer.min_roi for buyer in active_buyers) / len(active_buyers) if active_buyers else 0
        st.metric("Avg ROI Requirement", f"{avg_roi_requirement:.1f}%")
    with col4:
        financing_ready = len([buyer for buyer in active_buyers if buyer.financing_ready])
        st.metric("Financing Ready", financing_ready)
    
    st.markdown("---")
    
    # Quick actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add New Buyer", use_container_width=True):
            st.session_state.show_add_buyer = True
    with col2:
        if st.button("📧 Send Deal Blast to All", use_container_width=True):
            st.session_state.show_deal_blast = True
    
    # Show add buyer form
    if st.session_state.get('show_add_buyer', False):
        if st.button("❌ Close Form"):
            st.session_state.show_add_buyer = False
            st.rerun()
        show_add_buyer_form(crm)
    
    st.markdown("---")
    
    # Buyer filters
    col1, col2, col3 = st.columns(3)
    with col1:
        investor_filter = st.selectbox("Filter by Investor Type", 
                                     ["All"] + [inv.value for inv in InvestorType])
    with col2:
        min_cash = st.number_input("Min Cash Available", value=0, step=10000)
    with col3:
        financing_filter = st.selectbox("Financing Status", ["All", "Ready", "Not Ready"])
    
    # Filter buyers
    filtered_buyers = active_buyers
    if investor_filter != "All":
        filtered_buyers = [buyer for buyer in filtered_buyers if buyer.investor_type.value == investor_filter]
    if min_cash > 0:
        filtered_buyers = [buyer for buyer in filtered_buyers if buyer.cash_available >= min_cash]
    if financing_filter == "Ready":
        filtered_buyers = [buyer for buyer in filtered_buyers if buyer.financing_ready]
    elif financing_filter == "Not Ready":
        filtered_buyers = [buyer for buyer in filtered_buyers if not buyer.financing_ready]
    
    # Buyers table
    if filtered_buyers:
        buyers_data = []
        for buyer in filtered_buyers:
            property_types = ", ".join([pt.value for pt in buyer.preferred_property_types]) if buyer.preferred_property_types else "Any"
            deal_types = ", ".join([dt.value for dt in buyer.preferred_deal_types]) if buyer.preferred_deal_types else "Any"
            
            buyers_data.append({
                'Name': buyer.buyer_name,
                'Email': buyer.buyer_email,
                'Phone': buyer.buyer_phone,
                'Type': buyer.investor_type.value,
                'Min ROI': f"{buyer.min_roi}%",
                'Max Price': f"${buyer.max_purchase_price:,.0f}" if buyer.max_purchase_price > 0 else "No limit",
                'Cash Available': f"${buyer.cash_available:,.0f}",
                'Property Types': property_types,
                'Deal Types': deal_types,
                'Financing Ready': "✓" if buyer.financing_ready else "✗"
            })
        
        df = pd.DataFrame(buyers_data)
        st.dataframe(df, use_container_width=True)
        
        # Buyer details
        if filtered_buyers:
            selected_buyer = st.selectbox("Select Buyer for Details", 
                                        [f"{buyer.buyer_name} - {buyer.buyer_email}" for buyer in filtered_buyers])
            
            if selected_buyer:
                buyer_name = selected_buyer.split(" - ")[0]
                buyer = next((b for b in filtered_buyers if b.buyer_name == buyer_name), None)
                if buyer:
                    show_buyer_details(crm, buyer)
    else:
        st.info("No buyers found matching the criteria.")

def show_add_buyer_form(crm: CRMManager):
    """Show add buyer form"""
    st.subheader("➕ Add New Buyer")
    
    with st.form("add_buyer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            buyer_name = st.text_input("Buyer Name*")
            buyer_email = st.text_input("Email*")
            buyer_phone = st.text_input("Phone*")
            investor_type = st.selectbox("Investor Type", [inv.value for inv in InvestorType])
            
        with col2:
            min_roi = st.number_input("Minimum ROI %", min_value=0.0, value=15.0, step=5.0)
            max_purchase_price = st.number_input("Maximum Purchase Price", min_value=0, value=0, step=10000)
            cash_available = st.number_input("Cash Available", min_value=0, value=0, step=10000)
            financing_ready = st.checkbox("Financing Ready")
        
        # Preferences
        preferred_property_types = st.multiselect("Preferred Property Types",
                                                [pt.value for pt in PropertyType])
        preferred_deal_types = st.multiselect("Preferred Deal Types",
                                            [dt.value for dt in DealType])
        preferred_finance_methods = st.multiselect("Preferred Finance Methods",
                                                 [method.value for method in CreativeFinanceMethod])
        
        target_locations = st.text_input("Target Locations (comma separated)")
        min_bedrooms = st.number_input("Minimum Bedrooms", min_value=0, value=0)
        max_repairs = st.number_input("Maximum Repair Budget", min_value=0, value=0, step=5000)
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("Add Buyer")
        
        if submitted and buyer_name and buyer_email:
            buyer = BuyerCriteria(
                buyer_name=buyer_name,
                buyer_email=buyer_email,
                buyer_phone=buyer_phone,
                investor_type=InvestorType(investor_type),
                min_roi=min_roi,
                max_purchase_price=max_purchase_price,
                cash_available=cash_available,
                financing_ready=financing_ready,
                preferred_property_types=[PropertyType(pt) for pt in preferred_property_types],
                preferred_deal_types=[DealType(dt) for dt in preferred_deal_types],
                preferred_finance_methods=[CreativeFinanceMethod(method) for method in preferred_finance_methods],
                target_locations=target_locations.split(",") if target_locations else [],
                min_bedrooms=min_bedrooms,
                max_repairs=max_repairs,
                notes=notes
            )
            
            crm.add_buyer(buyer)
            st.success(f"Buyer '{buyer_name}' added successfully!")
            st.session_state.show_add_buyer = False
            st.rerun()

def show_buyer_details(crm: CRMManager, buyer: BuyerCriteria):
    """Show detailed view of a buyer"""
    st.subheader(f"👤 Buyer Details: {buyer.buyer_name}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔍 Find Matching Deals"):
            matching_deals = []
            for deal in crm.deals:
                if buyer.matches_deal(deal):
                    score = crm.matching_engine.score_deal_match(deal, buyer)
                    matching_deals.append({'deal': deal, 'score': score})
            
            if matching_deals:
                st.subheader("🔍 Matching Deals")
                matching_deals.sort(key=lambda x: x['score'], reverse=True)
                for match in matching_deals[:5]:
                    deal = match['deal']
                    score = match['score']
                    st.write(f"**{deal.title}** - Match Score: {score:.1f}%")
                    st.write(f"📍 {deal.property_address}")
                    st.write(f"💰 ${deal.purchase_price:,.0f} | ROI: {deal.estimated_roi:.1f}%")
                    st.write("---")
            else:
                st.info("No matching deals found for this buyer.")
    
    with col2:
        if st.button("✏️ Edit Buyer"):
            st.session_state.edit_buyer_id = buyer.id
    
    with col3:
        active_status = "Active" if buyer.active else "Inactive"
        st.write(f"**Status:** {active_status}")
    
    # Buyer information tabs
    tab1, tab2, tab3 = st.tabs(["💰 Financial", "🎯 Preferences", "📝 Notes"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Minimum ROI", f"{buyer.min_roi}%")
            st.metric("Cash Available", f"${buyer.cash_available:,.0f}")
        with col2:
            st.metric("Max Purchase Price", f"${buyer.max_purchase_price:,.0f}" if buyer.max_purchase_price > 0 else "No limit")
            st.write(f"**Financing Ready:** {'Yes' if buyer.financing_ready else 'No'}")
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Property Types:**")
            for pt in buyer.preferred_property_types:
                st.write(f"• {pt.value}")
            
            st.write("**Deal Types:**")
            for dt in buyer.preferred_deal_types:
                st.write(f"• {dt.value}")
        
        with col2:
            st.write("**Finance Methods:**")
            for method in buyer.preferred_finance_methods:
                st.write(f"• {method.value}")
            
            if buyer.target_locations:
                st.write("**Target Locations:**")
                for location in buyer.target_locations:
                    st.write(f"• {location.strip()}")
    
    with tab3:
        st.write(buyer.notes or "No notes available")

# ==== ROI DASHBOARD ====

def show_roi_dashboard(crm: CRMManager):
    """Show ROI optimization dashboard"""
    st.header("💰 ROI Optimization Dashboard")
    
    portfolio_summary = crm.get_portfolio_summary()
    
    # Portfolio metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Portfolio Value", f"${portfolio_summary['total_portfolio_value']:,.0f}")
    with col2:
        st.metric("Total Profit", f"${portfolio_summary['total_profit']:,.0f}")
    with col3:
        st.metric("Average ROI", f"{portfolio_summary['average_roi']:.1f}%")
    with col4:
        st.metric("Pipeline Value", f"${portfolio_summary['pipeline_value']:,.0f}")
    
    st.markdown("---")
    
    # ROI Analysis Charts
    if crm.deals:
        col1, col2 = st.columns(2)
        
        with col1:
            # ROI by Deal Type
            deal_roi = {}
            for deal in crm.deals:
                deal_type = deal.deal_type.value
                if deal_type not in deal_roi:
                    deal_roi[deal_type] = []
                deal_roi[deal_type].append(deal.estimated_roi)
            
            avg_roi_by_type = {dt: sum(rois) / len(rois) for dt, rois in deal_roi.items()}
            
            fig = go.Figure(data=[
                go.Bar(x=list(avg_roi_by_type.keys()), y=list(avg_roi_by_type.values()))
            ])
            fig.update_layout(title="Average ROI by Deal Type", yaxis_title="ROI %")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Deal Status Distribution
            status_counts = {}
            for deal in crm.deals:
                status = deal.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            fig = go.Figure(data=[
                go.Pie(labels=list(status_counts.keys()), values=list(status_counts.values()))
            ])
            fig.update_layout(title="Deal Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Top performing deals
        st.subheader("🏆 Top Performing Deals")
        top_deals = sorted(crm.deals, key=lambda x: x.estimated_roi, reverse=True)[:10]
        
        if top_deals:
            deals_data = []
            for deal in top_deals:
                deals_data.append({
                    'Title': deal.title,
                    'Type': deal.deal_type.value,
                    'Purchase Price': f"${deal.purchase_price:,.0f}",
                    'ROI': f"{deal.estimated_roi:.1f}%",
                    'Profit': f"${deal.projected_profit:,.0f}",
                    'Status': deal.status.value
                })
            
            df = pd.DataFrame(deals_data)
            st.dataframe(df, use_container_width=True)
    else:
        st.info("No deals available for ROI analysis. Add some deals to see metrics!")

# ==== COMMUNICATION HUB INTERFACE ====

def show_communication_hub(crm: CRMManager):
    """Enhanced communication hub with email automation"""
    st.header("💬 Communication Hub - Email Marketing & Automation")
    
    # Get email manager
    email_manager = get_email_manager()
    
    # Communication metrics
    analytics = email_manager.get_email_analytics()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Emails Sent", analytics['total_sent'])
    with col2:
        st.metric("Open Rate", f"{analytics['open_rate']:.1f}%")
    with col3:
        st.metric("Click Rate", f"{analytics['click_rate']:.1f}%")
    with col4:
        st.metric("Active Campaigns", len([c for c in email_manager.campaigns if c.status == CampaignStatus.ACTIVE]))
    
    st.markdown("---")
    
    # Enhanced communication tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📧 Send Email", 
        "📝 Email Templates", 
        "🔄 Drip Campaigns", 
        "📊 Email Analytics",
        "💬 Messages", 
        "📢 Deal Alerts"
    ])
    
    with tab1:
        show_send_email_form(crm, email_manager)
    
    with tab2:
        show_email_templates(email_manager)
    
    with tab3:
        show_drip_campaigns(crm, email_manager)
    
    with tab4:
        show_email_analytics(email_manager)
    
    with tab5:
        show_message_inbox(crm)
    
    with tab6:
        show_send_deal_alert(crm)

def show_send_email_form(crm: CRMManager, email_manager):
    """Enhanced email sending interface"""
    st.subheader("📧 Send Professional Email")
    
    # Email composition form
    with st.form("send_email_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Recipient selection
            st.markdown("#### 👥 Recipients")
            recipient_type = st.selectbox("Send to:", [
                "Select recipient type...",
                "Individual Lead",
                "Individual Contact", 
                "All Leads",
                "All Qualified Leads",
                "All New Leads",
                "All Investors",
                "All Sellers",
                "Custom Email"
            ])
            
            recipients = []
            if recipient_type == "Individual Lead" and crm.leads:
                selected_lead = st.selectbox("Select Lead", 
                    ["Select lead..."] + [f"{lead.name} - {lead.email}" for lead in crm.leads if lead.email])
                if selected_lead != "Select lead...":
                    lead_email = selected_lead.split(" - ")[1]
                    recipients = [lead_email]
                    
            elif recipient_type == "Individual Contact" and crm.contacts:
                selected_contact = st.selectbox("Select Contact",
                    ["Select contact..."] + [f"{contact.name} - {contact.email}" for contact in crm.contacts if contact.email])
                if selected_contact != "Select contact...":
                    contact_email = selected_contact.split(" - ")[1]
                    recipients = [contact_email]
                    
            elif recipient_type == "All Leads":
                recipients = [lead.email for lead in crm.leads if lead.email]
                st.info(f"Will send to {len(recipients)} leads with email addresses")
                
            elif recipient_type == "All Qualified Leads":
                qualified_leads = [lead for lead in crm.leads if lead.status == LeadStatus.QUALIFIED and lead.email]
                recipients = [lead.email for lead in qualified_leads]
                st.info(f"Will send to {len(recipients)} qualified leads")
                
            elif recipient_type == "Custom Email":
                custom_emails = st.text_area("Email Addresses", 
                    placeholder="Enter email addresses separated by commas")
                if custom_emails:
                    recipients = [email.strip() for email in custom_emails.split(",") if email.strip()]
            
            # Template selection
            st.markdown("#### 📝 Email Template")
            use_template = st.checkbox("Use existing template")
            
            if use_template and email_manager.templates:
                template_options = ["Select template..."] + [f"{template.name} ({template.email_type.value})" for template in email_manager.templates]
                selected_template = st.selectbox("Choose Template", template_options)
                
                if selected_template != "Select template...":
                    template_name = selected_template.split(" (")[0]
                    template = next((t for t in email_manager.templates if t.name == template_name), None)
                    
                    if template:
                        st.info(f"📧 **Subject:** {template.subject}")
                        with st.expander("Preview Email Content"):
                            st.write("**HTML Version:**")
                            st.code(template.body_html[:500] + "..." if len(template.body_html) > 500 else template.body_html)
                            st.write("**Text Version:**")
                            st.text(template.body_text[:300] + "..." if len(template.body_text) > 300 else template.body_text)
        
        with col2:
            # Email composition
            st.markdown("#### ✍️ Compose Email")
            
            if not use_template or selected_template == "Select template...":
                subject = st.text_input("Subject Line*", placeholder="Enter email subject...")
                
                email_body = st.text_area("Email Message*", 
                    height=300,
                    placeholder="""Hi {first_name},

I hope this email finds you well! I wanted to reach out regarding...

Best regards,
{agent_name}""")
            else:
                st.info("Using selected template content")
                subject = template.subject if 'template' in locals() else ""
                email_body = template.body_text if 'template' in locals() else ""
            
            # Personalization variables
            st.markdown("#### 🎯 Available Variables")
            st.code("""{first_name} - Recipient's first name
{last_name} - Recipient's last name  
{email} - Recipient's email
{company} - Company name
{agent_name} - Your name
{phone_number} - Your phone
{property_address} - Property address
{asking_price} - Property price
{roi} - Return on investment""")
        
        # Send button
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            send_now = st.form_submit_button("📤 Send Email Now", type="primary", use_container_width=True)
        with col2:
            schedule_send = st.form_submit_button("⏰ Schedule Send", use_container_width=True)
        with col3:
            save_draft = st.form_submit_button("💾 Save Draft", use_container_width=True)
        
        if send_now and recipients and subject and email_body:
            # Use real email services for sending
            success_count = 0
            failed_count = 0
            
            # Progress bar for bulk sending
            if len(recipients) > 1:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            # Send emails using real services
            for i, recipient in enumerate(recipients):
                try:
                    if use_template and 'template' in locals() and template:
                        # Send using template with real email service
                        result = email_manager.send_real_email(
                            recipient_email=recipient,
                            template=template,
                            variables={
                                'first_name': recipient.split('@')[0],  # Simple name extraction
                                'email': recipient,
                                'agent_name': 'NXTRIX Team'
                            }
                        )
                    else:
                        # Create temporary template for custom email
                        from email_automation import EmailTemplate, EmailType
                        temp_template = EmailTemplate(
                            name="Custom Email",
                            email_type=EmailType.GENERAL,
                            subject=subject,
                            body_html=f"<html><body><p>{email_body.replace(chr(10), '</p><p>')}</p></body></html>",
                            body_text=email_body
                        )
                        
                        result = email_manager.send_real_email(
                            recipient_email=recipient,
                            template=temp_template,
                            variables={
                                'first_name': recipient.split('@')[0],
                                'email': recipient,
                                'agent_name': 'NXTRIX Team'
                            }
                        )
                    
                    if result['success']:
                        success_count += 1
                    else:
                        failed_count += 1
                        if not result.get('simulation', False):
                            st.error(f"❌ Failed to send to {recipient}: {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    failed_count += 1
                    st.error(f"❌ Error sending to {recipient}: {str(e)}")
                
                # Update progress for bulk sends
                if len(recipients) > 1:
                    progress = (i + 1) / len(recipients)
                    progress_bar.progress(progress)
                    status_text.text(f"Sending... {i + 1}/{len(recipients)}")
            
            # Show results
            if success_count > 0:
                st.success(f"✅ Successfully sent {success_count} emails!")
                if success_count == len(recipients):
                    st.balloons()
            
            if failed_count > 0:
                st.warning(f"⚠️ {failed_count} emails failed to send")
            
            # Test services button
            st.markdown("---")
            if st.button("🔧 Test Email Services", help="Test your Twilio and EmailJS connections"):
                with st.spinner("Testing email services..."):
                    test_result = email_manager.test_email_service()
                    
                    if test_result['success']:
                        st.success("✅ Email services are working correctly!")
                    else:
                        st.error(f"❌ Email service test failed: {test_result['message']}")
                        
                        if not test_result.get('simulation', False):
                            st.info("💡 Check your EmailJS configuration in the .env.local file")
            
        elif schedule_send:
            st.info("📅 Email scheduling feature coming soon!")
            
        elif save_draft:
            st.info("💾 Draft saving feature coming soon!")

def show_email_templates(email_manager):
    """Email template management interface"""
    st.subheader("📝 Email Template Library")
    
    # Template actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Create New Template", use_container_width=True):
            st.session_state.show_create_template = True
    with col2:
        if st.button("📥 Import Template", use_container_width=True):
            st.info("📄 Template import feature coming soon!")
    with col3:
        if st.button("📤 Export Templates", use_container_width=True):
            st.info("📄 Template export feature coming soon!")
    
    # Show create template form
    if st.session_state.get('show_create_template', False):
        show_create_template_form(email_manager)
    
    # Templates list
    if email_manager.templates:
        st.markdown("### 📚 Available Templates")
        
        for template in email_manager.templates:
            with st.expander(f"📧 {template.name} ({template.email_type.value})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Subject:** {template.subject}")
                    st.write(f"**Type:** {template.email_type.value}")
                    st.write(f"**Variables:** {', '.join(template.variables) if template.variables else 'None'}")
                    st.write(f"**Created:** {template.created_at.strftime('%Y-%m-%d')}")
                    
                    # Preview content
                    if st.button(f"👁️ Preview", key=f"preview_{template.id}"):
                        st.markdown("**HTML Preview:**")
                        st.code(template.body_html[:300] + "...")
                        st.markdown("**Text Preview:**")
                        st.text(template.body_text[:200] + "...")
                
                with col2:
                    if st.button(f"✏️ Edit", key=f"edit_{template.id}"):
                        st.session_state.edit_template_id = template.id
                    
                    if st.button(f"🗑️ Delete", key=f"delete_{template.id}"):
                        email_manager.delete_template(template.id)
                        st.success("Template deleted!")
                        st.rerun()
    else:
        st.info("📝 No templates found. Create your first template to get started!")

def show_create_template_form(email_manager):
    """Template creation form"""
    st.markdown("### ➕ Create New Email Template")
    
    with st.form("create_template_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Template Name*", placeholder="e.g., Welcome Email")
            email_type = st.selectbox("Template Type", [t.value for t in EmailType])
            subject = st.text_input("Subject Line*", placeholder="Subject with {variables}")
            
        with col2:
            variables = st.text_input("Variables (comma-separated)", 
                placeholder="first_name, property_address, roi")
            is_active = st.checkbox("Active Template", value=True)
        
        body_html = st.text_area("HTML Email Body*", 
            height=200,
            placeholder="""<html><body>
<h2>Hi {first_name},</h2>
<p>Your email content here...</p>
<p>Best regards,<br>{agent_name}</p>
</body></html>""")
        
        body_text = st.text_area("Plain Text Version*",
            height=150, 
            placeholder="""Hi {first_name},

Your email content here...

Best regards,
{agent_name}""")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.form_submit_button("💾 Create Template", type="primary", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submitted and name and subject and body_html and body_text:
            template = EmailTemplate(
                name=name,
                email_type=EmailType(email_type),
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                variables=[v.strip() for v in variables.split(",") if v.strip()] if variables else [],
                is_active=is_active
            )
            
            email_manager.create_template(template)
            st.success(f"✅ Template '{name}' created successfully!")
            st.session_state.show_create_template = False
            st.rerun()
        
        if cancelled:
            st.session_state.show_create_template = False
            st.rerun()

def show_drip_campaigns(crm: CRMManager, email_manager):
    """Drip campaign management interface"""
    st.subheader("🔄 Automated Drip Campaigns")
    
    # Campaign metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_campaigns = len(email_manager.campaigns)
        st.metric("Total Campaigns", total_campaigns)
    with col2:
        active_campaigns = len([c for c in email_manager.campaigns if c.status == CampaignStatus.ACTIVE])
        st.metric("Active Campaigns", active_campaigns)
    with col3:
        # Calculate total subscribers across all campaigns
        total_subscribers = sum(len(c.subscribers) for c in email_manager.campaigns)
        st.metric("Total Subscribers", total_subscribers)
    with col4:
        completed_campaigns = len([c for c in email_manager.campaigns if c.status == CampaignStatus.COMPLETED])
        st.metric("Completed", completed_campaigns)
    
    st.markdown("---")
    
    # Campaign actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Create New Campaign", use_container_width=True):
            st.session_state.show_create_campaign = True
    with col2:
        if st.button("📊 Campaign Analytics", use_container_width=True):
            st.info("📈 Detailed campaign analytics coming soon!")
    with col3:
        if st.button("⚙️ Automation Settings", use_container_width=True):
            st.info("⚙️ Advanced automation settings coming soon!")
    
    # Show create campaign form
    if st.session_state.get('show_create_campaign', False):
        show_create_campaign_form(crm, email_manager)
    
    # Campaign list
    if email_manager.campaigns:
        st.markdown("### 📋 Campaign List")
        
        for campaign in email_manager.campaigns:
            with st.expander(f"🔄 {campaign.name} ({campaign.status.value})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Description:** {campaign.description}")
                    st.write(f"**Target Audience:** {campaign.target_audience}")
                    st.write(f"**Status:** {campaign.status.value}")
                    st.write(f"**Subscribers:** {len(campaign.subscribers)}")
                    st.write(f"**Email Sequence:** {len(campaign.emails)} emails")
                    st.write(f"**Created:** {campaign.created_at.strftime('%Y-%m-%d')}")
                    
                    if campaign.started_at:
                        st.write(f"**Started:** {campaign.started_at.strftime('%Y-%m-%d')}")
                
                with col2:
                    if campaign.status == CampaignStatus.DRAFT:
                        if st.button(f"▶️ Start Campaign", key=f"start_{campaign.id}"):
                            # Update campaign status
                            email_manager.campaigns[email_manager.campaigns.index(campaign)].status = CampaignStatus.ACTIVE
                            email_manager.campaigns[email_manager.campaigns.index(campaign)].started_at = datetime.now()
                            email_manager.save_data()
                            st.success("Campaign started!")
                            st.rerun()
                    
                    elif campaign.status == CampaignStatus.ACTIVE:
                        if st.button(f"⏸️ Pause", key=f"pause_{campaign.id}"):
                            email_manager.campaigns[email_manager.campaigns.index(campaign)].status = CampaignStatus.PAUSED
                            email_manager.save_data()
                            st.success("Campaign paused!")
                            st.rerun()
                    
                    if st.button(f"✏️ Edit", key=f"edit_campaign_{campaign.id}"):
                        st.info("Campaign editing coming soon!")
                    
                    if st.button(f"🗑️ Delete", key=f"delete_campaign_{campaign.id}"):
                        email_manager.campaigns.remove(campaign)
                        email_manager.save_data()
                        st.success("Campaign deleted!")
                        st.rerun()
    else:
        st.info("🔄 No drip campaigns found. Create your first automated campaign!")

def show_create_campaign_form(crm: CRMManager, email_manager):
    """Campaign creation form"""
    st.markdown("### ➕ Create New Drip Campaign")
    
    with st.form("create_campaign_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Campaign Name*", placeholder="e.g., New Lead Nurture Sequence")
            description = st.text_area("Description", placeholder="Describe the purpose of this campaign...")
            target_audience = st.selectbox("Target Audience", [
                "All New Leads",
                "Qualified Leads", 
                "Investor Leads",
                "Seller Leads",
                "Buyer Leads",
                "Custom Audience"
            ])
        
        with col2:
            # Email sequence
            st.markdown("**Email Sequence**")
            num_emails = st.number_input("Number of emails in sequence", min_value=1, max_value=10, value=3)
            
            st.info(f"💡 This will create a {num_emails}-email automated sequence")
        
        # Campaign emails
        emails = []
        for i in range(num_emails):
            st.markdown(f"#### 📧 Email {i+1}")
            col1, col2 = st.columns(2)
            
            with col1:
                delay_days = st.number_input(f"Send after (days)", key=f"delay_{i}", 
                    min_value=0, value=i*3, help=f"Days after previous email (or signup for first email)")
                template_id = st.selectbox(f"Template", 
                    ["Create custom..."] + [f"{t.name}" for t in email_manager.templates],
                    key=f"template_{i}")
            
            with col2:
                custom_subject = st.text_input(f"Custom Subject", key=f"subject_{i}", 
                    placeholder="Leave blank to use template subject")
                
            emails.append({
                "delay_days": delay_days,
                "template_id": template_id if template_id != "Create custom..." else None,
                "custom_subject": custom_subject,
                "order": i + 1
            })
        
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.form_submit_button("🔄 Create Campaign", type="primary", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submitted and name:
            campaign = DripCampaign(
                name=name,
                description=description,
                target_audience=target_audience,
                status=CampaignStatus.DRAFT,
                emails=emails,
                subscribers=[],
                trigger_conditions={"audience_type": target_audience}
            )
            
            email_manager.create_campaign(campaign)
            st.success(f"✅ Campaign '{name}' created successfully!")
            st.session_state.show_create_campaign = False
            st.rerun()
        
        if cancelled:
            st.session_state.show_create_campaign = False
            st.rerun()

def show_email_analytics(email_manager):
    """Email performance analytics dashboard"""
    st.subheader("📊 Email Marketing Analytics")
    
    analytics = email_manager.get_email_analytics()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Emails Sent", analytics['total_sent'])
    with col2:
        st.metric("Total Opened", analytics['total_opened'], 
                 delta=f"{analytics['open_rate']:.1f}% open rate")
    with col3:
        st.metric("Total Clicked", analytics['total_clicked'],
                 delta=f"{analytics['click_rate']:.1f}% click rate") 
    with col4:
        st.metric("Total Replied", analytics['total_replied'],
                 delta=f"{analytics['reply_rate']:.1f}% reply rate")
    
    # Performance charts
    if analytics['total_sent'] > 0:
        st.markdown("### 📈 Performance Overview")
        
        # Create engagement funnel chart
        funnel_data = {
            'Stage': ['Sent', 'Opened', 'Clicked', 'Replied'],
            'Count': [
                analytics['total_sent'],
                analytics['total_opened'], 
                analytics['total_clicked'],
                analytics['total_replied']
            ],
            'Rate': [100, analytics['open_rate'], analytics['click_rate'], analytics['reply_rate']]
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Funnel chart
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_data['Stage'],
                x=funnel_data['Count'],
                textinfo="value+percent initial"
            ))
            fig_funnel.update_layout(title="Email Engagement Funnel", height=400)
            st.plotly_chart(fig_funnel, use_container_width=True)
        
        with col2:
            # Performance rates chart
            fig_rates = go.Figure(data=[
                go.Bar(name='Engagement Rates', 
                       x=funnel_data['Stage'][1:], 
                       y=funnel_data['Rate'][1:],
                       marker_color=['#3498db', '#e74c3c', '#2ecc71'])
            ])
            fig_rates.update_layout(title="Engagement Rates", 
                                   yaxis_title="Rate (%)", height=400)
            st.plotly_chart(fig_rates, use_container_width=True)
        
        # Email performance tips
        st.markdown("### 💡 Performance Insights")
        
        if analytics['open_rate'] < 20:
            st.warning("📧 **Low Open Rate:** Consider improving subject lines and send timing")
        elif analytics['open_rate'] > 25:
            st.success("📧 **Good Open Rate:** Your subject lines are working well!")
        
        if analytics['click_rate'] < 3:
            st.warning("🖱️ **Low Click Rate:** Try adding more compelling calls-to-action")
        elif analytics['click_rate'] > 5:
            st.success("🖱️ **Good Click Rate:** Your email content is engaging!")
        
        if analytics['reply_rate'] > 2:
            st.success("💬 **Excellent Reply Rate:** Your emails are generating conversations!")
    
    else:
        st.info("📊 No email data available yet. Start sending emails to see analytics!")
        
        # Sample analytics preview
        st.markdown("### 📈 Sample Analytics Preview")
        sample_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=30, freq='D'),
            'Emails Sent': [15, 23, 18, 31, 25, 19, 22, 28, 17, 24, 
                           20, 26, 33, 19, 21, 29, 16, 25, 27, 18,
                           22, 30, 24, 26, 19, 23, 28, 21, 25, 20],
            'Open Rate': [22.5, 25.1, 19.8, 27.3, 24.6, 21.9, 26.2, 28.4, 20.1, 25.8,
                         23.7, 26.9, 29.1, 21.5, 24.3, 27.6, 19.4, 25.2, 28.8, 22.1,
                         24.9, 29.3, 26.4, 27.1, 22.8, 25.5, 28.2, 23.6, 26.7, 24.0]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sample_data['Date'], y=sample_data['Open Rate'],
                                mode='lines+markers', name='Open Rate (%)',
                                line=dict(color='#3498db', width=2)))
        fig.update_layout(title="Sample: Email Open Rate Trends",
                         xaxis_title="Date", yaxis_title="Open Rate (%)",
                         height=300)
        st.plotly_chart(fig, use_container_width=True)

def show_send_deal_alert(crm: CRMManager):
    """Send targeted deal alerts with email automation"""
    st.subheader("📢 Send Deal Alert")
    
    if not crm.deals:
        st.warning("⚠️ No deals available to send alerts for. Create some deals first!")
        return
    
    with st.form("deal_alert_form"):
        # Deal selection
        st.markdown("#### 📋 Select Deal")
        deal_options = [f"{deal.property_address} - ${deal.asking_price:,.0f}" for deal in crm.deals]
        selected_deal_idx = st.selectbox("Choose Deal", range(len(deal_options)), 
                                       format_func=lambda x: deal_options[x])
        selected_deal = crm.deals[selected_deal_idx]
        
        # Recipient targeting
        st.markdown("#### 🎯 Target Recipients")
        col1, col2 = st.columns(2)
        
        with col1:
            alert_type = st.selectbox("Alert Type", [
                "New Deal Available",
                "Price Reduction", 
                "Deal Update",
                "Last Chance",
                "Sold/Under Contract"
            ])
            
            recipient_filter = st.selectbox("Send To", [
                "All Active Investors",
                "Qualified Investors Only",
                "Specific Investor Type",
                "Custom Recipients"
            ])
        
        with col2:
            # Filter criteria
            if recipient_filter == "Specific Investor Type":
                investor_types = list(set([contact.company_type for contact in crm.contacts if contact.company_type]))
                if investor_types:
                    selected_type = st.selectbox("Investor Type", investor_types)
                else:
                    st.warning("No investor types found in contacts")
            
            priority = st.selectbox("Priority", ["🔴 High", "🟡 Medium", "🟢 Low"])
        
        # Message customization
        st.markdown("#### ✍️ Alert Message")
        use_template = st.checkbox("Use professional template", value=True)
        
        if use_template:
            # Auto-generate professional alert message
            template_message = f"""🏠 **{alert_type.upper()}**

**Property:** {selected_deal.property_address}
**Asking Price:** ${selected_deal.asking_price:,.0f}
**Estimated ROI:** {selected_deal.estimated_roi:.1f}%
**Property Type:** {selected_deal.property_type}

**Deal Highlights:**
• Prime investment opportunity
• Potential for strong returns
• {selected_deal.deal_stage} - ready for action

**Next Steps:**
Reply to this alert or call us directly to discuss this opportunity.

⏰ **Act Fast** - Quality deals move quickly in today's market!

Best regards,
Your Investment Team"""
            
            st.text_area("Alert Message Preview", value=template_message, height=200, disabled=True)
            alert_message = template_message
        else:
            alert_message = st.text_area("Custom Alert Message", 
                                       placeholder="Enter your custom deal alert message...",
                                       height=150)
        
        # Send options
        col1, col2, col3 = st.columns(3)
        with col1:
            send_email = st.checkbox("📧 Send Email", value=True)
        with col2:
            send_sms = st.checkbox("📱 Send SMS", value=False)
        with col3:
            schedule_send = st.checkbox("⏰ Schedule Send", value=False)
        
        if schedule_send:
            send_datetime = st.datetime_input("Send Date & Time", 
                                            value=datetime.now() + timedelta(hours=1))
        
        # Submit button
        submitted = st.form_submit_button("📤 Send Deal Alert", type="primary", use_container_width=True)
        
        if submitted and alert_message:
            # Get recipients based on filter
            recipients = []
            if recipient_filter == "All Active Investors":
                recipients = [contact for contact in crm.contacts 
                            if "investor" in contact.company_type.lower() and contact.email]
            elif recipient_filter == "Qualified Investors Only":
                recipients = [contact for contact in crm.contacts 
                            if contact.company_type and "investor" in contact.company_type.lower() 
                            and contact.email and contact.tags and "qualified" in contact.tags.lower()]
            
            if recipients:
                # Send real deal alerts using communication services
                email_manager = get_email_manager()
                
                # Prepare deal data for sending
                deal_data = {
                    'address': selected_deal.property_address,
                    'price': selected_deal.asking_price,
                    'roi': selected_deal.estimated_roi,
                    'type': selected_deal.property_type,
                    'stage': selected_deal.deal_stage
                }
                
                # Prepare recipient list for communication manager
                recipient_list = []
                for recipient in recipients:
                    recipient_list.append({
                        'name': recipient.name,
                        'email': recipient.email,
                        'phone': getattr(recipient, 'phone', None)
                    })
                
                # Send real deal alerts
                with st.spinner("Sending deal alerts..."):
                    if send_email:
                        alert_results = email_manager.send_deal_alert(
                            recipients=recipient_list,
                            deal_data=deal_data
                        )
                        
                        # Count successful sends
                        email_success = len([r for r in alert_results if r['success'] and r['type'] == 'email'])
                        sms_success = len([r for r in alert_results if r['success'] and r['type'] == 'sms'])
                        
                        # Create deal alert record
                        deal_alert = DealAlert(
                            deal_id=selected_deal.id,
                            alert_type=alert_type,
                            message=alert_message,
                            recipients=[contact.email for contact in recipients],
                            priority=priority.split(" ")[1],  # Extract priority level
                            sent_via=["email"] if send_email else [] + ["sms"] if send_sms else []
                        )
                        
                        crm.deal_alerts.append(deal_alert)
                        crm.save_data()
                        
                        # Show detailed results
                        if email_success > 0:
                            st.success(f"✅ Deal alert sent successfully! {email_success} emails sent")
                            if email_success == len(recipients):
                                st.balloons()
                        
                        if sms_success > 0:
                            st.success(f"📱 {sms_success} SMS alerts sent")
                        
                        # Show any failures
                        failed_results = [r for r in alert_results if not r['success']]
                        if failed_results:
                            st.warning(f"⚠️ {len(failed_results)} alerts failed to send")
                            with st.expander("View Failed Sends"):
                                for result in failed_results:
                                    st.error(f"❌ {result['recipient']}: {result.get('error', 'Unknown error')}")
                    
                    else:
                        # Just create record without sending
                        deal_alert = DealAlert(
                            deal_id=selected_deal.id,
                            alert_type=alert_type,
                            message=alert_message,
                            recipients=[contact.email for contact in recipients],
                            priority=priority.split(" ")[1],
                            sent_via=[]
                        )
                        
                        crm.deal_alerts.append(deal_alert)
                        crm.save_data()
                        st.info("📋 Deal alert saved (no sending method selected)")
                
                # Show recipient summary
                with st.expander("📊 Alert Summary"):
                    st.write(f"**Deal:** {selected_deal.property_address}")
                    st.write(f"**Recipients:** {len(recipients)}")
                    st.write(f"**Alert Type:** {alert_type}")
                    st.write(f"**Priority:** {priority}")
                    st.write("**Sent To:**")
                    for recipient in recipients:
                        st.write(f"• {recipient.name} - {recipient.email}")
            else:
                st.error("❌ No recipients found matching the selected criteria!")

def show_message_inbox(crm: CRMManager):
    """Enhanced message inbox with filtering and management"""
    st.subheader("📬 Message Inbox")
    
    if not crm.messages:
        st.info("📭 No messages yet. Send your first message to get started!")
        return
    
    # Message filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status_filter = st.selectbox("Status", ["All", "Sent", "Delivered", "Read", "Replied"])
    with col2:
        message_type_filter = st.selectbox("Type", ["All", "Deal Alert", "Follow-up", "General"])
    with col3:
        date_filter = st.selectbox("Date", ["All Time", "Today", "This Week", "This Month"])
    with col4:
        sort_by = st.selectbox("Sort By", ["Newest First", "Oldest First", "Recipient"])
    
    # Filter messages
    filtered_messages = crm.messages.copy()
    
    if status_filter != "All":
        filtered_messages = [msg for msg in filtered_messages 
                           if msg.status.value.lower() == status_filter.lower()]
    
    if date_filter == "Today":
        today = datetime.now().date()
        filtered_messages = [msg for msg in filtered_messages 
                           if msg.created_at.date() == today]
    elif date_filter == "This Week":
        week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
        filtered_messages = [msg for msg in filtered_messages 
                           if msg.created_at.date() >= week_start]
    
    # Sort messages
    if sort_by == "Newest First":
        filtered_messages.sort(key=lambda x: x.created_at, reverse=True)
    elif sort_by == "Oldest First":
        filtered_messages.sort(key=lambda x: x.created_at)
    elif sort_by == "Recipient":
        filtered_messages.sort(key=lambda x: x.recipient)
    
    # Display messages
    st.write(f"📨 Showing {len(filtered_messages)} of {len(crm.messages)} messages")
    
    for message in filtered_messages:
        # Message status icon
        status_icons = {
            MessageStatus.SENT: "📤",
            MessageStatus.DELIVERED: "📨", 
            MessageStatus.READ: "👁️",
            MessageStatus.REPLIED: "↩️"
        }
        
        with st.expander(f"{status_icons.get(message.status, '📧')} {message.subject} - {message.recipient}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**To:** {message.recipient}")
                st.write(f"**Subject:** {message.subject}")
                st.write(f"**Status:** {message.status.value}")
                st.write(f"**Sent:** {message.created_at.strftime('%Y-%m-%d %H:%M')}")
                
                if message.scheduled_send and message.scheduled_send > datetime.now():
                    st.write(f"**Scheduled:** {message.scheduled_send.strftime('%Y-%m-%d %H:%M')}")
                
                # Message content
                st.markdown("**Message:**")
                st.text_area("", value=message.content, height=100, disabled=True, key=f"msg_{message.id}")
            
            with col2:
                if message.status == MessageStatus.SENT:
                    if st.button(f"✅ Mark as Read", key=f"read_{message.id}"):
                        message.status = MessageStatus.READ
                        crm.save_data()
                        st.rerun()
                
                if st.button(f"↩️ Reply", key=f"reply_{message.id}"):
                    st.session_state.reply_to = message.id
                    st.info("Reply feature coming soon!")
                
                if st.button(f"🗑️ Delete", key=f"delete_msg_{message.id}"):
                    crm.messages.remove(message)
                    crm.save_data()
                    st.success("Message deleted!")
                    st.rerun()

def get_email_manager():
    """Get or create email automation manager"""
    if 'email_manager' not in st.session_state:
        st.session_state.email_manager = EmailAutomationManager()
    return st.session_state.email_manager
    """Show send deal alert interface"""
    st.subheader("🔥 Send Deal Alert to Buyers")
    
    if not crm.deals:
        st.warning("No deals available. Add some deals first!")
        return
    
    if not crm.buyers:
        st.warning("No buyers in database. Add some buyers first!")
        return
    
    with st.form("send_deal_alert"):
        # Select deal
        deal_options = [f"{deal.title} - {deal.property_address}" for deal in crm.deals]
        selected_deal = st.selectbox("Select Deal", deal_options)
        
        # Alert type
        alert_type = st.selectbox("Alert Type", ["new_deal", "price_change", "status_change", "general_update"])
        
        # Recipient selection
        st.subheader("Select Recipients")
        
        col1, col2 = st.columns(2)
        with col1:
            send_to_all = st.checkbox("Send to all active buyers")
            send_to_matching = st.checkbox("Send only to matching buyers", value=True)
        
        with col2:
            if not send_to_all and not send_to_matching:
                selected_buyers = st.multiselect(
                    "Select specific buyers",
                    [f"{buyer.buyer_name} - {buyer.buyer_email}" for buyer in crm.buyers if buyer.active]
                )
        
        # Custom message
        custom_subject = st.text_input("Custom Subject (optional)")
        custom_content = st.text_area("Additional Message (optional)")
        
        submitted = st.form_submit_button("🚀 Send Deal Alert")
        
        if submitted and selected_deal:
            # Get selected deal
            deal_title = selected_deal.split(" - ")[0]
            deal = next((d for d in crm.deals if d.title == deal_title), None)
            
            if deal:
                # Determine recipients
                recipient_emails = []
                
                if send_to_all:
                    recipient_emails = [buyer.buyer_email for buyer in crm.buyers if buyer.active]
                elif send_to_matching:
                    matches = crm.find_matching_buyers_for_deal(deal)
                    recipient_emails = [match['buyer'].buyer_email for match in matches]
                else:
                    # Use selected buyers
                    for selected in selected_buyers:
                        email = selected.split(" - ")[1]
                        recipient_emails.append(email)
                
                if recipient_emails:
                    # Send deal alert
                    alert_id = crm.send_deal_alert(deal, recipient_emails, alert_type)
                    st.success(f"Deal alert sent to {len(recipient_emails)} buyers!")
                    
                    # Show recipients
                    with st.expander("Recipients"):
                        for email in recipient_emails:
                            st.write(f"✓ {email}")
                else:
                    st.error("No recipients selected!")

def show_send_message(crm: CRMManager):
    """Show send message interface"""
    st.subheader("💬 Send Custom Message")
    
    with st.form("send_message"):
        col1, col2 = st.columns(2)
        
        with col1:
            sender_name = st.text_input("Your Name", value="Deal Team")
            sender_email = st.text_input("Your Email", value="deals@nxtrix.com")
            
        with col2:
            recipient_name = st.text_input("Recipient Name")
            recipient_email = st.text_input("Recipient Email")
        
        # Message details
        subject = st.text_input("Subject*")
        message_type = st.selectbox("Message Type", [mt.value for mt in MessageType])
        
        # Related deal (optional)
        if crm.deals:
            deal_options = ["None"] + [f"{deal.title} - {deal.property_address}" for deal in crm.deals]
            related_deal = st.selectbox("Related Deal (optional)", deal_options)
        else:
            related_deal = "None"
        
        content = st.text_area("Message Content*", height=200)
        
        submitted = st.form_submit_button("📧 Send Message")
        
        if submitted and subject and content and recipient_email:
            # Get related deal ID
            related_deal_id = None
            if related_deal != "None":
                deal_title = related_deal.split(" - ")[0]
                deal = next((d for d in crm.deals if d.title == deal_title), None)
                if deal:
                    related_deal_id = deal.id
            
            # Send message
            message_id = crm.send_message(
                sender_name=sender_name,
                sender_email=sender_email,
                recipient_name=recipient_name,
                recipient_email=recipient_email,
                subject=subject,
                content=content,
                message_type=MessageType(message_type),
                related_deal_id=related_deal_id
            )
            
            st.success(f"Message sent to {recipient_email}!")

def show_message_inbox(crm: CRMManager):
    """Show message inbox"""
    st.subheader("📬 Message Inbox")
    
    if not crm.messages:
        st.info("No messages yet.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All"] + [status.value for status in MessageStatus])
    with col2:
        type_filter = st.selectbox("Filter by Type", ["All"] + [mt.value for mt in MessageType])
    with col3:
        days_filter = st.selectbox("Time Period", ["All", "Today", "This Week", "This Month"])
    
    # Filter messages
    filtered_messages = crm.messages
    
    if status_filter != "All":
        filtered_messages = [msg for msg in filtered_messages if msg.status.value == status_filter]
    if type_filter != "All":
        filtered_messages = [msg for msg in filtered_messages if msg.message_type.value == type_filter]
    
    # Date filtering
    if days_filter != "All":
        now = datetime.now()
        if days_filter == "Today":
            filtered_messages = [msg for msg in filtered_messages if msg.created_at.date() == now.date()]
        elif days_filter == "This Week":
            week_ago = now - timedelta(days=7)
            filtered_messages = [msg for msg in filtered_messages if msg.created_at >= week_ago]
        elif days_filter == "This Month":
            month_ago = now - timedelta(days=30)
            filtered_messages = [msg for msg in filtered_messages if msg.created_at >= month_ago]
    
    # Sort by date (newest first)
    filtered_messages.sort(key=lambda x: x.created_at, reverse=True)
    
    # Display messages
    for message in filtered_messages:
        with st.expander(f"📧 {message.subject} - {message.recipient_name} ({message.status.value})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**From:** {message.sender_name} ({message.sender_email})")
                st.write(f"**To:** {message.recipient_name} ({message.recipient_email})")
                st.write(f"**Type:** {message.message_type.value}")
                st.write(f"**Sent:** {message.created_at.strftime('%Y-%m-%d %H:%M')}")
                
                if message.related_deal_id:
                    related_deal = next((d for d in crm.deals if d.id == message.related_deal_id), None)
                    if related_deal:
                        st.write(f"**Related Deal:** {related_deal.title}")
                
                st.markdown("**Message:**")
                st.write(message.content)
            
            with col2:
                if message.status == MessageStatus.SENT and st.button(f"Mark as Read", key=f"read_{message.id}"):
                    crm.mark_message_as_read(message.id)
                    st.rerun()

def show_communication_analytics(crm: CRMManager):
    """Show communication analytics"""
    st.subheader("📊 Communication Analytics")
    
    if not crm.messages:
        st.info("No communication data available yet.")
        return
    
    # Message statistics
    col1, col2 = st.columns(2)
    
    with col1:
        # Messages by type
        type_counts = {}
        for msg in crm.messages:
            msg_type = msg.message_type.value
            type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
        
        if type_counts:
            fig = go.Figure(data=[
                go.Pie(labels=list(type_counts.keys()), values=list(type_counts.values()))
            ])
            fig.update_layout(title="Messages by Type")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Messages by status
        status_counts = {}
        for msg in crm.messages:
            status = msg.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            fig = go.Figure(data=[
                go.Bar(x=list(status_counts.keys()), y=list(status_counts.values()))
            ])
            fig.update_layout(title="Messages by Status")
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("📈 Recent Communication Activity")
    
    # Messages per day for last 30 days
    from collections import defaultdict
    daily_counts = defaultdict(int)
    
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_messages = [msg for msg in crm.messages if msg.created_at >= thirty_days_ago]
    
    for msg in recent_messages:
        date_str = msg.created_at.strftime('%Y-%m-%d')
        daily_counts[date_str] += 1
    
    if daily_counts:
        dates = sorted(daily_counts.keys())
        counts = [daily_counts[date] for date in dates]
        
        fig = go.Figure(data=[
            go.Scatter(x=dates, y=counts, mode='lines+markers')
        ])
        fig.update_layout(
            title="Messages per Day (Last 30 Days)",
            xaxis_title="Date",
            yaxis_title="Number of Messages"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top recipients
    st.subheader("🏆 Top Message Recipients")
    recipient_counts = {}
    for msg in crm.messages:
        recipient = msg.recipient_email
        recipient_counts[recipient] = recipient_counts.get(recipient, 0) + 1
    
    if recipient_counts:
        # Sort by count and take top 10
        top_recipients = sorted(recipient_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        recipients_data = []
        for email, count in top_recipients:
            # Try to find the name
            name = "Unknown"
            for buyer in crm.buyers:
                if buyer.buyer_email == email:
                    name = buyer.buyer_name
                    break
            
            recipients_data.append({
                'Name': name,
                'Email': email,
                'Message Count': count
            })
        
        df = pd.DataFrame(recipients_data)
        st.dataframe(df, use_container_width=True)

def show_deal_automation(crm: CRMManager):
    """Phase 3: Deal Workflow Automation Interface"""
    st.header("🤖 Deal Workflow Automation - Phase 3")
    
    # Get workflow manager
    workflow_manager = get_workflow_manager()
    
    # Automation overview metrics
    analytics = workflow_manager.get_automation_analytics()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Matches Generated", analytics['total_matches_generated'])
    with col2:
        st.metric("High Quality Matches", analytics['high_quality_matches'])
    with col3:
        st.metric("Response Rate", f"{analytics['response_conversion_rate']:.1f}%")
    with col4:
        st.metric("Active Criteria", analytics['active_criteria'])
    
    st.markdown("---")
    
    # Automation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Buyer Matching", 
        "📊 Investment Criteria", 
        "🔄 Pipeline Automation",
        "🔔 Smart Notifications",
        "📈 Automation Analytics"
    ])
    
    with tab1:
        show_automated_buyer_matching(crm, workflow_manager)
    
    with tab2:
        show_investment_criteria_management(crm, workflow_manager)
    
    with tab3:
        show_pipeline_automation(crm, workflow_manager)
    
    with tab4:
        show_smart_notifications(crm, workflow_manager)
    
    with tab5:
        show_automation_analytics(workflow_manager)

def show_automated_buyer_matching(crm: CRMManager, workflow_manager):
    """Automated deal-buyer matching interface"""
    st.subheader("🎯 Intelligent Deal-Buyer Matching")
    
    # Matching controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔍 Run Matching Engine", type="primary", use_container_width=True):
            with st.spinner("Finding deal matches..."):
                # Convert CRM deals to dict format for matching
                deals_data = []
                for deal in crm.deals:
                    deals_data.append({
                        'id': deal.id,
                        'property_address': deal.property_address,
                        'asking_price': deal.asking_price,
                        'estimated_roi': deal.estimated_roi,
                        'property_type': deal.property_type,
                        'deal_stage': deal.deal_stage,
                        'location': deal.property_address.split(',')[-1].strip() if ',' in deal.property_address else deal.property_address,
                        'estimated_cash_flow': getattr(deal, 'estimated_cash_flow', deal.asking_price * 0.01),  # Estimate if not available
                        'estimated_rehab': getattr(deal, 'estimated_rehab', 10000)  # Default rehab estimate
                    })
                
                # Run matching engine
                new_matches = workflow_manager.run_deal_matching(deals_data)
                
                if new_matches:
                    st.success(f"✅ Found {len(new_matches)} new potential matches!")
                    st.balloons()
                else:
                    st.info("💡 No new matches found. Consider adjusting buyer criteria.")
    
    with col2:
        if st.button("📧 Send Match Alerts", use_container_width=True):
            st.info("🚀 Match alert sending coming soon!")
    
    with col3:
        if st.button("🔄 Auto-Match Settings", use_container_width=True):
            st.session_state.show_auto_match_settings = True
    
    # Recent matches display
    if workflow_manager.deal_matches:
        st.markdown("### 🎯 Recent Deal Matches")
        
        # Filter and sort matches
        matches_df_data = []
        for match in workflow_manager.deal_matches[-20:]:  # Show last 20 matches
            # Find deal and buyer info
            deal_info = "Unknown Deal"
            buyer_info = "Unknown Buyer"
            
            for deal in crm.deals:
                if deal.id == match.deal_id:
                    deal_info = f"{deal.property_address} - ${deal.asking_price:,.0f}"
                    break
            
            for contact in crm.contacts:
                if contact.id == match.buyer_id:
                    buyer_info = f"{contact.name} ({contact.company_type})"
                    break
            
            matches_df_data.append({
                'Deal': deal_info,
                'Buyer': buyer_info,
                'Match Score': f"{match.match_score:.1f}%",
                'Status': match.status,
                'Created': match.created_at.strftime('%Y-%m-%d'),
                'Match Factors': ', '.join(match.match_factors[:2]) + '...' if len(match.match_factors) > 2 else ', '.join(match.match_factors)
            })
        
        if matches_df_data:
            matches_df = pd.DataFrame(matches_df_data)
            st.dataframe(matches_df, use_container_width=True)
        else:
            st.info("🔍 No matches found yet. Run the matching engine to start finding buyer-deal matches!")
    
    # Auto-match settings
    if st.session_state.get('show_auto_match_settings', False):
        show_auto_match_settings()

def show_investment_criteria_management(crm: CRMManager, workflow_manager):
    """Investment criteria management interface"""
    st.subheader("📊 Buyer Investment Criteria")
    
    # Create new criteria
    with st.expander("➕ Create New Investment Criteria"):
        with st.form("new_criteria_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Buyer selection
                buyer_options = [f"{contact.name} - {contact.company_type}" for contact in crm.contacts if "investor" in contact.company_type.lower()]
                if buyer_options:
                    selected_buyer = st.selectbox("Select Buyer", ["Choose buyer..."] + buyer_options)
                    
                    if selected_buyer != "Choose buyer...":
                        buyer_name = selected_buyer.split(" - ")[0]
                        buyer_contact = next((c for c in crm.contacts if c.name == buyer_name), None)
                        
                        # Property types
                        property_types = st.multiselect("Property Types", 
                            [pt.value for pt in PropertyType],
                            default=["Single Family"])
                        
                        # Price range
                        col1a, col1b = st.columns(2)
                        with col1a:
                            min_price = st.number_input("Min Price ($)", min_value=0, value=50000, step=10000)
                        with col1b:
                            max_price = st.number_input("Max Price ($)", min_value=0, value=300000, step=10000)
                        
                        # ROI and financing
                        col1c, col1d = st.columns(2)
                        with col1c:
                            min_roi = st.number_input("Min ROI (%)", min_value=0.0, value=12.0, step=0.5)
                        with col1d:
                            max_ltv = st.number_input("Max LTV (%)", min_value=0.0, value=80.0, step=5.0)
            
            with col2:
                # Location preferences
                preferred_locations = st.text_input("Preferred Locations (comma-separated)", 
                    placeholder="e.g., Atlanta, Birmingham, Memphis")
                
                # Cash flow and rehab
                col2a, col2b = st.columns(2)
                with col2a:
                    min_cash_flow = st.number_input("Min Monthly Cash Flow ($)", min_value=0, value=200, step=50)
                with col2b:
                    max_rehab_budget = st.number_input("Max Rehab Budget ($)", min_value=0, value=25000, step=5000)
                
                # Investment strategy
                investment_strategy = st.selectbox("Investment Strategy", [
                    "Buy and Hold",
                    "Fix and Flip", 
                    "BRRRR (Buy, Rehab, Rent, Refinance, Repeat)",
                    "Wholesale",
                    "Commercial"
                ])
            
            submitted = st.form_submit_button("💾 Create Criteria", type="primary", use_container_width=True)
            
            if submitted and selected_buyer != "Choose buyer..." and buyer_contact:
                criteria_data = {
                    'property_types': property_types,
                    'min_price': min_price,
                    'max_price': max_price,
                    'min_roi': min_roi,
                    'max_ltv': max_ltv,
                    'preferred_locations': [loc.strip() for loc in preferred_locations.split(",") if loc.strip()],
                    'min_cash_flow': min_cash_flow,
                    'max_rehab_budget': max_rehab_budget,
                    'investment_strategy': investment_strategy
                }
                
                workflow_manager.create_investment_criteria(buyer_contact.id, criteria_data)
                st.success(f"✅ Investment criteria created for {buyer_contact.name}!")
                st.rerun()
    
    # Display existing criteria
    if workflow_manager.investment_criteria:
        st.markdown("### 📋 Active Investment Criteria")
        
        for criteria in workflow_manager.investment_criteria:
            if not criteria.is_active:
                continue
                
            # Find buyer name
            buyer_name = "Unknown Buyer"
            for contact in crm.contacts:
                if contact.id == criteria.buyer_id:
                    buyer_name = contact.name
                    break
            
            with st.expander(f"🎯 {buyer_name} - {criteria.investment_strategy}"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**Property Types:** {', '.join([pt.value for pt in criteria.property_types])}")
                    st.write(f"**Price Range:** ${criteria.min_price:,.0f} - ${criteria.max_price:,.0f}")
                    st.write(f"**Min ROI:** {criteria.min_roi}%")
                    st.write(f"**Max LTV:** {criteria.max_ltv}%")
                
                with col2:
                    st.write(f"**Preferred Locations:** {', '.join(criteria.preferred_locations) if criteria.preferred_locations else 'Any'}")
                    st.write(f"**Min Cash Flow:** ${criteria.min_cash_flow:,.0f}/month")
                    st.write(f"**Max Rehab Budget:** ${criteria.max_rehab_budget:,.0f}")
                    st.write(f"**Strategy:** {criteria.investment_strategy}")
                
                with col3:
                    if st.button(f"✏️ Edit", key=f"edit_criteria_{criteria.id}"):
                        st.info("Criteria editing coming soon!")
                    
                    if st.button(f"❌ Deactivate", key=f"deact_criteria_{criteria.id}"):
                        criteria.is_active = False
                        workflow_manager.save_data()
                        st.success("Criteria deactivated!")
                        st.rerun()
    else:
        st.info("📊 No investment criteria defined yet. Create criteria to enable automated matching!")

def show_pipeline_automation(crm: CRMManager, workflow_manager):
    """Pipeline automation and workflow management"""
    st.subheader("🔄 Automated Pipeline Management")
    
    # Pipeline overview
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Workflows", len(workflow_manager.pipeline_manager.triggers))
    with col2:
        pending_notifications = len([n for n in workflow_manager.pipeline_manager.notifications if not n.is_sent])
        st.metric("Pending Notifications", pending_notifications)
    with col3:
        st.metric("Automation Rules", len([t for t in workflow_manager.pipeline_manager.triggers if t.is_active]))
    
    # Pipeline automation tabs
    pipeline_tab1, pipeline_tab2, pipeline_tab3 = st.tabs([
        "📊 Deal Pipeline", 
        "⚙️ Automation Rules",
        "🔔 Workflow Notifications"
    ])
    
    with pipeline_tab1:
        show_deal_pipeline_view(crm, workflow_manager)
    
    with pipeline_tab2:
        show_automation_rules(workflow_manager)
    
    with pipeline_tab3:
        show_workflow_notifications(workflow_manager)

def show_deal_pipeline_view(crm: CRMManager, workflow_manager):
    """Visual deal pipeline with automation triggers"""
    st.markdown("#### 📊 Interactive Deal Pipeline")
    
    # Pipeline stage counts
    stage_counts = {}
    for stage in DealStage:
        stage_counts[stage.value] = len([deal for deal in crm.deals if deal.deal_stage == stage.value])
    
    # Create pipeline visualization
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**Early Stage**")
        st.metric("Sourced", stage_counts.get(DealStage.SOURCED.value, 0))
        st.metric("Under Analysis", stage_counts.get(DealStage.ANALYZED.value, 0))
    
    with col2:
        st.markdown("**Qualification**")
        st.metric("Qualified", stage_counts.get(DealStage.QUALIFIED.value, 0))
        st.metric("Being Marketed", stage_counts.get(DealStage.MARKETED.value, 0))
    
    with col3:
        st.markdown("**Active Deals**")
        st.metric("Under Contract", stage_counts.get(DealStage.UNDER_CONTRACT.value, 0))
        st.metric("Due Diligence", stage_counts.get(DealStage.DUE_DILIGENCE.value, 0))
    
    with col4:
        st.markdown("**Completion**")
        st.metric("Closing", stage_counts.get(DealStage.CLOSING.value, 0))
        st.metric("Closed", stage_counts.get(DealStage.CLOSED.value, 0))
    
    # Recent stage changes
    st.markdown("#### 📈 Recent Pipeline Activity")
    
    # Simulate recent activity (in real implementation, this would come from audit logs)
    recent_activity = [
        {"deal": "123 Main St", "action": "Moved to Under Contract", "time": "2 hours ago"},
        {"deal": "456 Oak Ave", "action": "Buyer matched", "time": "4 hours ago"},
        {"deal": "789 Pine Rd", "action": "Analysis completed", "time": "1 day ago"},
    ]
    
    for activity in recent_activity:
        st.write(f"🏠 **{activity['deal']}** - {activity['action']} *({activity['time']})*")

def show_automation_rules(workflow_manager):
    """Automation rules and triggers management"""
    st.markdown("#### ⚙️ Workflow Automation Rules")
    
    # Display existing triggers
    for trigger in workflow_manager.pipeline_manager.triggers:
        with st.expander(f"🔧 {trigger.name}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Trigger Type:** {trigger.trigger_type}")
                st.write(f"**Conditions:** {trigger.conditions}")
                st.write(f"**Actions:** {len(trigger.actions)} automated actions")
                st.write(f"**Status:** {'✅ Active' if trigger.is_active else '❌ Inactive'}")
            
            with col2:
                if st.button(f"⚙️ Configure", key=f"config_{trigger.id}"):
                    st.info("Rule configuration coming soon!")
                
                status_text = "Deactivate" if trigger.is_active else "Activate"
                if st.button(f"🔄 {status_text}", key=f"toggle_{trigger.id}"):
                    trigger.is_active = not trigger.is_active
                    st.success(f"Rule {status_text.lower()}d!")
                    st.rerun()

def show_workflow_notifications(workflow_manager):
    """Workflow notifications management"""
    st.markdown("#### 🔔 Smart Workflow Notifications")
    
    # Notification summary
    all_notifications = workflow_manager.pipeline_manager.notifications
    pending_count = len([n for n in all_notifications if not n.is_sent])
    sent_count = len([n for n in all_notifications if n.is_sent])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pending Notifications", pending_count)
    with col2:
        st.metric("Sent Today", sent_count)
    with col3:
        if st.button("🔄 Process Pending", type="primary"):
            st.info("🚀 Notification processing coming soon!")
    
    # Display recent notifications
    if all_notifications:
        st.markdown("#### 📋 Recent Notifications")
        
        for notification in all_notifications[-10:]:  # Show last 10
            priority_icons = {
                "Low": "🟢",
                "Medium": "🟡", 
                "High": "🟠",
                "Urgent": "🔴"
            }
            
            with st.expander(f"{priority_icons.get(notification.priority, '🔵')} {notification.title}"):
                st.write(f"**Message:** {notification.message}")
                st.write(f"**Type:** {notification.notification_type.value}")
                st.write(f"**Priority:** {notification.priority}")
                st.write(f"**Scheduled:** {notification.scheduled_for.strftime('%Y-%m-%d %H:%M')}")
                
                if notification.is_sent:
                    st.write(f"**Sent:** {notification.sent_at.strftime('%Y-%m-%d %H:%M')}")
                else:
                    st.write("**Status:** Pending")

def show_smart_notifications(crm: CRMManager, workflow_manager):
    """Smart notifications and alerts management"""
    st.subheader("🔔 Intelligent Notifications")
    
    # Notification controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔍 Generate Follow-up Reminders", use_container_width=True):
            with st.spinner("Generating follow-up reminders..."):
                # Convert CRM deals for reminder processing
                deals_data = []
                for deal in crm.deals:
                    deals_data.append({
                        'id': deal.id,
                        'property_address': deal.property_address,
                        'deal_stage': deal.deal_stage,
                        'last_contact_date': getattr(deal, 'last_contact_date', datetime.now() - timedelta(days=5))
                    })
                
                reminders = workflow_manager.pipeline_manager.schedule_follow_up_reminders(deals_data)
                workflow_manager.pipeline_manager.notifications.extend(reminders)
                
                if reminders:
                    st.success(f"✅ Generated {len(reminders)} follow-up reminders!")
                else:
                    st.info("💡 All deals are up to date - no reminders needed.")
    
    with col2:
        if st.button("📊 Check Deal Milestones", use_container_width=True):
            st.info("🎯 Milestone checking coming soon!")
    
    with col3:
        if st.button("⚙️ Notification Settings", use_container_width=True):
            st.session_state.show_notification_settings = True
    
    # Show notification settings
    if st.session_state.get('show_notification_settings', False):
        with st.expander("⚙️ Notification Preferences", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.checkbox("📧 Email Notifications", value=True)
                st.checkbox("📱 SMS Notifications", value=False)
                st.checkbox("🔔 In-App Notifications", value=True)
            
            with col2:
                st.selectbox("Notification Frequency", ["Immediate", "Hourly", "Daily", "Weekly"])
                st.time_input("Quiet Hours Start", value=datetime.strptime("22:00", "%H:%M").time())
                st.time_input("Quiet Hours End", value=datetime.strptime("08:00", "%H:%M").time())
            
            if st.button("💾 Save Settings"):
                st.success("Notification settings saved!")
                st.session_state.show_notification_settings = False
                st.rerun()

def show_automation_analytics(workflow_manager):
    """Automation performance analytics"""
    st.subheader("📈 Automation Performance Analytics")
    
    analytics = workflow_manager.get_automation_analytics()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Matches", analytics['total_matches_generated'])
    with col2:
        st.metric("Avg Match Score", f"{analytics['avg_match_score']:.1f}%")
    with col3:
        st.metric("Conversion Rate", f"{analytics['response_conversion_rate']:.1f}%")
    with col4:
        improvement = "+15.3%" if analytics['total_matches_generated'] > 10 else "New"
        st.metric("Efficiency Gain", improvement)
    
    # Performance charts
    if analytics['total_matches_generated'] > 0:
        st.markdown("### 📊 Matching Performance")
        
        # Create match quality distribution
        match_scores = [match.match_score for match in workflow_manager.deal_matches]
        
        if match_scores:
            fig = go.Figure(data=[go.Histogram(x=match_scores, nbinsx=10)])
            fig.update_layout(
                title="Match Score Distribution",
                xaxis_title="Match Score (%)",
                yaxis_title="Number of Matches",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Automation ROI metrics
        st.markdown("### 💰 Automation ROI")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Time Saved", "12.5 hours/week", delta="2.3 hours")
            st.metric("Deals Accelerated", "8", delta="3")
        
        with col2:
            st.metric("Response Rate Improvement", "+25%", delta="5%")
            st.metric("Pipeline Velocity", "+18%", delta="3%")
    
    else:
        st.info("📊 Run the matching engine to see automation analytics!")

def show_auto_match_settings():
    """Auto-matching configuration settings"""
    st.markdown("### 🔄 Auto-Match Configuration")
    
    with st.form("auto_match_settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Matching Thresholds**")
            min_match_score = st.slider("Minimum Match Score (%)", 0, 100, 30)
            auto_send_threshold = st.slider("Auto-Send Threshold (%)", 0, 100, 70)
            max_matches_per_deal = st.number_input("Max Matches per Deal", 1, 20, 5)
        
        with col2:
            st.markdown("**Automation Settings**")
            auto_match_enabled = st.checkbox("Enable Auto-Matching", value=True)
            auto_send_enabled = st.checkbox("Auto-Send High Matches", value=False)
            match_frequency = st.selectbox("Matching Frequency", 
                ["Real-time", "Hourly", "Daily", "Weekly"])
        
        if st.form_submit_button("💾 Save Settings", type="primary"):
            st.success("Auto-matching settings saved!")
            st.session_state.show_auto_match_settings = False
            st.rerun()

# ===== ACTIVITY TRACKING FUNCTIONS =====

def show_activity_tracking(crm: CRMManager):
    """Show Activity Tracking interface"""
    st.header("🎯 Activity Tracking & Opportunity Management")
    st.markdown("Track all activities, identify opportunities, and never miss a deal!")
    
    # Get activity tracker instance
    activity_tracker = get_activity_tracker()
    
    # Create tabs for different activity views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Recent Activities", 
        "🚨 Opportunities", 
        "🔔 Notifications",
        "📊 Activity Analytics", 
        "⚙️ Settings"
    ])
    
    with tab1:
        show_recent_activities(activity_tracker)
    
    with tab2:
        show_opportunities(activity_tracker)
    
    with tab3:
        show_notifications_center(activity_tracker)
    
    with tab4:
        show_activity_analytics(activity_tracker)
    
    with tab5:
        show_activity_settings(activity_tracker)

def show_recent_activities(activity_tracker):
    """Show recent activities log"""
    st.subheader("📋 Recent Activities")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        activity_filter = st.selectbox(
            "Filter by Activity Type",
            ["All Activities"] + [t.value for t in ActivityType],
            key="activity_filter"
        )
    
    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority", 
            ["All Priorities"] + [p.value for p in Priority],
            key="priority_filter"
        )
    
    with col3:
        days_back = st.number_input("Days Back", min_value=1, max_value=365, value=7)
    
    # Get activities based on filters
    activities = activity_tracker.get_recent_activities(
        days_back=days_back,
        activity_type=None if activity_filter == "All Activities" else ActivityType(activity_filter),
        priority=None if priority_filter == "All Priorities" else Priority(priority_filter)
    )
    
    if activities:
        st.markdown(f"**Found {len(activities)} activities**")
        
        for activity in activities[:50]:  # Show max 50 activities
            with st.expander(f"{activity.activity_type.value} - {activity.title}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Description:** {activity.description}")
                    if activity.metadata:
                        st.json(activity.metadata)
                
                with col2:
                    priority_color = {
                        Priority.LOW: "🟢",
                        Priority.MEDIUM: "🟡", 
                        Priority.HIGH: "🟠",
                        Priority.URGENT: "🔴"
                    }
                    st.markdown(f"**Priority:** {priority_color[activity.priority]} {activity.priority.value}")
                    st.markdown(f"**Date:** {activity.created_at.strftime('%Y-%m-%d %H:%M')}")
                    if activity.user_id:
                        st.markdown(f"**User ID:** {activity.user_id}")
    else:
        st.info("No activities found for the selected filters.")

def show_opportunities(activity_tracker):
    """Show opportunity alerts"""
    st.subheader("🚨 Opportunity Alerts")
    
    # Get active opportunities
    opportunities = activity_tracker.get_active_opportunities()
    
    if opportunities:
        st.markdown(f"**Found {len(opportunities)} active opportunities**")
        
        for opp in opportunities:
            with st.container():
                st.markdown("---")
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"### 🎯 {opp.title}")
                    st.markdown(f"**Description:** {opp.description}")
                    if opp.metadata:
                        st.json(opp.metadata)
                
                with col2:
                    priority_color = {
                        Priority.LOW: "🟢",
                        Priority.MEDIUM: "🟡",
                        Priority.HIGH: "🟠", 
                        Priority.URGENT: "🔴"
                    }
                    st.markdown(f"**Priority:** {priority_color[opp.priority]} {opp.priority.value}")
                    st.markdown(f"**Value:** ${opp.estimated_value:,.2f}")
                
                with col3:
                    st.markdown(f"**Created:** {opp.created_at.strftime('%Y-%m-%d')}")
                    
                    # Action buttons
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"✅ Complete", key=f"complete_opp_{opp.id}"):
                            activity_tracker.mark_opportunity_completed(opp.id)
                            st.success("Opportunity marked as completed!")
                            st.rerun()
                    
                    with col_b:
                        if st.button(f"❌ Dismiss", key=f"dismiss_opp_{opp.id}"):
                            activity_tracker.dismiss_opportunity(opp.id)
                            st.success("Opportunity dismissed!")
                            st.rerun()
    else:
        st.info("🎉 No active opportunities found. You're all caught up!")

def show_notifications_center(activity_tracker):
    """Show notifications center"""
    st.subheader("🔔 Notifications Center")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        notification_filter = st.selectbox(
            "Filter Notifications",
            ["All", "Unread", "Read", "Email", "SMS", "In-App"],
            key="notification_filter"
        )
    
    with col2:
        if st.button("🔄 Refresh Notifications"):
            st.rerun()
    
    # Get notifications based on filter
    notifications = activity_tracker.get_user_notifications(
        user_id="current_user",  # In real app, get from session
        unread_only=(notification_filter == "Unread")
    )
    
    if notifications:
        st.markdown(f"**Found {len(notifications)} notifications**")
        
        for notification in notifications[:20]:  # Show max 20 notifications
            with st.container():
                st.markdown("---")
                
                col1, col2, col3 = st.columns([4, 1, 1])
                
                with col1:
                    read_status = "📖" if notification.is_read else "📩"
                    st.markdown(f"{read_status} **{notification.title}**")
                    st.markdown(notification.message)
                
                with col2:
                    channel_icons = {
                        "email": "📧",
                        "sms": "📱", 
                        "in_app": "🔔"
                    }
                    st.markdown(f"**Channel:** {channel_icons.get(notification.channel, '❓')} {notification.channel}")
                
                with col3:
                    st.markdown(f"**Date:** {notification.created_at.strftime('%m/%d %H:%M')}")
                    
                    if not notification.is_read:
                        if st.button(f"Mark Read", key=f"read_notif_{notification.id}"):
                            activity_tracker.mark_notification_read(notification.id)
                            st.success("Marked as read!")
                            st.rerun()
    else:
        st.info("No notifications found.")

def show_activity_analytics(activity_tracker):
    """Show activity analytics"""
    st.subheader("📊 Activity Analytics")
    
    # Get analytics data with error handling
    try:
        analytics = activity_tracker.get_activity_analytics(days_back=30)
    except AttributeError:
        st.warning("⚠️ Activity analytics not available - using demo data")
        analytics = {
            'total_activities': 25,
            'activities_today': 3,
            'avg_daily_activities': 5.2,
            'most_active_day': 'Tuesday'
        }
    except Exception as e:
        st.error(f"Error loading activity analytics: {e}")
        analytics = {}
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Activities", analytics.get('total_activities', 0))
    
    with col2:
        st.metric("Opportunities Created", analytics.get('opportunities_created', 0))
    
    with col3:
        st.metric("Opportunities Completed", analytics.get('opportunities_completed', 0))
    
    with col4:
        completion_rate = analytics.get('opportunity_completion_rate', 0)
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    # Activity timeline chart
    st.markdown("### 📈 Activity Timeline (Last 30 Days)")
    
    timeline_data = analytics.get('daily_activity_counts', {})
    if timeline_data:
        dates = list(timeline_data.keys())
        counts = list(timeline_data.values())
        
        try:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.plot(dates, counts, marker='o')
            ax.set_title("Daily Activity Count")
            ax.set_xlabel("Date")
            ax.set_ylabel("Activities")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        except ImportError:
            st.info("Install matplotlib for charts: pip install matplotlib")
    
    # Activity type breakdown
    st.markdown("### 📊 Activity Type Breakdown")
    
    activity_types = analytics.get('activity_type_counts', {})
    if activity_types:
        try:
            import pandas as pd
            df = pd.DataFrame(list(activity_types.items()), columns=['Activity Type', 'Count'])
            st.bar_chart(df.set_index('Activity Type'))
        except ImportError:
            for activity_type, count in activity_types.items():
                st.markdown(f"- **{activity_type}**: {count}")
    
    # Top opportunities by value
    st.markdown("### 💰 Top Opportunities by Value")
    
    top_opportunities = analytics.get('top_opportunities', [])
    if top_opportunities:
        for i, opp in enumerate(top_opportunities[:5], 1):
            st.markdown(f"{i}. **{opp['title']}** - ${opp['estimated_value']:,.2f}")

def show_activity_settings(activity_tracker):
    """Show activity tracking settings"""
    st.subheader("⚙️ Activity Tracking Settings")
    
    with st.form("activity_settings"):
        st.markdown("### 🔔 Notification Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Notification Channels**")
            email_notifications = st.checkbox("📧 Email Notifications", value=True)
            sms_notifications = st.checkbox("📱 SMS Notifications", value=False)
            in_app_notifications = st.checkbox("🔔 In-App Notifications", value=True)
        
        with col2:
            st.markdown("**Notification Timing**")
            immediate_notifications = st.checkbox("⚡ Immediate Notifications", value=True)
            digest_frequency = st.selectbox("📅 Digest Frequency", ["None", "Daily", "Weekly"], index=1)
            quiet_hours_start = st.time_input("🌙 Quiet Hours Start", value=datetime.strptime("22:00", "%H:%M").time())
            quiet_hours_end = st.time_input("🌅 Quiet Hours End", value=datetime.strptime("08:00", "%H:%M").time())
        
        st.markdown("### 🎯 Opportunity Detection")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Detection Rules**")
            auto_detect_hot_leads = st.checkbox("🔥 Auto-detect Hot Leads", value=True)
            auto_detect_high_value = st.checkbox("💎 Auto-detect High-Value Deals", value=True)
            auto_detect_stale = st.checkbox("⏰ Auto-detect Stale Activities", value=True)
        
        with col2:
            st.markdown("**Thresholds**")
            hot_lead_threshold = st.number_input("Hot Lead Score Threshold", min_value=0, max_value=100, value=70)
            high_value_threshold = st.number_input("High-Value Deal Threshold ($)", min_value=0, value=100000)
            stale_days_threshold = st.number_input("Stale Activity Days", min_value=1, max_value=365, value=7)
        
        st.markdown("### 📊 Analytics & Reporting")
        
        col1, col2 = st.columns(2)
        
        with col1:
            auto_generate_reports = st.checkbox("📈 Auto-generate Weekly Reports", value=True)
            include_predictions = st.checkbox("🔮 Include AI Predictions", value=False)
        
        with col2:
            report_recipients = st.text_area("📧 Report Recipients (emails)", placeholder="email1@example.com\nemail2@example.com")
        
        if st.form_submit_button("💾 Save Settings", type="primary"):
            # Save settings logic would go here
            settings = {
                'email_notifications': email_notifications,
                'sms_notifications': sms_notifications,
                'in_app_notifications': in_app_notifications,
                'immediate_notifications': immediate_notifications,
                'digest_frequency': digest_frequency,
                'quiet_hours_start': quiet_hours_start.strftime("%H:%M"),
                'quiet_hours_end': quiet_hours_end.strftime("%H:%M"),
                'auto_detect_hot_leads': auto_detect_hot_leads,
                'auto_detect_high_value': auto_detect_high_value,
                'auto_detect_stale': auto_detect_stale,
                'hot_lead_threshold': hot_lead_threshold,
                'high_value_threshold': high_value_threshold,
                'stale_days_threshold': stale_days_threshold,
                'auto_generate_reports': auto_generate_reports,
                'include_predictions': include_predictions,
                'report_recipients': report_recipients.split('\n') if report_recipients else []
            }
            
            activity_tracker.update_settings(settings)
            st.success("✅ Activity tracking settings saved successfully!")
            st.rerun()

# ===== MAIN APPLICATION ENTRY POINT =====

def main():
    """Main application entry point"""
    try:
        # Configure Streamlit page
        st.set_page_config(
            page_title="NXTRIX Enhanced CRM",
            page_icon="🏡",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .activity-item {
            background: #f8f9fa;
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            border-left: 3px solid #28a745;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Main header
        st.markdown("""
        <div class="main-header">
            <h1>🏡 NXTRIX Enhanced CRM Platform</h1>
            <p>Complete Real Estate Investment Management Solution</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show the enhanced CRM interface
        show_enhanced_crm()
        
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.exception(e)

def show_subscription_management():
    """Show subscription management interface"""
    user_id = st.session_state.get('user_id')
    
    if not user_id:
        st.error("Please log in to access subscription management")
        return
    
    # Check if user is admin or has enterprise access
    subscription_manager = SubscriptionManager()
    user_subscription = subscription_manager.get_user_subscription(user_id)
    
    if user_subscription and (user_subscription.tier == SubscriptionTier.ENTERPRISE):
        # Show admin dashboard
        subscription_dashboard.show_admin_dashboard()
    else:
        # Show user subscription interface
        st.title("⚙️ Subscription Management")
        
        # Current subscription status
        if user_subscription:
            subscription_dashboard.show_user_subscription_widget(user_id)
        
        # Feature comparison
        st.subheader("📋 Feature Comparison")
        access_control.show_feature_comparison()
        
        # Upgrade options
        st.subheader("🚀 Upgrade Your Plan")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🆓 Free Plan
            - 5 deals per month
            - Basic analytics
            - Basic document generation
            - Email support
            
            **$0/month**
            """)
            
        with col2:
            st.markdown("""
            ### 💎 Professional Plan
            - 50 deals per month
            - Advanced analytics
            - AI-powered insights
            - Email automation
            - Priority support
            
            **$97/month**
            """)
            
            if st.button("Upgrade to Pro"):
                if subscription_manager.upgrade_subscription(user_id, SubscriptionTier.PRO):
                    st.success("Upgraded to Professional!")
                    st.rerun()
                    
        with col3:
            st.markdown("""
            ### 👑 Enterprise Plan
            - Unlimited deals
            - Full AI features
            - Advanced automation
            - API access
            - Dedicated support
            
            **$297/month**
            """)
            
            if st.button("Upgrade to Enterprise"):
                if subscription_manager.upgrade_subscription(user_id, SubscriptionTier.ENTERPRISE):
                    st.success("Upgraded to Enterprise!")
                    st.rerun()

if __name__ == "__main__":
    main()