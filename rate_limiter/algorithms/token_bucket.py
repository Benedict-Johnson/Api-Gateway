import time

from rate_limiter.config import RateLimitLoader
from rate_limiter.base import RateLimiter
from rate_limiter.redis import redis_client
from rate_limiter.results import RateLimitResult


class TokenBucketLimiter(RateLimiter):
    def __init__(self, config_loader: RateLimitLoader):
        self.config_loader = config_loader

    async def allow_request(self, key: str) -> RateLimitResult:
        config = self.config_loader.config
        redis_key = f"rate_limit:bucket:{key}"

        bucket = await redis_client.hgetall(redis_key)

        capacity = config.token_bucket.capacity
        refill = config.token_bucket.refill_rate
        now = time.time()

        if bucket:
            tokens = float(bucket["tokens"])
            last = float(bucket["last"])
        else:
            tokens = capacity
            last = now

        elapsed = now - last
        tokens = min(capacity, tokens + elapsed * refill)

        if tokens < 1:
            await redis_client.hset(
                redis_key,
                mapping={
                    "tokens": tokens,
                    "last": now
                }
            )
            return RateLimitResult(
                allowed=False,
                limit=capacity,
                remaining=int(tokens)
            )

        tokens -= 1

        await redis_client.hset(
            redis_key,
            mapping={
                "tokens": tokens,
                "last": now
            }
        )

        return RateLimitResult(
            allowed=True,
            limit=capacity,
            remaining=int(tokens)
        )