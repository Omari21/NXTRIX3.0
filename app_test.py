import streamlit as st

st.set_page_config(
    page_title="NXTRIX Platform - Test",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 NXTRIX Platform - Deployment Test")
st.success("✅ If you can see this, your Streamlit Cloud deployment is working!")
st.info("This is a test file to verify deployment. The main app is in streamlit_app.py")

st.markdown("---")
st.markdown("### 🔧 Next Steps:")
st.markdown("1. This test confirms your repository is accessible")
st.markdown("2. Switch the main file path to `streamlit_app.py` for the full platform")
st.markdown("3. Add your secrets configuration")

st.markdown("---")
st.markdown("### 📊 Repository Info:")
st.write("- **Repository**: Omari21/NXTRIX3.0")
st.write("- **Branch**: main")
st.write("- **Test File**: app_test.py")
st.write("- **Production File**: streamlit_app.py")