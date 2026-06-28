from config.rate_limit import RateLimitLoader
from rate_limiter.base import RateLimiter
from rate_limiter.redis_client import redis_client


config = RateLimitLoader(
    "config/rate_limit.yaml"
).config


class FixedWindowLimiter(RateLimiter):

    async def allow_request(self, key: str):

        redis_key = f"rate_limit:ip:{key}"

        count = await redis_client.client.incr(redis_key)

        if count == 1:
            await redis_client.client.expire(
                redis_key,
                config.fixed_window.window
            )

        return count <= config.fixed_window.limit