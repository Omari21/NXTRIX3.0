#!/usr/bin/env python
"""
Streamlit Application Launcher with Python 3.13 compatibility
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set event loop policy for Windows Python 3.13 compatibility
if sys.platform == 'win32' and sys.version_info >= (3, 13):
    # Use ProactorEventLoop for better Windows compatibility
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

def main():
    """Launch the Streamlit application"""
    try:
        import streamlit.web.cli as stcli
        import streamlit_app
        
        # Set working directory
        os.chdir(current_dir)
        
        # Launch Streamlit
        sys.argv = ["streamlit", "run", "streamlit_app.py", "--server.port", "8501"]
        stcli.main()
        
    except Exception as e:
        print(f"Error launching application: {e}")
        print("Trying alternative method...")
        
        # Alternative method using subprocess
        import subprocess
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py", "--server.port", "8501",
            "--server.headless", "false"
        ]
        subprocess.run(cmd, cwd=current_dir)

if __name__ == "__main__":
    main()