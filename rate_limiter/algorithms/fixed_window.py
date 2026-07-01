from rate_limiter.base import RateLimiter
from rate_limiter.config import RateLimitLoader
from rate_limiter.redis import redis_client
from rate_limiter.results import RateLimitResult


class FixedWindowLimiter(RateLimiter):
    def __init__(self, config_loader: RateLimitLoader):
        self.config_loader = config_loader

    async def allow_request(self, key: str) -> RateLimitResult:
        config = self.config_loader.config
        redis_key = f"rate_limit:ip:{key}"

        count = await redis_client.incr(redis_key)

        if count == 1:
            await redis_client.expire(redis_key, config.fixed_window.window)

        allowed = count <= config.fixed_window.limit
        remaining = max(0, config.fixed_window.limit - count)

        return RateLimitResult(
            allowed=allowed, limit=config.fixed_window.limit, remaining=remaining
        )
