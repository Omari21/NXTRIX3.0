import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NXTRIX Debug Test",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit UI
st.markdown("""
<style>
    .stApp > header {visibility: hidden;}
    .main > div {padding-top: 0px;}
    .block-container {padding-top: 0px; padding-bottom: 0px; max-width: 100%; margin: 0px;}
    [data-testid="stMainMenu"] {display: none !important;}
    [data-testid="stHeader"] {display: none !important;}
    button[data-testid="stBaseButton-headerNoPadding"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

# Simple test HTML
test_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NXTRIX Test</title>
    <style>
        body { 
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: white;
            margin: 0;
            padding: 20px;
            height: 100vh;
        }
        .test-container {
            text-align: center;
            padding: 50px;
        }
        .test-button {
            padding: 15px 30px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            margin: 10px;
        }
        .test-button:hover {
            background: #45a049;
        }
    </style>
</head>
<body>
    <div class="test-container">
        <h1>🏢 NXTRIX Debug Test</h1>
        <p>If you can see this, the HTML rendering works!</p>
        <button class="test-button" onclick="testFunction()">Test CTA Button</button>
        <button class="test-button" onclick="alert('Direct alert works!')">Direct Alert Test</button>
        <div id="result" style="margin-top: 20px; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 8px;">
            Click buttons to test functionality...
        </div>
    </div>
    
    <script>
        console.log('🔍 Debug script loaded');
        
        function testFunction() {
            console.log('✅ Test function called');
            document.getElementById('result').innerHTML = '✅ Test function works! JavaScript is functional.';
            alert('✅ CTA button test successful!');
        }
        
        // Test if script runs immediately
        document.getElementById('result').innerHTML = '🚀 JavaScript loaded successfully! Ready for testing.';
        
        console.log('✅ Debug test ready');
    </script>
</body>
</html>
"""

st.write("## Debug Test")
st.write("Testing if Streamlit components.html works properly...")

# Render the test
components.html(test_html, height=600, scrolling=False)

st.write("**If you see content above, HTML rendering works. If buttons don't work, it's a JavaScript issue.**")