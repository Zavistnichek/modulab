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


def test_api_missing_input():
    response = client.get("/bmi")
    assert response.status_code == 422


def test_calculate_bmi_with_invalid_type():
    with pytest.raises(ValueError):
        BMICalculator.calculate(None, 175)

    with pytest.raises(ValueError):
        BMICalculator.calculate(70, None)


def test_cli_main_without_args(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda x: "70" if "weight" in x else "175")

    with pytest.raises(SystemExit):
        cli_main()


def test_bmi_calculator_with_invalid_weight():
    assert BMICalculator.calculate(636, 175) is None
    assert BMICalculator.calculate(70, 273) is None


def test_cli_main_with_valid_args(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda x: "70" if "weight" in x else "175")
    sys.argv = ["bmi_calculator.py", "--weight", "70", "--height", "175"]
    cli_main()


def test_cli_with_invalid_string_input():
    sys.argv = ["bmi_calculator.py", "--weight", "invalid", "--height", "175"]
    with pytest.raises(SystemExit):
        cli_main()

    sys.argv = ["bmi_calculator.py", "--weight", "70", "--height", "invalid"]
    with pytest.raises(SystemExit):
        cli_main()


def test_api_bmi_success_with_different_values():
    response = client.get("/bmi?weight=50&height_cm=160")
    assert response.status_code == 200
    assert response.json() == {"bmi": 19.5, "category": "Normal weight"}

    response = client.get("/bmi?weight=95&height_cm=180")
    assert response.status_code == 200
    assert response.json() == {"bmi": 29.3, "category": "Overweight"}
