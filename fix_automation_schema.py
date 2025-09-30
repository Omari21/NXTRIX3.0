#!/usr/bin/env python3
"""
Check automation_rules table schema and fix missing columns
"""

import sqlite3
import os

def check_and_fix_automation_tables():
    """Check and fix automation_rules table schema"""
    
    db_path = 'crm_data.db'
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Checking automation tables...")
        
        # Check if automation_rules table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%automation%'")
        automation_tables = cursor.fetchall()
        print(f"Automation tables found: {[table[0] for table in automation_tables]}")
        
        # Check if automation_rules table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='automation_rules'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("📋 Creating automation_rules table...")
            cursor.execute('''
                CREATE TABLE automation_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    trigger_type TEXT NOT NULL,
                    trigger_conditions TEXT,
                    actions TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT,
                    updated_at TEXT,
                    user_id TEXT
                )
            ''')
            print("✅ Created automation_rules table")
        else:
            print("📋 automation_rules table exists, checking columns...")
            
            # Check existing columns
            cursor.execute("PRAGMA table_info(automation_rules)")
            existing_cols = [col[1] for col in cursor.fetchall()]
            print(f"Existing columns: {existing_cols}")
            
            # Add missing columns
            required_columns = [
                ('description', 'TEXT'),
                ('trigger_conditions', 'TEXT'),
                ('actions', 'TEXT'),
                ('is_active', 'BOOLEAN', '1'),
                ('created_at', 'TEXT'),
                ('updated_at', 'TEXT'),
                ('user_id', 'TEXT')
            ]
            
            for col_info in required_columns:
                col_name = col_info[0]
                col_type = col_info[1]
                default_val = col_info[2] if len(col_info) > 2 else None
                
                if col_name not in existing_cols:
                    try:
                        if default_val:
                            cursor.execute(f"ALTER TABLE automation_rules ADD COLUMN {col_name} {col_type} DEFAULT {default_val}")
                        else:
                            cursor.execute(f"ALTER TABLE automation_rules ADD COLUMN {col_name} {col_type}")
                        print(f"✅ Added column: {col_name} ({col_type})")
                    except sqlite3.OperationalError as e:
                        print(f"⚠️ Could not add {col_name}: {e}")
        
        # Check other automation-related tables
        other_automation_tables = [
            ('workflow_automations', '''
                CREATE TABLE workflow_automations (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    workflow_steps TEXT,
                    trigger_event TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT,
                    updated_at TEXT,
                    user_id TEXT
                )
            '''),
            ('email_automations', '''
                CREATE TABLE email_automations (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    email_template TEXT,
                    trigger_conditions TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT,
                    updated_at TEXT,
                    user_id TEXT
                )
            ''')
        ]
        
        for table_name, create_sql in other_automation_tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                cursor.execute(create_sql)
                print(f"✅ Created {table_name} table")
        
        conn.commit()
        
        # Verify final schema
        cursor.execute("PRAGMA table_info(automation_rules)")
        final_cols = [col[1] for col in cursor.fetchall()]
        print(f"\n📊 Final automation_rules columns: {len(final_cols)} total")
        print(f"Columns: {final_cols}")
        
        conn.close()
        print("\n✅ Automation tables schema update completed!")
        
    except Exception as e:
        print(f"❌ Error updating automation tables: {e}")

if __name__ == "__main__":
    check_and_fix_automation_tables()