from fastapi.testclient import TestClient
from services.qr_code_generator.main import app
from PIL import Image
from io import BytesIO

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the QR Code Generator API!"}


def test_generate_qr_success():
    data = {
        "data": "https://example.com",
        "version": 5,
        "box_size": 10,
        "border": 4,
        "error_correction": "H",
        "fill_color": "#FF5733",
        "back_color": "white",
    }
    response = client.post("/generate_qr/", json=data)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

    image = Image.open(BytesIO(response.content))
    assert image.format == "PNG"


def test_generate_qr_invalid_version():
    data = {
        "data": "https://example.com",
        "version": 50,
        "box_size": 10,
        "border": 4,
        "error_correction": "H",
        "fill_color": "#FF5733",
        "back_color": "white",
    }
    response = client.post("/generate_qr/", json=data)
    assert response.status_code == 400
    assert "Version must be between 1 and 40" in response.json()["detail"]


def test_generate_qr_invalid_border():
    data = {
        "data": "https://example.com",
        "version": 5,
        "box_size": 10,
        "border": 2,
        "error_correction": "H",
        "fill_color": "#FF5733",
        "back_color": "white",
    }
    response = client.post("/generate_qr/", json=data)
    assert response.status_code == 400
    assert "Border must be at least 4 modules" in response.json()["detail"]


def test_generate_qr_invalid_error_correction():
    data = {
        "data": "https://example.com",
        "version": 5,
        "box_size": 10,
        "border": 4,
        "error_correction": "X",
        "fill_color": "#FF5733",
        "back_color": "white",
    }
    response = client.post("/generate_qr/", json=data)
    assert response.status_code == 400
    assert "Invalid error correction level" in response.json()["detail"]


def test_generate_qr_invalid_color():
    data = {
        "data": "https://example.com",
        "version": 5,
        "box_size": 10,
        "border": 4,
        "error_correction": "H",
        "fill_color": "invalid_color",
        "back_color": "white",
    }
    response = client.post("/generate_qr/", json=data)
    assert response.status_code == 400
    assert "Color error" in response.json()["detail"]


def test_generate_qr_data_overflow():
    data = {
        "data": "A" * 10000,
        "version": 1,
        "box_size": 10,
        "border": 4,
        "error_correction": "L",
        "fill_color": "black",
        "back_color": "white",
    }
    response = client.post("/generate_qr/", json=data)
    assert response.status_code == 400
    assert "Data is too large for the selected version" in response.json()["detail"]
