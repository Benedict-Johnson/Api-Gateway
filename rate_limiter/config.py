from config.yaml_loader import YAMLLoader
from rate_limiter.models import RateLimitConfig


class RateLimitLoader(YAMLLoader):
    """Configuration loader for the rate limiter."""

    @property
    def config(self) -> RateLimitConfig:
        return RateLimitConfig(**self.raw)
