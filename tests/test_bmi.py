from day_01.bmi_calculator import BMICalculator


def test_normal_bmi():
    assert BMICalculator.calculate(70, 175) == 22.9


def test_invalid_height():
    assert BMICalculator.calculate(70, 0.4) is None
