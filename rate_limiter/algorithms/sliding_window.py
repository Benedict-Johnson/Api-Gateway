import time

from rate_limiter.config import RateLimitLoader
from rate_limiter.base import RateLimiter
from rate_limiter.redis import redis_client
from rate_limiter.results import RateLimitResult


class SlidingWindowLimiter(RateLimiter):
    def __init__(self, config_loader: RateLimitLoader):
        self.config_loader = config_loader

    async def allow_request(self, key: str) -> RateLimitResult:
        config = self.config_loader.config
        redis_key = f"rate_limit:sliding:{key}"

        now = time.time()
        window = config.sliding_window.window
        limit = config.sliding_window.limit

        await redis_client.zremrangebyscore(
            redis_key,
            0,
            now - window,
        )

        current = await redis_client.zcard(redis_key)
        
        remaining = max(0, limit - (current + 1))
        
        if current >= limit:
            return RateLimitResult(
                allowed=False,
                limit=limit,
                remaining=0
            )

        await redis_client.zadd(
            redis_key,
            {str(now): now},
        )

        await redis_client.expire(redis_key, window)

        return RateLimitResult(
            allowed=True,
            limit=limit,
            remaining=remaining
        )