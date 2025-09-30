"""
Advanced Caching System for NXTRIX CRM
Implements multi-level caching with intelligent invalidation
"""

import streamlit as st
import pickle
import hashlib
import os
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
import sqlite3

class AdvancedCacheManager:
    """Multi-level caching system"""
    
    def __init__(self, cache_dir="./cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.memory_cache = {}
        self.cache_stats = {'hits': 0, 'misses': 0}
    
    def _get_cache_key(self, key: str, params: dict = None) -> str:
        """Generate cache key"""
        if params:
            key += str(sorted(params.items()))
        return hashlib.md5(key.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_file: str, ttl: int) -> bool:
        """Check if cache file is still valid"""
        if not os.path.exists(cache_file):
            return False
        
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        return datetime.now() - file_time < timedelta(seconds=ttl)
    
    def get(self, key: str, params: dict = None, ttl: int = 300) -> Optional[Any]:
        """Get cached value"""
        cache_key = self._get_cache_key(key, params)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            self.cache_stats['hits'] += 1
            return self.memory_cache[cache_key]
        
        # Check disk cache
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        if self._is_cache_valid(cache_file, ttl):
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    self.memory_cache[cache_key] = data  # Promote to memory cache
                    self.cache_stats['hits'] += 1
                    return data
            except Exception:
                pass
        
        self.cache_stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any, params: dict = None, ttl: int = 300):
        """Set cached value"""
        cache_key = self._get_cache_key(key, params)
        
        # Store in memory cache
        self.memory_cache[cache_key] = value
        
        # Store in disk cache
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            st.warning(f"Failed to write cache: {e}")
    
    def invalidate(self, pattern: str = None):
        """Invalidate cache entries"""
        if pattern is None:
            # Clear all cache
            self.memory_cache.clear()
            for file in os.listdir(self.cache_dir):
                if file.endswith('.pkl'):
                    os.remove(os.path.join(self.cache_dir, file))
        else:
            # Clear matching entries
            pattern_hash = hashlib.md5(pattern.encode()).hexdigest()[:8]
            keys_to_remove = [k for k in self.memory_cache.keys() if pattern_hash in k]
            for key in keys_to_remove:
                del self.memory_cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = self.cache_stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'hit_rate': hit_rate,
            'total_hits': self.cache_stats['hits'],
            'total_misses': self.cache_stats['misses'],
            'memory_entries': len(self.memory_cache),
            'disk_entries': len([f for f in os.listdir(self.cache_dir) if f.endswith('.pkl')])
        }

# Global cache manager
cache_manager = AdvancedCacheManager()

# Streamlit integration
def st_cached_function(ttl=300, key_prefix=""):
    """Enhanced Streamlit cache decorator"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{key_prefix}{func.__name__}"
            params = {'args': str(args), 'kwargs': str(kwargs)}
            
            # Try to get from cache
            result = cache_manager.get(cache_key, params, ttl)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, params, ttl)
            return result
        
        return wrapper
    return decorator

# Cache warming functions
class CacheWarmer:
    """Pre-load frequently accessed data"""
    
    @staticmethod
    def warm_dashboard_cache():
        """Pre-warm dashboard data"""
        from performance_optimizer import performance_optimizer
        
        # Pre-load dashboard metrics
        performance_optimizer.get_dashboard_metrics()
        
        # Pre-load recent deals
        performance_optimizer.cached_query("""
            SELECT * FROM deals 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
    
    @staticmethod
    def warm_analytics_cache():
        """Pre-warm analytics data"""
        queries = [
            "SELECT property_type, COUNT(*) as count FROM deals GROUP BY property_type",
            "SELECT AVG(ai_score) as avg_score FROM deals WHERE created_at >= date('now', '-30 days')",
            "SELECT SUM(purchase_price) as total_value FROM deals"
        ]
        
        for query in queries:
            cache_manager.get(f"analytics_{hashlib.md5(query.encode()).hexdigest()}")

# Cache monitoring in Streamlit
def show_cache_stats():
    """Display cache statistics in admin panel"""
    if st.session_state.get('user_role') == 'admin':
        with st.expander("🔧 Cache Statistics"):
            stats = cache_manager.get_stats()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Hit Rate", f"{stats['hit_rate']:.1%}")
            with col2:
                st.metric("Memory Entries", stats['memory_entries'])
            with col3:
                st.metric("Disk Entries", stats['disk_entries'])
            
            if st.button("Clear Cache"):
                cache_manager.invalidate()
                st.success("Cache cleared!")
                st.rerun()

# Global instance management
_cache_manager_instance = None

def get_cache_manager():
    """Get or create the global cache manager instance"""
    global _cache_manager_instance
    if _cache_manager_instance is None:
        _cache_manager_instance = AdvancedCacheManager()
    return _cache_manager_instance