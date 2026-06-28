from abc import ABC, abstractmethod

from fastapi import Request


class AuthenticationStrategy(ABC):

    @abstractmethod
    async def authenticate(self, request: Request):
        pass