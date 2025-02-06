import os
import uuid
from fastapi.testclient import TestClient
from services.text_to_speech.main import (
    app,
    AUDIO_DIR,
    SUPPORTED_LANGUAGES,
    MAX_TEXT_LENGTH,
)
import pytest

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_audio_dir():
    for file in os.listdir(AUDIO_DIR):
        file_path = os.path.join(AUDIO_DIR, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the text-to-speech API!"}


def test_text_to_speech_success():
    test_text = "Hello world"
    response = client.post("/text-to-speech", data={"text": test_text, "lang": "en"})
    assert response.status_code == 200
    data = response.json()
    assert "audio_url" in data
    assert data["audio_url"].startswith("/download/")
    assert data["audio_url"].endswith(".mp3")

    filename = data["audio_url"].split("/")[-1]
    assert os.path.exists(os.path.join(AUDIO_DIR, filename))


def test_text_too_long():
    long_text = "a" * (MAX_TEXT_LENGTH + 1)
    response = client.post("/text-to-speech", data={"text": long_text, "lang": "en"})
    assert response.status_code == 400
    assert "Text is too long" in response.json()["detail"]


def test_unsupported_language():
    response = client.post("/text-to-speech", data={"text": "Hello", "lang": "xx"})
    assert response.status_code == 400
    assert "is not supported" in response.json()["detail"]


def test_download_audio():
    test_text = "Test download"
    response = client.post("/text-to-speech", data={"text": test_text, "lang": "en"})
    filename = response.json()["audio_url"].split("/")[-1]

    response = client.get(f"/download/{filename}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert int(response.headers["content-length"]) > 0


def test_download_nonexistent_file():
    fake_filename = str(uuid.uuid4()) + ".mp3"
    response = client.get(f"/download/{fake_filename}")
    assert response.status_code == 404
    assert "File not found" in response.json()["detail"]


def test_list_audio_files():
    test_files = []
    for _ in range(3):
        response = client.post("/text-to-speech", data={"text": "test", "lang": "en"})
        test_files.append(response.json()["audio_url"].split("/")[-1])

    response = client.get("/list-audio")
    assert response.status_code == 200
    listed_files = response.json()["audio_files"]
    assert len(listed_files) == 3
    for f in test_files:
        assert f in listed_files


def test_delete_audio():
    response = client.post("/text-to-speech", data={"text": "To delete", "lang": "en"})
    filename = response.json()["audio_url"].split("/")[-1]

    response = client.delete(f"/delete-audio/{filename}")
    assert response.status_code == 200
    assert "successfully" in response.json()["message"]

    assert not os.path.exists(os.path.join(AUDIO_DIR, filename))
    response = client.get("/list-audio")
    assert filename not in response.json()["audio_files"]


def test_delete_nonexistent_file():
    fake_filename = "nonexistent.mp3"
    response = client.delete(f"/delete-audio/{fake_filename}")
    assert response.status_code == 404
    assert "File not found" in response.json()["detail"]


def test_language_support():
    for lang in SUPPORTED_LANGUAGES:
        response = client.post("/text-to-speech", data={"text": "test", "lang": lang})
        assert response.status_code == 200


def test_audio_generation_failure():
    response = client.post("/text-to-speech", data={"text": "", "lang": "en"})
    assert response.status_code == 500
