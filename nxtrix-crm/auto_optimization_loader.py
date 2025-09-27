"""
Auto-Optimization Loader
Automatically applies all optimizations on application startup
No manual activation required - optimizations run permanently in background
"""

import streamlit as st
from typing import Dict, Any
import time
from datetime import datetime

class AutoOptimizationLoader:
    """Automatically loads and applies all optimizations on startup"""
    
    @staticmethod
    def initialize_all_optimizations():
        """Initialize all optimization modules automatically"""
        optimization_status = {
            'mobile_optimizer': False,
            'performance_optimizer': False, 
            'cache_manager': False,
            'database_optimizer': False,
            'security_manager': False,
            'final_optimizations': False
        }
        
        try:
            # 1. Mobile Optimizations (Always Active)
            from mobile_optimizer import apply_mobile_optimizations
            apply_mobile_optimizations()
            optimization_status['mobile_optimizer'] = True
            
        except ImportError:
            pass
            
        try:
            # 2. Performance Optimizer (Auto-Enable)
            from performance_optimizer import get_performance_optimizer, initialize_performance_optimizations
            optimizer = get_performance_optimizer()
            if optimizer:
                initialize_performance_optimizations()
                optimization_status['performance_optimizer'] = True
                
        except (ImportError, AttributeError):
            pass
            
        try:
            # 3. Advanced Cache Manager (Auto-Enable)
            from advanced_cache import get_cache_manager
            cache_manager = get_cache_manager()
            if cache_manager:
                # Cache manager is now active
                optimization_status['cache_manager'] = True
                
        except (ImportError, AttributeError):
            pass
            
        try:
            # 4. Database Optimizer (Auto-Enable Connection Pooling)
            from final_database_optimizer import EnhancedConnectionPool
            # Initialize connection pool automatically
            if 'db_pool' not in st.session_state:
                st.session_state.db_pool = EnhancedConnectionPool("crm_data.db")
                optimization_status['database_optimizer'] = True
                
        except ImportError:
            pass
            
        try:
            # 5. Enhanced Security (Always Active)
            from enhanced_security import get_security_manager
            security_manager = get_security_manager()
            if security_manager:
                # Security manager is now active
                optimization_status['security_manager'] = True
                
        except (ImportError, AttributeError):
            pass
            
        try:
            # 6. Final Cache Optimizer (Auto-Enable)
            from final_cache_optimizer import PredictiveCacheWarmer
            from advanced_cache import get_cache_manager
            if 'cache_warmer' not in st.session_state:
                cache_manager = get_cache_manager()
                st.session_state.cache_warmer = PredictiveCacheWarmer(cache_manager)
                if hasattr(st.session_state.cache_warmer, 'start_background_warming'):
                    st.session_state.cache_warmer.start_background_warming()
                optimization_status['final_optimizations'] = True
                
        except (ImportError, Exception):
            pass
        
        # Store optimization status
        st.session_state.auto_optimizations_enabled = optimization_status
        st.session_state.optimization_initialized_at = datetime.now()
        
        return optimization_status
    
    @staticmethod
    def get_optimization_status() -> Dict[str, Any]:
        """Get current optimization status"""
        if 'auto_optimizations_enabled' not in st.session_state:
            return AutoOptimizationLoader.initialize_all_optimizations()
        
        return st.session_state.auto_optimizations_enabled
    
    @staticmethod
    def show_optimization_status():
        """Show a brief optimization status (admin only)"""
        if not st.session_state.get('is_admin', False):
            return
            
        status = AutoOptimizationLoader.get_optimization_status()
        enabled_count = sum(status.values())
        total_count = len(status)
        
        if enabled_count == total_count:
            st.success(f"🚀 All {total_count} optimization modules active")
        else:
            st.info(f"⚡ {enabled_count}/{total_count} optimization modules active")

# Optimizations will be initialized when Streamlit session starts
# This prevents initialization during module import