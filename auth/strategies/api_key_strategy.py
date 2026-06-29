from fastapi import Request

from auth.api_key import APIKeyManager
from auth.base import AuthenticationStrategy


class APIKeyStrategy(AuthenticationStrategy):

    def __init__(self):
        self.manager = APIKeyManager("config/api_keys.yaml")

    async def authenticate(self, request: Request):

        key = request.headers.get("X-API-Key")

        if not key:
            return None

        api_key = self.manager.validate(key)

        if api_key is None:
            return None

        return {
            "client": api_key.client,
            "role": "admin"  # Temporary until API keys support roles
        }