"""
Rate limiting utilities for web scraping.
Implements token bucket algorithm to prevent overwhelming the server.
"""

import asyncio
import time
from typing import Dict, Optional
from src.config import config
from src.utils.logging import get_logger


class RateLimiter:
    """Token bucket rate limiter for API/scraping requests."""
    
    def __init__(self, 
                 requests_per_minute: Optional[int] = None, 
                 burst_size: Optional[int] = None,
                 trace_id: Optional[str] = None):
        self.logger = get_logger(__name__, trace_id)
        
        # Configure rate limits
        self.requests_per_minute = requests_per_minute or config.requests_per_minute
        self.burst_size = burst_size or min(self.requests_per_minute, 10)
        
        # Token bucket state
        self.tokens = float(self.burst_size)
        self.last_update = time.time()
        self.lock = asyncio.Lock()
        
        # Calculate token refill rate (tokens per second)
        self.refill_rate = self.requests_per_minute / 60.0
        
        self.logger.info(f"RateLimiter initialized: {self.requests_per_minute} req/min, burst: {self.burst_size}")
    
    async def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens from the bucket. Will wait if insufficient tokens.
        
        Args:
            tokens: Number of tokens to acquire (default 1)
        """
        async with self.lock:
            await self._wait_for_tokens(tokens)
            self.tokens -= tokens
            self.logger.debug(f"Acquired {tokens} tokens, remaining: {self.tokens:.2f}")
    
    async def _wait_for_tokens(self, required_tokens: int) -> None:
        """Wait until sufficient tokens are available."""
        while True:
            self._refill_tokens()
            
            if self.tokens >= required_tokens:
                break
            
            # Calculate wait time for next token
            wait_time = (required_tokens - self.tokens) / self.refill_rate
            self.logger.debug(f"Rate limited, waiting {wait_time:.2f}s for {required_tokens} tokens")
            
            await asyncio.sleep(min(wait_time, 1.0))  # Max 1 second wait per iteration
    
    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update
        
        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.burst_size, self.tokens + tokens_to_add)
        self.last_update = now
    
    async def get_status(self) -> Dict[str, float]:
        """Get current rate limiter status."""
        async with self.lock:
            self._refill_tokens()
            return {
                'available_tokens': self.tokens,
                'max_tokens': self.burst_size,
                'refill_rate_per_second': self.refill_rate,
                'requests_per_minute': self.requests_per_minute
            }


class ConcurrencyLimiter:
    """Limits concurrent operations to prevent overwhelming resources."""
    
    def __init__(self, max_concurrent: Optional[int] = None, trace_id: Optional[str] = None):
        self.logger = get_logger(__name__, trace_id)
        self.max_concurrent = max_concurrent or config.concurrent_requests
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        self.active_count = 0
        
        self.logger.info(f"ConcurrencyLimiter initialized: max {self.max_concurrent} concurrent operations")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.semaphore.acquire()
        self.active_count += 1
        self.logger.debug(f"Acquired concurrency slot, active: {self.active_count}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.active_count -= 1
        self.semaphore.release()
        self.logger.debug(f"Released concurrency slot, active: {self.active_count}")
    
    def get_status(self) -> Dict[str, int]:
        """Get current concurrency status."""
        return {
            'active_operations': self.active_count,
            'max_concurrent': self.max_concurrent,
            'available_slots': self.max_concurrent - self.active_count
        }


# Global rate limiter instances
_rate_limiter: Optional[RateLimiter] = None
_concurrency_limiter: Optional[ConcurrencyLimiter] = None


def get_rate_limiter(trace_id: Optional[str] = None) -> RateLimiter:
    """Get global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(trace_id=trace_id)
    return _rate_limiter


def get_concurrency_limiter(trace_id: Optional[str] = None) -> ConcurrencyLimiter:
    """Get global concurrency limiter instance."""
    global _concurrency_limiter
    if _concurrency_limiter is None:
        _concurrency_limiter = ConcurrencyLimiter(trace_id=trace_id)
    return _concurrency_limiter


async def rate_limited_request(operation_name: str = "request", trace_id: Optional[str] = None):
    """
    Decorator/context manager for rate-limited operations.
    
    Usage:
        async with rate_limited_request("scrape_page"):
            # Your scraping operation here
            pass
    """
    logger = get_logger(__name__, trace_id)
    rate_limiter = get_rate_limiter(trace_id)
    concurrency_limiter = get_concurrency_limiter(trace_id)
    
    class RateLimitedContext:
        async def __aenter__(self):
            logger.debug(f"Starting rate-limited operation: {operation_name}")
            await rate_limiter.acquire()
            await concurrency_limiter.__aenter__()
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await concurrency_limiter.__aexit__(exc_type, exc_val, exc_tb)
            logger.debug(f"Completed rate-limited operation: {operation_name}")
    
    return RateLimitedContext()
