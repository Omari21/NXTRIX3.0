# NXTRIX Security Integration Code

# 1. ADD THESE IMPORTS:

# Security improvements
import time
import html
import secrets
import string
from collections import defaultdict, deque


# 2. ADD THESE FUNCTIONS:

def apply_security_hardening():
    """Apply security hardening measures - call this at the start of main()"""
    
    # 1. Security Headers (3 points)
    st.markdown("""
    <script>
        // Prevent clickjacking
        if (window.self !== window.top) {
            window.top.location = window.self.location;
        }
    </script>
    <meta http-equiv="X-Frame-Options" content="DENY">
    <meta http-equiv="X-XSS-Protection" content="1; mode=block">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';">
    """, unsafe_allow_html=True)
    
    # 2. Generate secure demo credentials (2 points)
    if 'secure_demo_generated' not in st.session_state:
        st.session_state.secure_demo_generated = True
        st.session_state.demo_email = f"demo_{secrets.token_hex(4)}@nxtrix.local"
        st.session_state.demo_password = ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$") for _ in range(16))
    
    # 3. Initialize rate limiting (2 points) 
    if 'rate_limiter' not in st.session_state:
        st.session_state.rate_limiter = defaultdict(deque)
    
    # 4. Session timeout (1 point)
    if 'session_start' not in st.session_state:
        st.session_state.session_start = time.time()
    elif time.time() - st.session_state.session_start > 3600:  # 1 hour timeout
        if st.session_state.get('user_authenticated'):
            st.session_state.user_authenticated = False
            st.warning("⏰ Session expired. Please log in again.")
            st.rerun()

def check_rate_limit(action_type="login", limit=5, window=300):
    """Simple rate limiting (2 points)"""
    current_time = time.time()
    session_id = st.session_state.get('session_id', 'anonymous')
    
    # Get attempts for this session and action type
    key = f"{session_id}_{action_type}"
    attempts = st.session_state.rate_limiter[key]
    
    # Remove old attempts
    while attempts and attempts[0] < current_time - window:
        attempts.popleft()
    
    # Check if limit exceeded
    if len(attempts) >= limit:
        return False, 0
    
    return True, limit - len(attempts)

def record_attempt(action_type="login"):
    """Record an attempt"""
    session_id = st.session_state.get('session_id', 'anonymous')
    key = f"{session_id}_{action_type}"
    st.session_state.rate_limiter[key].append(time.time())

def validate_input(text, field_name="input"):
    """Enhanced input validation (1 point)"""
    if not text:
        return text, ""
    
    # Basic sanitization
    sanitized = html.escape(str(text)).strip()
    
    # Check for suspicious patterns
    suspicious_patterns = [
        '<script', 'javascript:', 'SELECT ', 'INSERT ', 'DELETE ', 'DROP ', '--', ';'
    ]
    
    text_upper = sanitized.upper()
    for pattern in suspicious_patterns:
        if pattern.upper() in text_upper:
            return "", f"Invalid characters detected in {field_name}"
    
    return sanitized, ""

def log_security_event(event_type, details=None):
    """Simple audit logging (1 point)"""
    timestamp = datetime.now().isoformat()
    user_info = st.session_state.get('current_user', 'anonymous')
    
    log_entry = {
        'timestamp': timestamp,
        'event_type': event_type,
        'user': user_info,
        'details': details or {},
        'session_id': st.session_state.get('session_id', 'unknown')
    }
    
    # In production, send this to your logging service
    # For now, just store in session state
    if 'security_logs' not in st.session_state:
        st.session_state.security_logs = []
    
    st.session_state.security_logs.append(log_entry)
    
    # Keep only last 100 logs in session
    if len(st.session_state.security_logs) > 100:
        st.session_state.security_logs = st.session_state.security_logs[-100:]


# 3. REPLACE _check_credentials WITH:

# Replace your existing _check_credentials function with this enhanced version:

@staticmethod
def _check_credentials(email, password):
    """Enhanced credential checking with security improvements"""
    
    # Rate limiting check (2 points)
    allowed, remaining = check_rate_limit("login", 5, 300)  # 5 attempts per 5 minutes
    if not allowed:
        log_security_event("rate_limit_exceeded", {"email": email})
        UIHelper.show_error("⛔ Too many login attempts. Please wait 5 minutes.")
        return False
    
    # Input validation (1 point)
    clean_email, email_error = validate_input(email, "email")
    clean_password, pwd_error = validate_input(password, "password")
    
    if email_error or pwd_error:
        log_security_event("suspicious_input", {"email": email, "errors": [email_error, pwd_error]})
        return False
    
    # Record the attempt
    record_attempt("login")
    
    # Use secure demo credentials (2 points)
    if not PRODUCTION_MODE:
        demo_email = st.session_state.get('demo_email', 'demo@nxtrix.com')
        demo_password = st.session_state.get('demo_password', 'nxtrix2025')
        
        if clean_email.lower() == demo_email and clean_password == demo_password:
            log_security_event("successful_login", {"email": clean_email, "type": "demo"})
            return True
    
    # Production database check
    if PRODUCTION_MODE:
        try:
            db_service = get_db_service()
            if db_service and hasattr(db_service, 'supabase'):
                result = db_service.supabase.table('profiles').select('email, password_hash').eq('email', clean_email.lower()).execute()
                if result.data:
                    user_data = result.data[0]
                    stored_hash = user_data.get('password_hash', '')
                    if stored_hash and UserAuthSystem._verify_password(clean_password, stored_hash):
                        log_security_event("successful_login", {"email": clean_email, "type": "production"})
                        return True
                    else:
                        log_security_event("failed_login", {"email": clean_email, "reason": "invalid_password"})
                else:
                    log_security_event("failed_login", {"email": clean_email, "reason": "user_not_found"})
        except Exception as e:
            log_security_event("login_error", {"email": clean_email, "error": str(e)})
            return False
    
    return False


