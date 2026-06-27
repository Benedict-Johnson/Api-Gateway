import jwt

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"


class JWTManager:

    def validate(self, token: str):

        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            return payload

        except jwt.InvalidTokenError:
            return None