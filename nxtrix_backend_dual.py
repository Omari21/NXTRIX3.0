"""
NXTRIX Backend - Supabase Adapter
Dual database support: SQLite (local) + Supabase (production)
"""

import os
from typing import Dict, List, Optional, Any
import sqlite3
import datetime
import json

# Supabase integration (optional)
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️ Supabase client not installed. Using SQLite only.")

class NXTRIXDualDatabase:
    """
    Dual database support - automatically switches between SQLite and Supabase
    """
    
    def __init__(self, use_supabase: bool = None):
        # Auto-detect based on environment
        if use_supabase is None:
            use_supabase = bool(os.getenv('SUPABASE_URL') and SUPABASE_AVAILABLE)
        
        self.use_supabase = use_supabase
        
        if self.use_supabase and SUPABASE_AVAILABLE:
            self._init_supabase()
        else:
            self._init_sqlite()
    
    def _init_supabase(self):
        """Initialize Supabase connection"""
        try:
            self.supabase_url = os.getenv('SUPABASE_URL')
            self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
            
            if not self.supabase_url or not self.supabase_key:
                raise ValueError("Supabase credentials not found in environment")
            
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            print("✅ Supabase connection initialized")
            
        except Exception as e:
            print(f"❌ Supabase initialization failed: {e}")
            print("🔄 Falling back to SQLite...")
            self._init_sqlite()
    
    def _init_sqlite(self):
        """Initialize SQLite connection"""
        self.use_supabase = False
        self.db_path = "nxtrix.db"
        self._init_sqlite_tables()
        print("✅ SQLite connection initialized")
    
    def _init_sqlite_tables(self):
        """Initialize SQLite tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Contacts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            contact_type TEXT,
            company TEXT,
            address TEXT,
            notes TEXT,
            tags TEXT,
            lead_score INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Deals table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_address TEXT NOT NULL,
            purchase_price REAL,
            deal_type TEXT,
            expected_roi REAL,
            status TEXT DEFAULT 'active',
            contact_id INTEGER,
            arv REAL,
            repair_costs REAL,
            closing_costs REAL,
            monthly_rent REAL,
            expenses REAL,
            profit_projection REAL,
            closing_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts (id)
        )
        ''')
        
        # Other tables...
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            content TEXT,
            target_audience TEXT,
            status TEXT DEFAULT 'draft',
            sent_count INTEGER DEFAULT 0,
            open_rate REAL DEFAULT 0,
            click_rate REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_at TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    # CONTACT OPERATIONS
    def add_contact(self, contact_data: Dict) -> int:
        """Add a new contact"""
        if self.use_supabase:
            return self._add_contact_supabase(contact_data)
        else:
            return self._add_contact_sqlite(contact_data)
    
    def _add_contact_sqlite(self, contact_data: Dict) -> int:
        """Add contact to SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO contacts (name, email, phone, contact_type, company, address, notes, tags, lead_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            contact_data.get('name'),
            contact_data.get('email'),
            contact_data.get('phone', ''),
            contact_data.get('contact_type', 'Lead'),
            contact_data.get('company', ''),
            contact_data.get('address', ''),
            contact_data.get('notes', ''),
            contact_data.get('tags', ''),
            contact_data.get('lead_score', 50)
        ))
        
        contact_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return contact_id
    
    def _add_contact_supabase(self, contact_data: Dict) -> int:
        """Add contact to Supabase"""
        try:
            response = self.supabase.table('contacts').insert({
                'name': contact_data.get('name'),
                'email': contact_data.get('email'),
                'phone': contact_data.get('phone', ''),
                'contact_type': contact_data.get('contact_type', 'Lead'),
                'company': contact_data.get('company', ''),
                'address': contact_data.get('address', ''),
                'notes': contact_data.get('notes', ''),
                'tags': contact_data.get('tags', ''),
                'lead_score': contact_data.get('lead_score', 50)
            }).execute()
            
            return response.data[0]['id']
        except Exception as e:
            print(f"❌ Supabase contact insert failed: {e}")
            raise
    
    def get_contacts(self) -> List[Dict]:
        """Get all contacts"""
        if self.use_supabase:
            return self._get_contacts_supabase()
        else:
            return self._get_contacts_sqlite()
    
    def _get_contacts_sqlite(self) -> List[Dict]:
        """Get contacts from SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM contacts ORDER BY created_at DESC')
        contacts = []
        
        for row in cursor.fetchall():
            contacts.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'contact_type': row[4],
                'company': row[5],
                'address': row[6],
                'notes': row[7],
                'tags': row[8],
                'lead_score': row[9],
                'created_at': row[10]
            })
        
        conn.close()
        return contacts
    
    def _get_contacts_supabase(self) -> List[Dict]:
        """Get contacts from Supabase"""
        try:
            response = self.supabase.table('contacts').select('*').order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"❌ Supabase contacts fetch failed: {e}")
            raise
    
    # DEAL OPERATIONS
    def add_deal(self, deal_data: Dict) -> int:
        """Add a new deal"""
        if self.use_supabase:
            return self._add_deal_supabase(deal_data)
        else:
            return self._add_deal_sqlite(deal_data)
    
    def _add_deal_sqlite(self, deal_data: Dict) -> int:
        """Add deal to SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO deals (property_address, purchase_price, deal_type, expected_roi, status, 
                          contact_id, arv, repair_costs, closing_costs, monthly_rent, expenses, 
                          profit_projection, closing_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            deal_data.get('property_address'),
            deal_data.get('purchase_price', 0),
            deal_data.get('deal_type'),
            deal_data.get('expected_roi', 0),
            deal_data.get('status', 'active'),
            deal_data.get('contact_id'),
            deal_data.get('arv', 0),
            deal_data.get('repair_costs', 0),
            deal_data.get('closing_costs', 0),
            deal_data.get('monthly_rent', 0),
            deal_data.get('expenses', 0),
            deal_data.get('profit_projection', 0),
            deal_data.get('closing_date'),
            deal_data.get('notes', '')
        ))
        
        deal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return deal_id
    
    def _add_deal_supabase(self, deal_data: Dict) -> int:
        """Add deal to Supabase"""
        try:
            response = self.supabase.table('deals').insert({
                'property_address': deal_data.get('property_address'),
                'purchase_price': deal_data.get('purchase_price', 0),
                'deal_type': deal_data.get('deal_type'),
                'expected_roi': deal_data.get('expected_roi', 0),
                'status': deal_data.get('status', 'active'),
                'contact_id': deal_data.get('contact_id'),
                'arv': deal_data.get('arv', 0),
                'repair_costs': deal_data.get('repair_costs', 0),
                'closing_costs': deal_data.get('closing_costs', 0),
                'monthly_rent': deal_data.get('monthly_rent', 0),
                'expenses': deal_data.get('expenses', 0),
                'profit_projection': deal_data.get('profit_projection', 0),
                'closing_date': deal_data.get('closing_date'),
                'notes': deal_data.get('notes', '')
            }).execute()
            
            return response.data[0]['id']
        except Exception as e:
            print(f"❌ Supabase deal insert failed: {e}")
            raise
    
    def get_deals(self) -> List[Dict]:
        """Get all deals"""
        if self.use_supabase:
            return self._get_deals_supabase()
        else:
            return self._get_deals_sqlite()
    
    def _get_deals_sqlite(self) -> List[Dict]:
        """Get deals from SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT d.*, c.name as contact_name, c.email as contact_email
        FROM deals d
        LEFT JOIN contacts c ON d.contact_id = c.id
        ORDER BY d.created_at DESC
        ''')
        
        deals = []
        for row in cursor.fetchall():
            deals.append({
                'id': row[0],
                'property_address': row[1],
                'purchase_price': row[2],
                'deal_type': row[3],
                'expected_roi': row[4],
                'status': row[5],
                'contact_id': row[6],
                'arv': row[7],
                'repair_costs': row[8],
                'closing_costs': row[9],
                'monthly_rent': row[10],
                'expenses': row[11],
                'profit_projection': row[12],
                'closing_date': row[13],
                'notes': row[14],
                'created_at': row[15],
                'updated_at': row[16],
                'contact_name': row[17],
                'contact_email': row[18]
            })
        
        conn.close()
        return deals
    
    def _get_deals_supabase(self) -> List[Dict]:
        """Get deals from Supabase"""
        try:
            response = self.supabase.table('deals').select('''
                *,
                contacts:contact_id (
                    name,
                    email
                )
            ''').order('created_at', desc=True).execute()
            
            # Flatten the nested contact data
            deals = []
            for deal in response.data:
                contact = deal.get('contacts', {}) or {}
                deal['contact_name'] = contact.get('name')
                deal['contact_email'] = contact.get('email')
                del deal['contacts']  # Remove nested object
                deals.append(deal)
            
            return deals
        except Exception as e:
            print(f"❌ Supabase deals fetch failed: {e}")
            raise
    
    # UTILITY METHODS
    def get_database_info(self) -> Dict:
        """Get information about current database"""
        return {
            'type': 'Supabase' if self.use_supabase else 'SQLite',
            'connected': True,
            'url': self.supabase_url if self.use_supabase else self.db_path,
            'supabase_available': SUPABASE_AVAILABLE
        }
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            if self.use_supabase:
                # Test with a simple query
                self.supabase.table('contacts').select('id').limit(1).execute()
            else:
                # Test SQLite connection
                conn = sqlite3.connect(self.db_path)
                conn.execute('SELECT 1')
                conn.close()
            return True
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

# Create global instance with auto-detection
db = NXTRIXDualDatabase()

# Backward compatibility - create aliases for existing code
class NXTRIXDatabase(NXTRIXDualDatabase):
    """Backward compatibility wrapper"""
    pass

# Export for existing imports
nxtrix_backend = NXTRIXDatabase()