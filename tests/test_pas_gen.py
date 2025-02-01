from day_02.password_generator import generate_password, is_password_strong


def test_generate_password():
    password = generate_password(
        length=16, use_uppercase=True, use_digits=True, use_special=True
    )
    assert len(password) == 16
    assert is_password_strong(password)


def test_is_password_strong():
    assert is_password_strong("Abc123!@#") is True
    assert is_password_strong("abc123") is False
