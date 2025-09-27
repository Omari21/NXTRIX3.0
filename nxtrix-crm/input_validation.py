#!/usr/bin/env python3
"""
Enhanced Input Validation for NXTRIX CRM
Comprehensive validation and sanitization
"""

import re
import html
from typing import Optional, List, Dict, Any

class SecurityValidator:
    
    SQL_INJECTION_PATTERNS = [
        r"((SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION))",
        r"(--|;|\/\*|\*\/|xp_|sp_)",
        r"((OR|AND)\s+\d+\s*=\s*\d+)",
        r"((OR|AND)\s+['"]?[^'"]*['"]?\s*=\s*['"]?[^'"]*['"]?)"
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>.*?</iframe>"
    ]
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email address format"""
        if not email or len(email) > 254:
            return False, "Email address is required and must be less than 254 characters"
            
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email address format"
            
        return True, ""
        
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if not password:
            return False, "Password is required"
            
        if len(password) < 12:
            return False, "Password must be at least 12 characters long"
            
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
            
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
            
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
            
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};':"\|,.<>\/?]', password):
            return False, "Password must contain at least one special character"
            
        # Check for common weak passwords
        weak_patterns = ['password', '123456', 'qwerty', 'abc123', 'letmein']
        password_lower = password.lower()
        for pattern in weak_patterns:
            if pattern in password_lower:
                return False, f"Password cannot contain common patterns like '{pattern}'"
                
        return True, ""
        
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """Validate phone number format"""
        if not phone:
            return True, ""  # Phone is optional
            
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        if len(digits_only) < 10 or len(digits_only) > 15:
            return False, "Phone number must be between 10-15 digits"
            
        return True, ""
        
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input to prevent XSS"""
        if not text:
            return ""
            
        # HTML escape
        text = html.escape(text)
        
        # Remove potential XSS patterns
        for pattern in SecurityValidator.XSS_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
        return text.strip()
        
    @staticmethod
    def detect_sql_injection(text: str) -> bool:
        """Detect potential SQL injection attempts"""
        if not text:
            return False
            
        text_upper = text.upper()
        for pattern in SecurityValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_upper, re.IGNORECASE):
                return True
                
        return False
        
    @staticmethod
    def validate_and_sanitize_form_data(data: Dict[str, Any]) -> Tuple[bool, Dict[str, str], List[str]]:
        """
        Validate and sanitize form data
        
        Returns:
            Tuple of (is_valid, sanitized_data, error_messages)
        """
        errors = []
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Check for SQL injection attempts
                if SecurityValidator.detect_sql_injection(value):
                    errors.append(f"Invalid characters detected in {key}")
                    continue
                    
                # Sanitize the input
                sanitized[key] = SecurityValidator.sanitize_input(value)
            else:
                sanitized[key] = value
                
        # Specific field validations
        if 'email' in sanitized:
            is_valid, error = SecurityValidator.validate_email(sanitized['email'])
            if not is_valid:
                errors.append(error)
                
        if 'password' in sanitized:
            is_valid, error = SecurityValidator.validate_password(sanitized['password'])
            if not is_valid:
                errors.append(error)
                
        if 'phone' in sanitized:
            is_valid, error = SecurityValidator.validate_phone(sanitized['phone'])
            if not is_valid:
                errors.append(error)
                
        return len(errors) == 0, sanitized, errors

# Usage example:
# is_valid, clean_data, errors = SecurityValidator.validate_and_sanitize_form_data({
#     'email': user_email,
#     'password': user_password,
#     'full_name': full_name
# })
