#!/usr/bin/env python3
"""
NXTRIX CRM - Security Implementation Verification
Verifies that all security hardening measures are properly implemented
"""

import ast
import os
import re
from typing import List, Dict, Tuple

class SecurityVerification:
    def __init__(self, app_file: str = "streamlit_app.py"):
        self.app_file = app_file
        self.security_score = 0
        self.max_score = 100
        self.results = []
        
    def verify_implementation(self) -> Dict:
        """Run comprehensive security verification"""
        print("🔒 NXTRIX CRM - Security Implementation Verification")
        print("=" * 60)
        
        # Read the application file
        try:
            with open(self.app_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"❌ Error: {self.app_file} not found")
            return {"score": 0, "results": ["File not found"]}
        
        # Run verification checks
        self._verify_imports(content)
        self._verify_security_functions(content)
        self._verify_authentication_hardening(content)
        self._verify_input_validation(content)
        self._verify_rate_limiting(content)
        self._verify_security_headers(content)
        self._verify_audit_logging(content)
        self._verify_main_function_integration(content)
        
        # Calculate final score
        final_score = min(self.security_score, self.max_score)
        
        # Display results
        self._display_results(final_score)
        
        return {
            "score": final_score,
            "max_score": self.max_score,
            "results": self.results,
            "status": "EXCELLENT" if final_score >= 95 else "GOOD" if final_score >= 85 else "NEEDS_IMPROVEMENT"
        }
    
    def _verify_imports(self, content: str):
        """Verify required security imports"""
        required_imports = ['bcrypt', 'hashlib', 'secrets', 're', 'time']
        missing_imports = []
        
        for imp in required_imports:
            if f"import {imp}" not in content:
                missing_imports.append(imp)
        
        if not missing_imports:
            self.security_score += 10
            self.results.append("✅ All required security imports present")
        else:
            self.results.append(f"❌ Missing imports: {', '.join(missing_imports)}")
    
    def _verify_security_functions(self, content: str):
        """Verify security functions are implemented"""
        required_functions = [
            'apply_security_hardening',
            'check_rate_limit',
            'validate_input',
            'log_security_event'
        ]
        
        missing_functions = []
        for func in required_functions:
            if f"def {func}" not in content:
                missing_functions.append(func)
        
        if not missing_functions:
            self.security_score += 20
            self.results.append("✅ All security functions implemented")
        else:
            score_deduction = len(missing_functions) * 5
            self.security_score += max(0, 20 - score_deduction)
            self.results.append(f"⚠️ Missing security functions: {', '.join(missing_functions)}")
    
    def _verify_authentication_hardening(self, content: str):
        """Verify authentication system hardening"""
        auth_checks = [
            ('rate limiting in auth', 'check_rate_limit("login_attempt"'),
            ('input validation in auth', 'validate_input(email'),
            ('security logging in auth', 'log_security_event'),
            ('bcrypt verification', '_verify_password')
        ]
        
        missing_checks = []
        for check_name, pattern in auth_checks:
            if pattern not in content:
                missing_checks.append(check_name)
        
        if not missing_checks:
            self.security_score += 20
            self.results.append("✅ Authentication system fully hardened")
        else:
            score_deduction = len(missing_checks) * 5
            self.security_score += max(0, 20 - score_deduction)
            self.results.append(f"⚠️ Missing auth hardening: {', '.join(missing_checks)}")
    
    def _verify_input_validation(self, content: str):
        """Verify input validation implementation"""
        validation_patterns = [
            'SQL injection patterns',
            'XSS patterns', 
            'max_length',
            'validate_input.*deal_creation',
            'validate_input.*feedback'
        ]
        
        missing_validations = []
        for pattern in validation_patterns:
            if not re.search(pattern, content, re.IGNORECASE):
                missing_validations.append(pattern)
        
        if not missing_validations:
            self.security_score += 15
            self.results.append("✅ Comprehensive input validation implemented")
        else:
            score_deduction = len(missing_validations) * 3
            self.security_score += max(0, 15 - score_deduction)
            self.results.append(f"⚠️ Missing validation patterns: {len(missing_validations)}")
    
    def _verify_rate_limiting(self, content: str):
        """Verify rate limiting implementation"""
        rate_limit_checks = [
            'check_rate_limit("login_attempt"',
            'check_rate_limit("deal_creation"',
            'check_rate_limit("feedback_submission"',
            'rate_limits' in content
        ]
        
        implemented = sum(1 for check in rate_limit_checks if 
                         (check if isinstance(check, bool) else check in content))
        
        if implemented >= 3:
            self.security_score += 10
            self.results.append("✅ Rate limiting properly implemented")
        else:
            self.security_score += implemented * 2
            self.results.append(f"⚠️ Rate limiting partially implemented ({implemented}/4)")
    
    def _verify_security_headers(self, content: str):
        """Verify security headers implementation"""
        header_checks = [
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-Content-Type-Options',
            'apply_security_hardening()'
        ]
        
        missing_headers = []
        for header in header_checks:
            if header not in content:
                missing_headers.append(header)
        
        if not missing_headers:
            self.security_score += 10
            self.results.append("✅ Security headers implemented")
        else:
            score_deduction = len(missing_headers) * 2
            self.security_score += max(0, 10 - score_deduction)
            self.results.append(f"⚠️ Missing security headers: {len(missing_headers)}")
    
    def _verify_audit_logging(self, content: str):
        """Verify security audit logging"""
        log_events = [
            'successful_login',
            'failed_login',
            'invalid_input_attempt',
            'rate_limit_exceeded',
            'deal_creation_attempt'
        ]
        
        logged_events = sum(1 for event in log_events if event in content)
        
        if logged_events >= 4:
            self.security_score += 10
            self.results.append("✅ Comprehensive security logging implemented")
        else:
            self.security_score += logged_events * 2
            self.results.append(f"⚠️ Security logging partially implemented ({logged_events}/5)")
    
    def _verify_main_function_integration(self, content: str):
        """Verify security integration in main function"""
        main_integrations = [
            'apply_security_hardening()',
            'def main():',
        ]
        
        all_integrated = all(integration in content for integration in main_integrations)
        
        if all_integrated:
            self.security_score += 5
            self.results.append("✅ Security hardening integrated in main function")
        else:
            self.results.append("❌ Security hardening not properly integrated in main function")
    
    def _display_results(self, final_score: int):
        """Display verification results"""
        print(f"\n📊 SECURITY VERIFICATION RESULTS")
        print("=" * 60)
        
        for result in self.results:
            print(f"   {result}")
        
        print(f"\n🎯 OVERALL SECURITY SCORE: {final_score}/{self.max_score}")
        
        if final_score >= 95:
            print("🏆 EXCELLENT - Security implementation is comprehensive!")
            status_color = "🟢"
        elif final_score >= 85:
            print("✅ GOOD - Strong security implementation with minor gaps")
            status_color = "🟡"
        else:
            print("⚠️ NEEDS IMPROVEMENT - Security gaps need attention")
            status_color = "🔴"
        
        print(f"\n{status_color} Security Status: {'PRODUCTION READY' if final_score >= 90 else 'DEVELOPMENT ONLY'}")
        
        # Security recommendations
        if final_score < 100:
            print(f"\n💡 RECOMMENDATIONS:")
            print("   • Review missing components identified above")
            print("   • Test security functions with various inputs")
            print("   • Consider additional security measures for production")
        
        print(f"\n🔒 Security verification completed!")

def main():
    """Run security verification"""
    verifier = SecurityVerification()
    results = verifier.verify_implementation()
    
    # Save results to file
    with open("security_verification_results.txt", "w") as f:
        f.write(f"NXTRIX CRM Security Verification Results\n")
        f.write(f"Score: {results['score']}/{results['max_score']}\n")
        f.write(f"Status: {results['status']}\n\n")
        f.write("Details:\n")
        for result in results['results']:
            f.write(f"  {result}\n")
    
    return results

if __name__ == "__main__":
    main()