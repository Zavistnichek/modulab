import pytest
from day_02.password_generator import generate_password, is_password_strong


@pytest.mark.parametrize(
    "length, use_uppercase, use_digits, use_special",
    [
        (16, True, True, True),
        (12, False, True, False),
        (20, True, False, True),
    ],
)
def test_generate_password(length, use_uppercase, use_digits, use_special):
    password = generate_password(length, use_uppercase, use_digits, use_special)
    assert len(password) == length
    assert any(c.isupper() for c in password) if use_uppercase else True
    assert any(c.isdigit() for c in password) if use_digits else True
    assert any(c in '!@#$%^&*(),.?":{}|<>' for c in password) if use_special else True


@pytest.mark.parametrize(
    "password, expected",
    [
        ("Abc123!@#", True),
        ("abc123", False),
        ("A1!", False),
        ("Abc1234", False),
    ],
)
def test_is_password_strong(password, expected):
    assert is_password_strong(password) == expected
