import yaml
from pydantic import BaseModel


class FixedWindowConfig(BaseModel):
    limit: int
    window: int


class SlidingWindowConfig(BaseModel):
    limit: int
    window: int


class TokenBucketConfig(BaseModel):
    capacity: int
    refill_rate: float


class RateLimitConfig(BaseModel):
    algorithm: str

    fixed_window: FixedWindowConfig
    sliding_window: SlidingWindowConfig
    token_bucket: TokenBucketConfig


class RateLimitLoader:

    def __init__(self, path: str):

        with open(path) as file:
            raw = yaml.safe_load(file)

        self.config = RateLimitConfig(**raw)