import jwt

from config.settings import settings

ALGORITHM = "HS256"


class JWTManager:

    def validate(self, token: str):

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])

            return payload

        except jwt.InvalidTokenError:
            return None
