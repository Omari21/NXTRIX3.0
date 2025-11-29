# -*- coding: utf-8 -*-
"""
Performance Optimizer for NXTRIX CRM
System performance monitoring and optimization
"""

import streamlit as st
import time
import psutil
import gc
from typing import Dict, Any, Optional
from datetime import datetime
import threading
import queue

class PerformanceOptimizer:
    """Performance optimization and monitoring system"""
    
    def __init__(self):
        self.metrics_history = []
        self.optimization_enabled = True
        self.cache_size_limit = 100  # MB
        
    def monitor_performance(self) -> Dict[str, Any]:
        """Monitor current system performance"""
        try:
            # Get CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Streamlit specific metrics
            session_count = len(st.session_state) if hasattr(st, 'session_state') else 0
            
            metrics = {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available': memory.available / (1024**3),  # GB
                'session_state_size': session_count,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store metrics history (keep last 100 entries)
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 100:
                self.metrics_history.pop(0)
            
            return metrics
            
        except Exception as e:
            return {
                'cpu_usage': 0,
                'memory_usage': 0,
                'memory_available': 0,
                'session_state_size': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def optimize_memory(self) -> Dict[str, Any]:
        """Optimize memory usage"""
        try:
            initial_memory = psutil.virtual_memory().percent
            
            # Clear unused session state items
            if hasattr(st, 'session_state'):
                self._cleanup_session_state()
            
            # Force garbage collection
            collected = gc.collect()
            
            final_memory = psutil.virtual_memory().percent
            memory_freed = initial_memory - final_memory
            
            return {
                'memory_freed_percent': memory_freed,
                'objects_collected': collected,
                'initial_memory': initial_memory,
                'final_memory': final_memory,
                'optimization_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'memory_freed_percent': 0,
                'objects_collected': 0,
                'error': str(e),
                'optimization_time': datetime.now().isoformat()
            }
    
    def optimize_cache(self) -> Dict[str, Any]:
        """Optimize Streamlit cache"""
        try:
            # Clear Streamlit cache if available
            if hasattr(st, 'cache_data'):
                st.cache_data.clear()
            if hasattr(st, 'cache_resource'):
                st.cache_resource.clear()
            
            return {
                'cache_cleared': True,
                'cache_clear_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'cache_cleared': False,
                'error': str(e),
                'cache_clear_time': datetime.now().isoformat()
            }
    
    def get_performance_recommendations(self) -> list:
        """Get performance optimization recommendations"""
        recommendations = []
        
        try:
            current_metrics = self.monitor_performance()
            
            if current_metrics['cpu_usage'] > 80:
                recommendations.append("High CPU usage detected. Consider reducing complex calculations.")
            
            if current_metrics['memory_usage'] > 85:
                recommendations.append("High memory usage. Consider clearing cache or optimizing data structures.")
            
            if current_metrics['session_state_size'] > 50:
                recommendations.append("Large session state detected. Consider cleanup of unused variables.")
            
            if len(self.metrics_history) > 10:
                avg_cpu = sum(m['cpu_usage'] for m in self.metrics_history[-10:]) / 10
                if avg_cpu > 70:
                    recommendations.append("Consistently high CPU usage. Consider performance optimization.")
            
            if not recommendations:
                recommendations.append("System performance is optimal.")
            
        except Exception as e:
            recommendations.append(f"Performance analysis error: {str(e)}")
        
        return recommendations
    
    def auto_optimize(self) -> Dict[str, Any]:
        """Automatically optimize system performance"""
        try:
            results = {}
            
            # Memory optimization
            memory_result = self.optimize_memory()
            results['memory_optimization'] = memory_result
            
            # Cache optimization
            cache_result = self.optimize_cache()
            results['cache_optimization'] = cache_result
            
            # Performance monitoring
            metrics = self.monitor_performance()
            results['current_metrics'] = metrics
            
            results['auto_optimization_time'] = datetime.now().isoformat()
            results['success'] = True
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'auto_optimization_time': datetime.now().isoformat()
            }
    
    def _cleanup_session_state(self):
        """Clean up unnecessary session state items"""
        try:
            if not hasattr(st, 'session_state'):
                return
            
            # List of keys that can be safely cleaned up
            cleanup_keys = []
            
            for key in st.session_state:
                # Clean up temporary or large objects
                if key.startswith('temp_') or key.startswith('cache_'):
                    cleanup_keys.append(key)
                elif isinstance(st.session_state[key], (dict, list)) and len(str(st.session_state[key])) > 10000:
                    # Large objects that might be taking up memory
                    cleanup_keys.append(key)
            
            # Remove identified keys
            for key in cleanup_keys:
                if key in st.session_state:
                    del st.session_state[key]
                    
        except Exception:
            pass  # Silent cleanup failure
    
    def display_performance_dashboard(self):
        """Display performance monitoring dashboard"""
        try:
            st.subheader("🚀 Performance Monitor")
            
            # Current metrics
            metrics = self.monitor_performance()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "CPU Usage",
                    f"{metrics['cpu_usage']:.1f}%",
                    delta=None
                )
            
            with col2:
                st.metric(
                    "Memory Usage",
                    f"{metrics['memory_usage']:.1f}%",
                    delta=None
                )
            
            with col3:
                st.metric(
                    "Available Memory",
                    f"{metrics['memory_available']:.1f} GB",
                    delta=None
                )
            
            with col4:
                st.metric(
                    "Session State Size",
                    f"{metrics['session_state_size']} items",
                    delta=None
                )
            
            # Optimization controls
            st.subheader("Optimization Controls")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🧹 Clear Memory"):
                    result = self.optimize_memory()
                    if result.get('memory_freed_percent', 0) > 0:
                        st.success(f"Freed {result['memory_freed_percent']:.1f}% memory")
                    else:
                        st.info("Memory optimization completed")
            
            with col2:
                if st.button("🗂️ Clear Cache"):
                    result = self.optimize_cache()
                    if result.get('cache_cleared'):
                        st.success("Cache cleared successfully")
                    else:
                        st.warning("Cache clear failed")
            
            with col3:
                if st.button("⚡ Auto Optimize"):
                    result = self.auto_optimize()
                    if result.get('success'):
                        st.success("Auto optimization completed")
                    else:
                        st.error("Auto optimization failed")
            
            # Recommendations
            st.subheader("Performance Recommendations")
            recommendations = self.get_performance_recommendations()
            
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
            
            # Performance history chart (if metrics available)
            if len(self.metrics_history) > 1:
                st.subheader("Performance History")
                
                import plotly.graph_objects as go
                
                timestamps = [m['timestamp'] for m in self.metrics_history[-20:]]  # Last 20 entries
                cpu_data = [m['cpu_usage'] for m in self.metrics_history[-20:]]
                memory_data = [m['memory_usage'] for m in self.metrics_history[-20:]]
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=cpu_data,
                    mode='lines+markers',
                    name='CPU Usage (%)',
                    line=dict(color='#ff7f0e')
                ))
                
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=memory_data,
                    mode='lines+markers',
                    name='Memory Usage (%)',
                    line=dict(color='#1f77b4')
                ))
                
                fig.update_layout(
                    title='System Performance Over Time',
                    xaxis_title='Time',
                    yaxis_title='Usage (%)',
                    hovermode='x unified',
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Performance dashboard error: {str(e)}")

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get performance optimizer instance"""
    if 'performance_optimizer' not in st.session_state:
        st.session_state.performance_optimizer = PerformanceOptimizer()
    return st.session_state.performance_optimizer