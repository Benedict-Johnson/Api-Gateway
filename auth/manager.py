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
        from config.settings import settings

        if settings.DEMO_MODE:
            # TEMPORARY DOCUMENTATION / DEMO MODE: Bypass authentication for screenshot generation.
            # Must remain disabled (DEMO_MODE=false) in production environments!
            return {"client": "demo-client", "role": "admin"}

        for strategy in self.strategies:

            result = await strategy.authenticate(request)

            if result:
                return result

        return None
