"""
Rate limiting middleware for FastAPI.
"""
from collections import defaultdict
from time import time
from typing import Callable
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter.
    Tracks requests per IP address with a sliding window.
    """
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self.requests: dict[str, list[float]] = defaultdict(list)
    
    def is_allowed(self, key: str) -> tuple[bool, int]:
        """
        Check if a request is allowed.
        Returns (is_allowed, remaining_requests)
        """
        now = time()
        window_start = now - self.window_seconds
        
        # Clean old requests outside the window
        self.requests[key] = [
            timestamp for timestamp in self.requests[key]
            if timestamp > window_start
        ]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= self.requests_per_minute:
            remaining = 0
            return False, remaining
        
        # Add current request
        self.requests[key].append(now)
        remaining = self.requests_per_minute - len(self.requests[key])
        
        return True, remaining
    
    def get_retry_after(self, key: str) -> int:
        """Get seconds until the oldest request expires."""
        if not self.requests[key]:
            return 0
        
        oldest = min(self.requests[key])
        now = time()
        retry_after = int(self.window_seconds - (now - oldest)) + 1
        return max(0, retry_after)


# Global rate limiter instances
# Different limits for different endpoint types
public_rate_limiter = RateLimiter(requests_per_minute=100)  # Public endpoints
admin_rate_limiter = RateLimiter(requests_per_minute=10)    # Admin endpoints


def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    # Check for forwarded IP (from proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client IP
    if request.client:
        return request.client.host
    
    return "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to apply rate limiting to all requests.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path == "/api/health":
            return await call_next(request)
        
        # Determine which rate limiter to use
        if request.url.path.startswith("/api/admin"):
            limiter = admin_rate_limiter
        else:
            limiter = public_rate_limiter
        
        # Get client identifier
        client_ip = get_client_ip(request)
        
        # Check rate limit
        is_allowed, remaining = limiter.is_allowed(client_ip)
        
        if not is_allowed:
            retry_after = limiter.get_retry_after(client_ip)
            logger.warning(
                f"Rate limit exceeded for {client_ip} on {request.url.path}. "
                f"Retry after {retry_after} seconds."
            )
            
            response = Response(
                content='{"detail": "Too Many Requests"}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json"
            )
            response.headers["Retry-After"] = str(retry_after)
            response.headers["X-RateLimit-Limit"] = str(limiter.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = "0"
            return response
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response



