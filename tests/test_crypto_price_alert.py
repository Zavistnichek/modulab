import pytest
from fastapi.testclient import TestClient
from services.crypto_price_alert.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_price():
    response = client.get("/price/bitcoin")
    assert response.status_code == 200
    data = response.json()
    assert "crypto" in data
    assert "price" in data
    assert data["crypto"] == "bitcoin"


@pytest.mark.asyncio
async def test_set_price_alert():
    response = client.post(
        "/set_alert/",
        json={"crypto": "ethereum", "above": 5000, "user": "test_user"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Alert for ethereum has been set!"


@pytest.mark.asyncio
async def test_websocket_alerts():
    with client.websocket_connect("/ws") as websocket:
        message = websocket.receive_text()
        assert isinstance(message, str)
        assert "Checking alerts" in message or "USD" in message


@pytest.mark.asyncio
async def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to the crypto_price_alert API!"


@pytest.mark.asyncio
async def test_get_price_invalid_crypto():
    response = client.get("/price/invalid_crypto")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Failed to retrieve the price"


@pytest.mark.asyncio
async def test_set_price_alert_invalid():
    response = client.post(
        "/set_alert/",
        json={"crypto": "bitcoin", "user": "test_user"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "At least one of 'above' or 'below' must be provided."
