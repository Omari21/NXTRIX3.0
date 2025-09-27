#!/usr/bin/env python3
"""
Create sample deal data for testing the advanced reporting functionality
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
import random

def create_sample_deals():
    """Create sample deals for testing"""
    
    conn = sqlite3.connect('crm_data.db')
    cursor = conn.cursor()
    
    print("🔄 Creating sample deal data...")
    
    # Sample property types and addresses
    property_types = ['Single Family', 'Duplex', 'Triplex', 'Fourplex', 'Condo', 'Townhouse']
    addresses = [
        '123 Main St, Springfield, IL',
        '456 Oak Ave, Chicago, IL', 
        '789 Pine Rd, Aurora, IL',
        '321 Elm St, Rockford, IL',
        '654 Maple Dr, Peoria, IL',
        '987 Cedar Ln, Decatur, IL',
        '147 Birch St, Champaign, IL',
        '258 Willow Ave, Evanston, IL',
        '369 Poplar Rd, Naperville, IL',
        '741 Ash St, Joliet, IL'
    ]
    
    deal_stages = ['New', 'Analyzing', 'Under Contract', 'Negotiating', 'Closed']
    priorities = ['Low', 'Medium', 'High', 'Critical']
    
    # Create 15 sample deals over the last 90 days
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(15):
        deal_id = str(uuid.uuid4())
        
        # Random date within last 90 days
        days_offset = random.randint(0, 90)
        deal_date = base_date + timedelta(days=days_offset)
        
        # Random property details
        property_type = random.choice(property_types)
        address = random.choice(addresses)
        bedrooms = random.randint(2, 5)
        bathrooms = round(random.uniform(1.0, 3.5), 1)
        square_feet = random.randint(800, 3000)
        year_built = random.randint(1950, 2020)
        
        # Financial details
        purchase_price = random.randint(80000, 400000)
        repair_costs = random.randint(5000, 50000)
        closing_costs = random.randint(3000, 15000)
        arv = purchase_price + repair_costs + random.randint(20000, 80000)
        monthly_rent = random.randint(800, 2500)
        
        # Calculated metrics
        cap_rate = round((monthly_rent * 12 / purchase_price) * 100, 2)
        cash_on_cash_return = round(random.uniform(8.0, 18.0), 2)
        estimated_roi = round(((arv - purchase_price - repair_costs) / purchase_price) * 100, 2)
        ai_score = round(random.uniform(60.0, 95.0), 1)
        
        # Deal management
        deal_stage = random.choice(deal_stages)
        priority = random.choice(priorities)
        status = 'Active' if deal_stage != 'Closed' else 'Closed'
        
        # Contact info
        contact_names = ['John Smith', 'Sarah Johnson', 'Mike Davis', 'Lisa Wilson', 'Tom Brown']
        contact_name = random.choice(contact_names)
        contact_email = f"{contact_name.lower().replace(' ', '.')}@example.com"
        contact_phone = f"(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        # Insert deal
        cursor.execute('''
            INSERT INTO deals (
                id, property_address, deal_type, property_type, purchase_price, arv, 
                repair_costs, estimated_roi, status, created_at, updated_at,
                date_added, cap_rate, monthly_rent, bedrooms, bathrooms, square_feet,
                year_built, closing_costs, ai_score, deal_stage, priority,
                deal_notes, contact_name, contact_email, contact_phone,
                cash_on_cash_return, assigned_to
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            deal_id, address, 'Buy & Hold', property_type, purchase_price, arv,
            repair_costs, estimated_roi, status, deal_date.isoformat(), deal_date.isoformat(),
            deal_date.isoformat(), cap_rate, monthly_rent, bedrooms, bathrooms, square_feet,
            year_built, closing_costs, ai_score, deal_stage, priority,
            f"Sample deal notes for {address}", contact_name, contact_email, contact_phone,
            cash_on_cash_return, 'Demo User'
        ))
        
        print(f"✅ Created deal {i+1}: {address} - ${purchase_price:,}")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Successfully created 15 sample deals!")
    print("📊 The advanced reporting should now have data to display")

if __name__ == "__main__":
    create_sample_deals()