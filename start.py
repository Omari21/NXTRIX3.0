#!/usr/bin/env python3
"""
Startup script for NXTRIX Platform on Railway
Handles dynamic port configuration
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
    
    # Build streamlit command
    cmd = [
        'streamlit', 'run', 'streamlit_app.py',
        '--server.port', port,
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.enableCORS', 'false',
        '--server.enableXsrfProtection', 'false'
    ]
    
    print(f"Starting NXTRIX Platform on port {port}")
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