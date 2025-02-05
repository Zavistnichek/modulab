from fastapi import FastAPI, HTTPException
import uvicorn
import os
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEMPERATURE_SCALES = {"celsius", "fahrenheit", "kelvin"}


def convert_temperature_general(value: float, from_scale: str, to_scale: str) -> float:
    """Function converts temperature between any scales."""
    if from_scale == to_scale:
        return value

    if from_scale == "fahrenheit":
        value = (value - 32) * 5 / 9
        logger.debug(f"Converted from Fahrenheit to Celsius: {value}")
    elif from_scale == "kelvin":
        value = value - 273.15
        logger.debug(f"Converted from Kelvin to Celsius: {value}")

    if to_scale == "fahrenheit":
        value = value * 9 / 5 + 32
        logger.debug(f"Converted from Celsius to Fahrenheit: {value}")
    elif to_scale == "kelvin":
        value = value + 273.15
        logger.debug(f"Converted from Celsius to Kelvin: {value}")

    return value


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the temperature_converter API!"}


@app.get("/convert")
def convert_temperature(value: float, from_scale: str, to_scale: str):
    logger.info(f"Received request for conversion: {value} {from_scale} -> {to_scale}")
    from_scale = from_scale.lower()
    to_scale = to_scale.lower()

    if from_scale not in TEMPERATURE_SCALES:
        error_message = (
            f"Invalid 'from_scale': {from_scale}. Use one of {TEMPERATURE_SCALES}."
        )
        logger.error(error_message)
        raise HTTPException(status_code=400, detail=error_message)

    if to_scale not in TEMPERATURE_SCALES:
        error_message = (
            f"Invalid 'to_scale': {to_scale}. Use one of {TEMPERATURE_SCALES}."
        )
        logger.error(error_message)
        raise HTTPException(status_code=400, detail=error_message)

    logger.debug(f"Conversion parameters: {value} {from_scale} -> {to_scale}")
    converted_value = convert_temperature_general(value, from_scale, to_scale)
    logger.info(
        f"Conversion completed: {value} {from_scale} -> {converted_value} {to_scale}"
    )

    return {
        "original_value": value,
        "from_scale": from_scale,
        "to_scale": to_scale,
        "converted_value": converted_value,
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
