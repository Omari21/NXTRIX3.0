import streamlit as st
import sys
import os
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="NXTRIX Enhanced CRM",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid #667eea;
}
.activity-item {
    background: #f8f9fa;
    padding: 0.5rem;
    border-radius: 5px;
    margin: 0.5rem 0;
    border-left: 3px solid #28a745;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    padding-left: 20px;
    padding-right: 20px;
}
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🤝 NXTRIX Enhanced CRM with Activity Tracking</h1>
    <p>Complete Real Estate Investment CRM & Opportunity Management</p>
</div>
""", unsafe_allow_html=True)

# Lazy loading function for CRM components
@st.cache_resource
def load_crm_manager():
    """Load CRM Manager with error handling"""
    try:
        from enhanced_crm import CRMManager
        return CRMManager()
    except Exception as e:
        st.error(f"Error loading CRM Manager: {e}")
        return None

@st.cache_resource  
def load_activity_tracker():
    """Load Activity Tracker with error handling"""
    try:
        from activity_tracker import get_activity_tracker
        return get_activity_tracker()
    except Exception as e:
        st.error(f"Error loading Activity Tracker: {e}")
        return None

def show_crm_dashboard():
    """Show main CRM dashboard"""
    crm = load_crm_manager()
    activity_tracker = load_activity_tracker()
    
    if not crm:
        st.error("❌ CRM Manager failed to load")
        return
        
    if not activity_tracker:
        st.error("❌ Activity Tracker failed to load")
        return
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total Leads", len(crm.leads))
    
    with col2:
        st.metric("💼 Active Deals", len([d for d in crm.deals if d.stage != "Closed"]))
    
    with col3:
        st.metric("👥 Contacts", len(crm.contacts))
    
    with col4:
        # Get recent activities count
        recent_activities = activity_tracker.get_recent_activities(days_back=7)
        st.metric("🎯 Week Activities", len(recent_activities))
    
    # Show recent activities
    st.subheader("📋 Recent Activities")
    recent_activities = activity_tracker.get_recent_activities(days_back=3)
    
    if recent_activities:
        for activity in recent_activities[:5]:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{activity.activity_type.value}** - {activity.title}")
                    st.markdown(f"_{activity.description}_")
                with col2:
                    st.markdown(f"📅 {activity.created_at.strftime('%m/%d %H:%M')}")
    else:
        st.info("No recent activities. Start by adding leads or deals!")

def show_leads_management():
    """Show leads management interface"""
    crm = load_crm_manager()
    if not crm:
        return
        
    st.subheader("👥 Lead Management")
    
    # Add new lead form
    with st.expander("➕ Add New Lead"):
        with st.form("add_lead"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Lead Name")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
            with col2:
                property_address = st.text_input("Property Address")
                budget = st.number_input("Budget ($)", min_value=0, value=100000)
                
            if st.form_submit_button("Add Lead"):
                try:
                    from enhanced_crm import Lead, LeadStatus, LeadType, LeadSource
                    lead = Lead(
                        name=name,
                        email=email,
                        phone=phone,
                        status=LeadStatus.NEW,
                        lead_type=LeadType.BUYER,
                        lead_source=LeadSource.WEBSITE,
                        property_address=property_address,
                        budget=budget
                    )
                    crm.add_lead(lead)
                    st.success(f"✅ Lead {name} added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding lead: {e}")
    
    # Display existing leads
    if crm.leads:
        st.markdown("### Current Leads")
        for lead in crm.leads[-10:]:  # Show last 10 leads
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{lead.name}**")
                    st.markdown(f"📧 {lead.email} | 📞 {lead.phone}")
                with col2:
                    st.markdown(f"Status: {lead.status.value}")
                    st.markdown(f"Score: {lead.score}")
                with col3:
                    st.markdown(f"Budget: ${lead.budget:,}")
                st.markdown("---")
    else:
        st.info("No leads yet. Add your first lead above!")

def show_deals_management():
    """Show deals management interface"""
    crm = load_crm_manager()
    if not crm:
        return
        
    st.subheader("💼 Deal Management")
    
    # Add new deal form
    with st.expander("➕ Add New Deal"):
        with st.form("add_deal"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Deal Title")
                property_address = st.text_input("Property Address")
                purchase_price = st.number_input("Purchase Price ($)", min_value=0, value=200000)
            with col2:
                arv = st.number_input("ARV ($)", min_value=0, value=250000)
                rehab_cost = st.number_input("Rehab Cost ($)", min_value=0, value=25000)
                
            if st.form_submit_button("Add Deal"):
                try:
                    from enhanced_crm import Deal, DealStage
                    deal = Deal(
                        title=title,
                        property_address=property_address,
                        purchase_price=purchase_price,
                        arv=arv,
                        rehab_cost=rehab_cost,
                        stage=DealStage.LEAD
                    )
                    crm.add_deal(deal)
                    st.success(f"✅ Deal {title} added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding deal: {e}")
    
    # Display existing deals
    if crm.deals:
        st.markdown("### Current Deals")
        for deal in crm.deals[-10:]:  # Show last 10 deals
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{deal.title}**")
                    st.markdown(f"📍 {deal.property_address}")
                with col2:
                    st.markdown(f"Stage: {deal.stage.value}")
                    st.markdown(f"ROI: {deal.estimated_roi:.1f}%")
                with col3:
                    st.markdown(f"Price: ${deal.purchase_price:,}")
                    st.markdown(f"ARV: ${deal.arv:,}")
                st.markdown("---")
    else:
        st.info("No deals yet. Add your first deal above!")

def show_activity_tracking():
    """Show activity tracking interface"""
    activity_tracker = load_activity_tracker()
    if not activity_tracker:
        return
        
    st.subheader("🎯 Activity Tracking & Opportunities")
    
    tab1, tab2, tab3 = st.tabs(["📋 Recent Activities", "🚨 Opportunities", "📊 Analytics"])
    
    with tab1:
        st.markdown("### Recent Activities")
        days_back = st.slider("Days to show", 1, 30, 7)
        activities = activity_tracker.get_recent_activities(days_back=days_back)
        
        if activities:
            for activity in activities[:20]:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        priority_colors = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "URGENT": "🔴"}
                        priority_icon = priority_colors.get(activity.priority.value, "⚪")
                        st.markdown(f"{priority_icon} **{activity.activity_type.value}** - {activity.title}")
                        st.markdown(f"_{activity.description}_")
                    with col2:
                        st.markdown(f"📅 {activity.created_at.strftime('%m/%d %H:%M')}")
                    st.markdown("---")
        else:
            st.info("No activities found.")
    
    with tab2:
        st.markdown("### Active Opportunities")
        opportunities = activity_tracker.get_active_opportunities()
        
        if opportunities:
            for opp in opportunities:
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"### 🎯 {opp.title}")
                        st.markdown(f"{opp.description}")
                    with col2:
                        priority_colors = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "URGENT": "🔴"}
                        priority_icon = priority_colors.get(opp.priority.value, "⚪")
                        st.markdown(f"**Priority:** {priority_icon} {opp.priority.value}")
                    with col3:
                        st.markdown(f"**Value:** ${opp.estimated_value:,.2f}")
                        if st.button(f"✅ Complete", key=f"complete_{opp.id}"):
                            activity_tracker.mark_opportunity_completed(opp.id)
                            st.success("Opportunity completed!")
                            st.rerun()
                    st.markdown("---")
        else:
            st.success("🎉 No active opportunities. You're all caught up!")
    
    with tab3:
        st.markdown("### Activity Analytics")
        analytics = activity_tracker.get_activity_analytics(days_back=30)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Activities", analytics.get('total_activities', 0))
        with col2:
            st.metric("Opportunities Created", analytics.get('opportunities_created', 0))
        with col3:
            completion_rate = analytics.get('opportunity_completion_rate', 0)
            st.metric("Completion Rate", f"{completion_rate:.1f}%")

# Main navigation
st.sidebar.title("🎯 CRM Navigation")

# Simple navigation without complex dependencies
nav_options = [
    "📊 Dashboard",
    "👥 Lead Management", 
    "💼 Deal Management",
    "🎯 Activity Tracking"
]

selected_page = st.sidebar.selectbox("Choose Section", nav_options)

# Show connection status
st.sidebar.markdown("---")
try:
    crm = load_crm_manager()
    if crm:
        st.sidebar.success("🟢 CRM Connected")
        st.sidebar.info(f"📋 {len(crm.leads)} leads")
        st.sidebar.info(f"💼 {len(crm.deals)} deals")
    else:
        st.sidebar.error("🔴 CRM Offline")
except Exception as e:
    st.sidebar.error("🔴 CRM Error")

# Route to selected page
if selected_page == "📊 Dashboard":
    show_crm_dashboard()
elif selected_page == "👥 Lead Management":
    show_leads_management()
elif selected_page == "💼 Deal Management":
    show_deals_management()
elif selected_page == "🎯 Activity Tracking":
    show_activity_tracking()

# Footer
st.markdown("---")
st.markdown("**NXTRIX Enhanced CRM** - Complete Real Estate Investment Management Platform")