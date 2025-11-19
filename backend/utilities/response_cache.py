# backend/response_cache.py

import time
from typing import Dict, Optional, Tuple

class ResponseCache:
    def __init__(self, ttl_seconds: int = 300):  # 5 minute cache
        self.cache: Dict[str, Tuple[str, float]] = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[str]:
        """Get cached response if not expired"""
        if key in self.cache:
            response, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return response
            else:
                # Remove expired entry
                del self.cache[key]
        return None
    
    def set(self, key: str, response: str):
        """Cache a response"""
        self.cache[key] = (response, time.time())
    
    def clear_expired(self):
        """Remove all expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]

# Global cache instance
response_cache = ResponseCache()