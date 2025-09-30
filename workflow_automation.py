"""
Advanced Workflow Automation System for NXTRIX CRM
Automates deal progression, client communication, and task management
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import sqlite3
import uuid
from communication_services import CommunicationManager

class TriggerType(Enum):
    DEAL_STAGE_CHANGE = "deal_stage_change"
    NEW_DEAL_ADDED = "new_deal_added"
    CLIENT_ADDED = "client_added"
    FOLLOW_UP_DUE = "follow_up_due"
    HIGH_AI_SCORE = "high_ai_score"
    TIME_BASED = "time_based"
    MANUAL = "manual"

class ActionType(Enum):
    SEND_EMAIL = "send_email"
    SEND_SMS = "send_sms"
    CREATE_TASK = "create_task"
    UPDATE_DEAL_STAGE = "update_deal_stage"
    SCHEDULE_FOLLOW_UP = "schedule_follow_up"
    SEND_NOTIFICATION = "send_notification"
    CREATE_DOCUMENT = "create_document"

@dataclass
class AutomationRule:
    """Automation rule definition"""
    id: str
    name: str
    description: str
    trigger_type: TriggerType
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_executed: Optional[datetime] = None
    execution_count: int = 0

@dataclass
class AutomationExecution:
    """Record of automation execution"""
    id: str
    rule_id: str
    trigger_data: Dict[str, Any]
    executed_at: datetime
    status: str  # success, failed, partial
    actions_completed: int
    total_actions: int
    error_message: Optional[str] = None

class WorkflowAutomationSystem:
    """Advanced workflow automation system"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.comm_manager = None
        self.init_database()
        self.setup_default_rules()
    
    def init_database(self):
        """Initialize automation database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS automation_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    trigger_type TEXT NOT NULL,
                    trigger_conditions TEXT,
                    actions TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_executed TIMESTAMP,
                    execution_count INTEGER DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS automation_executions (
                    id TEXT PRIMARY KEY,
                    rule_id TEXT NOT NULL,
                    trigger_data TEXT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL,
                    actions_completed INTEGER DEFAULT 0,
                    total_actions INTEGER DEFAULT 0,
                    error_message TEXT,
                    FOREIGN KEY (rule_id) REFERENCES automation_rules (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS automated_tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    assigned_to TEXT,
                    due_date TIMESTAMP,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'pending',
                    deal_id TEXT,
                    client_id TEXT,
                    created_by_automation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error initializing automation database: {e}")
    
    def setup_default_rules(self):
        """Setup default automation rules"""
        default_rules = [
            {
                "name": "Welcome New Client",
                "description": "Send welcome email when new client is added",
                "trigger_type": TriggerType.CLIENT_ADDED,
                "trigger_conditions": {},
                "actions": [
                    {
                        "type": ActionType.SEND_EMAIL,
                        "template": "welcome_client",
                        "delay_minutes": 0
                    }
                ]
            },
            {
                "name": "High Score Deal Alert",
                "description": "Send SMS alert for deals with AI score > 90",
                "trigger_type": TriggerType.HIGH_AI_SCORE,
                "trigger_conditions": {"min_score": 90},
                "actions": [
                    {
                        "type": ActionType.SEND_SMS,
                        "template": "high_score_alert",
                        "delay_minutes": 5
                    }
                ]
            },
            {
                "name": "Deal Analysis Complete",
                "description": "Create follow-up task when deal moves to 'Analyzing' stage",
                "trigger_type": TriggerType.DEAL_STAGE_CHANGE,
                "trigger_conditions": {"to_stage": "Analyzing"},
                "actions": [
                    {
                        "type": ActionType.CREATE_TASK,
                        "title": "Review Deal Analysis",
                        "priority": "high",
                        "delay_minutes": 60
                    }
                ]
            },
            {
                "name": "Weekly Follow-up Reminder",
                "description": "Send follow-up reminders for stale deals",
                "trigger_type": TriggerType.TIME_BASED,
                "trigger_conditions": {"frequency": "weekly", "day": "monday"},
                "actions": [
                    {
                        "type": ActionType.SEND_EMAIL,
                        "template": "follow_up_reminder",
                        "delay_minutes": 0
                    }
                ]
            }
        ]
        
        # Insert default rules if they don't exist
        for rule_data in default_rules:
            if not self.get_rule_by_name(rule_data["name"]):
                rule = AutomationRule(
                    id=str(uuid.uuid4()),
                    name=rule_data["name"],
                    description=rule_data["description"],
                    trigger_type=rule_data["trigger_type"],
                    trigger_conditions=rule_data["trigger_conditions"],
                    actions=rule_data["actions"]
                )
                self.save_rule(rule)
    
    def get_rule_by_name(self, name: str) -> Optional[AutomationRule]:
        """Get automation rule by name"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM automation_rules WHERE name = ?", (name,))
            row = cursor.fetchone()
            
            if row:
                # Handle invalid trigger_type values
                try:
                    trigger_type = TriggerType(row[3])
                except ValueError:
                    # If trigger_type is invalid, default to MANUAL
                    trigger_type = TriggerType.MANUAL
                    print(f"Warning: Invalid trigger_type '{row[3]}' for rule '{row[1]}', defaulting to MANUAL")
                
                return AutomationRule(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    trigger_type=trigger_type,
                    trigger_conditions=json.loads(row[4]) if row[4] else {},
                    actions=json.loads(row[5]) if row[5] else [],
                    is_active=bool(row[6]),
                    created_at=datetime.fromisoformat(row[7]),
                    last_executed=datetime.fromisoformat(row[8]) if row[8] else None,
                    execution_count=row[9] or 0
                )
            
            conn.close()
            return None
            
        except Exception as e:
            st.error(f"Error retrieving rule: {e}")
            return None
    
    def save_rule(self, rule: AutomationRule):
        """Save automation rule to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO automation_rules 
                (id, name, description, trigger_type, trigger_conditions, actions, 
                 is_active, created_at, last_executed, execution_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rule.id,
                rule.name,
                rule.description,
                rule.trigger_type.value,
                json.dumps(rule.trigger_conditions),
                json.dumps([{k: v.value if isinstance(v, Enum) else v for k, v in action.items()} for action in rule.actions]),
                rule.is_active,
                rule.created_at.isoformat(),
                rule.last_executed.isoformat() if rule.last_executed else None,
                rule.execution_count
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error saving rule: {e}")
    
    def get_all_rules(self) -> List[AutomationRule]:
        """Get all automation rules"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM automation_rules ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            rules = []
            for row in rows:
                rule = AutomationRule(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    trigger_type=TriggerType(row[3]),
                    trigger_conditions=json.loads(row[4]) if row[4] else {},
                    actions=json.loads(row[5]) if row[5] else [],
                    is_active=bool(row[6]),
                    created_at=datetime.fromisoformat(row[7]),
                    last_executed=datetime.fromisoformat(row[8]) if row[8] else None,
                    execution_count=row[9] or 0
                )
                rules.append(rule)
            
            conn.close()
            return rules
            
        except Exception as e:
            st.error(f"Error retrieving rules: {e}")
            return []
    
    def execute_rule(self, rule: AutomationRule, trigger_data: Dict[str, Any]) -> AutomationExecution:
        """Execute an automation rule"""
        execution = AutomationExecution(
            id=str(uuid.uuid4()),
            rule_id=rule.id,
            trigger_data=trigger_data,
            executed_at=datetime.now(),
            status="running",
            actions_completed=0,
            total_actions=len(rule.actions)
        )
        
        try:
            for i, action in enumerate(rule.actions):
                try:
                    self._execute_action(action, trigger_data)
                    execution.actions_completed += 1
                except Exception as e:
                    execution.error_message = str(e)
                    execution.status = "partial" if execution.actions_completed > 0 else "failed"
                    break
            
            if execution.actions_completed == execution.total_actions:
                execution.status = "success"
            
            # Update rule execution stats
            rule.last_executed = execution.executed_at
            rule.execution_count += 1
            self.save_rule(rule)
            
            # Save execution record
            self._save_execution(execution)
            
        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
        
        return execution
    
    def _execute_action(self, action: Dict[str, Any], trigger_data: Dict[str, Any]):
        """Execute a specific action"""
        action_type = ActionType(action["type"])
        
        if action_type == ActionType.SEND_EMAIL:
            self._send_automated_email(action, trigger_data)
        elif action_type == ActionType.SEND_SMS:
            self._send_automated_sms(action, trigger_data)
        elif action_type == ActionType.CREATE_TASK:
            self._create_automated_task(action, trigger_data)
        elif action_type == ActionType.SCHEDULE_FOLLOW_UP:
            self._schedule_follow_up(action, trigger_data)
        # Add more action types as needed
    
    def _send_automated_email(self, action: Dict[str, Any], trigger_data: Dict[str, Any]):
        """Send automated email"""
        if self.comm_manager and self.comm_manager.email_service.enabled:
            template = action.get("template", "default")
            recipient = trigger_data.get("email")
            
            if recipient:
                subject, message = self._get_email_template(template, trigger_data)
                result = self.comm_manager.send_email(recipient, subject, message, "NXTRIX CRM")
                if not result.success:
                    raise Exception(f"Email failed: {result.error_message}")
    
    def _send_automated_sms(self, action: Dict[str, Any], trigger_data: Dict[str, Any]):
        """Send automated SMS"""
        if self.comm_manager and self.comm_manager.sms_service.enabled:
            template = action.get("template", "default")
            recipient = trigger_data.get("phone")
            
            if recipient:
                message = self._get_sms_template(template, trigger_data)
                result = self.comm_manager.send_sms(recipient, message)
                if not result.success:
                    raise Exception(f"SMS failed: {result.error_message}")
    
    def _create_automated_task(self, action: Dict[str, Any], trigger_data: Dict[str, Any]):
        """Create automated task"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            task_id = str(uuid.uuid4())
            title = action.get("title", "Automated Task")
            description = action.get("description", "")
            priority = action.get("priority", "medium")
            
            cursor.execute('''
                INSERT INTO automated_tasks 
                (id, title, description, priority, deal_id, client_id, created_by_automation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_id,
                title,
                description,
                priority,
                trigger_data.get("deal_id"),
                trigger_data.get("client_id"),
                "automation_system"
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            raise Exception(f"Task creation failed: {e}")
    
    def _get_email_template(self, template: str, data: Dict[str, Any]) -> tuple:
        """Get email template with data substitution"""
        templates = {
            "welcome_client": (
                "Welcome to NXTRIX CRM",
                f"Dear {data.get('name', 'Valued Client')},\n\nWelcome to NXTRIX CRM! We're excited to work with you on your real estate investment journey.\n\nBest regards,\nNXTRIX Team"
            ),
            "high_score_alert": (
                "High-Scoring Deal Alert",
                f"🚨 NEW HIGH-SCORING DEAL ALERT!\n\nProperty: {data.get('address', 'N/A')}\nAI Score: {data.get('ai_score', 'N/A')}/100\nExpected ROI: {data.get('roi', 'N/A')}%\n\nReview immediately!"
            ),
            "follow_up_reminder": (
                "Follow-up Reminder",
                f"Don't forget to follow up on: {data.get('subject', 'pending items')}\n\nScheduled for: {data.get('follow_up_date', 'today')}"
            )
        }
        
        return templates.get(template, ("Automated Message", "This is an automated message from NXTRIX CRM."))
    
    def _get_sms_template(self, template: str, data: Dict[str, Any]) -> str:
        """Get SMS template with data substitution"""
        templates = {
            "high_score_alert": f"🚨 HIGH-SCORE DEAL: {data.get('address', 'Property')} - {data.get('ai_score', 'N/A')}/100 AI Score. Review now!",
            "follow_up_reminder": f"Reminder: Follow up on {data.get('subject', 'pending item')} today.",
            "default": "Automated notification from NXTRIX CRM"
        }
        
        return templates.get(template, templates["default"])
    
    def _save_execution(self, execution: AutomationExecution):
        """Save execution record to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO automation_executions 
                (id, rule_id, trigger_data, executed_at, status, actions_completed, total_actions, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                execution.id,
                execution.rule_id,
                json.dumps(execution.trigger_data),
                execution.executed_at.isoformat(),
                execution.status,
                execution.actions_completed,
                execution.total_actions,
                execution.error_message
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error saving execution: {e}")
    
    def get_automation_stats(self) -> Dict[str, Any]:
        """Get automation statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get rule stats
            cursor.execute("SELECT COUNT(*), SUM(CASE WHEN is_active THEN 1 ELSE 0 END) FROM automation_rules")
            total_rules, active_rules = cursor.fetchone()
            
            # Get execution stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_executions,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_executions,
                    SUM(actions_completed) as total_actions_completed
                FROM automation_executions 
                WHERE DATE(executed_at) >= DATE('now', '-30 days')
            """)
            exec_stats = cursor.fetchone()
            
            # Get recent executions
            cursor.execute("""
                SELECT ar.name, ae.status, ae.executed_at 
                FROM automation_executions ae
                JOIN automation_rules ar ON ae.rule_id = ar.id
                ORDER BY ae.executed_at DESC
                LIMIT 10
            """)
            recent_executions = cursor.fetchall()
            
            conn.close()
            
            success_rate = (exec_stats[1] / exec_stats[0] * 100) if exec_stats[0] > 0 else 0
            
            return {
                "total_rules": total_rules or 0,
                "active_rules": active_rules or 0,
                "total_executions": exec_stats[0] or 0,
                "successful_executions": exec_stats[1] or 0,
                "success_rate": success_rate,
                "total_actions_completed": exec_stats[2] or 0,
                "recent_executions": recent_executions
            }
            
        except Exception as e:
            st.error(f"Error getting automation stats: {e}")
            return {}

def show_workflow_automation():
    """Show workflow automation interface"""
    st.header("⚡ Workflow Automation Center")
    st.write("Automate your deal workflow, client communication, and task management.")
    
    # Initialize automation system
    if 'automation_system' not in st.session_state:
        st.session_state.automation_system = WorkflowAutomationSystem()
    
    automation_system = st.session_state.automation_system
    
    # Try to set communication manager
    try:
        from communication_services import CommunicationManager
        automation_system.comm_manager = CommunicationManager()
    except:
        pass
    
    # Get automation stats
    stats = automation_system.get_automation_stats()
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Rules", stats.get("active_rules", 0))
    with col2:
        st.metric("Total Executions", stats.get("total_executions", 0))
    with col3:
        st.metric("Success Rate", f"{stats.get('success_rate', 0):.1f}%")
    with col4:
        st.metric("Actions Completed", stats.get("total_actions_completed", 0))
    
    # Automation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Automation Rules",
        "➕ Create Rule",
        "📊 Execution History",
        "⚙️ Settings"
    ])
    
    with tab1:
        show_automation_rules(automation_system)
    
    with tab2:
        show_create_rule(automation_system)
    
    with tab3:
        show_execution_history(automation_system)
    
    with tab4:
        show_automation_settings(automation_system)

def show_automation_rules(automation_system: WorkflowAutomationSystem):
    """Show existing automation rules"""
    st.subheader("📋 Current Automation Rules")
    
    rules = automation_system.get_all_rules()
    
    if rules:
        for rule in rules:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    status_icon = "🟢" if rule.is_active else "🔴"
                    st.markdown(f"{status_icon} **{rule.name}**")
                    st.caption(rule.description)
                
                with col2:
                    st.caption(f"Trigger: {rule.trigger_type.value.replace('_', ' ').title()}")
                    st.caption(f"Actions: {len(rule.actions)}")
                
                with col3:
                    st.caption(f"Executed: {rule.execution_count}")
                    if rule.last_executed:
                        st.caption(f"Last: {rule.last_executed.strftime('%m/%d/%Y')}")
                
                with col4:
                    if st.button("⚙️", key=f"edit_{rule.id}", help="Edit rule"):
                        st.session_state.edit_rule_id = rule.id
                        st.rerun()
                    
                st.markdown("---")
    else:
        st.info("📝 No automation rules found. Create your first rule to get started!")

def show_create_rule(automation_system: WorkflowAutomationSystem):
    """Show create automation rule interface"""
    st.subheader("➕ Create New Automation Rule")
    
    with st.form("create_automation_rule"):
        # Basic rule info
        rule_name = st.text_input("Rule Name*", placeholder="Welcome New Client")
        rule_description = st.text_area("Description", placeholder="Send welcome email when new client is added")
        
        # Trigger configuration
        st.markdown("### 🎯 Trigger Configuration")
        trigger_type = st.selectbox("Trigger Type", [
            "New Deal Added",
            "Deal Stage Change",
            "Client Added",
            "High AI Score",
            "Follow-up Due",
            "Time Based"
        ])
        
        trigger_conditions = {}
        if trigger_type == "Deal Stage Change":
            trigger_conditions["to_stage"] = st.selectbox("To Stage", [
                "New", "Analyzing", "Under Contract", "Negotiating", "Closed", "Passed"
            ])
        elif trigger_type == "High AI Score":
            trigger_conditions["min_score"] = st.slider("Minimum AI Score", 0, 100, 80)
        
        # Action configuration
        st.markdown("### ⚡ Actions")
        action_type = st.selectbox("Action Type", [
            "Send Email",
            "Send SMS",
            "Create Task",
            "Schedule Follow-up"
        ])
        
        actions = []
        if action_type == "Send Email":
            email_template = st.selectbox("Email Template", [
                "welcome_client",
                "high_score_alert",
                "follow_up_reminder",
                "custom"
            ])
            actions.append({
                "type": ActionType.SEND_EMAIL,
                "template": email_template
            })
        elif action_type == "Send SMS":
            sms_template = st.selectbox("SMS Template", [
                "high_score_alert",
                "follow_up_reminder",
                "custom"
            ])
            actions.append({
                "type": ActionType.SEND_SMS,
                "template": sms_template
            })
        elif action_type == "Create Task":
            task_title = st.text_input("Task Title", "Review Deal Analysis")
            task_priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"])
            actions.append({
                "type": ActionType.CREATE_TASK,
                "title": task_title,
                "priority": task_priority
            })
        
        submitted = st.form_submit_button("✅ Create Rule", type="primary")
        
        if submitted and rule_name:
            # Map trigger type to enum
            trigger_mapping = {
                "New Deal Added": TriggerType.NEW_DEAL_ADDED,
                "Deal Stage Change": TriggerType.DEAL_STAGE_CHANGE,
                "Client Added": TriggerType.CLIENT_ADDED,
                "High AI Score": TriggerType.HIGH_AI_SCORE,
                "Follow-up Due": TriggerType.FOLLOW_UP_DUE,
                "Time Based": TriggerType.TIME_BASED
            }
            
            rule = AutomationRule(
                id=str(uuid.uuid4()),
                name=rule_name,
                description=rule_description,
                trigger_type=trigger_mapping[trigger_type],
                trigger_conditions=trigger_conditions,
                actions=actions
            )
            
            automation_system.save_rule(rule)
            st.success(f"✅ Automation rule '{rule_name}' created successfully!")
            st.rerun()

def show_execution_history(automation_system: WorkflowAutomationSystem):
    """Show automation execution history"""
    st.subheader("📊 Execution History")
    
    stats = automation_system.get_automation_stats()
    recent_executions = stats.get("recent_executions", [])
    
    if recent_executions:
        st.markdown("### Recent Executions")
        
        for execution in recent_executions:
            rule_name, status, executed_at = execution
            
            status_icon = {"success": "✅", "failed": "❌", "partial": "⚠️"}.get(status, "❓")
            
            col1, col2, col3 = st.columns([3, 1, 2])
            
            with col1:
                st.markdown(f"{status_icon} **{rule_name}**")
            
            with col2:
                st.caption(status.title())
            
            with col3:
                exec_time = datetime.fromisoformat(executed_at)
                st.caption(exec_time.strftime("%m/%d/%Y %H:%M"))
    else:
        st.info("📭 No execution history found.")

def show_automation_settings(automation_system: WorkflowAutomationSystem):
    """Show automation settings"""
    st.subheader("⚙️ Automation Settings")
    
    st.info("🔧 Advanced automation settings coming soon!")
    
    # Basic settings
    with st.expander("📧 Communication Settings"):
        st.checkbox("Enable Email Automation", value=True)
        st.checkbox("Enable SMS Automation", value=True)
        st.number_input("Max executions per hour", value=100, min_value=1)
    
    with st.expander("🎯 Trigger Settings"):
        st.checkbox("Enable time-based triggers", value=True)
        st.checkbox("Enable deal stage triggers", value=True)
        st.number_input("Trigger check interval (minutes)", value=5, min_value=1)
    
    with st.expander("📊 Logging & Analytics"):
        st.checkbox("Enable execution logging", value=True)
        st.checkbox("Enable performance analytics", value=True)
        st.number_input("Log retention days", value=30, min_value=1)