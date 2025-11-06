#!/usr/bin/env python3
"""
Startup script for NXTRIX Enterprise Platform
Handles dynamic port configuration for enterprise CRM interface
"""
import os
import subprocess
import sys

def main():
    # Get port from environment variable, default to 8000
    port = os.environ.get('PORT', '8000')
    
    # Validate port is numeric
    try:
        port_num = int(port)
        if not (1 <= port_num <= 65535):
            raise ValueError("Port out of range")
    except ValueError:
        print(f"Invalid port '{port}', using default 8000")
        port = '8000'
    
    # Build streamlit command for enterprise app
    cmd = [
        'streamlit', 'run', 'enterprise_app_fixed.py',
        '--server.port', port,
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.enableCORS', 'false',
        '--server.enableXsrfProtection', 'false',
        '--theme.base', 'light'
    ]
    
    print(f"Starting NXTRIX Enterprise Platform on port {port}")
    print(f"Command: {' '.join(cmd)}")
    
    # Execute streamlit
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Application stopped by user")
        sys.exit(0)

if __name__ == '__main__':
    main()