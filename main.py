# main.py - Replit entry point
import os
import subprocess
import sys

def install_dependencies():
    """Install required packages for NXTRIX CRM"""
    required_packages = [
        'streamlit>=1.28.0',
        'plotly>=5.15.0', 
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'sqlite3',
        'psutil>=5.9.0',
        'requests>=2.31.0',
        'python-dotenv>=1.0.0',
        'bcrypt>=4.0.0',
        'PyJWT>=2.6.0'
    ]
    
    print("🔧 Installing NXTRIX CRM dependencies...")
    for package in required_packages:
        try:
            # Check if already installed
            package_name = package.split('>=')[0] if '>=' in package else package
            if package_name == 'sqlite3':
                continue  # Built into Python
            __import__(package_name.replace('-', '_'))
            print(f"✅ {package_name} already installed")
        except ImportError:
            print(f"📦 Installing {package_name}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def setup_environment():
    """Setup environment variables for Replit deployment"""
    os.environ['STREAMLIT_SERVER_PORT'] = '8080'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Set production environment
    os.environ['PYTHONPATH'] = '/home/runner/NXTRIX-CRM'
    
    print("🌐 Environment configured for Replit deployment")

def main():
    """Main application entry point"""
    print("🚀 Starting NXTRIX CRM - Creative Finance Deal Analyzer...")
    print("💼 Enterprise Customer Relationship Management Platform")
    
    # Setup environment first
    setup_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Verify critical file exists
    if not os.path.exists('nxtrix_saas_app.py'):
        print("❌ ERROR: nxtrix_saas_app.py not found!")
        print("Please ensure your main CRM application file is uploaded.")
        return
    
    print("✅ NXTRIX CRM files verified")
    print("🌍 Starting web server on port 8080...")
    print("🔗 Your CRM will be available at: https://nxtrix-crm.replit.app")
    
    # Run your NXTRIX CRM
    os.system("streamlit run nxtrix_saas_app.py --server.port 8080 --server.address 0.0.0.0 --server.headless true")

if __name__ == "__main__":
    main()