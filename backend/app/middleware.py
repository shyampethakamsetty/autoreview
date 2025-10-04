import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse

# Initialize rate limiter with Redis backend if available
REDIS_URL = os.getenv('REDIS_URL')

if REDIS_URL:
    from slowapi.middleware import SlowAPIMiddleware
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=REDIS_URL,
        default_limits=["200/minute", "50/minute"]  # Global limits
    )
else:
    # In-memory fallback for development
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200/minute", "50/minute"]
    )

def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler"""
    response = JSONResponse(
        status_code=429,
        content={
            "detail": f"Rate limit exceeded: {exc.detail}",
            "retry_after": str(exc.retry_after) if exc.retry_after else None
        }
    )
    response.headers["Retry-After"] = str(exc.retry_after) if exc.retry_after else "60"
    return response

# Configure rate limiting rules
AI_RATE_LIMIT = "10/minute"  # More restrictive for AI endpoints
SEARCH_RATE_LIMIT = "30/minute"  # Moderate for search
GENERAL_RATE_LIMIT = "100/minute"  # Generous for general API