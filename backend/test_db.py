from app.utils.jwt import create_access_token, decode_access_token

token = create_access_token(
    {
        "sub": "123",
        "email": "admin@example.com",
    }
)

print(token)

payload = decode_access_token(token)

print(payload)