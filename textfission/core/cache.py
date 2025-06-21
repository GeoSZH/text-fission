from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta
import hashlib
import json
import pickle
from pathlib import Path
import os
from threading import Lock
from ..core.logger import Logger

logger = Logger.get_instance()

class CacheEntry:
    """Cache entry with expiration"""
    
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.created_at = datetime.now()
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)

class Cache:
    """Cache management class"""
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,
        cache_dir: Optional[str] = None
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache_dir = cache_dir
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.lock = Lock()
        
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
    
    def _get_key(self, key: Any) -> str:
        """Generate cache key from input"""
        if isinstance(key, (str, int, float, bool)):
            key_str = str(key)
        else:
            try:
                key_str = json.dumps(key, sort_keys=True)
            except:
                key_str = pickle.dumps(key)
        
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_file_path(self, key: str) -> Optional[Path]:
        """Get cache file path"""
        if not self.cache_dir:
            return None
        return Path(self.cache_dir) / f"{key}.cache"
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value from cache"""
        cache_key = self._get_key(key)
        
        # Try memory cache first
        with self.lock:
            entry = self.memory_cache.get(cache_key)
            if entry and not entry.is_expired():
                return entry.value
        
        # Try file cache
        file_path = self._get_file_path(cache_key)
        if file_path and file_path.exists():
            try:
                with open(file_path, "rb") as f:
                    entry = pickle.load(f)
                if not entry.is_expired():
                    # Update memory cache
                    with self.lock:
                        self.memory_cache[cache_key] = entry
                    return entry.value
                else:
                    # Remove expired file
                    file_path.unlink()
            except Exception as e:
                logger.warning(f"Error reading cache file: {str(e)}")
        
        return default
    
    def set(
        self,
        key: Any,
        value: Any,
        ttl: Optional[int] = None,
        persist: bool = False
    ) -> None:
        """Set value in cache"""
        cache_key = self._get_key(key)
        entry = CacheEntry(value, ttl or self.default_ttl)
        
        # Update memory cache
        with self.lock:
            # Check cache size
            if len(self.memory_cache) >= self.max_size:
                # Remove oldest entry
                oldest_key = min(
                    self.memory_cache.keys(),
                    key=lambda k: self.memory_cache[k].created_at
                )
                del self.memory_cache[oldest_key]
            
            self.memory_cache[cache_key] = entry
        
        # Update file cache if requested
        if persist and self.cache_dir:
            file_path = self._get_file_path(cache_key)
            try:
                with open(file_path, "wb") as f:
                    pickle.dump(entry, f)
            except Exception as e:
                logger.warning(f"Error writing cache file: {str(e)}")
    
    def delete(self, key: Any) -> None:
        """Delete value from cache"""
        cache_key = self._get_key(key)
        
        # Remove from memory cache
        with self.lock:
            self.memory_cache.pop(cache_key, None)
        
        # Remove from file cache
        file_path = self._get_file_path(cache_key)
        if file_path and file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                logger.warning(f"Error deleting cache file: {str(e)}")
    
    def clear(self) -> None:
        """Clear all cache entries"""
        # Clear memory cache
        with self.lock:
            self.memory_cache.clear()
        
        # Clear file cache
        if self.cache_dir:
            try:
                for file_path in Path(self.cache_dir).glob("*.cache"):
                    file_path.unlink()
            except Exception as e:
                logger.warning(f"Error clearing cache directory: {str(e)}")
    
    def get_or_set(
        self,
        key: Any,
        default_func: Callable[[], Any],
        ttl: Optional[int] = None,
        persist: bool = False
    ) -> Any:
        """Get value from cache or set if not exists"""
        value = self.get(key)
        if value is None:
            value = default_func()
            self.set(key, value, ttl, persist)
        return value
    
    def exists(self, key: Any) -> bool:
        """Check if key exists in cache"""
        return self.get(key) is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            memory_size = len(self.memory_cache)
            expired_count = sum(1 for entry in self.memory_cache.values() if entry.is_expired())
        
        file_count = 0
        if self.cache_dir:
            try:
                file_count = len(list(Path(self.cache_dir).glob("*.cache")))
            except Exception as e:
                logger.warning(f"Error getting cache file count: {str(e)}")
        
        return {
            "memory_size": memory_size,
            "expired_count": expired_count,
            "file_count": file_count,
            "max_size": self.max_size,
            "default_ttl": self.default_ttl
        }

class CacheManager:
    """Cache manager singleton"""
    _instance = None
    _cache = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> "CacheManager":
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def setup(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,
        cache_dir: Optional[str] = None
    ) -> Cache:
        """Setup cache with specified configuration"""
        if self._cache is None:
            self._cache = Cache(max_size, default_ttl, cache_dir)
        return self._cache
    
    def get_cache(self) -> Cache:
        """Get current cache instance"""
        if self._cache is None:
            self.setup()
        return self._cache 