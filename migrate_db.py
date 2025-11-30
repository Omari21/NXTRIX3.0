import sqlite3

def migrate_database():
    conn = sqlite3.connect('nxtrix_users.db')
    cursor = conn.cursor()
    
    # Get current schema
    cursor.execute('PRAGMA table_info(users)')
    columns = [row[1] for row in cursor.fetchall()]
    
    print("Current columns:", columns)
    
    # Rename table to backup
    try:
        cursor.execute('ALTER TABLE users RENAME TO users_backup')
        print("Backed up existing users table")
    except:
        pass
    
    # Create new table with correct schema
    cursor.execute('''
        CREATE TABLE users (
            user_uuid TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT DEFAULT '',
            company TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            subscription_tier TEXT DEFAULT 'starter',
            subscription_status TEXT DEFAULT 'trial',
            trial_started TEXT DEFAULT '',
            trial_ends TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_login TEXT DEFAULT '',
            is_active BOOLEAN DEFAULT 1,
            email_verified BOOLEAN DEFAULT 0,
            preferences TEXT DEFAULT '{}',
            usage_stats TEXT DEFAULT '{}'
        )
    ''')
    
    # Migrate data from backup
    try:
        cursor.execute('''
            INSERT INTO users (user_uuid, email, password_hash, full_name, company, phone, 
                             subscription_tier, subscription_status, created_at, last_login, 
                             email_verified, is_active)
            SELECT user_uuid, email, password_hash, 
                   COALESCE(first_name || ' ' || last_name, full_name, ''), 
                   company, phone, subscription_tier, subscription_status, 
                   created_at, last_login, email_verified, is_active
            FROM users_backup
        ''')
        
        migrated_count = cursor.rowcount
        print(f"Migrated {migrated_count} user accounts")
        
        conn.commit()
        
        # Drop backup table
        cursor.execute('DROP TABLE users_backup')
        print("Migration completed successfully")
        
    except Exception as e:
        print(f"Migration error: {e}")
        # Restore backup if migration fails
        try:
            cursor.execute('DROP TABLE users')
            cursor.execute('ALTER TABLE users_backup RENAME TO users')
            print("Restored original table")
        except:
            pass
    
    conn.close()

if __name__ == "__main__":
    migrate_database()