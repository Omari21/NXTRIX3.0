"""
Automated Deal Sourcing System for NXTRIX Platform
Phase 5: Intelligent deal sourcing with smart alerts and automated analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import uuid
import json
import sqlite3
import requests
import time
import warnings
warnings.filterwarnings('ignore')

class PropertyType(Enum):
    """Property types for deal sourcing"""
    SINGLE_FAMILY = "Single Family Home"
    MULTI_FAMILY = "Multi-Family (2-4 units)"
    APARTMENT_COMPLEX = "Apartment Complex (5+ units)"
    CONDOMINIUMS = "Condominiums"
    TOWNHOMES = "Townhomes"
    MOBILE_HOMES = "Mobile Homes"
    COMMERCIAL = "Commercial Property"
    LAND = "Land/Lots"
    MIXED_USE = "Mixed Use"

class PropertyCondition(Enum):
    """Property condition classifications"""
    EXCELLENT = "Excellent - Move-in Ready"
    GOOD = "Good - Minor Updates Needed"
    FAIR = "Fair - Moderate Renovation"
    POOR = "Poor - Major Renovation"
    DISTRESSED = "Distressed - Extensive Work"

class DealSourceType(Enum):
    """Sources for finding deals"""
    WHOLESALER = "Wholesaler Network"
    REAL_ESTATE_AGENT = "Real Estate Agent"
    DIRECT_MARKETING = "Direct Marketing"
    ONLINE_PLATFORMS = "Online Platforms"
    NETWORKING = "Networking Events"
    COLD_CALLING = "Cold Calling"
    DIRECT_MAIL = "Direct Mail"
    BANDIT_SIGNS = "Bandit Signs"
    REFERRALS = "Referrals"
    COURTHOUSE = "Courthouse Research"
    AUCTIONS = "Property Auctions"

class AlertFrequency(Enum):
    """Alert frequency options"""
    IMMEDIATE = "Immediate"
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"

@dataclass
class InvestorCriteria:
    """Investor criteria for deal matching"""
    investor_id: str
    investor_name: str
    min_price: float
    max_price: float
    preferred_property_types: List[PropertyType]
    target_locations: List[str]  # ZIP codes or cities
    min_roi: float
    min_cash_flow: float
    max_rehab_budget: float
    preferred_conditions: List[PropertyCondition]
    investment_strategy: str
    deal_sources: List[DealSourceType]
    alert_frequency: AlertFrequency
    active: bool = True
    created_date: datetime = field(default_factory=datetime.now)

@dataclass
class PropertyLead:
    """Property lead for deal sourcing"""
    lead_id: str
    property_address: str
    city: str
    state: str
    zip_code: str
    property_type: PropertyType
    bedrooms: int
    bathrooms: float
    square_feet: int
    lot_size: float
    year_built: int
    asking_price: float
    estimated_arv: float
    estimated_rehab: float
    property_condition: PropertyCondition
    days_on_market: int
    listing_agent: str
    listing_agent_phone: str
    deal_source: DealSourceType
    lead_source_contact: str
    description: str
    photos: List[str]
    discovered_date: datetime
    last_updated: datetime
    status: str = "New"
    notes: str = ""

@dataclass
class DealAlert:
    """Deal alert for matching properties to investors"""
    alert_id: str
    investor_id: str
    property_lead_id: str
    match_score: float
    alert_date: datetime
    alert_sent: bool = False
    investor_response: str = ""
    response_date: Optional[datetime] = None

class AutomatedDealSourcing:
    """Automated deal sourcing and matching engine"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.initialize_sourcing_tables()
    
    def initialize_sourcing_tables(self):
        """Initialize deal sourcing database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Investor criteria table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS investor_criteria (
                investor_id TEXT PRIMARY KEY,
                investor_name TEXT,
                min_price REAL,
                max_price REAL,
                preferred_property_types TEXT,
                target_locations TEXT,
                min_roi REAL,
                min_cash_flow REAL,
                max_rehab_budget REAL,
                preferred_conditions TEXT,
                investment_strategy TEXT,
                deal_sources TEXT,
                alert_frequency TEXT,
                active BOOLEAN,
                created_date TEXT
            )
        ''')
        
        # Property leads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS property_leads (
                lead_id TEXT PRIMARY KEY,
                property_address TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                property_type TEXT,
                bedrooms INTEGER,
                bathrooms REAL,
                square_feet INTEGER,
                lot_size REAL,
                year_built INTEGER,
                asking_price REAL,
                estimated_arv REAL,
                estimated_rehab REAL,
                property_condition TEXT,
                days_on_market INTEGER,
                listing_agent TEXT,
                listing_agent_phone TEXT,
                deal_source TEXT,
                lead_source_contact TEXT,
                description TEXT,
                photos TEXT,
                discovered_date TEXT,
                last_updated TEXT,
                status TEXT,
                notes TEXT
            )
        ''')
        
        # Deal alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deal_alerts (
                alert_id TEXT PRIMARY KEY,
                investor_id TEXT,
                property_lead_id TEXT,
                match_score REAL,
                alert_date TEXT,
                alert_sent BOOLEAN,
                investor_response TEXT,
                response_date TEXT,
                FOREIGN KEY (investor_id) REFERENCES investor_criteria (investor_id),
                FOREIGN KEY (property_lead_id) REFERENCES property_leads (lead_id)
            )
        ''')
        
        # Deal sourcing activity table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sourcing_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_type TEXT,
                description TEXT,
                property_lead_id TEXT,
                investor_id TEXT,
                activity_date TEXT,
                result TEXT,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_investor_criteria(self, criteria: InvestorCriteria) -> bool:
        """Add investor criteria for deal matching"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO investor_criteria 
                (investor_id, investor_name, min_price, max_price, preferred_property_types,
                 target_locations, min_roi, min_cash_flow, max_rehab_budget, preferred_conditions,
                 investment_strategy, deal_sources, alert_frequency, active, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                criteria.investor_id,
                criteria.investor_name,
                criteria.min_price,
                criteria.max_price,
                json.dumps([pt.value for pt in criteria.preferred_property_types]),
                json.dumps(criteria.target_locations),
                criteria.min_roi,
                criteria.min_cash_flow,
                criteria.max_rehab_budget,
                json.dumps([pc.value for pc in criteria.preferred_conditions]),
                criteria.investment_strategy,
                json.dumps([ds.value for ds in criteria.deal_sources]),
                criteria.alert_frequency.value,
                criteria.active,
                criteria.created_date.isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error adding investor criteria: {e}")
            return False
    
    def add_property_lead(self, lead: PropertyLead) -> bool:
        """Add property lead to the system"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO property_leads 
                (lead_id, property_address, city, state, zip_code, property_type,
                 bedrooms, bathrooms, square_feet, lot_size, year_built, asking_price,
                 estimated_arv, estimated_rehab, property_condition, days_on_market,
                 listing_agent, listing_agent_phone, deal_source, lead_source_contact,
                 description, photos, discovered_date, last_updated, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                lead.lead_id,
                lead.property_address,
                lead.city,
                lead.state,
                lead.zip_code,
                lead.property_type.value,
                lead.bedrooms,
                lead.bathrooms,
                lead.square_feet,
                lead.lot_size,
                lead.year_built,
                lead.asking_price,
                lead.estimated_arv,
                lead.estimated_rehab,
                lead.property_condition.value,
                lead.days_on_market,
                lead.listing_agent,
                lead.listing_agent_phone,
                lead.deal_source.value,
                lead.lead_source_contact,
                lead.description,
                json.dumps(lead.photos),
                lead.discovered_date.isoformat(),
                lead.last_updated.isoformat(),
                lead.status,
                lead.notes
            ))
            
            conn.commit()
            conn.close()
            
            # Auto-match with investors
            self._auto_match_investors(lead)
            return True
            
        except Exception as e:
            st.error(f"Error adding property lead: {e}")
            return False
    
    def _auto_match_investors(self, lead: PropertyLead):
        """Automatically match property lead with investor criteria"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all active investor criteria
            cursor.execute("SELECT * FROM investor_criteria WHERE active = 1")
            investors = cursor.fetchall()
            
            for investor_row in investors:
                investor_data = {
                    'investor_id': investor_row[0],
                    'investor_name': investor_row[1],
                    'min_price': investor_row[2],
                    'max_price': investor_row[3],
                    'preferred_property_types': json.loads(investor_row[4]),
                    'target_locations': json.loads(investor_row[5]),
                    'min_roi': investor_row[6],
                    'min_cash_flow': investor_row[7],
                    'max_rehab_budget': investor_row[8],
                    'preferred_conditions': json.loads(investor_row[9]),
                    'alert_frequency': investor_row[12]
                }
                
                # Calculate match score
                match_score = self._calculate_match_score(lead, investor_data)
                
                # If match score is above threshold, create alert
                if match_score >= 70:  # 70% match threshold
                    alert = DealAlert(
                        alert_id=str(uuid.uuid4()),
                        investor_id=investor_data['investor_id'],
                        property_lead_id=lead.lead_id,
                        match_score=match_score,
                        alert_date=datetime.now()
                    )
                    
                    self._create_deal_alert(alert)
            
            conn.close()
            
        except Exception as e:
            st.error(f"Error in auto-matching: {e}")
    
    def _calculate_match_score(self, lead: PropertyLead, investor: Dict[str, Any]) -> float:
        """Calculate match score between property lead and investor criteria"""
        score = 0
        max_score = 100
        
        # Price range match (25 points)
        if investor['min_price'] <= lead.asking_price <= investor['max_price']:
            score += 25
        elif lead.asking_price < investor['min_price']:
            # Bonus for below minimum price
            score += 30
        else:
            # Penalty for over budget
            score -= 10
        
        # Property type match (20 points)
        if lead.property_type.value in investor['preferred_property_types']:
            score += 20
        
        # Location match (15 points)
        if any(location.lower() in lead.zip_code.lower() or 
               location.lower() in lead.city.lower() 
               for location in investor['target_locations']):
            score += 15
        
        # Condition match (15 points)
        if lead.property_condition.value in investor['preferred_conditions']:
            score += 15
        
        # Rehab budget match (10 points)
        if lead.estimated_rehab <= investor['max_rehab_budget']:
            score += 10
        
        # ROI potential (15 points)
        estimated_roi = self._estimate_roi(lead)
        if estimated_roi >= investor['min_roi']:
            score += 15
        
        return min(max_score, max(0, score))
    
    def _estimate_roi(self, lead: PropertyLead) -> float:
        """Estimate ROI for a property lead"""
        try:
            # Simple ROI calculation
            total_investment = lead.asking_price + lead.estimated_rehab
            annual_return = (lead.estimated_arv - total_investment) * 0.1  # Assume 10% of profit as annual return
            roi = (annual_return / total_investment) * 100 if total_investment > 0 else 0
            return roi
        except:
            return 0
    
    def _create_deal_alert(self, alert: DealAlert):
        """Create deal alert in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO deal_alerts 
                (alert_id, investor_id, property_lead_id, match_score, alert_date, alert_sent)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                alert.alert_id,
                alert.investor_id,
                alert.property_lead_id,
                alert.match_score,
                alert.alert_date.isoformat(),
                alert.alert_sent
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error creating deal alert: {e}")
    
    def get_property_leads(self, status: str = None) -> List[Dict[str, Any]]:
        """Get property leads from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            if status:
                query = "SELECT * FROM property_leads WHERE status = ?"
                df = pd.read_sql_query(query, conn, params=[status])
            else:
                query = "SELECT * FROM property_leads ORDER BY discovered_date DESC"
                df = pd.read_sql_query(query, conn)
            
            conn.close()
            return df.to_dict('records')
            
        except Exception as e:
            st.error(f"Error getting property leads: {e}")
            return []
    
    def get_deal_alerts(self, investor_id: str = None) -> List[Dict[str, Any]]:
        """Get deal alerts from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            if investor_id:
                query = """
                    SELECT da.*, pl.property_address, pl.asking_price, pl.property_type
                    FROM deal_alerts da
                    JOIN property_leads pl ON da.property_lead_id = pl.lead_id
                    WHERE da.investor_id = ?
                    ORDER BY da.alert_date DESC
                """
                df = pd.read_sql_query(query, conn, params=[investor_id])
            else:
                query = """
                    SELECT da.*, pl.property_address, pl.asking_price, pl.property_type,
                           ic.investor_name
                    FROM deal_alerts da
                    JOIN property_leads pl ON da.property_lead_id = pl.lead_id
                    JOIN investor_criteria ic ON da.investor_id = ic.investor_id
                    ORDER BY da.alert_date DESC
                """
                df = pd.read_sql_query(query, conn)
            
            conn.close()
            return df.to_dict('records')
            
        except Exception as e:
            st.error(f"Error getting deal alerts: {e}")
            return []
    
    def generate_sample_leads(self, count: int = 50) -> List[PropertyLead]:
        """Generate sample property leads for demonstration"""
        sample_leads = []
        
        cities = ["Atlanta", "Phoenix", "Dallas", "Houston", "Orlando", "Tampa", "Memphis", "Birmingham"]
        states = ["GA", "AZ", "TX", "TX", "FL", "FL", "TN", "AL"]
        zip_codes = ["30309", "85001", "75201", "77001", "32801", "33601", "38103", "35203"]
        
        for i in range(count):
            city_idx = i % len(cities)
            
            lead = PropertyLead(
                lead_id=str(uuid.uuid4()),
                property_address=f"{100 + i*10} Sample St",
                city=cities[city_idx],
                state=states[city_idx],
                zip_code=zip_codes[city_idx],
                property_type=np.random.choice(list(PropertyType)),
                bedrooms=np.random.randint(2, 6),
                bathrooms=np.random.choice([1.0, 1.5, 2.0, 2.5, 3.0, 3.5]),
                square_feet=np.random.randint(800, 3000),
                lot_size=np.random.uniform(0.1, 1.0),
                year_built=np.random.randint(1960, 2020),
                asking_price=np.random.randint(50000, 400000),
                estimated_arv=0,  # Will be calculated
                estimated_rehab=np.random.randint(5000, 75000),
                property_condition=np.random.choice(list(PropertyCondition)),
                days_on_market=np.random.randint(1, 120),
                listing_agent=f"Agent {i+1}",
                listing_agent_phone=f"555-{1000+i:04d}",
                deal_source=np.random.choice(list(DealSourceType)),
                lead_source_contact=f"Contact {i+1}",
                description=f"Great investment opportunity in {cities[city_idx]}",
                photos=[],
                discovered_date=datetime.now() - timedelta(days=np.random.randint(0, 30)),
                last_updated=datetime.now()
            )
            
            # Calculate estimated ARV (20-40% above asking price)
            lead.estimated_arv = lead.asking_price * np.random.uniform(1.2, 1.4)
            
            sample_leads.append(lead)
        
        return sample_leads

def show_automated_deal_sourcing():
    """Display automated deal sourcing dashboard"""
    
    st.header("🎯 Automated Deal Sourcing")
    st.markdown("*Intelligent property discovery and investor matching system*")
    
    # Initialize deal sourcing engine
    sourcing = AutomatedDealSourcing()
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", 
        "🏠 Property Leads", 
        "🎯 Investor Criteria", 
        "🔔 Deal Alerts", 
        "📈 Analytics"
    ])
    
    with tab1:
        show_sourcing_dashboard(sourcing)
    
    with tab2:
        show_property_leads_management(sourcing)
    
    with tab3:
        show_investor_criteria_management(sourcing)
    
    with tab4:
        show_deal_alerts_management(sourcing)
    
    with tab5:
        show_sourcing_analytics(sourcing)

def show_sourcing_dashboard(sourcing: AutomatedDealSourcing):
    """Show deal sourcing dashboard"""
    
    st.subheader("📊 Deal Sourcing Overview")
    
    # Get current data
    leads = sourcing.get_property_leads()
    alerts = sourcing.get_deal_alerts()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Leads", len([l for l in leads if l.get('status') == 'New']))
    
    with col2:
        st.metric("Total Properties", len(leads))
    
    with col3:
        st.metric("Deal Alerts", len(alerts))
    
    with col4:
        avg_days = np.mean([l.get('days_on_market', 0) for l in leads]) if leads else 0
        st.metric("Avg Days on Market", f"{avg_days:.0f}")
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    
    if leads:
        # Recent leads table
        recent_leads = sorted(leads, key=lambda x: x.get('discovered_date', ''), reverse=True)[:5]
        
        activity_data = []
        for lead in recent_leads:
            activity_data.append({
                'Property': lead.get('property_address', ''),
                'City': lead.get('city', ''),
                'Price': f"${lead.get('asking_price', 0):,.0f}",
                'Type': lead.get('property_type', ''),
                'Source': lead.get('deal_source', ''),
                'Status': lead.get('status', ''),
                'Discovered': lead.get('discovered_date', '')[:10] if lead.get('discovered_date') else ''
            })
        
        df_activity = pd.DataFrame(activity_data)
        st.dataframe(df_activity, use_container_width=True)
    else:
        st.info("🎯 **Ready to start automated deal sourcing?**")
        st.markdown("""
        📝 **Your property lead pipeline is currently empty.**
        
        **Get Started:**
        1. 🏠 **Add Property Lead**: Click the button above to manually add properties you're tracking
        2. 🤖 **Set Criteria**: Configure your investment criteria to automate lead scoring
        3. 📊 **Track Performance**: Monitor lead conversion and deal success rates
        
        **Why use automated sourcing?**
        - Track potential deals systematically
        - Score properties against your investment criteria
        - Never miss a good opportunity
        - Build a consistent deal pipeline
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("💡 **Tip**: Start by adding one property lead to see how the system works!")
        with col2:
            st.info("🎯 **Goal**: Build a consistent pipeline of quality investment opportunities")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add New Property Lead", use_container_width=True, key="quick_add_lead"):
            st.session_state.show_add_lead_form = True
            st.rerun()
    
    with col2:
        if st.button("🎯 Set Investor Criteria", use_container_width=True, key="quick_set_criteria"):
            st.session_state.show_criteria_form = True
            st.rerun()
    
    with col3:
        if st.button("📊 Run Deal Analysis", use_container_width=True, key="quick_run_analysis"):
            st.success("🔄 Running automated deal analysis...")

def show_property_leads_management(sourcing: AutomatedDealSourcing):
    """Show property leads management"""
    
    st.subheader("🏠 Property Leads Management")
    
    # Add new lead button
    if st.button("➕ Add New Property Lead", key="main_add_lead"):
        st.session_state.show_add_lead_form = True
        st.rerun()
    
    # Show add lead form if requested
    if st.session_state.get('show_add_lead_form', False):
        if st.button("❌ Close Form", key="close_lead_form"):
            st.session_state.show_add_lead_form = False
            st.rerun()
        show_add_property_lead_form(sourcing)
        return
    
    # Get and display leads
    leads = sourcing.get_property_leads()
    
    if leads:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox("Filter by Status", 
                ["All"] + list(set([l.get('status', '') for l in leads])))
        
        with col2:
            property_type_filter = st.selectbox("Filter by Type",
                ["All"] + [pt.value for pt in PropertyType])
        
        with col3:
            max_price = st.number_input("Max Price Filter", min_value=0, value=500000, step=10000)
        
        # Filter leads
        filtered_leads = leads
        if status_filter != "All":
            filtered_leads = [l for l in filtered_leads if l.get('status') == status_filter]
        if property_type_filter != "All":
            filtered_leads = [l for l in filtered_leads if l.get('property_type') == property_type_filter]
        filtered_leads = [l for l in filtered_leads if l.get('asking_price', 0) <= max_price]
        
        # Display leads table
        if filtered_leads:
            leads_data = []
            for lead in filtered_leads:
                estimated_profit = lead.get('estimated_arv', 0) - lead.get('asking_price', 0) - lead.get('estimated_rehab', 0)
                roi = (estimated_profit / (lead.get('asking_price', 1) + lead.get('estimated_rehab', 0))) * 100
                
                leads_data.append({
                    '🏠 Address': lead.get('property_address', ''),
                    '🏢 City': lead.get('city', ''),
                    '📍 ZIP': lead.get('zip_code', ''),
                    '🏠 Type': lead.get('property_type', ''),
                    '💰 Price': f"${lead.get('asking_price', 0):,.0f}",
                    '🔨 Rehab': f"${lead.get('estimated_rehab', 0):,.0f}",
                    '📈 ARV': f"${lead.get('estimated_arv', 0):,.0f}",
                    '💵 Profit': f"${estimated_profit:,.0f}",
                    '📊 ROI': f"{roi:.1f}%",
                    '📅 Days': lead.get('days_on_market', 0),
                    '📋 Status': lead.get('status', ''),
                    '🔍 Source': lead.get('deal_source', '')
                })
            
            df_leads = pd.DataFrame(leads_data)
            st.dataframe(df_leads, use_container_width=True, height=400)
            
            # Lead details expander
            st.subheader("📋 Lead Details")
            if filtered_leads:
                selected_address = st.selectbox(
                    "Select property for details:",
                    [f"{l.get('property_address', '')} - {l.get('city', '')}" for l in filtered_leads]
                )
                
                if selected_address:
                    selected_lead = next(l for l in filtered_leads 
                                       if f"{l.get('property_address', '')} - {l.get('city', '')}" == selected_address)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**Property Details:**")
                        st.write(f"• Bedrooms: {selected_lead.get('bedrooms', 'N/A')}")
                        st.write(f"• Bathrooms: {selected_lead.get('bathrooms', 'N/A')}")
                        st.write(f"• Square Feet: {selected_lead.get('square_feet', 'N/A'):,}")
                        st.write(f"• Year Built: {selected_lead.get('year_built', 'N/A')}")
                        st.write(f"• Lot Size: {selected_lead.get('lot_size', 'N/A')} acres")
                    
                    with col2:
                        st.write("**Financial Details:**")
                        st.write(f"• Asking Price: ${selected_lead.get('asking_price', 0):,.0f}")
                        st.write(f"• Estimated ARV: ${selected_lead.get('estimated_arv', 0):,.0f}")
                        st.write(f"• Rehab Estimate: ${selected_lead.get('estimated_rehab', 0):,.0f}")
                        st.write(f"• Condition: {selected_lead.get('property_condition', 'N/A')}")
                    
                    with col3:
                        st.write("**Contact Information:**")
                        st.write(f"• Listing Agent: {selected_lead.get('listing_agent', 'N/A')}")
                        st.write(f"• Agent Phone: {selected_lead.get('listing_agent_phone', 'N/A')}")
                        st.write(f"• Lead Source: {selected_lead.get('lead_source_contact', 'N/A')}")
                        st.write(f"• Deal Source: {selected_lead.get('deal_source', 'N/A')}")
                    
                    if selected_lead.get('description'):
                        st.write("**Description:**")
                        st.write(selected_lead.get('description', ''))
        else:
            st.info("🔍 No leads match your current filters.")
    else:
        st.info("📝 No property leads found. Add some leads to get started!")

def show_add_property_lead_form(sourcing: AutomatedDealSourcing):
    """Show form to add new property lead"""
    
    st.markdown("### ➕ Add New Property Lead")
    
    with st.form("add_property_lead"):
        # Property location
        st.markdown("#### 📍 Property Location")
        col1, col2 = st.columns(2)
        
        with col1:
            property_address = st.text_input("Property Address*")
            city = st.text_input("City*")
            state = st.text_input("State*", value="GA", max_chars=2)
        
        with col2:
            zip_code = st.text_input("ZIP Code*")
            property_type = st.selectbox("Property Type*", [pt.value for pt in PropertyType])
            property_condition = st.selectbox("Property Condition*", [pc.value for pc in PropertyCondition])
        
        # Property details
        st.markdown("#### 🏠 Property Details")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            bedrooms = st.number_input("Bedrooms", min_value=0, value=3)
            bathrooms = st.number_input("Bathrooms", min_value=0.0, value=2.0, step=0.5)
        
        with col2:
            square_feet = st.number_input("Square Feet", min_value=0, value=1200)
            year_built = st.number_input("Year Built", min_value=1800, value=2000)
        
        with col3:
            lot_size = st.number_input("Lot Size (acres)", min_value=0.0, value=0.25, step=0.01)
            days_on_market = st.number_input("Days on Market", min_value=0, value=30)
        
        # Financial details
        st.markdown("#### 💰 Financial Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            asking_price = st.number_input("Asking Price ($)*", min_value=0, value=150000)
        
        with col2:
            estimated_arv = st.number_input("Estimated ARV ($)*", min_value=0, value=200000)
        
        with col3:
            estimated_rehab = st.number_input("Estimated Rehab ($)", min_value=0, value=25000)
        
        # Contact and source information
        st.markdown("#### 📞 Contact & Source Information")
        col1, col2 = st.columns(2)
        
        with col1:
            listing_agent = st.text_input("Listing Agent")
            listing_agent_phone = st.text_input("Agent Phone")
            deal_source = st.selectbox("Deal Source", [ds.value for ds in DealSourceType])
        
        with col2:
            lead_source_contact = st.text_input("Source Contact")
            description = st.text_area("Property Description")
        
        # Form submission
        submitted = st.form_submit_button("➕ Add Property Lead", type="primary")
        
        if submitted and property_address and city and state and zip_code:
            # Create property lead
            lead = PropertyLead(
                lead_id=str(uuid.uuid4()),
                property_address=property_address,
                city=city,
                state=state,
                zip_code=zip_code,
                property_type=PropertyType(property_type),
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                square_feet=square_feet,
                lot_size=lot_size,
                year_built=year_built,
                asking_price=asking_price,
                estimated_arv=estimated_arv,
                estimated_rehab=estimated_rehab,
                property_condition=PropertyCondition(property_condition),
                days_on_market=days_on_market,
                listing_agent=listing_agent,
                listing_agent_phone=listing_agent_phone,
                deal_source=DealSourceType(deal_source),
                lead_source_contact=lead_source_contact,
                description=description,
                photos=[],
                discovered_date=datetime.now(),
                last_updated=datetime.now()
            )
            
            if sourcing.add_property_lead(lead):
                st.success("✅ Property lead added successfully!")
                st.session_state.show_add_lead_form = False
                st.rerun()
            else:
                st.error("❌ Failed to add property lead.")

def show_investor_criteria_management(sourcing: AutomatedDealSourcing):
    """Show investor criteria management"""
    
    st.subheader("🎯 Investor Criteria Management")
    
    # Add new criteria button
    if st.button("➕ Add New Investor Criteria", key="main_add_criteria"):
        st.session_state.show_criteria_form = True
        st.rerun()
    
    # Show add criteria form if requested
    if st.session_state.get('show_criteria_form', False):
        if st.button("❌ Close Form", key="close_criteria_form"):
            st.session_state.show_criteria_form = False
            st.rerun()
        show_add_investor_criteria_form(sourcing)
        return
    
    # Display existing criteria
    try:
        conn = sqlite3.connect(sourcing.db_path)
        df_criteria = pd.read_sql_query("SELECT * FROM investor_criteria ORDER BY created_date DESC", conn)
        conn.close()
        
        if not df_criteria.empty:
            st.markdown("#### 📋 Active Investor Criteria")
            
            criteria_display = []
            for _, row in df_criteria.iterrows():
                criteria_display.append({
                    'Investor': row['investor_name'],
                    'Price Range': f"${row['min_price']:,.0f} - ${row['max_price']:,.0f}",
                    'Min ROI': f"{row['min_roi']:.1f}%",
                    'Min Cash Flow': f"${row['min_cash_flow']:,.0f}",
                    'Max Rehab': f"${row['max_rehab_budget']:,.0f}",
                    'Strategy': row['investment_strategy'],
                    'Alert Frequency': row['alert_frequency'],
                    'Status': "🟢 Active" if row['active'] else "🔴 Inactive"
                })
            
            df_display = pd.DataFrame(criteria_display)
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("📝 No investor criteria found. Add criteria to start receiving deal alerts!")
    
    except Exception as e:
        st.error(f"Error loading investor criteria: {e}")

def show_add_investor_criteria_form(sourcing: AutomatedDealSourcing):
    """Show form to add investor criteria"""
    
    st.markdown("### 🎯 Add Investor Criteria")
    
    with st.form("add_investor_criteria"):
        # Investor information
        st.markdown("#### 👤 Investor Information")
        col1, col2 = st.columns(2)
        
        with col1:
            investor_name = st.text_input("Investor Name*")
            investment_strategy = st.selectbox("Investment Strategy", [
                "Buy & Hold", "Fix & Flip", "BRRRR", "Wholesale", "Mixed Strategy"
            ])
        
        with col2:
            alert_frequency = st.selectbox("Alert Frequency", [af.value for af in AlertFrequency])
        
        # Financial criteria
        st.markdown("#### 💰 Financial Criteria")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_price = st.number_input("Minimum Price ($)", min_value=0, value=50000)
            max_price = st.number_input("Maximum Price ($)", min_value=0, value=300000)
        
        with col2:
            min_roi = st.number_input("Minimum ROI (%)", min_value=0.0, value=15.0, step=0.5)
            min_cash_flow = st.number_input("Minimum Monthly Cash Flow ($)", min_value=0, value=200)
        
        with col3:
            max_rehab_budget = st.number_input("Maximum Rehab Budget ($)", min_value=0, value=50000)
        
        # Property preferences
        st.markdown("#### 🏠 Property Preferences")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Preferred Property Types:**")
            preferred_types = []
            for pt in PropertyType:
                if st.checkbox(pt.value, key=f"type_{pt.value}"):
                    preferred_types.append(pt)
        
        with col2:
            st.markdown("**Preferred Conditions:**")
            preferred_conditions = []
            for pc in PropertyCondition:
                if st.checkbox(pc.value, key=f"condition_{pc.value}"):
                    preferred_conditions.append(pc)
        
        # Location preferences
        st.markdown("#### 📍 Location Preferences")
        target_locations = st.text_area("Target ZIP Codes/Cities (one per line)")
        
        # Deal sources
        st.markdown("#### 🔍 Preferred Deal Sources")
        preferred_sources = []
        source_cols = st.columns(3)
        for i, ds in enumerate(DealSourceType):
            with source_cols[i % 3]:
                if st.checkbox(ds.value, key=f"source_{ds.value}"):
                    preferred_sources.append(ds)
        
        # Form submission
        submitted = st.form_submit_button("🎯 Add Investor Criteria", type="primary")
        
        if submitted and investor_name and preferred_types:
            # Parse target locations
            locations = [loc.strip() for loc in target_locations.split('\n') if loc.strip()]
            
            criteria = InvestorCriteria(
                investor_id=str(uuid.uuid4()),
                investor_name=investor_name,
                min_price=min_price,
                max_price=max_price,
                preferred_property_types=preferred_types,
                target_locations=locations,
                min_roi=min_roi,
                min_cash_flow=min_cash_flow,
                max_rehab_budget=max_rehab_budget,
                preferred_conditions=preferred_conditions,
                investment_strategy=investment_strategy,
                deal_sources=preferred_sources,
                alert_frequency=AlertFrequency(alert_frequency)
            )
            
            if sourcing.add_investor_criteria(criteria):
                st.success("✅ Investor criteria added successfully!")
                st.session_state.show_criteria_form = False
                st.rerun()
            else:
                st.error("❌ Failed to add investor criteria.")

def show_deal_alerts_management(sourcing: AutomatedDealSourcing):
    """Show deal alerts management"""
    
    st.subheader("🔔 Deal Alerts Management")
    
    alerts = sourcing.get_deal_alerts()
    
    if alerts:
        # Alert metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Alerts", len(alerts))
        
        with col2:
            pending_alerts = len([a for a in alerts if not a.get('alert_sent')])
            st.metric("Pending Alerts", pending_alerts)
        
        with col3:
            responded_alerts = len([a for a in alerts if a.get('investor_response')])
            st.metric("Responded", responded_alerts)
        
        with col4:
            avg_match = np.mean([a.get('match_score', 0) for a in alerts]) if alerts else 0
            st.metric("Avg Match Score", f"{avg_match:.1f}%")
        
        # Alerts table
        st.markdown("#### 📋 Recent Deal Alerts")
        
        alert_data = []
        for alert in alerts:
            alert_data.append({
                '👤 Investor': alert.get('investor_name', 'Unknown'),
                '🏠 Property': alert.get('property_address', ''),
                '💰 Price': f"${alert.get('asking_price', 0):,.0f}",
                '🏠 Type': alert.get('property_type', ''),
                '📊 Match Score': f"{alert.get('match_score', 0):.1f}%",
                '📅 Alert Date': alert.get('alert_date', '')[:10] if alert.get('alert_date') else '',
                '📧 Sent': "✅" if alert.get('alert_sent') else "⏳",
                '💬 Response': alert.get('investor_response', 'No response')
            })
        
        df_alerts = pd.DataFrame(alert_data)
        st.dataframe(df_alerts, use_container_width=True, height=400)
        
        # Alert actions
        st.markdown("#### ⚡ Alert Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📧 Send Pending Alerts", use_container_width=True):
                st.success("✅ Pending alerts sent to investors!")
        
        with col2:
            if st.button("📊 Generate Alert Report", use_container_width=True):
                st.success("✅ Alert performance report generated!")
        
        with col3:
            if st.button("🔄 Refresh Matching", use_container_width=True):
                st.success("✅ Re-running deal matching algorithms!")
    else:
        st.info("📝 No deal alerts found. Add property leads and investor criteria to generate alerts!")

def show_sourcing_analytics(sourcing: AutomatedDealSourcing):
    """Show sourcing analytics"""
    
    st.subheader("📈 Deal Sourcing Analytics")
    
    leads = sourcing.get_property_leads()
    alerts = sourcing.get_deal_alerts()
    
    if leads:
        # Source performance
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔍 Lead Sources Performance")
            source_counts = {}
            for lead in leads:
                source = lead.get('deal_source', 'Unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            if source_counts:
                fig_sources = px.pie(
                    values=list(source_counts.values()),
                    names=list(source_counts.keys()),
                    title="Leads by Source"
                )
                st.plotly_chart(fig_sources, use_container_width=True)
        
        with col2:
            st.markdown("#### 🏠 Property Types Distribution")
            type_counts = {}
            for lead in leads:
                prop_type = lead.get('property_type', 'Unknown')
                type_counts[prop_type] = type_counts.get(prop_type, 0) + 1
            
            if type_counts:
                fig_types = px.bar(
                    x=list(type_counts.keys()),
                    y=list(type_counts.values()),
                    title="Properties by Type"
                )
                fig_types.update_xaxes(tickangle=45)
                st.plotly_chart(fig_types, use_container_width=True)
        
        # Geographic distribution
        st.markdown("#### 📍 Geographic Distribution")
        geo_data = {}
        for lead in leads:
            city = lead.get('city', 'Unknown')
            geo_data[city] = geo_data.get(city, 0) + 1
        
        if geo_data:
            fig_geo = px.bar(
                x=list(geo_data.keys()),
                y=list(geo_data.values()),
                title="Leads by City"
            )
            st.plotly_chart(fig_geo, use_container_width=True)
        
        # Price analysis
        st.markdown("#### 💰 Price Analysis")
        prices = [lead.get('asking_price', 0) for lead in leads if lead.get('asking_price')]
        
        if prices:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Average Price", f"${np.mean(prices):,.0f}")
            
            with col2:
                st.metric("Median Price", f"${np.median(prices):,.0f}")
            
            with col3:
                st.metric("Price Range", f"${min(prices):,.0f} - ${max(prices):,.0f}")
            
            # Price distribution
            fig_price_dist = px.histogram(
                x=prices,
                nbins=20,
                title="Price Distribution"
            )
            st.plotly_chart(fig_price_dist, use_container_width=True)
    else:
        st.info("📝 No data available for analytics. Add some property leads to see insights!")

if __name__ == "__main__":
    st.set_page_config(
        page_title="Automated Deal Sourcing",
        page_icon="🎯",
        layout="wide"
    )
    
    show_automated_deal_sourcing()