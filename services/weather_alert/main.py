from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import uvicorn
import requests

app = FastAPI()
weather_data_db = {}


@app.get("/")
def read_root():
    return {"message": "Welcome to the weather_alert API!"}


class WeatherData(BaseModel):
    location: str
    temperature: float
    humidity: float
    wind_speed: float
    timestamp: datetime = Field(default_factory=datetime.now)


class WeatherAlertResponse(BaseModel):
    location: str
    alerts: List[str]


def fetch_weather_data(location: str):
    """Fetch weather data from Open-Meteo API for a given location."""
    url = "https://api.open-meteo.com/v1/forecast"
    location_coords = {
        "Berlin": {"latitude": 52.52, "longitude": 13.405},
        "London": {"latitude": 51.5074, "longitude": -0.1278},
        "Paris": {"latitude": 48.8566, "longitude": 2.3522},
    }

    if location not in location_coords:
        raise HTTPException(
            status_code=404,
            detail=f"Location {location!r} not found in predefined coordinates.",
        )

    params = {
        "latitude": location_coords[location]["latitude"],
        "longitude": location_coords[location]["longitude"],
        "hourly": "temperature_2m,relative_humidity_2m,windspeed_10m",
        "timezone": "auto",
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(
            status_code=500, detail="Failed to fetch weather data from Open-Meteo API."
        )

    data = response.json()
    time_index = data["hourly"]["time"].index(max(data["hourly"]["time"]))
    temperature = data["hourly"]["temperature_2m"][time_index]
    humidity = data["hourly"]["relative_humidity_2m"][time_index]
    wind_speed = data["hourly"]["windspeed_10m"][time_index]

    return WeatherData(
        location=location,
        temperature=temperature,
        humidity=humidity,
        wind_speed=wind_speed,
        timestamp=datetime.now(),
    )


@app.post("/weather/")
async def post_weather_data(location: str):
    """Fetch and store weather data for a location using Open-Meteo API."""
    try:
        weather_data = fetch_weather_data(location)
        weather_data_db[weather_data.location] = weather_data
        return {
            "message": "Weather data stored successfully",
            "data": weather_data.dict(),
        }
    except HTTPException as e:
        raise e


@app.get("/alerts/", response_model=List[WeatherAlertResponse])
async def get_weather_alerts(
    temp_threshold: Optional[float] = None,
    humidity_threshold: Optional[float] = None,
    wind_speed_threshold: Optional[float] = None,
):
    """Get locations with weather conditions exceeding thresholds"""
    alerts = []
    if all(
        t is None for t in [temp_threshold, humidity_threshold, wind_speed_threshold]
    ):
        raise HTTPException(
            status_code=400, detail="At least one threshold parameter must be provided"
        )
    for location, data in weather_data_db.items():
        triggered_alerts = []
        if temp_threshold is not None and data.temperature > temp_threshold:
            triggered_alerts.append("temperature")
        if humidity_threshold is not None and data.humidity > humidity_threshold:
            triggered_alerts.append("humidity")
        if wind_speed_threshold is not None and data.wind_speed > wind_speed_threshold:
            triggered_alerts.append("wind_speed")
        if triggered_alerts:
            alerts.append(
                WeatherAlertResponse(location=location, alerts=triggered_alerts)
            )
    return alerts


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
