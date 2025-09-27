import sqlite3
import os

# Check if database exists
db_path = "crm_data.db"
if os.path.exists(db_path):
    print(f"✅ Database file found: {db_path}")
    
    # Connect and check tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\n📊 Current Tables ({len(tables)} total):")
    for table in tables:
        table_name = table[0]
        print(f"  - {table_name}")
        
        # Get column info for each table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"    └─ {col[1]} ({col[2]})")
    
    # Check database size
    size = os.path.getsize(db_path)
    print(f"\n💾 Database Size: {size:,} bytes ({size/1024:.1f} KB)")
    
    conn.close()
else:
    print(f"❌ Database file not found: {db_path}")
    print("The database will be created when the app runs for the first time.")

print("\n" + "="*60)
print("NEW TABLES NEEDED FOR PHASE 4 & 5:")
print("="*60)

# Tables needed for Phase 4 (Advanced Analytics)
print("📈 Phase 4 - Advanced Analytics:")
print("  - deal_analytics")
print("  - market_intelligence") 
print("  - deal_stage_history")
print("  - market_predictions")

# Tables needed for Phase 5 (Automated Deal Sourcing)
print("\n🔍 Phase 5 - Automated Deal Sourcing:")
print("  - investor_criteria")
print("  - property_leads")
print("  - deal_alerts")
print("  - sourcing_activity")

print("\n✅ All new tables use 'CREATE TABLE IF NOT EXISTS' so they will be")
print("   automatically created when you run the respective modules!")