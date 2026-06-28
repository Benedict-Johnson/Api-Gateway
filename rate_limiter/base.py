from abc import ABC, abstractmethod


class RateLimiter(ABC):

    @abstractmethod
    async def allow_request(self, key: str) -> bool:
        pass