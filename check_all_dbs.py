import sqlite3
import os

# Check all database files for user tables
db_files = [
    'nxtrix_users.db',
    'nxtrix.db', 
    'crm_data.db',
    'nxtrix_billing.db',
    'nxtrix_communications.db'
]

for db_file in db_files:
    if os.path.exists(db_file):
        print(f"\n=== {db_file} ===")
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Tables: {[t[0] for t in tables]}")
            
            # Check for users table
            for table in tables:
                table_name = table[0]
                if 'user' in table_name.lower():
                    print(f"\nTable: {table_name}")
                    cursor.execute(f'SELECT * FROM {table_name} LIMIT 5')
                    rows = cursor.fetchall()
                    if rows:
                        cursor.execute(f'PRAGMA table_info({table_name})')
                        columns = [col[1] for col in cursor.fetchall()]
                        print(f"Columns: {columns}")
                        print("Data:")
                        for row in rows:
                            print(row[:3])  # Show first 3 columns only for security
                    else:
                        print("No data found")
            
            conn.close()
        except Exception as e:
            print(f"Error reading {db_file}: {e}")