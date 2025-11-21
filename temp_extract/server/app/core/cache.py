import redis
import json
import pickle
from typing import Any, Optional, Union
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache manager"""
    
    def __init__(self):
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=False  # We'll handle encoding ourselves
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        return self.redis_client is not None
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set a value in cache"""
        if not self.is_available():
            return False
        
        try:
            # Serialize the value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = pickle.dumps(value)
            
            self.redis_client.setex(key, expire, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        if not self.is_available():
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # Try JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        if not self.is_available():
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.is_available():
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    def flush_all(self) -> bool:
        """Clear all cache"""
        if not self.is_available():
            return False
        
        try:
            self.redis_client.flushall()
            return True
        except Exception as e:
            logger.error(f"Cache flush error: {e}")
            return False
    
    def get_keys(self, pattern: str = "*") -> list:
        """Get all keys matching pattern"""
        if not self.is_available():
            return []
        
        try:
            keys = self.redis_client.keys(pattern)
            return [key.decode() if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
            logger.error(f"Cache get_keys error: {e}")
            return []


# Global cache instance
cache = RedisCache()


def cache_key(*args) -> str:
    """Generate cache key from arguments"""
    return ":".join(str(arg) for arg in args)


def cached(expire: int = 3600):
    """Decorator for caching function results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = cache_key(func.__name__, *args, *sorted(kwargs.items()))
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, expire)
            return result
        
        return wrapper
    return decorator