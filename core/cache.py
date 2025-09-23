"""
Caching layer for Vectorpenter to improve performance
"""

import hashlib
import json
import time
import threading
from functools import wraps, lru_cache
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass
from collections import OrderedDict

from core.logging import logger


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    created_at: float
    access_count: int = 0
    last_accessed: float = 0.0
    ttl: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def touch(self):
        """Update access statistics"""
        self.access_count += 1
        self.last_accessed = time.time()


class LRUCache:
    """Thread-safe LRU cache with TTL support"""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
    def _make_key(self, *args, **kwargs) -> str:
        """Create cache key from arguments"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self._cache[key]
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()
            
            return entry.value
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Put value in cache"""
        with self._lock:
            # Remove oldest entries if at capacity
            while len(self._cache) >= self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            
            # Create cache entry
            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                ttl=ttl or self.default_ttl
            )
            
            self._cache[key] = entry
            self._cache.move_to_end(key)
    
    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_entries = len(self._cache)
            expired_entries = sum(1 for entry in self._cache.values() if entry.is_expired())
            
            if total_entries > 0:
                avg_access_count = sum(entry.access_count for entry in self._cache.values()) / total_entries
                total_size_estimate = sum(len(str(entry.value)) for entry in self._cache.values())
            else:
                avg_access_count = 0
                total_size_estimate = 0
            
            return {
                "total_entries": total_entries,
                "expired_entries": expired_entries,
                "max_size": self.max_size,
                "utilization": total_entries / self.max_size if self.max_size > 0 else 0,
                "avg_access_count": avg_access_count,
                "estimated_size_bytes": total_size_estimate
            }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() 
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)


# Cache instances for different types of data
embedding_cache = LRUCache(max_size=5000, default_ttl=3600)  # 1 hour TTL
search_results_cache = LRUCache(max_size=1000, default_ttl=300)  # 5 minute TTL
context_cache = LRUCache(max_size=500, default_ttl=600)  # 10 minute TTL


def cache_embeddings(ttl: Optional[float] = None):
    """Decorator to cache embedding results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(texts: List[str], *args, **kwargs):
            # Create cache key from texts
            cache_key = embedding_cache._make_key(texts, *args, **kwargs)
            
            # Try to get from cache
            cached_result = embedding_cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for embedding batch of {len(texts)} texts")
                return cached_result
            
            # Cache miss - call original function
            logger.debug(f"Cache miss for embedding batch of {len(texts)} texts")
            result = func(texts, *args, **kwargs)
            
            # Store in cache
            embedding_cache.put(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def cache_search_results(ttl: Optional[float] = None):
    """Decorator to cache search results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = search_results_cache._make_key(*args, **kwargs)
            
            # Try to get from cache
            cached_result = search_results_cache.get(cache_key)
            if cached_result is not None:
                logger.debug("Cache hit for search results")
                return cached_result
            
            # Cache miss - call original function
            logger.debug("Cache miss for search results")
            result = func(*args, **kwargs)
            
            # Store in cache
            search_results_cache.put(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def cache_context(ttl: Optional[float] = None):
    """Decorator to cache built context"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(snippets: List[Dict], *args, **kwargs):
            # Create cache key from snippet IDs and parameters
            snippet_ids = [s.get('id', '') for s in snippets]
            cache_key = context_cache._make_key(snippet_ids, *args, **kwargs)
            
            # Try to get from cache
            cached_result = context_cache.get(cache_key)
            if cached_result is not None:
                logger.debug("Cache hit for context building")
                return cached_result
            
            # Cache miss - call original function
            logger.debug("Cache miss for context building")
            result = func(snippets, *args, **kwargs)
            
            # Store in cache
            context_cache.put(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


class ConnectionPool:
    """Simple connection pool for database connections"""
    
    def __init__(self, create_connection: Callable, max_connections: int = 10):
        self.create_connection = create_connection
        self.max_connections = max_connections
        self._pool = []
        self._active_connections = set()
        self._lock = threading.Lock()
    
    def get_connection(self):
        """Get a connection from the pool"""
        with self._lock:
            # Try to reuse existing connection
            if self._pool:
                conn = self._pool.pop()
                self._active_connections.add(conn)
                return conn
            
            # Create new connection if under limit
            if len(self._active_connections) < self.max_connections:
                conn = self.create_connection()
                self._active_connections.add(conn)
                return conn
            
            # Pool exhausted
            raise Exception(f"Connection pool exhausted (max: {self.max_connections})")
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        with self._lock:
            if conn in self._active_connections:
                self._active_connections.remove(conn)
                self._pool.append(conn)
    
    def close_all(self):
        """Close all connections"""
        with self._lock:
            for conn in list(self._active_connections) + self._pool:
                try:
                    conn.close()
                except Exception as e:
                    logger.warning(f"Error closing connection: {e}")
            
            self._active_connections.clear()
            self._pool.clear()
    
    def stats(self) -> Dict[str, int]:
        """Get connection pool statistics"""
        with self._lock:
            return {
                "active_connections": len(self._active_connections),
                "pooled_connections": len(self._pool),
                "max_connections": self.max_connections,
                "total_created": len(self._active_connections) + len(self._pool)
            }


@lru_cache(maxsize=1000)
def cached_hash_text(text: str) -> str:
    """Cache text hashing for duplicate detection"""
    return hashlib.sha256(text.encode()).hexdigest()


@lru_cache(maxsize=100)
def cached_chunk_count(text: str, chunk_size: int = 700) -> int:
    """Cache chunk count calculations"""
    words = text.split()
    return max(1, len(words) // chunk_size)


def warm_up_caches():
    """Warm up caches with common operations"""
    logger.info("Warming up caches...")
    
    # Warm up with common test patterns
    test_texts = [
        "This is a test document for cache warming",
        "Another test document with different content",
        "Machine learning and artificial intelligence"
    ]
    
    for text in test_texts:
        cached_hash_text(text)
        cached_chunk_count(text)
    
    logger.info("Cache warm-up completed")


def cache_maintenance():
    """Perform cache maintenance tasks"""
    logger.debug("Starting cache maintenance...")
    
    # Clean up expired entries
    embedding_expired = embedding_cache.cleanup_expired()
    search_expired = search_results_cache.cleanup_expired()
    context_expired = context_cache.cleanup_expired()
    
    total_expired = embedding_expired + search_expired + context_expired
    
    if total_expired > 0:
        logger.info(f"Cache maintenance: removed {total_expired} expired entries")
    
    # Log cache statistics
    embedding_stats = embedding_cache.stats()
    search_stats = search_results_cache.stats()
    context_stats = context_cache.stats()
    
    logger.debug(f"Cache stats - Embeddings: {embedding_stats['utilization']:.1%} full, "
                f"Search: {search_stats['utilization']:.1%} full, "
                f"Context: {context_stats['utilization']:.1%} full")


def get_cache_stats() -> Dict[str, Any]:
    """Get comprehensive cache statistics"""
    return {
        "embedding_cache": embedding_cache.stats(),
        "search_results_cache": search_results_cache.stats(),
        "context_cache": context_cache.stats(),
        "timestamp": time.time()
    }


# Automatic cache maintenance (could be run periodically)
import atexit
atexit.register(lambda: logger.info("Shutting down cache system..."))
