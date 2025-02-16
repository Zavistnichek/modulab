from fastapi.testclient import TestClient
from services.weather_alert.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the weather_alert API!"}


def test_post_weather_data():
    location = "Berlin"
    response = client.post(f"/weather/?location={location}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Weather data stored successfully"
    assert "data" in data
    assert data["data"]["location"] == location


def test_get_weather_alerts():
    """First, add weather data for testing"""
    client.post("/weather/?location=Berlin")
    client.post("/weather/?location=London")

    """Request alerts with threshold values"""
    response = client.get(
        "/alerts/?temp_threshold=20&humidity_threshold=50&wind_speed_threshold=10"
    )
    assert response.status_code == 200
    alerts = response.json()

    """Check that the response contains a list of alerts"""
    assert isinstance(alerts, list)
    for alert in alerts:
        assert "location" in alert
        assert "alerts" in alert
        assert isinstance(alert["alerts"], list)


def test_get_weather_alerts_no_thresholds():
    response = client.get("/alerts/")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "At least one threshold parameter must be provided"


def test_post_weather_data_invalid_location():
    location = "InvalidCity"
    response = client.post(f"/weather/?location={location}")
    assert response.status_code == 404
    data = response.json()
    assert (
        data["detail"] == f"Location {location!r} not found in predefined coordinates."
    )


def test_fetch_weather_data_api_error(monkeypatch):
    """Mock the requests.get method to simulate an API error"""

    def mock_response(*args, **kwargs):
        class MockResponse:
            status_code = 500

            def json(self):
                return {}

        return MockResponse()

    monkeypatch.setattr("requests.get", mock_response)

    location = "Berlin"
    response = client.post(f"/weather/?location={location}")
    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "Failed to fetch weather data from Open-Meteo API."
