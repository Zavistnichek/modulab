import string
from fastapi.testclient import TestClient
from day_02.password_generator import app

client = TestClient(app)


def test_generate_password_length():
    response = client.get("/generate-password?length=12")
    assert response.status_code == 200
    assert len(response.json()["password"]) == 12


def test_generate_password_minimum_length():
    response = client.get("/generate-password?length=7")
    assert response.status_code == 400
    assert response.json()["detail"] == "Password length must be at least 8 characters."


def test_generate_password_secure():
    response = client.get("/generate-password?length=12")
    password = response.json()["password"]
    assert any(c.isupper() for c in password)
    assert any(c.islower() for c in password)
    assert any(c.isdigit() for c in password)
    assert any(c in string.punctuation for c in password)


def test_generate_password_length_override():
    response = client.get("/generate-password?length=20")
    assert response.status_code == 200
    assert len(response.json()["password"]) == 20


def test_generate_password_default():
    response = client.get("/generate-password")
    assert response.status_code == 200
    assert len(response.json()["password"]) == 12
