from fastapi import FastAPI, WebSocket, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Lock
from contextlib import asynccontextmanager
from .models import PriceAlertRequest, PriceResponse
from .utils import get_crypto_price, format_crypto_price
import asyncio
from typing import Dict, Any

scheduler = BackgroundScheduler()
scheduler.start()
price_alerts = {}
lock = Lock()
price_alerts: Dict[str, Dict[str, Dict[str, Any]]] = {}


def check_price_alerts():
    """Checks if the prices have reached the limits set by users."""
    with lock:
        for crypto, alert_data in price_alerts.items():
            current_price = get_crypto_price(crypto)
            if current_price:
                formatted_price = format_crypto_price(current_price)
                for user, alert_price in alert_data.items():
                    if (
                        alert_price["above"] and current_price >= alert_price["above"]
                    ) or (
                        alert_price["below"] and current_price <= alert_price["below"]
                    ):
                        print(
                            f"🔔 Alert for {user}: {crypto} has reached "
                            f"{formatted_price} USD!"
                        )


scheduler.add_job(check_price_alerts, "interval", seconds=30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events."""
    try:
        yield
    finally:
        scheduler.shutdown()


app = FastAPI(lifespan=lifespan)


@app.get("/price/{crypto}", response_model=PriceResponse)
def get_price(crypto: str):
    """Returns the current price of the cryptocurrency."""
    price = get_crypto_price(crypto)
    if price is not None:
        formatted_price = format_crypto_price(price)
        return {"crypto": crypto, "price": formatted_price}
    raise HTTPException(status_code=404, detail="Failed to retrieve the price")


@app.post("/set_alert/")
def set_price_alert(request: PriceAlertRequest):
    """Sets a price alert for the user."""
    if not request.above and not request.below:
        raise HTTPException(
            status_code=400,
            detail="At least one of 'above' or 'below' must be provided.",
        )
    with lock:
        if request.crypto not in price_alerts:
            price_alerts[request.crypto] = {}
        price_alerts[request.crypto][request.user] = {
            "above": request.above,
            "below": request.below,
        }
    return {"message": f"Alert for {request.crypto} has been set!"}


@app.websocket("/ws")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket for sending real-time alerts."""
    await websocket.accept()
    try:
        while True:
            with lock:
                for crypto, _alert_data in price_alerts.items():
                    price = get_crypto_price(crypto)
                    if price:
                        formatted_price = format_crypto_price(price)
                        await websocket.send_text(f"🔔 {crypto}: {formatted_price} USD")
            await websocket.send_text("🔔 Checking alerts...")
            await asyncio.sleep(30)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()


@app.get("/")
async def read_root():
    return {"message": "Welcome to the crypto_price_alert API!"}
