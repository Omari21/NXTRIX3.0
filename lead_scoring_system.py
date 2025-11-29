"""
Lead Scoring System for NXTRIX CRM
Advanced algorithms for scoring and prioritizing leads
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import sqlite3
import uuid
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class LeadStatus(Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    REJECTED = "rejected"

class LeadSource(Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    EMAIL_CAMPAIGN = "email_campaign"
    COLD_OUTREACH = "cold_outreach"
    NETWORKING = "networking"
    ADVERTISEMENT = "advertisement"
    OTHER = "other"

@dataclass
class Lead:
    """Lead data structure"""
    id: str
    name: str
    email: str
    phone: str
    source: LeadSource
    status: LeadStatus
    property_interest: str
    budget_min: float
    budget_max: float
    investment_timeline: str
    experience_level: str
    preferred_areas: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    last_contact: Optional[datetime] = None
    score: int = 0
    notes: str = ""

class LeadScoringSystem:
    """Advanced lead scoring system"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize lead scoring database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leads (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    source TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'new',
                    property_interest TEXT,
                    budget_min REAL DEFAULT 0,
                    budget_max REAL DEFAULT 0,
                    investment_timeline TEXT,
                    experience_level TEXT,
                    preferred_areas TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_contact TIMESTAMP,
                    score INTEGER DEFAULT 0,
                    notes TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lead_activities (
                    id TEXT PRIMARY KEY,
                    lead_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    activity_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lead_id) REFERENCES leads (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scoring_rules (
                    id TEXT PRIMARY KEY,
                    rule_name TEXT NOT NULL,
                    criteria TEXT NOT NULL,
                    points INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Setup default scoring rules
            self.setup_default_scoring_rules()
            
        except Exception as e:
            st.error(f"Error initializing lead scoring database: {e}")
    
    def setup_default_scoring_rules(self):
        """Setup default lead scoring rules"""
        default_rules = [
            ("High Investment Budget", "budget_max >= 500000", 25),
            ("Medium Investment Budget", "budget_max >= 250000 AND budget_max < 500000", 15),
            ("Low Investment Budget", "budget_max >= 100000 AND budget_max < 250000", 10),
            ("Referral Source", "source == 'referral'", 20),
            ("Website Source", "source == 'website'", 15),
            ("Experienced Investor", "experience_level == 'experienced'", 15),
            ("Intermediate Investor", "experience_level == 'intermediate'", 10),
            ("Ready to Invest", "investment_timeline == 'immediately'", 20),
            ("6 Month Timeline", "investment_timeline == '6_months'", 15),
            ("Complete Contact Info", "phone IS NOT NULL AND email IS NOT NULL", 10),
            ("Recent Activity", "last_contact >= date('now', '-30 days')", 10)
        ]
        
        # Insert rules if they don't exist
        for rule_name, criteria, points in default_rules:
            if not self.get_scoring_rule_by_name(rule_name):
                self.create_scoring_rule(rule_name, criteria, points)
    
    def get_scoring_rule_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get scoring rule by name"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM scoring_rules WHERE rule_name = ?", (name,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'rule_name': row[1],
                    'criteria': row[2],
                    'points': row[3],
                    'is_active': bool(row[4])
                }
            
            conn.close()
            return None
            
        except Exception as e:
            return None
    
    def create_scoring_rule(self, name: str, criteria: str, points: int) -> bool:
        """Create a new scoring rule"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            rule_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO scoring_rules (id, rule_name, criteria, points)
                VALUES (?, ?, ?, ?)
            ''', (rule_id, name, criteria, points))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error creating scoring rule: {e}")
            return False
    
    def calculate_lead_score(self, lead: Lead) -> int:
        """Calculate comprehensive lead score"""
        score = 0
        
        # Budget scoring (40 points max)
        if lead.budget_max >= 500000:
            score += 25
        elif lead.budget_max >= 250000:
            score += 15
        elif lead.budget_max >= 100000:
            score += 10
        elif lead.budget_max >= 50000:
            score += 5
        
        # Source scoring (20 points max)
        source_scores = {
            LeadSource.REFERRAL: 20,
            LeadSource.WEBSITE: 15,
            LeadSource.NETWORKING: 15,
            LeadSource.SOCIAL_MEDIA: 10,
            LeadSource.EMAIL_CAMPAIGN: 8,
            LeadSource.ADVERTISEMENT: 5,
            LeadSource.COLD_OUTREACH: 3,
            LeadSource.OTHER: 2
        }
        score += source_scores.get(lead.source, 2)
        
        # Experience level scoring (15 points max)
        if lead.experience_level == "experienced":
            score += 15
        elif lead.experience_level == "intermediate":
            score += 10
        elif lead.experience_level == "beginner":
            score += 5
        
        # Timeline scoring (15 points max)
        if lead.investment_timeline == "immediately":
            score += 15
        elif lead.investment_timeline == "6_months":
            score += 10
        elif lead.investment_timeline == "1_year":
            score += 5
        
        # Contact completeness (10 points max)
        if lead.email and lead.phone:
            score += 10
        elif lead.email or lead.phone:
            score += 5
        
        # Recency bonus (10 points max)
        if lead.last_contact:
            days_since_contact = (datetime.now() - lead.last_contact).days
            if days_since_contact <= 7:
                score += 10
            elif days_since_contact <= 30:
                score += 5
        
        return min(100, score)  # Cap at 100
    
    def save_lead(self, lead: Lead) -> bool:
        """Save lead to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate score before saving
            lead.score = self.calculate_lead_score(lead)
            
            cursor.execute('''
                INSERT OR REPLACE INTO leads 
                (id, name, email, phone, source, status, property_interest, 
                 budget_min, budget_max, investment_timeline, experience_level, 
                 preferred_areas, created_at, last_contact, score, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                lead.id,
                lead.name,
                lead.email,
                lead.phone,
                lead.source.value,
                lead.status.value,
                lead.property_interest,
                lead.budget_min,
                lead.budget_max,
                lead.investment_timeline,
                lead.experience_level,
                json.dumps(lead.preferred_areas),
                lead.created_at.isoformat(),
                lead.last_contact.isoformat() if lead.last_contact else None,
                lead.score,
                lead.notes
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error saving lead: {e}")
            return False
    
    def get_leads(self, status: Optional[LeadStatus] = None, 
                  min_score: int = 0) -> List[Lead]:
        """Get leads with optional filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM leads WHERE score >= ?"
            params = [min_score]
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            query += " ORDER BY score DESC, created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            leads = []
            for row in rows:
                lead = Lead(
                    id=row[0],
                    name=row[1],
                    email=row[2],
                    phone=row[3] or "",
                    source=LeadSource(row[4]),
                    status=LeadStatus(row[5]),
                    property_interest=row[6] or "",
                    budget_min=row[7] or 0,
                    budget_max=row[8] or 0,
                    investment_timeline=row[9] or "",
                    experience_level=row[10] or "",
                    preferred_areas=json.loads(row[11]) if row[11] else [],
                    created_at=datetime.fromisoformat(row[12]),
                    last_contact=datetime.fromisoformat(row[13]) if row[13] else None,
                    score=row[14] or 0,
                    notes=row[15] or ""
                )
                leads.append(lead)
            
            conn.close()
            return leads
            
        except Exception as e:
            st.error(f"Error retrieving leads: {e}")
            return []
    
    def get_lead_statistics(self) -> Dict[str, Any]:
        """Get lead scoring statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total leads by score range
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN score >= 80 THEN 'Hot (80-100)'
                        WHEN score >= 60 THEN 'Warm (60-79)'
                        WHEN score >= 40 THEN 'Cold (40-59)'
                        ELSE 'Very Cold (0-39)'
                    END as score_range,
                    COUNT(*) as count
                FROM leads 
                GROUP BY score_range
            """)
            score_distribution = dict(cursor.fetchall())
            
            # Average score by source
            cursor.execute("""
                SELECT source, AVG(score) as avg_score, COUNT(*) as count
                FROM leads 
                GROUP BY source
                ORDER BY avg_score DESC
            """)
            source_performance = cursor.fetchall()
            
            # Conversion rates
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN status = 'converted' THEN 1 END) * 100.0 / COUNT(*) as conversion_rate,
                    AVG(score) as avg_score
                FROM leads
            """)
            conversion_data = cursor.fetchone()
            
            conn.close()
            
            return {
                'score_distribution': score_distribution,
                'source_performance': source_performance,
                'conversion_rate': conversion_data[0] if conversion_data else 0,
                'average_score': conversion_data[1] if conversion_data else 0
            }
            
        except Exception as e:
            st.error(f"Error getting lead statistics: {e}")
            return {}

def show_lead_scoring_system():
    """Show lead scoring system interface"""
    st.header("📊 Lead Scoring Algorithms")
    st.write("Advanced lead scoring and prioritization system for maximizing conversion rates.")
    
    # Initialize lead scoring system
    if 'lead_scoring_system' not in st.session_state:
        st.session_state.lead_scoring_system = LeadScoringSystem()
    
    scoring_system = st.session_state.lead_scoring_system
    
    # Get statistics
    stats = scoring_system.get_lead_statistics()
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_leads = sum(stats.get('score_distribution', {}).values())
        st.metric("Total Leads", total_leads)
    with col2:
        avg_score = stats.get('average_score', 0)
        st.metric("Average Score", f"{avg_score:.1f}/100")
    with col3:
        conversion_rate = stats.get('conversion_rate', 0)
        st.metric("Conversion Rate", f"{conversion_rate:.1f}%")
    with col4:
        hot_leads = stats.get('score_distribution', {}).get('Hot (80-100)', 0)
        st.metric("Hot Leads", hot_leads)
    
    # Lead scoring tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔥 Hot Leads",
        "➕ Add Lead",
        "📋 All Leads",
        "📊 Analytics",
        "⚙️ Scoring Rules"
    ])
    
    with tab1:
        show_hot_leads(scoring_system)
    
    with tab2:
        show_add_lead_form(scoring_system)
    
    with tab3:
        show_all_leads(scoring_system)
    
    with tab4:
        show_lead_analytics(scoring_system, stats)
    
    with tab5:
        show_scoring_rules(scoring_system)

def show_hot_leads(scoring_system: LeadScoringSystem):
    """Show high-scoring leads"""
    st.subheader("🔥 Hot Leads (Score ≥ 80)")
    
    hot_leads = scoring_system.get_leads(min_score=80)
    
    if hot_leads:
        st.success(f"🎯 You have {len(hot_leads)} hot leads ready for immediate follow-up!")
        
        for lead in hot_leads:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**{lead.name}**")
                    st.caption(f"📧 {lead.email} • 📱 {lead.phone}")
                    st.caption(f"💰 Budget: ${lead.budget_min:,.0f} - ${lead.budget_max:,.0f}")
                
                with col2:
                    st.caption(f"Source: {lead.source.value.replace('_', ' ').title()}")
                    st.caption(f"Experience: {lead.experience_level.title()}")
                    st.caption(f"Timeline: {lead.investment_timeline.replace('_', ' ').title()}")
                
                with col3:
                    # Score with color coding
                    if lead.score >= 90:
                        st.markdown(f"🔴 **{lead.score}/100**")
                    elif lead.score >= 80:
                        st.markdown(f"🟠 **{lead.score}/100**")
                    else:
                        st.markdown(f"🟡 **{lead.score}/100**")
                
                with col4:
                    if st.button("📞 Contact", key=f"contact_{lead.id}"):
                        st.info("📞 Contact initiated! (Integration with communication system)")
                    
                    status_color = {
                        LeadStatus.NEW: "🟢",
                        LeadStatus.CONTACTED: "🟡",
                        LeadStatus.QUALIFIED: "🟠",
                        LeadStatus.CONVERTED: "✅",
                        LeadStatus.REJECTED: "❌"
                    }
                    st.caption(f"{status_color.get(lead.status, '⚪')} {lead.status.value.title()}")
                
                st.markdown("---")
    else:
        st.info("📭 No hot leads found. Focus on lead generation and nurturing existing leads!")
        
        # Suggestions for improvement
        st.markdown("### 💡 Lead Generation Suggestions")
        st.write("• Launch targeted digital marketing campaigns")
        st.write("• Implement referral programs")
        st.write("• Attend networking events")
        st.write("• Optimize website for lead capture")

def show_add_lead_form(scoring_system: LeadScoringSystem):
    """Show add lead form"""
    st.subheader("➕ Add New Lead")
    
    with st.form("add_lead_form"):
        # Basic contact info
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name*", placeholder="John Smith")
            email = st.text_input("Email*", placeholder="john@example.com")
            phone = st.text_input("Phone", placeholder="+1 (555) 123-4567")
        
        with col2:
            source = st.selectbox("Lead Source", [s.value.replace('_', ' ').title() for s in LeadSource])
            investment_timeline = st.selectbox("Investment Timeline", [
                "Immediately", "6 Months", "1 Year", "2+ Years", "Just Exploring"
            ])
            experience_level = st.selectbox("Experience Level", [
                "Beginner", "Intermediate", "Experienced", "Professional"
            ])
        
        # Investment criteria
        st.markdown("### 💰 Investment Criteria")
        col3, col4 = st.columns(2)
        
        with col3:
            budget_min = st.number_input("Minimum Budget ($)", min_value=0, value=100000, step=10000)
            budget_max = st.number_input("Maximum Budget ($)", min_value=0, value=500000, step=10000)
        
        with col4:
            property_interest = st.selectbox("Property Interest", [
                "Single Family Homes", "Multi-Family", "Commercial", 
                "Fix & Flip", "Buy & Hold", "Any"
            ])
            preferred_areas = st.text_input("Preferred Areas", 
                placeholder="Downtown, Suburbs, etc.")
        
        notes = st.text_area("Notes", placeholder="Additional information about the lead...")
        
        submitted = st.form_submit_button("💾 Add Lead", type="primary")
        
        if submitted and name and email:
            # Create lead
            lead = Lead(
                id=str(uuid.uuid4()),
                name=name,
                email=email,
                phone=phone,
                source=LeadSource(source.lower().replace(' ', '_')),
                status=LeadStatus.NEW,
                property_interest=property_interest,
                budget_min=budget_min,
                budget_max=budget_max,
                investment_timeline=investment_timeline.lower().replace(' ', '_').replace('+', '_plus'),
                experience_level=experience_level.lower(),
                preferred_areas=preferred_areas.split(',') if preferred_areas else [],
                notes=notes
            )
            
            if scoring_system.save_lead(lead):
                st.success(f"✅ Lead '{name}' added successfully!")
                st.info(f"🎯 Lead Score: {lead.score}/100")
                st.rerun()
            else:
                st.error("❌ Failed to add lead.")
        elif submitted:
            st.warning("Please fill in the required fields (Name and Email).")

def show_all_leads(scoring_system: LeadScoringSystem):
    """Show all leads with filtering"""
    st.subheader("📋 All Leads")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", 
            ["All"] + [s.value.title() for s in LeadStatus])
    with col2:
        min_score_filter = st.slider("Minimum Score", 0, 100, 0)
    with col3:
        source_filter = st.selectbox("Source", 
            ["All"] + [s.value.replace('_', ' ').title() for s in LeadSource])
    
    # Get filtered leads
    status_filter_enum = None
    if status_filter != "All":
        status_filter_enum = LeadStatus(status_filter.lower())
    
    leads = scoring_system.get_leads(status=status_filter_enum, min_score=min_score_filter)
    
    # Apply source filter
    if source_filter != "All":
        source_enum = LeadSource(source_filter.lower().replace(' ', '_'))
        leads = [lead for lead in leads if lead.source == source_enum]
    
    # Display leads
    if leads:
        # Create DataFrame for display
        leads_data = []
        for lead in leads:
            leads_data.append({
                'Name': lead.name,
                'Email': lead.email,
                'Phone': lead.phone,
                'Score': lead.score,
                'Status': lead.status.value.title(),
                'Source': lead.source.value.replace('_', ' ').title(),
                'Budget Range': f"${lead.budget_min:,.0f} - ${lead.budget_max:,.0f}",
                'Timeline': lead.investment_timeline.replace('_', ' ').title(),
                'Experience': lead.experience_level.title(),
                'Created': lead.created_at.strftime('%m/%d/%Y')
            })
        
        df = pd.DataFrame(leads_data)
        st.dataframe(df, use_container_width=True, height=400)
        
        # Export option
        if st.button("📊 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"leads_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("📭 No leads match your filter criteria.")

def show_lead_analytics(scoring_system: LeadScoringSystem, stats: Dict[str, Any]):
    """Show lead analytics and insights"""
    st.subheader("📊 Lead Analytics")
    
    if not stats.get('score_distribution'):
        st.info("📊 No lead data available for analytics.")
        return
    
    # Score distribution chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Lead Score Distribution")
        
        score_data = stats.get('score_distribution', {})
        if score_data:
            fig_pie = px.pie(
                values=list(score_data.values()),
                names=list(score_data.keys()),
                title="Leads by Score Range"
            )
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("#### 📈 Source Performance")
        
        source_data = stats.get('source_performance', [])
        if source_data:
            sources = [row[0].replace('_', ' ').title() for row in source_data]
            scores = [row[1] for row in source_data]
            counts = [row[2] for row in source_data]
            
            fig_bar = px.bar(
                x=sources,
                y=scores,
                title="Average Score by Lead Source",
                labels={'x': 'Lead Source', 'y': 'Average Score'}
            )
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Performance insights
    st.markdown("### 🔍 Performance Insights")
    
    total_leads = sum(stats.get('score_distribution', {}).values())
    hot_leads = stats.get('score_distribution', {}).get('Hot (80-100)', 0)
    
    if total_leads > 0:
        hot_percentage = (hot_leads / total_leads) * 100
        
        if hot_percentage > 20:
            st.success(f"🔥 Excellent! {hot_percentage:.1f}% of your leads are hot leads.")
        elif hot_percentage > 10:
            st.info(f"👍 Good performance! {hot_percentage:.1f}% of your leads are hot leads.")
        else:
            st.warning(f"📈 Opportunity for improvement: Only {hot_percentage:.1f}% of your leads are hot leads.")
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    source_performance = stats.get('source_performance', [])
    
    if source_performance:
        best_source = source_performance[0][0].replace('_', ' ').title()
        st.success(f"🎯 Your best performing lead source is: **{best_source}**")
        st.info("💡 Consider investing more in your top-performing lead sources.")
        
        worst_source = source_performance[-1][0].replace('_', ' ').title()
        st.warning(f"⚠️ Consider optimizing or reducing investment in: **{worst_source}**")

def show_scoring_rules(scoring_system: LeadScoringSystem):
    """Show and manage scoring rules"""
    st.subheader("⚙️ Lead Scoring Rules")
    
    st.info("🔧 Advanced scoring rule management coming soon!")
    
    # Display current scoring criteria
    st.markdown("### 📋 Current Scoring Criteria")
    
    scoring_criteria = {
        "Investment Budget": {
            "≥ $500K": 25,
            "$250K - $500K": 15,
            "$100K - $250K": 10,
            "< $100K": 5
        },
        "Lead Source": {
            "Referral": 20,
            "Website": 15,
            "Networking": 15,
            "Social Media": 10,
            "Email Campaign": 8,
            "Advertisement": 5,
            "Cold Outreach": 3
        },
        "Experience Level": {
            "Experienced": 15,
            "Intermediate": 10,
            "Beginner": 5
        },
        "Investment Timeline": {
            "Immediately": 15,
            "6 Months": 10,
            "1 Year": 5
        },
        "Contact Completeness": {
            "Email + Phone": 10,
            "Email or Phone": 5
        },
        "Recent Activity": {
            "Last 7 days": 10,
            "Last 30 days": 5
        }
    }
    
    for category, rules in scoring_criteria.items():
        with st.expander(f"📊 {category}"):
            for criteria, points in rules.items():
                st.markdown(f"• **{criteria}**: {points} points")
    
    st.markdown("### 🎯 Total Score Interpretation")
    st.markdown("""
    - **90-100**: 🔴 **Extremely Hot** - Immediate follow-up required
    - **80-89**: 🟠 **Hot** - Priority follow-up within 24 hours  
    - **60-79**: 🟡 **Warm** - Follow-up within 3 days
    - **40-59**: 🔵 **Cold** - Nurture with email campaigns
    - **0-39**: ⚪ **Very Cold** - Long-term nurturing required
    """)