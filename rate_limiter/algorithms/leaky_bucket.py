import time
import math

from rate_limiter.config import RateLimitLoader
from rate_limiter.base import RateLimiter
from rate_limiter.redis import redis_client
from rate_limiter.results import RateLimitResult


class LeakyBucketLimiter(RateLimiter):
    def __init__(self, config_loader: RateLimitLoader):
        self.config_loader = config_loader

    async def allow_request(self, key: str) -> RateLimitResult:
        config = self.config_loader.config
        redis_key = f"rate_limit:leaky:{key}"

        bucket = await redis_client.hgetall(redis_key)

        capacity = config.leaky_bucket.capacity
        leak_rate = config.leaky_bucket.leak_rate
        now = time.time()

        if bucket:
            level = float(bucket["level"])
            last = float(bucket["last"])
        else:
            level = 0
            last = now

        elapsed = now - last
        level = max(0, level - elapsed * leak_rate)
        
        remaining = max(0, capacity - math.ceil(level))

        if level >= capacity:
            return RateLimitResult(
                allowed=False,
                limit=capacity,
                remaining=0
            )

        level += 1

        await redis_client.hset(
            redis_key,
            mapping={
                "level": level,
                "last": now
            }
        )

        return RateLimitResult(
            allowed=True,
            limit=capacity,
            remaining=max(0, capacity - math.ceil(level))
        )