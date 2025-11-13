#cache/redis_client.py
"""
Redis Client Configuration and Cache Management
"""
import redis
from typing import Optional, Any
import json
import pickle
from functools import wraps
from src.settings import APP_SETTINGS
import hashlib

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Get Redis client singleton"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            APP_SETTINGS.REDIS_URL,
            decode_responses=False  # For pickle support
        )
    return _redis_client


class CacheManager:
    """Manage caching operations with various strategies"""
    
    def __init__(self):
        self.redis = get_redis_client()
        self.default_ttl = 3600  # 1 hour
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set cache value
        
        Args:
            key: Cache key
            value: Value to cache (will be pickled)
            ttl: Time to live in seconds
        """
        try:
            serialized = pickle.dumps(value)
            ttl = ttl or self.default_ttl
            self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cache value
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        try:
            data = self.redis.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete cache key"""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.redis.exists(key) > 0
    
    def cache_extraction(self, key: str, data: dict, ttl: int = 3600):
        """Cache extraction result as JSON"""
        try:
            self.redis.setex(key, ttl, json.dumps(data))
            return True
        except Exception as e:
            print(f"Cache extraction error: {e}")
            return False
    @staticmethod
    def get_file_hash(file_bytes: bytes) -> str:
        """Tạo hash MD5 của file PDF để dùng làm cache key"""
        return hashlib.md5(file_bytes).hexdigest()
    
    def get_cached_extraction(self, key: str) -> Optional[dict]:
        """Get cached extraction result"""
        try:
            data = self.redis.get(key)
            if data:
                # Handle both bytes and string
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Get cached extraction error: {e}")
            return None
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache keys matching pattern
        
        Args:
            pattern: Redis key pattern (e.g., 'extraction:*')
            
        Returns:
            Number of keys deleted
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            print(f"Invalidate pattern error: {e}")
            return 0
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        return self.redis.incrby(key, amount)
    
    def get_ttl(self, key: str) -> int:
        """Get remaining TTL for key"""
        return self.redis.ttl(key)
    
    def set_hash(self, key: str, field: str, value: Any):
        """Set hash field"""
        self.redis.hset(key, field, pickle.dumps(value))
    
    def get_hash(self, key: str, field: str) -> Optional[Any]:
        """Get hash field"""
        data = self.redis.hget(key, field)
        return pickle.loads(data) if data else None
    
    def get_all_hash(self, key: str) -> dict:
        """Get all hash fields"""
        data = self.redis.hgetall(key)
        return {
            k.decode(): pickle.loads(v) 
            for k, v in data.items()
        }


def cache_result(key_prefix: str, ttl: int = 3600):
    """
    Decorator to cache function results
    
    Usage:
        @cache_result("extraction", ttl=1800)
        async def extract_document(doc_id):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{args}:{kwargs}"
            
            cache = CacheManager()
            
            # Check cache
            cached = cache.get(cache_key)
            if cached is not None:
                print(f"Cache hit: {cache_key}")
                return cached
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

