import streamlit as st

# Configure page
st.set_page_config(
    page_title="NXTRIX Enhanced CRM",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏡 NXTRIX Enhanced CRM Platform")
st.write("Testing basic functionality...")

try:
    # Test imports
    st.write("Testing imports...")
    from activity_tracker import get_activity_tracker
    st.success("✅ Activity tracker imported successfully")
    
    from deal_workflow_automation import get_workflow_manager
    st.success("✅ Deal workflow imported successfully")
    
    from email_automation import get_email_manager
    st.success("✅ Email automation imported successfully")
    
    # Test CRM Manager creation
    st.write("Testing CRM Manager...")
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    import enhanced_crm
    st.success("✅ Enhanced CRM module imported")
    
    if st.button("Test CRM Manager Creation"):
        with st.spinner("Creating CRM Manager..."):
            crm = enhanced_crm.CRMManager()
            st.success("✅ CRM Manager created successfully!")
            st.write(f"Leads: {len(crm.leads)}")
            st.write(f"Contacts: {len(crm.contacts)}")
            st.write(f"Deals: {len(crm.deals)}")
    
    if st.button("Load Enhanced CRM"):
        with st.spinner("Loading Enhanced CRM..."):
            enhanced_crm.show_enhanced_crm()
            
except Exception as e:
    st.error(f"❌ Error: {e}")
    st.exception(e)