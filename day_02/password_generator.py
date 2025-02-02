import string
import secrets
import logging
import uvicorn
import os

from fastapi import FastAPI, HTTPException

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    logger.info(f"Generating password of length {length}")
    if length < 8 or length > 64:
        raise HTTPException(
            status_code=400,
            detail="Password length must be between 8 and 64 characters.",
        )

    while True:
        password = generate_password(length)
        if is_password_secure(password):
            return {"password": password}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Render automatically assigns port
    uvicorn.run(app, host="0.0.0.0", port=port)
