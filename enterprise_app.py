"""
NXTRIX Platform - Enterprise CRM Application
Modern SaaS interface inspired by Salesforce, Monday.com, and HubSpot
"""

import streamlit as st
from enterprise_interface import create_enterprise_app

# Configure Streamlit page
st.set_page_config(
    page_title="NXTRIX - Enterprise CRM Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar completely
)

def main():
    """Main application entry point"""
    
    # Hide all Streamlit UI elements
    st.markdown("""
    <style>
    /* Hide Streamlit interface completely */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    .stDecoration {display: none;}
    .stToolbar {display: none;}
    
    /* Remove all padding and margins */
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: none !important;
    }
    
    .main {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Full viewport */
    html, body, [data-testid="stAppViewContainer"] {
        height: 100vh !important;
        width: 100vw !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: hidden !important;
    }
    
    [data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Load the enterprise interface
    create_enterprise_app()

if __name__ == "__main__":
    main()