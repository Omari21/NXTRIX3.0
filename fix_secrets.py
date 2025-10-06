#!/usr/bin/env python3
"""
Fix OpenAI and Supabase configuration with proper error handling
"""

def fix_secrets_config():
    # Read the file
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix OpenAI configuration
    old_openai = 'openai.api_key = st.secrets["OPENAI"]["OPENAI_API_KEY"]'
    new_openai = '''# Initialize OpenAI with error handling
try:
    openai.api_key = st.secrets["OPENAI"]["OPENAI_API_KEY"]
    OPENAI_AVAILABLE = True
except KeyError:
    st.warning("⚠️ OpenAI API key not configured. AI features will have limited functionality.")
    OPENAI_AVAILABLE = False
except Exception as e:
    st.error(f"OpenAI configuration error: {e}")
    OPENAI_AVAILABLE = False'''
    
    if old_openai in content:
        content = content.replace(old_openai, new_openai)
        print("✅ Fixed OpenAI configuration")
    else:
        print("❌ OpenAI configuration not found")
    
    # Fix Supabase configuration
    old_supabase = '''@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE"]["SUPABASE_URL"]
    key = st.secrets["SUPABASE"]["SUPABASE_KEY"]
    return create_client(url, key)'''
    
    new_supabase = '''@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["SUPABASE"]["SUPABASE_URL"]
        key = st.secrets["SUPABASE"]["SUPABASE_KEY"]
        return create_client(url, key)
    except KeyError:
        st.warning("⚠️ Supabase credentials not configured. Using demo mode.")
        return None
    except Exception as e:
        st.error(f"Supabase initialization failed: {e}")
        return None'''
    
    if old_supabase in content:
        content = content.replace(old_supabase, new_supabase)
        print("✅ Fixed Supabase configuration")
    else:
        print("❌ Supabase configuration not found")
    
    # Write back
    with open('streamlit_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Secrets configuration updated with error handling")

if __name__ == "__main__":
    fix_secrets_config()