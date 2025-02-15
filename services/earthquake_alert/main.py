from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import httpx
import asyncio
from math import radians, sin, cos, sqrt, asin
import os
import uvicorn

app = FastAPI()


@app.get("/")
async def read_root() -> dict:
    return {"message": "Welcome to the earthquake_alert API!"}


class Earthquake(BaseModel):
    id: Optional[str] = None
    magnitude: float
    latitude: float
    longitude: float
    depth: float
    time: datetime
    location_description: str


db: List[Earthquake] = []
active_connections: List[WebSocket] = []


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the distance between two points on the Earth's surface in kilometers.
    Uses the Haversine formula.
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r


@app.websocket("/ws/earthquake-alerts")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for sending real-time earthquake alerts.
    """
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)


async def fetch_usgs_earthquakes() -> List[dict]:
    """
    Fetches earthquake data from the USGS API for the last hour.
    Returns a list of GeoJSON features.
    """
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get("features", [])
            else:
                print(f"Failed to fetch data: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error fetching data from USGS API: {e}")
            return []


def convert_usgs_to_earthquake(feature: dict) -> Earthquake:
    """
    Converts a USGS GeoJSON feature into an Earthquake object.
    """
    properties = feature["properties"]
    geometry = feature["geometry"]
    return Earthquake(
        id=feature["id"],
        magnitude=properties["mag"],
        latitude=geometry["coordinates"][1],
        longitude=geometry["coordinates"][0],
        depth=geometry["coordinates"][2],
        time=datetime.utcfromtimestamp(properties["time"] / 1000),
        location_description=properties["place"],
    )


async def update_earthquake_data():
    """
    Periodically fetches earthquake data from the USGS API and updates the database.
    Sends notifications to active WebSocket connections.
    """
    while True:
        print("Fetching earthquake data from USGS...")
        features = await fetch_usgs_earthquakes()
        for feature in features:
            try:
                earthquake = convert_usgs_to_earthquake(feature)
                if all(eq.id != earthquake.id for eq in db):  # Check for duplicates
                    db.append(earthquake)
                    for connection in active_connections:
                        await connection.send_json(earthquake.dict())
            except KeyError as e:
                print(f"Invalid data from USGS API: Missing key {e}")
        await asyncio.sleep(3600)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_earthquake_data())


@app.post("/earthquakes", response_model=Earthquake)
async def create_earthquake(earthquake: Earthquake):
    """
    Creates a new earthquake record and broadcasts it via WebSocket.
    """
    earthquake.id = str(uuid.uuid4())
    db.append(earthquake)
    for connection in active_connections:
        await connection.send_json(earthquake.dict())
    return earthquake


min_magnitude_query = Query(None, ge=0, le=10)
max_magnitude_query = Query(None, ge=0, le=10)
latitude_query = Query(None, ge=-90, le=90)
longitude_query = Query(None, ge=-180, le=180)
radius_km_query = Query(None, ge=0)
days_query = Query(30, gt=0)


@app.get("/earthquakes", response_model=List[Earthquake])
async def get_earthquakes(
    min_magnitude: Optional[float] = min_magnitude_query,
    max_magnitude: Optional[float] = max_magnitude_query,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    latitude: Optional[float] = latitude_query,
    longitude: Optional[float] = longitude_query,
    radius_km: Optional[float] = radius_km_query,
):
    """
    Returns a filtered list of earthquakes based on query parameters.
    """
    filtered = db.copy()
    if min_magnitude is not None:
        filtered = [eq for eq in filtered if eq.magnitude >= min_magnitude]
    if max_magnitude is not None:
        filtered = [eq for eq in filtered if eq.magnitude <= max_magnitude]
    if start_time is not None:
        filtered = [eq for eq in filtered if eq.time >= start_time]
    if end_time is not None:
        filtered = [eq for eq in filtered if eq.time <= end_time]
    if latitude is not None and longitude is not None and radius_km is not None:
        filtered = [
            eq
            for eq in filtered
            if calculate_distance(eq.latitude, eq.longitude, latitude, longitude)
            <= radius_km
        ]
    return filtered


@app.get("/earthquakes/recent", response_model=List[Earthquake])
async def get_recent_earthquakes(days: Optional[int] = days_query):
    """
    Returns earthquakes from the last N days (default: 30 days).
    """
    start_time = datetime.utcnow() - timedelta(days=days)
    return [eq for eq in db if eq.time >= start_time]


@app.get("/earthquakes/{earthquake_id}", response_model=Optional[Earthquake])
async def get_earthquake(earthquake_id: str):
    """
    Returns data for a specific earthquake by ID.
    Returns None if the earthquake is not found.
    """
    for eq in db:
        if eq.id == earthquake_id:
            return eq
    raise HTTPException(status_code=404, detail="Earthquake not found")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
