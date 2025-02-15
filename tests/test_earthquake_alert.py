import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from services.earthquake_alert.main import app, db, active_connections, Earthquake

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    """
    Clears the database and active connections before each test.
    Ensures a clean state for every test case.
    """
    db.clear()
    active_connections.clear()


def create_earthquake(
    id: str,
    magnitude: float,
    latitude: float,
    longitude: float,
    depth: float,
    location_description: str,
) -> Earthquake:
    """
    Helper function to create an Earthquake object with default values.
    Simplifies the creation of test data.
    """
    return Earthquake(
        id=id,
        magnitude=magnitude,
        latitude=latitude,
        longitude=longitude,
        depth=depth,
        time=datetime.utcnow(),
        location_description=location_description,
    )


def test_read_root():
    """
    Test for the root endpoint.
    Verifies that the root endpoint returns the expected welcome message.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the earthquake_alert API!"}


def test_get_earthquakes():
    """
    Test for retrieving a list of earthquakes.
    Verifies that the endpoint returns all earthquakes stored in the database.
    """
    earthquake = create_earthquake(
        id="test_id_1",
        magnitude=6.0,
        latitude=34.0522,
        longitude=-118.2437,
        depth=10.0,
        location_description="Los Angeles",
    )
    db.append(earthquake)

    response = client.get("/earthquakes")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == "test_id_1"
    assert data[0]["location_description"] == "Los Angeles"


def test_filter_earthquakes_by_magnitude():
    """
    Test for filtering earthquakes by magnitude.
    Verifies that the endpoint correctly filters
    earthquakes based on the `min_magnitude` parameter.
    """
    earthquake_1 = create_earthquake(
        id="test_id_1",
        magnitude=5.0,
        latitude=34.0522,
        longitude=-118.2437,
        depth=10.0,
        location_description="Los Angeles",
    )
    earthquake_2 = create_earthquake(
        id="test_id_2",
        magnitude=7.0,
        latitude=34.0522,
        longitude=-118.2437,
        depth=10.0,
        location_description="San Francisco",
    )
    db.extend([earthquake_1, earthquake_2])

    response = client.get("/earthquakes?min_magnitude=6.0")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == "test_id_2"
    assert data[0]["magnitude"] == 7.0


def test_get_earthquake_by_id():
    """
    Test for retrieving an earthquake by ID.
    Verifies that the endpoint returns the correct earthquake when queried by ID.
    """
    earthquake = create_earthquake(
        id="test_id_1",
        magnitude=5.5,
        latitude=34.0522,
        longitude=-118.2437,
        depth=10.0,
        location_description="Los Angeles",
    )
    db.append(earthquake)

    response = client.get("/earthquakes/test_id_1")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == "test_id_1"
    assert data["magnitude"] == 5.5
    assert data["location_description"] == "Los Angeles"


def test_get_nonexistent_earthquake():
    """
    Test for attempting to retrieve a non-existent earthquake.
    Verifies that the endpoint returns a 404 status code
    and an appropriate error message.
    """
    response = client.get("/earthquakes/nonexistent_id")
    assert response.status_code == 404
    data = response.json()

    # Validate the response
    assert data["detail"] == "Earthquake not found"


def test_get_recent_earthquakes():
    """
    Test for retrieving recent earthquakes.
    Verifies that the endpoint returns earthquakes from the last N days.
    """
    recent_time = datetime.utcnow() - timedelta(days=10)
    old_time = datetime.utcnow() - timedelta(days=40)

    earthquake_1 = create_earthquake(
        id="test_id_1",
        magnitude=5.0,
        latitude=34.0522,
        longitude=-118.2437,
        depth=10.0,
        location_description="Los Angeles",
    )
    earthquake_1.time = recent_time  # Set the time to 10 days ago

    earthquake_2 = create_earthquake(
        id="test_id_2",
        magnitude=7.0,
        latitude=34.0522,
        longitude=-118.2437,
        depth=10.0,
        location_description="San Francisco",
    )
    earthquake_2.time = old_time  # Set the time to 40 days ago

    db.extend([earthquake_1, earthquake_2])

    response = client.get("/earthquakes/recent?days=30")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == "test_id_1"
