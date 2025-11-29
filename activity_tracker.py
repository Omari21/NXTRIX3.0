"""
Advanced Activity Tracking and Opportunity Management System
Comprehensive logging, user notifications, and opportunity tracking to ensure nothing falls through the cracks
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

class ActivityType(Enum):
    """Types of tracked activities"""
    DEAL_CREATED = "Deal Created"
    DEAL_UPDATED = "Deal Updated"
    DEAL_STAGE_CHANGED = "Deal Stage Changed"
    LEAD_CONTACTED = "Lead Contacted"
    BUYER_MATCHED = "Buyer Matched"
    EMAIL_SENT = "Email Sent"
    SMS_SENT = "SMS Sent"
    FOLLOW_UP_SCHEDULED = "Follow-up Scheduled"
    TASK_CREATED = "Task Created"
    TASK_COMPLETED = "Task Completed"
    DEADLINE_APPROACHING = "Deadline Approaching"
    OPPORTUNITY_IDENTIFIED = "Opportunity Identified"
    CONTACT_ADDED = "Contact Added"
    DOCUMENT_UPLOADED = "Document Uploaded"
    MEETING_SCHEDULED = "Meeting Scheduled"
    CALL_LOGGED = "Call Logged"
    PROPERTY_ANALYZED = "Property Analyzed"
    OFFER_SUBMITTED = "Offer Submitted"
    CONTRACT_SIGNED = "Contract Signed"
    CLOSING_SCHEDULED = "Closing Scheduled"

class Priority(Enum):
    """Priority levels for activities and notifications"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"
    CRITICAL = "Critical"

class NotificationChannel(Enum):
    """Notification delivery channels"""
    IN_APP = "In-App"
    EMAIL = "Email"
    SMS = "SMS"
    PUSH = "Push Notification"
    SLACK = "Slack"

@dataclass
class ActivityLog:
    """Comprehensive activity logging"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    activity_type: ActivityType = ActivityType.DEAL_CREATED
    title: str = ""
    description: str = ""
    entity_type: str = ""  # Deal, Lead, Contact, Task, etc.
    entity_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: Priority = Priority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    requires_action: bool = False
    action_deadline: Optional[datetime] = None
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class OpportunityAlert:
    """Opportunity identification and alerts"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    opportunity_type: str = ""  # Hot Lead, Deal Match, Price Drop, etc.
    title: str = ""
    description: str = ""
    entity_id: str = ""
    potential_value: float = 0.0
    confidence_score: float = 0.0  # 0-100%
    priority: Priority = Priority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_acted_upon: bool = False
    action_taken: str = ""
    action_date: Optional[datetime] = None
    outcome: str = ""

@dataclass
class UserNotification:
    """User notification system"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    title: str = ""
    message: str = ""
    notification_type: str = "reminder"  # reminder, alert, opportunity, deadline
    priority: Priority = Priority.MEDIUM
    channels: List[NotificationChannel] = field(default_factory=list)
    related_entity_type: str = ""
    related_entity_id: str = ""
    scheduled_for: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    is_sent: bool = False
    is_read: bool = False
    action_url: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReminderRule:
    """Automated reminder rules"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    entity_type: str = ""  # Deal, Lead, Task, etc.
    trigger_condition: str = ""  # days_since_last_contact, approaching_deadline, etc.
    trigger_value: int = 0  # Number of days, hours, etc.
    reminder_message: str = ""
    priority: Priority = Priority.MEDIUM
    channels: List[NotificationChannel] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

class ActivityTracker:
    """Comprehensive activity tracking system"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.activity_logs: List[ActivityLog] = []
        self.opportunity_alerts: List[OpportunityAlert] = []
        self.notifications: List[UserNotification] = []
        self.reminder_rules: List[ReminderRule] = []
        self.init_database()
        self.setup_default_reminder_rules()
        self.load_data()
    
    def init_database(self):
        """Initialize activity tracking database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Activity logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS activity_logs (
                        id TEXT PRIMARY KEY,
                        user_id TEXT,
                        activity_type TEXT,
                        title TEXT,
                        description TEXT,
                        entity_type TEXT,
                        entity_id TEXT,
                        metadata TEXT,
                        priority TEXT,
                        created_at TEXT,
                        requires_action BOOLEAN,
                        action_deadline TEXT,
                        is_completed BOOLEAN,
                        completed_at TEXT,
                        tags TEXT
                    )
                ''')
                
                # Opportunity alerts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS opportunity_alerts (
                        id TEXT PRIMARY KEY,
                        opportunity_type TEXT,
                        title TEXT,
                        description TEXT,
                        entity_id TEXT,
                        potential_value REAL,
                        confidence_score REAL,
                        priority TEXT,
                        created_at TEXT,
                        expires_at TEXT,
                        is_acted_upon BOOLEAN,
                        action_taken TEXT,
                        action_date TEXT,
                        outcome TEXT
                    )
                ''')
                
                # User notifications table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_notifications (
                        id TEXT PRIMARY KEY,
                        user_id TEXT,
                        title TEXT,
                        message TEXT,
                        notification_type TEXT,
                        priority TEXT,
                        channels TEXT,
                        related_entity_type TEXT,
                        related_entity_id TEXT,
                        scheduled_for TEXT,
                        sent_at TEXT,
                        read_at TEXT,
                        is_sent BOOLEAN,
                        is_read BOOLEAN,
                        action_url TEXT,
                        metadata TEXT
                    )
                ''')
                
                # Reminder rules table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reminder_rules (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        entity_type TEXT,
                        trigger_condition TEXT,
                        trigger_value INTEGER,
                        reminder_message TEXT,
                        priority TEXT,
                        channels TEXT,
                        is_active BOOLEAN,
                        created_at TEXT
                    )
                ''')
                
                conn.commit()
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def setup_default_reminder_rules(self):
        """Setup default reminder rules for common scenarios"""
        default_rules = [
            {
                'name': 'Deal Follow-up Reminder',
                'entity_type': 'Deal',
                'trigger_condition': 'days_since_last_contact',
                'trigger_value': 3,
                'reminder_message': 'Deal requires follow-up - no contact in 3 days',
                'priority': Priority.HIGH,
                'channels': [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
            },
            {
                'name': 'Hot Lead Response Reminder',
                'entity_type': 'Lead',
                'trigger_condition': 'days_since_creation',
                'trigger_value': 1,
                'reminder_message': 'New hot lead needs immediate response',
                'priority': Priority.URGENT,
                'channels': [NotificationChannel.IN_APP, NotificationChannel.SMS]
            },
            {
                'name': 'Task Deadline Alert',
                'entity_type': 'Task',
                'trigger_condition': 'hours_until_deadline',
                'trigger_value': 24,
                'reminder_message': 'Task deadline approaching in 24 hours',
                'priority': Priority.HIGH,
                'channels': [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
            },
            {
                'name': 'Contract Expiration Warning',
                'entity_type': 'Deal',
                'trigger_condition': 'days_until_contract_expiry',
                'trigger_value': 7,
                'reminder_message': 'Contract expires in 7 days - action required',
                'priority': Priority.CRITICAL,
                'channels': [NotificationChannel.IN_APP, NotificationChannel.EMAIL, NotificationChannel.SMS]
            },
            {
                'name': 'Buyer Interest Follow-up',
                'entity_type': 'Deal',
                'trigger_condition': 'days_since_buyer_interest',
                'trigger_value': 2,
                'reminder_message': 'Buyer showed interest - follow up required',
                'priority': Priority.HIGH,
                'channels': [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
            }
        ]
        
        for rule_data in default_rules:
            rule = ReminderRule(
                name=rule_data['name'],
                entity_type=rule_data['entity_type'],
                trigger_condition=rule_data['trigger_condition'],
                trigger_value=rule_data['trigger_value'],
                reminder_message=rule_data['reminder_message'],
                priority=rule_data['priority'],
                channels=rule_data['channels']
            )
            self.reminder_rules.append(rule)
    
    def log_activity(self, 
                    user_id: str,
                    activity_type: ActivityType,
                    title: str,
                    description: str = "",
                    entity_type: str = "",
                    entity_id: str = "",
                    metadata: Dict[str, Any] = None,
                    priority: Priority = Priority.MEDIUM,
                    requires_action: bool = False,
                    action_deadline: Optional[datetime] = None,
                    tags: List[str] = None) -> ActivityLog:
        """Log a new activity"""
        
        activity = ActivityLog(
            user_id=user_id,
            activity_type=activity_type,
            title=title,
            description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=metadata or {},
            priority=priority,
            requires_action=requires_action,
            action_deadline=action_deadline,
            tags=tags or []
        )
        
        self.activity_logs.append(activity)
        self.save_data()
        
        # Check if this activity triggers any opportunities or reminders
        self.check_opportunity_triggers(activity)
        
        return activity
    
    def create_opportunity_alert(self,
                               opportunity_type: str,
                               title: str,
                               description: str,
                               entity_id: str = "",
                               potential_value: float = 0.0,
                               confidence_score: float = 0.0,
                               priority: Priority = Priority.MEDIUM,
                               expires_at: Optional[datetime] = None) -> OpportunityAlert:
        """Create a new opportunity alert"""
        
        opportunity = OpportunityAlert(
            opportunity_type=opportunity_type,
            title=title,
            description=description,
            entity_id=entity_id,
            potential_value=potential_value,
            confidence_score=confidence_score,
            priority=priority,
            expires_at=expires_at
        )
        
        self.opportunity_alerts.append(opportunity)
        
        # Create notification for the opportunity
        self.create_notification(
            user_id="admin",  # In real app, determine appropriate user
            title=f"New Opportunity: {title}",
            message=description,
            notification_type="opportunity",
            priority=priority,
            channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
            related_entity_type="opportunity",
            related_entity_id=opportunity.id
        )
        
        self.save_data()
        return opportunity
    
    def create_notification(self,
                          user_id: str,
                          title: str,
                          message: str,
                          notification_type: str = "reminder",
                          priority: Priority = Priority.MEDIUM,
                          channels: List[NotificationChannel] = None,
                          related_entity_type: str = "",
                          related_entity_id: str = "",
                          scheduled_for: Optional[datetime] = None,
                          action_url: str = "",
                          metadata: Dict[str, Any] = None) -> UserNotification:
        """Create a new user notification"""
        
        notification = UserNotification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            channels=channels or [NotificationChannel.IN_APP],
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            scheduled_for=scheduled_for or datetime.now(),
            action_url=action_url,
            metadata=metadata or {}
        )
        
        self.notifications.append(notification)
        self.save_data()
        return notification
    
    def check_opportunity_triggers(self, activity: ActivityLog):
        """Check if an activity triggers opportunity identification"""
        
        # Hot lead identification
        if activity.activity_type == ActivityType.LEAD_CONTACTED:
            response_time = activity.metadata.get('response_time_minutes', 0)
            if response_time < 30:  # Responded within 30 minutes
                self.create_opportunity_alert(
                    opportunity_type="Hot Lead",
                    title=f"Hot Lead Identified: Quick Response",
                    description=f"Lead responded within {response_time} minutes - high conversion potential",
                    entity_id=activity.entity_id,
                    potential_value=50000,  # Estimated deal value
                    confidence_score=85.0,
                    priority=Priority.HIGH,
                    expires_at=datetime.now() + timedelta(hours=24)
                )
        
        # High-value deal opportunity
        elif activity.activity_type == ActivityType.DEAL_CREATED:
            deal_value = activity.metadata.get('asking_price', 0)
            roi = activity.metadata.get('estimated_roi', 0)
            
            if deal_value > 200000 and roi > 15:
                self.create_opportunity_alert(
                    opportunity_type="High-Value Deal",
                    title=f"Premium Investment Opportunity",
                    description=f"${deal_value:,.0f} deal with {roi:.1f}% ROI - priority marketing needed",
                    entity_id=activity.entity_id,
                    potential_value=deal_value * 0.1,  # Estimated commission
                    confidence_score=75.0,
                    priority=Priority.HIGH
                )
        
        # Buyer engagement spike
        elif activity.activity_type == ActivityType.BUYER_MATCHED:
            match_score = activity.metadata.get('match_score', 0)
            if match_score > 85:
                self.create_opportunity_alert(
                    opportunity_type="Perfect Match",
                    title=f"Exceptional Buyer Match ({match_score:.1f}%)",
                    description="High-probability deal closure - immediate contact recommended",
                    entity_id=activity.entity_id,
                    confidence_score=match_score,
                    priority=Priority.URGENT,
                    expires_at=datetime.now() + timedelta(hours=12)
                )
    
    def process_reminder_rules(self, deals: List[Any], leads: List[Any], tasks: List[Any]) -> List[UserNotification]:
        """Process all reminder rules and generate notifications"""
        generated_notifications = []
        current_time = datetime.now()
        
        for rule in self.reminder_rules:
            if not rule.is_active:
                continue
            
            if rule.entity_type == "Deal":
                for deal in deals:
                    notification = self.check_deal_reminder_rule(deal, rule, current_time)
                    if notification:
                        generated_notifications.append(notification)
            
            elif rule.entity_type == "Lead":
                for lead in leads:
                    notification = self.check_lead_reminder_rule(lead, rule, current_time)
                    if notification:
                        generated_notifications.append(notification)
            
            elif rule.entity_type == "Task":
                for task in tasks:
                    notification = self.check_task_reminder_rule(task, rule, current_time)
                    if notification:
                        generated_notifications.append(notification)
        
        return generated_notifications
    
    def check_deal_reminder_rule(self, deal: Any, rule: ReminderRule, current_time: datetime) -> Optional[UserNotification]:
        """Check if a deal triggers a reminder rule"""
        
        if rule.trigger_condition == "days_since_last_contact":
            last_contact = getattr(deal, 'last_contact_date', deal.created_at)
            days_since = (current_time - last_contact).days
            
            if days_since >= rule.trigger_value:
                return self.create_notification(
                    user_id="admin",
                    title=f"Deal Follow-up Required: {deal.property_address}",
                    message=f"No contact in {days_since} days. {rule.reminder_message}",
                    notification_type="reminder",
                    priority=rule.priority,
                    channels=rule.channels,
                    related_entity_type="Deal",
                    related_entity_id=deal.id,
                    action_url=f"/deal/{deal.id}"
                )
        
        elif rule.trigger_condition == "days_until_contract_expiry":
            if hasattr(deal, 'contract_expiry_date') and deal.contract_expiry_date:
                days_until = (deal.contract_expiry_date - current_time).days
                
                if days_until <= rule.trigger_value:
                    return self.create_notification(
                        user_id="admin",
                        title=f"Contract Expiring: {deal.property_address}",
                        message=f"Contract expires in {days_until} days. {rule.reminder_message}",
                        notification_type="deadline",
                        priority=Priority.CRITICAL,
                        channels=rule.channels,
                        related_entity_type="Deal",
                        related_entity_id=deal.id
                    )
        
        return None
    
    def check_lead_reminder_rule(self, lead: Any, rule: ReminderRule, current_time: datetime) -> Optional[UserNotification]:
        """Check if a lead triggers a reminder rule"""
        
        if rule.trigger_condition == "days_since_creation":
            days_since = (current_time - lead.created_at).days
            
            if days_since >= rule.trigger_value and lead.status == "New":
                return self.create_notification(
                    user_id="admin",
                    title=f"Urgent Lead Response: {lead.name}",
                    message=f"Lead created {days_since} days ago. {rule.reminder_message}",
                    notification_type="reminder",
                    priority=Priority.URGENT,
                    channels=rule.channels,
                    related_entity_type="Lead",
                    related_entity_id=lead.id
                )
        
        return None
    
    def check_task_reminder_rule(self, task: Any, rule: ReminderRule, current_time: datetime) -> Optional[UserNotification]:
        """Check if a task triggers a reminder rule"""
        
        if rule.trigger_condition == "hours_until_deadline":
            if hasattr(task, 'deadline') and task.deadline:
                hours_until = (task.deadline - current_time).total_seconds() / 3600
                
                if hours_until <= rule.trigger_value and not task.is_completed:
                    return self.create_notification(
                        user_id="admin",
                        title=f"Task Deadline Approaching: {task.title}",
                        message=f"Deadline in {hours_until:.1f} hours. {rule.reminder_message}",
                        notification_type="deadline",
                        priority=rule.priority,
                        channels=rule.channels,
                        related_entity_type="Task",
                        related_entity_id=task.id
                    )
        
        return None
    
    def get_activity_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get activity summary for the specified number of days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_activities = [a for a in self.activity_logs if a.created_at >= cutoff_date]
        
        # Activity type breakdown
        activity_counts = {}
        for activity in recent_activities:
            activity_type = activity.activity_type.value
            activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
        
        # Priority breakdown
        priority_counts = {}
        for activity in recent_activities:
            priority = activity.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Actions required
        actions_required = len([a for a in recent_activities if a.requires_action and not a.is_completed])
        
        # Opportunities
        recent_opportunities = [o for o in self.opportunity_alerts if o.created_at >= cutoff_date]
        total_opportunity_value = sum(o.potential_value for o in recent_opportunities)
        
        return {
            'total_activities': len(recent_activities),
            'activity_breakdown': activity_counts,
            'priority_breakdown': priority_counts,
            'actions_required': actions_required,
            'opportunities_identified': len(recent_opportunities),
            'total_opportunity_value': total_opportunity_value,
            'unread_notifications': len([n for n in self.notifications if not n.is_read]),
            'pending_notifications': len([n for n in self.notifications if not n.is_sent])
        }
    
    def get_pending_actions(self) -> List[ActivityLog]:
        """Get all activities requiring action"""
        return [a for a in self.activity_logs if a.requires_action and not a.is_completed]
    
    def get_recent_activities(self, days_back: int = 7, activity_type: ActivityType = None, priority: Priority = None) -> List[ActivityLog]:
        """Get recent activities with optional filtering"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Filter by date first
        activities = [a for a in self.activity_logs if a.created_at >= cutoff_date]
        
        # Filter by activity type if specified
        if activity_type:
            activities = [a for a in activities if a.activity_type == activity_type]
        
        # Filter by priority if specified
        if priority:
            activities = [a for a in activities if a.priority == priority]
        
        # Sort by creation date (newest first)
        activities.sort(key=lambda x: x.created_at, reverse=True)
        
        return activities
    
    def get_active_opportunities(self) -> List[OpportunityAlert]:
        """Get all active opportunities"""
        current_time = datetime.now()
        return [o for o in self.opportunity_alerts 
                if not o.is_acted_upon and (not o.expires_at or o.expires_at > current_time)]
    
    def get_unread_notifications(self, user_id: str) -> List[UserNotification]:
        """Get unread notifications for a user"""
        return [n for n in self.notifications if n.user_id == user_id and not n.is_read]
    
    def mark_notification_read(self, notification_id: str):
        """Mark a notification as read"""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.is_read = True
                notification.read_at = datetime.now()
                break
        self.save_data()
    
    def mark_opportunity_acted_upon(self, opportunity_id: str, action_taken: str, outcome: str = ""):
        """Mark an opportunity as acted upon"""
        for opportunity in self.opportunity_alerts:
            if opportunity.id == opportunity_id:
                opportunity.is_acted_upon = True
                opportunity.action_taken = action_taken
                opportunity.action_date = datetime.now()
                opportunity.outcome = outcome
                break
        self.save_data()
    
    def load_data(self):
        """Load activity data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Load activity logs
                cursor.execute("SELECT * FROM activity_logs ORDER BY created_at DESC LIMIT 1000")
                for row in cursor.fetchall():
                    activity = ActivityLog(
                        id=row[0],
                        user_id=row[1],
                        activity_type=ActivityType(row[2]),
                        title=row[3],
                        description=row[4],
                        entity_type=row[5],
                        entity_id=row[6],
                        metadata=json.loads(row[7]) if row[7] else {},
                        priority=Priority(row[8]),
                        created_at=datetime.fromisoformat(row[9]),
                        requires_action=bool(row[10]),
                        action_deadline=datetime.fromisoformat(row[11]) if row[11] else None,
                        is_completed=bool(row[12]),
                        completed_at=datetime.fromisoformat(row[13]) if row[13] else None,
                        tags=json.loads(row[14]) if row[14] else []
                    )
                    self.activity_logs.append(activity)
                
                # Load opportunity alerts
                cursor.execute("SELECT * FROM opportunity_alerts ORDER BY created_at DESC")
                for row in cursor.fetchall():
                    opportunity = OpportunityAlert(
                        id=row[0],
                        opportunity_type=row[1],
                        title=row[2],
                        description=row[3],
                        entity_id=row[4],
                        potential_value=row[5],
                        confidence_score=row[6],
                        priority=Priority(row[7]),
                        created_at=datetime.fromisoformat(row[8]),
                        expires_at=datetime.fromisoformat(row[9]) if row[9] else None,
                        is_acted_upon=bool(row[10]),
                        action_taken=row[11],
                        action_date=datetime.fromisoformat(row[12]) if row[12] else None,
                        outcome=row[13]
                    )
                    self.opportunity_alerts.append(opportunity)
                
                # Load notifications
                cursor.execute("SELECT * FROM user_notifications ORDER BY scheduled_for DESC LIMIT 500")
                for row in cursor.fetchall():
                    notification = UserNotification(
                        id=row[0],
                        user_id=row[1],
                        title=row[2],
                        message=row[3],
                        notification_type=row[4],
                        priority=Priority(row[5]),
                        channels=[NotificationChannel(c) for c in json.loads(row[6])],
                        related_entity_type=row[7],
                        related_entity_id=row[8],
                        scheduled_for=datetime.fromisoformat(row[9]),
                        sent_at=datetime.fromisoformat(row[10]) if row[10] else None,
                        read_at=datetime.fromisoformat(row[11]) if row[11] else None,
                        is_sent=bool(row[12]),
                        is_read=bool(row[13]),
                        action_url=row[14],
                        metadata=json.loads(row[15]) if row[15] else {}
                    )
                    self.notifications.append(notification)
                    
        except Exception as e:
            print(f"Error loading activity data: {e}")
    
    def get_user_notifications(self, user_id, unread_only=False):
        """Get notifications for a specific user"""
        try:
            user_notifications = [n for n in self.notifications if n.user_id == user_id]
            if unread_only:
                user_notifications = [n for n in user_notifications if not n.is_read]
            return user_notifications
        except Exception as e:
            print(f"Error getting user notifications: {e}")
            return []
    
    def save_data(self):
        """Save activity data to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Save activity logs (only recent ones to prevent database bloat)
                cursor.execute("DELETE FROM activity_logs")
                for activity in self.activity_logs[-1000:]:  # Keep last 1000 activities
                    cursor.execute('''
                        INSERT INTO activity_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        activity.id,
                        activity.user_id,
                        activity.activity_type.value,
                        activity.title,
                        activity.description,
                        activity.entity_type,
                        activity.entity_id,
                        json.dumps(activity.metadata),
                        activity.priority.value,
                        activity.created_at.isoformat(),
                        activity.requires_action,
                        activity.action_deadline.isoformat() if activity.action_deadline else None,
                        activity.is_completed,
                        activity.completed_at.isoformat() if activity.completed_at else None,
                        json.dumps(activity.tags)
                    ))
                
                # Save opportunity alerts
                cursor.execute("DELETE FROM opportunity_alerts")
                for opportunity in self.opportunity_alerts:
                    cursor.execute('''
                        INSERT INTO opportunity_alerts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        opportunity.id,
                        opportunity.opportunity_type,
                        opportunity.title,
                        opportunity.description,
                        opportunity.entity_id,
                        opportunity.potential_value,
                        opportunity.confidence_score,
                        opportunity.priority.value,
                        opportunity.created_at.isoformat(),
                        opportunity.expires_at.isoformat() if opportunity.expires_at else None,
                        opportunity.is_acted_upon,
                        opportunity.action_taken,
                        opportunity.action_date.isoformat() if opportunity.action_date else None,
                        opportunity.outcome
                    ))
                
                # Save notifications
                cursor.execute("DELETE FROM user_notifications")
                for notification in self.notifications[-500:]:  # Keep last 500 notifications
                    cursor.execute('''
                        INSERT INTO user_notifications VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        notification.id,
                        notification.user_id,
                        notification.title,
                        notification.message,
                        notification.notification_type,
                        notification.priority.value,
                        json.dumps([c.value for c in notification.channels]),
                        notification.related_entity_type,
                        notification.related_entity_id,
                        notification.scheduled_for.isoformat(),
                        notification.sent_at.isoformat() if notification.sent_at else None,
                        notification.read_at.isoformat() if notification.read_at else None,
                        notification.is_sent,
                        notification.is_read,
                        notification.action_url,
                        json.dumps(notification.metadata)
                    ))
                
                conn.commit()
        except Exception as e:
            print(f"Error saving activity data: {e}")

# Global activity tracker
@st.cache_resource
def get_activity_tracker():
    """Get cached activity tracker"""
    return ActivityTracker()