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


class LeakyBucketConfig(BaseModel):
    capacity: int
    leak_rate: float


class RateLimitConfig(BaseModel):
    algorithm: str

    fixed_window: FixedWindowConfig
    sliding_window: SlidingWindowConfig
    token_bucket: TokenBucketConfig
    leaky_bucket: LeakyBucketConfig