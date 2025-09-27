"""
Database Service Wrapper for Supabase
Provides a consistent interface for database operations
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import uuid

@dataclass
class Deal:
    """Deal data structure"""
    id: str
    property_address: str
    asking_price: float
    estimated_value: float
    cash_flow: float
    cap_rate: float
    ai_score: float
    deal_type: str
    created_at: datetime
    status: str = "active"

class SupabaseDatabaseService:
    """Database service wrapper for Supabase"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self._connection_tested = False
    
    def is_connected(self) -> bool:
        """Test if the Supabase connection is working"""
        try:
            # Try a simple query to test connection
            result = self.supabase.table('profiles').select('email').limit(1).execute()
            self._connection_tested = True
            return True
        except Exception as e:
            st.error(f"Database connection test failed: {e}")
            return False
    
    def get_deals(self) -> List[Deal]:
        """Get all deals from the database"""
        try:
            # In production, we might not have a deals table yet
            # For now, return sample data or try to query if table exists
            result = self.supabase.table('deals').select('*').execute()
            
            deals = []
            for row in result.data:
                deals.append(Deal(
                    id=row.get('id', str(uuid.uuid4())),
                    property_address=row.get('property_address', ''),
                    asking_price=float(row.get('asking_price', 0)),
                    estimated_value=float(row.get('estimated_value', 0)),
                    cash_flow=float(row.get('cash_flow', 0)),
                    cap_rate=float(row.get('cap_rate', 0)),
                    ai_score=float(row.get('ai_score', 0)),
                    deal_type=row.get('deal_type', 'rental'),
                    created_at=datetime.fromisoformat(row.get('created_at', datetime.now().isoformat())),
                    status=row.get('status', 'active')
                ))
            return deals
            
        except Exception as e:
            # If deals table doesn't exist, return sample data
            return self._get_sample_deals()
    
    def _get_sample_deals(self) -> List[Deal]:
        """Return sample deals when database is not available"""
        return [
            Deal(
                id="sample-1",
                property_address="123 Main St, Sample City",
                asking_price=250000,
                estimated_value=275000,
                cash_flow=1200,
                cap_rate=5.8,
                ai_score=85,
                deal_type="rental",
                created_at=datetime.now() - timedelta(days=5),
                status="active"
            ),
            Deal(
                id="sample-2", 
                property_address="456 Oak Ave, Demo Town",
                asking_price=180000,
                estimated_value=195000,
                cash_flow=950,
                cap_rate=6.2,
                ai_score=78,
                deal_type="flip",
                created_at=datetime.now() - timedelta(days=3),
                status="active"
            ),
            Deal(
                id="sample-3",
                property_address="789 Pine St, Test City",
                asking_price=320000,
                estimated_value=340000,
                cash_flow=1500,
                cap_rate=5.4,
                ai_score=92,
                deal_type="rental",
                created_at=datetime.now() - timedelta(days=1),
                status="active"
            )
        ]
    
    def add_deal(self, deal_data: Dict[str, Any]) -> bool:
        """Add a new deal to the database"""
        try:
            result = self.supabase.table('deals').insert(deal_data).execute()
            return bool(result.data)
        except Exception as e:
            st.error(f"Failed to add deal: {e}")
            return False
    
    def update_deal(self, deal_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing deal"""
        try:
            result = self.supabase.table('deals').update(updates).eq('id', deal_id).execute()
            return bool(result.data)
        except Exception as e:
            st.error(f"Failed to update deal: {e}")
            return False
    
    def delete_deal(self, deal_id: str) -> bool:
        """Delete a deal from the database"""
        try:
            result = self.supabase.table('deals').delete().eq('id', deal_id).execute()
            return True
        except Exception as e:
            st.error(f"Failed to delete deal: {e}")
            return False
    
    def get_user_profile(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user profile by email"""
        try:
            result = self.supabase.table('profiles').select('*').eq('email', email.lower()).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            st.error(f"Failed to get user profile: {e}")
            return None
    
    def create_user_profile(self, profile_data: Dict[str, Any]) -> bool:
        """Create a new user profile"""
        try:
            result = self.supabase.table('profiles').insert(profile_data).execute()
            return bool(result.data)
        except Exception as e:
            st.error(f"Failed to create user profile: {e}")
            return False