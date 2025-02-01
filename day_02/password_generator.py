import secrets
import string
import re


def generate_password(
    length: int = 12,
    use_uppercase: bool = True,
    use_digits: bool = True,
    use_special: bool = True,
) -> str:
    """
    Generate a cryptographically secure random password.

    Args:
        length (int): Length of the password. Default is 12.
        use_uppercase (bool): Include uppercase letters. Default is True.
        use_digits (bool): Include digits. Default is True.
        use_special (bool): Include special characters. Default is True.

    Returns:
        str: Generated password.
    """
    characters = string.ascii_lowercase
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_digits:
        characters += string.digits
    if use_special:
        characters += string.punctuation

    if not characters:
        raise ValueError("At least one character set must be enabled.")

    return "".join(secrets.choice(characters) for _ in range(length))


password = generate_password(
    length=16, use_uppercase=True, use_digits=True, use_special=True
)
print(password)


def is_password_strong(password: str, min_length: int = 8) -> bool:
    """
    Checks if the password meets complexity requirements.

    Args:
        password (str): Password to check.
        min_length (int): Minimum length of the password. Default is 8.

    Returns:
        bool: True if the password is strong, False otherwise.
    """
    if len(password) < min_length:
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"\d", password):
        return False

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False

    return True


print(is_password_strong(password))
