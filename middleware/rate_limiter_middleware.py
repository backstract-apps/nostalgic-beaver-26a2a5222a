from fastapi import FastAPI, Request, Response, HTTPException
import os
import time
import asyncio
from typing import Dict, Tuple
from collections import defaultdict


def setup_rate_limiter_middleware(app: FastAPI) -> FastAPI:
    """
    Setup Rate Limiter middleware with configurable capacity, refill rate, and exempted paths
    Uses token bucket algorithm for rate limiting
    """

    # Get configuration from environment variables
    capacity = int(
        os.getenv("RATE_LIMITER_CAPACITY", "2000")
    )  # Maximum requests per minute
    refill_rate = int(
        os.getenv("RATE_LIMITER_REFILL_RATE", "600")
    )  # Tokens added per minute
    exempted_path = os.getenv("RATE_LIMITER_EXEMPTED_PATH", "")

    # Validate configuration
    if capacity <= 0:
        capacity = 2000
    if refill_rate <= 0:
        refill_rate = 600
    if refill_rate > capacity:
        refill_rate = capacity  # Refill rate cannot exceed capacity

    # Token bucket storage: {client_id: (tokens, last_refill_time)}
    token_buckets: Dict[str, Tuple[float, float]] = defaultdict(
        lambda: (float(capacity), time.time())
    )

    # Lock for thread-safe access to token buckets
    bucket_lock = asyncio.Lock()

    def get_client_id(request: Request) -> str:
        """
        Get client identifier (IP address) for rate limiting
        """
        # Try to get real IP from various headers (for proxied requests)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                client_ip = real_ip
            else:
                client_ip = request.client.host if request.client else "unknown"

        return client_ip

    def is_path_exempted(path: str, exempted_path: str) -> bool:
        """
        Check if the request path is exempted from rate limiting
        """
        if not exempted_path:
            return False

        # Exact match or prefix match
        return path == exempted_path or path.startswith(exempted_path.rstrip("/") + "/")

    def refill_tokens(client_id: str) -> Tuple[float, float]:
        """
        Refill tokens for a client based on elapsed time
        Returns (current_tokens, last_refill_time)
        Note: This should be called within the bucket_lock context
        """
        current_time = time.time()
        tokens, last_refill = token_buckets[client_id]

        # Calculate time elapsed since last refill (in minutes)
        elapsed_minutes = (current_time - last_refill) / 60.0

        # Calculate tokens to add
        tokens_to_add = elapsed_minutes * refill_rate

        # Refill tokens (but don't exceed capacity)
        new_tokens = min(capacity, tokens + tokens_to_add)

        # Update last refill time
        new_last_refill = current_time

        # Update bucket
        token_buckets[client_id] = (new_tokens, new_last_refill)

        return (new_tokens, new_last_refill)

    async def consume_token(client_id: str) -> bool:
        """
        Try to consume a token from the client's bucket
        Returns True if token was consumed, False if rate limit exceeded
        """
        async with bucket_lock:
            tokens, last_refill = refill_tokens(client_id)

            if tokens >= 1.0:
                # Consume one token
                token_buckets[client_id] = (tokens - 1.0, last_refill)
                return True
            else:
                # Rate limit exceeded
                return False

    @app.middleware("http")
    async def rate_limiter_middleware(request: Request, call_next):
        # Get request path
        path = request.url.path

        # Check if path is exempted
        if is_path_exempted(path, exempted_path):
            # Process request without rate limiting
            response = await call_next(request)
            return response

        # Get client identifier
        client_id = get_client_id(request)

        # Try to consume a token
        allowed = await consume_token(client_id)

        if not allowed:
            # Rate limit exceeded
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Too many requests.",
                headers={
                    "Retry-After": "60",  # Suggest retrying after 60 seconds
                    "X-RateLimit-Limit": str(capacity),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        async with bucket_lock:
            tokens, _ = refill_tokens(client_id)
            remaining = max(0, int(tokens))
            response.headers["X-RateLimit-Limit"] = str(capacity)
            response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response

    return app
