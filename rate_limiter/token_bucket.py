import time

from config.rate_limit import RateLimitLoader
from rate_limiter.base import RateLimiter
from rate_limiter.redis_client import redis_client


config = RateLimitLoader(
    "config/rate_limit.yaml"
).config


class TokenBucketLimiter(RateLimiter):

    async def allow_request(self, key: str):

        redis_key = f"rate_limit:bucket:{key}"

        bucket = await redis_client.client.hgetall(redis_key)

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

        tokens = min(
            capacity,
            tokens + elapsed * refill
        )

        if tokens < 1:

            await redis_client.client.hset(
                redis_key,
                mapping={
                    "tokens": tokens,
                    "last": now
                }
            )

            return False

        tokens -= 1

        await redis_client.client.hset(
            redis_key,
            mapping={
                "tokens": tokens,
                "last": now
            }
        )

        return True