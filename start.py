#!/usr/bin/env python3
"""
NXTRIX Platform - Production Startup Script
High-performance web application with custom interface
"""

import os
import sys
import subprocess

def main():
    """Main startup function for NXTRIX web application"""
    
    # Get port from environment (Railway/Netlify)
    port = os.environ.get('PORT', '8000')
    
    print(f"🚀 Starting NXTRIX High-Performance Platform on port {port}")
    print("✨ Custom web application with enterprise-grade interface")
    
    try:
        # Validate port is numeric
        port_num = int(port)
        if not (1 <= port_num <= 65535):
            raise ValueError("Port out of range")
    except ValueError:
        print(f"Invalid port '{port}', using default 8000")
        port = '8000'
    
    # Build streamlit command for high-performance web app
    cmd = [
        'streamlit', 'run', 'nxtrix_webapp.py',
        '--server.port', port,
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.enableCORS', 'false',
        '--server.enableXsrfProtection', 'false'
    ]
    
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