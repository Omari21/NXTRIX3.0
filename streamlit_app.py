import streamlit as st

st.title("ðŸ¢ NXTRIX 3.0 - Investment Management Platform")
st.write("Welcome to your comprehensive investment management system!")

st.header("Quick Status")
st.success("âœ… Application is running successfully!")

if st.button("Test Button"):
    st.balloons()
    st.write("ðŸŽ‰ Everything is working!")

st.sidebar.title("Navigation")
st.sidebar.write("Your investment platform is ready to use!")
