import os
from fastapi.testclient import TestClient
from services.language_translator.main import app

client = TestClient(app)

os.environ["DEEPL_API_KEY"] = "dummy_api_key"


def test_read_root():
    """
    Test the root endpoint.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the language_translator API!"}


def test_translate_text_success(mocker):
    """
    Test successful translation.
    """
    mock_translate = mocker.patch("deep_translator.DeeplTranslator.translate")
    mock_translate.return_value = "Bonjour"
    mocker.patch("deep_translator.DeeplTranslator.__init__", return_value=None)
    response = client.post(
        "/translate/", json={"text": "Hello", "target_language": "fr"}
    )

    assert response.status_code == 200
    assert response.json() == {"translated_text": "Bonjour"}


def test_translate_text_failure(mocker):
    """
    Test translation failure due to an exception.
    """
    mocker.patch(
        "deep_translator.DeeplTranslator.translate",
        side_effect=Exception("Translation error"),
    )
    mocker.patch("deep_translator.DeeplTranslator.__init__", return_value=None)
    response = client.post(
        "/translate/", json={"text": "Hello", "target_language": "fr"}
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Translation failed: Translation error"}


def test_get_supported_languages_success(mocker):
    """
    Test successful fetching of supported languages.
    """
    mock_get_supported_languages = mocker.patch(
        "deep_translator.DeeplTranslator.get_supported_languages"
    )
    mock_get_supported_languages.return_value = {"en": "English", "fr": "French"}
    mocker.patch("deep_translator.DeeplTranslator.__init__", return_value=None)
    response = client.get("/languages/")
    assert response.status_code == 200
    assert response.json() == {"supported_languages": {"en": "English", "fr": "French"}}


def test_get_supported_languages_failure(mocker):
    """
    Test failure when fetching supported languages.
    """
    mocker.patch(
        "deep_translator.DeeplTranslator.get_supported_languages",
        side_effect=Exception("Failed to fetch languages"),
    )
    mocker.patch("deep_translator.DeeplTranslator.__init__", return_value=None)
    response = client.get("/languages/")
    assert response.status_code == 500
    assert response.json() == {
        "detail": "Failed to fetch supported languages: Failed to fetch languages"
    }
