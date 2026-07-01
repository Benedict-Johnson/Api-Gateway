from rate_limiter.algorithms import (
    FixedWindowLimiter,
    LeakyBucketLimiter,
    SlidingWindowLimiter,
    TokenBucketLimiter,
)
from rate_limiter.config import RateLimitLoader


class RateLimiterManager:

    def __init__(self, config_loader: RateLimitLoader):
        self.config_loader = config_loader
        self.algorithms = {
            "fixed_window": FixedWindowLimiter(self.config_loader),
            "sliding_window": SlidingWindowLimiter(self.config_loader),
            "token_bucket": TokenBucketLimiter(self.config_loader),
            "leaky_bucket": LeakyBucketLimiter(self.config_loader),
        }

    @property
    def limiter(self):
        algorithm = self.config_loader.config.algorithm
        limiter = self.algorithms.get(algorithm)
        if limiter is None:
            raise ValueError(f"Unknown rate limiter: {algorithm}")
        return limiter

    async def allow(self, key: str):
        return await self.limiter.allow_request(key)
