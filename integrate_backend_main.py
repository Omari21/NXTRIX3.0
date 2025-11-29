#!/usr/bin/env python3
"""
Add missing authentication UI and integrate backend into main function
"""

def integrate_backend_into_main():
    """Add authentication UI and integrate backend initialization"""
    
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find where to add the authentication UI function (before main function)
        main_function_pos = content.find('def main():')
        if main_function_pos == -1:
            print("❌ Could not find main function")
            return False
        
        # Add the authentication UI function
        auth_ui_function = '''
def show_authentication_ui():
    """Enhanced authentication UI with backend integration"""
    
    if st.session_state.get('authenticated', False):
        # User is already authenticated, show user info
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.success(f"✅ Welcome back, {st.session_state.get('first_name', 'User')}!")
            
            user_tier = st.session_state.get('user_tier', 'free')
            tier_emoji = {"free": "🆓", "professional": "💼", "enterprise": "🏢"}
            st.info(f"{tier_emoji.get(user_tier, '🆓')} {user_tier.title()} Plan")
            
            if st.button("🚪 Logout", use_container_width=True):
                result = logout_user()
                if result["success"]:
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result["message"])
        return
    
    st.header("🔐 Welcome to NXTRIX CRM")
    st.subheader("Please login or register to continue")
    
    # Authentication tabs
    tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Register", "🎮 Demo Access"])
    
    with tab1:
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email Address", placeholder="your.email@company.com")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            remember_me = st.checkbox("🔄 Remember me")
            
            col1, col2 = st.columns(2)
            with col1:
                login_button = st.form_submit_button("🔑 Login", use_container_width=True)
            with col2:
                forgot_password = st.form_submit_button("❓ Forgot Password", use_container_width=True)
            
            if login_button and email and password:
                with st.spinner("🔐 Authenticating..."):
                    result = authenticate_user(email, password)
                    
                    if result["success"]:
                        # Set session state
                        st.session_state['authenticated'] = True
                        st.session_state['user_id'] = result["user_id"]
                        st.session_state['email'] = result["email"]
                        st.session_state['first_name'] = result["first_name"]
                        st.session_state['last_name'] = result["last_name"]
                        st.session_state['company'] = result["company"]
                        st.session_state['user_tier'] = result["user_tier"]
                        st.session_state['is_admin'] = result["is_admin"]
                        
                        st.success(f"✅ Welcome back, {result['first_name']}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
            
            elif forgot_password:
                st.info("🔗 Password reset functionality would be implemented here")
    
    with tab2:
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("👤 First Name", placeholder="John")
                email = st.text_input("📧 Email Address", placeholder="john@company.com")
                password = st.text_input("🔒 Password", type="password", placeholder="Min 8 characters")
            
            with col2:
                last_name = st.text_input("👥 Last Name", placeholder="Doe")
                company = st.text_input("🏢 Company (Optional)", placeholder="Your Company")
                confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm password")
            
            terms_accepted = st.checkbox("✅ I agree to the Terms of Service and Privacy Policy")
            newsletter_signup = st.checkbox("📧 Subscribe to product updates (optional)")
            
            register_button = st.form_submit_button("📝 Create Account", use_container_width=True)
            
            if register_button:
                # Validation
                if not all([first_name, last_name, email, password, confirm_password]):
                    st.error("❌ Please fill in all required fields")
                elif password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(password) < 8:
                    st.error("❌ Password must be at least 8 characters")
                elif not terms_accepted:
                    st.error("❌ Please accept the Terms of Service")
                else:
                    with st.spinner("📝 Creating your account..."):
                        result = register_user(email, password, first_name, last_name, company)
                        
                        if result["success"]:
                            st.success(f"✅ {result['message']}")
                            st.info("🔐 Please use the Login tab to access your account")
                        else:
                            st.error(f"❌ {result['message']}")
    
    with tab3:
        st.subheader("🎮 Try Demo Mode")
        st.info("Experience NXTRIX CRM with sample data - no registration required!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**👤 Demo User Access**")
            st.text("Email: demo@nxtrix.com")
            st.text("Password: demo123")
            st.text("Tier: Professional")
            
            if st.button("🎮 Login as Demo User", use_container_width=True):
                with st.spinner("🔐 Logging in as demo user..."):
                    result = authenticate_user("demo@nxtrix.com", "demo123")
                    
                    if result["success"]:
                        # Set session state
                        st.session_state['authenticated'] = True
                        st.session_state['user_id'] = result["user_id"]
                        st.session_state['email'] = result["email"]
                        st.session_state['first_name'] = result["first_name"]
                        st.session_state['last_name'] = result["last_name"]
                        st.session_state['company'] = result["company"]
                        st.session_state['user_tier'] = result["user_tier"]
                        st.session_state['is_admin'] = result["is_admin"]
                        
                        st.success(f"✅ Welcome to the demo, {result['first_name']}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Demo access failed")
        
        with col2:
            st.markdown("**🔧 Admin Demo Access**")
            st.text("Email: admin@nxtrix.com")
            st.text("Password: admin123")
            st.text("Tier: Enterprise (Admin)")
            
            if st.button("🔧 Login as Admin Demo", use_container_width=True):
                with st.spinner("🔐 Logging in as admin..."):
                    result = authenticate_user("admin@nxtrix.com", "admin123")
                    
                    if result["success"]:
                        # Set session state
                        st.session_state['authenticated'] = True
                        st.session_state['user_id'] = result["user_id"]
                        st.session_state['email'] = result["email"]
                        st.session_state['first_name'] = result["first_name"]
                        st.session_state['last_name'] = result["last_name"]
                        st.session_state['company'] = result["company"]
                        st.session_state['user_tier'] = result["user_tier"]
                        st.session_state['is_admin'] = result["is_admin"]
                        
                        st.success(f"✅ Welcome Admin {result['first_name']}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Admin demo access failed")
        
        st.divider()
        st.markdown("**✨ Demo Features Include:**")
        st.markdown("• Full CRM functionality with sample data")
        st.markdown("• All Professional/Enterprise features")
        st.markdown("• No time limits or restrictions")
        st.markdown("• Data resets every 24 hours")

'''
        
        # Insert the authentication UI function before main
        new_content = content[:main_function_pos] + auth_ui_function + '\n' + content[main_function_pos:]
        
        # Now find the main function and add backend initialization
        main_start = new_content.find('def main():')
        main_body_start = new_content.find('"""', main_start) + 3
        main_body_start = new_content.find('"""', main_body_start) + 3
        
        # Add backend initialization at the start of main function
        backend_init = '''
    # Initialize backend connection
    init_database_connection()
    
'''
        
        new_content = new_content[:main_body_start] + backend_init + new_content[main_body_start:]
        
        # Write the updated content
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Successfully integrated authentication UI and backend initialization")
        
        # Test compilation
        try:
            compile(new_content, 'streamlit_app.py', 'exec')
            print("✅ File compiles successfully")
            return True
        except SyntaxError as e:
            print(f"⚠️ Syntax error: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    integrate_backend_into_main()