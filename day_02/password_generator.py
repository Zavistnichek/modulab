from fastapi import FastAPI, HTTPException
import string
import secrets

app = FastAPI()


def generate_password(length: int = 12) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for _ in range(length))


def is_password_secure(password: str) -> bool:
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in string.punctuation for c in password)
    return has_upper and has_lower and has_digit and has_special


@app.get("/generate-password")
def generate_secure_password(length: int = 12):
    if length < 8:
        raise HTTPException(
            status_code=400, detail="Password length must be at least 8 characters."
        )

    while True:
        password = generate_password(length)
        if is_password_secure(password):
            return {"password": password}
