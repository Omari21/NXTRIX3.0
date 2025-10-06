
# === AUTHENTICATION SYSTEM ===

def show_authentication_ui():
    """Show login/registration interface"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🏢 NXTRIX Enterprise CRM</h1>
        <h3>Secure Access Portal</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Register", "👀 Demo Access"])
        
        with tab1:
            st.subheader("Login to Your Account")
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="your@email.com")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                remember_me = st.checkbox("Remember me")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    login_btn = st.form_submit_button("🔑 Login", type="primary", use_container_width=True)
                with col_b:
                    forgot_btn = st.form_submit_button("❓ Forgot Password", use_container_width=True)
                
                if login_btn and email and password:
                    # Authenticate user
                    if authenticate_user(email, password):
                        st.session_state.user_authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_tier = get_user_tier(email)
                        st.session_state.is_admin = check_admin_status(email)
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
                        
                if forgot_btn:
                    st.info("📧 Password reset instructions will be sent to your email")
        
        with tab2:
            st.subheader("Create New Account")
            with st.form("register_form"):
                reg_name = st.text_input("Full Name", placeholder="John Doe")
                reg_email = st.text_input("Email Address", placeholder="john@company.com")
                reg_password = st.text_input("Password", type="password", placeholder="Choose a strong password")
                reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                reg_company = st.text_input("Company Name", placeholder="Your Company")
                reg_tier = st.selectbox("Account Type", ["Free", "Professional", "Enterprise"])
                
                terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy")
                
                register_btn = st.form_submit_button("🚀 Create Account", type="primary", use_container_width=True)
                
                if register_btn:
                    if not all([reg_name, reg_email, reg_password, reg_confirm]):
                        st.error("❌ Please fill in all fields")
                    elif reg_password != reg_confirm:
                        st.error("❌ Passwords don't match")
                    elif not terms_accepted:
                        st.error("❌ Please accept the terms and conditions")
                    else:
                        # Register user
                        if register_user(reg_email, reg_password, reg_name, reg_company, reg_tier.lower()):
                            st.success("✅ Account created successfully! Please login.")
                        else:
                            st.error("❌ Registration failed. Email may already exist.")
        
        with tab3:
            st.subheader("Demo Access")
            st.info("🎯 Experience NXTRIX CRM with full demo access - no registration required!")
            
            demo_features = [
                "✅ Full CRM Dashboard",
                "✅ Deal Analysis Tools", 
                "✅ Portfolio Analytics",
                "✅ AI-Powered Insights",
                "✅ Sample Data Included"
            ]
            
            for feature in demo_features:
                st.write(feature)
            
            if st.button("🚀 Start Demo", type="primary", use_container_width=True):
                st.session_state.user_authenticated = True
                st.session_state.user_email = "demo@nxtrix.com"
                st.session_state.user_tier = "demo"
                st.session_state.is_admin = False
                st.success("🎉 Demo access granted! Exploring NXTRIX CRM...")
                st.rerun()

def authenticate_user(email: str, password: str) -> bool:
    """Authenticate user against database"""
    # For now, implement basic authentication
    # In production, this would check against your Supabase auth
    demo_users = {
        "admin@nxtrix.com": {"password": "admin123", "tier": "enterprise", "is_admin": True},
        "demo@nxtrix.com": {"password": "demo123", "tier": "professional", "is_admin": False},
        "test@nxtrix.com": {"password": "test123", "tier": "free", "is_admin": False}
    }
    
    if email in demo_users and demo_users[email]["password"] == password:
        return True
    return False

def register_user(email: str, password: str, name: str, company: str, tier: str) -> bool:
    """Register new user in database"""
    # In production, this would create user in Supabase
    # For now, just return True for demo purposes
    return True

def get_user_tier(email: str) -> str:
    """Get user's subscription tier"""
    demo_users = {
        "admin@nxtrix.com": "enterprise",
        "demo@nxtrix.com": "professional", 
        "test@nxtrix.com": "free"
    }
    return demo_users.get(email, "free")

def check_admin_status(email: str) -> bool:
    """Check if user has admin privileges"""
    return email == "admin@nxtrix.com"