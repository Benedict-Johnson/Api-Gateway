from config.rate_limit import RateLimitLoader
from rate_limiter.token_bucket import TokenBucketLimiter
from rate_limiter.fixed_window import FixedWindowLimiter
from rate_limiter.sliding_window import SlidingWindowLimiter


config = RateLimitLoader(
    "config/rate_limit.yaml"
).config


class RateLimiterManager:

    def __init__(self):

        self.algorithms = {
        "fixed_window": FixedWindowLimiter(),
        "sliding_window": SlidingWindowLimiter(),
        "token_bucket": TokenBucketLimiter(),
    }

        self.limiter = self.algorithms.get(
            config.algorithm
        )

        if self.limiter is None:
            raise ValueError(
                f"Unknown rate limiter: {config.algorithm}"
            )

    async def allow(self, key: str):

        return await self.limiter.allow_request(key)