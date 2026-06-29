from fastapi import Request

from auth.base import AuthenticationStrategy
from auth.jwt import JWTManager


class JWTStrategy(AuthenticationStrategy):

    def __init__(self):
        self.manager = JWTManager()

    async def authenticate(self, request: Request):

        auth = request.headers.get("Authorization")

        if not auth:
            return None

        if not auth.startswith("Bearer "):
            return None

        token = auth.split()[1]

        return self.manager.validate(token)