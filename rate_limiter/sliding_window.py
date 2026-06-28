import time

from config.rate_limit import RateLimitLoader
from rate_limiter.base import RateLimiter
from rate_limiter.redis_client import redis_client


config = RateLimitLoader(
    "config/rate_limit.yaml"
).config


class SlidingWindowLimiter(RateLimiter):

    async def allow_request(self, key: str):

        redis_key = f"rate_limit:sliding:{key}"

        now = time.time()

        window = config.sliding_window.window
        limit = config.sliding_window.limit

        await redis_client.client.zremrangebyscore(
            redis_key,
            0,
            now - window,
        )

        current = await redis_client.client.zcard(redis_key)

        if current >= limit:
            return False

        await redis_client.client.zadd(
            redis_key,
            {
                str(now): now
            },
        )

        await redis_client.client.expire(
            redis_key,
            window,
        )

        return True