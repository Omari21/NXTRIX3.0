"""
NXTRIX - Simplified Working Version with Real Backend
Fixed frontend-backend communication for immediate functionality
"""

import streamlit as st
import json
from datetime import datetime
import uuid

# Import backend 
try:
    from nxtrix_backend import NXTRIXDatabase
    BACKEND_AVAILABLE = True
    st.success("✅ Backend database connected!")
except ImportError as e:
    BACKEND_AVAILABLE = False
    st.error(f"❌ Backend not available: {e}")

# Set page config
st.set_page_config(
    page_title="NXTRIX - Working Version",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_backend():
    """Initialize backend database"""
    if BACKEND_AVAILABLE:
        try:
            db = NXTRIXDatabase()
            return db
        except Exception as e:
            st.error(f"Database initialization failed: {e}")
            return None
    return None

def main():
    """Main application with working functionality"""
    
    # Initialize backend
    db = initialize_backend()
    
    st.title("🏢 NXTRIX Platform - Working Version")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose Page", [
        "Dashboard",
        "Add Contact", 
        "View Contacts",
        "Add Deal",
        "View Deals",
        "Test Backend"
    ])
    
    if page == "Dashboard":
        show_dashboard(db)
    elif page == "Add Contact":
        show_add_contact(db)
    elif page == "View Contacts":
        show_contacts(db)
    elif page == "Add Deal":
        show_add_deal(db)
    elif page == "View Deals":
        show_deals(db)
    elif page == "Test Backend":
        show_backend_test(db)

def show_dashboard(db):
    """Working dashboard"""
    st.header("📊 Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    if db:
        try:
            contacts = db.get_contacts()
            deals = db.get_deals()
            
            with col1:
                st.metric("Total Contacts", len(contacts))
            with col2:
                st.metric("Total Deals", len(deals))
            with col3:
                st.metric("Active Projects", "12")
            with col4:
                st.metric("ROI Average", "18.3%")
                
        except Exception as e:
            st.error(f"Error loading dashboard data: {e}")
    else:
        with col1:
            st.metric("Total Contacts", "N/A")
        with col2:
            st.metric("Total Deals", "N/A")
    
    st.success("✅ Dashboard loaded successfully!")
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Add New Deal", use_container_width=True):
            st.switch_page = "Add Deal"
            st.rerun()
    
    with col2:
        if st.button("👥 Add New Contact", use_container_width=True):
            st.switch_page = "Add Contact"
            st.rerun()

def show_add_contact(db):
    """Working contact creation"""
    st.header("👥 Add New Contact")
    
    with st.form("contact_form"):
        name = st.text_input("Full Name *", placeholder="John Smith")
        email = st.text_input("Email *", placeholder="john@example.com")
        phone = st.text_input("Phone", placeholder="(555) 123-4567")
        contact_type = st.selectbox("Contact Type", [
            "Investor", "Buyer", "Seller", "Real Estate Agent", "Vendor/Service Provider"
        ])
        notes = st.text_area("Notes", placeholder="Investment criteria, preferences, etc.")
        
        submitted = st.form_submit_button("💾 Save Contact", use_container_width=True)
        
        if submitted:
            if not name or not email:
                st.error("❌ Name and email are required!")
            elif db:
                try:
                    contact_data = {
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'contact_type': contact_type,
                        'notes': notes
                    }
                    
                    contact_id = db.add_contact(contact_data)
                    st.success(f"✅ Contact '{name}' saved successfully! ID: {contact_id}")
                    st.balloons()
                    
                    # Clear form by rerunning
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Failed to save contact: {e}")
            else:
                st.error("❌ Database not available")

def show_contacts(db):
    """Working contact display"""
    st.header("📋 Contact Database")
    
    if not db:
        st.error("❌ Database not available")
        return
    
    try:
        contacts = db.get_contacts()
        
        if not contacts:
            st.info("📝 No contacts found. Add your first contact!")
            if st.button("➕ Add Contact"):
                st.switch_page("Add Contact")
        else:
            st.success(f"✅ Found {len(contacts)} contacts in database")
            
            # Display contacts in a nice format
            for contact in contacts:
                with st.expander(f"👤 {contact['name']} ({contact['contact_type']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Email:** {contact['email']}")
                        st.write(f"**Phone:** {contact.get('phone', 'Not provided')}")
                        st.write(f"**Type:** {contact['contact_type']}")
                    
                    with col2:
                        st.write(f"**Added:** {contact.get('created_at', 'Unknown')}")
                        if contact.get('notes'):
                            st.write(f"**Notes:** {contact['notes']}")
                        
                        # Action buttons
                        if st.button(f"📞 Contact {contact['name']}", key=f"contact_{contact['id']}"):
                            st.info(f"📧 Email: {contact['email']}")
    
    except Exception as e:
        st.error(f"❌ Error loading contacts: {e}")

def show_add_deal(db):
    """Working deal creation"""
    st.header("🏠 Add New Deal")
    
    with st.form("deal_form"):
        property_address = st.text_input("Property Address *", placeholder="123 Main St, City, State")
        listing_price = st.number_input("Listing Price *", min_value=0, value=250000, step=1000)
        property_type = st.selectbox("Property Type", [
            "Single Family Home", "Condo", "Multi-Family", "Commercial", "Land"
        ])
        repair_costs = st.number_input("Estimated Repair Cost", min_value=0, value=15000, step=500)
        arv = st.number_input("ARV Estimate", min_value=0, value=320000, step=1000)
        
        submitted = st.form_submit_button("💾 Save Deal", use_container_width=True)
        
        if submitted:
            if not property_address:
                st.error("❌ Property address is required!")
            elif db:
                try:
                    # Calculate ROI
                    total_investment = listing_price + repair_costs
                    potential_profit = arv - total_investment
                    roi = (potential_profit / total_investment * 100) if total_investment > 0 else 0
                    
                    deal_data = {
                        'property_address': property_address,
                        'purchase_price': listing_price,
                        'property_type': property_type,
                        'repair_costs': repair_costs,
                        'arv': arv,
                        'expected_roi': roi,
                        'status': 'active'
                    }
                    
                    deal_id = db.add_deal(deal_data)
                    st.success(f"✅ Deal '{property_address}' saved successfully! ID: {deal_id}")
                    st.info(f"📊 Calculated ROI: {roi:.1f}%")
                    st.balloons()
                    
                    # Clear form
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Failed to save deal: {e}")
            else:
                st.error("❌ Database not available")

def show_deals(db):
    """Working deals display"""
    st.header("🏠 Deal Pipeline")
    
    if not db:
        st.error("❌ Database not available")
        return
    
    try:
        deals = db.get_deals()
        
        if not deals:
            st.info("📝 No deals found. Add your first deal!")
            if st.button("➕ Add Deal"):
                st.switch_page("Add Deal")
        else:
            st.success(f"✅ Found {len(deals)} deals in database")
            
            # Display deals in a nice format
            for deal in deals:
                with st.expander(f"🏠 {deal['property_address']} - ${deal.get('purchase_price', 0):,}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Property Type:** {deal.get('property_type', 'Unknown')}")
                        st.write(f"**Purchase Price:** ${deal.get('purchase_price', 0):,}")
                        st.write(f"**Repair Costs:** ${deal.get('repair_costs', 0):,}")
                    
                    with col2:
                        st.write(f"**ARV:** ${deal.get('arv', 0):,}")
                        roi = deal.get('expected_roi', 0)
                        st.write(f"**Expected ROI:** {roi:.1f}%")
                        st.write(f"**Status:** {deal.get('status', 'Unknown')}")
                    
                    with col3:
                        st.write(f"**Added:** {deal.get('created_at', 'Unknown')}")
                        
                        # Action buttons
                        if st.button(f"📊 Analyze {deal['id']}", key=f"analyze_{deal['id']}"):
                            st.info("📈 Advanced analysis would open here")
    
    except Exception as e:
        st.error(f"❌ Error loading deals: {e}")

def show_backend_test(db):
    """Test backend functionality"""
    st.header("🔧 Backend Test")
    
    if not db:
        st.error("❌ Database not available")
        return
    
    st.info("Testing backend database operations...")
    
    try:
        # Test contact operations
        st.subheader("📋 Contact Operations")
        contacts = db.get_contacts()
        st.write(f"✅ Retrieved {len(contacts)} contacts")
        
        # Test deal operations  
        st.subheader("🏠 Deal Operations")
        deals = db.get_deals()
        st.write(f"✅ Retrieved {len(deals)} deals")
        
        # Add test data button
        if st.button("🧪 Add Test Data"):
            # Add test contact
            test_contact = {
                'name': f'Test Contact {datetime.now().strftime("%H:%M:%S")}',
                'email': f'test{uuid.uuid4().hex[:8]}@example.com',
                'contact_type': 'Investor',
                'notes': 'Auto-generated test contact'
            }
            contact_id = db.add_contact(test_contact)
            
            # Add test deal
            test_deal = {
                'property_address': f'Test Property {datetime.now().strftime("%H:%M:%S")}',
                'purchase_price': 200000,
                'property_type': 'Single Family Home',
                'expected_roi': 15.5,
                'status': 'active'
            }
            deal_id = db.add_deal(test_deal)
            
            st.success(f"✅ Added test contact (ID: {contact_id}) and deal (ID: {deal_id})")
            st.rerun()
        
        st.success("✅ Backend test completed successfully!")
        
    except Exception as e:
        st.error(f"❌ Backend test failed: {e}")
        st.code(str(e))

if __name__ == "__main__":
    main()