#!/usr/bin/env python3
"""
NXTRIX CRM - Comprehensive Security Audit
Scans for potential security vulnerabilities and provides recommendations
"""

import os
import re
from pathlib import Path

class SecurityAuditor:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.vulnerabilities = []
        self.warnings = []
        self.recommendations = []
        
    def audit_authentication(self):
        """Audit authentication-related security"""
        print("🔐 Auditing Authentication Security...")
        
        # Check for hardcoded credentials
        self._check_hardcoded_credentials()
        
        # Check authentication bypass patterns
        self._check_auth_bypass_patterns()
        
        # Check password security
        self._check_password_security()
        
    def audit_input_validation(self):
        """Audit input validation and sanitization"""
        print("🛡️ Auditing Input Validation...")
        
        # Check for SQL injection vulnerabilities
        self._check_sql_injection()
        
        # Check for XSS vulnerabilities
        self._check_xss_vulnerabilities()
        
        # Check file upload security
        self._check_file_upload_security()
        
    def audit_api_security(self):
        """Audit API and external service security"""
        print("🔌 Auditing API Security...")
        
        # Check API key exposure
        self._check_api_key_exposure()
        
        # Check rate limiting
        self._check_rate_limiting()
        
        # Check external service calls
        self._check_external_services()
        
    def audit_data_protection(self):
        """Audit data protection and privacy"""
        print("🔒 Auditing Data Protection...")
        
        # Check for sensitive data exposure
        self._check_sensitive_data()
        
        # Check database security
        self._check_database_security()
        
        # Check logging security
        self._check_logging_security()
        
    def _check_hardcoded_credentials(self):
        """Check for hardcoded credentials"""
        patterns = [
            r'password\s*=\s*["\'][^"\']{8,}["\']',
            r'api_key\s*=\s*["\'][^"\']{20,}["\']',
            r'secret\s*=\s*["\'][^"\']{16,}["\']',
            r'token\s*=\s*["\'][^"\']{20,}["\']'
        ]
        
        for py_file in self.project_path.glob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.vulnerabilities.append({
                            'type': 'CRITICAL',
                            'category': 'Authentication',
                            'file': str(py_file),
                            'issue': 'Hardcoded credentials detected',
                            'recommendation': 'Move credentials to environment variables'
                        })
            except Exception:
                pass
                
    def _check_auth_bypass_patterns(self):
        """Check for authentication bypass patterns"""
        bypass_patterns = [
            r'len\(password\)\s*>=?\s*\d+',
            r'if.*password.*:.*return.*True',
            r'authenticated\s*=\s*True',
            r'user_authenticated\s*=\s*True'
        ]
        
        for py_file in self.project_path.glob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in bypass_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Check context to avoid false positives
                        line_start = content.rfind('\n', 0, match.start()) + 1
                        line_end = content.find('\n', match.end())
                        line = content[line_start:line_end]
                        
                        if 'demo' not in line.lower() and 'test' not in line.lower():
                            self.warnings.append({
                                'type': 'WARNING',
                                'category': 'Authentication',
                                'file': str(py_file),
                                'line': line.strip(),
                                'issue': 'Potential authentication bypass pattern',
                                'recommendation': 'Review authentication logic carefully'
                            })
            except Exception:
                pass
                
    def _check_password_security(self):
        """Check password security implementation"""
        has_bcrypt = False
        has_hashing = False
        
        for py_file in self.project_path.glob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                if 'import bcrypt' in content or 'from bcrypt' in content:
                    has_bcrypt = True
                if 'hashpw' in content or 'checkpw' in content:
                    has_hashing = True
            except Exception:
                pass
                
        if not has_bcrypt:
            self.recommendations.append({
                'type': 'RECOMMENDATION',
                'category': 'Password Security',
                'issue': 'No bcrypt import found',
                'recommendation': 'Consider using bcrypt for password hashing'
            })
            
        if not has_hashing:
            self.warnings.append({
                'type': 'WARNING',
                'category': 'Password Security',
                'issue': 'No password hashing functions found',
                'recommendation': 'Implement secure password hashing'
            })
            
    def _check_sql_injection(self):
        """Check for SQL injection vulnerabilities"""
        dangerous_patterns = [
            r'\.execute\([^)]*%s[^)]*\)',
            r'\.execute\([^)]*\+[^)]*\)',
            r'f".*\{.*\}.*".*\.execute',
            r'format\(.*\).*\.execute'
        ]
        
        for py_file in self.project_path.glob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in dangerous_patterns:
                    if re.search(pattern, content):
                        self.vulnerabilities.append({
                            'type': 'HIGH',
                            'category': 'SQL Injection',
                            'file': str(py_file),
                            'issue': 'Potential SQL injection vulnerability',
                            'recommendation': 'Use parameterized queries'
                        })
            except Exception:
                pass
                
    def _check_xss_vulnerabilities(self):
        """Check for XSS vulnerabilities"""
        xss_patterns = [
            r'unsafe_allow_html\s*=\s*True',
            r'st\.markdown\([^)]*unsafe_allow_html\s*=\s*True',
            r'st\.write\([^)]*unsafe_allow_html\s*=\s*True'
        ]
        
        unsafe_html_count = 0
        for py_file in self.project_path.glob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in xss_patterns:
                    matches = list(re.finditer(pattern, content))
                    unsafe_html_count += len(matches)
            except Exception:
                pass
                
        if unsafe_html_count > 20:  # Threshold for concern
            self.warnings.append({
                'type': 'WARNING',
                'category': 'XSS Prevention',
                'issue': f'High usage of unsafe_allow_html ({unsafe_html_count} instances)',
                'recommendation': 'Review HTML content for potential XSS vulnerabilities'
            })
            
    def _check_file_upload_security(self):
        """Check file upload security"""
        upload_patterns = [
            r'st\.file_uploader',
            r'uploaded_file',
            r'\.save\(',
            r'open\([^)]*wb[^)]*\)'
        ]
        
        has_uploads = False
        for py_file in self.project_path.glob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in upload_patterns:
                    if re.search(pattern, content):
                        has_uploads = True
                        break
            except Exception:
                pass
                
        if has_uploads:
            self.recommendations.append({
                'type': 'RECOMMENDATION',
                'category': 'File Upload Security',
                'issue': 'File upload functionality detected',
                'recommendation': 'Implement file type validation, size limits, and secure storage'
            })
            
    def _check_api_key_exposure(self):
        """Check for API key exposure"""
        # Check if secrets are properly handled
        uses_secrets = False
        uses_env = False
        
        for py_file in self.project_path.glob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                if 'st.secrets' in content:
                    uses_secrets = True
                if 'os.getenv' in content:
                    uses_env = True
            except Exception:
                pass
                
        if uses_secrets and uses_env:
            self.recommendations.append({
                'type': 'GOOD',
                'category': 'API Security',
                'issue': 'Proper secret management detected',
                'recommendation': 'Continue using environment variables and Streamlit secrets'
            })
        elif not uses_secrets and not uses_env:
            self.vulnerabilities.append({
                'type': 'HIGH',
                'category': 'API Security',
                'issue': 'No proper secret management found',
                'recommendation': 'Use environment variables or Streamlit secrets for API keys'
            })
            
    def _check_rate_limiting(self):
        """Check for rate limiting implementation"""
        rate_limit_patterns = [
            r'rate.*limit',
            r'throttle',
            r'sleep\(\d+\)',
            r'time\.sleep'
        ]
        
        has_rate_limiting = False
        for py_file in self.project_path.glob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in rate_limit_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        has_rate_limiting = True
                        break
            except Exception:
                pass
                
        if not has_rate_limiting:
            self.recommendations.append({
                'type': 'MEDIUM',
                'category': 'API Security',
                'issue': 'No rate limiting detected',
                'recommendation': 'Consider implementing rate limiting for API calls'
            })
            
    def _check_external_services(self):
        """Check external service security"""
        external_services = []
        service_patterns = {
            'OpenAI': r'openai\.',
            'Stripe': r'stripe\.',
            'Twilio': r'twilio',
            'Supabase': r'supabase\.',
            'EmailJS': r'emailjs'
        }
        
        for py_file in self.project_path.glob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                for service, pattern in service_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        if service not in external_services:
                            external_services.append(service)
            except Exception:
                pass
                
        if external_services:
            self.recommendations.append({
                'type': 'GOOD',
                'category': 'External Services',
                'issue': f'External services in use: {", ".join(external_services)}',
                'recommendation': 'Ensure all API keys are secure and monitor for service updates'
            })
            
    def _check_sensitive_data(self):
        """Check for sensitive data exposure"""
        sensitive_patterns = [
            r'print\([^)]*password[^)]*\)',
            r'print\([^)]*token[^)]*\)',
            r'print\([^)]*key[^)]*\)',
            r'st\.write\([^)]*password[^)]*\)',
            r'st\.write\([^)]*token[^)]*\)'
        ]
        
        for py_file in self.project_path.glob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in sensitive_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.warnings.append({
                            'type': 'WARNING',
                            'category': 'Data Protection',
                            'file': str(py_file),
                            'issue': 'Potential sensitive data exposure in output',
                            'recommendation': 'Remove or mask sensitive data in logs/output'
                        })
            except Exception:
                pass
                
    def _check_database_security(self):
        """Check database security"""
        has_rls = False
        has_auth_check = False
        
        # Check SQL files for RLS (Row Level Security)
        for sql_file in self.project_path.glob("*.sql"):
            try:
                content = sql_file.read_text(encoding='utf-8')
                if 'ROW LEVEL SECURITY' in content.upper():
                    has_rls = True
                if 'auth.uid()' in content:
                    has_auth_check = True
            except Exception:
                pass
                
        if has_rls:
            self.recommendations.append({
                'type': 'GOOD',
                'category': 'Database Security',
                'issue': 'Row Level Security (RLS) implemented',
                'recommendation': 'Continue using RLS for data isolation'
            })
        else:
            self.warnings.append({
                'type': 'MEDIUM',
                'category': 'Database Security',
                'issue': 'No Row Level Security found',
                'recommendation': 'Consider implementing RLS in Supabase'
            })
            
    def _check_logging_security(self):
        """Check logging security"""
        logging_patterns = [
            r'logging\.info',
            r'logging\.debug',
            r'print\(',
            r'st\.write\(',
            r'st\.error\(',
            r'st\.warning\('
        ]
        
        logging_count = 0
        for py_file in self.project_path.glob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in logging_patterns:
                    logging_count += len(re.findall(pattern, content))
            except Exception:
                pass
                
        if logging_count > 50 and logging_count < 200:
            self.recommendations.append({
                'type': 'GOOD',
                'category': 'Logging Security',
                'issue': f'Moderate logging usage ({logging_count} instances)',
                'recommendation': 'Ensure logs don\'t contain sensitive information'
            })
        elif logging_count > 200:
            self.warnings.append({
                'type': 'WARNING',
                'category': 'Logging Security',
                'issue': f'High logging usage ({logging_count} instances)',
                'recommendation': 'Review logs for potential information disclosure'
            })
            
    def generate_report(self):
        """Generate comprehensive security report"""
        print("\n" + "="*60)
        print("🛡️  NXTRIX CRM - SECURITY AUDIT REPORT")
        print("="*60)
        
        # Critical vulnerabilities
        critical_vulns = [v for v in self.vulnerabilities if v['type'] == 'CRITICAL']
        high_vulns = [v for v in self.vulnerabilities if v['type'] == 'HIGH']
        medium_vulns = [v for v in self.vulnerabilities if v['type'] == 'MEDIUM']
        
        print(f"\n📊 SECURITY SUMMARY:")
        print(f"   🔴 Critical: {len(critical_vulns)}")
        print(f"   🟠 High: {len(high_vulns)}")
        print(f"   🟡 Medium: {len(medium_vulns)}")
        print(f"   ⚠️  Warnings: {len(self.warnings)}")
        print(f"   💡 Recommendations: {len(self.recommendations)}")
        
        # Critical issues
        if critical_vulns:
            print(f"\n🔴 CRITICAL VULNERABILITIES ({len(critical_vulns)}):")
            for vuln in critical_vulns:
                print(f"   ❌ {vuln['issue']}")
                print(f"      📁 File: {vuln['file']}")
                print(f"      💡 Fix: {vuln['recommendation']}")
                print()
                
        # High priority issues
        if high_vulns:
            print(f"\n🟠 HIGH PRIORITY ISSUES ({len(high_vulns)}):")
            for vuln in high_vulns:
                print(f"   ⚠️  {vuln['issue']}")
                print(f"      📁 File: {vuln['file']}")
                print(f"      💡 Fix: {vuln['recommendation']}")
                print()
                
        # Warnings
        if self.warnings:
            print(f"\n⚠️  SECURITY WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:5]:  # Show first 5
                print(f"   ⚠️  {warning['issue']}")
                if 'file' in warning:
                    print(f"      📁 File: {warning['file']}")
                print(f"      💡 Recommendation: {warning['recommendation']}")
                print()
            if len(self.warnings) > 5:
                print(f"   ... and {len(self.warnings) - 5} more warnings")
                
        # Good practices
        good_practices = [r for r in self.recommendations if r['type'] == 'GOOD']
        if good_practices:
            print(f"\n✅ GOOD SECURITY PRACTICES ({len(good_practices)}):")
            for practice in good_practices:
                print(f"   ✅ {practice['issue']}")
                print(f"      💡 {practice['recommendation']}")
                print()
                
        # Overall security score
        total_issues = len(critical_vulns) + len(high_vulns) + len(medium_vulns)
        if total_issues == 0:
            security_score = 95 + min(len(good_practices) * 1, 5)
        elif total_issues <= 2:
            security_score = 85 - (len(critical_vulns) * 20) - (len(high_vulns) * 10)
        else:
            security_score = max(60 - (len(critical_vulns) * 20) - (len(high_vulns) * 10) - (len(medium_vulns) * 5), 10)
            
        print(f"\n🎯 OVERALL SECURITY SCORE: {security_score}/100")
        
        if security_score >= 90:
            print("   🛡️  EXCELLENT - Production ready with strong security")
        elif security_score >= 80:
            print("   ✅ GOOD - Minor improvements recommended")
        elif security_score >= 70:
            print("   ⚠️  FAIR - Several security issues need attention")
        else:
            print("   🔴 POOR - Critical security issues must be fixed")
            
        return security_score

def main():
    project_path = r"C:\Users\Mania\OneDrive\Documents\NXTRIX3.0\nxtrix-crm"
    
    auditor = SecurityAuditor(project_path)
    
    # Run all security audits
    auditor.audit_authentication()
    auditor.audit_input_validation()
    auditor.audit_api_security()
    auditor.audit_data_protection()
    
    # Generate comprehensive report
    score = auditor.generate_report()
    
    print(f"\n🎯 Security audit completed!")
    print(f"📋 Review the recommendations above to improve security.")
    
    return score >= 80

if __name__ == "__main__":
    main()