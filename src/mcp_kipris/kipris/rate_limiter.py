"""
Rate limiting utilities for KIPRIS API requests.
Implements token bucket algorithm to prevent API throttling.
"""

import asyncio
import time
import threading
from typing import Dict, Optional
from collections import deque
from datetime import datetime, timedelta


class TokenBucket:
    """Token bucket for rate limiting."""

    def __init__(self, capacity: int, refill_rate: float, tokens_per_refill: int = 1):
        """
        Initialize token bucket.

        Args:
            capacity: Maximum number of tokens the bucket can hold
            refill_rate: Rate at which tokens are added (tokens per second)
            tokens_per_refill: Number of tokens added each refill
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.tokens_per_refill = tokens_per_refill
        self.last_refill = datetime.now()
        self._lock = threading.Lock()

    def consume(self, tokens: int) -> bool:
        """
        Try to consume tokens from bucket.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False otherwise
        """
        with self._lock:
            now = datetime.now()
            # Refill tokens based on time elapsed
            time_elapsed = (now - self.last_refill).total_seconds()
            tokens_to_add = int(time_elapsed * self.refill_rate)

            if tokens_to_add > 0:
                self.tokens = min(self.capacity, self.tokens + tokens_to_add)
                self.last_refill = now
            else:
                self.tokens = max(0, self.tokens + tokens_to_add)

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            else:
                return False

    def time_until_available(self, tokens: int) -> float:
        """
        Calculate time until specified tokens are available.

        Args:
            tokens: Number of tokens needed

        Returns:
            Seconds until tokens will be available
        """
        with self._lock:
            if self.tokens >= tokens:
                return 0.0

            now = datetime.now()
            time_elapsed = (now - self.last_refill).total_seconds()
            tokens_needed = tokens - self.tokens

            if tokens_needed <= 0:
                return 0.0

            # Calculate time needed for refill
            tokens_per_second = self.refill_rate
            seconds_needed = tokens_needed / tokens_per_second
            return seconds_needed


class RateLimiter:
    """Rate limiter for KIPRIS API requests."""

    def __init__(self, max_requests_per_minute: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests_per_minute: Maximum requests allowed per minute
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.requests = deque(maxlen=max_requests_per_minute)
        self._lock = threading.Lock()

    def can_make_request(self) -> bool:
        """
        Check if a request can be made.

        Returns:
            True if request is allowed, False otherwise
        """
        with self._lock:
            now = datetime.now()
            # Remove requests older than 1 minute
            one_minute_ago = now - timedelta(minutes=1)

            # Filter old requests
            while self.requests and self.requests[0] < one_minute_ago:
                self.requests.popleft()

            # Check if we can make a new request
            if len(self.requests) < self.max_requests_per_minute:
                return True
            else:
                return False

    def record_request(self) -> None:
        """Record a successful request."""
        with self._lock:
            self.requests.append(datetime.now())


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter(max_requests_per_minute: int = 60) -> RateLimiter:
    """
    Get or create a rate limiter instance.

    Args:
        max_requests_per_minute: Maximum requests per minute

    Returns:
        RateLimiter instance
    """
    global _rate_limiter

    if _rate_limiter is None:
        _rate_limiter = RateLimiter(max_requests_per_minute)

    return _rate_limiter


async def wait_if_rate_limited() -> None:
    """
    Wait if rate limited. Should be called before making API requests.
    """
    rate_limiter = get_rate_limiter()

    while not rate_limiter.can_make_request():
        wait_time = 60.0  # Wait 1 second before checking again
        logger.warning(f"Rate limit reached. Waiting {wait_time:.1f} seconds before next request.")
        await asyncio.sleep(wait_time)
