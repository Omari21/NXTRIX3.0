#!/usr/bin/env python3
"""
Security Headers for NXTRIX CRM
Implements security headers to prevent common web vulnerabilities
"""

import streamlit as st

def apply_security_headers():
    """Apply security headers to prevent XSS, clickjacking, etc."""
    
    # Security headers as HTML meta tags and JavaScript
    security_html = """
    <script>
        // Security Headers Implementation
        if (window.self !== window.top) {
            // Prevent iframe embedding (clickjacking protection)
            window.top.location = window.self.location;
        }
        
        // Content Security Policy
        const meta_csp = document.createElement('meta');
        meta_csp.httpEquiv = "Content-Security-Policy";
        meta_csp.content = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: https:;";
        document.head.appendChild(meta_csp);
        
        // X-Content-Type-Options
        const meta_nosniff = document.createElement('meta');
        meta_nosniff.httpEquiv = "X-Content-Type-Options";
        meta_nosniff.content = "nosniff";
        document.head.appendChild(meta_nosniff);
        
        // Referrer Policy
        const meta_referrer = document.createElement('meta');
        meta_referrer.name = "referrer";
        meta_referrer.content = "strict-origin-when-cross-origin";
        document.head.appendChild(meta_referrer);
    </script>
    
    <meta http-equiv="X-Frame-Options" content="DENY">
    <meta http-equiv="X-XSS-Protection" content="1; mode=block">
    """
    
    st.markdown(security_html, unsafe_allow_html=True)

# Call this function at the start of your main app
if __name__ == "__main__":
    apply_security_headers()
