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
        from config.settings import settings

        if settings.DEMO_MODE:
            # TEMPORARY DOCUMENTATION / DEMO MODE: Bypass rate limiting for screenshot generation.
            # Must remain disabled (DEMO_MODE=false) in production environments!
            from rate_limiter.results import RateLimitResult

            return RateLimitResult(
                allowed=True,
                limit=999999,
                remaining=999999,
                retry_after=None,
                reset_at=None,
            )

        return await self.limiter.allow_request(key)
