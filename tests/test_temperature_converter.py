import pytest
from fastapi.testclient import TestClient
from services.temperature_converter.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_celsius_to_fahrenheit(client):
    response = client.get("/convert?value=0&from_scale=celsius&to_scale=fahrenheit")
    assert response.status_code == 200
    assert response.json() == {
        "original_value": 0,
        "from_scale": "celsius",
        "to_scale": "fahrenheit",
        "converted_value": 32,
    }


def test_fahrenheit_to_celsius(client):
    response = client.get("/convert?value=32&from_scale=fahrenheit&to_scale=celsius")
    assert response.status_code == 200
    assert response.json() == {
        "original_value": 32,
        "from_scale": "fahrenheit",
        "to_scale": "celsius",
        "converted_value": 0,
    }


def test_kelvin_to_celsius(client):
    response = client.get("/convert?value=273.15&from_scale=kelvin&to_scale=celsius")
    assert response.status_code == 200
    assert response.json() == {
        "original_value": 273.15,
        "from_scale": "kelvin",
        "to_scale": "celsius",
        "converted_value": 0,
    }


def test_celsius_to_kelvin(client):
    response = client.get("/convert?value=0&from_scale=celsius&to_scale=kelvin")
    assert response.status_code == 200
    assert response.json() == {
        "original_value": 0,
        "from_scale": "celsius",
        "to_scale": "kelvin",
        "converted_value": 273.15,
    }


def test_fahrenheit_to_kelvin(client):
    response = client.get("/convert?value=32&from_scale=fahrenheit&to_scale=kelvin")
    assert response.status_code == 200
    assert response.json() == {
        "original_value": 32,
        "from_scale": "fahrenheit",
        "to_scale": "kelvin",
        "converted_value": 273.15,
    }


def test_invalid_from_scale(client):
    response = client.get("/convert?value=0&from_scale=invalid_scale&to_scale=celsius")
    assert response.status_code == 400
    assert "Invalid 'from_scale'" in response.json()["detail"]


def test_invalid_to_scale(client):
    response = client.get("/convert?value=0&from_scale=celsius&to_scale=invalid_scale")
    assert response.status_code == 400
    assert "Invalid 'to_scale'" in response.json()["detail"]


def test_same_scale_conversion(client):
    response = client.get("/convert?value=0&from_scale=celsius&to_scale=celsius")
    assert response.status_code == 200
    assert response.json() == {
        "original_value": 0,
        "from_scale": "celsius",
        "to_scale": "celsius",
        "converted_value": 0,
    }
