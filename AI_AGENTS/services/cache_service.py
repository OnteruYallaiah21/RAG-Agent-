"""
===========================================================
Project: Thryvix Email Agent
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Cache Service - Caching LLM outputs to avoid repeated calls
Handles intelligent caching with TTL and invalidation
"""

import asyncio
import json
import hashlib
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

from utils.logger import logger

class CacheEntry:
    """Cache entry with metadata"""
    def __init__(self, value: Any, ttl: int = 3600):
        self.value = value
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(seconds=ttl)
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() > self.expires_at
    
    def access(self):
        """Record access to cache entry"""
        self.access_count += 1
        self.last_accessed = datetime.now()

class CacheService:
    """Service for caching LLM outputs and other data"""
    
    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = 1000  # Maximum number of cache entries
        self.default_ttl = 3600  # Default TTL in seconds
        self.cleanup_interval = 300  # Cleanup interval in seconds
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""
        # Don't start the task during initialization
        # It will be started when the first async operation occurs
        pass
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            # Start cleanup task if not already started
            if not hasattr(self, '_cleanup_task_started') and self._cleanup_task is None:
                try:
                    self._cleanup_task = asyncio.create_task(self._cleanup_expired_entries())
                    self._cleanup_task_started = True
                except RuntimeError:
                    # No event loop running, skip cleanup task
                    pass
            
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self.cache[key]
                return None
            
            # Record access
            entry.access()
            
            logger.debug(f"Cache hit for key: {key}")
            return entry.value
            
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            # Use default TTL if not specified
            if ttl is None:
                ttl = self.default_ttl
            
            # Create cache entry
            entry = CacheEntry(value, ttl)
            
            # Check cache size limit
            if len(self.cache) >= self.max_size:
                await self._evict_oldest()
            
            # Store in cache
            self.cache[key] = entry
            
            logger.debug(f"Cached value for key: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Deleted cache entry: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            self.cache.clear()
            logger.info("Cleared all cache entries")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if key not in self.cache:
                return False
            
            entry = self.cache[key]
            if entry.is_expired():
                del self.cache[key]
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking cache existence: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            total_entries = len(self.cache)
            expired_entries = sum(1 for entry in self.cache.values() if entry.is_expired())
            active_entries = total_entries - expired_entries
            
            # Calculate average access count
            if active_entries > 0:
                avg_access = sum(entry.access_count for entry in self.cache.values() if not entry.is_expired()) / active_entries
            else:
                avg_access = 0
            
            return {
                'total_entries': total_entries,
                'active_entries': active_entries,
                'expired_entries': expired_entries,
                'max_size': self.max_size,
                'utilization': (active_entries / self.max_size) * 100,
                'average_access_count': avg_access
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    async def _evict_oldest(self):
        """Evict oldest cache entry"""
        try:
            if not self.cache:
                return
            
            # Find oldest entry by last accessed time
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].last_accessed)
            del self.cache[oldest_key]
            
            logger.debug(f"Evicted oldest cache entry: {oldest_key}")
            
        except Exception as e:
            logger.error(f"Error evicting oldest cache entry: {e}")
    
    async def _cleanup_expired_entries(self):
        """Background task to clean up expired entries"""
        try:
            while True:
                await asyncio.sleep(self.cleanup_interval)
                
                expired_keys = [
                    key for key, entry in self.cache.items() 
                    if entry.is_expired()
                ]
                
                for key in expired_keys:
                    del self.cache[key]
                
                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                
        except Exception as e:
            logger.error(f"Error in cache cleanup task: {e}")
    
    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        try:
            # Create a string representation of the arguments
            key_data = {
                'args': args,
                'kwargs': kwargs
            }
            
            # Convert to JSON string
            key_string = json.dumps(key_data, sort_keys=True)
            
            # Generate hash
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            
            return f"cache_{key_hash}"
            
        except Exception as e:
            logger.error(f"Error generating cache key: {e}")
            return f"cache_{hash(str(args) + str(kwargs))}"
    
    async def get_or_set(self, key: str, factory_func, ttl: Optional[int] = None) -> Any:
        """Get value from cache or set it using factory function"""
        try:
            # Try to get from cache
            value = await self.get(key)
            if value is not None:
                return value
            
            # Generate value using factory function
            if asyncio.iscoroutinefunction(factory_func):
                value = await factory_func()
            else:
                value = factory_func()
            
            # Cache the value
            await self.set(key, value, ttl)
            
            return value
            
        except Exception as e:
            logger.error(f"Error in get_or_set: {e}")
            # Fallback to factory function
            if asyncio.iscoroutinefunction(factory_func):
                return await factory_func()
            else:
                return factory_func()

# Global cache service instance
cache_service = CacheService()
