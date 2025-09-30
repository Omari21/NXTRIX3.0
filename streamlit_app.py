import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import os
from supabase import create_client, Client
import uuid
from dataclasses import dataclass, asdict
import time
from dotenv import load_dotenv
import bcrypt
import hashlib

# AI Features
try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configuration
st.set_page_config(
    page_title="NXTRIX CRM",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Supabase
@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        if not url or not key:
            st.error("Missing Supabase configuration in environment variables")
            return None
        return create_client(url, key)
    except Exception as e:
        st.error(f"Failed to initialize Supabase: {e}")
        return None

supabase = init_supabase()

# Data Models
@dataclass
class Deal:
    id: str
    property_address: str
    deal_type: str
    property_value: float
    investor_name: str
    status: str
    created_at: str
    contact_info: str = ""
    notes: str = ""

# Authentication Functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except:
        return False

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user against Supabase"""
    if not supabase:
        return False
    
    try:
        response = supabase.table('users').select('*').eq('username', username).execute()
        if response.data and len(response.data) > 0:
            user = response.data[0]
            return verify_password(password, user['password_hash'])
        return False
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False

def register_user(username: str, password: str, email: str) -> bool:
    """Register new user"""
    if not supabase:
        return False
    
    try:
        password_hash = hash_password(password)
        user_data = {
            'id': str(uuid.uuid4()),
            'username': username,
            'password_hash': password_hash,
            'email': email,
            'created_at': datetime.now().isoformat()
        }
        
        response = supabase.table('users').insert(user_data).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Registration error: {e}")
        return False

# AI Functions
def analyze_deal_with_ai(deal: Deal) -> Dict[str, Any]:
    """Analyze deal using OpenAI"""
    if not AI_AVAILABLE or not openai.api_key:
        return {"score": 75, "analysis": "AI analysis not available", "recommendations": ["Manual review recommended"]}
    
    try:
        prompt = f"""
        Analyze this real estate deal:
        
        Property: {deal.property_address}
        Type: {deal.deal_type}
        Value: ${deal.property_value:,.2f}
        Investor: {deal.investor_name}
        Status: {deal.status}
        Notes: {deal.notes}
        
        Please provide:
        1. Deal score (1-100)
        2. Analysis summary
        3. 3 key recommendations
        
        Respond in JSON format: {{"score": number, "analysis": "text", "recommendations": ["rec1", "rec2", "rec3"]}}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        return {"score": 75, "analysis": f"AI analysis error: {str(e)}", "recommendations": ["Manual review recommended"]}

def generate_market_insights() -> List[str]:
    """Generate AI-powered market insights"""
    if not AI_AVAILABLE:
        return ["AI insights not available - upgrade to enable AI features"]
    
    try:
        prompt = """
        Generate 5 current real estate market insights for investors in 2025.
        Focus on trends, opportunities, and risks.
        Keep each insight to 1-2 sentences.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        
        insights = response.choices[0].message.content.strip().split('\n')
        return [insight.strip('- ').strip() for insight in insights if insight.strip()]
        
    except Exception as e:
        return [f"AI insights error: {str(e)}"]

# Database Functions
def get_deals() -> List[Deal]:
    """Fetch all deals from database"""
    if not supabase:
        return []
    
    try:
        response = supabase.table('deals').select('*').order('created_at', desc=True).execute()
        return [Deal(**deal) for deal in response.data]
    except Exception as e:
        st.error(f"Error fetching deals: {e}")
        return []

def add_deal(deal: Deal) -> bool:
    """Add new deal to database"""
    if not supabase:
        return False
    
    try:
        deal_data = asdict(deal)
        response = supabase.table('deals').insert(deal_data).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Error adding deal: {e}")
        return False

def update_deal(deal: Deal) -> bool:
    """Update existing deal"""
    if not supabase:
        return False
    
    try:
        deal_data = asdict(deal)
        response = supabase.table('deals').update(deal_data).eq('id', deal.id).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Error updating deal: {e}")
        return False

def delete_deal(deal_id: str) -> bool:
    """Delete deal from database"""
    if not supabase:
        return False
    
    try:
        response = supabase.table('deals').delete().eq('id', deal_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting deal: {e}")
        return False

# Dashboard Functions
def show_dashboard():
    """Display main dashboard"""
    st.title("🏢 NXTRIX CRM Dashboard")
    
    # Get deals data
    deals = get_deals()
    
    if not deals:
        st.info("No deals found. Add your first deal to get started!")
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame([asdict(deal) for deal in deals])
    df['property_value'] = pd.to_numeric(df['property_value'], errors='coerce')
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Deals", len(deals))
    
    with col2:
        total_value = df['property_value'].sum()
        st.metric("Total Portfolio Value", f"${total_value:,.0f}")
    
    with col3:
        active_deals = len(df[df['status'] == 'Active'])
        st.metric("Active Deals", active_deals)
    
    with col4:
        avg_value = df['property_value'].mean()
        st.metric("Avg Deal Value", f"${avg_value:,.0f}")
    
    # AI Insights Section
    if AI_AVAILABLE:
        st.subheader("🤖 AI Market Insights")
        with st.expander("View AI-Powered Market Analysis"):
            insights = generate_market_insights()
            for i, insight in enumerate(insights[:5], 1):
                st.write(f"**{i}.** {insight}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Deals by Status")
        status_counts = df['status'].value_counts()
        fig_status = px.pie(values=status_counts.values, names=status_counts.index)
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        st.subheader("Deals by Type")
        type_counts = df['deal_type'].value_counts()
        fig_type = px.bar(x=type_counts.index, y=type_counts.values)
        fig_type.update_layout(xaxis_title="Deal Type", yaxis_title="Count")
        st.plotly_chart(fig_type, use_container_width=True)
    
    # Recent deals
    st.subheader("Recent Deals")
    recent_deals = df.head(10)
    st.dataframe(recent_deals[['property_address', 'deal_type', 'property_value', 'investor_name', 'status']], use_container_width=True)

def show_deals():
    """Display deals management page"""
    st.title("💼 Deal Management")
    
    tab1, tab2 = st.tabs(["View Deals", "Add New Deal"])
    
    with tab1:
        st.subheader("All Deals")
        deals = get_deals()
        
        if deals:
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox("Filter by Status", 
                                           ["All"] + list(set([deal.status for deal in deals])))
            
            with col2:
                type_filter = st.selectbox("Filter by Type", 
                                         ["All"] + list(set([deal.deal_type for deal in deals])))
            
            with col3:
                search_term = st.text_input("Search Address")
            
            # Filter deals
            filtered_deals = deals
            if status_filter != "All":
                filtered_deals = [d for d in filtered_deals if d.status == status_filter]
            if type_filter != "All":
                filtered_deals = [d for d in filtered_deals if d.deal_type == type_filter]
            if search_term:
                filtered_deals = [d for d in filtered_deals if search_term.lower() in d.property_address.lower()]
            
            # Display deals
            for deal in filtered_deals:
                with st.expander(f"{deal.property_address} - ${deal.property_value:,.0f}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Type:** {deal.deal_type}")
                        st.write(f"**Investor:** {deal.investor_name}")
                        st.write(f"**Status:** {deal.status}")
                    
                    with col2:
                        st.write(f"**Value:** ${deal.property_value:,.0f}")
                        st.write(f"**Contact:** {deal.contact_info}")
                        st.write(f"**Created:** {deal.created_at}")
                    
                    if deal.notes:
                        st.write(f"**Notes:** {deal.notes}")
                    
                    # AI Analysis Section
                    if AI_AVAILABLE:
                        if st.button(f"🤖 AI Analysis {deal.id[:8]}", key=f"ai_{deal.id}"):
                            with st.spinner("Analyzing deal with AI..."):
                                ai_result = analyze_deal_with_ai(deal)
                                st.success(f"**AI Score:** {ai_result['score']}/100")
                                st.write(f"**Analysis:** {ai_result['analysis']}")
                                st.write("**Recommendations:**")
                                for rec in ai_result['recommendations']:
                                    st.write(f"• {rec}")
                    
                    # Action buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Edit {deal.id[:8]}", key=f"edit_{deal.id}"):
                            st.session_state.edit_deal = deal
                    with col2:
                        if st.button(f"Delete {deal.id[:8]}", key=f"delete_{deal.id}"):
                            if delete_deal(deal.id):
                                st.success("Deal deleted successfully!")
                                st.rerun()
        else:
            st.info("No deals found. Add your first deal!")
    
    with tab2:
        st.subheader("Add New Deal")
        
        with st.form("add_deal_form"):
            property_address = st.text_input("Property Address*")
            deal_type = st.selectbox("Deal Type*", 
                                   ["Fix & Flip", "Buy & Hold", "Wholesale", "Commercial", "Land"])
            property_value = st.number_input("Property Value*", min_value=0.0, step=1000.0)
            investor_name = st.text_input("Investor Name*")
            contact_info = st.text_input("Contact Information")
            status = st.selectbox("Status*", ["Active", "Pending", "Closed", "Cancelled"])
            notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("Add Deal")
            
            if submitted:
                if property_address and deal_type and property_value and investor_name and status:
                    new_deal = Deal(
                        id=str(uuid.uuid4()),
                        property_address=property_address,
                        deal_type=deal_type,
                        property_value=property_value,
                        investor_name=investor_name,
                        contact_info=contact_info,
                        status=status,
                        notes=notes,
                        created_at=datetime.now().isoformat()
                    )
                    
                    if add_deal(new_deal):
                        st.success("Deal added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add deal. Please try again.")
                else:
                    st.error("Please fill in all required fields marked with *")

def show_investors():
    """Display investor management page"""
    st.title("👥 Investor Management")
    
    deals = get_deals()
    if not deals:
        st.info("No deals found. Add deals to see investor information.")
        return
    
    # Create investor summary
    df = pd.DataFrame([asdict(deal) for deal in deals])
    investor_summary = df.groupby('investor_name').agg({
        'property_value': ['sum', 'count', 'mean'],
        'status': lambda x: list(x)
    }).reset_index()
    
    investor_summary.columns = ['Investor', 'Total_Value', 'Deal_Count', 'Avg_Value', 'Statuses']
    
    st.subheader("Investor Overview")
    
    for _, investor in investor_summary.iterrows():
        with st.expander(f"{investor['Investor']} - {investor['Deal_Count']} deals"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Investment", f"${investor['Total_Value']:,.0f}")
                st.metric("Number of Deals", investor['Deal_Count'])
            
            with col2:
                st.metric("Average Deal Size", f"${investor['Avg_Value']:,.0f}")
                status_counts = pd.Series(investor['Statuses']).value_counts()
                for status, count in status_counts.items():
                    st.write(f"**{status}:** {count}")

def login_page():
    """Display login page"""
    st.title("🔐 Login to NXTRIX CRM")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if authenticate_user(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Choose Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif not new_username or not new_email:
                    st.error("Please fill in all fields")
                else:
                    if register_user(new_username, new_password, new_email):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Registration failed. Username might already exist.")

def show_ai_analytics():
    """Display AI-powered analytics page"""
    st.title("🤖 AI-Powered Analytics")
    
    if not AI_AVAILABLE:
        st.warning("AI features require OpenAI API key. Please configure your environment variables.")
        return
    
    deals = get_deals()
    if not deals:
        st.info("No deals available for AI analysis. Add some deals first!")
        return
    
    st.subheader("📊 Portfolio AI Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Market Insights**")
        insights = generate_market_insights()
        for insight in insights[:3]:
            st.success(insight)
    
    with col2:
        st.write("**Deal Recommendations**")
        # Analyze a few recent deals
        recent_deals = deals[:3]
        for deal in recent_deals:
            with st.expander(f"Analysis: {deal.property_address}"):
                ai_result = analyze_deal_with_ai(deal)
                st.write(f"**Score:** {ai_result['score']}/100")
                st.write(f"**Analysis:** {ai_result['analysis']}")
    
    st.subheader("🎯 AI Investment Recommendations")
    st.info("Based on your current portfolio, here are AI-generated investment strategies:")
    
    # Generate portfolio recommendations
    try:
        portfolio_prompt = f"""
        Based on a real estate portfolio of {len(deals)} deals with these property types: {', '.join(set([d.deal_type for d in deals]))},
        provide 3 strategic investment recommendations for 2025.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": portfolio_prompt}],
            max_tokens=300
        )
        
        recommendations = response.choices[0].message.content.strip().split('\n')
        for i, rec in enumerate(recommendations[:3], 1):
            if rec.strip():
                st.write(f"**{i}.** {rec.strip('- ').strip()}")
                
    except Exception as e:
        st.error(f"AI recommendation error: {str(e)}")

# Main App
def main():
    """Main application"""
    
    # Check authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Sidebar navigation
    st.sidebar.title(f"Welcome, {st.session_state.get('username', 'User')}")
    
    page = st.sidebar.selectbox("Navigate", 
                               ["Dashboard", "Deals", "Investors", "AI Analytics", "Settings"])
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    # AI Status
    if AI_AVAILABLE:
        st.sidebar.success("🤖 AI Features: Enabled")
    else:
        st.sidebar.warning("🤖 AI Features: Disabled")
    
    # Display selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Deals":
        show_deals()
    elif page == "Investors":
        show_investors()
    elif page == "AI Analytics":
        show_ai_analytics()
    elif page == "Settings":
        st.title("⚙️ Settings")
        st.info("Settings page coming soon!")

if __name__ == "__main__":
    main()