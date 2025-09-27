#!/usr/bin/env python3
"""
Test script to verify all optimization modules import correctly
"""

import sys
from datetime import datetime

def test_imports():
    print(f"🧪 Testing Optimization Module Imports - {datetime.now()}")
    print("=" * 60)
    
    modules_to_test = [
        ("Performance Optimizer", "performance_optimizer", "PerformanceOptimizer"),
        ("Advanced Cache", "advanced_cache", "AdvancedCacheManager"),
        ("Enhanced Security", "enhanced_security", "EnhancedSecurityManager"),
        ("Advanced Analytics", "advanced_analytics", "AdvancedAnalyticsEngine"),
        ("Mobile Optimizer", "mobile_optimizer", "MobileOptimizer"),
        ("Cloud Integration", "cloud_integration", "CloudStorageManager"),
        ("Integration Hub", "integration_hub", "NXTRIXIntegrationHub")
    ]
    
    results = []
    
    for name, module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {name}: PASSED")
            results.append((name, True, None))
        except Exception as e:
            print(f"❌ {name}: FAILED - {str(e)}")
            results.append((name, False, str(e)))
    
    print("\n" + "=" * 60)
    print("📊 Import Test Summary:")
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All optimization modules imported successfully!")
        print("🚀 Ready for 100% efficiency implementation!")
    else:
        print("\n⚠️  Some modules failed to import. Issues to resolve:")
        for name, success, error in results:
            if not success:
                print(f"   • {name}: {error}")
    
    return passed, total

if __name__ == "__main__":
    passed, total = test_imports()
    sys.exit(0 if passed == total else 1)