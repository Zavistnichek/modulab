from fastapi.testclient import TestClient
from services.word_counter.main import app


client = TestClient(app)


def test_read_root():
    """
    Test for the root endpoint "/"
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the word_counter API!"}


def test_word_count():
    """
    Test for the endpoint "/word_count/"
    """
    response = client.post(
        "/word_count/", json={"text": "Hello world! This is a test."}
    )
    assert response.status_code == 200
    assert response.json() == {"word_count": 6}

    response = client.post("/word_count/", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == {"word_count": 0}

    response = client.post("/word_count/", json={"text": "   Hello   world!   "})
    assert response.status_code == 200
    assert response.json() == {"word_count": 2}

    response = client.post(
        "/word_count/", json={"text": "Hello\nworld!\nThis is a test."}
    )
    assert response.status_code == 200
    assert response.json() == {"word_count": 6}


def test_word_count_invalid_input():
    """
    Test for handling invalid input data
    """
    response = client.post("/word_count/", json={})
    assert response.status_code == 422  # Unprocessable Entity

    response = client.post("/word_count/", json={"text": 12345})
    assert response.status_code == 422  # Unprocessable Entity
