"""
CacheManager: Optimizes rule resolution performance.
"""

import logging
import time
from typing import Any, Dict, Optional, List, Tuple
from collections import OrderedDict
import json
import hashlib

logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        Initialize cache manager with LRU eviction and TTL.

        Args:
            max_size: Maximum number of items in cache
            ttl: Time to live for cache entries in seconds
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, float] = {}
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            self.miss_count += 1
            return None

        # Check if expired
        if self._is_expired(key):
            self._remove(key)
            self.miss_count += 1
            return None

        # Move to end (most recently used)
        self.cache.move_to_end(key)
        self.hit_count += 1
        return self.cache[key]

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        current_time = time.time()

        # Update existing key
        if key in self.cache:
            self.cache[key] = value
            self.timestamps[key] = current_time
            self.cache.move_to_end(key)
            return

        # Add new key
        self.cache[key] = value
        self.timestamps[key] = current_time

        # Evict if over max size
        if len(self.cache) > self.max_size:
            self._evict_lru()

    def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False if not found
        """
        if key in self.cache:
            self._remove(key)
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.timestamps.clear()
        self.hit_count = 0
        self.miss_count = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'expired_keys': len([k for k in self.cache.keys() if self._is_expired(k)])
        }

    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.

        Returns:
            Number of expired entries removed
        """
        expired_keys = [key for key in self.cache.keys() if self._is_expired(key)]
        for key in expired_keys:
            self._remove(key)
        return len(expired_keys)

    def get_cache_key(self, rule_type: str, rule_id: int, context: Dict[str, Any] = None) -> str:
        """
        Generate a consistent cache key for rule resolution.

        Args:
            rule_type: Type of rule ('task', 'semantic', 'primitive')
            rule_id: ID of the rule
            context: Context dictionary

        Returns:
            Cache key string
        """
        if context is None:
            context = {}

        # Create a hash of the context for consistent keys
        context_str = json.dumps(context, sort_keys=True)
        context_hash = hashlib.md5(context_str.encode()).hexdigest()[:8]

        return f"{rule_type}_{rule_id}_{context_hash}"

    def invalidate_rule_cache(self, rule_type: str, rule_id: int) -> int:
        """
        Invalidate all cache entries related to a specific rule.

        Args:
            rule_type: Type of rule ('task', 'semantic', 'primitive')
            rule_id: ID of the rule

        Returns:
            Number of cache entries invalidated
        """
        prefix = f"{rule_type}_{rule_id}_"
        invalidated_keys = [key for key in self.cache.keys() if key.startswith(prefix)]

        for key in invalidated_keys:
            self._remove(key)

        return len(invalidated_keys)

    def warm_cache(self, rule_resolutions: List[Tuple[str, int, Dict[str, Any], Any]]) -> None:
        """
        Pre-populate cache with rule resolutions.

        Args:
            rule_resolutions: List of (rule_type, rule_id, context, result) tuples
        """
        for rule_type, rule_id, context, result in rule_resolutions:
            cache_key = self.get_cache_key(rule_type, rule_id, context)
            self.set(cache_key, result)

    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired."""
        if key not in self.timestamps:
            return True

        return time.time() - self.timestamps[key] > self.ttl

    def _remove(self, key: str) -> None:
        """Remove key from cache and timestamps."""
        if key in self.cache:
            del self.cache[key]
        if key in self.timestamps:
            del self.timestamps[key]

    def _evict_lru(self) -> None:
        """Evict least recently used item."""
        if self.cache:
            # Remove oldest item (first in OrderedDict)
            oldest_key = next(iter(self.cache))
            self._remove(oldest_key)


class MemoryEfficientCache:
    """
    A more memory-efficient cache implementation for large-scale deployments.
    """

    def __init__(self, max_memory_mb: int = 100):
        """
        Initialize memory-efficient cache.

        Args:
            max_memory_mb: Maximum memory usage in MB
        """
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: Dict[str, Any] = {}
        self.access_times: Dict[str, float] = {}
        self.memory_usage = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self.cache:
            return None

        self.access_times[key] = time.time()
        return self.cache[key]

    def set(self, key: str, value: Any) -> None:
        """Set value in cache with memory management."""
        # Estimate memory usage
        value_size = self._estimate_size(value)

        # Remove old entry if updating
        if key in self.cache:
            old_size = self._estimate_size(self.cache[key])
            self.memory_usage -= old_size

        # Check if we need to evict
        while self.memory_usage + value_size > self.max_memory_bytes and self.cache:
            self._evict_lru()

        # Store new value
        self.cache[key] = value
        self.access_times[key] = time.time()
        self.memory_usage += value_size

    def _estimate_size(self, obj: Any) -> int:
        """Estimate memory size of an object."""
        try:
            if isinstance(obj, str):
                return len(obj.encode('utf-8'))
            elif isinstance(obj, (int, float)):
                return 8  # Approximate
            elif isinstance(obj, dict):
                return sum(self._estimate_size(k) + self._estimate_size(v) for k, v in obj.items())
            elif isinstance(obj, list):
                return sum(self._estimate_size(item) for item in obj)
            else:
                return len(str(obj).encode('utf-8'))
        except Exception:
            return 1000  # Default estimate

    def _evict_lru(self) -> None:
        """Evict least recently used item."""
        if not self.cache:
            return

        # Find least recently used key
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])

        # Remove from cache
        old_size = self._estimate_size(self.cache[lru_key])
        del self.cache[lru_key]
        del self.access_times[lru_key]
        self.memory_usage -= old_size
