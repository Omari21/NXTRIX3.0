import sqlite3

try:
    conn = sqlite3.connect('nxtrix_users.db')
    cursor = conn.cursor()
    
    print("Database schema:")
    cursor.execute('PRAGMA table_info(users)')
    for row in cursor.fetchall():
        print(row)
    
    print("\nExisting accounts:")
    try:
        cursor.execute('SELECT email, created_at FROM users')
        accounts = cursor.fetchall()
        if accounts:
            for row in accounts:
                print(row)
        else:
            print("No accounts found")
    except Exception as e:
        print('Error reading accounts:', e)
    
    conn.close()
except Exception as e:
    print('Database error:', e)