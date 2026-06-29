from abc import ABC, abstractmethod
from rate_limiter.results import RateLimitResult

class RateLimiter(ABC):

    @abstractmethod
    async def allow_request(self, key: str) -> RateLimitResult:
        pass