"""
Test script to verify all imports work correctly
This will help debug the Streamlit Cloud deployment issue
"""

import sys
print("Python version:", sys.version)
print("Available modules test:")

# Test boto3 import
try:
    import boto3
    print("✅ boto3 imported successfully")
    print(f"   boto3 version: {boto3.__version__}")
except ImportError as e:
    print(f"❌ boto3 import failed: {e}")

# Test other critical imports
try:
    import botocore
    print("✅ botocore imported successfully")
except ImportError as e:
    print(f"❌ botocore import failed: {e}")

# Test cloud_integration
try:
    from cloud_integration import CloudStorageManager
    print("✅ CloudStorageManager imported successfully")
except ImportError as e:
    print(f"❌ CloudStorageManager import failed: {e}")

# Test other optimization modules
modules_to_test = [
    'mobile_optimizer',
    'performance_optimizer', 
    'advanced_cache',
    'final_database_optimizer',
    'enhanced_security',
    'final_cache_optimizer'
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f"✅ {module} imported successfully")
    except ImportError as e:
        print(f"❌ {module} import failed: {e}")

print("\nImport test completed!")