"""
Phase 3: Deal Workflow Automation System
Automated buyer matching, pipeline management, and smart notifications
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set
from enum import Enum
import uuid
import json
import sqlite3

class DealStage(Enum):
    """Deal pipeline stages"""
    SOURCED = "Sourced"
    ANALYZED = "Under Analysis"
    QUALIFIED = "Qualified"
    MARKETED = "Being Marketed"
    UNDER_CONTRACT = "Under Contract"
    DUE_DILIGENCE = "Due Diligence"
    CLOSING = "Closing"
    CLOSED = "Closed"
    LOST = "Lost/Dead"

class BuyerStatus(Enum):
    """Buyer qualification status"""
    NEW = "New"
    QUALIFYING = "Qualifying"
    QUALIFIED = "Qualified"
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    CLOSED_BUYER = "Closed Buyer"

class NotificationType(Enum):
    """Types of automated notifications"""
    DEAL_MATCH = "Deal Match"
    DEADLINE_ALERT = "Deadline Alert"
    STATUS_UPDATE = "Status Update"
    MILESTONE_REACHED = "Milestone Reached"
    FOLLOW_UP_REMINDER = "Follow-up Reminder"

class PropertyType(Enum):
    """Property investment types"""
    SINGLE_FAMILY = "Single Family"
    MULTI_FAMILY = "Multi-Family"
    COMMERCIAL = "Commercial"
    LAND = "Land"
    MIXED_USE = "Mixed Use"
    INDUSTRIAL = "Industrial"

@dataclass
class InvestmentCriteria:
    """Buyer's investment criteria for matching"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    buyer_id: str = ""
    property_types: List[PropertyType] = field(default_factory=list)
    min_price: float = 0
    max_price: float = 1000000
    min_roi: float = 0
    max_ltv: float = 80  # Loan to value ratio
    preferred_locations: List[str] = field(default_factory=list)
    max_rehab_budget: float = 50000
    min_cash_flow: float = 0
    investment_strategy: str = "Buy and Hold"  # Buy and Hold, Fix and Flip, etc.
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class DealMatch:
    """Represents a match between deal and buyer"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    deal_id: str = ""
    buyer_id: str = ""
    match_score: float = 0.0  # 0-100 match percentage
    match_factors: List[str] = field(default_factory=list)
    status: str = "Pending"  # Pending, Sent, Viewed, Interested, Declined
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    viewed_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    notes: str = ""

@dataclass
class WorkflowTrigger:
    """Automated workflow trigger"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    trigger_type: str = "stage_change"  # stage_change, time_based, manual
    conditions: Dict[str, Any] = field(default_factory=dict)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class SmartNotification:
    """Smart notification for deal workflow"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    notification_type: NotificationType = NotificationType.DEAL_MATCH
    title: str = ""
    message: str = ""
    deal_id: Optional[str] = None
    buyer_id: Optional[str] = None
    recipient_emails: List[str] = field(default_factory=list)
    scheduled_for: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    is_sent: bool = False
    priority: str = "Medium"  # Low, Medium, High, Urgent
    metadata: Dict[str, Any] = field(default_factory=dict)

class DealMatchingEngine:
    """Intelligent deal matching system"""
    
    def __init__(self):
        self.match_weights = {
            'property_type': 25,
            'price_range': 20,
            'roi_target': 20,
            'location': 15,
            'cash_flow': 10,
            'rehab_budget': 10
        }
    
    def calculate_match_score(self, deal: Dict[str, Any], criteria: InvestmentCriteria) -> float:
        """Calculate match score between deal and buyer criteria"""
        score = 0.0
        match_factors = []
        
        # Property type match
        if hasattr(criteria, 'property_types') and criteria.property_types:
            deal_type = deal.get('property_type', '')
            for prop_type in criteria.property_types:
                if prop_type.value.lower() in deal_type.lower():
                    score += self.match_weights['property_type']
                    match_factors.append(f"Property type match: {prop_type.value}")
                    break
        
        # Price range match
        deal_price = deal.get('asking_price', 0)
        if criteria.min_price <= deal_price <= criteria.max_price:
            score += self.match_weights['price_range']
            match_factors.append(f"Price within range: ${deal_price:,.0f}")
        elif deal_price < criteria.max_price * 1.1:  # 10% tolerance
            score += self.match_weights['price_range'] * 0.5
            match_factors.append(f"Price close to range: ${deal_price:,.0f}")
        
        # ROI match
        deal_roi = deal.get('estimated_roi', 0)
        if deal_roi >= criteria.min_roi:
            roi_score = min(deal_roi / criteria.min_roi, 2.0)  # Cap at 2x bonus
            score += self.match_weights['roi_target'] * min(roi_score, 1.0)
            match_factors.append(f"ROI meets target: {deal_roi:.1f}%")
        
        # Location match
        deal_location = deal.get('location', '').lower()
        if criteria.preferred_locations:
            for location in criteria.preferred_locations:
                if location.lower() in deal_location:
                    score += self.match_weights['location']
                    match_factors.append(f"Preferred location: {location}")
                    break
        
        # Cash flow estimation (simplified)
        estimated_cash_flow = deal.get('estimated_cash_flow', 0)
        if estimated_cash_flow >= criteria.min_cash_flow:
            score += self.match_weights['cash_flow']
            match_factors.append(f"Cash flow target met: ${estimated_cash_flow:,.0f}")
        
        # Rehab budget consideration
        rehab_needed = deal.get('estimated_rehab', 0)
        if rehab_needed <= criteria.max_rehab_budget:
            score += self.match_weights['rehab_budget']
            match_factors.append(f"Rehab within budget: ${rehab_needed:,.0f}")
        
        return min(score, 100.0), match_factors
    
    def find_matches(self, deals: List[Dict[str, Any]], 
                    all_criteria: List[InvestmentCriteria]) -> List[DealMatch]:
        """Find all potential matches between deals and buyers"""
        matches = []
        
        for deal in deals:
            for criteria in all_criteria:
                if not criteria.is_active:
                    continue
                
                score, factors = self.calculate_match_score(deal, criteria)
                
                # Only create matches above threshold
                if score >= 30.0:  # 30% minimum match
                    match = DealMatch(
                        deal_id=deal.get('id', ''),
                        buyer_id=criteria.buyer_id,
                        match_score=score,
                        match_factors=factors,
                        status="Pending"
                    )
                    matches.append(match)
        
        # Sort by match score descending
        matches.sort(key=lambda x: x.match_score, reverse=True)
        return matches

class DealPipelineManager:
    """Manages deal pipeline and automated workflows"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.triggers: List[WorkflowTrigger] = []
        self.notifications: List[SmartNotification] = []
        self.init_database()
        self.setup_default_triggers()
    
    def init_database(self):
        """Initialize workflow database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Workflow triggers table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS workflow_triggers (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        trigger_type TEXT,
                        conditions TEXT,
                        actions TEXT,
                        is_active BOOLEAN,
                        created_at TEXT
                    )
                ''')
                
                # Smart notifications table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS smart_notifications (
                        id TEXT PRIMARY KEY,
                        notification_type TEXT,
                        title TEXT,
                        message TEXT,
                        deal_id TEXT,
                        buyer_id TEXT,
                        recipient_emails TEXT,
                        scheduled_for TEXT,
                        sent_at TEXT,
                        is_sent BOOLEAN,
                        priority TEXT,
                        metadata TEXT
                    )
                ''')
                
                # Investment criteria table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS investment_criteria (
                        id TEXT PRIMARY KEY,
                        buyer_id TEXT,
                        property_types TEXT,
                        min_price REAL,
                        max_price REAL,
                        min_roi REAL,
                        max_ltv REAL,
                        preferred_locations TEXT,
                        max_rehab_budget REAL,
                        min_cash_flow REAL,
                        investment_strategy TEXT,
                        is_active BOOLEAN,
                        created_at TEXT
                    )
                ''')
                
                # Deal matches table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS deal_matches (
                        id TEXT PRIMARY KEY,
                        deal_id TEXT,
                        buyer_id TEXT,
                        match_score REAL,
                        match_factors TEXT,
                        status TEXT,
                        created_at TEXT,
                        sent_at TEXT,
                        viewed_at TEXT,
                        responded_at TEXT,
                        notes TEXT
                    )
                ''')
                
                conn.commit()
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def setup_default_triggers(self):
        """Setup default workflow triggers"""
        default_triggers = [
            {
                'name': 'New Deal Auto-Matching',
                'trigger_type': 'deal_created',
                'conditions': {'status': 'qualified'},
                'actions': [
                    {'type': 'find_matches'},
                    {'type': 'notify_matches', 'threshold': 70}
                ]
            },
            {
                'name': 'Deal Stage Notifications',
                'trigger_type': 'stage_change',
                'conditions': {'stages': ['under_contract', 'closing']},
                'actions': [
                    {'type': 'notify_stakeholders'},
                    {'type': 'update_timeline'}
                ]
            },
            {
                'name': 'Follow-up Reminders',
                'trigger_type': 'time_based',
                'conditions': {'days_since_contact': 3},
                'actions': [
                    {'type': 'create_reminder'},
                    {'type': 'schedule_follow_up'}
                ]
            }
        ]
        
        for trigger_data in default_triggers:
            trigger = WorkflowTrigger(
                name=trigger_data['name'],
                trigger_type=trigger_data['trigger_type'],
                conditions=trigger_data['conditions'],
                actions=trigger_data['actions']
            )
            self.triggers.append(trigger)
    
    def process_deal_stage_change(self, deal_id: str, old_stage: str, new_stage: str):
        """Process deal stage changes and trigger workflows"""
        notifications = []
        
        # Create stage change notification
        notification = SmartNotification(
            notification_type=NotificationType.STATUS_UPDATE,
            title=f"Deal Stage Updated: {new_stage}",
            message=f"Deal has moved from {old_stage} to {new_stage}",
            deal_id=deal_id,
            priority="Medium"
        )
        notifications.append(notification)
        
        # Check for milestone notifications
        milestone_stages = {
            DealStage.UNDER_CONTRACT.value: "Deal is now under contract!",
            DealStage.CLOSING.value: "Deal is approaching closing!",
            DealStage.CLOSED.value: "Congratulations! Deal has closed successfully!"
        }
        
        if new_stage in milestone_stages:
            milestone_notification = SmartNotification(
                notification_type=NotificationType.MILESTONE_REACHED,
                title=f"Milestone Reached: {new_stage}",
                message=milestone_stages[new_stage],
                deal_id=deal_id,
                priority="High"
            )
            notifications.append(milestone_notification)
        
        return notifications
    
    def schedule_follow_up_reminders(self, deals: List[Dict[str, Any]]) -> List[SmartNotification]:
        """Schedule automatic follow-up reminders"""
        reminders = []
        current_time = datetime.now()
        
        for deal in deals:
            last_contact = deal.get('last_contact_date')
            if last_contact:
                days_since_contact = (current_time - last_contact).days
                
                # Schedule reminders based on deal stage and time elapsed
                reminder_schedule = {
                    DealStage.SOURCED.value: 1,
                    DealStage.ANALYZED.value: 2,
                    DealStage.QUALIFIED.value: 3,
                    DealStage.MARKETED.value: 1
                }
                
                stage = deal.get('deal_stage', '')
                reminder_days = reminder_schedule.get(stage, 7)
                
                if days_since_contact >= reminder_days:
                    reminder = SmartNotification(
                        notification_type=NotificationType.FOLLOW_UP_REMINDER,
                        title=f"Follow-up Reminder: {deal.get('property_address', 'Deal')}",
                        message=f"It's been {days_since_contact} days since last contact. Consider following up.",
                        deal_id=deal.get('id', ''),
                        scheduled_for=current_time + timedelta(hours=1),
                        priority="Medium"
                    )
                    reminders.append(reminder)
        
        return reminders

class DealWorkflowAutomation:
    """Main deal workflow automation system"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.matching_engine = DealMatchingEngine()
        self.pipeline_manager = DealPipelineManager(db_path)
        self.investment_criteria: List[InvestmentCriteria] = []
        self.deal_matches: List[DealMatch] = []
        self.load_data()
    
    def load_data(self):
        """Load automation data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Load investment criteria
                cursor.execute("SELECT * FROM investment_criteria")
                criteria_rows = cursor.fetchall()
                
                for row in criteria_rows:
                    criteria = InvestmentCriteria(
                        id=row[0],
                        buyer_id=row[1],
                        property_types=[PropertyType(t) for t in json.loads(row[2]) if t],
                        min_price=row[3],
                        max_price=row[4],
                        min_roi=row[5],
                        max_ltv=row[6],
                        preferred_locations=json.loads(row[7]),
                        max_rehab_budget=row[8],
                        min_cash_flow=row[9],
                        investment_strategy=row[10],
                        is_active=bool(row[11]),
                        created_at=datetime.fromisoformat(row[12])
                    )
                    self.investment_criteria.append(criteria)
                
                # Load deal matches
                cursor.execute("SELECT * FROM deal_matches")
                match_rows = cursor.fetchall()
                
                for row in match_rows:
                    match = DealMatch(
                        id=row[0],
                        deal_id=row[1],
                        buyer_id=row[2],
                        match_score=row[3],
                        match_factors=json.loads(row[4]),
                        status=row[5],
                        created_at=datetime.fromisoformat(row[6]),
                        sent_at=datetime.fromisoformat(row[7]) if row[7] else None,
                        viewed_at=datetime.fromisoformat(row[8]) if row[8] else None,
                        responded_at=datetime.fromisoformat(row[9]) if row[9] else None,
                        notes=row[10]
                    )
                    self.deal_matches.append(match)
                    
        except Exception as e:
            print(f"Error loading automation data: {e}")
    
    def save_data(self):
        """Save automation data to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Save investment criteria
                cursor.execute("DELETE FROM investment_criteria")
                for criteria in self.investment_criteria:
                    cursor.execute('''
                        INSERT INTO investment_criteria VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        criteria.id,
                        criteria.buyer_id,
                        json.dumps([pt.value for pt in criteria.property_types]),
                        criteria.min_price,
                        criteria.max_price,
                        criteria.min_roi,
                        criteria.max_ltv,
                        json.dumps(criteria.preferred_locations),
                        criteria.max_rehab_budget,
                        criteria.min_cash_flow,
                        criteria.investment_strategy,
                        criteria.is_active,
                        criteria.created_at.isoformat()
                    ))
                
                # Save deal matches
                cursor.execute("DELETE FROM deal_matches")
                for match in self.deal_matches:
                    cursor.execute('''
                        INSERT INTO deal_matches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        match.id,
                        match.deal_id,
                        match.buyer_id,
                        match.match_score,
                        json.dumps(match.match_factors),
                        match.status,
                        match.created_at.isoformat(),
                        match.sent_at.isoformat() if match.sent_at else None,
                        match.viewed_at.isoformat() if match.viewed_at else None,
                        match.responded_at.isoformat() if match.responded_at else None,
                        match.notes
                    ))
                
                conn.commit()
        except Exception as e:
            print(f"Error saving automation data: {e}")
    
    def create_investment_criteria(self, buyer_id: str, criteria_data: Dict[str, Any]) -> InvestmentCriteria:
        """Create new investment criteria for a buyer"""
        criteria = InvestmentCriteria(
            buyer_id=buyer_id,
            property_types=[PropertyType(pt) for pt in criteria_data.get('property_types', [])],
            min_price=criteria_data.get('min_price', 0),
            max_price=criteria_data.get('max_price', 1000000),
            min_roi=criteria_data.get('min_roi', 0),
            max_ltv=criteria_data.get('max_ltv', 80),
            preferred_locations=criteria_data.get('preferred_locations', []),
            max_rehab_budget=criteria_data.get('max_rehab_budget', 50000),
            min_cash_flow=criteria_data.get('min_cash_flow', 0),
            investment_strategy=criteria_data.get('investment_strategy', 'Buy and Hold')
        )
        
        self.investment_criteria.append(criteria)
        self.save_data()
        return criteria
    
    def run_deal_matching(self, deals: List[Dict[str, Any]]) -> List[DealMatch]:
        """Run automated deal matching for all active criteria"""
        new_matches = self.matching_engine.find_matches(deals, self.investment_criteria)
        
        # Filter out existing matches
        existing_match_keys = {(m.deal_id, m.buyer_id) for m in self.deal_matches}
        filtered_matches = [
            m for m in new_matches 
            if (m.deal_id, m.buyer_id) not in existing_match_keys
        ]
        
        self.deal_matches.extend(filtered_matches)
        self.save_data()
        return filtered_matches
    
    def get_automation_analytics(self) -> Dict[str, Any]:
        """Get automation performance analytics"""
        total_matches = len(self.deal_matches)
        high_quality_matches = len([m for m in self.deal_matches if m.match_score >= 70])
        sent_matches = len([m for m in self.deal_matches if m.sent_at])
        responded_matches = len([m for m in self.deal_matches if m.responded_at])
        
        conversion_rate = (responded_matches / sent_matches * 100) if sent_matches > 0 else 0
        
        return {
            'total_matches_generated': total_matches,
            'high_quality_matches': high_quality_matches,
            'matches_sent': sent_matches,
            'matches_responded': responded_matches,
            'response_conversion_rate': conversion_rate,
            'active_criteria': len([c for c in self.investment_criteria if c.is_active]),
            'avg_match_score': sum(m.match_score for m in self.deal_matches) / total_matches if total_matches > 0 else 0
        }

# Global workflow automation manager
@st.cache_resource
def get_workflow_manager():
    """Get cached workflow automation manager"""
    return DealWorkflowAutomation()