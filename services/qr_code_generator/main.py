from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import qrcode
from qrcode.constants import (
    ERROR_CORRECT_L,
    ERROR_CORRECT_M,
    ERROR_CORRECT_Q,
    ERROR_CORRECT_H,
)
from qrcode.exceptions import DataOverflowError
from io import BytesIO
from PIL import ImageColor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="QR Code Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the QR Code Generator API!"}


class QRCodeRequest(BaseModel):
    data: str
    version: Optional[int] = None
    box_size: int = 10
    border: int = 4
    error_correction: str = "L"
    fill_color: str = "black"
    back_color: str = "white"

    class Config:
        schema_extra = {
            "example": {
                "data": "https://example.com",
                "version": 5,
                "box_size": 10,
                "border": 4,
                "error_correction": "H",
                "fill_color": "#FF5733",
                "back_color": "white",
            }
        }


ERROR_CORRECTION_MAP = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}


@app.post(
    "/generate_qr/",
    response_class=Response,
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Returns a PNG image of the QR code",
        },
        400: {"description": "Invalid request parameters"},
    },
)
async def generate_qr(request: QRCodeRequest):
    """
    Generates a QR code with the specified parameters:
    - **data**: Data to encode (required)
    - **version**: QR code version (1-40, optional)
    - **box_size**: Size of each module in pixels (default 10)
    - **border**: Border size in modules (minimum 4)
    - **error_correction**: Error correction level (L, M, Q, H)
    - **fill_color**: Module color (name or HEX)
    - **back_color**: Background color (name or HEX)
    """
    if request.version is not None and not 1 <= request.version <= 40:
        raise HTTPException(400, "Version must be between 1 and 40")

    if request.border < 4:
        raise HTTPException(400, "Border must be at least 4 modules")

    ec = ERROR_CORRECTION_MAP.get(request.error_correction.upper())
    if not ec:
        raise HTTPException(
            400,
            "Invalid error correction level. " "Allowed values: L, M, Q, H",
        )

    try:
        fill = ImageColor.getrgb(request.fill_color)
        back = ImageColor.getrgb(request.back_color)
    except ValueError as e:
        raise HTTPException(400, f"Color error: {str(e)}") from e

    qr = qrcode.QRCode(
        version=request.version,
        error_correction=ec,
        box_size=request.box_size,
        border=request.border,
    )

    qr.add_data(request.data)

    try:
        qr.make(fit=request.version is None)
    except DataOverflowError as e:
        raise HTTPException(
            400,
            "Data is too large for the selected version. "
            "Increase the version or error correction level",
        ) from e

    img = qr.make_image(fill_color=fill, back_color=back)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="image/png",
        headers={"Content-Disposition": "attachment; filename=qrcode.png"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
