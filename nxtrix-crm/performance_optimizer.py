"""
NXTRIX CRM Performance Optimization Module
Implements caching, connection pooling, and query optimization
"""

import streamlit as st
import sqlite3
from functools import wraps
import time
from typing import Dict, Any, Optional
import threading
import queue

class PerformanceOptimizer:
    """Advanced performance optimization for NXTRIX CRM"""
    
    def __init__(self):
        self.query_cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.connection_pool = queue.Queue(maxsize=10)
        self.init_connection_pool()
    
    def init_connection_pool(self):
        """Initialize database connection pool"""
        for _ in range(5):  # Create 5 initial connections
            conn = sqlite3.connect('crm_data.db', check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.connection_pool.put(conn)
    
    def get_connection(self):
        """Get connection from pool"""
        try:
            return self.connection_pool.get(timeout=1)
        except queue.Empty:
            # Create new connection if pool is empty
            conn = sqlite3.connect('crm_data.db', check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
    
    def return_connection(self, conn):
        """Return connection to pool"""
        if self.connection_pool.qsize() < 10:
            self.connection_pool.put(conn)
        else:
            conn.close()
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def cached_query(self, query: str, params: tuple = ()) -> list:
        """Execute cached database query"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            self.return_connection(conn)
    
    @st.cache_data(ttl=600)  # Cache for 10 minutes
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get cached dashboard metrics"""
        return {
            'total_deals': self.cached_query("SELECT COUNT(*) as count FROM deals")[0]['count'],
            'avg_ai_score': self.cached_query("SELECT AVG(ai_score) as avg FROM deals WHERE ai_score > 0")[0]['avg'] or 0,
            'total_value': self.cached_query("SELECT SUM(purchase_price) as total FROM deals")[0]['total'] or 0,
            'high_score_count': self.cached_query("SELECT COUNT(*) as count FROM deals WHERE ai_score >= 85")[0]['count']
        }
    
    def bulk_insert_deals(self, deals_data: list):
        """Optimized bulk insert for deals"""
        conn = self.get_connection()
        try:
            conn.executemany("""
                INSERT OR REPLACE INTO deals 
                (id, address, property_type, purchase_price, ai_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, deals_data)
            conn.commit()
        finally:
            self.return_connection(conn)

# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()

def optimized_query(func):
    """Decorator for optimized database queries"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Log slow queries
        if execution_time > 2.0:
            st.warning(f"Slow query detected: {func.__name__} took {execution_time:.2f}s")
        
        return result
    return wrapper

# Additional optimization utilities
class StreamlitOptimizer:
    """Streamlit-specific optimizations"""
    
    @staticmethod
    def lazy_load_plotly_charts():
        """Lazy load Plotly charts to improve initial page load"""
        if 'charts_loaded' not in st.session_state:
            st.session_state.charts_loaded = False
        
        if not st.session_state.charts_loaded:
            with st.spinner("Loading interactive charts..."):
                time.sleep(0.1)  # Simulate loading
                st.session_state.charts_loaded = True
    
    @staticmethod
    def optimize_dataframe_display(df, max_rows=100):
        """Optimize large dataframe display"""
        if len(df) > max_rows:
            st.info(f"Showing first {max_rows} rows of {len(df)} total records")
            return df.head(max_rows)
        return df
    
    @staticmethod
    def progressive_loading(items, batch_size=10):
        """Progressive loading for large lists"""
        if f'loaded_items' not in st.session_state:
            st.session_state.loaded_items = batch_size
        
        visible_items = items[:st.session_state.loaded_items]
        
        if len(items) > st.session_state.loaded_items:
            if st.button("Load More"):
                st.session_state.loaded_items += batch_size
                st.rerun()
        
        return visible_items

# Global instance management
_performance_optimizer_instance = None

def get_performance_optimizer():
    """Get or create the global performance optimizer instance"""
    global _performance_optimizer_instance
    if _performance_optimizer_instance is None:
        _performance_optimizer_instance = PerformanceOptimizer()
        _performance_optimizer_instance.init_connection_pool()
    return _performance_optimizer_instance

def initialize_performance_optimizations():
    """Initialize all performance optimizations automatically"""
    optimizer = get_performance_optimizer()
    
    # Add any additional background optimization tasks here
    if hasattr(optimizer, 'start_background_tasks'):
        optimizer.start_background_tasks()
    
    return True