"""
Database service layer for NXTRIX CRM
Handles all CRUD operations with Supabase
"""
import os
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
from datetime import datetime
import streamlit as st
from models import Deal, Investor, Portfolio

class DatabaseService:
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.connect()
    
    def connect(self):
        """Initialize Supabase connection"""
        try:
            # Try to get credentials from environment or Streamlit secrets
            supabase_url = None
            supabase_key = None
            
            # First try environment variables
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            
            # Then try Streamlit secrets if available
            if not supabase_url or not supabase_key:
                try:
                    if hasattr(st, 'secrets') and 'SUPABASE' in st.secrets:
                        supabase_url = st.secrets['SUPABASE']['SUPABASE_URL']
                        supabase_key = st.secrets['SUPABASE']['SUPABASE_KEY']
                except Exception:
                    pass  # Secrets not available, continue without database
            
            if supabase_url and supabase_key and supabase_url != "your_supabase_project_url_here":
                self.supabase = create_client(supabase_url, supabase_key)
                print("✅ Connected to database successfully!")
            else:
                print("⚠️ Database credentials not configured. Using local data only.")
                print("💡 To connect to database, add your Supabase credentials to .streamlit/secrets.toml")
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            print("💡 The application will work in offline mode.")
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.supabase is not None
    
    # DEALS CRUD Operations
    def create_deal(self, deal: Deal) -> bool:
        """Create a new deal in the database"""
        if not self.is_connected():
            return False
        
        try:
            deal_data = deal.to_dict()
            result = self.supabase.table('deals').insert(deal_data).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error creating deal: {str(e)}")
            return False
    
    def get_deals(self, user_id: Optional[str] = None) -> List[Deal]:
        """Get all deals, optionally filtered by user"""
        if not self.is_connected():
            return []
        
        try:
            query = self.supabase.table('deals').select('*')
            if user_id:
                query = query.eq('user_id', user_id)
            
            result = query.order('created_at', desc=True).execute()
            
            deals = []
            for deal_data in result.data:
                deals.append(Deal.from_dict(deal_data))
            
            return deals
        except Exception as e:
            st.error(f"Error fetching deals: {str(e)}")
            return []
    
    def get_deal_by_id(self, deal_id: str) -> Optional[Deal]:
        """Get a specific deal by ID"""
        if not self.is_connected():
            return None
        
        try:
            result = self.supabase.table('deals').select('*').eq('id', deal_id).execute()
            if result.data:
                return Deal.from_dict(result.data[0])
            return None
        except Exception as e:
            st.error(f"Error fetching deal: {str(e)}")
            return None
    
    def update_deal(self, deal: Deal) -> bool:
        """Update an existing deal"""
        if not self.is_connected():
            return False
        
        try:
            deal.updated_at = datetime.now()
            deal_data = deal.to_dict()
            result = self.supabase.table('deals').update(deal_data).eq('id', deal.id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error updating deal: {str(e)}")
            return False
    
    def delete_deal(self, deal_id: str) -> bool:
        """Delete a deal"""
        if not self.is_connected():
            return False
        
        try:
            result = self.supabase.table('deals').delete().eq('id', deal_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deleting deal: {str(e)}")
            return False
    
    # INVESTORS CRUD Operations
    def create_investor(self, investor: Investor) -> bool:
        """Create a new investor in the database"""
        if not self.is_connected():
            return False
        
        try:
            investor_data = investor.to_dict()
            result = self.supabase.table('investors').insert(investor_data).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error creating investor: {str(e)}")
            return False
    
    def get_investors(self, user_id: Optional[str] = None) -> List[Investor]:
        """Get all investors, optionally filtered by user"""
        if not self.is_connected():
            return []
        
        try:
            query = self.supabase.table('investors').select('*')
            if user_id:
                query = query.eq('user_id', user_id)
            
            result = query.order('created_at', desc=True).execute()
            
            investors = []
            for investor_data in result.data:
                investors.append(Investor.from_dict(investor_data))
            
            return investors
        except Exception as e:
            st.error(f"Error fetching investors: {str(e)}")
            return []
    
    def update_investor(self, investor: Investor) -> bool:
        """Update an existing investor"""
        if not self.is_connected():
            return False
        
        try:
            investor.updated_at = datetime.now()
            investor_data = investor.to_dict()
            result = self.supabase.table('investors').update(investor_data).eq('id', investor.id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error updating investor: {str(e)}")
            return False
    
    def delete_investor(self, investor_id: str) -> bool:
        """Delete an investor"""
        if not self.is_connected():
            return False
        
        try:
            result = self.supabase.table('investors').delete().eq('id', investor_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deleting investor: {str(e)}")
            return False
    
    # PORTFOLIO CRUD Operations
    def create_portfolio_entry(self, portfolio: Portfolio) -> bool:
        """Create a new portfolio entry"""
        if not self.is_connected():
            return False
        
        try:
            portfolio_data = portfolio.to_dict()
            result = self.supabase.table('portfolio').insert(portfolio_data).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error creating portfolio entry: {str(e)}")
            return False
    
    def get_portfolio(self, user_id: Optional[str] = None) -> List[Portfolio]:
        """Get all portfolio entries, optionally filtered by user"""
        if not self.is_connected():
            return []
        
        try:
            query = self.supabase.table('portfolio').select('*')
            if user_id:
                query = query.eq('user_id', user_id)
            
            result = query.order('created_at', desc=True).execute()
            
            portfolio = []
            for portfolio_data in result.data:
                portfolio.append(Portfolio.from_dict(portfolio_data))
            
            return portfolio
        except Exception as e:
            st.error(f"Error fetching portfolio: {str(e)}")
            return []
    
    # ANALYTICS AND REPORTING
    def get_deal_analytics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics data for deals"""
        deals = self.get_deals(user_id)
        
        if not deals:
            return {
                'total_deals': 0,
                'avg_ai_score': 0,
                'total_value': 0,
                'status_breakdown': {},
                'property_type_breakdown': {}
            }
        
        total_deals = len(deals)
        avg_ai_score = sum(deal.ai_score for deal in deals) / total_deals
        total_value = sum(deal.purchase_price for deal in deals)
        
        status_breakdown = {}
        property_type_breakdown = {}
        
        for deal in deals:
            # Status breakdown
            status_breakdown[deal.status] = status_breakdown.get(deal.status, 0) + 1
            
            # Property type breakdown
            property_type_breakdown[deal.property_type] = property_type_breakdown.get(deal.property_type, 0) + 1
        
        return {
            'total_deals': total_deals,
            'avg_ai_score': round(avg_ai_score, 1),
            'total_value': total_value,
            'status_breakdown': status_breakdown,
            'property_type_breakdown': property_type_breakdown
        }
    
    def get_high_scoring_deals(self, min_score: int = 80, user_id: Optional[str] = None) -> List[Deal]:
        """Get deals with high AI scores"""
        deals = self.get_deals(user_id)
        return [deal for deal in deals if deal.ai_score >= min_score]
    
    def search_deals(self, search_term: str, user_id: Optional[str] = None) -> List[Deal]:
        """Search deals by address, property type, or status"""
        deals = self.get_deals(user_id)
        search_term = search_term.lower()
        
        filtered_deals = []
        for deal in deals:
            if (search_term in deal.address.lower() or 
                search_term in deal.property_type.lower() or 
                search_term in deal.status.lower()):
                filtered_deals.append(deal)
        
        return filtered_deals

# Global database service instance
db_service = DatabaseService()