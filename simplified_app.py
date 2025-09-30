import streamlit as st
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the CRM functions
try:
    from enhanced_crm import show_enhanced_crm, CRMManager
    ENHANCED_CRM_AVAILABLE = True
except ImportError as e:
    st.error(f"Could not import enhanced_crm: {e}")
    ENHANCED_CRM_AVAILABLE = False

def main():
    st.set_page_config(
        page_title="NXTRIX 3.0 - Investment Platform",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏢 NXTRIX 3.0 - Investment Management Platform")
    
    if not ENHANCED_CRM_AVAILABLE:
        st.error("Enhanced CRM module is not available. Please check the installation.")
        st.stop()
    
    st.sidebar.title("🧭 Navigation")
    
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Dashboard", "📊 Enhanced CRM", "💼 Deal Management", "🎯 Buyer Management"]
    )
    
    if page == "🏠 Dashboard":
        st.header("Welcome to Your Investment Management Platform")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Deals", "Loading...", "📈")
            
        with col2:
            st.metric("Total Buyers", "Loading...", "👥")
            
        with col3:
            st.metric("ROI Average", "Loading...", "💰")
            
        st.success("✅ Platform is operational!")
        
        if st.button("🚀 Launch Full CRM"):
            st.session_state.page = "📊 Enhanced CRM"
            st.rerun()
    
    elif page == "📊 Enhanced CRM":
        try:
            show_enhanced_crm()
        except Exception as e:
            st.error(f"Error loading Enhanced CRM: {e}")
            st.write("Please check the application logs for more details.")
    
    else:
        st.info(f"Page '{page}' is under development. Full functionality available in Enhanced CRM.")
        
        if st.button("Go to Enhanced CRM"):
            st.session_state.page = "📊 Enhanced CRM"
            st.rerun()

if __name__ == "__main__":
    main()