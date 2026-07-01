from fastapi import Request

from auth.strategies.api_key_strategy import APIKeyStrategy
from auth.strategies.jwt_strategy import JWTStrategy


class AuthenticationManager:

    def __init__(self):

        self.strategies = [
            APIKeyStrategy(),
            JWTStrategy(),
        ]

    async def authenticate(self, request: Request):

        for strategy in self.strategies:

            result = await strategy.authenticate(request)

            if result:
                return result

        return None
