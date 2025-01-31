#!/usr/bin/env python3
"""
BMI Calculator with input validation and professional error handling
"""

import argparse
import logging
import sys
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
import uvicorn
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()


class BMICalculator:
    """Class for BMI calculation with data validation"""

    MIN_WEIGHT = 2.0  # kg
    MAX_WEIGHT = 635.0  # Guinness record
    MIN_HEIGHT = 50  # centimeters
    MAX_HEIGHT = 272  # Guinness record

    @classmethod
    def calculate(cls, weight: float, height_cm: float) -> Optional[float]:
        """
        Calculates BMI with input parameter validation

        Args:
            weight: weight in kilograms
            height_cm: height in centimeters

        Returns:
            float: BMI value or None in case of error
        """
        try:
            if not isinstance(weight, (float, int)) or not isinstance(
                height_cm, (float, int)
            ):
                raise ValueError(
                    "Both weight and height must be numbers (int or float)."
                )

            if not cls._validate_input(weight, height_cm):
                return None

            height_m = height_cm / 100  # Convert height to meters
            return round(weight / (height_m**2), 1)

        except ValueError as ve:
            logger.error(f"Input error: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Calculation error: {str(e)}")
            return None

    @classmethod
    def _validate_input(cls, weight: float, height_cm: float) -> bool:
        """Validates input data"""
        if not (cls.MIN_WEIGHT <= weight <= cls.MAX_WEIGHT):
            logger.error(
                f"Weight must be between {cls.MIN_WEIGHT} and {cls.MAX_WEIGHT} kg"
            )
            return False

        if not (cls.MIN_HEIGHT <= height_cm <= cls.MAX_HEIGHT):
            logger.error(
                f"Height must be between {cls.MIN_HEIGHT} and {cls.MAX_HEIGHT} cm"
            )
            return False

        return True


@app.get("/")
def read_root():
    return {"message": "Welcome to the BMI Calculator!"}


@app.get("/bmi")
def calculate_bmi(weight: float, height_cm: float):
    """
    Calculate BMI via HTTP GET request.

    Args:
        weight (float): Weight in kilograms.
        height_cm (float): Height in centimeters.

    Returns:
        dict: BMI value and category.
    """
    try:
        bmi = BMICalculator.calculate(weight, height_cm)
        if bmi is None:
            raise HTTPException(status_code=400, detail="Invalid input parameters")

        category = "Unknown"
        if bmi < 18.5:
            category = "Underweight"
        elif 18.5 <= bmi < 25:
            category = "Normal weight"
        elif 25 <= bmi < 30:
            category = "Overweight"
        else:
            category = "Obesity"

        return {"bmi": bmi, "category": category}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


def get_args() -> argparse.Namespace:
    """Gets arguments via command line or interactive input"""
    parser = argparse.ArgumentParser(
        description="Calculate Body Mass Index (BMI)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("-w", "--weight", type=float, help="Weight in kilograms")
    parser.add_argument("-H", "--height", type=float, help="Height in centimeters")

    args = parser.parse_args()

    if args.weight is None:
        args.weight = float(input("Enter weight (kg): "))
    if args.height is None:
        args.height = float(input("Enter height (cm): "))

    return args


def main() -> None:
    """Main program logic for CLI usage"""
    args = get_args()
    bmi = BMICalculator.calculate(args.weight, args.height)

    if bmi is not None:
        logger.info(f"Your BMI: {bmi}")
        logger.info("BMI Categories:")
        logger.info("Underweight = <18.5")
        logger.info("Normal weight = 18.5–24.9")
        logger.info("Overweight = 25–29.9")
        logger.info("Obesity = BMI of 30 or greater")
    else:
        sys.exit(1)


def cli_main():
    """Entry point for CLI usage."""
    if len(sys.argv) > 1:
        main()
    else:
        port = int(os.getenv("PORT", 5000))
        uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    cli_main()
