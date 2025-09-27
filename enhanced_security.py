"""
Enterprise Security Module for NXTRIX CRM
Advanced authentication, authorization, and security monitoring
"""

import streamlit as st
import hashlib
import jwt
import secrets
import time
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import sqlite3
import re
import logging
from dataclasses import dataclass

@dataclass
class SecurityEvent:
    timestamp: datetime
    event_type: str
    user_id: str
    ip_address: str
    details: Dict[str, Any]
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL

class EnhancedSecurityManager:
    """Enterprise-grade security management"""
    
    def __init__(self):
        self.secret_key = self._get_or_create_secret()
        self.failed_attempts = {}
        self.active_sessions = {}
        self.security_events = []
        self.setup_logging()
    
    def _get_or_create_secret(self) -> str:
        """Get or create JWT secret key"""
        secret_file = ".streamlit/jwt_secret"
        try:
            with open(secret_file, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            secret = secrets.token_urlsafe(32)
            os.makedirs(os.path.dirname(secret_file), exist_ok=True)
            with open(secret_file, 'w') as f:
                f.write(secret)
            return secret
    
    def setup_logging(self):
        """Setup security logging"""
        logging.basicConfig(
            filename='security.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('nxtrix_security')
    
    def log_security_event(self, event_type: str, user_id: str, details: Dict[str, Any], severity: str = "MEDIUM"):
        """Log security event"""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            user_id=user_id,
            ip_address=self._get_client_ip(),
            details=details,
            severity=severity
        )
        
        self.security_events.append(event)
        self.logger.info(f"{severity}: {event_type} - User: {user_id} - Details: {details}")
        
        # Alert on critical events
        if severity == "CRITICAL":
            self._send_security_alert(event)
    
    def _get_client_ip(self) -> str:
        """Get client IP address"""
        # In production, this would get the real client IP
        return "127.0.0.1"
    
    def _send_security_alert(self, event: SecurityEvent):
        """Send security alert (email, Slack, etc.)"""
        # In production, integrate with alerting system
        st.error(f"🚨 SECURITY ALERT: {event.event_type}")
    
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 with SHA-256
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """Verify password against hash"""
        password_hash, _ = self.hash_password(password, salt)
        return secrets.compare_digest(password_hash, hashed)
    
    def create_jwt_token(self, user_id: str, permissions: List[str], expires_in: int = 3600) -> str:
        """Create JWT token"""
        payload = {
            'user_id': user_id,
            'permissions': permissions,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(16)  # JWT ID for revocation
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Check if token is revoked
            if self._is_token_revoked(payload.get('jti')):
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def _is_token_revoked(self, jti: str) -> bool:
        """Check if token is revoked"""
        # In production, check against revoked tokens database
        return False
    
    def check_rate_limit(self, user_id: str, action: str, limit: int = 5, window: int = 300) -> bool:
        """Advanced rate limiting"""
        current_time = time.time()
        key = f"{user_id}:{action}"
        
        if key not in self.failed_attempts:
            self.failed_attempts[key] = []
        
        # Clean old attempts
        self.failed_attempts[key] = [
            timestamp for timestamp in self.failed_attempts[key]
            if current_time - timestamp < window
        ]
        
        # Check limit
        if len(self.failed_attempts[key]) >= limit:
            self.log_security_event(
                "RATE_LIMIT_EXCEEDED",
                user_id,
                {"action": action, "attempts": len(self.failed_attempts[key])},
                "HIGH"
            )
            return False
        
        # Record attempt
        self.failed_attempts[key].append(current_time)
        return True
    
    def validate_input(self, input_value: str, input_type: str) -> tuple:
        """Advanced input validation"""
        if not input_value:
            return False, "Input cannot be empty"
        
        # SQL injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(--|/\*|\*/|;)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, input_value, re.IGNORECASE):
                self.log_security_event(
                    "SQL_INJECTION_ATTEMPT",
                    st.session_state.get('user_id', 'anonymous'),
                    {"input": input_value[:100], "pattern": pattern},
                    "CRITICAL"
                )
                return False, "Invalid input detected"
        
        # XSS patterns
        xss_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<.*?on\w+.*?>"
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, input_value, re.IGNORECASE):
                self.log_security_event(
                    "XSS_ATTEMPT",
                    st.session_state.get('user_id', 'anonymous'),
                    {"input": input_value[:100]},
                    "HIGH"
                )
                return False, "Potentially malicious input detected"
        
        # Type-specific validation
        if input_type == "email":
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, input_value):
                return False, "Invalid email format"
        
        elif input_type == "password":
            if len(input_value) < 8:
                return False, "Password must be at least 8 characters"
            if not re.search(r"[A-Z]", input_value):
                return False, "Password must contain uppercase letter"
            if not re.search(r"[a-z]", input_value):
                return False, "Password must contain lowercase letter"
            if not re.search(r"\d", input_value):
                return False, "Password must contain number"
        
        return True, "Valid input"
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """Get security dashboard data"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        recent_events = [e for e in self.security_events if e.timestamp > last_24h]
        
        return {
            'total_events_24h': len(recent_events),
            'critical_events_24h': len([e for e in recent_events if e.severity == "CRITICAL"]),
            'failed_logins_24h': len([e for e in recent_events if e.event_type == "LOGIN_FAILED"]),
            'active_sessions': len(self.active_sessions),
            'top_events': self._get_top_security_events(recent_events)
        }
    
    def _get_top_security_events(self, events: List[SecurityEvent]) -> List[Dict[str, Any]]:
        """Get top security events"""
        event_counts = {}
        for event in events:
            key = event.event_type
            event_counts[key] = event_counts.get(key, 0) + 1
        
        return [
            {'event_type': event_type, 'count': count}
            for event_type, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

# Global security manager
security_manager = EnhancedSecurityManager()

# Streamlit integration
def require_authentication(func):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            st.error("Authentication required")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            user_permissions = st.session_state.get('permissions', [])
            if permission not in user_permissions:
                st.error(f"Permission required: {permission}")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator

def show_security_dashboard():
    """Show security dashboard for admins"""
    if st.session_state.get('user_role') != 'admin':
        st.error("Admin access required")
        return
    
    st.subheader("🔒 Security Dashboard")
    
    dashboard_data = security_manager.get_security_dashboard()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Events (24h)", dashboard_data['total_events_24h'])
    
    with col2:
        st.metric("Critical Events", dashboard_data['critical_events_24h'])
    
    with col3:
        st.metric("Failed Logins", dashboard_data['failed_logins_24h'])
    
    with col4:
        st.metric("Active Sessions", dashboard_data['active_sessions'])
    
    # Top security events
    if dashboard_data['top_events']:
        st.subheader("Top Security Events")
        for event in dashboard_data['top_events']:
            st.write(f"**{event['event_type']}**: {event['count']} occurrences")
    
    # Recent events table
    if security_manager.security_events:
        st.subheader("Recent Security Events")
        events_df = pd.DataFrame([
            {
                'Timestamp': e.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Event': e.event_type,
                'User': e.user_id,
                'Severity': e.severity,
                'IP': e.ip_address
            }
            for e in security_manager.security_events[-20:]  # Last 20 events
        ])
        st.dataframe(events_df, use_container_width=True)

# Global instance management
_security_manager_instance = None

def get_security_manager():
    """Get or create the global security manager instance"""
    global _security_manager_instance
    if _security_manager_instance is None:
        _security_manager_instance = EnhancedSecurityManager()
    return _security_manager_instance