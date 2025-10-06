#!/usr/bin/env python3
"""
Fix the AI module import issue in streamlit_app.py
"""

def fix_ai_import():
    # Read the file
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the problematic import line
    old_import = 'from ai_prediction_engine import AIMarketPredictor, get_ai_predictor, create_prediction_visualizations'
    
    # Define the new import with error handling
    new_import = '''# Optional AI module import with error handling
try:
    from ai_prediction_engine import AIMarketPredictor, get_ai_predictor, create_prediction_visualizations
    AI_MODULE_AVAILABLE = True
except ImportError:
    AI_MODULE_AVAILABLE = False
    # Create placeholder functions when module is not available
    class AIMarketPredictor:
        def __init__(self, *args, **kwargs):
            pass
        def predict(self, *args, **kwargs):
            return {"error": "AI module not available"}
    
    def get_ai_predictor(*args, **kwargs):
        return AIMarketPredictor()
    
    def create_prediction_visualizations(*args, **kwargs):
        return None'''
    
    # Check if the import exists
    if old_import in content:
        print("Found problematic import, fixing...")
        content = content.replace(old_import, new_import)
        
        # Write back
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed AI module import with error handling")
        return True
    else:
        print("❌ Could not find the problematic import line")
        return False

if __name__ == "__main__":
    fix_ai_import()