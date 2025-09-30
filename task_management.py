"""
Advanced Task Management System for NXTRIX CRM
Handles automated tasks, manual tasks, and team collaboration
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import sqlite3
import uuid

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Task:
    """Task data structure"""
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assigned_to: str
    created_by: str
    deal_id: Optional[str] = None
    client_id: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    is_automated: bool = False

class TaskManager:
    """Advanced task management system"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize task database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    priority TEXT NOT NULL DEFAULT 'medium',
                    assigned_to TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    deal_id TEXT,
                    client_id TEXT,
                    due_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    tags TEXT,
                    is_automated BOOLEAN DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_comments (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    comment TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error initializing task database: {e}")
    
    def create_task(self, task: Task) -> bool:
        """Create a new task"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tasks 
                (id, title, description, status, priority, assigned_to, created_by, 
                 deal_id, client_id, due_date, created_at, tags, is_automated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.id,
                task.title,
                task.description,
                task.status.value,
                task.priority.value,
                task.assigned_to,
                task.created_by,
                task.deal_id,
                task.client_id,
                task.due_date.isoformat() if task.due_date else None,
                task.created_at.isoformat(),
                json.dumps(task.tags),
                task.is_automated
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error creating task: {e}")
            return False
    
    def get_tasks(self, status: Optional[TaskStatus] = None, 
                  assigned_to: Optional[str] = None,
                  priority: Optional[TaskPriority] = None) -> List[Task]:
        """Get tasks with optional filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM tasks WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            if assigned_to:
                query += " AND assigned_to = ?"
                params.append(assigned_to)
            
            if priority:
                query += " AND priority = ?"
                params.append(priority.value)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            tasks = []
            for row in rows:
                task = Task(
                    id=row[0],
                    title=row[1],
                    description=row[2] or "",
                    status=TaskStatus(row[3]),
                    priority=TaskPriority(row[4]),
                    assigned_to=row[5],
                    created_by=row[6],
                    deal_id=row[7],
                    client_id=row[8],
                    due_date=datetime.fromisoformat(row[9]) if row[9] else None,
                    created_at=datetime.fromisoformat(row[10]),
                    completed_at=datetime.fromisoformat(row[11]) if row[11] else None,
                    tags=json.loads(row[12]) if row[12] else [],
                    is_automated=bool(row[13])
                )
                tasks.append(task)
            
            conn.close()
            return tasks
            
        except Exception as e:
            st.error(f"Error retrieving tasks: {e}")
            return []
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update task status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            completed_at = datetime.now() if status == TaskStatus.COMPLETED else None
            
            cursor.execute('''
                UPDATE tasks 
                SET status = ?, completed_at = ?
                WHERE id = ?
            ''', (status.value, completed_at.isoformat() if completed_at else None, task_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error updating task status: {e}")
            return False
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get task statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get counts by status
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM tasks 
                GROUP BY status
            """)
            status_counts = dict(cursor.fetchall())
            
            # Get overdue tasks
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tasks 
                WHERE due_date < datetime('now') AND status NOT IN ('completed', 'cancelled')
            """)
            overdue_count = cursor.fetchone()[0]
            
            # Get tasks due today
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tasks 
                WHERE DATE(due_date) = DATE('now') AND status NOT IN ('completed', 'cancelled')
            """)
            due_today_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_tasks": sum(status_counts.values()),
                "pending": status_counts.get("pending", 0),
                "in_progress": status_counts.get("in_progress", 0),
                "completed": status_counts.get("completed", 0),
                "overdue": overdue_count,
                "due_today": due_today_count
            }
            
        except Exception as e:
            st.error(f"Error getting task stats: {e}")
            return {}

def show_task_management():
    """Show task management interface"""
    st.header("📋 Task Management Center")
    st.write("Manage your tasks, assignments, and team collaboration.")
    
    # Initialize task manager
    if 'task_manager' not in st.session_state:
        st.session_state.task_manager = TaskManager()
    
    task_manager = st.session_state.task_manager
    
    # Get task statistics
    stats = task_manager.get_task_stats()
    
    # Display key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Tasks", stats.get("total_tasks", 0))
    with col2:
        st.metric("Pending", stats.get("pending", 0))
    with col3:
        st.metric("In Progress", stats.get("in_progress", 0))
    with col4:
        st.metric("Due Today", stats.get("due_today", 0))
    with col5:
        overdue = stats.get("overdue", 0)
        st.metric("Overdue", overdue, delta="🚨" if overdue > 0 else None)
    
    # Task management tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 My Tasks",
        "➕ Create Task",
        "👥 Team Tasks",
        "📊 Analytics"
    ])
    
    with tab1:
        show_my_tasks(task_manager)
    
    with tab2:
        show_create_task(task_manager)
    
    with tab3:
        show_team_tasks(task_manager)
    
    with tab4:
        show_task_analytics(task_manager)

def show_my_tasks(task_manager: TaskManager):
    """Show user's tasks"""
    st.subheader("📋 My Tasks")
    
    # Task filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", 
            ["All"] + [status.value.replace('_', ' ').title() for status in TaskStatus])
    with col2:
        priority_filter = st.selectbox("Priority", 
            ["All"] + [priority.value.title() for priority in TaskPriority])
    with col3:
        show_completed = st.checkbox("Show Completed", value=False)
    
    # Get filtered tasks
    status_filter_enum = None
    if status_filter != "All":
        status_filter_enum = TaskStatus(status_filter.lower().replace(' ', '_'))
    
    priority_filter_enum = None
    if priority_filter != "All":
        priority_filter_enum = TaskPriority(priority_filter.lower())
    
    tasks = task_manager.get_tasks(
        status=status_filter_enum,
        priority=priority_filter_enum
    )
    
    # Filter out completed tasks if not requested
    if not show_completed:
        tasks = [task for task in tasks if task.status != TaskStatus.COMPLETED]
    
    # Display tasks
    if tasks:
        for task in tasks:
            with st.container():
                # Task card
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    # Priority indicator
                    priority_colors = {
                        TaskPriority.LOW: "🟢",
                        TaskPriority.MEDIUM: "🟡", 
                        TaskPriority.HIGH: "🟠",
                        TaskPriority.URGENT: "🔴"
                    }
                    priority_icon = priority_colors.get(task.priority, "⚪")
                    
                    # Automation indicator
                    auto_icon = "🤖" if task.is_automated else "👤"
                    
                    st.markdown(f"{priority_icon} {auto_icon} **{task.title}**")
                    if task.description:
                        st.caption(task.description[:100] + "..." if len(task.description) > 100 else task.description)
                
                with col2:
                    st.caption(f"Status: {task.status.value.replace('_', ' ').title()}")
                    if task.due_date:
                        days_until_due = (task.due_date - datetime.now()).days
                        if days_until_due < 0:
                            st.caption("🚨 Overdue")
                        elif days_until_due == 0:
                            st.caption("⏰ Due Today")
                        else:
                            st.caption(f"Due in {days_until_due} days")
                
                with col3:
                    st.caption(f"Created: {task.created_at.strftime('%m/%d/%Y')}")
                    if task.deal_id:
                        st.caption(f"Deal: {task.deal_id[:8]}...")
                
                with col4:
                    # Status update buttons
                    if task.status == TaskStatus.PENDING:
                        if st.button("▶️ Start", key=f"start_{task.id}"):
                            task_manager.update_task_status(task.id, TaskStatus.IN_PROGRESS)
                            st.rerun()
                    elif task.status == TaskStatus.IN_PROGRESS:
                        if st.button("✅ Complete", key=f"complete_{task.id}"):
                            task_manager.update_task_status(task.id, TaskStatus.COMPLETED)
                            st.rerun()
                    elif task.status == TaskStatus.COMPLETED:
                        st.success("✅ Done")
                
                st.markdown("---")
    else:
        st.info("📭 No tasks found. Create some tasks to get started!")

def show_create_task(task_manager: TaskManager):
    """Show create task interface"""
    st.subheader("➕ Create New Task")
    
    with st.form("create_task_form"):
        # Basic task info
        col1, col2 = st.columns(2)
        
        with col1:
            task_title = st.text_input("Task Title*", placeholder="Review property analysis")
            task_priority = st.selectbox("Priority", [
                "Low", "Medium", "High", "Urgent"
            ])
            assigned_to = st.text_input("Assigned To", placeholder="team@example.com")
        
        with col2:
            due_date = st.date_input("Due Date", value=datetime.now() + timedelta(days=3))
            due_time = st.time_input("Due Time", value=datetime.now().time())
            task_tags = st.text_input("Tags", placeholder="urgent, analysis, review")
        
        task_description = st.text_area("Description", 
            placeholder="Detailed description of the task...")
        
        # Optional associations
        st.markdown("### 🔗 Associations (Optional)")
        col3, col4 = st.columns(2)
        
        with col3:
            deal_id = st.text_input("Deal ID", placeholder="Associate with specific deal")
        
        with col4:
            client_id = st.text_input("Client ID", placeholder="Associate with specific client")
        
        submitted = st.form_submit_button("✅ Create Task", type="primary")
        
        if submitted and task_title:
            # Create task
            due_datetime = datetime.combine(due_date, due_time) if due_date else None
            
            task = Task(
                id=str(uuid.uuid4()),
                title=task_title,
                description=task_description,
                status=TaskStatus.PENDING,
                priority=TaskPriority(task_priority.lower()),
                assigned_to=assigned_to or "current_user",
                created_by="current_user",
                deal_id=deal_id if deal_id else None,
                client_id=client_id if client_id else None,
                due_date=due_datetime,
                tags=task_tags.split(',') if task_tags else []
            )
            
            if task_manager.create_task(task):
                st.success(f"✅ Task '{task_title}' created successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to create task.")

def show_team_tasks(task_manager: TaskManager):
    """Show team tasks overview"""
    st.subheader("👥 Team Tasks Overview")
    
    tasks = task_manager.get_tasks()
    
    if tasks:
        # Group tasks by assignee
        assignee_tasks = {}
        for task in tasks:
            if task.assigned_to not in assignee_tasks:
                assignee_tasks[task.assigned_to] = []
            assignee_tasks[task.assigned_to].append(task)
        
        # Display team workload
        st.markdown("### 📊 Team Workload")
        
        for assignee, assignee_task_list in assignee_tasks.items():
            with st.expander(f"👤 {assignee} ({len(assignee_task_list)} tasks)"):
                
                # Assignee stats
                pending = len([t for t in assignee_task_list if t.status == TaskStatus.PENDING])
                in_progress = len([t for t in assignee_task_list if t.status == TaskStatus.IN_PROGRESS])
                completed = len([t for t in assignee_task_list if t.status == TaskStatus.COMPLETED])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Pending", pending)
                with col2:
                    st.metric("In Progress", in_progress)
                with col3:
                    st.metric("Completed", completed)
                
                # Recent tasks
                recent_tasks = sorted(assignee_task_list, key=lambda x: x.created_at, reverse=True)[:5]
                
                for task in recent_tasks:
                    priority_icon = {"low": "🟢", "medium": "🟡", "high": "🟠", "urgent": "🔴"}[task.priority.value]
                    status_text = task.status.value.replace('_', ' ').title()
                    st.markdown(f"{priority_icon} **{task.title}** - {status_text}")
    else:
        st.info("📭 No team tasks found.")

def show_task_analytics(task_manager: TaskManager):
    """Show task analytics"""
    st.subheader("📊 Task Analytics")
    
    stats = task_manager.get_task_stats()
    
    # Completion rate
    total_tasks = stats.get("total_tasks", 0)
    completed_tasks = stats.get("completed", 0)
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
        st.metric("Average Tasks/Day", "2.3")  # Placeholder
    
    with col2:
        st.metric("On-Time Completion", "87%")  # Placeholder
        st.metric("Team Efficiency", "Good")  # Placeholder
    
    # Task distribution chart would go here
    st.info("📈 Advanced task analytics charts coming soon!")
    
    # Quick insights
    st.markdown("### 🔍 Quick Insights")
    if stats.get("overdue", 0) > 0:
        st.warning(f"⚠️ You have {stats['overdue']} overdue tasks that need attention.")
    
    if stats.get("due_today", 0) > 0:
        st.info(f"⏰ {stats['due_today']} tasks are due today.")
    
    if completion_rate > 80:
        st.success("🎉 Great job! Your task completion rate is excellent.")
    elif completion_rate < 50:
        st.warning("📈 Consider reviewing your task management workflow to improve completion rates.")