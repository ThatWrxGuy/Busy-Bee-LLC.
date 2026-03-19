"""
Signal Cache

In-memory cache for signals with TTL support and size limits.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import threading
import time


@dataclass
class CacheEntry:
    """A cached signal entry"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.ttl_seconds is None:
            return False
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds


class SignalCache:
    """
    In-memory cache for signals.
    
    Features:
    - TTL (time-to-live) support
    - Size limits
    - Thread-safe operations
    - Access statistics
    """
    
    def __init__(
        self,
        max_size: int = 10000,
        default_ttl: int = 3600,  # 1 hour
        cleanup_interval: int = 300  # 5 minutes
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._last_cleanup = time.time()
        self._hits = 0
        self._misses = 0
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        with self._lock:
            # Cleanup if needed
            self._maybe_cleanup()
            
            # Enforce size limit
            if len(self._cache) >= self.max_size:
                self._evict_oldest()
            
            now = datetime.now()
            self._cache[key] = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                last_accessed=now,
                ttl_seconds=ttl or self.default_ttl
            )
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._misses += 1
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return None
            
            # Update access stats
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self._hits += 1
            
            return entry.value
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cached data"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "default_ttl": self.default_ttl
            }
    
    def _maybe_cleanup(self) -> None:
        """Run cleanup if interval has passed"""
        now = time.time()
        if now - self._last_cleanup > self.cleanup_interval:
            self._cleanup_expired()
            self._last_cleanup = now
    
    def _cleanup_expired(self) -> None:
        """Remove all expired entries"""
        expired = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        for key in expired:
            del self._cache[key]
    
    def _evict_oldest(self) -> None:
        """Evict the oldest entry"""
        if not self._cache:
            return
        
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed
        )
        del self._cache[oldest_key]
    
    def get_all(self) -> List[Any]:
        """Get all cached values"""
        with self._lock:
            # Cleanup first
            self._cleanup_expired()
            return [entry.value for entry in self._cache.values()]
    
    def get_by_prefix(self, prefix: str) -> List[Any]:
        """Get all cached values with keys starting with prefix"""
        with self._lock:
            self._cleanup_expired()
            return [
                entry.value
                for key, entry in self._cache.items()
                if key.startswith(prefix)
            ]
    
    def keys(self) -> List[str]:
        """Get all cache keys"""
        with self._lock:
            return list(self._cache.keys())


# Global cache instance
_global_cache: Optional[SignalCache] = None


def get_signal_cache() -> SignalCache:
    """Get the global signal cache"""
    global _global_cache
    if _global_cache is None:
        _global_cache = SignalCache()
    return _global_cache


__all__ = [
    "SignalCache",
    "CacheEntry",
    "get_signal_cache",
]
