"""
NxTrix CRM - Phase 3D: Advanced Automation System
Comprehensive automation workflows for email marketing, CRM processes, document generation, and contract management
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, List, Optional, Tuple, Any
import re
from dataclasses import dataclass, asdict
import asyncio
import time
import threading
from io import BytesIO
import base64
from jinja2 import Template
import zipfile
import os
from pathlib import Path

# Document generation imports
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    st.warning("ReportLab not installed. Document generation will be limited.")

@dataclass
class AutomationRule:
    """Data class for automation rules"""
    id: str
    name: str
    trigger_type: str  # 'deal_status_change', 'time_based', 'data_change', 'manual'
    trigger_conditions: Dict
    actions: List[Dict]
    is_active: bool
    created_at: datetime
    last_executed: Optional[datetime] = None
    execution_count: int = 0

@dataclass
class EmailTemplate:
    """Data class for email templates"""
    id: str
    name: str
    subject: str
    body: str
    template_type: str  # 'deal_update', 'investor_alert', 'follow_up', 'marketing'
    variables: List[str]
    is_active: bool
    created_at: datetime

@dataclass
class DocumentTemplate:
    """Data class for document templates"""
    id: str
    name: str
    template_type: str  # 'contract', 'analysis', 'report', 'invoice'
    content: str
    variables: List[str]
    is_active: bool
    created_at: datetime

@dataclass
class WorkflowStep:
    """Data class for workflow steps"""
    id: str
    workflow_id: str
    step_order: int
    step_type: str  # 'email', 'task', 'document', 'api_call', 'delay'
    step_config: Dict
    conditions: Dict
    is_active: bool

class AdvancedAutomationSystem:
    """Comprehensive Automation System for NxTrix CRM"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.automation_rules = []
        self.email_templates = []
        self.document_templates = []
        self.workflows = []
        self.execution_log = []
        self.setup_automation_tables()
        self.load_automation_data()
        
    def setup_automation_tables(self):
        """Setup automation-related database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Automation rules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS automation_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    trigger_type TEXT NOT NULL,
                    trigger_conditions TEXT,
                    actions TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_executed TIMESTAMP,
                    execution_count INTEGER DEFAULT 0
                )
            """)
            
            # Email templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    template_type TEXT NOT NULL,
                    variables TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Document templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    template_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    variables TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Workflows table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflows (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    trigger_type TEXT NOT NULL,
                    trigger_conditions TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Workflow steps table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_steps (
                    id TEXT PRIMARY KEY,
                    workflow_id TEXT,
                    step_order INTEGER,
                    step_type TEXT NOT NULL,
                    step_config TEXT,
                    conditions TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (workflow_id) REFERENCES workflows (id)
                )
            """)
            
            # Automation execution log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS automation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    automation_type TEXT NOT NULL,
                    automation_id TEXT,
                    execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT,
                    details TEXT,
                    error_message TEXT
                )
            """)
            
            # Email campaigns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_campaigns (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    template_id TEXT,
                    recipient_list TEXT,
                    schedule_time TIMESTAMP,
                    status TEXT DEFAULT 'draft',
                    sent_count INTEGER DEFAULT 0,
                    opened_count INTEGER DEFAULT 0,
                    clicked_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (template_id) REFERENCES email_templates (id)
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error setting up automation tables: {e}")
    
    def load_automation_data(self):
        """Load automation data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Load automation rules
            rules_df = pd.read_sql_query("SELECT * FROM automation_rules", conn)
            self.automation_rules = []
            for _, row in rules_df.iterrows():
                rule = AutomationRule(
                    id=row['id'],
                    name=row['name'],
                    trigger_type=row['trigger_type'],
                    trigger_conditions=json.loads(row['trigger_conditions'] or '{}'),
                    actions=json.loads(row['actions'] or '[]'),
                    is_active=bool(row['is_active']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_executed=datetime.fromisoformat(row['last_executed']) if row['last_executed'] else None,
                    execution_count=row['execution_count']
                )
                self.automation_rules.append(rule)
            
            # Load email templates
            templates_df = pd.read_sql_query("SELECT * FROM email_templates", conn)
            self.email_templates = []
            for _, row in templates_df.iterrows():
                template = EmailTemplate(
                    id=row['id'],
                    name=row['name'],
                    subject=row['subject'],
                    body=row['body'],
                    template_type=row['template_type'],
                    variables=json.loads(row['variables'] or '[]'),
                    is_active=bool(row['is_active']),
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                self.email_templates.append(template)
            
            conn.close()
            
        except Exception as e:
            st.error(f"Error loading automation data: {e}")
    
    def create_automation_rule(self, rule: AutomationRule) -> bool:
        """Create a new automation rule"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO automation_rules 
                (id, name, trigger_type, trigger_conditions, actions, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                rule.id,
                rule.name,
                rule.trigger_type,
                json.dumps(rule.trigger_conditions),
                json.dumps(rule.actions),
                rule.is_active,
                rule.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            self.automation_rules.append(rule)
            return True
            
        except Exception as e:
            st.error(f"Error creating automation rule: {e}")
            return False
    
    def execute_automation_rule(self, rule: AutomationRule, context: Dict) -> bool:
        """Execute an automation rule"""
        try:
            if not rule.is_active:
                return False
            
            # Check trigger conditions
            if not self._check_trigger_conditions(rule.trigger_conditions, context):
                return False
            
            # Execute actions
            success = True
            for action in rule.actions:
                action_success = self._execute_action(action, context)
                if not action_success:
                    success = False
            
            # Update execution count and last executed time
            rule.execution_count += 1
            rule.last_executed = datetime.now()
            self._update_rule_execution_stats(rule)
            
            # Log execution
            self._log_automation_execution(
                automation_type='rule',
                automation_id=rule.id,
                status='success' if success else 'partial_failure',
                details=f"Executed {len(rule.actions)} actions"
            )
            
            return success
            
        except Exception as e:
            self._log_automation_execution(
                automation_type='rule',
                automation_id=rule.id,
                status='error',
                error_message=str(e)
            )
            st.error(f"Error executing automation rule {rule.name}: {e}")
            return False
    
    def _check_trigger_conditions(self, conditions: Dict, context: Dict) -> bool:
        """Check if trigger conditions are met"""
        try:
            for condition_key, condition_value in conditions.items():
                if condition_key not in context:
                    return False
                
                if isinstance(condition_value, dict):
                    operator = condition_value.get('operator', 'equals')
                    value = condition_value.get('value')
                    
                    context_value = context[condition_key]
                    
                    if operator == 'equals' and context_value != value:
                        return False
                    elif operator == 'not_equals' and context_value == value:
                        return False
                    elif operator == 'greater_than' and context_value <= value:
                        return False
                    elif operator == 'less_than' and context_value >= value:
                        return False
                    elif operator == 'contains' and value not in str(context_value):
                        return False
                else:
                    if context[condition_key] != condition_value:
                        return False
            
            return True
            
        except Exception as e:
            st.error(f"Error checking trigger conditions: {e}")
            return False
    
    def _execute_action(self, action: Dict, context: Dict) -> bool:
        """Execute a single automation action"""
        try:
            action_type = action.get('type')
            
            if action_type == 'send_email':
                return self._execute_email_action(action, context)
            elif action_type == 'create_task':
                return self._execute_task_action(action, context)
            elif action_type == 'update_deal':
                return self._execute_deal_update_action(action, context)
            elif action_type == 'generate_document':
                return self._execute_document_action(action, context)
            elif action_type == 'api_call':
                return self._execute_api_action(action, context)
            elif action_type == 'delay':
                return self._execute_delay_action(action, context)
            else:
                st.warning(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            st.error(f"Error executing action {action.get('type', 'unknown')}: {e}")
            return False
    
    def _execute_email_action(self, action: Dict, context: Dict) -> bool:
        """Execute email sending action"""
        try:
            template_id = action.get('template_id')
            recipients = action.get('recipients', [])
            
            # Get email template
            template = next((t for t in self.email_templates if t.id == template_id), None)
            if not template:
                st.error(f"Email template {template_id} not found")
                return False
            
            # Replace variables in template
            subject = self._replace_template_variables(template.subject, context)
            body = self._replace_template_variables(template.body, context)
            
            # Send email
            return self.send_email(recipients, subject, body)
            
        except Exception as e:
            st.error(f"Error executing email action: {e}")
            return False
    
    def _execute_task_action(self, action: Dict, context: Dict) -> bool:
        """Execute task creation action"""
        try:
            task_title = self._replace_template_variables(action.get('title', ''), context)
            task_description = self._replace_template_variables(action.get('description', ''), context)
            due_date = action.get('due_date')
            assigned_to = action.get('assigned_to')
            
            # Create task in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tasks (title, description, due_date, assigned_to, status, created_at)
                VALUES (?, ?, ?, ?, 'pending', ?)
            """, (task_title, task_description, due_date, assigned_to, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            st.error(f"Error creating task: {e}")
            return False
    
    def _execute_deal_update_action(self, action: Dict, context: Dict) -> bool:
        """Execute deal update action"""
        try:
            deal_id = context.get('deal_id')
            if not deal_id:
                return False
            
            updates = action.get('updates', {})
            
            # Build update query
            set_clauses = []
            values = []
            
            for field, value in updates.items():
                if isinstance(value, str):
                    value = self._replace_template_variables(value, context)
                set_clauses.append(f"{field} = ?")
                values.append(value)
            
            if not set_clauses:
                return False
            
            values.append(deal_id)
            
            # Execute update
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = f"UPDATE deals SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            st.error(f"Error updating deal: {e}")
            return False
    
    def _execute_document_action(self, action: Dict, context: Dict) -> bool:
        """Execute document generation action"""
        try:
            template_id = action.get('template_id')
            output_path = action.get('output_path', '')
            
            # Get document template
            template = next((t for t in self.document_templates if t.id == template_id), None)
            if not template:
                st.error(f"Document template {template_id} not found")
                return False
            
            # Generate document
            return self.generate_document(template, context, output_path)
            
        except Exception as e:
            st.error(f"Error generating document: {e}")
            return False
    
    def _replace_template_variables(self, template_text: str, context: Dict) -> str:
        """Replace template variables with context values"""
        try:
            template = Template(template_text)
            return template.render(**context)
        except Exception as e:
            st.error(f"Error replacing template variables: {e}")
            return template_text
    
    def send_email(self, recipients: List[str], subject: str, body: str, 
                  smtp_server: str = None, smtp_port: int = 587, 
                  username: str = None, password: str = None) -> bool:
        """Send email using SMTP"""
        try:
            # Get email configuration from Streamlit secrets or session state
            smtp_server = smtp_server or st.secrets.get("SMTP_SERVER") or st.session_state.get("smtp_server", "smtp.gmail.com")
            smtp_port = smtp_port or st.secrets.get("SMTP_PORT") or st.session_state.get("smtp_port", 587)
            username = username or st.secrets.get("EMAIL_USERNAME") or st.session_state.get("email_username")
            password = password or st.secrets.get("EMAIL_PASSWORD") or st.session_state.get("email_password")
            
            if not all([username, password]):
                st.warning("Email credentials not configured")
                return False
            
            # Create message
            message = MIMEMultipart()
            message["From"] = username
            message["Subject"] = subject
            
            # Add body to email
            message.attach(MIMEText(body, "html" if "<html>" in body.lower() else "plain"))
            
            # Create SMTP session
            context = ssl.create_default_context()
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)
                server.login(username, password)
                
                # Send email to each recipient
                for recipient in recipients:
                    message["To"] = recipient
                    text = message.as_string()
                    server.sendmail(username, recipient, text)
                    del message["To"]
            
            return True
            
        except Exception as e:
            st.error(f"Error sending email: {e}")
            return False
    
    def create_email_template(self, template: EmailTemplate) -> bool:
        """Create a new email template"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO email_templates 
                (id, name, subject, body, template_type, variables, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template.id,
                template.name,
                template.subject,
                template.body,
                template.template_type,
                json.dumps(template.variables),
                template.is_active,
                template.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            self.email_templates.append(template)
            return True
            
        except Exception as e:
            st.error(f"Error creating email template: {e}")
            return False
    
    def generate_document(self, template: DocumentTemplate, context: Dict, output_path: str = None) -> bool:
        """Generate document from template"""
        try:
            if not REPORTLAB_AVAILABLE:
                st.warning("Document generation requires ReportLab library")
                return False
            
            # Replace variables in template content
            content = self._replace_template_variables(template.content, context)
            
            # Create PDF document
            if output_path:
                doc_path = output_path
            else:
                doc_path = f"generated_documents/{template.template_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(doc_path), exist_ok=True)
            
            # Create PDF
            doc = SimpleDocTemplate(doc_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Add content to PDF
            paragraphs = content.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    story.append(Paragraph(paragraph, styles['Normal']))
                    story.append(Spacer(1, 12))
            
            doc.build(story)
            
            # Store document reference in database
            self._store_generated_document(template.id, doc_path, context.get('deal_id'))
            
            return True
            
        except Exception as e:
            st.error(f"Error generating document: {e}")
            return False
    
    def _store_generated_document(self, template_id: str, file_path: str, deal_id: str = None):
        """Store generated document reference in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generated_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id TEXT,
                    file_path TEXT,
                    deal_id TEXT,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                INSERT INTO generated_documents (template_id, file_path, deal_id)
                VALUES (?, ?, ?)
            """, (template_id, file_path, deal_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error storing document reference: {e}")
    
    def create_email_campaign(self, campaign_data: Dict) -> bool:
        """Create and manage email campaigns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO email_campaigns 
                (id, name, template_id, recipient_list, schedule_time, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                campaign_data['id'],
                campaign_data['name'],
                campaign_data['template_id'],
                json.dumps(campaign_data['recipients']),
                campaign_data.get('schedule_time'),
                'scheduled' if campaign_data.get('schedule_time') else 'draft',
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            st.error(f"Error creating email campaign: {e}")
            return False
    
    def execute_scheduled_campaigns(self):
        """Execute scheduled email campaigns"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get scheduled campaigns that are due
            scheduled_campaigns = pd.read_sql_query("""
                SELECT * FROM email_campaigns 
                WHERE status = 'scheduled' 
                AND schedule_time <= ?
            """, conn, params=[datetime.now().isoformat()])
            
            for _, campaign in scheduled_campaigns.iterrows():
                self._execute_email_campaign(campaign)
            
            conn.close()
            
        except Exception as e:
            st.error(f"Error executing scheduled campaigns: {e}")
    
    def _execute_email_campaign(self, campaign):
        """Execute a single email campaign"""
        try:
            # Get email template
            template = next((t for t in self.email_templates if t.id == campaign['template_id']), None)
            if not template:
                return False
            
            recipients = json.loads(campaign['recipient_list'])
            
            # Send emails
            sent_count = 0
            for recipient in recipients:
                # Create context for each recipient (could include personalized data)
                context = {'recipient_email': recipient}
                
                subject = self._replace_template_variables(template.subject, context)
                body = self._replace_template_variables(template.body, context)
                
                if self.send_email([recipient], subject, body):
                    sent_count += 1
            
            # Update campaign status
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE email_campaigns 
                SET status = 'sent', sent_count = ?
                WHERE id = ?
            """, (sent_count, campaign['id']))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            st.error(f"Error executing email campaign: {e}")
            return False
    
    def _update_rule_execution_stats(self, rule: AutomationRule):
        """Update automation rule execution statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE automation_rules 
                SET execution_count = ?, last_executed = ?
                WHERE id = ?
            """, (rule.execution_count, rule.last_executed.isoformat(), rule.id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error updating rule execution stats: {e}")
    
    def _log_automation_execution(self, automation_type: str, automation_id: str, 
                                status: str, details: str = None, error_message: str = None):
        """Log automation execution"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO automation_log 
                (automation_type, automation_id, status, details, error_message)
                VALUES (?, ?, ?, ?, ?)
            """, (automation_type, automation_id, status, details, error_message))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error logging automation execution: {e}")
    
    def get_automation_analytics(self) -> Dict:
        """Get automation system analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get execution statistics
            stats = {}
            
            # Total rules
            rules_df = pd.read_sql_query("SELECT COUNT(*) as count FROM automation_rules", conn)
            stats['total_rules'] = rules_df.iloc[0]['count']
            
            # Active rules
            active_rules_df = pd.read_sql_query("SELECT COUNT(*) as count FROM automation_rules WHERE is_active = 1", conn)
            stats['active_rules'] = active_rules_df.iloc[0]['count']
            
            # Total executions
            executions_df = pd.read_sql_query("SELECT COUNT(*) as count FROM automation_log", conn)
            stats['total_executions'] = executions_df.iloc[0]['count']
            
            # Success rate
            success_df = pd.read_sql_query("SELECT COUNT(*) as count FROM automation_log WHERE status = 'success'", conn)
            success_count = success_df.iloc[0]['count']
            stats['success_rate'] = (success_count / stats['total_executions'] * 100) if stats['total_executions'] > 0 else 0
            
            # Recent activity
            recent_activity_df = pd.read_sql_query("""
                SELECT automation_type, automation_id, status, execution_time
                FROM automation_log 
                ORDER BY execution_time DESC 
                LIMIT 10
            """, conn)
            stats['recent_activity'] = recent_activity_df.to_dict('records')
            
            conn.close()
            return stats
            
        except Exception as e:
            st.error(f"Error getting automation analytics: {e}")
            return {}

def show_advanced_automation_system():
    """Main function to display Advanced Automation System"""
    st.header("⚡ Advanced Automation System")
    st.subheader("Comprehensive workflow automation for maximum efficiency")
    
    # Initialize automation system
    if 'automation_system' not in st.session_state:
        st.session_state.automation_system = AdvancedAutomationSystem()
    
    automation_system = st.session_state.automation_system
    
    # Sidebar for configuration
    with st.sidebar:
        st.subheader("🔧 Automation Configuration")
        
        # Email configuration
        with st.expander("📧 Email Configuration"):
            smtp_server = st.text_input("SMTP Server", value=st.session_state.get("smtp_server", "smtp.gmail.com"))
            smtp_port = st.number_input("SMTP Port", value=st.session_state.get("smtp_port", 587))
            email_username = st.text_input("Email Username", value=st.session_state.get("email_username", ""))
            email_password = st.text_input("Email Password", type="password", value=st.session_state.get("email_password", ""))
            
            if st.button("Save Email Config"):
                st.session_state.smtp_server = smtp_server
                st.session_state.smtp_port = smtp_port
                st.session_state.email_username = email_username
                st.session_state.email_password = email_password
                st.success("Email configuration saved!")
    
    # Main automation features tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔄 Automation Rules",
        "📧 Email Templates", 
        "📄 Document Generation",
        "📊 Workflows",
        "📈 Campaigns",
        "📋 Analytics"
    ])
    
    with tab1:
        show_automation_rules(automation_system)
    
    with tab2:
        show_email_templates(automation_system)
    
    with tab3:
        show_document_generation(automation_system)
    
    with tab4:
        show_workflows(automation_system)
    
    with tab5:
        show_email_campaigns(automation_system)
    
    with tab6:
        show_automation_analytics(automation_system)

def show_automation_rules(automation_system: AdvancedAutomationSystem):
    """Automation Rules tab"""
    st.subheader("🔄 Automation Rules")
    
    # Display existing rules
    if automation_system.automation_rules:
        st.write("### Existing Automation Rules")
        
        for rule in automation_system.automation_rules:
            with st.expander(f"{'✅' if rule.is_active else '❌'} {rule.name}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Trigger:** {rule.trigger_type}")
                    st.write(f"**Executions:** {rule.execution_count}")
                
                with col2:
                    st.write(f"**Created:** {rule.created_at.strftime('%Y-%m-%d')}")
                    if rule.last_executed:
                        st.write(f"**Last Run:** {rule.last_executed.strftime('%Y-%m-%d %H:%M')}")
                
                with col3:
                    st.write(f"**Actions:** {len(rule.actions)}")
                    if st.button(f"Edit Rule", key=f"edit_{rule.id}"):
                        st.session_state.editing_rule = rule.id
                
                # Show trigger conditions
                st.write("**Trigger Conditions:**")
                st.json(rule.trigger_conditions)
                
                # Show actions
                st.write("**Actions:**")
                for i, action in enumerate(rule.actions):
                    st.write(f"{i+1}. {action.get('type', 'Unknown')} - {action.get('description', 'No description')}")
    
    # Create new rule
    st.write("### Create New Automation Rule")
    
    with st.form("create_automation_rule"):
        rule_name = st.text_input("Rule Name")
        
        trigger_type = st.selectbox(
            "Trigger Type",
            ["deal_status_change", "time_based", "data_change", "manual"]
        )
        
        # Trigger conditions based on type
        trigger_conditions = {}
        
        if trigger_type == "deal_status_change":
            from_status = st.selectbox("From Status", ["any", "analyzing", "approved", "rejected", "pending"])
            to_status = st.selectbox("To Status", ["analyzing", "approved", "rejected", "pending"])
            
            trigger_conditions = {
                "from_status": from_status if from_status != "any" else None,
                "to_status": to_status
            }
        
        elif trigger_type == "time_based":
            schedule_type = st.selectbox("Schedule", ["daily", "weekly", "monthly"])
            schedule_time = st.time_input("Time")
            
            trigger_conditions = {
                "schedule_type": schedule_type,
                "schedule_time": schedule_time.strftime("%H:%M")
            }
        
        # Actions
        st.write("**Actions:**")
        action_type = st.selectbox(
            "Action Type",
            ["send_email", "create_task", "update_deal", "generate_document"]
        )
        
        actions = []
        
        if action_type == "send_email":
            email_template = st.selectbox(
                "Email Template",
                [t.name for t in automation_system.email_templates] if automation_system.email_templates else ["No templates available"]
            )
            recipients = st.text_area("Recipients (one per line)")
            
            if email_template != "No templates available":
                template_id = next((t.id for t in automation_system.email_templates if t.name == email_template), None)
                actions.append({
                    "type": "send_email",
                    "template_id": template_id,
                    "recipients": recipients.split('\n') if recipients else [],
                    "description": f"Send email using {email_template}"
                })
        
        elif action_type == "create_task":
            task_title = st.text_input("Task Title")
            task_description = st.text_area("Task Description")
            
            actions.append({
                "type": "create_task",
                "title": task_title,
                "description": task_description,
                "description": f"Create task: {task_title}"
            })
        
        is_active = st.checkbox("Active", value=True)
        
        submitted = st.form_submit_button("Create Automation Rule")
        
        if submitted and rule_name and actions:
            rule = AutomationRule(
                id=f"rule_{int(time.time())}",
                name=rule_name,
                trigger_type=trigger_type,
                trigger_conditions=trigger_conditions,
                actions=actions,
                is_active=is_active,
                created_at=datetime.now()
            )
            
            if automation_system.create_automation_rule(rule):
                st.success(f"Automation rule '{rule_name}' created successfully!")
                st.experimental_rerun()
            else:
                st.error("Failed to create automation rule")

def show_email_templates(automation_system: AdvancedAutomationSystem):
    """Email Templates tab"""
    st.subheader("📧 Email Templates")
    
    # Display existing templates
    if automation_system.email_templates:
        st.write("### Existing Email Templates")
        
        for template in automation_system.email_templates:
            with st.expander(f"📧 {template.name} ({template.template_type})"):
                st.write(f"**Subject:** {template.subject}")
                st.write(f"**Variables:** {', '.join(template.variables)}")
                st.write("**Body Preview:**")
                st.text_area("", value=template.body[:200] + "..." if len(template.body) > 200 else template.body, height=100, disabled=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Edit Template", key=f"edit_template_{template.id}"):
                        st.session_state.editing_template = template.id
                with col2:
                    if st.button(f"Test Send", key=f"test_template_{template.id}"):
                        test_email = st.text_input("Test Email Address", key=f"test_email_{template.id}")
                        if test_email:
                            # Send test email with sample data
                            context = {
                                "deal_address": "123 Sample St",
                                "purchase_price": "$150,000",
                                "roi": "15.5%"
                            }
                            subject = automation_system._replace_template_variables(template.subject, context)
                            body = automation_system._replace_template_variables(template.body, context)
                            
                            if automation_system.send_email([test_email], subject, body):
                                st.success("Test email sent!")
                            else:
                                st.error("Failed to send test email")
    
    # Create new template
    st.write("### Create New Email Template")
    
    with st.form("create_email_template"):
        template_name = st.text_input("Template Name")
        template_type = st.selectbox(
            "Template Type",
            ["deal_update", "investor_alert", "follow_up", "marketing", "system_notification"]
        )
        
        subject = st.text_input("Email Subject")
        
        st.write("**Available Variables:** {{deal_address}}, {{purchase_price}}, {{roi}}, {{deal_type}}, {{investor_name}}")
        body = st.text_area("Email Body", height=300, help="Use {{variable_name}} for dynamic content")
        
        # Extract variables from template
        variables = list(set(re.findall(r'\{\{(\w+)\}\}', subject + body)))
        
        is_active = st.checkbox("Active", value=True)
        
        submitted = st.form_submit_button("Create Email Template")
        
        if submitted and template_name and subject and body:
            template = EmailTemplate(
                id=f"template_{int(time.time())}",
                name=template_name,
                subject=subject,
                body=body,
                template_type=template_type,
                variables=variables,
                is_active=is_active,
                created_at=datetime.now()
            )
            
            if automation_system.create_email_template(template):
                st.success(f"Email template '{template_name}' created successfully!")
                st.experimental_rerun()
            else:
                st.error("Failed to create email template")

def show_document_generation(automation_system: AdvancedAutomationSystem):
    """Document Generation tab"""
    st.subheader("📄 Document Generation")
    
    if not REPORTLAB_AVAILABLE:
        st.warning("⚠️ Document generation requires the ReportLab library. Install it using: `pip install reportlab`")
        return
    
    # Document template creation
    st.write("### Create Document Template")
    
    with st.form("create_document_template"):
        template_name = st.text_input("Template Name")
        template_type = st.selectbox(
            "Document Type",
            ["contract", "analysis_report", "investment_summary", "invoice", "letter"]
        )
        
        st.write("**Available Variables:** {{deal_address}}, {{purchase_price}}, {{arv}}, {{repair_costs}}, {{roi}}, {{investor_name}}, {{date}}")
        
        content = st.text_area(
            "Document Content",
            height=400,
            value="""Property Investment Analysis Report

Date: {{date}}
Property Address: {{deal_address}}
Investor: {{investor_name}}

FINANCIAL SUMMARY
Purchase Price: {{purchase_price}}
After Repair Value: {{arv}}
Repair Costs: {{repair_costs}}
Expected ROI: {{roi}}%

INVESTMENT RECOMMENDATION
Based on our analysis, this property presents a {{roi_assessment}} investment opportunity with {{risk_level}} risk profile.

Key factors:
- Market appreciation potential: {{market_trend}}
- Cash flow projection: {{cash_flow}}
- Exit strategy options: {{exit_strategies}}

CONCLUSION
This investment aligns with conservative investment criteria and offers potential for steady returns.

Generated by NxTrix CRM""",
            help="Use {{variable_name}} for dynamic content"
        )
        
        # Extract variables from template
        variables = list(set(re.findall(r'\{\{(\w+)\}\}', content)))
        
        submitted = st.form_submit_button("Create Document Template")
        
        if submitted and template_name and content:
            template = DocumentTemplate(
                id=f"doc_template_{int(time.time())}",
                name=template_name,
                template_type=template_type,
                content=content,
                variables=variables,
                is_active=True,
                created_at=datetime.now()
            )
            
            # Save to database
            try:
                conn = sqlite3.connect(automation_system.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO document_templates 
                    (id, name, template_type, content, variables, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    template.id,
                    template.name,
                    template.template_type,
                    template.content,
                    json.dumps(template.variables),
                    template.is_active,
                    template.created_at.isoformat()
                ))
                
                conn.commit()
                conn.close()
                
                automation_system.document_templates.append(template)
                st.success(f"Document template '{template_name}' created successfully!")
                
            except Exception as e:
                st.error(f"Error creating document template: {e}")
    
    # Test document generation
    st.write("### Test Document Generation")
    
    # Load existing templates
    try:
        conn = sqlite3.connect(automation_system.db_path)
        templates_df = pd.read_sql_query("SELECT * FROM document_templates WHERE is_active = 1", conn)
        conn.close()
        
        if not templates_df.empty:
            selected_template = st.selectbox(
                "Select Template",
                options=templates_df['id'].tolist(),
                format_func=lambda x: templates_df[templates_df['id']==x]['name'].iloc[0]
            )
            
            if selected_template:
                template_data = templates_df[templates_df['id']==selected_template].iloc[0]
                variables = json.loads(template_data['variables'])
                
                # Input values for variables
                st.write("**Provide Values for Variables:**")
                context = {}
                
                col1, col2 = st.columns(2)
                for i, var in enumerate(variables):
                    with col1 if i % 2 == 0 else col2:
                        if var == 'date':
                            context[var] = st.date_input(f"{var}", datetime.now().date()).strftime('%Y-%m-%d')
                        elif any(keyword in var.lower() for keyword in ['price', 'cost', 'value']):
                            context[var] = f"${st.number_input(f'{var} ($)', value=0, step=1000):,.0f}"
                        elif var.lower() == 'roi':
                            context[var] = f"{st.number_input(f'{var} (%)', value=0.0, step=0.1):.1f}"
                        else:
                            context[var] = st.text_input(f"{var}", value=f"Sample {var}")
                
                if st.button("Generate Document"):
                    template_obj = DocumentTemplate(
                        id=template_data['id'],
                        name=template_data['name'],
                        template_type=template_data['template_type'],
                        content=template_data['content'],
                        variables=variables,
                        is_active=True,
                        created_at=datetime.now()
                    )
                    
                    if automation_system.generate_document(template_obj, context):
                        st.success("Document generated successfully!")
                        st.info("Document saved to generated_documents folder")
                    else:
                        st.error("Failed to generate document")
        else:
            st.info("No document templates available. Create one above!")
            
    except Exception as e:
        st.error(f"Error loading templates: {e}")

def show_workflows(automation_system: AdvancedAutomationSystem):
    """Workflows tab"""
    st.subheader("📊 Automated Workflows")
    
    st.info("🚧 Advanced workflow builder coming soon! This will allow you to create complex multi-step automation sequences.")
    
    # Placeholder for workflow visualization
    st.write("### Workflow Designer")
    st.write("Create sophisticated automation workflows with multiple steps, conditions, and branches.")
    
    # Example workflow display
    workflow_example = {
        "name": "New Deal Processing Workflow",
        "steps": [
            {"type": "trigger", "name": "Deal Status Changed to 'Analyzing'"},
            {"type": "action", "name": "Send Welcome Email to Investor"},
            {"type": "delay", "name": "Wait 1 Day"},
            {"type": "action", "name": "Generate Analysis Report"},
            {"type": "condition", "name": "If ROI > 15%"},
            {"type": "action", "name": "Send High-Priority Alert"},
            {"type": "action", "name": "Create Follow-up Task"}
        ]
    }
    
    st.write("### Example Workflow")
    for i, step in enumerate(workflow_example["steps"]):
        step_emoji = {
            "trigger": "🎯",
            "action": "⚡",
            "delay": "⏰",
            "condition": "🔀"
        }.get(step["type"], "📝")
        
        st.write(f"{i+1}. {step_emoji} {step['name']}")

def show_email_campaigns(automation_system: AdvancedAutomationSystem):
    """Email Campaigns tab"""
    st.subheader("📈 Email Marketing Campaigns")
    
    # Campaign creation
    st.write("### Create Email Campaign")
    
    with st.form("create_campaign"):
        campaign_name = st.text_input("Campaign Name")
        
        # Select template
        if automation_system.email_templates:
            template_options = [(t.id, t.name) for t in automation_system.email_templates]
            selected_template_id = st.selectbox(
                "Email Template",
                options=[t[0] for t in template_options],
                format_func=lambda x: next(t[1] for t in template_options if t[0] == x)
            )
        else:
            st.warning("No email templates available. Create templates first.")
            selected_template_id = None
        
        # Recipients
        recipient_source = st.radio(
            "Recipient Source",
            ["Manual List", "Database Query"]
        )
        
        if recipient_source == "Manual List":
            recipients_text = st.text_area("Email Addresses (one per line)")
            recipients = [email.strip() for email in recipients_text.split('\n') if email.strip()]
        else:
            # Database query for recipients
            query_type = st.selectbox(
                "Recipient Group",
                ["All Investors", "Active Investors", "Deal Participants"]
            )
            recipients = []  # This would be populated based on query
        
        # Scheduling
        send_immediately = st.checkbox("Send Immediately")
        schedule_time = None
        
        if not send_immediately:
            schedule_date = st.date_input("Schedule Date")
            schedule_time_input = st.time_input("Schedule Time")
            schedule_time = datetime.combine(schedule_date, schedule_time_input)
        
        submitted = st.form_submit_button("Create Campaign")
        
        if submitted and campaign_name and selected_template_id and recipients:
            campaign_data = {
                'id': f"campaign_{int(time.time())}",
                'name': campaign_name,
                'template_id': selected_template_id,
                'recipients': recipients,
                'schedule_time': schedule_time.isoformat() if schedule_time else None
            }
            
            if automation_system.create_email_campaign(campaign_data):
                st.success(f"Email campaign '{campaign_name}' created successfully!")
                
                if send_immediately:
                    # Execute campaign immediately
                    st.info("Sending emails...")
                    # This would trigger immediate execution
            else:
                st.error("Failed to create email campaign")
    
    # Display existing campaigns
    try:
        conn = sqlite3.connect(automation_system.db_path)
        campaigns_df = pd.read_sql_query("SELECT * FROM email_campaigns ORDER BY created_at DESC", conn)
        conn.close()
        
        if not campaigns_df.empty:
            st.write("### Campaign History")
            
            for _, campaign in campaigns_df.iterrows():
                with st.expander(f"📧 {campaign['name']} - {campaign['status'].title()}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Status", campaign['status'].title())
                        st.metric("Sent", campaign['sent_count'])
                    
                    with col2:
                        st.metric("Opened", campaign['opened_count'])
                        st.metric("Clicked", campaign['clicked_count'])
                    
                    with col3:
                        open_rate = (campaign['opened_count'] / campaign['sent_count'] * 100) if campaign['sent_count'] > 0 else 0
                        click_rate = (campaign['clicked_count'] / campaign['sent_count'] * 100) if campaign['sent_count'] > 0 else 0
                        st.metric("Open Rate", f"{open_rate:.1f}%")
                        st.metric("Click Rate", f"{click_rate:.1f}%")
        else:
            st.info("No email campaigns found.")
            
    except Exception as e:
        st.error(f"Error loading campaigns: {e}")

def show_automation_analytics(automation_system: AdvancedAutomationSystem):
    """Automation Analytics tab"""
    st.subheader("📋 Automation Analytics")
    
    # Get analytics data
    analytics = automation_system.get_automation_analytics()
    
    if analytics:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Rules", analytics.get('total_rules', 0))
        with col2:
            st.metric("Active Rules", analytics.get('active_rules', 0))
        with col3:
            st.metric("Total Executions", analytics.get('total_executions', 0))
        with col4:
            st.metric("Success Rate", f"{analytics.get('success_rate', 0):.1f}%")
        
        # Recent activity
        if analytics.get('recent_activity'):
            st.write("### Recent Automation Activity")
            
            activity_df = pd.DataFrame(analytics['recent_activity'])
            activity_df['execution_time'] = pd.to_datetime(activity_df['execution_time'])
            
            # Format for display
            display_df = activity_df.copy()
            display_df['execution_time'] = display_df['execution_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            st.dataframe(display_df, use_container_width=True)
        
        # Performance charts
        try:
            conn = sqlite3.connect(automation_system.db_path)
            
            # Execution trends
            trend_df = pd.read_sql_query("""
                SELECT DATE(execution_time) as date, status, COUNT(*) as count
                FROM automation_log 
                WHERE execution_time >= date('now', '-30 days')
                GROUP BY DATE(execution_time), status
                ORDER BY date
            """, conn)
            
            if not trend_df.empty:
                st.write("### Execution Trends (Last 30 Days)")
                
                fig = px.line(
                    trend_df, 
                    x='date', 
                    y='count', 
                    color='status',
                    title='Daily Automation Executions'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            conn.close()
            
        except Exception as e:
            st.error(f"Error loading trend data: {e}")
    
    else:
        st.info("No automation analytics available yet. Create and run some automation rules to see analytics.")

if __name__ == "__main__":
    show_advanced_automation_system()