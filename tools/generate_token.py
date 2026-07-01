import jwt

from config.settings import settings

payload = {"sub": "freya", "role": "user"}

token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

print(token)
