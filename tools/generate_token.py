import jwt

SECRET_KEY = "super-secret-key"

payload = {
    "sub": "freya",
    "role": "user"
}

token = jwt.encode(
    payload,
    SECRET_KEY,
    algorithm="HS256"
)

print(token)