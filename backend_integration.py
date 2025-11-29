#!/usr/bin/env python3
"""
Phase 3: Backend Integration for NXTRIX CRM
Connects authentication and data to Supabase backend
"""

import streamlit as st
import os

def setup_backend_integration():
    """Add backend integration to NXTRIX CRM"""
    
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check if backend is already integrated
        if 'SUPABASE_URL' in content and 'init_supabase_client' in content:
            print("✅ Backend integration already present")
            return True
        
        # Find the imports section
        imports_end = content.find('# Optional AI module import')
        if imports_end == -1:
            imports_end = content.find('st.set_page_config')
        
        if imports_end == -1:
            print("❌ Could not find imports section")
            return False
        
        # Add backend configuration
        backend_config = '''
# === BACKEND CONFIGURATION ===
def init_supabase_client():
    """Initialize Supabase client with error handling"""
    try:
        # Get credentials from Streamlit secrets or environment
        if hasattr(st, 'secrets') and 'SUPABASE_URL' in st.secrets:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
        else:
            # Fallback to environment variables
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
        
        if url and key:
            supabase = create_client(url, key)
            return supabase
        else:
            print("⚠️ Supabase credentials not found - using demo mode")
            return None
    except Exception as e:
        print(f"⚠️ Could not connect to Supabase: {e}")
        return None

def init_database_connection():
    """Initialize database connection with fallback"""
    global supabase_client
    
    # Try to initialize Supabase client
    supabase_client = init_supabase_client()
    
    if supabase_client:
        print("✅ Connected to Supabase backend")
        st.session_state['backend_connected'] = True
        return True
    else:
        print("⚠️ Running in demo mode without backend")
        st.session_state['backend_connected'] = False
        return False

# Initialize global variables
supabase_client = None

# === USER MANAGEMENT FUNCTIONS ===
def register_user(email: str, password: str, first_name: str, last_name: str, company: str = "") -> dict:
    """Register a new user in the backend"""
    try:
        if supabase_client:
            # Register with Supabase Auth
            auth_response = supabase_client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "company": company,
                        "user_tier": "free",
                        "created_at": datetime.now().isoformat()
                    }
                }
            })
            
            if auth_response.user:
                # Create user profile in users table
                profile_data = {
                    "id": auth_response.user.id,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "company": company,
                    "user_tier": "free",
                    "is_active": True,
                    "created_at": datetime.now().isoformat()
                }
                
                supabase_client.table("users").insert(profile_data).execute()
                
                return {
                    "success": True,
                    "message": "Registration successful! Please check your email for verification.",
                    "user_id": auth_response.user.id
                }
            else:
                return {"success": False, "message": "Registration failed"}
        else:
            # Demo mode - simulate registration
            return {
                "success": True,
                "message": "Demo mode: Registration simulated successfully!",
                "user_id": f"demo_user_{len(st.session_state.get('demo_users', []))}"
            }
    except Exception as e:
        return {"success": False, "message": f"Registration error: {str(e)}"}

def authenticate_user(email: str, password: str) -> dict:
    """Authenticate user with backend"""
    try:
        if supabase_client:
            # Authenticate with Supabase
            auth_response = supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                # Get user profile from database
                profile_response = supabase_client.table("users").select("*").eq("id", auth_response.user.id).execute()
                
                if profile_response.data:
                    user_profile = profile_response.data[0]
                    return {
                        "success": True,
                        "user_id": auth_response.user.id,
                        "email": user_profile["email"],
                        "first_name": user_profile["first_name"],
                        "last_name": user_profile["last_name"],
                        "company": user_profile["company"],
                        "user_tier": user_profile["user_tier"],
                        "is_admin": user_profile.get("is_admin", False)
                    }
                else:
                    return {"success": False, "message": "User profile not found"}
            else:
                return {"success": False, "message": "Invalid credentials"}
        else:
            # Demo mode authentication
            demo_users = {
                "demo@nxtrix.com": {
                    "password": "demo123",
                    "first_name": "Demo",
                    "last_name": "User",
                    "company": "NXTRIX Demo",
                    "user_tier": "professional",
                    "is_admin": False
                },
                "admin@nxtrix.com": {
                    "password": "admin123",
                    "first_name": "Admin",
                    "last_name": "User",
                    "company": "NXTRIX",
                    "user_tier": "enterprise",
                    "is_admin": True
                }
            }
            
            if email in demo_users and demo_users[email]["password"] == password:
                user_data = demo_users[email]
                return {
                    "success": True,
                    "user_id": f"demo_{email}",
                    "email": email,
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "company": user_data["company"],
                    "user_tier": user_data["user_tier"],
                    "is_admin": user_data["is_admin"]
                }
            else:
                return {"success": False, "message": "Invalid demo credentials"}
                
    except Exception as e:
        return {"success": False, "message": f"Authentication error: {str(e)}"}

def logout_user():
    """Logout current user"""
    try:
        if supabase_client:
            supabase_client.auth.sign_out()
        
        # Clear session state
        for key in list(st.session_state.keys()):
            if key.startswith(('authenticated', 'user_', 'email', 'first_name', 'last_name', 'company', 'is_admin')):
                del st.session_state[key]
        
        return {"success": True, "message": "Logged out successfully"}
    except Exception as e:
        return {"success": False, "message": f"Logout error: {str(e)}"}

def update_user_profile(user_id: str, updates: dict) -> dict:
    """Update user profile in backend"""
    try:
        if supabase_client:
            response = supabase_client.table("users").update(updates).eq("id", user_id).execute()
            
            if response.data:
                return {"success": True, "message": "Profile updated successfully"}
            else:
                return {"success": False, "message": "Profile update failed"}
        else:
            # Demo mode - simulate update
            return {"success": True, "message": "Demo mode: Profile update simulated"}
    except Exception as e:
        return {"success": False, "message": f"Update error: {str(e)}"}

def upgrade_user_tier(user_id: str, new_tier: str) -> dict:
    """Upgrade user subscription tier"""
    try:
        if supabase_client:
            updates = {
                "user_tier": new_tier,
                "upgraded_at": datetime.now().isoformat()
            }
            
            response = supabase_client.table("users").update(updates).eq("id", user_id).execute()
            
            if response.data:
                return {"success": True, "message": f"Upgraded to {new_tier} tier successfully"}
            else:
                return {"success": False, "message": "Upgrade failed"}
        else:
            # Demo mode - simulate upgrade
            return {"success": True, "message": f"Demo mode: Upgraded to {new_tier} tier"}
    except Exception as e:
        return {"success": False, "message": f"Upgrade error: {str(e)}"}

# === DATA MANAGEMENT FUNCTIONS ===
def save_deal_data(user_id: str, deal_data: dict) -> dict:
    """Save deal data to backend"""
    try:
        if supabase_client:
            deal_data["user_id"] = user_id
            deal_data["created_at"] = datetime.now().isoformat()
            deal_data["id"] = str(uuid.uuid4())
            
            response = supabase_client.table("deals").insert(deal_data).execute()
            
            if response.data:
                return {"success": True, "message": "Deal saved successfully", "deal_id": deal_data["id"]}
            else:
                return {"success": False, "message": "Failed to save deal"}
        else:
            # Demo mode - simulate save
            return {"success": True, "message": "Demo mode: Deal saved locally", "deal_id": f"demo_{len(st.session_state.get('demo_deals', []))}"}`
    except Exception as e:
        return {"success": False, "message": f"Save error: {str(e)}"}

def load_user_deals(user_id: str) -> list:
    """Load user's deals from backend"""
    try:
        if supabase_client:
            response = supabase_client.table("deals").select("*").eq("user_id", user_id).execute()
            return response.data if response.data else []
        else:
            # Demo mode - return sample deals
            return [
                {
                    "id": "demo_1",
                    "title": "Sunset Apartments",
                    "value": 2500000,
                    "stage": "Due Diligence",
                    "created_at": "2024-01-15T10:00:00Z"
                },
                {
                    "id": "demo_2", 
                    "title": "Downtown Office Complex",
                    "value": 8200000,
                    "stage": "Negotiation",
                    "created_at": "2024-01-10T14:30:00Z"
                }
            ]
    except Exception as e:
        print(f"Error loading deals: {e}")
        return []

def save_client_data(user_id: str, client_data: dict) -> dict:
    """Save client data to backend"""
    try:
        if supabase_client:
            client_data["user_id"] = user_id
            client_data["created_at"] = datetime.now().isoformat()
            client_data["id"] = str(uuid.uuid4())
            
            response = supabase_client.table("clients").insert(client_data).execute()
            
            if response.data:
                return {"success": True, "message": "Client saved successfully", "client_id": client_data["id"]}
            else:
                return {"success": False, "message": "Failed to save client"}
        else:
            # Demo mode - simulate save
            return {"success": True, "message": "Demo mode: Client saved locally"}
    except Exception as e:
        return {"success": False, "message": f"Save error: {str(e)}"}

def load_user_clients(user_id: str) -> list:
    """Load user's clients from backend"""
    try:
        if supabase_client:
            response = supabase_client.table("clients").select("*").eq("user_id", user_id).execute()
            return response.data if response.data else []
        else:
            # Demo mode - return sample clients
            return [
                {
                    "id": "demo_client_1",
                    "name": "ABC Investments",
                    "type": "Institutional",
                    "portfolio_value": 25000000,
                    "last_contact": "2024-01-20"
                },
                {
                    "id": "demo_client_2",
                    "name": "Smith Holdings", 
                    "type": "High Net Worth",
                    "portfolio_value": 8000000,
                    "last_contact": "2024-01-18"
                }
            ]
    except Exception as e:
        print(f"Error loading clients: {e}")
        return []

# === COMMUNICATION FUNCTIONS ===
def log_communication(user_id: str, comm_data: dict) -> dict:
    """Log communication in backend"""
    try:
        if supabase_client:
            comm_data["user_id"] = user_id
            comm_data["created_at"] = datetime.now().isoformat()
            comm_data["id"] = str(uuid.uuid4())
            
            response = supabase_client.table("communications").insert(comm_data).execute()
            
            if response.data:
                return {"success": True, "message": "Communication logged successfully"}
            else:
                return {"success": False, "message": "Failed to log communication"}
        else:
            # Demo mode - simulate logging
            return {"success": True, "message": "Demo mode: Communication logged locally"}
    except Exception as e:
        return {"success": False, "message": f"Logging error: {str(e)}"}

def get_communication_history(user_id: str, client_id: str = None) -> list:
    """Get communication history from backend"""
    try:
        if supabase_client:
            query = supabase_client.table("communications").select("*").eq("user_id", user_id)
            
            if client_id:
                query = query.eq("client_id", client_id)
            
            response = query.order("created_at", desc=True).execute()
            return response.data if response.data else []
        else:
            # Demo mode - return sample communications
            return [
                {
                    "id": "demo_comm_1",
                    "type": "email",
                    "subject": "Investment Proposal Follow-up",
                    "created_at": "2024-01-22T09:30:00Z",
                    "client_name": "ABC Investments"
                },
                {
                    "id": "demo_comm_2",
                    "type": "call",
                    "subject": "Portfolio Review Discussion",
                    "created_at": "2024-01-20T14:15:00Z",
                    "client_name": "Smith Holdings"
                }
            ]
    except Exception as e:
        print(f"Error loading communications: {e}")
        return []

'''
        
        # Insert the backend configuration after imports
        new_content = content[:imports_end] + backend_config + '\n' + content[imports_end:]
        
        # Write the updated content
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Successfully added backend integration functions")
        
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
    setup_backend_integration()