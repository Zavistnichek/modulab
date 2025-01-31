import pytest
import sys
from fastapi.testclient import TestClient
from day_01.bmi_calculator import BMICalculator, app, cli_main

client = TestClient(app)


def test_normal_bmi():
    assert BMICalculator.calculate(70, 175) == 22.9


def test_invalid_height():
    assert BMICalculator.calculate(70, 40) is None


def test_boundary_values():
    assert BMICalculator.calculate(2.0, 50) == 8.0
    assert BMICalculator.calculate(635.0, 272) == 85.8
    assert BMICalculator.calculate(1.9, 50) is None
    assert BMICalculator.calculate(70, 49) is None


def test_validate_input():
    assert BMICalculator._validate_input(70, 175) is True
    assert BMICalculator._validate_input(1.9, 175) is False
    assert BMICalculator._validate_input(636, 175) is False
    assert BMICalculator._validate_input(70, 49) is False


def test_api_success():
    response = client.get("/bmi?weight=70&height_cm=175")
    assert response.status_code == 200
    assert response.json() == {"bmi": 22.9, "category": "Normal weight"}


def test_cli_invalid_input():
    sys.argv = ["bmi_calculator.py", "--weight", "70", "--height", "40"]
    with pytest.raises(SystemExit):
        cli_main()


def test_calculate_with_exception():
    with pytest.raises(ValueError):
        BMICalculator.calculate("70", "175")


def test_non_numeric_input():
    with pytest.raises(ValueError):
        BMICalculator.calculate("invalid", "input")


def test_calculate_logging_invalid_input(caplog):
    with pytest.raises(ValueError):
        BMICalculator.calculate("70", "175")
    assert "must be numbers" in caplog.text


def test_api_logging(caplog):
    with caplog.at_level("ERROR"):
        client.get("/bmi?weight=700&height_cm=175")
    assert "Weight must be between" in caplog.text
