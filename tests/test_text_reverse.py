from fastapi.testclient import TestClient
from services.text_reverse.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the text_reverse API!"}


def test_reverse_text():
    response = client.post("/text_reverse", json={"text": "Hello, World!"})
    assert response.status_code == 200
    assert response.json() == {"reversed_text": "!dlroW ,olleH"}


def test_reverse_empty_text():
    response = client.post("/text_reverse", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == {"reversed_text": ""}


def test_reverse_text_with_spaces():
    response = client.post("/text_reverse", json={"text": "   "})
    assert response.status_code == 200
    assert response.json() == {"reversed_text": "   "}


def test_reverse_unicode_text():
    response = client.post("/text_reverse", json={"text": "Привет, мир!"})
    assert response.status_code == 200
    assert response.json() == {"reversed_text": "!рим ,тевирП"}
