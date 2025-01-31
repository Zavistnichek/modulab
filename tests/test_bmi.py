import pytest
import sys
from day_01.bmi_calculator import BMICalculator, get_args, main


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
    assert BMICalculator._validate_input(70, 273) is False


def test_calculate_with_exception():
    with pytest.raises(ValueError):
        BMICalculator.calculate("70", "175")


def test_get_args():
    sys.argv = ["bmi_calculator.py", "--weight", "70", "--height", "175"]
    args = get_args()
    assert args.weight == 70
    assert args.height == 175


def test_invalid_weight_type():
    with pytest.raises(ValueError):
        BMICalculator.calculate("70", 175)


def test_invalid_height_type():
    with pytest.raises(ValueError):
        BMICalculator.calculate(70, "175")


def test_non_numeric_input():
    with pytest.raises(ValueError):
        BMICalculator.calculate("invalid", "input")


def test_calculate_logging_invalid_input(caplog):
    with pytest.raises(ValueError):
        BMICalculator.calculate("70", "175")
    assert (
        "Input error: Both weight and height must be numbers (int or float)."
        in caplog.text
    )


def test_main(monkeypatch, caplog):
    monkeypatch.setattr("builtins.input", lambda _: "70")  # для веса
    monkeypatch.setattr("builtins.input", lambda _: "175")  # для роста
    with caplog.at_level("INFO"):
        main()
    assert "Your BMI: 22.9" in caplog.text
    assert "BMI Categories:" in caplog.text
    assert "Underweight = <18.5" in caplog.text
    assert "Normal weight = 18.5–24.9" in caplog.text
