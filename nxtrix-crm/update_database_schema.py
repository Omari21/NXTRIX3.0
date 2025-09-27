#!/usr/bin/env python3
"""
Database schema update script to add missing columns
"""

import sqlite3
import os
from datetime import datetime

def update_database_schema():
    """Add missing columns to the database"""
    
    db_path = 'crm_data.db'
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Updating database schema...")
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(deals)")
        existing_cols = [col[1] for col in cursor.fetchall()]
        print(f"Existing columns: {existing_cols}")
        
        # Add missing columns to deals table
        missing_columns = [
            ('date_added', 'TEXT', datetime.now().isoformat()),
            ('cap_rate', 'REAL', 0.0),
            ('monthly_rent', 'REAL', 0.0),
            ('bedrooms', 'INTEGER', 3),
            ('bathrooms', 'REAL', 2.0),
            ('square_feet', 'INTEGER', 1200),
            ('year_built', 'INTEGER', 2000),
            ('closing_costs', 'REAL', 0.0),
            ('ai_score', 'REAL', 75.0),
            ('deal_stage', 'TEXT', 'New'),
            ('priority', 'TEXT', 'Medium'),
            ('assigned_to', 'TEXT', ''),
            ('deal_notes', 'TEXT', ''),
            ('contact_name', 'TEXT', ''),
            ('contact_email', 'TEXT', ''),
            ('contact_phone', 'TEXT', '')
        ]
        
        added_columns = []
        for col_name, col_type, default_value in missing_columns:
            if col_name not in existing_cols:
                try:
                    if col_type == 'TEXT':
                        cursor.execute(f"ALTER TABLE deals ADD COLUMN {col_name} {col_type} DEFAULT '{default_value}'")
                    else:
                        cursor.execute(f"ALTER TABLE deals ADD COLUMN {col_name} {col_type} DEFAULT {default_value}")
                    added_columns.append(col_name)
                    print(f"✅ Added column: {col_name} ({col_type})")
                except sqlite3.OperationalError as e:
                    print(f"⚠️ Could not add {col_name}: {e}")
        
        # Update existing records with date_added if null
        if 'date_added' in added_columns:
            cursor.execute("UPDATE deals SET date_added = ? WHERE date_added IS NULL OR date_added = ''", 
                         (datetime.now().isoformat(),))
            print("✅ Updated existing records with date_added")
        
        # Calculate cap_rate for existing records where possible
        if 'cap_rate' in added_columns:
            cursor.execute("""
                UPDATE deals 
                SET cap_rate = CASE 
                    WHEN purchase_price > 0 AND monthly_rent > 0 
                    THEN (monthly_rent * 12.0 / purchase_price) * 100 
                    ELSE 8.5 
                END 
                WHERE cap_rate = 0 OR cap_rate IS NULL
            """)
            print("✅ Calculated cap_rate for existing records")
        
        conn.commit()
        
        # Verify the updates
        cursor.execute("PRAGMA table_info(deals)")
        updated_cols = [col[1] for col in cursor.fetchall()]
        print(f"\n📊 Updated table columns: {len(updated_cols)} total")
        
        # Check some sample data
        cursor.execute("SELECT COUNT(*) FROM deals")
        deal_count = cursor.fetchone()[0]
        print(f"📈 Total deals in database: {deal_count}")
        
        conn.close()
        print("\n✅ Database schema update completed successfully!")
        
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")

if __name__ == "__main__":
    update_database_schema()