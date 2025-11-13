"""
Performance Metrics Collection and Analysis
"""
from typing import Dict, Any
import time
from functools import wraps
from datetime import datetime
from src.cache.redis_client import get_redis_client


class MetricsCollector:
    """Collect and store performance metrics"""
    
    def __init__(self):
        try:
            self.redis = get_redis_client()
            self.enabled = True
        except:
            self.enabled = False
            print("⚠️  Redis not available, metrics disabled")
    
    def record_extraction_time(self, duration: float, pages: int):
        """Record extraction processing time"""
        if not self.enabled:
            return
        
        try:
            key = "metrics:extraction_times"
            self.redis.lpush(key, f"{duration}:{pages}")
            self.redis.ltrim(key, 0, 999)  # Keep last 1000
        except Exception as e:
            print(f"Metrics error: {e}")
    
    def record_api_call(
        self, 
        endpoint: str, 
        method: str,
        status_code: int, 
        duration: float
    ):
        """Record API call metrics"""
        if not self.enabled:
            return
        
        try:
            key = f"metrics:api:{endpoint}:{method}"
            
            # Increment counters
            self.redis.hincrby(key, "total_calls", 1)
            self.redis.hincrby(key, f"status_{status_code}", 1)
            self.redis.hincrbyfloat(key, "total_duration", duration)
            
            # Set expiry (24 hours)
            self.redis.expire(key, 86400)
        except Exception as e:
            print(f"Metrics error: {e}")
    
    def record_error(self, error_type: str, message: str):
        """Record error occurrence"""
        if not self.enabled:
            return
        
        try:
            key = "metrics:errors"
            error_data = f"{error_type}:{message}:{datetime.utcnow().isoformat()}"
            self.redis.lpush(key, error_data)
            self.redis.ltrim(key, 0, 499)  # Keep last 500
        except Exception as e:
            print(f"Metrics error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics"""
        if not self.enabled:
            return {"error": "Metrics not available"}
        
        try:
            stats = {}
            
            # Extraction times
            extraction_times = self.redis.lrange("metrics:extraction_times", 0, -1)
            
            if extraction_times:
                times = []
                pages = []
                
                for entry in extraction_times:
                    if isinstance(entry, bytes):
                        entry = entry.decode()
                    
                    parts = entry.split(':')
                    if len(parts) == 2:
                        times.append(float(parts[0]))
                        pages.append(int(parts[1]))
                
                stats["total_extractions"] = len(times)
                stats["average_extraction_time"] = sum(times) / len(times) if times else 0
                stats["min_extraction_time"] = min(times) if times else 0
                stats["max_extraction_time"] = max(times) if times else 0
                stats["average_pages"] = sum(pages) / len(pages) if pages else 0
            else:
                stats["total_extractions"] = 0
                stats["average_extraction_time"] = 0
            
            # API calls
            api_keys = self.redis.keys("metrics:api:*")
            total_api_calls = 0
            
            for key in api_keys:
                if isinstance(key, bytes):
                    key = key.decode()
                
                calls = self.redis.hget(key, "total_calls")
                if calls:
                    total_api_calls += int(calls)
            
            stats["total_api_calls"] = total_api_calls
            
            # Errors
            errors = self.redis.lrange("metrics:errors", 0, -1)
            stats["total_errors"] = len(errors)
            
            return stats
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_api_stats(self, endpoint: str, method: str) -> Dict[str, Any]:
        """Get statistics for specific API endpoint"""
        if not self.enabled:
            return {}
        
        try:
            key = f"metrics:api:{endpoint}:{method}"
            
            if not self.redis.exists(key):
                return {}
            
            data = self.redis.hgetall(key)
            
            # Decode bytes keys
            decoded = {}
            for k, v in data.items():
                if isinstance(k, bytes):
                    k = k.decode()
                if isinstance(v, bytes):
                    v = v.decode()
                decoded[k] = v
            
            # Calculate average
            total_calls = int(decoded.get("total_calls", 0))
            total_duration = float(decoded.get("total_duration", 0))
            
            decoded["average_duration"] = (
                total_duration / total_calls if total_calls > 0 else 0
            )
            
            return decoded
        
        except Exception as e:
            return {"error": str(e)}
    
    def clear_metrics(self):
        """Clear all metrics"""
        if not self.enabled:
            return False
        
        try:
            # Clear extraction times
            self.redis.delete("metrics:extraction_times")
            
            # Clear API metrics
            api_keys = self.redis.keys("metrics:api:*")
            if api_keys:
                self.redis.delete(*api_keys)
            
            # Clear errors
            self.redis.delete("metrics:errors")
            
            return True
        except Exception as e:
            print(f"Clear metrics error: {e}")
            return False


def track_time(metric_name: str = "function_call"):
    """
    Decorator to track function execution time
    
    Usage:
        @track_time("extract_document")
        async def extract_document(doc_id):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs)
            duration = time.time() - start
            
            collector = MetricsCollector()
            collector.record_extraction_time(duration, 1)
            
            print(f"⏱️  {metric_name} took {duration:.2f}s")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            
            collector = MetricsCollector()
            collector.record_extraction_time(duration, 1)
            
            print(f"⏱️  {metric_name} took {duration:.2f}s")
            
            return result
        
        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class PerformanceMonitor:
    """Context manager for performance monitoring"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.collector = MetricsCollector()
    
    def __enter__(self):
        self.start_time = time.time()
        print(f"▶️  Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            print(f"✓ Completed: {self.operation_name} in {duration:.2f}s")
            self.collector.record_extraction_time(duration, 1)
        else:
            print(f"❌ Failed: {self.operation_name} after {duration:.2f}s")
            self.collector.record_error(
                error_type=exc_type.__name__,
                message=str(exc_val)
            )
        
        return False