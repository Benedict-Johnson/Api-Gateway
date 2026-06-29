from dataclasses import dataclass
from typing import Optional


@dataclass
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after: Optional[int] = None
    reset_at: Optional[int] = None
