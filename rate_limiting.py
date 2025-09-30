#!/usr/bin/env python3
"""
Rate Limiting for NXTRIX CRM
Prevents brute force attacks and API abuse
"""

import streamlit as st
import time
from collections import defaultdict, deque
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self):
        self.attempts = defaultdict(deque)
        
    def is_rate_limited(self, identifier: str, limit: int, window: int) -> Tuple[bool, int]:
        """
        Check if an identifier is rate limited
        
        Args:
            identifier: IP address, user ID, or session ID
            limit: Maximum number of attempts
            window: Time window in seconds
            
        Returns:
            Tuple of (is_limited, remaining_attempts)
        """
        current_time = time.time()
        user_attempts = self.attempts[identifier]
        
        # Remove old attempts outside the window
        while user_attempts and user_attempts[0] < current_time - window:
            user_attempts.popleft()
            
        # Check if limit exceeded
        if len(user_attempts) >= limit:
            return True, 0
            
        return False, limit - len(user_attempts)
        
    def record_attempt(self, identifier: str):
        """Record an attempt for the identifier"""
        self.attempts[identifier].append(time.time())
        
    def clear_attempts(self, identifier: str):
        """Clear all attempts for an identifier (e.g., after successful login)"""
        if identifier in self.attempts:
            del self.attempts[identifier]

# Global rate limiter instance
rate_limiter = RateLimiter()

def check_login_rate_limit() -> bool:
    """Check if login attempts are rate limited"""
    # Use session ID or IP as identifier
    identifier = st.session_state.get('session_id', 'unknown')
    
    is_limited, remaining = rate_limiter.is_rate_limited(identifier, 5, 300)  # 5 attempts per 5 minutes
    
    if is_limited:
        st.error("⛔ Too many login attempts. Please wait 5 minutes before trying again.")
        return False
        
    if remaining <= 2:
        st.warning(f"⚠️ {remaining} login attempts remaining before rate limit.")
        
    return True

def record_login_attempt():
    """Record a login attempt"""
    identifier = st.session_state.get('session_id', 'unknown')
    rate_limiter.record_attempt(identifier)
    
def clear_login_attempts():
    """Clear login attempts after successful login"""
    identifier = st.session_state.get('session_id', 'unknown')
    rate_limiter.clear_attempts(identifier)
