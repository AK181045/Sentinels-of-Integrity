"""
=============================================================================
SENTINELS OF INTEGRITY — Rate Limiter Middleware
Redis-based sliding window rate limiting.
=============================================================================

Security (TechStack.txt §2):
- "Rate Limiting: Redis-based sliding window to prevent DDoS on GPU nodes."
=============================================================================
"""

import logging
import time
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("sentinels.api.rate_limiter")


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Sliding window rate limiter middleware.

    Uses Redis (in production) or an in-memory dict (in dev) to track
    request counts per client IP within a sliding time window.

    This protects GPU inference nodes from being overwhelmed by
    excessive requests (DDoS or runaway clients).
    """

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._redis_client = None  # TODO: Initialize Redis connection

        # In-memory fallback for development
        self._memory_store: dict[str, list[float]] = {}

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP, accounting for reverse proxies."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def _check_rate_limit_memory(self, client_ip: str) -> tuple[bool, int]:
        """In-memory rate limit check (development fallback)."""
        now = time.time()
        window_start = now - self.window_seconds

        # Get or create request history for this client
        if client_ip not in self._memory_store:
            self._memory_store[client_ip] = []

        # Remove expired entries
        self._memory_store[client_ip] = [
            ts for ts in self._memory_store[client_ip] if ts > window_start
        ]

        current_count = len(self._memory_store[client_ip])

        if current_count >= self.max_requests:
            return False, 0  # Rate limited

        # Record this request
        self._memory_store[client_ip].append(now)
        remaining = self.max_requests - current_count - 1
        return True, remaining

    async def _check_rate_limit_redis(self, client_ip: str) -> tuple[bool, int]:
        """Redis-based sliding window rate limit check."""
        # TODO: Implement Redis sliding window:
        # key = f"rate_limit:{client_ip}"
        # Use ZADD with timestamp scores and ZRANGEBYSCORE to count
        # within the sliding window
        return await self._check_rate_limit_memory(client_ip)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ("/api/v1/health", "/api/v1/health/ready", "/"):
            return await call_next(request)

        client_ip = self._get_client_ip(request)

        # Check rate limit
        if self._redis_client:
            allowed, remaining = await self._check_rate_limit_redis(client_ip)
        else:
            allowed, remaining = await self._check_rate_limit_memory(client_ip)

        if not allowed:
            logger.warning(f"Rate limit exceeded | client={client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Too many requests. Limit: {self.max_requests} per {self.window_seconds}s.",
                    "retry_after": self.window_seconds,
                },
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # Process request and add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
