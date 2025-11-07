"""
NXTRIX Web Application Launcher
Clean startup script for the high-performance web app
"""

import subprocess
import sys
import os

def launch_webapp():
    """Launch the NXTRIX web application"""
    
    try:
        # Set environment variables for clean Streamlit startup
        os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
        
        print("🚀 Starting NXTRIX High-Performance Web Application...")
        print("📍 URL: http://localhost:8511")
        print("✨ Breaking away from traditional Streamlit layout...")
        
        # Launch the web application
        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "nxtrix_webapp.py", 
            "--server.port", "8511",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching web application: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Web application stopped by user")
        return True
    
    return True

if __name__ == "__main__":
    launch_webapp()