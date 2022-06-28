from string import ascii_lowercase, ascii_letters, ascii_uppercase, digits, punctuation

ALL_PASSWORD = ascii_uppercase + ascii_letters + ascii_lowercase + digits + punctuation
ALL_USERNAME = ascii_uppercase + ascii_letters + ascii_lowercase + digits + "_-."


def check_password(password: str) -> str | bool:
    invalid = ""
    for ch in password:
        if ch not in ALL_USERNAME:
            if ch not in invalid:
                invalid += ch
    return invalid if invalid else True


def check_username(username: str) -> str | bool:
    invalid = ""
    for ch in username:
        if ch not in ALL_USERNAME:
            if ch not in invalid:
                invalid += ch
    return invalid if invalid else True
