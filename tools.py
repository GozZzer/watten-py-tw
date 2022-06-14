import json
from string import ascii_lowercase, ascii_letters, ascii_uppercase, digits, punctuation

from kivy.properties import ObjectProperty

from objects import Client

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


def check_login(username: str, password: str) -> str | bool:
    with open("user_data.json", "r") as f:
        data = json.load(f)
        user_id = [user_id for user_id in data if data[user_id]["username"] == username][0]
        if user_id is None:
            return f"No username with the name {username} is registered"
        if data[user_id]["password"] != password:
            return f"Wrong password for user {username}"
    return True


def check_register(username: ObjectProperty, email: ObjectProperty, password: ObjectProperty, password_conf: ObjectProperty) -> str | Client:
    not_set = ""
    if username is None:
        not_set += "Username/"
    if email is None:
        not_set += "Email/"
    if password is None:
        not_set += "Password/"
    if password_conf is None:
        not_set += "Password-Confirmation/"
    if not_set != "":
        return f"Missing {not_set[:-1]}"
    with open("user_data.json", "r") as f:
        data = json.load(f)
        user_email = ""
        try:
            _ = [user_id for user_id in data if data[user_id]["username"] == username.text][0]
            user_email += username.text
            username.text = ""
        except IndexError:
            pass
        emails = [dt["email"] for dt in list(data.values())]
        if email.text in emails:
            if user_email != "":
                user_email += f"/{email.text} is already used"
            else:
                user_email += f"{email.text} is already used"
            email.text = ""
        else:
            if user_email != "":
                user_email += " is already used"
    if user_email != "":
        return user_email

    if password.text != password_conf.text:
        password.text = ""
        password_conf.text = ""
        return f"Passwords don't match"
    user = Client.new_user(username.text, email.text, password.text)
    username.text = ""
    email.text = ""
    password.text = ""
    password_conf.text = ""
    return user
