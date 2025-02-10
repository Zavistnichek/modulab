from pydantic import BaseModel
from typing import Optional


class PriceAlertRequest(BaseModel):
    crypto: str
    above: Optional[float] = None
    below: Optional[float] = None
    user: str = "default"


class PriceResponse(BaseModel):
    crypto: str
    price: str
