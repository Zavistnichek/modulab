from pydantic import BaseModel


class PriceAlertRequest(BaseModel):
    crypto: str
    above: float = None
    below: float = None
    user: str = "default"


class PriceResponse(BaseModel):
    crypto: str
    price: str
