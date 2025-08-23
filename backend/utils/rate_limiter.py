#!/usr/bin/env python3
"""
Rate limiting utility for API endpoints
"""

import time
from typing import Dict, Optional
from collections import defaultdict

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client"""
        current_time = time.time()
        expired_time = current_time - self.window_seconds
        
        # Clean up expired requests for this client
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > expired_time
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(current_time)
            return True
        
        return False
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client"""
        current_time = time.time()
        expired_time = current_time - self.window_seconds
        
        # Clean up expired requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > expired_time
        ]
        
        return max(0, self.max_requests - len(self.requests[client_id]))
    
    def get_reset_time(self, client_id: str) -> Optional[float]:
        """Get time when rate limit resets for client"""
        if not self.requests[client_id]:
            return None
        
        oldest_request = min(self.requests[client_id])
        return oldest_request + self.window_seconds

# Global rate limiter instance
from config import Config
rate_limiter = RateLimiter(
    max_requests=Config.RATE_LIMIT_MAX_REQUESTS, 
    window_seconds=Config.RATE_LIMIT_WINDOW_SECONDS
)
