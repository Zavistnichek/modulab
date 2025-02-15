import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from services.earthquake_alert.main import app, db, active_connections

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    """Clears the database before each test."""
    db.clear()
    active_connections.clear()


def test_read_root():
    """Test for the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the eathquake_alert API!"}


def test_create_earthquake():
    """Test for creating a new earthquake."""
    earthquake_data = {
        "magnitude": 5.5,
        "latitude": 34.0522,
        "longitude": -118.2437,
        "depth": 10.0,
        "time": datetime.utcnow().isoformat(),
        "location_description": "Los Angeles",
    }
    response = client.post("/earthquakes", json=earthquake_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["magnitude"] == 5.5
    assert data["location_description"] == "Los Angeles"


def test_get_earthquakes():
    """Test for retrieving a list of earthquakes."""
    earthquake_data = {
        "id": "test_id_1",
        "magnitude": 6.0,
        "latitude": 34.0522,
        "longitude": -118.2437,
        "depth": 10.0,
        "time": datetime.utcnow().isoformat(),
        "location_description": "Los Angeles",
    }
    db.append(earthquake_data)

    response = client.get("/earthquakes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "test_id_1"


def test_filter_earthquakes_by_magnitude():
    """Test for filtering earthquakes by magnitude."""
    earthquake_data_1 = {
        "id": "test_id_1",
        "magnitude": 5.0,
        "latitude": 34.0522,
        "longitude": -118.2437,
        "depth": 10.0,
        "time": datetime.utcnow().isoformat(),
        "location_description": "Los Angeles",
    }
    earthquake_data_2 = {
        "id": "test_id_2",
        "magnitude": 7.0,
        "latitude": 34.0522,
        "longitude": -118.2437,
        "depth": 10.0,
        "time": datetime.utcnow().isoformat(),
        "location_description": "San Francisco",
    }
    db.extend([earthquake_data_1, earthquake_data_2])

    response = client.get("/earthquakes?min_magnitude=6.0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "test_id_2"


def test_websocket_connection():
    """Test for WebSocket connection."""
    with client.websocket_connect("/ws/earthquake-alerts") as websocket:
        websocket.send_text("ping")
        assert len(active_connections) == 1


def test_get_earthquake_by_id():
    """Test for retrieving an earthquake by ID."""
    earthquake_data = {
        "id": "test_id_1",
        "magnitude": 5.5,
        "latitude": 34.0522,
        "longitude": -118.2437,
        "depth": 10.0,
        "time": datetime.utcnow().isoformat(),
        "location_description": "Los Angeles",
    }
    db.append(earthquake_data)

    response = client.get("/earthquakes/test_id_1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test_id_1"
    assert data["location_description"] == "Los Angeles"
