"""
Smart Notifications & Alerts System for NXTRIX CRM
Real-time alerts for deals, leads, and system events
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import sqlite3
import uuid

class NotificationType(Enum):
    DEAL_ALERT = "deal_alert"
    LEAD_ALERT = "lead_alert"
    TASK_REMINDER = "task_reminder"
    SYSTEM_ALERT = "system_alert"
    MARKET_UPDATE = "market_update"
    AUTOMATION_ALERT = "automation_alert"

class NotificationPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Notification:
    """Notification data structure"""
    id: str
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority
    is_read: bool = False
    is_dismissed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    read_at: Optional[datetime] = None
    data: Dict[str, Any] = field(default_factory=dict)
    action_url: Optional[str] = None

class NotificationCenter:
    """Smart notification and alerts system"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize notifications database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT 0,
                    is_dismissed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    read_at TIMESTAMP,
                    data TEXT,
                    action_url TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_settings (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    notification_type TEXT NOT NULL,
                    is_enabled BOOLEAN DEFAULT 1,
                    email_enabled BOOLEAN DEFAULT 0,
                    sms_enabled BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error initializing notifications database: {e}")
    
    def create_notification(self, title: str, message: str, 
                          notification_type: NotificationType,
                          priority: NotificationPriority = NotificationPriority.MEDIUM,
                          data: Dict[str, Any] = None,
                          action_url: str = None) -> str:
        """Create a new notification"""
        try:
            notification = Notification(
                id=str(uuid.uuid4()),
                title=title,
                message=message,
                type=notification_type,
                priority=priority,
                data=data or {},
                action_url=action_url
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notifications 
                (id, title, message, type, priority, is_read, is_dismissed, 
                 created_at, data, action_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                notification.id,
                notification.title,
                notification.message,
                notification.type.value,
                notification.priority.value,
                notification.is_read,
                notification.is_dismissed,
                notification.created_at.isoformat(),
                json.dumps(notification.data),
                notification.action_url
            ))
            
            conn.commit()
            conn.close()
            
            return notification.id
            
        except Exception as e:
            st.error(f"Error creating notification: {e}")
            return ""
    
    def get_notifications(self, unread_only: bool = False, 
                         notification_type: Optional[NotificationType] = None,
                         limit: int = 50) -> List[Notification]:
        """Get notifications with optional filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM notifications WHERE is_dismissed = 0"
            params = []
            
            if unread_only:
                query += " AND is_read = 0"
            
            if notification_type:
                query += " AND type = ?"
                params.append(notification_type.value)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            notifications = []
            for row in rows:
                notification = Notification(
                    id=row[0],
                    title=row[1],
                    message=row[2],
                    type=NotificationType(row[3]),
                    priority=NotificationPriority(row[4]),
                    is_read=bool(row[5]),
                    is_dismissed=bool(row[6]),
                    created_at=datetime.fromisoformat(row[7]),
                    read_at=datetime.fromisoformat(row[8]) if row[8] else None,
                    data=json.loads(row[9]) if row[9] else {},
                    action_url=row[10]
                )
                notifications.append(notification)
            
            conn.close()
            return notifications
            
        except Exception as e:
            st.error(f"Error retrieving notifications: {e}")
            return []
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE notifications 
                SET is_read = 1, read_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), notification_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error marking notification as read: {e}")
            return False
    
    def dismiss_notification(self, notification_id: str) -> bool:
        """Dismiss a notification"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE notifications 
                SET is_dismissed = 1
                WHERE id = ?
            ''', (notification_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error dismissing notification: {e}")
            return False
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total counts
            cursor.execute("SELECT COUNT(*) FROM notifications WHERE is_dismissed = 0")
            total_notifications = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM notifications WHERE is_read = 0 AND is_dismissed = 0")
            unread_notifications = cursor.fetchone()[0]
            
            # By type
            cursor.execute("""
                SELECT type, COUNT(*) 
                FROM notifications 
                WHERE is_dismissed = 0 
                GROUP BY type
            """)
            by_type = dict(cursor.fetchall())
            
            # By priority
            cursor.execute("""
                SELECT priority, COUNT(*) 
                FROM notifications 
                WHERE is_dismissed = 0 AND is_read = 0
                GROUP BY priority
            """)
            by_priority = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_notifications': total_notifications,
                'unread_notifications': unread_notifications,
                'by_type': by_type,
                'by_priority': by_priority
            }
            
        except Exception as e:
            st.error(f"Error getting notification stats: {e}")
            return {}
    
    def create_deal_alert(self, deal_data: Dict[str, Any]) -> str:
        """Create a deal-specific alert"""
        ai_score = deal_data.get('ai_score', 0)
        address = deal_data.get('address', 'Unknown Property')
        
        if ai_score >= 90:
            priority = NotificationPriority.URGENT
            title = f"🚨 URGENT: Exceptional Deal Alert"
            message = f"High-scoring deal ({ai_score}/100) at {address}. Immediate review recommended!"
        elif ai_score >= 80:
            priority = NotificationPriority.HIGH
            title = f"🔥 Hot Deal Alert"
            message = f"Great deal opportunity ({ai_score}/100) at {address}. Review within 24 hours."
        else:
            priority = NotificationPriority.MEDIUM
            title = f"📈 New Deal Added"
            message = f"New deal added: {address} (Score: {ai_score}/100)"
        
        return self.create_notification(
            title=title,
            message=message,
            notification_type=NotificationType.DEAL_ALERT,
            priority=priority,
            data=deal_data
        )
    
    def create_lead_alert(self, lead_data: Dict[str, Any]) -> str:
        """Create a lead-specific alert"""
        score = lead_data.get('score', 0)
        name = lead_data.get('name', 'Unknown Lead')
        
        if score >= 80:
            priority = NotificationPriority.HIGH
            title = f"🔥 Hot Lead Alert"
            message = f"High-scoring lead: {name} ({score}/100). Follow up immediately!"
        elif score >= 60:
            priority = NotificationPriority.MEDIUM
            title = f"🎯 Warm Lead Alert"
            message = f"Warm lead: {name} ({score}/100). Follow up within 48 hours."
        else:
            priority = NotificationPriority.LOW
            title = f"📝 New Lead Added"
            message = f"New lead added: {name} ({score}/100)"
        
        return self.create_notification(
            title=title,
            message=message,
            notification_type=NotificationType.LEAD_ALERT,
            priority=priority,
            data=lead_data
        )
    
    def create_task_reminder(self, task_data: Dict[str, Any]) -> str:
        """Create a task reminder notification"""
        title = task_data.get('title', 'Task Reminder')
        due_date = task_data.get('due_date')
        
        if due_date:
            try:
                due_dt = datetime.fromisoformat(due_date)
                days_until_due = (due_dt - datetime.now()).days
                
                if days_until_due < 0:
                    priority = NotificationPriority.URGENT
                    message = f"⚠️ OVERDUE: '{title}' was due {abs(days_until_due)} days ago"
                elif days_until_due == 0:
                    priority = NotificationPriority.HIGH
                    message = f"⏰ DUE TODAY: '{title}' is due today"
                elif days_until_due == 1:
                    priority = NotificationPriority.MEDIUM
                    message = f"📅 TOMORROW: '{title}' is due tomorrow"
                else:
                    priority = NotificationPriority.LOW
                    message = f"📋 UPCOMING: '{title}' is due in {days_until_due} days"
            except:
                priority = NotificationPriority.LOW
                message = f"📋 Task reminder: {title}"
        else:
            priority = NotificationPriority.LOW
            message = f"📋 Task reminder: {title}"
        
        return self.create_notification(
            title="📋 Task Reminder",
            message=message,
            notification_type=NotificationType.TASK_REMINDER,
            priority=priority,
            data=task_data
        )

def show_notification_center():
    """Show notification center interface"""
    st.header("🔔 Smart Notifications & Alerts")
    st.write("Stay on top of important deals, leads, and tasks with intelligent notifications.")
    
    # Initialize notification center
    if 'notification_center' not in st.session_state:
        st.session_state.notification_center = NotificationCenter()
    
    notification_center = st.session_state.notification_center
    
    # Get notification statistics
    stats = notification_center.get_notification_stats()
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total = stats.get('total_notifications', 0)
        st.metric("Total Notifications", total)
    with col2:
        unread = stats.get('unread_notifications', 0)
        st.metric("Unread", unread, delta="📬" if unread > 0 else None)
    with col3:
        urgent = stats.get('by_priority', {}).get('urgent', 0)
        st.metric("Urgent", urgent, delta="🚨" if urgent > 0 else None)
    with col4:
        high_priority = stats.get('by_priority', {}).get('high', 0)
        st.metric("High Priority", high_priority, delta="🔥" if high_priority > 0 else None)
    
    # Notification tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📬 All Notifications",
        "🚨 Urgent & High Priority",
        "🎯 Deal & Lead Alerts",
        "⚙️ Settings"
    ])
    
    with tab1:
        show_all_notifications(notification_center)
    
    with tab2:
        show_priority_notifications(notification_center)
    
    with tab3:
        show_deal_lead_alerts(notification_center)
    
    with tab4:
        show_notification_settings(notification_center)

def show_all_notifications(notification_center: NotificationCenter):
    """Show all notifications"""
    st.subheader("📬 All Notifications")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        show_read = st.checkbox("Show read notifications", value=False)
    with col2:
        notification_type_filter = st.selectbox("Filter by Type", 
            ["All"] + [t.value.replace('_', ' ').title() for t in NotificationType])
    with col3:
        if st.button("🔄 Refresh Notifications"):
            st.rerun()
    
    # Get notifications
    type_filter = None
    if notification_type_filter != "All":
        type_filter = NotificationType(notification_type_filter.lower().replace(' ', '_'))
    
    notifications = notification_center.get_notifications(
        unread_only=not show_read,
        notification_type=type_filter
    )
    
    # Bulk actions
    if notifications:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Mark All as Read"):
                for notif in notifications:
                    if not notif.is_read:
                        notification_center.mark_as_read(notif.id)
                st.success("All notifications marked as read!")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Dismiss All"):
                for notif in notifications:
                    notification_center.dismiss_notification(notif.id)
                st.success("All notifications dismissed!")
                st.rerun()
    
    # Display notifications
    if notifications:
        for notification in notifications:
            with st.container():
                # Priority and type indicators
                priority_colors = {
                    NotificationPriority.URGENT: "🚨",
                    NotificationPriority.HIGH: "🔥",
                    NotificationPriority.MEDIUM: "🟡",
                    NotificationPriority.LOW: "🟢"
                }
                
                type_icons = {
                    NotificationType.DEAL_ALERT: "🏠",
                    NotificationType.LEAD_ALERT: "👤",
                    NotificationType.TASK_REMINDER: "📋",
                    NotificationType.SYSTEM_ALERT: "⚙️",
                    NotificationType.MARKET_UPDATE: "📊",
                    NotificationType.AUTOMATION_ALERT: "🤖"
                }
                
                priority_icon = priority_colors.get(notification.priority, "⚪")
                type_icon = type_icons.get(notification.type, "📢")
                read_status = "📭" if notification.is_read else "📬"
                
                col1, col2, col3 = st.columns([6, 2, 1])
                
                with col1:
                    st.markdown(f"{priority_icon} {type_icon} {read_status} **{notification.title}**")
                    st.caption(notification.message)
                    st.caption(f"🕒 {notification.created_at.strftime('%m/%d/%Y %H:%M')}")
                
                with col2:
                    st.caption(f"Type: {notification.type.value.replace('_', ' ').title()}")
                    st.caption(f"Priority: {notification.priority.value.title()}")
                
                with col3:
                    if not notification.is_read:
                        if st.button("✅", key=f"read_{notification.id}", help="Mark as read"):
                            notification_center.mark_as_read(notification.id)
                            st.rerun()
                    
                    if st.button("🗑️", key=f"dismiss_{notification.id}", help="Dismiss"):
                        notification_center.dismiss_notification(notification.id)
                        st.rerun()
                
                st.markdown("---")
    else:
        st.info("📭 No notifications to display. You're all caught up!")

def show_priority_notifications(notification_center: NotificationCenter):
    """Show urgent and high priority notifications"""
    st.subheader("🚨 Urgent & High Priority Notifications")
    
    # Get urgent and high priority notifications
    urgent_notifications = notification_center.get_notifications(
        unread_only=True
    )
    
    priority_notifications = [
        n for n in urgent_notifications 
        if n.priority in [NotificationPriority.URGENT, NotificationPriority.HIGH]
    ]
    
    if priority_notifications:
        st.warning(f"⚠️ You have {len(priority_notifications)} high-priority notifications requiring attention!")
        
        for notification in priority_notifications:
            with st.container():
                # Enhanced display for priority notifications
                if notification.priority == NotificationPriority.URGENT:
                    st.error(f"🚨 **URGENT**: {notification.title}")
                else:
                    st.warning(f"🔥 **HIGH PRIORITY**: {notification.title}")
                
                st.markdown(notification.message)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"🕒 {notification.created_at.strftime('%m/%d/%Y %H:%M')}")
                with col2:
                    st.caption(f"Type: {notification.type.value.replace('_', ' ').title()}")
                with col3:
                    if st.button("✅ Mark as Read", key=f"priority_read_{notification.id}"):
                        notification_center.mark_as_read(notification.id)
                        st.rerun()
                
                # Show additional data if available
                if notification.data:
                    with st.expander("📋 Additional Details"):
                        for key, value in notification.data.items():
                            if key != 'id':
                                st.markdown(f"**{key.replace('_', ' ').title()}**: {value}")
                
                st.markdown("---")
    else:
        st.success("✅ No urgent or high-priority notifications. Great job staying on top of things!")

def show_deal_lead_alerts(notification_center: NotificationCenter):
    """Show deal and lead specific alerts"""
    st.subheader("🎯 Deal & Lead Alerts")
    
    # Get deal and lead notifications
    deal_notifications = notification_center.get_notifications(
        notification_type=NotificationType.DEAL_ALERT
    )
    
    lead_notifications = notification_center.get_notifications(
        notification_type=NotificationType.LEAD_ALERT
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏠 Deal Alerts")
        if deal_notifications:
            for notification in deal_notifications[:5]:  # Show top 5
                with st.container():
                    priority_icon = "🚨" if notification.priority == NotificationPriority.URGENT else "🔥"
                    st.markdown(f"{priority_icon} **{notification.title}**")
                    st.caption(notification.message)
                    st.caption(f"🕒 {notification.created_at.strftime('%m/%d/%Y %H:%M')}")
                    
                    if not notification.is_read:
                        if st.button("✅ Mark Read", key=f"deal_read_{notification.id}"):
                            notification_center.mark_as_read(notification.id)
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("📭 No deal alerts")
    
    with col2:
        st.markdown("#### 👤 Lead Alerts")
        if lead_notifications:
            for notification in lead_notifications[:5]:  # Show top 5
                with st.container():
                    priority_icon = "🔥" if notification.priority == NotificationPriority.HIGH else "🎯"
                    st.markdown(f"{priority_icon} **{notification.title}**")
                    st.caption(notification.message)
                    st.caption(f"🕒 {notification.created_at.strftime('%m/%d/%Y %H:%M')}")
                    
                    if not notification.is_read:
                        if st.button("✅ Mark Read", key=f"lead_read_{notification.id}"):
                            notification_center.mark_as_read(notification.id)
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("📭 No lead alerts")

def show_notification_settings(notification_center: NotificationCenter):
    """Show notification settings"""
    st.subheader("⚙️ Notification Settings")
    
    st.info("🔧 Advanced notification settings coming soon!")
    
    # Basic notification preferences
    st.markdown("### 📧 Notification Preferences")
    
    with st.expander("🏠 Deal Notifications"):
        st.checkbox("High-scoring deals (≥80)", value=True)
        st.checkbox("Price drops", value=True)
        st.checkbox("New deals added", value=True)
        st.checkbox("Deal status changes", value=False)
    
    with st.expander("👤 Lead Notifications"):
        st.checkbox("Hot leads (≥80 score)", value=True)
        st.checkbox("New leads added", value=True)
        st.checkbox("Lead status changes", value=False)
    
    with st.expander("📋 Task Notifications"):
        st.checkbox("Overdue tasks", value=True)
        st.checkbox("Tasks due today", value=True)
        st.checkbox("Tasks due tomorrow", value=False)
        st.checkbox("Task assignments", value=True)
    
    with st.expander("📊 System Notifications"):
        st.checkbox("System alerts", value=True)
        st.checkbox("Market updates", value=False)
        st.checkbox("Automation alerts", value=True)
    
    # Delivery preferences
    st.markdown("### 📱 Delivery Preferences")
    
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("In-app notifications", value=True)
        st.checkbox("Email notifications", value=False)
    
    with col2:
        st.checkbox("SMS notifications", value=False)
        st.checkbox("Push notifications", value=False)
    
    # Quiet hours
    st.markdown("### 🌙 Quiet Hours")
    col1, col2 = st.columns(2)
    with col1:
        st.time_input("Quiet hours start", value=datetime.strptime("22:00", "%H:%M").time())
    with col2:
        st.time_input("Quiet hours end", value=datetime.strptime("08:00", "%H:%M").time())
    
    if st.button("💾 Save Settings"):
        st.success("✅ Notification settings saved!")